# Results

This is a public-data feasibility study with a separate exploratory reanalysis of immune source data. It does not test a measured phageome stability versus immune-response relationship.

The source workbook contains 50 animal rows across two experiments. The principal archive contains 104 sequencing specimens: 77 individual recipient bulk metagenomes, 8 enriched pools and 19 inocula. The initial paper captions imply 12 pool-by-time enriched profiles across group and time; these must not be added to the second experiment as longitudinal animals. No processed viral abundance profile was retrieved and zero are matched to immune outcomes. This is missing evidence, not a biological null result.

## Separate immune contrasts

Three endpoints and two contrasts were selected after reading the published paper and before calculating the present contrasts. These are exploratory unadjusted animal-level summaries. All estimates use untransformed source units. Extended Data Table 1c identifies the two selected flow outcomes as basal (before forced swim, after chronic stress), percent of parent population; their differences are percentage points. Table 1b identifies unstimulated splenocyte TNF-alpha as pg/mL. Intervals are pointwise 95% Welch intervals. P values have a six-test BH correction. Unknown cage allocation, incomplete terminal measurements and unresolved detection censoring limit inferential calibration.

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

CD62L-positive monocyte fraction is higher with FVT than stressed control, while its stress-control contrast is imprecise. This is not demonstrated reversal of a stress-induced deficit. TNF-alpha has a highly dispersed stressed group: its FVT comparison differs between raw-mean Welch and rank-based tests. These estimate different aspects of the distribution; neither result is hidden. The monocyte FVT comparison uses Welch P=0.01265 here, whereas the article Fig. 4 reports Tukey pairwise P=0.106. The present six-test family, unequal-variance tests, retained workbook observations and upstream exclusions differ from the original orthogonal-contrast/Tukey analysis. This numerical difference is method sensitivity, not independent replication or evidence that the original calculation was wrong.

Endpoint-specific n=9 FVT groups contain different animals: monocyte and CD62L outcomes lack source ID 31, while TNF-alpha lacks ID 11. Equal sample counts do not establish matched endpoints.

No viral composition, temporal stability, reference deviation, bacterial-adjusted association or phage-host relationship was estimated. Original paired bulk-derived viral profiles could support additional work if their processed matrix, confidence annotations and verified animal map become available. Endpoint immune measurements would still not measure chronic-stress immune stability.

## Validation

The executed validation suite ran 25 tests with 0 failures and 0 errors. Independent checks cover Welch inference, BH adjustment, community-distance identities and linkage invariants. Synthetic fixtures are software tests only.

Source: [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y). Exact values and missingness are in results/tables; raw observations retain source-cell locations.
