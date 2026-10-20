# Methods

## Design and source selection

The original study is Ritz et al. (2024), DOI
[10.1038/s41564-023-01564-y](https://doi.org/10.1038/s41564-023-01564-y).
The reference repository was inspected first. The article, supplementary
source workbook, Zenodo code release and three sequencing accession manifests
were audited. Small frozen inputs are accompanied by URLs and SHA-256 digests.
No raw sequencing reads, assemblies or viral reference databases were acquired.
The alternative dataset screen retained the psychosocial-stress question.
The expanded search records 52 saved evidence responses or representations,
including the complete supplementary package and scoped archive/repository
queries. It recovered no missing community matrix or verified crosswalk. The
prenatal-stress candidate remains unresolved rather than classified from its
abstract as an analysis-ready substitute. These are bounded retrieval findings;
see [processed_data_search.md](processed_data_search.md) and
[new_prenatal_stress_candidate.md](new_prenatal_stress_candidate.md).

The [feasibility gate](../results/reports/data_feasibility.md) excluded viral
community and association analyses because the processed matrices and animal
crosswalk were missing from the inspected releases. The original individual
bulk-derived viral profiles are distinguished from pooled enriched viromes.
Public raw specimens cannot substitute for measured abundance features.

## Sample independence and matching

Run and BioSample identities must agree exactly. Multiple runs for one specimen
would be combined only in the inventory, not counted as animals. Explicit pool
and gavage annotations define specimen roles. No pool has an individual mouse
ID; no inoculum becomes a recipient community. Before/After comes from
BioSample annotations. Workbook animal keys include experiment, group and
literal source identifier. Decimal punctuation remains unchanged. No
cross-assay match relies on row order, inferred punctuation or renumbering.
Other accession manifests are inventoried without assigning animals.

## Immune source data

The unchanged workbook is parsed read-only with openpyxl. Fully empty formatted
rows are omitted. Every source phenotype, including missing cells, is exported
with sheet, row, column and source-cell coordinates. Initial and FVT experiments
contain 20 and 30 nonempty source rows, respectively. Any-assay availability does
not imply complete cases. Selected endpoints are fixed before the present
contrast calculations, after the published findings were known.

Selected outcomes are basal LY6Chi monocyte proportion, basal CD62L-positive
fraction of that population and unstimulated splenocyte TNF-alpha. Extended
Data Table 1c confirms the flow measurements are percentages of parent
population, before forced swim after chronic stress. Effects are percentage
points. Table 1b confirms the culture cytokine unit pg/mL. These are relative
cell proportions and 24-hour culture output, not absolute blood cell counts or
circulating TNF-alpha. No assay detection threshold is invented. The original
study reports exclusions below detection and statistical/technical exclusions;
the available workbook does not identify all such decisions.

All observed endpoint values are retained. No zero substitution, outlier
deletion, transformation, technical-replicate expansion or missing-value
imputation is performed. Original per-individual assay summaries are used;
technical replicates are not available for independent reaggregation.

## Exploratory statistical analysis

Two contrasts are calculated per endpoint: stressed control minus unstressed
control, and FVT stress minus stressed control. Each mean difference uses
the Welch standard error, Satterthwaite degrees of freedom, two-sided t-test and
pointwise 95% interval. A single six-test Benjamini-Hochberg correction is used.
The nominal intervals are not simultaneous multiple-comparison intervals.
Unknown cage allocation and stress-associated housing differences prevent a
strong claim that individual-animal standard errors capture all dependence.
No adjusted or high-dimensional model is fitted.

Mann-Whitney U is a distributional sensitivity check, using SciPy auto exact or
asymptotic handling, with a separate six-test sensitivity BH family. It does
not test the same raw-mean estimand. Leave-one-out analysis removes each
observed animal once and records the full range of refitted differences and
P values. No favorable refit is substituted for the full estimate. Nonsignificant
tests are not interpreted as equivalence. A posterior observed-power estimate
would merely restate the P value and was not used; small-sample precision is
shown through intervals and influence diagnostics instead.

## Separate original-method reconstruction

The same observed study II values are additionally summarized under the
original three-group common-variance model. The pooled residual sum of squares
and degrees of freedom determine the planned contrast with coefficients
`[-0.5, 1, -0.5]` in Ctr, Ctr Stress, FVT Stress order. All three Tukey-Kramer
pairs are exported, with finite-df studentized-range probabilities and
simultaneous 95% intervals within each endpoint. Planned-contrast intervals are
pointwise. The original across-outcome BH family is not reconstructed.

This layer reproduces all nine selected caption statistics at reported
precision, including monocyte FVT Tukey P=0.106409 versus the present Welch
P=0.012645. Pooled variance and Tukey multiplicity explain that difference from
the same observations; extra exclusions are unnecessary. It does not replace
the fixed six Welch tests or select a preferred significant result.

Eight of nine group-summary checks match the published table. FVT unstimulated
TNF-alpha has source mean 27.8492778 pg/mL, directly rounding to 27.8, versus
the visibly printed 27.9. That discrepancy is retained. The combined check
count is 17 matches out of 18, not complete agreement of all table cells.

The paper's label of orthogonal contrasts does not establish independence of
all contrast estimates with unequal group sizes. Under the common-variance
model, covariance of contrasts c and d is `MSE * sum(c_i*d_i/n_i)`; unweighted
coefficient orthogonality is insufficient. Complete original SPSS syntax is
unavailable. See [original_analysis_review.md](original_analysis_review.md).

## Synthetic software calibration

The expanded full pipeline ran a separate 20,000-replicate
all-null benchmark in each of four fixed scenarios: independent equal-variance
Gaussian, Gaussian variances 4/1/1, centered lognormal and artificial Gaussian
clusters with ICC 0.5. Three independently generated endpoints use group sizes
10/10/9 and jointly retain the two overlapping adjacent contrasts per endpoint.
The six P values enter one BH family. Reported events are per-test false
positives, pointwise Welch coverage, all-null family rejection and three-pair
Tukey interval coverage. Wilson intervals quantify Monte Carlo error only.

No actual outcome or cage label is read by that module. Its all-group cluster
assignment is a generic assumption stress test; it does not describe the
original singly housed stressed groups or estimate their ICC. Default batches
are bounded at 500, seeded scenario streams are batch-invariant under the
recorded NumPy version, and raw simulated observations are not saved. The full
benchmark completed with seed 20261020 in all four scenarios; its labeled
table and report record that execution separately from quick unit fixtures. See
[calibration_design.md](calibration_design.md).

## Excluded community inference and controls

No viral composition, temporal distance, reference centroid, dispersion,
taxon-level phage test, bacterial adjustment or host prediction was calculated.
Validated CLR/Aitchison and Bray-Curtis routines are exercised on explicitly
synthetic software fixtures only. Zero replacement is explicit and preserves
positive-component ratios; those tests do not validate a biological normalization
choice for an unavailable matrix. No synthetic value enters a biological table.

Measured unstressed and stressed treatment groups are the available biological
comparators. No independent phage-specific positive control or exchangeable
permutation design was identifiable, so none is fabricated. Unknown cage
allocation precludes a defensible cage-restricted permutation. Analytical
identities and independently implemented library checks provide computational
controls rather than biological discoveries.

## Execution and outputs

Ten numbered stages run sequentially. Excluded stages generate explicit
availability/eligibility reports, never fabricated scientific estimates.
Pilot, full, offline, resume and validation-only modes are implemented.
Fingerprinting covers configuration, code, test code and frozen inputs;
resumption also checks declared output hashes. Streaming fetches reject
over-cap content and changed hashes, with partial files removed. Native child
RSS, concurrent descendant RSS, available memory and disk usage are monitored
during execution. Storage uses a host/checkout-bound persistent local baseline;
historical environment records do not set another invocation's allowance.
Resumed results are distinguished from newly measured stage peaks. The
supported five-figure set uses actual source rows, availability inventories or
the original-method reconstruction. It does not plot synthetic calibration as
biology. PNG/PDF files and their visual review are verified separately;
machine-readable tables retain underlying observations and estimators. A prior
review establishes current QA only when the recorded file hashes still match.
