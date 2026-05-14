# Online Retail Exception Register

Identify critical and high-priority replenishment exceptions from the replenishment rules.

This is an atomic task split from `online-retail-replenishment-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/daily_sku_demand.csv`
- `/app/data/current_inventory.csv`
- `/app/data/inventory_policy.csv`

## Required Outputs

- `/app/output/replenishment_exceptions.json`

## Requirements

1. Write replenishment_exceptions.json with exception_count and sorted exceptions.
2. Include trigger_rule labels exactly as specified.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
