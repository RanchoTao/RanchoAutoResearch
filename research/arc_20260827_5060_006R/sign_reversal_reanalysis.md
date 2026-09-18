# Sign-reversal reanalysis

The exact ARC-006 convention (`sign(cell residual) != aggregate negative sign`)
is retained; zero cells therefore count as reversals. Strict-positive and zero
counts are shown separately.

- Old reversals: **18/103**.
- Corrected reversals: **24/103**.
- Old/corrected strict-positive: 17 / 24.
- Old/corrected zero: 1 / 0.
- Cells changing membership: **8**.

Changed cell identities are in `sign_reversal_membership_changes.csv`; the
run-by-checkpoint distribution is in `sign_reversal_distribution.csv`. No old
label is reused as the corrected label.
