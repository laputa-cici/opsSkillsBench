# OR-Library Recovery Schedule

This atomic task belongs to the `scheduling` problem domain.

Parent task: `orlib-disruption-recovery-control`

## Purpose

Repair a disrupted job-shop schedule while preserving precedence and avoiding downtime windows.

The task turns one previously nested verifier checkpoint into a standalone benchmark item, so benchmark reports count it as an individual task instead of a hidden sub-question inside a larger scenario.

## Checked Outputs

- `/app/output/recovery_schedule.csv`

## Skill Sensitivity

The task keeps the parent task's external-source data and skill candidates, while narrowing the required output to a single operational decision surface. This makes it easier to scale the benchmark to many independent items and to analyze which decision surfaces benefit from provided skills.
