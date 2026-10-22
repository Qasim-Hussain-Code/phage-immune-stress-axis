# Execution environments and dependency provenance

The analysis has been executed on Windows and in an existing Ubuntu WSL2
distribution on the same physical host. The Windows runs reuse an installed
Python environment. The Linux replays install the pinned dependencies into a
new temporary environment. These are different reproduction checks and retain
separate source identities and results.

## Executed source revisions

| Execution | Source | Environment | Result |
|---|---|---|---|
| Full Windows workflow, 22 October 2026 | Working source subsequently committed as `21546d6` | CPython 3.14.0; existing packages | Ten stages executed; 174 tests collected, 168 executed, six Linux-only skips; no failures or errors |
| Fresh Windows checkout, 21 October 2026 | `eb7ba6c` | Same CPython 3.14.0 environment | Ten stages executed without resume; all 30 scientific files reproduced exactly |
| Fresh Ubuntu WSL2 environment, 21 October 2026 | `eb7ba6c` | CPython 3.14.4; 21 pinned distributions newly installed | Ten stages executed; 174 tests collected, 165 executed, nine Windows-only skips; all 20 CSV comparisons passed |

The October 22 revision changes the report narrative and the explanation of
viral–immune eligibility. Its numerical observations, estimates and figures
match the preceding analysis; only the eligibility table's question and reason
text changed. The earlier Linux replay does not establish execution of that
revised report generator. The [current invocation](../results/reports/run_status.json),
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

The Windows fresh-checkout comparison requires exact SHA-256 equality for all
30 scientific files. Linux uses the [fixed comparison protocol](cross_platform_plan.md):
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

The runner writes JSON records atomically and retains a journal for each
invocation. Resume requires matching source, configuration, dependency, input
and output fingerprints. A newer failed or interrupted attempt cannot inherit
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
