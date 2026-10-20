"""Reconstruct selected published three-group immune calculations separately.

This is a provenance check of the original pooled-variance method. It does not
replace the fixed Welch family, infer a viral association, or reconstruct the
original BH correction over an incompletely specified outcome family.
"""

from __future__ import annotations

import csv
import json
import math
from pathlib import Path
from statistics import mean, variance
from typing import Mapping, Sequence

from .immune import ENDPOINTS, _read_long


GROUPS = ("ctr", "ctr_stress", "fvt_stress")
COEFFICIENTS = (-0.5, 1.0, -0.5)
PAIRS = (("ctr_stress", "ctr"), ("fvt_stress", "ctr_stress"), ("fvt_stress", "ctr"))
PAPER_URL = "https://www.nature.com/articles/s41564-023-01564-y"
PUBLISHED = {
    "ly6chi_monocytes": {
        "means": (4.38, 2.35, 3.91), "mean_decimals": 2, "n": (10, 10, 9),
        "t": -2.867, "t_decimals": 3, "planned_p_upper": 0.01, "reported_bh_q": 0.030,
        "pairs": {
            "ctr_stress_minus_ctr": {"upper": 0.05},
            "fvt_stress_minus_ctr_stress": {"p": 0.106, "decimals": 3},
        },
    },
    "ly6chi_monocytes_cd62": {
        "means": (61.4, 59.6, 75.5), "mean_decimals": 1, "n": (10, 10, 9),
        "t": -3.18, "t_decimals": 2, "planned_p_upper": 0.05, "reported_bh_q": 0.030,
        "pairs": {
            "ctr_stress_minus_ctr": {"p": 0.845, "decimals": 3},
            "fvt_stress_minus_ctr_stress": {"upper": 0.001},
        },
    },
    "tnfa_splenocyte_unstimulated": {
        "means": (34.4, 102.0, 27.9), "mean_decimals": 1, "n": (9, 8, 9),
        "t": 2.68, "t_decimals": 2, "planned_p_upper": 0.05, "reported_bh_q": 0.075,
        "pairs": {
            "ctr_stress_minus_ctr": {"p": 0.086, "decimals": 3},
            "fvt_stress_minus_ctr_stress": {"p": 0.056, "decimals": 3},
        },
    },
}
FIELDS = (
    "experiment_id", "endpoint", "record_type", "contrast", "group_first", "group_second",
    "n_first", "n_second", "n_total", "group_mean", "group_variance", "group_sse",
    "residual_sse", "pooled_mse", "residual_df", "numerator_df", "effect", "standard_error",
    "statistic", "statistic_name", "p_value", "ci_low", "ci_high", "confidence_level",
    "interval_scope", "comparison_family_size", "coefficients_json", "source_units",
    "effect_units", "published_reference", "published_n", "published_mean",
    "published_mean_decimals", "computed_mean_at_published_precision", "published_t", "published_t_decimals", "published_p_value",
    "published_p_relation", "published_p_decimals", "published_planned_bh_q",
    "original_bh_family_status", "published_agreement", "interpretation",
)


def rounded_agreement(value: float, expected: float, decimals: int) -> bool:
    return f"{value:.{decimals}f}" == f"{expected:.{decimals}f}"


def pooled_analysis(groups: Mapping[str, Sequence[float]], confidence: float = 0.95) -> dict:
    """ANOVA, one fixed contrast and all three finite-df Tukey-Kramer pairs.

    The contrast direction reproduces the published signs. Tukey intervals
    cover the three pairwise comparisons within one endpoint under the original
    common-variance model. No across-endpoint correction is computed here.
    """
    from scipy.stats import f, studentized_range, t

    if set(groups) != set(GROUPS):
        raise ValueError("Exactly the three documented study II groups are required")
    if not 0 < confidence < 1:
        raise ValueError("Confidence must lie strictly between zero and one")
    summaries = {}
    for name in GROUPS:
        values = [float(value) for value in groups[name]]
        if len(values) < 2 or not all(math.isfinite(value) for value in values):
            raise ValueError("Each group needs at least two finite observed values")
        sample_variance = variance(values)
        summaries[name] = {"n": len(values), "mean": mean(values), "variance": sample_variance,
                           "sse": (len(values) - 1) * sample_variance}
    n_total = sum(item["n"] for item in summaries.values())
    residual_df = n_total - len(GROUPS)
    residual_sse = math.fsum(item["sse"] for item in summaries.values())
    mse = residual_sse / residual_df
    if mse <= 0:
        raise ValueError("Pooled inference requires a positive residual variance")
    grand = math.fsum(item["n"] * item["mean"] for item in summaries.values()) / n_total
    between_ss = math.fsum(item["n"] * (item["mean"] - grand) ** 2 for item in summaries.values())
    f_statistic = between_ss / (len(GROUPS) - 1) / mse
    effect = math.fsum(coef * summaries[name]["mean"] for coef, name in zip(COEFFICIENTS, GROUPS))
    standard_error = math.sqrt(mse * math.fsum(coef ** 2 / summaries[name]["n"] for coef, name in zip(COEFFICIENTS, GROUPS)))
    statistic = effect / standard_error
    alpha = 1 - confidence
    t_critical = float(t.ppf(1 - alpha / 2, residual_df))
    # Cache one critical range per endpoint, rather than repeating integration
    # for each of its three comparisons.
    range_critical = float(studentized_range.ppf(confidence, len(GROUPS), residual_df))
    pairs = []
    for first, second in PAIRS:
        a, b = summaries[first], summaries[second]
        difference = a["mean"] - b["mean"]
        pair_se = math.sqrt(mse * (1 / a["n"] + 1 / b["n"]))
        range_scale = pair_se / math.sqrt(2)
        range_statistic = abs(difference) / range_scale
        pairs.append({
            "group_first": first, "group_second": second,
            "contrast": f"{first}_minus_{second}", "n_first": a["n"], "n_second": b["n"],
            "effect": difference, "standard_error": pair_se,
            "statistic": range_statistic, "statistic_name": "studentized_range_q",
            "p_value": float(studentized_range.sf(range_statistic, len(GROUPS), residual_df)),
            "ci_low": difference - range_critical * range_scale,
            "ci_high": difference + range_critical * range_scale,
        })
    return {
        "groups": summaries, "n_total": n_total, "residual_df": residual_df,
        "residual_sse": residual_sse, "pooled_mse": mse,
        "anova": {"statistic": f_statistic, "p_value": float(f.sf(f_statistic, len(GROUPS) - 1, residual_df)),
                  "numerator_df": len(GROUPS) - 1},
        "planned_contrast": {
            "coefficients_json": json.dumps(dict(zip(GROUPS, COEFFICIENTS)), separators=(",", ":")),
            "effect": effect, "standard_error": standard_error, "statistic": statistic,
            "statistic_name": "t", "p_value": float(2 * t.sf(abs(statistic), residual_df)),
            "ci_low": effect - t_critical * standard_error,
            "ci_high": effect + t_critical * standard_error,
        },
        "pairs": pairs, "confidence_level": confidence,
    }


def _units(endpoint: str) -> tuple[str, str]:
    if endpoint == "tnfa_splenocyte_unstimulated":
        return "pg/mL; unstimulated splenocyte culture", "pg/mL"
    return "percent of parent population; basal before acute FST", "percentage points"


def result_rows(endpoint: str, result: dict) -> list[dict]:
    """Generate one tidy verification table, including unselected Tukey pairs."""
    reference = PUBLISHED[endpoint]
    source_units, effect_units = _units(endpoint)
    common = dict.fromkeys(FIELDS, "")
    common.update({
        "experiment_id": "study_ii", "endpoint": endpoint, "n_total": result["n_total"],
        "residual_sse": result["residual_sse"], "pooled_mse": result["pooled_mse"],
        "residual_df": result["residual_df"], "confidence_level": result["confidence_level"],
        "source_units": source_units, "effect_units": effect_units,
        "original_bh_family_status": "not_reproduced_unknown_full_family",
        "published_agreement": "not_reported_for_this_statistic",
        "interpretation": "original common-variance method replication; primary Welch family unchanged; cage dependence unresolved",
    })
    rows = []
    for index, name in enumerate(GROUPS):
        group = result["groups"][name]
        agreement = group["n"] == reference["n"][index] and rounded_agreement(group["mean"], reference["means"][index], reference["mean_decimals"])
        rows.append({**common, "record_type": "group", "group_first": name, "n_first": group["n"],
                     "group_mean": group["mean"], "group_variance": group["variance"], "group_sse": group["sse"],
                     "published_n": reference["n"][index], "published_mean": reference["means"][index],
                     "published_mean_decimals": reference["mean_decimals"],
                     "computed_mean_at_published_precision": f"{group['mean']:.{reference['mean_decimals']}f}",
                     "published_reference": PAPER_URL + "; Extended Data Table 1b,c and Figure 4 sample counts",
                     "published_agreement": "matches_published_precision" if agreement else "mismatch"})
    rows.append({**common, "record_type": "anova", "statistic_name": "F", **result["anova"]})
    planned = result["planned_contrast"]
    agreement = rounded_agreement(planned["statistic"], reference["t"], reference["t_decimals"]) and planned["p_value"] < reference["planned_p_upper"]
    rows.append({**common, "record_type": "planned_contrast", "contrast": "ctr_stress_minus_mean_ctr_fvt_stress",
                 **planned, "interval_scope": "pointwise planned contrast; not adjusted across endpoints",
                 "comparison_family_size": 1, "published_t": reference["t"], "published_t_decimals": reference["t_decimals"],
                 "published_p_value": reference["planned_p_upper"], "published_p_relation": "<",
                 "published_planned_bh_q": reference["reported_bh_q"],
                 "published_reference": PAPER_URL + "; Figure 4 planned contrast; published BH q is reference only",
                 "published_agreement": "matches_published_precision" if agreement else "mismatch"})
    for pair in result["pairs"]:
        row = {**common, "record_type": "tukey_kramer", **pair,
               "interval_scope": "simultaneous across all three pairwise comparisons within this endpoint",
               "comparison_family_size": 3}
        published = reference["pairs"].get(pair["contrast"])
        if published:
            row["published_reference"] = PAPER_URL + "; Figure 4 Tukey pairwise comparison"
            if "upper" in published:
                agreement = pair["p_value"] < published["upper"]
                row.update(published_p_value=published["upper"], published_p_relation="<")
            else:
                agreement = rounded_agreement(pair["p_value"], published["p"], published["decimals"])
                row.update(published_p_value=published["p"], published_p_relation="rounded_equal", published_p_decimals=published["decimals"])
            row["published_agreement"] = "matches_published_precision" if agreement else "mismatch"
        rows.append(row)
    return rows


def run(root: Path, config: dict) -> dict:
    """Write separate original-method tables and a numerical replication report."""
    del config  # Keep endpoint and method scope fixed by the independent review.
    root = Path(root)
    source = _read_long(root / "data/processed/immune_long.csv")
    rows = []
    for endpoint in ENDPOINTS:
        groups = {
            group: [float(row["value"]) for row in source if row["experiment_id"] == "study_ii"
                    and row["endpoint"] == endpoint and row["group"] == group and row["observation_status"] == "observed"]
            for group in GROUPS
        }
        rows.extend(result_rows(endpoint, pooled_analysis(groups)))
    path = root / "results/tables/original_method_replication.csv"
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=FIELDS, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)
    mismatches = [row for row in rows if row["published_agreement"] == "mismatch"]
    comparisons = sum(row["published_agreement"] != "not_reported_for_this_statistic" for row in rows)
    matches = sum(row["published_agreement"] == "matches_published_precision" for row in rows)
    source_checks = [row for row in rows if row["record_type"] == "group"]
    caption_checks = [row for row in rows if row["record_type"] in ("planned_contrast", "tukey_kramer")
                      and row["published_agreement"] != "not_reported_for_this_statistic"]
    caption_matches = sum(row["published_agreement"] == "matches_published_precision" for row in caption_checks)
    source_matches = sum(row["published_agreement"] == "matches_published_precision" for row in source_checks)
    tnf_fvt = next(row for row in source_checks if row["endpoint"] == "tnfa_splenocyte_unstimulated" and row["group_first"] == "fvt_stress")
    report = [
        "# Original-method immune replication", "",
        "This separate verification uses the same three study II endpoints and every supplied observed value. The primary six-test Welch family is unchanged.", "",
        "All three groups contribute to the pooled residual variance. Planned contrasts use Ctr, Ctr Stress and FVT Stress coefficients [-0.5, 1, -0.5]. Tukey-Kramer P values and simultaneous intervals use the finite residual degrees of freedom and all three pairwise comparisons per endpoint.", "",
        "| Endpoint | Pooled MSE | Residual df | Planned t | Planned P | FVT minus stressed-control Tukey P |", "|---|---:|---:|---:|---:|---:|",
    ]
    for endpoint in ENDPOINTS:
        planned = next(row for row in rows if row["endpoint"] == endpoint and row["record_type"] == "planned_contrast")
        pair = next(row for row in rows if row["endpoint"] == endpoint and row["record_type"] == "tukey_kramer" and row["contrast"] == "fvt_stress_minus_ctr_stress")
        report.append(f"| {endpoint} | {planned['pooled_mse']:.10g} | {planned['residual_df']} | {planned['statistic']:.10g} | {planned['p_value']:.10g} | {pair['p_value']:.10g} |")
    report.extend([
        "", f"Published sample counts/means or caption statistics checked: {comparisons}. Matches at published precision: {matches}. Mismatches: {len(mismatches)}. The CSV distinguishes rounded equalities, reported inequalities and statistics not individually reported.", "",
        f"Caption-statistic matches: {caption_matches} of {len(caption_checks)}. Source group count/mean matches: {source_matches} of {len(source_checks)}. The FVT Stress TNF-alpha source mean is {tnf_fvt['group_mean']:.12g} pg/mL, which rounds directly to {tnf_fvt['computed_mean_at_published_precision']} at one decimal; Extended Data Table 1b visibly prints {tnf_fvt['published_mean']}. This comparison is retained without a wider rounding tolerance. The caption-statistic matches are recorded independently of the printed-mean comparison.", "",
        "The monocyte FVT Tukey result reproduces the published 0.106, using the same source observations that give a smaller Welch P value. Pooled variance across all three groups and Tukey multiplicity explain this difference. Additional source exclusions are unnecessary for this numerical reconciliation. Upstream exclusions, censoring thresholds and omitted values remain unavailable.", "",
        "The paper calls its contrasts orthogonal. This single planned coefficient vector can be reconstructed, but orthogonality of a full contrast set cannot be claimed from a label. For independent unequal-size means, covariance of contrasts c and d is MSE times sum(c_i*d_i/n_i). An unweighted coefficient dot product of zero is not sufficient when group sizes differ, and the complete SPSS contrast syntax is unavailable.", "",
        "Planned-contrast intervals are pointwise. Tukey intervals are simultaneous within one endpoint's three-pair family, not across endpoints. Published planned BH q values in the CSV are explicitly reference values; the original complete BH family is unresolved and no reconstructed original q is claimed.", "",
        "Numerical agreement does not establish homoscedasticity, normality, independent animals or a viral mechanism. Cage allocation is missing; TNF-alpha variances are strongly unequal. CD62L-positive monocytes need not show reversal of a preceding stress deficit. All original-method output is a separate provenance check, not a preferred result selected for significance.", "",
        f"Source: [Ritz et al. (2024)]({PAPER_URL}). Detailed independent review: docs/original_analysis_review.md.",
    ])
    report_path = root / "results/reports/original_method_replication.md"
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_text("\n".join(report) + "\n", encoding="utf-8")
    return {"status": "completed", "endpoints": len(ENDPOINTS), "rows": len(rows),
            "published_checks": comparisons, "published_matches": matches, "published_mismatches": len(mismatches),
            "source_group_summary_checks": len(source_checks),
            "source_group_summary_matches": source_matches,
            "caption_statistic_checks": len(caption_checks),
            "caption_statistic_matches": caption_matches,
            "additional_observations_excluded": 0, "original_bh_reproduced": False,
            "primary_welch_family_unchanged": True,
            "outputs": ["results/tables/original_method_replication.csv", "results/reports/original_method_replication.md"]}
