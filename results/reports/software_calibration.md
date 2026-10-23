# Synthetic software calibration

Every result on this page has purpose synthetic_not_biological. No experimental outcomes, source mouse IDs, real cage assignments or fitted clinical parameters were read. These simulations do not estimate biological power or validate an unknown cage structure.

Seed: 20261020. Replicates per scenario: 20000, with an absolute bound of 20,000. Five scenarios use at most 500 replicates per batch, with an absolute batch-size bound of 500. Three independent synthetic endpoints use group sizes 10,10,9 and two overlapping adjacent Welch contrasts each. Every true mean contrast is zero.

| Synthetic assumption | All-null BH family any rejection | Wilson 95% Monte Carlo interval |
|---|---:|---|
| independent_gaussian_equal_variance | 0.04620 | 0.04338 to 0.04920 |
| independent_gaussian_unequal_variance | 0.04795 | 0.04507 to 0.05100 |
| independent_centered_lognormal | 0.01150 | 0.01011 to 0.01307 |
| artificial_gaussian_clusters_icc_0_5 | 0.16495 | 0.15987 to 0.17016 |
| hypothetical_controls_only_gaussian_clusters_icc_0_5 | 0.06890 | 0.06547 to 0.07249 |

Under the complete null, FDR equals the probability of at least one rejection (FWER). The nominal level is 0.05. The six tests share the middle synthetic group within an endpoint, so they are generated jointly rather than treated as independent P values.

The CSV also records per-contrast unadjusted false-positive probability and pointwise 95% Welch interval coverage. These are complementary zero-null events, apart from exact numerical boundaries. Tukey coverage concerns all three pairwise mean intervals within one synthetic endpoint, using the original common-variance formula with finite df=26. It does not adjust across endpoints.

Wilson bounds measure binomial Monte Carlo error across independent generated replicates. They are pointwise intervals for software performance probabilities, not confidence intervals for any mouse effect and not simultaneous bounds across all simulation summaries.

The artificial cluster scenario assigns five generic Gaussian random-intercept clusters to every group, with ICC 0.5, five pairs in groups 0 and 1 and four pairs plus one singleton in group 2. This is a deliberate assumption stress test. It is not inferred from the source experiment; in particular, the original stressed groups were singly housed, and no actual cage IDs are reconstructed. Endpoint-specific cluster effects are independent.

The additional controls-only scenario instead gives group 0 six hypothetical clusters of sizes 2,2,1,2,2,1, with ICC 0.5, while groups 1 and 2 remain independent. The layout is motivated by integer portions of control IDs and the stated group housing; those IDs are not confirmed cages, and the ICC is imposed rather than estimated. The code reads neither source IDs nor biological outcomes. This scenario was added after the earlier four-model benchmark, without changing its streams.

Control-only dependence directly affects the group-1-minus-group-0 Welch contrast. The group-2-minus-group-1 unadjusted Welch calculation still uses only independent Gaussian groups; its model is unchanged. The six-test BH event can nevertheless change because its family also includes the control contrasts. All three groups enter the pooled variance for Tukey intervals, so their coverage must be evaluated separately.

Equal means are preserved in every scenario. The centered lognormal scenario subtracts its known expectation exp(0.5), without estimating a center from observed study outcomes. No scenario or parameter was selected to match a biological result.

A scenario has its own fixed PCG64 stream derived from the recorded seed and scenario index. The controls-only scenario is appended at index 4; indices 0 through 3 and their innovation draws are unchanged. Replicate-major draws preserve results across batch partitions under the recorded NumPy version. The unchanged CSV schema records 16 performance summaries per scenario, hence 80 rows for five models. Only count accumulators and batches of at most 500 are retained; raw simulated observations are not written. Full benchmark execution is separate from short synthetic unit checks.

This benchmark shows how the software behaves under stated generating assumptions. It cannot establish whether those assumptions hold for the original experiment, remedy missing phage data, or turn endpoint phenotypes into longitudinal immune stability.
