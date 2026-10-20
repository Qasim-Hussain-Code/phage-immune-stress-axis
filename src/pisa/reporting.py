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
       f"The principal archive contains {summary['principal_run_count']} sequencing runs representing "
       f"{summary['principal_specimen_count']} specimens: "
       f"{summary['sequencing_category_counts'].get('individual_recipient_bulk_metagenome',0)} individual recipient bulk specimens, "
       f"{summary['sequencing_category_counts'].get('pooled_fecal_virome',0)} enriched pools and "
       f"{summary['sequencing_category_counts'].get('transplant_inoculum',0)} inocula. "
       'The initial paper captions imply 12 pool-by-time enriched profiles across group and time; '
       'these must not be added to the second experiment as longitudinal animals. '
       'No processed viral abundance profile was retrieved and zero are matched to immune outcomes. '
       'This is missing evidence, not a biological null result.','',
       '## Separate immune contrasts','',
       'Three endpoints and two contrasts were selected after reading the published paper and before calculating '
       'the present contrasts. These are exploratory unadjusted animal-level summaries. All estimates use '
       'untransformed source units. Extended Data Table 1c identifies the two selected flow outcomes as basal '
       '(blood collected on study day 19 before forced swim, after 16 defeat days), percent of parent '
       'population; their differences are percentage points. Table 1b identifies unstimulated '
       'splenocyte TNF-alpha as pg/mL, from terminal day-23 spleen collection after 19 defeat sessions. '
       'These source-linked assays are not contemporaneous measurements. '
       'Intervals are pointwise 95% Welch intervals. P values have a six-test BH correction. '
       'Housing differs for the stress-control contrast: unstressed controls were group housed '
       'and stressed groups singly housed. Both groups in the FVT-stressed comparison share the '
       'stated single-housing regime. Incomplete assay measurements, unresolved detection '
       'censoring and unavailable allocation details still limit interpretation.','',
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
       'The monocyte FVT comparison differs from the article\'s Tukey pairwise P=0.106. '
       'The original three-group pooled residual variance and Tukey adjustment differ from the '
       'present unequal-variance pairwise test and six-test BH family. Those method choices explain '
       'the numerical difference without requiring different source observations. This comparison '
       'does not identify an error in the original calculation. Upstream censoring and exclusions '
       'remain a separate general limitation.','',
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
    replication=root/'results/tables/original_method_replication.csv'
    if replication.is_file():
        replication_rows=read_csv(replication)
        if replication_rows:
            checked=[r for r in replication_rows if r['published_agreement'] not in ['not_reported_for_this_statistic','']]
            mismatches=[r for r in checked if r['published_agreement']=='mismatch']
            captions=[r for r in checked if r['record_type']!='group']
            lines.extend(['','## Original-method reconstruction','',
                f'A separate reconstruction table contains {len(replication_rows)} records: '
                '`results/tables/original_method_replication.csv`. It is distinct from the fixed '
                'Welch family. Its presence does not imply that every original outcome or the '
                'original full multiplicity family was reconstructed. '
                f'{len(checked)-len(mismatches)} of {len(checked)} printed reference checks agree, '
                f'including all {len(captions)} selected caption-statistic checks.', '',
                'The three-group pooled-variance calculation reproduces the selected planned '
                't statistics and Tukey comparisons at the published precision. In particular, '
                'the monocyte FVT comparison is P=0.106409 under Tukey-Kramer, explaining '
                'the published P=0.106 without additional exclusions. One printed group mean '
                'remains discrepant: unstimulated FVT TNF-alpha averages 27.8492778 pg/mL '
                'in the workbook, which rounds directly to 27.8, versus 27.9 in Table 1b. '
                'The discrepancy is retained; no tolerance was widened and no value changed.', '',
                'The planned contrast compares the stressed mean with the average of Control '
                'and FVT Stress. It does not jointly establish a stress effect and its reversal. '
                'Tukey intervals cover three pairwise comparisons within one endpoint under '
                'a common-variance model; the original across-outcome BH family remains unreconstructed.'])
    bounds_path=root/'results/tables/immune_missingness_bounds.csv'
    ranks_path=root/'results/tables/immune_rank_effects.csv'
    if bounds_path.is_file() and ranks_path.is_file():
        bounds=read_csv(bounds_path);ranks=read_csv(ranks_path)
        if len(bounds)!=6 or len(ranks)!=6:
            raise ValueError('Descriptive robustness must retain the existing six comparisons')
        lines.extend(['','## Descriptive missingness and rank effects','',
            'These diagnostics were added after inspecting the earlier reanalysis. They add '
            'no hypothesis tests and leave the primary six-test family unchanged. Bounds target '
            'the animals represented by workbook rows, conditional on missing percentage assays '
            'having well-defined values anywhere in [0,100]. They are descriptive extrema, '
            'not confidence intervals or evidence of robust statistical significance.','',
            '| Percentage endpoint | FVT Stress minus Control Stress support bounds |',
            '|---|---|'])
        for row in bounds:
            if row['contrast']=='fvt_stress_minus_ctr_stress' and row['lower_mean_difference']!='':
                lines.append(f"| {NAMES[row['endpoint']]} | {float(row['lower_mean_difference']):.6g} to "
                             f"{float(row['upper_mean_difference']):.6g} percentage points |")
        tnf=next(row for row in ranks if row['endpoint']=='tnfa_splenocyte_unstimulated'
                 and row['contrast']=='fvt_stress_minus_ctr_stress')
        lines.extend(['',
            'Under those support assumptions, neither missing percentage value can reverse '
            'the source-cohort FVT-versus-stressed mean direction. An undefined parent population '
            'would violate the well-defined-assay assumption. TNF-alpha has missing values and '
            'no identified finite upper support, so analogous finite bounds are unavailable.','',
            f"For observed TNF-alpha, {tnf['direct_first_greater_pairs']} first-greater and "
            f"{tnf['direct_tied_pairs']} tied comparisons among {tnf['cross_group_pair_count']} cross-group pairs "
            f"give empirical superiority {float(tnf['empirical_probability_first_greater_plus_half_ties']):.6g} "
            f"and rank-biserial effect {float(tnf['rank_biserial_first_minus_second']):.6g} for FVT Stress "
            f"versus Control Stress. The pairs reuse {tnf['n_observed_animals']} observed animals; "
            'they are not independent replicates. See `results/reports/phenotype_robustness.md` '
            'and the complete six-row bounds/rank tables.'])
    calibration=root/'results/reports/software_calibration.md'
    if calibration.is_file():
        calibration_rows=read_csv(root/'results/tables/software_calibration.csv')
        expected=config.get('calibration',{}).get('replicates',20000)
        if len(calibration_rows)!=64 or any(
            r['purpose']!='synthetic_not_biological' or int(r['replicates'])!=expected
            or int(r['seed'])!=config['seed'] for r in calibration_rows):
            raise ValueError('Synthetic calibration output does not match the current configured run')
        lines.extend(['','## Conditional software calibration','',
            f'A separate synthetic benchmark completed {expected:,} replicates in each of four '
            'known zero-mean scenarios, evaluating variance '
            'heterogeneity, skew and artificial clustering. It reads no biological observations. '
            'Its Monte Carlo uncertainty is simulation uncertainty, not mouse-level uncertainty. '
            'See `results/reports/software_calibration.md` and '
            '`results/tables/software_calibration.csv`. These checks cannot infer missing cage '
            'assignments or calibrate the actual experiment under an unknown dependence structure.'])
    text='\n'.join(lines)+'\n'
    (root/'docs/results.md').write_text(text,encoding='utf-8')



def figure_qa_status(root):
    """A matching prior visual review is evidence; file existence alone is not."""
    from .figure_qa import review_status
    path=root/'data/manifests/figure_qa.json'
    if not path.is_file():
        return {'status':'unverified','reason':'No tracked visual-review manifest'}
    try:
        record=json.loads(path.read_text(encoding='utf-8'))
        if record.get('schema_version')!=1 or not record.get('figures'):
            raise ValueError('Empty or unsupported visual-review manifest')
        verified=review_status(root)
        if verified['status']!='previous_review_matches_current_files':
            raise ValueError('Current PDF files do not all match the recorded passed visual review')
        return {'status':'prior_visual_review_matches_current_files',
                'reviewed_utc':record.get('reviewed_utc') or
                    (str(record.get('review_date_taipei'))+' Taipei date; exact UTC time not recorded'
                     if record.get('review_date_taipei') else 'exact date/time not recorded'),
                'figures_verified':verified['matched']}
    except (OSError,ValueError,KeyError,TypeError) as exc:
        return {'status':'unverified','reason':str(exc)}


def invocation_text(root, invocation):
    """Only this invocation's evidence may establish its completion status."""
    state=invocation.get('status','resource_snapshot_only')
    stages=invocation.get('stages',[])
    completed=sum(row.get('status')=='completed' for row in stages)
    resumed=sum(row.get('status')=='resumed_verified' for row in stages)
    lines=['## Invocation status','',
        f"Invocation: {invocation.get('invocation_id','not recorded')}. Mode: {invocation.get('mode','not recorded')}. Status: {state}.",
        f'{completed} stages executed and {resumed} stages resumed after verifying their declared outputs and upstream dependencies.']
    if state=='completed_pilot':
        lines.append('Pilot stops after phenotype preparation. Immune inference, robustness tests and figures were not executed by this pilot.')
    elif state=='completed_validation':
        lines.append('Validation checked cached frozen inputs and software tests. It did not download data, extract metadata, or execute scientific analysis stages.')
    elif state=='completed_restricted_analysis':
        lines.append('All selected restricted-workflow stages completed or were verified from cache. Scientifically excluded analyses remain exclusions.')
    elif state in ('failed','interrupted'):
        lines.append(f"This invocation did not complete. Failure stage: {invocation.get('failed_stage') or 'startup/validation'}. "
                     f"{invocation.get('error_type','')}: {invocation.get('error','')}")
    validation=invocation.get('validation')
    validation_scope='executed in this invocation'
    if validation is None:
        item=next((row for row in stages if row.get('name')=='09_robustness_checks'),None)
        if item:
            validation=item.get('result',{})
            validation_scope='verified cached stage result' if item.get('status')=='resumed_verified' else 'executed in this invocation'
    if validation and validation.get('success'):
        lines.append(f"Validation ({validation_scope}): {validation.get('tests_run',0)} tests, "
                     f"{validation.get('failures',0)} failures, {validation.get('errors',0)} errors, "
                     f"{validation.get('skipped',0)} skipped.")
    else:
        lines.append('No successful validation result is established by this invocation record.')
    qa=figure_qa_status(root)
    if qa['status']=='prior_visual_review_matches_current_files':
        lines.append(f"Prior visual review dated {qa['reviewed_utc']} matches the current bytes of {qa['figures_verified']} PDF files. This is not a new visual review by this invocation.")
    else:
        lines.append('Current figure visual QA is unverified: '+qa['reason']+'.')
    lines.extend(['','Publication status is documented separately in `docs/publication_status.md`; executing this pipeline does not establish a GitHub publication.',
                  'Researcher and sole project author: Qasim Hussain. No causal phage mechanism or stability-immune association is established by this restricted analysis.'])
    return '\n'.join(lines)+'\n'


def resource_report(root,usage,invocation=None,config=None):
    """Report local measurements without rewriting a cached scientific artifact."""
    invocation=invocation or {'status':'resource_snapshot_only'}
    config=config or {'resources':{}}
    resources=config.get('resources',{})
    current_path=root/'data/manifests/environment_local.json'
    current=json.loads(current_path.read_text(encoding='utf-8')) if current_path.is_file() else {}
    samples=usage.get('aggregate_memory_samples',0)
    rows=[
        ('Local baseline disk free',usage.get('baseline_disk_free_bytes')),
        ('Conservative total-project storage ceiling',usage.get('operational_storage_budget_bytes')),
        ('Maximum measured native per-process RSS this invocation',usage.get('max_measured_stage_peak_rss_bytes')),
        ('Maximum sampled concurrent process-family RSS',usage.get('max_sampled_aggregate_rss_bytes') if samples else None),
        ('Project snapshot including Git',usage.get('project_bytes_including_git')),
        ('Project snapshot excluding Git',usage.get('project_bytes_excluding_git')),
        ('Disk free at snapshot',usage.get('disk_free_bytes')),
        ('Available system memory at snapshot',usage.get('available_memory_bytes')),
    ]
    lines=['# Resource usage','',
        f"Invocation: {invocation.get('invocation_id','not recorded')}. Status: {invocation.get('status','not recorded')}.",
        f"Current measured platform: {current.get('platform','not recorded')}. "
        f"Python: {str(current.get('python','not recorded')).splitlines()[0]}.",
        'Historical `environment_initial.json` records the original research execution only. '
        'It does not govern this checkout\'s resource budget. The ignored local persistent '
        'baseline is bound to checkout location, filesystem and host. A fresh checkout measures '
        'its own available space. Restarting the same checkout does not reset its budget.','',
        '| Measurement | Bytes | Decimal MB/GB |','|---|---:|---|']
    for label,value in rows:
        lines.append(f'| {label} | {value if value is not None else "not measured"} | '
                     +(f'{value/1e6:.3f} MB / {value/1e9:.6f} GB |' if value is not None else 'not measured |'))
    lines.extend(['',
        f"Configured minimum free disk: {resources.get('disk_reserve_bytes','not recorded')} bytes. "
        f"Per-process ceiling: {resources.get('max_process_rss_bytes','not recorded')} bytes. "
        f"Aggregate process-family ceiling: {resources.get('max_aggregate_rss_bytes',resources.get('max_process_rss_bytes','not recorded'))} bytes. "
        f"Available-memory floor: {resources.get('min_available_memory_bytes','not recorded')} bytes.",
        f'Concurrent-memory samples: {samples}; maximum unreadable or already-exited processes in one sample: '
        f"{usage.get('max_unreadable_or_exited_processes_per_sample','not recorded')}.",
        'The aggregate statistic sums simultaneous current RSS across runner descendants. It is '
        'sampled at approximately 0.1-second intervals during child execution and is not an exact '
        'whole-machine peak or an operating-system allocation limit. Brief processes or allocation '
        'spikes between polls may be missed. Native per-process peaks are reported separately; '
        'historical peaks from resumed stages are not counted as newly measured current-run peaks.',
        'The storage cap conservatively counts the entire checkout, including existing inputs, '
        'Git, environments, caches and temporary products inside it. Free disk is checked '
        'independently. Pre-existing software outside the checkout is not included in project '
        'bytes; installing a fresh environment requires a separate disk/RAM check. No raw '
        'sequencing data or reference database is acquired by the selected workflow.','',
        '## Observed local package versions',''])
    lines.extend(f'- {name}: {version}' for name,version in current.get('packages',{}).items() if version)
    if usage.get('snapshot_error'):
        lines.extend(['','Final resource check did not pass: '+usage['snapshot_error']])
    text='\n'.join(lines)+'\n\n'+invocation_text(root,invocation)
    (root/'docs').mkdir(parents=True,exist_ok=True)
    (root/'results/reports').mkdir(parents=True,exist_ok=True)
    (root/'docs/resource_usage.md').write_text(text,encoding='utf-8')
    assessment='# Current invocation assessment\n\n'
    if invocation.get('status')=='completed_restricted_analysis' and (root/'docs/results.md').is_file():
        assessment=(root/'docs/results.md').read_text(encoding='utf-8')+'\n'
    else:
        assessment+='Scientific results from earlier invocations are not evidence that this invocation executed those analyses.\n\n'
    assessment+=invocation_text(root,invocation)
    (root/'results/reports/final_assessment.md').write_text(assessment,encoding='utf-8')
    identifier=invocation.get('invocation_id')
    if identifier and all(char.isalnum() or char in '_-' for char in identifier):
        target=root/f'results/reports/invocations/{identifier}.md'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding='utf-8')
