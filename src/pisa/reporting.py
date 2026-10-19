import json
from .io import read_csv

NAMES={'ly6chi_monocytes':'Basal LY6Chi monocyte proportion',
       'ly6chi_monocytes_cd62':'Basal CD62L-positive fraction of LY6Chi monocytes',
       'tnfa_splenocyte_unstimulated':'Unstimulated splenocyte TNF-alpha'}
CONTRAST_NAMES={'ctr_stress_minus_ctr':'Control Stress minus Control',
                'fvt_stress_minus_ctr_stress':'FVT Stress minus Control Stress'}


def summarize(root,config):
    results=read_csv(root/'results/tables/immune_contrasts.csv')
    sensitivities=read_csv(root/'results/tables/immune_sensitivity.csv')
    summary=json.loads((root/'results/reports/sample_audit_summary.json').read_text())
    validation=json.loads((root/'results/reports/validation_summary.json').read_text())
    lines=['# Results','',
       'This is a public-data feasibility study with a separate exploratory reanalysis of immune source data. '
       'It does not test a measured phageome stability versus immune-response relationship.','',
       f"The source workbook contains {summary['workbook_animal_rows']} animal rows across two experiments. "
       f"The principal archive contains {summary['principal_run_count']} sequencing specimens: "
       '77 individual recipient bulk metagenomes, 8 enriched pools and 19 inocula. '
       'The initial paper captions imply 12 pool-by-time enriched profiles across group and time; '
       'these must not be added to the second experiment as longitudinal animals. '
       'No processed viral abundance profile was retrieved and zero are matched to immune outcomes. '
       'This is missing evidence, not a biological null result.','',
       '## Separate immune contrasts','',
       'Three endpoints and two contrasts were selected after reading the published paper and before calculating '
       'the present contrasts. These are exploratory unadjusted animal-level summaries. All estimates use '
       'untransformed source units. Extended Data Table 1c identifies the two selected flow outcomes as basal '
       '(before forced swim, after chronic stress), percent of parent population; their differences are '
       'percentage points. Table 1b identifies unstimulated splenocyte TNF-alpha as pg/mL. '
       'Intervals are pointwise 95% Welch intervals. P values have a six-test BH correction. '
       'Unknown cage allocation, incomplete terminal measurements and unresolved detection censoring '
       'limit inferential calibration.','',
       '| Endpoint | Contrast | n first/second | Mean difference | 95% CI | P | BH q |',
       '|---|---|---:|---:|---|---:|---:|']
    for row in results:
        lines.append(f"| {NAMES[row['endpoint']]} | {CONTRAST_NAMES[row['contrast']]} | "
                     f"{row['n_first']}/{row['n_second']} | {float(row['mean_difference']):.4g} | "
                     f"{float(row['ci_low']):.4g} to {float(row['ci_high']):.4g} | "
                     f"{float(row['p_value']):.4g} | {float(row['q_value']):.4g} |")
    lines.extend(['','## Robustness and interpretation','',
       'No observed animal was deleted as an outlier. Each contrast was recomputed after omitting each '
       'observed animal once. Rank-based comparisons are distributional sensitivity checks, with their '
       'own six-comparison BH family; they do not estimate the same mean difference. The intervals below '
       'are ranges of refitted effects, not confidence intervals.','',
       '| Endpoint | Contrast | Leave-one-animal-out difference range | Rank sensitivity P | Direction preserved |',
       '|---|---|---|---:|---|'])
    for row in sensitivities:
        lines.append(f"| {NAMES[row['endpoint']]} | {CONTRAST_NAMES[row['contrast']]} | "
                     f"{float(row['loo_mean_difference_min']):.4g} to {float(row['loo_mean_difference_max']):.4g} | "
                     f"{float(row['mann_whitney_p_value']):.4g} | {row['loo_direction_preserved']} |")
    lines.extend(['',
       'Group differences in immune source data do not imply that a phage or viral feature caused those '
       'differences. The original article already reports related treatment-associated immune results. '
       'Different endpoints and contrasts need not support a uniform restoration interpretation. '
       'Nonsignificant contrasts are not evidence of equivalence or absence of an immune effect.','',
       'CD62L-positive monocyte fraction is higher with FVT than stressed control, while its stress-control '
       'contrast is imprecise. This is not demonstrated reversal of a stress-induced deficit. TNF-alpha '
       'has a highly dispersed stressed group: its FVT comparison differs between raw-mean Welch and '
       'rank-based tests. These estimate different aspects of the distribution; neither result is hidden. '
       'The monocyte FVT comparison uses Welch P=0.01265 here, whereas the article Fig. 4 reports '
       'Tukey pairwise P=0.106. The present six-test family, unequal-variance tests, retained workbook '
       'observations and upstream exclusions differ from the original orthogonal-contrast/Tukey analysis. '
       'This numerical difference is method sensitivity, not independent replication or evidence that '
       'the original calculation was wrong.','',
       'Endpoint-specific n=9 FVT groups contain different animals: monocyte and CD62L outcomes lack '
       'source ID 31, while TNF-alpha lacks ID 11. Equal sample counts do not establish matched endpoints.','',
       'No viral composition, temporal stability, reference deviation, bacterial-adjusted association or '
       'phage-host relationship was estimated. Original paired bulk-derived viral profiles could support '
       'additional work if their processed matrix, confidence annotations and verified animal map become '
       'available. Endpoint immune measurements would still not measure chronic-stress immune stability.','',
       '## Validation','',
       f"The executed validation suite ran {validation['tests_run']} tests with {validation['failures']} failures "
       f"and {validation['errors']} errors. Independent checks cover Welch inference, BH adjustment, "
       'community-distance identities and linkage invariants. Synthetic fixtures are software tests only.','',
       'Source: [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y). '
       'Exact values and missingness are in results/tables; raw observations retain source-cell locations.'])
    text='\n'.join(lines)+'\n'
    (root/'docs/results.md').write_text(text,encoding='utf-8')
    (root/'results/reports/final_assessment.md').write_text(text,encoding='utf-8')


def resource_report(root,usage):
    initial=json.loads((root/'data/manifests/environment_initial.json').read_text())
    current=root/'data/manifests/environment_local.json'
    packages=json.loads(current.read_text())['packages'] if current.exists() else initial['packages']
    text=f'''# Resource usage

The measured analysis host is Windows 11, not the Linux Mint system specified
in the project brief. Scripts are portable; Linux execution was not performed.
The initial standard `python` on PATH was an unrelated Python 2 installation;
execution used the explicitly located Python 3.14 interpreter. R 4.5.2 was found
under Program Files but was not required. Conda/Mamba executables were not on
PATH. Existing scientific libraries were used without reinstalling them.

## Measured values

| Measurement | Bytes | Decimal MB/GB |
|---|---:|---:|
| Initial installed physical RAM | {initial['memory']['total_bytes']} | {initial['memory']['total_bytes']/1e9:.3f} GB |
| Initial available physical RAM | {initial['memory']['available_bytes']} | {initial['memory']['available_bytes']/1e6:.1f} MB |
| Initial disk free | {initial['disk_free_bytes']} | {initial['disk_free_bytes']/1e9:.3f} GB |
| Operational new-storage ceiling | {usage['operational_storage_budget_bytes']} | {usage['operational_storage_budget_bytes']/1e9:.3f} GB |
| Maximum measured process peak RSS | {usage['max_measured_stage_peak_rss_bytes']} | {usage['max_measured_stage_peak_rss_bytes']/1e6:.1f} MB |
| Project snapshot including Git | {usage['project_bytes_including_git']} | {usage['project_bytes_including_git']/1e6:.2f} MB |
| Project snapshot excluding Git | {usage['project_bytes_excluding_git']} | {usage['project_bytes_excluding_git']/1e6:.2f} MB |
| Disk free at snapshot | {usage['disk_free_bytes']} | {usage['disk_free_bytes']/1e9:.3f} GB |

The RAM maximum includes native peaks from the runner, stages and validation
child. It is the maximum of per-process measurements, not a measured sum of
concurrent processes or whole-machine memory. Each active process is capped
at 1 GB; runner monitors child native RSS and project storage every 0.1 seconds.
Available system memory is checked with a 100 MB minimum; a low-memory failure
records a resumable failure rather than silently increasing the budget.
Resource snapshots precede later documentation/Git housekeeping and can be
regenerated. Logs and native measurements are in results/reports.

## Footprint decisions

The initial selected scientific inputs and outputs were estimated below 25 MB.
The core run used about 3 MB before optional PDF QA installation. Public raw
PRJNA970614 FASTQs total 262,211,457,238 compressed bytes; transcriptomic FASTQs
total 320,396,480,444 bytes. Neither was fetched. The 16S archive totals
1,731,077,490 bytes compressed, but reprocessing would not resolve missing viral
matrices and was not selected. No MetaPhage pipeline, GPU model, classifier
database, cloud account or paid compute service was installed or used.

PDF rendering required optional workspace-only pypdfium2: a verified 3.95 MB
wheel and about 8.09 MB installed files, plus small metadata and rendered PNGs.
This is documented in pdf_qa.md. These caches count toward the guard's budget
but are excluded from Git. A fresh scientific virtual environment is not part
of the measured execution; installing one would require a separate budget
check and several hundred MB depending on platform.

## Observed library versions

'''
    text+='\n'.join(f'- {name}: {version}' for name,version in packages.items() if version)+'\n'
    (root/'docs/resource_usage.md').write_text(text,encoding='utf-8')

