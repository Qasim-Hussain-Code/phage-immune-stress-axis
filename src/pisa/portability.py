"""Prespecified, bounded CSV portability comparison; no scientific computation.

Schema and tolerance choices are fixed here before cross-platform analysis.
CSV semantic equality is distinct from byte equality. Figure differences always
require visual review. Source values, IDs, counts, JSON and publication fields
are exact; only explicitly listed derived continuous fields admit tolerance.
"""
from __future__ import annotations

import argparse
import csv
from decimal import Decimal, localcontext
import hashlib
from itertools import zip_longest
import json
import math
from pathlib import Path
from types import MappingProxyType

ABS_TOLERANCE = Decimal('1e-10')
REL_TOLERANCE = Decimal('1e-12')
MAX_CSV_BYTES = 8_388_608
MAX_FIGURE_BYTES = 33_554_432
MAX_ROWS = 50_000
MAX_FIELD_CHARACTERS = 65_536
MAX_RECORDED_DIFFERENCES = 100

_LONG = 'experiment_id|source_sheet|source_row|source_column|source_cell|source_id|mouse_id|source_group|group|endpoint|assay_domain|selected_endpoint|value|observation_status'
_SENSITIVITY = 'experiment_id|endpoint|contrast|mann_whitney_u_first|mann_whitney_p_value|rank_method|loo_n_refits|loo_mean_difference_min|loo_mean_difference_max|loo_min_difference_omitted_mouse|loo_max_difference_omitted_mouse|loo_p_value_min|loo_p_value_max|loo_direction_preserved|interpretation|mann_whitney_q_value_sensitivity_family'
_POSTHOC_COMMON = 'experiment_id|endpoint|contrast|first_group|second_group|posthoc_status|assumption_status|effect_units'
_WELCH = 'n_first|n_second|mean_first|mean_second|mean_difference|standard_error|ci_low|ci_high|confidence_level|t_statistic|degrees_freedom|p_value'
_HC3 = 'mean_difference|standard_error|t_statistic|degrees_freedom|p_value|ci_low|ci_high|confidence_level'
_UNADJUSTED_HC3 = '|'.join('unadjusted_hc3_'+column for column in _HC3.split('|'))
_POSTHOC_BH = 'q_value|bh_family|bh_family_size'
_HEADERS = {
    'data/processed/immune_long.csv': _LONG,
    'results/tables/archive_files.csv': 'name|bytes|source_record|role',
    'results/tables/article_methods_evidence.csv': 'section_id|title|source|text',
    'results/tables/figure1_data.csv': 'category|count|unit|source',
    'results/tables/figure4_data.csv': _LONG,
    'results/tables/figure5_data.csv': 'measurement|count|status',
    'results/tables/figure7_data.csv': _SENSITIVITY + '|full_mean_difference|welch_p_value|welch_q_value',
    'results/tables/figure8_data.csv': 'endpoint|contrast|method|mean_difference|ci_low|ci_high|p_value|interval_scope|effect_units',
    'results/tables/hypothesis_eligibility.csv': 'hypothesis|question|status|reason',
    'results/tables/immune_contrasts.csv': 'experiment_id|endpoint|contrast|first_group|second_group|n_first|n_second|mean_first|mean_second|mean_difference|standard_error|ci_low|ci_high|confidence_level|t_statistic|degrees_freedom|p_value|method|scale|effect_units|family|family_size|interpretation|q_value',
    'results/tables/immune_missingness.csv': 'experiment_id|group|endpoint|assay_domain|selected_endpoint|n_source_animals|n_observed|n_missing|missing_source_ids_json|missing_reason',
    'results/tables/immune_missingness_bounds.csv': 'experiment_id|endpoint|contrast|first_group|second_group|n_source_first|n_source_second|n_observed_first|n_observed_second|n_missing_first|n_missing_second|observed_sum_first|observed_sum_second|support_lower|support_upper|lower_mean_difference|upper_mean_difference|bound_status|missing_source_ids_first_json|missing_source_ids_second_json|effect_units|target|assumption|interpretation',
    'results/tables/immune_rank_effects.csv': 'experiment_id|endpoint|contrast|first_group|second_group|n_observed_first|n_observed_second|n_observed_animals|cross_group_pair_count|direct_first_greater_pairs|direct_tied_pairs|direct_first_less_pairs|mann_whitney_u_first_midrank|mann_whitney_u_first_direct|existing_sensitivity_u_first|existing_u_verified|empirical_probability_first_greater_plus_half_ties|rank_biserial_first_minus_second|target|interpretation',
    'results/tables/immune_sensitivity.csv': _SENSITIVITY,
    'results/tables/immune_summary.csv': 'experiment_id|endpoint|group|n_source_animals|n_observed|n_missing|mean|standard_deviation|median|minimum|maximum|scale|units',
    'results/tables/original_method_replication.csv': 'experiment_id|endpoint|record_type|contrast|group_first|group_second|n_first|n_second|n_total|group_mean|group_variance|group_sse|residual_sse|pooled_mse|residual_df|numerator_df|effect|standard_error|statistic|statistic_name|p_value|ci_low|ci_high|confidence_level|interval_scope|comparison_family_size|coefficients_json|source_units|effect_units|published_reference|published_n|published_mean|published_mean_decimals|computed_mean_at_published_precision|published_t|published_t_decimals|published_p_value|published_p_relation|published_p_decimals|published_planned_bh_q|original_bh_family_status|published_agreement|interpretation',
    'results/tables/sample_linkage_audit.csv': 'sample_id|mouse_id|pool_id|experiment_id|group|timepoint|virome_available|bacteriome_available|immune_available|behavior_available|matched_assays|linkage_confidence|sample_type|source|run_id|metadata_candidate_mouse_id|note|raw_reads_deposited',
    'results/tables/sequencing_inventory.csv': 'accession|sample_type|run_count|sample_count|fastq_file_count|compressed_fastq_bytes|compressed_fastq_gb_decimal|source|analysis_role',
    'results/tables/software_calibration.csv': 'purpose|scenario|scenario_description|endpoint|contrast|metric|successes|replicates|estimate|mc_ci_low|mc_ci_high|mc_interval_method|nominal_probability|alpha|group_0_n|group_1_n|group_2_n|seed|scenario_stream_index|rng|batch_size|max_actual_batch_size|batches|all_null|endpoint_dependence|numpy_version|scipy_version',
    'results/tables/source_inventory.csv': 'experiment_id|source_sheet|source_max_row|source_column_count|phenotype_column_count|nonempty_animal_rows|fully_blank_rows_excluded|observed_phenotype_cells|missing_phenotype_cells|group_counts_json|identifier_scope|virome_linkage_verified',
    'results/tables/immune_design_membership.csv': 'experiment_id|group|source_id|mouse_id|source_sheet|source_row|id_range_block|putative_control_cage_id|block_verified|cage_verified|posthoc_status|assumption_status|block_basis|cage_basis',
    'results/tables/immune_block_adjusted.csv': _POSTHOC_COMMON+'|n_first|n_second|n_model_observed|'+_HC3+'|method|model_formula|id_block_B_minus_A_estimate|covariance_scope|model_assumptions|'+_UNADJUSTED_HC3+'|unadjusted_comparator_scope|'+_POSTHOC_BH,
    'results/tables/immune_within_block.csv': _POSTHOC_COMMON+'|id_range_block|'+_WELCH+'|overall_raw_mean_difference|same_direction_as_overall_raw|method|'+_POSTHOC_BH,
    'results/tables/immune_putative_cage_units.csv': 'experiment_id|endpoint|group|putative_control_cage_id|source_ids_json|observed_source_ids_json|n_source_animals|n_observed_animals|unit_mean|observation_status|posthoc_status|assumption_status|weighting',
    'results/tables/immune_putative_cage_means.csv': _POSTHOC_COMMON+'|'+_WELCH+'|n_observed_animals_first|n_observed_animals_second|first_unit|second_unit|n_putative_control_cages|method|estimand|'+_POSTHOC_BH,
    'results/tables/immune_control_cage_omission.csv': _POSTHOC_COMMON+'|omitted_group|omitted_putative_control_cage_id|omitted_source_ids_json|'+_WELCH+'|method|omission_scope|'+_POSTHOC_BH,
    'results/tables/immune_tnfa_log_sensitivity.csv': _POSTHOC_COMMON+'|geometric_mean_first|geometric_mean_second|geometric_mean_ratio|ratio_ci_low|ratio_ci_high|n_first|n_second|log_mean_difference|log_standard_error|log_ci_low|log_ci_high|t_statistic|degrees_freedom|p_value|confidence_level|raw_mean_difference|raw_ci_low|raw_ci_high|raw_p_value|raw_effect_units|log_effect_units|method|ratio_units|geometric_mean_units|positivity_policy|raw_comparator_scope|'+_POSTHOC_BH,
    'results/tables/sequencing_design_inventory.csv': 'accession|source_condition|specimen_role|gavage_status|run_count|specimen_count|fastq_file_count|compressed_fastq_bytes|source',
    'results/tables/candidate_recipient_pairs.csv': 'workbook_sheet|workbook_row|workbook_group|workbook_id|ena_sample_type|replicate_num|before_sample_accessions|before_run_accessions|before_specimen_count|before_run_count|before_fastq_file_count|before_compressed_fastq_bytes|after_sample_accessions|after_run_accessions|after_specimen_count|after_run_count|after_fastq_file_count|after_compressed_fastq_bytes|total_run_count|total_compressed_fastq_bytes|candidate_status|linkage_status|processed_virome_profiles_retrieved|verified_virome_immune_matches',
}
CSV_HEADERS = MappingProxyType({path: tuple(value.split('|')) for path, value in _HEADERS.items()})
_SENSITIVITY_DERIVED = 'mann_whitney_p_value loo_mean_difference_min loo_mean_difference_max loo_p_value_min loo_p_value_max mann_whitney_q_value_sensitivity_family'
_WELCH_DERIVED = 'mean_first mean_second mean_difference standard_error ci_low ci_high t_statistic degrees_freedom p_value'
_HC3_DERIVED = 'mean_difference standard_error t_statistic p_value ci_low ci_high'
_DERIVED = {
    'figure7_data.csv': _SENSITIVITY_DERIVED + ' full_mean_difference welch_p_value welch_q_value',
    'figure8_data.csv': 'mean_difference ci_low ci_high p_value',
    'immune_contrasts.csv': 'mean_first mean_second mean_difference standard_error ci_low ci_high t_statistic degrees_freedom p_value q_value',
    'immune_missingness_bounds.csv': 'observed_sum_first observed_sum_second lower_mean_difference upper_mean_difference',
    'immune_rank_effects.csv': 'empirical_probability_first_greater_plus_half_ties rank_biserial_first_minus_second',
    'immune_sensitivity.csv': _SENSITIVITY_DERIVED,
    'immune_summary.csv': 'mean standard_deviation median',
    'original_method_replication.csv': 'group_mean group_variance group_sse residual_sse pooled_mse effect standard_error statistic p_value ci_low ci_high',
    'software_calibration.csv': 'estimate mc_ci_low mc_ci_high',
    'immune_block_adjusted.csv': _HC3_DERIVED+' id_block_B_minus_A_estimate '
        +' '.join('unadjusted_hc3_'+column for column in _HC3_DERIVED.split())+' q_value',
    'immune_within_block.csv': _WELCH_DERIVED+' overall_raw_mean_difference q_value',
    'immune_putative_cage_units.csv': 'unit_mean',
    'immune_putative_cage_means.csv': _WELCH_DERIVED+' q_value',
    'immune_control_cage_omission.csv': _WELCH_DERIVED+' q_value',
    'immune_tnfa_log_sensitivity.csv': 'geometric_mean_first geometric_mean_second geometric_mean_ratio ratio_ci_low ratio_ci_high log_mean_difference log_standard_error log_ci_low log_ci_high t_statistic degrees_freedom p_value raw_mean_difference raw_ci_low raw_ci_high raw_p_value q_value',
}
DERIVED_COLUMNS = MappingProxyType({path: frozenset(_DERIVED.get(Path(path).name, '').split()) for path in CSV_HEADERS})
# Numeric validation never changes comparison types. These columns remain exact.
_EXACT_NUMERIC = {
    'immune_long.csv': 'source_row source_column value',
    'figure4_data.csv': 'source_row source_column value',
    'archive_files.csv': 'bytes',
    'figure1_data.csv': 'count', 'figure5_data.csv': 'count',
    'figure7_data.csv': 'mann_whitney_u_first loo_n_refits',
    'immune_contrasts.csv': 'n_first n_second confidence_level family_size',
    'immune_missingness.csv': 'n_source_animals n_observed n_missing',
    'immune_missingness_bounds.csv': 'n_source_first n_source_second n_observed_first n_observed_second n_missing_first n_missing_second support_lower support_upper',
    'immune_rank_effects.csv': 'n_observed_first n_observed_second n_observed_animals cross_group_pair_count direct_first_greater_pairs direct_tied_pairs direct_first_less_pairs mann_whitney_u_first_midrank mann_whitney_u_first_direct existing_sensitivity_u_first',
    'immune_sensitivity.csv': 'mann_whitney_u_first loo_n_refits',
    'immune_summary.csv': 'n_source_animals n_observed n_missing minimum maximum',
    'original_method_replication.csv': 'n_first n_second n_total residual_df numerator_df confidence_level comparison_family_size published_n published_mean published_mean_decimals computed_mean_at_published_precision published_t published_t_decimals published_p_value published_p_decimals published_planned_bh_q',
    'sequencing_inventory.csv': 'run_count sample_count fastq_file_count compressed_fastq_bytes compressed_fastq_gb_decimal',
    'software_calibration.csv': 'successes replicates nominal_probability alpha group_0_n group_1_n group_2_n seed scenario_stream_index batch_size max_actual_batch_size batches',
    'source_inventory.csv': 'source_max_row source_column_count phenotype_column_count nonempty_animal_rows fully_blank_rows_excluded observed_phenotype_cells missing_phenotype_cells',
    'immune_design_membership.csv': 'source_row',
    'immune_block_adjusted.csv': 'n_first n_second n_model_observed degrees_freedom confidence_level unadjusted_hc3_degrees_freedom unadjusted_hc3_confidence_level bh_family_size',
    'immune_within_block.csv': 'n_first n_second confidence_level bh_family_size',
    'immune_putative_cage_units.csv': 'n_source_animals n_observed_animals',
    'immune_putative_cage_means.csv': 'n_first n_second confidence_level n_observed_animals_first n_observed_animals_second n_putative_control_cages bh_family_size',
    'immune_control_cage_omission.csv': 'n_first n_second confidence_level bh_family_size',
    'immune_tnfa_log_sensitivity.csv': 'n_first n_second confidence_level bh_family_size',
    'sequencing_design_inventory.csv': 'run_count specimen_count fastq_file_count compressed_fastq_bytes',
    'candidate_recipient_pairs.csv': 'workbook_row before_specimen_count before_run_count before_fastq_file_count before_compressed_fastq_bytes after_specimen_count after_run_count after_fastq_file_count after_compressed_fastq_bytes total_run_count total_compressed_fastq_bytes processed_virome_profiles_retrieved verified_virome_immune_matches',
}
NUMERIC_COLUMNS = MappingProxyType({path: DERIVED_COLUMNS[path] | frozenset(_EXACT_NUMERIC.get(Path(path).name, '').split()) for path in CSV_HEADERS})
FIGURE_PATHS = tuple(sorted(f'figures/{name}.{extension}' for name in
    ('figure1_design', 'figure4_immune', 'figure5_linkage_limit', 'figure7_robustness', 'figure8_method_comparison')
    for extension in ('png', 'pdf')))
EXPECTED_PATHS = tuple(sorted((*CSV_HEADERS, *FIGURE_PATHS)))


def comparison_plan():
    """Serializable fixed plan, suitable for freezing before either analysis."""
    plan = {'schema_version': 1, 'expected_paths': list(EXPECTED_PATHS),
        'absolute_tolerance': str(ABS_TOLERANCE), 'relative_tolerance': str(REL_TOLERANCE),
        'numeric_rule': 'absolute_difference <= 1e-10 OR absolute_difference/max(abs(reference),abs(reproduced)) <= 1e-12',
        'exact_policy': 'headers, row order, all other fields, IDs, source values, counts, JSON text and publication references exact',
        'figure_policy': 'SHA-256 exact; changed PNG/PDF requires visual review',
        'bounds': {'csv_bytes': MAX_CSV_BYTES, 'data_rows': MAX_ROWS,
            'figure_bytes': MAX_FIGURE_BYTES,
            'field_characters': MAX_FIELD_CHARACTERS, 'recorded_differences_per_file': MAX_RECORDED_DIFFERENCES},
        'csv_schemas': {path: {'header': list(CSV_HEADERS[path]),
            'tolerated_columns': sorted(DERIVED_COLUMNS[path]),
            'finite_numeric_columns': sorted(NUMERIC_COLUMNS[path])} for path in sorted(CSV_HEADERS)}}
    plan['sha256'] = hashlib.sha256(json.dumps(plan, sort_keys=True, separators=(',', ':'), allow_nan=False).encode()).hexdigest()
    return plan


def _digest(path):
    value = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(65536), b''):
            value.update(block)
    return value.hexdigest()


def _number(value):
    # Do not apply this to IDs or arbitrary text. Blank means not applicable.
    if value == '':
        return None
    try:
        result = Decimal(value)
        if not result.is_finite() or not math.isfinite(float(value)):
            raise ValueError('nonfinite numeric value')
        return result
    except (ArithmeticError, ValueError) as error:
        raise ValueError(f'Invalid finite numeric field: {value!r}') from error


def _reject_json_constant(value):
    raise ValueError(f'Nonfinite JSON constant: {value}')


def compare_csv(reference, reproduced, allowed_columns):
    """Compare one known schema; caller may narrow, never broaden its whitelist.

    Numeric maxima are decimal strings, avoiding overflowing JSON floats. Row
    numbers are one-based data rows. Every changed field is counted, with a
    bounded detail sample; equal numeric cells are also validated for finiteness.
    """
    reference, reproduced = Path(reference), Path(reproduced)
    names = {Path(path).name: path for path in CSV_HEADERS}
    if reference.name != reproduced.name or reference.name not in names:
        raise ValueError('Unknown or mismatched scientific CSV schema')
    schema = names[reference.name]
    allowed = frozenset(allowed_columns)
    if not allowed <= DERIVED_COLUMNS[schema]:
        raise ValueError('Tolerance whitelist includes an unknown or protected column')
    for path in (reference, reproduced):
        if path.stat().st_size > MAX_CSV_BYTES:
            raise ValueError('CSV byte bound exceeded')
    hashes = [_digest(path) for path in (reference, reproduced)]
    report = {'schema': schema, 'reference_sha256': hashes[0], 'reproduced_sha256': hashes[1],
        'byte_identical': hashes[0] == hashes[1], 'semantic_match': True,
        'absolute_tolerance': str(ABS_TOLERANCE), 'relative_tolerance': str(REL_TOLERANCE),
        'allowed_columns': sorted(allowed), 'reference_rows': 0, 'reproduced_rows': 0,
        'changed_fields': 0, 'tolerated_numeric_fields': 0, 'disallowed_fields': 0,
        'changed_rows': 0, 'disallowed_rows': 0, 'differences': []}
    report['numeric_difference_scope'] = 'explicitly allowed derived columns; other numeric fields remain exact'
    maximum_absolute = maximum_relative = Decimal(0)
    sentinel = object()

    def detail(row, column, first, second, kind, absolute=None, relative=None):
        if len(report['differences']) < MAX_RECORDED_DIFFERENCES:
            report['differences'].append({'data_row': row, 'column': column, 'kind': kind,
                'reference': first[:2000] if isinstance(first, str) else first,
                'reproduced': second[:2000] if isinstance(second, str) else second,
                'absolute_difference': str(absolute) if absolute is not None else None,
                'relative_difference': str(relative) if relative is not None else None})

    with reference.open(encoding='utf-8', newline='') as first, reproduced.open(encoding='utf-8', newline='') as second:
        readers = [csv.reader(stream, strict=True) for stream in (first, second)]
        expected = list(CSV_HEADERS[schema])
        for reader in readers:
            if next(reader, None) != expected:
                raise ValueError('Unknown, reordered or changed CSV header: ' + schema)
        for index, pair in enumerate(zip_longest(*readers, fillvalue=sentinel), 1):
            if index > MAX_ROWS:
                raise ValueError('CSV row bound exceeded')
            changed = disallowed = False
            for side, row in enumerate(pair):
                if row is sentinel:
                    continue
                report['reference_rows' if side == 0 else 'reproduced_rows'] += 1
                if len(row) != len(expected):
                    raise ValueError(f'CSV row width mismatch: {schema}, row {index}')
                for column, value in zip(expected, row):
                    if len(value) > MAX_FIELD_CHARACTERS:
                        raise ValueError('CSV field bound exceeded')
                    if column in NUMERIC_COLUMNS[schema]:
                        try:
                            _number(value)
                        except ValueError as error:
                            raise ValueError(f'{schema}, data row {index}, column {column}: {error}') from error
                    if value and (column.endswith('_json') or column == 'metadata_candidate_mouse_id'):
                        json.loads(value, parse_constant=_reject_json_constant, parse_float=_number)
            if sentinel in pair:
                report['changed_rows'] += 1
                report['disallowed_rows'] += 1
                report['semantic_match'] = False
                detail(index, None, None, None, 'missing_reference_row' if pair[0] is sentinel else 'missing_reproduced_row')
                continue
            for column, left, right in zip(expected, *pair):
                if left == right:
                    continue
                changed = True
                report['changed_fields'] += 1
                accepted = False
                absolute = relative = None
                if column in allowed and left != '' and right != '':
                    with localcontext() as context:
                        context.prec = 50
                        a, b = _number(left), _number(right)
                        absolute = abs(a-b)
                        denominator = max(abs(a), abs(b))
                        relative = absolute / denominator if denominator else Decimal(0)
                        accepted = absolute <= ABS_TOLERANCE or relative <= REL_TOLERANCE
                        maximum_absolute = max(maximum_absolute, absolute)
                        maximum_relative = max(maximum_relative, relative)
                if accepted:
                    report['tolerated_numeric_fields'] += 1
                else:
                    disallowed = True
                    report['disallowed_fields'] += 1
                    report['semantic_match'] = False
                detail(index, column, left, right, 'within_numeric_tolerance' if accepted else
                    'outside_numeric_tolerance' if column in allowed else 'exact_field_changed', absolute, relative)
            report['changed_rows'] += int(changed)
            report['disallowed_rows'] += int(disallowed)
    report['max_absolute_difference'] = str(maximum_absolute)
    report['max_relative_difference'] = str(maximum_relative)
    report['differences_truncated'] = report['changed_fields'] + abs(report['reference_rows']-report['reproduced_rows']) > len(report['differences'])
    report['status'] = 'different_csv' if not report['semantic_match'] else 'identical_bytes' if report['byte_identical'] else 'equivalent_csv'
    if hashes != [_digest(path) for path in (reference, reproduced)]:
        raise ValueError('CSV changed during comparison')
    return report


def compare_roots(reference_root, reproduced_root):
    """Require the fixed complete inventory; reuse the existing discovery policy."""
    from .reproduction import contained_path, scientific_paths
    reference_root, reproduced_root = Path(reference_root).resolve(), Path(reproduced_root).resolve()
    inventories = [set(scientific_paths(root)) for root in (reference_root, reproduced_root)]
    expected = set(EXPECTED_PATHS)
    inventory_match = all(value == expected for value in inventories)
    comparisons = []
    for relative in sorted(expected | inventories[0] | inventories[1]):
        result = {'path': relative}
        if relative not in expected:
            result['status'] = 'unexpected_output'
        elif not all(relative in inventory for inventory in inventories):
            result['status'] = 'missing_output'
        else:
            try:
                paths = [contained_path(root, relative) for root in (reference_root, reproduced_root)]
                if relative in CSV_HEADERS:
                    result.update(compare_csv(*paths, DERIVED_COLUMNS[relative]))
                else:
                    if any(path.stat().st_size > MAX_FIGURE_BYTES for path in paths):
                        raise ValueError('Figure byte bound exceeded')
                    hashes = [_digest(path) for path in paths]
                    result.update(reference_sha256=hashes[0], reproduced_sha256=hashes[1],
                        byte_identical=hashes[0] == hashes[1],
                        status='identical_bytes' if hashes[0] == hashes[1] else 'needs_visual_review')
            except (OSError, ValueError, csv.Error) as error:
                result.update(status='invalid_output', error=str(error))
        comparisons.append(result)
    csv_match = inventory_match and all(row.get('semantic_match', False) for row in comparisons if row['path'] in CSV_HEADERS)
    visual_review = any(row['status'] == 'needs_visual_review' for row in comparisons)
    passed = inventory_match and csv_match and all(row['status'] in ('identical_bytes', 'equivalent_csv') for row in comparisons)
    review_only = csv_match and visual_review and all(row['status'] in
        ('identical_bytes', 'equivalent_csv', 'needs_visual_review') for row in comparisons)
    return {'schema_version': 1, 'purpose': 'cross_platform_software_output_comparison',
        'comparison_plan': comparison_plan(), 'inventory_match': inventory_match,
        'reference_inventory': sorted(inventories[0]), 'reproduced_inventory': sorted(inventories[1]),
        'csv_semantic_match': csv_match, 'figure_visual_review_required': visual_review,
        'all_outputs_byte_identical': inventory_match and all(row.get('byte_identical', False) for row in comparisons),
        'byte_identical_outputs': sum(row.get('byte_identical', False) for row in comparisons),
        'status': 'passed' if passed else 'needs_visual_review' if review_only else 'failed',
        'comparisons': comparisons}


def compare_scientific_trees(reference_root, reproduced_root):
    """Public tree-comparison entry point; no analysis, downloads or writes."""
    return compare_roots(reference_root, reproduced_root)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('reference_root', type=Path)
    parser.add_argument('reproduced_root', type=Path)
    parser.add_argument('--output', type=Path)
    args = parser.parse_args()
    from .io import write_json
    permitted = (args.reference_root/'results/reports').resolve()
    output = args.output.resolve() if args.output else permitted/'portability_comparison.json'
    if not output.is_relative_to(permitted) or output == permitted:
        raise ValueError('Comparison report must be inside reference results/reports')
    report = compare_roots(args.reference_root, args.reproduced_root)
    write_json(output, report)
    print(json.dumps({'status': report['status'], 'report': str(output)}))
    raise SystemExit(0 if report['status'] == 'passed' else 1)


if __name__ == '__main__':
    main()
