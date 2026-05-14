# Online Retail Replenishment Schema

This atomic task belongs to the `inventory` problem domain.

Parent task: `online-retail-replenishment-review`

## Purpose

Produce the replenishment plan file with the required SKU ordering and schema.

The task turns one previously nested verifier checkpoint into a standalone benchmark item, so benchmark reports count it as an individual task instead of a hidden sub-question inside a larger scenario.

## Checked Outputs

- `/app/output/replenishment_plan.csv`

## Skill Sensitivity

The task keeps the parent task's external-source data and skill candidates, while narrowing the required output to a single operational decision surface. This makes it easier to scale the benchmark to many independent items and to analyze which decision surfaces benefit from provided skills.
