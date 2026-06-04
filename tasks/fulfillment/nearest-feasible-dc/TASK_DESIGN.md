# Nearest Feasible Distribution Center

This atomic task adds an order-allocation style fulfillment item beyond the original DataCo control-tower split.

## Purpose

Assign each order to the nearest warehouse that has enough available inventory, or mark it for review.

## Output

- `/app/output/warehouse_assignment.csv`

## Skill Surface

The task is designed to exercise fulfillment concepts from logistics and operations skills: feasible inventory, warehouse capacity, SLA risk, split-order tradeoffs, action codes, and reason-code discipline.
