# Page-budget audit

## Official rule

The local ICLR 2027 instructions set a strict 9-page main-text limit for the
initial submission, with unlimited additional pages for citations. The AI use,
ethics, and reproducibility statements do not count toward that limit.

## Compiled structure

- Physical pages containing main text: pages 1--10.
- Conclusion ends: page 10.
- Required/recommended statements: page 10, after the conclusion.
- References start: page 10.
- References occupy: parts of pages 10--11 (2 physical pages).
- Appendix starts: page 11, after the references.
- Appendix occupies: parts of pages 11--13 (3 physical pages).
- Total PDF length: 13 pages.

## Result

`PAGE-BUDGET-REQUIRES-EDITORIAL-CUT`

The submission uses a tenth main-text page and therefore exceeds the official
limit by 1 physical page. Approximately one third of page 10 is scientific main
text (the end of Discussion and the Conclusion); the remainder contains
non-counting statements and references. No margin, font, spacing, or float hack
was applied.

## Approximate main-section usage

These are visual occupancy estimates under the official style; they exclude
title whitespace and do not sum exactly because sections share pages and floats
move independently.

| Component | Approximate pages | Physical span |
|---|---:|---|
| Abstract | 0.4 | 1 |
| Introduction | 1.1 | 1--2 |
| Related Work | 0.8 | 2--3 |
| Experimental Setup | 1.3 | 3--4 |
| Core Results / Reproducibility | 1.0 | 4--5 |
| Functional Damage | 1.0 | 5--6 |
| Family Residual | 1.2 | 6--7 |
| Output Geometry | 0.7 | 7--8 |
| Discussion and Limitations | 1.6 | 8--10 |
| Conclusion | 0.2 | 10 |

## Ranked editorial compression opportunities

1. **Discussion and Limitations**: largest section; consolidate repeated scope
   boundaries and move implementation-level repair detail to the existing
   appendix without weakening the main limitation disclosure.
2. **Experimental Setup**: move exact matching-caliper and stream-construction
   details to Appendix C/E while retaining the estimands, preregistration, and
   statistical unit in the main paper.
3. **Introduction plus Related Work**: remove duplicated explanations of the
   broad collision and protocol dependence while keeping No Free Swap and
   SteerCheck prominent.

The central family-residual section is also large (about 1.2 pages) but is not
recommended as the first cut because it contains the paper's primary evidence.
