# Limitations

## What the available data can answer

The retrieved phenotype workbook supports exploratory treatment comparisons.
Public raw reads and literal condition-qualified labels identify 20 candidate
Stress/FVT source keys, including 17 before/after specimen pairs. Processed
viral abundance matrices and a validated analytic animal map were not recovered.
An individual viral-immune analysis therefore needs both a reconstruction or
release of the measurements and resolution of their linkage, calibration and
exclusions. The original paper
describes paired individual bulk-metagenome-derived viral profiles alongside
pooled enriched viromes. Their absence from the inspected releases is a data
availability finding, not evidence that the measurements never existed or that
viral change is unrelated to immunity. The
[data feasibility assessment](data_feasibility.md) distinguishes these sample
types and the analyses each could support.

Repeated individual viromes linked to an immune endpoint could support an
analysis of viral change versus endpoint immune phenotype. Such an analysis
does not require a prestress immune measurement. A claim about within-mouse
immune change or immune stability across chronic stress would additionally
require repeated immune measurements. The selected basal blood and terminal
spleen assays provide different outcomes, collected four study days apart;
neither is a prechronic-stress immune baseline.

## Missing observations and measurement scope

The FVT workbook contains ten source rows per treatment. Available monocyte and
CD62L observations number 10, 10 and nine in Control, Control Stress and FVT
Stress; TNF-alpha observations number nine, eight and nine. The two n=9 FVT
sets contain different animals: source ID 31 lacks the selected flow outcomes,
whereas ID 11 lacks TNF-alpha. Equal counts therefore do not establish complete
paired endpoints. Availability may depend on the outcome.

The publication excluded measurements outside detection limits, technical
failures and statistical outliers beyond 2.5 standard deviations. The workbook
does not identify every excluded observation, censoring threshold or omitted
value. Retaining every supplied observation avoids additional exclusions but
cannot recover those removed upstream. These records do not support a reliable
missingness model.

The percentage support bounds apply only to animals represented by workbook
rows, conditional on a missing assay having a well-defined value in [0,100].
An undefined parent-cell population would violate that assumption. The bounds
do not cover omitted animals or sampling uncertainty. TNF-alpha has no justified
finite upper support. Empirical rank effects reuse animals across pairs; those
pairs are not independent replicates.

Flow proportions describe fractions of parent-cell populations, so a change in
percentage does not establish a change in absolute cell number or trafficking.
Unstimulated splenocyte TNF-alpha measures ex vivo culture output rather than
circulating cytokine concentration. Eight of nine selected workbook means
round to the published table cells. FVT unstimulated TNF-alpha averages
27.8492778 pg/mL, rounding directly to 27.8, whereas Extended Data Table 1b
prints 27.9. This small discrepancy remains unresolved.

## Design and statistical interpretation

Animal-level Welch inference assumes independent observations. Unstressed
controls were group housed, while both stressed groups were singly housed.
The stress-control comparison includes that housing difference. FVT Stress
versus Control Stress shares the stated housing regime, but missing cage,
allocation and shared-exposure information still prevents an assessment or
adjustment of all dependence. Numeric ID blocks and decimal identifiers can
motivate requests for allocation records; they are not verified batch or cage
definitions. Calibration plates in the archived community-processing scripts
are also not evidence of shared housing or independent biological cohorts.

The three endpoints were chosen with knowledge of the published findings.
This is an exploratory reanalysis. BH adjustment is confined to the six
reported mean tests; it does not remove the effect of that selection.
Intervals are pointwise. Small groups and incomplete assays
limit precision, and nonsignificant results do not establish equivalence.

The original common-variance model and the present Welch comparisons have
different variance and multiplicity assumptions. Reconstructing the selected
original calculations explains the monocyte FVT Tukey P=0.106409 versus Welch
P=0.012645 from the same observations; additional exclusions are unnecessary
to explain this difference. All nine selected caption-statistic checks agree,
but the original complete across-outcome BH family remains unreconstructed.

Interpretation also depends on the contrast and estimand. The higher
CD62L-positive fraction under FVT does not establish reversal of a stress
deficit, because the stress-control estimate is imprecise. TNF-alpha is highly
dispersed in stressed controls, and its Welch and rank comparisons differ.
The rank test is a distributional comparison and need not describe a mean or
median shift when group shapes differ. The [results](results.md) retain both.
Preserved effect directions under single-animal omission describe influence;
they do not establish stable significance or resolve confounding.

## Biological interpretation and transfer

Treatment-associated immune differences do not isolate a virome-specific
mechanism. The published three-arm FVT experiment has no unstressed FVT arm,
and the available measurements do not separate every treatment-associated
constituent or provide a fully factorial intervention analysis. They cannot establish direct phage
immune regulation or a gut-brain mechanism. Any future computational viral
classification or bacterial-host assignment would also require its uncertainty
to be retained.

The metagenomic deposit additionally includes 20 hkFVT-labelled recipient bulk
specimens (ten Before and ten After), ten hkFVT inocula and two pools. Their
cohort, treatment protocol and immune outcomes are unresolved; there are no
hkFVT phenotype rows in the source workbook. The article describes three FVT
groups and discusses fully inactivated FVT as future work. These records
require clarification before defining an additional comparison. Even a verified
active-versus-heat-inactivated comparison would test a preparation difference:
heat can alter multiple constituents. Phage-specific interpretation would
require matched dose and composition, validated loss of infectivity and
appropriate controls. The [data requirements](data_requirements.md) specify
the records needed to assess that route.

The cohorts comprise male C57BL/6J mice under specific stress and housing
conditions. Transfer to females, other strains or human stress responses is
unestablished. The public-data search is bounded by the sources and dates
recorded in its ledgers; the newer Chen prenatal-stress candidate remains
unresolved. Access failures do not establish scientific ineligibility or the
absence of a public deposit.

## Scope of computational validation

Reproduction and software tests check source identity, calculations and output
agreement. They cannot supply missing measurements, cage assignments or
biological controls. The separate calibration examines known simulated models
without reading biological observations. Its
artificial clustering does not identify the original cage structure, and its
Wilson intervals quantify Monte Carlo error rather than mouse-level
uncertainty. These checks support the implemented computations under stated
conditions, not calibration of the experiment under unknown dependence.
