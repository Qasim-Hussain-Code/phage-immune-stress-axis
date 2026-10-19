"""Identifier invariants use artificial records, never biological test data."""

import unittest

from pisa.samples import (
    _fastq_counts,
    _sequencing_record,
    _workbook_records,
    literal_id,
    source_animal_key,
)


class SampleIdentityTests(unittest.TestCase):
    def test_identifiers_require_experiment_and_group(self):
        self.assertNotEqual(
            source_animal_key("experiment1", "control", 1),
            source_animal_key("experiment1", "stress", 1),
        )
        self.assertNotEqual(
            source_animal_key("experiment1", "control", 1),
            source_animal_key("experiment2", "control", 1),
        )
        with self.assertRaises(ValueError):
            source_animal_key("experiment1", "", 1)

    def test_decimal_source_ids_do_not_collapse(self):
        values = [1.1, 1.2, 19.1, 19.2, "1x2", "12"]
        keys = [source_animal_key("fvt", "ctr", value) for value in values]
        self.assertEqual(len(set(keys)), len(values))
        self.assertEqual(literal_id(19.2), "19.2")
        self.assertNotEqual(literal_id("1.10"), literal_id("1.1"))

    def test_source_rows_match_only_observed_within_row_assays(self):
        artificial_rows = [
            ("id", "group", "sit_si_ratio", "ly6chi_monocytes", "cort_auc"),
            (1.1, "ctr", 0, 0, None),
            (1.1, "ctr_stress", 2, None, 5),
            (None, None, None, None, None),
        ]
        rows = _workbook_records(artificial_rows, "test", "test sheet")
        self.assertEqual(len(rows), 2)
        self.assertNotEqual(rows[0]["sample_id"], rows[1]["sample_id"])
        self.assertEqual(rows[0]["mouse_id"], "1.1")
        self.assertEqual(rows[0]["matched_assays"], "immune;behavior")
        self.assertTrue(rows[0]["immune_available"])
        self.assertFalse(rows[1]["immune_available"])
        self.assertEqual(rows[1]["matched_assays"], "")
        self.assertFalse(rows[0]["virome_available"])

    def test_duplicate_source_row_fails_instead_of_merging(self):
        rows = [("id", "group", "sit_x"), (1, "ctr", 1), (1, "ctr", 2)]
        with self.assertRaisesRegex(ValueError, "Duplicate source animal key"):
            _workbook_records(rows, "test", "test sheet")

    def test_pool_cannot_link_to_an_individual(self):
        run = {"sample_accession": "TESTPOOL", "sample_alias": "ControlBeforepool", "run_accession": "TESTRUN"}
        attributes = {
            "sample_alias": "ControlBeforepool", "sample_type": "Control",
            "replicate_num": "1", "gavage_status": "Before",
        }
        row = _sequencing_record([run], attributes)
        self.assertEqual(row["pool_id"], "ControlBeforepool")
        self.assertEqual(row["mouse_id"], "")
        self.assertEqual(row["metadata_candidate_mouse_id"], "")
        self.assertEqual(row["matched_assays"], "")
        self.assertFalse(row["immune_available"])

    def test_inoculum_not_assigned_to_recipient(self):
        run = {"sample_accession": "TESTGAVAGE", "sample_alias": "FVTGavage9", "run_accession": "TESTRUN"}
        attributes = {
            "sample_alias": "FVTGavage9", "sample_type": "FVT gavage",
            "replicate_num": "9", "gavage_status": "Gavage",
        }
        row = _sequencing_record([run], attributes)
        self.assertEqual(row["sample_type"], "transplant_inoculum")
        self.assertEqual(row["mouse_id"], "")
        self.assertEqual(row["metadata_candidate_mouse_id"], "")

    def test_fastq_sizes_count_files_not_biological_replicates(self):
        self.assertEqual(_fastq_counts({"fastq_bytes": "100;120"}), (2, 220))
        with self.assertRaises(ValueError):
            _fastq_counts({"fastq_bytes": "100;-1"})


if __name__ == "__main__":
    unittest.main()
