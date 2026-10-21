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

## Executed verification

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

Fresh committed-source reproduction is reported separately in
[Windows reproduction](reproduction_validation.md) and
[Linux reproduction](linux_reproduction_validation.md), with their actual source
revisions. The earlier Linux proof remains evidence for its stated commit until
a newer execution is completed; dependency installation or preparation alone
does not count as a completed scientific run.

These changes strengthen software and provenance checks. They do not supply the
missing community matrix or animal crosswalk and do not make the proposed
phage-stability/immune association identifiable.
