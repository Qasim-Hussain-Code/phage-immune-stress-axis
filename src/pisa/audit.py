"""Availability decisions derived from the frozen public evidence."""
import json
import xml.etree.ElementTree as ET
from .io import read_csv, write_csv, write_json


def source_audit(root, config):
    article = ET.parse(root/'data/raw/article.xml').getroot()
    evidence = []
    for section in article.iter('sec'):
        title = section.findtext('title','')
        if title in ['Faecal virome collection and sequencing',
                     'Analysis of total viral sequences within the bulk metagenomic sequencing data',
                     'Flow cytometry', 'Inflammatory cytokine analysis']:
            text = ' '.join(''.join(section.itertext()).split())
            evidence.append({'section_id': section.attrib.get('id',''), 'title': title,
                             'source': 'PMC10847049', 'text': text})
    if len(evidence) < 4:
        raise ValueError('Expected article methods sections missing; re-audit changed input')
    # This is an attributed extraction from the CC BY 4.0 article, not new prose.
    write_csv(root/'results/tables/article_methods_evidence.csv', evidence)
    record = json.loads((root/'data/manifests/zenodo_release.json').read_text(encoding='utf-8'))
    files = record['files']
    files = list(files.values()) if isinstance(files,dict) else files
    rows = [{'name': f.get('key',f.get('filename','')), 'bytes': f.get('size',0),
             'source_record': str(record['id']), 'role':'archived_code_pdf'} for f in files]
    if len(rows) != 1 or not rows[0]['name'].lower().endswith('.pdf'):
        raise ValueError('Archive contents changed; scientific gate must be reviewed')
    write_csv(root/'results/tables/archive_files.csv', rows)
    return {'article_methods_verified': len(evidence), 'archive_files': len(rows),
            'processed_matrices_in_archive': 0, 'gate': 'restricted_analysis'}


def virome_qc(root, config):
    if config['virome']['enable_biological_analysis']:
        raise ValueError('No verified input contract for viral analysis; re-audit required')
    report = '''# Viral data quality and availability

The inspected code release contains a PDF of scripts, not viral abundance or
annotation tables. The source workbook contains phenotype columns. Deposited
sequence metadata are not abundance measurements. Individual bulk-derived
viral profiles existed in the original analysis, but none can be recomputed
from the small retrieved inputs. The following QC fields are therefore
unassessable: feature normalization, all-zero profiles, sequencing-depth effects
on viral composition, contig quality, confident phage classification, prevalence
and annotation coverage. None is silently marked as passed.

The raw archive has pooled, inoculum and recipient samples; see the linkage
audit. No inoculum was assigned to a recipient. No synthetic abundance matrix
was used for biological analysis. Composition and phage confidence-filter
sensitivity are excluded until processed matrices and annotations are supplied.
'''
    (root/'results/reports/virome_qc.md').write_text(report, encoding='utf-8')
    return {'status':'excluded_missing_processed_inputs', 'biological_profiles_analyzed':0}


def eligibility(root, config):
    rows = [
        ('Primary','Within-mouse phage change versus immune disruption','untestable','No retrieved individual abundance matrix, verified crosswalk or chronic-stress immune baseline'),
        ('H1','Stress-associated viral composition','untestable','Processed pool and recipient abundance matrices unavailable; no raw reprocessing within budget'),
        ('H2','Reference deviation versus immune outcomes','untestable','No retrieved processed viral profiles linked to immune measurements'),
        ('H3','Bacterial-adjusted viral association','untestable','No matched processed viral or bacterial tables; sample size limits adjustment'),
        ('H4','FVT-associated viral and immune outcomes','immune_component_only_testable','Separate immune contrasts only; no joint viral analysis or virome-specific mechanism'),
        ('H5','Robustness to viral filtering and compositional choices','untestable','No abundance or confidence annotations; mathematical estimators tested using software fixtures only')]
    out = [{'hypothesis':h,'question':q,'status':s,'reason':r} for h,q,s,r in rows]
    write_csv(root/'results/tables/hypothesis_eligibility.csv',out)
    return {'temporal_stability_estimates':0,'reference_state_estimates':0,'hypotheses':len(out)}


def association_gate(root, config):
    text = '''# Phage-immune association eligibility

No retrieved processed recipient viral profile is linked to an immune outcome.
The usable matched virome-immune count is zero. Metadata compatibility and
published sample counts are not measured community features. No animal-level
viral correlations, adjusted association models, or group-mean correlations
were fitted. This is a data availability limit, not a statistical null finding.
Separate exploratory immune contrasts are in immune_contrasts.csv.
'''
    (root/'results/reports/phage_immune_associations.md').write_text(text, encoding='utf-8')


def bacteriome_gate(root, config):
    (root/'results/reports/bacteriome_integration.md').write_text('''# Bacteriome integration eligibility

Individual bulk metagenomes and first-experiment 16S runs are deposited, but
the inspected public code archive references unavailable species.tsv and
metadata/recalibration tables. No processed bacterial abundance table was
retrieved. No bacterial covariate, cross-domain distance correlation,
phage-host infection or mediation analysis was calculated. Raw reprocessing
was excluded by the resource audit. This stage records the exclusion.
''', encoding='utf-8')
    return {'status':'excluded_missing_processed_inputs','models_fitted':0}
