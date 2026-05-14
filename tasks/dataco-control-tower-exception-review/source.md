# Source and Provenance

Status: `runnable_external_source`

Note: the current runnable data slice is a compact deterministic derivative of the raw DataCo SMART Supply Chain CSV. Raw data is stored locally under an ignored `sources/datasets/.../raw/` path; only the small derived task slice is committed.

## Dataset

Primary dataset:

- DataCo SMART SUPPLY CHAIN FOR BIG DATA ANALYSIS
- Source: https://data.mendeley.com/datasets/8gx2fvg2k6/5
- Local provenance: `sources/datasets/dataco-smart-supply-chain/provenance.md`
- Preprocessing script: `scripts/preprocess/build_dataco_control_tower.py`
- Intended use: derive order-level delivery and fulfillment risk snapshots.

Derived task inputs:

- `environment/data/order_snapshot.csv`
- `environment/data/carrier_lane_scorecard.csv`
- `environment/data/customer_commitments.csv`
- `environment/data/control_policy.json`

Transformation summary:

1. Exclude canceled shipments.
2. Aggregate DataCo order lines to one row per `Order Id`.
3. Build lane ids from `Market` and `Order Region`.
4. Compute promised vs. actual shipping delay.
5. Derive lane scorecards with shipment count, OTIF rate, average delay, and a deterministic cost proxy.
6. Select a compact deterministic slice across six lanes and three representative orders per lane.
7. Add benchmark-local customer commitments and control policies to keep scoring reproducible.

## Skill Candidates

| Skill | Source | Role |
| --- | --- | --- |
| `supply-chain-manager` | SkillsMP / `theneoai/awesome-skills`; already vendored in `sources/skills/supply-chain-manager` | Primary supply-chain hierarchy, scorecard, inventory/logistics, SOP, and risk framework. |
| `logistics-manager` | SkillsMP / `theneoai/awesome-skills`; vendored in `sources/skills/logistics-manager` | Transportation, lane, carrier, fulfillment, and logistics cost/service tradeoff framework. |
| `operations-manager` | SkillsMP / `theneoai/awesome-skills`; vendored in `sources/skills/operations-manager` | Operational excellence, KPI, workflow ownership, and process-improvement framework. |

## Verification

Oracle validation on 2026-04-08:

```bash
.venv/bin/python scripts/run_task_local.py dataco-control-tower-exception-review --oracle --test
```

Result: `3 passed`.
