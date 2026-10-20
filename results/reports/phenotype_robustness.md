# Descriptive phenotype robustness

These descriptive diagnostics were added after inspecting the earlier reanalysis. They use the existing three selected endpoints and two contrasts, add no P values, adjusted P values, confidence intervals or hypothesis tests, and do not change the primary or sensitivity tables.

## Missing-outcome support bounds

The denominator is the source-row cohort, including rows with missing assays; it is not an inferred complete randomized cohort. For percentages, each missing assay is assumed to have a well-defined value anywhere in [0,100]. Each endpoint of the bound is attainable under that support, with no imputed value adopted as data. Bounds describe a finite source-row mean difference, not population uncertainty, statistical significance or a causal effect.

| Endpoint | Contrast | Source animals first / second | Missing first / second | Lower difference | Upper difference | Status |
|---|---|---:|---:|---:|---:|---|
| Basal LY6Chi monocyte proportion | Control Stress minus Control | 10 / 10 | 0 / 0 | -2.034038 | -2.034038 | complete source rows |
| Basal LY6Chi monocyte proportion | FVT Stress minus Control Stress | 10 / 10 | 1 / 0 | 1.1658098 | 11.16581 | finite-support bounds |
| Basal CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | 10 / 10 | 0 / 0 | -1.760441 | -1.760441 | complete source rows |
| Basal CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 10 / 10 | 1 / 0 | 8.322593 | 18.322593 | finite-support bounds |
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 10 / 10 | 2 / 1 | unavailable | unavailable | finite bounds unavailable |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | 10 / 10 | 1 / 2 | unavailable | unavailable | finite bounds unavailable |

Percentage differences are percentage points. TNF-alpha is in pg/mL; missing values and no identified finite upper support prevent finite bounds. No detection limit, zero substitution or missing-at-random assumption is supplied. Leave-one-out diagnostics omit observed values and answer a different question.

## Existing rank effects

Average-rank U and direct cross-animal pair enumeration agree, and both reproduce each existing sensitivity U. Empirical superiority equals (first-greater pairs + half tied pairs) / cross-group pairs; the rank-biserial effect is twice this probability minus one. These describe observed distributions, not raw means or automatically a common median shift. Cross-group pairs reuse animals and are not independent replicates.

| Endpoint | Contrast | Observed animals first / second | First greater / tied / first less pairs | Empirical superiority | Rank-biserial effect |
|---|---|---:|---:|---:|---:|
| Basal LY6Chi monocyte proportion | Control Stress minus Control | 10 / 10 | 11 / 0 / 89 | 0.11 | -0.78 |
| Basal LY6Chi monocyte proportion | FVT Stress minus Control Stress | 9 / 10 | 78 / 0 / 12 | 0.86666667 | 0.73333333 |
| Basal CD62L-positive fraction of LY6Chi monocytes | Control Stress minus Control | 10 / 10 | 36 / 0 / 64 | 0.36 | -0.28 |
| Basal CD62L-positive fraction of LY6Chi monocytes | FVT Stress minus Control Stress | 9 / 10 | 82 / 0 / 8 | 0.91111111 | 0.82222222 |
| Unstimulated splenocyte TNF-alpha | Control Stress minus Control | 8 / 9 | 48 / 0 / 24 | 0.66666667 | 0.33333333 |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Control Stress | 9 / 8 | 8 / 0 / 64 | 0.11111111 | -0.77777778 |

Unknown cage allocation, upstream exclusions and censoring remain unresolved. These descriptive checks cannot supply missing viral measurements, establish independence or isolate a phage mechanism. Methods: docs/phenotype_robustness.md. Source-cell provenance remains in data/processed/immune_long.csv.
