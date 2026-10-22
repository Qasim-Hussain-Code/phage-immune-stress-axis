# Reconstruction of the original immune analyses

The monocyte FVT comparison gives a smaller P value in the Welch analysis than
in the publication. This appendix asks whether the original result can be
reconstructed from the same observations, and which features of the statistical
model explain the difference. The three-group pooled-variance Tukey-Kramer
calculation gives P = 0.10641, reproducing the published 0.106; the two-group
Welch calculation gives P = 0.012645. No supplied observation is removed to
reconcile them.

The reconstruction uses the same three selected study II endpoints as the
exploratory analysis. It is a comparison of methods on unchanged observations,
not an expansion of the endpoint family or a replacement for the six Welch
tests. All nine selected Figure 4 caption checks agree at published precision.
One printed group mean remains inconsistent with direct rounding of the source
values.

## Observations and group variation

The [source workbook](https://static-content.springer.com/esm/art%3A10.1038%2Fs41564-023-01564-y/MediaObjects/41564_2023_1564_MOESM2_ESM.xlsx)
is the frozen file recorded in the [input manifest](../data/manifests/inputs.json).
The calculation uses all observed selected values on its `FVT study II` sheet,
retaining literal animal identifiers and missing assays in the
[prepared records](../data/processed/immune_long.csv). Fully blank formatted
rows are not observations. The group summaries below show why a variance model
can materially affect these small-sample comparisons.

| Endpoint | Control: n; mean; sample variance | Control Stress: n; mean; sample variance | FVT Stress: n; mean; sample variance |
|---|---|---|---|
| Basal LY6Chi monocyte proportion | 10; 4.3844; 4.8800 | 10; 2.3503; 0.85614 | 9; 3.9068; 1.8884 |
| Basal CD62L-positive fraction of LY6Chi monocytes | 10; 61.397; 15.965 | 10; 59.637; 57.386 | 9; 75.511; 80.966 |
| Unstimulated splenocyte TNF-alpha | 9; 34.437; 130.25 | 8; 101.98; 12543 | 9; 27.849; 19.204 |

Flow means are percentages of the parent population, and their variances are
in squared percentage points. TNF-alpha means are pg/mL from unstimulated
splenocyte culture, with variances in `(pg/mL)^2`. Basal blood was collected on
day 19 before forced swim, after chronic stress exposure had begun; the spleen
was collected on day 23. These are endpoint phenotypes, not within-mouse immune
changes. The [methods](methods.md) describe collection and assay timing.

## Common-variance model and comparison families

For group sizes `n_g`, means `m_g` and unbiased sample variances `s_g^2`, the
three-group residual variance and degrees of freedom are

```text
df = N - 3
MSE = sum_g [(n_g - 1)*s_g^2] / df
```

The planned contrast uses coefficients `[-0.5, 1, -0.5]` in Control, Control
Stress, FVT Stress order. It compares the stressed mean with the average of the
other two means:

```text
L = m_stress - (m_control + m_FVT)/2
SE_L = sqrt[MSE * sum_g (c_g^2/n_g)]
t = L / SE_L
```

Its two-sided t probability and pointwise 95% interval use `N - 3` degrees of
freedom. A nonzero planned contrast does not require both component pairwise
differences to be nonzero or demonstrate that FVT reverses a stress deficit.

For each of the three pairs, Tukey-Kramer uses the same pooled MSE:

```text
range_scale = sqrt[(MSE/2)*(1/n_A + 1/n_B)]
q = abs(m_A - m_B) / range_scale
95% pair interval = (m_A - m_B) +/- q_(0.95;3,df)*range_scale
```

The studentized-range reference has three groups and finite residual degrees of
freedom. These intervals are simultaneous within one endpoint's three-pair
family, not across endpoints. All three pairs are exported to document that
family, including FVT minus Control, which is not an added primary contrast.

The Welch analysis instead estimates variance from the two groups in each
comparison, allows unequal group variances and reports pointwise intervals.
Its six P values have a separate BH adjustment across the three selected
endpoints and two contrasts. Tukey P values and Welch BH q values therefore
belong to different procedures and comparison families.

## Reconstructed results

| Endpoint | Pooled MSE | Residual df | Planned t | Unadjusted planned P |
|---|---:|---:|---:|---:|
| LY6Chi monocyte proportion | 2.5666 | 26 | -2.8669 | 0.0081095 |
| CD62L-positive fraction of LY6Chi monocytes | 50.303 | 26 | -3.1805 | 0.0037811 |
| Unstimulated splenocyte TNF-alpha | 3869.5 | 23 | 2.6799 | 0.013373 |

The FVT-versus-stressed comparison illustrates that identical mean differences
can have different uncertainty under the two methods:

| Endpoint | FVT minus Control Stress mean difference | Welch P | Tukey-Kramer P | Published Tukey P |
|---|---:|---:|---:|---:|
| LY6Chi monocyte proportion | 1.5565 percentage points | 0.012645 | 0.10641 | 0.106 |
| CD62L-positive fraction of LY6Chi monocytes | 15.874 percentage points | 0.00079989 | 0.00013585 | <0.001 |
| Unstimulated splenocyte TNF-alpha | -74.131 pg/mL | 0.10343 | 0.055687 | 0.056 |

For monocytes, the Tukey 95% interval is -0.27264 to 3.3856 percentage points,
whereas the pointwise Welch interval is 0.38926 to 2.7237. The pooled estimate
includes the higher-variance Control arm even when comparing only FVT Stress
with Control Stress, and Tukey accounts for all three pairs. Together these
choices explain the published-versus-Welch difference. The CD62L and TNF-alpha
results also show that variance pooling and multiplicity do not necessarily
move a P value in the same direction.

The exact [reconstruction table](../results/tables/original_method_replication.csv)
retains full-precision group summaries, omnibus ANOVA, planned contrast, all
three pairs, interval scopes and comparisons with printed references.

## Agreement with the publication

| Published quantities checked | Matches / checks |
|---|---:|
| Figure 4 planned t statistics and reported P thresholds | 3 / 3 |
| Figure 4 selected Tukey pairwise P values or inequalities | 6 / 6 |
| Group counts (Figure 4) and rounded means (Extended Data Table 1b,c) | 8 / 9 |
| Combined | 17 / 18 |

The nine caption-statistic checks all agree. The separate group-summary
mismatch is FVT Stress unstimulated TNF-alpha: its source mean is
**27.8492778 pg/mL**, which rounds directly to **27.8** at one decimal, while
Table 1b visibly prints **27.9**. Visual inspection confirms that this is not an
OCR ambiguity. Its origin is unresolved, and the rounding comparison is not
relaxed to count it as a match. The [generated verification report](../results/reports/original_method_replication.md)
records the caption and group-summary checks separately.

## Interpretation and limits

Numerical agreement establishes compatibility with selected calculations, not
the suitability of their assumptions. The TNF-alpha variance is particularly
large in Control Stress relative to both other groups. Reproducing its
pooled-variance statistic does not establish a credible common variance or
normal sampling distribution. Likewise, the CD62L planned contrast does not
establish restoration when the stress-control difference is small and
imprecisely estimated.

All animal-level inference also assumes appropriate independence. Controls were
group housed and both stressed groups singly housed, so the stress-control
contrast includes a housing difference; the FVT contrast shares the stated
housing regime. Missing cage and allocation records prevent a justified
cage-adjusted model or permutation scheme. These constraints remain after an
original P value is reproduced.

The original methods describe technical, detection-limit and statistical
exclusions, including a rule beyond 2.5 standard deviations with at most two
statistical exclusions per test. The deposited workbook lacks a complete
observation-level exclusion log and censoring thresholds. No further deletions
are needed to reproduce the selected statistics, but that does not establish
that upstream exclusions never occurred.

The [article](https://www.nature.com/articles/s41564-023-01564-y) names SPSS v.28
for these analyses; its complete syntax is unavailable. This is a reconstruction
of compatible calculations, not a rerun of the SPSS session. The paper's
description of orthogonal contrasts does not establish independence under
unequal sample sizes: the estimated covariance of contrasts `c` and `d` is
`MSE * sum_g(c_g*d_g/n_g)`, so an unweighted coefficient dot product of zero is
insufficient. The complete contrast set cannot be verified from the label.

The publication's full across-outcome BH family is also unresolved. Its printed
q values are retained as references in the CSV, not reproduced values. Applying
BH to these three planned contrasts would define a new family. This
reconstruction remains separate from the unchanged six-test exploratory Welch
analysis and supplies no viral association.

The implementation is [original_methods.py](../src/pisa/original_methods.py).
Existing [calculation checks](../tests/test_original_methods.py) compare pooled
calculations with statsmodels OLS and linear contrasts, and finite-df
Tukey-Kramer calculations with `pairwise_tukeyhsd` on unequal-size fixtures.
