from __future__ import annotations

import json
import shutil
import textwrap
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
SOURCE_SKILLS_DIR = TASKS_DIR / "dataco-control-tower-exception-review" / "environment" / "skills"


DATA_FILES = {
    "orders.csv": """order_id,sku,qty,customer_segment,order_value,is_expedited,promised_hours,ship_to_zone
O1001,SKU-A,8,premium,920,false,48,North
O1002,SKU-B,6,standard,180,false,72,South
O1003,SKU-C,12,premium,1440,true,36,East
O1004,SKU-D,5,standard,95,false,48,West
O1005,SKU-A,15,premium,1725,false,24,South
O1006,SKU-E,4,standard,240,false,48,North
O1007,SKU-B,14,premium,560,true,24,East
O1008,SKU-F,3,standard,75,false,72,West
""",
    "warehouse_inventory.csv": """warehouse_id,sku,on_hand,reserved,damaged
W1,SKU-A,20,3,1
W1,SKU-B,4,0,0
W1,SKU-C,5,0,0
W1,SKU-D,8,1,0
W1,SKU-E,2,0,0
W2,SKU-A,10,0,0
W2,SKU-B,10,0,0
W2,SKU-C,8,0,0
W2,SKU-D,2,0,0
W2,SKU-E,6,1,0
W3,SKU-A,5,0,0
W3,SKU-B,8,0,0
W3,SKU-C,10,0,0
W3,SKU-D,5,0,0
W3,SKU-E,1,0,0
""",
    "warehouse_capacity.csv": """warehouse_id,pick_capacity_remaining,load_index
W1,20,0.72
W2,12,0.88
W3,25,0.55
""",
    "transit_times.csv": """warehouse_id,zone,transit_hours,cost_per_shipment
W1,North,12,8
W1,South,36,14
W1,East,30,16
W1,West,40,18
W2,North,30,12
W2,South,14,8
W2,East,24,13
W2,West,32,15
W3,North,28,11
W3,South,26,10
W3,East,16,9
W3,West,18,8
""",
    "fulfillment_policy.json": json.dumps(
        {
            "capacity_guardrail_load_index": 0.85,
            "sla_high_buffer_hours": 12,
            "sla_premium_buffer_hours": 16,
            "expedite_buffer_hours": 8,
            "standard_handling_hours": 8,
            "constrained_handling_hours": 16,
            "split_max_shipments": 2,
            "split_cost_limit": 24,
            "allowed_actions": ["ALLOCATE", "EXPEDITE", "SPLIT", "REVIEW"],
            "reason_codes": [
                "NEAREST_FEASIBLE_DC",
                "CAPACITY_BALANCED_DC",
                "SLA_RISK",
                "SPLIT_REQUIRED",
                "NO_FEASIBLE_INVENTORY",
                "DATA_REVIEW",
            ],
        },
        indent=2,
    )
    + "\n",
}


COMMON_TEST_HELPERS = r"""
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
"""


TASKS = {
    "nearest-feasible-dc": {
        "title": "Nearest Feasible Distribution Center",
        "description": "Assign each order to the nearest warehouse that has enough available inventory, or mark it for review.",
        "output": "warehouse_assignment.csv",
        "columns": ["order_id", "assigned_warehouse", "action_code", "reason_code", "transit_hours"],
        "test": """
def test_nearest_feasible_dc_assignment():
    expected = nearest_inventory_assignment()
    with (OUT / "warehouse_assignment.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actual = list(reader)
        assert reader.fieldnames == ["order_id", "assigned_warehouse", "action_code", "reason_code", "transit_hours"]
    assert actual == expected
""",
    },
    "capacity-aware-allocation": {
        "title": "Capacity Aware Allocation",
        "description": "Assign orders to warehouses that satisfy inventory, remaining pick capacity, and load guardrail constraints.",
        "output": "capacity_adjusted_assignment.csv",
        "columns": ["order_id", "assigned_warehouse", "action_code", "reason_code", "capacity_after_pick"],
        "test": """
def test_capacity_aware_allocation():
    expected = capacity_assignment()
    with (OUT / "capacity_adjusted_assignment.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actual = list(reader)
        assert reader.fieldnames == ["order_id", "assigned_warehouse", "action_code", "reason_code", "capacity_after_pick"]
    assert actual == expected
""",
    },
    "sla-risk-estimator": {
        "title": "SLA Risk Estimator",
        "description": "Estimate fulfillment SLA risk using assigned warehouse, handling time, transit time, promised hours, and customer segment.",
        "output": "sla_risk_register.json",
        "columns": [],
        "test": """
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
""",
    },
    "split-order-decision": {
        "title": "Split Order Decision",
        "description": "Decide whether orders without a single feasible warehouse can be split across at most two warehouses.",
        "output": "split_order_plan.csv",
        "columns": ["order_id", "action_code", "warehouse_split", "shipment_count", "total_split_cost", "reason_code"],
        "test": """
def test_split_order_decision():
    inventory = inventory_by_sku()
    transit = transit_lookup()
    caps = capacities()
    policy = json.loads((DATA / "fulfillment_policy.json").read_text(encoding="utf-8"))
    expected = []
    for order in read_csv("orders.csv"):
        qty = int(order["qty"])
        single = [w for w in sorted(caps) if inventory.get((w, order["sku"]), 0) >= qty]
        if single:
            expected.append({
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
            expected.append({
                "order_id": order["order_id"],
                "action_code": "SPLIT",
                "warehouse_split": "+".join(f"{warehouse_id}:{take}" for warehouse_id, take in allocation),
                "shipment_count": str(len(allocation)),
                "total_split_cost": str(cost),
                "reason_code": "SPLIT_REQUIRED",
            })
        else:
            expected.append({
                "order_id": order["order_id"],
                "action_code": "REVIEW",
                "warehouse_split": "",
                "shipment_count": "0",
                "total_split_cost": "",
                "reason_code": "NO_FEASIBLE_INVENTORY",
            })
    with (OUT / "split_order_plan.csv").open(newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        actual = list(reader)
        assert reader.fieldnames == ["order_id", "action_code", "warehouse_split", "shipment_count", "total_split_cost", "reason_code"]
    assert actual == expected
""",
    },
}


SOLUTION = r"""#!/usr/bin/env bash
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
"""


def write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(textwrap.dedent(text).lstrip(), encoding="utf-8")


def render_task_toml(task_id: str, spec: dict) -> str:
    return f'''schema_version = "1.1"

[task]
name = "ops/fulfillment/{task_id}"
description = "{spec["description"]}"
authors = [{{ name = "OpsSkillsBench", email = "support@example.com" }}]
keywords = ["operations", "fulfillment", "allocation", "warehouse"]

[metadata]
domain = "operations-management"
problem_domain = "fulfillment"
difficulty = "medium"
status = "runnable_prototype_external_schema"
atomic_task = true
parent_task = "dataco-control-tower-exception-review"
dataset_sources = ["prototype-olist-style-fulfillment-slice"]
skill_candidates = ["supply-chain-manager", "logistics-manager", "operations-manager"]
expected_outputs = ["/app/output/{spec["output"]}"]
source_note = "Prototype fulfillment allocation task based on the PDF backlog; uses committed synthetic operational fields and inherits task-local skills from the DataCo fulfillment parent."

[agent]
timeout_sec = 300.0

[verifier]
timeout_sec = 300.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 1024
allow_internet = false
skills_dir = "/opt/skills"
'''


def render_instruction(task_id: str, spec: dict) -> str:
    outputs = f"- `/app/output/{spec['output']}`"
    if spec["columns"]:
        columns = "\n".join(spec["columns"])
        schema = f"\nRequired columns:\n\n```text\n{columns}\n```\n"
    else:
        schema = "\nUse the JSON structure described by the task policy and verifier.\n"
    return f"""# {spec["title"]}

{spec["description"]}

Read the runtime input files:

- `/app/data/orders.csv`
- `/app/data/warehouse_inventory.csv`
- `/app/data/warehouse_capacity.csv`
- `/app/data/transit_times.csv`
- `/app/data/fulfillment_policy.json`

Create:

{outputs}
{schema}
Keep all action and reason codes inside `fulfillment_policy.json`. Sort output rows by `order_id` when writing CSV files. Do not run the bundled oracle solution.
"""


def render_design(task_id: str, spec: dict) -> str:
    return f"""# {spec["title"]}

This atomic task adds an order-allocation style fulfillment item beyond the original DataCo control-tower split.

## Purpose

{spec["description"]}

## Output

- `/app/output/{spec["output"]}`

## Skill Surface

The task is designed to exercise fulfillment concepts from logistics and operations skills: feasible inventory, warehouse capacity, SLA risk, split-order tradeoffs, action codes, and reason-code discipline.
"""


def render_source() -> str:
    return """# Prototype Fulfillment Allocation Source

This task uses a committed prototype fulfillment slice designed from the order allocation scenario in `docs/Operations领域适合做SkillsBench工作的题目建议.pdf`.

The slice is intentionally small and deterministic. Public-data expansion candidates:

- Brazilian E-Commerce Public Dataset by Olist
- Instacart Market Basket Analysis
- DataCo SMART Supply Chain

Operational fields such as warehouse capacity, transit time, reserved inventory, damaged inventory, and fulfillment policy thresholds are synthetic control fields used to make the verifier deterministic.
"""


def build() -> None:
    for task_id, spec in TASKS.items():
        root = TASKS_DIR / "fulfillment" / task_id
        if root.exists():
            shutil.rmtree(root)
        for name, text in DATA_FILES.items():
            write(root / "environment" / "data" / name, text)
        write(root / "solution" / "solve.sh", SOLUTION)
        (root / "solution" / "solve.sh").chmod(0o755)
        write(root / "tests" / "test.sh", "#!/usr/bin/env bash\nset -euo pipefail\npython3 -m pytest /tests/test_outputs.py -rA\n")
        (root / "tests" / "test.sh").chmod(0o755)
        write(root / "tests" / "test_outputs.py", COMMON_TEST_HELPERS + "\n" + spec["test"])
        write(root / "task.toml", render_task_toml(task_id, spec))
        write(root / "instruction.md", render_instruction(task_id, spec))
        write(root / "TASK_DESIGN.md", render_design(task_id, spec))
        write(root / "source.md", render_source())
        print(f"[fulfillment-task] {root.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    build()
