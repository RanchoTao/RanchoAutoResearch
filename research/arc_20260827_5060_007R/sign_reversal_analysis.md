# Corrected sign-reversal analysis

All corrected 24/103 reversal cells were retained. A preregistered
leave-one-pretraining-run-out L2 logistic model used intact margin and paired
family differences in boundary displacement, log norm, and absolute cosine.

- Held-out AUC: `0.6640`
- Held-out balanced accuracy at 0.5: `0.6498`
- Frozen gate: AUC >=0.70 and balanced accuracy >=0.65
- Result: **not predictively informative**

Reversal cells had lower mean paired boundary displacement (`-0.00787` versus
`0.01302`) and higher mean log-norm ratio (`0.07898` versus `0.05038`), but
these group associations did not generalize strongly enough across runs.

Hardest true reversals for the frozen classifier were:

| Cell | Predicted reversal probability |
| --- | ---: |
| r2_s14000_l10 | 0.151 |
| r6_s143000_l3 | 0.186 |
| r2_s72000_l10 | 0.206 |

The geometry tested here does not explain the corrected sign reversals. They
remain scientifically meaningful unexplained heterogeneity, not removable
noise.
