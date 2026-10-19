# Methods

## Design and source selection

The original study is Ritz et al. (2024), DOI
[10.1038/s41564-023-01564-y](https://doi.org/10.1038/s41564-023-01564-y).
The reference repository was inspected first. The article, supplementary
source workbook, Zenodo code release and three sequencing accession manifests
were audited. Small frozen inputs are accompanied by URLs and SHA-256 digests.
No raw sequencing reads, assemblies or viral reference databases were acquired.
The alternative dataset screen retained the psychosocial-stress question.

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
RSS and disk usage are monitored during execution. All reported figures are
derived from actual source rows or the availability inventory. Both PNG and
vector PDF outputs are inspected for layout; machine-readable figure tables
retain underlying observations and estimators.
