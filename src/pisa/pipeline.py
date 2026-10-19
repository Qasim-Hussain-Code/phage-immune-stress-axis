"""Sequential, resumable runner with explicit scientific exclusion statuses."""
import argparse
from datetime import datetime, timezone
import hashlib
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
 STAGES[6]:['results/tables/immune_contrasts.csv','results/tables/immune_sensitivity.csv','results/tables/immune_summary.csv','results/reports/phage_immune_associations.md'],
 STAGES[7]:['results/reports/bacteriome_integration.md'],
 STAGES[8]:['results/reports/validation.log','results/reports/validation_summary.json','docs/results.md'],
 STAGES[9]:[f'figures/{name}.{ext}' for name in ['figure1_design','figure4_immune','figure5_linkage_limit','figure7_robustness'] for ext in ['png','pdf']]+[f'results/tables/figure{n}_data.csv' for n in [1,4,5,7]]}


def load_config(path):
    import yaml
    config = yaml.safe_load(Path(path).read_text(encoding='utf-8'))
    fixed = ['ly6chi_monocytes', 'ly6chi_monocytes_cd62', 'tnfa_splenocyte_unstimulated']
    if config['immune']['endpoints'] != fixed:
        raise ValueError('Endpoint changes require an updated analysis plan and test family')
    if config['immune']['confidence_level'] != 0.95:
        raise ValueError('The fixed analysis plan uses pointwise 95% intervals')
    return config


def fingerprint(root, config_path):
    paths = [config_path, root/'data/manifests/inputs.json']
    for directory in ['src','scripts','tests']:
        paths.extend(sorted(p for p in (root/directory).rglob('*') if p.is_file() and '__pycache__' not in p.parts))
    for row in json.loads((root/'data/manifests/inputs.json').read_text()):
        path = root/row['path']
        if path.exists():
            paths.append(path)
    h = hashlib.sha256()
    for path in paths:
        h.update(str(path.relative_to(root)).encode())
        h.update(digest(path).encode())
    return h.hexdigest()


def validate(root,config):
    guard=Guard(root,config)
    path=root/'results/reports/validation.log'
    code=monitored_run([sys.executable,str(root/'scripts/validate.py')],root,path,guard)
    log=path.read_text(encoding='utf-8')
    if code:
        raise RuntimeError('Validation failed; see results/reports/validation.log\n'+log[-5000:])
    return {'status':'passed','test_log':'results/reports/validation.log'}


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
        result=analyze(root,config)
        audit.association_gate(root,config)
        return result
    if stage == STAGES[7]:
        return audit.bacteriome_gate(root,config)
    if stage == STAGES[8]:
        result=validate(root,config)
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
    config=load_config(root/args.config)
    guard=Guard(root,config)
    try:
        result=dispatch(stage,root,config,guard,args.offline)
        changed={p:digest(root/p) for p in DECLARED[stage]}
        result=result or {}
        record={'stage':stage,'result':result,'resources':guard.check(),'outputs':changed}
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
    config=load_config(config_path)
    if not 1 <= args.threads <= config['resources']['max_workers']:
        parser.error('threads must be between 1 and 4; this small workflow executes serially')
    os.environ.update({name:'1' for name in ['OMP_NUM_THREADS','OPENBLAS_NUM_THREADS','MKL_NUM_THREADS','NUMEXPR_NUM_THREADS']})
    for folder in ['results/reports/stages','results/reports/logs','results/tables','data/processed','figures']:
        (root/folder).mkdir(parents=True,exist_ok=True)
    # Preserve the original run's initial probe, and measure a fresh local probe
    # for a new checkout rather than inheriting the researcher's machine budget.
    env_path=root/'data/manifests/environment_initial.json'
    if not env_path.exists():
        subprocess.run([sys.executable,str(root/'scripts/environment_probe.py')],cwd=root,check=True)
    current_environment=runpy.run_path(str(root/'scripts/environment_probe.py'))['probe'](root)
    write_json(root/'data/manifests/environment_local.json',current_environment)
    guard=Guard(root,config)
    if args.validate_only:
        from .acquisition import fetch
        fetch(root,config,guard,args.offline)
        print(json.dumps(validate(root,config)))
        return
    selected=STAGES[:6] if args.mode=='pilot' else STAGES
    status={'mode':args.mode,'offline':args.offline,'requested_threads':args.threads,
            'actual_workers':1,'seed':config['seed'],'started_utc':datetime.now(timezone.utc).isoformat(),
            'stages':[],'status':'running'}
    started=time.monotonic()
    peak=peak_rss()
    for stage in selected:
        guard.check()
        stamp=root/f'results/reports/stages/{stage}.json'
        key=fingerprint(root,config_path)
        old=json.loads(stamp.read_text()) if stamp.exists() else {}
        if args.resume and old.get('fingerprint')==key and old.get('outputs') and all(
                (root/p).exists() and digest(root/p)==h for p,h in old['outputs'].items()):
            record=old
            state='resumed_verified'
        else:
            cmd=[sys.executable,str(root/f'scripts/{stage}.py'),'--config',str(config_path)]
            if args.offline: cmd.append('--offline')
            log_path=root/f'results/reports/logs/{stage}.log'
            code=monitored_run(cmd,root,log_path,guard)
            if code:
                status['status']='failed'
                status['failed_stage']=stage
                write_json(root/'results/reports/run_status.json',status)
                raise RuntimeError(f'{stage} failed. '+log_path.read_text(encoding='utf-8')[-3000:])
            record=json.loads(stamp.read_text())
            record['fingerprint']=fingerprint(root,config_path)
            write_json(stamp,record)
            state='completed'
        peak=max(peak,record['resources']['process_peak_rss_bytes'])
        status['stages'].append({'name':stage,'status':state,'result':record['result'],
                                 'peak_rss_bytes':record['resources']['process_peak_rss_bytes']})
        write_json(root/'results/reports/run_status.json',status)
        print(f'{stage}: {state}',flush=True)
    status['status']='completed_pilot' if args.mode=='pilot' else 'completed_restricted_analysis'
    status['elapsed_seconds']=round(time.monotonic()-started,3)
    status['max_measured_stage_peak_rss_bytes']=peak
    write_json(root/'results/reports/run_status.json',status)
    validation_path=root/'results/reports/validation_summary.json'
    if validation_path.exists():
        peak=max(peak,json.loads(validation_path.read_text())['peak_rss_bytes'])
        status['max_measured_stage_peak_rss_bytes']=peak
        write_json(root/'results/reports/run_status.json',status)
    usage=guard.check()
    usage['max_measured_stage_peak_rss_bytes']=peak
    usage['scope']='maximum native process peak among stages, runner and validation child; not aggregate simultaneous system memory'
    write_json(root/'results/reports/resource_usage.json',usage)
    from .reporting import resource_report
    resource_report(root,usage)

