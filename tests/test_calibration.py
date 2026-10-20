"""Small synthetic software checks; the 20,000-replicate benchmark is separate."""

from __future__ import annotations

import csv
import math
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))

from pisa.calibration import (
    GROUP_SIZES, PURPOSE, SCENARIOS, benchmark, bh_any_rejection,
    cluster_from_innovations, group_moments, run, synthetic_batch,
    vectorized_welch, wilson_interval,
)


class SoftwareCalibrationTests(unittest.TestCase):
    def test_vectorized_welch_against_independent_scipy_samples(self):
        import numpy as np
        from scipy.stats import ttest_ind

        rng = np.random.default_rng(4921)
        samples = synthetic_batch(rng, SCENARIOS[1][0], 7)
        means, variances = group_moments(samples)
        actual = vectorized_welch(means, variances)
        for replicate in range(7):
            for endpoint in range(3):
                for contrast, (first, second) in enumerate(((1, 0), (2, 1))):
                    a = samples[replicate, endpoint, first, :GROUP_SIZES[first]]
                    b = samples[replicate, endpoint, second, :GROUP_SIZES[second]]
                    reference = ttest_ind(a, b, equal_var=False)
                    interval = reference.confidence_interval()
                    key = (replicate, endpoint, contrast)
                    self.assertAlmostEqual(actual["statistic"][key], reference.statistic, places=11)
                    self.assertAlmostEqual(actual["p_value"][key], reference.pvalue, places=11)
                    self.assertAlmostEqual(actual["degrees_freedom"][key], reference.df, places=11)
                    self.assertAlmostEqual(actual["ci_low"][key], interval.low, places=10)
                    self.assertAlmostEqual(actual["ci_high"][key], interval.high, places=10)

    def test_replicate_major_generators_preserve_batches_exactly(self):
        import numpy as np

        for scenario, _ in SCENARIOS:
            with self.subTest(scenario=scenario):
                first = np.random.default_rng(6101)
                second = np.random.default_rng(6101)
                whole = synthetic_batch(first, scenario, 128)
                partitioned = np.concatenate([synthetic_batch(second, scenario, n) for n in (31, 53, 44)])
                self.assertTrue(np.array_equal(whole, partitioned))

    def test_benchmark_seed_and_batch_invariance(self):
        first = benchmark(981, replicates=128, batch_size=32)
        second = benchmark(981, replicates=128, batch_size=64)
        fields = ("purpose", "scenario", "endpoint", "contrast", "metric", "successes", "estimate", "mc_ci_low", "mc_ci_high")
        self.assertEqual([{field: row[field] for field in fields} for row in first],
                         [{field: row[field] for field in fields} for row in second])
        self.assertEqual(len(first), 64)
        self.assertTrue(all(row["purpose"] == PURPOSE for row in first))
        for scenario, _ in SCENARIOS:
            for endpoint in range(1, 4):
                for contrast in ("synthetic_group_1_minus_group_0", "synthetic_group_2_minus_group_1"):
                    rows = [row for row in first if row["scenario"] == scenario and row["endpoint"] == f"synthetic_endpoint_{endpoint}" and row["contrast"] == contrast]
                    self.assertEqual(sum(row["successes"] for row in rows), 128)

    def test_cluster_covariance_matches_analytical_contract(self):
        import numpy as np

        # Each row is one basis innovation. Its linear map supplies the exact
        # covariance under 15 independent unit-variance Gaussian innovations.
        mapping = cluster_from_innovations(np.eye(15), icc=0.5)
        covariance = mapping.T @ mapping
        expected = np.eye(10)
        for first in range(0, 10, 2):
            expected[first, first + 1] = expected[first + 1, first] = 0.5
        self.assertTrue(np.allclose(covariance, expected, atol=1e-14, rtol=0))
        self.assertEqual(covariance[:9, :9].shape, (9, 9))
        self.assertAlmostEqual(covariance[8, 8], 1)
        self.assertTrue(np.allclose(covariance[8, :8], 0))

    def test_wilson_matches_statsmodels_including_boundaries(self):
        from statsmodels.stats.proportion import proportion_confint

        for count, total in ((0, 128), (128, 128), (7, 128), (1001, 20000)):
            actual = wilson_interval(count, total)
            expected = proportion_confint(count, total, alpha=0.05, method="wilson")
            self.assertAlmostEqual(actual[0], expected[0], places=13)
            self.assertAlmostEqual(actual[1], expected[1], places=13)

    def test_obvious_zero_signal_and_added_signal_controls(self):
        import numpy as np

        variances = np.ones((1, 3, 3))
        null = vectorized_welch(np.zeros((1, 3, 3)), variances)
        self.assertTrue(np.array_equal(null["p_value"], np.ones((1, 3, 2))))
        self.assertFalse(bh_any_rejection(null["p_value"].reshape(1, 6))[0])
        # Added synthetic signal verifies orientation and detection plumbing;
        # it is not used for a scientific effect-size or power calculation.
        alternative = vectorized_welch(np.array([[[0.0, 20.0, 0.0]] * 3]), variances)
        self.assertTrue(np.all(alternative["mean_difference"][..., 0] > 0))
        self.assertTrue(np.all(alternative["mean_difference"][..., 1] < 0))
        self.assertTrue(bh_any_rejection(alternative["p_value"].reshape(1, 6))[0])

    def test_invalid_and_bounded_settings(self):
        import numpy as np

        with self.assertRaises(ValueError):
            benchmark(1, 128, 501)
        with self.assertRaises(ValueError):
            benchmark(-1, 128, 64)
        with self.assertRaises(ValueError):
            wilson_interval(129, 128)
        with self.assertRaises(ValueError):
            bh_any_rejection([[0.1, 0.2]])
        with self.assertRaises(ValueError):
            vectorized_welch(np.zeros((1, 3)), np.zeros((1, 3)))

    def test_outputs_need_no_biological_inputs_and_are_labeled(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            summary = run(root, {"seed": 910, "calibration": {"replicates": 128, "batch_size": 64}})
            self.assertEqual(summary["biological_observations_used"], 0)
            self.assertEqual(summary["purpose"], PURPOSE)
            self.assertEqual(summary["rows"], 64)
            with (root / "results/tables/software_calibration.csv").open(encoding="utf-8", newline="") as handle:
                rows = list(csv.DictReader(handle))
            self.assertTrue(all(row["purpose"] == PURPOSE and row["replicates"] == "128" for row in rows))
            self.assertFalse((root / "data").exists())


if __name__ == "__main__":
    unittest.main()
