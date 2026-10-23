# Data available for reanalysis

The public releases inspected on 20 October 2026 provide individual immune
source data, raw sequencing reads and detailed specimen metadata. Reassessment
of these frozen inputs on 23 October identified literal sequencing-label
matches for all 20 Stress/FVT workbook rows and candidate before/after pairs
for 17. These matches make a recipient reprocessing route identifiable. They
do not supply the processed viral abundances, calibration records or validated
crosswalk needed for viral-change versus immune-endpoint analysis.

The original study analysed individual recipient bulk metagenomes as well as
pooled enriched viromes. The present limits combine missing processed inputs,
unresolved analytic linkage and the resources required to rebuild those inputs
from raw reads. The 23 October reassessment used the existing frozen files;
it did not retrieve sequencing reads or new biological measurements.

## Retrieved source collection

The frozen [input manifest](../data/manifests/inputs.json) contains ten files.
It records their URLs, byte sizes, SHA-256 checksums and any transformation.
[Data provenance](data_provenance.md) describes their acquisition and reuse.

| Source | Retrieved material | Information supplied |
|---|---|---|
| [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y) | Europe PMC article XML | Experimental design, assay methods, captions and declared data locations |
| Publisher source data | One 23,358-byte workbook | Fifty animal rows across two experiments, with immune and behavioral measurements and assay-specific missingness |
| [Zenodo release 10460215](https://zenodo.org/records/10460215) | Release catalog and its sole file, the 502,039-byte script PDF | Analysis code and references to local input tables; the inspected release does not contain those tables |
| [PRJNA970614](https://www.ebi.ac.uk/ena/browser/view/PRJNA970614) | Run report, study XML, complete sample XML and a selected-sample XML subset | Run/specimen identities, specimen roles, Before/After annotations and compressed-read sizes |
| [PRJEB69687](https://www.ebi.ac.uk/ena/browser/view/PRJEB69687) | 16S run report | Additional sequence inventory, without a processed bacterial table or verified immune crosswalk |
| [PRJEB67706](https://www.ebi.ac.uk/ena/browser/view/PRJEB67706) | Transcriptomic run report | Additional sequence inventory, without assigning its samples to workbook animals |

No raw reads were downloaded. The exact inventory and the narrower candidate
recipient subset are distinguished below; the whole-project size is not the
cost of processing only the relevant Stress/FVT labels.

## Specimens are not interchangeable with animals

The initial experiment contributes 20 workbook rows, ten Control and ten
Stress, with identifiers that restart within group. Its enriched viromes
combine three or four animals per pool. The figure captions describe three
pools per group at each of two times, implying 12 published pool-by-time
profiles. Pool membership across time is unresolved, and the article's prose
and captions differ in their contributor counts. These profiles cannot be
treated as 12 independent mouse trajectories or assigned individually to the
20 immune rows.

The FVT experiment contributes 30 workbook rows, ten per published treatment,
with fewer observations for some assays. The deposited PRJNA970614 inventory
contains 104 runs for 104 specimens: 77 individual recipient bulk specimens,
eight pool-labelled specimens and 19 inocula. Its treatment labels extend
beyond the three source-workbook groups:

| Deposited condition | Bulk Before | Bulk After | Inocula | Pools Before / After |
|---|---:|---:|---:|---:|
| Control | 10 | 10 | 0 | 1 / 1 |
| Control stress | 10 | 8 | 0 | 1 / 1 |
| FVT stress / FVT gavage | 10 | 9 | 9 | 1 / 1 |
| hkFVT stress / hkFVT gavage | 10 | 10 | 10 | 1 / 1 |

The [sequencing design inventory](../results/tables/sequencing_design_inventory.csv)
retains the literal condition, role and time labels, with run, specimen, file
and compressed-byte counts. Inocula and pools are not additional recipient
animals. Technical runs would likewise remain runs of the same specimen.

The 32 hkFVT-labelled specimens are scientifically relevant to treatment
specificity. Their relationship to the published three-arm experiment is
unresolved: the workbook has no hkFVT rows, and the article describes assessment
of fully inactivated FVT as future work (Discussion, XML Sec8). Metadata alone
does not establish whether these specimens share its cohort, allocation or
assays. A verified active-versus-inactivated preparation comparison would be
informative, but heat treatment can alter several constituents; that comparison
alone would not isolate phage infectivity or prove phage-specific causality.

Individual recipient bulk metagenomes were mapped to an inoculum-derived viral
catalog in the original analysis. An inoculum measures administered material;
it cannot replace the recipient's intestinal profile. The
[article design audit](paper_audit_notes.md) gives the evidence for each
measurement route and its timing.

## Literal recipient labels and raw-read scope

Within a workbook sheet, assays are linked by experiment, treatment and literal
source ID. The ten Control Stress IDs are `4,5,6,7,8,22,23,24,25,26`; the ten
FVT Stress IDs are `9,10,11,12,13,27,28,29,30,31`. Every one has an exact
condition-qualified match to ENA `replicate_num`. Stress IDs 6 and 7 and FVT
ID 11 have Before specimens only. The other 17 have both Before and After
specimens: eight Stress and nine FVT candidates. The
[candidate-pair table](../results/tables/candidate_recipient_pairs.csv) records
their source rows, accessions, run inventories and bytes without assigning
processed profiles or verified viral-immune matches.

Control labels require a different caution. Only source IDs `3` and `21`
match literally. Aliases containing `191`, `19x2` or `1x2` cannot be equated
with workbook decimals by punctuation removal or row position. Controls are
therefore excluded from this candidate-pair table. Numeric label blocks do
not independently verify experimental batches or cages.

| Scope | Runs in scope | Compressed FASTQ bytes | Decimal GB |
|---|---:|---:|---:|
| Whole PRJNA970614 project, including pools and inocula | 104 total runs | 262,211,457,238 | 262.211 |
| All individual recipient bulk specimens | 77 | 189,984,457,053 | 189.984 |
| All 20 literal Stress/FVT candidate keys | 37 | 92,534,634,174 | 92.535 |
| Seventeen complete candidate before/after pairs | 34 | 85,586,830,532 | 85.587 |

The roughly 190 GB figure describes all 77 recipient specimens, not just the
20 Stress/FVT source keys. These are compressed input sizes, excluding
assembly, databases, outputs and working space. A new resource plan could
evaluate reprocessing the smaller subset; no such reconstruction was run here.

Literal concordance is a useful starting point, not the final analytic map.
The archived scripts (pp. 15–16) reference `recal_metadata.csv`,
`Proposed_mouse_ID`, `Full_ID`, `post_recal_name`, `calib_batch` and calibration
plate tables. One community-processing path excludes IDs 6, 7 and 11 and
`Contrasts == "hkFVT"`. Its rationale and translation to the processed columns
are not supplied by the workbook or ENA metadata. Those filters do not justify
removing observations from every immune assay. The similarly promising
`bacteriome.virome.matching.fvt.stress.051022.csv` is used on script p. 23 to
select taxa by `Location` and recode host phyla; its filename does not verify
an animal crosswalk.

## Which questions are currently estimable?

| Question | Required observations | Present status |
|---|---|---|
| Treatment differences in selected immune endpoints | Individual immune values and treatment labels | Available for separate exploratory contrasts |
| Stress-associated viral composition | Processed recipient or pool abundance profiles with appropriate biological units and annotations | Matrix unavailable |
| Within-mouse viral change | Repeated individual recipient viral profiles and verified pairing across time | Seventeen literal raw-specimen pairs identified; processed values and final analytic mapping missing |
| Viral change or reference-state deviation versus an immune endpoint | Individual viral features and an explicit map to the measured immune animals | Twenty candidate Stress/FVT keys identified, 17 paired; no processed viral profiles or validated cross-assay matches |
| Within-mouse immune change or chronic-stress immune stability | Repeated immune measurements spanning the relevant stress interval | Not supplied by the selected endpoint assays |
| Bacterial-adjusted viral-immune association | Matched viral, bacterial and immune measurements, with adequate complete-case replication | Processed community tables and crosswalk unavailable |

A prestress immune baseline is not required to relate viral change to an endpoint
immune phenotype. It is required, together with a later immune measurement, to
define within-animal immune change. The current viral-immune endpoint question
is blocked by the missing viral matrix and validated analytic crosswalk,
independently of the absence of an immune baseline. No measured viral composition, stability,
reference deviation, bacterial-adjusted association or phage-host relationship
is reported here. This is an availability conclusion, not a biological null.

## Search scope and requirements for further analysis

The [data-search overview](data_search.md) summarizes the primary release and
alternative-study checks performed on 20 October 2026.

The [expanded primary-data search](processed_data_search.md), dated 20 October
2026, checked the complete publisher-linked supplementary package, BioStudies,
accession-linked analysis and assembly records, MGnify, selected author
repositories and data/code indexes. Its 32-member supplementary inventory
contains the same phenotype workbook, a reporting PDF and figure/table images.
It supplies no additional community matrix. The 52 saved evidence records
document the checked routes, rather than 52 independent datasets or an
exhaustive search of every possible location.

The [alternative-study audit](alternative_dataset_audit.md) distinguishes donor
viromes from recipient measurements and immune assays from endocrine or
metabolite outcomes. It did not verify an eligible replacement. The relevant
[Chen 2026 candidate](new_prenatal_stress_candidate.md) remains unresolved after
a [focused public-route follow-up](chen2026_public_route_followup.md); access
failures are not treated as data-absence evidence.

Further analysis requires processed individual recipient viral abundances,
sample times and animal identifiers; a crosswalk to immune source rows that
records exclusions, calibration and pool membership; and contig quality and
viral-classification annotations. Bacterial adjustment additionally requires
matched bacterial abundances. The inoculum-derived catalog's detectable viral
fraction, predicted hosts and normalization choices would then need assessment.
The [data requirements](data_requirements.md) give a reusable checklist,
including hkFVT provenance, calibration and exclusion decisions. Any release
or reconstructed matrix must first pass a new sample-linkage and completeness
review.

The supported analysis retains the selected immune contrasts, original-method
reconstruction and descriptive sensitivity checks described in
[methods](methods.md). The endpoints were selected after reading the published
findings and before calculating the present contrasts, so this remains
exploratory work.
