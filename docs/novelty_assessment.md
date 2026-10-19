# Novelty assessment

Assessment date: 2026-10-20. The completed contribution is a reproducible
availability and sample-linkage audit with a separate exploratory immune
reanalysis. No new association between measured phageome stability and immune
responses is reported.

## What the original study already established

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

## Contradictions retained

The FVT versus stressed-control monocyte comparison gives Welch P = 0.01265 and
BH q = 0.03794 in this reanalysis, whereas the original publication reports
Tukey pairwise P = 0.106. These are different tests and correction schemes.
Upstream assay exclusions and the original analysis population are not fully
resolved. The difference must remain visible; it does not establish that the
published result was wrong.

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

The defensible conclusion is that this project identifies what the retrieved
public inputs can support and what would be needed for the proposed integrated
analysis. Biological novelty remains unestablished.
