# Gut phageome stability and stress-related immune responses

Researcher and project author: **Qasim Hussain**
([Qasim-Hussain-Code](https://github.com/Qasim-Hussain-Code)).

This repository contains a completed public-data feasibility audit and a
restricted, exploratory immune source-data reanalysis. The proposed association
between gut phageome stability and stress-related immune disruption could not
be tested from the retrieved processed inputs. That is a data availability
conclusion, not evidence of no biological relationship.

## Research question and biological context

Is preservation of a mouse's gut phage community during chronic stress
associated with less immune disruption, after considering treatment and
bacterial variation? Phages may alter bacterial ecology, but a viral community
change alone does not identify bacterial function, immune regulation or a
gut-brain mechanism. Temporal stability requires repeated measurements of the
same individual. Cross-sectional similarity, group dispersion and alpha
diversity are different quantities.

The source study is [Ritz et al., Nature Microbiology 9, 359-376
(2024)](https://doi.org/10.1038/s41564-023-01564-y). Its stress, transplantation,
immune and behavioral results are upstream findings, not discoveries of this
repository. The reference research repository was
[reviewed before implementation](docs/reference_repository_review.md).

## Data and linkage findings

| Source | Retrieved material | Observational unit |
|---|---|---|
| Article / PMC10847049 | Full article XML and experimental methods | Published design and assay descriptions |
| Supplementary source workbook | 20 initial-study and 30 FVT-study animal rows | Source-local individual mouse row; endpoint missingness varies |
| [Zenodo 10460215](https://zenodo.org/records/10460215) | 75-page code PDF and frozen file catalog | Scripts referencing absent processed matrices and metadata |
| [PRJNA970614](https://www.ebi.ac.uk/ena/browser/view/PRJNA970614) | 104 run records and BioSample metadata | 77 individual recipient bulk specimens, 8 pools, 19 inocula |
| [PRJEB69687](https://www.ebi.ac.uk/ena/browser/view/PRJEB69687) | 52 run records | Initial-study 16S metadata; no source-row crosswalk inferred |
| [PRJEB67706](https://www.ebi.ac.uk/ena/browser/view/PRJEB67706) | 74 run records | Brain transcriptomic metadata, outside selected analysis |

The initial-study captions imply 12 pool-by-time profiles: three per group at
two times. Their membership and deposited profile crosswalk are unresolved.
They are not 12 independently verified animals or longitudinal pools.

The FVT study contains both pooled enriched viromes and individual bulk-derived
viral signals. The inspected code releases contain only script PDFs. Their
viral/bacterial matrices, annotations and animal recalibration map are absent.
Control identifiers such as `1.1`, `19.2`, `19x2` and `1x2` cannot be repaired by
punctuation removal or presumed renumbering. No profile is assigned using row
order. Inocula are never treated as recipient communities.

**Retrieved processed viral profiles: 0. Verified usable virome-immune matches:
0. Measured temporal stability estimates: 0.** Same-row immune and behavioral
measurements are linked only within their source sheet. Sequencing specimens,
mouse rows, pools, technical observations and complete cases remain distinct.

See the mandatory [feasibility gate](results/reports/data_feasibility.md),
[sample audit](results/reports/sample_linkage.md),
[machine-readable linkage map](results/tables/sample_linkage_audit.csv) and
[archive audit](results/reports/archive_availability.md).

## Hypotheses and selected analysis

The primary within-mouse stability/immune hypothesis and H1-H3/H5 viral
composition, reference-deviation, adjustment and filtering hypotheses are
untestable from these inputs. H4 permits only a separate immune treatment
comparison. Exact criteria are in
[hypothesis_eligibility.csv](results/tables/hypothesis_eligibility.csv).
A [focused alternative search](docs/alternative_dataset_search.md) did not
verify a suitable replacement with public processed profiles and explicit
immune linkage. This was not a systematic review or proof that none exists.

The restricted analysis uses three biologically motivated FVT-study outcomes:
basal LY6Chi monocyte proportion, basal CD62L-positive monocyte fraction, and
unstimulated splenocyte TNF-alpha. “Basal” means before forced swim, after
chronic stress; it is not a baseline before chronic stress. Original source
values remain unchanged. No missing outcome or below-detection value is
replaced with zero. All observed values are retained.

For each endpoint, Control Stress minus Control and FVT Stress minus Control
Stress are analyzed using Welch mean differences, pointwise 95% intervals and
two-sided P values. One six-test Benjamini-Hochberg family is used. Rank tests
and leave-one-observed-animal-out fits are sensitivity checks. Endpoint choices
followed reading the published results and precede the present calculations;
this is exploratory reanalysis, not preregistered confirmation. Cage allocation,
original outlier flags and quantitative detection thresholds are unavailable.

## Primary results

| Outcome | Contrast | n | Difference (95% CI) | BH q |
|---|---|---:|---|---:|
| LY6Chi monocytes | Stress minus Control | 10 / 10 | -2.034 percentage points (-3.683, -0.385) | 0.0395 |
| LY6Chi monocytes | FVT Stress minus Stress | 9 / 10 | +1.556 percentage points (0.389, 2.724) | 0.0379 |
| CD62L-positive monocytes | Stress minus Control | 10 / 10 | -1.760 percentage points (-7.583, 4.062) | 0.5265 |
| CD62L-positive monocytes | FVT Stress minus Stress | 9 / 10 | +15.874 percentage points (7.726, 24.021) | 0.00480 |
| Unstimulated splenocyte TNF-alpha | Stress minus Control | 8 / 9 | +67.543 pg/mL (-26.175, 161.262) | 0.1591 |
| Unstimulated splenocyte TNF-alpha | FVT Stress minus Stress | 9 / 8 | -74.131 pg/mL (-167.776, 19.513) | 0.1551 |

CD62L is higher with FVT without an established stress-induced deficit, so this
is not evidence of reversal of that deficit. TNF-alpha is sensitive to the
estimand: its FVT rank-test sensitivity q is approximately 0.0110, whereas the
raw mean contrast remains imprecise. The monocyte FVT comparison also differs
from the article's Tukey P=0.106: Welch P=0.01265 here. Test families, unequal
variance treatment and upstream exclusions differ. Neither result is hidden,
and the difference is not presented as a correction of the original research.
Relative cell percentages do not establish absolute cell expansion.

These are separate immune comparisons. They do not establish a specific phage
effect, bacterial mediation, immune resilience or a causal gut-brain mechanism.
See [full results](docs/results.md), [limitations](docs/limitations.md),
[methods](docs/methods.md) and [novelty assessment](docs/novelty_assessment.md).

## Figures and machine-readable results

- [Figure 1](figures/figure1_design.png): study design and public-data coverage.
- [Figure 4](figures/figure4_immune.png): observed immune values and uncertainty.
- [Figure 5](figures/figure5_linkage_limit.png): why no phage-immune model was fitted.
- [Figure 7](figures/figure7_robustness.png): influence of omitting each animal.

Each figure has a vector PDF and `results/tables/figureN_data.csv`.
Figure 4 contrast intervals are in `immune_contrasts.csv`. Composition,
stability and bacteriome figures 2, 3 and 6 are excluded because their necessary
processed inputs were not retrieved. Their absence is intentional.

## Reproduction

Use Python 3.11 or newer. The recorded execution used Python 3.14 on Windows 11
and existing NumPy, SciPy, Matplotlib, openpyxl, PyYAML and statsmodels. The
portable scripts support Linux; an actual Linux execution was not performed.
Do not use an unrelated Python 2 installation that happens to be on PATH.
Optional PDF text extraction uses pypdf. Exact observed versions are in
`data/manifests/environment_initial.json`. Small frozen public inputs are
included for offline reproduction; large raw reads and reference databases are
not included or downloaded.

```bash
python scripts/environment_probe.py
python -m venv .venv
# Linux: source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/run_all.py --config config/analysis.yaml --threads 4 --offline
python scripts/run_all.py --config config/analysis.yaml --threads 4 --offline --resume
python scripts/run_all.py --config config/analysis.yaml --threads 4 --offline --validate-only
python scripts/run_all.py --config config/analysis.yaml --threads 4 --offline --mode pilot
```

The first two installation commands are instructions for a fresh environment;
no scientific packages were installed during the recorded analysis. Check free
disk/RAM before installing; a fresh environment is expected to require several
hundred MB, depending on platform. Cached inputs are verified by SHA-256.
Omit `--offline` only to retrieve a missing frozen input. Changed public content
fails checksum validation and requires a documented new audit. Resume checks
code/config/input fingerprints and declared output hashes. Pilot stops after
phenotype preparation and does not imply that immune analysis or figures ran.

`--threads 4` is a ceiling interface; the selected small workflow executes
serially and restricts numerical-library threads to one. It monitors native
child RSS and project storage, rejects oversized downloads, preserves a 4 GB
free-disk reserve and enforces the smaller of 10 GB or available budget. Initial
free disk was only 8.897 GB, so the actual initial new-storage limit was
4.897 GB. Raw PRJNA970614 FASTQs alone total 262.211 GB compressed and were
excluded. See [resource measurements](docs/resource_usage.md).

## Validation and publication status

The full restricted pipeline and offline pilot completed. The initial suite
passed all 25 tests, including independent SciPy/statsmodels comparisons,
analytical log-ratio identities, missingness, pooling and inoculum safeguards.
Final executed counts are in `results/reports/validation_summary.json`.
Synthetic fixtures are exclusively software checks. Negative biological
controls are the measured control groups; an independent positive biological
control for a phage-stability association is unavailable.

The repository is prepared locally. GitHub publication is conditional on
available authorized creation/push access; consult
[publication status](docs/publication_status.md) for the actual outcome.

## Provenance, license and attribution

Project code is MIT licensed. Upstream article/source data and the archived
code PDF retain their CC BY 4.0 licenses and attribution; see
[data provenance](docs/data_provenance.md) and [third-party notices](docs/third_party_notices.md).
This does not relicense upstream work. Cite Ritz and colleagues for the
experiment, the original accessions and archived scripts for their inputs,
and the software used. Project authorship is Qasim Hussain alone. AI assistance
was used for coding, audit support and drafting; it does not constitute human
authorship or independent experimental validation.
