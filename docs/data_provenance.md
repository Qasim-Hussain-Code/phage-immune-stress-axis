# Data provenance

The analysis uses public material from
[Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y), acquired and
reviewed on 20 October 2026. The ten required files are fixed in the
[input manifest](../data/manifests/inputs.json), which records source URLs,
byte sizes, SHA-256 checksums, download limits and transformations. Executed
size and checksum comparisons are in
[input integrity](../results/tables/input_integrity.csv).

## Sources

| Material | Source and retained form | Role |
|---|---|---|
| Article | Europe PMC full-text XML for [PMC10847049](https://europepmc.org/articles/PMC10847049) | Experimental design, methods, captions and declared data locations |
| Phenotype source data | Publisher workbook `41564_2023_1564_MOESM2_ESM.xlsx`, 23,358 bytes | Individual immune and behavioral measurements from the two experiments |
| Archived code | [Zenodo release 10460215](https://zenodo.org/records/10460215), reached through [concept DOI 10144096](https://doi.org/10.5281/zenodo.10144096) | Release catalog and `Fvtstress_scripts_040124.pdf`, 502,039 bytes |
| Metagenomic inventory | ENA run report, study XML and sample XML for [PRJNA970614](https://www.ebi.ac.uk/ena/browser/view/PRJNA970614) | Specimen identities, sample roles, time annotations and compressed-read sizes |
| 16S inventory | ENA run report for [PRJEB69687](https://www.ebi.ac.uk/ena/browser/view/PRJEB69687) | Additional sequencing inventory |
| Transcriptomic inventory | ENA run report for [PRJEB67706](https://www.ebi.ac.uk/ena/browser/view/PRJEB67706) | Additional sequencing inventory, outside the selected analysis |

The publisher workbook is retrieved from its `static-content.springer.com`
URL. Both inspected Zenodo versions contain script PDFs rather than the
referenced community tables. Sequence files were inventoried without
downloading FASTQs. [Data availability](data_feasibility.md) explains which
biological questions these inputs can support.

## Preservation and transformations

Article XML, source XLSX, script PDF, ENA XML and TSV files preserve their
retrieved bytes. The Zenodo catalog is normalized to record ID, title, license
and sorted file names, sizes and checksums. Changing usage counters and
transport formatting are excluded. The transformation is implemented in
[acquisition.py](../src/pisa/acquisition.py).

Phenotype extraction reads the unchanged workbook. Every exported observation
or missing cell retains its source sheet, row, column and cell coordinate.
Animal keys combine experiment, treatment and literal source identifier;
punctuation is preserved. BioSample attributes are derived from frozen XML
without changing source labels. Extracted PDF text is an audit aid derived
from the archived PDF, not another data file supplied by the original deposit.

The historical
[source-download ledger](../data/raw/ritz2024_archive/raw_sources.csv) records
the initial retrievals and derived extracts. The execution manifest separately
identifies the ten files required by the reproducible workflow.

## Additional search evidence

The [processed-data search](processed_data_search.md) has a separate manifest
of 52 saved responses or connector representations and a 32-member
supplementary-file inventory. The complete 6.44 MB Europe PMC supplementary
package contains the same phenotype workbook, a reporting PDF and figure/table
images. Its workbook matches the frozen XLSX exactly. These search materials
do not add individual viral abundance observations.

The complete package and extracted working files remain outside the tracked
input collection. Search manifests distinguish original response bytes,
derived text and connector representations, and retain failed access routes
without treating them as evidence of data absence.

## Attribution and reuse

Processed observations, summaries and figures are adaptations of the original
source data. Cite Ritz and colleagues for the experiment and measurements,
and the original accessions and archived scripts for their inputs. Article,
source-data and code-release terms are recorded in
[third-party notices](third_party_notices.md). The project's MIT license does
not replace those upstream terms.
