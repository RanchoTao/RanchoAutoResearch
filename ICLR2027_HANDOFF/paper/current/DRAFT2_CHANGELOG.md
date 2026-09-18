# Draft 2 changelog

Draft 2 is a scientific-compression pass over the official-format Draft 1. It
does not contain new experiments, new literature claims, or formatting-rule
changes.

## Main-text changes

| Section | Change | Reason |
| --- | --- | --- |
| Introduction | Reduced repeated motivation, evidence recitation, and scope caveats; retained the exact three-part contribution and prohibited-claim boundary. | State the paper's question and result once. |
| Related Work | Collapsed paper-by-paper summaries into five collision-oriented paragraphs. | Preserve positioning while removing background detail. |
| Experimental Setup | Kept the intervention, all primary metrics, statistical unit, matching logic, uncertainty, and equivalence rule; moved exact allocations, calipers, and selection counts to Appendix A. | Keep the contract auditable without spending main-text space on implementation detail. |
| Sections 4--7 | Scientific prose and numerical evidence unchanged. Only figure paths were redirected to byte-identical local package copies. | Protect the validated result chain. |
| Discussion | Removed repeated numerical summaries and compressed caveats into scope, construct-validity, and mechanism/repair paragraphs. | Concentrate interpretation and negative evidence. |
| Conclusion | Reduced to the strongest defensible result and the unidentified-mechanism boundary. | Avoid repeating the abstract. |

## Appendix and figures

- Added exact run/checkpoint allocation, selection counts, matching calipers,
  confidence bins, direction-gate statistics, and continuous-alpha support
  details to the appendix.
- Retained empirical Figures 1--4 with their original pixels.
- Removed the manuscript-native conceptual Figure 5 because it repeated the
  prose argument and carried no independent evidence.
- Rewired all figure references to package-local files so the Overleaf archive
  has no dependency on directories outside the paper tree.

## Quantitative compression

- Draft 1 scientific main-text words (detex estimate): 3,943.
- Draft 2 scientific main-text words (detex estimate): 3,015.
- Approximate main-text reduction: 928 words (23.5%).
- Appendix words: 761 to 931; approximately 170 words of frozen protocol and
  negative-evidence detail were added there.
- Draft 1 main text: 10 pages. Draft 2 main text: 8 pages.

**NO VALIDATED NUMERICAL RESULT WAS CHANGED.**

The official ICLR style files, font sizes, margins, line spacing, and anonymity
mode were not modified.
