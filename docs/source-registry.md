# External Source Registry

Last updated: 2026-06-04

This is the active registry for building a `management-operations` SkillBench from external skill markets and public operations datasets. The old synthetic pilot tasks have been removed from `tasks/`.

## Skill Market Candidates

Only vendor a skill after checking the upstream package and license. Marketplace snippets are discovery signals, not sufficient provenance by themselves.

| Priority | Candidate | Market / source | Operations fit | Current decision |
| --- | --- | --- | --- | --- |
| P0 | `supply-chain-manager` | SkillsMP, `theneoai/awesome-skills` listing: https://skillsmp.com/skills/theneoai-awesome-skills-skills-manufacturing-supply-chain-manager-skill-md | Manufacturing supply chain, procurement, logistics, inventory, supplier relationship management. | Vendored to `sources/skills/supply-chain-manager` from upstream commit `10d1e09e3907265e38ab1e9c3d6e38efd6a41611`; license is MIT with attribution requirement. |
| P0 | `logistics-manager` | SkillsMP, `theneoai/awesome-skills` listing: https://skillsmp.com/skills/theneoai-awesome-skills-skills-transportation-logistics-manager-skill-md | Transportation management, warehouse operations, 3PL management, logistics cost/service tradeoffs, network optimization. | Vendored `SKILL.md` to `sources/skills/logistics-manager` from upstream commit `10d1e09e3907265e38ab1e9c3d6e38efd6a41611`; license is MIT with attribution requirement. |
| P0 | `operations-manager` | SkillsMP, `theneoai/awesome-skills` listing: https://skillsmp.com/skills/theneoai-awesome-skills-skills-business-operations-manager-skill-md | Process optimization, lean operations, KPI management, operational excellence, workflow design. | Vendored `SKILL.md` to `sources/skills/operations-manager` from upstream commit `10d1e09e3907265e38ab1e9c3d6e38efd6a41611`; license is MIT with attribution requirement. |
| P0 | `operations` | Agent Skills listing: https://agent-skills.md/skills/travisjneuman/.claude/operations | Broad operations excellence, process improvement, supply chain KPIs, vendor management, capacity. | Keep as secondary candidate; verify upstream license before import. |
| P1 | `afrexai-warehouse-ops` | ClawHub listing: https://www.clawhub-skills.com/skills/afrexai-warehouse-ops | Warehouse layout, labor, pick efficiency, inventory accuracy, safety, automation ROI. | Use for warehouse task track after license verification. |
| P1 | `operations-manager-alt` | Agent Skills listing: https://agent-skills.md/skills/borghei/claude-skills/operations-manager | Process optimization, workflow design, resource planning, vendor management. | Alternate source for operations-manager-style skill; verify upstream before import. |
| P1 | `capacity-planning` | Agent Skills / prompt-skill listing from prior screening | Capacity planning, bottleneck analysis, resource allocation. | Use for capacity and scheduling track if package is accessible. |
| P1 | `procurement-review` | SkillsMP candidate from prior screening | Procurement review, P2P workflow audit, vendor governance. | Use for procurement audit track after license verification. |
| P2 | `demand-forecasting` | Claude SkillHub listing: https://claudeskillhub.com/skills/demand-forecasting/examples/seasonal-outdoor-grills | Demand forecasting, inventory optimization, reorder planning. | Do not vendor from examples alone; locate package/upstream first. |
| P2 | `supplier-research` | Claude SkillHub listing: https://claudeskillhub.com/skills/supplier-research/examples/plastic-injection-molding-budget | Supplier comparison, sourcing matrix, lead-time and cost tradeoffs. | Do not vendor from examples alone; locate package/upstream first. |

## Dataset Candidates

| Priority | Dataset | Source | Operations fit | Current decision |
| --- | --- | --- | --- | --- |
| P0 | Online Retail II | UCI Machine Learning Repository: https://archive.ics.uci.edu/dataset/502/online+retail+ii | Transaction history for demand, replenishment, SKU prioritization, stockout-risk scenarios. | Imported raw file locally under ignored `sources/datasets/online-retail-ii/raw/`; committed derived slice for `online-retail-replenishment-review`. |
| P0 | DataCo SMART Supply Chain | Mendeley Data: https://data.mendeley.com/datasets/8gx2fvg2k6/5 | Supply-chain orders, sales, distribution, logistics exceptions, late delivery risk. | Imported raw CSV locally under ignored `sources/datasets/dataco-smart-supply-chain/raw/`; committed derived slice for `dataco-control-tower-exception-review`. |
| P0 | OR-Library Job Shop Scheduling | OR-Library: https://people.brunel.ac.uk/~mastjjb/jeb/orlib/jobshopinfo.html | Classic job-shop scheduling instances for machine-verifiable capacity and schedule repair tasks. | Imported `jobshop1.txt` locally under ignored `sources/datasets/orlib-jobshop/raw/`; committed derived `ft06` slice for `orlib-disruption-recovery-control`. |
| P1 | Open Contracting Data Registry | https://data.open-contracting.org/ | Public procurement, contracting, supplier concentration, award anomalies. | Use after selecting a specific publisher dataset. |
| P1 | City of Portland procurement dataset | Open Contracting registry publication: https://data.open-contracting.org/en/publication/155 | Purchases/contracts since 2015, supplier concentration and purchasing audit. | Imported all-time CSV package locally under ignored `sources/datasets/portland-procurement/raw/`; committed derived slice for `portland-sourcing-concentration-review`. |
| P1 | Brazilian E-Commerce Public Dataset by Olist | Kaggle listing: https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce | Orders, fulfillment timing, sellers, customers, products, and logistics SLA analysis. | Candidate source for expanding fulfillment allocation tasks beyond the committed prototype slice. |
| P1 | Instacart Market Basket Analysis | Kaggle listing: https://www.kaggle.com/c/instacart-market-basket-analysis | Order baskets, SKU demand patterns, substitutions, picking and replenishment variants. | Candidate source for inventory/fulfillment variants; verify license and raw-data access before import. |
| P2 | Prototype Olist-style fulfillment slice | Committed task data only | Warehouse inventory, capacity, transit, SLA and split-order decisions matching public e-commerce fulfillment schemas. | Committed compact prototype slice for `fulfillment/nearest-feasible-dc`, `fulfillment/capacity-aware-allocation`, `fulfillment/sla-risk-estimator`, and `fulfillment/split-order-decision`; replace or supplement with verified public-data slices before paper freeze. |

## Import Rules

1. Keep raw large datasets out of git unless they are tiny and clearly licensed.
2. Commit only deterministic task slices in `tasks/<task-id>/environment/data/`.
3. Store preprocessing scripts under `scripts/preprocess/`.
4. Every runnable task must include `source.md` with source URL, access date, license signal, transformations, and skill provenance.
5. Every provided skill must be either `external_unmodified` or `adapted_from_external`; synthetic distractors must be explicitly labeled as synthetic.
6. Do not use a marketplace page alone as the source for a skill unless it exposes the full skill content and license.
