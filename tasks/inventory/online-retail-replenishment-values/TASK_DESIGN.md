# Online Retail Replenishment Values

This atomic task belongs to the `inventory` problem domain.

Parent task: `online-retail-replenishment-review`

## Purpose

Compute average demand, reorder points, order quantities, priority bands, and post-order cover.

The task turns one previously nested verifier checkpoint into a standalone benchmark item, so benchmark reports count it as an individual task instead of a hidden sub-question inside a larger scenario.

## Checked Outputs

- `/app/output/replenishment_plan.csv`

## Skill Sensitivity

The task keeps the parent task's external-source data and skill candidates, while narrowing the required output to a single operational decision surface. This makes it easier to scale the benchmark to many independent items and to analyze which decision surfaces benefit from provided skills.
