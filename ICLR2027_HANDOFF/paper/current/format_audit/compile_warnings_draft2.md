# Draft 2 compile-warning audit

The authoritative log is from a clean build of the extracted Overleaf ZIP.

- LaTeX errors: 0
- Undefined citations: 0
- Undefined references: 0
- Overfull boxes: 0
- Underfull boxes: 4

The underfull notices are limited to the long title line and three lines in the
Appendix A provenance paragraph containing long artifact paths. They do not
produce visible clipping, overlap, or margin overflow. The Perl locale message
printed by `latexmk` is an environment warning, not a manuscript warning.
