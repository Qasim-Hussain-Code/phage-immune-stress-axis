# Resource usage

Invocation: 20261020T121334137518Z_3504. Status: completed_restricted_analysis.
Current measured platform: Windows-11-10.0.26300-SP0. Python: 3.14.0 (tags/v3.14.0:ebf955d, Oct  7 2025, 10:15:03) [MSC v.1944 64 bit (AMD64)].
Historical `environment_initial.json` records the original research execution only. It does not govern this checkout's resource budget. The ignored local persistent baseline is bound to checkout location, filesystem and host. A fresh checkout measures its own available space. Restarting the same checkout does not reset its budget.

| Measurement | Bytes | Decimal MB/GB |
|---|---:|---|
| Local baseline disk free | 14208532480 | 14208.532 MB / 14.208532 GB |
| Conservative total-project storage ceiling | 10000000000 | 10000.000 MB / 10.000000 GB |
| Maximum measured native per-process RSS this invocation | 218083328 | 218.083 MB / 0.218083 GB |
| Maximum sampled concurrent process-family RSS | 322330624 | 322.331 MB / 0.322331 GB |
| Project snapshot including Git | 187131006 | 187.131 MB / 0.187131 GB |
| Project snapshot excluding Git | 184964706 | 184.965 MB / 0.184965 GB |
| Disk free at snapshot | 13669621760 | 13669.622 MB / 13.669622 GB |
| Available system memory at snapshot | 2298576896 | 2298.577 MB / 2.298577 GB |

Configured minimum free disk: 4000000000 bytes. Per-process ceiling: 1000000000 bytes. Aggregate process-family ceiling: 1000000000 bytes. Available-memory floor: 100000000 bytes.
Concurrent-memory samples: 139; maximum unreadable or already-exited processes in one sample: 1.
The aggregate statistic sums simultaneous current RSS across runner descendants. It is sampled at approximately 0.1-second intervals during child execution and is not an exact whole-machine peak or an operating-system allocation limit. Brief processes or allocation spikes between polls may be missed. Native per-process peaks are reported separately; historical peaks from resumed stages are not counted as newly measured current-run peaks.
The storage cap conservatively counts the entire checkout, including existing inputs, Git, environments, caches and temporary products inside it. Free disk is checked independently. Pre-existing software outside the checkout is not included in project bytes; installing a fresh environment requires a separate disk/RAM check. No raw sequencing data or reference database is acquired by the selected workflow.

## Observed local package versions

- contourpy: 1.3.3
- cycler: 0.12.1
- et_xmlfile: 2.0.0
- fonttools: 4.60.1
- kiwisolver: 1.4.9
- matplotlib: 3.10.7
- numpy: 2.3.4
- openpyxl: 3.1.5
- packaging: 25.0
- pandas: 2.3.3
- patsy: 1.0.2
- pillow: 12.0.0
- pyparsing: 3.2.5
- pypdf: 6.13.0
- python-dateutil: 2.9.0.post0
- pytz: 2025.2
- PyYAML: 6.0.3
- scipy: 1.16.3
- six: 1.17.0
- statsmodels: 0.14.6
- tzdata: 2025.2

## Invocation status

Invocation: 20261020T121334137518Z_3504. Mode: full. Status: completed_restricted_analysis.
10 stages executed and 0 stages resumed after verifying their declared outputs and upstream dependencies.
All selected restricted-workflow stages completed or were verified from cache. Scientifically excluded analyses remain exclusions.
Validation (executed in this invocation): 131 tests, 0 failures, 0 errors, 6 skipped.
Prior visual review dated 2026-10-20T06:23:59.007316+00:00 matches the current bytes of 5 PDF files. This is not a new visual review by this invocation.

Publication status is documented separately in `docs/publication_status.md`; executing this pipeline does not establish a GitHub publication.
Researcher and sole project author: Qasim Hussain. No causal phage mechanism or stability-immune association is established by this restricted analysis.
