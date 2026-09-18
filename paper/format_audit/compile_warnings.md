# Compile warnings

## Final clean build

- Build: `latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex`
- LaTeX fatal errors: 0
- Undefined citations: 0
- Undefined references: 0
- Duplicate labels: 0
- Missing figures: 0
- Overfull boxes: 0
- Final-log layout warnings: 6

## Residual warnings

1. One underfull horizontal box in the long title line.
2. One underfull vertical box while completing page 3.
3. Three underfull horizontal boxes in Appendix A's long artifact-path
   paragraph.
4. One underfull vertical box while completing page 12.

All six are benign whitespace/stretch warnings. Visual inspection found no
clipping, overflow, overlap, or unreadable content. They are retained rather
than changing scientific text or official geometry solely to silence warnings.

`latexmk` also emits a Windows/Perl locale fallback notice before compilation;
this is a tool-environment diagnostic, not a LaTeX document warning, and does
not affect the PDF.
