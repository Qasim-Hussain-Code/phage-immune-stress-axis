# Ritz 2024 public archive and sample identity audit

Audit date: 2026-10-20 (Asia/Taipei).

## Decision

The archived materials verified here do not provide downloadable processed viral or bacterial abundance matrices. The article did analyze individual recipient bulk metagenomes and map their reads to viral contigs; it would therefore be incorrect to describe all published recipient virome measurements as pooled. The release limitation is missing processed matrices and crosswalks, rather than proof that the individual measurements never existed.

The [Zenodo concept record](https://zenodo.org/records/10144096) resolves to [version 10460215](https://zenodo.org/records/10460215). The public API and complete version listing were retrieved successfully. Both released versions contain one PDF of scripts and no data matrices:

| Version record | Published file | Bytes | Zenodo MD5 |
|---|---|---:|---|
| 10460215 | Fvtstress_scripts_040124.pdf | 502,039 | 598de702471b1b50492d8c3b8bb36c75 |
| 10144097 | Fvtstress_scripts.pdf | 414,827 | cc60ed3d0df5d733c3892015ed95af3b |

Only the latest PDF was downloaded. It has 75 pages. Its scripts refer to local inputs that are absent from both archive versions:

| PDF page | Referenced input | Relevance |
|---:|---|---|
| 1-2 | OtuTable, Table_TAXA, Sample_data | First experiment bacterial abundance, taxonomy and sample metadata |
| 9 | ViromeOTUtable, Sample_data.csv | First experiment virome abundance and metadata |
| 15 | species.tsv, recal_metadata.csv | FVT bacterial abundance, calibration/batch and Proposed_mouse_ID crosswalk |
| 22 | filtered_master_taxa_table.tsv | Viral taxonomy/host linkage input |
| 23 | bacteriome.virome.matching.fvt.stress.051022.csv | Bacteriome/virome matching input |
| 37 | RNASEQ/gene_counts.txt, metadata_KO_FVT.csv | Brain RNA abundance and RNA/sample crosswalk |

These filenames are evidence that the analysis depended on unavailable local files. The PDF does not embed the referenced count matrices. Exact-name web searches for Fvtstress, recal_metadata.csv, metadata_KO_FVT.csv and StressVeronicaVirome returned no alternative public deposit in this audit. This is a bounded search finding, not a claim that no copy can exist anywhere.

## Public sequence manifests

Small ENA run metadata TSVs were downloaded. No FASTQ reads were downloaded.

| Project | Modality | Runs / unique samples | Listed compressed FASTQ bytes | Metadata bytes |
|---|---|---:|---:|---:|
| PRJNA970614 | Bulk metagenome / virome study | 104 / 104 | 262,211,457,238 | 24,906 |
| PRJEB69687 | 16S amplicon | 52 / 52 | 1,731,077,490 | 14,914 |
| PRJEB67706 | Brain RNA sequencing | 74 / 74 | 320,396,480,444 | 21,682 |

The manifests record run_accession, sample_accession, sample_alias, experiment_alias, library_name, library_source, library_strategy, library_layout, fastq_bytes and fastq_ftp. Byte totals sum both mates across listed runs; they are transfer sizes, not estimated RAM or computational requirements.

## PRJNA970614 identities and pooling

All 104 BioSample XML records were also retrieved and parsed. Public attributes include sample_type, replicate_num and gavage_status. Individual aliases ending A explicitly have gavage_status=After and aliases ending B have gavage_status=Before. This timepoint assignment is confirmed by the public metadata, rather than inferred from the suffix alone.

| Public sample_type | Individual Before aliases | Individual After aliases | Group pools | Gavage samples |
|---|---:|---:|---:|---:|
| Control | 10 | 10 | 2 | 0 |
| Control stress | 10 | 8 | 2 | 0 |
| FVT stress | 10 | 9 | 2 | 0 |
| hkFVT stress | 10 | 10 | 2 | 0 |
| FVT gavage | 0 | 0 | 0 | 9 |
| hkFVT gavage | 0 | 0 | 0 | 10 |

Thus the manifest includes 77 individual recipient sample aliases, 8 recipient group-pool aliases, and 19 gavage aliases. Pool aliases explicitly contain Beforepool or Afterpool and have replicate_num=NA. Public metadata alone do not establish the exact member mice for each pool.

Using only exact public (sample_type, replicate_num) keys yields 35 apparent Before/After pairs: Control 8, Control stress 8, FVT stress 9 and hkFVT stress 10. Seven keys have only one listed timepoint. These counts are a metadata audit, not an analysis-ready longitudinal cohort: the unavailable recal_metadata.csv contains a Proposed_mouse_ID field, and the control aliases include ambiguous labels such as 191, 192, 19x2, 20x1 and 1x2. They must not be silently repaired, collapsed or reassigned to mice.

The same replicate_num can occur in different sample_type groups. Joining on the number alone would be unsafe. The public records contain no cytokine, flow-cytometry or behavioural measurements and no explicit crosswalk to the spreadsheet source-data rows.

## Source workbook identity check

The separately retrieved source_data.xlsx was inspected read-only. The FVT study II sheet has 30 nonempty data rows (10 ctr, 10 ctr_stress, 10 fvt_stress); its larger formatted worksheet range must not be mistaken for additional subjects. There are no nonempty hkFVT outcome rows in this sheet.

The source Control IDs are 1.1, 1.2, 2.1, 2.2, 3, 19.1, 19.2, 20.1, 20.2 and 21. The ENA Control replicate_num labels instead include 11, 12, 191, 192, 19x2, 1x2, 202, 20x1, 21, 22, 2x1 and 3. Only 3 and 21 match literally. Removing punctuation or interpreting x as a decimal marker would invent a crosswalk.

For the ten Control stress and ten FVT stress spreadsheet IDs, the integer labels match public replicate_num strings within the corresponding treatment. These are potential metadata matches only. They do not supply viral/bacterial abundance data, and do not justify extending a mapping to the ambiguous Control labels. No phage-immune or bacteria-immune association can be computed from the verified archive files alone.

## Provenance and limits

The manifest data/raw/ritz2024_archive/raw_sources.csv records exact source URLs, saved byte sizes, SHA256 checksums, access date and whether each file is downloaded or derived. The archived PDF's SHA256 is 1a510d1e8691d01856383446999a5af57776b65d68504f73a54ef28733c59048. The extracted PDF text and flattened sample-attribute CSV are explicitly marked derived. The two Zenodo JSON files were serialized with PowerShell ConvertTo-Json; their checksums describe the saved serializations, not an original HTTP byte stream.

The public ENA data demonstrate that sequence reads are available, but reconstructing abundance matrices from hundreds of gigabytes of raw reads is outside a laptop-feasible metadata audit. The immediate prerequisites for integrated phage-host-immune analysis are the processed individual viral abundance matrix, bacterial abundance matrix, viral annotation/host table, and verified mouse/sample/source-row crosswalk including exclusions, calibration and pool membership. This report does not assume these prerequisites are available merely because the scripts reference them.
