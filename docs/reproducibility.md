# Reproducing the study

The workflow extracts the frozen phenotype workbook, audits sequencing and
sample metadata, calculates the selected immune contrasts and diagnostics,
runs numerical checks, and regenerates the figures. Viral community analyses
remain excluded until their missing inputs are supplied.

## Installation and execution

Use Python 3.11 or newer. The executed environments used CPython 3.14.0 on
Windows and CPython 3.14.4 in Ubuntu WSL2. Package versions are pinned in
[requirements.txt](../requirements.txt). Check available memory and disk before
installing; a fresh environment requires several hundred MB.

On Linux or WSL:

```bash
python3 scripts/environment_probe.py
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python scripts/run_all.py --config config/analysis.yaml --threads 1 --offline
```

On Windows PowerShell:

```powershell
py -3 scripts/environment_probe.py
py -3 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python scripts/run_all.py --config config/analysis.yaml --threads 1 --offline
```

The ten small frozen input files are included. Offline mode requires their
recorded sizes and SHA-256 checksums to match. Omit `--offline` to retrieve a
missing input from its recorded public source; changed source content stops
the run. The workflow does not download raw reads or a viral reference database.

## Commands and outputs

Add an option to the full command above for a different execution mode:

| Option | Behavior |
|---|---|
| `--resume` | Verify fingerprints and declared output hashes, then reuse valid stages |
| `--validate-only` | Run software checks while preserving scientific inputs, tables and figures |
| `--mode pilot` | Stop after stage six, once phenotype extraction is complete |

The full command runs all ten stages, including the 20,000-replicate-per-scenario
synthetic calibration. The selected workflow is serial; the worker argument is
a ceiling and numerical libraries use one thread. Main outputs are
[immune estimates](../results/tables/immune_contrasts.csv),
[sensitivity checks](../results/tables/immune_sensitivity.csv),
[source-linked observations](../data/processed/immune_long.csv),
[scientific results](results.md) and five PNG/PDF figure pairs.

The runner writes the latest status to
[run_status.json](../results/reports/run_status.json) and keeps a separate record
for each invocation. These distinguish newly executed stages from verified
cached stages, pilots and validation-only runs. A successful cached resume is
not a fresh replay.

## Reproduction evidence

The latest full Windows workflow completed on 23 October 2026 with the conditional
design/scale sensitivities and revised figures. All ten stages executed without
resume; 219 tests were collected, 213 executed and six Linux-only cases skipped,
with zero failures or errors. There are now 29 scientific CSVs and ten figure
files. The six original raw-scale contrasts, their intervals, P and q values
and the source observations are unchanged from `f20cbdb`. The original four
calibration scenarios are preserved; the controls-only scenario is appended.
The ten frozen inputs still match their byte hashes. The
[latest invocation](../results/reports/run_status.json) identifies the source,
and the [comparison record](../results/reports/design_sensitivity_validation.json)
retains the hashes, CSV-record comparisons and scope. Explicit LF serialization
avoids native Windows CSV/JSON newline translation. Historical byte-equality
claims remain specific to their recorded working/reference files and source
normalization rules; CSV-record equality is reported separately.

The earlier 23 October release-check run collected 180 tests, executed 174 and
skipped six. Its [comparison record](../results/reports/invocation_binding_validation.json)
retains the earlier 30-file exact comparison and is not the current sensitivity run.

The 22 October runs revised the research narrative and eligibility explanation,
then clarified defeat-day terminology. The earlier eligibility edit changed
only its question and missing-input explanation; the final timing-wording run
reproduced all 30 scientific files exactly. Those runs collected 174 tests,
executed 168 and skipped six. Their dated journal records are retained.

The separate fresh-checkout Windows and Linux replays below were completed on
21 October 2026 at commit `eb7ba6c8b945670a1f55c493d89435f36750900c`.
They precede the revised report text, eligibility wording and source-to-invocation
release check, new sensitivities and revised figures. Those later revisions
have not been rerun on Linux.

The [Windows replay report](../results/reports/reproduction_check.json) identifies
the Git revision exported to a disposable checkout. It removes generated
scientific files and stage receipts, executes all ten stages offline without
resume, and compares 30 scientific files by exact SHA-256. The
[Linux report](../results/reports/linux_reproduction_check.json) identifies its
separate source export, newly installed dependency environment and comparisons.
Both use the same physical host.

Windows reproduced all 30 scientific files exactly. Linux passed all 20 CSV
comparisons: 18 were byte-identical and two differed only in derived floating
values by at most 3e-14. The fixed policy preserves observations, identifiers,
counts and schemas exactly; only listed derived fields receive numerical
tolerances. Linux figure files differ from Windows. All ten match the Linux
files covered by the retained visual review. Exact source revisions, dates and
figure acceptance records are in the [Windows](reproduction_validation.md) and
[Linux](linux_reproduction_validation.md) execution documents.

Those fresh replays each collected 174 tests with zero failures or errors. Windows
executed 168 with six Linux-only skips; Linux executed 165 with nine Windows-only
skips. These checks establish calculation and workflow behavior under the
recorded environments. They do not recover missing biological measurements or
establish animal independence.

## Resource requirements

The workflow maintains a 4 GB free-disk reserve and a project allowance no
larger than 10 GB. It includes environments, caches and temporary products
inside the checkout in the storage checks. Individual and aggregate process
memory limits are 1 GB; available host memory is checked throughout execution.

The completed source replays used less than 0.4 GB sampled concurrent
process-family RSS. The Windows project, including its disposable checkout,
peaked near 0.2 GB; the complete temporary Linux directory, including installed
dependencies and cached wheels, occupied about 0.48 GB. These are measurements
from particular runs, not universal installation sizes. The Linux virtual
machine and guest process measurements have separate scopes. See the detailed
execution reports for exact bytes and the [resource report](resource_usage.md)
for the latest invocation's telemetry.

## Verification detail

[Statistical validation](statistical_validation.md) describes estimator checks.
[Environment provenance](environment_reproduction.md) records dependency and
platform scope. The [comparison protocol](cross_platform_plan.md) fixes the
cross-platform rules, and [figure review](pdf_qa.md) binds inspected files to
their hashes. The synthetic benchmark has its own
[design](calibration_design.md) and [results](../results/reports/software_calibration.md).
