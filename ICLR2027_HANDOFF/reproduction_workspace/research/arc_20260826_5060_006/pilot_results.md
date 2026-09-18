# Blinded pilot results

No `D_S`, agreement, top-1, or confidence outcome was computed or inspected.

## Design and integrity

- 16 disjoint pilot targets: seeds 1/4 x steps 14k/143k x layers 2/5/8/10.
- All four checkpoint harnesses passed.
- Zero target solutions selected a beta boundary.
- KL and NLL were nondecreasing in beta for 16/16 targets.
- Selected-beta independent verification reproduced KL/NLL bit-for-bit.
- Initial search used 15 unique beta trials per target.

## Feasibility

- Class A: 8/16 (50.0%).
- Class A+B: 14/16 (87.5%).
- Class C: 2/16, both seed1 step14k (layers 8 and 10).
- Mean relative KL error: 4.83%.
- Mean relative NLL error: 5.14%.
- Runtime: 151.15 seconds; peak allocated CUDA 1,062,193,152 bytes.

The two Class C targets had opposing coordinate compromises consistent with a
one-dimensional damage-manifold mismatch, not search-bound clipping.

## Precision probe

Seed1 was repeated with 14 golden refinements and 0.0005 stopping width. All
8/8 match classes were identical. The maximum objective improvement was 0.0189;
both Class C targets remained C. The refined settings are retained for
confirmation to remove avoidable numerical-resolution criticism, not because
they changed feasibility.

## Decision

Inverse targeting is technically feasible but cannot guarantee exact joint
matching for every cell. Proceed to the complete systematic 150-cell target
set under prespecified coverage gates. Do not restrict confirmation to the
pilot-easy layers or runs.

