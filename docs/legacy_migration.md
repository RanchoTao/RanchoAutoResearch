# Progressive migration from legacy research artifacts

## Goal

Migration adds a structured index and provenance graph around existing files.
It does not rewrite historical reports, reinterpret conclusions, or require all
projects to migrate at once.

## Source inventory

Typical legacy sources include:

- `README.md` for project identity and setup;
- `FINAL_REPORT.md` for conclusions and decision rationale;
- `FROZEN.md` and `RESUME.md` for operational state;
- `search_log.md` and `collision_matrix.csv` for literature provenance;
- theorem/feasibility/counterexample audits;
- experiment configs, raw results, figures, and provenance files;
- code commits and agent conversation/run records.

Original files remain immutable inputs. Each migrated Artifact records path,
version, and SHA-256 when available.

## Migration levels

### Level 0 — legacy only

- No structured state exists.
- Inventory paths and identify which files appear authoritative.
- Do not infer current status from filenames alone.

### Level 1 — Project + Decision + Checkpoint

- Create the project envelope and stable ID.
- Extract explicit GO/KILL/RESTRICTED_GO/FREEZE/RESUME decisions.
- Preserve each historical decision; do not keep only the latest label.
- Add a Checkpoint with blockers, next action, resume instructions, artifact
  paths, and Git commit if available.
- Unknown timestamps, authors, or costs remain null/unverified.

This level is enough for a portfolio Dashboard to answer “what is alive?” and
“where should work resume?”

### Level 2 — Hypothesis + Claim + Evidence

- Split broad and narrowed hypotheses into branches.
- Extract the minimum claims required to explain decisions.
- Create Evidence records for papers, experiments, counterexamples, and human
  review; record both supporting and opposing polarity.
- Link source Artifacts and preserve conservative scope language.

This level supports evidence-backed decision views and novelty threat panels.

### Level 3 — Theorem / Experiment / AgentRun

- Represent theorem statements, assumptions, missing Lemmas, proof and
  counterexample attempts, and human verification.
- Register experiments with exact config, seed, environment, metrics, results,
  compute, and artifacts.
- Add AgentRuns from logs where metadata exist. Do not guess model, tokens,
  duration, or cost.

This level supports theory, experiment, resource, and run history views.

### Level 4 — full provenance graph

- Register all primary Artifacts and hashes.
- Resolve every object reference and blocker.
- Add literature records and collision classifications.
- Add append-only corrections/supersession edges.
- Optionally generate a SQLite portfolio index from validated files.

## File-specific extraction guidance

| Legacy source | Primary objects | Guardrail |
|---|---|---|
| `README.md` | Project, Artifact | Descriptive text is not automatically a decision |
| `FINAL_REPORT.md` | Claims, Evidence, Decisions | Separate measured results from interpretation |
| `FROZEN.md` | FREEZE Decision, Checkpoint, Task | FROZEN must retain a resume point |
| `RESUME.md` | RESUME Decision, Task updates | Never delete the frozen checkpoint |
| `search_log.md` | AgentRun, Artifact, Evidence | Search strategy is not paper evidence |
| `collision_matrix.csv` | Papers, Claims, Evidence | Preserve verified/unverified metadata distinctions |
| experiment report/results | Experiment, Evidence, Artifacts | Record exact seed/config/output and failed runs |
| theorem audit | Theorem, Lemma, Dependencies | Agent proof is not human verification |
| conversation | AgentRun or human Decision | Import only explicit durable facts, not every utterance |

## Migration workflow

1. Copy no content; compute hashes and register existing files as Artifacts.
2. Create Project and stable IDs.
3. Extract explicit decisions in chronological order.
4. Add the smallest hypothesis/claim/evidence graph explaining those decisions.
5. Add blockers and one bounded next action.
6. Validate schema, duplicate IDs, prefixes, and references.
7. Review the generated `status`, `decisions`, `blockers`, and graph views.
8. Ask a human to verify high-impact claims and decisions.
9. Commit the new state file without modifying legacy evidence.

## Updating after migration

- New runs append AgentRun and Artifact records.
- New evidence appends Evidence; it does not overwrite contrary evidence.
- State transitions append Decisions and update current pointers.
- A RESUME creates a new Decision and later Checkpoint.
- Schema upgrades update migration metadata but preserve object IDs.

## Current example

`examples/emergent_levy_project_state.yaml` is a Level-3 migration. It includes
real legacy artifacts and hashes, two hypothesis branches, five claims, five
evidence records, literature threats, a conjectured theorem and Lemmas, one
executed pilot, two AgentRuns with unknown fields left null, three Decisions, a
blocking Dependency, a freeze Checkpoint, and one next Task.

