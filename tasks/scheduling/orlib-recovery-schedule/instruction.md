# OR-Library Recovery Schedule

Repair a disrupted job-shop schedule while preserving precedence and avoiding downtime windows.

This is an atomic task split from `orlib-disruption-recovery-control`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/jobshop_instance.csv`
- `/app/data/baseline_schedule.csv`
- `/app/data/machine_downtime.csv`

## Required Outputs

- `/app/output/recovery_schedule.csv`

## Requirements

1. Write recovery_schedule.csv with one row per operation.
2. Use baseline start and operation_id ordering as the dispatch sequence.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
