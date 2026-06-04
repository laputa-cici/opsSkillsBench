# Task Structure Redesign

Last updated: 2026-06-04

## Problem

The previous layout had four scenario-level tasks:

- `online-retail-replenishment-review`
- `dataco-control-tower-exception-review`
- `portland-sourcing-concentration-review`
- `orlib-disruption-recovery-control`

Each scenario contained several verifier checks, but benchmark reporting still counted only four tasks. That is too coarse for a SkillBench: we need many independently counted items per operations problem domain.

## New Convention

A benchmark task is now any directory under `tasks/` that contains `task.toml`.

This supports:

```text
tasks/<legacy-scenario-task>/
tasks/<problem-domain>/<atomic-task>/
```

The runner discovers tasks recursively, so future domains can add dozens of task directories without changing the harness.

## Current Domains

| Domain | Scope | Current atomic tasks |
| --- | --- | ---: |
| `inventory` | Replenishment, stockout risk, inventory exception handling | 3 |
| `fulfillment` | Order allocation, delivery risk, control-tower actions | 7 |
| `procurement` | Sourcing strategy, supplier concentration, risk registers | 3 |
| `scheduling` | Job-shop recovery, capacity, bottleneck action planning | 3 |

## Split Strategy

The first restructuring pass split the existing scenario verifier checkpoints into standalone runnable tasks:

| Parent task | New atomic surfaces |
| --- | --- |
| `online-retail-replenishment-review` | schema/order, replenishment values, exception register |
| `dataco-control-tower-exception-review` | order actions, lane risk register, scorecard summary |
| `portland-sourcing-concentration-review` | Kraljic matrix, supplier action plan, procurement risk register |
| `orlib-disruption-recovery-control` | recovery schedule, schedule metrics, bottleneck/action plan |

The old scenario-level tasks remain in place for continuity with prior experiment logs.

The second restructuring pass added four prototype fulfillment allocation tasks from the operations backlog:

| Domain | New atomic surfaces |
| --- | --- |
| `fulfillment` | nearest feasible distribution center, capacity-aware allocation, SLA risk estimation, split-order decision |

## Harness Changes

`scripts/run_task_local.py` now:

- recursively discovers every `task.toml`;
- accepts full task names such as `fulfillment/dataco-order-risk-actions`;
- accepts a unique basename such as `dataco-order-risk-actions`;
- reports an ambiguity error if a basename matches more than one task.

`scripts/run_benchmark_local.py` imports the same discovery functions, so `--all` now includes both legacy scenario tasks and nested atomic tasks.

## Scaling Direction

The next step is to create more task variants per domain rather than adding only more scenario-level tasks. Good variants include:

- different data slices from the same source;
- alternate thresholds in policy files;
- separate framework taxonomy fields;
- separate operational action mappings;
- edge cases for noisy data, missing records, capacity limits, or supplier constraints.

For paper experiments, the recommended default is to run atomic tasks and use legacy scenario tasks only as integration or smoke tests.
