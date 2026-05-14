#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import csv
import json
from pathlib import Path

APP = Path("/app")
DATA = APP / "data"
OUT = APP / "output"
OUT.mkdir(parents=True, exist_ok=True)

with (DATA / "control_policy.json").open(encoding="utf-8") as f:
    policy = json.load(f)

with (DATA / "carrier_lane_scorecard.csv").open(newline="", encoding="utf-8") as f:
    lanes = {row["lane"]: row for row in csv.DictReader(f)}
for row in lanes.values():
    row["otif_rate"] = float(row["otif_rate"])
    row["avg_delay_days"] = float(row["avg_delay_days"])
    row["cost_per_order"] = float(row["cost_per_order"])

with (DATA / "customer_commitments.csv").open(newline="", encoding="utf-8") as f:
    commitments = {row["customer_segment"]: row for row in csv.DictReader(f)}
for row in commitments.values():
    row["target_otif"] = float(row["target_otif"])
    row["escalation_value"] = float(row["escalation_value"])

actions = []
with (DATA / "order_snapshot.csv").open(newline="", encoding="utf-8") as f:
    for row in csv.DictReader(f):
        lane = lanes[row["lane"]]
        commitment = commitments[row["customer_segment"]]
        order_value = float(row["order_value"])
        delay_days = max(int(row["actual_days"]) - int(row["promised_days"]), 0)
        if delay_days > 0 and (
            order_value >= commitment["escalation_value"]
            or lane["otif_rate"] < commitment["target_otif"] - 0.10
        ):
            risk_band = "critical"
        elif delay_days > 0 or lane["otif_rate"] < commitment["target_otif"]:
            risk_band = "high"
        else:
            risk_band = "monitor"

        if risk_band == "critical" and row["shipping_mode"] in {"Standard Class", "Second Class"}:
            action_code = "mode_change"
        elif risk_band == "critical":
            action_code = "customer_notify"
        elif risk_band == "high" and lane["otif_rate"] < commitment["target_otif"]:
            action_code = "carrier_review"
        elif risk_band == "high":
            action_code = "customer_notify"
        else:
            action_code = "monitor"

        reason_code = "stable"
        if lane["otif_rate"] < commitment["target_otif"] - 0.10:
            reason_code = "carrier_lane_failure"
        elif delay_days > 0:
            reason_code = "service_failure"

        decision_hierarchy = "service" if risk_band in {"critical", "high"} else "cost" if lane["cost_per_order"] >= 25 else "service"
        actions.append(
            {
                "order_id": row["order_id"],
                "risk_band": risk_band,
                "action_code": action_code,
                "owner_function": policy["owner_functions"][action_code],
                "decision_hierarchy": decision_hierarchy,
                "workflow_phase": "deliver",
                "reason_code": reason_code,
                "delay_days": delay_days,
                "value_at_risk": int(order_value) if risk_band in {"critical", "high"} else 0,
            }
        )

actions.sort(key=lambda row: row["order_id"])
with (OUT / "control_tower_actions.csv").open("w", newline="", encoding="utf-8") as f:
    fieldnames = [
        "order_id",
        "risk_band",
        "action_code",
        "owner_function",
        "decision_hierarchy",
        "workflow_phase",
        "reason_code",
        "delay_days",
        "value_at_risk",
    ]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(actions)

risks = []
for lane, row in lanes.items():
    if row["otif_rate"] < 0.90 or row["avg_delay_days"] >= 2.0:
        risks.append(
            {
                "lane": lane,
                "risk_type": "carrier_lane_failure",
                "mitigation_code": "carrier_improvement_plan",
                "escalation_level": 1 if row["otif_rate"] < 0.80 else 2,
                "decision_hierarchy": "resilience",
                "workflow_phase": "deliver",
            }
        )
risks.sort(key=lambda row: (row["escalation_level"], row["lane"]))
with (OUT / "lane_risk_register.json").open("w", encoding="utf-8") as f:
    json.dump({"lane_count": len(risks), "risks": risks}, f, indent=2)

highest = sorted(lanes.values(), key=lambda row: (row["otif_rate"], -row["avg_delay_days"], row["lane"]))[0]["lane"]
action_counts = {}
for row in actions:
    action_counts[row["action_code"]] = action_counts.get(row["action_code"], 0) + 1
summary = {
    "orders_total": len(actions),
    "critical_count": sum(1 for row in actions if row["risk_band"] == "critical"),
    "high_count": sum(1 for row in actions if row["risk_band"] == "high"),
    "monitor_count": sum(1 for row in actions if row["risk_band"] == "monitor"),
    "value_at_risk_total": sum(row["value_at_risk"] for row in actions),
    "lane_count": len(lanes),
    "highest_risk_lane": highest,
    "action_counts": dict(sorted(action_counts.items())),
}
with (OUT / "scorecard_summary.json").open("w", encoding="utf-8") as f:
    json.dump(summary, f, indent=2)
PY
