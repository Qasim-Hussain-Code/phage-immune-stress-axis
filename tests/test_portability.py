"""Synthetic software fixtures for a prespecified cross-platform comparator."""
import csv
from decimal import Decimal
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from pisa import portability as p


class PortabilityContracts(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.reference = self.root/'reference'
        self.copy = self.root/'copy'

    def table(self, root, schema, rows, newline='\n'):
        path = root/schema
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open('w', encoding='utf-8', newline='') as stream:
            writer = csv.DictWriter(stream, fieldnames=p.CSV_HEADERS[schema], lineterminator=newline)
            writer.writeheader()
            for row in rows:
                writer.writerow(dict.fromkeys(p.CSV_HEADERS[schema], '') | row)
        return path

    def compare(self, schema, first, second, newline='\n', allowed=None):
        a = self.table(self.reference, schema, first)
        b = self.table(self.copy, schema, second, newline)
        return p.compare_csv(a, b, p.DERIVED_COLUMNS[schema] if allowed is None else allowed)

    def test_exact_bytes_and_newline_only_semantic_equality_are_distinct(self):
        schema = 'data/processed/immune_long.csv'
        row = {'source_id': '001.10', 'mouse_id': 'synthetic|001.10', 'value': '1.25'}
        self.assertTrue(self.compare(schema, [row], [row])['byte_identical'])
        result = self.compare(schema, [row], [row], newline='\r\n')
        self.assertTrue(result['semantic_match'])
        self.assertFalse(result['byte_identical'])
        self.assertEqual(result['status'], 'equivalent_csv')
        self.assertNotEqual(result['reference_sha256'], result['reproduced_sha256'])
        self.assertEqual(result['changed_fields'], 0)

    def test_absolute_and_relative_boundaries_are_fixed_or_conditions(self):
        schema = 'results/tables/immune_contrasts.csv'
        for first, second, expected in [('1', '1.0000000001', True),
                ('1', '1.00000000010001', False),
                ('1000000', '1000000.000001', True),
                ('1000000', '1000000.000002', False), ('0', '0.0000000001', True)]:
            with self.subTest(first=first, second=second):
                result = self.compare(schema, [{'mean_difference': first}], [{'mean_difference': second}])
                self.assertEqual(result['semantic_match'], expected)
                self.assertFalse(result['byte_identical'])
                self.assertEqual(result['changed_fields'], 1)
                self.assertEqual(result['tolerated_numeric_fields'], int(expected))
                self.assertEqual(result['differences'][0]['column'], 'mean_difference')
                self.assertGreater(Decimal(result['max_absolute_difference']), 0)
        reverse = self.compare(schema, [{'mean_difference': '1000000.000001'}], [{'mean_difference': '1000000'}])
        self.assertTrue(reverse['semantic_match'])

    def test_ids_source_values_counts_json_and_publication_fields_remain_exact(self):
        cases = [
            ('data/processed/immune_long.csv', 'source_id', '1.1', '1.10'),
            ('data/processed/immune_long.csv', 'value', '3.31', '3.31000000000001'),
            ('results/tables/figure4_data.csv', 'value', '3.31', '3.31000000000001'),
            ('results/tables/immune_contrasts.csv', 'n_first', '10', '10.0'),
            ('results/tables/software_calibration.csv', 'successes', '1000', '1000.000000000001'),
            ('results/tables/immune_missingness.csv', 'missing_source_ids_json', '["001"]', '[ "001" ]'),
            ('results/tables/original_method_replication.csv', 'published_mean', '27.9', '27.900000000001'),
            ('results/tables/original_method_replication.csv', 'computed_mean_at_published_precision', '27.8', '27.800000000001'),
        ]
        for schema, column, first, second in cases:
            with self.subTest(column=column):
                result = self.compare(schema, [{column: first}], [{column: second}])
                self.assertFalse(result['semantic_match'])
                self.assertEqual(result['differences'][0]['kind'], 'exact_field_changed')
        # Literal IDs are never auto-typed, including numeric-looking strings.
        self.assertTrue(self.compare('data/processed/immune_long.csv',
            [{'source_id': 'NaN'}], [{'source_id': 'NaN'}])['semantic_match'])

    def test_nonfinite_values_are_rejected_even_when_bytes_match(self):
        for schema, column in [('data/processed/immune_long.csv', 'value'),
                ('results/tables/immune_contrasts.csv', 'p_value'),
                ('results/tables/software_calibration.csv', 'successes')]:
            for value in ('NaN', 'Infinity', '-Infinity', '1e309', 'not a number'):
                with self.subTest(column=column, value=value), self.assertRaises(ValueError):
                    self.compare(schema, [{column: value}], [{column: value}])
        for value in ('{"x":NaN}', '{"x":1e309}'):
            with self.subTest(json_value=value), self.assertRaises(ValueError):
                self.compare('results/tables/source_inventory.csv',
                    [{'group_counts_json': value}], [{'group_counts_json': value}])

    def test_header_row_order_row_count_and_row_width_are_enforced(self):
        schema = 'results/tables/immune_summary.csv'
        rows = [{'group': 'synthetic_a', 'mean': '1'}, {'group': 'synthetic_b', 'mean': '2'}]
        self.assertFalse(self.compare(schema, rows, list(reversed(rows)))['semantic_match'])
        missing = self.compare(schema, rows, rows[:1])
        self.assertFalse(missing['semantic_match'])
        self.assertEqual((missing['reference_rows'], missing['reproduced_rows']), (2, 1))
        a = self.table(self.reference, schema, rows)
        b = self.table(self.copy, schema, rows)
        b.write_text('unknown,mean\nsynthetic,1\n')
        with self.assertRaises(ValueError):
            p.compare_csv(a, b, p.DERIVED_COLUMNS[schema])
        b.write_text(','.join(p.CSV_HEADERS[schema])+'\nwrong,width\n')
        with self.assertRaises(ValueError):
            p.compare_csv(a, b, p.DERIVED_COLUMNS[schema])

    def test_unknown_schema_and_broadened_whitelist_fail_closed(self):
        schema = 'results/tables/immune_contrasts.csv'
        a = self.table(self.reference, schema, [{'n_first': '10'}])
        b = self.table(self.copy, schema, [{'n_first': '10'}])
        with self.assertRaises(ValueError):
            p.compare_csv(a, b, {'n_first'})
        a = a.rename(a.with_name('unknown.csv'))
        b = b.rename(b.with_name('unknown.csv'))
        with self.assertRaises(ValueError):
            p.compare_csv(a, b, set())

    def test_bounds_limit_detail_without_hiding_total_differences(self):
        schema = 'results/tables/immune_summary.csv'
        result = self.compare(schema, [{'mean': '1'}]*110, [{'mean': '2'}]*110)
        self.assertFalse(result['semantic_match'])
        self.assertEqual(result['changed_fields'], 110)
        self.assertEqual(result['disallowed_rows'], 110)
        self.assertEqual(len(result['differences']), p.MAX_RECORDED_DIFFERENCES)
        self.assertTrue(result['differences_truncated'])
        with patch.object(p, 'MAX_CSV_BYTES', 1), self.assertRaisesRegex(ValueError, 'byte bound'):
            self.compare(schema, [{'mean': '1'}], [{'mean': '1'}])

    def populate_tree(self, root):
        for schema in p.CSV_HEADERS:
            self.table(root, schema, [])
        for name in p.FIGURE_PATHS:
            path = root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'explicit synthetic figure-byte fixture')

    def test_tree_inventory_and_figure_review_never_claim_byte_identity(self):
        self.populate_tree(self.reference)
        self.populate_tree(self.copy)
        result = p.compare_scientific_trees(self.reference, self.copy)
        self.assertEqual(result['status'], 'passed')
        self.assertTrue(result['all_outputs_byte_identical'])
        self.assertEqual(result['byte_identical_outputs'], 30)
        figure = self.copy/p.FIGURE_PATHS[0]
        figure.write_bytes(b'different synthetic figure bytes')
        result = p.compare_scientific_trees(self.reference, self.copy)
        self.assertEqual(result['status'], 'needs_visual_review')
        self.assertTrue(result['csv_semantic_match'])
        self.assertTrue(result['figure_visual_review_required'])
        self.assertFalse(result['all_outputs_byte_identical'])
        self.assertEqual(result['byte_identical_outputs'], 29)
        (self.copy/'results/tables/unplanned.csv').write_text('x\n1\n')
        self.assertEqual(p.compare_scientific_trees(self.reference, self.copy)['status'], 'failed')
        (self.copy/'results/tables/unplanned.csv').unlink()
        (self.reference/'results/tables/immune_summary.csv').unlink()
        (self.copy/'results/tables/immune_summary.csv').unlink()
        self.assertFalse(p.compare_scientific_trees(self.reference, self.copy)['inventory_match'])
        json.dumps(result, allow_nan=False)

    def test_plan_is_deterministic_and_names_every_fixed_schema(self):
        first, second = p.comparison_plan(), p.comparison_plan()
        self.assertEqual(first, second)
        self.assertEqual(len(first['csv_schemas']), 20)
        self.assertEqual(len(first['expected_paths']), 30)
        self.assertEqual(first['absolute_tolerance'], '1E-10')
        self.assertEqual(first['relative_tolerance'], '1E-12')
        for path, allowed in p.DERIVED_COLUMNS.items():
            self.assertTrue(allowed <= set(p.CSV_HEADERS[path]))
            self.assertFalse(any(column.endswith('_json') or column.startswith('published') or column.startswith('n_')
                or column in ('value', 'source_id', 'mouse_id', 'successes', 'replicates', 'seed') for column in allowed))

    def test_hard_invalid_figure_takes_precedence_over_other_visual_review(self):
        self.populate_tree(self.reference)
        self.populate_tree(self.copy)
        (self.copy/p.FIGURE_PATHS[0]).write_bytes(b'changed figure')
        (self.copy/p.FIGURE_PATHS[1]).write_bytes(b'x'*101)
        with patch.object(p, 'MAX_FIGURE_BYTES', 100):
            result = p.compare_scientific_trees(self.reference, self.copy)
        self.assertTrue(result['csv_semantic_match'])
        self.assertTrue(result['figure_visual_review_required'])
        self.assertEqual(result['status'], 'failed')
        invalid = next(row for row in result['comparisons'] if row['path'] == p.FIGURE_PATHS[1])
        self.assertEqual(invalid['status'], 'invalid_output')
        self.assertIn('Figure byte bound', invalid['error'])


if __name__ == '__main__':
    unittest.main()
