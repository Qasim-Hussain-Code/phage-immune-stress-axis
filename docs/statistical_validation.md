# Statistical validation

The executed suite ran 25 tests with zero failures, zero errors and zero skipped
tests. The machine-readable record is
`results/reports/validation_summary.json`; individual outcomes are in
`results/reports/validation.log`. The measured test-process peak resident memory
was 157,196,288 bytes. This is a test-process measurement, not total system RAM.

All synthetic values and workbooks used below are software fixtures. They are
not included in biological result tables or interpreted as experimental data.

## Independent estimator checks

| Calculation | Independent reference or identity | Executed checks |
|---|---|---|
| Welch mean contrast | `scipy.stats.ttest_ind(equal_var=False)` and its confidence interval | Compare statistic, degrees of freedom, two-sided P value and interval across unequal-size and unequal-variance fixtures, including a constant arm. |
| Direction and interval symmetry | Analytical reversal identity | Swapping groups negates the difference and reverses interval limits while preserving two-sided P. |
| Benjamini-Hochberg adjustment | `statsmodels.stats.multitest.multipletests(method="fdr_bh")` | Compare full ordered output with ties and boundary P values; reject invalid or nonfinite inputs. |
| Leave-one-animal-out ranges | Separate brute-force sample means | Check every deletion's effect range, count, influential identifier and direction change on a fixture with a known influential observation. |
| Aitchison distance | Pairwise log-ratio identity | Compare CLR Euclidean distance to the independent all-pairs expression on positive synthetic compositions. |
| Bray-Curtis distance | `scipy.spatial.distance.braycurtis` | Compare after closure on synthetic compositions. |
| Compositional input behavior | Mathematical invariants and explicit failures | Check closure scale invariance, zero-sum CLR, identical-profile distance and pseudocount sensitivity; reject all-zero, negative, nonfinite or mismatched inputs. |

The log includes SciPy's precision-loss warning for a deliberately constant-arm
synthetic Welch fixture. The independent comparisons passed. This warning was
not generated from the biological contrast tables.

The community functions are validated software utilities only. No unavailable
biological abundance matrix was substituted with the synthetic fixture, and no
community-distance biological result is reported.

## Source extraction and independence checks

Source IDs retain their literal representation and are scoped by experiment
and group. Tests ensure that `19.2`, `19.1`, `1x2`, `12` and similar labels do
not collapse through punctuation removal. Reused numeric IDs across groups or
experiments produce different keys. Duplicate individual endpoint records and
unknown source groups fail validation.

Synthetic workbook checks verify that the source file is unchanged, fully blank
formatted rows are excluded, zero remains observed, missing outcomes remain
missing and the selected analyses contain exactly six study II tests. Study I
observations remain in the audit but are not subjected to the selected
inferential family. Missing source files cause a clear error rather than an
empty scientific output.

Separate sample-linkage tests ensure that pools and inocula do not acquire an
individual recipient identity or immune linkage. FASTQ files and bytes are
counted as technical data objects rather than additional biological replicates.
These checks enforce recorded identifiers; they cannot verify an absent
cross-assay mapping.

## Acquisition and resume safeguards

The executed tests check rejection of missing offline inputs, checksum mismatch,
streaming downloads above a hard byte limit and removal of partial files.
Changing a frozen input changes the pipeline fingerprint. Zenodo usage counters
are excluded from normalized scientific release metadata so that changing view
counts do not masquerade as a dataset change.

## Analysis family and reported uncertainty

The biological mean-test family contains three selected endpoints by two
contrasts, all from study II. Each contrast uses the observed outcome values in
its two groups. It estimates mean(first group) minus mean(second group), with
an unpaired two-sided Welch test and a pointwise 95% Welch interval. One BH
adjustment is applied across the six P values. The family was fixed before
calculating these contrasts, after the original published results were known;
the results remain exploratory.

Rank-based Mann-Whitney comparisons form a separately labeled six-test
sensitivity family. They examine distributional ordering rather than the same
mean estimand. Their q values do not replace the Welch results. Leave-one-animal
omissions are influence diagnostics; their minimum and maximum refitted effects
are not uncertainty intervals and their P values are not independent tests.

## Observed sensitivity and discrepancies

All six mean contrasts retain their direction after every single-animal
omission. This supports a limited statement about directional influence, not
proof of full robustness. For the TNF-alpha FVT contrast, omission-refit P values
range from 0.1007 to 0.2177, while the observed Welch q is 0.1551. The rank
sensitivity q is 0.01102. Unequal dispersion and influential upper-tail values
make the distinction between mean and rank inference material.

The monocyte FVT Welch P of 0.01265 differs from the original article's Tukey
pairwise P of 0.106. This reanalysis does not reproduce the original three-group
variance model and post hoc correction. Upstream exclusions are incompletely
documented at the observation level. This difference remains a reported
limitation rather than a validation failure or a reason to select a preferred
significance result.

## What has not been validated

No empirical null calibration was performed for cage dependence because cage
assignments were unavailable. No phage-immune permutation test, repeated-measures
model, biological stability estimator, bacterial-adjusted association or mediation
analysis was executed. There is no evidence that any unavailable analysis
succeeded. Mathematical agreement with trusted implementations does not establish
that animal independence, censoring assumptions, treatment attribution or
external generalizability hold.

The sample size and missingness do not support high-dimensional adjustment, and
no post hoc power calculation is used to reinterpret nonsignificant contrasts
as evidence of absence. Detailed scope and biological limits are in
[limitations.md](limitations.md).
