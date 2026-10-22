# Experimental design and source interpretation

This guide identifies the measurements and experimental units described by
[Ritz et al. (2024), *Nature Microbiology* 9, 359–376](https://doi.org/10.1038/s41564-023-01564-y).
It is based on the article and supplementary material reviewed on 20 October
2026. Section identifiers refer to the frozen
[article XML](../data/raw/article.xml), available from
[Europe PMC](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10847049/fullTextXML).
The article is licensed [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/).

## Two experiments and several types of viral measurement

| Component | Published design | Unit relevant to reanalysis |
|---|---|---|
| Initial stress experiment | Twenty male C57BL/6J mice, ten allocated to Control and ten to Stress; 20 days of social defeat and overcrowding | Individual animals for immune assays; enriched viromes combine three or four mice per pool |
| FVT experiment | Thirty male C57BL/6J mice, ten allocated to Control, Control Stress and FVT Stress; 19 defeat days over 22 study days | Individual animals for the source-workbook assays; no unstressed FVT arm |
| FVT inocula | Purified autochthonous viromes prepared from prestress feces; Figure 3 reports nine individual FVT preparations | Administered material, distinct from the recipient intestinal community |
| FVT enriched recipient viromes | Methods combine one fecal sample from each mouse into a group pool | Group pools, which cannot supply individual viral values |
| FVT bulk metagenomes | Individual fecal DNA sequenced; bulk reads mapped to an inoculum-derived viral catalog | A separate route to individual recipient viral signals, requiring the actual abundance matrix and animal map |

Sections Sec10–Sec14 and Sec23–Sec27 describe these designs. The initial
experiment used both defeat and overcrowding, while the FVT experiment omitted
overcrowding to reduce coprophagy during treatment. Control and Control Stress
received vehicle buffer; FVT Stress received purified prestress autochthonous
virome preparations.

In the FVT experiment, each defeat day included two bouts separated by two
hours across a perforated divider (Sec14). Counts of defeat days therefore
differ from counts of individual bouts.

The initial cohort's prose reports ten control and nine stressed contributors,
whereas the virome captions report ten per group. Extended Data Figure 2
(XML Fig7) describes three pools per group at each of two times. This implies
12 published pool-by-time profiles, but does not verify 12 deposited accessions
or stable pool membership across time. The same caption describes pooled
prestress bacteriome controls, so individual longitudinal bacterial coverage
cannot be assumed for that cohort.

For the FVT experiment, Extended Data Figure 4 (XML Fig9) reports pre/post
bacteriome and virome summaries with group counts 10, eight and nine. These
support the individual bulk-derived measurement route alongside the pooled
enriched viromes. They do not supply a verified map to the immune workbook.
The accession inventory also contains heat-inactivated treatment specimens
absent from that workbook; the [data assessment](data_feasibility.md) reconciles
the deposited specimen categories.

## Immune measurements and collection times

The selected flow outcomes and cytokine outcome were collected at different
times in the FVT experiment:

| Occasion | Biological measurement | Source evidence |
|---|---|---|
| Day 19, five minutes before forced swim | Basal blood-cell measurements, after 16 defeat days | Timeline in Sec11; sampling in Sec18; flow methods in Sec20; Figure 4 |
| Day 19, 45 minutes after forced swim | A separate acute-stress blood-cell measurement | Sec18 and Sec20; separately labelled columns in Extended Data Table 1c |
| Day 23, after 19 defeat days over the study | Terminal spleens for subsequent ex vivo culture | Sec11 and Sec21 |

Blood was processed on the collection day; fixed cells were analysed by flow
cytometry the following day. Splenocyte methods describe a 2.5-hour rest and
24-hour culture. Collection time therefore differs from assay readout time.
Technical replicates were averaged per individual in the original study
(Sec32), rather than counted as additional animals.

Basal means before the acute forced-swim test, after chronic stress exposure
had already begun. The selected blood assays and terminal spleen assay do not
measure within-mouse immune change across chronic stress. An endpoint immune
phenotype could nevertheless serve as an outcome for an association with viral
change, if repeated individual viral values and a legitimate animal crosswalk
were available.

Figure 4 reports different observed sample counts by assay:

| Immune endpoint | Control | Control Stress | FVT Stress |
|---|---:|---:|---:|
| LY6Chi monocyte proportion | 10 | 10 | 9 |
| Neutrophil proportion | 10 | 9 | 9 |
| CD62L-positive fraction of LY6Chi monocytes | 10 | 10 | 9 |
| Plasma IP-10 | 9 | 10 | 7 |
| Unstimulated splenocyte TNF-alpha | 9 | 8 | 9 |
| Unstimulated splenocyte IL-12/IL-23p40 | 10 | 8 | 9 |
| Unstimulated splenocyte IL-6 | 9 | 6 | 9 |
| ConA-stimulated splenocyte IL-6 | 10 | 8 | 9 |

These are published counts, not additional analyses in this repository. The
selected family remains the two monocyte outcomes and unstimulated splenocyte
TNF-alpha, each with two treatment contrasts. Initial-experiment ConA cytokine
measurements belong to the other cohort and are kept separate.

## Units and source-column interpretation

Extended Data Table 1b,c identifies the selected monocyte values as percentages
of parent population and unstimulated culture TNF-alpha as pg/mL. The workbook
columns match the table's basal flow summaries:

| Workbook column | Source means: Control / Stress / FVT Stress | Printed means |
|---|---|---|
| `ly6chi_monocytes` | 4.3843577 / 2.3503197 / 3.9068106 | 4.38 / 2.35 / 3.91 |
| `ly6chi_monocytes_cd62` | 61.397405 / 59.636964 / 75.510619 | 61.4 / 59.6 / 75.5 |
| `tnfa_splenocyte_unstimulated` | 34.437477 / 101.980594 / 27.849278 | 34.4 / 102.0 / 27.9 |

Eight of nine source means round to the printed cells. The FVT TNF-alpha mean
is 27.8492778 pg/mL, which rounds directly to 27.8, while the inspected original
table image prints 27.9. The cause remains unresolved. The selected caption
statistics agree with the source observations despite that minor discrepancy.

The table's separate 45-minute post-FST monocyte means are 2.47 / 2.37 / 2.75,
and CD62L-positive means are 71.1 / 73.7 / 75.4. Those do not identify the
selected workbook columns. Flow differences are percentage points, rather
than absolute cell counts or evidence of trafficking. Culture TNF-alpha is
distinct from circulating plasma TNF-alpha. The
[original-method reconstruction](original_analysis_review.md) gives the full
numerical comparison with published statistics.

## Housing and treatment interpretation

Section Sec10 states that stressed groups were singly housed after habituation
while controls remained group housed. Stress versus Control therefore includes
the housing-regime difference. FVT Stress versus Control Stress compares two
groups with the same stated regime. Missing cage allocation, aggressor
assignment and other shared-exposure information still prevent a measured
dependence adjustment.

The original planned contrast compares the stressed mean with the average of
Control and FVT Stress. Its significance does not establish both a stress
effect and its reversal. The present [results](results.md) report the two
component comparisons separately. Upstream detection-limit, technical and
statistical exclusions remain unresolved at the observation level; Sec32
describes the original 2.5-standard-deviation rule and a maximum of two
statistical exclusions per test.

## What the viral signals represent

Sections Sec26–Sec28 describe a catalog assembled from FVT inocula and used to
map recipient bulk reads. It represents an inoculum-informed detectable viral
fraction, rather than an unbiased census of all intestinal phages. The
publication used sequence and protein comparisons alongside computational
viral callers; bacterial-host assignments remain predictions.

Quantitative inclusion required CheckV completeness of at least 50%, at least
one viral gene and at least 10% viral genes. Counts were set to zero when
coverage at 1× did not span 75% of a contig. Counts were length-normalized and
scaled by library size. Q33 spike-based absolute-count calculations were
described for inocula; those counts cannot be transferred to individual
recipient profiles. Subsequent compositional analysis excluded phages with
prevalence below 50%, replaced zeros and used CLR/Aitchison calculations.

No corresponding processed matrix, annotation set or verified immune-animal
crosswalk was recovered. Those missing inputs, not a blanket claim that the
original viromes were pooled, block the proposed individual viral–immune
analysis. [Data availability](data_feasibility.md) lists the required inputs.

## An unresolved caption check outside the selected family

Figure 4 prints `t(22) = 2.328` and BH-adjusted `q = 0.010` for unstimulated
splenocyte IL-6. Under a two-sided t reference, that t statistic gives
P ≈ 0.02950. Allowing for rounding of t to three decimal places leaves P near
0.02947–0.02954. Ordinary BH adjusted P values cannot be smaller than their
corresponding raw P values, so that printed combination is incompatible with
BH adjustment of the same two-sided t test.

The figure caption and Sec32 identify the stated procedure. Without the full
original outputs and family definitions, a different calculation, notation or
reporting error cannot be distinguished. No cause or correction is assigned.
This documentary check adds no endpoint to the analysis and does not alter
the nine selected caption matches or the present six-test family.

## Source locations

The article declares the publisher [source workbook](https://static-content.springer.com/esm/art%3A10.1038%2Fs41564-023-01564-y/MediaObjects/41564_2023_1564_MOESM2_ESM.xlsx),
the [reporting summary](https://static-content.springer.com/esm/art%3A10.1038%2Fs41564-023-01564-y/MediaObjects/41564_2023_1564_MOESM1_ESM.pdf),
[PRJEB69687](https://www.ebi.ac.uk/ena/browser/view/PRJEB69687) for 16S,
[PRJNA970614](https://www.ebi.ac.uk/ena/browser/view/PRJNA970614) for metagenomics,
[PRJEB67706](https://www.ebi.ac.uk/ena/browser/view/PRJEB67706) for transcriptomics,
and [Zenodo 10144096](https://doi.org/10.5281/zenodo.10144096) for scripts.
Exact retained file identities are in [data provenance](data_provenance.md) and
the [input manifest](../data/manifests/inputs.json).
