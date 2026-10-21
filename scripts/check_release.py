"""Check scientific lineage, execution evidence, artifact review and Git payloads."""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.io import read_csv,digest,write_json,code_digest
from pisa.figure_qa import review_status


def require(condition,message):
    if not condition:
        raise ValueError(message)


def _invocation_record(path):
    """Read one canonical journal record, without trusting filesystem times."""
    try:
        record=json.loads(path.read_text(encoding='utf-8'))
    except (OSError,ValueError) as exc:
        raise ValueError(f'Unreadable or malformed invocation record: {path.name}') from exc
    require(isinstance(record,dict),'Invocation record must be a JSON object: '+path.name)
    identifier=record.get('invocation_id')
    require(isinstance(identifier,str) and re.fullmatch(r'[A-Za-z0-9_-]{1,128}',identifier) is not None,
            'Unsafe or missing invocation ID: '+path.name)
    started=record.get('started_utc')
    require(isinstance(started,str),'Invocation needs an ISO start timestamp: '+path.name)
    try:
        timestamp=datetime.fromisoformat(started)
        require(timestamp.tzinfo is not None and timestamp.utcoffset() is not None,
                'Invocation start timestamp must be timezone-aware: '+path.name)
        timestamp=timestamp.astimezone(timezone.utc)
    except (ValueError,OverflowError) as exc:
        raise ValueError('Invalid timezone-aware invocation start timestamp: '+path.name) from exc
    require(record.get('status') in {'running','failed','interrupted','completed_validation',
                'completed_pilot','completed_restricted_analysis'},
            'Unknown or missing invocation status: '+path.name)
    return record,timestamp


def verify_latest_invocation(root):
    """Reject stale latest-success records and incomplete or malformed journals.

    A latest record must equal its canonical per-invocation counterpart in full.
    Every persisted JSON attempt must be valid; any newer or simultaneous other
    attempt makes an older latest record insufficient proof, regardless of its
    outcome. Only aware ISO start times are compared, never file mtimes.
    """
    root=Path(root).resolve()
    latest,started=_invocation_record(root/'results/reports/run_status.json')
    directory=root/'results/reports/invocations'
    require(directory.is_dir() and directory.resolve().is_relative_to(root),
            'Missing or unsafe per-invocation journal directory')
    counterpart=directory/(latest['invocation_id']+'.json')
    require(counterpart.is_file(),'Latest status has no per-invocation counterpart')
    require(counterpart.resolve().is_relative_to(directory.resolve()),
            'Unsafe latest-status counterpart path')
    counterpart_record,counterpart_started=_invocation_record(counterpart)
    require(counterpart_record==latest and counterpart_started==started,
            'Latest status differs from its per-invocation counterpart')
    records=sorted(directory.glob('*.json'))
    require(bool(records),'Per-invocation journal contains no JSON records')
    for path in records:
        require(path.is_file() and path.resolve().is_relative_to(directory.resolve()),
                'Unsafe per-invocation record path: '+path.name)
        record,timestamp=_invocation_record(path)
        require(path.name==record['invocation_id']+'.json',
                'Invocation filename and record ID disagree: '+path.name)
        if record['invocation_id']!=latest['invocation_id']:
            require(timestamp<started,
                    'A newer or simultaneous persisted invocation makes the latest-status proof stale: '+record['invocation_id'])
    return latest


def git_files(root,scope):
    prefix=['git','-c',f'safe.directory={root.as_posix()}']
    repo=subprocess.run(prefix+['rev-parse','--git-dir'],cwd=root,capture_output=True)
    if repo.returncode:
        require(scope=='working','Index/HEAD checks require a Git checkout')
        return [p.relative_to(root).as_posix() for p in root.rglob('*') if p.is_file()
                and not any(x in p.relative_to(root).parts for x in ['.git','.cache','__pycache__','tmp'])]
    args=['ls-tree','-rz','--name-only','HEAD'] if scope=='head' else ['ls-files','-z']
    result=subprocess.run(prefix+args,cwd=root,capture_output=True,check=True)
    files=[p for p in result.stdout.decode('utf-8').split('\0') if p]
    if scope=='working':
        extra=subprocess.run(prefix+['ls-files','--others','--exclude-standard','-z'],cwd=root,capture_output=True,check=True)
        files.extend(p for p in extra.stdout.decode('utf-8').split('\0') if p)
    return sorted(set(files))


def read_payload(root,path,scope):
    if scope=='working':return (root/path).read_bytes()
    spec=('HEAD:' if scope=='head' else ':')+path
    return subprocess.run(['git','-c',f'safe.directory={root.as_posix()}','show',spec],
                          cwd=root,capture_output=True,check=True).stdout


def verify_payload_consistency(root,scope):
    """The tested working science must be the science selected for release."""
    if scope=='working':return 0
    prefixes=('src/','scripts/','tests/','config/','data/raw/','data/processed/',
              'results/tables/','figures/')
    exact={'requirements.txt','data/manifests/inputs.json','data/manifests/figure_qa.json'}
    working={p for p in git_files(root,'working') if p.startswith(prefixes) or p in exact}
    selected={p for p in git_files(root,scope) if p.startswith(prefixes) or p in exact}
    require(working==selected,'Release code/scientific file inventory differs from the working reference')
    text_suffixes={'.py','.md','.json','.yaml','.yml','.txt','.csv','.tsv','.toml'}
    for name in sorted(working):
        actual=(root/name).read_bytes(); released=read_payload(root,name,scope)
        # Git's configured LF normalization is permitted for project text only.
        # Frozen upstream data, figures and binary files require exact bytes.
        normalize=not name.startswith('data/raw/') and Path(name).suffix.lower() in text_suffixes
        if normalize:
            actual=actual.replace(b'\r\n',b'\n');released=released.replace(b'\r\n',b'\n')
        require(actual==released,f'Release payload differs from tested working file: {name}')
    return len(working)


def verify_frozen_inputs(root,scope='working'):
    """Apply the acquisition contract to working and selected Git input bytes."""
    from pisa.acquisition import load_manifest,verify_input_file
    root=Path(root).resolve()
    manifest=load_manifest(root)
    for entry in manifest:
        verify_input_file(root/entry['path'],entry)
        if scope!='working':
            payload=read_payload(root,entry['path'],scope)
            require(len(payload)==entry['bytes'],f'Frozen input size differs in Git {scope}: '+entry['path'])
            require(hashlib.sha256(payload).hexdigest()==entry['sha256'],
                    f'Frozen input bytes differ in Git {scope}: '+entry['path'])
    return manifest


def check(root,scope='working',require_review=True):
    root=Path(root).resolve()
    payload_files=verify_payload_consistency(root,scope)
    manifest=verify_frozen_inputs(root,scope)

    from pisa.immune import parse_workbook,ENDPOINTS,CONTRASTS
    prepared=read_csv(root/'data/processed/immune_long.csv')
    source_rows,_=parse_workbook(root/'data/raw/source_data.xlsx')
    source={(r['mouse_id'],r['endpoint']):r for r in source_rows}
    require(len(prepared)==len(source),'Prepared phenotype row count differs from source')
    require(len({(r['mouse_id'],r['endpoint']) for r in prepared})==len(prepared),'Duplicate prepared phenotype key')
    for row in prepared:
        reference=source.get((row['mouse_id'],row['endpoint']))
        require(reference is not None,'Prepared phenotype has no source-cell observation')
        require(row['source_cell']==reference['source_cell'] and row['source_sheet']==reference['source_sheet'],
                'Source-cell lineage differs')
        require(row['observation_status']==reference['observation_status'],'Missingness changed during preparation')
        if row['observation_status']=='observed':
            require(float(row['value'])==reference['value'],'Prepared value differs from source workbook')
        else:require(row['value']=='','A missing source cell was filled')

    summary=json.loads((root/'results/reports/sample_audit_summary.json').read_text(encoding='utf-8'))
    require(summary['verified_virome_immune_matches']==0,'The current gate has no verified processed viral input contract')
    require(summary['workbook_animal_rows']==len({r['mouse_id'] for r in prepared}),'Source animal inventory differs')
    linkage=read_csv(root/'results/tables/sample_linkage_audit.csv')
    for row in linkage:
        if row['sample_type'] in ['pooled_fecal_virome','transplant_inoculum']:
            require(not row['mouse_id'] and not row['metadata_candidate_mouse_id'],'A pool or inoculum was assigned to an individual')

    contrasts=read_csv(root/'results/tables/immune_contrasts.csv')
    require(len(contrasts)==len(ENDPOINTS)*len(CONTRASTS),'Unexpected inferential family size')
    for row in contrasts:
        a=[float(x['value']) for x in prepared if x['experiment_id']=='study_ii' and x['endpoint']==row['endpoint']
           and x['group']==row['first_group'] and x['observation_status']=='observed']
        b=[float(x['value']) for x in prepared if x['experiment_id']=='study_ii' and x['endpoint']==row['endpoint']
           and x['group']==row['second_group'] and x['observation_status']=='observed']
        require(len(a)==int(row['n_first']) and len(b)==int(row['n_second']),'Contrast sample counts differ from observed source cells')
        require(abs(sum(a)/len(a)-sum(b)/len(b)-float(row['mean_difference']))<1e-10,'Contrast effect differs from independent source sum')

    validation=json.loads((root/'results/reports/validation_summary.json').read_text(encoding='utf-8'))
    require(validation.get('success') and validation.get('tests_run',0)>0,'No successful executed validation record')
    require(validation.get('code_sha256')==code_digest(root),'Code or test fixtures changed after the executed validation suite')
    status=verify_latest_invocation(root)
    require(status.get('status')=='completed_restricted_analysis','Latest invocation did not complete the full restricted analysis')
    from pisa.pipeline import STAGES,cache_valid,fingerprint,upstream_hashes
    key=fingerprint(root,root/'config/analysis.yaml')
    for stage in STAGES:
        record=json.loads((root/f'results/reports/stages/{stage}.json').read_text(encoding='utf-8'))
        require(cache_valid(root,stage,record,key,upstream_hashes(root,stage)),
                'Current scientific output contract is stale: '+stage)
    qa=review_status(root)
    if require_review:require(qa['status']=='previous_review_matches_current_files','Current PDF bytes lack a matching recorded visual review')

    from pypdf import PdfReader
    pdfs=sorted((root/'figures').glob('*.pdf'))
    require(bool(pdfs),'No PDF figures generated')
    for path in pdfs:
        reader=PdfReader(path)
        require(len(reader.pages)==1 and reader.pages[0].extract_text().strip(),'Empty or unexpected figure PDF: '+path.name)
        require(path.with_suffix('.png').is_file(),'Missing PNG companion: '+path.name)
    require(read_csv(root/'results/tables/figure4_data.csv')==[
        r for r in prepared if r['experiment_id']=='study_ii' and r['endpoint'] in ENDPOINTS],
        'Figure 4 observations differ from source-verified selected phenotype rows')

    files=git_files(root,scope)
    large=[];suspects=[]
    patterns=[re.compile(x) for x in [r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',
              r'AKIA[0-9A-Z]{16}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']]
    text_suffixes={'.py','.md','.json','.yaml','.yml','.txt','.csv','.tsv','.cff','.xml','.toml'}
    for name in files:
        payload=read_payload(root,name,scope)
        if len(payload)>5_000_000:large.append(name)
        if Path(name).suffix.lower() in text_suffixes:
            text=payload.decode('utf-8-sig',errors='replace')
            if any(p.search(text) for p in patterns):suspects.append(name)
    require(not large,'Files over 5 MB in selected release payload: '+', '.join(large))
    require(not suspects,'Potential credential patterns in release payload: '+', '.join(suspects))
    return {'status':'passed','git_scope':scope,'frozen_inputs':len(manifest),'phenotype_cells_verified':len(prepared),
            'contrasts':len(contrasts),'figures':len(pdfs),'matched_virome_immune':0,
            'tests_run':validation['tests_run'],'code_sha256':validation['code_sha256'],
            'release_payload_files_verified':payload_files,
            'invocation_id':status['invocation_id'],'invocation_started_utc':status['started_utc'],
            'files_scanned':len(files),'large_files_over_5MB':large,'credential_pattern_matches':suspects,
            'figure_review':qa['status'],'scope':'Common credential patterns; not a guarantee of complete secret detection'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--git-scope',choices=['working','index','head'],default='working')
    parser.add_argument('--allow-unreviewed-figures',action='store_true',help='For CI: structural checks only; record visual QA as unverified')
    parser.add_argument('--output',help='Optional report path; omitted checks do not modify release records')
    args=parser.parse_args()
    root=Path(__file__).resolve().parents[1]
    result=check(root,args.git_scope,not args.allow_unreviewed_figures)
    if args.output:write_json(root/args.output,result)
    print(json.dumps(result))


if __name__=='__main__':main()
