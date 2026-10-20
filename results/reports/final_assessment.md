# Results

This is a public-data feasibility study with a separate exploratory reanalysis of immune source data. It does not test a measured phageome stability versus immune-response relationship.

The source workbook contains 50 animal rows across two experiments. The principal archive contains 104 sequencing runs representing 104 specimens: 77 individual recipient bulk specimens, 8 enriched pools and 19 inocula. The initial paper captions imply 12 pool-by-time enriched profiles across group and time; these must not be added to the second experiment as longitudinal animals. No processed viral abundance profile was retrieved and zero are matched to immune outcomes. This is missing evidence, not a biological null result.

## Separate immune contrasts

Three endpoints and two contrasts were selected after reading the published paper and before calculating the present contrasts. These are exploratory unadjusted animal-level summaries. All estimates use untransformed source units. Extended Data Table 1c identifies the two selected flow outcomes as basal (blood collected on study day 19 before forced swim, after 16 defeat days), percent of parent population; their differences are percentage points. Table 1b identifies unstimulated splenocyte TNF-alpha as pg/mL, from terminal day-23 spleen collection after 19 defeat sessions. These source-linked assays are not contemporaneous measurements. Intervals are pointwise 95% Welch intervals. P values have a six-test BH correction. Housing differs for the stress-control contrast: unstressed controls were group housed and stressed groups singly housed. Both groups in the FVT-stressed comparison share the stated single-housing regime. Incomplete assay measurements, unresolved detection censoring and unavailable allocation details still limit interpretation.

| Endpoint | Contrast | n first/second | Mean difference | 95% CI | P | BH q |
|---|---|---:|---:|---|---:|---:|
| Basal LY6Chi monocyte proportion | Control Stress minus Control | 10/10 | -2.034 | -3.683 to -0.3848 | 0.01975 | 0.0395 |
| Basal LY6Chi monocyte proportion | FVT Stress minus Control Stress | 9/10 | 1.556 | 0.3893 to 2.724 | 0.01265 | 0.03794 |
| Basal CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | 10/10 | -1.76 | -7.583 to 4.062 | 0.5265 | 0.5265 |
| Basal CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 9/10 | 15.87 | 7.726 to 24.02 | 0.0007999 | 0.004799 |
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 8/9 | 67.54 | -26.18 to 161.3 | 0.1325 | 0.1591 |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | 9/8 | -74.13 | -167.8 to 19.51 | 0.1034 | 0.1551 |

## Robustness and interpretation

No observed animal was deleted as an outlier. Each contrast was recomputed after omitting each observed animal once. Rank-based comparisons are distributional sensitivity checks, with their own six-comparison BH family; they do not estimate the same mean difference. The intervals below are ranges of refitted effects, not confidence intervals.

| Endpoint | Contrast | Leave-one-animal-out difference range | Rank sensitivity P | Direction preserved |
|---|---|---|---:|---|
| Basal LY6Chi monocyte proportion | Control Stress minus Control | -2.26 to -1.534 | 0.003611 | True |
| Basal LY6Chi monocyte proportion | FVT Stress minus Control Stress | 1.213 to 1.812 | 0.007963 | True |
| Basal CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | -3.454 to -0.7602 | 0.3075 | True |
| Basal CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 14.15 to 17.72 | 0.00288 | True |
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 40.28 to 78.05 | 0.2766 | True |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | -84.64 to -46.87 | 0.005512 | True |

Group differences in immune source data do not imply that a phage or viral feature caused those differences. The original article already reports related treatment-associated immune results. Different endpoints and contrasts need not support a uniform restoration interpretation. Nonsignificant contrasts are not evidence of equivalence or absence of an immune effect.

CD62L-positive monocyte fraction is higher with FVT than stressed control, while its stress-control contrast is imprecise. This is not demonstrated reversal of a stress-induced deficit. TNF-alpha has a highly dispersed stressed group: its FVT comparison differs between raw-mean Welch and rank-based tests. These estimate different aspects of the distribution; neither result is hidden. The monocyte FVT comparison differs from the article's Tukey pairwise P=0.106. The original three-group pooled residual variance and Tukey adjustment differ from the present unequal-variance pairwise test and six-test BH family. Those method choices explain the numerical difference without requiring different source observations. This comparison does not identify an error in the original calculation. Upstream censoring and exclusions remain a separate general limitation.

Endpoint-specific n=9 FVT groups contain different animals: monocyte and CD62L outcomes lack source ID 31, while TNF-alpha lacks ID 11. Equal sample counts do not establish matched endpoints.

No viral composition, temporal stability, reference deviation, bacterial-adjusted association or phage-host relationship was estimated. Original paired bulk-derived viral profiles could support additional work if their processed matrix, confidence annotations and verified animal map become available. Endpoint immune measurements would still not measure chronic-stress immune stability.

## Validation

The executed validation suite ran 135 tests with 0 failures and 0 errors. Independent checks cover Welch inference, BH adjustment, community-distance identities and linkage invariants. Synthetic fixtures are software tests only.

Source: [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y). Exact values and missingness are in results/tables; raw observations retain source-cell locations.

## Original-method reconstruction

A separate reconstruction table contains 24 records: `results/tables/original_method_replication.csv`. It is distinct from the fixed Welch family. Its presence does not imply that every original outcome or the original full multiplicity family was reconstructed. 17 of 18 printed reference checks agree, including all 9 selected caption-statistic checks.

The three-group pooled-variance calculation reproduces the selected planned t statistics and Tukey comparisons at the published precision. In particular, the monocyte FVT comparison is P=0.106409 under Tukey-Kramer, explaining the published P=0.106 without additional exclusions. One printed group mean remains discrepant: unstimulated FVT TNF-alpha averages 27.8492778 pg/mL in the workbook, which rounds directly to 27.8, versus 27.9 in Table 1b. The discrepancy is retained; no tolerance was widened and no value changed.

The planned contrast compares the stressed mean with the average of Control and FVT Stress. It does not jointly establish a stress effect and its reversal. Tukey intervals cover three pairwise comparisons within one endpoint under a common-variance model; the original across-outcome BH family remains unreconstructed.

## Descriptive missingness and rank effects

These diagnostics were added after inspecting the earlier reanalysis. They add no hypothesis tests and leave the primary six-test family unchanged. Bounds target the animals represented by workbook rows, conditional on missing percentage assays having well-defined values anywhere in [0,100]. They are descriptive extrema, not confidence intervals or evidence of robust statistical significance.

| Percentage endpoint | FVT Stress minus Control Stress support bounds |
|---|---|
| Basal LY6Chi monocyte proportion | 1.16581 to 11.1658 percentage points |
| Basal CD62L-positive fraction of LY6Chi monocytes | 8.32259 to 18.3226 percentage points |

Under those support assumptions, neither missing percentage value can reverse the source-cohort FVT-versus-stressed mean direction. An undefined parent population would violate the well-defined-assay assumption. TNF-alpha has missing values and no identified finite upper support, so analogous finite bounds are unavailable.

For observed TNF-alpha, 8 first-greater and 0 tied comparisons among 72 cross-group pairs give empirical superiority 0.111111 and rank-biserial effect -0.777778 for FVT Stress versus Control Stress. The pairs reuse 17 observed animals; they are not independent replicates. See `results/reports/phenotype_robustness.md` and the complete six-row bounds/rank tables.

## Conditional software calibration

A separate synthetic benchmark completed 20,000 replicates in each of four known zero-mean scenarios, evaluating variance heterogeneity, skew and artificial clustering. It reads no biological observations. Its Monte Carlo uncertainty is simulation uncertainty, not mouse-level uncertainty. See `results/reports/software_calibration.md` and `results/tables/software_calibration.csv`. These checks cannot infer missing cage assignments or calibrate the actual experiment under an unknown dependence structure.

## Invocation status

Invocation: 20261020T123200773661Z_38916. Mode: full. Status: completed_restricted_analysis.
0 stages executed and 10 stages resumed after verifying their declared outputs and upstream dependencies.
All selected restricted-workflow stages completed or were verified from cache. Scientifically excluded analyses remain exclusions.
Validation (verified cached stage result): 135 tests, 0 failures, 0 errors, 6 skipped.
Prior visual review dated 2026-10-20T06:23:59.007316+00:00 matches the current bytes of 5 PDF files. This is not a new visual review by this invocation.

Publication status is documented separately in `docs/publication_status.md`; executing this pipeline does not establish a GitHub publication.
Researcher and sole project author: Qasim Hussain. No causal phage mechanism or stability-immune association is established by this restricted analysis.
