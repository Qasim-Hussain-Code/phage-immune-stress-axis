# PDF rendering quality assurance

Date: 2026-10-20 (Asia/Taipei).

## Renderer preparation

No existing Poppler executable was found at four exact conventional Windows locations. A small optional renderer was therefore installed only inside the workspace. The project's Python environment was not modified.

The public [PyPI pypdfium2 metadata](https://pypi.org/pypi/pypdfium2/json) was retrieved with a 2,000,000-byte cap after passing the project resource guard. Saved metadata: `.cache/downloads/pypdfium2_metadata.json`; 1,520,075 bytes; SHA256 `e761a338dfa137de8017585ce72085e36d271b5a6c7a5c4159909d63c79dbaca`.

Selected package: pypdfium2 5.14.0, `pypdfium2-5.14.0-py3-none-win_amd64.whl`. The [official wheel](https://files.pythonhosted.org/packages/00/dc/ca7874924c9cfd701ad53f89529968523790e70473e0b71e834668316148/pypdfium2-5.14.0-py3-none-win_amd64.whl) is 3,947,280 bytes. Its SHA256 was checked against the PyPI metadata before installation: `149fd5c6397b8df8bf7911a93506eff0be874f877afe7ac936cf5d37d21a6a06`. The wheel was streamed under a 15,000,000-byte cap, with no dependency downloads.

Installation command, using the existing Python 3.14 executable:

```powershell
python -m pip install --disable-pip-version-check --no-index --no-deps --no-cache-dir --no-compile --target .cache/pdf_renderer .cache/downloads/pypdfium2-5.14.0-py3-none-win_amd64.whl
```

The installed directory contains 75 files totalling 8,094,031 bytes. Its permissions were reset to inherit the workspace ACL because pip's temporary-directory move initially preserved permissions that prevented sandbox access. Import and native PDFium library loading then succeeded in the ordinary sandbox. No global/site-packages installation was performed.

At the completed installation check, the guard measured 16,567,228 project bytes excluding Git, 8,878,952,448 free disk bytes, 557,203,456 available RAM bytes and a 40,689,664-byte process peak working set. The frozen operational project storage budget was 4,897,466,368 bytes, with a 4,000,000,000-byte free-space reserve.

## Figure review

All four generated PDF files were rendered with pypdfium2 5.14.0 / PDFium 156.0.8076.0 at scale 1.5. Each actual PDF-page render was inspected at its original PNG dimensions using the image viewer. This checks the exported PDFs rather than relying on the separately exported scientific PNGs. All PDFs contain one page.

| PDF | Rendered pixels | Visual result |
|---|---|---|
| figure1_design.pdf | 859 x 489 | Pass after correction and repeat PDF rendering: all text fits inside the four design boxes; arrows, titles and margins are clear |
| figure4_immune.pdf | 1284 x 758 | Pass: all titles, axis labels, group counts, q-values, confidence intervals and caption are visible without overlap |
| figure5_linkage_limit.pdf | 1026 x 433 | Pass: both table columns, separators and margins are clear without overlap or clipping |
| figure7_robustness.pdf | 1286 x 423 | Pass: titles, contrast labels, axes, estimate/range marks and caption are clear without overlap or clipping |

All four final PDFs pass visual review: no text clipping, box overflow, label overlap or missing-glyph boxes were found. The initial Figure 1 review detected horizontal text overflow inside the first design box. The text was shortened and the figure regenerated; the corrected PDF was rendered again and visually inspected. The QA agent did not change scientific figure code or source PDFs. The three other final PDF hashes were rechecked and remain identical to the inspected versions.

Current source-PDF SHA256 hashes:

```text
81866e290d55eacfb106ed9506641bd622257deeb21784af03040a0977b279be  figures/figure1_design.pdf
35917ac4a8a0345a7dfca5102b3ce47a0ae01375f4151c8950cfba57e93cd888  figures/figure4_immune.pdf
8af3b8017388ae8bbf85c5ade6b79bc6463f55bb2a76a0e44ff512425267b0d0  figures/figure5_linkage_limit.pdf
b9fb5f17dfb7e73cd755c7eda547f01e64807ab632cbdd9b4d17b6a35d23d018  figures/figure7_robustness.pdf
```

The PNG renders, source and PNG hashes, PDF point dimensions and byte sizes are recorded in `.cache/pdf_qa/render_manifest.json`. Rendering ran sequentially and measured a 45,158,400-byte peak process working set. The first post-render guard measured 16,937,587 project bytes including Git, 8,877,326,336 free disk bytes and 666,980,352 available RAM bytes. The corrected Figure 1 repeat render used a 40,411,136-byte process peak, with 8,878,092,288 free disk bytes and 561,270,784 available RAM bytes. Rendering did not change any source PDF.

Disposable rendered PNGs and the verified installation wheel were removed after visual QA. The installed workspace renderer and the render hash manifest remain available.
