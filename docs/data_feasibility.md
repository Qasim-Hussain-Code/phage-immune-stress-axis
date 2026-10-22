# Data available for reanalysis

The public releases inspected on 20 October 2026 provide individual immune
source data and detailed sequencing metadata. They do not provide the processed
recipient viral abundance matrix and verified animal crosswalk needed to relate
viral change to immune phenotypes. The original study did analyse individual
recipient bulk metagenomes as well as pooled enriched viromes; the missing
inputs concern access to those measurements and their linkage.

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

No raw reads were downloaded. PRJNA970614 alone lists 262,211,457,238 bytes of
compressed FASTQ files, before assembly, reference databases or temporary
products. Reconstructing the original community tables from those reads was
outside this small-file reanalysis.

## Specimens are not interchangeable with animals

The initial experiment contributes 20 workbook rows, ten Control and ten
Stress, with identifiers that restart within group. Its enriched viromes
combine three or four animals per pool. The figure captions describe three
pools per group at each of two times, implying 12 published pool-by-time
profiles. Pool membership across time is unresolved, and the article's prose
and captions differ in their contributor counts. These profiles cannot be
treated as 12 independent mouse trajectories or assigned individually to the
20 immune rows.

The FVT experiment contributes 30 workbook rows, ten per treatment, with fewer
observations for some assays. The deposited PRJNA970614 inventory contains
104 runs for 104 specimens: 77 individual recipient bulk specimens, eight
pool-labelled specimens and 19 inocula. These categories include samples from
a heat-inactivated treatment absent from the source workbook. The inventory
therefore represents neither 104 animals nor 104 immune-matched profiles.

Individual recipient bulk metagenomes were mapped to an inoculum-derived viral
catalog in the original analysis. An inoculum measures administered material;
it cannot replace the recipient's intestinal profile. The
[article design audit](paper_audit_notes.md) gives the evidence for each
measurement route and its timing.

Within a workbook sheet, assays are linked by experiment, treatment and literal
source ID. Across sequencing and phenotype resources, a documented map is still
needed. Aliases such as `Ctr191`, `Ctr19x2` and `Ctr1x2` cannot be equated with
source IDs such as `1.1` and `19.2` by punctuation removal or row position.
Some labels are compatible, but compatibility does not supply abundance values
or resolve recalibrated and excluded samples.

## Which questions are currently estimable?

| Question | Required observations | Present status |
|---|---|---|
| Treatment differences in selected immune endpoints | Individual immune values and treatment labels | Available for separate exploratory contrasts |
| Stress-associated viral composition | Processed recipient or pool abundance profiles with appropriate biological units and annotations | Matrix unavailable |
| Within-mouse viral change | Repeated individual recipient viral profiles and verified pairing across time | Published measurement route identified; processed values and pairing unavailable |
| Viral change or reference-state deviation versus an immune endpoint | Individual viral features and an explicit map to the measured immune animals | Not estimable from the retrieved inputs |
| Within-mouse immune change or chronic-stress immune stability | Repeated immune measurements spanning the relevant stress interval | Not supplied by the selected endpoint assays |
| Bacterial-adjusted viral-immune association | Matched viral, bacterial and immune measurements, with adequate complete-case replication | Processed community tables and crosswalk unavailable |

A prestress immune baseline is not required to relate viral change to a terminal
immune phenotype. It is required, together with a later immune measurement, to
define within-animal immune change. The current viral-immune endpoint question
is blocked by the missing viral matrix and crosswalk, independently of the
absence of an immune baseline. No measured viral composition, stability,
reference deviation, bacterial-adjusted association or phage-host relationship
is reported here. This is an availability conclusion, not a biological null.

## Search scope and requirements for further analysis

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
Any release must first pass a new sample-linkage and completeness review.

The supported analysis retains the selected immune contrasts, original-method
reconstruction and descriptive sensitivity checks described in
[methods](methods.md). The endpoints were selected after reading the published
findings and before calculating the present contrasts, so this remains
exploratory work.
