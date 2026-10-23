"""Synthetic software calibration under five explicit all-null assumptions.

This module reads no biological observations or real cage IDs. Its Monte Carlo
intervals quantify simulation error, not uncertainty about mice. The artificial
all-group cluster scenario is a generic stress test. The additional controls-
only layout comes from an unverified interpretation of source IDs, not confirmed
cage assignments. Neither model estimates the original experiment's dependence.
"""

from __future__ import annotations

import csv
import json
import math
from functools import lru_cache
from pathlib import Path
from statistics import NormalDist


PURPOSE = "synthetic_not_biological"
GROUP_SIZES = (10, 10, 9)
N_ENDPOINTS = 3
ALPHA = 0.05
CONTROL_CLUSTER_SIZES = (2, 2, 1, 2, 2, 1)
MAX_REPLICATES = 20000
MAX_BATCH_SIZE = 500
SCENARIOS = (
    ("independent_gaussian_equal_variance", "Independent Gaussian zero means; group variances 1,1,1"),
    ("independent_gaussian_unequal_variance", "Independent Gaussian zero means; group variances 4,1,1"),
    ("independent_centered_lognormal", "Independent exp(N(0,1))-exp(0.5); identical zero means and skewed distributions"),
    ("artificial_gaussian_clusters_icc_0_5", "Artificial Gaussian random-intercept clusters in every group; ICC 0.5; five clusters, at most two observations per cluster"),
    ("hypothetical_controls_only_gaussian_clusters_icc_0_5", "Hypothetical control-only Gaussian clusters; ICC 0.5; control cluster sizes 2,2,1,2,2,1 inferred from IDs, not confirmed cages; groups 1 and 2 independent"),
)
CONTRASTS = ("synthetic_group_1_minus_group_0", "synthetic_group_2_minus_group_1")
FIELDS = (
    "purpose", "scenario", "scenario_description", "endpoint", "contrast", "metric",
    "successes", "replicates", "estimate", "mc_ci_low", "mc_ci_high", "mc_interval_method",
    "nominal_probability", "alpha", "group_0_n", "group_1_n", "group_2_n", "seed",
    "scenario_stream_index", "rng", "batch_size", "max_actual_batch_size", "batches",
    "all_null", "endpoint_dependence", "numpy_version", "scipy_version",
)


def wilson_interval(successes: int, trials: int, confidence: float = 0.95) -> tuple[float, float]:
    """Binomial Monte Carlo uncertainty, including zero and all successes."""
    if not isinstance(successes, int) or not isinstance(trials, int) or trials < 1 or not 0 <= successes <= trials:
        raise ValueError("Wilson counts require 0 <= integer successes <= positive integer trials")
    if not 0 < confidence < 1:
        raise ValueError("Confidence must lie strictly between zero and one")
    z = NormalDist().inv_cdf((1 + confidence) / 2)
    proportion = successes / trials
    denominator = 1 + z * z / trials
    center = (proportion + z * z / (2 * trials)) / denominator
    half = z * math.sqrt(proportion * (1 - proportion) / trials + z * z / (4 * trials * trials)) / denominator
    return max(0.0, center - half), min(1.0, center + half)


def cluster_from_innovations(innovations, icc: float = 0.5):
    """Map five cage effects and ten residuals to five synthetic pairs.

    Group n=9 later omits the last padded observation, leaving four pairs and
    one singleton. A shared random effect is used only within each synthetic
    endpoint/group pair. Covariances across endpoints and groups are zero.
    """
    import numpy as np

    values = np.asarray(innovations, dtype=float)
    if values.ndim < 1 or values.shape[-1] != 15 or not 0 <= icc <= 1 or not np.all(np.isfinite(values)):
        raise ValueError("Cluster generation requires 15 finite innovations and ICC in [0,1]")
    cage_index = np.arange(10) // 2
    return math.sqrt(icc) * values[..., cage_index] + math.sqrt(1 - icc) * values[..., 5:15]


def controls_only_from_innovations(innovations, icc: float = 0.5):
    """Apply the hypothetical six-cluster layout only to group 0.

    The last dimensions contain three groups and sixteen independent Gaussian
    innovations each. Controls use six cluster effects and ten residuals;
    groups 1 and 2 use their first ten independent innovations. The padded
    tenth group-2 value is discarded by group_moments, as in the older models.
    """
    import numpy as np

    values = np.asarray(innovations, dtype=float)
    if (values.ndim < 2 or values.shape[-2:] != (3, 16)
            or not 0 <= icc <= 1 or not np.all(np.isfinite(values))):
        raise ValueError("Control-only generation requires three groups of 16 finite innovations and ICC in [0,1]")
    cluster_index = np.repeat(np.arange(len(CONTROL_CLUSTER_SIZES)), CONTROL_CLUSTER_SIZES)
    result = values[..., :10].copy()
    result[..., 0, :] = (math.sqrt(icc) * values[..., 0, cluster_index]
                         + math.sqrt(1 - icc) * values[..., 0, 6:16])
    return result


def synthetic_batch(rng, scenario: str, replicates: int):
    """Return replicate-major (batch,3 endpoints,3 groups,10 padded values).

    Each call consumes a fixed number of normal draws per replicate. Combined
    with replicate-major ordering, this preserves the exact random sequence
    across different batch partitions for the recorded NumPy implementation.
    The final padded observation of group 2 is never analyzed.
    """
    import numpy as np

    if isinstance(replicates, bool) or not isinstance(replicates, int) or not 1 <= replicates <= MAX_BATCH_SIZE:
        raise ValueError("Synthetic batches must contain 1 through 500 replicates")
    if scenario not in {name for name, _ in SCENARIOS}:
        raise ValueError(f"Unknown prespecified software scenario: {scenario}")
    if scenario == "artificial_gaussian_clusters_icc_0_5":
        innovations = rng.standard_normal((replicates, N_ENDPOINTS, 3, 15))
        return cluster_from_innovations(innovations, 0.5)
    if scenario == "hypothetical_controls_only_gaussian_clusters_icc_0_5":
        innovations = rng.standard_normal((replicates, N_ENDPOINTS, 3, 16))
        return controls_only_from_innovations(innovations, 0.5)
    values = rng.standard_normal((replicates, N_ENDPOINTS, 3, 10))
    if scenario == "independent_gaussian_unequal_variance":
        values *= np.array([2.0, 1.0, 1.0])[None, None, :, None]
    elif scenario == "independent_centered_lognormal":
        values = np.exp(values) - math.exp(0.5)
    return values


def group_moments(values):
    import numpy as np

    samples = np.asarray(values, dtype=float)
    if samples.ndim < 2 or samples.shape[-2:] != (3, 10) or not np.all(np.isfinite(samples)):
        raise ValueError("Synthetic values must end in three groups by ten padded observations")
    means = np.stack([samples[..., group, :n].mean(axis=-1) for group, n in enumerate(GROUP_SIZES)], axis=-1)
    variances = np.stack([samples[..., group, :n].var(axis=-1, ddof=1) for group, n in enumerate(GROUP_SIZES)], axis=-1)
    return means, variances


def vectorized_welch(means, variances, sizes=GROUP_SIZES, alpha: float = ALPHA) -> dict:
    """The same adjacent Welch contrasts used by the six-test software family."""
    import numpy as np
    from scipy.special import stdtr, stdtrit

    means = np.asarray(means, dtype=float)
    variances = np.asarray(variances, dtype=float)
    sizes = np.asarray(sizes, dtype=float)
    if means.ndim < 1 or means.shape != variances.shape or means.shape[-1] != 3 or sizes.shape != (3,):
        raise ValueError("Welch moments require matching three-group dimensions")
    if not 0 < alpha < 1 or np.any(sizes < 2) or not np.all(np.isfinite(sizes)):
        raise ValueError("Welch inference requires valid alpha and at least two observations per group")
    if not np.all(np.isfinite(means)) or not np.all(np.isfinite(variances)) or np.any(variances < 0):
        raise ValueError("Welch moments must be finite with nonnegative variances")
    first, second = np.array([1, 2]), np.array([0, 1])
    mean_difference = means[..., first] - means[..., second]
    components = variances / sizes
    va, vb = components[..., first], components[..., second]
    se_squared = va + vb
    if np.any(se_squared <= 0):
        raise ValueError("Welch inference requires positive variance for every contrast")
    degrees = se_squared ** 2 / (va ** 2 / (sizes[first] - 1) + vb ** 2 / (sizes[second] - 1))
    standard_error = np.sqrt(se_squared)
    statistic = mean_difference / standard_error
    p_values = 2 * stdtr(degrees, -np.abs(statistic))
    critical = stdtrit(degrees, 1 - alpha / 2)
    return {"mean_difference": mean_difference, "standard_error": standard_error,
            "degrees_freedom": degrees, "statistic": statistic, "p_value": p_values,
            "ci_low": mean_difference - critical * standard_error,
            "ci_high": mean_difference + critical * standard_error}


def bh_any_rejection(p_values, alpha: float = ALPHA):
    """One complete six-test step-up family per replicate, with overlapping pairs."""
    import numpy as np

    p = np.asarray(p_values, dtype=float)
    if p.ndim != 2 or p.shape[1] != 6 or not np.all(np.isfinite(p)) or np.any((p < 0) | (p > 1)):
        raise ValueError("Each benchmark replicate requires six valid P values")
    if not 0 < alpha < 1:
        raise ValueError("alpha must lie in (0,1)")
    return np.any(np.sort(p, axis=1) <= alpha * np.arange(1, 7) / 6, axis=1)


@lru_cache(maxsize=4)
def tukey_critical(confidence: float = 0.95) -> float:
    from scipy.stats import studentized_range

    return float(studentized_range.ppf(confidence, 3, sum(GROUP_SIZES) - 3))


def tukey_simultaneous_coverage(means, variances, critical: float):
    """Coverage of all three true-zero pair differences within each endpoint."""
    import numpy as np

    means, variances = np.asarray(means), np.asarray(variances)
    sizes = np.asarray(GROUP_SIZES, dtype=float)
    mse = np.sum((sizes - 1) * variances, axis=-1) / (sizes.sum() - 3)
    covered = np.ones(means.shape[:-1], dtype=bool)
    for first, second in ((1, 0), (2, 1), (2, 0)):
        scale = np.sqrt(mse / 2 * (1 / sizes[first] + 1 / sizes[second]))
        covered &= np.abs(means[..., first] - means[..., second]) <= critical * scale
    return covered


def benchmark(seed: int, replicates: int = 20000, batch_size: int = 500) -> list[dict]:
    """Run bounded all-null simulations without reading experimental data."""
    import numpy as np
    import scipy

    if not isinstance(seed, int) or seed < 0:
        raise ValueError("The software benchmark seed must be a nonnegative integer")
    if isinstance(replicates, bool) or not isinstance(replicates, int) or not 1 <= replicates <= MAX_REPLICATES:
        raise ValueError("The number of synthetic replicates must be an integer from 1 through 20000")
    if isinstance(batch_size, bool) or not isinstance(batch_size, int) or not 1 <= batch_size <= MAX_BATCH_SIZE:
        raise ValueError("The synthetic batch size must be between 1 and 500")
    critical = tukey_critical()
    rows = []
    for stream_index, (scenario, description) in enumerate(SCENARIOS):
        rng = np.random.default_rng(np.random.SeedSequence(seed, spawn_key=(stream_index,)))
        rejected = np.zeros((N_ENDPOINTS, 2), dtype=np.int64)
        coverage = np.zeros((N_ENDPOINTS, 2), dtype=np.int64)
        tukey_coverage = np.zeros(N_ENDPOINTS, dtype=np.int64)
        bh_rejected = 0
        completed = 0
        batches = 0
        maximum_batch = 0
        while completed < replicates:
            count = min(batch_size, replicates - completed)
            values = synthetic_batch(rng, scenario, count)
            means, variances = group_moments(values)
            welch = vectorized_welch(means, variances)
            rejected += np.sum(welch["p_value"] < ALPHA, axis=0)
            coverage += np.sum((welch["ci_low"] <= 0) & (welch["ci_high"] >= 0), axis=0)
            bh_rejected += int(np.sum(bh_any_rejection(welch["p_value"].reshape(count, 6))))
            tukey_coverage += np.sum(tukey_simultaneous_coverage(means, variances, critical), axis=0)
            completed += count
            batches += 1
            maximum_batch = max(maximum_batch, count)
        common = {
            "purpose": PURPOSE, "scenario": scenario, "scenario_description": description,
            "replicates": replicates, "mc_interval_method": "pointwise Wilson 95% binomial Monte Carlo interval",
            "alpha": ALPHA, "group_0_n": GROUP_SIZES[0], "group_1_n": GROUP_SIZES[1], "group_2_n": GROUP_SIZES[2],
            "seed": seed, "scenario_stream_index": stream_index, "rng": "NumPy PCG64; replicate-major normal innovations",
            "batch_size": batch_size, "max_actual_batch_size": maximum_batch, "batches": batches,
            "all_null": True, "endpoint_dependence": "independent endpoints; overlapping adjacent contrasts within endpoint",
            "numpy_version": np.__version__, "scipy_version": scipy.__version__,
        }

        def append(metric: str, endpoint: str, contrast: str, successes: int, nominal: float) -> None:
            low, high = wilson_interval(successes, replicates)
            rows.append({**common, "endpoint": endpoint, "contrast": contrast, "metric": metric,
                         "successes": successes, "estimate": successes / replicates,
                         "mc_ci_low": low, "mc_ci_high": high, "nominal_probability": nominal})

        for endpoint in range(N_ENDPOINTS):
            endpoint_name = f"synthetic_endpoint_{endpoint + 1}"
            for contrast in range(2):
                append("welch_unadjusted_false_positive_probability", endpoint_name, CONTRASTS[contrast], int(rejected[endpoint, contrast]), ALPHA)
                append("welch_pointwise_95_ci_coverage", endpoint_name, CONTRASTS[contrast], int(coverage[endpoint, contrast]), 1 - ALPHA)
            append("tukey_three_pair_simultaneous_95_ci_coverage", endpoint_name, "all_three_pairwise_comparisons", int(tukey_coverage[endpoint]), 1 - ALPHA)
        append("bh_all_null_family_any_rejection_probability", "all_three_synthetic_endpoints", "six_adjacent_welch_tests", bh_rejected, ALPHA)
    return rows


def run(root: Path, config: dict) -> dict:
    """Write separate software-only simulation tables and a labeled report."""
    root = Path(root)
    settings = config.get("calibration", {})
    replicates = settings.get("replicates", 20000)
    batch_size = settings.get("batch_size", 500)
    seed = config.get("seed", 20261020)
    rows = benchmark(seed, replicates, batch_size)
    table = root / "results/tables/software_calibration.csv"
    table.parent.mkdir(parents=True, exist_ok=True)
    with table.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    report = [
        "# Synthetic software calibration", "",
        "Every result on this page has purpose synthetic_not_biological. No experimental outcomes, source mouse IDs, real cage assignments or fitted clinical parameters were read. These simulations do not estimate biological power or validate an unknown cage structure.", "",
        f"Seed: {seed}. Replicates per scenario: {replicates}, with an absolute bound of 20,000. Five scenarios use at most {batch_size} replicates per batch, with an absolute batch-size bound of 500. Three independent synthetic endpoints use group sizes 10,10,9 and two overlapping adjacent Welch contrasts each. Every true mean contrast is zero.", "",
        "| Synthetic assumption | All-null BH family any rejection | Wilson 95% Monte Carlo interval |", "|---|---:|---|",
    ]
    for row in rows:
        if row["metric"] == "bh_all_null_family_any_rejection_probability":
            report.append(f"| {row['scenario']} | {row['estimate']:.5f} | {row['mc_ci_low']:.5f} to {row['mc_ci_high']:.5f} |")
    report.extend([
        "", "Under the complete null, FDR equals the probability of at least one rejection (FWER). The nominal level is 0.05. The six tests share the middle synthetic group within an endpoint, so they are generated jointly rather than treated as independent P values.", "",
        "The CSV also records per-contrast unadjusted false-positive probability and pointwise 95% Welch interval coverage. These are complementary zero-null events, apart from exact numerical boundaries. Tukey coverage concerns all three pairwise mean intervals within one synthetic endpoint, using the original common-variance formula with finite df=26. It does not adjust across endpoints.", "",
        "Wilson bounds measure binomial Monte Carlo error across independent generated replicates. They are pointwise intervals for software performance probabilities, not confidence intervals for any mouse effect and not simultaneous bounds across all simulation summaries.", "",
        "The artificial cluster scenario assigns five generic Gaussian random-intercept clusters to every group, with ICC 0.5, five pairs in groups 0 and 1 and four pairs plus one singleton in group 2. This is a deliberate assumption stress test. It is not inferred from the source experiment; in particular, the original stressed groups were singly housed, and no actual cage IDs are reconstructed. Endpoint-specific cluster effects are independent.", "",
        "The additional controls-only scenario instead gives group 0 six hypothetical clusters of sizes 2,2,1,2,2,1, with ICC 0.5, while groups 1 and 2 remain independent. The layout is motivated by integer portions of control IDs and the stated group housing; those IDs are not confirmed cages, and the ICC is imposed rather than estimated. The code reads neither source IDs nor biological outcomes. This scenario was added after the earlier four-model benchmark, without changing its streams.", "",
        "Control-only dependence directly affects the group-1-minus-group-0 Welch contrast. The group-2-minus-group-1 unadjusted Welch calculation still uses only independent Gaussian groups; its model is unchanged. The six-test BH event can nevertheless change because its family also includes the control contrasts. All three groups enter the pooled variance for Tukey intervals, so their coverage must be evaluated separately.", "",
        "Equal means are preserved in every scenario. The centered lognormal scenario subtracts its known expectation exp(0.5), without estimating a center from observed study outcomes. No scenario or parameter was selected to match a biological result.", "",
        "A scenario has its own fixed PCG64 stream derived from the recorded seed and scenario index. The controls-only scenario is appended at index 4; indices 0 through 3 and their innovation draws are unchanged. Replicate-major draws preserve results across batch partitions under the recorded NumPy version. The unchanged CSV schema records 16 performance summaries per scenario, hence 80 rows for five models. Only count accumulators and batches of at most 500 are retained; raw simulated observations are not written. Full benchmark execution is separate from short synthetic unit checks.", "",
        "This benchmark shows how the software behaves under stated generating assumptions. It cannot establish whether those assumptions hold for the original experiment, remedy missing phage data, or turn endpoint phenotypes into longitudinal immune stability.",
    ])
    report_path = root / "results/reports/software_calibration.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"status": "completed", "purpose": PURPOSE, "scenarios": len(SCENARIOS),
            "replicates_per_scenario": replicates, "seed": seed, "batch_size": batch_size,
            "maximum_batch_bound": 500, "rows": len(rows), "biological_observations_used": 0,
            "outputs": ["results/tables/software_calibration.csv", "results/reports/software_calibration.md"]}
