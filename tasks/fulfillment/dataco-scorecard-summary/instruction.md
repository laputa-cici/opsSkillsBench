# DataCo Scorecard Summary

Summarize control-tower risk counts, value at risk, lane count, and action distribution.

This is an atomic task split from `dataco-control-tower-exception-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/order_snapshot.csv`
- `/app/data/carrier_lane_scorecard.csv`
- `/app/data/customer_commitments.csv`
- `/app/data/control_policy.json`

## Required Outputs

- `/app/output/scorecard_summary.json`

## Requirements

1. Write scorecard_summary.json.
2. Compute risk-band counts, total value at risk, highest risk lane, and action_counts.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
