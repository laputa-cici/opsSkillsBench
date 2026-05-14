# DataCo Order Risk Actions

Classify order-level delivery risk and map each order to a control-tower action.

This is an atomic task split from `dataco-control-tower-exception-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/order_snapshot.csv`
- `/app/data/carrier_lane_scorecard.csv`
- `/app/data/customer_commitments.csv`
- `/app/data/control_policy.json`

## Required Outputs

- `/app/output/control_tower_actions.csv`

## Requirements

1. Write control_tower_actions.csv sorted by order_id.
2. Include risk_band, action_code, owner_function, decision_hierarchy, workflow_phase, reason_code, delay_days, and value_at_risk.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
