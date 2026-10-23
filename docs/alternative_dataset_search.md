# Focused alternative dataset search

Search date: 2026-10-20. This screen was initiated because the primary study's
initial viromes are pooled and the archived scripts reference processed matrices
not supplied in that archive. It is a focused feasibility screen, not a
systematic review or proof that no suitable dataset exists.

The subsequent [full-methods and actual-supplement audit](alternative_dataset_audit.md)
verifies Choi, Duan and Li in more detail and adds the unresolved Chen 2026
prenatal-stress lead. It also records rejected content-mismatched mirror files,
correct recovered supplements, and tracked source provenance. Use that audit
for the current file-availability assessment.

## Inclusion criteria

A replacement would need a relevant stress context, individual study-animal
fecal viromes, measured immune outcomes, explicit animal identifiers linking the
assays, and accessible processed data small enough for the resource budget.
Repeated individual viromes would additionally be required for temporal
stability. In an FVT experiment, the viral profiles must come from recipient
animals; an inoculum profile cannot substitute for them. A study with only
metabolites or behavior cannot substitute for measured immune phenotypes.

## Queries

Public web search and primary-paper inspection used these focused queries:

- `mouse stress gut virome cytokines longitudinal virome dataset processed data`
- `stress bacteriophage virome immune mice dataset cytokine fecal virome transplantation public data`
- `"Fecal virome transplantation alleviates weaning stress" data availability`
- `"chronic stress" "virome" "cytokines" -Ritz -associated -s41564-023-01564-y`
- `"virome" "stress" "processed" "mice" cytokines`
- `"gut virome" "stress" "data availability" rats immune`
- `"Gulf War" "virome" "Mendeley"`

## Candidate decisions

| Candidate | Relevant evidence | Decision |
|---|---|---|
| [Choi et al. 2026, Scientific Reports, doi:10.1038/s41598-026-49647-0](https://www.nature.com/articles/s41598-026-49647-0) | Piglet material collected before and after weaning was pooled for FVT into mice; mouse colonic inflammatory-gene and corticosterone measurements are described. Raw metagenomes are reported under `PRJNA1250699`; other data are available on request. | Relevant stress context, but no public processed, individually linked recipient virome and immune table was verified. Do not assign pooled donor measurements to recipients. Not selected. |
| [Duan et al. 2022, Frontiers in Microbiology, doi:10.3389/fmicb.2022.1046894](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2022.1046894/full) | Chronic restraint stress in mice with fecal viral metagenomics, behavior, and targeted neurotransmitter metabolomics; accession `PRJNA877780`. | The inspected methods describe metabolites rather than a directly measured immune endpoint. No eligible matched immune table was verified. Not selected. |
| [Li et al. 2023, Frontiers in Microbiology, doi:10.3389/fmicb.2023.1132403](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2023.1132403/full) | Rat chronic unpredictable mild stress, antidepressant treatments, and gut DNA virome composition/function. | Relevant stress model but different species and no eligible public linked cytokine or immune-cell dataset verified in the inspected paper. Not selected. |
| [Gut viral metagenomics identifies viral signatures and their role in depression, 2025, doi:10.3389/fmicb.2025.1573851](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2025.1573851/full) | Human depression virome study; deposited data listed as `PRJCA046198` / `CRA030037`. | Human observational depression differs from experimentally imposed mouse stress; no eligible directly measured matched immune data verified. Not selected. |
| [Saha et al. 2021, Brain Sciences, doi:10.3390/brainsci11070905](https://www.mdpi.com/2076-3425/11/7/905) | Chemical-exposure Gulf War illness model, virome and IL-6; [Mendeley record doi:10.17632/sn7tvhs84d.1](https://data.mendeley.com/datasets/sn7tvhs84d) describes correlation analyses; sequencing reported under `PRJNA731934`. | Candidate with inflammatory measurements, but chemical-exposure illness is a different biological condition. Processed correlation outputs do not by themselves establish access to the individual abundance/immune linkage. No condition switch made. |

The screen also located arthritis, Crohn's disease, and diet-induced metabolic
syndrome FVT studies. These conditions were not substituted for psychosocial
stress. A more easily available inflammatory association would not answer the
specified question.

The Choi accession description above follows the article's data statement.
The [later supplement audit](alternative_dataset_audit.md) found 46 ENA records
labelled AMPLICON and did not verify a deposited recipient virome.

## Consequence

No screened alternative was verified to satisfy the full combination of a
relevant stress design, public processed individual study-animal viromes,
measured immune phenotypes, and explicit individual linkage. This is an availability and
verification conclusion, not a biological null result. The project retains the
primary study's supported source-data and design analyses. Any future release
of processed virome matrices and a legitimate animal crosswalk must trigger a
new linkage audit before association analysis is enabled.

No raw read archives, viral reference databases, or candidate alternative data
packages were downloaded for this screen. No authors were contacted.

The no-package-download statement describes this initial screen. The
[later methods and supplement audit](alternative_dataset_audit.md) retrieved
and inspected candidate supplements; its file-level assessments supersede
this screen.

## Subsequent bounded checks

The initial focused screen above is supplemented by the
[expanded primary-data search](processed_data_search.md), which records 52
saved evidence objects without recovering the Ritz study's processed matrices
or cross-assay map. Those are retrieval records, not 52 independent biological
datasets or evidence that every possible public location was checked.

A relevant newer [prenatal-stress candidate](new_prenatal_stress_candidate.md)
remains unresolved. Its abstract and accessible publisher preview mention
virome/immune work and a request-based availability route, but do not verify
public processed recipient profiles with individually linked immune outcomes.
Access failures do not establish absence or scientific ineligibility. No data
from that candidate enter the present biological analysis, and the existing
feasibility gate is unchanged.
