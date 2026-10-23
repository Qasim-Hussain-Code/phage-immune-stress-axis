# Results

The public source workbook supports an exploratory comparison of three immune outcomes in the Control, Control Stress and FVT Stress groups of Ritz et al. (2024). The outcomes were selected after reading the published findings, before calculating the present contrasts. All supplied observations were retained.

The blood samples used for the two flow outcomes were collected on study day 19, before forced swim and after 16 defeat days. Their values are percentages of parent population, and differences are percentage points rather than absolute cell counts. TNF-alpha was measured in unstimulated splenocyte culture supernatant, in pg/mL, from spleens collected on day 23 after 19 defeat days. These assays belong to the same source cohort but were not collected at the same time.

Each table reports unadjusted animal-level mean differences with pointwise 95% Welch intervals. The six P values form one Benjamini-Hochberg family. Sample sizes are available observations for that endpoint.

## LY6Chi monocytes

The stressed-control group had a lower basal LY6Chi monocyte proportion than Control. The FVT Stress group had a higher proportion than stressed controls. The two component comparisons describe the observed pattern more directly than a single restoration contrast.

| Endpoint | Contrast | n first/second | Mean difference | 95% CI | P | BH q |
|---|---|---:|---:|---|---:|---:|
| Basal LY6Chi monocyte proportion | Control Stress minus Control | 10/10 | -2.034 | -3.683 to -0.3848 | 0.01975 | 0.0395 |
| Basal LY6Chi monocyte proportion | FVT Stress minus Control Stress | 9/10 | 1.556 | 0.3893 to 2.724 | 0.01265 | 0.03794 |

## CD62L-positive monocytes

The CD62L-positive fraction of LY6Chi monocytes was higher in FVT Stress than in stressed controls. The stress-versus-Control difference was small and imprecise. This is an FVT-associated difference without an established preceding stress deficit, so it does not demonstrate reversal of such a deficit.

| Endpoint | Contrast | n first/second | Mean difference | 95% CI | P | BH q |
|---|---|---:|---:|---|---:|---:|
| Basal CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | 10/10 | -1.76 | -7.583 to 4.062 | 0.5265 | 0.5265 |
| Basal CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 9/10 | 15.87 | 7.726 to 24.02 | 0.0007999 | 0.004799 |

## Unstimulated splenocyte TNF-alpha

The stressed-control group had a higher mean TNF-alpha concentration, with substantial dispersion. The FVT-versus-stressed mean difference was negative, but both TNF-alpha intervals were wide and included zero. These estimates remain imprecise; they do not establish equivalence between groups. The measurement describes ex vivo culture output, not circulating plasma TNF-alpha.

| Endpoint | Contrast | n first/second | Mean difference | 95% CI | P | BH q |
|---|---|---:|---:|---|---:|---:|
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 8/9 | 67.54 | -26.18 to 161.3 | 0.1325 | 0.1591 |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | 9/8 | -74.13 | -167.8 to 19.51 | 0.1034 | 0.1551 |

## Dependence on the statistical comparison

The monocyte FVT comparison gives Welch P=0.012645 here and Tukey-Kramer P=0.106409 under the original three-group calculation, reproducing the published P=0.106. Both use the same observations and mean difference. Pooling the residual variance across all three groups and adjusting for three pairwise comparisons explains the different uncertainty estimates; additional source exclusions are unnecessary for this numerical reconciliation.

The [original-method reconstruction](../results/reports/original_method_replication.md) contains 24 records. It matches 9 of 9 selected caption-statistic checks and 17 of 18 combined caption and group-summary checks at published precision. One printed mean remains unresolved: FVT unstimulated TNF-alpha averages 27.8492778 pg/mL in the workbook, directly rounding to 27.8, while Table 1b prints 27.9. Source values and rounding tolerances were retained.

The planned contrast compares the stressed mean with the average of Control and FVT Stress. It does not jointly establish a stress effect and its reversal. Tukey intervals cover three pairs within each endpoint under a common-variance model. The reconstruction verifies compatible calculations, rather than re-executing the original SPSS session or reconstructing its full BH family.

## Sensitivity and missing observations

Each comparison was refitted after omitting each observed animal once. The ranges below describe influence on the mean difference; they are not confidence intervals. All six observed directions persisted, which does not establish stable significance. The Mann-Whitney comparisons describe distributional ordering and use their own six-test sensitivity BH family. They do not test the same raw-mean estimand.

| Endpoint | Contrast | Leave-one-animal-out difference range | Rank sensitivity P | Direction preserved |
|---|---|---|---:|---|
| Basal LY6Chi monocyte proportion | Control Stress minus Control | -2.26 to -1.534 | 0.003611 | True |
| Basal LY6Chi monocyte proportion | FVT Stress minus Control Stress | 1.213 to 1.812 | 0.007963 | True |
| Basal CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | -3.454 to -0.7602 | 0.3075 | True |
| Basal CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 14.15 to 17.72 | 0.00288 | True |
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 40.28 to 78.05 | 0.2766 | True |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | -84.64 to -46.87 | 0.005512 | True |

TNF-alpha illustrates the distinction between the mean and rank comparisons: the highly dispersed stressed group produces different results for those different features of the distribution. A rank result is not automatically a median shift. Neither method is selected as a replacement because it gives a smaller P value.

The n=9 FVT samples also differ by assay. Monocyte and CD62L measurements lack source ID 31, while TNF-alpha lacks ID 11. Equal sample counts therefore do not establish a common complete-case set. The workbook does not identify all upstream technical exclusions, detection thresholds or statistical exclusions.

Two descriptive checks were added after inspecting the earlier reanalysis. For the animals represented by workbook rows, allowing each missing percentage assay any well-defined value in [0,100] gives the following sharp support bounds. No value is imputed into the analysis.

| Percentage endpoint | FVT Stress minus Control Stress support bounds |
|---|---|
| Basal LY6Chi monocyte proportion | 1.16581 to 11.1658 percentage points |
| Basal CD62L-positive fraction of LY6Chi monocytes | 8.32259 to 18.3226 percentage points |

Both source-cohort mean directions remain positive under that support assumption. These are descriptive extrema, not confidence intervals or evidence of robust significance. An undefined parent population would invalidate the well-defined assay assumption. Missing TNF-alpha values have no identified finite upper support, so analogous finite bounds are unavailable.

For observed TNF-alpha, 8 first-greater and 0 tied comparisons among 72 cross-group pairs give empirical superiority 0.111111 and rank-biserial effect -0.777778 for FVT Stress versus Control Stress. Those pairs reuse 17 animals. They are not independent replicates. The full six-comparison tables and definitions are in the [descriptive robustness report](../results/reports/phenotype_robustness.md).

## Post hoc design and scale sensitivities

Literal IDs define two treatment-balanced ranges and six putative control cages with source sizes 2,2,1,2,2,1. Their interpretation as batches or cages is unverified. The following conditional comparisons give each observed control cage mean equal weight, while the singly housed stressed groups retain animals as units. This changes the control estimand as well as its uncertainty. The six comparisons have a separate exploratory BH family.

| Stress minus Control, conditional cage units | Mean difference | Pointwise 95% CI | Raw P | Sensitivity BH q |
|---|---:|---|---:|---:|
| Basal LY6Chi monocyte proportion | -1.753 | -4.023 to 0.5166 | 0.108 | 0.1531 |
| Basal CD62L-positive fraction of LY6Chi monocytes | -1.46 | -7.248 to 4.328 | 0.594 | 0.594 |
| Unstimulated splenocyte TNF-alpha | 68.57 | -25.14 to 162.3 | 0.1276 | 0.1531 |

The LY6Chi Stress–Control inference depends on the assumed independent unit. Every putative cage was also omitted in turn, retaining the six-test family in each diagnostic refit; LY6Chi Stress–Control q ranges from 0.03073 to 0.09367. These refits are not independent replications or source exclusions.

Treatment-plus-ID-stratum fits use HC3 covariance and finite-df t intervals, with treatment-only HC3 fits as like-for-like reference columns. 6 of 6 FVT endpoint-by-stratum differences preserve their overall raw direction. This is direction agreement, not replicated significance. Adjusted-model tests form a BH family of six; within-stratum tests form a separate family of twelve.

All observed TNF-alpha concentrations are positive. Log-Welch estimates below retain every observed value without a pseudocount and target geometric-mean ratios, rather than raw means or rank ordering. The two tests have their own exploratory BH family. Pointwise intervals do not incorporate that correction.

| TNF-alpha comparison | Geometric-mean ratio | Pointwise 95% CI | Raw P | Two-test BH q |
|---|---:|---|---:|---:|
| Control Stress / Control | 1.952 | 0.8546 to 4.457 | 0.09946 | 0.09946 |
| FVT Stress / Control Stress | 0.4296 | 0.19 to 0.9715 | 0.04414 | 0.08827 |

These post hoc checks quantify dependence on assumptions and scale. They do not replace the primary six-test family or establish confirmed effects. The [design sensitivity appendix](design_sensitivity.md) defines the models, assumptions and full membership, contrast, omission and log-scale tables.

## What the dataset leaves unanswered

The workbook contains 50 animal rows across two experiments. The sequencing archive contains 104 runs representing 104 specimens: 77 recipient bulk specimens, 8 enriched pools and 19 inocula. The initial-study captions imply 12 pool-by-time profiles. Pool membership across time remains unresolved, so these are not 12 verified animal trajectories.

The intended association between viral change and an immune phenotype requires individual longitudinal viral abundance profiles and a verified link to immune source animals. No processed viral profile was retrieved and none was matched to immune outcomes. Endpoint immune measurements could serve as outcomes for such an association if those viral inputs became available; they would still not measure within-mouse immune change or temporal immune stability. Bacterial adjustment also requires the missing matched bacterial profiles.

Heat-inactivated-FVT-labelled specimens also occur in the archive: 20 recipient bulk samples, ten inocula and two pools. Their immune outcomes and allocation key are not supplied by the retrieved workbook. This arm could strengthen the active-versus-inactivated comparison, while heating may also alter other transplant constituents. The 17 candidate complete Stress/FVT Before/After pairs require about 85.6 GB of compressed reads alone. The current limit combines missing processed inputs and validated linkage with a local reprocessing constraint. The [data requirements](data_requirements.md) describe what would make these routes usable.

Unstressed controls were group housed and both stressed groups singly housed. Thus the stress-versus-Control contrast includes different housing regimes, while FVT Stress versus Control Stress shares the stated regime. Unavailable allocation details limit the animal-level uncertainty estimates. The treatment comparisons describe selected immune phenotypes; they do not isolate a phage mechanism or establish immune resilience.

## Reproducibility

Validation: 219 tests collected, 213 executed, 6 skipped, 0 failures and 0 errors. [Executed records](../results/reports/validation_summary.json) and [statistical checks](statistical_validation.md) document the software verification. Synthetic fixtures are kept separate from biological observations. The separate [software calibration](../results/reports/software_calibration.md) used 20,000 replicates in each of 5 known zero-mean scenarios. Its Monte Carlo uncertainty is simulation uncertainty and does not calibrate the actual experiment under an unknown dependence structure.

Source: [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y). Observation-level source cells, exact estimates and missingness are retained in [results/tables](../results/tables) and [data/processed/immune_long.csv](../data/processed/immune_long.csv).
