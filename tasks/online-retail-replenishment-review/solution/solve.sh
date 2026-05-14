#!/bin/bash
set -euo pipefail

python - <<'PY'
import json
import math
from pathlib import Path

import pandas as pd

data_dir = Path("/app/data")
out_dir = Path("/app/output")
out_dir.mkdir(parents=True, exist_ok=True)

daily = pd.read_csv(data_dir / "daily_sku_demand.csv")
inventory = pd.read_csv(data_dir / "current_inventory.csv")
policy = pd.read_csv(data_dir / "inventory_policy.csv")

avg = (
    daily.groupby("sku", as_index=False)["demand_units"]
    .mean()
    .rename(columns={"demand_units": "avg_daily_demand"})
)

df = policy.merge(inventory, on="sku", how="left").merge(avg, on="sku", how="left")
df["avg_daily_demand"] = df["avg_daily_demand"].clip(lower=1e-9)
df["reorder_point_units"] = (
    df["avg_daily_demand"] * df["lead_time_days"] + df["safety_stock_units"]
).apply(math.ceil)

def round_order(row):
    gap = row["reorder_point_units"] - row["on_hand_units"]
    if gap <= 0:
        return 0
    pack_qty = int(math.ceil(gap / row["order_pack_size"]) * row["order_pack_size"])
    return max(pack_qty, int(row["minimum_order_qty"]))

df["recommended_order_qty"] = df.apply(round_order, axis=1)
df["current_days_of_cover"] = df["on_hand_units"] / df["avg_daily_demand"]

def priority(row):
    if row["current_days_of_cover"] <= row["lead_time_days"]:
        return "critical"
    if row["current_days_of_cover"] <= row["high_priority_cover_days"]:
        return "high"
    return "monitor"

df["priority_band"] = df.apply(priority, axis=1)
df["expected_days_of_cover_after_order"] = (
    (df["on_hand_units"] + df["recommended_order_qty"]) / df["avg_daily_demand"]
)

plan = pd.DataFrame(
    {
        "sku": df["sku"],
        "avg_daily_demand": df["avg_daily_demand"].round(1),
        "reorder_point_units": df["reorder_point_units"].astype(int),
        "recommended_order_qty": df["recommended_order_qty"].astype(int),
        "priority_band": df["priority_band"],
        "expected_days_of_cover_after_order": df["expected_days_of_cover_after_order"].round(1),
    }
)
plan.to_csv(out_dir / "replenishment_plan.csv", index=False)

exceptions = df[
    (df["recommended_order_qty"] > 0) & (df["priority_band"].isin(["critical", "high"]))
].copy()
severity = {"critical": 0, "high": 1}
exceptions["_severity"] = exceptions["priority_band"].map(severity)
exceptions = exceptions.sort_values(["_severity", "current_days_of_cover", "sku"])

records = []
for _, row in exceptions.iterrows():
    if row["priority_band"] == "critical":
        rule = "current_days_of_cover <= lead_time_days"
    else:
        rule = "current_days_of_cover <= high_priority_cover_days"
    records.append(
        {
            "sku": row["sku"],
            "priority_band": row["priority_band"],
            "days_of_cover": round(float(row["current_days_of_cover"]), 1),
            "recommended_order_qty": int(row["recommended_order_qty"]),
            "trigger_rule": rule,
        }
    )

(out_dir / "replenishment_exceptions.json").write_text(
    json.dumps({"exception_count": len(records), "exceptions": records}, indent=2),
    encoding="utf-8",
)
PY

