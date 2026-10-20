"""Frozen, bounded public downloads and deterministic extraction."""
import csv
import json
from pathlib import Path
import re
import urllib.request
from urllib.parse import urlparse
import xml.etree.ElementTree as ET
from .io import digest, read_csv, write_csv


def load_manifest(root,config):
    """Validate the frozen input contract before touching a destination."""
    root=Path(root).resolve()
    manifest=json.loads((root/'data/manifests/inputs.json').read_text(encoding='utf-8'))
    if not isinstance(manifest,list) or not manifest:
        raise ValueError('Input manifest must be a nonempty list')
    seen=set()
    for source in manifest:
        if not isinstance(source,dict):
            raise ValueError('Invalid source record')
        relative=source.get('path')
        if not isinstance(relative,str) or not relative or Path(relative).is_absolute():
            raise ValueError('Input paths must be nonempty relative paths')
        path=(root/relative).resolve()
        if not path.is_relative_to(root) or path==root or path in seen:
            raise ValueError('Input paths must be unique and remain inside the project')
        seen.add(path)
        if not re.fullmatch('[0-9a-f]{64}',str(source.get('sha256',''))):
            raise ValueError('Every input requires a SHA-256 digest')
        cap=source.get('max_bytes')
        if isinstance(cap,bool) or not isinstance(cap,int) or cap<=0:
            raise ValueError('Input download caps must be positive integers')
        parsed=urlparse(source.get('url',''))
        if parsed.scheme!='https' or not parsed.hostname or parsed.username or parsed.password:
            raise ValueError('Public source URLs must use HTTPS without embedded credentials')
        if source.get('transformation') not in [None,'zenodo_catalog']:
            raise ValueError('Unrecognized input transformation')
    return manifest


def verify_cached_inputs(root,config,guard):
    """Read-only cache verification: no retrieval, extraction or scientific writes."""
    root=Path(root)
    checks=[]
    for source in load_manifest(root,config):
        guard.check()
        path=root/source['path']
        if not path.is_file():
            raise FileNotFoundError(f'Cached input missing: {source["path"]}; source: {source["url"]}')
        if source.get('bytes') is not None and path.stat().st_size!=source['bytes']:
            raise ValueError(f'Frozen input size mismatch: {source["path"]}')
        if digest(path)!=source['sha256']:
            raise ValueError(f'Checksum mismatch in frozen input: {source["path"]}')
        checks.append({'path':source['path'],'status':'verified_cache','sha256':source['sha256']})
    return {'status':'verified','verified_inputs':len(checks),'checks':checks,
            'downloads':0,'scientific_files_written':0}


def normalize_zenodo(payload):
    record=json.loads(payload.decode('utf-8-sig'))
    files=record['files']
    files=list(files.values()) if isinstance(files,dict) else files
    selected={'id':record['id'], 'title':record['metadata']['title'],
              'license':record['metadata'].get('license'),
              'files':[{'key':f.get('key',f.get('filename','')), 'size':f['size'],
                        'checksum':f.get('checksum','')} for f in files]}
    selected['files'].sort(key=lambda f:f['key'])
    return (json.dumps(selected,sort_keys=True,indent=2,ensure_ascii=False)+'\n').encode('utf-8')


def fetch(root, config, guard, offline=False):
    manifest = load_manifest(root,config)
    checks = []
    for source in manifest:
        path = root/source['path']
        if path.exists():
            if digest(path) != source['sha256']:
                raise ValueError(f'Checksum mismatch in frozen input: {source["path"]}')
            checks.append({'path': source['path'], 'status': 'verified_cache', 'sha256': source['sha256']})
            continue
        if offline:
            raise FileNotFoundError(f'Offline input missing: {source["path"]}; source: {source["url"]}')
        cap = min(config['resources']['max_download_bytes'], source['max_bytes'])
        guard.check(cap)
        path.parent.mkdir(parents=True, exist_ok=True)
        part = path.with_suffix(path.suffix+'.part')
        try:
            request = urllib.request.Request(source['url'], headers={'User-Agent': 'pisa-research-audit/0.1'})
            with urllib.request.urlopen(request, timeout=60) as response, part.open('wb') as stream:
                length = response.headers.get('Content-Length')
                if length and int(length) > cap:
                    raise ValueError(f'Oversized download rejected: {source["url"]}')
                count = 0
                while True:
                    chunk = response.read(min(65536, cap-count+1))
                    if not chunk:
                        break
                    count += len(chunk)
                    if count > cap:
                        raise ValueError('Streaming download size limit exceeded')
                    stream.write(chunk)
                    guard.check()
            if source.get('transformation')=='zenodo_catalog':
                part.write_bytes(normalize_zenodo(part.read_bytes()))
            if digest(part) != source['sha256']:
                raise ValueError(f'Public input changed: {source["url"]}; frozen hash {source["sha256"]}')
            part.replace(path)
        finally:
            part.unlink(missing_ok=True)
        checks.append({'path': source['path'], 'status': 'downloaded_verified', 'sha256': source['sha256']})
    write_csv(root/'results/tables/input_integrity.csv', checks)
    extract_metadata(root)
    return {'verified_inputs': len(checks), 'offline': offline, 'raw_reads_downloaded': 0}


def extract_metadata(root):
    source = root/'data/raw/ritz2024_archive/PRJNA970614_samples.xml'
    rows = []
    fields = ['sample_accession', 'sample_alias']
    for sample in ET.parse(source).getroot().iter('SAMPLE'):
        row = {'sample_accession': sample.attrib['accession'], 'sample_alias': sample.attrib.get('alias','')}
        for attribute in sample.findall('./SAMPLE_ATTRIBUTES/SAMPLE_ATTRIBUTE'):
            tag = attribute.findtext('TAG')
            row[tag] = attribute.findtext('VALUE','')
            if tag not in fields:
                fields.append(tag)
        rows.append(row)
    write_csv(root/'data/raw/ritz2024_archive/PRJNA970614_sample_attributes.csv', rows, fields)
    return len(rows)
