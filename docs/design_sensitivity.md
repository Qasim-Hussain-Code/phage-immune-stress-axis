# Sensitivity to ID structure and TNF-alpha scale

The source identifiers contain a structure worth examining alongside the
animal-level results. This appendix asks how the selected contrasts change
after conditioning on ID ranges, after giving putative control cages equal
weight, and after expressing TNF-alpha on a logarithmic scale. These analyses
were added after the initial reanalysis. They are post hoc sensitivities of the
same three endpoints, not new endpoint discoveries or replacements for the six
primary Welch comparisons.

## What the identifiers establish

The unchanged `FVT study II` workbook contains the following literal IDs. Each
range-defined stratum contains five source animals per treatment before
assay-specific missingness.

| Group | ID stratum A | ID stratum B |
|---|---|---|
| Control | `1.1`, `1.2`, `2.1`, `2.2`, `3` | `19.1`, `19.2`, `20.1`, `20.2`, `21` |
| Control Stress | `4`–`8` | `22`–`26` |
| FVT Stress | `9`–`13` | `27`–`31` |

The numerical partition is directly observable; its interpretation as a batch,
cohort or allocation block is not documented. Likewise, the common integer
prefixes of control IDs suggest six possible cages, with sizes
`2,2,1,2,2,1`, but do not verify cage membership. The labels `1`, `2`, `3`,
`19`, `20` and `21` below identify that proposed partition, not confirmed cage
allocations. The article states that controls were group housed and stressed
groups singly housed. That housing description motivates the sensitivity but
does not establish the ID key.

The [membership table](../results/tables/immune_design_membership.csv) retains
all 30 source animals, literal identifiers and workbook row coordinates, and
marks both interpretations as unverified. It assigns no putative control cage
to stressed animals and constructs no sequencing or pooled-sample crosswalk.
Missing assays remain attached to their source animals.

## Adjustment for the inferred ID strata

For each endpoint, ordinary least squares fits the additive model

```text
outcome = intercept + beta_S*I(Control Stress) + beta_F*I(FVT Stress)
          + beta_B*I(ID stratum B) + error
```

Control and stratum A are reference categories. The two treatment estimates
are `beta_S` and `beta_F - beta_S`. The model assumes a common additive stratum
effect, without a treatment-by-stratum interaction. It uses all observed values
of the selected endpoint and an HC3 heteroskedasticity-robust covariance:

```text
HC3 = (X'X)^-1 X' diag[e_i^2/(1-h_ii)^2] X (X'X)^-1
SE(c'beta) = sqrt(c' HC3 c)
95% interval = c'beta +/- t_(0.975,n-p)*SE(c'beta)
```

Here `p=4` for the stratum-adjusted model. The residual-degrees-of-freedom t
reference is a finite-sample approximation, not an exact guarantee of coverage
with these small groups. HC3 permits unequal outcome variances; it does not
correct within-cage dependence or verify allocation. A treatment-only HC3/t
model with `p=3` provides the same-method comparator. Its raw P values and
pointwise intervals are exported as reference columns without a comparator BH
adjustment. Comparing those two HC3 models isolates the addition of the stratum
term more directly than comparing the adjusted model with primary Welch.

The [adjusted contrasts](../results/tables/immune_block_adjusted.csv) have a
separate six-test BH family. Adding the inferred stratum term changes the
selected estimates little: the LY6Chi FVT difference is 1.5315 percentage
points, versus 1.5565 in treatment-only HC3. The Stress–Control estimate remains
-2.0340. This numerical stability does not establish that the strata are real
batches or remove the housing difference between stressed and unstressed mice.

The [within-stratum table](../results/tables/immune_within_block.csv) separately
reports the two raw-scale Welch contrasts in each of the two strata for all
three endpoints. Its 12 P values form their own BH family. All three FVT-versus-
Stress directions agree with their overall raw-mean direction in both strata.
The small stratum-specific samples make this a direction check rather than
independent replication or evidence of a common effect size.

## Conditional control-cage weighting

Under the proposed control partition, each observed putative cage mean receives
equal weight. For Control Stress minus Control, the estimate becomes

```text
mean(observed stressed animals) - mean(observed putative control-cage means)
```

This differs from giving every control animal equal weight when putative cages
have unequal sizes. Welch inference compares the singly housed stress-animal
values with those cage means, conditional on the proposed units being
independent. The six putative control cages therefore supply six control units,
not ten. Each cage mean uses its observed assays; an entirely missing cage assay
would remain missing rather than become zero. The
[unit table](../results/tables/immune_putative_cage_units.csv) records the source
members, observed members and means for each endpoint.

The [conditional contrasts](../results/tables/immune_putative_cage_means.csv)
retain the same six endpoint/contrast combinations in a separate BH family.
FVT Stress minus Control Stress still compares individual animals, because
both groups share the stated single-housing regime. For LY6Chi Stress–Control,
the equal-cage estimate is -1.7534 percentage points with P=0.1080 and q=0.1531,
compared with the primary animal-weighted estimate -2.0340 and q=0.03950.
The change reflects both a different weighting target and fewer conditional
control units. It cannot establish the correct sampling variance without a
verified cage key.

The [cage-omission table](../results/tables/immune_control_cage_omission.csv)
removes all source animals in each of the six proposed control cages in turn.
Every omission refits the original six animal-weighted Welch comparisons and
recomputes BH within that six-test family, producing 36 diagnostic rows. FVT
versus Stress uses the same observations in every refit, although its q value
can change when other P values in the family change. None of these omissions
is a source exclusion or a preferred result selected after seeing its P value.
For LY6Chi, omission of putative cage `2` reduces the Stress–Control difference
to -1.0326 percentage points; across all six omissions its q values range from
0.03073 to 0.09367. The full pattern is more informative than removing only the
two high controls that share that prefix.

## Raw versus log-scale TNF-alpha

Every observed TNF-alpha concentration is strictly positive. The sensitivity
retains every observed assay and takes its natural logarithm, without deleting
zeros, adding a pseudocount or imputing missing cells. If a nonpositive observed
value were encountered, this calculation would fail rather than change that
policy. Welch inference on the log values estimates a difference in mean logs;
exponentiating it gives the geometric-mean ratio. Exponentiating the pointwise
95% log interval gives the ratio interval.

The [TNF-alpha table](../results/tables/immune_tnfa_log_sensitivity.csv) retains
the raw-scale Welch estimate, interval and P value alongside each log result.
The log comparison targets a geometric-mean ratio, whereas primary raw-scale
Welch targets an arithmetic-mean difference in pg/mL. Neither is selected by a
normality test. The two log P values have their own BH adjustment:

| Ratio: first / second | Geometric-mean ratio | Pointwise 95% interval | Log-Welch P | Two-test BH q |
|---|---:|---|---:|---:|
| Control Stress / Control | 1.9517 | 0.85456 to 4.4575 | 0.09946 | 0.09946 |
| FVT Stress / Control Stress | 0.42958 | 0.18995 to 0.97150 | 0.04414 | 0.08827 |

The FVT ratio interval excludes one at its pointwise confidence level, while
the corresponding two-test q value exceeds 0.05. This is not a new confirmatory
positive result. It describes how the conclusion depends on scale and
multiplicity while preserving the primary raw-scale analysis.

## Scope and implementation

The sensitivity families remain separate: six stratum-adjusted HC3 tests,
12 within-stratum Welch tests, six conditional cage-unit tests, six tests within
each of six cage-omission refits, and two log-TNF tests. Their BH adjustments do
not correct for selecting these methods after the initial results or for every
possible analytical choice. All intervals are pointwise. No other phenotype
columns are screened, and the six primary mean contrasts remain unchanged.

[design_sensitivity.py](../src/pisa/design_sensitivity.py) implements the
calculations. Independent [tests](../tests/test_design_sensitivity.py) compare
HC3 coefficients, covariances and contrasts with statsmodels, Welch/log results
with SciPy, and each BH family with statsmodels. They also check literal source
membership, positivity, all six omissions and preservation of the primary
tables. These analyses cannot determine the actual cages, establish a viral
mechanism or supply the missing individual viral abundances and assay crosswalk.
