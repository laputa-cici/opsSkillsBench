# Portland Supplier Action Plan

Map category concentration and procurement anti-patterns to supplier actions.

This is an atomic task split from `portland-sourcing-concentration-review`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

- `/app/data/awards.csv`
- `/app/data/supplier_profile.csv`
- `/app/data/category_policy.json`

## Required Outputs

- `/app/output/supplier_action_plan.csv`

## Requirements

1. Write supplier_action_plan.csv sorted by category.
2. Include concentration_flag, anti_pattern, mitigation_code, owner_function, and follow_up.

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
