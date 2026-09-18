# Solver definition

For each frozen cell and family, the direction is unchanged and only scalar
alpha varies in `[0.125 * selected_beta, 2.0 * selected_beta]`.

1. Evaluate the two endpoints.
2. If each target is bracketed, independently bisect KL and NLL damage to a
   relative metric error of 0.25% or a log-alpha interval width of 0.001, with
   at most 14 iterations.
3. Build the candidate pool from endpoints, `selected_beta`, both roots, their
   geometric mean, and every exact evaluation made during bisection.
4. Jointly select block/noise alpha using the unchanged ARC-008 objective.
5. Perform four deterministic bounded coordinate-refinement rounds around the
   current pair, starting with a log-alpha half-step of `log(sqrt(2))` and
   halving it each round. All metrics at candidate alphas are measured by real
   model forwards; interpolation is not used for the final selection.
6. If a target is not bracketed, evaluate a frozen 17-point log-spaced fallback
   grid. The cell remains `FAIL-NO-BRACKET` even if pair balance happens to be
   good, because the frozen downstream target was not reachable.

The unchanged objective is the sum of four target log-errors, block/noise KL
and NLL log-imbalances, half-weighted hidden/output norm log-imbalances, and
five times the absolute output-alignment difference.

No objective component uses top-1 identity, top-1 change, residual, reversal,
or `D_S`.

