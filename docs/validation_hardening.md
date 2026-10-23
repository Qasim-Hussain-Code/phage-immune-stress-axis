# Validation hardening, version 0.2.2

This revision fixes three operational issues without changing source observations,
statistical estimators, selected outcomes, multiplicity families or figure data.

Frozen input records must now declare a nonnegative integer byte size. Missing,
Boolean, string, floating-point and negative sizes are rejected. Acquisition,
read-only cache verification, release checks and the native Linux bootstrap all
use the same size-and-SHA contract. Downloaded Zenodo catalogues are checked
after canonicalization, against the stored representation. A correct checksum
does not excuse incorrect byte provenance. The ten original input files and
their manifest remain unchanged.

Generated validation summaries distinguish collected tests, executed tests and
platform-specific skips. Executed counts include failures and errors; a skipped
or failed suite is not presented as a successful execution. The historical
unittest `tests_run` field remains unchanged in machine-readable records.

The maintained [private-push tool](private_push.md) checks the actual push URL,
URL rewrites, private visibility, the account and sole-contributor requirements,
commit subjects and coauthor trailers. It pins the source commit and destination,
checks new history and commit messages for common credential patterns, and
verifies the remote commit after pushing. Regression fixtures cover separate or
multiple push destinations, environment-hidden rewrites, replacement objects,
GitHub host selection and credentials deleted by a later commit. No test pushes
or contacts GitHub.

## Executed verification: 21 October 2026

The full Windows offline workflow completed all ten stages for code SHA-256
`9d62cd4b5958b1275f06687c47eb11acb5250a46dad14f11167e956d67cf4d4d`.
It collected **174 tests: 168 executed, six Linux-only skips, zero failures and
zero errors**. Twenty-one of the executed cases exercise private-push policy.
All 30 scientific CSV and PNG/PDF files exactly match their hashes recorded
before the changes, and all ten frozen inputs remain unchanged. The
[machine-readable record](../results/reports/hardening_validation.json) binds
these checks to the code and output hashes. The working-source invocation is
`20261021T131343730951Z_32180`; it does not itself establish a committed-source
replay or a new Linux execution.

Fresh committed-source reproduction also passed at `eb7ba6c8b945670a1f55c493d89435f36750900c` on both
Windows and Ubuntu WSL. Windows reproduced all 30 scientific outputs exactly;
Linux passed all 20 CSV comparisons and matched all ten previously reviewed
Linux figure files. Both collected 174 tests, with 168 executed on Windows and
165 on Linux; the remaining six/nine cases were platform-specific skips.
See [Windows reproduction](reproduction_validation.md) and
[Linux reproduction](linux_reproduction_validation.md).

The executed command-mode checks passed for the same code digest:
validation-only changed no scientific inputs, tables or figures; the pilot
stopped after six verified stages; full resume recomputed validation and figure
generation after validation records changed; and the final unchanged resume verified all ten
stages with zero recomputation. The [mode record](../results/reports/mode_checks.json)
distinguishes these invocations from the fresh full executions.

These changes strengthen software and provenance checks. They do not supply the
missing community matrix or animal crosswalk and do not make the proposed
phage-stability/immune association identifiable.

## Source-to-invocation binding: 23 October 2026

Release validation now requires the latest full-run journal to describe the
same source, runtime, configuration, requirements and input manifest as the
current verified stages. Previously, separately rebuilding the numbered stages
after a source change could leave an older successful full-run journal in
place. Current stage files alone did not establish that the recorded full
invocation had executed that source.

The check compares the ordered ten-stage inventory and captured stage results
with their fingerprint- and upstream-verified records. Completed and resumed
counts must match the recorded stage states. Fresh, mixed and fully resumed
full invocations remain valid when those contracts agree. Six regression tests
cover the stale-source case, stale stage results, missing identities,
incomplete or reordered stages, invalid states and inconsistent counters.

The full serial Windows offline run completed all ten stages for code SHA-256
`f5882a0104e16809ae3c736dbe727db4768b4fe2c8dddf2d21f131856cc1c030`.
It collected 180 tests, executed 174 and skipped six Linux-only cases, with no
failures or errors. All 30 scientific files and ten frozen inputs exactly match
the pre-change snapshot at `e0cd5a5`. The
[comparison record](../results/reports/invocation_binding_validation.json)
identifies the run and hashes. This is a working-source check in the existing
Windows environment; it does not replace the earlier committed-source replays
or establish a new Linux execution. No estimator, observation or figure changed.
