# Calibration under explicit sampling assumptions

The immune analysis uses small-group Welch comparisons, a six-test
Benjamini-Hochberg (BH) family and a separate reconstruction of the original
Tukey-Kramer comparisons. A synthetic benchmark examines their false-positive
and interval-coverage behavior when stated sampling assumptions hold or are
deliberately violated. It reads no biological outcomes, animal identifiers,
observed effect estimates or real cage assignments. Its probabilities describe
software performance under the generating models below, not biological power
or the validity of the study's unknown dependence structure. One added model
uses a hypothetical control-cluster layout motivated by source identifiers;
the identifiers do not establish confirmed cages.

## Generating models and comparison structure

Each replicate contains three independent synthetic endpoints and three groups
of sizes 10, 10 and 9. Every true group mean is zero. Within each endpoint, the
contrasts are group 1 minus group 0 and group 2 minus group 1. They share group 1,
so their estimates and P values are dependent. The six tests across the three
endpoints form one BH family per replicate; the benchmark does not replace them
with six unrelated uniform P values.

The original four models were fixed before the 20 October benchmark. A fifth
model was added after the subsequent design review, using the proposed control
cluster sizes without fitting an ICC or selecting parameters to reproduce an
outcome. It supplements the earlier all-group cluster stress test.

| Scenario | Generating model | Assumption examined |
|---|---|---|
| Independent Gaussian, equal variance | Independent `N(0,1)` observations in all groups | Symmetric, independent sampling with a common variance |
| Independent Gaussian, unequal variance | Independent zero-mean Gaussian observations with group variances `4,1,1` | Fixed variance heterogeneity |
| Independent centered lognormal | Independent `exp(Z) - exp(0.5)`, with `Z ~ N(0,1)` | Skewed sampling with identical distributions and known zero means |
| Artificial Gaussian clusters | `Y_i = sqrt(0.5)*C_k(i) + sqrt(0.5)*E_i`, with independent standard-normal cluster effects and residuals | Dependence within artificial pairs |
| Hypothetical controls-only Gaussian clusters | The same random-intercept model only in group 0, with six cluster sizes `2,2,1,2,2,1`; groups 1 and 2 remain independent `N(0,1)` | Dependence confined to group-housed controls under an unverified ID interpretation |

The cluster model uses five independent cluster effects per endpoint and group,
with `k(i) = floor((i-1)/2) + 1`. Groups of ten contain five pairs; the group of
nine contains four pairs and a singleton. Each observation has variance one,
and two observations sharing a cluster have covariance and correlation 0.5.
This ICC applies only within a synthetic pair. Different clusters, groups and
endpoints are independent.

That all-group assignment is a generic stress test. The original stressed
groups were singly housed, whereas unstressed controls were group housed. The
additional model assigns control observations to hypothetical clusters
`[0,0,1,1,2,3,3,4,4,5]`, with sizes `[2,2,1,2,2,1]`. The layout follows the
integer portions of the ten control IDs under a proposed cage interpretation;
neither those integers nor their shared prefixes confirm actual cages. The
ICC of 0.5 is imposed, not estimated. The code uses fixed sizes and reads no
source IDs, outcomes or cage key.

In this controls-only model, individual variances remain one. Only control
pairs in the same hypothetical cluster have covariance 0.5; Stress and FVT
observations are independent of each other and of controls. The control mean
has variance `0.14`, compared with `0.10` under independence. The true variance
of Stress minus Control is consequently `0.24`. FVT minus Stress still has
variance `1/9 + 1/10`, and the two contrast estimates have covariance `-0.10`
because both use the Stress mean. These are generating-model properties, not
estimated uncertainties for the biological contrasts.

Both cluster models omit possible immune correlations and shared assay batches
because their endpoint-specific effects are independent. The 10/10/9 pattern
is a small-group benchmark, not a model of endpoint-specific source missingness.
Neither model reconstructs actual cages or calibrates the study's unknown ICC.

## Estimated probabilities

For a pair of groups A and B, the Welch calculation uses unbiased sample
variances:

```text
d = mean_A - mean_B
SE^2 = s_A^2/n_A + s_B^2/n_B
df = SE^4 / [(s_A^2/n_A)^2/(n_A-1) + (s_B^2/n_B)^2/(n_B-1)]
95% interval = d +/- t_(0.975,df)*SE
```

Two-sided t probabilities determine unadjusted rejection at 0.05. For the six
sorted P values, BH rejects at least one hypothesis when any
`p_(i) <= i*0.05/6`. Because all hypotheses are null, the probability of any BH
rejection equals both familywise error rate and false discovery rate in this
benchmark. That equality is specific to the complete null.

The table records per-contrast unadjusted rejection and pointwise Welch interval
coverage, plus the six-test BH event. It also records simultaneous coverage of
all three Tukey-Kramer pairwise intervals within each endpoint. Those intervals
use

```text
MSE = sum_g [(n_g-1)*s_g^2] / 26
pair interval = d +/- q_(0.95;3,26)*sqrt[(MSE/2)*(1/n_A + 1/n_B)]
```

The residual degrees of freedom are `10 + 10 + 9 - 3 = 26`. The finite-df
studentized-range critical value is computed once. Tukey coverage concerns a
three-pair family within one endpoint, not simultaneous coverage across all
three endpoints. The common-variance formula is deliberately retained under
unequal variance, skewness and clustering to examine its behavior there.

In the controls-only scenario, the unadjusted FVT-minus-Stress Welch calculation
uses independent Gaussian groups and has the same generating law as in the
independent equal-variance scenario. Its simulation stream is separate, so
finite-run counts need not be identical. Control dependence can still change
the six-test BH event, since that family includes Stress-minus-Control tests.
Every group contributes to the Tukey pooled variance, and its simultaneous
three-pair coverage must be assessed separately. A per-contrast false-positive
probability is not the BH family rejection probability.

## Findings from the recorded benchmark

The original four-scenario full run used seed **20261020**, **20,000 independent
replicates per scenario**, and **40 batches of 500**. Its all-null BH family
results are retained below; the controls-only model was not part of that run.

| Scenario | Replicates with any BH rejection | Estimated probability | Wilson 95% Monte Carlo interval |
|---|---:|---:|---:|
| Independent Gaussian, equal variance | 924 / 20,000 | 0.04620 | 0.04338 to 0.04920 |
| Independent Gaussian, unequal variance | 959 / 20,000 | 0.04795 | 0.04507 to 0.05100 |
| Independent centered lognormal | 230 / 20,000 | 0.01150 | 0.01011 to 0.01307 |
| Artificial Gaussian clusters, within-pair ICC 0.5 | 3,299 / 20,000 | 0.16495 | 0.15987 to 0.17016 |

The independent Gaussian models give family rejection probabilities close to
the nominal 0.05 level. The centered lognormal model is conservative for this
event at these sample sizes. Ignoring the artificial pair dependence raises
family rejection well above nominal. In that cluster scenario, the six
pointwise Welch coverage estimates range from 0.88450 to 0.89220, and the three
within-endpoint Tukey simultaneous coverage estimates from 0.85640 to 0.86095,
against nominal 0.95. These findings illustrate the consequences of this
specified dependence model; they do not show that the study animals followed
it or provide an adjustment for their unknown dependence.

The expanded benchmark produces 16 estimates per scenario, hence 80 rows. The
controls-only model is identified by
`hypothetical_controls_only_gaussian_clusters_icc_0_5` and stream index 4 in the
[complete table](../results/tables/software_calibration.csv) and
[generated report](../results/reports/software_calibration.md). Its results
must not be inferred from the earlier all-group rejection probability 0.16495.
The original four scenario streams and generating formulas are unchanged.
Every row is labeled `purpose=synthetic_not_biological`.

## Monte Carlo uncertainty and reproducibility

Each event probability has a pointwise Wilson 95% binomial interval across
independent generated replicates. These intervals describe Monte Carlo error,
not uncertainty about a mouse effect or the actual cage ICC, and are not
simultaneous intervals across the expanded 80 summaries. At probability 0.05, 20,000
replicates give a Monte Carlo standard error of about 0.00154. The unadjusted
zero-null rejection and pointwise coverage events are complementary apart from
numerical boundary cases.

Each scenario has a fixed PCG64 stream derived from the global seed and stable
scenario index. Replicate-major draws use a fixed number of innovations per
replicate; the tenth padded observation of group 2 is never analyzed. This
preserves the random sequence across batch partitions under the recorded NumPy
implementation. The output records the stream index, library versions, batch
sizes and replicate counts. Only batch arrays and event counts are retained;
raw simulated observations are not saved. Replicates are capped at 20,000 per
scenario and batch size at 500. The fifth scenario is appended at index 4,
preserving indices 0 through 3 and their original draw consumption. It uses
six control effects and ten control residuals per endpoint; the other groups
use independent normal innovations. Padding and unused draws have a fixed
layout so uneven batch partitions preserve the sequence too.

[calibration.py](../src/pisa/calibration.py) implements the benchmark, with
settings in [analysis.yaml](../config/analysis.yaml). Existing small fixtures
compare Welch calculations with sample-based SciPy results, Wilson intervals
with statsmodels, and both cluster covariances with exact analytical matrices.
They check independence across endpoints/groups, the controls-only mean and
contrast variances, preservation of the four earlier streams and counts, and
seeded batch invariance. Added-signal fixtures verify software
orientation and rejection behavior only. They are not power estimates. The
20,000-replicate benchmark runs separately from those quick checks. It cannot
replace the viral profiles and animal linkage needed to relate viral change to
endpoint immune phenotypes, or supply the immune baseline needed to study
within-mouse immune change.
