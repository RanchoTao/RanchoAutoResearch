# Geometry definitions

- `c1`: canonical lowest-index intact maximum-logit token.
- `c2`: canonical lowest-index intact runner-up after masking `c1`.
- `m_intact = z[c1]-z[c2]`.
- `delta_boundary = (z'[c1]-z[c1])-(z'[c2]-z[c2])`.
- `delta_margin = (z'[c1]-z'[c2])-m_intact`.
- Identity: `delta_margin == delta_boundary` exactly under the anchored pair.
- `logit_norm = ||z'-z||_2`.
- `cosine = delta_boundary/(sqrt(2)*logit_norm)`.
- `abs_cosine`: fraction-alignment magnitude along the local boundary axis.
- `D_S`: corrected top-1 flip rate; retained rate is `1-D_S`.
- top1-to-runner-up and other-flip rates partition corrected flips.

All family differences are noise minus block at the same frozen
run/checkpoint/layer cell. Intact-margin statistics are shared by both family
rows and never rematched.
