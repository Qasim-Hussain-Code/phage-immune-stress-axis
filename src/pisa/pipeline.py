"""Sequential, resumable runner with explicit scientific exclusion statuses."""
import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
import runpy
from pathlib import Path
import subprocess
import sys
import time
import traceback
from .io import digest, write_csv, write_json
from .resources import Guard, project_size, peak_rss, monitored_run

STAGES = [
    '01_audit_sources', '02_fetch_data', '03_validate_samples', '04_virome_qc',
    '05_stability_metrics', '06_immune_phenotypes', '07_immune_associations',
    '08_bacteriome_integration', '09_robustness_checks', '10_generate_figures']

DECLARED = {
 STAGES[0]:['results/reports/source_audit.json'],
 STAGES[1]:['results/tables/input_integrity.csv','results/tables/article_methods_evidence.csv','results/tables/archive_files.csv','data/raw/ritz2024_archive/PRJNA970614_sample_attributes.csv'],
 STAGES[2]:['results/tables/sample_linkage_audit.csv','results/tables/sequencing_inventory.csv','results/reports/sample_linkage.md','results/reports/sample_audit_summary.json'],
 STAGES[3]:['results/reports/virome_qc.md'],
 STAGES[4]:['results/tables/hypothesis_eligibility.csv'],
 STAGES[5]:['data/processed/immune_long.csv','results/tables/immune_missingness.csv','results/tables/source_inventory.csv'],
 STAGES[6]:['results/tables/immune_contrasts.csv','results/tables/immune_sensitivity.csv','results/tables/immune_summary.csv','results/reports/phage_immune_associations.md','results/tables/original_method_replication.csv','results/reports/original_method_replication.md'],
 STAGES[7]:['results/reports/bacteriome_integration.md'],
 STAGES[8]:['results/reports/validation.log','results/reports/validation_summary.json','docs/results.md','results/tables/software_calibration.csv','results/reports/software_calibration.md'],
 STAGES[9]:[f'figures/{name}.{ext}' for name in ['figure1_design','figure4_immune','figure5_linkage_limit','figure7_robustness','figure8_method_comparison'] for ext in ['png','pdf']]+[f'results/tables/figure{n}_data.csv' for n in [1,4,5,7,8]]}


def runtime_identity():
    """Library changes invalidate cached calculations without importing them."""
    versions = {}
    for name in ['numpy', 'scipy', 'matplotlib', 'openpyxl', 'PyYAML', 'statsmodels', 'pypdf']:
        try:
            versions[name] = importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:
            versions[name] = None
    return {'python': sys.version, 'platform': sys.platform, 'packages': versions}


def configure_environment(root):
    """Keep child temporaries and ordinary numerical caches within the budget."""
    cache=Path(root)/'.cache'
    temporary=cache/'tmp'
    temporary.mkdir(parents=True,exist_ok=True)
    os.environ.update({name:'1' for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']})
    os.environ.update({name:str(temporary) for name in ['TMP','TEMP','TMPDIR']})
    os.environ.update({'XDG_CACHE_HOME':str(cache),'MPLCONFIGDIR':str(cache/'matplotlib'),
                      'PIP_CACHE_DIR':str(cache/'pip')})


def upstream_hashes(root, stage):
    """Explicit conservative dependency chain across all preceding stages."""
    result = {}
    for previous in STAGES[:STAGES.index(stage)]:
        for relative in DECLARED[previous]:
            path = root/relative
            if not path.is_file():
                raise FileNotFoundError(f'{stage} prerequisite missing: {relative}; run preceding stages')
            result[relative] = digest(path)
    return result


def cache_valid(root, stage, record, key, dependencies):
    if not isinstance(record,dict) or stage not in DECLARED:
        return False
    if record.get('schema_version') != 2 or record.get('stage') != stage:
        return False
    if not all(isinstance(record.get(field),dict) for field in ['result','resources','outputs','upstream_outputs']):
        return False
    recorded_peak=record['resources'].get('process_peak_rss_bytes')
    if isinstance(recorded_peak,bool) or not isinstance(recorded_peak,int) or recorded_peak<0:
        return False
    if record.get('fingerprint') != key or record.get('upstream_outputs') != dependencies:
        return False
    saved = record['outputs']
    if set(saved) != set(DECLARED[stage]):
        return False
    if any(not isinstance(value,str) or len(value)!=64 or any(char not in '0123456789abcdef' for char in value)
           for value in saved.values()):
        return False
    if not all((root/path).is_file() and digest(root/path) == value for path, value in saved.items()):
        return False
    if stage==STAGES[8]:
        # Counts/runtime identities displayed from a resumed result must agree
        # with the separately hash-verified executed validation summary.
        try:
            validation=json.loads((root/'results/reports/validation_summary.json').read_text(encoding='utf-8'))
        except (ValueError,OSError):
            return False
        if not isinstance(validation,dict) or not validation.get('success'):
            return False
        if any(record['result'].get(name)!=value for name,value in validation.items()):
            return False
    return True


def load_config(path):
    import yaml
    config = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    fixed = ['ly6chi_monocytes', 'ly6chi_monocytes_cd62', 'tnfa_splenocyte_unstimulated']
    if config['immune']['endpoints'] != fixed:
        raise ValueError('Endpoint changes require an updated analysis plan and test family')
    if config['immune']['confidence_level'] != 0.95:
        raise ValueError('The fixed analysis plan uses pointwise 95% intervals')
    limits=config['resources']
    for name in ['max_workers','max_new_storage_bytes','disk_reserve_bytes','max_download_bytes',
                 'max_process_rss_bytes','max_aggregate_rss_bytes','stage_timeout_seconds',
                 'min_available_memory_bytes']:
        value=limits[name]
        if isinstance(value,bool) or not isinstance(value,int) or value<=0:
            raise ValueError(f'Resource limits must be positive integers: {name}')
    if limits['max_workers']>4:
        raise ValueError('The authorized initial worker ceiling is four')
    if limits['max_new_storage_bytes']>10_000_000_000 or limits['disk_reserve_bytes']<4_000_000_000:
        raise ValueError('The project requires at most 10 GB new storage and at least 4 GB free reserve')
    if max(limits['max_process_rss_bytes'],limits['max_aggregate_rss_bytes'])>8_000_000_000:
        raise ValueError('The local workflow must stay within the 8 GB memory ceiling')
    return config


def fingerprint(root, config_path):
    root, config_path = Path(root), Path(config_path)
    paths = [config_path, root/'data/manifests/inputs.json']
    if (root/'requirements.txt').is_file(): paths.append(root/'requirements.txt')
    for directory in ['src','scripts','tests']:
        paths.extend(sorted(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts))
    for row in json.loads((root/'data/manifests/inputs.json').read_text()):
        path = root/row['path']
        if path.exists():
            paths.append(path)
    h = hashlib.sha256()
    h.update(json.dumps(runtime_identity(), sort_keys=True).encode('utf-8'))
    for path in paths:
        try:
            label = path.relative_to(root).as_posix()
        except ValueError:
            label = 'external_config' if path == config_path else path.name
        h.update(label.encode())
        h.update(digest(path).encode())
    return h.hexdigest()


def validate(root,config,guard=None):
    guard=guard or Guard(root,config)
    path=root/'results/reports/validation.log'
    summary_path=root/'results/reports/validation_summary.json'
    summary_path.unlink(missing_ok=True)
    code=monitored_run([sys.executable,str(root/'scripts/validate.py')],root,path,guard)
    log=path.read_text(encoding='utf-8')
    if code:
        raise RuntimeError('Validation failed; see results/reports/validation.log\n'+log[-5000:])
    summary=json.loads(summary_path.read_text(encoding='utf-8'))
    if not summary.get('success') or summary.get('tests_run',0)<1:
        raise RuntimeError('Validation did not produce a successful nonempty test suite')
    return {'status':'passed','test_log':'results/reports/validation.log',
            'scope':'software_tests_not_reexecution_of_scientific_stages',**summary}


def validate_only(root,config,guard):
    """Read-only scientific inputs plus separately written test diagnostics."""
    from .acquisition import verify_cached_inputs
    return {'input_verification':verify_cached_inputs(root,config,guard),
            'validation':validate(root,config,guard)}


def dispatch(stage, root, config, guard, offline):
    from . import audit
    if stage == STAGES[0]:
        paths = json.loads((root/'data/manifests/inputs.json').read_text())
        result = {'public_inputs':len(paths),'gate':'restricted_analysis',
                  'reference_review':'docs/reference_repository_review.md',
                  'processed_virome_inputs':0}
        write_json(root/'results/reports/source_audit.json',result)
        return result
    if stage == STAGES[1]:
        from .acquisition import fetch
        result = fetch(root,config,guard,offline)
        result.update(audit.source_audit(root,config))
        return result
    if stage == STAGES[2]:
        from .samples import audit as sample_audit
        return sample_audit(root,config)
    if stage == STAGES[3]:
        return audit.virome_qc(root,config)
    if stage == STAGES[4]:
        return audit.eligibility(root,config)
    if stage == STAGES[5]:
        from .immune import prepare
        return prepare(root,config)
    if stage == STAGES[6]:
        from .immune import analyze
        from .original_methods import run as replicate_original
        result=analyze(root,config)
        result['original_method_reconstruction']=replicate_original(root,config)
        audit.association_gate(root,config)
        return result
    if stage == STAGES[7]:
        return audit.bacteriome_gate(root,config)
    if stage == STAGES[8]:
        result=validate(root,config,guard)
        # Run the benchmark after the validation child exits, keeping concurrent
        # memory low on the researcher's machine.
        from .calibration import run as calibrate_software
        result['synthetic_software_calibration']=calibrate_software(root,config)
        from .reporting import summarize
        summarize(root,config)
        return result
    if stage == STAGES[9]:
        from .figures import generate
        return generate(root,config)
    raise ValueError(stage)


def outputs(root):
    return {str(p.relative_to(root)):digest(p) for folder in ['data/processed','results/tables','results/reports','figures']
            for p in (root/folder).rglob('*') if p.is_file() and not any(x in p.parts for x in ['stages','logs'])
            and p.name not in ['run_status.json','resource_usage.json']}


def stage_entry(stage):
    parser=argparse.ArgumentParser()
    parser.add_argument('--config',default='config/analysis.yaml')
    parser.add_argument('--offline',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    try:
        configure_environment(root)
        config_path=(root/args.config).resolve()
        config=load_config(config_path)
        guard=Guard(root,config)
        dependencies=upstream_hashes(root,stage)
        result=dispatch(stage,root,config,guard,args.offline)
        changed={p:digest(root/p) for p in DECLARED[stage]}
        result=result or {}
        record={'schema_version':2,'stage':stage,'result':result,'resources':guard.check(),
                'outputs':changed,'upstream_outputs':dependencies,
                'fingerprint':fingerprint(root,config_path)}
        write_json(root/f'results/reports/stages/{stage}.json',record)
        print(json.dumps(record,allow_nan=False))
    except Exception as exc:
        print(f'{stage}: {type(exc).__name__}: {exc}',file=sys.stderr)
        traceback.print_exc()
        raise SystemExit(1)


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--config',default='config/analysis.yaml')
    parser.add_argument('--threads',type=int,default=4)
    parser.add_argument('--mode',choices=['pilot','full'],default='full')
    parser.add_argument('--offline',action='store_true')
    parser.add_argument('--resume',action='store_true')
    parser.add_argument('--validate-only',action='store_true')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[2]
    config_path=(root/args.config).resolve()
    for folder in ['results/reports/stages','results/reports/logs','results/tables','data/processed','figures']:
        (root/folder).mkdir(parents=True,exist_ok=True)
    now=datetime.now(timezone.utc)
    invocation_id=now.strftime('%Y%m%dT%H%M%S%fZ')+'_'+str(os.getpid())
    status={'invocation_id':invocation_id,'mode':'validation' if args.validate_only else args.mode,
            'offline':args.offline,'resume_requested':args.resume,'requested_threads':args.threads,
            'actual_workers':1,'started_utc':now.isoformat(),'stages':[],'status':'running',
            'scientific_stages_executed':0,'scientific_stages_resumed_verified':0,
            'runtime':runtime_identity()}
    def save_status():
        write_json(root/'results/reports/run_status.json',status)
        write_json(root/f'results/reports/invocations/{invocation_id}.json',status)
    save_status()
    started=time.monotonic()
    guard=None; config=None; usage={}; peak=peak_rss(); active_stage=None
    try:
        configure_environment(root)
        config=load_config(config_path)
        if not 1 <= args.threads <= config['resources']['max_workers']:
            raise ValueError(f"threads must be between 1 and {config['resources']['max_workers']}; execution is serial")
        status['seed']=config['seed']
        current_environment=runpy.run_path(str(root/'scripts/environment_probe.py'))['probe'](root)
        write_json(root/'data/manifests/environment_local.json',current_environment)
        guard=Guard(root,config)
        if args.validate_only:
            # Verification must not extract metadata, fetch missing inputs or
            # write scientific source/processed tables, even without --offline.
            status.update(validate_only(root,config,guard))
            peak=max(peak,status['validation'].get('peak_rss_bytes',0))
            status['status']='completed_validation'
            status['validation_scope']='cached_frozen_inputs_and_software_tests_only'
        else:
            selected=STAGES[:6] if args.mode=='pilot' else STAGES
            for stage in selected:
                active_stage=stage
                guard.check()
                dependencies=upstream_hashes(root,stage)
                stamp=root/f'results/reports/stages/{stage}.json'
                key=fingerprint(root,config_path)
                try:
                    old=json.loads(stamp.read_text(encoding='utf-8')) if stamp.exists() else {}
                except (ValueError,OSError):
                    old={}
                if args.resume and cache_valid(root,stage,old,key,dependencies):
                    record=old; state='resumed_verified'
                    status['scientific_stages_resumed_verified']+=1
                else:
                    cmd=[sys.executable,str(root/f'scripts/{stage}.py'),'--config',str(config_path)]
                    if args.offline: cmd.append('--offline')
                    log_path=root/f'results/reports/logs/{stage}.log'
                    code=monitored_run(cmd,root,log_path,guard)
                    if code:
                        raise RuntimeError(f'{stage} failed. '+log_path.read_text(encoding='utf-8')[-3000:])
                    record=json.loads(stamp.read_text(encoding='utf-8'))
                    # Child records must obey the same declared-output and
                    # dependency contract as cache records.
                    if not cache_valid(root,stage,record,fingerprint(root,config_path),dependencies):
                        raise RuntimeError(f'{stage} produced an invalid stage record')
                    state='completed'; status['scientific_stages_executed']+=1
                    peak=max(peak,record['resources']['process_peak_rss_bytes'])
                    if stage==STAGES[8]:
                        peak=max(peak,record['result'].get('peak_rss_bytes',0))
                status['stages'].append({'name':stage,'status':state,'result':record['result'],
                    'recorded_peak_rss_bytes':record['resources']['process_peak_rss_bytes'],
                    'resource_scope':'historical_cached_stage' if state=='resumed_verified' else 'measured_this_invocation'})
                save_status(); print(f'{stage}: {state}',flush=True)
            status['status']='completed_pilot' if args.mode=='pilot' else 'completed_restricted_analysis'
        usage=guard.check()
        peak=max(peak,usage.get('max_observed_native_process_peak_rss_bytes',0),peak_rss())
        status['max_measured_stage_peak_rss_bytes']=peak
    except BaseException as exc:
        status['status']='interrupted' if isinstance(exc,KeyboardInterrupt) else 'failed'
        status['failed_stage']=active_stage
        status['error_type']=type(exc).__name__; status['error']=str(exc)
        raise
    finally:
        status['elapsed_seconds']=round(time.monotonic()-started,3)
        status['finished_utc']=datetime.now(timezone.utc).isoformat()
        if guard is not None:
            try:
                usage=guard.check()
            except Exception as exc:
                usage['snapshot_error']=str(exc)
            peak=max(peak,guard.max_observed_native_process_peak_rss_bytes,peak_rss())
        usage['max_measured_stage_peak_rss_bytes']=peak
        usage['invocation_id']=invocation_id
        usage['scope']='current invocation; native per-process peaks and separately sampled concurrent process-family RSS'
        status['max_measured_stage_peak_rss_bytes']=peak
        save_status()
        write_json(root/'results/reports/resource_usage.json',usage)
        if config is not None:
            from .reporting import resource_report
            try:
                resource_report(root,usage,invocation=status,config=config)
            except Exception as report_error:
                status['report_error']=str(report_error)
                if status['status'] not in ('failed','interrupted'):
                    status['status']='failed'; status['error_type']=type(report_error).__name__
                    status['error']=str(report_error); save_status()
                    raise
                save_status()  # Preserve the original failure, not a reporting error.
    print(json.dumps({'invocation_id':invocation_id,'status':status['status']}),flush=True)

