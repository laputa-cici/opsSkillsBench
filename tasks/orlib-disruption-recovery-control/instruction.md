# OR-Library Disruption Recovery Control

You are repairing a disrupted job-shop schedule after a machine outage and preparing an operations recovery control plan.

Read the runtime input files:

- `/app/data/jobshop_instance.csv`
- `/app/data/baseline_schedule.csv`
- `/app/data/machine_downtime.csv`
- `/app/data/customer_priority.csv`
- `/app/data/recovery_policy.json`

Create:

- `/app/output/recovery_schedule.csv`
- `/app/output/schedule_metrics.json`
- `/app/output/bottleneck_report.json`
- `/app/output/recovery_action_plan.csv`

The schedule must preserve job operation precedence, avoid machine overlap, avoid downtime windows, and report deterministic metrics such as makespan and total tardiness. The recovery control outputs should also identify the bottleneck machine, constrained jobs, service/cost tradeoff, and recovery action choices such as resequencing, overtime, customer escalation, or monitor while keeping output values inside the allowed taxonomy in `recovery_policy.json`.

## Required Recovery Schedule

`recovery_schedule.csv` must include one row for every operation with these columns:

```text
job_id
operation_id
operation_index
machine
start
end
```

Rules:

1. Use the operation order from `baseline_schedule.csv` as the dispatch sequence, sorted by baseline `start`, then `operation_id`.
2. Schedule each operation at the earliest integer time that satisfies:
   - the previous operation of the same job is complete
   - the target machine is available
   - the operation does not overlap any machine downtime window
3. Keep the original machine and processing time from `jobshop_instance.csv`.

## Required Schedule Metrics

`schedule_metrics.json` must include:

```text
operation_count
makespan
total_tardiness
downtime_violations
machine_overlap_violations
precedence_violations
policy_compliance
```

Use `policy_compliance = true` only when all three violation counts are zero.

## Required Bottleneck Report

`bottleneck_report.json` must include:

```text
bottleneck_machine
load_plus_downtime
constrained_jobs
root_cause
decision_hierarchy
```

Compute bottleneck load as total processing time on the machine plus total downtime duration. Choose the highest load; break ties by machine name ascending.

Use a concise operations-control framing for `root_cause` and `decision_hierarchy` instead of a free-form narrative.

## Required Recovery Action Plan

`recovery_action_plan.csv` must contain one row per job sorted by `job_id`, with these columns:

```text
job_id
tardiness
service_criticality
recovery_action
owner_function
decision_hierarchy
```

Rules:

1. `tardiness = max(job_completion - due_date, 0)`.
2. If `tardiness > 0` and `service_criticality = high`, set `recovery_action = customer_escalation`.
3. Else if the job uses the bottleneck machine and `tardiness > 0`, set `recovery_action = overtime`.
4. Else if `tardiness > 0`, set `recovery_action = resequencing`.
5. Otherwise, set `recovery_action = monitor`.
6. `owner_function` and `decision_hierarchy` must stay within the allowed recovery taxonomy and should reflect an operations-control interpretation of the chosen action.
