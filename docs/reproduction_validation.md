# Local committed-source reproduction validation

Status: passed. Recorded UTC completion: 2026-10-21T13:26:43.056490+00:00.
Selected Git commit: eb7ba6c8b945670a1f55c493d89435f36750900c.
Scope: same-host committed-source checkout, existing interpreter/packages, offline full execution.

This check uses a fresh Git archive inside the existing workspace and the same Python interpreter and installed package environment. It does not establish Linux execution, independent dependency installation, virtual-machine reproduction, or remote CI success. No network or package installation is requested.

Before execution, generated scientific outputs and stage stamps are removed from the disposable checkout. The full ten-stage command is run offline with one worker and without resume. Frozen inputs are checked before and after. Scientific CSV and PNG/PDF inventories must agree and all output bytes must match the starting working reference. Git-normalized source/reference equivalence to the selected commit is checked separately. No numeric-tolerance fallback is used. Timestamps, run statuses, resource measurements and acquisition-cache status tables are operational records and are excluded from scientific output comparison.

Stages verified as executed: 10. Identical scientific outputs: 30 / 30.
Disposable checkout/archive cleanup: removed.
Outer storage checks include the archive, disposable checkout, its generated outputs and temporary/cache files. Outer sampled aggregate memory includes the reproduction controller, fresh runner, stages and validation descendants. Per-process native peaks and sampled simultaneous RSS remain distinct measurements.

Machine-readable evidence: `results/reports/reproduction_check.json`. Child log: `results/reports/reproduction_run.log`. The JSON contains exact source identities, input checks, each comparison and resource observations.
