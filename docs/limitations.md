# Limitations

## The primary ecological question was not tested

No processed viral abundance profile was retrieved. Zero such profiles were
matched to immune outcomes. Viral composition, within-mouse phageome stability,
reference-state deviation, dispersion, bacterial-adjusted viral associations and
phage-host relationships were not estimated. Missing evidence is not a null
association result.

The paper describes individual pre/post bulk metagenomes mapped to an
inoculum-derived viral catalog, alongside pooled enriched viromes. Additional
analysis may become possible if the abundance matrix, viral annotations and
verified animal map are released. The present availability gap does not prove
that all original measurements were pooled or that individual data never
existed. See [data_feasibility.md](data_feasibility.md) and
[paper_audit_notes.md](paper_audit_notes.md).

## Pools and inocula limit linkage

Initial enriched viromes combine three or four animals per pool. Twelve
published pool-by-time profiles are reconstructed from two groups, two sampling
times and three pools; pool membership across time is unresolved. They are not
twelve verified longitudinal animal trajectories. The deposited metagenomic
archive contains 104 specimens, comprising 77 recipient bulk samples, eight
pool-labeled samples and 19 inocula. Deposited and published counts describe
different sample categories and are not interchangeable.

A donor inoculum describes administered material, not the recipient's intestinal
community. Pool measurements cannot be distributed among individual immune rows.
Literal identifiers also differ across resources. Punctuation removal, presumed
renumbering and row position do not establish identity. The initial-study mouse
IDs restart within group and must remain scoped by experiment and treatment.

## Immune outcomes are endpoint phenotypes

The selected LY6Chi monocyte and CD62L-positive measurements are basal blood
proportions from blood collected on study day 19, before the acute forced-swim
test and after 16 defeat days. Both flow outcomes are percentages of parent
populations. Contrasts are percentage
points, not absolute cell counts or relative percentage changes. Basal here is
not a prechronic-stress baseline. Changes in proportions need not demonstrate
changes in absolute circulating cell numbers or cell trafficking.

TNF-alpha is measured in unstimulated splenocyte culture supernatant, in pg/mL,
from terminal day-23 spleen collection after 19 defeat sessions. Source-row
linkage does not make the blood and spleen assays contemporaneous.
It is distinct from plasma TNF-alpha and does not measure a within-mouse change
across chronic stress. These unit and timing assignments follow Extended Data
Table 1b,c of the [original article](https://doi.org/10.1038/s41564-023-01564-y),
whose selected units and timing were checked against the actual table image.
Eight of nine selected means round to the printed values. FVT unstimulated
TNF-alpha averages 27.8492778 pg/mL, directly rounding to 27.8, whereas Table 1b
prints 27.9. The small discrepancy is explicit and unresolved; no tolerance or
source value was changed to conceal it.

## Sample size, missingness and upstream exclusions

The FVT workbook lists ten animals per treatment. The selected monocyte
endpoints have 10, 10 and nine observations in Control, Control Stress and FVT
Stress; TNF-alpha has nine, eight and nine. Endpoint-specific available-case
analysis preserves all supplied observations and does not impute missing values.
Mouse 11 has incomplete later measurements, and mouse 31 lacks selected
monocyte measurements. Availability cannot be assumed independent of outcome.

Conditional [0,100] support bounds describe how missing percentages can change
the source-row cohort mean differences. They do not address population sampling
uncertainty, undefined parent-cell populations, upstream omitted animals or
statistical significance. Missing TNF-alpha has no justified finite upper bound.
The added rank effects are descriptive; cross-group pairs share animals and
cannot be treated as additional independent observations.

The publication excluded measurements outside detection limits, technical
failures and statistical outliers beyond 2.5 standard deviations. The retrieved
workbook does not identify every exclusion, censoring threshold or omitted
value. Keeping every observed source value does not reconstruct observations
removed upstream. Missingness cannot be reliably modeled from these inputs.
Small groups and variable completeness yield wide intervals; nonsignificant
tests do not establish equivalence or absence of a meaningful effect.

## Inferential calibration is limited by design information

Welch inference accommodates unequal sample variances but assumes independent
animal observations. Cage allocation and possible cage-level dependence are
unavailable. Unstressed controls were group housed and both stressed groups
singly housed. Housing therefore differs for stress-control comparisons, while
FVT-versus-stressed comparisons share the stated regime. No cage-adjusted standard errors or
housing-independent stress effect can be recovered from the available table.

Three endpoints and two contrasts were selected after reading the published
results and before computing the present statistics. This is an exploratory
reanalysis, not a preregistered confirmation. The BH correction concerns the six
reported mean tests; it does not remove selection informed by prior results.
The 95% intervals are pointwise and are not simultaneous confidence bands.

## Restoration and method dependence

The FVT versus stressed-control monocyte Welch P = 0.01265 differs from the
published Tukey pairwise P = 0.106. Welch pairwise tests and the original
three-group analysis have different variance and multiplicity assumptions.
A separate reconstruction from the same supplied observations gives
Tukey-Kramer P = 0.106409 and matches all nine selected caption-statistic
checks. Thus variance pooling and multiplicity explain this difference without
additional exclusions. Upstream exclusions remain a general availability
limitation, not a necessary explanation for this numerical comparison. The
reconstruction does not identify an error in the original test or reproduce its
complete across-outcome BH family.

The CD62L-positive FVT contrast is 15.87 percentage points, but the preceding
stress contrast is -1.76 points with a 95% interval of -7.58 to 4.06. These data
do not establish a stress-induced deficit that was subsequently reversed.

Stressed-control TNF-alpha values have a mean of 101.98 pg/mL, median of 40.48
pg/mL and standard deviation of 112.00 pg/mL. The FVT mean contrast is -74.13
pg/mL, with a 95% interval of -167.78 to 19.51 and q = 0.1551. Its rank
sensitivity q = 0.01102 describes a different distributional comparison. With
unequal distribution shapes, the rank test must not be labeled a test of equal
means or interpreted automatically as a median shift. Both results are retained.

Leave-one-animal-out effect directions persist in all six contrasts. This does
not establish stable statistical significance, remove treatment confounding or
compensate for shared housing. Omission ranges are diagnostic ranges, not
confidence intervals, and repeated omissions do not create new observations.

## Biological and external validity

Treatment-associated immune differences alone do not identify a virome-specific
causal effect, direct phage immune regulation or a gut-brain mechanism. The
selected FVT design lacks an unstressed FVT arm. The immune table does not
provide a fully factorial intervention analysis or measurements that isolate
viral constituents from every treatment-associated component.

The original cohorts involve male C57BL/6J mice in particular stress and housing
conditions. Generalization to females, other mouse strains or human stress
responses is not established. Computational viral and host predictions, if
subsequently acquired, would remain predictions unless independently validated.

## Validation cannot supply missing measurements

The software suite verifies calculations, source identity rules and acquisition
safeguards; the current executed outcome is recorded in
`results/reports/validation_summary.json`. It does not validate biological independence,
recover excluded observations, establish statistical power or demonstrate null
calibration under an unknown cage structure. No biological viral stability
estimate is validated by testing a distance function on synthetic fixtures.

The separate synthetic calibration benchmark uses known generating assumptions
and no biological measurements. Its artificial clustered scenario cannot
identify the actual cage structure, particularly for the original singly
housed stressed groups. Good or poor simulated calibration is conditional on
the chosen model. Wilson bounds describe Monte Carlo error, not biological
uncertainty. The completed benchmark used 20,000 replicates per scenario;
its results remain conditional software observations, not calibration of the
actual experiment's unknown dependence.

The expanded public search's 52 evidence records bound what was checked, not
all possible public or private locations. A newer prenatal-stress candidate
remains unresolved. Access failures and request-based availability statements
cannot establish that a study is biologically ineligible or that no public
deposit exists.
