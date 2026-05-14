# 新任务矩阵测试记录

运行日期：`2026-04-07`

## 任务范围

本轮测试覆盖重新设计后的 3 个 runnable prototype task。注意：这是 2026-04-07 的历史 pilot 矩阵，当时三个任务都还使用紧凑原型切片，字段设计锚定 DataCo / Portland / OR-Library 场景；不能把本轮结果写成最终 paper benchmark 结果。2026-04-08 起，`dataco-control-tower-exception-review` 已升级为 raw DataCo 派生任务，后续应重新运行正式矩阵。

| 任务 | 目标 |
| --- | --- |
| `dataco-control-tower-exception-review` | DataCo 风格供应链 control tower 异常动作、lane 风险登记、scorecard summary。 |
| `portland-sourcing-concentration-review` | Portland/Open Contracting 风格采购集中度、Kraljic 分类、供应商行动计划、风险登记。 |
| `orlib-disruption-recovery-control` | OR-Library 风格排程恢复、瓶颈报告、恢复行动计划。 |

每个任务先用 oracle 跑通，确认测试链路有效：

| 任务 | Oracle 结果 |
| --- | --- |
| `dataco-control-tower-exception-review` | `3 passed` |
| `portland-sourcing-concentration-review` | `3 passed` |
| `orlib-disruption-recovery-control` | `3 passed` |

## 测试矩阵

| Agent | 模型 | Skill 条件 | 任务 | Run | 结果 |
| --- | --- | --- | --- | --- | --- |
| Codex | `gpt-5.4` | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-provided_skills-20260407T143740Z` | failed, `2 passed / 1 failed` |
| Codex | `gpt-5.4` | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-provided_skills-20260407T144107Z` | failed, `2 passed / 1 failed` |
| Codex | `gpt-5.4` | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-provided_skills-20260407T144401Z` | failed, `2 passed / 1 failed` |
| Codex | `gpt-5.4` | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-no_skill-20260407T144812Z` | passed, `3 passed` |
| Codex | `gpt-5.4` | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-no_skill-20260407T145114Z` | passed, `3 passed` |
| Codex | `gpt-5.4` | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-no_skill-20260407T145414Z` | failed, `2 passed / 1 failed` |
| Claude Code | `qwen3.5-plus` via stream metadata; model argument was not explicit in this historical run | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-provided_skills-20260407T145826Z` | failed, `1 passed / 2 failed` |
| Claude Code | `qwen3.5-plus` via stream metadata; model argument was not explicit in this historical run | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-provided_skills-20260407T150014Z` | failed, `2 passed / 1 failed` |
| Claude Code | `qwen3.5-plus` via stream metadata; model argument was not explicit in this historical run | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-provided_skills-20260407T150144Z` | failed, `2 passed / 1 failed` |
| Claude Code | `qwen3.5-plus` via stream metadata; model argument was not explicit in this historical run | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-no_skill-20260407T150335Z` | failed, `0 passed / 3 failed` |
| Claude Code | `qwen3.5-plus` via stream metadata; model argument was not explicit in this historical run | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-no_skill-20260407T150518Z` | failed, `2 passed / 1 failed` |
| Claude Code | `qwen3.5-plus` via stream metadata; model argument was not explicit in this historical run | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-no_skill-20260407T150656Z` | failed, `2 passed / 1 failed` |

## 初步观察

1. 新任务已经能区分更多失败形态，不再只是旧补货任务里的 `trigger_rule` 单字段问题。
2. Codex 在 `no_skill` 下通过了 DataCo 和 Portland，说明当前 instruction 仍然足够详细，部分任务仍可由强模型直接按规则完成。
3. Codex 在 `provided_skills` 下反而更容易输出额外枚举或解释性字段，例如 DataCo summary 中多出 `monitor: 0`，说明提供 skill 可能诱导更“管理化”的自然表达，反而偏离精确 schema。
4. Claude Code 在 DataCo `no_skill` 下明显更弱，`0 passed / 3 failed`；在 `provided_skills` 下提升到 `1 passed / 2 failed`，这里出现了初步 skill 条件差异。
5. Portland 任务两个 agent 的主要失败都集中在 `procurement_risk_register.json` 的精确 JSON 匹配，说明主表计算和行动计划较容易，风险登记字段仍是主要难点。
6. OR-Library 任务两个 agent 都能生成可行排程和 metrics，但在 `bottleneck_report.json` 中把枚举字段写成自然语言或列表，例如 `root_cause` 和 `decision_hierarchy`，说明瓶颈解释/框架字段是稳定失败点。

## Harness 说明

本轮测试前更新了 `no_skill` 条件：

- `provided_skills`：agent 工作目录为仓库根目录，prompt 显式暴露 task-local skill 路径。
- `no_skill`：agent 工作目录切到该任务 runtime `/app`，prompt 不提供 skill 路径，尽量避免 agent 读取仓库中的预置 skill。

Claude Code run 使用 `--output-format stream-json --verbose --include-hook-events`，每次 run 记录：

- `claude.stream.jsonl`
- `claude.debug.log`
- `claude.last_message.txt`

本轮历史矩阵没有显式传 `--model`，但 `claude.stream.jsonl` 元数据显示实际模型为 `qwen3.5-plus`。2026-04-08 的临时 smoke test 已确认 Claude Code 可以显式使用 `--model qwen3.5-plus`，后续 run 统一显式传该参数。

Codex run 记录：

- `codex.stdout.log`
- `codex.stderr.log`
- `codex.last_message.txt`

## 下一步建议

不要为了让 agent 通过而放宽测试。当前失败正好说明这些字段能够捕捉“运营框架输出是否精确可执行”。

下一步应该：

1. 保留当前测试结果作为第一轮新任务矩阵 pilot。
2. 进一步减少 instruction 中直接给出的规则，把更多 taxonomy 放进 provided skills 或 policy 文件，增强 `provided_skills` 与 `no_skill` 的差异。
3. 为 `provided_skills` 增加 explicit skill-use evidence 检查，例如要求 `framework_trace.json` 记录使用的 skill 段落或 framework id。
