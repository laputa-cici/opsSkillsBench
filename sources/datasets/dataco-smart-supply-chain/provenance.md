# DataCo SMART Supply Chain Provenance

Dataset: DataCo SMART SUPPLY CHAIN FOR BIG DATA ANALYSIS

Primary source:

- https://data.mendeley.com/datasets/8gx2fvg2k6/5

Local raw file:

- `sources/datasets/dataco-smart-supply-chain/raw/DataCoSupplyChainDataset.csv`

Access / import date:

- 2026-04-08

Raw file policy:

- The raw CSV is kept under `sources/datasets/dataco-smart-supply-chain/raw/`, which is ignored by git.
- Committed task files are deterministic derived slices, not the full raw dataset.

Derived benchmark task:

- `tasks/dataco-control-tower-exception-review`

Preprocessing script:

- `scripts/preprocess/build_dataco_control_tower.py`

Transformation summary:

1. Read the DataCo order-level and order-line columns needed for logistics review:
   `Order Id`, `Market`, `Order Region`, `Customer Segment`, `Shipping Mode`,
   shipping days, order value, category, and delivery status.
2. Exclude `Shipping canceled` rows because they do not represent normal completed delivery performance.
3. Aggregate order lines into one row per `Order Id`, summing `Order Item Total`.
4. Construct a deterministic lane id from `Market` and `Order Region`.
5. Compute `delay_days = max(actual_days - promised_days, 0)`.
6. Select six deterministic lanes using a mix of low-OTIF, high-OTIF, and high-volume lanes.
7. Select three representative orders per lane: a high-value delayed order, a high-value on-time order, and a low-value delayed order when available.
8. Derive lane-level scorecards with shipment count, OTIF rate, average delay, and cost proxy.
9. Add benchmark-local customer commitment and control policy files to make the task deterministic and machine-verifiable.

Derived files:

- `tasks/dataco-control-tower-exception-review/environment/data/order_snapshot.csv`
- `tasks/dataco-control-tower-exception-review/environment/data/carrier_lane_scorecard.csv`
- `tasks/dataco-control-tower-exception-review/environment/data/customer_commitments.csv`
- `tasks/dataco-control-tower-exception-review/environment/data/control_policy.json`
