"""Read-only scientific consistency, tracked-size and credential-pattern checks."""
from pathlib import Path
import csv
import json
import re
import subprocess
import sys
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'src'))
from pisa.io import read_csv,digest,write_json

root=Path(__file__).resolve().parents[1]
for entry in json.loads((root/'data/manifests/inputs.json').read_text()):
    assert digest(root/entry['path'])==entry['sha256'],entry['path']
summary=json.loads((root/'results/reports/sample_audit_summary.json').read_text())
assert summary['principal_specimen_count']==104
assert summary['verified_virome_immune_matches']==0
assert summary['workbook_animal_rows']==50
long=read_csv(root/'data/processed/immune_long.csv')
contrasts=read_csv(root/'results/tables/immune_contrasts.csv')
assert len(contrasts)==6
for row in contrasts:
    a=[float(x['value']) for x in long if x['experiment_id']=='study_ii' and x['endpoint']==row['endpoint'] and x['group']==row['first_group'] and x['observation_status']=='observed']
    b=[float(x['value']) for x in long if x['experiment_id']=='study_ii' and x['endpoint']==row['endpoint'] and x['group']==row['second_group'] and x['observation_status']=='observed']
    assert len(a)==int(row['n_first']) and len(b)==int(row['n_second'])
    assert abs(sum(a)/len(a)-sum(b)/len(b)-float(row['mean_difference']))<1e-10
    for field in ['mean_difference','ci_low','ci_high']:
        assert f'{float(row[field]):.3f}' in (root/'README.md').read_text(encoding='utf-8'),(row['endpoint'],field)
from pypdf import PdfReader
for number,name in [(1,'design'),(4,'immune'),(5,'linkage_limit'),(7,'robustness')]:
    path=root/f'figures/figure{number}_{name}.pdf'
    reader=PdfReader(path)
    assert len(reader.pages)==1 and reader.pages[0].extract_text().strip()
    assert (root/f'figures/figure{number}_{name}.png').stat().st_size>10000
    assert read_csv(root/f'results/tables/figure{number}_data.csv')
tracked=subprocess.run(['git','ls-files','-z'],cwd=root,capture_output=True,check=True).stdout.decode().split('\0')
tracked=[p for p in tracked if p]
if subprocess.run(['git','rev-parse','--verify','HEAD'],cwd=root,capture_output=True).returncode==0:
    # Check staged blobs as well as the working tree, so line-ending conversion
    # cannot silently break frozen inputs in a fresh Linux checkout.
    import hashlib
    for entry in json.loads((root/'data/manifests/inputs.json').read_text()):
        blob=subprocess.run(['git','show',':'+entry['path']],cwd=root,capture_output=True,check=True).stdout
        assert hashlib.sha256(blob).hexdigest()==entry['sha256'],('staged bytes',entry['path'])
large=[];suspects=[]
patterns=[re.compile(x) for x in [r'gh[pousr]_[A-Za-z0-9]{30,}',r'github_pat_[A-Za-z0-9_]{30,}',r'AKIA[0-9A-Z]{16}',r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----']]
for name in tracked:
    path=root/name
    if path.stat().st_size>5_000_000:large.append(name)
    if path.suffix.lower() in ['.py','.md','.json','.yaml','.yml','.txt','.csv','.tsv','.cff','.xml']:
        text=path.read_text(encoding='utf-8-sig',errors='replace')
        if any(p.search(text) for p in patterns):suspects.append(name)
assert not large,large
assert not suspects,suspects
result={'status':'passed','frozen_inputs':10,'contrasts':6,'figures':4,
        'matched_virome_immune':0,'tracked_files_scanned':len(tracked),
        'large_files_over_5MB':large,'credential_pattern_matches':suspects,
        'scope':'common credential patterns, not a guarantee of complete secret detection'}
write_json(root/'results/reports/release_checks.json',result)
print(json.dumps(result))
