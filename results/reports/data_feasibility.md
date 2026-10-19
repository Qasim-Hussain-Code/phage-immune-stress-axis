# Data feasibility gate

Audit date: 2026-10-20. This gate was recorded before implementation of the
selected biological analyses. Numerical outcome summaries were not used to
select endpoints. The original article's published findings were already known;
the subsequent immune reanalysis is exploratory, not a registered confirmation.

## Retrieved inputs and experimental units

The open-access full article XML (PMC10847049), supplementary source workbook
(23,358 bytes), Zenodo release metadata and its only archived file, the 75-page
script PDF (502,039 bytes), and PRJNA970614 run and BioSample metadata were
retrieved. Additional accession manifests are audited separately. Exact source
URLs, dates, sizes and SHA-256 digests are recorded in data/manifests.

- Initial experiment: the workbook contains 20 individual rows, 10 Control and
  10 Stress. IDs restart within group. Published VLP-enriched viromes consist
  of three pools per group at each of two sampling times, with 3-4 animals per
  pool. The reported animal counts vary between prose and captions. A pool
  membership crosswalk and processed pool abundance matrix were not retrieved.
- Transplant experiment: the workbook contains 30 individual rows, 10 ctr,
  10 ctr_stress and 10 fvt_stress. Assay-specific missingness reduces these
  counts. Rows are not equivalent to complete-case animals; for example,
  fvt_stress ID 11 has several early measurements but many later missing values.
- PRJNA970614: 104 deposited sequencing runs correspond to 104 sample records:
  8 aliases explicitly describing pools, 19 gavage/inoculum aliases and 77
  individual recipient aliases. These are distinct specimen categories, not
  104 independent animals. The archive includes heat-inactivated treatment
  samples absent from the source workbook.
- Individual recipient bulk metagenomes were used for viral-contig mapping in
  the original study. Published paired virome summaries therefore cannot be
  dismissed as universally pooled. The required processed abundance matrices,
  annotations and recal_metadata.csv/Proposed_mouse_ID mapping are not included
  in the inspected Zenodo releases. The PDF references local input paths.

## Linkage decision

Immune and behavioral columns in a workbook row are linked within that sheet
using experiment, group and literal source ID. Initial-study IDs must never be
joined across groups or experiments. The deposited recipient IDs include
ambiguous aliases such as Ctr191, Ctr19x2 and Ctr1x2, while source IDs include
1.1 and 19.2. Punctuation removal, row order and presumed renumbering are not
valid crosswalks. Some literal identifiers are compatible across sources, but
this does not provide an abundance profile or resolve excluded/recalibrated
samples. Zero observed processed virome profiles can presently be joined to
immune outcomes. This is an availability limitation, not proof that the
experiment lacked such measurements.

## Time and identifiability

The initial experiment has before/after stress pools. Recipient bulk sequences
have Before/After gavage-status annotations; A/B are corroborated by BioSample
attributes, not guessed. Pool membership across time is unresolved. Gavage
samples are donor material, never recipient intestinal profiles. Flow cytometry
around forced swim and terminal cytokines are not an immune baseline before
chronic stress. Temporal phageome stability is not calculable from the retrieved
inputs. A phage-stability versus immune-disruption association and bacterial
adjustment are consequently unidentifiable here.

## Selected analysis and exclusions

The feasible analysis combines a pooling-aware design and availability audit
with separate descriptive and exploratory immune contrasts. It is a restricted
Pathway C for pooled assays plus a missing-input gate for the individually
sequenced bulk data, not a claim that all viral observations were pooled.

Selected immune outcomes are LY6Chi monocyte proportion, CD62L-positive fraction
of those monocytes and unstimulated splenocyte TNF-alpha. These cover the paper's
circulating-cell and inflammatory outcomes without searching all cytokines.
Two contrasts per endpoint are Control Stress minus Control, and FVT Stress
minus Control Stress. Report raw-unit means, Welch intervals, two-sided Welch
tests and a single six-test Benjamini-Hochberg family. Missing values remain
missing. Retain all observed outcomes, describe the late incomplete animal,
and check leave-one-animal-out and rank-based sensitivity. Treat these as
unadjusted animal-level summaries; cage allocation and censoring thresholds are
unavailable and limit inferential calibration. Published treatment effects are
not novel phage findings.

Excluded: viral composition tests, diversity recomputation, Aitchison temporal
metrics, reference deviations, dispersion inference, viral taxa testing,
phage-immune models, bacteriome adjustment, phage-host claims and mediation.
No alpha diversity summary is used as evidence of stability. Missing analysis
stages must emit explicit exclusions rather than empty scientific outputs.

## Resources and alternative search

The measured host is Windows 11 with 16.79 GB installed RAM, about 0.38 GB
available at the recorded initial probe and 8.897 GB disk free. The operational
new-storage limit is 4.897 GB, leaving 4 GB free. Existing scientific Python
packages suffice; no installation, raw-read acquisition or database is selected.
The selected frozen inputs, tables and figures are expected to remain below
25 MB, with sequential execution and a 1 GB process-memory ceiling subject to
available system memory. Each download must have a hard size cap.

Deposited PRJNA970614 compressed FASTQ sizes total 262,211,457,238 bytes, before
assembly, databases or temporary products. Full raw reprocessing is excluded.
A focused alternative screen did not verify another stress dataset satisfying
the processed-data, immune-endpoint and explicit-linkage requirements; see
docs/alternative_dataset_search.md. This is not evidence that none exists.

Sources: [article](https://doi.org/10.1038/s41564-023-01564-y),
[frozen code release](https://zenodo.org/records/10460215),
[BioProject](https://www.ebi.ac.uk/ena/browser/view/PRJNA970614).
