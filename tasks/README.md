# Task Queue

The benchmark now treats each directory with a `task.toml` file as an independently counted task. This supports both the original scenario-level tasks and the newer scalable layout:

```text
tasks/<problem-domain>/<task-id>/
```

Status values:

| Status | Meaning |
| --- | --- |
| `design_external_source` | Task is designed around external skills and datasets, but data slices/tests are not committed yet. |
| `runnable_prototype_external_schema` | Task has data, oracle, and tests, but the committed slice is a compact prototype matching an external-source schema rather than a verified raw-data derivation. |
| `runnable_external_source` | Task has data, oracle, tests, and provenance. |
| `runnable_smoke_not_skill_sensitive` | Task is runnable and useful for runner smoke tests, but pilot runs showed it is not suitable as a paper-facing skill benchmark. |
| `frozen` | Task is ready for paper experiments. |

## Legacy Scenario Tasks

These remain available for continuity with prior experiments.

| Task | Status | Dataset | Skill candidates |
| --- | --- | --- | --- |
| `online-retail-replenishment-review` | `runnable_smoke_not_skill_sensitive` | UCI Online Retail II | `supply-chain-manager` |
| `dataco-control-tower-exception-review` | `runnable_external_source` | DataCo SMART Supply Chain | `supply-chain-manager`, `logistics-manager`, `operations-manager` |
| `portland-sourcing-concentration-review` | `runnable_external_source` | Open Contracting / City of Portland | `supply-chain-manager`, `operations-manager`, `procurement-review` |
| `orlib-disruption-recovery-control` | `runnable_external_source` | OR-Library Job Shop Scheduling | `capacity-planning`, `operations-manager`, `supply-chain-manager` |

## Atomic Task Domains

These tasks are split from scenario-level verifier checkpoints and count as standalone benchmark items.

| Domain | Tasks |
| --- | ---: |
| `inventory` | 3 |
| `fulfillment` | 3 |
| `procurement` | 3 |
| `scheduling` | 3 |

## Current Atomic Queue

| Task | Parent | Primary output |
| --- | --- | --- |
| `inventory/online-retail-replenishment-schema` | `online-retail-replenishment-review` | `replenishment_plan.csv` schema and ordering |
| `inventory/online-retail-replenishment-values` | `online-retail-replenishment-review` | `replenishment_plan.csv` calculations |
| `inventory/online-retail-exception-register` | `online-retail-replenishment-review` | `replenishment_exceptions.json` |
| `fulfillment/dataco-order-risk-actions` | `dataco-control-tower-exception-review` | `control_tower_actions.csv` |
| `fulfillment/dataco-lane-risk-register` | `dataco-control-tower-exception-review` | `lane_risk_register.json` |
| `fulfillment/dataco-scorecard-summary` | `dataco-control-tower-exception-review` | `scorecard_summary.json` |
| `procurement/portland-kraljic-category-matrix` | `portland-sourcing-concentration-review` | `kraljic_category_matrix.csv` |
| `procurement/portland-supplier-action-plan` | `portland-sourcing-concentration-review` | `supplier_action_plan.csv` |
| `procurement/portland-procurement-risk-register` | `portland-sourcing-concentration-review` | `procurement_risk_register.json` |
| `scheduling/orlib-recovery-schedule` | `orlib-disruption-recovery-control` | `recovery_schedule.csv` |
| `scheduling/orlib-schedule-metrics` | `orlib-disruption-recovery-control` | `schedule_metrics.json` |
| `scheduling/orlib-bottleneck-action-plan` | `orlib-disruption-recovery-control` | `bottleneck_report.json`, `recovery_action_plan.csv` |
