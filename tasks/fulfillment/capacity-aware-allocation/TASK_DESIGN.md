# Capacity Aware Allocation

This atomic task adds an order-allocation style fulfillment item beyond the original DataCo control-tower split.

## Purpose

Assign orders to warehouses that satisfy inventory, remaining pick capacity, and load guardrail constraints.

## Output

- `/app/output/capacity_adjusted_assignment.csv`

## Skill Surface

The task is designed to exercise fulfillment concepts from logistics and operations skills: feasible inventory, warehouse capacity, SLA risk, split-order tradeoffs, action codes, and reason-code discipline.
