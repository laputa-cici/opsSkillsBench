# 实验测试矩阵与题目清单

更新日期：2026-06-18

本文整理当前 opsSkillsBench 中可运行题目，并给出后续模型 / agent 测试的推荐分组。当前仓库共有 20 个 runnable task，其中 4 个 legacy scenario task、16 个 atomic task。

## 测试前结论

建议后续测试按三层推进：

1. **环境冒烟层**：先跑少量题确认 agent、模型、权限、输出目录和 verifier 都正常。
2. **当前完整 pilot 层**：跑当前所有 16 个 atomic task，但结果分组汇报，不把 smoke/prototype 直接混入论文主结论。
3. **当前 paper-facing 主分析层**：优先分析 9 个 `runnable_external_source` atomic task，也就是 DataCo / Portland / OR-Library 拆出的外部来源原子题。

当前不建议把 4 个 legacy scenario task 作为主统计题数。它们适合做集成测试、历史兼容和附录分析。

最新本地 oracle 回归：

| 时间 | 命令 | 结果 |
| --- | --- | --- |
| 2026-06-18 | `.venv/bin/python scripts/run_task_local.py --all --oracle --test` | `passed = 20`, `failed = 0` |

结果文件：

```text
.local_results/local-run-20260618T011534Z.json
```

## 任务总览

| 类别 | 数量 | 用途 |
| --- | ---: | --- |
| Legacy scenario task | 4 | 集成测试、历史兼容、冒烟 |
| Atomic task | 16 | 当前主要测试对象 |
| Atomic external-source task | 9 | 当前最适合进入主分析 |
| Atomic prototype task | 4 | 适合 pilot，不宜直接作为 paper-ready 主结论 |
| Atomic smoke task | 3 | 适合 runner smoke，不宜作为 skill-sensitive 主结论 |

## 领域分布

| 问题域 | Atomic 数量 | 当前定位 |
| --- | ---: | --- |
| `inventory` | 3 | smoke，已知不够 skill-sensitive |
| `fulfillment` | 7 | 3 个外部来源题 + 4 个 prototype 题 |
| `procurement` | 3 | 外部来源题，适合主分析 |
| `scheduling` | 3 | 外部来源题，适合主分析 |

## Legacy Scenario Tasks

这些任务保留用于兼容旧实验和端到端集成测试，不建议计入当前 atomic 主统计。

| Task | 状态 | 数据来源 | 建议用途 |
| --- | --- | --- | --- |
| `online-retail-replenishment-review` | `runnable_smoke_not_skill_sensitive` | UCI Online Retail II | runner smoke，不做主分析 |
| `dataco-control-tower-exception-review` | `runnable_external_source` | DataCo SMART Supply Chain | 履约题端到端集成测试 |
| `portland-sourcing-concentration-review` | `runnable_external_source` | Open Contracting / Portland | 采购题端到端集成测试 |
| `orlib-disruption-recovery-control` | `runnable_external_source` | OR-Library Job Shop | 排程题端到端集成测试 |

## Atomic Tasks

### Inventory

当前 inventory 三题来自 `online-retail-replenishment-review`，历史 pilot 显示更像 CSV/规则处理，不够 skill-sensitive。建议只做 smoke 或低优先级分析。

| Task | 状态 | 难度 | 输出 | 测试定位 |
| --- | --- | --- | --- | --- |
| `inventory/online-retail-replenishment-schema` | `runnable_smoke_not_skill_sensitive` | easy | `replenishment_plan.csv` | smoke |
| `inventory/online-retail-replenishment-values` | `runnable_smoke_not_skill_sensitive` | medium | `replenishment_plan.csv` | smoke |
| `inventory/online-retail-exception-register` | `runnable_smoke_not_skill_sensitive` | medium | `replenishment_exceptions.json` | smoke |

### Fulfillment

Fulfillment 当前有 7 个 atomic task。其中 3 个来自 DataCo 外部来源，适合主分析；4 个是 Olist-style prototype，适合 pilot 和后续扩题验证。

| Task | 状态 | 难度 | 输出 | 测试定位 |
| --- | --- | --- | --- | --- |
| `fulfillment/dataco-order-risk-actions` | `runnable_external_source` | hard | `control_tower_actions.csv` | 主分析 |
| `fulfillment/dataco-lane-risk-register` | `runnable_external_source` | medium | `lane_risk_register.json` | 主分析 |
| `fulfillment/dataco-scorecard-summary` | `runnable_external_source` | medium | `scorecard_summary.json` | 主分析 |
| `fulfillment/nearest-feasible-dc` | `runnable_prototype_external_schema` | medium | `warehouse_assignment.csv` | prototype pilot |
| `fulfillment/capacity-aware-allocation` | `runnable_prototype_external_schema` | medium | `capacity_adjusted_assignment.csv` | prototype pilot |
| `fulfillment/sla-risk-estimator` | `runnable_prototype_external_schema` | medium | `sla_risk_register.json` | prototype pilot |
| `fulfillment/split-order-decision` | `runnable_prototype_external_schema` | medium | `split_order_plan.csv` | prototype pilot |

### Procurement

Procurement 三题均来自 Portland / Open Contracting 外部来源，适合进入当前主分析。

| Task | 状态 | 难度 | 输出 | 测试定位 |
| --- | --- | --- | --- | --- |
| `procurement/portland-kraljic-category-matrix` | `runnable_external_source` | hard | `kraljic_category_matrix.csv` | 主分析 |
| `procurement/portland-supplier-action-plan` | `runnable_external_source` | hard | `supplier_action_plan.csv` | 主分析 |
| `procurement/portland-procurement-risk-register` | `runnable_external_source` | hard | `procurement_risk_register.json` | 主分析 |

### Scheduling

Scheduling 三题均来自 OR-Library 外部来源，适合进入当前主分析。

| Task | 状态 | 难度 | 输出 | 测试定位 |
| --- | --- | --- | --- | --- |
| `scheduling/orlib-recovery-schedule` | `runnable_external_source` | hard | `recovery_schedule.csv` | 主分析 |
| `scheduling/orlib-schedule-metrics` | `runnable_external_source` | medium | `schedule_metrics.json` | 主分析 |
| `scheduling/orlib-bottleneck-action-plan` | `runnable_external_source` | hard | `bottleneck_report.json`, `recovery_action_plan.csv` | 主分析 |

## 推荐测试任务集

### Set A: 环境冒烟集

用途：每次换模型、换 agent、换服务器环境时先跑，确认基本链路正常。

| Task | 原因 |
| --- | --- |
| `inventory/online-retail-replenishment-values` | 覆盖 inventory / CSV 数值计算 |
| `fulfillment/dataco-order-risk-actions` | 覆盖 fulfillment / action mapping |
| `fulfillment/nearest-feasible-dc` | 覆盖 prototype data / warehouse allocation |
| `procurement/portland-kraljic-category-matrix` | 覆盖 procurement / taxonomy |
| `scheduling/orlib-recovery-schedule` | 覆盖 scheduling / precedence and capacity |

建议先用 1 个便宜模型 + `provided_skills` 跑 Set A。如果失败，不要扩大矩阵，先修 agent adapter / 文件权限 / prompt。

### Set B: 当前 Atomic Pilot

用途：当前最完整的一轮 agent 测试。包含全部 16 个 atomic task，但输出汇总时按定位拆开分析。

```text
inventory/online-retail-replenishment-schema
inventory/online-retail-replenishment-values
inventory/online-retail-exception-register
fulfillment/dataco-order-risk-actions
fulfillment/dataco-lane-risk-register
fulfillment/dataco-scorecard-summary
fulfillment/nearest-feasible-dc
fulfillment/capacity-aware-allocation
fulfillment/sla-risk-estimator
fulfillment/split-order-decision
procurement/portland-kraljic-category-matrix
procurement/portland-supplier-action-plan
procurement/portland-procurement-risk-register
scheduling/orlib-recovery-schedule
scheduling/orlib-schedule-metrics
scheduling/orlib-bottleneck-action-plan
```

建议汇总标签：

| 标签 | 任务数 | 用途 |
| --- | ---: | --- |
| `main_external_atomic` | 9 | 当前主分析 |
| `prototype_atomic` | 4 | prototype pilot |
| `smoke_atomic` | 3 | runner smoke |

### Set C: 当前主分析集

用途：当前最适合进入报告或论文草稿主图表的题目集合。

```text
fulfillment/dataco-order-risk-actions
fulfillment/dataco-lane-risk-register
fulfillment/dataco-scorecard-summary
procurement/portland-kraljic-category-matrix
procurement/portland-supplier-action-plan
procurement/portland-procurement-risk-register
scheduling/orlib-recovery-schedule
scheduling/orlib-schedule-metrics
scheduling/orlib-bottleneck-action-plan
```

这 9 题都满足：

1. atomic task。
2. `runnable_external_source`。
3. 有确定性 verifier。
4. 不是已知 smoke-not-skill-sensitive 的 inventory 题。

## Skill 条件

建议每个任务至少跑三种条件：

| 条件 | 目的 | 当前建议 |
| --- | --- | --- |
| `no_skill` | baseline | 必跑 |
| `provided_skills` | 测外部 skill 是否提升 | 必跑 |
| `self_created_skills` | 测 agent 自建技能能力 | 第二轮再跑，先确保 adapter 稳定 |

第一轮测试可以先跑：

```text
Set A * provided_skills
```

第二轮再跑：

```text
Set B * no_skill
Set B * provided_skills
```

第三轮稳定后再补：

```text
Set C * self_created_skills
```

## 模型 / Agent 组合

当前建议沿用预算文档中的低成本优先策略：

| 层级 | 模型 / Agent | 用途 |
| --- | --- | --- |
| smoke | DeepSeek 或 Kimi + 当前 agent adapter | 先验证链路 |
| pilot | `gpt-5.5` 或当前 OpenAI 强模型 | 强模型上限 |
| pilot | `Claude Sonnet 4.6` 或当前 Sonnet | Claude Code 主力 |
| pilot | `deepseek-v4-pro` | 低成本强推理 / 代码对照 |
| pilot | `Kimi K2.6` | 长上下文 / 中文对照 |
| extended | `gpt-5.4 mini`, `Claude Opus 4.8`, `deepseek-v4-flash`, `Kimi K2.5` | 第二阶段扩展 |

## 建议执行顺序

### Step 0: Oracle 全量回归

每次正式 agent 测试前先跑：

```bash
.venv/bin/python scripts/run_task_local.py --all --oracle --test
```

通过标准：

```text
passed = 20
failed = 0
```

### Step 1: 单模型冒烟

先用一个低成本模型跑 Set A + `provided_skills`，确认：

1. agent 能读取 task。
2. agent 能写 `/app/output`。
3. verifier 能读到输出。
4. 失败日志可追踪。

### Step 2: 当前 Atomic Pilot

跑 Set B 的两种条件：

```text
no_skill
provided_skills
```

建议先不跑 `self_created_skills`，因为它更容易引入文件系统污染、技能复用路径、重复运行隔离等问题。

### Step 3: 主分析补测

对 Set C 跑：

```text
no_skill
provided_skills
self_created_skills
```

每个模型至少 1 次 repeat；当任务数扩大到 50+ 后再做 3 次 repeat。

## 结果汇总建议

结果表至少保留以下字段：

| 字段 | 说明 |
| --- | --- |
| `task` | 任务名 |
| `task_set` | `smoke`, `atomic_pilot`, `main_external_atomic`, `prototype_atomic` |
| `problem_domain` | inventory / fulfillment / procurement / scheduling |
| `status_group` | external / prototype / smoke |
| `agent` | codex / claude / kimi / deepseek adapter |
| `model` | 模型名 |
| `skill_condition` | no_skill / provided_skills / self_created_skills |
| `repeat_index` | 第几次重复 |
| `passed` | verifier 是否通过 |
| `error_type` | schema / calculation / missing_output / timeout / agent_error |
| `prompt_tokens` | 如果 provider 可返回则记录 |
| `completion_tokens` | 如果 provider 可返回则记录 |
| `estimated_cost_usd` | 可后处理计算 |

## 当前不足

1. 当前 atomic task 只有 16 个，离 100 题目标还比较远。
2. Inventory 目前主要是 smoke，不适合主分析，需要新增更 skill-sensitive 的库存题。
3. Fulfillment 的 4 个新增题仍是 prototype schema，需要后续替换或补充真实外部数据切片。
4. `self_created_skills` 测试前需要确认 agent 运行目录隔离，否则可能跨任务污染。
5. 需要在 benchmark runner 结果中正式记录 token 和模型版本，便于后续费用与稳定性分析。
