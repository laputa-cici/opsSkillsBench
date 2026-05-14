# OR-Library Bottleneck Action Plan

Identify the bottleneck machine and map tardy jobs to recovery actions and owners.

This is an atomic task split from `orlib-disruption-recovery-control`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/jobshop_instance.csv`
- `/app/data/baseline_schedule.csv`
- `/app/data/machine_downtime.csv`
- `/app/data/customer_priority.csv`
- `/app/data/recovery_policy.json`

## Required Outputs

- `/app/output/bottleneck_report.json`
- `/app/output/recovery_action_plan.csv`

## Requirements

1. Write bottleneck_report.json and recovery_action_plan.csv.
2. Use the operations-control taxonomy from the parent recovery task.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
