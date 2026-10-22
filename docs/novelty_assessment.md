# Contribution and scope

## Relationship to the original experiment

[Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y) reported the
stress experiment, fecal virome transplantation, community profiles, immune
phenotypes, behavior and brain transcriptomics. The animals and measurements
analysed here come from that work. Treatment-associated immune differences are
therefore findings of the original experiment, rather than new observations
produced by this repository.

The proposed ecological extension asks whether within-mouse viral change is
associated with an immune endpoint. That question requires repeated recipient
viral profiles linked to individual immune measurements. The inspected public
releases supplied the phenotype workbook and sequencing metadata, but not the
processed community tables and verified animal map. The ecological extension
remains unestimated.

## What this reanalysis contributes

The completed work makes three aspects of the source data easier to assess.

First, it reconciles the biological units. Fifty workbook animal rows, 104
deposited specimens, enriched pools and donor inocula describe different
objects. The [linkage assessment](data_feasibility.md) records which specimens
could support an individual analysis and where values or identifiers are
missing. It preserves the original paper's individual bulk-metagenome route
alongside its pooled viromes.

Second, it separates the two treatment comparisons for each selected immune
outcome. The resulting patterns differ: LY6Chi proportions are lower with
stress and higher with FVT; CD62L-positive fractions are higher with FVT
without an established preceding stress deficit; and the TNF-alpha raw-mean
contrast remains imprecise. Reporting those component estimates makes the
scope of a restoration interpretation visible. Endpoint selection followed
reading the published findings, so these remain exploratory comparisons.

Third, it explains method dependence using the same observations. The
LY6Chi FVT comparison has Welch P = 0.01265 and reconstructed Tukey–Kramer
P = 0.106409. Variance pooling and multiplicity account for that difference.
The reconstruction matches all nine selected caption statistics and 17 of 18
combined caption and group-summary checks. One small printed TNF-alpha mean
discrepancy remains unresolved. This is a numerical reconciliation of selected
results, not a rerun of the original SPSS analysis or a reconstruction of its
complete across-outcome BH family.

The [sensitivity analyses](phenotype_robustness.md) retain single-animal
influence, conditional missing-percentage bounds and empirical ordering
effects. They describe different sources of uncertainty and add no biological
observations. The separate synthetic calibration evaluates the software under
specified generating models; it does not estimate the original cage structure.

## The remaining scientific question

The present immune comparisons cannot connect treatment differences to a
particular viral feature or establish a phage-mediated gut–brain mechanism.
A processed recipient viral matrix, its quality and classification annotations,
and an explicit immune-animal crosswalk would permit the intended endpoint
association to be assessed. Matched bacterial measurements would be required
for bacterial adjustment. Within-mouse immune change would additionally require
appropriate repeated immune assays.

The dated [processed-data search](processed_data_search.md) and
[alternative-study assessment](alternative_dataset_audit.md) delimit what was
checked on 20 October 2026. They did not verify a replacement dataset. The
[Chen prenatal-stress candidate](new_prenatal_stress_candidate.md) remains
unresolved. These searches support an account of available evidence, without
establishing a literature-wide absence or a priority claim.
