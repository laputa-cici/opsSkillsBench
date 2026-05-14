# Online Retail Replenishment Values

Compute average demand, reorder points, order quantities, priority bands, and post-order cover.

This is an atomic task split from `online-retail-replenishment-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/daily_sku_demand.csv`
- `/app/data/current_inventory.csv`
- `/app/data/inventory_policy.csv`

## Required Outputs

- `/app/output/replenishment_plan.csv`

## Requirements

1. Compute the full replenishment_plan.csv values.
2. Round demand and cover values to one decimal place.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
