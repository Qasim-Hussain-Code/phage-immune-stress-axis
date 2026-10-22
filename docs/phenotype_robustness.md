# Missing assays and distributional robustness

The immune comparisons raise two questions that mean estimates and their
confidence intervals do not answer alone: could the missing assays reverse a
source-cohort mean difference, and how consistently are observed values ordered
between groups? This appendix examines those questions for the same three
selected endpoints and two contrasts used in the [main results](results.md).
These diagnostics were added after inspecting the earlier reanalysis and remain
post hoc. They add no hypothesis tests, P values or confidence intervals.

The flow outcomes come from basal blood collected on day 19, before forced swim
but after 16 defeat days. Unstimulated splenocyte TNF-alpha comes from the
terminal day-23 spleen collection after 19 defeat days, followed by ex vivo culture.
Neither is an immune measurement before chronic stress began. The diagnostics
describe endpoint phenotypes, not within-mouse immune change.

## Missing assays and the source-cohort mean

The FVT workbook represents ten animals in each of Control, Control Stress and
FVT Stress. A missing assay still belongs to a represented animal. In particular,
FVT source animal `31` lacks both selected flow measurements but has an observed
TNF-alpha value; the missing FVT TNF-alpha assay belongs to animal `11`.
These ten-row denominators do not establish that every originally randomized
animal was deposited or recover exclusions made before deposition.

The bounds target the mean difference across all represented animals in each
group. This differs from the primary Welch comparison of observed assays. Let
`N_A` be the number of source-row animals in group A, `m_A` the number with a
missing assay, and `S_A` the sum of observed values; define the corresponding
quantities for group B. If every missing assay has a well-defined value in a
common finite support `[L,U]`, then the possible source-cohort mean differences
are bounded by

```text
lower = (S_A + m_A*L)/N_A - (S_B + m_B*U)/N_B
upper = (S_A + m_A*U)/N_A - (S_B + m_B*L)/N_B
```

The bounds are sharp under this assumption: placing missing A and B values at
opposite support endpoints attains each extreme. No endpoint is adopted as an
imputed observation. With complete assays, both bounds reduce to the observed
source-cohort mean difference.

Both flow outcomes are percentages of a parent population, giving support
`[0,100]` and differences in percentage points. This requires each missing assay
to have a well-defined percentage at the intended collection time. If its
parent population does not exist or cannot be measured, zero is not an automatic
substitute. No additional relation between the two missing flow values is
assumed.

| Flow endpoint | Contrast: first minus second | Missing assays, first / second | Possible mean difference, percentage points |
|---|---|---:|---:|
| LY6Chi monocyte proportion | Control Stress minus Control | 0 / 0 | -2.034038 |
| LY6Chi monocyte proportion | FVT Stress minus Control Stress | 1 / 0 | 1.165810 to 11.165810 |
| CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | 0 / 0 | -1.760441 |
| CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 1 / 0 | 8.322593 to 18.322593 |

Each row uses ten source animals per group. Under the stated support, the
missing FVT assay cannot reverse the positive source-cohort mean difference for
either flow endpoint. These are descriptive extrema, not confidence limits or
evidence that a P value, population effect or causal conclusion is insensitive
to missingness. A positive FVT contrast also does not establish restoration of
a stress-induced deficit.

TNF-alpha has missing assays in all three groups: one in Control, two in Control
Stress and one in FVT Stress. A nonnegative concentration scale alone gives no
finite upper support; assay-specific thresholds and missingness causes are
unavailable. Consequently neither TNF-alpha contrast has finite two-sided
bounds. No detection limit, zero substitution or missing-at-random assumption
is supplied. The complete six-row table is
[immune_missingness_bounds.csv](../results/tables/immune_missingness_bounds.csv).

## Ordering among observed animals

For groups A and B with `n_A` and `n_B` observed animals, let `W` count cross-group
pairs with a larger A value and `T` count ties. The empirical superiority measure
and rank-biserial effect are

```text
p_order = (W + T/2) / (n_A*n_B)
rank_biserial = 2*p_order - 1
```

Thus `p_order = 0.5` indicates equal numbers of greater and lesser comparisons
after giving ties half credit. Positive rank-biserial values indicate larger A
values. These measures describe empirical ordering rather than an arithmetic
mean difference; when distribution shapes differ, they do not automatically
describe a common median shift.

| Endpoint | Contrast: first minus second | Observed animals, first / second | Empirical superiority | Rank-biserial effect |
|---|---|---:|---:|---:|
| LY6Chi monocyte proportion | Control Stress minus Control | 10 / 10 | 0.110000 | -0.780000 |
| LY6Chi monocyte proportion | FVT Stress minus Control Stress | 9 / 10 | 0.866667 | 0.733333 |
| CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | 10 / 10 | 0.360000 | -0.280000 |
| CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 9 / 10 | 0.911111 | 0.822222 |
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 8 / 9 | 0.666667 | 0.333333 |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | 9 / 8 | 0.111111 | -0.777778 |

There are no ties in these comparisons. For TNF-alpha, the FVT value is lower in
64 of 72 cross-group pairs, despite the wide raw-mean interval reported in the
main analysis. The two summaries address different features of the observed
distribution. Those 72 comparisons reuse 17 animals; they are not 72 independent
replicates, and no interval or standard error is calculated by treating them as
such. The rank summaries also condition on observed assays and do not resolve
the missing TNF-alpha measurements.

The [rank-effect table](../results/tables/immune_rank_effects.csv) records wins,
ties, losses and animal counts. Average pooled ranks give
`U_A = rank_sum_A - n_A*(n_A+1)/2`, independently checked against `W + T/2` and
the U statistic in the existing sensitivity analysis. Reversing group order
complements superiority and changes the sign of the rank-biserial effect.

## Interpretation and implementation

These diagnostics complement leave-one-animal-out analysis, which examines
influence by removing observed animals. They do not establish independent
sampling. Controls were group housed and both stressed groups singly housed;
the stress-control contrast includes that housing difference, while the FVT
contrast shares the stated regime. Cage allocation, upstream exclusions and
censoring remain unresolved. Neither diagnostic supplies the missing viral
profiles and animal crosswalk needed for a phage-immune association.

The calculations are implemented in
[phenotype_robustness.py](../src/pisa/phenotype_robustness.py), using the
[prepared source records](../data/processed/immune_long.csv). Existing checks
enumerate missing-value corners, verify rank identities including ties and
reversal, and reject incomplete source records or values outside the assumed
support. The [generated report](../results/reports/phenotype_robustness.md)
contains all six comparisons for both diagnostics.
