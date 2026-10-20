# Synthetic software calibration design

This benchmark evaluates software behavior under four explicitly synthetic
all-null generating models. Every output row is labeled
`purpose=synthetic_not_biological`. The module reads no experimental outcomes,
mouse identifiers, real cage assignments or observed effect estimates. It does
not estimate biological power or validate the actual experiment's unknown
dependence structure.

## Prespecified scenarios

Each replicate contains three independently generated synthetic endpoints and
three groups of 10, 10 and nine observations. All true group means are zero.
For each endpoint, the same middle group's data appear in both adjacent
contrasts. The resulting six Welch tests form one BH family per replicate.

| Scenario | Generating rule | Purpose |
|---|---|---|
| Independent Gaussian, equal variance | Independent N(0,1) observations in every group | Reference behavior under independent symmetric equal-variance sampling. |
| Independent Gaussian, unequal variance | Independent Gaussian observations with group variances 4,1,1 and zero means | Assumption sensitivity to fixed variance heterogeneity. |
| Independent centered lognormal | exp(N(0,1)) minus exp(0.5) in every group | A skewed distribution with known equal zero means, without fitting its center to source data. |
| Artificial Gaussian clusters | Five independent unit-variance Gaussian cage effects and independent residuals per endpoint/group; both components scaled by sqrt(0.5) | A generic dependence stress test with marginal variance one and within-pair ICC 0.5. |

The artificial cluster scenario contains five pairs in groups of ten, and four
pairs plus one singleton in the group of nine. Cluster effects are independent
across endpoints and groups. This assignment is deliberately artificial. The
source experiment's stressed groups were singly housed; this scenario does not
describe their cages, infer shared cages for those animals or claim to estimate
their ICC. It measures consequences of violating the software's independence
assumption under one transparent hypothetical design.

The choices were fixed before running the full benchmark. They are not selected
to reproduce any published or reanalyzed biological P value. The sample-size
pattern is a generic small-group benchmark; endpoint-specific source missingness
and biological heterogeneity are not modeled.

## Estimators and events

The vectorized Welch calculation uses unbiased sample variances, finite Welch
degrees of freedom, two-sided t probabilities and pointwise 95% t intervals.
Its formulas are independently checked against SciPy's sample-based
`ttest_ind(equal_var=False)`. Across the six jointly generated P values, the
standard BH step-up rule is evaluated at 0.05.

The benchmark records:

- Unadjusted per-contrast false-positive probability at 0.05.
- Per-contrast coverage of the true-zero difference by the pointwise 95% Welch
  interval.
- Probability of any BH rejection in the all-null six-test family. Because all
  hypotheses are null, this equals both FWER and FDR in this benchmark.
- Coverage of all three true pairwise differences by the original-method
  Tukey-Kramer simultaneous 95% intervals, separately for each endpoint.

Tukey intervals use the three-group pooled variance and one finite-df
studentized-range critical value at residual df 26. The critical value is
computed once and cached. There is no per-replicate studentized-range CDF
integration. Its family is the three pairs within an endpoint, not all endpoints
jointly.

The BH event retains the dependence created by overlapping contrasts; it does
not simulate six unrelated uniform P values. The three endpoints are otherwise
independent by design. The result need not describe endpoints correlated through
actual immune biology, assay batches or actual housing.

## Monte Carlo precision and resource bounds

Full execution defaults to 20,000 independent replicates per scenario, with seed
`config.seed` and batches of at most 500. Optional `calibration.replicates` and
`calibration.batch_size` settings control execution size; values above the batch
bound are rejected. Only batch arrays and event counts are retained. Simulated
observations are not saved. The largest innovation batch has 500 by 3 by 3 by
15 float64 entries, approximately 0.54 MB before derived arrays.

Each event proportion has a pointwise Wilson 95% binomial interval. These bounds
measure Monte Carlo sampling error across generated replicates. They are not
mouse-effect intervals, do not quantify uncertainty about the true cage ICC and
are not simultaneous bounds across the entire simulation table. At 20,000
replicates, the standard error near probability 0.05 is about 0.00154.

Each scenario has a fixed PCG64 stream derived from the global seed and stable
scenario index. Innovations are drawn in replicate-major order with a fixed
number of draws per replicate; the unused tenth padded observation for group
two is never analyzed. Exact batch-partition invariance is tested under the
recorded NumPy implementation. The output records the seed, scenario stream,
library versions, configured and observed maximum batch sizes, batch count and
replicate count.

## Validation and interpretation

Quick tests use 128-replicate benchmarks and small deterministic arrays. They
check vectorized Welch calculations against independent sample-based SciPy
results, exact seeded batch invariance, BH zero-signal and obvious synthetic
signal controls, Wilson intervals against statsmodels, and the exact covariance
matrix implied by the Gaussian cluster mapping. Positive controls only verify
software orientation and rejection plumbing; they are not biological power
results.

The 20,000-replicate benchmark runs separately from quick unit tests during the
full pipeline. Its CSV is `results/tables/software_calibration.csv`, with a
labeled report in `results/reports/software_calibration.md`. Neither file mixes
simulations with observed immune measurements. No simulation figure is generated.

Nominal performance in one scenario cannot establish model validity for the
original study. Poor performance under an artificial dependence model cannot
establish that the original animals had that dependence. The benchmark cannot
recover missing virome inputs or substantiate a phageome-immune association.
