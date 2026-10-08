# Immutable public source import

`source-v1.tar.gz` is the exact archive returned by https://arxiv.org/src/2610.01165v1 on 2026-10-07. Its SHA-256 and size are in `dependencies.json`. The archive includes the final manuscript, canonical figures/tables, exported scientific caches, protocols and the original ancillary SHA256SUMS. It is not the older Candidate A freeze or ICLR handoff.

arXiv expanded `anc/source/data/broad/window_counts.npz` into 35 `.npy` archive members. In the disposable copy only, `reproduce.py` restores the NPZ with `numpy.savez_compressed` in archive member order. The restored bytes must match the original ancillary manifest hash `e4df41b3fc593683fefd67059cabaa199f2ef28ca9426507cca2f5c40fb8ef8f`. This repackages saved integer arrays and computes no measurements, bootstrap intervals or fitted models. All 103 original ancillary manifest entries can then be verified without changing the manifest.

The published protocols are retained reader-oriented transcriptions, as explicitly disclosed by the release; they do not become new preregistrations. Original-record hashes within protocols and exported-copy hashes have different scopes. Historical frozen records remain unchanged at their existing paths.

`legacy-inputs.sha256` hashes the actual checkout bytes of the existing scientific paths at base commit `e6bcfaf280022a8ac682157222e567ed4b9b58f5`. It is an additive preservation check, not a replacement or reseal of any historical integrity manifest. No remote tags were advertised when checked; the historical freeze tag declaration is retained without manufacturing a missing ref.
