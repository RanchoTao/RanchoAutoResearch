# Main-paper figure plan

Use at most five main figures. No new decorative figure is justified.

## Figure 1 — Core training-associated decline

- Panel A: independent 160M trajectories from
  `meta_arc05/ARC-20260826-5060-003/figures/fig1_independent_trajectories.png`.
- Panel B: early-to-late run distribution from
  `meta_arc05/ARC-20260826-5060-003/figures/fig2_late_minus_early_distribution.png`.
- Panel C: run-level intervals from
  `meta_arc05/ARC-20260826-5060-003/figures/fig3_run_level_forest.png`.

Purpose: establish the experimental unit, effect size, and non-cherry-picked run
distribution before any mechanism analysis.

## Figure 2 — Robustness boundaries

- Panel A: fixed-confidence results from
  `meta_arc05/ARC-20260826-5060-003/figures/fig4_confidence_matched.png`.
- Panel B: run × layer heatmap from
  `meta_arc05/ARC-20260826-5060-003/figures/fig5_layer_progress_heatmap.png`.
- Panel C: intact NLL, intervention NLL damage, and KL from
  `meta_arc05/ARC-20260826-5060-003/figures/fig6_functional_metrics.png`.
- Include the 70M summary numerically or as a small inset generated from the
  sealed summary, rather than implying a broad scaling curve.

## Figure 3 — Raw magnitude versus functional damage

- Panel A: `research/arc_20260826_5060_004/figures/fig_c_magnitude_matched.png`.
- Panel B: `research/arc_20260826_5060_004/figures/fig_d_damage_matched.png`.
- Supplemental context only if space permits:
  `fig_a_ds_vs_functional_damage.png` and `fig_b_ds_vs_magnitude.png`.

Purpose: center matched contrasts, not observational regression slopes.

## Figure 4 — Intervention-family replication and corrected residual

- Panel A: qualitative family support from
  `research/arc_20260826_5060_005/figures/fig1_family_damage_support.png`.
- Panel B: canonical repaired residual from
  `research/arc_20260827_5060_006R/figures/fig1_corrected_residual.png`.
- Panel C: corrected layer reanalysis from
  `research/arc_20260827_5060_006R/figures/fig2_layer_reanalysis.png`.

The caption must state that ARC-006 was withdrawn and ARC-006R is canonical.

## Figure 5 — Explanatory boundary

- Panel A: preregistered model sequence from
  `research/arc_20260827_5060_007R/figures/fig3_model_sequence.png`.
- Panel B: geometry-matched/boundary result from
  `research/arc_20260827_5060_007R/figures/fig2_residual_boundary.png`.
- Panel C: reversal failure from
  `research/arc_20260827_5060_007R/figures/fig5_reversal_geometry.png`.

Purpose: show what measured output geometry explains and what remains, without
turning the residual into a mechanism. ARC-008/009 causal-gate failures belong in
the appendix, not a decorative mechanism schematic.
