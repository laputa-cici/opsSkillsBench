# Portland Procurement Risk Register

Create a procurement risk register for non-empty sourcing anti-patterns.

This is an atomic task split from `portland-sourcing-concentration-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/awards.csv`
- `/app/data/supplier_profile.csv`
- `/app/data/category_policy.json`

## Required Outputs

- `/app/output/procurement_risk_register.json`

## Requirements

1. Write procurement_risk_register.json with risk_count and sorted risks.
2. Evidence must use top_supplier_share=<share> with three decimals.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
