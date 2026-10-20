# Local committed-source reproduction validation

Status: passed. Recorded UTC completion: 2026-10-20T06:34:46.564876+00:00.
Selected Git commit: 53ffec7b6f77178ecde8cf4c5044d444fe172735.
Scope: same-host committed-source checkout, existing interpreter/packages, offline full execution.

This check uses a fresh Git archive inside the existing workspace and the same Python interpreter and installed package environment. It does not establish Linux execution, independent dependency installation, virtual-machine reproduction, or remote CI success. No network or package installation is requested.

Before execution, generated scientific outputs and stage stamps are removed from the disposable checkout. The full ten-stage command is run offline with one worker and without resume. Frozen inputs are checked before and after. Scientific CSV and PNG/PDF inventories must agree and all output bytes must match the starting working reference. Git-normalized source/reference equivalence to the selected commit is checked separately. No numeric-tolerance fallback is used. Timestamps, run statuses, resource measurements and acquisition-cache status tables are operational records and are excluded from scientific output comparison.

Stages verified as executed: 10. Identical scientific outputs: 28 / 28.
Disposable checkout/archive cleanup: removed.
Outer storage checks include the archive, disposable checkout, its generated outputs and temporary/cache files. Outer sampled aggregate memory includes the reproduction controller, fresh runner, stages and validation descendants. Per-process native peaks and sampled simultaneous RSS remain distinct measurements.

Machine-readable evidence: `results/reports/reproduction_check.json`. Child log: `results/reports/reproduction_run.log`. The JSON contains exact source identities, input checks, each comparison and resource observations.

## Source text normalization check

A separate read-only Git object comparison checked all 45 tracked source, script and fixture files. The 11 raw byte differences were exclusively CRLF versus LF line endings. The committed-source code digest 5cc889a9822b425840ea94e4540fd73bcfe512818809b359d08da1f2efa8be04 matches the exported checkout and its executed validation summary. The working-tree raw digest differs because of those recorded text line endings. Scientific outputs still matched byte-for-byte. No source file was changed.
