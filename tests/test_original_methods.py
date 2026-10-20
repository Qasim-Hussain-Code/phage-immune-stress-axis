"""Original-method checks against independent OLS and Tukey implementations.

Synthetic fixtures verify the calculations. A separate explicitly labeled test
checks the cached real source observations against published rounded captions.
"""

from __future__ import annotations

import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pisa.original_methods import ENDPOINTS, GROUPS, PUBLISHED, pooled_analysis, result_rows, rounded_agreement, run


class OriginalMethodSyntheticTests(unittest.TestCase):
    @staticmethod
    def fixture():
        return {"ctr": [1, 2, 4, 8, 11], "ctr_stress": [0, 2, 3, 4], "fvt_stress": [2, 4, 6, 7, 9, 14]}

    def test_anova_and_contrast_against_independent_ols(self):
        import numpy as np
        import statsmodels.api as sm

        groups = self.fixture()
        values = np.array([value for group in GROUPS for value in groups[group]], dtype=float)
        design = np.array([[1, group == "ctr_stress", group == "fvt_stress"]
                           for group in GROUPS for _ in groups[group]], dtype=float)
        reference = sm.OLS(values, design).fit()
        contrast = reference.t_test([0, 1, -0.5])
        actual = pooled_analysis(groups)
        self.assertAlmostEqual(actual["residual_sse"], reference.ssr, places=10)
        self.assertAlmostEqual(actual["pooled_mse"], reference.mse_resid, places=10)
        self.assertEqual(actual["residual_df"], reference.df_resid)
        self.assertAlmostEqual(actual["anova"]["statistic"], reference.fvalue, places=10)
        self.assertAlmostEqual(actual["anova"]["p_value"], reference.f_pvalue, places=10)
        planned = actual["planned_contrast"]
        self.assertAlmostEqual(planned["effect"], contrast.effect.item(), places=10)
        self.assertAlmostEqual(planned["standard_error"], contrast.sd.item(), places=10)
        self.assertAlmostEqual(planned["statistic"], contrast.tvalue.item(), places=10)
        self.assertAlmostEqual(planned["p_value"], contrast.pvalue.item(), places=10)
        self.assertAlmostEqual(planned["ci_low"], contrast.conf_int()[0, 0], places=10)
        self.assertAlmostEqual(planned["ci_high"], contrast.conf_int()[0, 1], places=10)

    def test_tukey_against_statsmodels_for_unequal_group_sizes(self):
        from statsmodels.stats.multicomp import pairwise_tukeyhsd

        groups = self.fixture()
        values = [value for group in GROUPS for value in groups[group]]
        labels = [group for group in GROUPS for _ in groups[group]]
        reference = pairwise_tukeyhsd(values, labels, alpha=0.05)
        actual = pooled_analysis(groups)
        # statsmodels enumerates alphabetical group pairs and reports second
        # group minus first. Our pairs use that same effect direction.
        indices = [(0, 1), (0, 2), (1, 2)]
        for index, (second_index, first_index) in enumerate(indices):
            first, second = GROUPS[first_index], GROUPS[second_index]
            pair = next(row for row in actual["pairs"] if row["group_first"] == first and row["group_second"] == second)
            self.assertAlmostEqual(pair["effect"], reference.meandiffs[index], places=10)
            self.assertAlmostEqual(pair["p_value"], reference.pvalues[index], places=9)
            self.assertAlmostEqual(pair["ci_low"], reference.confint[index, 0], places=9)
            self.assertAlmostEqual(pair["ci_high"], reference.confint[index, 1], places=9)

    def test_planned_contrast_is_not_conjunction_of_pairwise_effects(self):
        groups = {"ctr": [9, 10, 11], "ctr_stress": [9, 10, 11], "fvt_stress": [19, 20, 21]}
        actual = pooled_analysis(groups)
        stress = next(row for row in actual["pairs"] if row["contrast"] == "ctr_stress_minus_ctr")
        self.assertEqual(stress["effect"], 0)
        self.assertAlmostEqual(stress["p_value"], 1)
        self.assertLess(actual["planned_contrast"]["p_value"], 0.05)

    def test_invalid_groups_and_degenerate_variance(self):
        invalid = [
            {"ctr": [1, 2], "ctr_stress": [2, 3]},
            {"ctr": [1], "ctr_stress": [2, 3], "fvt_stress": [4, 5]},
            {"ctr": [1, math.nan], "ctr_stress": [2, 3], "fvt_stress": [4, 5]},
            {"ctr": [1, 1], "ctr_stress": [2, 2], "fvt_stress": [3, 3]},
        ]
        for groups in invalid:
            with self.subTest(groups=groups), self.assertRaises(ValueError):
                pooled_analysis(groups)
        with self.assertRaises(ValueError):
            pooled_analysis(self.fixture(), confidence=1)

    def test_published_rounding_is_explicit(self):
        self.assertTrue(rounded_agreement(0.1064091013, 0.106, 3))
        self.assertFalse(rounded_agreement(0.0126452597, 0.106, 3))
        self.assertTrue(rounded_agreement(-2.866926809, -2.867, 3))

    def test_contrast_covariance_depends_on_unequal_sizes(self):
        c, d = (-0.5, 1, -0.5), (-1, 0, 1)
        self.assertEqual(sum(a * b for a, b in zip(c, d)), 0)
        sizes = (10, 10, 9)
        self.assertNotEqual(sum(a * b / n for a, b, n in zip(c, d, sizes)), 0)
        balanced = (10, 10, 10)
        self.assertEqual(sum(a * b / n for a, b, n in zip(c, d, balanced)), 0)


class OriginalMethodRealDataVerification(unittest.TestCase):
    def test_cached_source_matches_published_caption_without_extra_exclusions(self):
        """This is real-source verification, separate from synthetic unit tests."""
        source_root = Path(__file__).resolve().parents[1]
        source_path = source_root / "data/processed/immune_long.csv"
        if not source_path.exists():
            self.skipTest("Frozen source inputs not prepared; run stages 01 through 06")
        original_welch = source_root / "results/tables/immune_contrasts.csv"
        before = original_welch.read_bytes() if original_welch.exists() else None
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            target = root / "data/processed/immune_long.csv"
            target.parent.mkdir(parents=True)
            target.write_bytes(source_path.read_bytes())
            result = run(root, {})
            self.assertEqual(result["rows"], 24)
            self.assertEqual(result["published_checks"], 18)
            self.assertEqual(result["published_matches"], 17)
            self.assertEqual(result["published_mismatches"], 1)
            self.assertEqual(result["source_group_summary_checks"], 9)
            self.assertEqual(result["source_group_summary_matches"], 8)
            self.assertEqual(result["caption_statistic_checks"], 9)
            self.assertEqual(result["caption_statistic_matches"], 9)
            self.assertEqual(result["additional_observations_excluded"], 0)
            self.assertFalse(result["original_bh_reproduced"])
            with (root / "results/tables/original_method_replication.csv").open(newline="", encoding="utf-8") as handle:
                rows = list(csv.DictReader(handle))
            for endpoint in ENDPOINTS:
                pairs = [row for row in rows if row["endpoint"] == endpoint and row["record_type"] == "tukey_kramer"]
                self.assertEqual(len(pairs), 3)
                self.assertTrue(all(row["comparison_family_size"] == "3" for row in pairs))
                planned = next(row for row in rows if row["endpoint"] == endpoint and row["record_type"] == "planned_contrast")
                self.assertTrue(rounded_agreement(float(planned["statistic"]), PUBLISHED[endpoint]["t"], PUBLISHED[endpoint]["t_decimals"]))
                self.assertEqual(planned["published_agreement"], "matches_published_precision")
            mismatches = [row for row in rows if row["published_agreement"] == "mismatch"]
            self.assertEqual(len(mismatches), 1)
            mismatch = mismatches[0]
            self.assertEqual(mismatch["record_type"], "group")
            self.assertEqual(mismatch["endpoint"], "tnfa_splenocyte_unstimulated")
            self.assertEqual(mismatch["group_first"], "fvt_stress")
            self.assertAlmostEqual(float(mismatch["group_mean"]), 27.84927777777778)
            self.assertEqual(mismatch["computed_mean_at_published_precision"], "27.8")
            self.assertEqual(float(mismatch["published_mean"]), 27.9)
        if before is not None:
            self.assertEqual(original_welch.read_bytes(), before)


if __name__ == "__main__":
    unittest.main()
