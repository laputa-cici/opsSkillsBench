# Capacity Aware Allocation

Assign orders to warehouses that satisfy inventory, remaining pick capacity, and load guardrail constraints.

Read the runtime input files:

- `/app/data/orders.csv`
- `/app/data/warehouse_inventory.csv`
- `/app/data/warehouse_capacity.csv`
- `/app/data/transit_times.csv`
- `/app/data/fulfillment_policy.json`

Create:

- `/app/output/capacity_adjusted_assignment.csv`

Required columns:

```text
order_id
assigned_warehouse
action_code
reason_code
capacity_after_pick
```

Keep all action and reason codes inside `fulfillment_policy.json`. Sort output rows by `order_id` when writing CSV files. Do not run the bundled oracle solution.
