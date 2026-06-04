# SLA Risk Estimator

Estimate fulfillment SLA risk using assigned warehouse, handling time, transit time, promised hours, and customer segment.

Read the runtime input files:

- `/app/data/orders.csv`
- `/app/data/warehouse_inventory.csv`
- `/app/data/warehouse_capacity.csv`
- `/app/data/transit_times.csv`
- `/app/data/fulfillment_policy.json`

Create:

- `/app/output/sla_risk_register.json`

Use the JSON structure described by the task policy and verifier.

Keep all action and reason codes inside `fulfillment_policy.json`. Sort output rows by `order_id` when writing CSV files. Do not run the bundled oracle solution.
