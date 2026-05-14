# DataCo Lane Risk Register

Build a lane-level risk register from carrier lane reliability and delay metrics.

This is an atomic task split from `dataco-control-tower-exception-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/carrier_lane_scorecard.csv`
- `/app/data/control_policy.json`

## Required Outputs

- `/app/output/lane_risk_register.json`

## Requirements

1. Write lane_risk_register.json with lane_count and sorted risks.
2. Use the carrier_lane_failure taxonomy and escalation rules from the parent task.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
