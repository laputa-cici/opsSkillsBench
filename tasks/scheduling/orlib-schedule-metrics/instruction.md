# OR-Library Schedule Metrics

Compute schedule feasibility metrics, makespan, and total tardiness for the repaired schedule.

This is an atomic task split from `orlib-disruption-recovery-control`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/jobshop_instance.csv`
- `/app/data/baseline_schedule.csv`
- `/app/data/machine_downtime.csv`
- `/app/data/customer_priority.csv`

## Required Outputs

- `/app/output/schedule_metrics.json`

## Requirements

1. Write schedule_metrics.json.
2. Report zero violation counts when the generated schedule is feasible.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
