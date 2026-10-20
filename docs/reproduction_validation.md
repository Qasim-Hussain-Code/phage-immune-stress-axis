# Local committed-source reproduction validation

The verifier is implemented but has not been executed against the final committed source revision. No successful fresh-checkout reproduction is claimed by this document.

After the scientific outputs and source are committed, run:

```bash
python scripts/check_reproduction.py --ref HEAD
```

The verifier exports that committed revision with Git into a bounded workspace cache, removes generated outputs and stage stamps, and runs all ten stages offline without resume. It uses the existing Python interpreter and packages. No installation, external server, VM or network request is part of this check.

Scientific CSVs and PNG/PDF files are compared by exact SHA-256 against the starting working reference. Operational timestamps, runtime/resource records and acquisition-cache status tables are excluded. Git-normalized equivalence to the selected committed source/reference is checked separately because configured text normalization can alter line endings in an archive. No semantic numeric tolerance fallback is used.

The archive and disposable checkout count toward the outer storage budget. The outer process-family monitor includes the controller, runner, stages and validation descendants. Disposable files are removed by default after the report, or retained with `--keep` for diagnosis. Cleanup validates the resolved target inside `.cache/reproduction` before recursive removal.

An actual invocation writes `results/reports/reproduction_check.json`, `results/reports/reproduction_run.log` and a measured replacement for this document. Unit fixtures exercise containment and comparison behavior only; they do not execute the research pipeline.
