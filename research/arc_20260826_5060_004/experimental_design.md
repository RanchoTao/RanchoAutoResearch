# Experimental design

This document operationalizes the frozen preregistration without changing its
scientific criteria.

## Design matrix

| Axis | Frozen values |
| --- | --- |
| Model | PolyPythias/Pythia-160M |
| Pilot runs | seed1, seed4, seed9 |
| Confirmatory runs | seed6, seed7, seed8 |
| Checkpoints | step14000, step72000, step143000 |
| Locations | interior blocks 1-10 of 12 |
| Attenuation | alpha 0.25, 0.50, 0.75, 1.00 |
| Evaluation selections | 11, 23, 37 |
| Sequences | 6 per selection, length 256 |
| Corpus | frozen cached WikiText-2 train text |

Each formal run/checkpoint produces 40 intervention cells and three fixed data
resamples. Intact predictions are evaluated once per batch and reused only as
the comparison target for interventions on that same batch.

## Why this discriminates mechanisms

The strength grid creates overlapping raw-magnitude and functional-damage
ranges across layers. Experiment A compares interventions that move the local
hidden state by nearly the same amount but produce different predictive KL.
Experiment B reverses the control: predictive damage is similar while layer or
raw local displacement differs. Pairing within run and checkpoint blocks the
largest known training/run confounds before any regression is fit.

The alpha family nests the old deletion exactly. It therefore changes the dose
of the existing intervention without changing its target or inventing an
unrelated perturbation family.

## Resource strategy

All requested checkpoints are already in the local Hugging Face cache. Runs
are checkpoint-resumable and save raw JSON after every checkpoint. GPU-active
and peak-memory measurements are recorded inside every checkpoint result;
wall-clock and disk deltas are recorded separately. No network is needed.

## Integrity strategy

- Offline model loading prevents revision drift.
- Immutable Hugging Face commit hashes are written to raw output.
- Wrapper equivalence is checked before formal evaluation.
- The original module list is restored after every intervention and checkpoint.
- Intervention order is a fixed deterministic shuffle and an order-reversal
  check is run on the harness batch.
- Raw results are append-only by checkpoint; completed checkpoints are not
  silently overwritten.
- Aggregation and figures consume raw JSON only and are deterministic.

