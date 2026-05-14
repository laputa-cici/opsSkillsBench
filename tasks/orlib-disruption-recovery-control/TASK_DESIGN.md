# Task Design: OR-Library Disruption Recovery Control

## Goal

Evaluate whether agents can repair a manufacturing schedule under deterministic feasibility constraints and produce an operations recovery control plan.

This task should not be a pure scheduling puzzle. The schedule itself is still machine-checkable, but the paper-facing value should come from bottleneck diagnosis, recovery lever selection, and service/cost tradeoff classification.

## Public Source Basis

| Source type | Planned source |
| --- | --- |
| Dataset | OR-Library Job Shop Scheduling |
| Primary skill candidate | `capacity-planning` if a licensable public skill is found |
| Additional skill candidates | `operations-manager`, `supply-chain-manager` as broad planning support |

## Planned Inputs

| File | Description |
| --- | --- |
| `jobshop_instance.txt` | OR-Library-derived operation routes and processing times. |
| `baseline_schedule.csv` | A valid or near-valid baseline schedule before disruption. |
| `machine_downtime.csv` | Machine downtime windows that invalidate some operations. |
| `customer_priority.csv` | Due dates, order value, and service criticality for jobs. |
| `recovery_policy.json` | Rules for allowed shifts, freeze windows, and metric priorities. |

## Planned Outputs

| File | Description |
| --- | --- |
| `recovery_schedule.csv` | Operation-level repaired schedule. |
| `schedule_metrics.json` | Makespan, tardiness, downtime violations, service recovery, and policy compliance metrics. |
| `bottleneck_report.json` | Bottleneck machine, constrained jobs, root cause, and service/cost tradeoff. |
| `recovery_action_plan.csv` | Job-level recovery levers such as resequencing, overtime, customer escalation, or monitor. |

## Deterministic Scoring Ideas

- Every operation appears exactly once.
- Job precedence constraints are satisfied.
- Machine overlap is absent.
- Downtime windows are respected.
- Metrics match the schedule.
- `bottleneck_machine` must match deterministic load/slack calculation.
- `recovery_action` must follow frozen policy mappings:
  - high service criticality and late after recovery: `customer_escalation`
  - bottleneck machine with feasible overtime window: `overtime`
  - local sequence conflict with no overtime need: `resequencing`
  - feasible and low risk: `monitor`
- Optional improvement target beats the disrupted baseline.

## Expected Skill Effect

Scheduling feasibility may be solved by algorithms without skill. Skill impact should be measured on bottleneck diagnosis, recovery lever choice, owner assignment, and service/cost tradeoff classification.
