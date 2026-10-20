"""Offline native-WSL validation worker; stdin bootstrap tar, stdout result tar.

The host owns the physical Windows disk/RAM guard and source-commit selection.
This worker writes only its fresh, marked /tmp run directory and leaves it for
host verification/cleanup. It must be invoked with guest CWD / and inline code.
"""
from __future__ import annotations

import contextlib
import datetime
import hashlib
import importlib.metadata
import io
import json
import os
from pathlib import Path, PurePosixPath
import platform
import re
import shutil
import signal
import sys
import tarfile
import time
import traceback
import zipfile

PREPARATION_CAP = 1_500_000_000
BOOTSTRAP_CAP = 125_000_000
SOURCE_CAP = 50_000_000
ARTIFACT_CAP = 50_000_000
PARENT = Path('/tmp/phage-immune-stress-axis_validation')


def sha(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b''):
            value.update(chunk)
    return value.hexdigest()


def emit(message):
    print(message, file=sys.stderr, flush=True)


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2, allow_nan=False) + '\n', encoding='utf-8')


def relative(name):
    if not isinstance(name, str) or '\\' in name or '\x00' in name:
        raise ValueError('Invalid archive path')
    value = PurePosixPath(name)
    if value.is_absolute() or not value.parts or any(p in ('', '.', '..') for p in value.parts):
        raise ValueError('Archive path escapes target')
    return value


def extract(archive, destination, byte_cap, member_cap):
    """Extract only fresh ordinary files/directories; never follow archive links."""
    total = count = 0
    names = set()
    for member in archive:
        count += 1
        if count > member_cap:
            raise ValueError('Archive member count exceeds bound')
        rel = relative(member.name.rstrip('/'))
        key = rel.as_posix()
        if key in names:
            raise ValueError('Duplicate archive member')
        names.add(key)
        target = destination.joinpath(*rel.parts)
        if member.isdir():
            target.mkdir(parents=True, exist_ok=True, mode=0o700)
            continue
        if not member.isfile() or member.issparse():
            raise ValueError('Only ordinary non-sparse archive files are accepted')
        total += member.size
        if member.size < 0 or total > byte_cap:
            raise ValueError('Archive expanded bytes exceed bound')
        target.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
        with archive.extractfile(member) as source, target.open('xb') as output:
            left = member.size
            while left:
                data = source.read(min(left, 1024 * 1024))
                if not data:
                    raise ValueError('Truncated archive member')
                output.write(data)
                left -= len(data)
        target.chmod(0o600)
    return {'members': count, 'regular_file_bytes': total}


def verify_file(root, record):
    path = root.joinpath(*relative(record['path']).parts)
    expected_bytes = record.get('bytes', record.get('wheel_bytes'))
    expected_sha = record.get('sha256', record.get('wheel_sha256'))
    if not isinstance(expected_bytes, int) or isinstance(expected_bytes, bool) or expected_bytes <= 0:
        raise ValueError('Invalid declared file size')
    if not re.fullmatch('[0-9a-f]{64}', str(expected_sha)):
        raise ValueError('Missing declared SHA-256')
    if not path.is_file() or path.stat().st_size != expected_bytes or sha(path) != expected_sha:
        raise ValueError('Staged file differs from verified host metadata: ' + record['path'])
    return path


def snapshot_inputs(checkout):
    manifest = json.loads((checkout / 'data/manifests/inputs.json').read_text())
    rows = []
    for source in manifest:
        path = checkout.joinpath(*relative(source['path']).parts)
        observed = sha(path)
        if observed != source['sha256'] or ('bytes' in source and path.stat().st_size != source['bytes']):
            raise ValueError('Frozen scientific input changed: ' + source['path'])
        rows.append({'path': source['path'], 'bytes': path.stat().st_size, 'sha256': observed})
    if len(rows) != 10:
        raise ValueError('Expected the frozen ten-input manifest')
    return rows


def canonical(name):
    return re.sub(r'[-_.]+', '-', name).lower()


def run_worker(run):
    started = time.monotonic()
    evidence = {'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'native_run_directory': str(run), 'status': 'starting',
                'python': sys.version, 'platform': platform.platform(), 'uid': os.getuid(),
                'base_executable': sys.executable, 'analysis_executed': False,
                'network_retrieval_requested': False, 'commands': [],
                'limits': {'preparation_bytes': PREPARATION_CAP, 'bootstrap_regular_bytes': BOOTSTRAP_CAP,
                           'source_regular_bytes': SOURCE_CAP, 'artifact_tar_bytes': ARTIFACT_CAP,
                           'whole_guest_timeout_seconds': 900, 'per_command_timeout_seconds': 600}}
    setup = {'status': 'not_started', 'commands': evidence['commands']}
    checkout = run / 'checkout'
    logs = run / 'logs'
    logs.mkdir(mode=0o700)
    guard = None
    error = None
    try:
        emit('Extract bounded bootstrap into ' + str(run))
        staged = run / 'staged'
        staged.mkdir(mode=0o700)
        with tarfile.open(fileobj=sys.stdin.buffer, mode='r|') as archive:
            evidence['bootstrap_extraction'] = extract(archive, staged, BOOTSTRAP_CAP, 100)
        metadata = json.loads((staged / 'metadata.json').read_text())
        source = metadata['source']
        source_tar = verify_file(staged, source)
        commit = source['commit']
        if not re.fullmatch('[0-9a-f]{40,64}', commit) or source_tar.stat().st_size > SOURCE_CAP:
            raise ValueError('Invalid source archive/commit contract')
        checkout.mkdir(mode=0o700)
        with tarfile.open(source_tar, mode='r:') as archive:
            comment = archive.pax_headers.get('comment')
            if comment is not None and comment.strip() != commit:
                raise ValueError('Git source archive commit marker differs from expected commit')
            evidence['source_archive_commit_marker'] = comment
            evidence['source_extraction'] = extract(archive, checkout, SOURCE_CAP, 10_000)
        wheels = metadata['wheels']
        if isinstance(wheels, dict):
            wheels = list(wheels.values())
        if len(wheels) != 21:
            raise ValueError('Expected twenty-one pinned wheels')
        paths = [verify_file(staged, item) for item in wheels]
        if any(not p.name.endswith('.whl') or p.stat().st_size > 60_000_000 for p in paths):
            raise ValueError('Only bounded prebuilt wheels are accepted')
        expected = {canonical(item['name']): item['version'] for item in wheels}
        if len(expected) != 21 or len(set(paths)) != 21:
            raise ValueError('Duplicate wheel name/path')
        declared = {}
        for line in (checkout / 'requirements.txt').read_text().splitlines():
            line = line.split('#', 1)[0].strip()
            if line:
                name, version = line.split('==')
                declared[canonical(name.strip())] = version.strip()
        if declared != expected:
            raise ValueError('Source requirements and verified wheel versions differ')
        pip = metadata['pip']
        pip_path = verify_file(staged, pip)
        if pip.get('version') != '25.2':
            raise ValueError('Expected copied pure-Python pip25.2 bootstrap')
        expanded = 0
        for path in [*paths, pip_path]:
            with zipfile.ZipFile(path) as wheel:
                expanded += sum(item.file_size for item in wheel.infolist())
        if expanded > 1_000_000_000:
            raise ValueError('Expanded wheel member total exceeds one GB')
        evidence['expanded_wheel_member_bytes_including_bootstrap'] = expanded
        if pip_path.name != 'pip-25.2-py3-none-any.whl':
            canonical_pip = staged / 'pip-25.2-py3-none-any.whl'
            with pip_path.open('rb') as source_stream, canonical_pip.open('xb') as output:
                shutil.copyfileobj(source_stream, output, 1024 * 1024)
            pip_path = canonical_pip
        sys.path.insert(0, str(checkout / 'src'))
        from pisa.resources import Guard, monitored_run
        from pisa.io import code_digest
        original = {'commit': commit, 'source_tar_sha256': sha(source_tar),
                    'code_sha256': code_digest(checkout),
                    'requirements_sha256': sha(checkout / 'requirements.txt'),
                    'input_manifest_sha256': sha(checkout / 'data/manifests/inputs.json'),
                    'original_config_sha256': sha(checkout / 'config/analysis.yaml')}
        for key in ('code_sha256', 'requirements_sha256', 'input_manifest_sha256'):
            if original[key] != source[key]:
                raise ValueError('Extracted source contract differs: ' + key)
        if source.get('config_sha256') and original['original_config_sha256'] != source['config_sha256']:
            raise ValueError('Original source configuration hash differs')
        evidence['source_before'] = original
        evidence['inputs_before'] = snapshot_inputs(checkout)
        from pisa.reproduction import clear_generated, scientific_paths
        source_scientific_paths = scientific_paths(checkout)
        if len(source_scientific_paths) != 30:
            raise ValueError('Committed source must contain the locked thirty-output reference inventory')
        evidence['expected_scientific_paths'] = source_scientific_paths
        evidence['removed_generated_paths'] = clear_generated(checkout)
        if scientific_paths(checkout):
            raise ValueError('Generated scientific outputs survived fresh-checkout cleanup')
        evidence['scientific_paths_empty_before_execution'] = True
        config = json.loads(json.dumps(metadata['config']))
        config['resources'].update(max_new_storage_bytes=PREPARATION_CAP, disk_reserve_bytes=4_000_000_000,
                                   max_workers=1, stage_timeout_seconds=600)
        config['threads'] = 1
        limits = config['resources']
        if any(limits[key] > 1_000_000_000 for key in ('max_process_rss_bytes', 'max_aggregate_rss_bytes')):
            raise ValueError('Guest memory ceiling exceeds one GB')
        config_path = checkout / 'config/native_validation.json'
        save(config_path, config)
        evidence['native_config_sha256'] = sha(config_path)
        evidence['native_config'] = config
        temporary = run / 'tmp'
        temporary.mkdir(mode=0o700)
        for key in list(os.environ):
            if key.startswith('PIP_') or key in ('PYTHONPATH', 'PYTHONHOME'):
                del os.environ[key]
        os.environ.update({k: str(temporary) for k in ('TMPDIR', 'TMP', 'TEMP')})
        os.environ.update({k: '1' for k in ('OMP_NUM_THREADS', 'OPENBLAS_NUM_THREADS', 'MKL_NUM_THREADS', 'NUMEXPR_NUM_THREADS')})
        os.environ.update(PYTHONDONTWRITEBYTECODE='1', PIP_CONFIG_FILE='/dev/null',
                          PIP_CACHE_DIR=str(run / 'pip_cache'), PIP_NO_INPUT='1',
                          XDG_CACHE_HOME=str(run / 'cache'), MPLCONFIGDIR=str(run / 'cache/matplotlib'))
        guard = Guard(run, config)
        evidence['resources_before'] = guard.check(500_000_000)
        env = run / 'env'
        python = str(env / 'bin/python')

        def command(name, argv):
            emit('START ' + name)
            row = {'name': name, 'argv': argv, 'started_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}
            evidence['commands'].append(row)
            begin = time.monotonic()
            left = 900 - (begin - started)
            if left <= 0:
                raise TimeoutError('Whole guest deadline reached')
            returncode = monitored_run(argv, run, logs / (name + '.log'), guard, timeout=min(600, left))
            row.update(returncode=returncode, elapsed_seconds=round(time.monotonic() - begin, 3), resources=guard.check())
            if returncode:
                raise RuntimeError(name + ' returned ' + str(returncode))
            emit('DONE ' + name)

        setup['status'] = 'installing_new_isolated_linux_environment'
        command('create_venv', [sys.executable, '-I', '-B', '-m', 'venv', '--without-pip', '--copies', str(env)])
        if 'include-system-site-packages = false' not in (env / 'pyvenv.cfg').read_text():
            raise ValueError('Venv exposes base distributions')
        bootstrap_code = "import sys,runpy;sys.path.insert(0,sys.argv.pop(1));sys.argv[0]='pip';runpy.run_module('pip',run_name='__main__',alter_sys=True)"
        install = ['--isolated', '--disable-pip-version-check', 'install', '--no-index', '--no-deps',
                   '--no-compile', '--no-cache-dir', '--no-input', '--only-binary=:all:']
        command('bootstrap_pip', [python, '-I', '-B', '-c', bootstrap_code, str(pip_path), *install, str(pip_path)])
        command('install_pins', [python, '-I', '-B', '-m', 'pip', *install, *map(str, paths)])
        command('pip_check', [python, '-I', '-B', '-m', 'pip', '--isolated', '--disable-pip-version-check', 'check'])
        inspect_code = """import sys,pathlib,json,re,importlib.metadata as m,contextlib,io
expected=json.loads(sys.argv[1]);canon=lambda n:re.sub(r'[-_.]+','-',n).lower()
observed={canon(d.metadata['Name']):d.version for d in m.distributions()}
assert sys.prefix!=sys.base_prefix and pathlib.Path(sys.prefix).resolve()==pathlib.Path(sys.argv[2]).resolve()
assert {k:v for k,v in observed.items() if k!='pip'}==expected and observed.get('pip')=='25.2'
import yaml
assert yaml.safe_load(pathlib.Path(sys.argv[3]).read_text())==json.loads(sys.argv[4])
print(json.dumps({'python':sys.version,'prefix':sys.prefix,'base_prefix':sys.base_prefix,'packages':observed,'expected_pins_matched':len(expected)}))
import numpy,scipy
for name,module in [('numpy',numpy),('scipy',scipy)]:
 stream=io.StringIO()
 with contextlib.redirect_stdout(stream):module.show_config()
 print(json.dumps({'binary_configuration':name,'text':stream.getvalue()}))
"""
        command('inspect_installed', [python, '-I', '-B', '-c', inspect_code, json.dumps(expected), str(env),
                                      str(checkout / 'config/analysis.yaml'), json.dumps(metadata['config'])])
        setup.update(status='prepared_dependency_and_binary_configuration_verified',
                     installed_metadata_log=(logs / 'inspect_installed.log').read_text(), wheels=wheels, pip=pip,
                     newly_installed=True, numerical_analysis_run=False)
        evidence['original_config_matches_host_metadata'] = True
        if scientific_paths(checkout):
            raise ValueError('Scientific output appeared during dependency setup')
        evidence['analysis_executed'] = True
        command('full_pipeline', [python, '-B', str(checkout / 'scripts/run_all.py'), '--mode', 'full',
                                  '--threads', '1', '--offline', '--config', str(config_path)])
        status = json.loads((checkout / 'results/reports/run_status.json').read_text())
        validation = json.loads((checkout / 'results/reports/validation_summary.json').read_text())
        from pisa.pipeline import STAGES
        if (status.get('status') != 'completed_restricted_analysis' or status.get('scientific_stages_executed') != 10
                or status.get('scientific_stages_resumed_verified') != 0
                or [row['name'] for row in status.get('stages', [])] != STAGES
                or any(row['status'] != 'completed' for row in status.get('stages', []))
                or not validation.get('success') or validation.get('tests_run', 0) < 1
                or validation.get('code_sha256') != original['code_sha256']
                or not validation.get('source_unchanged_during_validation')):
            raise ValueError('Full pipeline/validation did not complete fresh ten-stage execution')
        if scientific_paths(checkout) != source_scientific_paths:
            raise ValueError('Reproduced scientific inventory differs from the locked thirty outputs')
        evidence.update(status='completed_independent_linux_validation', full_pipeline_status=status, validation=validation)
    except BaseException as exc:
        error = exc
        evidence.update(status='failed', error_type=type(exc).__name__, error=str(exc), traceback=traceback.format_exc())
        emit(evidence['traceback'])
    finally:
        # Keep the original alarm active through finalization and stdout drain.
        # If it already fired, bound failure-evidence recovery as well; the host
        # independently enforces its outer deadline and verifies termination.
        if time.monotonic() - started >= 900:
            signal.alarm(1)
        if guard is not None:
            try:
                evidence['resources_after'] = guard.check()
            except BaseException as exc:
                evidence['resource_finalization_error'] = repr(exc)
                if error is None:
                    error = exc
                    evidence['status'] = 'failed'
        if 'source_before' in evidence:
            try:
                from pisa.io import code_digest
                evidence['source_after'] = {**evidence['source_before'], 'code_sha256': code_digest(checkout),
                    'requirements_sha256': sha(checkout / 'requirements.txt'),
                    'input_manifest_sha256': sha(checkout / 'data/manifests/inputs.json'),
                    'original_config_sha256': sha(checkout / 'config/analysis.yaml')}
                evidence['inputs_after'] = snapshot_inputs(checkout)
                if evidence['source_before'] != evidence['source_after'] or evidence['inputs_before'] != evidence['inputs_after']:
                    raise ValueError('Source specification or frozen inputs changed during guest execution')
            except BaseException as exc:
                evidence['immutability_error'] = repr(exc)
                evidence['status'] = 'failed'
                if error is None:
                    error = exc
        evidence['elapsed_seconds'] = round(time.monotonic() - started, 3)
        setup['analysis_executed_by_this_worker'] = evidence['analysis_executed']
        reports = checkout / 'results/reports'
        save(reports / 'setup_evidence.json', setup)
        save(reports / 'guest_evidence.json', evidence)
    emit('Package bounded result artifacts; status=' + evidence['status'])
    selected = {}
    for prefix in ('results', 'figures', 'data/processed'):
        for path in (checkout / prefix).rglob('*'):
            if path.is_file() and not path.is_symlink():
                selected[path.relative_to(checkout).as_posix()] = path
    for rel in ('docs/results.md', 'data/manifests/environment_local.json', 'data/manifests/resource_baseline_local.json', 'config/native_validation.json'):
        if (checkout / rel).is_file():
            selected[rel] = checkout / rel
    for path in logs.glob('*.log'):
        selected['results/reports/native_setup_logs/' + path.name] = path
    if sum(path.stat().st_size for path in selected.values()) > ARTIFACT_CAP - 2_000_000:
        raise ValueError('Selected artifact bytes exceed output allowance')
    if guard is not None:
        guard.check(ARTIFACT_CAP)
    artifact = run / 'artifacts.tar'
    with tarfile.open(artifact, 'w', format=tarfile.PAX_FORMAT) as archive:
        for name, path in sorted(selected.items()):
            archive.add(path, arcname=name, recursive=False)
    if artifact.stat().st_size > ARTIFACT_CAP:
        raise ValueError('Result tar exceeds fifty MB')
    if guard is not None:
        guard.check()
    with artifact.open('rb') as stream:
        shutil.copyfileobj(stream, sys.stdout.buffer, 1024 * 1024)
    sys.stdout.buffer.flush()
    signal.alarm(0)
    return 1 if error is not None else 0


def main():
    if len(sys.argv) != 2:
        raise ValueError('Expected one fresh native run directory argument')
    run = Path(sys.argv[1])
    if run.parent != PARENT or not re.fullmatch(r'run_[A-Za-z0-9_-]+', run.name):
        raise ValueError('Native run directory must be a direct child of the dedicated /tmp parent')
    def host_cancellation(signum, frame):
        raise RuntimeError('Host requested cancellation')
    signal.signal(signal.SIGTERM, host_cancellation)
    if PARENT.exists() and (PARENT.is_symlink() or PARENT.owner() != __import__('pwd').getpwuid(os.getuid()).pw_name):
        raise ValueError('Native parent is not owned ordinary directory')
    PARENT.mkdir(mode=0o700, exist_ok=True)
    run.mkdir(mode=0o700)
    start_ticks = int(Path('/proc/self/stat').read_text().rsplit(')', 1)[1].split()[19])
    (run / '.pisa_native_validation_owned').write_text(json.dumps({'uid': os.getuid(), 'pid': os.getpid(),
        'start_ticks': start_ticks, 'created_utc': datetime.datetime.now(datetime.timezone.utc).isoformat()}) + '\n')
    if (run / '.cancelled_by_host').exists():
        raise RuntimeError('Host requested cancellation')
    if shutil.disk_usage(run).free - PREPARATION_CAP < 4_000_000_000:
        raise RuntimeError('Native filesystem reserve would be exceeded')
    def deadline(signum, frame):
        raise TimeoutError('Whole native setup and validation exceeded900seconds')
    signal.signal(signal.SIGALRM, deadline)
    signal.alarm(900)
    return run_worker(run)


if __name__ == '__main__':
    raise SystemExit(main())
