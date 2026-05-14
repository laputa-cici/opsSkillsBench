# Online Retail Replenishment Review

You are preparing a daily replenishment review for a small online retailer.

Read these runtime input files:

- `/app/data/daily_sku_demand.csv`
- `/app/data/current_inventory.csv`
- `/app/data/inventory_policy.csv`

Create these output files:

- `/app/output/replenishment_plan.csv`
- `/app/output/replenishment_exceptions.json`

## CSV Output

Write `/app/output/replenishment_plan.csv` with one row per SKU in the order from `inventory_policy.csv`.

Required columns:

```text
sku
avg_daily_demand
reorder_point_units
recommended_order_qty
priority_band
expected_days_of_cover_after_order
```

Rules:

1. Compute `avg_daily_demand` as the mean of `demand_units` across all dates available for that SKU in `daily_sku_demand.csv`.
2. Round `avg_daily_demand` to one decimal place in the output.
3. Compute `reorder_point_units` as:

```text
ceil(avg_daily_demand * lead_time_days + safety_stock_units)
```

4. Compute the raw order gap as:

```text
reorder_point_units - on_hand_units
```

5. If the raw order gap is less than or equal to zero, set `recommended_order_qty` to `0`.
6. Otherwise, round the gap up to the nearest `order_pack_size` and also enforce `minimum_order_qty`.
7. Compute current days of cover as:

```text
on_hand_units / avg_daily_demand
```

8. Assign `priority_band`:

```text
critical = current days of cover <= lead_time_days
high = current days of cover <= high_priority_cover_days
monitor = otherwise
```

9. Compute `expected_days_of_cover_after_order` as:

```text
(on_hand_units + recommended_order_qty) / avg_daily_demand
```

Round it to one decimal place in the output.

## JSON Output

Write `/app/output/replenishment_exceptions.json` with this structure:

```json
{
  "exception_count": 0,
  "exceptions": []
}
```

Include one exception for every SKU where `recommended_order_qty > 0` and `priority_band` is `critical` or `high`.

Each exception object must include:

```text
sku
priority_band
days_of_cover
recommended_order_qty
trigger_rule
```

Sort exceptions by priority severity (`critical` before `high`), then by `days_of_cover` ascending, then by `sku` ascending. Round `days_of_cover` to one decimal place.

