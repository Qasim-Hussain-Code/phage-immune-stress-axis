# Expanded public processed-data search

Search date: 2026-10-20 (Asia/Taipei). Scope: Ritz et al., Nature Microbiology 2024, DOI [10.1038/s41564-023-01564-y](https://doi.org/10.1038/s41564-023-01564-y). This search extends the initial paper, archive and alternative-dataset audits. No authors were contacted.

## Outcome and scientific consequence

No new processed recipient viral abundance matrix, bacterial abundance matrix, study viral-contig catalog, or verified assay-to-mouse crosswalk was retrieved. The existing restricted analysis remains appropriate. This is a bounded retrieval finding for the sources and searches below, not proof that these objects do not exist elsewhere or that the original study measured only pooled viromes.

The expanded search materially strengthens the attachment and repository audit. An independently retrieved complete Europe PMC supplementary package and its BioStudies counterpart contain the same phenotype workbook already held by this project, a reporting-summary PDF, and figure/table images. They do not supply additional individual community measurements. Individual bulk-metagenome-derived viral profiles remain a published measurement route whose processed inputs and verified crosswalk were not recovered here.

## Frozen evidence

New evidence is catalogued in `data/manifests/processed_search_sources.json` and `.csv`: 52 saved records with URLs, byte sizes, SHA256, status and representation/extraction notes. The core scientific `data/manifests/inputs.json` was not changed. The supplementary member inventory is `data/manifests/processed_search_supplementary_members.csv`; it records all 32 members and their individual SHA256 checksums.

The source responses and extracted evidence are under ignored `data/raw/processed_data_search/`. The 6.44 MB ZIP remains ignored by Git. Connector snapshots are explicitly identified as saved structured representations, rather than original HTTP bytes. HTTP error pages, a publisher challenge page, and a superseded incorrect API filter are retained with their limitations rather than treated as substantive negative results.

## Publisher, Europe PMC and BioStudies

| Check | Retrieved evidence | Finding |
|---|---|---|
| Existing full-text JATS | Frozen `data/raw/article.xml` | Exactly two supplementary media objects: reporting summary `MOESM1` and phenotype source workbook `MOESM2`. The three Extended Data tables are image-backed. |
| [Europe PMC complete supplementary-files endpoint](https://www.ebi.ac.uk/europepmc/webservices/rest/PMC10847049/supplementaryFiles) | `europepmc_supplementary_files.zip`; 6,442,714 bytes; SHA256 `66423aea4ac42461cb5055c96ea63dc2fda4fbeb1cdb5e1d5a36cdaf8227e1bb` | 32 members: 30 WebP/GIF figure/table images, one 3,385,643-byte reporting PDF and one 23,358-byte XLSX. No additional CSV, TSV, FASTA, archive, figure-data workbook or processed abundance file is present in this package. |
| Supplementary XLSX inside that ZIP | Member `41564_2023_1564_MOESM2_ESM.xlsx` | SHA256 `1eac33250329c4160caff224c8ae4618a4a4849d5a086986bd12e5bb1c50d368`, exactly matching the existing frozen source workbook. It is not a new community dataset. |
| [BioStudies article record S-EPMC10847049](https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC10847049) | `biostudies_article.json`; 9,308 bytes | Independently lists exactly the reporting PDF and same XLSX, with no additional submitted file list. |
| [BioStudies DOI search](https://www.ebi.ac.uk/biostudies/api/v1/search?query=%2210.1038%2Fs41564-023-01564-y%22) | `biostudies_search_doi.json` | One hit, S-EPMC10847049; two files. |
| [BioStudies project search](https://www.ebi.ac.uk/biostudies/api/v1/search?query=PRJNA970614) | `biostudies_search_project.json` | Zero indexed hits for this project identifier. |
| Publisher article HTML | `nature_article.html`; HTTP 200, 3,038 bytes | The response is titled Client Challenge and is not article HTML. It does not establish that publisher-only attachments are absent. The independent JATS/package/BioStudies inventories provide the usable evidence. |

The 32-member package includes main Figures 1-5, Extended Data Figures 1-7, and Extended Data Tables 1-3, generally in WebP and GIF variants. These images were distinguished from underlying numerical source data. No points were digitized from plots and no image was turned into an individual abundance table.

The only nucleotide accession extracted as a BioStudies article link is JX564242. The frozen article identifies JX564242.1 as the lactococcal phage Q33 reference used as an internal viral standard. It is not the missing study viral-contig catalog.

## Reporting summary and Extended Data tables

The reporting PDF was extracted directly from the ZIP. It contains four image-backed pages; text extraction yielded only page markers, so all four pages were rendered and inspected visually. Page 2 names PRJNA970614 and PRJEB67706, and says source data can be requested from the corresponding author. It contains no additional processed-data repository or matrix URL. Its form is dated August 5, 2023 and describes 16S data as supplementary material; this predates the final publication's PRJEB69687 deposit and does not override the final data-availability statement.

The three full-resolution table images were also inspected. Their local names are `41564_2023_1564_Tab1_ESM.webp`, `Tab2_ESM.webp` and `Tab3_ESM.webp` in the search evidence directory.

| Table | Explicit content verified visually | Consequence |
|---|---|---|
| Extended Data Table 1a,b | Cytokines are labelled pg/ml. Splenocyte Vehicle, ConA and LPS cultures are separate; panel b additionally separates basal blood plasma. | Culture and circulating measurements must remain separate. These are published summary cells, not new individual observations. |
| Extended Data Table 1c | Flow cytometry is labelled percent of parent population; basal and 45-minute post-stress columns are separate. Basal selected monocyte means are 4.38/2.35/3.91 and CD62L-positive monocyte means 61.4/59.6/75.5. | Confirms the existing basal-unit interpretation from actual table imagery. This is not a prechronic-stress immune baseline. |
| Extended Data Table 1b, vehicle TNF-alpha | Ctr 34.4, Stress 102.0, FVT Stress 27.9 are explicitly printed. An enlarged read-only crop confirmed the FVT cell is 27.9, not 27.8. | The workbook-derived mean 27.8492777778 rounds to 27.8 at one decimal. Preserve this discrepancy rather than widening a rounding tolerance or changing source values. The summary image cannot resolve the cause. |
| Extended Data Tables 2 and 3 | Gut-brain or gut-metabolic module names with restoration-effect P and Q values. | Summary statistics only; no per-animal functional abundances, viral abundances, identifiers or assay crosswalk are supplied. |

No numerical table was imported into a new biological analysis during this search. The selected table-cell check was sent to the independent replication reviewer.

## Sequence and secondary-analysis archives

| Service/query | Result and interpretation |
|---|---|
| [ENA analysis-file report, PRJNA970614](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA970614&result=analysis&format=tsv) | Header only: analysis_accession, submitted_ftp, submitted_bytes, submitted_md5. No analysis-file rows. This is distinct from the 104 raw-read runs already inventoried. |
| [ENA analysis-file report, PRJEB69687](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJEB69687&result=analysis&format=tsv) | Same header-only result; no additional submitted analysis files retrieved. |
| [NCBI Assembly accession search](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=assembly&term=PRJNA970614&retmode=json&retmax=20) | Count zero. The response records the query translation and no matching project phrase. |
| [NCBI Nucleotide BioProject search](https://eutils.ncbi.nlm.nih.gov/entrez/eutils/esearch.fcgi?db=nuccore&term=PRJNA970614%5BBioProject%5D&retmode=json&retmax=20) | Count zero. No nucleotide records indexed under this exact BioProject query were retrieved. |
| NCBI explicit BioProject-to-Assembly and BioProject-to-Nucleotide link queries | Both return the input BioProject ID with no linked-record list. These support the scoped accession search; they do not rule out every possible third-party reassembly project. |
| MGnify current API v2 search | Searching study titles/accessions for PRJNA970614, SRP441601, PRJEB69687 and PRJEB67706 returned zero items for each. The v2 OpenAPI schema explicitly documents this search scope. The exact INSDC lookup `/api/v2/studies/insdc/PRJNA970614` returned HTTP 404. |
| MGnify v2 title search, gut virome | Five indexed studies were returned, all belonging to other source projects: PRJNA196801, PRJEB26154, PRJEB22538, PRJEB55189 and PRJEB57834. None supplies the Ritz study's linked processed data. |
| MGnify legacy API v1 | The valid `accession=PRJNA970614` filter and free-text project search both returned zero. A positive control `accession=PRJEB92327` returned one study, confirming that this filter was being applied. |

The [current MGnify documentation](https://docs.mgnify.org/src/docs/api.html), dated October 15, 2026, states that v1 is deprecated and frozen and excludes V6 analyses. Therefore the current v2 check was necessary. An initial v1 request using `study_accession` returned the unfiltered 5,203-study collection because that parameter was ignored. That response is explicitly marked invalid for this question in the evidence manifest and was replaced by the confirmed accession filter; it was not counted as a negative finding.

Both legacy and current-domain PMC OA-package locator URLs returned HTTP 404 in this environment. Their error bodies were saved. The usable Europe PMC complete supplementary package was obtained independently; no absence claim relies on these errors.

## Author repositories and public code indexes

The connected GitHub connector was used rather than a local GitHub token or login. Public repository metadata, contents, recursive trees, selected documentation and public issue/code searches were read only. Example call syntax was `github_fetch({url: "https://api.github.com/repos/OWNER/REPO/git/trees/main?recursive=1"})`.

Repository search enumerated 21 public repositories for thomazbastiaanssen: Tjazi, anansi, kronos, Volatility, coffee, MicroFoodDB, deleuze, scoreTools, thomazbastiaanssen, DeepLabCut, FMT_Aging, OMA, research, ECNP_resilience_network, tfs, thomazbastiaanssen.github.io, woltka, FMT_pain_analysis, Helper_functions, books and biocmask. Seven were enumerated for Chrisjrt: hafeZ, Chrisjrt, random_useful_scripts, Budding_biologist_2024, Ratatoskr, Nezam-Abadi_DSM21599_genome_MRA_2023 and Turkington_mouse_virome_2025. Enumeration alone is not a claim that every historical blob was read.

Recursive default-branch trees were inspected for ten candidate repositories, covering 871 untruncated tree entries. The research repository root and the apparently relevant Turkington repository were additionally checked. File inventories and Git object identifiers are frozen in the connector snapshots.

| Candidate | Verified content and disposition |
|---|---|
| [Chrisjrt/Turkington_mouse_virome_2025](https://github.com/Chrisjrt/Turkington_mouse_virome_2025) | GitHub reports size zero; the contents API explicitly returns repository empty. No processed data were retrieved. |
| [thomazbastiaanssen/Tjazi](https://github.com/thomazbastiaanssen/Tjazi) | The only named bundled dataset is guidebook_data.RData with tutorial caches. Its source documentation explicitly identifies 171 human schizophrenia samples from DOI 10.1038/s41467-020-15457-9. It is not the Ritz mouse study. The binary example data were not downloaded. |
| [thomazbastiaanssen/Volatility](https://github.com/thomazbastiaanssen/Volatility) | Documentation describes a 120-sample, 137-genus bacterial table from another chronic-social-defeat study, DOI 10.1016/j.psyneuen.2020.105047. It is a separate study and does not provide the target study's viral matrix or immune crosswalk. |
| [thomazbastiaanssen/anansi](https://github.com/thomazbastiaanssen/anansi) | FMT_data is documented as 36 samples from the FMT-aging study, DOI 10.1038/s43587-021-00093-9, with inferred functions and hippocampal metabolomics. It is not the target study. |
| [thomazbastiaanssen/kronos](https://github.com/thomazbastiaanssen/kronos) | Documentation explicitly labels the bundled example measurements dummy data for rhythmicity demonstrations. They were not substituted for biological observations. |
| [thomazbastiaanssen/FMT_pain_analysis](https://github.com/thomazbastiaanssen/FMT_pain_analysis) | Contains bacterial DADA2 tables, PICRUSt2-inferred functions, metadata_DNBS and pathological/therapeutic FMT analyses. No target-study viral matrix or catalog was identified in the tree. No binary/count tables from this different project were downloaded. |
| research, Helper_functions, random_useful_scripts | The inspected roots/trees contain only minimal readme/license or helper-code material, not the target data files. |
| deleuze, ECNP_resilience_network and the author website | Count-resampling software, represented-country/member files, or website assets, respectively; no target viral/count/crosswalk filename was identified in the inspected trees. Member contact data were not fetched. |

Exact public code searches returned zero results for `ViromeOTUtable`, `recal_metadata.csv`, `PRJNA970614`, `Fvtstress`, `metadata_KO_FVT.csv` and `filtered_master_taxa_table.tsv`. Additional searches for `bacteriome.virome.matching`, `StressVeronicaVirome` and `FVTStress32A` returned zero. Scoped FVT/stress searches across selected author repositories, repository searches for Ritz virome and FVT stress, and the recorded public issue searches also returned zero relevant results. These are index/default-branch searches, not a crawl of private repositories, deleted history, unindexed binaries or every author's possible account.

Guessed usernames NathanielRitz and LorraineDraper returned the connector's not-found-or-no-permission validation error, so they were not treated as verified author accounts. Public ORCID researcher-URL endpoints for the two publication identifiers returned empty URL lists and supplied no further repository identity. No account credentials or login state was changed.

## Additional DOI and web discovery

The Zenodo project-identifier search returned zero. A title/topic query for gut virome AND stress returned three current records: the already inspected script-PDF record 10460215, an unrelated book, and a literature-derived PathMap output. The latter two were not downloaded. No additional target-study processed-data deposit was identified.

DataCite full-text metadata searches for PRJNA970614 and the article DOI returned zero records. Crossref's article metadata had an empty relation object and only article HTML/PDF links. These are limited index/metadata findings; a record can omit an accession or citation string and therefore escape such a search.

Web discovery included the article DOI with data, PRJNA970614 with MGnify, the DOI with BioStudies, exact missing filenames, the former study title, and author names with GitHub restricted where practical. It found the existing publisher/PMC records, institutional bibliographic pages and the author accounts described above, without an additional verified processed matrix. Search snippets and unrelated personal-name results were not used as data evidence.

## Resource use and stopping point

The 33 direct HTTP queries saved 7,017,234 response bytes in total, including the 6,442,714-byte supplementary ZIP. The complete 52-record evidence collection, including extracted members and connector snapshots, is 11,509,954 bytes at manifest creation. All direct response caps were at most 10 MB; no raw sequencing reads or database packages were downloaded and no package was installed during this search. Existing resource guards were checked before the requests and extraction/rendering work. The largest measured process peak was 174,678,016 bytes during read-only PDF inspection; the visual rendering process peaked at 64,098,304 bytes.

The directly advertised attachments, accession-linked analysis/assembly routes, current and legacy MGnify routes, selected author repositories, and supplementary DOI/code indexes have now been checked. No recovered object changes the integrated-analysis gate. A future public release should be assessed against the actual required inputs: individual recipient abundance values, contig quality/taxonomy/host annotations, bacterial abundance values if adjustment is proposed, and explicit mouse/specimen/immune-row mappings including calibration, exclusions and pool membership. Without those inputs, additional computation on the present metadata cannot create an identifiable phage-immune association.
