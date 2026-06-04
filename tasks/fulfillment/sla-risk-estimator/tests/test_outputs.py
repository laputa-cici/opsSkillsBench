import csv
import json
from pathlib import Path


APP = Path("/app")
DATA = APP / "data"
OUT = APP / "output"


def read_csv(name):
    with (DATA / name).open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def inventory_by_sku():
    inventory = {}
    for row in read_csv("warehouse_inventory.csv"):
        available = int(row["on_hand"]) - int(row["reserved"]) - int(row["damaged"])
        inventory[(row["warehouse_id"], row["sku"])] = available
    return inventory


def capacities():
    result = {}
    for row in read_csv("warehouse_capacity.csv"):
        result[row["warehouse_id"]] = {
            "pick_capacity_remaining": int(row["pick_capacity_remaining"]),
            "load_index": float(row["load_index"]),
        }
    return result


def transit_lookup():
    result = {}
    for row in read_csv("transit_times.csv"):
        result[(row["warehouse_id"], row["zone"])] = {
            "transit_hours": int(row["transit_hours"]),
            "cost_per_shipment": int(row["cost_per_shipment"]),
        }
    return result


def nearest_inventory_assignment():
    inventory = inventory_by_sku()
    transit = transit_lookup()
    caps = capacities()
    rows = []
    for order in read_csv("orders.csv"):
        qty = int(order["qty"])
        candidates = []
        for warehouse_id in sorted(caps):
            available = inventory.get((warehouse_id, order["sku"]), 0)
            if available >= qty:
                lane = transit[(warehouse_id, order["ship_to_zone"])]
                candidates.append((lane["transit_hours"], caps[warehouse_id]["load_index"], warehouse_id, lane))
        if candidates:
            _, _, warehouse_id, lane = sorted(candidates)[0]
            rows.append({
                "order_id": order["order_id"],
                "assigned_warehouse": warehouse_id,
                "action_code": "ALLOCATE",
                "reason_code": "NEAREST_FEASIBLE_DC",
                "transit_hours": str(lane["transit_hours"]),
            })
        else:
            rows.append({
                "order_id": order["order_id"],
                "assigned_warehouse": "",
                "action_code": "REVIEW",
                "reason_code": "NO_FEASIBLE_INVENTORY",
                "transit_hours": "",
            })
    return rows


def capacity_assignment():
    inventory = inventory_by_sku()
    transit = transit_lookup()
    caps = capacities()
    policy = json.loads((DATA / "fulfillment_policy.json").read_text(encoding="utf-8"))
    rows = []
    for order in read_csv("orders.csv"):
        qty = int(order["qty"])
        candidates = []
        for warehouse_id in sorted(caps):
            available = inventory.get((warehouse_id, order["sku"]), 0)
            cap = caps[warehouse_id]
            if (
                available >= qty
                and cap["pick_capacity_remaining"] >= qty
                and cap["load_index"] <= policy["capacity_guardrail_load_index"]
            ):
                lane = transit[(warehouse_id, order["ship_to_zone"])]
                candidates.append((lane["transit_hours"], cap["load_index"], warehouse_id, lane, cap))
        if not candidates:
            rows.append({
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
        reason = "SLA_RISK" if action == "EXPEDITE" else "CAPACITY_BALANCED_DC"
        rows.append({
            "order_id": order["order_id"],
            "assigned_warehouse": warehouse_id,
            "action_code": action,
            "reason_code": reason,
            "capacity_after_pick": str(cap["pick_capacity_remaining"] - qty),
        })
    return rows


def test_sla_risk_register():
    policy = json.loads((DATA / "fulfillment_policy.json").read_text(encoding="utf-8"))
    assigned = {row["order_id"]: row for row in capacity_assignment()}
    orders = {row["order_id"]: row for row in read_csv("orders.csv")}
    transit = transit_lookup()
    caps = capacities()
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
        order = orders[order_id]
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
    expected = {"risk_count": len(risks), "risks": risks}
    assert json.loads((OUT / "sla_risk_register.json").read_text(encoding="utf-8")) == expected
