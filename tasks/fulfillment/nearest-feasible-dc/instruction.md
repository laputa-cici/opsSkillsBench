# Nearest Feasible Distribution Center

Assign each order to the nearest warehouse that has enough available inventory, or mark it for review.

Read the runtime input files:

- `/app/data/orders.csv`
- `/app/data/warehouse_inventory.csv`
- `/app/data/warehouse_capacity.csv`
- `/app/data/transit_times.csv`
- `/app/data/fulfillment_policy.json`

Create:

- `/app/output/warehouse_assignment.csv`

Required columns:

```text
order_id
assigned_warehouse
action_code
reason_code
transit_hours
```

Keep all action and reason codes inside `fulfillment_policy.json`. Sort output rows by `order_id` when writing CSV files. Do not run the bundled oracle solution.
