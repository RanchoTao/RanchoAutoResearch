# ICLR 2027 build

The paper uses the unmodified official files under `iclr2027/` and compiles
from this directory with the locally installed TeX distribution.

## PowerShell

```powershell
Set-Location paper
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

To verify a clean rebuild:

```powershell
latexmk -C main.tex
latexmk -pdf -interaction=nonstopmode -halt-on-error main.tex
```

If `latexmk` is unavailable, use the equivalent explicit sequence:

```powershell
pdflatex -interaction=nonstopmode -halt-on-error main.tex
bibtex main
pdflatex -interaction=nonstopmode -halt-on-error main.tex
pdflatex -interaction=nonstopmode -halt-on-error main.tex
```

The submission entry point is `main.tex`. The final build remains anonymous
because `\iclrfinalcopy` is intentionally not enabled.

The compiled deliverable is copied to:

```text
paper/output/candidate_a_iclr2027_draft1.pdf
```
