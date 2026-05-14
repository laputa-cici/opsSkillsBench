# Source and Provenance

Status: `runnable_external_source`

Note: the current runnable data slice is a compact deterministic derivative of the City of Portland Open Contracting publication. Raw data is stored locally under an ignored `sources/datasets/.../raw/` path; only the small derived task slice is committed.

## Dataset

Primary dataset:

- Open Contracting Data Registry, City of Portland procurement publication
- Source: https://data.open-contracting.org/en/publication/155
- Registry: https://data.open-contracting.org/
- Local provenance: `sources/datasets/portland-procurement/provenance.md`
- Preprocessing script: `scripts/preprocess/build_portland_sourcing_concentration.py`
- Intended use: derive supplier spend concentration, Kraljic segmentation, sourcing strategy, and procurement risk-register tasks.

Derived task inputs:

- `environment/data/awards.csv`
- `environment/data/supplier_profile.csv`
- `environment/data/category_policy.json`

Transformation summary:

1. Download the all-time Open Contracting CSV package for publication `155`.
2. Join `awards.csv`, `awards_suppliers.csv`, `contracts_items.csv`, and `main.csv`.
3. Keep positive USD awards with usable supplier, bureau, category, and award value fields.
4. Map item classification descriptions into five deterministic sourcing categories.
5. Map procurement method into deterministic contract types.
6. Select the top five awards by value per category.
7. Derive category-level supplier profiles and add benchmark-local policy thresholds for deterministic scoring.

## Skill Candidates

| Skill | Source | Role |
| --- | --- | --- |
| `supply-chain-manager` | SkillsMP / `theneoai/awesome-skills`; already vendored in `sources/skills/supply-chain-manager` | Primary Kraljic matrix, sourcing strategy, supplier scorecard, and procurement anti-pattern framework. |
| `operations-manager` | SkillsMP / `theneoai/awesome-skills`; vendored in `sources/skills/operations-manager` | Process ownership, KPI, workflow, and operational follow-up framework. |
| `procurement-review` | SkillsMP candidate | Future P2P and vendor-governance skill if a licensable public package is found. |

## Verification

Oracle validation on 2026-04-08:

```bash
.venv/bin/python scripts/run_task_local.py portland-sourcing-concentration-review --oracle --test
```

Result: `3 passed`.
