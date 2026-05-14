# 清理任务内 Skill 泄露后的矩阵记录

运行日期：`2026-04-15`

## 范围说明

本轮测试发生在以下修改之后：

1. 三个主任务的 `instruction.md` 中不再出现“使用 provided skills”之类的表述。
2. 三个主任务的正式输出中移除了 `skill_framework` 字段。
3. 三个主任务的 policy JSON 中移除了直接暴露 skill 名称的 framework 列表。

重要说明：

- 本轮 run 发生时，`no_skill` prompt 仍包含 runner 追加的 `Skill condition` 段。
- 之后 runner 已进一步修改：`no_skill` 情况下不再追加任何 skill 相关提示。
- 因此本文件记录的是“任务定义已清理，但 runner no-skill 提示尚未最终清理”的中间版本结果。

## 结果矩阵

| Agent | Skill 条件 | DataCo | Portland | OR-Library |
| --- | --- | --- | --- | --- |
| Codex `gpt-5.4` | `provided_skills` | failed `2/3` | passed `3/3` | passed `3/3` |
| Codex `gpt-5.4` | `no_skill` | failed `2/3` | failed `1/3` | failed `2/3` |
| Claude Code `qwen3.5-plus` | `provided_skills` | failed `1/3` | failed `0/3` | failed `2/3` |
| Claude Code `qwen3.5-plus` | `no_skill` | failed `2/3` | failed `0/3` | failed `2/3` |

## Run 目录

| Agent | Skill | 任务 | Run |
| --- | --- | --- | --- |
| Codex | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-provided_skills-20260415T043553Z` |
| Codex | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-no_skill-20260415T043854Z` |
| Claude Code | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-provided_skills-20260415T044156Z` |
| Claude Code | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-no_skill-20260415T044455Z` |
| Codex | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-provided_skills-20260415T044917Z` |
| Codex | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-no_skill-20260415T045232Z` |
| Claude Code | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-provided_skills-20260415T045531Z` |
| Claude Code | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-no_skill-20260415T045645Z` |
| Codex | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-provided_skills-20260415T045834Z` |
| Codex | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-no_skill-20260415T050149Z` |
| Claude Code | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-provided_skills-20260415T050459Z` |
| Claude Code | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-no_skill-20260415T050645Z` |

## 主要观察

### 1. `no_skill` 的任务内污染明显降低

本轮已经移除了三个主要泄露源：

- instruction 中的 skill 提示语
- 输出字段中的 `skill_framework`
- policy JSON 中的 skill framework 名称

因此本轮失败不再主要来自“agent 直接复述 skill 名称”，而是更集中在：

- 枚举字段精确性
- 专业分类判断
- 数值字符串格式
- 自然语言解释替代 frozen taxonomy

### 2. Portland 仍然是最有希望的 skill-sensitive 主任务

Codex 在 Portland 上表现出清晰差异：

- `provided_skills`: `3/3`
- `no_skill`: `1/3`

这说明在任务内 skill 泄露被清理后，Portland 仍然保留了较好的 skill-sensitive 特征。

主要差异集中在：

- `anti_pattern`
- `mitigation_code`
- `owner_function`
- `follow_up`
- `procurement_risk_register.json`

### 3. DataCo 仍需要重新校准 taxonomy 边界

DataCo 没有形成稳定的正向 skill gap：

- Codex 两种条件都是 `2/3`
- Claude Code 的 `provided_skills` 反而低于 `no_skill`

失败主要集中在：

- `reason_code` 被自由命名，例如 `delivery_delay`、`elevated_risk`
- `value_at_risk` 输出为 `10.0` 而不是 `10`
- lane risk 的 `decision_hierarchy` 偏向 `service` 而不是 frozen taxonomy 中的 `resilience`

这说明 DataCo 当前不是单纯“缺少 skill”，而是 frozen taxonomy 与自然控制塔语言之间仍有冲突。

### 4. OR-Library 对 Codex 开始出现差异

OR-Library 在 Codex 上从之前两种条件都能通过，变成：

- `provided_skills`: `3/3`
- `no_skill`: `2/3`

失败集中在 `bottleneck_report.json`：

- `root_cause` 写成 `M5_load_downtime_constraint`
- `decision_hierarchy` 写成 `cost_efficiency`

Claude Code 在两种条件下均为 `2/3`，仍然会把：

- `root_cause` 写成自然语言
- `decision_hierarchy` 写成列表

## 本轮结论

本轮修改是有效的，主要价值不是提高整体通过率，而是让比较条件更干净：

1. `no_skill` 不再被任务输出 schema 和 policy 文件直接污染。
2. Portland 的 skill-sensitive 特征依然保留。
3. OR-Library 对 Codex 开始出现更清楚的 skill 差异。
4. DataCo 暴露出 taxonomy 设计需要进一步校准，而不是继续简单增删 skill 提示。

## 后续注意

本轮之后，runner 又做了一项重要改动：

- `no_skill` prompt 不再追加 `Skill condition` 段。
- 不再写 `Do not use any prebuilt task skill files.`
- 不再写 `Solve the task directly from the instruction and data only.`

因此，如果后续要作为正式论文结果，应基于 runner 最新版本重新跑矩阵。
