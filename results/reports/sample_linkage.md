# Sample linkage audit

This report is generated from frozen accession manifests, BioSample attributes,
and the supplementary source workbook. No raw reads were downloaded.

## Counts and source scope

PRJNA970614 contains 104 runs representing 104 sequencing
specimens. Categories from explicit aliases/BioSample attributes are individual_recipient_bulk_metagenome: 77, pooled_fecal_virome: 8, transplant_inoculum: 19.
These specimen counts are not independent animal counts. Multiple runs per
specimen, if encountered, share an accession row and remain technical sequencing
observations. Compressed FASTQ sizes total
262,211,457,238 bytes before processing.

The source workbook contributes 50 animal rows:

| Experiment | Literal group | Animal rows |
|---|---|---:|
| fvt_study_ii | ctr | 10 |
| fvt_study_ii | ctr_stress | 10 |
| fvt_study_ii | fvt_stress | 10 |
| stress_study_i | Control | 10 |
| stress_study_i | Stress | 10 |

The linkage CSV includes these principal sequencing specimens and source-workbook
animal rows. PRJEB69687 and PRJEB67706 are represented by totals in
`sequencing_inventory.csv`; their aliases are not assigned to workbook animals.

## Identifier policy

`sample_id` is a literal BioSample accession for a sequencing specimen. Workbook
keys are explicitly constructed from experiment, literal group, and literal ID.
They identify a source row and do not assert a shared upstream animal naming
scheme. Workbook `mouse_id` remains source-local. Initial-study IDs restart in
each treatment group. Decimal identifiers such as `1.1`, `1.2`, `19.1`, and `19.2`
retain their punctuation and never become integer IDs. No match uses row order,
punctuation removal, numeric rounding, or presumed renumbering.

Sequencing `replicate_num` values are retained only as experiment/accession and
group-qualified `metadata_candidate_mouse_id` keys. They do not populate
`mouse_id`, and no candidate is joined to the workbook. This metadata contains
42 candidate animal keys, with
35 having both explicit Before
and After specimen annotations. These are candidate repeated raw specimens,
not calculated longitudinal viral profiles. Before/After comes from the
BioSample `gavage_status` field. Pool aliases populate `pool_id`; pools have no
individual mouse ID or candidate ID. Inocula remain exposure material and are
never recipient intestinal observations. Heat-inactivated FVT specimens remain
in the sequencing inventory despite no corresponding source-workbook group.

## What is available and linked

The boolean `virome_available` and `bacteriome_available` fields mean a retrieved
processed abundance profile, not the existence of deposited raw reads. Both are
false for all audit rows. `raw_reads_deposited` distinguishes sequenced specimens.
The workbook has 50 rows with at
least one observed immune measurement and
50 with a behavioral measurement.
There are 50 same-row immune and
behavior links. Individual endpoint missingness is not summarized by these
any-assay flags. Corticosterone is treated as endocrine and does not create an
immune-available flag. The source's late incomplete animal is retained.

No retrieved abundance profile is linked to an immune outcome. The original
paper describes individual bulk-metagenomic reads mapped to a gavage-derived
viral catalog, alongside pooled enriched viromes. Therefore the obstacle is
missing processed inputs and an unverified crosswalk, rather than a claim that
all original viral measurements were pooled. Do not infer phage-immune
associations, bacterial adjustment, recipient viral load from inoculum spikes,
or measured longitudinal stability from this inventory.

Source-row immune/behavior links remain valid within their sheet. Whole-study
mouse and pool membership across assays remain unresolved. See
`data_feasibility.md` and `docs/paper_audit_notes.md` for experimental details.
