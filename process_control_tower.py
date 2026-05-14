#!/usr/bin/env python3
"""
DataCo Control-Tower Exception Review
Processes order snapshot, carrier lane scorecard, and customer commitments
to produce control tower actions, lane risk register, and scorecard summary.
"""

import csv
import json
from pathlib import Path

# Paths
DATA_DIR = Path("/Users/cici/code/opsSkillsBench-main/.local_runtime/dataco-control-tower-exception-review/app/data")
OUTPUT_DIR = Path("/Users/cici/code/opsSkillsBench-main/.local_runtime/dataco-control-tower-exception-review/app/output")

OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

# Load control policy
with open(DATA_DIR / "control_policy.json") as f:
    policy = json.load(f)

# Load customer commitments (customer segment -> target_otif, escalation_value)
customer_segments = {}
with open(DATA_DIR / "customer_commitments.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        customer_segments[row["customer_segment"]] = {
            "target_otif": float(row["target_otif"]),
            "escalation_value": float(row["escalation_value"])
        }

# Load carrier lane scorecard (lane -> otif_rate, avg_delay_days)
carrier_lanes = {}
with open(DATA_DIR / "carrier_lane_scorecard.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        carrier_lanes[row["lane"]] = {
            "otif_rate": float(row["otif_rate"]),
            "avg_delay_days": float(row["avg_delay_days"]),
            "shipment_count": int(row["shipment_count"]),
            "cost_per_order": float(row["cost_per_order"])
        }

# Load order snapshot
orders = []
with open(DATA_DIR / "order_snapshot.csv") as f:
    reader = csv.DictReader(f)
    for row in reader:
        orders.append({
            "order_id": row["order_id"],
            "lane": row["lane"],
            "shipping_mode": row["shipping_mode"],
            "customer_segment": row["customer_segment"],
            "category": row["category"],
            "order_value": float(row["order_value"]),
            "promised_days": int(row["promised_days"]),
            "actual_days": int(row["actual_days"])
        })

# Process orders
control_tower_actions = []

for order in orders:
    order_id = order["order_id"]
    lane = order["lane"]
    shipping_mode = order["shipping_mode"]
    customer_segment = order["customer_segment"]
    order_value = order["order_value"]
    promised_days = order["promised_days"]
    actual_days = order["actual_days"]

    # Calculate delay_days
    delay_days = max(actual_days - promised_days, 0)

    # Get lane metrics
    lane_data = carrier_lanes.get(lane, {})
    otif_rate = lane_data.get("otif_rate", 1.0)

    # Get customer segment thresholds
    seg_data = customer_segments.get(customer_segment, {})
    target_otif = seg_data.get("target_otif", 0.5)
    escalation_value = seg_data.get("escalation_value", 500)

    # Determine risk band
    # Critical: delay_days > 0 AND (order_value >= escalation_value OR otif_rate < target_otif - 0.10)
    # High: not critical AND (delay_days > 0 OR otif_rate < target_otif)
    # Monitor: otherwise

    is_delayed = delay_days > 0
    is_high_value = order_value >= escalation_value
    is_lane_critical = otif_rate < (target_otif - 0.10)
    is_lane_high = otif_rate < target_otif

    if is_delayed and (is_high_value or is_lane_critical):
        risk_band = "critical"
    elif is_delayed or is_lane_high:
        risk_band = "high"
    else:
        risk_band = "monitor"

    # Determine action_code
    if risk_band == "critical":
        if shipping_mode in ["Standard Class", "Second Class"]:
            action_code = "mode_change"
        else:
            action_code = "customer_notify"
    elif risk_band == "high":
        if is_lane_high:
            action_code = "carrier_review"
        else:
            action_code = "customer_notify"
    else:
        action_code = "monitor"

    # Determine owner_function from policy
    owner_function = policy["owner_functions"].get(action_code, "control_tower")

    # Determine decision_hierarchy and workflow_phase
    # For delivery/control-tower framing, use "service" for critical/high, "resilience" for monitor
    if risk_band == "critical":
        decision_hierarchy = "service"
        workflow_phase = "deliver"
    elif risk_band == "high":
        decision_hierarchy = "service"
        workflow_phase = "deliver"
    else:
        decision_hierarchy = "resilience"
        workflow_phase = "deliver"

    # Determine reason_code
    if risk_band == "critical":
        if is_lane_critical:
            reason_code = "lane_performance_degradation"
        else:
            reason_code = "high_value_order_delay"
    elif risk_band == "high":
        if is_lane_high:
            reason_code = "lane_below_target"
        else:
            reason_code = "order_delay"
    else:
        reason_code = "on_track"

    # Calculate value_at_risk
    if risk_band in ["critical", "high"]:
        value_at_risk = order_value
    else:
        value_at_risk = 0

    control_tower_actions.append({
        "order_id": order_id,
        "risk_band": risk_band,
        "action_code": action_code,
        "owner_function": owner_function,
        "decision_hierarchy": decision_hierarchy,
        "workflow_phase": workflow_phase,
        "reason_code": reason_code,
        "delay_days": delay_days,
        "value_at_risk": value_at_risk
    })

# Sort by order_id
control_tower_actions.sort(key=lambda x: x["order_id"])

# Write control_tower_actions.csv
with open(OUTPUT_DIR / "control_tower_actions.csv", "w", newline="") as f:
    fieldnames = ["order_id", "risk_band", "action_code", "owner_function",
                  "decision_hierarchy", "workflow_phase", "reason_code",
                  "delay_days", "value_at_risk"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(control_tower_actions)

print(f"Created control_tower_actions.csv with {len(control_tower_actions)} rows")

# Build lane_risk_register.json
# Include one risk object for each lane where otif_rate < 0.90 or avg_delay_days >= 2.0
risks = []
for lane, lane_data in carrier_lanes.items():
    otif_rate = lane_data["otif_rate"]
    avg_delay_days = lane_data["avg_delay_days"]

    if otif_rate < 0.90 or avg_delay_days >= 2.0:
        # risk_type = carrier_lane_failure
        risk_type = "carrier_lane_failure"
        # mitigation_code = carrier_improvement_plan
        mitigation_code = "carrier_improvement_plan"
        # escalation_level = 1 when otif_rate < 0.80, otherwise 2
        if otif_rate < 0.80:
            escalation_level = 1
        else:
            escalation_level = 2

        risks.append({
            "lane": lane,
            "risk_type": risk_type,
            "mitigation_code": mitigation_code,
            "escalation_level": escalation_level,
            "decision_hierarchy": "service",
            "workflow_phase": "deliver"
        })

# Sort by escalation_level, then lane
risks.sort(key=lambda x: (x["escalation_level"], x["lane"]))

lane_risk_register = {
    "lane_count": len(risks),
    "risks": risks
}

with open(OUTPUT_DIR / "lane_risk_register.json", "w") as f:
    json.dump(lane_risk_register, f, indent=2)

print(f"Created lane_risk_register.json with {len(risks)} risks")

# Build scorecard_summary.json
orders_total = len(orders)
critical_count = sum(1 for a in control_tower_actions if a["risk_band"] == "critical")
high_count = sum(1 for a in control_tower_actions if a["risk_band"] == "high")
monitor_count = sum(1 for a in control_tower_actions if a["risk_band"] == "monitor")
value_at_risk_total = sum(a["value_at_risk"] for a in control_tower_actions)
lane_count = len(carrier_lanes)

# Find highest_risk_lane: lowest otif_rate, then highest avg_delay_days, then lane name ascending
sorted_lanes = sorted(
    carrier_lanes.items(),
    key=lambda x: (x[1]["otif_rate"], -x[1]["avg_delay_days"], x[0])
)
highest_risk_lane = sorted_lanes[0][0] if sorted_lanes else None

# Count actions
action_counts = {}
for action in control_tower_actions:
    action_code = action["action_code"]
    action_counts[action_code] = action_counts.get(action_code, 0) + 1

scorecard_summary = {
    "orders_total": orders_total,
    "critical_count": critical_count,
    "high_count": high_count,
    "monitor_count": monitor_count,
    "value_at_risk_total": value_at_risk_total,
    "lane_count": lane_count,
    "highest_risk_lane": highest_risk_lane,
    "action_counts": action_counts
}

with open(OUTPUT_DIR / "scorecard_summary.json", "w") as f:
    json.dump(scorecard_summary, f, indent=2)

print(f"Created scorecard_summary.json")
print(f"  Orders total: {orders_total}")
print(f"  Critical: {critical_count}, High: {high_count}, Monitor: {monitor_count}")
print(f"  Value at risk total: {value_at_risk_total}")
print(f"  Highest risk lane: {highest_risk_lane}")
