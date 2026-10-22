# Linux dependency installation and replay

Two completed Linux replays used fresh virtual environments inside the existing
Ubuntu WSL2 distribution. The October 21 replay is the later source check;
the October 20 manifest preserves an earlier installation and its preceding
failed attempts. Both share the Windows physical host.

## Source and record scope

| Replay | Source revision | Installation and execution records |
|---|---|---|
| 21 October 2026, version 0.2.2 | `eb7ba6c8b945670a1f55c493d89435f36750900c` | [Setup manifest](../data/manifests/linux_environment_0_2_2.json), [execution JSON](../results/reports/linux_reproduction_check.json) and [comparison report](linux_reproduction_validation.md) |
| 20 October 2026, version 0.2.1 | `06b7cab84937c174c3197ba63d560ddc9cc70b1c` | [Historical setup manifest](../data/manifests/linux_environment_setup.json), including its execution-report snapshot and attempt records |

The historical manifest captured the October 20 execution before figure review.
Its pending-review status belongs to that snapshot, rather than the current
execution JSON. The later retained [Linux figure review](../data/manifests/linux_figure_qa.json)
covers the inspected PDF and PNG files; the October 21
[reuse record](../data/manifests/linux_figure_reuse_0_2_2.json) confirms exact
matches to those bytes. The reporting revision committed on October 22 has
been executed on Windows and has not been rerun in Linux.

## Installed software

The Linux environments used CPython 3.14.4 on x86_64 Ubuntu WSL2, glibc 2.43
and kernel 6.18.33.2. The existing distribution and its configuration were
retained. Installation used prebuilt wheels for the same 21 versions in
[requirements.txt](../requirements.txt), with no system-package installation or
source build.

Official version-specific PyPI metadata supplied wheel compatibility tags,
download URLs, sizes and SHA-256 values. The scientific wheels total
101,465,096 compressed bytes and 334,183,637 expanded member bytes. A copied
pure-Python pip 25.2 wheel adds 1,752,557 compressed bytes and 5,361,123 expanded
bytes. The combined expanded member total is 339,544,760 bytes; this is not a
separately measured installed-environment footprint. The October 21 run reused
and reverified the previously retrieved wheels and metadata.

Each replay created a virtual environment using `venv --without-pip --copies`,
bootstrapped the copied pip wheel, and installed the verified local wheels with
`--no-index --no-deps --no-compile --no-cache-dir --only-binary=:all:`. Package
checks verified all 21 versions plus pip and environment isolation. NumPy and
SciPy build reports identify OpenBLAS 0.3.30 and 0.3.29.dev respectively.
Numerical-library thread settings were one; build-time thread maxima are not
execution measurements. The manifests retain commands and build output.

## Completed execution and resources

Both successful replays removed generated scientific outputs and stage receipts
before starting all ten stages offline without resume. Input files and source
identities were checked before and after. Biological settings and the
20,000-replicate-per-scenario calibration matched the source configuration.
Native execution tightened resource settings to one worker, a 1.5 GB complete
run-directory allowance and 600-second stage limit.

| Measurement | October 20 | October 21 |
|---|---:|---:|
| Tests collected / executed / skipped | 135 / 126 / 9 | 174 / 165 / 9 |
| Failures and errors | 0 | 0 |
| Native directory after full execution, before packaging | 481,159,184 bytes | 482,644,068 bytes |
| Outer guest monitor, sampled concurrent process-family RSS | 337,580,032 bytes | 338,358,272 bytes |
| Largest observed native per-process RSS | 254,656,512 bytes | 254,431,232 bytes |
| Minimum recorded host available RAM during successful run | 908,636,160 bytes | 319,045,632 bytes |
| Minimum recorded physical Windows disk free space | 13,356,269,568 bytes | 10,217,545,728 bytes |

The successful replays used a 2 GB host-memory startup gate. Runtime host memory
and physical free space were monitored separately from the guest's virtual
filesystem capacity. The guest alarm was 900 seconds, the scientific-child
limit 600 seconds and the outer limit 950 seconds. Process RSS is sampled and
does not measure an exact whole-machine peak.

All 20 CSV comparisons passed the fixed policy in both replays. Eighteen were
byte-identical to the Windows reference and two contained only permitted
derived-value differences. The ten Linux figure files differ from Windows;
their separate review and exact-byte reuse are described above.

## Earlier unsuccessful attempts

The historical setup manifest retains three attempts that preceded the
October 20 successful replay:

| Attempt | Stopping point | Consequence |
|---|---|---|
| Mounted Windows workspace | Slow filesystem traversal during virtual-environment creation | Stopped before numerical dependencies were installed |
| Native `/tmp` | Free-space preflight; `/tmp` was a memory-backed filesystem | No package installation or scientific execution |
| First native `/var/tmp` run | Dependencies installed and checked, then host available RAM fell to 93,134,848 bytes | Scientific command cancelled; not a completed replay |

The successful retry created another environment and checkout after passing
the stricter startup gate. It did not resume the cancelled scientific command.
These attempt records distinguish environment preparation from completed
analysis. They do not assign the host's changing free memory to any particular
application.

## Cleanup and retained evidence

Successful native environments and host disposable checkouts were removed after
bounded artifact verification. The RAM-cancelled native and host directories
were removed after preserving their small evidence files. The historical
manifest records the earlier partial mounted environment and cache footprints
at capture; those are dated measurements, not a current disk inventory.

Verified wheel and pip caches were retained for offline replay. Deleting native
files need not shrink the WSL virtual-disk file, and the observed Windows free
space change is not a causal estimate of WSL-only consumption. Detailed storage
scope and configuration-integrity records remain in the manifests.
