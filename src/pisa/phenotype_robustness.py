"""Descriptive robustness checks for the existing six immune comparisons.

No additional hypothesis test, imputation or confidence interval is calculated.
Finite-support bounds concern the animals represented by source workbook rows,
conditional on their missing assays having well-defined values in that support.
"""

from __future__ import annotations

import csv
import json
import math
from collections import defaultdict
from pathlib import Path
from typing import Iterable, Sequence

from .immune import CONTRASTS, EFFECT_UNITS, ENDPOINTS, _read_long, _write_csv


GROUPS = ("ctr", "ctr_stress", "fvt_stress")
SUPPORT = {
    "ly6chi_monocytes": (0.0, 100.0),
    "ly6chi_monocytes_cd62": (0.0, 100.0),
    "tnfa_splenocyte_unstimulated": None,
}
OUTPUTS = (
    "results/tables/immune_missingness_bounds.csv",
    "results/tables/immune_rank_effects.csv",
    "results/reports/phenotype_robustness.md",
)


def _finite(values: Iterable[float]) -> list[float]:
    result = []
    for value in values:
        if isinstance(value, bool):
            raise ValueError("Boolean values are not phenotype measurements")
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Phenotype measurements must be finite")
        result.append(number)
    return result


def support_difference(
    first: Iterable[float], n_source_first: int,
    second: Iterable[float], n_source_second: int,
    support: Sequence[float] | None,
) -> dict:
    """Sharp bounds on a source-row cohort mean difference, without imputation.

    Each unobserved outcome may independently take any value in the stated
    support. The endpoints are extrema of a descriptive mean, not confidence
    limits. Without finite support, missing outcomes yield no finite bounds.
    """
    a, b = _finite(first), _finite(second)
    for total, observed in ((n_source_first, len(a)), (n_source_second, len(b))):
        if isinstance(total, bool) or not isinstance(total, int) or total < 1 or total < observed:
            raise ValueError("Source-row counts must be positive integers covering all observations")
    missing_a, missing_b = n_source_first - len(a), n_source_second - len(b)
    sum_a, sum_b = math.fsum(a), math.fsum(b)
    result = {
        "n_source_first": n_source_first, "n_source_second": n_source_second,
        "n_observed_first": len(a), "n_observed_second": len(b),
        "n_missing_first": missing_a, "n_missing_second": missing_b,
        "observed_sum_first": sum_a, "observed_sum_second": sum_b,
        "support_lower": "", "support_upper": "",
        "lower_mean_difference": "", "upper_mean_difference": "",
        "bound_status": "no_finite_bounds_missing_outcomes_without_finite_support",
    }
    if support is not None:
        if len(support) != 2:
            raise ValueError("Support requires exactly two finite endpoints")
        lower, upper = _finite(support)
        if lower > upper:
            raise ValueError("Support endpoints are reversed")
        if any(value < lower or value > upper for value in a + b):
            raise ValueError("An observed outcome lies outside the assumed support")
        result.update({
            "support_lower": lower, "support_upper": upper,
            "lower_mean_difference": (sum_a + missing_a * lower) / n_source_first
                                     - (sum_b + missing_b * upper) / n_source_second,
            "upper_mean_difference": (sum_a + missing_a * upper) / n_source_first
                                     - (sum_b + missing_b * lower) / n_source_second,
            "bound_status": "sharp_finite_support_bounds",
        })
    if not missing_a and not missing_b:
        difference = sum_a / n_source_first - sum_b / n_source_second
        result.update(lower_mean_difference=difference, upper_mean_difference=difference,
                      bound_status="fully_observed_source_cohort_difference")
    return result


def rank_effect(first: Iterable[float], second: Iterable[float], expected_u: float | None = None) -> dict:
    """Empirical superiority and rank-biserial effect with an independent U check.

    Average ranks provide U; direct pair enumeration independently verifies it,
    including half credit for ties. Cross-group pairs share animals.
    """
    a, b = _finite(first), _finite(second)
    if not a or not b:
        raise ValueError("Rank effects require observed animals in both groups")
    pooled = sorted([(value, True) for value in a] + [(value, False) for value in b])
    first_rank_sum = 0.0
    start = 0
    while start < len(pooled):
        stop = start + 1
        while stop < len(pooled) and pooled[stop][0] == pooled[start][0]:
            stop += 1
        average_rank = (start + 1 + stop) / 2
        first_rank_sum += average_rank * sum(is_first for _, is_first in pooled[start:stop])
        start = stop
    midrank_u = first_rank_sum - len(a) * (len(a) + 1) / 2
    wins = sum(x > y for x in a for y in b)
    ties = sum(x == y for x in a for y in b)
    pairs = len(a) * len(b)
    direct_u = wins + 0.5 * ties
    if midrank_u != direct_u:
        raise AssertionError("Midrank and direct-pair U calculations disagree")
    if expected_u is not None:
        reference_u = _finite([expected_u])[0]
        if not 0 <= reference_u <= pairs or not math.isclose(reference_u, direct_u, rel_tol=0, abs_tol=1e-12):
            raise ValueError("Existing sensitivity U does not match prepared source observations")
    probability = direct_u / pairs
    return {
        "n_observed_first": len(a), "n_observed_second": len(b),
        "n_observed_animals": len(a) + len(b), "cross_group_pair_count": pairs,
        "direct_first_greater_pairs": wins, "direct_tied_pairs": ties,
        "direct_first_less_pairs": pairs - wins - ties,
        "mann_whitney_u_first_midrank": midrank_u, "mann_whitney_u_first_direct": direct_u,
        "existing_sensitivity_u_first": "" if expected_u is None else reference_u,
        "existing_u_verified": expected_u is not None,
        "empirical_probability_first_greater_plus_half_ties": probability,
        "rank_biserial_first_minus_second": 2 * probability - 1,
    }


def _source_groups(rows: list[dict]) -> dict[tuple[str, str], list[dict]]:
    """Require complete endpoint records for every represented source animal."""
    animals: dict[str, set[str]] = defaultdict(set)
    data: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        if row["experiment_id"] != "study_ii":
            continue
        group = row["group"]
        if group not in GROUPS:
            raise ValueError("Unexpected study II source group")
        animals[group].add(row["mouse_id"])
        if row["endpoint"] in ENDPOINTS:
            data[(row["endpoint"], group)].append(row)
    for endpoint in ENDPOINTS:
        for group in GROUPS:
            represented = {row["mouse_id"] for row in data[(endpoint, group)]}
            if not animals[group] or represented != animals[group]:
                raise ValueError("Selected endpoint records do not cover the source-row cohort")
    return data


def _sensitivity_u(path: Path) -> dict[tuple[str, str], float]:
    expected = {(endpoint, f"{first}_minus_{second}")
                for endpoint in ENDPOINTS for first, second in CONTRASTS}
    result = {}
    with path.open(encoding="utf-8", newline="") as stream:
        reader = csv.DictReader(stream)
        required = {"experiment_id", "endpoint", "contrast", "mann_whitney_u_first"}
        if not required.issubset(reader.fieldnames or ()):
            raise ValueError("Existing sensitivity table lacks its U identity fields")
        for row in reader:
            key = (row["endpoint"], row["contrast"])
            if row["experiment_id"] != "study_ii" or key not in expected or key in result:
                raise ValueError("Existing sensitivity table must contain each fixed comparison once")
            result[key] = _finite([row["mann_whitney_u_first"]])[0]
    if set(result) != expected:
        raise ValueError("Existing sensitivity table is missing a fixed comparison")
    return result


def run(root: Path, config: dict) -> dict:
    """Write six descriptive rows per table without changing primary statistics."""
    from .reporting import NAMES,CONTRAST_NAMES
    del config
    root = Path(root)
    data = _source_groups(_read_long(root / "data/processed/immune_long.csv"))
    existing = _sensitivity_u(root / "results/tables/immune_sensitivity.csv")
    bounds, ranks = [], []
    for endpoint in ENDPOINTS:
        for first, second in CONTRASTS:
            contrast = f"{first}_minus_{second}"
            a, b = data[(endpoint, first)], data[(endpoint, second)]
            observed_a = [float(row["value"]) for row in a if row["observation_status"] == "observed"]
            observed_b = [float(row["value"]) for row in b if row["observation_status"] == "observed"]
            common = {"experiment_id": "study_ii", "endpoint": endpoint,
                      "contrast": contrast, "first_group": first, "second_group": second}
            finite_support = SUPPORT[endpoint]
            bounds.append({
                **common, **support_difference(observed_a, len(a), observed_b, len(b), finite_support),
                "missing_source_ids_first_json": json.dumps([row["source_id"] for row in a if row["observation_status"] == "missing"], separators=(",", ":")),
                "missing_source_ids_second_json": json.dumps([row["source_id"] for row in b if row["observation_status"] == "missing"], separators=(",", ":")),
                "effect_units": EFFECT_UNITS[endpoint],
                "target": "mean difference among animals represented by source workbook rows",
                "assumption": ("every missing assay has a well-defined value in [0,100] percent of parent population"
                               if finite_support else "no assay-specific finite upper support or missingness mechanism identified"),
                "interpretation": "sharp descriptive support bounds; not confidence intervals, imputation, or significance proof; not an unknown full randomized cohort",
            })
            ranks.append({
                **common, **rank_effect(observed_a, observed_b, existing[(endpoint, contrast)]),
                "target": "empirical cross-group ordering among observed source animals",
                "interpretation": "descriptive distributional effect; pairs share animals and are not independent replicates; not a mean or automatically a median effect",
            })
    # Compute and validate every row before creating any declared output.
    _write_csv(root / OUTPUTS[0], bounds)
    _write_csv(root / OUTPUTS[1], ranks)
    report = [
        "# Descriptive phenotype robustness", "",
        "These descriptive diagnostics were added after inspecting the earlier reanalysis. They use the existing three selected endpoints and two contrasts, add no P values, adjusted P values, confidence intervals or hypothesis tests, and do not change the primary or sensitivity tables.", "",
        "## Missing-outcome support bounds", "",
        "The denominator is the source-row cohort, including rows with missing assays; it is not an inferred complete randomized cohort. For percentages, each missing assay is assumed to have a well-defined value anywhere in [0,100]. Each endpoint of the bound is attainable under that support, with no imputed value adopted as data. Bounds describe a finite source-row mean difference, not population uncertainty, statistical significance or a causal effect.", "",
        "| Endpoint | Contrast | Source animals first / second | Missing first / second | Lower difference | Upper difference | Status |",
        "|---|---|---:|---:|---:|---:|---|",
    ]
    for row in bounds:
        lower = "unavailable" if row["lower_mean_difference"] == "" else f"{row['lower_mean_difference']:.8g}"
        upper = "unavailable" if row["upper_mean_difference"] == "" else f"{row['upper_mean_difference']:.8g}"
        status={'sharp_finite_support_bounds':'finite-support bounds',
                'fully_observed_source_cohort_difference':'complete source rows',
                'no_finite_bounds_missing_outcomes_without_finite_support':'finite bounds unavailable'}[row['bound_status']]
        report.append(f"| {NAMES[row['endpoint']]} | {CONTRAST_NAMES[row['contrast']]} | {row['n_source_first']} / {row['n_source_second']} | {row['n_missing_first']} / {row['n_missing_second']} | {lower} | {upper} | {status} |")
    report.extend([
        "", "Percentage differences are percentage points. TNF-alpha is in pg/mL; missing values and no identified finite upper support prevent finite bounds. No detection limit, zero substitution or missing-at-random assumption is supplied. Leave-one-out diagnostics omit observed values and answer a different question.", "",
        "## Existing rank effects", "",
        "Average-rank U and direct cross-animal pair enumeration agree, and both reproduce each existing sensitivity U. Empirical superiority equals (first-greater pairs + half tied pairs) / cross-group pairs; the rank-biserial effect is twice this probability minus one. These describe observed distributions, not raw means or automatically a common median shift. Cross-group pairs reuse animals and are not independent replicates.", "",
        "| Endpoint | Contrast | Observed animals first / second | First greater / tied / first less pairs | Empirical superiority | Rank-biserial effect |",
        "|---|---|---:|---:|---:|---:|",
    ])
    for row in ranks:
        report.append(f"| {NAMES[row['endpoint']]} | {CONTRAST_NAMES[row['contrast']]} | {row['n_observed_first']} / {row['n_observed_second']} | {row['direct_first_greater_pairs']} / {row['direct_tied_pairs']} / {row['direct_first_less_pairs']} | {row['empirical_probability_first_greater_plus_half_ties']:.8g} | {row['rank_biserial_first_minus_second']:.8g} |")
    report.extend([
        "", "Unknown cage allocation, upstream exclusions and censoring remain unresolved. These descriptive checks cannot supply missing viral measurements, establish independence or isolate a phage mechanism. Methods: docs/phenotype_robustness.md. Source-cell provenance remains in data/processed/immune_long.csv.",
    ])
    path = root / OUTPUTS[2]
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"status": "completed", "bounds_rows": len(bounds), "rank_effect_rows": len(ranks),
            "finite_bounds_rows": sum(row["lower_mean_difference"] != "" for row in bounds),
            "existing_u_checks": len(ranks), "new_hypothesis_tests": 0,
            "primary_tables_changed": False, "outputs": list(OUTPUTS)}
