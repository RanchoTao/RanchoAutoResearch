# Candidate B resource policy

Campus-network conservation is a hard constraint.

Default policy:

- local-first execution;
- reuse existing model and dataset caches read-only;
- external downloads forbidden unless explicitly approved;
- never repeat model downloads;
- no automatic `pip` upgrades;
- bounded experiment runtime and disk growth;
- one scientific question per ARC;
- an explicit stop condition before execution;
- a compact `EXECUTIVE_SUMMARY` for every completed ARC;
- GO/KILL decisions before expensive validation;
- no AutoDL or paid external compute until local evidence justifies a written
  escalation request;
- no paid API use without explicit approval;
- no cross-project writes into Candidate A directories or artifact IDs.

Before any experiment, record expected information gain, maximum wall/GPU time,
network bytes, disk growth, seeds, and cleanup policy. Stop when the decisive
question is answered rather than consuming the remaining budget.
