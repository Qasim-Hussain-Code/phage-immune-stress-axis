# Study documentation

The [project README](../README.md) introduces the biological question and main
immune findings. These documents provide the scientific detail and the records
needed to reproduce the analysis.

## Research

| Document | Purpose |
|---|---|
| [Methods](methods.md) | Study design, biological units, assay timing, six mean contrasts and sensitivity analyses |
| [Results](results.md) | Findings by immune endpoint, method dependence and missing-data diagnostics |
| [Limitations](limitations.md) | What the design, missing observations and available measurements leave unresolved |
| [Data availability](data_feasibility.md) | Retrieved inputs, sample categories and requirements for a viral–immune analysis |
| [Data provenance](data_provenance.md) | Source locations, transformations and workbook-cell lineage |
| [Contribution and scope](novelty_assessment.md) | Relationship to the original experiment and the question that remains open |

## Statistical detail

| Document | Purpose |
|---|---|
| [Original-analysis reconstruction](original_analysis_review.md) | Pooled variance, planned contrasts, Tukey–Kramer comparisons and printed-statistic checks |
| [Phenotype robustness](phenotype_robustness.md) | Conditional percentage bounds and empirical rank effects |
| [Design and scale sensitivity](design_sensitivity.md) | Inferred ID strata, conditional control-cage weighting and log TNF ratios |
| [Statistical validation](statistical_validation.md) | Independent numerical checks and their assumptions |
| [Calibration design](calibration_design.md) | Five synthetic null scenarios, separate from biological observations |
| [Article design audit](paper_audit_notes.md) | Source passages supporting sample roles, timing and assay interpretation |

## Reproduction and evidence

Start with the [reproduction guide](reproducibility.md). Detailed execution
records retain their source revisions and measured environments:

- [Windows committed-source replay](reproduction_validation.md) and
  [Linux replay](linux_reproduction_validation.md).
- [Environment provenance](environment_reproduction.md),
  [Linux installation records](linux_environment_setup.md) and the dated
  [cross-platform comparison protocol](cross_platform_plan.md).
- [Resource measurements](resource_usage.md), [figure review](pdf_qa.md) and
  [validation changes](validation_hardening.md).
- Machine-readable [execution reports](../results/reports/) and
  [source manifests](../data/manifests/).

## Data search and reuse

The [data requirements](data_requirements.md) specify the unresolved allocation,
heat-inactivated-arm phenotypes and processed-profile linkage needed for further work.

The [data-search overview](data_search.md) brings together the October 20
checks, study comparisons and unresolved inputs. Detailed evidence remains in
the [primary-data search](processed_data_search.md),
[alternative-study audit](alternative_dataset_audit.md) and
[Chen public-route follow-up](chen2026_public_route_followup.md), with links to
the original screen and source ledgers.

The [23 October follow-up](public_data_recheck.md) records the narrower fresh
archive and Chen checks, separately from those historical searches.

[Third-party notices](third_party_notices.md) record upstream licenses and
attribution. Repository maintenance instructions are separate:
[private-push checks](maintenance/private_push.md).
