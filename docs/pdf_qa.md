# PDF figure review

All five PDF figures were regenerated or verified by the full offline workflow on 20 October 2026 (Asia/Taipei), rendered from their actual PDF pages with pypdfium2 5.14.0, and visually inspected through the image viewer. Each is one page. Titles, labels, units, intervals, legends and captions are legible, with no observed clipping or overlap.

The tracked review record is `data/manifests/figure_qa.json`. It binds the passed visual inspection to exact PDF SHA-256 values and records the UTC review time. `python scripts/check_figures.py` verifies that current PDFs still match this record, including the complete file inventory. It does not perform a new visual inspection.

| Figure | Visual and scientific checks |
|---|---|
| 1: study design | Cohorts and pool profiles remain distinct. The 104 archive specimens are not labeled as 104 mice. The zero verified matches gate is visible. |
| 4: immune outcomes | Individual observations, endpoint-specific sample counts, percentage versus pg/mL units, pointwise Welch intervals and the six-test BH family are labeled. |
| 5: linkage limit | Retrieved immune measurements and unavailable processed viral inputs are clearly distinguished. |
| 7: influence | The leave-one-animal-out range is explicitly labeled as an influence diagnostic, not a confidence interval. |
| 8: method comparison | Identical observed mean differences are displayed with unequal-variance pointwise Welch intervals and pooled-variance simultaneous Tukey-Kramer intervals; their coverage scopes are explicit. |

The optional command `python scripts/check_figures.py --render` renders current pages for a new human or agent visual inspection. Rendering alone never updates the passed-review record. The optional renderer is held in the ignored workspace cache and is not a mandatory analysis dependency. PNG companions and machine-readable figure source tables are supplied for all five figures. Unsupported viral composition, stability and bacterial-integration figures are excluded.
