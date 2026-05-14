# Task Queue

The old synthetic pilot tasks have been removed. This directory now contains external-source task designs only.

Task status values:

| Status | Meaning |
| --- | --- |
| `design_external_source` | Task is designed around external skills and datasets, but data slices/tests are not committed yet. |
| `runnable_prototype_external_schema` | Task has data, oracle, and tests, but the committed slice is a compact prototype matching an external-source schema rather than a verified raw-data derivation. |
| `runnable_external_source` | Task has data, oracle, tests, and provenance. |
| `runnable_smoke_not_skill_sensitive` | Task is runnable and useful for runner smoke tests, but pilot runs showed it is not suitable as a paper-facing skill benchmark. |
| `frozen` | Task is ready for paper experiments. |

Current queue:

| Task | Status | Dataset | Skill candidates |
| --- | --- | --- | --- |
| `online-retail-replenishment-review` | `runnable_smoke_not_skill_sensitive` | UCI Online Retail II | `supply-chain-manager` |
| `dataco-control-tower-exception-review` | `runnable_prototype_external_schema` | DataCo SMART Supply Chain | `supply-chain-manager`, `logistics-manager`, `operations-manager` |
| `portland-sourcing-concentration-review` | `runnable_prototype_external_schema` | Open Contracting / City of Portland | `supply-chain-manager`, `operations-manager`, `procurement-review` |
| `orlib-disruption-recovery-control` | `runnable_prototype_external_schema` | OR-Library Job Shop Scheduling | `capacity-planning`, `operations-manager`, `supply-chain-manager` |
