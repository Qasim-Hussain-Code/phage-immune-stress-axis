"""Post hoc sensitivities to inferred ID strata, control cages and TNF scale.

The source identifiers establish the partitions used here, not their biological
meaning. Neither ID-range blocks nor integer-prefix control cages are verified
allocation metadata. Primary source values and the original six tests are not
modified. All covariance/independence assumptions remain conditional.
"""

from __future__ import annotations

import json
import math
from pathlib import Path
from statistics import mean
from typing import Sequence

from .immune import (
    CONTRASTS, EFFECT_UNITS, ENDPOINTS, _read_long, benjamini_hochberg,
    composite_mouse_id, validate_plan, welch_difference,
)
from .io import write_csv


GROUPS = ("ctr", "ctr_stress", "fvt_stress")
BLOCKS = ("A", "B")
ID_RANGES = {
    "ctr": (("1.1", "1.2", "2.1", "2.2", "3"), ("19.1", "19.2", "20.1", "20.2", "21")),
    "ctr_stress": (tuple(str(i) for i in range(4, 9)), tuple(str(i) for i in range(22, 27))),
    "fvt_stress": (tuple(str(i) for i in range(9, 14)), tuple(str(i) for i in range(27, 32))),
}
CONTROL_CAGES = {
    "1": ("1.1", "1.2"), "2": ("2.1", "2.2"), "3": ("3",),
    "19": ("19.1", "19.2"), "20": ("20.1", "20.2"), "21": ("21",),
}
POSTHOC = "post hoc sensitivity added after initial results; selected endpoints unchanged"
ASSUMPTION = "ID-range blocks and integer-prefix control cages inferred, not verified"
OUTPUTS = (
    "results/tables/immune_design_membership.csv",
    "results/tables/immune_block_adjusted.csv",
    "results/tables/immune_within_block.csv",
    "results/tables/immune_putative_cage_units.csv",
    "results/tables/immune_putative_cage_means.csv",
    "results/tables/immune_control_cage_omission.csv",
    "results/tables/immune_tnfa_log_sensitivity.csv",
)


def _json(value) -> str:
    return json.dumps(value, separators=(",", ":"), sort_keys=True)


def inferred_design(group: str, source_id: str) -> dict:
    """Map only documented literal source IDs; never map pools or ENA aliases."""
    if group not in ID_RANGES or not isinstance(source_id, str):
        raise ValueError("An exact study II group and literal source identifier are required")
    for block, identifiers in zip(BLOCKS, ID_RANGES[group]):
        if source_id in identifiers:
            cage = next((name for name, members in CONTROL_CAGES.items()
                         if group == "ctr" and source_id in members), "")
            return {"id_range_block": block, "putative_control_cage_id": cage,
                    "block_verified": False, "cage_verified": False}
    raise ValueError(f"Source ID outside the fixed study II sensitivity mapping: {group}, {source_id}")


def source_design(rows: Sequence[dict]) -> tuple[list[dict], dict]:
    """Require all three selected records for each of the 30 source animals."""
    data = {endpoint: {group: [] for group in GROUPS} for endpoint in ENDPOINTS}
    animals, seen = {}, set()
    for source in rows:
        if source["experiment_id"] != "study_ii" or source["endpoint"] not in ENDPOINTS:
            continue
        row = dict(source)
        group, identifier, endpoint = row["group"], row["source_id"], row["endpoint"]
        design = inferred_design(group, identifier)
        key = composite_mouse_id("study_ii", group, identifier)
        if row["mouse_id"] != key or (key, endpoint) in seen:
            raise ValueError("Altered or repeated source-animal endpoint identifier")
        seen.add((key, endpoint))
        status = row["observation_status"]
        if status not in ("missing", "observed") or (status == "missing") != (row["value"] == ""):
            raise ValueError("Inconsistent source missingness")
        if status == "observed":
            if isinstance(row["value"], bool) or not math.isfinite(float(row["value"])):
                raise ValueError("Observed outcomes must be finite numeric values")
            row["value"] = float(row["value"])
        row.update(design)
        data[endpoint][group].append(row)
        animal = {"experiment_id": "study_ii", "group": group, "source_id": identifier,
                  "mouse_id": key, "source_sheet": row["source_sheet"],
                  "source_row": row["source_row"], **design,
                  "posthoc_status": POSTHOC, "assumption_status": ASSUMPTION,
                  "block_basis": "Control 1–3/19–21; Stress 4–8/22–26; FVT 9–13/27–31",
                  "cage_basis": "control integer-prefix interpretation only; no sequencing crosswalk"}
        if key in animals and animals[key] != animal:
            raise ValueError("Inconsistent source coordinates across endpoint records")
        animals[key] = animal
    for endpoint in ENDPOINTS:
        for group in GROUPS:
            expected = set(ID_RANGES[group][0] + ID_RANGES[group][1])
            if {r["source_id"] for r in data[endpoint][group]} != expected:
                raise ValueError("Selected records do not cover the fixed source-row cohort")
            order = {identifier: i for i, identifier in enumerate(ID_RANGES[group][0] + ID_RANGES[group][1])}
            data[endpoint][group].sort(key=lambda r: order[r["source_id"]])
    membership = [animals[composite_mouse_id("study_ii", group, identifier)]
                  for group in GROUPS for block in ID_RANGES[group] for identifier in block]
    return membership, data


def fit_hc3(observations: Sequence[dict], adjust_block: bool = True) -> dict:
    """OLS coefficients and HC3 covariance, with residual-df t references.

    X is intercept, Stress, FVT, and optionally inferred block B. HC3 addresses
    heteroskedasticity, not within-cage dependence or unverified allocation.
    """
    import numpy as np

    design, values = [], []
    for row in observations:
        if row["group"] not in GROUPS or row["id_range_block"] not in BLOCKS:
            raise ValueError("Unknown treatment or inferred ID block")
        value = float(row["value"])
        if not math.isfinite(value):
            raise ValueError("HC3 outcomes must be finite")
        design.append([1.0, float(row["group"] == "ctr_stress"), float(row["group"] == "fvt_stress")]
                      + ([float(row["id_range_block"] == "B")] if adjust_block else []))
        values.append(value)
    x, y = np.asarray(design), np.asarray(values)
    columns = 4 if adjust_block else 3
    if len(y) <= columns or x.shape != (len(y), columns) or np.linalg.matrix_rank(x) != columns:
        raise ValueError("Insufficient or rank-deficient treatment/block model")
    bread = np.linalg.inv(x.T @ x)
    beta = np.linalg.lstsq(x, y, rcond=None)[0]
    residual = y - x @ beta
    leverage = np.einsum("ij,jk,ik->i", x, bread, x)
    if np.any(leverage >= 1 - 1e-12):
        raise ValueError("HC3 requires residual leverage below one")
    covariance = bread @ (x.T @ (x * ((residual / (1 - leverage)) ** 2)[:, None])) @ bread
    return {"coefficients": beta, "covariance": covariance, "n_observed": len(y),
            "degrees_freedom": len(y) - columns, "adjust_block": adjust_block}


def hc3_contrast(model: dict, first: str, second: str) -> dict:
    import numpy as np
    from scipy.stats import t

    if first not in GROUPS or second not in GROUPS or first == second:
        raise ValueError("A contrast needs two distinct documented groups")
    vector = np.zeros(len(model["coefficients"]))
    for group, sign in ((first, 1), (second, -1)):
        if group != "ctr":
            vector[GROUPS.index(group)] += sign
    effect = float(vector @ model["coefficients"])
    squared = float(vector @ model["covariance"] @ vector)
    if not math.isfinite(squared) or squared <= 0:
        raise ValueError("HC3 contrast variance must be positive and finite")
    se, df = math.sqrt(squared), model["degrees_freedom"]
    statistic = effect / se
    critical = float(t.ppf(0.975, df))
    return {"mean_difference": effect, "standard_error": se,
            "t_statistic": statistic, "degrees_freedom": df,
            "p_value": float(2 * t.sf(abs(statistic), df)),
            "ci_low": effect - critical * se, "ci_high": effect + critical * se,
            "confidence_level": 0.95}


def positive_log_ratio(first: Sequence[float], second: Sequence[float]) -> dict:
    """Natural-log Welch sensitivity; no zero deletion or pseudocount."""
    a, b = list(first), list(second)
    for value in a + b:
        if isinstance(value, bool) or not math.isfinite(float(value)) or float(value) <= 0:
            raise ValueError("Every observed TNF-alpha value must be finite and strictly positive")
    a, b = [float(value) for value in a], [float(value) for value in b]
    log_stats = welch_difference([math.log(x) for x in a], [math.log(x) for x in b])
    raw_stats = welch_difference(a, b)
    try:
        result = {"geometric_mean_first": math.exp(mean([math.log(x) for x in a])),
                  "geometric_mean_second": math.exp(mean([math.log(x) for x in b])),
                  "geometric_mean_ratio": math.exp(log_stats["mean_difference"]),
                  "ratio_ci_low": math.exp(log_stats["ci_low"]),
                  "ratio_ci_high": math.exp(log_stats["ci_high"])}
    except OverflowError as exc:
        raise ValueError("Geometric-ratio interval exceeds finite numeric range") from exc
    if any(not math.isfinite(value) or value <= 0 for value in result.values()):
        raise ValueError("Geometric-ratio calculation exceeds positive finite numeric range")
    return {**result, "n_first": len(a), "n_second": len(b),
            "log_mean_difference": log_stats["mean_difference"],
            "log_standard_error": log_stats["standard_error"],
            "log_ci_low": log_stats["ci_low"], "log_ci_high": log_stats["ci_high"],
            "t_statistic": log_stats["t_statistic"], "degrees_freedom": log_stats["degrees_freedom"],
            "p_value": log_stats["p_value"], "confidence_level": 0.95,
            "raw_mean_difference": raw_stats["mean_difference"],
            "raw_ci_low": raw_stats["ci_low"], "raw_ci_high": raw_stats["ci_high"],
            "raw_p_value": raw_stats["p_value"]}


def _observed(rows: Sequence[dict]) -> list[dict]:
    return [row for row in rows if row["observation_status"] == "observed"]


def _values(rows: Sequence[dict]) -> list[float]:
    return [row["value"] for row in _observed(rows)]


def _common(endpoint: str, first: str, second: str) -> dict:
    return {"experiment_id": "study_ii", "endpoint": endpoint,
            "contrast": f"{first}_minus_{second}", "first_group": first, "second_group": second,
            "posthoc_status": POSTHOC, "assumption_status": ASSUMPTION,
            "effect_units": EFFECT_UNITS[endpoint]}


def _adjust(rows: list[dict], family: str) -> None:
    for row, q in zip(rows, benjamini_hochberg([row["p_value"] for row in rows])):
        row.update(q_value=q, bh_family=family, bh_family_size=len(rows))


def calculate(rows: Sequence[dict]) -> dict[str, list[dict]]:
    """Calculate every table before any output write; fixed selected endpoints."""
    membership, data = source_design(rows)
    adjusted, within, units, cages, omissions, logarithmic = [], [], [], [], [], []
    for endpoint in ENDPOINTS:
        observations = [row for group in GROUPS for row in _observed(data[endpoint][group])]
        block_model = fit_hc3(observations, True)
        unadjusted_model = fit_hc3(observations, False)
        for first, second in CONTRASTS:
            comparator = hc3_contrast(unadjusted_model, first, second)
            adjusted.append({**_common(endpoint, first, second),
                             "n_first": len(_observed(data[endpoint][first])),
                             "n_second": len(_observed(data[endpoint][second])),
                             "n_model_observed": len(observations),
                             **hc3_contrast(block_model, first, second),
                             "method": "additive treatment plus inferred ID-range block; OLS HC3/t",
                             "model_formula": "outcome ~ intercept + Stress + FVT + inferred_block_B",
                             "id_block_B_minus_A_estimate": float(block_model["coefficients"][3]),
                             "covariance_scope": "heteroskedasticity robust HC3; not cage corrected",
                             "model_assumptions": "additive common block term; independent animals; residual-df t approximation",
                             **{f"unadjusted_hc3_{key}": value for key, value in comparator.items()},
                             "unadjusted_comparator_scope": "treatment-only HC3/t; raw P and pointwise intervals; no comparator BH"})
        for block in BLOCKS:
            for first, second in CONTRASTS:
                a = _values([r for r in data[endpoint][first] if r["id_range_block"] == block])
                b = _values([r for r in data[endpoint][second] if r["id_range_block"] == block])
                overall = mean(_values(data[endpoint][first])) - mean(_values(data[endpoint][second]))
                stats = welch_difference(a, b)
                within.append({**_common(endpoint, first, second), "id_range_block": block, **stats,
                               "overall_raw_mean_difference": overall,
                               "same_direction_as_overall_raw": stats["mean_difference"] * overall > 0,
                               "method": "within inferred ID block; raw-scale Welch/t"})
        cage_values = []
        for cage, identifiers in CONTROL_CAGES.items():
            members = [r for r in data[endpoint]["ctr"] if r["source_id"] in identifiers]
            observed = _observed(members)
            value = mean(_values(members)) if observed else ""
            units.append({"experiment_id": "study_ii", "endpoint": endpoint,
                          "group": "ctr", "putative_control_cage_id": cage,
                          "source_ids_json": _json(list(identifiers)),
                          "observed_source_ids_json": _json([r["source_id"] for r in observed]),
                          "n_source_animals": len(members), "n_observed_animals": len(observed),
                          "unit_mean": value, "observation_status": "observed" if observed else "missing",
                          "posthoc_status": POSTHOC, "assumption_status": ASSUMPTION,
                          "weighting": "equal weight per observed putative control cage"})
            if observed:
                cage_values.append(value)
        for first, second in CONTRASTS:
            a = _values(data[endpoint][first])
            b = cage_values if second == "ctr" else _values(data[endpoint][second])
            cages.append({**_common(endpoint, first, second), **welch_difference(a, b),
                          "n_observed_animals_first": len(_observed(data[endpoint][first])),
                          "n_observed_animals_second": len(_observed(data[endpoint][second])),
                          "first_unit": "individually housed animal",
                          "second_unit": "putative control cage mean" if second == "ctr" else "individually housed animal",
                          "n_putative_control_cages": len(cage_values) if second == "ctr" else 0,
                          "method": "Welch/t on conditional independent units",
                          "estimand": ("mean stressed animal minus equal-weight mean of observed putative control cages"
                                       if second == "ctr" else "mean FVT animal minus mean stressed-control animal; both singly housed")})
    _adjust(adjusted, "six treatment contrasts adjusted for inferred ID block; HC3/t")
    _adjust(within, "twelve within-inferred-ID-block Welch contrasts")
    _adjust(cages, "six conditional putative-control-cage-unit Welch contrasts")
    for cage, identifiers in CONTROL_CAGES.items():
        family = []
        for endpoint in ENDPOINTS:
            for first, second in CONTRASTS:
                a = _values(data[endpoint][first])
                second_rows = [r for r in data[endpoint][second]
                               if second != "ctr" or r["source_id"] not in identifiers]
                family.append({**_common(endpoint, first, second),
                               "omitted_group": "ctr", "omitted_putative_control_cage_id": cage,
                               "omitted_source_ids_json": _json(list(identifiers)),
                               **welch_difference(a, _values(second_rows)),
                               "method": "animal-weighted Welch/t after omitting all members of one putative control cage",
                               "omission_scope": "all six putative control cages; diagnostic refits, not source exclusions"})
        _adjust(family, f"original six endpoint/contrast tests after omitting putative control cage {cage}")
        omissions.extend(family)
    endpoint = "tnfa_splenocyte_unstimulated"
    # Check all observed TNF values, not only a selected subset or positive tail.
    if any(value <= 0 for group in GROUPS for value in _values(data[endpoint][group])):
        raise ValueError("Every observed TNF-alpha value must be strictly positive; no deletion or pseudocount")
    for first, second in CONTRASTS:
        logarithmic.append({**_common(endpoint, first, second),
                            **positive_log_ratio(_values(data[endpoint][first]), _values(data[endpoint][second])),
                            "effect_units": "geometric-mean ratio (dimensionless)",
                            "raw_effect_units": "pg/mL", "log_effect_units": "natural-log ratio (dimensionless)",
                            "method": "natural-log Welch/t; exponentiated geometric-mean ratio",
                            "ratio_units": "dimensionless", "geometric_mean_units": "pg/mL",
                            "positivity_policy": "every observed TNF value strictly positive; all retained; missing cells remain missing",
                            "raw_comparator_scope": "original raw-scale Welch estimate and raw P; primary BH family unchanged"})
    _adjust(logarithmic, "two post hoc TNF-alpha log-Welch contrasts")
    return dict(zip(OUTPUTS, (membership, adjusted, within, units, cages, omissions, logarithmic)))


def run(root: Path, config: dict) -> dict:
    """Stage-07 hook after phenotype extraction; primary results unchanged."""
    validate_plan(config)
    root = Path(root)
    tables = calculate(_read_long(root / "data/processed/immune_long.csv"))
    for relative, rows in tables.items():
        write_csv(root / relative, rows)
    return {"status": "completed", "posthoc_status": POSTHOC,
            "assumption_status": ASSUMPTION, "verified_block_metadata": False,
            "verified_control_cage_metadata": False, "primary_tables_changed": False,
            "table_rows": {path: len(rows) for path, rows in tables.items()},
            "bh_families": {"block_adjusted": 6, "within_block": 12, "putative_cage_means": 6,
                            "each_control_cage_omission": 6, "tnfa_log": 2},
            "outputs": list(OUTPUTS)}
