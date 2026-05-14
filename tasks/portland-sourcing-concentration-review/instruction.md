# Portland Sourcing Concentration Review

You are preparing a sourcing concentration review for a public-sector operations team.

Read the runtime input files:

- `/app/data/awards.csv`
- `/app/data/supplier_profile.csv`
- `/app/data/category_policy.json`

Create:

- `/app/output/kraljic_category_matrix.csv`
- `/app/output/supplier_action_plan.csv`
- `/app/output/procurement_risk_register.json`

The outputs should combine deterministic spend aggregation with framework-driven sourcing decisions. They should include Kraljic quadrant, sourcing strategy, procurement anti-pattern, mitigation code, owner function, and escalation level, while keeping all output values inside the allowed taxonomy in `category_policy.json`.

## Required Category Matrix

`kraljic_category_matrix.csv` must contain one row per category, sorted by category name, with these columns:

```text
category
total_spend
top_supplier
top_supplier_share
spend_impact
supply_risk
kraljic_quadrant
sourcing_strategy
```

Rules:

1. `total_spend` is the sum of `award_value` for the category.
2. `top_supplier` is the supplier with the highest spend in the category; ties sort by supplier name ascending.
3. `top_supplier_share = top_supplier_spend / total_spend`, rounded to three decimals.
4. `spend_impact = high` if `total_spend >= spend_impact_threshold`, otherwise `low`.
5. `supply_risk = high` if `criticality_score >= high_supply_risk_criticality` or `competition_flag = limited_competition`, otherwise `low`.
6. `kraljic_quadrant` and `sourcing_strategy` must stay within the allowed taxonomy in `category_policy.json`.

## Required Supplier Action Plan

`supplier_action_plan.csv` must contain one row per category/top supplier, sorted by category name, with these columns:

```text
category
supplier
concentration_flag
anti_pattern
mitigation_code
owner_function
follow_up
```

Rules:

1. `concentration_flag = high` when `top_supplier_share >= high_concentration_share`, otherwise `normal`.
2. `anti_pattern`, `mitigation_code`, `owner_function`, and `follow_up` must use the procurement taxonomy in `category_policy.json`.

## Required Risk Register

`procurement_risk_register.json` must contain:

```json
{
  "risk_count": 0,
  "risks": []
}
```

Include one risk for every category where `anti_pattern != none`. Sort by `escalation_level`, then category. Each object must include:

```text
category
supplier
anti_pattern
mitigation_code
escalation_level
evidence
```

`escalation_level` must remain inside the allowed policy taxonomy. `evidence` must be `top_supplier_share=<share>` using the three-decimal share.
