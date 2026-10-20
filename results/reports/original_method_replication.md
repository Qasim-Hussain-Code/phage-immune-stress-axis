# Original-method immune replication

This separate verification uses the same three study II endpoints and every supplied observed value. The primary six-test Welch family is unchanged.

All three groups contribute to the pooled residual variance. Planned contrasts use Ctr, Ctr Stress and FVT Stress coefficients [-0.5, 1, -0.5]. Tukey-Kramer P values and simultaneous intervals use the finite residual degrees of freedom and all three pairwise comparisons per endpoint.

| Endpoint | Pooled MSE | Residual df | Planned t | Planned P | FVT minus stressed-control Tukey P |
|---|---:|---:|---:|---:|---:|
| ly6chi_monocytes | 2.566631092 | 26 | -2.866926809 | 0.008109467204 | 0.1064091013 |
| ly6chi_monocytes_cd62 | 50.30336452 | 26 | -3.180494077 | 0.003781051114 | 0.0001358531699 |
| tnfa_splenocyte_unstimulated | 3869.543697 | 23 | 2.679946857 | 0.01337308961 | 0.05568679863 |

Published sample counts/means or caption statistics checked: 18. Matches at published precision: 17. Mismatches: 1. The CSV distinguishes rounded equalities, reported inequalities and statistics not individually reported.

Caption-statistic matches: 9 of 9. Source group count/mean matches: 8 of 9. The FVT Stress TNF-alpha source mean is 27.8492777778 pg/mL, which rounds directly to 27.8 at one decimal; Extended Data Table 1b visibly prints 27.9. This comparison is retained without a wider rounding tolerance. The caption-statistic matches are recorded independently of the printed-mean comparison.

The monocyte FVT Tukey result reproduces the published 0.106, using the same source observations that give a smaller Welch P value. Pooled variance across all three groups and Tukey multiplicity explain this difference. Additional source exclusions are unnecessary for this numerical reconciliation. Upstream exclusions, censoring thresholds and omitted values remain unavailable.

The paper calls its contrasts orthogonal. This single planned coefficient vector can be reconstructed, but orthogonality of a full contrast set cannot be claimed from a label. For independent unequal-size means, covariance of contrasts c and d is MSE times sum(c_i*d_i/n_i). An unweighted coefficient dot product of zero is not sufficient when group sizes differ, and the complete SPSS contrast syntax is unavailable.

Planned-contrast intervals are pointwise. Tukey intervals are simultaneous within one endpoint's three-pair family, not across endpoints. Published planned BH q values in the CSV are explicitly reference values; the original complete BH family is unresolved and no reconstructed original q is claimed.

Numerical agreement does not establish homoscedasticity, normality, independent animals or a viral mechanism. Cage allocation is missing; TNF-alpha variances are strongly unequal. CD62L-positive monocytes need not show reversal of a preceding stress deficit. All original-method output is a separate provenance check, not a preferred result selected for significance.

Source: [Ritz et al. (2024)](https://www.nature.com/articles/s41564-023-01564-y). Detailed independent review: docs/original_analysis_review.md.
