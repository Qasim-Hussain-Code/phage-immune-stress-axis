"""Independent small synthetic fixtures for descriptive phenotype checks."""

from __future__ import annotations

import csv
import itertools
import math
import sys
import tempfile
import unittest
from pathlib import Path
from statistics import mean

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pisa.immune import ENDPOINTS, LONG_FIELDS, composite_mouse_id
from pisa.phenotype_robustness import OUTPUTS, rank_effect, run, support_difference


def write_table(path, rows, fields):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=fields)
        writer.writeheader()
        writer.writerows(rows)


def read_table(path):
    with path.open(encoding="utf-8", newline="") as stream:
        return list(csv.DictReader(stream))


def pipeline_fixture(root):
    """Synthetic prepared-stage fixture; literal IDs deliberately recur by group."""
    values = {
        ENDPOINTS[0]: {"ctr": [1, 2, 3], "ctr_stress": [2, 4, 5], "fvt_stress": [4, 6, None]},
        ENDPOINTS[1]: {"ctr": [10, 20, 30], "ctr_stress": [15, 25, 35], "fvt_stress": [40, 50, None]},
        ENDPOINTS[2]: {"ctr": [10, 12, None], "ctr_stress": [30, 40, None], "fvt_stress": [4, 5, None]},
        "fixture_other_assay": {group: [1, 2, 3] for group in ("ctr", "ctr_stress", "fvt_stress")},
    }
    rows = []
    for column, (endpoint, groups) in enumerate(values.items(), 3):
        for group, measurements in groups.items():
            for index, value in enumerate(measurements, 2):
                source_id = ("1.1", "1.2", "3")[index - 2]
                rows.append(dict(zip(LONG_FIELDS, (
                    "study_ii", "synthetic fixture", index, column, f"C{index}", source_id,
                    composite_mouse_id("study_ii", group, source_id), group, group, endpoint,
                    "immune", endpoint in ENDPOINTS, "" if value is None else value,
                    "missing" if value is None else "observed",
                ))))
    write_table(root / "data/processed/immune_long.csv", rows, LONG_FIELDS)
    # These six values are hand-counted from the small fixture above.
    u_values = (7.5, 4.5, 6, 6, 4, 0)
    sensitivity = []
    for endpoint_index, endpoint in enumerate(ENDPOINTS):
        for contrast_index, contrast in enumerate(("ctr_stress_minus_ctr", "fvt_stress_minus_ctr_stress")):
            sensitivity.append({"experiment_id": "study_ii", "endpoint": endpoint, "contrast": contrast,
                                "mann_whitney_u_first": u_values[2 * endpoint_index + contrast_index]})
    write_table(root / "results/tables/immune_sensitivity.csv", sensitivity, tuple(sensitivity[0]))
    return rows, sensitivity


class SupportBoundTests(unittest.TestCase):
    def test_bounds_equal_independently_enumerated_corners(self):
        first, second = [15], [35, 65]
        # Enumerate every corner of a three-dimensional missing-outcome cube.
        differences = [mean(first + list(corner[:2])) - mean(second + [corner[2]])
                       for corner in itertools.product((0, 100), repeat=3)]
        actual = support_difference(first, 3, second, 3, (0, 100))
        self.assertAlmostEqual(actual["lower_mean_difference"], min(differences))
        self.assertAlmostEqual(actual["upper_mean_difference"], max(differences))
        self.assertEqual(actual["n_missing_first"], 2)
        self.assertEqual(actual["n_missing_second"], 1)
        complete = support_difference([10, 20], 2, [15, 25], 2, (0, 100))
        self.assertEqual(complete["lower_mean_difference"], -5)
        self.assertEqual(complete["upper_mean_difference"], -5)
        self.assertEqual(complete["bound_status"], "fully_observed_source_cohort_difference")

    def test_bounds_reversal_all_missing_and_unknown_support(self):
        forward = support_difference([1, 5], 3, [3], 2, (0, 100))
        reverse = support_difference([3], 2, [1, 5], 3, (0, 100))
        self.assertAlmostEqual(forward["lower_mean_difference"], -reverse["upper_mean_difference"])
        self.assertAlmostEqual(forward["upper_mean_difference"], -reverse["lower_mean_difference"])
        all_missing = support_difference([], 2, [], 3, (0, 100))
        self.assertEqual((all_missing["lower_mean_difference"], all_missing["upper_mean_difference"]), (-100, 100))
        unknown = support_difference([10], 2, [20], 2, None)
        self.assertEqual(unknown["lower_mean_difference"], "")
        self.assertEqual(unknown["upper_mean_difference"], "")
        self.assertIn("no_finite_bounds", unknown["bound_status"])
        known_no_missing = support_difference([10], 1, [20], 1, None)
        self.assertEqual(known_no_missing["lower_mean_difference"], -10)

    def test_invalid_counts_support_and_outcomes_fail(self):
        cases = [
            ([1, 2], 1, [3], 1, (0, 100)), ([1], 0, [3], 1, (0, 100)),
            ([1], True, [3], 1, (0, 100)), ([1], 1.0, [3], 1, (0, 100)),
            ([1], 1, [3], 1, (100, 0)), ([1], 1, [3], 1, (0, math.inf)),
            ([1], 1, [3], 1, (0,)), ([-1], 1, [3], 1, (0, 100)),
            ([1], 1, [101], 1, (0, 100)), ([math.nan], 1, [3], 1, None),
            ([True], 1, [3], 1, (0, 100)),
        ]
        for args in cases:
            with self.subTest(args=args), self.assertRaises(ValueError):
                support_difference(*args)


class RankEffectTests(unittest.TestCase):
    def test_tied_midrank_u_matches_independent_library_and_pair_counts(self):
        from scipy.stats import rankdata

        first, second = [1, 2, 2, 5], [2, 3, 5]
        reference_ranks = rankdata(first + second, method="average")
        reference_u = sum(reference_ranks[:len(first)]) - len(first) * (len(first) + 1) / 2
        # Enumerated by hand: two wins and three ties, hence U=3.5.
        actual = rank_effect(first, second, reference_u)
        self.assertEqual(actual["direct_first_greater_pairs"], 2)
        self.assertEqual(actual["direct_tied_pairs"], 3)
        self.assertEqual(actual["direct_first_less_pairs"], 7)
        self.assertEqual(actual["mann_whitney_u_first_midrank"], reference_u)
        self.assertEqual(actual["mann_whitney_u_first_direct"], 3.5)
        self.assertEqual(actual["empirical_probability_first_greater_plus_half_ties"], 3.5 / 12)
        self.assertAlmostEqual(actual["rank_biserial_first_minus_second"], -5 / 12)
        self.assertEqual(actual["n_observed_animals"], 7)
        self.assertEqual(actual["cross_group_pair_count"], 12)

    def test_rank_reversal_all_ties_and_invalid_inputs(self):
        first, second = [1, 2, 3], [2, 4]
        forward, reverse = rank_effect(first, second), rank_effect(second, first)
        self.assertAlmostEqual(forward["rank_biserial_first_minus_second"], -reverse["rank_biserial_first_minus_second"])
        self.assertAlmostEqual(forward["empirical_probability_first_greater_plus_half_ties"]
                               + reverse["empirical_probability_first_greater_plus_half_ties"], 1)
        tied = rank_effect([2, 2], [2, 2, 2])
        self.assertEqual(tied["direct_tied_pairs"], 6)
        self.assertEqual(tied["empirical_probability_first_greater_plus_half_ties"], 0.5)
        self.assertEqual(tied["rank_biserial_first_minus_second"], 0)
        for args in (([], [1]), ([1], []), ([math.inf], [1]), ([False], [1]),
                     ([1], [2], 1), ([1], [2], -1), ([1], [2], math.nan)):
            with self.subTest(args=args), self.assertRaises(ValueError):
                rank_effect(*args)


class PreparedStageFixtureTests(unittest.TestCase):
    def test_prepared_stage_fixture_outputs_are_descriptive_and_repeatable(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source_rows, _ = pipeline_fixture(root)
            primary = root / "results/tables/immune_contrasts.csv"
            primary.write_bytes(b"synthetic primary-output sentinel\r\n")
            inputs = {path: path.read_bytes() for path in (
                root / "data/processed/immune_long.csv", root / "results/tables/immune_sensitivity.csv", primary)}
            summary = run(root, {})
            self.assertEqual(summary["bounds_rows"], 6)
            self.assertEqual(summary["finite_bounds_rows"], 4)
            self.assertEqual(summary["rank_effect_rows"], 6)
            self.assertEqual(summary["new_hypothesis_tests"], 0)
            self.assertFalse(summary["primary_tables_changed"])
            bounds = read_table(root / OUTPUTS[0])
            ranks = read_table(root / OUTPUTS[1])
            self.assertTrue(all(row["n_source_first"] == "3" for row in bounds))
            self.assertTrue(all(row["existing_u_verified"] == "True" for row in ranks))
            self.assertTrue(all(row["lower_mean_difference"] == "" for row in bounds if row["endpoint"] == ENDPOINTS[2]))
            self.assertFalse(any(name in row for row in bounds + ranks for name in ("p_value", "q_value", "ci_low", "ci_high")))
            # Independently enumerate every support corner for all four finite
            # comparisons, including the two fully observed (one-corner) cases.
            for bound in bounds:
                if bound["endpoint"] == ENDPOINTS[2]:
                    continue
                first = [float(row["value"]) for row in source_rows if row["endpoint"] == bound["endpoint"]
                         and row["group"] == bound["first_group"] and row["observation_status"] == "observed"]
                second = [float(row["value"]) for row in source_rows if row["endpoint"] == bound["endpoint"]
                          and row["group"] == bound["second_group"] and row["observation_status"] == "observed"]
                missing_first, missing_second = 3 - len(first), 3 - len(second)
                differences = [mean(first + list(corner[:missing_first]))
                               - mean(second + list(corner[missing_first:]))
                               for corner in itertools.product((0, 100), repeat=missing_first + missing_second)]
                self.assertAlmostEqual(float(bound["lower_mean_difference"]), min(differences))
                self.assertAlmostEqual(float(bound["upper_mean_difference"]), max(differences))
            self.assertEqual([float(row["mann_whitney_u_first_direct"]) for row in ranks], [7.5, 4.5, 6, 6, 4, 0])
            fvt_mono = next(row for row in bounds if row["endpoint"] == ENDPOINTS[0] and row["first_group"] == "fvt_stress")
            self.assertEqual(fvt_mono["missing_source_ids_first_json"], '["3"]')
            snapshots = {path: (root / path).read_bytes() for path in OUTPUTS}
            run(root, {})
            self.assertEqual(snapshots, {path: (root / path).read_bytes() for path in OUTPUTS})
            self.assertTrue(all(path.read_bytes() == content for path, content in inputs.items()))

    def test_tampered_or_incomplete_existing_u_fails_before_outputs(self):
        for mutation in ("wrong_u", "duplicate", "missing", "nonfinite", "unknown_comparison"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                _, sensitivity = pipeline_fixture(root)
                if mutation == "wrong_u":
                    sensitivity[-1]["mann_whitney_u_first"] = 1
                elif mutation == "duplicate":
                    sensitivity.append(dict(sensitivity[0]))
                elif mutation == "missing":
                    sensitivity.pop()
                elif mutation == "nonfinite":
                    sensitivity[0]["mann_whitney_u_first"] = math.nan
                else:
                    sensitivity[0]["contrast"] = "fixture_unknown"
                write_table(root / "results/tables/immune_sensitivity.csv", sensitivity, tuple(sensitivity[0]))
                with self.assertRaises(ValueError):
                    run(root, {})
                self.assertFalse(any((root / path).exists() for path in OUTPUTS))

    def test_missing_source_endpoint_record_and_support_violation_fail(self):
        for mutation in ("missing_endpoint", "outside_support"):
            with self.subTest(mutation=mutation), tempfile.TemporaryDirectory() as directory:
                root = Path(directory)
                rows, _ = pipeline_fixture(root)
                if mutation == "missing_endpoint":
                    rows.pop(0)
                else:
                    rows[0]["value"] = 101
                write_table(root / "data/processed/immune_long.csv", rows, LONG_FIELDS)
                with self.assertRaises(ValueError):
                    run(root, {})
                self.assertFalse(any((root / path).exists() for path in OUTPUTS))


if __name__ == "__main__":
    unittest.main()
