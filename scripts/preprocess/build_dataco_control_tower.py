#!/usr/bin/env python3
"""Build a deterministic control-tower task slice from DataCo order data."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

import pandas as pd


DEFAULT_RAW = Path("sources/datasets/dataco-smart-supply-chain/raw/DataCoSupplyChainDataset.csv")
DEFAULT_OUT = Path("tasks/dataco-control-tower-exception-review/environment/data")

RAW_COLUMNS = [
    "Order Id",
    "Market",
    "Order Region",
    "Customer Segment",
    "Shipping Mode",
    "Days for shipping (real)",
    "Days for shipment (scheduled)",
    "Order Item Total",
    "Category Name",
    "Delivery Status",
]

CUSTOMER_COMMITMENTS = [
    {"customer_segment": "Consumer", "target_otif": 0.44, "escalation_value": 500},
    {"customer_segment": "Corporate", "target_otif": 0.46, "escalation_value": 650},
    {"customer_segment": "Home Office", "target_otif": 0.42, "escalation_value": 450},
]

CONTROL_POLICY = {
    "risk_bands": ["critical", "high", "monitor"],
    "actions": ["mode_change", "customer_notify", "carrier_review", "monitor"],
    "decision_hierarchy": ["service", "cost", "resilience"],
    "workflow_phases": ["plan", "source", "make", "deliver", "return"],
    "owner_functions": {
        "mode_change": "logistics",
        "customer_notify": "customer_service",
        "carrier_review": "transportation",
        "monitor": "control_tower",
    },
    "risk_types": ["carrier_lane_failure", "service_failure", "stable"],
    "lane_mitigations": {
        "carrier_lane_failure": "carrier_improvement_plan",
        "service_failure": "customer_recovery_plan",
        "stable": "monitor",
    },
    "frameworks": [
        "logistics-manager:G4-carrier-performance",
        "supply-chain-manager:service-cost-cash-resilience",
        "operations-manager:kpi-control",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--orders-per-lane", type=int, default=3)
    parser.add_argument("--lane-count", type=int, default=6)
    return parser.parse_args()


def slug(value: object) -> str:
    cleaned = re.sub(r"[^A-Z0-9]+", "-", str(value).upper()).strip("-")
    return cleaned or "UNKNOWN"


def load_raw(raw: Path) -> pd.DataFrame:
    df = pd.read_csv(raw, encoding="latin1", usecols=RAW_COLUMNS)
    df = df[df["Delivery Status"] != "Shipping canceled"].copy()
    for column in ["Days for shipping (real)", "Days for shipment (scheduled)", "Order Item Total"]:
        df[column] = pd.to_numeric(df[column], errors="coerce")
    df = df.dropna(subset=RAW_COLUMNS).copy()
    df["lane"] = df["Market"].map(slug) + "-" + df["Order Region"].map(slug)
    return df


def build_order_level(df: pd.DataFrame) -> pd.DataFrame:
    orders = (
        df.sort_values(["Order Id", "Order Item Total"], ascending=[True, False])
        .groupby("Order Id", as_index=False)
        .agg(
            lane=("lane", "first"),
            shipping_mode=("Shipping Mode", "first"),
            customer_segment=("Customer Segment", "first"),
            category=("Category Name", "first"),
            order_value=("Order Item Total", "sum"),
            promised_days=("Days for shipment (scheduled)", "first"),
            actual_days=("Days for shipping (real)", "first"),
        )
    )
    orders["delay_days"] = (orders["actual_days"] - orders["promised_days"]).clip(lower=0)
    return orders


def choose_lanes(orders: pd.DataFrame, lane_count: int) -> list[str]:
    scorecard = build_lane_scorecard(orders)
    eligible = scorecard[scorecard["shipment_count"] >= 250].copy()

    selected: list[str] = []
    for frame in [
        eligible.sort_values(["otif_rate", "shipment_count"], ascending=[True, False]).head(2),
        eligible.sort_values(["otif_rate", "shipment_count"], ascending=[False, False]).head(2),
        eligible.sort_values(["shipment_count", "lane"], ascending=[False, True]).head(lane_count),
    ]:
        for lane in frame["lane"]:
            if lane not in selected:
                selected.append(str(lane))
            if len(selected) >= lane_count:
                return selected
    return selected


def build_lane_scorecard(orders: pd.DataFrame) -> pd.DataFrame:
    scorecard = (
        orders.groupby("lane", as_index=False)
        .agg(
            shipment_count=("order_id", "nunique") if "order_id" in orders.columns else ("Order Id", "nunique"),
            otif_rate=("delay_days", lambda values: round(float((values <= 0).mean()), 3)),
            avg_delay_days=("delay_days", lambda values: round(float(values.mean()), 2)),
            cost_per_order=("order_value", lambda values: round(float(values.mean()) / 10 + 10, 2)),
        )
        .sort_values("lane")
    )
    return scorecard


def select_orders(orders: pd.DataFrame, lanes: list[str], orders_per_lane: int) -> pd.DataFrame:
    selected = []
    for lane in lanes:
        lane_orders = orders[orders["lane"] == lane].copy()
        if lane_orders.empty:
            continue

        delayed = lane_orders[lane_orders["delay_days"] > 0]
        on_time = lane_orders[lane_orders["delay_days"] <= 0]
        picks = [
            delayed.sort_values(["order_value", "Order Id"], ascending=[False, True]).head(1),
            on_time.sort_values(["order_value", "Order Id"], ascending=[False, True]).head(1),
            delayed.sort_values(["order_value", "Order Id"], ascending=[True, True]).head(1),
        ]
        lane_selected = pd.concat([pick for pick in picks if not pick.empty]).drop_duplicates("Order Id")
        if len(lane_selected) < orders_per_lane:
            extras = lane_orders.sort_values(["Order Id"]).head(orders_per_lane)
            lane_selected = pd.concat([lane_selected, extras]).drop_duplicates("Order Id")
        selected.append(lane_selected.head(orders_per_lane))

    if not selected:
        raise ValueError("No orders selected; check the raw DataCo file and lane selection filters.")
    return pd.concat(selected).drop_duplicates("Order Id").copy()


def write_outputs(orders: pd.DataFrame, out: Path, lane_count: int, orders_per_lane: int) -> None:
    out.mkdir(parents=True, exist_ok=True)
    lanes = choose_lanes(orders, lane_count)
    selected_orders = select_orders(orders, lanes, orders_per_lane)

    order_snapshot = selected_orders[
        [
            "Order Id",
            "lane",
            "shipping_mode",
            "customer_segment",
            "category",
            "order_value",
            "promised_days",
            "actual_days",
        ]
    ].rename(columns={"Order Id": "order_id"})
    order_snapshot["order_id"] = order_snapshot["order_id"].map(lambda value: f"DC-{int(value)}")
    order_snapshot["order_value"] = order_snapshot["order_value"].round(0).astype(int)
    order_snapshot["promised_days"] = order_snapshot["promised_days"].astype(int)
    order_snapshot["actual_days"] = order_snapshot["actual_days"].astype(int)
    order_snapshot = order_snapshot.sort_values("order_id")
    order_snapshot.to_csv(out / "order_snapshot.csv", index=False)

    scorecard_orders = orders[orders["lane"].isin(lanes)].rename(columns={"Order Id": "order_id"})
    lane_scorecard = build_lane_scorecard(scorecard_orders)[
        ["lane", "shipment_count", "otif_rate", "avg_delay_days", "cost_per_order"]
    ]
    lane_scorecard.to_csv(out / "carrier_lane_scorecard.csv", index=False)

    pd.DataFrame(CUSTOMER_COMMITMENTS).to_csv(out / "customer_commitments.csv", index=False)
    (out / "control_policy.json").write_text(json.dumps(CONTROL_POLICY, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    args = parse_args()
    raw = load_raw(args.raw)
    orders = build_order_level(raw)
    write_outputs(orders, args.out, args.lane_count, args.orders_per_lane)


if __name__ == "__main__":
    main()
