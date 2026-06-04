#!/usr/bin/env bash
set -euo pipefail
python3 - <<'PY'
import csv
import json
from pathlib import Path


APP = Path("/app")
DATA = APP / "data"
OUT = APP / "output"
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def write_csv(name, fieldnames, rows):
    with (OUT / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def inventory_by_sku():
    result = {}
    for row in read_csv("warehouse_inventory.csv"):
        result[(row["warehouse_id"], row["sku"])] = int(row["on_hand"]) - int(row["reserved"]) - int(row["damaged"])
    return result


def capacities():
    return {
        row["warehouse_id"]: {
            "pick_capacity_remaining": int(row["pick_capacity_remaining"]),
            "load_index": float(row["load_index"]),
        }
        for row in read_csv("warehouse_capacity.csv")
    }


def transit_lookup():
    return {
        (row["warehouse_id"], row["zone"]): {
            "transit_hours": int(row["transit_hours"]),
            "cost_per_shipment": int(row["cost_per_shipment"]),
        }
        for row in read_csv("transit_times.csv")
    }


policy = json.loads((DATA / "fulfillment_policy.json").read_text(encoding="utf-8"))
orders = read_csv("orders.csv")
inventory = inventory_by_sku()
caps = capacities()
transit = transit_lookup()

nearest_rows = []
for order in orders:
    qty = int(order["qty"])
    candidates = []
    for warehouse_id in sorted(caps):
        available = inventory.get((warehouse_id, order["sku"]), 0)
        if available >= qty:
            lane = transit[(warehouse_id, order["ship_to_zone"])]
            candidates.append((lane["transit_hours"], caps[warehouse_id]["load_index"], warehouse_id, lane))
    if candidates:
        _, _, warehouse_id, lane = sorted(candidates)[0]
        nearest_rows.append({
            "order_id": order["order_id"],
            "assigned_warehouse": warehouse_id,
            "action_code": "ALLOCATE",
            "reason_code": "NEAREST_FEASIBLE_DC",
            "transit_hours": str(lane["transit_hours"]),
        })
    else:
        nearest_rows.append({
            "order_id": order["order_id"],
            "assigned_warehouse": "",
            "action_code": "REVIEW",
            "reason_code": "NO_FEASIBLE_INVENTORY",
            "transit_hours": "",
        })
write_csv("warehouse_assignment.csv", ["order_id", "assigned_warehouse", "action_code", "reason_code", "transit_hours"], nearest_rows)

capacity_rows = []
for order in orders:
    qty = int(order["qty"])
    candidates = []
    for warehouse_id in sorted(caps):
        available = inventory.get((warehouse_id, order["sku"]), 0)
        cap = caps[warehouse_id]
        if available >= qty and cap["pick_capacity_remaining"] >= qty and cap["load_index"] <= policy["capacity_guardrail_load_index"]:
            lane = transit[(warehouse_id, order["ship_to_zone"])]
            candidates.append((lane["transit_hours"], cap["load_index"], warehouse_id, lane, cap))
    if not candidates:
        capacity_rows.append({
            "order_id": order["order_id"],
            "assigned_warehouse": "",
            "action_code": "REVIEW",
            "reason_code": "NO_FEASIBLE_INVENTORY",
            "capacity_after_pick": "",
        })
        continue
    _, _, warehouse_id, lane, cap = sorted(candidates)[0]
    buffer = int(order["promised_hours"]) - lane["transit_hours"] - policy["standard_handling_hours"]
    action = "EXPEDITE" if buffer < policy["sla_high_buffer_hours"] else "ALLOCATE"
    capacity_rows.append({
        "order_id": order["order_id"],
        "assigned_warehouse": warehouse_id,
        "action_code": action,
        "reason_code": "SLA_RISK" if action == "EXPEDITE" else "CAPACITY_BALANCED_DC",
        "capacity_after_pick": str(cap["pick_capacity_remaining"] - qty),
    })
write_csv("capacity_adjusted_assignment.csv", ["order_id", "assigned_warehouse", "action_code", "reason_code", "capacity_after_pick"], capacity_rows)

assigned = {row["order_id"]: row for row in capacity_rows}
orders_by_id = {row["order_id"]: row for row in orders}
severity = {"critical": 0, "high": 1}
risks = []
for order_id, row in assigned.items():
    if row["action_code"] == "REVIEW":
        risks.append({
            "order_id": order_id,
            "risk_level": "critical",
            "assigned_warehouse": "",
            "estimated_delivery_hours": "",
            "sla_buffer_hours": "",
            "recommended_action": "REVIEW",
            "reason_code": "NO_FEASIBLE_INVENTORY",
        })
        continue
    order = orders_by_id[order_id]
    warehouse_id = row["assigned_warehouse"]
    handling = policy["constrained_handling_hours"] if caps[warehouse_id]["load_index"] > policy["capacity_guardrail_load_index"] else policy["standard_handling_hours"]
    delivery = handling + transit[(warehouse_id, order["ship_to_zone"])]["transit_hours"]
    buffer = int(order["promised_hours"]) - delivery
    if buffer < 0 or (order["is_expedited"] == "true" and buffer < policy["expedite_buffer_hours"]):
        risk = "critical"
    elif buffer < policy["sla_high_buffer_hours"] or (order["customer_segment"] == "premium" and buffer < policy["sla_premium_buffer_hours"]):
        risk = "high"
    else:
        risk = "monitor"
    if risk != "monitor":
        risks.append({
            "order_id": order_id,
            "risk_level": risk,
            "assigned_warehouse": warehouse_id,
            "estimated_delivery_hours": delivery,
            "sla_buffer_hours": buffer,
            "recommended_action": "EXPEDITE" if risk == "critical" else "ALLOCATE",
            "reason_code": "SLA_RISK",
        })
risks.sort(key=lambda row: (severity[row["risk_level"]], row["order_id"]))
(OUT / "sla_risk_register.json").write_text(json.dumps({"risk_count": len(risks), "risks": risks}, indent=2), encoding="utf-8")

split_rows = []
for order in orders:
    qty = int(order["qty"])
    single = [warehouse_id for warehouse_id in sorted(caps) if inventory.get((warehouse_id, order["sku"]), 0) >= qty]
    if single:
        split_rows.append({
            "order_id": order["order_id"],
            "action_code": "ALLOCATE",
            "warehouse_split": single[0],
            "shipment_count": "1",
            "total_split_cost": str(transit[(single[0], order["ship_to_zone"])]["cost_per_shipment"]),
            "reason_code": "NEAREST_FEASIBLE_DC",
        })
        continue
    candidates = []
    for warehouse_id in sorted(caps):
        available = inventory.get((warehouse_id, order["sku"]), 0)
        if available > 0:
            lane = transit[(warehouse_id, order["ship_to_zone"])]
            candidates.append((lane["transit_hours"], -available, warehouse_id, available, lane["cost_per_shipment"]))
    remaining = qty
    allocation = []
    cost = 0
    for _, _, warehouse_id, available, lane_cost in sorted(candidates):
        take = min(remaining, available)
        allocation.append((warehouse_id, take))
        cost += lane_cost
        remaining -= take
        if remaining == 0 or len(allocation) == policy["split_max_shipments"]:
            break
    if remaining == 0 and len(allocation) <= policy["split_max_shipments"] and cost <= policy["split_cost_limit"]:
        split_rows.append({
            "order_id": order["order_id"],
            "action_code": "SPLIT",
            "warehouse_split": "+".join(f"{warehouse_id}:{take}" for warehouse_id, take in allocation),
            "shipment_count": str(len(allocation)),
            "total_split_cost": str(cost),
            "reason_code": "SPLIT_REQUIRED",
        })
    else:
        split_rows.append({
            "order_id": order["order_id"],
            "action_code": "REVIEW",
            "warehouse_split": "",
            "shipment_count": "0",
            "total_split_cost": "",
            "reason_code": "NO_FEASIBLE_INVENTORY",
        })
write_csv("split_order_plan.csv", ["order_id", "action_code", "warehouse_split", "shipment_count", "total_split_cost", "reason_code"], split_rows)
PY
