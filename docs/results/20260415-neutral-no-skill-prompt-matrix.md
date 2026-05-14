# Neutral No-Skill Prompt 矩阵记录

运行日期：`2026-04-15`

## 范围说明

本轮测试发生在以下修改之后：

1. 三个主任务的 `instruction.md` 中不再出现 skill 相关提示。
2. 三个主任务输出中不再包含 `skill_framework` 字段。
3. 三个主任务的 policy JSON 中不再包含显式 skill framework 名称。
4. `no_skill` prompt 不再追加任何 skill 相关文字。

也就是说，`no_skill` prompt 不再包含：

```text
Skill condition:
Do not use any prebuilt task skill files.
Solve the task directly from the instruction and data only.
```

该条件下，agent 只收到任务说明、runtime data 路径、runtime output 路径和通用输出要求。

## 结果矩阵

| Agent | Skill 条件 | DataCo | Portland | OR-Library |
| --- | --- | --- | --- | --- |
| Codex `gpt-5.4` | `provided_skills` | failed `2/3` | passed `3/3` | failed `2/3` |
| Codex `gpt-5.4` | `no_skill` | failed `2/3` | passed `3/3` | failed `2/3` |
| Claude Code `qwen3.5-plus` | `provided_skills` | failed `1/3` | failed `0/3` | failed `1/3` |
| Claude Code `qwen3.5-plus` | `no_skill` | failed `1/3` | failed `0/3` | failed `2/3` |

## Run 目录

| Agent | Skill | 任务 | Run |
| --- | --- | --- | --- |
| Codex | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-provided_skills-20260415T065719Z` |
| Codex | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-no_skill-20260415T070035Z` |
| Claude Code | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-provided_skills-20260415T070417Z` |
| Claude Code | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-no_skill-20260415T070610Z` |
| Codex | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-provided_skills-20260415T070756Z` |
| Codex | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-no_skill-20260415T071126Z` |
| Claude Code | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-provided_skills-20260415T071453Z` |
| Claude Code | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-no_skill-20260415T071910Z` |
| Codex | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-provided_skills-20260415T072524Z` |
| Codex | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-no_skill-20260415T072936Z` |
| Claude Code | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-provided_skills-20260415T073308Z` |
| Claude Code | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-no_skill-20260415T073627Z` |

## 主要观察

### 1. 去掉 no-skill 提示后，Codex 在 Portland 上的 skill gap 消失

上一轮中间版本里，Portland 对 Codex 的结果是：

- `provided_skills`: `3/3`
- `no_skill`: `1/3`

本轮改成 neutral no-skill prompt 后，结果变为：

- `provided_skills`: `3/3`
- `no_skill`: `3/3`

这说明之前 no-skill prompt 中的“不要使用 skill”提示本身可能改变了 Codex 的解题策略。更自然的 no-skill 条件下，Codex 能直接从任务、数据和 policy 中恢复出正确输出。

### 2. DataCo 仍然主要卡在 frozen taxonomy

DataCo 的主要失败仍集中在 `control_tower_actions.csv`：

- `reason_code` 被判成 `carrier_lane_failure`、`order_delay`、`delivery_delay_detected` 等自然替代表达
- `decision_hierarchy` 在部分 lane-performance 场景中偏向 `resilience`
- `value_at_risk` 有时输出为 `10.0` 而不是 `10`

这说明 DataCo 的主要问题不是 skill 泄露，而是测试要求的 frozen taxonomy 和自然 control-tower 语言之间仍有冲突。

### 3. Portland 对 Claude Code 仍然困难

Claude Code 在 Portland 上两种条件均为 `0/3`。

常见问题包括：

- 供应商名称保真度不稳定，例如去掉公司名中的逗号
- `top_supplier_share` 格式不稳定，例如 `0.58` 而非 `0.580`
- `anti_pattern` 判断偏差
- `owner_function` 和 `follow_up` 使用自然语言或非预期枚举

这说明 Portland 对 Claude Code 的难点不只是领域知识，也包括严格结构化输出与字符串保真。

### 4. OR-Library 的稳定难点仍是 bottleneck report

OR-Library 的主要失败仍集中在 `bottleneck_report.json`：

- `root_cause` 被写成自然语言解释或模型自造枚举
- `decision_hierarchy` 被写成列表，而不是单个 frozen value

本轮 Codex 的 `provided_skills` 和 `no_skill` 都是 `2/3`，说明 OR-Library 在当前设计下没有稳定形成 skill-condition gap。

Claude Code 则为：

- `provided_skills`: `1/3`
- `no_skill`: `2/3`

其中 `provided_skills` 还额外错了 `recovery_schedule.csv` 的行顺序。

## 本轮结论

这轮结果非常重要，因为它说明：

1. `no_skill` prompt 必须保持中性。
   - 显式说“不要使用 skill”会改变 agent 行为，不是纯粹的无 skill 条件。
2. 仅仅清理 skill 泄露后，当前任务的 skill gap 并不稳定。
   - Portland 对 Codex 的 gap 在 neutral no-skill prompt 下消失。
   - DataCo 和 OR-Library 主要暴露的是 frozen taxonomy 与自然语言判断之间的冲突。
3. 当前任务更像是在测：
   - schema discipline
   - taxonomy exact match
   - 字符串/数值格式保真
   - 部分运营分类判断
4. 要真正研究 skill 贡献，下一步不能只靠现有输出字段。
   - 需要重新设计 skill-use evidence 或更明确地把专业 procedure 放入 provided skills，而不是放在 instruction 或 policy 中。

## 下一步建议

1. 把 `no_skill` prompt 中性化作为正式 runner 约定保留。
2. 重新设计 `provided_skills` 的作用方式：
   - 不在任务输出里暴露 skill 名称
   - 但增加独立、可评分的 framework-use evidence
3. 对 DataCo 和 OR-Library 放宽或重构部分 frozen taxonomy 字段：
   - 不要把自然语言上合理的解释全部判错
   - 或者把字段改成更明确的 code taxonomy，并由 policy 明确给出 allowed codes
4. Portland 仍可保留为结构化采购任务，但需要进一步区分：
   - 专业判断错误
   - 字符串保真错误
   - 格式错误
