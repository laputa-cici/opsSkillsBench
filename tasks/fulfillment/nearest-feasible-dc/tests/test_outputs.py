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


def test_nearest_feasible_dc_assignment():
    expected = nearest_inventory_assignment()
    with (OUT / "warehouse_assignment.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actual = list(reader)
        assert reader.fieldnames == ["order_id", "assigned_warehouse", "action_code", "reason_code", "transit_hours"]
    assert actual == expected
