# OR-Library Job Shop Provenance

Dataset: OR-Library Job Shop Scheduling instances

Primary source:

- https://people.brunel.ac.uk/~mastjjb/jeb/orlib/jobshopinfo.html

Downloaded file:

- https://people.brunel.ac.uk/~mastjjb/jeb/orlib/files/jobshop1.txt

Local raw file:

- `sources/datasets/orlib-jobshop/raw/jobshop1.txt`

Access / import date:

- 2026-04-08

Raw file policy:

- Raw OR-Library files are kept under `sources/datasets/orlib-jobshop/raw/`, which is ignored by git.
- Committed task files are deterministic derived slices, not the full raw instance collection.

Derived benchmark task:

- `tasks/orlib-disruption-recovery-control`

Preprocessing script:

- `scripts/preprocess/build_orlib_disruption_recovery.py`

Selected instance:

- `ft06`
- Fisher and Thompson 6x6 job-shop instance, also known as `mt06`.

Transformation summary:

1. Parse the named `ft06` instance from `jobshop1.txt`.
2. Convert OR-Library machine numbers to benchmark machine ids such as `M0`, `M1`, etc.
3. Convert jobs and operations to `J<job>-O<operation>` rows.
4. Generate a deterministic round-robin earliest-start baseline schedule without downtime.
5. Add fixed machine downtime windows on `M5` and `M0` to create a reproducible disruption.
6. Add benchmark-local customer priority metadata with due dates, order value, and service criticality.
7. Add benchmark-local recovery policy enumerations to make scoring deterministic and machine-verifiable.

Derived files:

- `tasks/orlib-disruption-recovery-control/environment/data/jobshop_instance.csv`
- `tasks/orlib-disruption-recovery-control/environment/data/baseline_schedule.csv`
- `tasks/orlib-disruption-recovery-control/environment/data/machine_downtime.csv`
- `tasks/orlib-disruption-recovery-control/environment/data/customer_priority.csv`
- `tasks/orlib-disruption-recovery-control/environment/data/recovery_policy.json`
