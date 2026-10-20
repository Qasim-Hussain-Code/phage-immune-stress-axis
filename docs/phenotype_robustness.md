# Descriptive phenotype robustness methods

This module adds information about the same three selected study II outcomes
and two existing contrasts. It calculates no additional hypothesis tests,
P values, adjusted P values or confidence intervals. The original Welch and
rank-sensitivity tables remain unchanged. These descriptive diagnostics were
added after inspecting the earlier reanalysis; they are not prespecified
confirmatory tests. Generated results are in
`results/reports/phenotype_robustness.md`, with machine-readable tables
`immune_missingness_bounds.csv` and `immune_rank_effects.csv`.

## Target and source cohort

The prepared source data retain every phenotype record, including missing
assays, for each animal represented by a workbook row. Composite animal keys
contain experiment, group and the literal source identifier. Group denominators
come from these source rows; they do not establish that every originally
randomized animal is represented or recover animals removed before deposition.
Every selected endpoint must retain a record for every represented animal,
including an explicit missing record when necessary. The code rejects absent
endpoint records, altered identifiers and duplicate individual outcomes.

## Sharp finite-support bounds

Let group A contain N_A source-row animals, of which m_A have missing assays,
and let S_A be the sum of its observed values; define N_B, m_B and S_B similarly.
If every missing assay has a well-defined value within a common support [L,U],
the source-cohort mean difference has bounds

`lower = (S_A + m_A*L)/N_A - (S_B + m_B*U)/N_B`

`upper = (S_A + m_A*U)/N_A - (S_B + m_B*L)/N_B`.

These bounds are sharp under the stated support alone: assigning missing
values to the relevant support corners attains each endpoint. No corner value
is inserted into the source data or selected as an estimated observation.
When neither group has missing values, the bounds collapse to the observed
source-cohort mean difference. They are descriptive extrema, not confidence
limits, a test of significance, or a population treatment-effect interval.
Bounds preserving a sign do not establish that an associated P value, interval
or causal conclusion is robust.

The two selected flow outcomes are percentages of parent population, so their
assumed support is [0,100] and differences are percentage points. Applying the
bounds is conditional on each missing assay having a well-defined percentage
at the intended sampling time. A nonexistent or unmeasurable parent population
must not automatically be assigned zero. Observed values outside the support
cause failure rather than clipping. No cross-assay constraints on the missing
values are assumed. In the frozen source, the missing FVT flow measurements
belong to source animal31, which has an observed TNF-alpha value; it is not an
absent source animal.

For TNF-alpha, the assay-specific detection thresholds, missingness causes and
finite upper support are unavailable. Missing assays occur in both groups in
each selected contrast. A nonnegative concentration scale supplies no finite
upper value, and therefore no finite two-sided bounds are reported. Blank
bound fields carry an explicit unavailable status, rather than zero, infinity
or a guessed detection limit. No missing-at-random assumption is made.

These checks differ from leave-one-out diagnostics, which remove observed
animals and do not vary unobserved assays.

## Empirical rank effects and independent identity check

For observed values in groups A and B, count W cross-group pairs in which the
first value is greater, T ties and K pairs in total. The empirical superiority
measure is `(W + T/2)/K`; the rank-biserial effect is twice that measure minus
one. Positive values favor larger observed A values. This is an empirical
ordering description; it does not estimate the same quantity as a raw mean
difference and need not describe a common median shift when shapes differ.

Average pooled ranks independently calculate `U_A = rank_sum_A - n_A*(n_A+1)/2`.
The module requires agreement with direct enumeration `U_A = W + T/2` and with
the U already recorded in the existing sensitivity table. It neither imports
nor recalculates the sensitivity P or adjusted P values. Reversing groups
complements superiority and negates the rank-biserial effect; ties receive
half credit. Output includes both animal counts and pair counts explicitly.
Pairs share animals and are not independent replicates or additional sample
units. No standard error or confidence interval is calculated from K as though
it were an independent sample size.

## Limits and verification

These summaries cannot remove unknown dependence, censoring or upstream
exclusions, recover missing viral measurements, or identify a phage mechanism.
They preserve the endpoint selection and exploratory status of the analysis.
Synthetic unit fixtures enumerate every missing-value corner, verify tie and
reversal identities against independently calculated ranks, reject invalid
support and stale U values, and exercise the prepared-stage file contract.
No synthetic values enter biological result tables.
