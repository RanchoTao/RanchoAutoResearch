# Boundary question — frozen after replication, before checkpoint sweep

## Replicated anchor

Pythia-410M retains most intact top-1 predictions after deletion of a middle
Transformer block, while early/final blocks are more causally sensitive.

## Three candidate variables

### 1. Pretraining progress (selected)

- **Architecture-only prediction:** agreement is already high at initialization
  and changes little after accounting for intact-model output entropy/NLL.
- **Learned-redundancy prediction:** agreement grows with training and saturates
  after language-model competence appears.
- **Learned-specialization prediction:** agreement starts high for near-identity
  random residual blocks, then declines as individual blocks become necessary.

This variable is selected because Pythia exposes immutable checkpoints with the
same architecture/data/order, making it the cleanest causal time coordinate.

### 2. Token predictability

High-margin tokens may dominate headline top-1 agreement. If so, deletion
robustness should be almost entirely explained by intact top-1 confidence rather
than checkpoint age. This is retained as the mandatory trivial-proxy control.

### 3. Model depth

The source reports deeper models are more robust. This is not selected because it
would mostly re-describe the paper and confounds parameter count/compute.

## Single-variable sweep

Discovery model: `EleutherAI/pythia-160m-deduped` at revisions `step0`,
`step1000`, `step10000`, `step50000`, and `step143000`. Architecture and text are
fixed. Every layer is deleted separately on the same three WikiText shards.

Primary magnitude: mean middle-layer top-1 agreement. Secondary: excess NLL and
KL. Confound proxies: intact NLL, entropy, top-1 confidence, and margin.

No phase-transition language will be used. A boundary claim requires a replicated
monotone/reversal pattern plus held-out model prediction beyond the simple proxies.
