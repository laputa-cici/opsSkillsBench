# Operations Management SkillBench

中文说明见 [README.zh-CN.md](README.zh-CN.md).

This repository is being rebuilt around one core goal: create a `management-operations` SkillBench for studying how external domain skills affect agent performance on deterministic operations-management tasks.

Current focus:

1. Find management-operations skills from external skill markets.
2. Find public operations-management datasets.
3. Construct realistic, machine-verifiable benchmark tasks from those skills and datasets.

The previous synthetic pilot tasks and synthetic skills have been removed from the workspace. The first external-source replenishment task is now treated as a runner smoke test because pilot runs showed it was not skill-sensitive enough for paper-facing evaluation.

## Skill Conditions

| Condition | Meaning |
| --- | --- |
| `no_skill` | Task and raw runtime environment only. |
| `provided_skills` | Benchmark-provided skills, preferably imported or adapted from external skill markets with provenance. |
| `self_created_skills` | No provided skills initially, but the agent may create procedural skills during the run. |

## Task Structure

The benchmark now separates problem domains from individual benchmark items.

- Legacy scenario tasks remain under `tasks/<scenario-task>/` for continuity.
- Scalable atomic tasks live under `tasks/<problem-domain>/<task-id>/`.
- A runnable task is any directory, at any depth under `tasks/`, that contains `task.toml`.

This means a single operations problem domain can contain many independently counted benchmark tasks. For example, `fulfillment` now contains separate tasks for order actions, lane risk registers, and scorecard summaries instead of hiding them as subtests inside one large task.

## Current Problem Domains

| Task | Dataset source | Skill candidates | Status |
| --- | --- | --- | --- |
| `online-retail-replenishment-review` | UCI Online Retail II | `supply-chain-manager` | `runnable_smoke_not_skill_sensitive` |
| `dataco-control-tower-exception-review` | DataCo SMART Supply Chain | `supply-chain-manager`, `logistics-manager`, `operations-manager` | `runnable_external_source` |
| `portland-sourcing-concentration-review` | Open Contracting / City of Portland | `supply-chain-manager`, `operations-manager`, `procurement-review` | `runnable_external_source` |
| `orlib-disruption-recovery-control` | OR-Library Job Shop Scheduling | `capacity-planning`, `operations-manager`, `supply-chain-manager` | `runnable_external_source` |

Current atomic task count:

| Problem domain | Atomic tasks |
| --- | ---: |
| `inventory` | 3 |
| `fulfillment` | 3 |
| `procurement` | 3 |
| `scheduling` | 3 |

Runnable tasks include:

```text
tasks/<task-id>/
├── TASK_DESIGN.md
├── instruction.md
├── source.md
├── task.toml
├── environment/
│   ├── data/
│   └── skills/
├── solution/
│   └── solve.sh
└── tests/
    ├── test.sh
    └── test_outputs.py
```

Nested atomic tasks use the same layout:

```text
tasks/<problem-domain>/<task-id>/
```

## Source Registry

External skill and dataset candidates are tracked in [docs/source-registry.md](docs/source-registry.md).

Skill markets under review:

- SkillsMP
- Agent Skills
- ClawHub
- Claude SkillHub

Datasets under review:

- UCI Online Retail II
- DataCo SMART Supply Chain
- OR-Library Job Shop Scheduling
- Open Contracting Data Registry / City of Portland procurement data

## Local Dependencies

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## Local Smoke Test

The first runnable external-source task can be tested with:

```bash
.venv/bin/python scripts/run_task_local.py dataco-control-tower-exception-review --oracle --test
.venv/bin/python scripts/run_task_local.py fulfillment/dataco-order-risk-actions --oracle --test
```

## Benchmark Model Commands

Use explicit model arguments for reproducibility:

```bash
.venv/bin/python scripts/run_benchmark_local.py --agent codex --model gpt-5.4 --task dataco-control-tower-exception-review --skill-condition provided_skills
.venv/bin/python scripts/run_benchmark_local.py --agent claude --model qwen3.5-plus --task dataco-control-tower-exception-review --skill-condition provided_skills
```

## Next Step

Implement the redesigned skill-sensitive task track:

1. Use `online-retail-replenishment-review` only as a runner smoke test.
2. Add `self_created_skills` evaluation support and rerun the external-source matrix.
3. Decide whether to import an additional `capacity-planning` skill or continue using `operations-manager` for bottleneck reasoning.
4. Score framework taxonomy, operational action mapping, and skill evidence separately from numeric calculations.
