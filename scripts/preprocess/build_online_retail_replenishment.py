#!/usr/bin/env python3
"""Build a small deterministic replenishment task slice from Online Retail II."""

from __future__ import annotations

import argparse
import math
from pathlib import Path

import pandas as pd


DEFAULT_RAW = Path("sources/datasets/online-retail-ii/raw/online_retail_II.xlsx")
DEFAULT_OUT = Path("tasks/online-retail-replenishment-review/environment/data")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--sheet", default="Year 2010-2011")
    parser.add_argument("--start", default="2011-11-01")
    parser.add_argument("--end", default="2011-11-28")
    parser.add_argument("--sku-count", type=int, default=12)
    return parser.parse_args()


def clean_transactions(raw: Path, sheet: str) -> pd.DataFrame:
    df = pd.read_excel(
        raw,
        sheet_name=sheet,
        usecols=["StockCode", "Description", "Quantity", "InvoiceDate", "Price", "Country"],
    )
    df = df.rename(
        columns={
            "StockCode": "sku",
            "Description": "description",
            "Quantity": "quantity",
            "InvoiceDate": "invoice_date",
            "Price": "unit_price",
            "Country": "country",
        }
    )
    df["sku"] = df["sku"].astype(str).str.strip()
    df["invoice_date"] = pd.to_datetime(df["invoice_date"])
    df["date"] = df["invoice_date"].dt.date
    return df[
        (df["quantity"] > 0)
        & (df["unit_price"] > 0)
        & (df["country"] == "United Kingdom")
        & (df["sku"].str.fullmatch(r"[0-9A-Z]+"))
        & (~df["sku"].isin(["POST", "M", "DOT", "BANK CHARGES"]))
    ].copy()


def build_slice(df: pd.DataFrame, start: str, end: str, sku_count: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    start_date = pd.to_datetime(start).date()
    end_date = pd.to_datetime(end).date()
    window = df[(df["date"] >= start_date) & (df["date"] <= end_date)].copy()

    top_skus = (
        window.groupby("sku", as_index=False)["quantity"]
        .sum()
        .sort_values(["quantity", "sku"], ascending=[False, True])
        .head(sku_count)["sku"]
        .tolist()
    )
    window = window[window["sku"].isin(top_skus)].copy()
    sku_order = {sku: idx for idx, sku in enumerate(top_skus)}

    dates = pd.date_range(start_date, end_date, freq="D").date
    index = pd.MultiIndex.from_product([top_skus, dates], names=["sku", "date"])
    daily = (
        window.groupby(["sku", "date"], as_index=True)["quantity"]
        .sum()
        .reindex(index, fill_value=0)
        .reset_index()
        .rename(columns={"quantity": "demand_units"})
    )
    daily["date"] = daily["date"].astype(str)

    descriptions = (
        window.sort_values("invoice_date")
        .drop_duplicates("sku")
        .set_index("sku")["description"]
        .to_dict()
    )

    avg = daily.groupby("sku")["demand_units"].mean().reindex(top_skus)
    avg = avg.clip(lower=1.0)
    lead_times = [4, 7, 10, 5, 8, 6, 9, 12, 3, 11, 5, 7]
    pack_sizes = [6, 12, 24, 10, 8, 15, 20, 25, 30, 5, 18, 16]
    safety_multipliers = [0.35, 0.50, 0.25, 0.75, 0.40, 0.60, 0.30, 0.55, 0.45, 0.65, 0.20, 0.70]
    cover_targets = [2, 5, 8, 12, 4, 9, 15, 6, 3, 11, 7, 14]

    policy_rows = []
    inventory_rows = []
    for sku in top_skus:
        idx = sku_order[sku]
        daily_demand = float(avg.loc[sku])
        lead_time = lead_times[idx % len(lead_times)]
        pack_size = pack_sizes[idx % len(pack_sizes)]
        safety_stock = int(math.ceil(daily_demand * lead_time * safety_multipliers[idx % len(safety_multipliers)]))
        min_order_qty = pack_size if idx % 4 != 2 else pack_size * 2
        service_threshold = lead_time + (2 if idx % 3 == 0 else 4)
        on_hand = int(round(daily_demand * cover_targets[idx % len(cover_targets)]))
        policy_rows.append(
            {
                "sku": sku,
                "description": descriptions.get(sku, ""),
                "lead_time_days": lead_time,
                "safety_stock_units": safety_stock,
                "order_pack_size": pack_size,
                "minimum_order_qty": min_order_qty,
                "high_priority_cover_days": service_threshold,
            }
        )
        inventory_rows.append({"sku": sku, "on_hand_units": on_hand})

    inventory = pd.DataFrame(inventory_rows)
    policy = pd.DataFrame(policy_rows)
    return daily, inventory, policy


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    df = clean_transactions(args.raw, args.sheet)
    daily, inventory, policy = build_slice(df, args.start, args.end, args.sku_count)
    daily.to_csv(args.out / "daily_sku_demand.csv", index=False)
    inventory.to_csv(args.out / "current_inventory.csv", index=False)
    policy.to_csv(args.out / "inventory_policy.csv", index=False)


if __name__ == "__main__":
    main()

