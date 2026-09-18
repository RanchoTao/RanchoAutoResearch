# Anonymous-submission audit

## Status

`ANONYMITY-PASS`

## Checks

- `\iclrfinalcopy` is not enabled.
- The official style renders `Anonymous authors` and `Paper under double-blind
  review` on page 1.
- No real author names, affiliations, emails, acknowledgments, grant numbers,
  personal websites, repository URLs, usernames, or local filesystem paths
  appear in the compiled PDF.
- PDF metadata has empty Title, Subject, Keywords, and Author fields. Creator
  and Producer identify only LaTeX/pdfTeX.
- The PDF is US Letter and carries official submission line numbers and page
  numbers.
- The paper sources compiled by `main.tex` contain no author-identifying
  comments or metadata.
- The preserved official example source contains its vendor-supplied fictional
  author example but is not included by `main.tex` and does not appear in the
  PDF.
- Audit documents contain a local template provenance path but are not part of
  the manuscript or submission PDF.

No anonymity blocker was found.
