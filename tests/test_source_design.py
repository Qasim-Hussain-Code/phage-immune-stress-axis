"""Raw-read design accounting never creates a verified cross-assay match."""

import copy
import unittest

from pisa.source_design import RECIPIENT, derive, workbook_keys


def source_design_fixture():
    """Artificial accessions preserve the independently audited strata/totals.

    No phenotype values or sequencing reads enter these software fixtures.
    The totals are fixed expectations from the frozen ENA metadata, not values
    calculated with the functions under test.
    """
    stress = ["4", "5", "6", "7", "8", "22", "23", "24", "25", "26"]
    fvt = ["9", "10", "11", "12", "13", "27", "28", "29", "30", "31"]
    control_b = ["11", "12", "191", "192", "202", "20x1", "21", "22", "2x1", "3"]
    control_a = ["11", "1x2", "191", "19x2", "202", "20x1", "21", "22", "2x1", "3"]
    strata = [
        ("Control", "Before", "bulk", control_b, 27340474318),
        ("Control", "After", "bulk", control_a, 19347772064),
        ("Control stress", "Before", "bulk", stress, 25175514338),
        ("Control stress", "After", "bulk", [x for x in stress if x not in ("6", "7")], 18415480841),
        ("FVT stress", "Before", "bulk", fvt, 24048176624),
        ("FVT stress", "After", "bulk", [x for x in fvt if x != "11"], 24895462371),
        ("hkFVT stress", "Before", "bulk", [str(x) for x in range(32, 42)], 25687262797),
        ("hkFVT stress", "After", "bulk", [str(x) for x in range(32, 42)], 25074313700),
        ("FVT gavage", "Gavage", "inoculum", fvt[:9], 21640370591),
        ("hkFVT gavage", "Gavage", "inoculum", [str(x) for x in range(32, 42)], 21179190107),
        ("Control", "Before", "pool", ["NA"], 2298342771),
        ("Control", "After", "pool", ["NA"], 6201417648),
        ("Control stress", "Before", "pool", ["NA"], 3029938190),
        ("Control stress", "After", "pool", ["NA"], 3168521803),
        ("FVT stress", "Before", "pool", ["NA"], 2884200470),
        ("FVT stress", "After", "pool", ["NA"], 4003629493),
        ("hkFVT stress", "Before", "pool", ["NA"], 2909615820),
        ("hkFVT stress", "After", "pool", ["NA"], 4911773292),
    ]
    runs, attrs = [], []
    for condition, status, role, identifiers, byte_total in strata:
        quotient, remainder = divmod(byte_total, len(identifiers))
        for index, identifier in enumerate(identifiers):
            number = len(runs) + 1
            alias = f"fixture_{number}_{role}"
            accession, run_id = f"SAMPLE{number}", f"RUN{number}"
            size = quotient + (index < remainder)
            first, second = size // 2, size - size // 2
            attrs.append({"sample_accession": accession, "sample_alias": alias,
                          "sample_type": condition, "gavage_status": status,
                          "replicate_num": identifier})
            runs.append({"sample_accession": accession, "sample_alias": alias,
                         "run_accession": run_id, "fastq_bytes": f"{first};{second}"})
    rows = [("id", "group"), ("1.1", "ctr"), ("3", "ctr"), ("21", "ctr")]
    rows += [(identifier, "ctr_stress") for identifier in stress]
    rows += [(identifier, "fvt_stress") for identifier in fvt]
    return runs, attrs, workbook_keys(rows)


class SourceDesignTests(unittest.TestCase):
    def setUp(self):
        self.runs, self.attrs, self.keys = source_design_fixture()

    def test_independent_source_strata_counts_and_bytes(self):
        inventory, candidates, summary = derive(self.runs, self.attrs, self.keys)
        self.assertEqual(len(inventory), 18)
        self.assertEqual(summary["inventory"], {
            "run_count": 104, "specimen_count": 104, "fastq_file_count": 208,
            "compressed_fastq_bytes": 262211457238,
        })
        self.assertEqual(summary["recipient_bulk"]["run_count"], 77)
        self.assertEqual(summary["recipient_bulk"]["compressed_fastq_bytes"], 189984457053)
        self.assertEqual(summary["candidate_workbook_keys"], 20)
        self.assertEqual(summary["candidate_recipients"]["run_count"], 37)
        self.assertEqual(summary["candidate_recipients"]["compressed_fastq_bytes"], 92534634174)
        self.assertEqual(summary["candidate_before_after_keys"], 17)
        self.assertEqual(summary["paired_candidate_recipients"]["run_count"], 34)
        # Complete pairs omit the three before-only source labels. The fixture's
        # within-stratum sizes are artificial; real paired bytes are derived at run time.
        self.assertLess(summary["paired_candidate_recipients"]["compressed_fastq_bytes"],
                        summary["candidate_recipients"]["compressed_fastq_bytes"])
        hk = summary["hkFVT_by_role"]
        self.assertEqual(hk[RECIPIENT]["specimen_count"], 20)
        self.assertEqual(hk["transplant_inoculum"]["specimen_count"], 10)
        self.assertEqual(hk["pooled_fecal_virome"]["specimen_count"], 2)
        self.assertEqual({(r["workbook_group"], r["workbook_id"]) for r in candidates
                          if r["candidate_status"] == "before_only"},
                         {("ctr_stress", "6"), ("ctr_stress", "7"), ("fvt_stress", "11")})

    def test_control_labels_remain_excluded_even_when_literal_labels_overlap(self):
        _, candidates, _ = derive(self.runs, self.attrs, self.keys)
        self.assertTrue(any(row["replicate_num"] == "3" for row in self.attrs))
        self.assertEqual({row["workbook_group"] for row in candidates}, {"ctr_stress", "fvt_stress"})
        self.assertTrue(all(row["workbook_id"] not in ("1.1", "3", "21") for row in candidates))

    def test_pool_and_inoculum_labels_cannot_supply_recipient_candidates(self):
        for attrs in self.attrs:
            if "pool" in attrs["sample_alias"]:
                attrs["sample_type"], attrs["replicate_num"] = "Control stress", "6"
            elif attrs["gavage_status"] == "Gavage":
                attrs["sample_type"], attrs["replicate_num"] = "Control stress", "6"
        _, candidates, _ = derive(self.runs, self.attrs, self.keys)
        six = next(row for row in candidates if row["workbook_id"] == "6")
        self.assertEqual(six["candidate_status"], "before_only")
        self.assertEqual(six["total_run_count"], 1)

    def test_multiple_runs_of_one_specimen_do_not_add_an_animal(self):
        run = copy.deepcopy(self.runs[20])  # Control Stress before label 4.
        run.update(run_accession="EXTRA_TECHNICAL_RUN", fastq_bytes="3;4")
        self.runs.append(run)
        _, candidates, summary = derive(self.runs, self.attrs, self.keys)
        four = next(row for row in candidates if row["workbook_group"] == "ctr_stress"
                    and row["workbook_id"] == "4")
        self.assertEqual(four["before_run_count"], 2)
        self.assertEqual(four["before_specimen_count"], 1)
        self.assertEqual(summary["candidate_before_after_keys"], 17)
        self.assertEqual(summary["candidate_recipients"]["specimen_count"], 37)
        self.assertEqual(summary["candidate_recipients"]["compressed_fastq_bytes"], 92534634181)

    def test_duplicate_or_unjoined_accessions_fail_closed(self):
        for change in ("duplicate_run", "duplicate_sample", "alias_disagreement", "orphan_sample"):
            with self.subTest(change=change):
                runs, attrs = copy.deepcopy(self.runs), copy.deepcopy(self.attrs)
                if change == "duplicate_run":
                    runs.append(copy.deepcopy(runs[0]))
                elif change == "duplicate_sample":
                    attrs.append(copy.deepcopy(attrs[0]))
                elif change == "alias_disagreement":
                    runs[0]["sample_alias"] += "_different"
                else:
                    runs.pop()
                with self.assertRaises(ValueError):
                    derive(runs, attrs, self.keys)

    def test_ambiguous_recipient_condition_time_label_fails(self):
        self.attrs[1]["replicate_num"] = self.attrs[0]["replicate_num"]
        with self.assertRaisesRegex(ValueError, "Ambiguous recipient"):
            derive(self.runs, self.attrs, self.keys)

    def test_literal_ids_are_not_repaired_and_condition_qualifies_identity(self):
        keys = workbook_keys([("id", "group"), ("4.0", "ctr_stress"),
                              ("4", "fvt_stress"), ("4", "ctr_stress")])
        _, candidates, _ = derive(self.runs, self.attrs, keys)
        self.assertEqual([row["candidate_status"] for row in candidates],
                         ["no_matching_recipient_label", "no_matching_recipient_label", "before_after_candidate"])
        self.assertEqual(candidates[0]["workbook_id"], "4.0")

    def test_candidate_table_does_not_claim_processed_or_verified_linkage(self):
        _, candidates, summary = derive(self.runs, self.attrs, self.keys)
        self.assertEqual(summary["verified_virome_immune_matches"], 0)
        for row in candidates:
            self.assertEqual(row["linkage_status"], "literal_label_candidate_not_validated_crosswalk")
            self.assertEqual(row["processed_virome_profiles_retrieved"], 0)
            self.assertEqual(row["verified_virome_immune_matches"], 0)

    def test_invalid_bytes_and_duplicate_workbook_keys_fail(self):
        for invalid in ("", "1;", "1;-1", "1;2.0", "1; 2"):
            with self.subTest(invalid=invalid):
                runs = copy.deepcopy(self.runs)
                runs[0]["fastq_bytes"] = invalid
                with self.assertRaises(ValueError):
                    derive(runs, self.attrs, self.keys)
        with self.assertRaisesRegex(ValueError, "Duplicate FVT source key"):
            workbook_keys([("id", "group"), (4, "ctr_stress"), (4, "ctr_stress")])


if __name__ == "__main__":
    unittest.main()
