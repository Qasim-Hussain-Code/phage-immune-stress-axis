# Public-data follow-up: 23 October 2026

A focused recheck of the Ritz archive and the unresolved Chen prenatal-stress
study recovered no newly usable processed viral–immune pairing. The checks
concern data access, not a new biological analysis. The broader
[20 October search](data_search.md) and its source ledgers remain unchanged.

## Ritz: the advertised files are unchanged

The [Zenodo version inventory](https://zenodo.org/api/records/10460215/versions)
lists two published versions. Each contains one script PDF: 414,827 bytes in
record 10144097 and 502,039 bytes in record 10460215. The inventory marks
10460215 as the latest version. Its current catalog, after the project's
documented normalization, exactly matches the frozen catalog used by the
analysis. No abundance matrix or animal crosswalk appears in those file lists.
The separate latest-version endpoint returned a server error; the version
assessment relies on the successfully retrieved inventory.

The [BioStudies article record](https://www.ebi.ac.uk/biostudies/api/v1/studies/S-EPMC10847049)
is byte-identical to the 20 October response. It lists the reporting PDF and
phenotype workbook. Both ENA analysis-file reports—
[PRJNA970614](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJNA970614&result=analysis&format=tsv)
and [PRJEB69687](https://www.ebi.ac.uk/ena/portal/api/filereport?accession=PRJEB69687&result=analysis&format=tsv)—
again contain only column headers, without submitted analysis-file rows.
These results do not repeat the complete supplementary-package inspection or
the earlier repository search. They leave the missing processed matrices and
verified immune-animal crosswalk unresolved.

## Chen: methods and individual pairing remain unverified

For [Chen et al. (2026)](https://doi.org/10.1016/j.bbi.2026.106532), the
advertised [Elsevier XML route](https://api.elsevier.com/content/article/PII:S0889159126002801?httpAccept=text/xml)
returned the same 1,865-byte bibliographic response as before, without an
article body, supplement inventory or individual observations. Crossref,
Europe PMC and PubMed metadata supplied no additional processed-data location.
PubMed LinkOut continued to list subscription article providers; its general
MedlinePlus Stress link is not a study-data source.

Exact-DOI searches of
[BioStudies](https://www.ebi.ac.uk/biostudies/api/v1/search?query=%2210.1016%2Fj.bbi.2026.106532%22)
and [Zenodo](https://zenodo.org/api/records?q=%2210.1016%2Fj.bbi.2026.106532%22&size=25)
returned no indexed records. Those query results do not exclude deposits that
omit the DOI. DataCite returned a server error, and the bioRxiv/medRxiv requests
timed out; no fresh result count was obtained from those routes. The direct
publisher and full-text requests failed, the CSU repository could not be
searched, and the Hunan Normal University library response remained a
JavaScript shell without an advertised target-data link in the returned HTML.

The on-request data statement described in the
[earlier candidate assessment](new_prenatal_stress_candidate.md) comes from an
older indexed publisher preview. Full text was not newly recovered here.
Recipient immune assays, sampling times, animal identifiers and the crosswalk
to individual viral abundances therefore remain unverified. Chen remains a
relevant unresolved candidate, rather than a scientifically excluded study.

## Evidence and scope

The [dated request ledger](../data/manifests/public_data_recheck_20261023.json)
records 21 direct requests: 13 successful responses totalling 78,828 bytes,
four HTTP errors and four requests without a response. It retains URLs,
timestamps, response sizes and hashes where available, selected contents and
their interpretation. Error responses and timeouts are distinguished from
valid empty searches. Raw response bodies are outside the tracked inputs.

Requests were bounded to at most 2 MB each. No raw reads, new software or
biological observations were acquired, and no authors were contacted. A usable
release would still need individual viral abundances, times and identifiers,
measured immune values and a verified animal-level crosswalk; temporal
stability would additionally require repeated individual viral profiles.
