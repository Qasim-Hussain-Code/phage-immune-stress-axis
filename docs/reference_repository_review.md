# Reference repository review

Reviewed on 2026-10-20, before implementation of this study's analysis. The
reference was inspected through the connected GitHub API rather than cloned.
No code, scientific question, data, or results from that study are reused here.

## Repository state

[post-adsorption-phage-resistance](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance)
was public and used the `main` branch. The recursive tree resolved to
`a63bde39b748b4fcc65b22a9e285ed0219676039` at inspection. The tree was not
truncated. This identifies the inspected state; it does not assert that the
reference's reported results were independently reproduced during this review.

## Practices supported by inspected files

| Practice | Evidence inspected | Application to this study |
|---|---|---|
| Reconcile observed units with publication-level counts | [Acquisition and validation script](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/scripts/01_fetch_and_validate_data.py) explicitly distinguishes metadata rows, measured matrix rows, missing cells, and partial replicate coverage. | Report pools, individual mice, source-data entries, sequencing runs, and linkable biological units separately. |
| Verify cached inputs and preserve provenance | The acquisition script uses SHA-256 digests, temporary downloads, and an input manifest; [provenance](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/docs/data_provenance.md) describes upstream sources and redistribution policy. | Freeze small public inputs, record URLs and checksums, and refuse silent changes to cached inputs. |
| Check estimators independently | [Statistical tests](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/tests/test_statistics.py) compare statistical calculations with statsmodels, SciPy, or brute-force definitions. | Verify compositional distances and applicable immune estimators against separate implementations or analytical identities. |
| Test the null model's contract | [Limitations](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/docs/limitations.md) describes a null generator that did not preserve the claimed dependence and explains its correction. | Preserve biological independence and treatment structure in any resampling; avoid animal-level inference from pooled viromes. |
| Evaluate adjustment and sensitivity before interpreting candidates | [README](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/README.md) distinguishes adjusted associations, within-cluster comparisons, power limits, and sensitivity failures. | Treat stress group, donor material, pooling, sampling time, and assay matching as design constraints rather than arbitrary covariates. |
| Preserve contradictory and null results | README and limitations retain corrections and distinguish an uninformative null from evidence against an effect. | Report unavailable individual matching and unmeasurable temporal stability as substantive constraints; do not force a positive phage-immune result. |
| Separate code, data, tables, and figures | The inspected tree contains numbered scripts, a shared `src/papr` package, tests, source manifests, methods/provenance/limitations documents, CSV tables, and PNG/PDF figures. | Use the requested `src/pisa` and numbered-stage structure, with every scientific figure backed by a machine-readable table. |
| Fail clearly on execution errors | [Runner](https://github.com/Qasim-Hussain-Code/post-adsorption-phage-resistance/blob/a63bde39b748b4fcc65b22a9e285ed0219676039/scripts/run_all.py) executes ordered stages and stops at the first nonzero exit status. | Use explicit stage outcomes, resource enforcement, and resumable/offline execution; describe unsupported stages as excluded. |

## Scope of the reference review

This review records software and reporting practices inspected at the stated
commit. It does not reproduce the reference project's results. This study uses
its own data, source-cell lineage, sample-linkage criteria, statistical models
and resource measurements.
