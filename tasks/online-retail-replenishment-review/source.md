# Source and Provenance

Status: `runnable_smoke_not_skill_sensitive`

This task has valid external dataset and skill provenance, but pilot runs showed that it is not skill-sensitive enough for paper-facing benchmark claims. Keep it as a runner smoke test unless it is redesigned into a framework-heavy control task.

## Dataset

Primary dataset:

- UCI Machine Learning Repository, Online Retail II
- Source: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- Intended use: derive SKU-level daily demand histories from transaction records.

Local augmentations:

- `current_inventory.csv`
- `inventory_policy.csv` with lead time, safety stock, minimum order quantity, and pack-size rules.

## Provided Skill

| Skill | Source | Role |
| --- | --- | --- |
| `supply-chain-manager` | `sources/skills/supply-chain-manager`, vendored from `theneoai/awesome-skills` commit `10d1e09e3907265e38ab1e9c3d6e38efd6a41611` | Relevant provided skill for supply-chain and inventory policy. |

## Remaining Skill Candidates

| Skill | Source | Role |
| --- | --- | --- |
| `demand-forecasting` | Claude SkillHub candidate, package pending | Potential relevant skill if a full package and license are found. |

## Transformation

The preprocessing script `scripts/preprocess/build_online_retail_replenishment.py` reads the `Year 2010-2011` sheet, filters positive United Kingdom transactions, selects the top 12 SKUs in the 2011-11-01 to 2011-11-28 window, and writes:

- `daily_sku_demand.csv`
- `current_inventory.csv`
- `inventory_policy.csv`

Raw files are stored in `sources/datasets/online-retail-ii/raw/`, which is ignored by git.
