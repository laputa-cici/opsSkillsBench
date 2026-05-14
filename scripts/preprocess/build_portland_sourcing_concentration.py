#!/usr/bin/env python3
"""Build a deterministic sourcing-concentration task slice from Portland OCDS CSVs."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd


DEFAULT_RAW_DIR = Path("sources/datasets/portland-procurement/raw/full")
DEFAULT_OUT = Path("tasks/portland-sourcing-concentration-review/environment/data")

CATEGORY_ORDER = [
    "Road & Construction",
    "Technology & Equipment",
    "Office & Facilities",
    "Emergency & Safety",
    "Professional Services",
]

CATEGORY_CRITICALITY = {
    "Road & Construction": 5,
    "Technology & Equipment": 5,
    "Emergency & Safety": 5,
    "Professional Services": 3,
    "Office & Facilities": 2,
}

CATEGORY_POLICY = {
    "spend_impact_threshold": 75_000_000,
    "high_supply_risk_criticality": 4,
    "high_concentration_share": 0.55,
    "quadrant_strategy": {
        "strategic": "partnership_development",
        "leverage": "competitive_bidding",
        "bottleneck": "ensure_supply_and_buffer",
        "non_critical": "process_efficiency",
    },
    "mitigation_by_antipattern": {
        "single_sourcing": "develop_second_source",
        "price_only_focus": "run_total_cost_review",
        "supplier_fragmentation": "consolidate_tail_spend",
        "none": "monitor",
    },
    "skill_frameworks": [
        "supply-chain-manager:kraljic-matrix",
        "supply-chain-manager:anti-patterns",
        "operations-manager:kpi-control",
    ],
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw-dir", type=Path, default=DEFAULT_RAW_DIR)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--awards-per-category", type=int, default=5)
    return parser.parse_args()


def category_bucket(description: object) -> str:
    text = str(description).upper()
    if any(token in text for token in ["ROAD", "HWY", "HIGHWAY", "ASPHALT", "CONSTRUCTION", "ENGINEERING"]):
        return "Road & Construction"
    if any(token in text for token in ["COMPUTER", "SOFTWARE", "HARDWARE", "ELECTRICAL", "TELECOMMUNICATION", "DATA PROCESSING"]):
        return "Technology & Equipment"
    if any(token in text for token in ["OFFICE", "FURNITURE", "BUILDING MAINTENANCE", "FACILITY"]):
        return "Office & Facilities"
    if any(token in text for token in ["SECURITY", "FIRE", "SAFETY", "EMERGENCY", "HAZARDOUS"]):
        return "Emergency & Safety"
    if any(token in text for token in ["PROFESSIONAL", "CONSULTING", "ARCHITECT"]):
        return "Professional Services"
    return "Other"


def contract_type(method: object) -> str:
    normalized = str(method).lower()
    if normalized == "direct":
        return "sole_source"
    if normalized == "limited":
        return "limited"
    if normalized in {"open", "selective"}:
        return "competitive"
    return "renewal"


def load_joined(raw_dir: Path) -> pd.DataFrame:
    awards = pd.read_csv(
        raw_dir / "awards.csv",
        usecols=["id", "value_amount", "value_currency", "main_id"],
        dtype={"id": str, "main_id": str},
    )
    suppliers = (
        pd.read_csv(raw_dir / "awards_suppliers.csv", usecols=["name", "awards_id"], dtype={"awards_id": str})
        .drop_duplicates(["awards_id", "name"])
        .sort_values(["awards_id", "name"])
        .drop_duplicates("awards_id")
    )
    main = (
        pd.read_csv(raw_dir / "main.csv", usecols=["id", "buyer_name", "tender_procurementMethod"], dtype={"id": str})
        .drop_duplicates("id")
    )
    items = pd.read_csv(
        raw_dir / "contracts_items.csv",
        usecols=["contracts_id", "classification_description"],
        dtype={"contracts_id": str},
    )
    dominant_class = (
        items.dropna(subset=["classification_description"])
        .drop_duplicates(["contracts_id", "classification_description"])
        .groupby(["contracts_id", "classification_description"], as_index=False)
        .size()
        .sort_values(["contracts_id", "size", "classification_description"], ascending=[True, False, True])
        .drop_duplicates("contracts_id")
    )

    df = (
        awards.merge(suppliers, left_on="id", right_on="awards_id", how="left")
        .merge(main, left_on="main_id", right_on="id", how="left", suffixes=("", "_main"))
        .merge(dominant_class, left_on="id", right_on="contracts_id", how="left")
    )
    df = df.dropna(subset=["value_amount", "name", "classification_description", "buyer_name"])
    df = df[(df["value_currency"] == "USD") & (df["value_amount"] > 0)].copy()
    df["category"] = df["classification_description"].map(category_bucket)
    df["contract_type"] = df["tender_procurementMethod"].map(contract_type)
    df = df[df["category"].isin(CATEGORY_ORDER)].copy()
    return df.sort_values(["value_amount", "id"], ascending=[False, True]).drop_duplicates("id")


def build_awards(df: pd.DataFrame, awards_per_category: int) -> pd.DataFrame:
    selected = []
    for category in CATEGORY_ORDER:
        category_awards = df[df["category"] == category].sort_values(["value_amount", "id"], ascending=[False, True])
        if category_awards.empty:
            raise ValueError(f"No Portland awards found for category bucket: {category}")
        selected.append(category_awards.head(awards_per_category))
    awards = pd.concat(selected).copy()
    awards["award_value"] = awards["value_amount"].round(0).astype(int)
    awards = awards.rename(columns={"id": "award_id", "name": "supplier", "buyer_name": "bureau"})
    awards["award_id"] = "POR-" + awards["award_id"].astype(str)
    return awards[["award_id", "category", "supplier", "bureau", "contract_type", "award_value"]].sort_values(
        ["category", "award_id"]
    )


def build_supplier_profile(awards: pd.DataFrame) -> pd.DataFrame:
    rows = []
    for category, group in awards.groupby("category"):
        supplier_count = int(group["supplier"].nunique())
        incumbent_count = int(group[group["contract_type"] == "renewal"]["supplier"].nunique())
        criticality = CATEGORY_CRITICALITY[category]
        noncompetitive_share = float(group["contract_type"].isin(["sole_source", "limited", "renewal"]).mean())
        competition_flag = "limited_competition" if supplier_count <= 2 or noncompetitive_share >= 0.50 else "competitive"
        rows.append(
            {
                "category": category,
                "supplier_count": supplier_count,
                "incumbent_supplier_count": incumbent_count,
                "criticality_score": criticality,
                "competition_flag": competition_flag,
            }
        )
    return pd.DataFrame(rows).sort_values("category")


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)
    joined = load_joined(args.raw_dir)
    awards = build_awards(joined, args.awards_per_category)
    profile = build_supplier_profile(awards)

    awards.to_csv(args.out / "awards.csv", index=False)
    profile.to_csv(args.out / "supplier_profile.csv", index=False)
    (args.out / "category_policy.json").write_text(json.dumps(CATEGORY_POLICY, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
