# Online Retail II Provenance

Status: raw source identified, derived task slice pending.

## Source

- Dataset: Online Retail II
- Publisher: UCI Machine Learning Repository
- URL: https://archive.ics.uci.edu/dataset/502/online+retail+ii
- DOI: `10.24432/C5CG6D`
- License signal: CC BY 4.0 on the UCI dataset page
- Access date: 2026-04-07

## Planned Use

The dataset will be used to derive SKU-level demand history for `tasks/online-retail-replenishment-review`.

Raw files should be stored under `sources/datasets/online-retail-ii/raw/`, which is ignored by git.

Committed task slices should be small CSV fixtures under:

```text
tasks/online-retail-replenishment-review/environment/data/
```

