# Figure guide and visual review

The five figures connect the study's biological units, the selected immune
comparisons and the data needed for a viral–immune analysis. The observations
come from [Ritz et al. (2024)](https://doi.org/10.1038/s41564-023-01564-y);
the plots and comparisons are adaptations for this reanalysis. Read them with
the [methods](methods.md) and [results](results.md).

## Figure 1: study structure and available data

This diagram separates the initial stress and FVT experiments, their phenotype
rows, pooled enriched viromes and individual bulk-metagenomic route. The
104 deposited specimens include recipient samples, pools and inocula; they are
not 104 immune-matched mice. Published pool-by-time profiles also remain
distinct from verified individual trajectories.
The archive's heat-inactivated-FVT labels are shown separately from the
published three-group phenotype design; their cohort relationship is unresolved.

[PNG](../figures/figure1_design.png) · [PDF](../figures/figure1_design.pdf) ·
[Source counts](../results/tables/figure1_data.csv).

## Figure 4: observed immune outcomes and treatment contrasts

The upper panels show individual observed values and group means for basal
LY6Chi monocytes, their CD62L-positive fraction and unstimulated splenocyte
TNF-alpha. The concentration panel uses a log y-axis, with arithmetic mean
bars retained; the lower raw-mean contrasts remain on linear axes. Sample
counts differ by endpoint. The lower panels show Control
Stress minus Control and FVT Stress minus Control Stress mean differences.
Blood outcomes are percentages of parent populations, with contrasts in
percentage points; culture TNF-alpha uses pg/mL. Blood was collected on day 19
and spleens on day 23, so these are different sampling occasions.

Intervals are pointwise 95% Welch intervals. The displayed q values belong to
the six-test BH family; they do not make the intervals simultaneous.

[PNG](../figures/figure4_immune.png) · [PDF](../figures/figure4_immune.pdf) ·
[Source observations and missing cells](../results/tables/figure4_data.csv) ·
[Contrast estimates](../results/tables/immune_contrasts.csv).

## Figure 5: the missing viral–immune linkage

This summary sets the available individual immune observations beside the
unavailable processed viral profiles and validated animal crosswalk. Literal
Stress/FVT labels provide candidate pairing, while processing/exclusion
records remain unresolved and the raw paired subset exceeds the local budget.
It explains why
separate immune contrasts could be calculated but no viral–immune association
was fitted. Zero retrieved matches is an availability result, rather than a
zero biological association.

[PNG](../figures/figure5_linkage_limit.png) ·
[PDF](../figures/figure5_linkage_limit.pdf) ·
[Source availability counts](../results/tables/figure5_data.csv).

## Figure 7: influence of individual observations

Black points show the full mean differences. Blue ranges span the estimates
obtained by omitting each observed animal once. They describe influence on
effect size and direction, not confidence intervals. Repeated omissions do not
create new observations or establish robust statistical significance. The
source table also retains the separate rank comparisons.

[PNG](../figures/figure7_robustness.png) ·
[PDF](../figures/figure7_robustness.pdf) ·
[Source estimates and diagnostics](../results/tables/figure7_data.csv).

## Figure 8: why the interval method matters

The same pairwise mean differences appear under two interval calculations.
Welch uses the two groups' unequal-variance standard error and pointwise 95%
coverage. Tukey–Kramer uses pooled residual variance from all three groups and
simultaneous 95% coverage for all three pairs within an endpoint, although only
the two selected comparisons are plotted. The original across-outcome BH family
is not reconstructed. This figure explains a change in inference without a
change in the observed pairwise mean difference.

[PNG](../figures/figure8_method_comparison.png) ·
[PDF](../figures/figure8_method_comparison.pdf) ·
[Source interval comparison](../results/tables/figure8_data.csv).

## Recorded visual review

The links above point to the Windows reference figures. All five PDFs are
single-page files. The retained inspections checked titles, labels, units,
sample counts, intervals, legends and captions, with no observed clipping,
overlap or broken glyphs.

| Date and scope | Evidence |
|---|---|
| 23 October 2026, 05:32:33 UTC: all five current Windows PDFs were rendered from their actual pages and inspected through the image viewer after the sensitivity/figure revision | [Current Windows review](../data/manifests/figure_qa.json) |
| 20 October 2026, 06:23:59 UTC: all five earlier Windows-reference PDFs were rendered and inspected | [Historical Windows review](../data/manifests/windows_figure_qa_20261020.json) |
| 20 October 2026, 12:51:09 UTC: all five independently generated Linux PDFs were rendered and viewed; their five original PNG companions were also viewed | [Linux review record](../data/manifests/linux_figure_qa.json) |
| 21 October 2026, 13:34:36 UTC: all ten files from the version 0.2.2 Linux replay matched the previously reviewed Linux hashes exactly | [Exact-byte reuse record](../data/manifests/linux_figure_reuse_0_2_2.json) |

The current Windows review used Poppler pdftoppm 26.07.0 at 110 dpi.
The earlier renderer was pypdfium2 5.14.0 with PDFium 156.0.8076.0.
The Linux record explicitly identifies AI-assisted visual inspection, not
independent human peer review. Linux and Windows figure bytes differ and have
separate records. The October 21 acceptance reused an existing inspection;
it did not perform a new one. Exact timestamps and file hashes remain in the
linked manifests.

## Maintenance checks

From the repository root:

```bash
python scripts/check_figures.py
python scripts/check_figures.py --render
```

The first command checks current PDF identities against the Windows review
record. The optional second command renders pages for inspection using an
existing pypdfium2 environment or the workspace renderer cache; pypdfium2 is not
a required analysis dependency. Rendering alone does not approve the figures
or update a passed-review record. See [reproduction](reproducibility.md) for
the separate execution and output-comparison evidence.
