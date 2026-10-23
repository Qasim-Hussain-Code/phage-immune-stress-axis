# Methods

## Study and data

This reanalysis uses the published source data from
[Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y), which studied
psychosocial stress and fecal virome transplantation (FVT) in male C57BL/6J
mice. The research question concerns within-mouse viral change and its
relationship to immune phenotypes. The retrieved data support an assessment of
that question's data requirements and a separate exploratory analysis of three
immune outcomes.

The source collection comprises the article, supplementary phenotype workbook,
archived analysis scripts and sequencing metadata. Exact sources and checksums
are recorded in the [input manifest](../data/manifests/inputs.json). The workbook
contains 20 animal rows from the initial stress experiment and 30 from the
three-arm FVT experiment. The latter supplies the selected immune comparisons:
Control, Control Stress and FVT Stress, with ten source rows per group.
[Data feasibility](data_feasibility.md) describes the available viral samples
and missing processed community data. Raw sequencing reads were not reprocessed.

## Biological units and linkage

An immune observation is the original per-animal assay summary. The workbook
is read without modification; fully empty formatted rows are omitted. Exported
phenotypes retain missing cells and their worksheet, row, column and cell
coordinates. Animal keys combine experiment, treatment group and the literal
source identifier, because initial-experiment identifiers restart within group.
Technical replicates were averaged in the original study and are not available
for independent reaggregation.

Sequencing runs are inventoried by specimen, using exact run and BioSample
identities. Pool and inoculum annotations distinguish those specimens from
individual recipient samples. Before/After labels follow BioSample attributes.
The study includes pooled enriched viromes and individual recipient bulk
metagenomes mapped to a viral catalog. Neither treatment labels nor similar
sample counts establish a link between those profiles and workbook animals.
Cross-assay linkage requires a documented animal map; punctuation changes,
presumed renumbering and row position are not used to create one.

## Selected immune outcomes

Three endpoints were selected after reading the published findings and before
calculating the present contrasts. Their assay definitions follow Extended Data
Table 1b,c and the original collection methods.

| Endpoint | Biological material and collection | Unit |
|---|---|---|
| Basal LY6Chi monocyte proportion | Blood collected on study day 19, five minutes before forced swim, after 16 defeat days | Percent of parent population |
| Basal CD62L-positive fraction of LY6Chi monocytes | The same basal blood collection | Percent of parent population |
| Unstimulated splenocyte TNF-alpha | Terminal day-23 spleen collection, after 19 defeat days, followed by ex vivo culture | pg/mL |

Each defeat day included two bouts separated by two hours across a perforated
divider. The counts above refer to defeat days, not individual bouts.

The fixed blood cells were analysed the following day. Splenocyte methods
describe a 2.5-hour rest followed by 24-hour culture. Thus collection day and
assay readout are distinct, and the blood and spleen outcomes are collected
four study days apart. Basal refers to sampling before the acute forced-swim
test, after chronic stress exposure had already begun. Flow differences are
expressed in percentage points; culture TNF-alpha is distinct from circulating
plasma TNF-alpha.

Each primary endpoint comparison uses its available observations on the raw
scale. All supplied values are retained without added outlier removal, zero
substitution or imputation. The later log-TNF sensitivity is described below.
The original study reports detection-limit, technical and statistical
exclusions, but the workbook does not identify all omitted observations or
thresholds. No additional detection rule is inferred.

## Exploratory treatment contrasts

For each endpoint, the two contrasts are Control Stress minus Control and FVT
Stress minus Control Stress. The estimand is the difference in arithmetic means
in the source unit. Each estimate has a Welch standard error, Satterthwaite
degrees of freedom, two-sided t-test and pointwise 95% confidence interval.
Benjamini-Hochberg adjustment is applied once to the six mean tests. The
intervals are not simultaneous intervals, and this correction does not account
for endpoint selection informed by the published results.

These are unadjusted animal-level comparisons. Welch inference allows unequal
group variances and assumes independent animal observations. Unstressed
controls were group housed; both stressed groups were singly housed. The
stress-control contrast therefore includes a housing difference, whereas the
FVT-versus-stressed contrast compares groups with the same stated housing
regime. Verified cage and allocation details are unavailable. The later
conditional ID-stratum and putative-cage sensitivities described below do not
establish that missing design information. No high-dimensional model is fitted.

## Sensitivity and descriptive diagnostics

Mann-Whitney U comparisons describe distributional differences, using SciPy's
automatic exact or asymptotic calculation and a separate six-test BH family.
They address a different estimand from the raw-mean tests. Leave-one-animal-out
analysis refits each contrast after omitting each observed animal once and
records the full ranges of differences and P values. Those ranges describe
influence, rather than confidence limits. Precision is described by the Welch
intervals; post hoc observed power is not calculated.

Two further diagnostics were added after inspecting the earlier reanalysis,
without adding hypothesis tests. Conditional support bounds allow missing
percentage measurements to take any well-defined value in [0,100] and describe
the resulting extrema of source-row cohort mean differences. A finite upper
support is unavailable for TNF-alpha. Normalized U statistics describe empirical
ordering, counting ties as half a comparison. Cross-group pairs share animals
and do not increase the number of independent observations. The formulas,
denominators and assumptions appear in
[phenotype robustness](phenotype_robustness.md).

## Post hoc design and scale sensitivities

The literal study-II IDs divide each treatment into two strata of five source
animals: Control `1`–`3`/`19`–`21` with decimal suffixes retained, Control Stress
`4`–`8`/`22`–`26`, and FVT Stress `9`–`13`/`27`–`31`. This partition is observed;
its meaning as batch or allocation block is unverified. Integer prefixes also
suggest six possible control cages with sizes `2,2,1,2,2,1`, conditional on an
unverified ID interpretation. No cage or batch key is reconstructed as fact.

Added after the initial reanalysis, the sensitivity fits an additive
treatment-plus-ID-stratum model with HC3 covariance and residual-df t intervals.
A treatment-only HC3/t model provides a same-method comparator. Separate BH
families cover six adjusted treatment contrasts, 12 within-stratum raw Welch
contrasts and six conditional cage-unit contrasts. In the latter, control cage
means receive equal weight while singly housed stress animals remain individual
units, changing the weighting target and control-unit count. All six putative
control cages are omitted in turn as influence diagnostics; each omission
refits the original six animal-weighted tests and recomputes its six-test BH
adjustment. These are conditional refits, not source exclusions.

A separate natural-log TNF-alpha sensitivity verifies that every observed value
is positive, retains all observed assays, and reports geometric-mean ratios
with pointwise Welch intervals and its own two-test BH family. No pseudocount,
imputation or normality-test selection is used. The primary raw-scale contrasts
remain unchanged. The [design-sensitivity appendix](design_sensitivity.md)
defines the estimands, assumptions, findings and seven output tables.

## Reconstruction of the original selected analyses

A separate calculation applies the original three-group common-variance model
to the same observed FVT-experiment values. The pooled residual mean square and
degrees of freedom determine the planned contrast, with coefficients
`[-0.5, 1, -0.5]` in Control, Control Stress, FVT Stress order. All three
Tukey-Kramer pairwise comparisons are exported using finite-degrees-of-freedom
studentized-range probabilities and simultaneous 95% intervals within each
endpoint. Planned-contrast intervals are pointwise. The original across-outcome
BH family is not reconstructed.

This calculation examines how variance pooling and multiplicity affect the
selected published statistics; it remains separate from the six Welch tests.
The planned contrast compares the stressed mean with the average of the other
two means. Coefficient orthogonality alone does not imply independent contrast
estimates when sample sizes differ: under this model their covariance is
`MSE * sum(c_i*d_i/n_i)`. Full original SPSS syntax is unavailable.
[Original-analysis review](original_analysis_review.md) records the assumptions,
printed-statistic checks and unresolved group-mean discrepancy.

## Synthetic calibration

A separate software benchmark generates 20,000 all-null replicates in each of
five scenarios: independent equal-variance Gaussian outcomes, Gaussian
variances 4/1/1, centered lognormal outcomes, artificial all-group Gaussian
clusters, and hypothetical controls-only clusters. Both cluster scenarios use
intraclass correlation 0.5. Three independently generated endpoints use
group sizes 10/10/9. Each retains the same two overlapping contrasts, giving six
P values in one BH family. Recorded events include per-test false positives,
pointwise Welch coverage, all-null family rejection and three-pair Tukey
interval coverage. Wilson intervals describe Monte Carlo uncertainty.

The benchmark reads no biological outcomes or cage labels. The first four
models precede the added controls-only scenario, whose six control-cluster
sizes `2,2,1,2,2,1` follow the proposed ID interpretation while leaving both
stressed groups independent. The scenarios examine assumed dependence rather
than estimate the experiment's actual cage allocation or ICC. They use seed
20261020 and batches of 500; scenario streams are batch-invariant under the
recorded NumPy version. Raw simulated observations are not saved. Scenario
definitions and interpretation are in
[calibration design](calibration_design.md).

## Analysis stages and outputs

The ten sequential stages audit and acquire inputs, validate sample identities,
assess viral-data eligibility, extract immune phenotypes, calculate the
supported contrasts and diagnostics, validate computations, and draw figures.
The viral QC, stability and bacteriome stages record unavailable analyses,
as detailed in [data feasibility](data_feasibility.md). The stage named
`07_immune_associations` exports the separate immune contrasts and an explicit
phage-immune eligibility report; it fits no viral association.

Measured treatment groups provide the biological comparisons. The workbook
supplies no inactivated-FVT immune comparison, and available allocation records
do not support a verified cage-restricted permutation. CLR/Aitchison and Bray-Curtis
calculations, including ratio-preserving zero replacement, are checked on
synthetic fixtures only. Computational checks, acquisition safeguards, output verification and
reproduction evidence are documented separately in
[statistical validation](statistical_validation.md) and
[environment reproduction](environment_reproduction.md).
