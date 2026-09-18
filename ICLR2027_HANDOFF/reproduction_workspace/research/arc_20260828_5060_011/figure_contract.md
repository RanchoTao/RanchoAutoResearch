# Figure contract

Delivery surface: static PNG files inside the ARC directory, generated from
saved CSV/JSON data and inspected in their final form.

| Figure | Analytical question | Form | Grain | Honest-scale rule |
|---|---|---|---|---|
| 1 | Does per-run ΔS agree across corpora? | Paired dot/slope comparison | Six pretraining runs | Shared signed axis with visible zero and exact points. |
| 2 | Does magnitude-matched functional damage replicate? | Run-level interval/dot comparison | Six run medians per corpus | Shared signed axis with zero; no pooled-cell pseudoreplication. |
| 3 | Does fixed-confidence control preserve the effect? | Confidence-bin grouped point plot | Run × eligible fixed bin | Show every run-bin comparison and counts in source table. |
| 4 | How do aggregate effects and uncertainty compare? | Faceted dot-and-interval | Corpus-level estimates from run bootstrap | Shared signed axis; label CI and run N. |

Palette policy: hard two-root cap—blue for WikiText-2, orange for HellaSwag,
with dark-neutral zero/reference lines. Shapes, direct labels, and line styles
must preserve meaning in grayscale. Titles remain neutral descriptions; scope,
sample size, and units appear in subtitles/captions.

