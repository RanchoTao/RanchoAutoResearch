# Paper thesis audit

## Thesis A — conservative

> Across independent small-Pythia pretraining runs, a frozen next-token assay
> reveals a reproducible decline in the top-1 substitutability of interior
> Transformer blocks. The direction survives a second small scale and a second
> intervention family and is not explained by raw perturbation magnitude alone.

This is fully defensible but leaves the most interesting corrected family
residual outside the thesis.

## Thesis B — moderate and recommended

> During small-Pythia pretraining, interior-block top-1 substitutability declines
> reproducibly even as intact language-model fit improves. Predictive damage
> discriminates this decline better than raw perturbation size within the
> original intervention family, yet matching KL and NLL leaves stable
> intervention-family structure that simple output geometry does not explain.

This is the strongest coherent thesis. It accurately joins ARC-003 through
ARC-007R while preserving three boundaries: `S` is an operational next-token
assay, the models are small Pythia variants, and the remaining family component
is not a discovered mechanism.

## Thesis C — aggressive and prohibited

> Pretraining universally causes causal layer specialization in language models
> through intervention-direction geometry, making later models intrinsically
> fragile to layer removal.

This is not defensible. “Universally” exceeds two small Pythia scales and one
exploratory SmolLM2 trajectory; “causal layer specialization” is not identified
by top-1 agreement; downstream fragility is untested; geometry explains only a
minority of the residual; and the direction-causality branch failed its support
gate without revealing the outcome.

## Selection

Use Thesis B, always accompanied by the assay/model/corpus scope. Do not begin a
full manuscript until the single-corpus gap and the local-literature gap are
addressed.

## Working titles

1. **Safest:** *Training Dynamics of Transformer Block Substitutability*
2. **Strongest:** *Pretraining Erodes Transformer Block Substitutability*
3. **Most ICLR-style:** *When Transformer Blocks Stop Being Substitutable*
4. *Predictive Damage Is Not the Whole Story: Intervention-Dependent Block Substitutability*
5. *From Layer Robustness to Layer Dependence Across Language-Model Pretraining*

All are working titles. Titles 2–5 require the scope qualifiers to be explicit
in the abstract.
