# Split Order Decision

This atomic task adds an order-allocation style fulfillment item beyond the original DataCo control-tower split.

## Purpose

Decide whether orders without a single feasible warehouse can be split across at most two warehouses.

## Output

- `/app/output/split_order_plan.csv`

## Skill Surface

The task is designed to exercise fulfillment concepts from logistics and operations skills: feasible inventory, warehouse capacity, SLA risk, split-order tradeoffs, action codes, and reason-code discipline.
