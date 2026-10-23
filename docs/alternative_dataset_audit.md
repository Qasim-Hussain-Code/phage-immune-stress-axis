# Alternative stress–virome datasets

This assessment extends the [initial feasibility screen](alternative_dataset_search.md)
with full methods, data-availability statements, supplementary files and
repository metadata inspected on **20 October 2026**. None of the inspected
releases established the combination of individual study-animal viral profiles,
measured immune phenotypes and an explicit animal-level crosswalk needed for
the proposed association. The reasons differ by study: Choi measures donor
viromes rather than recipient viromes; Duan and Li do not identify the required
host immune measurements; Chen remains unresolved because the necessary
methods and data were not accessible through the checked routes.

Eligibility requires a relevant stress design, fecal viral profiles from the
animals with measured host immune outcomes, identifiers linking those assays,
and accessible processed inputs within the resource budget. FVT studies need
recipient profiles; non-FVT studies can provide profiles from the individual
stress-exposed animals themselves. Temporal stability additionally requires
repeated individual viromes. Donor inocula and bacterial 16S profiles cannot
replace the relevant viral measurements, while metabolites, corticosterone,
predicted viral functions and bacterial antiviral defenses do not replace
measured host immune phenotypes.

## Choi: donor viromes and recipient inflammatory transcripts

[Choi et al. (2026)](https://www.nature.com/articles/s41598-026-49647-0)
describe pooled pre-/post-weaning piglet material used for FVT into mice.
The [full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC13276362/fullTextXML),
particularly “Experimental design,” “Fecal virome transplantation,” “Bacteriome
analysis” and “Colonic barrier and inflammatory markers,” distinguishes the
donor and recipient measurements. The pre-weaning and post-weaning FMT/FVT
pools each combined feces from six piglets. Viral shotgun sequencing used
donor-source material prepared in parallel; the administered aliquots themselves
were not sequenced.

Recipient mouse feces underwent bacterial 16S profiling at four stages, using
four selected mice per group to align bacterial and behavioral observations.
Colonic TNF-α, IL-6 and IL-10 qRT-PCR provide measured immune-related endpoints.
Serum corticosterone is an endocrine outcome; fecal metabolites and brain
transcripts are separate measurements. The recipient immune assays therefore
do not lack biological relevance, but neither donor sequencing nor recipient
16S data supply the recipient viral profiles required for a viral–immune
association or recipient viral stability.

The accepted publisher DOCX contains six supplementary figures concerning
donor bacterial/viral composition, antibiotic depletion, donor particle
characterization, colon/growth readouts and bacterial–metabolite correlations.
Its single ten-row, four-column table reports endpoint-level effect sizes and
post hoc power. The package contains six images and no embedded files; it
provides no recipient viral matrix, individual immune table or crosswalk.

The article deposits raw sequencing under PRJNA1250699 and offers other data
on request. The [ENA run report](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA1250699&result=read_run&fields=run_accession,study_accession,sample_accession,secondary_sample_accession,sample_alias,library_strategy,library_source,scientific_name,fastq_bytes&format=tsv)
saved on 20 October contains 46 records, all labelled `AMPLICON`, with the same
broad study description in their aliases. These records do not resolve the
donor-shotgun deposit or provide recipient viral measurements. They do not
establish what additional sequencing might exist elsewhere.

## Duan: individual viromes without a verified immune endpoint

[Duan et al. (2022)](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2022.1046894/full)
study 21-day chronic restraint stress in mice, with seven controls and eight
stressed animals. Individual fecal samples underwent VLP-enriched viral
metagenomics; there is no donor/recipient FVT design. The
[full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9706091/fullTextXML)
describes viral DNA extraction and sequencing alongside behavioral tests, body
weight and LC–MS/MS fecal neurotransmitter analysis. The reported virome–host
molecular correlations concern metabolites, including tryptophan-pathway
compounds. Discussion of immune mechanisms does not establish a measured host
cytokine or immune-cell outcome.

The accepted Europe PMC supplement contains two virome composition/function
figures and one aggregate baseline SPT/FST/TST table, with no embedded files.
It supplies neither individual immune observations nor an individual viral
abundance matrix linked to them. The [ENA metadata report](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA877780&result=read_run&fields=run_accession,study_accession,sample_accession,secondary_sample_accession,sample_alias,library_strategy,library_source,scientific_name,fastq_bytes&format=tsv)
contains 15 WGS records under PRJNA877780, with aliases such as A1 and A38.
The limitation for this question is the absence of a verified measured immune
pairing in the inspected study, rather than the lack of individual viromes.

## Li: processed viral annotations without host immune observations

[Li et al. (2023)](https://www.frontiersin.org/journals/microbiology/articles/10.3389/fmicb.2023.1132403/full)
study rat chronic unpredictable mild stress and antidepressant/Xiaoyaosan
treatment. “Animals, treatments, and collection of fecal samples” in the
[full-text XML](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10140408/fullTextXML)
specifies endpoint fecal collection at week 15 from three individual rats in
each of five groups: HC, CUMS, amitriptyline, fluoxetine and Xiaoyaosan. Viral
sequences were identified computationally from bulk fecal metagenomes. Methods
cover viral sequence recovery, taxonomic/functional annotation, lifestyle
prediction, bacterial host assignment and network analysis. Behavior and body
weight are reported, but the inspected methods do not describe a host cytokine
or immune-cell assay. CRISPR/tRNA/BLAST-based bacterial host prediction is not a
mammalian immune phenotype. An endpoint viral profile also cannot establish
within-animal temporal stability.

All eight authentic supplementary XLSXs were recovered from Europe PMC and
every worksheet inspected. Their contents match the publisher/XML captions:

| Table | Verified contents |
|---|---|
| S1 | Sequencing QC for 15 samples, including HC01 |
| S2 | CheckV quality annotations for 5,029 vOTUs |
| S3–S5 | Group-specific virus–bacterial-host matches/predictions |
| S6 | Aggregate bacterial host counts |
| S7 | 25,106 bacterial host assignments |
| S8 | 157 viral–bacterial correlation links |

There are no additional hidden worksheets. These are processed annotations,
not a raw-only release, but none is a virus-by-individual-sample abundance
matrix or a set of individual mammalian immune observations. The accession
PRJNA910226 is verified in article XML and BioStudies links. The 20 October ENA
run-metadata requests timed out; those failures do not establish deposit
absence. The content assessment rests on the authentic files, rather than the
unrelated mirror responses described below.

## Chen: relevant biology with unresolved assay and data access

The public publisher preview for
[Chen et al. (2026)](https://www.sciencedirect.com/science/article/pii/S0889159126002801),
inspected through its search-index representation, describes prenatal stress
in Sprague–Dawley rats, offspring virome/bacteriome analysis, FVT and immune
responses. It offers supporting data through the corresponding author on
reasonable request. Full methods and the supplement listing were not recovered
in the 20 October checks. Consequently immune-assay identity, recipient-level
co-measurement, sampling times, reusable animal identifiers and public
processed pairing remained unverified.

This is an unresolved relevant candidate, rather than a demonstrated scientific
exclusion. The [candidate assessment](new_prenatal_stress_candidate.md) and
[public-route follow-up](chen2026_public_route_followup.md) separate the
preview's biological claims from the missing methodological and data evidence.
An on-request availability statement does not establish that no separate public
deposit exists.

## Retrieval record: 20 October 2026

The accepted documents and packages used for these content assessments are
identified below. No plot values were digitized into new animal observations.

| Retained artifact | Bytes | SHA-256 |
|---|---:|---|
| [Choi publisher DOCX](https://static-content.springer.com/esm/art%3A10.1038%2Fs41598-026-49647-0/MediaObjects/41598_2026_49647_MOESM1_ESM.docx) | 2,031,912 | `a7a4a5b6d51a96c4a6202fdaf94d3741b199dc5dfb25ac8a5174b1d593683515` |
| [Duan Europe PMC package](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC9706091/supplementaryFiles) | 1,098,719 | `7b58dca6d0c4d3b741262252a2acf66710cd1e65f4071ab6d706f635bce3b7fd` |
| Duan package member `Data_Sheet_1.docx` | 593,069 | `3cd29b0d75afd63e87ada4ca9103b36a5f8a6a0847477a26fe3c184eae49b798` |
| [Li Europe PMC package](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10140408/supplementaryFiles) | 5,873,635 | `11c85c127b3fb2208e849454e0ba34952ef102fed28de69b04c0a7b15ae21f2a` |

Source validation mattered because filenames and listed sizes were insufficient.
The [BioStudies Duan record](https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC9706091)
advertised a 5,534,654-byte DOCX whose exact redirected file URL returned
plant-associated bacterial-isolate tables. The
[BioStudies Li record](https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC10140408)
listed eight XLSX filenames and sizes; it did not supply their content
descriptions, which came from publisher/XML captions. The downloaded files
matched those listed sizes but contained Rubus fruiting, SNPs, Arabidopsis
orthologues and other genetic traits. These nine mirror downloads are marked
`rejected_content_mismatch` in the inventory and source ledger. The mismatch
records the observed responses, without assigning a cause or responsible party.
Choi's BioStudies accession S-EPMC13276362 returned HTTP 404 during this audit;
its direct publisher supplement was obtained independently.

Queries combined `virome`, `stress`, `cytokines`, `immune responses`, `chronic
restraint`, `chronic unpredictable`, `prenatal`, `2025` and `2026`. Returns also
included the original Ritz study, human depression/bipolar studies and reviews;
reviews served as discovery leads rather than evidence of assay availability.
Arthritis, chemical-exposure and colitis studies were not substituted for the
specified stress context.

The [source ledger](../data/manifests/alternative_search_sources.json),
its [CSV view](../data/manifests/alternative_search_sources.csv),
[package/cell inventory](../data/manifests/alternative_supplement_inventory.json)
and [package-member hashes](../data/manifests/alternative_supplement_members.json)
retain exact URLs, statuses, content decisions and checksums. The record covers
51 HTTP attempts: 31 successful responses totalling 18,981,221 bytes and
20 failed requests. It distinguishes nine rejected mirror responses from nine
accepted extracted data-file members. The two accepted Europe PMC archives
have a frozen 31-member inventory. Saved responses and extracted data-file
hashes were checked against these ledgers. Raw responses and binary supplements
remain ignored local cache under `data/raw/alternative_search/`; the tracked
ledgers preserve the findings for a fresh checkout.

Requests were preceded by the project resource guard, with caps of 2 MB for
metadata/HTML/XLSX and 12 MB for DOCX/package responses. Read-only package/cell
inspection peaked at 70,524,928 bytes RSS. No raw sequencing reads, heavy
reference databases or new dependencies were acquired, and no authors were
contacted or access-control workaround used. Core scientific inputs and
pipeline code were unchanged during this audit. Failed requests are access
observations, not evidence of data absence. This bounded assessment does not
exclude unindexed, closed-access or subsequently released datasets.
