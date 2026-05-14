# Portland Open Contracting Provenance

Dataset: City of Portland procurement publication in the Open Contracting Data Registry

Primary source:

- https://data.open-contracting.org/en/publication/155

Downloaded package:

- https://data.open-contracting.org/en/publication/155/download?name=full.csv.tar.gz

License signal:

- Public Domain Dedication and License (PDDL), as shown on the Open Contracting Data Registry publication page.

Local raw files:

- `sources/datasets/portland-procurement/raw/full.csv.tar.gz`
- `sources/datasets/portland-procurement/raw/full/`

Access / import date:

- 2026-04-08

Raw file policy:

- Raw downloaded CSV files are kept under `sources/datasets/portland-procurement/raw/`, which is ignored by git.
- Committed task files are deterministic derived slices, not the full raw dataset.

Derived benchmark task:

- `tasks/portland-sourcing-concentration-review`

Preprocessing script:

- `scripts/preprocess/build_portland_sourcing_concentration.py`

Transformation summary:

1. Use OCDS CSV tables `awards.csv`, `awards_suppliers.csv`, `contracts_items.csv`, and `main.csv`.
2. Join awards to suppliers, buyer bureau, procurement method, and item classification.
3. Keep USD awards with positive award value and usable supplier/category fields.
4. Map item classifications into deterministic benchmark categories:
   `Road & Construction`, `Technology & Equipment`, `Office & Facilities`,
   `Emergency & Safety`, and `Professional Services`.
5. Map OCDS procurement method into benchmark contract type:
   `competitive`, `limited`, `sole_source`, or `renewal`.
6. Select the top five awards by value for each benchmark category.
7. Derive category-level supplier profiles with supplier count, incumbent count,
   criticality score, and competition flag.
8. Add benchmark-local category policy thresholds and Kraljic/anti-pattern mappings
   to keep scoring deterministic and machine-verifiable.

Derived files:

- `tasks/portland-sourcing-concentration-review/environment/data/awards.csv`
- `tasks/portland-sourcing-concentration-review/environment/data/supplier_profile.csv`
- `tasks/portland-sourcing-concentration-review/environment/data/category_policy.json`
