# Primary article experimental-design audit

Audit date: 2026-10-20. This is an independent reading of the article XML, not a claim that the referenced processed matrices have been retrieved. Original authors: Ritz NL, Draper LA, Bastiaanssen TFS, et al. (2024), Nature Microbiology 9, 359-376, DOI [10.1038/s41564-023-01564-y](https://doi.org/10.1038/s41564-023-01564-y).

The frozen XML is `data/raw/article.xml`, retrieved from [Europe PMC full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10847049/fullTextXML). Article section identifiers below allow the evidence to be checked without relying on web search snippets. The article is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/). This document paraphrases the methods and separates the audit's interpretation from the authors' reported results.

## Experiments and biological units

| Component | Experimental units and timing | Consequence for reanalysis |
|---|---|---|
| Experiment 1 | Twenty male C57BL/6J mice, randomized to Ctr or Stress, ten per group. Twenty days of psychosocial stress, including defeat and overcrowding. SIT day 21, FST day 22, tissue collection day 23. | Keep this cohort separate from the FVT experiment. Stress includes a housing/cage component. |
| Experiment 1 enriched virome | Fecal material combined from 3-4 mice per pool. Figure 1 reports three profiles per group. | The virome unit is a pool. Twenty immune measurements do not provide twenty independent virome observations. |
| Experiment 2 | Thirty randomized male C57BL/6J mice: Ctr, Ctr Stress, FVT Stress, ten allocated per group. Nineteen defeat sessions over 22 study days. Vehicle gavage in the first two groups; autochthonous prestress FVT in the third. | This is a three-arm treatment design, with no unstressed FVT arm. |
| Experiment 2 enriched recipient virome | Methods explicitly combine one fecal sample from each mouse into a group pool. | These enriched profiles cannot be assigned to individual recipients. |
| Experiment 2 inocula | Figure 3 reports nine individual FVT preparations. | Inocula describe viral exposure, not the recipients' post-treatment intestinal community. |
| Experiment 2 bulk metagenomics | Individual fecal DNA was sequenced. Section Sec27 describes mapping each bulk sample to the gavage-derived viral-contig catalog. Extended Data Figure 4 reports pre/post bacteriome and virome summaries, with Ctr 10, Ctr Stress 8, FVT Stress 9. | An individual longitudinal *bulk-read viral signal* may exist separately from pooled enriched viromes. This route requires the actual matrix, contig annotation, mouse identifiers, and assay bridge. Figure captions alone do not establish those links. |

Evidence: XML sections Sec10, Sec11, Sec13, Sec14, Sec23, Sec24, Sec27; Figure 1, Figure 3 and Extended Data Figure 4 (XML Fig9).

The initial-cohort prose reports ten control and nine stressed contributors, whereas Figure 1 virome captions report ten per group. Preserve this inconsistency until sample metadata resolves it. Do not silently choose one count.

Extended Data Figure 2b,d (XML Fig7) explicitly describes both Pre and Post virome comparisons and gives three pools per group. Combining two groups, two times and three pools implies twelve published pool-by-time profiles. This is a reconstruction from the figure caption, not verification of twelve deposited sequencing accessions or twelve independent longitudinal biological units. Pool membership and its consistency across time remain unresolved. The same caption also describes pooled prestress bacteriome controls, so individual longitudinal bacteriome completeness in the initial cohort must not be assumed.

## Immune assay scope

Experiment 1 Figure 1 reports ten observations per group for ConA-stimulated splenocyte IL-6 and IL-10. These are individual immune measurements paired with group-pooled viromes at the cohort level only.

Experiment 2 immune counts vary by endpoint:

| Figure 4 endpoint | Ctr | Ctr Stress | FVT Stress |
|---|---:|---:|---:|
| Relative Ly6Chi monocytes | 10 | 10 | 9 |
| Relative neutrophils | 10 | 9 | 9 |
| CD62L-positive Ly6Chi monocytes | 10 | 10 | 9 |
| Plasma IP-10 | 9 | 10 | 7 |
| Unstimulated splenocyte TNF-alpha | 9 | 8 | 9 |
| Unstimulated splenocyte IL-12/IL-23p40 | 10 | 8 | 9 |
| Unstimulated splenocyte IL-6 | 9 | 6 | 9 |
| ConA-stimulated splenocyte IL-6 | 10 | 8 | 9 |

Flow cytometry methods describe blood before and 45 minutes after FST, using the blood-cell fraction remaining after plasma collection. Figure 4 describes assessment after 16 days of defeat. The experiment timeline places FST on study day 19, and Sec18 places basal blood collection five minutes before FST. This follows 16 defeat sessions: ten before the day-11 behavioural test, three before the day-15 test, and three before day19. Terminal plasma and spleen collection occurred on day23, after the 19-session course. The biological blood and spleen collections are therefore four study days apart; source-animal linkage does not make these measurements contemporaneous. These are specimen collection days, not exact assay readout times: Sec20 describes cytometer analysis on the following day, and Sec21 describes 24-hour splenocyte culture after a 2.5-hour rest. Corticosterone sampling at -5, +15, +45, +90 minutes around FST is acute stress reactivity, not a prechronic-stress immune baseline. Splenocyte cultures include unstimulated, ConA and LPS conditions. Below-detection cytokine samples were excluded in the publication. Technical replicates were averaged per individual.

Evidence: Sec18-Sec22, Sec32, Figure 4. Consequently, endpoint cytokines from plasma and stimulated splenocyte cultures must remain separate outcomes. Neither measures a repeated within-mouse immune response across the entire chronic stress period.

The housing caveat is contrast-specific. Sec10 states that stress groups were singly housed after habituation, while control groups remained group housed. The stressed-versus-unstressed contrast therefore includes different stated housing regimes. FVT Stress versus Ctr Stress compares two singly housed groups; it does not have that same between-regime difference. Cage membership, allocation history, aggressor assignment and other shared exposures remain unavailable, so this distinction does not establish independent errors or permit a retrospective cage correction.

## Endpoint units and basal timing verified against the published table

The publisher's [article PDF](https://www.nature.com/articles/s41564-023-01564-y.pdf), Extended Data Table 1b,c, provides unit and timing evidence absent from the workbook column names. The table was inspected through indexed primary-source text, with the TNF-alpha cell subsequently checked visually. Eight of the nine selected group means agree with direct rounding of the workbook means. The printed FVT unstimulated TNF-alpha mean is an unresolved exception:

| Selected workbook column | Published Ctr / Stress / FVT Stress means | Recalculated source means | Published unit and timing |
|---|---|---|---|
| `ly6chi_monocytes` | 4.38 / 2.35 / 3.91 | 4.3843577 / 2.3503197 / 3.9068106 | Table 1c: percent of parent population, basal blood sample |
| `ly6chi_monocytes_cd62` | 61.4 / 59.6 / 75.5 | 61.397405 / 59.636964 / 75.510619 | Table 1c: percent of parent population, basal blood sample |
| `tnfa_splenocyte_unstimulated` | 34.4 / 102.0 / 27.9 | 34.437477 / 101.980594 / 27.849278 | Table 1b: pg/mL, vehicle/unstimulated splenocyte culture |

The FVT unstimulated TNF-alpha workbook mean is 27.8492778 pg/mL, which rounds directly to 27.8 at one decimal place, whereas Table 1b prints 27.9. No source correction or explanation is inferred. The published units, ordering and assay context remain supported. The reconstructed caption t statistics and Tukey comparisons agree with the source observations despite this printed group-mean discrepancy.

Basal in Table 1c means before the acute forced-swim test, after the chronic stress exposure already received. It does not denote a baseline before chronic stress. The table separately reports 45-minute post-FST monocyte means of 2.47 / 2.37 / 2.75 and CD62L-positive monocyte means of 71.1 / 73.7 / 75.4. Those do not match these workbook columns. Therefore the selected cell outcomes should be labeled basal, before FST, with the chronic-stress context retained. Their additive mean contrasts are percentage points, not relative percentage changes, absolute cell counts, or demonstrated immune-cell trafficking.

The culture TNF-alpha endpoint is distinct from circulating plasma TNF-alpha. The paper's terminal sampling and culture methods establish its assay scope. It should not be called systemic TNF-alpha concentration or cytokine response to chronic stress within the same animal over time.

The supplementary table itself is named Extended Data Table 1. It appears as an image-backed table in the frozen XML, where captions do not preserve its numeric cells. The primary publisher PDF URL above is the evidence location for its table cells. Search used to locate these primary cells: DOI plus `Percent of parent population`, `LY6Chi Monocytes`, `61.4`, and `TNF pg`.

## Viral measurement qualifications

The bulk viral catalog was assembled from FVT inocula and then used to map bulk metagenomic reads. It is therefore an inoculum-informed detectable viral fraction, not an unbiased census of every intestinal phage. A sensitivity analysis would need to distinguish confident phages, other viruses and unclassified putative viral sequences. The catalog construction included sequence/protein evidence and computational viral calling; predicted hosts remain predictions.

Quantitative inclusion required at least 50% CheckV completeness, at least one viral gene, and at least 10% viral genes. Mapping coverage was required over at least 75% of contig length. Counts were length-normalized and total-sum scaled; Q33 spike-based absolute counts apply to the characterized inocula. Recipient bulk-read fractions should not inherit inoculum absolute particle counts. Published analyses further excluded phages with prevalence below 50%, replaced zeros, and used CLR/Aitchison methods (Sec26-Sec28).

## Identifiability decision

The paper supports the existence of a potentially useful individual pre/post bulk-metagenomic viral measurement route. It does **not** itself supply a verified one-to-one map between those profiles and immune source-data rows. That map must use stable animal identifiers, not treatment plus row position. Until the inputs and map are present, animal-level viral-immune models and measured longitudinal phageome stability remain unexecuted and unverified.

Even if matching succeeds, distinguish viral within-mouse change from endpoint immune phenotype; the paper does not establish a prechronic-stress baseline for every immune endpoint. Adjustment for treatment and bacterial change needs adequate complete-case sample size. Inoculum profiles must never substitute for recipient profiles.

The paper's restoration contrast averages Ctr and FVT Stress against Ctr Stress. A significant contrast does not establish both individual pairwise effects. For example, the Figure 4 stressed-versus-FVT pairwise P values are 0.106 for monocytes and 0.231 for neutrophils. CD62L-positive monocytes show little Ctr-versus-stressed difference (P=0.845), despite a strong FVT difference. A reanalysis should report the component contrasts and intervals, not assume a common restoration pattern. The publication used an FDR threshold of 0.2 in some analyses and excluded statistical outliers beyond 2.5 standard deviations (Sec32); these choices warrant explicit sensitivity analysis if raw source observations can be retrieved.

## Caption multiplicity consistency outside the selected endpoint family

The three selected endpoints reproduce all nine selected caption-statistic checks at the reported precision; that statement does not cover every Figure4 endpoint or the original full BH family. A separate documentary check found an unresolved inconsistency for unstimulated splenocyte IL-6, which is outside the current selected family and has not been added as a biological hypothesis test. Figure4 prints `t(22)=2.328` and `q=0.010`. The publisher [HTML](https://www.nature.com/articles/s41564-023-01564-y) and [PDF](https://www.nature.com/articles/s41564-023-01564-y.pdf) agree with frozen XML Fig4 on these values. The caption identifies q as the BH-FDR-adjusted P value, and Sec32 explicitly describes Benjamini-Hochberg adjustment of the calculated planned-contrast P values.

A two-sided t reference gives P=0.02950474 from that printed t and df. Allowing the t statistic to round to 2.328 gives P approximately 0.02947341-0.02953610, still above 0.010. Ordinary BH adjusted P values cannot be smaller than the corresponding raw P value: each eligible step-up term is `m*p_(j)/j >= p_(i)` for `j >= i`, before the minimum and cap at one. Thus the printed t/P/q combination cannot be reconciled as ordinary BH adjustment of that same two-sided t test. A different underlying calculation, notation or reporting error cannot be distinguished without complete original outputs and family definitions. No correction or cause is assigned. This narrow consistency check is not a reconstruction of the original BH family and does not alter the selected nine caption matches or the present six-test family.

## Exact supplementary targets

XML media elements identify the files, independently of inferred URL conventions:

- `41564_2023_1564_MOESM1_ESM.pdf`: reporting summary.
- `41564_2023_1564_MOESM2_ESM.xlsx`: supplementary source data.

Publisher source-data URL: [supplementary XLSX](https://static-content.springer.com/esm/art%3A10.1038%2Fs41564-023-01564-y/MediaObjects/41564_2023_1564_MOESM2_ESM.xlsx).

Other primary resources declared in the XML: [PRJEB69687](https://www.ebi.ac.uk/ena/browser/view/PRJEB69687) (16S), [PRJNA970614](https://www.ncbi.nlm.nih.gov/bioproject/PRJNA970614) (metagenomics), [PRJEB67706](https://www.ebi.ac.uk/ena/browser/view/PRJEB67706) (transcriptomics), and [Zenodo 10144096](https://doi.org/10.5281/zenodo.10144096) (analysis scripts). An accession or filename establishes provenance, not availability of processed abundance values or cross-assay matching.
