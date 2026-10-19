# Data provenance

Acquisition and review date: 2026-10-20, Asia/Taipei. Machine UTC timestamps are
retained in execution reports; the acquisition date uses the session's local
date. The main public input manifest is `data/manifests/inputs.json`.
It contains exact URLs, stored byte sizes, SHA-256 digests, caps and
transformations. `results/tables/input_integrity.csv` records executed checks.

- Article XML: Europe PMC full text for PMC10847049, corresponding to
  [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y).
- Source workbook: publisher file `41564_2023_1564_MOESM2_ESM.xlsx` (23,358
  bytes). The working URL uses static-content.springer.com; the older
  springer-cdn.com hostname failed DNS resolution during this session.
- Code: [Zenodo concept 10144096](https://doi.org/10.5281/zenodo.10144096)
  resolves to release [10460215](https://zenodo.org/records/10460215), whose only
  file is `Fvtstress_scripts_040124.pdf` (502,039 bytes). Its record identifies
  CC BY 4.0. Both inspected versions contain script PDFs; no abundance table
  was downloaded from this archive.
- Sequencing: ENA filereport endpoints for PRJNA970614, PRJEB69687 and
  PRJEB67706 provide run/sample identity and compressed file sizes. ENA XML
  supplies PRJNA970614 study/BioSample attributes. These are public metadata;
  no FASTQ was fetched.

The frozen Zenodo catalog selects record ID, title, license, and sorted file
key/size/checksum fields. Changing usage statistics and transport serialization
are intentionally excluded. The exact deterministic transformation is in
`src/pisa/acquisition.py`. Source PDFs, XML, TSV and XLSX inputs preserve
downloaded bytes. BioSample attribute CSV is regenerated from frozen XML;
its values retain source labels. PDF text is an attributed derived audit aid,
not another uploaded file in the source release. The supplementary historical
`data/raw/ritz2024_archive/raw_sources.csv` records original audit downloads,
including PowerShell-serialized JSON and derived extracts; the execution
manifest separately identifies the required reproducible inputs.

Only small public files are tracked, with the largest approximately 0.5 MB.
Original workbook content is never edited. Source-local keys and cell locations
make the numerical path auditable. Processed tables and figures are adaptations
of the original source data and are identified as this reanalysis, without
transferring original authorship to the project author. License and attribution
details appear in `third_party_notices.md`.

No contact with upstream authors, private dataset, inferred mouse-ID repair,
raw read acquisition, paid service or external compute was used. Missing
processed inputs are listed in `results/reports/archive_availability.md`.
