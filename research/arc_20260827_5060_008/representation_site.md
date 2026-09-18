# Representation site

The sole primary site is the residual-stream block output immediately after
the intervention-relevant original GPT-NeoX transformer block at frozen module
index `L` (ARC layer values 1-10).

For the same block call:

- `h_before` is the hidden state passed into original block `L`;
- `h_after` is `outputs[0]` returned by original block `L`;
- block-deletion direction is `delta_h_block = h_before - h_after`;
- noise direction is the existing deterministic token-wise normalized Gaussian
  direction used by `NormControlledActivationNoise`;
- all directional injections are applied to `h_after` before block `L+1`.

Thus adding the full token-specific block vector exactly returns the hidden
state to `h_before`; a constant relative magnitude is a controlled directional
analogue, not literal structural layer deletion. Attention output, MLP output,
layer-norm input/output, and other sites are not tested.
