# Independent Ubuntu WSL environment setup

**Latest replay:** version 0.2.2 at `eb7ba6c8b945670a1f55c493d89435f36750900c` completed a new independent
installation and all ten offline stages on 21 October 2026. The current
[setup manifest](../data/manifests/linux_environment_0_2_2.json) and
[Linux execution report](linux_reproduction_validation.md) record 174 collected
tests, 165 executed and nine platform skips. The original dated setup snapshot
below remains historical evidence for version 0.2.1.

Recorded 2026-10-20T12:47:15.508155+00:00. The fresh Linux environment and all ten offline pipeline stages completed for commit `06b7cab84937c174c3197ba63d560ddc9cc70b1c`. All 20 CSV comparisons passed the locked exact-field/numeric-tolerance policy. At this setup snapshot the overall comparison is **pending figure review**: 18 of 30 files are byte-identical, two CSVs are semantically equivalent, and ten changed figure files require visual QA. Consult the [execution report](../results/reports/linux_reproduction_check.json) for its subsequent final outcome.

The [self-contained setup manifest](../data/manifests/linux_environment_setup.json) records official PyPI metadata URLs, response sizes/statuses and SHA-256 hashes for every selected wheel; installed versions; binary build configuration; commands; resource measurements; failed attempts; and cleanup. Its execution-report snapshot was captured before figure QA and can differ in hash from the later updated execution report. The prospective rules are in [cross_platform_plan.md](cross_platform_plan.md).

## What was installed

The Windows reference used its existing CPython 3.14.0 environment. This check newly installed the same 21 pinned distributions in a fresh CPython 3.14.4 virtual environment under Ubuntu WSL (x86_64, glibc 2.43, Linux kernel 6.18.33.2-microsoft-standard-WSL2). This shares the Windows physical host; it is not a Linux Mint or separate-machine validation. No OS/global package installation, source build or package download occurred during the scientific run.

All 21 prebuilt wheels were selected using actual Linux compatibility tags from version-specific official PyPI JSON, then checked against the published SHA-256 values. They total **101,465,096 compressed bytes** and **334,183,637 expanded member bytes**. A copied, pure-Python pip 25.2 wheel from the existing Windows CPython ensurepip bundle adds 1,752,557 compressed and 5,361,123 expanded bytes. The verified combined expanded total is 339,544,760 bytes. Wheel acquisition used public HTTPS; scientific execution used only frozen local inputs.

The runner created `venv --without-pip --copies`, bootstrapped that copied pip wheel, and installed the verified local wheels using `--no-index --no-deps --no-compile --no-cache-dir --only-binary=:all:`. It then ran `pip check`, checked all 21 installed versions plus pip, verified isolation, and imported NumPy/SciPy to record `show_config()` output. NumPy reports OpenBLAS 0.3.30 with 64-bit integer support; SciPy reports OpenBLAS 0.3.29.dev. These are wheel build strings, not claims that every numerical execution used that wheel build-time thread maximum; numerical thread environment variables were set to one.

| Distribution | Installed version |
|---|---|
| contourpy | 1.3.3 |
| cycler | 0.12.1 |
| et_xmlfile | 2.0.0 |
| fonttools | 4.60.1 |
| kiwisolver | 1.4.9 |
| numpy | 2.3.4 |
| scipy | 1.16.3 |
| matplotlib | 3.10.7 |
| openpyxl | 3.1.5 |
| packaging | 25.0 |
| pandas | 2.3.3 |
| patsy | 1.0.2 |
| pillow | 12.0.0 |
| pyparsing | 3.2.5 |
| PyYAML | 6.0.3 |
| pypdf | 6.13.0 |
| python-dateutil | 2.9.0.post0 |
| pytz | 2025.2 |
| six | 1.17.0 |
| statsmodels | 0.14.6 |
| tzdata | 2025.2 |

## Failed attempts remain part of the record

1. The initial mounted-workspace attempt spent long intervals in 9P filesystem resource traversals. It was stopped during virtual-environment creation before dependency installation. The controller exited through its stop handler; the later exact-PID cancellation probe found it already absent and sent no signal. Earlier zero memory-sampling fields mean no completed sample, not zero RAM usage.
2. The first native `/tmp` attempt refused the free-space preflight before extracting stdin or installing packages. A read-only mount-table snapshot identifies `/tmp` as tmpfs with about 3.1 GB total capacity. `/var/tmp` and `/home` are on root ext4 (`/dev/sdd`); `/mnt/c` is 9P. The complete mount JSON was captured although its bounded launcher timed out during teardown; that return status is retained. The concurrent Windows fresh-check attempt also stopped at its host RAM guard, rather than producing valid reproduction evidence.
3. The first `/var/tmp` attempt successfully installed all 21 pins, passed package checks and recorded binary configuration. Its full scientific command was then cancelled when the Windows host reported **93,134,848 available bytes**, below the configured floor. Exact owned-process cancellation confirmed termination. Its reports/logs were preserved before the failed native directory and host scratch were removed. This attempt was not a completed scientific reproduction. Host RAM changes are recorded without assigning a cause.

The successful fresh serial retry used a stricter startup threshold of 2,000,000,000 available host bytes; its preflight measured **3,705,389,056 bytes**. It created a new environment and checkout; it did not resume the cancelled command.

## Resource and execution evidence

The native guard counted the complete run directory, including source, wheels, environment, logs and results, against a 1.5 GB ceiling and a 4 GB native-filesystem reserve. Total logical bytes were 479,269,188 after package installation and 481,159,184 after the full run before result-tar creation. The standalone environment footprint was not separately measured. The Windows outer guard separately reserved 1.5 GB for native VHD growth while enforcing the global 10 GB storage limit, physical-volume 4 GB reserve, and host RAM floor; the ext4 filesystem's large virtual free capacity was not substituted for physical C: free space.

Linux monitoring sampled a maximum concurrent process-family RSS of **337,580,032 bytes** and a largest observed native per-process peak of **254,656,512 bytes** over 166 samples. Both stayed below their 1 GB ceilings. The successful host run recorded a minimum available RAM of 908,636,160 bytes and lowest recorded physical disk free space of 13,356,269,568 bytes. Guest RSS and Windows/VM memory measures have different scopes and are not summed.

Physical Windows free space was 13,519,425,536 bytes before this attempt and 13,472,624,640 after cleanup (observed change -46,800,896 bytes). This is not a causal WSL-only estimate. No true pre-boot baseline exists, so a boot-only disk delta is unknown. Logical deletion also need not shrink the WSL virtual-disk file. The pre-existing 6 GB VM memory/2 GB swap configuration remained unchanged, confirmed by matching `.wslconfig` hashes.

The committed source archive, original configuration, requirements, frozen ten-input manifest and individual input hashes matched before and after execution. Only execution-resource settings were tightened in a separate native configuration: one worker, 1.5 GB storage ceiling, four-GB reserve and 600-second stage limit; biological and calibration settings matched the original source configuration. Generated scientific outputs and stage records were cleared before execution. All ten stages newly completed with zero resumed stages. Validation discovered **135 tests: 126 executed, nine skipped, zero failures and zero errors**. The whole guest alarm was 900 seconds, the full scientific child/stage limits 600 seconds and the outer host limit 950 seconds.

## Cleanup and retained files

The successful native directory, including its temporary environment, and successful host disposable checkout/archive were removed after bounded artifact verification. The preceding RAM-cancelled native and host scratch were removed after their small evidence members were preserved. No system environment was modified.

The workspace retains the verified wheel cache (101,465,096 bytes), copied pip bootstrap directory (1,752,557 bytes), and the earlier partial mounted-workspace environment (29,923,436 bytes). The complete `.cache/linux` evidence/cache directory measured 104,863,505 logical bytes at manifest capture; these child-directory subtotals overlap that total. Small failed-attempt evidence is self-contained in the tracked manifest even when ignored cache files are absent from a checkout. Cleanup of the earlier `/tmp` preflight-only directory was not independently measured by this setup manifest.

This check establishes a fresh software execution with independently installed Linux wheels. It does not supply the missing matched virome/immune dataset or validate causal biological conclusions.
