# Task Design

## Status

This task is kept as a runner smoke test, not as a paper-facing skill-sensitive task.

The first pilot showed that both `provided_skills` and `no_skill` agents solved the main work by creating a Python script. That means the task mostly evaluates CSV processing and deterministic arithmetic, not whether a management-operations skill improves agent performance.

## Goal

Evaluate whether agents can turn transaction-derived demand and policy tables into a clean replenishment review.

## Inputs

| File | Description |
| --- | --- |
| `daily_sku_demand.csv` | SKU-level demand by date derived from Online Retail II invoice rows. |
| `current_inventory.csv` | Current on-hand inventory for the selected SKU slice. |
| `inventory_policy.csv` | Lead time, safety stock, order pack size, minimum order quantity, and service-level band rules. |

## Outputs

| File | Description |
| --- | --- |
| `replenishment_plan.csv` | Reorder point, recommended order quantity, priority band, expected cover after order. |
| `replenishment_exceptions.json` | Top stockout-risk exceptions and reasons. |

## Deterministic Scoring

- Output files exist and schemas match.
- SKU order is preserved.
- Reorder quantities round correctly to pack-size and minimum-order rules.
- Priority bands match days-of-cover thresholds.
- Exception list contains exactly the SKUs triggered by frozen rules.

## Redesign Direction

Do not extend this task by merely adding more formulas. The replacement should become `retail-sop-replenishment-control` and require outputs that are difficult to infer from data tables alone:

| Output | Skill-sensitive requirement |
| --- | --- |
| `inventory_control_plan.csv` | ABC policy, service/cash tradeoff, action code, and workflow phase. |
| `supply_chain_risk_register.json` | Risk type, mitigation code, hierarchy priority, and SOP reference. |
| `framework_trace.json` | Explicit mapping to allowed `supply-chain-manager` concepts such as supply-chain hierarchy, inventory strategy, risk taxonomy, and Plan-Source-Make-Deliver-Return workflow. |

The current task can continue to verify runner/oracle/test plumbing, but should not be used as the main paper evidence for skill benefit.
