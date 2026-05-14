# DataCo Control-Tower Exception Review

You are reviewing a supply-chain control-tower snapshot for delivery and fulfillment risk.

Read the runtime input files:

- `/app/data/order_snapshot.csv`
- `/app/data/carrier_lane_scorecard.csv`
- `/app/data/customer_commitments.csv`
- `/app/data/control_policy.json`

Create:

- `/app/output/control_tower_actions.csv`
- `/app/output/lane_risk_register.json`
- `/app/output/scorecard_summary.json`

The CSV should classify each order into a risk band and recommend a deterministic control-tower action. It should include framework-driven fields such as `decision_hierarchy`, `workflow_phase`, `owner_function`, and `reason_code`.

The risk register should classify lane-level risks and mitigations using the allowed taxonomy in `control_policy.json`.

The scorecard summary should compute OTIF-style lane reliability, value at risk, and action counts.

## Required CSV Columns

`control_tower_actions.csv` must contain one row per order, sorted by `order_id`, with these columns:

```text
order_id
risk_band
action_code
owner_function
decision_hierarchy
workflow_phase
reason_code
delay_days
value_at_risk
```

Rules:

1. `delay_days = max(actual_days - promised_days, 0)`.
2. An order is `critical` if `delay_days > 0` and either `order_value >= escalation_value` for its customer segment or the lane `otif_rate < target_otif - 0.10`.
3. An order is `high` if it is not `critical` and either `delay_days > 0` or the lane `otif_rate < target_otif`.
4. Otherwise, the order is `monitor`.
5. For `critical` orders with `shipping_mode` in `Standard Class` or `Second Class`, set `action_code = mode_change`.
6. For other `critical` orders, set `action_code = customer_notify`.
7. For `high` orders where lane `otif_rate < target_otif`, set `action_code = carrier_review`.
8. For other `high` orders, set `action_code = customer_notify`.
9. For `monitor` orders, set `action_code = monitor`.
10. `owner_function`, `decision_hierarchy`, `workflow_phase`, and `reason_code` must remain within the allowed values or mappings in `control_policy.json`.
11. For order-level actions, use a delivery/control-tower workflow framing rather than plan-only or sourcing-only framing.
12. `value_at_risk = order_value` for `critical` or `high` orders, otherwise `0`.

## Required Risk Register

`lane_risk_register.json` must contain:

```json
{
  "lane_count": 0,
  "risks": []
}
```

Include one risk object for each lane where `otif_rate < 0.90` or `avg_delay_days >= 2.0`. Sort by `escalation_level`, then `lane`. Each risk object must include:

```text
lane
risk_type
mitigation_code
escalation_level
decision_hierarchy
workflow_phase
```

Rules:

1. `risk_type = carrier_lane_failure`.
2. `mitigation_code = carrier_improvement_plan`.
3. `escalation_level = 1` when `otif_rate < 0.80`, otherwise `2`.
4. `decision_hierarchy` and `workflow_phase` must remain inside the allowed taxonomy in `control_policy.json`.

## Required Summary

`scorecard_summary.json` must contain:

```text
orders_total
critical_count
high_count
monitor_count
value_at_risk_total
lane_count
highest_risk_lane
action_counts
```

`highest_risk_lane` is the lane with lowest `otif_rate`, then highest `avg_delay_days`, then lane name ascending.
