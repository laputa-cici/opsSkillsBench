# Portland Kraljic Category Matrix

This atomic task belongs to the `procurement` problem domain.

Parent task: `portland-sourcing-concentration-review`

## Purpose

Classify procurement categories into Kraljic quadrants from spend impact and supply risk.

The task turns one previously nested verifier checkpoint into a standalone benchmark item, so benchmark reports count it as an individual task instead of a hidden sub-question inside a larger scenario.

## Checked Outputs

- `/app/output/kraljic_category_matrix.csv`

## Skill Sensitivity

The task keeps the parent task's external-source data and skill candidates, while narrowing the required output to a single operational decision surface. This makes it easier to scale the benchmark to many independent items and to analyze which decision surfaces benefit from provided skills.
