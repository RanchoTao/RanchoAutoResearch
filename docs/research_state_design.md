# Research State Schema v0.1 design

## Scope

Research State v0.1 adds a machine-readable state layer to AutoResearchClaw. It
does not change the research pipeline, execute research, replace legacy reports,
or implement a Dashboard. The canonical contract is
`schemas/research_state_v0.1.schema.json`; YAML and JSON documents conforming to
that contract are the source of truth.

## Non-negotiable principles

1. **Research is a graph, not a chat log.** Conversation may explain work, but
   durable state is represented by linked research objects.
2. **Decisions are evidence-backed, not labels.** A decision records supporting
   and opposing evidence, uncertainty, authorship, timestamp, and next action.
3. **Historical decisions are preserved.** Later decisions append to history
   and may point to `supersedes`; they do not erase earlier decisions.
4. **Agent output is not automatically trusted.** Every trust-sensitive object
   records human verification separately from agent status.
5. **KILL can apply to a branch, not necessarily the whole project.** Decision
   `scope` and `target_id` make the affected object explicit.
6. **FROZEN is reversible; KILL is epistemic rejection.** Project lifecycle
   state and research verdict are distinct fields.
7. **RESTRICTED GO must specify the surviving claim.** The linked hypothesis,
   claim, assumptions, exclusions, and evidence define the restriction.
8. **Every theorem needs dependency and verification state.** A theorem links
   lemmas, proof attempts, counterexample attempts, papers, gaps, and human
   verification.
9. **Every claim should expose provenance.** Supporting and opposing evidence
   remain visible simultaneously.
10. **Dashboard is a view over research state, not the source of truth.** UI
    actions must produce validated state changes or append-only records.

## Storage architecture decision

### Options considered

| Property | Option A: YAML/JSON files | Option B: SQLite | Option C: SQLite source + generated views |
|---|---|---|---|
| Git friendliness | Excellent diffs; per-project files can merge | Binary diffs; poor merge behavior | Source DB remains hard to diff |
| Queryability | Adequate for one project; cross-project scans required | Excellent SQL queries | Excellent |
| Schema evolution | Explicit schema version and migrations | Requires SQL migrations | Requires DB and view migrations |
| Dashboard integration | Direct API parsing; index may be added | Direct and efficient | Direct and efficient |
| Merge conflicts | Localized but possible in large arrays | Whole-file conflict | Whole-DB conflict plus generated-file churn |
| Human editing | Strong, especially YAML | Weak without tooling | Views readable but not canonical |
| Portability | A directory and standard text files | Single portable file, but SQLite-aware tooling required | More moving parts |
| Agent access | Safe read/patch with ordinary tools | Requires transaction/query discipline | Requires DB discipline and generation pipeline |

### v0.1 choice

**Choose Option A: canonical structured YAML/JSON plus generated Markdown and
Mermaid views.**

Reasons:

- Current AutoResearch projects already live in Git-oriented workspaces with
  Markdown, CSV, and code artifacts.
- State remains inspectable and recoverable when the CLI is unavailable.
- Agents can make narrow, reviewable patches without database locking.
- JSON Schema provides an explicit contract independent of Python classes.
- The current scale is one state document per research project, not a
  high-write multi-user service.

For larger portfolios, SQLite should be introduced later as a **disposable
materialized read model/index generated from canonical state files**, not as a
second source of truth. This preserves Git history while enabling fast
cross-project queries.

## Document envelope

Each project state contains:

- `schema_version`: exact contract version;
- `migration`: source/target version, timestamp, migration ID, and notes;
- one `project` object;
- arrays for all remaining core object types.

Collections are explicit even when empty. This avoids absent-field ambiguity
and makes migrations deterministic.

## ID convention

Research State uses **prefixed ULIDs**:

```text
proj_01M17ZEH007KG04GE8NASNVVG4
hyp_01M17ZEH01AXR0EPS18S3YRPW0
claim_01M17ZEH03B2ZJ0D95S5XY6WJM
```

Prefixes are `proj`, `hyp`, `claim`, `ev`, `paper`, `thm`, `lem`, `exp`,
`run`, `dec`, `dep`, `art`, `chk`, and `task`.

- The 26-character Crockford Base32 payload is ULID-compatible.
- The timestamp component makes newly created IDs sortable.
- The prefix makes logs, broken references, and graph nodes debuggable.
- IDs are generated once and remain stable across edits, moves, and migrations.
- Titles and slugs are not IDs; renaming must not change identity.
- A random short hash alone was rejected because it is not sortable. UUIDv4 was
  rejected for v0.1 because it lacks temporal ordering and readable type cues.

## Human verification

Trust-sensitive objects use:

```text
UNREVIEWED
PARTIALLY_REVIEWED
VERIFIED
REJECTED
```

This is independent of workflow status. In particular:

- `Theorem.status = PROVED_BY_AGENT` does not imply
  `human_verification = VERIFIED`.
- A human-reviewed agent proof should be promoted to
  `Theorem.status = HUMAN_VERIFIED` with a new evidence/decision record.
- `Evidence.verified` means its source/artifact was checked; the separate human
  verification field records epistemic review.

The validator rejects a theorem that simultaneously claims
`PROVED_BY_AGENT` and human `VERIFIED` without status promotion.

## Decision metrics

Objects may attach optional `decision_metrics` in `[0, 1]`:

- novelty;
- theorem feasibility;
- empirical support;
- collision risk;
- technical risk;
- estimated cost;
- expected information gain.

These are heuristic metadata, not objective truth. Missing values remain
`null`. The system must not compute a weighted average that automatically
decides GO/KILL. A valid Decision always preserves reasoning and evidence.

## Core object contracts

The lists below summarize the contract. The JSON Schema is normative for exact
types and enums.

### Project

- **Purpose:** root aggregate for one research project; separates lifecycle
  state from epistemic research verdict.
- **ID:** `proj_<ULID>`.
- **Required fields:** ID, title, short name, description, creation/update time,
  status, domain, owners/advisors, repository, current operational and research
  decisions, research verdict, phase, priority, tags, dependencies, active
  hypotheses, next action, resume point, freeze/archive timestamps.
- **Optional fields:** decision metrics.
- **Status:** `IDEA`, `AUDITING`, `RUNNING`, `BLOCKED`, `FROZEN`,
  `PAPER_WRITING`, `SUBMITTED`, `ACCEPTED`, `REJECTED`, `KILLED`, `ARCHIVED`.
- **Relations:** contains all objects; points to current decisions,
  dependencies, active hypotheses, and next task.
- **Lifecycle:** IDEA → AUDITING/RUNNING; may become BLOCKED/FROZEN; KILLED is
  not FROZEN; publication states do not delete research history.
- **Example:** the Emergent Lévy project is `FROZEN` while its research verdict
  remains `RESTRICTED_GO`.

### Hypothesis

- **Purpose:** falsifiable research branch, including forks and narrowed forms.
- **ID:** `hyp_<ULID>`.
- **Required fields:** project, statement/formal statement, status, parent,
  children, assumptions, supporting/attacking claims, creator/timestamps,
  confidence, kill reason, human verification.
- **Optional fields:** creating AgentRun.
- **Status:** `PROPOSED`, `UNDER_TEST`, `SUPPORTED`, `RESTRICTED`, `REFUTED`,
  `SUPERSEDED`, `FROZEN`.
- **Relations:** parent/children form a hypothesis tree; Claims support or
  attack branches; Decisions target one branch explicitly.
- **Lifecycle:** proposed → tested → supported/restricted/refuted; a child may
  survive after its parent is killed.
- **Example:** the broad jump-versus-burst hypothesis is REFUTED; its
  estimator-transfer child is RESTRICTED.

### Claim

- **Purpose:** one precise theoretical, empirical, novelty, literature,
  engineering, assumption, or interpretation statement.
- **ID:** `claim_<ULID>`.
- **Required fields:** project, statement/type/scope/status/confidence,
  supporting and opposing evidence, dependencies, sources, creator/reviewers,
  timestamps, human verification.
- **Optional fields:** AgentRun and notes.
- **Status:** `PROPOSED`, `ACTIVE`, `SUPPORTED`, `RESTRICTED`, `REFUTED`,
  `SUPERSEDED`, `FROZEN`, `UNVERIFIED`.
- **Relations:** Evidence supports/opposes; Dependencies gate validity; source
  links preserve provenance.
- **Lifecycle:** proposed → active → supported/restricted/refuted; later
  verification appends evidence rather than erasing contrary evidence.
- **Example:** “the audit did not identify a prelimit-to-Lévy estimator-transfer
  theorem” is RESTRICTED to the documented search, not universalized.

### Evidence

- **Purpose:** normalized support or opposition from papers, theorems,
  experiments, counterexamples, simulations, benchmarks, derivations, code, or
  expert feedback.
- **ID:** `ev_<ULID>`.
- **Required fields:** project, type/title/summary, supported and opposed
  Claims, strength, source links, timestamp, verification, notes.
- **Optional fields:** Artifact, Paper, Experiment, Theorem, AgentRun, URI, and
  human source are nullable but explicitly present.
- **Status:** no mutable workflow status; `strength`, `verified`,
  `verification_status`, and `human_verification` describe state.
- **Relations:** may simultaneously support one Claim and oppose another.
- **Lifecycle:** append-only; correction creates new Evidence or a Decision
  marking earlier evidence rejected.
- **Example:** the executed crossover pilot supports a restricted empirical
  claim while opposing the broad interpretation.

### Paper / LiteratureRecord

- **Purpose:** verified bibliographic and collision-analysis record.
- **ID:** `paper_<ULID>`.
- **Required fields:** metadata, source paths/links, status, reading priority,
  relevance/collision fields, cluster, contributions/theorems, overlap,
  limitations, cited Claims, verification, last check, optional Artifact link.
- **Optional/null fields:** year, venue, DOI, arXiv, URL, PDF path, scores, and
  last check may be null when unavailable.
- **Status:** `IDENTIFIED`, `SCREENED`, `VERIFIED`, `EXCLUDED`, `RETRACTED`,
  `UNVERIFIED`; reading priority is `MUST_READ`, `SHOULD_READ`, `BACKGROUND`, or
  `NOVELTY_THREAT`.
- **Relations:** provides Evidence and is cited by Claims/Theorems.
- **Lifecycle:** identified → screened → verified/excluded; metadata conflicts
  remain visible and must not be guessed.
- **Example:** unavailable Paper I is UNVERIFIED with unknown author/year rather
  than a fabricated citation.

### Theorem

- **Purpose:** mathematical result candidate with explicit proof and
  counterexample provenance.
- **ID:** `thm_<ULID>`.
- **Required fields:** project, title/statement/formal statement, status,
  assumptions, dependencies, required Lemmas, proof and counterexample AgentRuns,
  known gaps, Papers, supporting Claims, confidence, review/human verification,
  timestamps.
- **Optional/null fields:** formal statement and confidence may be null.
- **Status:** `CONJECTURED`, `FORMALIZED`, `PROOF_SEARCH`, `PARTIAL_PROOF`,
  `PROVED_BY_AGENT`, `COUNTEREXAMPLE_FOUND`, `REFUTED`, `HUMAN_VERIFIED`,
  `SUBMITTED`.
- **Relations:** depends on Lemmas/Dependencies, cites Papers, receives AgentRun
  attempts, and supports Claims.
- **Lifecycle:** conjectured → formalized/search → partial/proved/refuted;
  agent proof and human verification never collapse into one state.
- **Example:** estimator-specific transfer is CONJECTURED and blocked by an
  unverified quantitative rate.

### Lemma

- **Purpose:** node in a theorem dependency DAG.
- **ID:** `lem_<ULID>`.
- **Required fields:** project, title/statement/status, parent Theorems,
  dependencies, proof attempts, Papers, counterexample Evidence, notes, human
  verification.
- **Optional fields:** notes may be null.
- **Status:** theorem-like statuses through `HUMAN_VERIFIED`.
- **Relations:** belongs to one or more Theorems and may depend on Lemmas,
  Papers, or other objects.
- **Lifecycle:** conjectured → formalized/search → proved/refuted.
- **Example:** one lemma controls one coarse increment; a second propagates the
  error over dependent observations.

### Experiment

- **Purpose:** preregistered or executed empirical test, including negative and
  aborted outcomes.
- **ID:** `exp_<ULID>`.
- **Required fields:** project, title/goal, tested Hypotheses, config, dataset,
  code, status/times, compute, metrics/results, Artifacts/Evidence,
  interpretation, failure, reproducibility, seed, environment, AgentRun.
- **Optional/null fields:** code, times, interpretation, failure, seed, AgentRun.
- **Status:** `PLANNED`, `RUNNING`, `PASSED`, `FAILED`, `INCONCLUSIVE`, `ABORTED`.
- **Relations:** tests Hypotheses, emits Evidence/Artifacts, is executed by an
  AgentRun.
- **Lifecycle:** planned → running → terminal status; raw result history is
  append-only.
- **Example:** the fixed-width pilot PASSED its descriptive thresholds without
  validating the broad theorem.

### AgentRun

- **Purpose:** append-only record for each bounded AutoResearch/Codex/proof run.
- **ID:** `run_<ULID>`.
- **Required fields:** project, role/model/prompt, times/duration, task,
  input/output object IDs, Artifacts, created/modified Claims, proposed
  Decisions, errors, compute/tokens/cost, status.
- **Optional/null fields:** model, prompt, timing, tokens, and cost may be null
  when legacy records lack them.
- **Status:** `PLANNED`, `RUNNING`, `COMPLETED`, `FAILED`, `ABORTED`, `BLOCKED`.
- **Relations:** consumes and produces graph objects; it proposes but does not
  silently enact trusted conclusions.
- **Lifecycle:** planned → running → terminal; never overwrite a completed run.
- **Example:** literature-search and counterexample runs are separate records.

### Decision

- **Purpose:** append-only epistemic or operational transition with evidence.
- **ID:** `dec_<ULID>`.
- **Required fields:** project, decision type, scope/target, reasoning,
  supporting/opposing Evidence, confidence, decider/AgentRun, timestamp,
  superseded decision, next task, optional metrics, human verification.
- **Optional/null fields:** confidence, AgentRun, supersedes, next action, and
  metrics.
- **Type enum:** `GO`, `RESTRICTED_GO`, `KILL`, `FREEZE`, `RESUME`, `BLOCK`,
  `UNBLOCK`, `PRIORITIZE`, `DEPRIORITIZE`.
- **Relations:** targets Project/Hypothesis/Claim/Theorem/Experiment/Task and
  can supersede an earlier Decision without deleting it.
- **Lifecycle:** immutable after recording except explicit correction metadata.
- **Example:** a KILL targets the original Hypothesis; a later RESTRICTED_GO
  targets the Project; FREEZE records an operational stop.

### Dependency

- **Purpose:** explicit scientific or operational edge, including blockers.
- **ID:** `dep_<ULID>`.
- **Required fields:** source, target, type, status, description, create/resolve
  times.
- **Optional/null fields:** resolution time.
- **Status:** `ACTIVE`, `SATISFIED`, `BLOCKED`, `WAIVED`, `INVALIDATED`.
- **Type:** `REQUIRES`, `BLOCKS`, `SUPPORTS`, `CONTRADICTS`, `EXTENDS`,
  `SUPERSEDES`, `DERIVED_FROM`.
- **Relations:** both endpoints must resolve to known objects.
- **Lifecycle:** active/blocked → satisfied/waived/invalidated; preserve history.
- **Example:** the transfer Theorem REQUIRES the unavailable Paper I rate.

### Artifact

- **Purpose:** content-addressed registry for reports, code, data, figures,
  proofs, checkpoints, and other files.
- **ID:** `art_<ULID>`.
- **Required fields:** type/path/title/description, creator/AgentRun, timestamp,
  SHA-256, project, related objects, primary flag, version.
- **Optional/null fields:** AgentRun and hash may be null only when unavailable.
- **Status:** no mutable status; `version` and new Artifact records preserve
  revisions.
- **Relations:** any object may reference an Artifact; related object IDs are
  validated.
- **Lifecycle:** append new version with a new Artifact ID; do not silently
  repoint an old hash.
- **Example:** the collision matrix and final reports retain real SHA-256 values.

### Checkpoint

- **Purpose:** recoverable project snapshot for FROZEN/RESUME workflows.
- **ID:** `chk_<ULID>`.
- **Required fields:** project/timestamp/reason, status snapshot, current
  Decision, active Hypotheses, blocking Dependencies, next Task, resume
  instructions, Git commit, Artifacts.
- **Optional/null fields:** Decision, Task, and Git commit.
- **Status:** state is encoded in `status_snapshot`; checkpoints are append-only.
- **Relations:** snapshots Project state and all resume-critical IDs.
- **Lifecycle:** created at meaningful boundary; RESUME creates a new Decision
  and later Checkpoint without deleting the frozen one.
- **Example:** the Emergent Lévy checkpoint freezes at Paper I acquisition.

### Task / NextAction

- **Purpose:** bounded next action sortable by priority, cost, and expected
  information gain.
- **ID:** `task_<ULID>`.
- **Required fields:** project, title/description, priority/status, target,
  dependencies, cost, information gain, assigned agent/AgentRun, timestamps,
  due date, result object IDs.
- **Optional/null fields:** target, information gain, assigned agent/run, due.
- **Status:** `TODO`, `READY`, `BLOCKED`, `IN_PROGRESS`, `DONE`, `CANCELLED`.
- **Relations:** targets a research object and links prerequisites/results.
- **Lifecycle:** TODO/READY → in progress → done/cancelled; a blocker is explicit.
- **Example:** “Obtain and audit Paper I” is READY and targets its unverified
  LiteratureRecord.

## Append-only and mutable boundaries

- Append-only by default: AgentRun, Decision, Evidence, completed Experiment
  result, Checkpoint, and immutable Artifact versions.
- Status-bearing nodes such as Project, Hypothesis, Claim, Theorem, Dependency,
  and Task may update their current fields, but the Decision/Evidence history
  explains each transition.
- Correcting a source does not delete prior evidence. Add the correction and
  mark rejection through human verification or a Decision.

## Schema evolution

- Every document states `schema_version` and migration metadata.
- v0.x additions should be backward-compatible where possible.
- Breaking changes require a new schema file and an idempotent migration.
- IDs remain unchanged across schema migrations.
- Unknown legacy facts remain `null`, `unknown`, or `UNVERIFIED`; migration is
  not permission to infer missing history.

