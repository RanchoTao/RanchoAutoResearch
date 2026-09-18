# Technical failure log

## Calibration analyzer omission

- No confirmatory outcome existed and calibration `S`/`Delta S` values had not
  been revealed.
- The first damage-support summary implemented the exact-cell-match branch of
  preregistration criterion 4 but omitted its explicit alternative: retain a
  strength needed to cover a different anchor damage quartile.
- Consequence: beta 0.50 was initially marked unretained despite 100% of its
  pilot cells lying jointly inside the historical KL/NLL support and no
  catastrophic cells.
- Fix: define anchor damage quartiles by KL, the frozen primary functional
  variable in ARC-004, while continuing to require joint NLL support. For an
  uncovered quartile, choose the eligible beta closest to its KL midpoint;
  smaller beta is the deterministic tie-break.
- No hypothesis, outcome, broad sweep, run, checkpoint, layer, support bound,
  catastrophic threshold, or confirmatory result was changed or inspected.

