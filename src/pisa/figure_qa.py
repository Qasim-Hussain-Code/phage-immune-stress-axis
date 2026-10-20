"""Artifact integrity for recorded visual review and optional fresh PDF renders.

Rendering does not constitute visual approval. A render manifest is evidence of
rendering only; the tracked review manifest records an actual image inspection.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import sys
from .io import digest,write_json


def review_status(root):
    root=Path(root)
    manifest_path=root/'data/manifests/figure_qa.json'
    if not manifest_path.is_file():
        return {'status':'unverified','reason':'No recorded visual review manifest','matched':0,'figures':[]}
    manifest=json.loads(manifest_path.read_text(encoding='utf-8'))
    records=[]
    for row in manifest.get('figures',[]):
        path=root/row['path']
        if not path.resolve().is_relative_to(root.resolve()):
            raise ValueError('Figure review path leaves workspace')
        matches=path.is_file() and digest(path)==row['sha256']
        records.append({'path':row['path'],'hash_matches_reviewed_pdf':matches,
                        'recorded_visual_status':row.get('visual_status','unverified')})
    current={p.relative_to(root).as_posix() for p in (root/'figures').glob('*.pdf')}
    recorded={r['path'] for r in records}
    passed=bool(records) and current==recorded and all(
        r['hash_matches_reviewed_pdf'] and r['recorded_visual_status']=='passed' for r in records)
    return {'status':'previous_review_matches_current_files' if passed else 'unverified_current_files',
            'reviewed_utc':manifest.get('reviewed_utc'),
            'matched':sum(r['hash_matches_reviewed_pdf'] for r in records),
            'unreviewed_current_pdfs':sorted(current-recorded),'figures':records,
            'scope':'Hash agreement with previously rendered and visually inspected PDFs; no new visual review performed by this check'}


def render_for_review(root,output,renderer_path=None,scale=1.5,guard=None):
    root=Path(root).resolve();output=Path(output).resolve()
    if not output.is_relative_to(root):
        raise ValueError('Render output must be inside the workspace')
    if not 0<scale<=4:
        raise ValueError('Render scale must be in (0,4]')
    if renderer_path:
        sys.path.insert(0,str(Path(renderer_path).resolve()))
    try:
        import pypdfium2 as pdfium
    except ImportError as exc:
        raise RuntimeError('Optional pypdfium2 renderer is unavailable; install it in an audited environment or use the workspace QA cache') from exc
    output.mkdir(parents=True,exist_ok=True)
    records=[]
    for path in sorted((root/'figures').glob('*.pdf')):
        if guard:guard.check()
        document=pdfium.PdfDocument(path)
        try:
            for page_index in range(len(document)):
                page=document[page_index]
                bitmap=page.render(scale=scale)
                try:
                    picture=bitmap.to_pil()
                    png=output/f'{path.stem}_page{page_index+1}.png'
                    picture.save(png)
                    records.append({'pdf':path.relative_to(root).as_posix(),'pdf_sha256':digest(path),
                                    'page':page_index+1,'png':png.relative_to(root).as_posix(),
                                    'png_sha256':digest(png),'pixels':list(picture.size)})
                    picture.close()
                finally:
                    bitmap.close();page.close()
        finally:
            document.close()
    result={'schema_version':1,'rendered_utc':datetime.now(timezone.utc).isoformat(),
            'status':'rendered_for_visual_review','scale':scale,'records':records,
            'note':'Rendering alone does not mark visual QA as passed'}
    write_json(output/'render_manifest.json',result)
    return result
