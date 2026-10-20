# Statistical validation

Current executed test counts, failures, errors and skips are recorded in
`results/reports/validation_summary.json`, with individual outcomes in
`results/reports/validation.log`. The expanded software suite and full synthetic
benchmark completed successfully. Completion of the remaining workflow and
visual QA is established by their matching invocation records; an earlier
successful run does not establish a current invocation's outcome. Resource peaks belong to the
invocation that measured them; see [resource_usage.md](resource_usage.md) and
[reproduction_validation.md](reproduction_validation.md).

Synthetic fixtures and calibration outputs are software checks only. They are
kept separate from biological observations and cannot replace missing assays.

## Independent estimator checks

| Calculation | Independent reference or identity | Implemented checks |
|---|---|---|
| Welch mean contrast | SciPy `ttest_ind(equal_var=False)` and confidence interval | Statistic, finite degrees of freedom, two-sided P and interval across unequal-size/variance fixtures. |
| Contrast reversal | Analytical identity | Group reversal negates the effect and reverses limits while retaining two-sided P. |
| BH adjustment | statsmodels `multipletests(method="fdr_bh")` | Full adjusted vector, ties, boundary P values and invalid inputs. |
| Leave-one-animal-out ranges | Separate brute-force sample means | Omission count, effect extrema, influential identifier and direction. |
| Original pooled ANOVA and planned contrast | Independently fitted statsmodels OLS and `t_test` | Residual sum of squares, pooled variance, F, contrast effect, standard error, t, P and interval. |
| Original Tukey-Kramer pairs | statsmodels `pairwise_tukeyhsd` | All three pairs and simultaneous intervals in unequal-size synthetic fixtures. |
| Aitchison distance | Pairwise log-ratio identity | Independent all-pairs expression versus CLR Euclidean distance. |
| Bray-Curtis distance | SciPy `braycurtis` | Agreement after closure on synthetic compositions. |
| Compositional edge cases | Mathematical invariants | Scale invariance, zero-sum CLR, zero handling and rejection of invalid/all-zero inputs. |
| Vectorized calibration Welch | Independent sample-based SciPy tests | P, degrees of freedom, orientation and intervals from explicit sample arrays. |
| Artificial cluster generator | Exact linear-map covariance | Marginal variance one, within-pair covariance 0.5 and zero cross-cluster covariance. |
| Monte Carlo intervals | statsmodels Wilson implementation | Binomial interval agreement including zero and all successes. |

The deliberately constant-arm synthetic Welch fixture can produce a SciPy
precision-loss warning. It is distinct from biological source data. Community
utilities likewise have no biological matrix to analyze; their successful unit
checks do not establish a measured phageome stability result.

## Real-source reconstruction

The separate original-method table contains group summaries, pooled ANOVA,
the planned contrast and all three Tukey-Kramer comparisons for each of the
same three selected endpoints. No supplied observation is excluded. All nine
selected caption t/P comparisons reproduce at reported precision. Eight of
nine group-summary comparisons agree, giving 17 matches out of 18 combined
checks. FVT unstimulated TNF-alpha has source mean 27.8492778 pg/mL, directly
rounding to 27.8, while the visually verified Table 1b prints 27.9. This one
discrepancy remains explicit and does not trigger relaxed tolerances.

The original monocyte FVT Tukey P is reconstructed as 0.106409 from the same
observations that yield Welch P=0.012645. Pooled variance from all three groups
and Tukey multiplicity explain the difference. No population change or extra
exclusion is needed for this reconciliation. Original planned BH q values are
reference annotations only; the complete original endpoint family remains
unreconstructed. Detailed evidence is in
[original_analysis_review.md](original_analysis_review.md).

## Source identity and independence safeguards

Source IDs retain literal punctuation and are scoped by experiment and group.
Tests prevent decimal labels, repeated group-local numbers and similar-looking
sequencing aliases from collapsing into an invented identity. Duplicate
individual endpoint records and unknown groups fail clearly. The unchanged
source workbook, blank formatted rows, observed zeroes and missing cells are
checked separately. Study I remains in the audit without entering the selected
study II inferential family.

Pool and inoculum records cannot acquire an individual recipient's immune
outcome. FASTQ files are technical objects, not biological replicates. These
software rules enforce available metadata; they cannot verify an absent
animal-to-assay crosswalk or supply missing abundance values.

## Acquisition, resources and resumption

Checks cover missing offline inputs, corrupt hashes, capped streaming downloads,
partial-file cleanup, and code/config/input/output changes that invalidate a
cached stage. Dynamic Zenodo usage counters are excluded from normalized
scientific metadata. Stage contracts prevent an unexecuted downstream analysis
from inheriting success merely because an old file exists.

Resource checks distinguish per-process native peaks from sampled concurrent
descendant RSS. Storage and free-disk constraints use a persistent local
host/checkout baseline, not historical disk values from another run. Timeouts
bound elapsed stage time rather than CPU time. Resume and pilot/validation-only
status are recorded per invocation; they are not claims that all scientific
stages ran. Figure visual review is separately tied to current file hashes.

## Inferential families and uncertainty

The primary biological mean family remains three endpoints by two contrasts,
using available observations, two-sided Welch inference and one six-test BH
adjustment. Its 95% intervals are pointwise. Endpoints were selected after the
published results were known and before calculating these contrasts, so this
remains exploratory. The rank-based six-test family is a labeled sensitivity
analysis of distributional ordering, not a replacement mean test. Omission
ranges are influence diagnostics rather than confidence intervals.

All six observed mean contrasts retain direction after individual omissions.
This limited observation does not establish stable significance or remove
housing dependence. TNF-alpha remains method-sensitive: its FVT Welch q is
0.1551 and rank sensitivity q is 0.01102. Both are reported.

## Conditional synthetic null calibration

The separate benchmark has four fixed zero-mean models: independent equal-
variance Gaussian, unequal-variance Gaussian, centered lognormal and artificial
Gaussian clusters with ICC 0.5. It jointly generates the overlapping contrasts
and records per-test false-positive rates, Welch coverage, all-null BH family
rejection and within-endpoint three-pair Tukey coverage. Defaults are 20,000
replicates per scenario and batches at most 500. Quick checks use much smaller
fixtures. Seeded replicate-major streams are tested for batch invariance.

Every benchmark row has `purpose=synthetic_not_biological`. Wilson bounds measure
simulation error across replicates, not mouse-effect uncertainty. The artificial
all-group clusters do not represent the original singly housed stressed groups
or estimate actual cage ICC. No observed immune values enter the generator,
and no biological power calculation is claimed. The expanded benchmark
completed 20,000 replicates per scenario with seed 20261020 and batches of 500.
Its recorded all-null BH family any-rejection probabilities are:

| Synthetic assumption | Probability | Wilson 95% Monte Carlo interval |
|---|---:|---|
| Independent equal-variance Gaussian | 0.04620 | 0.04338 to 0.04920 |
| Independent unequal-variance Gaussian | 0.04795 | 0.04507 to 0.05100 |
| Independent centered lognormal | 0.01150 | 0.01011 to 0.01307 |
| Artificial clusters, ICC 0.5 | 0.16495 | 0.15987 to 0.17016 |

These are measured software behavior under complete-null assumptions. In this
special case FDR equals FWER; neither probability is an estimate of the actual
study's error rate. Per-test and interval-coverage outcomes are retained in
`results/tables/software_calibration.csv`.
See [calibration_design.md](calibration_design.md).

## Limits of validation

No empirical cage-aware null calibration of the actual experiment is possible
without its dependence information. A synthetic assumption stress test does
not close that gap. No phage-immune permutation test, repeated-measures
stability model, bacterial-adjusted association or mediation was executed.
Agreement with trusted software does not establish normality, homoscedasticity,
independent mice, unbiased censoring, causal treatment attribution or external
generalizability. The unknown design and missing inputs remain the scientific
limits described in [limitations.md](limitations.md).
