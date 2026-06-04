# 大模型与 Agent 测试 Token 估算

更新日期：2026-06-04

本文估算 opsSkillsBench 后续开发与实验评测需要覆盖的 Agent / 大模型组合，以及大致 token 用量。估算目标是先给项目排期、预算和实验矩阵一个可执行基线；正式跑论文实验前，还需要按当时 provider 官方价格页和可用模型名重新冻结一次配置。

参考入口：

- OpenAI models: https://platform.openai.com/docs/models
- OpenAI Codex: https://developers.openai.com/codex/
- Anthropic Claude Code: https://docs.anthropic.com/en/docs/claude-code/overview
- Google Gemini CLI: https://github.com/google-gemini/gemini-cli
- Qwen Code: https://github.com/QwenLM/qwen-code

## 当前任务规模

截至本文件更新时，仓库中有 20 个可被 runner 发现的任务：

| 类型 | 数量 | 说明 |
| --- | ---: | --- |
| legacy scenario task | 4 | 保留用于兼容历史实验和集成冒烟 |
| atomic task | 16 | 正式扩展方向，后续论文实验应以这些题为主 |

当前 atomic task 分布：

| 问题域 | 原子题数量 |
| --- | ---: |
| inventory | 3 |
| fulfillment | 7 |
| procurement | 3 |
| scheduling | 3 |

## 评测条件

每个 Agent / 模型组合建议在三种 skill 条件下运行：

| 条件 | 用途 | 预计 token 特征 |
| --- | --- | --- |
| `no_skill` | 测 baseline，没有领域技能帮助时模型能否靠任务说明完成 | 输入较低，失败重试可能较多 |
| `provided_skills` | 测 benchmark 预置外部 skill 是否提升表现 | 输入较高，因为会读 skill 文件 |
| `self_created_skills` | 测 agent 自建技能、沉淀流程、复用经验的能力 | 首轮输出较高，跨题复用后输入可下降 |

## Agent 与模型分层

建议把模型分成三层，而不是一次性铺满所有 provider。

| 层级 | 推荐用途 | Agent / 模型示例 | 备注 |
| --- | --- | --- | --- |
| A. 主实验层 | 论文主结果，优先保证能力上限 | Codex + GPT 系列强模型；Claude Code + Claude Sonnet/Opus 系列；Claude Code + `qwen3.5-plus`（沿用历史配置） | 每题至少 3 次重复，统计稳定性 |
| B. 成本对照层 | 验证技能是否能帮助中等模型追近强模型 | Codex + 经济 GPT 模型；Gemini CLI + Gemini Flash/Pro；Qwen Code + Qwen 系列 | 先跑 1 次或 2 次，表现好再扩 |
| C. 开发冒烟层 | 题目开发、CI、快速回归 | 本地 oracle；Codex/Claude/Gemini 任一低成本模型 | 主要检查 harness、文件权限、输出格式 |

第一阶段建议不要把所有模型都跑满。更稳的路线是：

1. 当前 20 题做一个小规模 sanity matrix。
2. 扩到 50 个 atomic task 后做一次中期 pilot。
3. 扩到 100 个 atomic task 后再跑完整论文矩阵。

## 单次运行 Token 假设

下面是按当前任务结构估算的单个 task-run 用量。这里的 task-run 指一个 Agent 在一个任务、一个 skill 条件、一次重复中的完整执行。

| 条件 | 输入 token/次 | 输出 token/次 | 合计 token/次 | 说明 |
| --- | ---: | ---: | ---: | --- |
| `no_skill` | 20k-45k | 3k-8k | 25k-55k | 读任务说明、数据、少量脚本和输出 |
| `provided_skills` | 45k-90k | 4k-10k | 50k-100k | 额外读取 1-3 个 skill，部分 Agent 会反复读取 |
| `self_created_skills` | 55k-110k | 8k-20k | 65k-130k | 包含创建/更新 skill 的思考和文件写入 |

为了预算保守，本文统一采用平均值：

| 条件 | 预算均值 |
| --- | ---: |
| `no_skill` | 40k token/次 |
| `provided_skills` | 75k token/次 |
| `self_created_skills` | 95k token/次 |
| 三条件平均 | 70k token/次 |

## 当前 20 题测试预算

### 最小 sanity matrix

用途：确认 runner、任务输出、Agent 权限和三种 skill 条件都能跑通。

配置：

- 20 个任务
- 2 个 Agent
- 1 个模型层
- 3 个 skill 条件
- 1 次重复

计算：

```text
20 tasks * 2 agents * 1 model layer * 3 skill conditions * 1 repeat = 120 runs
120 runs * 70k token/run ~= 8.4M token
```

建议预算：约 8M-12M token。

### 当前任务 pilot matrix

用途：在现在的 20 题规模上初步比较 Agent / 模型差异。

配置：

- 20 个任务
- 2 个 Agent
- 2 个模型层
- 3 个 skill 条件
- 3 次重复

计算：

```text
20 tasks * 2 agents * 2 model layers * 3 skill conditions * 3 repeats = 720 runs
720 runs * 70k token/run ~= 50.4M token
```

建议预算：约 45M-65M token。

## 100 题完整实验预算

目标规模：100 个 atomic task。legacy scenario task 只作为冒烟或附录，不进入主统计。

### 论文主矩阵

配置：

- 100 个 atomic task
- 3 个 Agent
- 2 个模型层
- 3 个 skill 条件
- 3 次重复

计算：

```text
100 tasks * 3 agents * 2 model layers * 3 skill conditions * 3 repeats = 5,400 runs
5,400 runs * 70k token/run ~= 378M token
```

建议预算：约 320M-450M token。

### 更完整的扩展矩阵

如果加入第 3 个模型层或更多 provider：

```text
100 tasks * 4 agents * 3 model layers * 3 skill conditions * 3 repeats = 10,800 runs
10,800 runs * 70k token/run ~= 756M token
```

建议预算：约 650M-900M token。这个规模适合在任务冻结、verifier 稳定后再跑。

## 开发新增题 Token 预算

新增一个可运行 atomic task 通常包括：题目设计、数据切片、标准答案、pytest verifier、文档、oracle 回归、至少一次 Agent 试跑。按现在项目节奏估算：

| 工作项 | token/题 |
| --- | ---: |
| 题目设计与数据 schema | 20k-50k |
| 生成/修改代码、oracle、测试 | 50k-120k |
| 调试 verifier 与文档 | 20k-60k |
| Agent 试跑与修正 | 30k-100k |
| 合计 | 120k-330k |

如果目标从 16 个 atomic task 扩到 100 个，还需要新增约 84 个 atomic task：

```text
84 tasks * 120k-330k token/task ~= 10M-28M development token
```

建议开发预算：约 12M-35M token，另留 20% buffer 给重构、失败试跑和文档同步。

## 总预算建议

| 阶段 | 目标 | 估算 token |
| --- | --- | ---: |
| 当前 sanity matrix | 20 题、2 Agent、1 模型层、1 repeat | 8M-12M |
| 当前 pilot matrix | 20 题、2 Agent、2 模型层、3 repeats | 45M-65M |
| 扩题开发 | 从 16 atomic 扩到 100 atomic | 12M-35M |
| 100 题主实验 | 100 atomic、3 Agent、2 模型层、3 repeats | 320M-450M |
| 100 题扩展实验 | 100 atomic、4 Agent、3 模型层、3 repeats | 650M-900M |

实际执行建议：

1. 先预留 20M token 做当前任务 sanity + 小规模 pilot。
2. 扩题阶段每新增 10-15 题做一次 oracle 全量回归，不要频繁跑完整 Agent matrix。
3. 50 题时跑一次中期 pilot，确认题目确实 skill-sensitive。
4. 100 题冻结后再一次性跑正式矩阵。

## 降本策略

1. 开发阶段主要跑 oracle 和低成本模型，不用强模型反复调题。
2. 每个新题先只跑 `provided_skills` 和 `no_skill`，确认 skill-sensitive 后再加入 `self_created_skills`。
3. legacy scenario task 不进入主实验矩阵，只在 runner 或集成变更后冒烟。
4. 对失败任务先做一次自动重跑；如果还是失败，再人工看日志，避免把格式错误误判为能力问题。
5. 对同一 Agent 的 skill 文件读取做缓存或 prompt 压缩，尤其是 `provided_skills` 条件。
6. 正式实验前冻结模型名、Agent 版本、runner commit、task manifest 和 provider 价格页日期。

## 后续落地清单

1. 在 `scripts/run_benchmark_local.py` 的结果 JSON 中记录 `agent_version`、`model`、`skill_condition`、`repeat_index`、`prompt_token_estimate`、`completion_token_estimate`。
2. 增加一个 `docs/experiment-matrix.zh-CN.md`，把正式实验的任务列表和模型列表冻结下来。
3. 给每个 task 增加 `paper_ready = false/true` 或等价字段，避免 prototype 题误入正式主实验。
4. 扩题优先级继续按 `docs/atomic-task-backlog.zh-CN.md` 推进，先补 inventory/procurement/scheduling，让四个问题域更均衡。
