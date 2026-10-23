# Prespecified Windows–Linux reproduction comparison

Plan recorded 20 October 2026 before any full Linux scientific pipeline run.
**Execution is pending at plan lock.** Environment preparation, wheel retrieval
and process fixtures do not establish a successful reproduction. The selected
committed Git reference and actual outcomes will be recorded in the execution
report; no successful Linux result is claimed here.

The planned [Linux execution report](../results/reports/linux_reproduction_check.json)
and [Linux environment setup manifest](../data/manifests/linux_environment_setup.json)
are pending artifacts, not evidence already created. Environment context is in
[environment_reproduction.md](environment_reproduction.md); the earlier
same-environment replay is documented separately in
[reproduction_validation.md](reproduction_validation.md).

## Fixed inputs and independent installation

Both executions must use the same selected committed code, configuration,
21-version dependency specification in [requirements.txt](../requirements.txt),
and frozen scientific inputs. Record the commit and tree IDs, exported source
identity, configuration hash, dependency specification hash, and every input
hash. Freeze the Windows reference output inventory and hashes before Linux
execution. A changed source, input or output inventory requires an explicit new
comparison, not an unrecorded substitution.

The Windows reference uses Python 3.14.0; the available Ubuntu WSL environment
uses Python 3.14.4. This patch-version difference is recorded, not treated as an
identical interpreter. Install the same 21 pinned distributions independently
using verified prebuilt wheels. The first setup attempt placed all files in the
workspace; the pre-execution operational amendment below moves the final
environment and disposable source into a separately budgeted native temporary
directory. Wheel downloads remain inside the workspace. No system-wide package
install, source build, new distribution or
operating-system installation is part of this check. Record wheel filenames,
sizes and SHA-256 hashes, installed versions, interpreter/build, platform,
architecture and numerical-library/BLAS information. Equal version pins do not
imply equal Windows/Linux wheel binaries, fonts, BLAS or OS libraries.

Setup must finish and pass its manifest checks before scientific execution.
The setup manifest must distinguish successful, incomplete and failed actions;
a wheel present on disk is not proof that a package was installed or imported.
No further installation or network retrieval is allowed during the scientific
run.

## Fresh execution contract

Export the selected committed reference using `git archive` into a bounded
disposable workspace checkout. Validate archive members and resolved paths;
reject traversal, links and special files. Before launching, remove copied
generated scientific outputs, stage stamps, invocation status and generated
reports. Verify that no scientific output or resumable stage record survives.
Retain frozen inputs and manually authored provenance/feasibility evidence.

Run all ten numbered stages sequentially in full mode, offline, with one worker
and one numerical-library thread. Do not use resume or pilot mode. The report
must demonstrate ten actually executed stages and fresh software validation,
with no downloaded scientific inputs, inherited stage success or reused
scientific output. Excluded biological analyses must remain explicitly
excluded; executing their eligibility stages is not execution of unavailable
virome analyses.

## Thirty-output inventory

The scientific comparison contains exactly 20 CSVs and ten figure files.
The CSV inventory is:

- `data/processed/immune_long.csv`;
- `results/tables/archive_files.csv`, `article_methods_evidence.csv`,
  `hypothesis_eligibility.csv`, `sample_linkage_audit.csv`,
  `sequencing_inventory.csv`, `source_inventory.csv`;
- `results/tables/immune_contrasts.csv`, `immune_missingness.csv`,
  `immune_missingness_bounds.csv`, `immune_rank_effects.csv`,
  `immune_sensitivity.csv`, `immune_summary.csv`,
  `original_method_replication.csv`, `software_calibration.csv`;
- `results/tables/figure1_data.csv`, `figure4_data.csv`, `figure5_data.csv`,
  `figure7_data.csv`, `figure8_data.csv`.

The figures are `figures/figure1_design`, `figure4_immune`,
`figure5_linkage_limit`, `figure7_robustness` and `figure8_method_comparison`,
each with `.png` and `.pdf` extensions. Missing or unexpected scientific files
fail the inventory check. Operational `input_integrity.csv`, logs, timestamps,
resource measurements and invocation reports are not scientific comparison
outputs; their exclusion must not hide a scientific discrepancy.

## Fixed CSV comparison policy

Compute and disclose SHA-256 hashes for every file even when semantic CSV
comparison is needed. CSV column names and order, row counts and order, cell
counts, blank/missing positions, identifiers, source values, labels and all
non-whitelisted cells must agree exactly after ordinary CSV decoding. No
sorting, identifier repair, whitespace trimming, dropped rows or inferred
joins are allowed. Source values in `immune_long.csv` and `figure4_data.csv`
are exact fields, not tolerant floating-point comparisons. Counts, sample n,
Monte Carlo successes/replicates/seed/batches, half-integer U values, support
limits, boolean/status fields, fixed parameters and published/reference values
also remain exact. CSV newline or quoting differences may yield different
hashes while decoded cells agree; such byte differences are still disclosed.

Only the following derived continuous columns may use numerical tolerance.
All other columns, including numeric-looking columns, remain exact.

| CSV | Tolerant derived columns |
|---|---|
| `immune_contrasts.csv` | `mean_first`, `mean_second`, `mean_difference`, `standard_error`, `ci_low`, `ci_high`, `t_statistic`, `degrees_freedom`, `p_value`, `q_value` |
| `immune_summary.csv` | `mean`, `standard_deviation`, `median` |
| `immune_sensitivity.csv` | `mann_whitney_p_value`, `loo_mean_difference_min`, `loo_mean_difference_max`, `loo_p_value_min`, `loo_p_value_max`, `mann_whitney_q_value_sensitivity_family` |
| `immune_missingness_bounds.csv` | `observed_sum_first`, `observed_sum_second`, `lower_mean_difference`, `upper_mean_difference` |
| `immune_rank_effects.csv` | `empirical_probability_first_greater_plus_half_ties`, `rank_biserial_first_minus_second` |
| `original_method_replication.csv` | `group_mean`, `group_variance`, `group_sse`, `residual_sse`, `pooled_mse`, `effect`, `standard_error`, `statistic`, `p_value`, `ci_low`, `ci_high` |
| `software_calibration.csv` | `estimate`, `mc_ci_low`, `mc_ci_high` |
| `sequencing_inventory.csv` | `compressed_fastq_gb_decimal` |
| `figure7_data.csv` | The tolerant columns listed for `immune_sensitivity.csv`, plus `full_mean_difference`, `welch_p_value`, `welch_q_value` |
| `figure8_data.csv` | `mean_difference`, `ci_low`, `ci_high`, `p_value` |

For a nonblank tolerant cell, both values must parse as finite numbers. Accept
only `abs(a-b) <= 1e-10` **or** relative difference
`abs(a-b)/max(abs(a),abs(b)) <= 1e-12`; two zeros have zero relative difference.
Blank cells must match blank cells exactly. NaN and infinity fail, including
matching nonfinite tokens. Record every numerically different tolerant cell,
its absolute and relative difference, and every failed exact comparison.
Report byte-identical, numerically agreeing within this policy, and disagreeing
outputs separately. No tolerance broadening, new whitelisted column or relaxed
discrete/reference comparison is allowed after observing results. A genuine
change of policy requires a separately identified prospective validation.

## Figures and interpretation

Figure bytes have no numerical-tolerance exception. A byte-identical claim
requires identical SHA-256 hashes. Any differing PNG or PDF must be disclosed
and actually rendered/opened for visual review against its Windows reference.
Record render tools, pages and review outcome; a successful render or automated
hash comparison alone is not a visual pass. Until that inspection is complete,
figure equivalence remains unverified. Review labels, units, points, intervals,
legends, clipping and layout. A visually acceptable rendering difference is
reported as such, never relabeled byte-identical.

Successful execution would test a fresh Linux dependency installation and
cross-platform numerical/rendering agreement on the same committed research
inputs. Ubuntu WSL is not Linux Mint, a new physical host, remote CI or
biological replication. WSL shares the Windows host and physical hardware.
This check cannot validate animal independence, censoring assumptions, causal
claims or the unavailable phageome–immune association.

## Resource limits, timeout and cleanup

The Windows outer guard measures all workspace storage, including wheels,
environment, archive, disposable checkout and temporary products, and checks
global free disk and host available memory. Preserve the configured 10 GB
new-storage ceiling and 4 GB disk reserve. Wheel preparation retains its
250 MB compressed-download ceiling and 1.5 GB workspace reservation. Inspect
caps and hashes before installation; incomplete downloads are not successful
artifacts.

The Linux guest has a separate current, persisted guard baseline and measures
its own process-family RSS, elapsed runtime, available memory and disk. Preserve configured
1 GB per-process and aggregate process-family RSS ceilings. Record host and
guest measurements separately. The WSL VM is outside the Windows supervisor's
process family; a small Windows child RSS does not measure Linux workload RAM.
Do not add guest RSS to VM memory as if these were disjoint allocations. The
existing 6 GB WSL VM cap remains unchanged; this is an upper VM limit, not a
claim about observed usage.

The guest wrapper's full-command timeout is 600 elapsed seconds, its Windows
outer supervisor timeout is 650 seconds, and the individual stage timeout
remains 600 seconds. These are elapsed-time limits, not CPU-time allowances.
Timeout, resource breach, interruption or any comparison failure remains a
failed or incomplete outcome even if later cleanup restores free space.
Terminate the supervised workload before cleanup. Resolve and check every
disposable target against its intended workspace directory before recursive
removal. By default remove the disposable checkout/archive after preserving
logs and reports; record any deliberately retained installation/wheel cache
and its size rather than implying it was deleted. Keep failures and cleanup
errors visible. No broad deletion, WSL configuration change or OS setting
change is part of this validation.

## Operational amendment before the first full Linux run

The initial mounted-workspace setup attempt was cancelled before package
installation after very slow 9P filesystem resource traversals. The Windows
supervisor remained active and its failure evidence is retained. No Linux
scientific reproduction resulted from that attempt. The completed comparison
rules above, including the exact-field policy and numeric tolerances, are
unchanged.

The next attempt stages a capped, hash-verified archive through standard input
into a uniquely named `/var/tmp/phage-immune-stress-axis_validation/run_*` directory
in the existing distribution. Both the isolated environment and committed-source
checkout use this native temporary filesystem. No system package or WSL setting
changes. The additional temporary files require an explicitly monitored 1.5 GB
reservation: native Linux guards count the complete environment, wheels,
archives and source/results, while the Windows guard reserves that allowance
in addition to workspace bytes and measures actual free space on the physical
Windows volume. The Linux virtual filesystem's reported free space cannot
substitute for that physical-volume check. The global 4 GB reserve and 10 GB
new-storage ceiling still apply.

The native bootstrap has a 900-second total alarm and a 950-second outer host
timeout, covering installation and execution; the full scientific child and
each stage retain their 600-second elapsed limits. On success, capture a bounded
result archive, verify all comparisons, and remove only the verified owned
native run directory. A failure with unconfirmed guest termination preserves
its cancellation marker and evidence. Logical deletion need not shrink an
already expanded WSL virtual-disk file; report observed host free space rather
than claiming that all physical space was returned. These operational changes
are recorded before the first full Linux analysis, not selected after viewing
its scientific results.

An initial native `/tmp` preflight found a 3.106 GB RAM-backed filesystem and
refused execution before extraction or installation. The actual disk-backed
`/var/tmp` filesystem has separately measured capacity; the final attempt uses
that location. A concurrent Windows replay also stopped at its available-memory
floor. Subsequent replays run serially. Neither refused attempt is a successful
scientific execution, and neither changes the comparison rules.

## Current protocol extension: 23 October 2026

The current code adds nine scientific CSVs for post hoc design sensitivities
and source-metadata inventories. Its prospective inventory is **29 CSVs and
ten figure files**, or 39 scientific outputs. The earlier thirty-output
protocol, recorded source identities and Linux execution evidence retain their
original scope. This extension does not establish a new Linux execution or
extend a previous replay to the added analyses. A new comparison must record
the current committed source, complete inventory and comparison-plan hash.

Headers and row order are explicit in [portability.py](../src/pisa/portability.py).
The old twenty CSV schemas and their implemented tolerances are unchanged.
The following additions use the same absolute `1e-10` or relative `1e-12` rule
for only the listed derived statistics:

| Added CSV | Tolerant derived fields |
|---|---|
| `immune_design_membership.csv` | None |
| `immune_block_adjusted.csv` | `mean_difference`, `standard_error`, `t_statistic`, `p_value`, `ci_low`, `ci_high`, their six `unadjusted_hc3_` counterparts, `id_block_B_minus_A_estimate`, `q_value` |
| `immune_within_block.csv` | The Welch fields listed below, `overall_raw_mean_difference`, `q_value` |
| `immune_putative_cage_units.csv` | `unit_mean` |
| `immune_putative_cage_means.csv` | The Welch fields listed below and `q_value` |
| `immune_control_cage_omission.csv` | The Welch fields listed below and `q_value` |
| `immune_tnfa_log_sensitivity.csv` | `geometric_mean_first`, `geometric_mean_second`, `geometric_mean_ratio`, `ratio_ci_low`, `ratio_ci_high`, `log_mean_difference`, `log_standard_error`, `log_ci_low`, `log_ci_high`, `t_statistic`, `degrees_freedom`, `p_value`, `raw_mean_difference`, `raw_ci_low`, `raw_ci_high`, `raw_p_value`, `q_value` |
| `sequencing_design_inventory.csv` | None |
| `candidate_recipient_pairs.csv` | None |

The Welch fields are `mean_first`, `mean_second`, `mean_difference`,
`standard_error`, `ci_low`, `ci_high`, `t_statistic`, `degrees_freedom` and
`p_value`. Welch degrees of freedom are continuous; HC3 residual degrees of
freedom are integer counts and remain exact, including the treatment-only
comparator. All source and specimen identifiers, workbook rows, counts, byte
sums, categories, booleans, membership JSON, confidence levels, family sizes
and assumptions remain exact. Literal label candidates do not become verified
crosswalks through numerical comparison.

The shared CSV writer now writes LF directly. Native-byte comparisons still
report actual hashes; decoded agreement never implies byte identity. Figure
differences still require separate visual review, and this extension changes
no scientific or causal interpretation of the underlying studies.
