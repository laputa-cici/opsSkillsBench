# Online Retail Replenishment Schema

Produce the replenishment plan file with the required SKU ordering and schema.

This is an atomic task split from `online-retail-replenishment-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/daily_sku_demand.csv`
- `/app/data/current_inventory.csv`
- `/app/data/inventory_policy.csv`

## Required Outputs

- `/app/output/replenishment_plan.csv`

## Requirements

1. Write one row per SKU in inventory_policy.csv order.
2. Use the exact replenishment_plan.csv columns from the parent task.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
