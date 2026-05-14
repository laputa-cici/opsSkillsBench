# Source and Provenance

Status: `runnable_external_source`

Note: the current runnable data slice is a compact deterministic derivative of the OR-Library `ft06` job-shop instance. Raw data is stored locally under an ignored `sources/datasets/.../raw/` path; only the small derived task slice is committed.

## Dataset

Primary dataset:

- OR-Library Job Shop Scheduling
- Source: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/jobshopinfo.html
- Raw file: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/jobshop1.txt
- Local provenance: `sources/datasets/orlib-jobshop/provenance.md`
- Preprocessing script: `scripts/preprocess/build_orlib_disruption_recovery.py`
- Selected instance: `ft06`, Fisher and Thompson 6x6 instance, also known as `mt06`
- Intended use: derive a small job-shop instance, disrupted baseline schedule, bottleneck report, and recovery action planning task.

Derived task inputs:

- `environment/data/jobshop_instance.csv`
- `environment/data/baseline_schedule.csv`
- `environment/data/machine_downtime.csv`
- `environment/data/customer_priority.csv`
- `environment/data/recovery_policy.json`

Transformation summary:

1. Parse the named `ft06` instance from `jobshop1.txt`.
2. Convert machine numbers and operations into benchmark CSV rows.
3. Generate a deterministic round-robin earliest-start baseline schedule.
4. Add fixed downtime windows on `M5` and `M0`.
5. Add benchmark-local due dates, order values, service criticality, and recovery policy enumerations for reproducible scoring.

## Skill Candidates

| Skill | Source | Role |
| --- | --- | --- |
| `capacity-planning` | Agent Skills candidate | Relevant skill for bottleneck and capacity reasoning. |
| `operations-manager` | SkillsMP / `theneoai/awesome-skills`; vendored in `sources/skills/operations-manager` | Operational recovery, KPI, owner assignment, and process-control framework. |
| `supply-chain-manager` | SkillsMP / `theneoai/awesome-skills`; already vendored in `sources/skills/supply-chain-manager` | Broad Plan-Make-Deliver workflow and service/cost/cash/resilience tradeoff framework. |

## Verification

Oracle validation on 2026-04-08:

```bash
.venv/bin/python scripts/run_task_local.py orlib-disruption-recovery-control --oracle --test
```

Result: `3 passed`.
