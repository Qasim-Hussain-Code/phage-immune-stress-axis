# Resource usage

The measured analysis host is Windows 11, not the Linux Mint system specified
in the project brief. Scripts are portable; Linux execution was not performed.
The initial standard `python` on PATH was an unrelated Python 2 installation;
execution used the explicitly located Python 3.14 interpreter. R 4.5.2 was found
under Program Files but was not required. Conda/Mamba executables were not on
PATH. Existing scientific libraries were used without reinstalling them.

## Measured values

| Measurement | Bytes | Decimal MB/GB |
|---|---:|---:|
| Initial installed physical RAM | 16786583552 | 16.787 GB |
| Initial available physical RAM | 375021568 | 375.0 MB |
| Initial disk free | 8897466368 | 8.897 GB |
| Operational new-storage ceiling | 4897466368 | 4.897 GB |
| Maximum measured process peak RSS | 186699776 | 186.7 MB |
| Project snapshot including Git | 14221240 | 14.22 MB |
| Project snapshot excluding Git | 12700926 | 12.70 MB |
| Disk free at snapshot | 8878968832 | 8.879 GB |

The RAM maximum includes native peaks from the runner, stages and validation
child. It is the maximum of per-process measurements, not a measured sum of
concurrent processes or whole-machine memory. Each active process is capped
at 1 GB; runner monitors child native RSS and project storage every 0.1 seconds.
Available system memory is checked with a 100 MB minimum; a low-memory failure
records a resumable failure rather than silently increasing the budget.
Resource snapshots precede later documentation/Git housekeeping and can be
regenerated. Logs and native measurements are in results/reports.

## Footprint decisions

The initial selected scientific inputs and outputs were estimated below 25 MB.
The core run used about 3 MB before optional PDF QA installation. Public raw
PRJNA970614 FASTQs total 262,211,457,238 compressed bytes; transcriptomic FASTQs
total 320,396,480,444 bytes. Neither was fetched. The 16S archive totals
1,731,077,490 bytes compressed, but reprocessing would not resolve missing viral
matrices and was not selected. No MetaPhage pipeline, GPU model, classifier
database, cloud account or paid compute service was installed or used.

PDF rendering required optional workspace-only pypdfium2: a verified 3.95 MB
wheel and about 8.09 MB installed files, plus small metadata and rendered PNGs.
This is documented in pdf_qa.md. These caches count toward the guard's budget
but are excluded from Git. A fresh scientific virtual environment is not part
of the measured execution; installing one would require a separate budget
check and several hundred MB depending on platform.

## Observed library versions

- numpy: 2.3.4
- pandas: 2.3.3
- scipy: 1.16.3
- statsmodels: 0.14.6
- matplotlib: 3.10.7
- openpyxl: 3.1.5
- PyYAML: 6.0.3
- scikit-learn: 1.7.2
- pypdf: 6.13.0
