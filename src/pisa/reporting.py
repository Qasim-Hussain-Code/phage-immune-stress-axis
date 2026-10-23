import json
import re
from decimal import Decimal
from .io import read_csv,redact_local_paths

NAMES={'ly6chi_monocytes':'Basal LY6Chi monocyte proportion',
       'ly6chi_monocytes_cd62':'Basal CD62L-positive fraction of LY6Chi monocytes',
       'tnfa_splenocyte_unstimulated':'Unstimulated splenocyte TNF-alpha'}
CONTRAST_NAMES={'ctr_stress_minus_ctr':'Control Stress minus Control',
                'fvt_stress_minus_ctr_stress':'FVT Stress minus Control Stress'}


def verify_readme_primary_table(text,rows):
    """Check reader-facing estimates to their displayed decimal precision."""
    labels={'ly6chi_monocytes':'LY6Chi monocytes','ly6chi_monocytes_cd62':'CD62L-positive fraction',
            'tnfa_splenocyte_unstimulated':'Splenocyte TNF-alpha'}
    comparisons={'ctr_stress_minus_ctr':'Stress − Control','fvt_stress_minus_ctr_stress':'FVT Stress − Stress'}
    table={}
    for line in text.splitlines():
        cells=[cell.strip() for cell in line.split('|')[1:-1]]
        if len(cells)==5 and cells[0] in labels.values():
            key=(cells[0],cells[1])
            if key in table: raise ValueError('Duplicate README primary contrast')
            table[key]=cells
    if len(table)!=6 or len(rows)!=6: raise ValueError('README must contain the six primary comparisons')
    for row in rows:
        cells=table.get((labels[row['endpoint']],comparisons[row['contrast']]))
        if cells is None or cells[2]!=f"{row['n_first']} / {row['n_second']}":
            raise ValueError('README primary sample count or comparison differs')
        displayed=re.findall(r'[+-]?\d+(?:\.\d+)?(?:e[+-]?\d+)?',cells[3].replace('−','-'))
        values=[row[name] for name in ('mean_difference','ci_low','ci_high')]+[row['q_value']]
        displayed.append(cells[4])
        if len(displayed)!=4: raise ValueError('README primary estimate is malformed')
        for printed,actual in zip(displayed,values):
            tolerance=0.5*10**Decimal(printed).as_tuple().exponent
            if abs(float(printed)-float(actual))>tolerance+1e-12:
                raise ValueError('README primary estimate differs from computed result')
    return True


def validation_counts_text(validation):
    """Unittest tests_run includes skips; executed counts include failed tests."""
    counts={name:validation.get(name,0) for name in ('tests_run','skipped','failures','errors')}
    if any(isinstance(value,bool) or not isinstance(value,int) or value<0
           for value in counts.values()) or counts['skipped']>counts['tests_run']:
        raise ValueError('Validation counts must be nonnegative integers with skips within collected tests')
    executed=counts['tests_run']-counts['skipped']
    return (f"{counts['tests_run']} tests collected, {executed} executed, "
            f"{counts['skipped']} skipped, {counts['failures']} failures and {counts['errors']} errors")


def design_sensitivity_lines(root):
    if not (root/'results/tables/immune_putative_cage_means.csv').is_file(): return []
    cages=read_csv(root/'results/tables/immune_putative_cage_means.csv')
    logs=read_csv(root/'results/tables/immune_tnfa_log_sensitivity.csv')
    within=read_csv(root/'results/tables/immune_within_block.csv')
    omitted=read_csv(root/'results/tables/immune_control_cage_omission.csv')
    lines=['','## Post hoc design and scale sensitivities','',
        'Literal IDs define two treatment-balanced ranges and six putative control cages '
        'with source sizes 2,2,1,2,2,1. Their interpretation as batches or cages is unverified. '
        'The following conditional comparisons give each observed control cage mean equal '
        'weight, while the singly housed stressed groups retain animals as units. This '
        'changes the control estimand as well as its uncertainty. The six comparisons '
        'have a separate exploratory BH family.','',
        '| Stress minus Control, conditional cage units | Mean difference | Pointwise 95% CI | Raw P | Sensitivity BH q |',
        '|---|---:|---|---:|---:|']
    for row in cages:
        if row['contrast']=='ctr_stress_minus_ctr':
            lines.append(f"| {NAMES[row['endpoint']]} | {float(row['mean_difference']):.4g} | "
                f"{float(row['ci_low']):.4g} to {float(row['ci_high']):.4g} | "
                f"{float(row['p_value']):.4g} | {float(row['q_value']):.4g} |")
    diagnostic=[r for r in omitted if r['endpoint']=='ly6chi_monocytes' and r['contrast']=='ctr_stress_minus_ctr']
    fvts=[r for r in within if r['contrast']=='fvt_stress_minus_ctr_stress']
    lines.extend(['',
        'The LY6Chi Stress–Control inference depends on the assumed independent unit. '
        'Every putative cage was also omitted in turn, retaining the six-test family '
        f"in each diagnostic refit; LY6Chi Stress–Control q ranges from {min(float(r['q_value']) for r in diagnostic):.4g} "
        f"to {max(float(r['q_value']) for r in diagnostic):.4g}. These refits are not independent replications or source exclusions.",'',
        'Treatment-plus-ID-stratum fits use HC3 covariance and finite-df t intervals, '
        'with treatment-only HC3 fits as like-for-like reference columns. '
        f"{sum(r['same_direction_as_overall_raw']=='True' for r in fvts)} of {len(fvts)} FVT endpoint-by-stratum differences preserve their overall raw direction. "
        'This is direction agreement, not replicated significance. Adjusted-model '
        'tests form a BH family of six; within-stratum tests form a separate family of twelve.','',
        'All observed TNF-alpha concentrations are positive. Log-Welch estimates below '
        'retain every observed value without a pseudocount and target geometric-mean '
        'ratios, rather than raw means or rank ordering. The two tests have their own '
        'exploratory BH family. Pointwise intervals do not incorporate that correction.','',
        '| TNF-alpha comparison | Geometric-mean ratio | Pointwise 95% CI | Raw P | Two-test BH q |',
        '|---|---:|---|---:|---:|'])
    for row in logs:
        ratio_label={'ctr_stress_minus_ctr':'Control Stress / Control',
                     'fvt_stress_minus_ctr_stress':'FVT Stress / Control Stress'}[row['contrast']]
        lines.append(f"| {ratio_label} | {float(row['geometric_mean_ratio']):.4g} | "
            f"{float(row['ratio_ci_low']):.4g} to {float(row['ratio_ci_high']):.4g} | "
            f"{float(row['p_value']):.4g} | {float(row['q_value']):.4g} |")
    lines.extend(['',
        'These post hoc checks quantify dependence on assumptions and scale. They '
        'do not replace the primary six-test family or establish confirmed effects. '
        'The [design sensitivity appendix](design_sensitivity.md) defines the models, '
        'assumptions and full membership, contrast, omission and log-scale tables.'])
    return lines


def summarize(root,config):
    """Write the biological results from the fixed comparisons and source audit."""
    results=read_csv(root/'results/tables/immune_contrasts.csv')
    sensitivities=read_csv(root/'results/tables/immune_sensitivity.csv')
    summary=json.loads((root/'results/reports/sample_audit_summary.json').read_text())
    validation=json.loads((root/'results/reports/validation_summary.json').read_text())
    lines=['# Results','',
        'The public source workbook supports an exploratory comparison of three immune outcomes '
        'in the Control, Control Stress and FVT Stress groups of Ritz et al. (2024). '
        'The outcomes were selected after reading the published findings, before calculating '
        'the present contrasts. All supplied observations were retained.','',
        'The blood samples used for the two flow outcomes were collected on study day 19, '
        'before forced swim and after 16 defeat days. Their values are percentages of parent '
        'population, and differences are percentage points rather than absolute cell counts. '
        'TNF-alpha was measured in unstimulated splenocyte culture supernatant, in pg/mL, '
        'from spleens collected on day 23 after 19 defeat days. These assays belong to '
        'the same source cohort but were not collected at the same time.','',
        'Each table reports unadjusted animal-level mean differences with pointwise 95% Welch '
        'intervals. The six P values form one Benjamini-Hochberg family. Sample sizes are '
        'available observations for that endpoint.']
    narratives={
        'ly6chi_monocytes':('LY6Chi monocytes',
            'The stressed-control group had a lower basal LY6Chi monocyte proportion than '
            'Control. The FVT Stress group had a higher proportion than stressed controls. '
            'The two component comparisons describe the observed pattern more directly than '
            'a single restoration contrast.'),
        'ly6chi_monocytes_cd62':('CD62L-positive monocytes',
            'The CD62L-positive fraction of LY6Chi monocytes was higher in FVT Stress than '
            'in stressed controls. The stress-versus-Control difference was small and imprecise. '
            'This is an FVT-associated difference without an established preceding stress '
            'deficit, so it does not demonstrate reversal of such a deficit.'),
        'tnfa_splenocyte_unstimulated':('Unstimulated splenocyte TNF-alpha',
            'The stressed-control group had a higher mean TNF-alpha concentration, with '
            'substantial dispersion. The FVT-versus-stressed mean difference was negative, '
            'but both TNF-alpha intervals were wide and included zero. These estimates '
            'remain imprecise; they do not establish equivalence between groups. '
            'The measurement describes ex vivo culture output, not circulating plasma TNF-alpha.'),
    }
    for endpoint,(title,narrative) in narratives.items():
        endpoint_rows=[row for row in results if row['endpoint']==endpoint]
        if not endpoint_rows:
            continue
        lines.extend(['','## '+title,'',narrative,'',
            '| Endpoint | Contrast | n first/second | Mean difference | 95% CI | P | BH q |',
            '|---|---|---:|---:|---|---:|---:|'])
        for row in endpoint_rows:
            lines.append(f"| {NAMES[row['endpoint']]} | {CONTRAST_NAMES[row['contrast']]} | "
                         f"{row['n_first']}/{row['n_second']} | {float(row['mean_difference']):.4g} | "
                         f"{float(row['ci_low']):.4g} to {float(row['ci_high']):.4g} | "
                         f"{float(row['p_value']):.4g} | {float(row['q_value']):.4g} |")
    replication=root/'results/tables/original_method_replication.csv'
    replication_rows=read_csv(replication) if replication.is_file() else []
    monocyte=next((r for r in results if r['endpoint']=='ly6chi_monocytes'
                  and r['contrast']=='fvt_stress_minus_ctr_stress'),None)
    tukey=next((r for r in replication_rows if r['endpoint']=='ly6chi_monocytes'
               and r['record_type']=='tukey_kramer' and r['contrast']=='fvt_stress_minus_ctr_stress'),None)
    if monocyte and tukey:
        lines.extend(['','## Dependence on the statistical comparison','',
            f"The monocyte FVT comparison gives Welch P={float(monocyte['p_value']):.5g} here and "
            f"Tukey-Kramer P={float(tukey['p_value']):.6g} under the original three-group calculation, "
            f"reproducing the published P={tukey['published_p_value']}. Both use the same observations "
            'and mean difference. Pooling the residual variance across all three groups and '
            'adjusting for three pairwise comparisons explains the different uncertainty estimates; '
            'additional source exclusions are unnecessary for this numerical reconciliation.'])
    if replication.is_file():
        replication_rows=read_csv(replication)
        if replication_rows:
            checked=[r for r in replication_rows if r['published_agreement'] not in ['not_reported_for_this_statistic','']]
            mismatches=[r for r in checked if r['published_agreement']=='mismatch']
            captions=[r for r in checked if r['record_type']!='group']
            caption_matches=sum(r['published_agreement']=='matches_published_precision' for r in captions)
            tnf_group=next(r for r in replication_rows if r['endpoint']=='tnfa_splenocyte_unstimulated'
                           and r['record_type']=='group' and r['group_first']=='fvt_stress')
            lines.extend(['',
                f'The [original-method reconstruction](../results/reports/original_method_replication.md) '
                f'contains {len(replication_rows)} records. It matches {caption_matches} of '
                f'{len(captions)} selected caption-statistic checks and '
                f'{len(checked)-len(mismatches)} of {len(checked)} combined caption and group-summary '
                'checks at published precision. One printed mean remains unresolved: FVT '
                f"unstimulated TNF-alpha averages {float(tnf_group['group_mean']):.9g} pg/mL in the workbook, directly "
                f"rounding to {float(tnf_group['group_mean']):.1f}, while Table 1b prints {tnf_group['published_mean']}. Source values and rounding "
                'tolerances were retained.','',
                'The planned contrast compares the stressed mean with the average of Control '
                'and FVT Stress. It does not jointly establish a stress effect and its reversal. '
                'Tukey intervals cover three pairs within each endpoint under a common-variance '
                'model. The reconstruction verifies compatible calculations, rather than '
                're-executing the original SPSS session or reconstructing its full BH family.'])
    lines.extend(['','## Sensitivity and missing observations','',
        'Each comparison was refitted after omitting each observed animal once. The ranges '
        'below describe influence on the mean difference; they are not confidence intervals. '
        'All six observed directions persisted, which does not establish stable significance. '
        'The Mann-Whitney comparisons describe distributional ordering and use their own '
        'six-test sensitivity BH family. They do not test the same raw-mean estimand.','',
        '| Endpoint | Contrast | Leave-one-animal-out difference range | Rank sensitivity P | Direction preserved |',
        '|---|---|---|---:|---|'])
    for row in sensitivities:
        lines.append(f"| {NAMES[row['endpoint']]} | {CONTRAST_NAMES[row['contrast']]} | "
                     f"{float(row['loo_mean_difference_min']):.4g} to {float(row['loo_mean_difference_max']):.4g} | "
                     f"{float(row['mann_whitney_p_value']):.4g} | {row['loo_direction_preserved']} |")
    lines.extend(['',
        'TNF-alpha illustrates the distinction between the mean and rank comparisons: the '
        'highly dispersed stressed group produces different results for those different '
        'features of the distribution. A rank result is not automatically a median shift. '
        'Neither method is selected as a replacement because it gives a smaller P value.','',
        'The n=9 FVT samples also differ by assay. Monocyte and CD62L measurements lack '
        'source ID 31, while TNF-alpha lacks ID 11. Equal sample counts therefore do not '
        'establish a common complete-case set. The workbook does not identify all upstream '
        'technical exclusions, detection thresholds or statistical exclusions.'])
    bounds_path=root/'results/tables/immune_missingness_bounds.csv'
    ranks_path=root/'results/tables/immune_rank_effects.csv'
    if bounds_path.is_file() and ranks_path.is_file():
        bounds=read_csv(bounds_path);ranks=read_csv(ranks_path)
        if len(bounds)!=6 or len(ranks)!=6:
            raise ValueError('Descriptive robustness must retain the existing six comparisons')
        lines.extend(['',
            'Two descriptive checks were added after inspecting the earlier reanalysis. '
            'For the animals represented by workbook rows, allowing each missing percentage '
            'assay any well-defined value in [0,100] gives the following sharp support bounds. '
            'No value is imputed into the analysis.','',
            '| Percentage endpoint | FVT Stress minus Control Stress support bounds |',
            '|---|---|'])
        for row in bounds:
            if row['contrast']=='fvt_stress_minus_ctr_stress' and row['lower_mean_difference']!='':
                lines.append(f"| {NAMES[row['endpoint']]} | {float(row['lower_mean_difference']):.6g} to "
                             f"{float(row['upper_mean_difference']):.6g} percentage points |")
        tnf=next(row for row in ranks if row['endpoint']=='tnfa_splenocyte_unstimulated'
                 and row['contrast']=='fvt_stress_minus_ctr_stress')
        lines.extend(['',
            'Both source-cohort mean directions remain positive under that support assumption. '
            'These are descriptive extrema, not confidence intervals or evidence of robust '
            'significance. An undefined parent population would invalidate the well-defined '
            'assay assumption. Missing TNF-alpha values have no identified finite upper support, '
            'so analogous finite bounds are unavailable.','',
            f"For observed TNF-alpha, {tnf['direct_first_greater_pairs']} first-greater and "
            f"{tnf['direct_tied_pairs']} tied comparisons among {tnf['cross_group_pair_count']} cross-group pairs "
            f"give empirical superiority {float(tnf['empirical_probability_first_greater_plus_half_ties']):.6g} "
            f"and rank-biserial effect {float(tnf['rank_biserial_first_minus_second']):.6g} for FVT Stress "
            f"versus Control Stress. Those pairs reuse {tnf['n_observed_animals']} animals. They are "
            'not independent replicates. The full six-comparison tables and definitions are '
            'in the [descriptive robustness report](../results/reports/phenotype_robustness.md).'])
    lines.extend(design_sensitivity_lines(root))
    lines.extend(['','## What the dataset leaves unanswered','',
        f"The workbook contains {summary['workbook_animal_rows']} animal rows across two experiments. "
        f"The sequencing archive contains {summary['principal_run_count']} runs representing "
        f"{summary['principal_specimen_count']} specimens: "
        f"{summary['sequencing_category_counts'].get('individual_recipient_bulk_metagenome',0)} recipient bulk specimens, "
        f"{summary['sequencing_category_counts'].get('pooled_fecal_virome',0)} enriched pools and "
        f"{summary['sequencing_category_counts'].get('transplant_inoculum',0)} inocula. "
        'The initial-study captions imply 12 pool-by-time profiles. Pool membership across '
        'time remains unresolved, so these are not 12 verified animal trajectories.','',
        'The intended association between viral change and an immune phenotype requires '
        'individual longitudinal viral abundance profiles and a verified link to immune '
        'source animals. No processed viral profile was retrieved and none was matched to '
        'immune outcomes. Endpoint immune measurements could serve as outcomes for such an '
        'association if those viral inputs became available; they would still not measure '
        'within-mouse immune change or temporal immune stability. Bacterial adjustment also '
        'requires the missing matched bacterial profiles.','',
        'Heat-inactivated-FVT-labelled specimens also occur in the archive: 20 recipient '
        'bulk samples, ten inocula and two pools. Their immune outcomes and allocation '
        'key are not supplied by the retrieved workbook. This arm could strengthen '
        'the active-versus-inactivated comparison, while heating may also alter other '
        'transplant constituents. The 17 candidate complete Stress/FVT Before/After '
        'pairs require about 85.6 GB of compressed reads alone. The current limit '
        'combines missing processed inputs and validated linkage with a local '
        'reprocessing constraint. The [data requirements](data_requirements.md) '
        'describe what would make these routes usable.','',
        'Unstressed controls were group housed and both stressed groups singly housed. '
        'Thus the stress-versus-Control contrast includes different housing regimes, while '
        'FVT Stress versus Control Stress shares the stated regime. Unavailable allocation '
        'details limit the animal-level uncertainty estimates. The treatment comparisons '
        'describe selected immune phenotypes; they do not isolate a phage mechanism or '
        'establish immune resilience.'])
    calibration=root/'results/reports/software_calibration.md'
    calibration_note=''
    if calibration.is_file():
        calibration_rows=read_csv(root/'results/tables/software_calibration.csv')
        expected=config.get('calibration',{}).get('replicates',20000)
        from .calibration import SCENARIOS
        if len(calibration_rows)!=16*len(SCENARIOS) or any(
            r['purpose']!='synthetic_not_biological' or int(r['replicates'])!=expected
            or int(r['seed'])!=config['seed'] for r in calibration_rows):
            raise ValueError('Synthetic calibration output does not match the current configured run')
        calibration_note=(f' The separate [software calibration](../results/reports/software_calibration.md) '
            f'used {expected:,} replicates in each of {len(SCENARIOS)} known zero-mean scenarios. Its '
            'Monte Carlo uncertainty is simulation uncertainty and does not calibrate the '
            'actual experiment under an unknown dependence structure.')
    lines.extend(['','## Reproducibility','',
        f"Validation: {validation_counts_text(validation)}. "
        '[Executed records](../results/reports/validation_summary.json) and '
        '[statistical checks](statistical_validation.md) document the software verification. '
        'Synthetic fixtures are kept separate from biological observations.'+calibration_note,'',
        'Source: [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y). '
        'Observation-level source cells, exact estimates and missingness are retained in '
        '[results/tables](../results/tables) and [data/processed/immune_long.csv](../data/processed/immune_long.csv).'])
    (root/'docs/results.md').write_text('\n'.join(lines)+'\n',encoding='utf-8')


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
    invocation=redact_local_paths(invocation)
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
    if validation:
        lines.append(f"Validation ({validation_scope}): {validation_counts_text(validation)}.")
    if not (validation and validation.get('success')
            and validation.get('tests_run',0)>validation.get('skipped',0)
            and not validation.get('failures',0) and not validation.get('errors',0)):
        lines.append('No successful validation result is established by this invocation record.')
    qa=figure_qa_status(root)
    if qa['status']=='prior_visual_review_matches_current_files':
        lines.append(f"Prior visual review dated {qa['reviewed_utc']} matches the current bytes of {qa['figures_verified']} PDF files. This is not a new visual review by this invocation.")
    else:
        lines.append('Current figure visual QA is unverified: '+qa['reason']+'.')
    lines.extend(['','Publication status is documented separately in `docs/maintenance/publication_status.md`; executing this pipeline does not establish a GitHub publication.',
                  'Researcher and sole project author: Qasim Hussain. No causal phage mechanism or stability-immune association is established by this restricted analysis.'])
    return '\n'.join(lines)+'\n'


def resource_report(root,usage,invocation=None,config=None):
    usage=redact_local_paths(usage)
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
        assessment+='The full restricted workflow completed. Read the [scientific results](../../docs/results.md) for estimates and interpretation.\n\n'
    else:
        assessment+='Scientific results from earlier invocations are not evidence that this invocation executed those analyses.\n\n'
    assessment+=invocation_text(root,invocation)
    (root/'results/reports/final_assessment.md').write_text(assessment,encoding='utf-8')
    identifier=invocation.get('invocation_id')
    if identifier and all(char.isalnum() or char in '_-' for char in identifier):
        target=root/f'results/reports/invocations/{identifier}.md'
        target.parent.mkdir(parents=True,exist_ok=True)
        target.write_text(text,encoding='utf-8')
