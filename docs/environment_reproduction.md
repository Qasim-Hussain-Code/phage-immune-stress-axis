# Execution environments and dependency provenance

The analysis has been executed on Windows and in an existing Ubuntu WSL2
distribution on the same physical host. The Windows runs reuse an installed
Python environment. The Linux replays install the pinned dependencies into a
new temporary environment. These are different reproduction checks and retain
separate source identities and results.

## Executed source revisions

| Execution | Source | Environment | Result |
|---|---|---|---|
| Full Windows workflow, 23 October 2026 | Conditional design/scale sensitivities, source inventory and figure updates; [source identity](../results/reports/run_status.json) | CPython 3.14.0; existing packages | Ten stages executed; 219 tests collected, 213 executed, six Linux-only skips; no failures or errors |
| Fresh Windows checkout, 23 October 2026 | `c5504eb`; [replay report](../results/reports/reproduction_check.json) | Same CPython 3.14.0 environment | Ten stages executed without resume; all 39 scientific files reproduced exactly; 219 tests collected, 213 executed, six skips |
| Earlier Windows workflow, 23 October 2026 | Release source-to-invocation checks; [dated invocation](../results/reports/invocations/20261023T000334060517Z_5240.json) | CPython 3.14.0; existing packages | Ten stages executed; 180 tests collected, 174 executed, six Linux-only skips; no failures or errors |
| Full Windows workflow, 22 October 2026 | Reporting and timing terminology revision; [dated invocation](../results/reports/invocations/20261022T065653884702Z_26348.json) | CPython 3.14.0; existing packages | Ten stages executed; 174 tests collected, 168 executed, six Linux-only skips; no failures or errors |
| Fresh Ubuntu WSL2 environment, 21 October 2026 | `eb7ba6c` | CPython 3.14.4; 21 pinned distributions newly installed | Ten stages executed; 174 tests collected, 165 executed, nine Windows-only skips; all 20 CSV comparisons passed |

The October 22 revisions changed the report narrative, clarified viral–immune
eligibility and distinguished defeat days from individual bouts. Observations,
estimates and figures remain unchanged. The earlier eligibility explanation
changed that table's question and reason text; the final timing-wording rerun
reproduced all 30 scientific files exactly. On 23 October, the release checker
was updated to bind the latest full-run journal to the current source and
verified stage results. Its full Windows rerun again reproduced all 30 files
exactly; [comparison evidence](../results/reports/invocation_binding_validation.json)
records the unchanged inputs and outputs. The later design-sensitivity run
adds nine CSVs and a fifth calibration scenario, clarifies primary-result
annotations, and revises three figures. All primary statistical values and
the ten frozen inputs are unchanged; the
[comparison record](../results/reports/design_sensitivity_validation.json)
distinguishes CSV-record equality from byte equality. Derived CSV/JSON writers
now explicitly emit LF. The older Linux replay does not establish execution
of these later revisions. The
[current invocation](../results/reports/run_status.json),
[Windows replay](../results/reports/reproduction_check.json) and
[Linux replay](../results/reports/linux_reproduction_check.json) retain their
complete source and execution records.

## Dependency identity

[requirements.txt](../requirements.txt) pins 21 distributions, including the
transitive dependencies used by figure rendering and independent estimator
checks. The environment inventory records the same set. Runner fingerprints
include these versions, so a change in a recorded rendering library invalidates
cached stages even if SciPy and Matplotlib retain their versions. Missing
packages remain explicit in the inventory.

Version pins identify distributions; binary builds, operating-system libraries
and fonts can still differ. The Linux setup additionally verifies each wheel
against its official PyPI SHA-256 value and records numerical-library build
configuration. The [installation report](linux_environment_setup.md) links the
wheel provenance, installed-version checks and retained historical snapshots.
Windows dependency reinstallation is not part of its same-environment replay.

## Comparing outputs across platforms

The 23 October Windows fresh-checkout comparison requires exact SHA-256 equality
for all 39 scientific files. The historical 21 October Linux run uses the
[fixed comparison protocol](cross_platform_plan.md):
observations, identifiers, counts, schemas and specified exact fields must
agree, while a listed set of derived continuous values has numerical
tolerances. Eighteen CSVs matched exactly; two differed only in derived values
by at most 3e-14. The tolerances were not widened after execution.

Linux PDF and PNG bytes differ from Windows. The October 21 replay produced
the same ten Linux figure hashes as the retained visual review. Its acceptance
uses that exact match and makes no claim of a new inspection. See
[Linux reproduction](linux_reproduction_validation.md) and
[figure review](pdf_qa.md) for the separate comparison and review records.

## Resources and execution records

The selected workflow runs serially and limits numerical libraries to one
thread. The native Linux directory contains the source, wheels, environment,
logs and outputs under its 1.5 GB allowance. Windows separately checks physical
disk space and reserves capacity for native virtual-disk growth. Guest process
RSS and virtual-machine memory have different scopes and are not added
together. Exact measurements belong to their dated execution reports; the
[latest resource report](resource_usage.md) describes the current invocation.

The runner writes JSON records atomically and journals each invocation locally.
The repository retains current and cited historical JSON records; duplicate
Markdown summaries and uncited development journals are omitted. Resume requires
matching source, configuration, dependency, input and output fingerprints.
A newer failed or interrupted attempt cannot inherit
an earlier successful status. Historical environment measurements remain
unchanged; each checkout uses its own local resource baseline.

Process cleanup uses Windows Job Objects or Linux process groups and observed
descendant identities. The Linux monitor can retain descendants after session
changes or reparenting, but polling cannot guarantee detection of a process
that detaches between observations. Platform-specific process fixtures test
these execution controls. They do not establish independence of the biological
observations or replace the design assumptions in [methods](methods.md).

For installation commands and analysis modes, use the
[reproduction guide](reproducibility.md).
