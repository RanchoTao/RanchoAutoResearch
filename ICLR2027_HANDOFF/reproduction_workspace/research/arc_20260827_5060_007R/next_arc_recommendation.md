# Next ARC recommendation

Run exactly one **internal-direction counterfactual** on the same Pythia-160M
Class A assay, prioritizing supported layers 4-6.

At each matched cell/layer, construct paired internal residual-stream
perturbations whose magnitude and achieved KL/NLL plus the frozen M3 output
geometry are approximately matched, but whose direction is taken from the
block-deletion perturbation versus the noise-family perturbation. Then measure
corrected `D_S` under the canonical tie rule.

The discriminating question is whether family residual follows the internal
perturbation direction after functional damage and output geometry are held
approximately fixed. Pre-freeze calipers and require overlap before revealing
`D_S`. This directly targets the dominant unexplained component without a new
model, family, corpus, metric search, or scale increase.

Do not execute automatically. If adequate joint overlap cannot be achieved,
return nonidentifiable rather than loosening calipers.
