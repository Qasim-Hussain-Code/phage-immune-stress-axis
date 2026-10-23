# Statistical validation

The checks in this appendix ask whether the implemented calculations agree
with independent software, direct enumeration and mathematical identities.
They also compare selected published statistics with calculations from the
unchanged source workbook. Agreement supports the numerical implementation;
it does not establish independent animals, valid censoring assumptions or a
virome-specific biological effect.

## Calculations checked independently

| Calculation | Independent reference or identity | Checks |
|---|---|---|
| Welch mean contrast | SciPy `ttest_ind(equal_var=False)` and confidence interval | Statistic, finite degrees of freedom, two-sided P and interval on unequal-size and unequal-variance fixtures. |
| Contrast reversal | Analytical identity | Reversing groups negates the effect and reverses interval limits while retaining the two-sided P value. |
| BH adjustment | statsmodels `multipletests(method="fdr_bh")` | Complete adjusted vector, ties, boundary P values and invalid inputs. |
| Leave-one-animal-out ranges | Separate brute-force sample means | Omission count, effect extrema, influential identifier and direction. |
| Finite-support missingness bounds | Exhaustive support-corner enumeration | Both extrema, complete and all-missing cases, reversal, invalid support and out-of-support observations. |
| Empirical rank effects | SciPy average ranks and direct cross-animal pair counting | U, ties, reversal, superiority, rank-biserial effect and agreement with the existing sensitivity U. |
| Original pooled ANOVA and planned contrast | Independently fitted statsmodels OLS and `t_test` | Residual sum of squares, pooled variance, F, contrast effect, standard error, t, P and interval. |
| Original Tukey-Kramer pairs | statsmodels `pairwise_tukeyhsd` | All three pairs and simultaneous intervals on unequal-size fixtures. |
| Aitchison distance | Pairwise log-ratio identity | All-pairs expression versus CLR Euclidean distance. |
| Bray-Curtis distance | SciPy `braycurtis` | Agreement after closure on synthetic compositions. |
| Compositional edge cases | Mathematical invariants | Scale invariance, zero-sum CLR, zero handling and rejection of invalid or all-zero inputs. |
| Vectorized calibration Welch | Independent sample-based SciPy tests | P, degrees of freedom, orientation and intervals from explicit sample arrays. |
| Artificial cluster generator | Exact linear-map covariance | Marginal variance one, within-pair covariance 0.5 and zero cross-cluster covariance. |
| Monte Carlo intervals | statsmodels Wilson implementation | Binomial intervals, including zero and all successes. |

The compositional calculations are tested on synthetic fixtures. No retrieved
biological community matrix was available to apply them to. The deliberately
constant-arm Welch fixture can produce a SciPy precision-loss warning; it is
not an experimental observation.

## Reconstruction from the source workbook

The [original-method table](../results/tables/original_method_replication.csv)
contains group summaries, pooled ANOVA, the planned contrast and all three
Tukey-Kramer comparisons for the same three selected endpoints. No supplied
observation is excluded. Seventeen of 18 printed-reference checks agree:
all nine selected caption-statistic checks and eight of nine group-summary
checks. The remaining FVT unstimulated TNF-alpha mean is 27.8492778 pg/mL in
the workbook, which rounds directly to 27.8; the visually checked Extended Data
Table 1b prints 27.9. The discrepancy remains unresolved, with no changed
source value or widened rounding tolerance.

For the monocyte FVT comparison, the same observations give Welch P=0.012645
and Tukey-Kramer P=0.106409. The latter reproduces the published P=0.106.
Pooling variance across all three groups and adjusting the three pairwise
comparisons explains the difference. This numerical reconstruction does not
establish the common-variance assumption or reproduce the unavailable original
SPSS session. The [reconstruction report](../results/reports/original_method_replication.md)
and [original-analysis review](original_analysis_review.md) retain the detailed
calculations and publication comparisons.

## Families, biological units and uncertainty

The exploratory mean-test family contains three FVT-experiment endpoints by two contrasts,
with one six-test BH adjustment and pointwise 95% Welch intervals. Endpoint
selection was informed by the published findings. The six rank comparisons
have their own BH family and concern distributional ordering. Original-method
Tukey intervals cover three pairs within one endpoint; the publication's
complete across-outcome BH family remains unreconstructed. The [methods](methods.md)
define the endpoints and comparisons.

Source identifiers retain their punctuation and are scoped by experiment and
treatment. Tests distinguish missing cells from observed zeroes, reject
duplicate endpoint records, and prevent pools or inocula from acquiring an
individual recipient's immune outcome. Sequencing files are not biological
replicates. These checks cannot create an absent animal crosswalk. Welch
inference still assumes independent observations; unknown cage and allocation
details and unresolved upstream exclusions limit its interpretation.

The support bounds and normalized rank effects were added after the earlier
reanalysis and introduce no hypothesis tests. Bounds concern workbook-row
animals, conditional on every missing percentage assay having a well-defined
value in [0,100]. They do not cover omitted animals or sampling uncertainty,
and TNF-alpha lacks a justified finite upper support. Empirical rank effects
reuse animals across pairs: the 72 TNF-alpha comparisons involve 17 observed
animals. Leave-one-animal-out ranges describe influence, not confidence
limits. See [phenotype robustness](phenotype_robustness.md) for the definitions
and [limitations](limitations.md) for their biological scope.

## Conditional synthetic calibration

The benchmark generated 20,000 all-null replicates for each of five fixed
models, using seed 20261020 and batches of 500. Three independent synthetic
endpoints have group sizes 10/10/9. Each endpoint retains the shared middle
group in its two adjacent contrasts, so the six Welch P values form one BH
family with that dependence preserved. The outputs record per-test false
positives, pointwise Welch coverage, family rejection and within-endpoint
three-pair Tukey coverage.

The recorded probability of any BH rejection at 0.05 is:

| Synthetic model | Probability | Wilson 95% Monte Carlo interval |
|---|---:|---|
| Independent equal-variance Gaussian | 0.04620 | 0.04338 to 0.04920 |
| Independent Gaussian, variances 4/1/1 | 0.04795 | 0.04507 to 0.05100 |
| Independent centered lognormal | 0.01150 | 0.01011 to 0.01307 |
| Artificial all-group Gaussian clusters, ICC 0.5 | 0.16495 | 0.15987 to 0.17016 |
| Hypothetical controls-only clusters, ICC 0.5 | 0.06890 | 0.06547 to 0.07249 |

These five rows come from [software_calibration.csv](../results/tables/software_calibration.csv).
Because every null is true, the family rejection probability equals both
FWER and FDR in this simulation. Wilson intervals describe Monte Carlo error,
not uncertainty about mouse effects or the real cage structure. The artificial
all-group scenario imposes clusters in every group. The added controls-only
scenario instead uses the inferred control layout and leaves both stressed
groups independent; its marginal FVT–Stress test law remains independent, while
the six-test BH family also depends on Stress–Control P values. Neither model
estimates actual cages or ICC. Their common 10/10/9 group sizes also abstract
from endpoint-specific missingness. No biological
observations enter the generator, and these results do not calibrate the
actual experiment under its unknown dependence. The [calibration design](calibration_design.md)
sets out the scenarios and their interpretation.

## Recorded executions

The latest Windows suite on 23 October 2026 collected 219 tests, executed
213 and skipped six platform-specific cases, with zero failures or errors.
New numerical checks compare HC3 covariance, contrast intervals and P values
with statsmodels, log-Welch calculations with SciPy, and each declared BH
family independently. Source tests verify the literal-label inventory without
turning it into a validated assay join. The suite also retains the release
check's full-invocation binding and legitimate-resume regressions. The source
identity and individual outcomes are in the
[validation summary](../results/reports/validation_summary.json) and
[log](../results/reports/validation.log). The primary statistical values remain
unchanged; nine CSVs, a fifth calibration scenario and revised figures extend
the output collection to 39 files. The
[comparison evidence](../results/reports/design_sensitivity_validation.json)
records exact bytes separately from CSV-record comparisons.

The fresh [Windows replay](../results/reports/reproduction_check.json) on
23 October used commit `c5504eb64600300b12b6ad7951a492d32fb33677`. It executed all
ten stages without resume, reproduced all 39 scientific files exactly, and
collected 219 tests: 213 executed, six skips, zero failures or errors.

The historical [Linux replay](../results/reports/linux_reproduction_check.json)
on 21 October used commit `eb7ba6c8b945670a1f55c493d89435f36750900c`, with code
SHA-256 beginning `9d62cd4b5958`. It collected 174 tests, executed 165 and
skipped nine, with zero failures or errors. It
passed all 20 CSV comparisons under the fixed policy and matched the ten
Linux figure files covered by the retained visual review. Its
[suite summary](../results/reports/linux_validation_summary.json) records the
Linux cases. This replay applies to that earlier source identity; it does not
establish Linux execution of the later reporting, timing, release-check,
design/scale sensitivity or figure revisions.
