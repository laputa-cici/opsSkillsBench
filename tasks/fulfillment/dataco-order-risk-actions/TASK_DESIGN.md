# DataCo Order Risk Actions

This atomic task belongs to the `fulfillment` problem domain.

Parent task: `dataco-control-tower-exception-review`

## Purpose

Classify order-level delivery risk and map each order to a control-tower action.

The task turns one previously nested verifier checkpoint into a standalone benchmark item, so benchmark reports count it as an individual task instead of a hidden sub-question inside a larger scenario.

## Checked Outputs

- `/app/output/control_tower_actions.csv`

## Skill Sensitivity

The task keeps the parent task's external-source data and skill candidates, while narrowing the required output to a single operational decision surface. This makes it easier to scale the benchmark to many independent items and to analyze which decision surfaces benefit from provided skills.
