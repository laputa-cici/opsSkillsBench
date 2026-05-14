# Portland Kraljic Category Matrix

Classify procurement categories into Kraljic quadrants from spend impact and supply risk.

This is an atomic task split from `portland-sourcing-concentration-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/awards.csv`
- `/app/data/supplier_profile.csv`
- `/app/data/category_policy.json`

## Required Outputs

- `/app/output/kraljic_category_matrix.csv`

## Requirements

1. Write kraljic_category_matrix.csv sorted by category.
2. Include spend, top supplier share, impact, risk, quadrant, and sourcing strategy.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
