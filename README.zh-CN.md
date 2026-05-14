# Operations Management SkillBench（中文版）

本仓库现在聚焦一个核心目标：构建面向 `management-operations` 领域的 SkillBench，用于研究大语言模型与 agent 框架在真实管理运营任务上的表现。

核心研究问题：

```text
领域技能（skills）到底能在多大程度上提升 agent 完成确定性运营任务的能力？
当没有现成技能时，agent 又能否自行创建并复用有效技能？
```

## 当前状态

截至 `2026-04-08`：

- 旧的 synthetic pilot 任务、synthetic skills 和本地运行产物已经从工作空间中清理。
- 当前 `online-retail-replenishment-review` 已经跑通过 agent 测试链路，但四次 pilot 表明它主要是在测 CSV 处理，不适合作为论文里的 skill-sensitive 主任务。
- 当前重点是三件事：找外部 skill、找运营数据集、基于它们构造可验证任务。
- 外部技能与数据集候选记录在 [docs/source-registry.md](docs/source-registry.md)。
- 任务重设计结论见 [docs/task-redesign-after-pilot.md](docs/task-redesign-after-pilot.md)。
- 当前任务中文总览见 [docs/task-catalog.zh-CN.md](docs/task-catalog.zh-CN.md)。

## 研究设计

每个系统都应在三种 skill 条件下评测：

| 条件 | 含义 |
| --- | --- |
| `no_skill` | 只提供任务说明和原始环境，不提供预置技能。 |
| `provided_skills` | 提供 benchmark 内置领域技能，优先来自外部技能市场并保留 provenance。 |
| `self_created_skills` | 不提供预置技能，但允许 agent 在执行前或执行中自行创建技能。 |

计划比较的 agent / framework 包括：

- `Codex`
- `Claude Code`
- `OpenClaw`
- 后续可扩展到其他 agent 框架

## 当前任务队列

| 任务 | 数据集来源 | 外部 skill 候选 | 状态 |
| --- | --- | --- | --- |
| `online-retail-replenishment-review` | UCI Online Retail II | `supply-chain-manager` | `runnable_smoke_not_skill_sensitive` |
| `dataco-control-tower-exception-review` | DataCo SMART Supply Chain | `supply-chain-manager`, `logistics-manager`, `operations-manager` | `runnable_external_source` |
| `portland-sourcing-concentration-review` | Open Contracting / City of Portland | `supply-chain-manager`, `operations-manager`, `procurement-review` | `runnable_external_source` |
| `orlib-disruption-recovery-control` | OR-Library Job Shop Scheduling | `capacity-planning`, `operations-manager`, `supply-chain-manager` | `runnable_external_source` |

可运行任务目录格式：

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

## 外部来源

主要 skill marketplace 候选：

- SkillsMP
- Agent Skills
- ClawHub
- Claude SkillHub

主要 dataset 候选：

- UCI Online Retail II
- DataCo SMART Supply Chain
- OR-Library Job Shop Scheduling
- Open Contracting Data Registry / City of Portland procurement data

详细候选、导入优先级和注意事项见 [docs/source-registry.md](docs/source-registry.md)。

## 本地依赖

```bash
.venv/bin/python -m pip install -r requirements.txt
```

## 工作区结构

```text
opsSkillsBench-main/
├── docs/
│   ├── management-operations-skillbench-plan.md
│   ├── paper-outline.md
│   └── source-registry.md
├── sources/
│   ├── datasets/
│   └── skills/
├── scripts/
│   ├── adapters/
│   ├── preprocess/
│   ├── run_benchmark_local.py
│   └── run_task_local.py
└── tasks/
```

## 本地冒烟测试

第一个论文主任务方向的外部来源任务可以这样测试：

```bash
.venv/bin/python scripts/run_task_local.py dataco-control-tower-exception-review --oracle --test
```

## Benchmark 模型参数

为了实验可复现，后续运行都显式传模型名：

```bash
.venv/bin/python scripts/run_benchmark_local.py --agent codex --model gpt-5.4 --task dataco-control-tower-exception-review --skill-condition provided_skills
.venv/bin/python scripts/run_benchmark_local.py --agent claude --model qwen3.5-plus --task dataco-control-tower-exception-review --skill-condition provided_skills
```

## 下一步

1. 把 `online-retail-replenishment-review` 只作为 runner 冒烟测试保留。
2. 补齐 `self_created_skills` 条件的运行链路和文件系统隔离。
3. 对已升级为外部来源的任务重新运行正式评测矩阵。
4. 决定是否继续导入额外的 `capacity-planning` skill，或先用 `operations-manager` 覆盖瓶颈/约束推理。
5. 测试拆分为数值正确性、框架分类、运营动作映射和 skill evidence 四类，避免任务再次退化成单纯脚本题。
