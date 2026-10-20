# Novelty assessment

Assessment date: 2026-10-20. The completed contribution is a reproducible
availability and sample-linkage audit with a separate exploratory immune
reanalysis. No new association between measured phageome stability and immune
responses is reported.

## What the original study already reported

[Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y) studied chronic
stress, gut viral and bacterial profiles, fecal virome transplantation, selected
immune outcomes, behavior, and brain transcriptomics. Treatment-associated
immune differences and viral community alterations were already part of that
publication. Replotting or retesting those endpoints is not an independent
biological discovery.

The published design includes both pooled enriched viromes and individual
recipient bulk metagenomes. The latter were mapped to a viral catalog derived
from inocula. The paired summaries in the article therefore cannot be dismissed
as universally pooled. They also do not establish an available, independently
verified animal-level abundance and immune crosswalk.

## Intended gap and identifiability

The intended question was whether within-mouse preservation of the phageome
during stress is associated with immune phenotype after appropriate treatment
and bacterial adjustment. This requires repeated individual viral profiles,
legitimate animal identifiers, confidence-filtered viral features, and enough
matched immune observations. The audit retrieved no processed abundance matrix
or resolved cross-assay map. The archived script PDF references local inputs
that were not included in the inspected release. Zero processed viral profiles
could consequently be matched to immune outcomes in this analysis.

This is a missing-input result. It does not demonstrate biological absence of
an association or prove that the original experiment lacked useful individual
measurements. The immune endpoints also lack a verified prechronic-stress
baseline, so an endpoint cytokine contrast cannot be called immune temporal
stability.

## What the completed work adds

The project makes specimen type, pooling, unresolved identifiers, data
availability and excluded analyses machine-readable. It preserves the
distinction among pool-by-time profiles, individual recipient bulk samples,
inocula and individual immune outcomes. It implements checks that prevent
pooled or inoculum measurements from becoming recipient immune observations.

The immune reanalysis separates two component contrasts rather than assuming a
uniform restoration pattern. It reports pointwise intervals, one fixed six-test
BH family, observed sample counts, missingness, rank sensitivity and
leave-one-animal-out diagnostics. These are transparent methodological and
reporting contributions, not evidence that an ecological mechanism has been
identified. The endpoints were chosen after reading published results and
before computing these contrasts. The reanalysis is exploratory.

The subsequent descriptive robustness diagnostics were added after inspecting
that reanalysis. They show support-constrained ranges for missing percentage
assays in the source-row cohort and normalized ordering effects for the same
existing U statistics. They add no endpoints or hypothesis tests, establish no
new biological association, and do not make the selected comparisons
confirmatory. Conditional support bounds are not confidence intervals or a
claim of robust significance; cross-group pairs are not independent animal
replicates. Details are in [phenotype_robustness.md](phenotype_robustness.md).

An independent original-method reconstruction adds a numerical provenance
check. All nine selected caption t/P checks match, and 17 of 18 combined caption
and group-summary checks match. FVT TNF-alpha has source mean 27.8492778,
rounding directly to 27.8, versus 27.9 in the original table image; this remains
an explicit minor discrepancy. The original across-outcome BH family is not
claimed to be reproduced. A synthetic calibration module adds a conditional
software benchmark, not another biological result. Its four 20,000-replicate
scenarios completed with no observed study outcomes read by the generator.

## Contradictions retained

The FVT versus stressed-control monocyte comparison gives Welch P = 0.01265 and
BH q = 0.03794 in this reanalysis, whereas the original publication reports
Tukey pairwise P = 0.106. Reconstructing the original three-group pooled variance
and Tukey-Kramer calculation gives P = 0.106409 from the same source values.
These method choices explain the numerical difference; no extra deletions are
needed. Neither result is hidden or promoted as a correction of the original
research. Upstream missingness remains a separate limitation.

CD62L-positive monocytes have a strong FVT-associated difference, while the
stressed-versus-control contrast does not establish a preceding deficit. Calling
that pattern restoration would add a claim the component contrasts do not
support. For unstimulated splenocyte TNF-alpha, the FVT mean contrast is
inconclusive under Welch inference (q = 0.1551), while the rank sensitivity
family gives q = 0.01102. The methods examine different distributional features;
their disagreement is not resolved by selecting the smaller P value.

Exact estimates are in `results/tables/immune_contrasts.csv` and
`results/tables/immune_sensitivity.csv`.

## Subsequent literature and alternatives

The focused screen in [alternative_dataset_search.md](alternative_dataset_search.md)
reviewed stress-virome candidates through the search date, including mouse
restraint stress, rat chronic stress, human depression and piglet-derived FVT
into mice. No screened alternative was verified to supply the required relevant
stress design, public processed recipient viromes, measured immune outcomes and
explicit individual linkage. This was not a systematic review and does not
support a priority claim or proof that no suitable dataset exists.

The [expanded primary-data search](processed_data_search.md) adds 52 saved
evidence records without recovering the missing matrices or crosswalk.
A newer [prenatal-stress candidate](new_prenatal_stress_candidate.md) remains
unresolved after a [focused public-route follow-up](chen2026_public_route_followup.md)
of advertised publisher routes, institutional sources and exact-DOI preprint
lookups. The recovered responses did not establish recipient immune-assay
protocols, timing, a legitimate animal crosswalk or public processed paired
measurements. That candidate is not silently substituted or declared absent
on the basis of access failures.

The defensible conclusion is that this project identifies what the retrieved
public inputs can support and what would be needed for the proposed integrated
analysis. Biological novelty remains unestablished.
