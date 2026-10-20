# Gut phageome stability and stress-related immune responses

Researcher and project author: **Qasim Hussain**
([Qasim-Hussain-Code](https://github.com/Qasim-Hussain-Code)).

This repository contains a completed public-data feasibility audit and a
restricted, exploratory immune source-data reanalysis, with a separate
reconstruction of selected original statistical calculations. The proposed association
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

An [expanded processed-data search](docs/processed_data_search.md) records 52
saved evidence records. Its complete supplementary package contains the same
phenotype workbook, a reporting summary and figure/table images, with no
additional processed community matrix. Accession-linked analysis routes,
selected author repositories and secondary indexes did not yield a verified
replacement for the missing inputs. This is a bounded search result. A newer
[prenatal-stress candidate](docs/new_prenatal_stress_candidate.md) remains
unresolved; its preview and abstract do not establish public, linked recipient
virome and immune measurements.

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
16 defeat sessions on study day 19; it is not a baseline before chronic stress.
Spleens were collected on day 23, after 19 defeat sessions, for subsequent
ex vivo cytokine assays. These assays are not contemporaneous blood measurements.
Original source
values remain unchanged. No missing outcome or below-detection value is
replaced with zero. All observed values are retained.

For each endpoint, Control Stress minus Control and FVT Stress minus Control
Stress are analyzed using Welch mean differences, pointwise 95% intervals and
two-sided P values. One six-test Benjamini-Hochberg family is used. Rank tests
and leave-one-observed-animal-out fits are sensitivity checks. Endpoint choices
followed reading the published results and precede the present calculations;
this is exploratory reanalysis, not preregistered confirmation. Cage allocation,
original outlier flags and quantitative detection thresholds are unavailable.
Stressed animals were singly housed while unstressed controls remained group
housed, so the stress-versus-control comparison also includes housing differences.
FVT Stress and Control Stress share the reported single-housing regime.

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
from the article's Tukey P=0.106: Welch P=0.01265 here. The separate
three-group pooled-variance reconstruction gives Tukey-Kramer P=0.106409 from
the same source observations. Variance estimation and multiplicity explain the
difference; no additional exclusions are needed. This is not a correction of
the original calculation.
Relative cell percentages do not establish absolute cell expansion.

All nine selected caption-statistic checks match reported precision. Across
those statistics and nine source group summaries, 17 of 18 checks match. One
printed mean is retained as a discrepancy: FVT unstimulated TNF-alpha averages
27.8492778 pg/mL in the workbook, rounding directly to 27.8, while the original
table image prints 27.9. No source value or rounding tolerance was changed.
The original complete BH family remains unreconstructed. See the
[independent review](docs/original_analysis_review.md) and
[replication table](results/tables/original_method_replication.csv).

Two [post-hoc descriptive checks](docs/phenotype_robustness.md) add no hypothesis
tests or imputed observations. If each missing percentage assay has a well-defined
value in [0,100], the FVT-minus-stress mean difference among the ten source rows
per group lies between 1.166 and 11.166 percentage points for LY6Chi monocytes,
and between 8.323 and 18.323 points for CD62L-positive monocytes. These bounds
retain positive direction under that assumption; they are not confidence
intervals or significance claims. No finite TNF-alpha bounds are justified.
The TNF-alpha FVT rank comparison has 8 greater and 64 lesser cross-group pairs,
with no ties. Those 72 pairs reuse 17 animals and are not independent replicates.

These are separate immune comparisons. They do not establish a specific phage
effect, bacterial mediation, immune resilience or a causal gut-brain mechanism.
See [full results](docs/results.md), [limitations](docs/limitations.md),
[methods](docs/methods.md) and [novelty assessment](docs/novelty_assessment.md).

## Figures and machine-readable results

- [Figure 1](figures/figure1_design.png): study design and public-data coverage.
- [Figure 4](figures/figure4_immune.png): observed immune values and uncertainty.
- [Figure 5](figures/figure5_linkage_limit.png): why no phage-immune model was fitted.
- [Figure 7](figures/figure7_robustness.png): influence of omitting each animal.
- [Figure 8](figures/figure8_method_comparison.png), original-method comparison: contrasts the fixed Welch intervals
  with the original pooled-variance Tukey-Kramer intervals, using identical
  observations and point estimates with different interval coverage scopes.

All five actual PDF pages were rendered and visually inspected. The
[review record](docs/pdf_qa.md) binds that inspection to the current PDF hashes.

Each figure has a vector PDF and `results/tables/figureN_data.csv`.
Figure 4 contrast intervals are in `immune_contrasts.csv`. Composition,
stability and bacteriome figures 2, 3 and 6 are excluded because their necessary
processed inputs were not retrieved. Their absence is intentional.

The separate [software calibration design](docs/calibration_design.md) specifies
four synthetic all-null scenarios, including skew, unequal variance and an
artificial cluster dependence stress test. Every simulation row is labeled
`synthetic_not_biological`. The default full benchmark is 20,000 replicates per
scenario in batches no larger than 500. The executed benchmark used seed
20261020 and completed all 20,000 replicates in each scenario. Its all-null BH
family rejection probabilities were 0.04620 for equal-variance Gaussian,
0.04795 for unequal-variance Gaussian, 0.01150 for centered lognormal and
0.16495 for artificial clusters with ICC 0.5. Exact Wilson intervals and
coverage results are in the [software-only report](results/reports/software_calibration.md).
These Monte Carlo intervals describe simulation error; no real cage structure
or biological power is inferred. The artificial clusters do not describe the
original singly housed stressed groups.

## Reproduction

Use Python 3.11 or newer. Version 0.2.1 was executed with CPython 3.14.0
on Windows 11 and CPython 3.14.4 in the existing Ubuntu WSL2 distribution.
The Linux check newly installed all 21 pinned distributions in an isolated
environment from verified official wheels. The Windows reference used its
existing packages. These runs share one physical host. Exact environment,
installation and build evidence is in the [environment report](docs/environment_reproduction.md)
and [Linux setup report](docs/linux_environment_setup.md). Do not use an
unrelated Python 2 installation on PATH. Small frozen public inputs are
included for offline reproduction; large raw reads and reference databases
are excluded.

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

The environment and installation commands create a fresh environment. Check free
disk/RAM before installing; a fresh environment is expected to require several
hundred MB, depending on platform. Cached inputs are verified by SHA-256.
Omit `--offline` only to retrieve a missing frozen input. Changed public content
fails checksum validation and requires a documented new audit. Resume checks
code/config/input fingerprints and declared output hashes. Pilot stops after
phenotype preparation and does not imply that immune analysis or figures ran.
Per-invocation records distinguish newly executed stages, verified resumed
outputs, validation-only runs, pilots and failures. An earlier successful run
does not establish completion of the current invocation. See
[reproduction validation](docs/reproduction_validation.md).

The executed [command-mode checks](results/reports/mode_checks.json) also verify
that validation leaves scientific files unchanged, the pilot stops after stage
six, and an unchanged full resume verifies all ten stages without recomputation.

`--threads 4` is a ceiling interface; the selected small workflow executes
serially and restricts numerical-library threads to one. It monitors native
per-process peaks and sampled concurrent process-family RSS, project storage
and available memory. Downloads are capped and a 4 GB free-disk reserve is
preserved. The storage ceiling is initialized from the current host and checkout
as the smaller of 10 GB or free space minus the reserve; a persistent local
baseline prevents a restart from resetting that allowance. Historical
`environment_initial.json` is provenance, not another checkout's resource budget.
Sampled aggregate RSS is not an exact whole-machine peak. Raw PRJNA970614 FASTQs
alone total 262.211 GB compressed and were
excluded. See [resource measurements](docs/resource_usage.md).

During the final Windows fresh-checkout reproduction, sampled concurrent
process-family RSS peaked at 366.9 MB and the largest native per-process peak
was 220.0 MB. Project storage peaked at 196.5 MB including disposable files,
then fell to 187.9 MB after cleanup, with 13.54 GB free. The separate Linux
attempt used about 481.2 MB in its complete native directory before packaging;
its outer guest monitor sampled 337.6 MB concurrent RSS. These scopes are
reported separately, and guest RSS is not added to virtual-machine memory.
See the [Linux execution evidence](docs/linux_reproduction_validation.md).

## Validation and publication status

Version 0.2.1 collected 135 tests on each platform, with zero failures or
errors: Windows executed 129 and skipped six Linux-only tests; Linux executed
126 and skipped nine Windows-only tests. A fresh Git archive of commit
`06b7cab84937c174c3197ba63d560ddc9cc70b1c` executed all ten stages offline
without resume on both platforms. All 30 Windows scientific CSV and PNG/PDF
outputs matched the reference by exact SHA-256. On Linux, all 20 CSVs passed
the fixed exact-field/numeric-tolerance policy: 18 were byte-identical and two
had derived-value differences at most 3e-14. All ten changed Linux figure
files passed actual visual review. Linux outputs are not byte-identical overall.

The [Windows evidence](results/reports/reproduction_check.json) and
[Linux validation report](docs/linux_reproduction_validation.md) record source,
inputs, comparisons, resources and completed cleanup. The Linux environment
was independently installed on the same host; no separate physical-machine,
Linux Mint, macOS or remote CI execution is claimed. The suite includes
independent SciPy/statsmodels comparisons, original-method reconstruction,
analytical identities, missingness, pooling, inoculum, acquisition, resource and
resume safeguards. Current executed counts and outcomes are in
`results/reports/validation_summary.json`; current completion is established by
the matching invocation record. Synthetic fixtures and calibration simulations
are exclusively software checks. The measured control groups provide treatment
references. Independent biological negative and positive controls for the
unmeasured phage-stability association are unavailable.

The local release is validated. Authorized GitHub CLI access has been verified;
publication is in progress. Consult [publication status](docs/publication_status.md)
for the verified remote outcome.

## Provenance, license and attribution

Project code is MIT licensed. Upstream article/source data and the archived
code PDF retain their CC BY 4.0 licenses and attribution; see
[data provenance](docs/data_provenance.md) and [third-party notices](docs/third_party_notices.md).
This does not relicense upstream work. Cite Ritz and colleagues for the
experiment, the original accessions and archived scripts for their inputs,
and the software used. Project authorship is Qasim Hussain alone. AI assistance
was used for coding, audit support and drafting; it does not constitute human
authorship or independent experimental validation.
