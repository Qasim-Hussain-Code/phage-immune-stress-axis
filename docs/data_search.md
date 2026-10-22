# Finding data for the viral–immune question

Search date: **20 October 2026**. This overview draws on the retained search
records and retrieved material from that date.

The searches recovered individual immune measurements and sequencing metadata
for the Ritz study, but not the processed community tables and verified animal
map needed for the proposed analysis. Other stress studies supplied different
combinations of measurements; none was verified as ready for this paired
analysis. Chen's prenatal-stress study remains a relevant unresolved lead.
The sources and access limits are recorded below.

## Data needed

Relating within-mouse viral change to an immune phenotype requires repeated
individual fecal viral abundance profiles, sampling times, viral annotations,
individual immune measurements and explicit identifiers connecting them.
Donor inocula and group pools cannot be assigned to individual recipients.
Bacterial adjustment additionally needs matched bacterial profiles. An immune
baseline is needed to estimate immune change across stress, but is not required
merely to relate viral change to a terminal immune phenotype.

## The Ritz releases

[Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y)
describes individual recipient bulk metagenomes mapped to an inoculum-derived
viral catalog alongside pooled enriched viromes. Individual viral measurements
therefore existed in the original analysis. The recovered phenotype workbook
contains 50 animal rows across two experiments. The metagenomic inventory has
104 specimens: 77 recipient bulk samples, eight pools and 19 inocula. Those
categories cannot be counted as 104 immune-matched animals.

The [Zenodo release](https://zenodo.org/records/10460215) contains a script PDF
that references local data tables. The complete
[Europe PMC supplementary package](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10847049/supplementaryFiles)
contains the same phenotype workbook, a reporting PDF and figure/table images,
without another abundance matrix. Its 32 members were inventoried. The
[BioStudies record](https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC10847049)
independently lists the workbook and reporting PDF.

The search also checked accession-linked ENA analysis files, NCBI assembly and
nucleotide records, current and legacy MGnify, selected author repositories,
exact filenames from the scripts, and DOI/data indexes. Its 52 evidence records
are saved responses or representations, not 52 datasets. No processed recipient
viral or bacterial matrix, study contig catalog or verified immune-animal
crosswalk was recovered. Raw reads were inventoried without reprocessing.

## Other stress studies

The comparison used full methods and actual supplements where accessible,
rather than treating references to immune mechanisms as measured immune data.

| Study | Viral and host measurements | Consequence for this question |
|---|---|---|
| [Choi 2026](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13276362/fullTextXML) | Viral sequencing concerns pooled pre-/post-weaning piglet donor material. Mouse recipients have bacterial 16S profiles and measured colonic TNF-alpha, IL-6 and IL-10 transcripts. | Recipient viromes are not established. The supplement contains figures and an aggregate power table, without an individual viral–immune release. |
| [Duan 2022](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9706091/fullTextXML) | Individual mouse fecal viromes after chronic restraint stress; behavior, weight and neurotransmitter metabolites. | Full methods and the correct supplement identify no directly measured cytokine or immune-cell assay. |
| [Li 2023](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10140408/fullTextXML) | Endpoint rat metagenomes after chronic unpredictable mild stress and treatment. Eight processed XLSXs provide viral QC and bacterial-host annotations or correlations. | Processed annotations are available, but these tables contain neither an individual viral abundance matrix nor measured mammalian immune outcomes. Endpoint sampling also cannot estimate temporal stability. |
| [Chen 2026](https://www.sciencedirect.com/science/article/pii/S0889159126002801) | Prenatal-stress rat offspring virome/bacteriome analysis, FVT and immune responses appear in the public abstract/preview. | Recipient immune assays, timing, identifiers and processed pairing remain unverified. Retained as unresolved. |

Choi's article-reported sequencing accession returned 46 ENA records labelled
AMPLICON; it was not assumed to supply viral metagenomes. For Duan and Li,
nine content-mismatched BioStudies mirror responses were rejected. Correct
Europe PMC supplements were recovered and inspected; Li was not classified as
a raw-only release. The initial screen also considered human depression and
chemical-exposure illness, without substituting those conditions for the
specified stress question.

## Why Chen remains unresolved

The publisher preview offers supporting data through the corresponding author
on reasonable request. Advertised Elsevier routes, PubMed LinkOut, university
pages and exact-DOI bioRxiv/medRxiv lookups did not yield full methods, a
supplement inventory or a processed animal-level pairing. One successful
Elsevier XML response contained bibliographic metadata only. Inaccessible
institutional routes and unsuccessful requests leave access unknown; they do
not establish scientific ineligibility or deposit absence. No authors were
contacted.

## What would enable further analysis?

A release would need recipient abundances, repeated-sample identifiers and
times, immune values and assay definitions, and a verified specimen-to-animal
crosswalk documenting exclusions, calibration and pool membership. Contig
quality and viral-classification annotations would define the detectable
viral fraction; bacterial adjustment would need matching bacterial data.
Linkage and complete-case sample sizes would be assessed before fitting a model.

For Ritz, those inputs could support an endpoint association while retaining
the design's limits: stress versus Control includes different housing regimes,
whereas both stressed groups share the stated single-housing regime. The blood
and spleen assays also have different collection times. Data access would not
by itself isolate a phage mechanism or establish within-mouse immune change.

## Audit records

- Ritz: [detailed search](processed_data_search.md),
  [source ledger](../data/manifests/processed_search_sources.json) and
  [supplement inventory](../data/manifests/processed_search_supplementary_members.csv).
- Alternatives: [initial screen](alternative_dataset_search.md),
  [methods and supplement audit](alternative_dataset_audit.md),
  [source ledger](../data/manifests/alternative_search_sources.json) and
  [content inventory](../data/manifests/alternative_supplement_inventory.json).
- Chen: [initial assessment](new_prenatal_stress_candidate.md),
  [public-route follow-up](chen2026_public_route_followup.md),
  [initial evidence](../data/manifests/chen2026_candidate_evidence.json),
  [HTTP ledger](../data/manifests/chen2026_http_sources.json) and
  [follow-up ledger](../data/manifests/chen2026_followup_sources.json).
