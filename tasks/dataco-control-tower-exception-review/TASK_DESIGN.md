# Task Design: DataCo Control-Tower Exception Review

## Goal

Evaluate whether agents can convert a DataCo-derived supply-chain snapshot into a deterministic control-tower decision package.

This task should be the next paper-facing implementation target because it is more naturally skill-sensitive than the current retail replenishment smoke test. It should require logistics, supply-chain, and operations frameworks, not only delivery-delay arithmetic.

## Public Source Basis

| Source type | Planned source |
| --- | --- |
| Dataset | DataCo SMART Supply Chain |
| Primary skill | `supply-chain-manager` |
| Additional skill candidates | `logistics-manager`, `operations-manager` |

## Why This Should Be Skill-Sensitive

The output should require the agent to apply framework concepts from public skills:

| Skill concept | Required use in task |
| --- | --- |
| Service-cost-cash-resilience hierarchy | Decide whether an exception should prioritize service recovery, cost control, or resilience. |
| Logistics and fulfillment layer | Distinguish carrier/lane issues from order-management issues. |
| Supplier/carrier scorecard | Compute and interpret OTIF-style lane reliability and escalation triggers. |
| Risk documentation | Classify risks such as service failure, demand surge, supplier/carrier failure, or disruption exposure. |
| SOP/workflow phase | Map each exception to `plan`, `source`, `make`, `deliver`, or `return`. |

## Planned Inputs

| File | Description |
| --- | --- |
| `order_snapshot.csv` | DataCo-derived order rows with promised/actual delivery signals, shipping mode, market, category, customer segment, and order value. |
| `carrier_lane_scorecard.csv` | Derived lane-level delay rate, cost, reliability, and shipment volume aggregates. |
| `customer_commitments.csv` | Service target and escalation rules by customer segment. |
| `control_policy.json` | Frozen thresholds, allowed enum values, and action mappings. |

## Planned Outputs

| File | Description |
| --- | --- |
| `control_tower_actions.csv` | Order-level action file with `risk_band`, `action_code`, `owner_function`, `decision_hierarchy`, `workflow_phase`, and `reason_code`. |
| `lane_risk_register.json` | Lane-level risk register with `risk_type`, `mitigation_code`, `escalation_level`, `decision_hierarchy`, and `workflow_phase`. |
| `scorecard_summary.json` | OTIF-style reliability metrics, value at risk, action counts, and top lanes. |

## Deterministic Scoring Ideas

- Risk bands match frozen threshold rules.
- `action_code` must distinguish `expedite`, `carrier_review`, `customer_notify`, `mode_change`, and `monitor`.
- `decision_hierarchy` must prioritize service for premium/high-value delayed orders and cost for low-value non-critical orders.
- `workflow_phase` must map delivery exceptions to `deliver` and demand/customer commitment exceptions to `plan`.
- `risk_type` must match deterministic combinations of lane delay rate, value at risk, customer segment, and shipping mode.
- `scorecard_summary` must compute lane OTIF, value at risk, and action counts exactly.

## Expected Skill Effect

`provided_skills` should improve framework taxonomy and action consistency. `no_skill` may still compute delay statistics, but should be less reliable on owner assignment, hierarchy priority, risk classification, and mitigation mapping.
