# Draft 2 Overleaf package audit

## Package

- Archive: `paper/output/candidate_a_iclr2027_draft2_overleaf.zip`
- Archive root: `candidate_a_iclr2027_draft2/`
- Entry point: `main.tex`
- Engine: pdfLaTeX
- Bibliography: BibTeX with the packaged official ICLR 2027 `.bst`
- Entries: 33 ZIP entries (32 files plus one directory entry)
- Package size: 783,277 bytes (approximately 765 KiB)

The archive contains the manuscript sections, appendix, result table,
references, numerical provenance table, nine empirical PNG panels, build
instructions, and all seven locally supplied official style/template support
files. Figure paths are package-local.

## Independent build verification

1. The source tree was cleaned before packaging.
2. The ZIP was expanded into a new directory outside the source tree.
3. `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex` was run from
   the extracted archive root.
4. The resulting 11-page PDF became the delivered Draft 2 PDF.

Result: **PASS**. BibTeX ran, all cross-references resolved, all citations
resolved, and no external repository file was needed. The final log contains
no LaTeX error, overfull box, undefined citation, or undefined reference. It
contains four underfull-box notices: one title-line notice and three notices
from long provenance paths in Appendix A. Visual inspection confirms that none
causes clipping or overlap.

## Integrity and policy checks

- Official style directory differs from the pre-compression commit: **no**.
- Anonymous author block present: **yes**.
- Personal names, local Windows paths, and repository URLs in PDF text: **none
  detected**.
- Required AI-use, ethics, and reproducibility statements present: **yes**.
- Figure copies match their sealed ARC source PNGs byte-for-byte: **9/9**.
- New experiment or recomputed scientific result: **none**.
- Missing dependency in extracted build: **none**.

No `.aux`, `.bbl`, `.blg`, `.fdb_latexmk`, `.fls`, `.log`, `.out`, or PDF build
artifact is present in the ZIP. The extracted build creates its bibliography
normally from `references.bib`.
