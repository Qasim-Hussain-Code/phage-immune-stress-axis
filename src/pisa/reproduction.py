"""Bounded same-host offline reproduction from a committed Git archive.

This verifies a new source checkout, not an independently installed software
environment or another operating system. It never installs or downloads.
"""
from __future__ import annotations

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
import shutil
import subprocess
import sys
import tarfile
import time

from .acquisition import verify_cached_inputs
from .io import code_digest, digest, write_json
from .pipeline import DECLARED, STAGES, configure_environment, load_config, runtime_identity
from .resources import Guard, monitored_run


OPERATIONAL_CSV_NAMES = {'input_integrity.csv'}
SOURCE_PATHS = ['src', 'scripts', 'tests', 'config', 'requirements.txt', 'data/manifests/inputs.json']
REFERENCE_PATHS = ['data/processed', 'results/tables', 'figures']


def contained_path(base, relative):
    """Reject archive traversal, Windows drives/streams and alternate separators."""
    base=Path(base).resolve()
    value=str(relative)
    posix=PurePosixPath(value)
    if (not value or '\\' in value or ':' in value or posix.is_absolute()
            or PureWindowsPath(value).drive or any(part in ('..',) for part in posix.parts)):
        raise ValueError(f'Unsafe relative archive/output path: {value!r}')
    result=(base/Path(*posix.parts)).resolve()
    if result==base or not result.is_relative_to(base):
        raise ValueError(f'Path leaves its permitted directory: {value!r}')
    return result


def scientific_paths(root):
    """Deterministic scientific CSVs and figure bytes, not operational records."""
    root=Path(root)
    paths=set()
    for folder in ['data/processed','results/tables']:
        for path in (root/folder).rglob('*.csv'):
            if path.is_file() and path.name not in OPERATIONAL_CSV_NAMES:
                paths.add(path.relative_to(root).as_posix())
    for suffix in ['*.png','*.pdf']:
        for path in (root/'figures').rglob(suffix):
            if path.is_file(): paths.add(path.relative_to(root).as_posix())
    return sorted(paths)


def compare_scientific(reference_hashes, reproduced_root):
    current=set(scientific_paths(reproduced_root))
    expected=set(reference_hashes)
    rows=[]
    for relative in sorted(expected|current):
        path=contained_path(reproduced_root,relative)
        actual=digest(path) if relative in current else None
        original=reference_hashes.get(relative)
        rows.append({'path':relative,'reference_sha256':original,'reproduced_sha256':actual,
                     'status':'identical' if original is not None and original==actual else
                              'unexpected_output' if relative not in expected else
                              'missing_output' if relative not in current else 'different_bytes'})
    return rows


def safe_extract(archive, destination, max_bytes, guard, max_members=10000):
    """Extract regular files/directories only, with explicit expansion limits."""
    if max_bytes<=0 or max_members<=0:
        raise ValueError('Archive bounds must be positive')
    destination=Path(destination).resolve()
    destination.mkdir(parents=True,exist_ok=False)
    members=[]; seen=set(); total=0
    with tarfile.open(archive,'r:') as stream:
        for member in stream:
            if len(members)>=max_members: raise ValueError('Archive member limit exceeded')
            target=contained_path(destination,member.name)
            if member.name in seen: raise ValueError('Duplicate archive member')
            seen.add(member.name)
            if not member.isdir() and not member.isfile():
                raise ValueError('Archive links and special files are forbidden')
            if member.size<0: raise ValueError('Negative archive member size')
            total+=member.size
            if total>max_bytes: raise ValueError('Archive expansion size limit exceeded')
            members.append((member,target))
        guard.check(total)
        for member,target in members:
            if member.isdir():
                target.mkdir(parents=True,exist_ok=True)
                continue
            target.parent.mkdir(parents=True,exist_ok=True)
            source=stream.extractfile(member)
            if source is None: raise ValueError('Regular archive file has no content')
            with source, target.open('xb') as output:
                while True:
                    block=source.read(65536)
                    if not block: break
                    output.write(block)
                    guard.check()
            guard.observe_processes()
    return {'members':len(members),'regular_file_bytes':total}


def remove_disposable(root, target):
    """Recursive deletion is confined to a verified run under the cache root."""
    root=Path(root).resolve()
    permitted=contained_path(root,'.cache/reproduction')
    target=Path(target).resolve()
    if target==permitted or not target.is_relative_to(permitted) or not target.name.startswith('run_'):
        raise ValueError('Refuse deletion outside a named disposable reproduction run')
    if target.exists(): shutil.rmtree(target)


def clear_generated(checkout):
    """Preserve manual feasibility/provenance reports while removing all outputs."""
    checkout=Path(checkout).resolve()
    removed=[]
    directories=['data/processed','results/tables','figures','results/reports/stages',
                 'results/reports/logs','results/reports/invocations']
    for relative in directories:
        target=contained_path(checkout,relative)
        if target.exists():
            shutil.rmtree(target); removed.append(relative+'/')
    files={relative for values in DECLARED.values() for relative in values}
    files.update(['docs/results.md','docs/resource_usage.md','results/reports/run_status.json',
        'results/reports/resource_usage.json','results/reports/final_assessment.md',
        'results/reports/reproduction_check.json','data/manifests/environment_local.json',
        'data/manifests/resource_baseline_local.json'])
    for relative in sorted(files):
        target=contained_path(checkout,relative)
        if target.is_file(): target.unlink(); removed.append(relative)
    return sorted(removed)


def _git(root, arguments, timeout=30, allow_difference=False):
    result=subprocess.run(['git','-C',str(root),*arguments],capture_output=True,
                          text=True,encoding='utf-8',errors='strict',timeout=timeout)
    if result.returncode and not (allow_difference and result.returncode==1):
        raise RuntimeError('Git operation failed: '+result.stderr[-2000:])
    return result


def committed_identity(root, ref):
    commit=_git(root,['rev-parse','--verify','--end-of-options',str(ref)+'^{commit}']).stdout.strip()
    if len(commit) not in (40,64) or any(c not in '0123456789abcdef' for c in commit):
        raise ValueError('Expected a full Git commit ID from this repository')
    tree=_git(root,['rev-parse',commit+'^{tree}']).stdout.strip()
    # Git applies the repository's normal text normalization. Raw working and
    # exported code digests are additionally reported rather than conflated.
    changed=_git(root,['diff','--quiet',commit,'--',*SOURCE_PATHS,*REFERENCE_PATHS],allow_difference=True)
    if changed.returncode:
        raise ValueError('Code/config or scientific reference outputs differ from selected committed ref')
    untracked=_git(root,['ls-files','--others','--exclude-standard','--',*SOURCE_PATHS,*REFERENCE_PATHS]).stdout.strip()
    if untracked:
        raise ValueError('Untracked code or scientific reference files must be committed first: '+untracked[:1000])
    listing=_git(root,['ls-tree','-r','-l','-z',commit]).stdout
    if len(listing)>5_000_000: raise ValueError('Git tree inventory exceeds bounded metadata size')
    rows=[row for row in listing.split('\0') if row]
    if len(rows)>10000: raise ValueError('Git archive file-count limit exceeded')
    total=0
    for row in rows:
        description,name=row.split('\t',1)
        mode,kind,object_id,size=description.split()
        if kind!='blob' or mode not in ('100644','100755'):
            raise ValueError('Reproduction archive requires ordinary tracked files, without links/submodules')
        total+=int(size)
    return {'requested_ref':str(ref),'commit':commit,'tree':tree,'tracked_files':len(rows),
            'tracked_file_bytes':total,'estimated_tar_bound_bytes':total+4096*len(rows)+1_048_576,
            'working_git_normalized_source_and_reference_match':True}


class RecordingGuard:
    """Retain the outer guard's sampled peak checkout storage, including copies."""
    def __init__(self, guard):
        self.guard=guard; self.config=guard.config
        self.max_project_bytes=0; self.last={}
    def check(self, additional=0):
        self.last=self.guard.check(additional)
        self.max_project_bytes=max(self.max_project_bytes,self.last['project_bytes_including_git'])
        return self.last
    def observe_processes(self): return self.guard.observe_processes()
    def snapshot(self):
        result=self.check()
        result['max_sampled_project_bytes_including_disposable_checkout']=self.max_project_bytes
        return result


def record_resource_snapshot(report, guard, label, error_key):
    """Cleanup cannot convert a detected resource breach into a passed check."""
    try:
        report[label]=guard.snapshot()
    except Exception as exc:
        report[error_key]=str(exc)
        if report.get('status')!='interrupted': report['status']='failed'
        report.setdefault('error_type','ResourceCheckError')
        report.setdefault('error',f'{label}: {exc}')


def run(root, ref='HEAD', keep=False, timeout=600, max_export_bytes=50_000_000):
    root=Path(root).resolve()
    started=time.monotonic()
    timestamp=datetime.now(timezone.utc)
    identifier='run_'+timestamp.strftime('%Y%m%dT%H%M%S%fZ')
    disposable=contained_path(root,'.cache/reproduction/'+identifier)
    report={'schema_version':1,'started_utc':timestamp.isoformat(),'status':'running',
        'scope':'same-host committed-source checkout, existing interpreter/packages, offline full execution',
        'network_requested':False,'packages_installed':False,'keep_requested':keep,
        'runtime':runtime_identity(),'requested_ref':str(ref),'comparisons':[]}
    report_path=root/'results/reports/reproduction_check.json'
    guard=None
    try:
        if timeout<=0 or max_export_bytes<=0: raise ValueError('Timeout and export cap must be positive')
        configure_environment(root)
        config=load_config(root/'config/analysis.yaml')
        guard=RecordingGuard(Guard(root,config)); guard.check()
        identity=committed_identity(root,ref); report['git']=identity
        if identity['estimated_tar_bound_bytes']>max_export_bytes:
            raise ValueError('Selected committed tree exceeds bounded export estimate')
        expected_paths=scientific_paths(root)
        if not expected_paths: raise ValueError('No reference scientific outputs exist for comparison')
        expected={relative:digest(root/relative) for relative in expected_paths}
        report['reference_scope']='working file bytes at start, Git-normalized equivalent to selected commit'
        report['reference_sha256']=expected
        report['working_code_digest']=code_digest(root)
        guard.check(2*identity['estimated_tar_bound_bytes'])
        disposable.mkdir(parents=True,exist_ok=False)
        archive=disposable/'source.tar'; checkout=disposable/'checkout'
        command=['git','-C',str(root),'archive','--format=tar','--output='+str(archive),identity['commit']]
        code=monitored_run(command,root,disposable/'git_archive.log',guard,timeout=60)
        if code: raise RuntimeError('git archive failed; see disposable git_archive.log')
        if archive.stat().st_size>max_export_bytes: raise ValueError('Exported archive exceeds hard byte cap')
        report['archive']={'sha256':digest(archive),'bytes':archive.stat().st_size}
        report['extraction']=safe_extract(archive,checkout,max_export_bytes,guard)
        report['exported_code_digest']=code_digest(checkout)
        report['raw_code_digests_equal']=report['working_code_digest']==report['exported_code_digest']
        report['code_digest_note']='Git-normalized equivalence is checked; raw code bytes can differ only through configured text normalization'
        if set(scientific_paths(checkout))!=set(expected):
            raise ValueError('Committed and working reference output inventories differ')
        report['cleared_generated_paths']=clear_generated(checkout)
        if scientific_paths(checkout): raise AssertionError('Generated scientific outputs survived cleanup')
        if (checkout/'results/reports/stages').exists(): raise AssertionError('Stage stamps survived cleanup')
        report['inputs_before_execution']=verify_cached_inputs(checkout,config,guard)
        command=[sys.executable,str(checkout/'scripts/run_all.py'),'--config','config/analysis.yaml',
                 '--threads','1','--offline','--mode','full']
        report['command']=command
        log=root/'results/reports/reproduction_run.log'
        code=monitored_run(command,checkout,log,guard,timeout=timeout)
        report['child_exit_code']=code
        if code:
            raise RuntimeError('Fresh offline full pipeline failed; see results/reports/reproduction_run.log')
        state=json.loads((checkout/'results/reports/run_status.json').read_text(encoding='utf-8'))
        stages=state.get('stages',[])
        report['executed_stages']=[{'name':row['name'],'status':row['status']} for row in stages]
        if (state.get('status')!='completed_restricted_analysis' or state.get('mode')!='full'
                or [row['name'] for row in stages]!=STAGES
                or any(row['status']!='completed' for row in stages)
                or state.get('scientific_stages_executed')!=len(STAGES)
                or state.get('scientific_stages_resumed_verified')!=0):
            raise ValueError('Fresh run did not execute every required stage without resume')
        report['inputs_after_execution']=verify_cached_inputs(checkout,config,guard)
        if any(not (root/relative).is_file() or digest(root/relative)!=value for relative,value in expected.items()):
            raise ValueError('Working reference changed during reproduction; comparison is invalid')
        report['comparisons']=compare_scientific(expected,checkout)
        report['comparison_method']='exact SHA-256 byte equality; no semantic or numeric tolerance fallback'
        report['identical_outputs']=sum(row['status']=='identical' for row in report['comparisons'])
        report['comparison_outputs']=len(report['comparisons'])
        report['validation']=json.loads((checkout/'results/reports/validation_summary.json').read_text(encoding='utf-8'))
        report['fresh_run_resources']=json.loads((checkout/'results/reports/resource_usage.json').read_text(encoding='utf-8'))
        if not all(row['status']=='identical' for row in report['comparisons']):
            raise ValueError('Scientific outputs failed exact-byte reproduction; inspect comparisons')
        report['status']='passed'
    except BaseException as exc:
        report['status']='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed'
        report['error_type']=type(exc).__name__; report['error']=str(exc)
        raise
    finally:
        if guard:
            record_resource_snapshot(report,guard,'outer_resources_before_cleanup','outer_resource_check_error')
        if disposable.exists() and not keep:
            try:
                remove_disposable(root,disposable); report['disposable_cleanup']='removed'
            except Exception as exc:
                report['disposable_cleanup']='failed'; report['cleanup_error']=str(exc)
                report['status']='failed'
        else:
            report['disposable_cleanup']='retained' if disposable.exists() else 'not_created'
        report['disposable_path']=disposable.relative_to(root).as_posix() if disposable.exists() else None
        if guard:
            record_resource_snapshot(report,guard,'outer_resources_after_cleanup','final_resource_check_error')
        report['elapsed_seconds']=round(time.monotonic()-started,3)
        report['finished_utc']=datetime.now(timezone.utc).isoformat()
        write_json(report_path,report)
        write_documentation(root,report)
    return report


def write_documentation(root,report):
    lines=['# Local committed-source reproduction validation','',
        f"Status: {report['status']}. Recorded UTC completion: {report.get('finished_utc','not recorded')}.",
        f"Selected Git commit: {report.get('git',{}).get('commit','not resolved')}.",
        f"Scope: {report['scope']}.",'',
        'This check uses a fresh Git archive inside the existing workspace and the same Python '
        'interpreter and installed package environment. It does not establish Linux execution, '
        'independent dependency installation, virtual-machine reproduction, or remote CI success. '
        'No network or package installation is requested.','',
        'Before execution, generated scientific outputs and stage stamps are removed from the '
        'disposable checkout. The full ten-stage command is run offline with one worker and '
        'without resume. Frozen inputs are checked before and after. Scientific CSV and PNG/PDF '
        'inventories must agree and all output bytes must match the starting working reference. '
        'Git-normalized source/reference equivalence to the selected commit is checked separately. '
        'No numeric-tolerance fallback is used. Timestamps, run statuses, resource measurements '
        'and acquisition-cache status tables are operational records and are excluded from '
        'scientific output comparison.','',
        f"Stages verified as executed: {len(report.get('executed_stages',[]))}. "
        f"Identical scientific outputs: {report.get('identical_outputs',0)} / {report.get('comparison_outputs',0)}.",
        f"Disposable checkout/archive cleanup: {report.get('disposable_cleanup','not recorded')}.",
        'Outer storage checks include the archive, disposable checkout, its generated outputs and '
        'temporary/cache files. Outer sampled aggregate memory includes the reproduction controller, '
        'fresh runner, stages and validation descendants. Per-process native peaks and sampled '
        'simultaneous RSS remain distinct measurements.','',
        'Machine-readable evidence: `results/reports/reproduction_check.json`. Child log: '
        '`results/reports/reproduction_run.log`. The JSON contains exact source identities, '
        'input checks, each comparison and resource observations.']
    if report.get('error'):
        lines.extend(['','Failure: '+report['error']])
    (root/'docs').mkdir(parents=True,exist_ok=True)
    (root/'docs/reproduction_validation.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--ref',default='HEAD')
    parser.add_argument('--keep',action='store_true')
    parser.add_argument('--timeout',type=float,default=600)
    parser.add_argument('--max-export-bytes',type=int,default=50_000_000)
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    result=run(root,args.ref,args.keep,args.timeout,args.max_export_bytes)
    print(json.dumps({'status':result['status'],'commit':result['git']['commit'],
                      'identical_outputs':result.get('identical_outputs',0)}))
    if result['status']!='passed': raise SystemExit(1)
