# PDF visual QA

Rendered with Poppler at 130 DPI and inspected page by page after the final
clean build.

| Page | Content checked | Result |
|---:|---|---|
| 1 | Anonymous title, under-review header, abstract, Introduction | PASS |
| 2 | Contributions, Related Work transition | PASS |
| 3 | Related Work, Setup, Equation 1 | PASS |
| 4 | Equations 2--9, matching text, core-result transition | PASS |
| 5 | Table 1, three-panel Figure 1, section transition | PASS |
| 6 | Two-panel Figure 2, matched comparisons, family section | PASS |
| 7 | Two-panel Figure 3, corrected residual equations, geometry transition | PASS |
| 8 | Two-panel Figure 4, Discussion transition | PASS |
| 9 | Figure 5, unresolved-mechanism text, limitations | PASS |
| 10 | Implication, Conclusion, three statements, references start | PASS; page-limit overflow documented separately |
| 11 | References end, Appendix A--B | PASS |
| 12 | Appendix C--H | PASS |
| 13 | Appendix I--L and final page | PASS; expected trailing whitespace |

Across all 13 pages:

- no clipped labels or equations;
- no overlapping text, floats, captions, headers, or footers;
- no orphaned heading at a page bottom;
- all five main figures and the main table fit the official text width;
- captions remain attached and readable;
- references and URLs remain legible;
- official line numbering and page numbering render consistently;
- appendix numbering and ordering are correct.

The only submission-format issue is the documented one-page main-text overflow;
visual rendering itself passes.
