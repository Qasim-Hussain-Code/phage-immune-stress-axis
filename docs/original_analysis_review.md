# Independent review of the original immune analysis

Review date: 2026-10-20. This review uses the same three fixed study II endpoints
as the exploratory immune analysis. It adds no endpoints, excludes no supplied
observations and does not replace the existing six-test Welch family.

## Main finding

The published monocyte FVT pairwise P = 0.106 is reproduced as 0.1064091013 by
a three-group pooled-variance Tukey-Kramer calculation. The existing pairwise
Welch P = 0.0126452597 answers a comparison with a different variance estimator
and multiplicity procedure. The apparent discrepancy is numerically explained
without changing any source observations or invoking additional exclusions.

For all three selected endpoints, the reconstructed planned-contrast t statistic
and each published numeric Tukey pairwise P value match the caption at its
reported precision. This is evidence of internal consistency between the public
workbook and those original statistics. It does not validate common variance,
normality or animal independence.

## Evidence and scope

The original [Figure 4 caption and statistical methods](https://www.nature.com/articles/s41564-023-01564-y)
describe a planned contrast, BH correction and Tukey pairwise comparisons.
The frozen article is `data/raw/article.xml`; the caption is also independently
available in the publisher's indexed text. The methods name SPSS v.28 for
non-sequencing analyses. The inspected code archive does not supply SPSS syntax.
Consequently, this is a numerical reconstruction of compatible calculations,
not a re-execution of the original software session. One printed group-mean
discrepancy is retained separately from the matching caption statistics.

The public [supplementary source workbook](https://static-content.springer-cdn.com/esm/art%3A10.1038%2Fs41564-023-01564-y/MediaObjects/41564_2023_1564_MOESM2_ESM.xlsx)
was read without modification. Values were taken from its `FVT study II` sheet
through `data/processed/immune_long.csv`, retaining all observed values and
literal scoped animal IDs. Fully blank formatted rows are not observations.

The [publisher PDF](https://www.nature.com/articles/s41564-023-01564-y.pdf),
Extended Data Table 1b,c, identifies the selected cell outcomes as basal
percentages of parent population and TNF-alpha as pg/mL from vehicle or
unstimulated splenocyte culture. The basal cell sample precedes the acute
forced-swim test, not the chronic stress exposure. Eight of the nine selected
source means agree with the published rounded means:

| Endpoint | Ctr n, mean, sample variance | Ctr Stress n, mean, sample variance | FVT Stress n, mean, sample variance | Published means |
|---|---|---|---|---|
| Basal LY6Chi monocytes | 10; 4.3843577; 4.88002709 | 10; 2.3503197; 0.85614234 | 9; 3.90681056; 1.88836045 | 4.38; 2.35; 3.91 |
| Basal CD62L-positive LY6Chi monocytes | 10; 61.397405; 15.96487748 | 10; 59.636964; 57.38627982 | 9; 75.51061889; 80.96588273 | 61.4; 59.6; 75.5 |
| Unstimulated splenocyte TNF-alpha | 9; 34.43747667; 130.25020977 | 8; 101.98059375; 12543.41025651 | 9; 27.84927778; 19.20394429 | 34.4; 102.0; 27.9 |

Direct visual inspection of the original table image,
`data/raw/processed_data_search/41564_2023_1564_Tab1_ESM.webp`, confirms that
Table 1b prints 27.9 for vehicle/unstimulated FVT Stress TNF-alpha. The source
mean 27.8492777778 rounds directly to 27.8 at one decimal. This is not an OCR
ambiguity. The printed number differs by approximately 0.051 pg/mL from the
calculated mean. Its origin is unresolved; intermediate rounding is possible
but was not verified. The validation retains this as one mismatch without
relaxing the stated rounding comparison. All nine selected caption-statistic
checks still agree with the unchanged observations. The combined check count
is therefore 17 matches out of 18, including one group-mean discrepancy.

Cell mean differences are percentage points. Cytokine mean differences are
pg/mL. Neither is an absolute cell count, a within-mouse chronic-stress change
or an ecological stability measurement.

## Reconstruction

For group sizes n, means m and unbiased sample variances s squared, the residual
variance is the sum of `(n - 1) * s_squared` divided by `N - 3`. The planned
contrast uses coefficients `[-0.5, 1, -0.5]` in the order Ctr, Ctr Stress,
FVT Stress. Its estimate is the stressed-control mean minus the average of the
other two means, and its standard error is the square root of
`MSE * sum(coefficient_squared / n)`. The two-sided t reference uses `N - 3`
degrees of freedom.

For each pair, Tukey-Kramer uses the absolute mean difference divided by
`sqrt(MSE * (1/n_first + 1/n_second) / 2)`, evaluated against a studentized range
with three groups and the same finite residual degrees of freedom. All three
pairwise comparisons are reported below, including the FVT versus Ctr comparison
that was not one of this project's two selected biological contrasts.

The calculation used SciPy's finite-df `studentized_range.sf` and `.ppf`, not
an infinite-df or normal approximation. The assumptions and unequal-size
Tukey-Kramer convention are documented in the
[SciPy Tukey reference](https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.tukey_hsd.html).

| Endpoint | Residual df | Pooled residual variance | Omnibus F | Omnibus P | Planned contrast t | Planned contrast P | Published t |
|---|---:|---:|---:|---:|---:|---:|---|
| LY6Chi monocytes | 26 | 2.5666310920 | 4.381803325 | 0.02291029966 | -2.866926809 | 0.008109467204 | -2.867, df 26 |
| CD62L-positive LY6Chi monocytes | 26 | 50.3033645204 | 14.02316928 | 0.00007390807938 | -3.180494077 | 0.003781051114 | -3.18, df 26 |
| Unstimulated splenocyte TNF-alpha | 23 | 3869.5436968707 | 3.616295650 | 0.04309266208 | 2.679946857 | 0.01337308961 | 2.68, df 23 |

| Endpoint | Pairwise contrast | Mean difference | Tukey-Kramer P | Published pairwise P | Agreement |
|---|---|---:|---:|---|---|
| LY6Chi monocytes | Ctr Stress minus Ctr | -2.034038 | 0.02280378315 | <0.05 | Matches inequality |
| LY6Chi monocytes | FVT Stress minus Ctr Stress | 1.556490856 | 0.1064091013 | 0.106 | Matches rounding |
| LY6Chi monocytes | FVT Stress minus Ctr | -0.4775471444 | 0.7947058379 | Not individually reported in caption | Additional model verification output |
| CD62L-positive LY6Chi monocytes | Ctr Stress minus Ctr | -1.760441 | 0.8448303242 | 0.845 | Matches rounding |
| CD62L-positive LY6Chi monocytes | FVT Stress minus Ctr Stress | 15.87365489 | 0.0001358531699 | <0.001 | Matches inequality |
| CD62L-positive LY6Chi monocytes | FVT Stress minus Ctr | 14.11321389 | 0.0005582177576 | Not individually reported in caption | Additional model verification output |
| Unstimulated splenocyte TNF-alpha | Ctr Stress minus Ctr | 67.54311708 | 0.08640501712 | 0.086 | Matches rounding |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Ctr Stress | -74.13131597 | 0.05568679863 | 0.056 | Matches rounding |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Ctr | -6.588198889 | 0.9725905184 | Not individually reported in caption | Additional model verification output |

The Tukey 95% interval for the monocyte FVT versus stressed-control difference is
-0.27264 to 3.38562 percentage points. Its pointwise Welch interval is 0.38926
to 2.72372. The pooled residual variance includes the higher-variance Ctr arm
even for a pair involving only the other two groups; Tukey also adjusts for
three pairwise comparisons. This concretely explains why the two intervals
have different widths and conclusions at a 0.05 threshold.

The original BH q values are not reproduced here. Their complete endpoint
families are not fully specified by the selected source columns and caption.
Applying BH to only these three planned contrasts would define a new family,
not reconstruct the publication's q values.

## Outlier and censoring policy

The original methods describe technical exclusions, below-detection cytokine
exclusions and a statistical rule beyond 2.5 standard deviations, with at most
two statistical exclusions per test. The workbook has missing cells but no
complete observation-level exclusion log or censoring thresholds. Numerical
agreement shows that additional deletions are unnecessary to reproduce the
selected reported statistics. It does not establish that upstream exclusions
never occurred or that unavailable values can be recovered.

No supplied value was discarded in this reconstruction. Outlier removal must
not be introduced to force either Welch or original-method significance.

## Scientific interpretation and assumptions

The planned contrast does not test a conjunction of both component effects.
For CD62L-positive monocytes, the FVT-associated rise coexists with a small,
imprecisely estimated stress-control difference. Reproducing the planned
contrast therefore does not establish reversal of a demonstrated deficit.

The TNF-alpha sample variances differ markedly, and the stressed group has only
eight observed values. Matching a pooled-variance statistic does not make the
common-variance assumption credible. A small-sample variance test would not
resolve that concern, and no significance-driven assumption selection is
appropriate. Mean contrasts, rank sensitivity and the original-method
reconstruction should remain separately labeled.

All animal-level methods also require valid independence. Cage allocation and
shared-housing dependence are unavailable; the original stress and handling
design does not supply a verified exchangeability scheme for a cage-aware
permutation analysis. Randomly permuting individual labels without that design
would add unjustified precision. Small group sizes and missingness also limit
normal approximation and multivariable adjustment. These constraints are not
removed by exact agreement with an original P value.

## Implementation and calculation checks

The reconstruction in `src/pisa/original_methods.py` exports group counts and
variances, pooled ANOVA, the planned contrast, all three Tukey-Kramer pairs and
comparisons with the published rounded statistics. Independent tests in
`tests/test_original_methods.py` compare the pooled calculations with
statsmodels OLS and linear contrasts, and the Tukey calculations with
statsmodels `pairwise_tukeyhsd` on unequal-size fixtures.

The [verification report](../results/reports/original_method_replication.md)
and [result table](../results/tables/original_method_replication.csv) retain the
full calculations. This layer checks numerical compatibility with the selected
published results. The six Welch comparisons remain unchanged, and the original
full BH family remains unresolved.
