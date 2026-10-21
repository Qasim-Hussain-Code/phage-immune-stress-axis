# Independent Linux reproduction validation

Status: **passed with the fixed numerical tolerances and unchanged reviewed figure files**.
The full run finished at 2026-10-21T13:31:37.550663+00:00. Source commit: `eb7ba6c8b945670a1f55c493d89435f36750900c`.
Project version: **0.2.2**. Code SHA-256: `9d62cd4b5958b1275f06687c47eb11acb5250a46dad14f11167e956d67cf4d4d`.

All ten stages newly executed offline, with no resumed stages, in a fresh CPython
3.14.4 environment under the existing Ubuntu WSL2 distribution. All 21 pinned
scientific distributions were newly installed from verified local Linux wheels;
pip was bootstrapped from the previously verified pure-Python wheel. Package
checks and binary configurations passed. Source, original configuration and all
ten frozen input files matched before and after execution. A separate native
configuration tightened resource settings while retaining the same biological
selections, seed and 20,000-replicate calibration per scenario.

The [execution report](../results/reports/linux_reproduction_check.json) contains
the full source, package, command, resource, comparison and cleanup evidence.
The [current setup manifest](../data/manifests/linux_environment_0_2_2.json)
links the same 21 wheel hashes to their previously captured official PyPI URLs
and records the fresh installation. No OS/global package installation, source
build, network retrieval during analysis or WSL configuration change was requested.
This uses the same physical host as Windows; it does not establish Linux Mint,
macOS, a separate physical machine or remote CI execution.

## Fixed comparison and actual results

The machine-readable comparison-policy SHA-256 is
`fb41c3626e1e1097cb60578a816d7a6449cb52ef286eed78009f1147f049ea2e`. This identifies the policy returned by
`pisa.portability.comparison_plan()`, rather than the Markdown file's bytes.
The rules were fixed before execution and are explained in
[cross_platform_plan.md](cross_platform_plan.md). Identifiers, observations,
schema, order, counts, rank U values and simulation success counts remain exact.
Only explicitly listed derived continuous fields allow finite absolute
differences at most 1e-10 or symmetric relative differences at most 1e-12.
No tolerance was widened after seeing these results.

| Files | Result |
|---|---|
| 18 CSVs | Exact SHA-256 match to Windows |
| `figure8_data.csv` | 11 derived fields differ; maximum absolute difference 1.42e-14 |
| `original_method_replication.csv` | 19 derived fields differ; maximum absolute difference 3e-14 |
| Five Linux PDFs and five Linux PNGs | Different from Windows, but exactly match the previously visually reviewed Linux files |

All 20 CSVs passed the policy. Eighteen of the 30 total files were byte-identical
to Windows. The largest relative numerical difference was approximately
8.1721e-13. Linux outputs are not byte-identical overall.

The [new hash-comparison record](../data/manifests/linux_figure_reuse_0_2_2.json)
binds all ten newly generated Linux files to the exact bytes covered by the
[retained visual review](../data/manifests/linux_figure_qa.json). It explicitly
records that a new visual inspection was not performed. The original automated
`needs_visual_review` comparison remains unchanged inside the final execution
report; the separate exact-match acceptance supplies its final passed status.
Windows reference figures and their existing QA record were retained.

## Tests and resources

Linux collected **174 tests: 165 executed, nine Windows-only skips, zero failures
and errors**. The [validation summary](../results/reports/linux_validation_summary.json)
and [log](../results/reports/linux_validation.log) retain the executed cases.
The same committed source on Windows collected 174, executed 168 and skipped
six Linux-only cases, and reproduced all 30 scientific files byte-for-byte.
See [Windows reproduction](reproduction_validation.md).

Execution was serial with numerical-library threads set to one. The complete
native directory occupied **482,644,068 logical bytes** after the full run,
before artifact packaging, against a 1.5 GB allowance. The outer guest monitor
sampled **338,358,272 bytes** concurrent process-family RSS and a largest
per-process peak of **254,431,232 bytes**. The inner scientific runner separately
sampled 305,127,424 concurrent bytes. These monitored scopes and sampling
intervals are distinct and are not exact whole-machine peaks.

The host startup gate measured **2,225,131,520 available bytes**, above its 2 GB
threshold. The successful run's minimum recorded host RAM was **319,045,632
bytes**, above the configured runtime floor, and its minimum physical disk free
space was **10,217,545,728 bytes**. A separate host reservation covered native
VHD growth while preserving the four-GB physical-volume reserve. The guest's
large virtual ext4 free capacity was not substituted for physical C: space;
guest RSS is not added to virtual-machine memory.

The complete run took about 117 seconds, within the 900-second guest,
600-second scientific-child and 950-second outer limits. Verified native and
host disposable directories, including the temporary environment, were removed.
An earlier host preflight refusal began no guest analysis; its local diagnostic
was retained privately before the successful retry. The separately documented
older setup attempts remain historical records, not successful new runs.

The prior version 0.2.1 Linux replay at commit
`06b7cab84937c174c3197ba63d560ddc9cc70b1c` remains identifiable in repository
history and the original setup snapshot. This latest report records the new
source revision rather than attributing that older run to version 0.2.2.

These checks establish software reproduction under the recorded environments.
They supply no missing community matrix or animal crosswalk and do not make
the proposed phage-stability/immune association testable.
