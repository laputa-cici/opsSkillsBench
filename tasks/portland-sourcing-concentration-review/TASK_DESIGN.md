# Task Design: Portland Sourcing Concentration Review

## Goal

Evaluate whether agents can turn public procurement records into a deterministic sourcing strategy and supplier-risk review.

The task should not stop at spend aggregation. It should require the agent to apply sourcing frameworks such as the Kraljic matrix, concentration risk, supplier strategy, and procurement anti-patterns.

## Public Source Basis

| Source type | Planned source |
| --- | --- |
| Dataset | City of Portland procurement data via Open Contracting Data Registry |
| Primary skill | `supply-chain-manager` |
| Additional skill candidates | `operations-manager`, future `procurement-review` if a licensable public skill is found |

## Planned Inputs

| File | Description |
| --- | --- |
| `awards.csv` | Open Contracting-derived supplier, category, award date, bureau, contract type, and award value fields. |
| `supplier_profile.csv` | Derived supplier count, incumbency, bureau exposure, and category coverage fields. |
| `category_policy.json` | Frozen thresholds for spend impact, supply risk, concentration, and strategy mapping. |

## Planned Outputs

| File | Description |
| --- | --- |
| `kraljic_category_matrix.csv` | Category-level spend impact, supply risk, Kraljic quadrant, and sourcing strategy. |
| `supplier_action_plan.csv` | Supplier/category action plan with consolidation flag, bid strategy, owner function, and follow-up. |
| `procurement_risk_register.json` | Exception list with anti-pattern, mitigation code, evidence, and escalation level. |

## Deterministic Scoring Ideas

- Spend aggregation by supplier/category is exact.
- Concentration percentages round according to frozen rules.
- `kraljic_quadrant` must match frozen spend-impact and supply-risk rules.
- `sourcing_strategy` must match the quadrant:
  - strategic: `partnership_development`
  - leverage: `competitive_bidding`
  - bottleneck: `ensure_supply_and_buffer`
  - non_critical: `process_efficiency`
- `anti_pattern` must match deterministic supplier concentration and award history conditions, such as `single_sourcing`, `price_only_focus`, or `supplier_fragmentation`.
- Output order follows specified ranking by risk severity, category spend, and supplier name.

## Expected Skill Effect

`provided_skills` should improve the mapping from procurement metrics to sourcing strategy. `no_skill` may aggregate spend correctly, but should be less reliable on Kraljic quadrant strategy and mitigation taxonomy.
