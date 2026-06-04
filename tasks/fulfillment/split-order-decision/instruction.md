# Split Order Decision

Decide whether orders without a single feasible warehouse can be split across at most two warehouses.

Read the runtime input files:

- `/app/data/orders.csv`
- `/app/data/warehouse_inventory.csv`
- `/app/data/warehouse_capacity.csv`
- `/app/data/transit_times.csv`
- `/app/data/fulfillment_policy.json`

Create:

- `/app/output/split_order_plan.csv`

Required columns:

```text
order_id
action_code
warehouse_split
shipment_count
total_split_cost
reason_code
```

Keep all action and reason codes inside `fulfillment_policy.json`. Sort output rows by `order_id` when writing CSV files. Do not run the bundled oracle solution.
