"""Deposited specimen design and literal candidate labels, without assay linkage.

These tables inventory raw-read metadata. A literal workbook/ENA label match is
not a validated animal crosswalk and does not supply a processed viral profile.
"""

from __future__ import annotations

from collections import defaultdict
from pathlib import Path

from .io import read_csv, write_csv
from .samples import classify_sequencing_sample, literal_id


ARCHIVE = Path("data/raw/ritz2024_archive")
SHEET = "FVT study II"
RECIPIENT = "individual_recipient_bulk_metagenome"
TARGET_CONDITIONS = {"ctr_stress": "Control stress", "fvt_stress": "FVT stress"}
INVENTORY_FIELDS = [
    "accession", "source_condition", "specimen_role", "gavage_status",
    "run_count", "specimen_count", "fastq_file_count", "compressed_fastq_bytes",
    "source",
]
PAIR_FIELDS = [
    "workbook_sheet", "workbook_row", "workbook_group", "workbook_id",
    "ena_sample_type", "replicate_num",
    "before_sample_accessions", "before_run_accessions", "before_specimen_count",
    "before_run_count", "before_fastq_file_count", "before_compressed_fastq_bytes",
    "after_sample_accessions", "after_run_accessions", "after_specimen_count",
    "after_run_count", "after_fastq_file_count", "after_compressed_fastq_bytes",
    "total_run_count", "total_compressed_fastq_bytes", "candidate_status",
    "linkage_status", "processed_virome_profiles_retrieved",
    "verified_virome_immune_matches",
]


def workbook_keys(rows):
    """Read source-local literal keys, including row provenance but no assays."""
    rows = iter(rows)
    try:
        header = next(rows)
    except StopIteration as exc:
        raise ValueError("Empty FVT source worksheet") from exc
    if tuple(header[:2]) != ("id", "group"):
        raise ValueError("Unexpected FVT source worksheet header")
    result, seen = [], set()
    for row_number, values in enumerate(rows, 2):
        if not any(value is not None for value in values):
            continue
        if len(values) < 2 or values[0] is None or not values[1]:
            raise ValueError(f"Missing FVT source key at row {row_number}")
        identifier, group = literal_id(values[0]), str(values[1])
        key = (group, identifier)
        if key in seen:
            raise ValueError(f"Duplicate FVT source key at row {row_number}")
        seen.add(key)
        result.append({"workbook_row": row_number, "workbook_group": group,
                       "workbook_id": identifier})
    return result


def _fastq_counts(run):
    values = run.get("fastq_bytes", "").split(";")
    if not values or any(not value or not value.isascii() or not value.isdecimal()
                         for value in values):
        raise ValueError(f"Invalid FASTQ byte inventory for {run.get('run_accession')}")
    return len(values), sum(int(value) for value in values)


def _joined_runs(runs, attributes):
    """Join on accession AND literal alias; reject ambiguous metadata identities."""
    by_accession, by_alias = {}, {}
    for row in attributes:
        accession, alias = row.get("sample_accession"), row.get("sample_alias")
        if not accession or not alias:
            raise ValueError("Missing sample accession or alias")
        if accession in by_accession or alias in by_alias:
            raise ValueError("Duplicate sample accession or alias")
        by_accession[accession], by_alias[alias] = row, accession
    result, seen_runs, used_samples = [], set(), set()
    specimen_keys = {}
    for run in runs:
        run_id, accession = run.get("run_accession"), run.get("sample_accession")
        if not run_id or run_id in seen_runs:
            raise ValueError("Missing or duplicate run accession")
        seen_runs.add(run_id)
        if accession not in by_accession:
            raise ValueError(f"Run has no sample metadata: {accession}")
        attrs = by_accession[accession]
        if run.get("sample_alias") != attrs["sample_alias"]:
            raise ValueError(f"Run/sample alias disagreement: {accession}")
        used_samples.add(accession)
        role = classify_sequencing_sample(attrs["sample_alias"], attrs)
        condition, status = attrs.get("sample_type", ""), attrs.get("gavage_status", "")
        if not condition or status not in ("Before", "After", "Gavage"):
            raise ValueError(f"Missing condition or unexpected time label: {accession}")
        if (role == "transplant_inoculum") != (status == "Gavage"):
            raise ValueError(f"Inconsistent specimen role and time label: {accession}")
        replicate = attrs.get("replicate_num", "")
        if role == RECIPIENT:
            if not replicate or replicate.lower() in ("na", "n/a", "none"):
                raise ValueError(f"Missing recipient replicate label: {accession}")
            key = (condition, replicate, status)
            if key in specimen_keys and specimen_keys[key] != accession:
                raise ValueError(f"Ambiguous recipient condition/replicate/time: {key}")
            specimen_keys[key] = accession
        file_count, byte_count = _fastq_counts(run)
        result.append({
            "run_accession": run_id, "sample_accession": accession,
            "source_condition": condition, "specimen_role": role,
            "gavage_status": status, "replicate_num": replicate,
            "fastq_file_count": file_count, "compressed_fastq_bytes": byte_count,
        })
    if used_samples != set(by_accession):
        raise ValueError("Sample metadata and run inventory accession sets differ")
    return result


def _totals(rows):
    return {
        "run_count": len(rows),
        "specimen_count": len({row["sample_accession"] for row in rows}),
        "fastq_file_count": sum(row["fastq_file_count"] for row in rows),
        "compressed_fastq_bytes": sum(row["compressed_fastq_bytes"] for row in rows),
    }


def derive(runs, attributes, keys):
    """Return design inventory, candidate-label table and exact count summary.

    Repeated technical runs remain multiple runs of one specimen. Control IDs
    are deliberately excluded from candidate linkage: their decimal workbook
    labels and altered sequencing aliases have no validated translation.
    """
    joined = _joined_runs(runs, attributes)
    strata = defaultdict(list)
    recipient_keys = defaultdict(list)
    for row in joined:
        strata[(row["source_condition"], row["specimen_role"], row["gavage_status"])].append(row)
        if row["specimen_role"] == RECIPIENT:
            recipient_keys[(row["source_condition"], row["replicate_num"])].append(row)
    inventory = []
    for (condition, role, status), rows in sorted(strata.items()):
        inventory.append({
            "accession": "PRJNA970614", "source_condition": condition,
            "specimen_role": role, "gavage_status": status, **_totals(rows),
            "source": (ARCHIVE / "PRJNA970614_ena_runs.tsv").as_posix()
                      + ";" + (ARCHIVE / "PRJNA970614_sample_attributes.csv").as_posix(),
        })
    candidates, candidate_runs, paired_runs, seen_keys = [], [], [], set()
    for key in keys:
        group, identifier = key["workbook_group"], key["workbook_id"]
        if (group, identifier) in seen_keys:
            raise ValueError("Duplicate workbook candidate key")
        seen_keys.add((group, identifier))
        if group not in TARGET_CONDITIONS:
            continue
        condition = TARGET_CONDITIONS[group]
        rows = recipient_keys.get((condition, identifier), [])
        before = [row for row in rows if row["gavage_status"] == "Before"]
        after = [row for row in rows if row["gavage_status"] == "After"]
        candidate_runs.extend(rows)
        if before and after:
            status = "before_after_candidate"
            paired_runs.extend(rows)
        elif before:
            status = "before_only"
        elif after:
            status = "after_only"
        else:
            status = "no_matching_recipient_label"
        record = {
            "workbook_sheet": SHEET, **key, "ena_sample_type": condition,
            "replicate_num": identifier if rows else "",
        }
        for prefix, subset in (("before", before), ("after", after)):
            record[prefix + "_sample_accessions"] = ";".join(sorted({
                row["sample_accession"] for row in subset}))
            record[prefix + "_run_accessions"] = ";".join(sorted(
                row["run_accession"] for row in subset))
            record.update({prefix + "_" + name: value for name, value in _totals(subset).items()})
        record.update({
            "total_run_count": len(rows),
            "total_compressed_fastq_bytes": sum(row["compressed_fastq_bytes"] for row in rows),
            "candidate_status": status,
            "linkage_status": "literal_label_candidate_not_validated_crosswalk",
            "processed_virome_profiles_retrieved": 0,
            "verified_virome_immune_matches": 0,
        })
        candidates.append(record)
    recipient = [row for row in joined if row["specimen_role"] == RECIPIENT]
    hk = [row for row in joined if row["source_condition"].startswith("hkFVT")]
    summary = {
        "inventory": _totals(joined), "recipient_bulk": _totals(recipient),
        "candidate_workbook_keys": len(candidates),
        "candidate_recipients": _totals(candidate_runs),
        "candidate_before_after_keys": sum(row["candidate_status"] == "before_after_candidate"
                                            for row in candidates),
        "paired_candidate_recipients": _totals(paired_runs),
        "hkFVT_by_role": {role: _totals([row for row in hk if row["specimen_role"] == role])
                          for role in sorted({row["specimen_role"] for row in hk})},
        "linkage_status": "literal_label_candidate_not_validated_crosswalk",
        "processed_virome_profiles_retrieved": 0, "verified_virome_immune_matches": 0,
    }
    return inventory, candidates, summary


def run(root, config):
    """Derive two evidence tables from the unchanged frozen source inputs."""
    from openpyxl import load_workbook

    root = Path(root)
    runs = read_csv(root / ARCHIVE / "PRJNA970614_ena_runs.tsv", delimiter="\t")
    attributes = read_csv(root / ARCHIVE / "PRJNA970614_sample_attributes.csv")
    workbook = load_workbook(root / "data/raw/source_data.xlsx", read_only=True, data_only=True)
    try:
        keys = workbook_keys(workbook[SHEET].iter_rows(values_only=True))
    finally:
        workbook.close()
    inventory, candidates, summary = derive(runs, attributes, keys)
    write_csv(root / "results/tables/sequencing_design_inventory.csv", inventory, INVENTORY_FIELDS)
    write_csv(root / "results/tables/candidate_recipient_pairs.csv", candidates, PAIR_FIELDS)
    return summary
