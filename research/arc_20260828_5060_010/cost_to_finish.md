# Cost to finish

These are forward-looking costs only; prior ARC work is sunk and excluded.
AutoDL is not authorized or currently justified.

| Scenario | Human hours | Local GPU hours | Potential AutoDL hours | Added disk | Network | API cost | Calendar |
|---|---:|---:|---:|---:|---:|---:|---:|
| Optimistic | 30–40 | 1–2 | 0 | <1 GB beyond existing caches | <0.1 GB if a corpus is already cached | USD 0 | 2 weeks |
| Expected | 55–75 | 3–6 | 0 initially | 2–5 GB | 0.2–2 GB | USD 0 | 4–6 weeks |
| Pessimistic | 100–140 | 10–20 | 8–15 only after explicit approval and a passed gate | 10–25 GB | 5–20 GB | USD 0 unless separately approved | 8–10 weeks |

## Cost composition

- 12–20 human-hours: primary-source novelty audit and collision matrix.
- 6–12 human-hours plus 1–2 local GPU-hours: selected cross-corpus experiment,
  preregistration, analysis, figures, and report.
- 6–12 human-hours plus 0–1 local GPU-hour: alternative-metric construct audit.
- 10–20 human-hours: unified reproducibility package and clean-environment test.
- Remaining time: manuscript outline, figure harmonization, limitations, and
  reviewer-control decisions.

The expected case excludes a new model family, 1B scaling, and another mechanism
branch. Those enter only after both the corpus and novelty gates pass.
