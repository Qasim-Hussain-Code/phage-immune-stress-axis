# Data needed for an individual viral-immune analysis

The immediate priority is a release of processed recipient measurements and
their documented identities. Raw sequencing already exists in
[PRJNA970614](https://www.ebi.ac.uk/ena/browser/view/PRJNA970614). Frozen metadata
identify 20 condition-qualified Stress/FVT workbook labels, including 17
candidate before/after pairs, but do not resolve the final processed-sample
map. This checklist describes the additional records needed to evaluate the
questions in the [feasibility assessment](data_feasibility.md).

## Measurements and their processing

- Individual recipient viral count or coverage tables before and after FVT,
  with feature identifiers, sample columns, measurement units and normalization
  rules. Include pre-filter values where available, filtering decisions, zero
  replacement and the tables actually used for the published analyses.
- Viral contig sequences and annotations: catalog construction, contig length,
  completeness, viral-gene evidence, coverage thresholds, viral/phage
  classification and host predictions with their uncertainty. Identify the
  detectable fraction imposed by the inoculum-derived reference catalog.
- Matched bacterial abundance tables and feature definitions if bacterial
  adjustment is proposed. An individual recipient bacterial table is distinct
  from the pooled enriched virome and from the administered inoculum.
- Code, parameter settings, software/database versions and a data dictionary
  sufficient to distinguish raw counts, length-normalized counts, relative
  abundances and any absolute quantities. Inoculum Q33-derived quantities must
  not be assigned to recipient samples without a justified measurement model.

## Identities, times and biological units

Provide an explicit map from BioSample and run accession through the original
animal identifier to the source-workbook experiment, treatment and row.
Preserve the original labels alongside any corrected names. The map should
include the archived processing fields `Proposed_mouse_ID`, `Full_ID` and
`post_recal_name`, with the processed columns to which each refers.

Each record needs collection time, Before/After meaning, specimen role and
technical-repeat identity. List pool contributors and whether pool composition
was maintained across time. Identify inoculum preparation and recipient
separately. Literal label matches must be checked against these records;
Control decimal IDs must not be reconstructed by punctuation removal.

Allocation records should define cohort, cage membership and changes,
housing, aggressor assignment and other shared exposures. Distinguish these
from extraction, sequencing, assay and calibration plate batches. Numeric ID
blocks and decimal IDs do not establish those definitions themselves.

The immune map should retain endpoint-specific availability and collection
time: day-19 basal and post-forced-swim blood measurements differ from terminal
day-23 spleen cultures. A prestress immune measurement is needed for
within-animal immune change, but not necessarily for viral change associated
with a terminal immune phenotype. Different assays must not inherit each
other's exclusions or be declared paired merely because their sample counts
are equal.

## Calibration, exclusions and the hkFVT series

The archived [scripts](https://zenodo.org/records/10460215/files/Fvtstress_scripts_040124.pdf)
(pp. 15–16) reference `recal_metadata.csv`, `calib_batch`, plate-specific inputs
and recalibrated names. Supply those inputs, the calibration procedure and
its diagnostics. Document each omission with sample, assay, reason and stage:
technical failure, detection/censoring limit, statistical exclusion or other
decision. The community-processing filters for IDs 6, 7 and 11 and hkFVT need
their rationale and scope; they do not authorize removing other observed
immune values. Clarify whether absent endpoints are missing measurements or
biologically undefined parent-population quantities.

Clarify the 32 hkFVT-labelled deposited specimens: ten Before and ten After
recipient bulk specimens, ten inocula and two pools. State the treatment
definition, preparation, dose, inactivation method and validation, cohort
membership, allocation, measured phenotypes and inclusion in each analysis.
The [article](https://doi.org/10.1038/s41564-023-01564-y) describes a three-arm
FVT experiment and discusses fully inactivated FVT as future work; the
relationship between those descriptions and the deposited series is currently
unresolved.

A usable active-versus-inactivated comparison also needs evidence about
composition and dose after treatment and appropriate controls. Heating can
change constituents besides infectious phages; this comparison alone cannot
isolate phage infectivity or establish phage-specific causality.

An editable, versioned release with checksums, reuse terms and a clear
sample/feature dictionary would allow a new completeness and linkage review
before any viral-immune model is specified. Processed tables and validated
metadata would address the immediate gap more directly than another copy of
the already public raw reads.
