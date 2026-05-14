# 外部来源任务正式矩阵记录

运行日期：`2026-04-08`

## 范围

本轮测试覆盖 3 个已经升级为 `runnable_external_source` 的主任务：

| 任务 | 外部来源 |
| --- | --- |
| `dataco-control-tower-exception-review` | DataCo SMART Supply Chain |
| `portland-sourcing-concentration-review` | Open Contracting / City of Portland |
| `orlib-disruption-recovery-control` | OR-Library `ft06` |

Agent 与模型：

| Agent | 模型 |
| --- | --- |
| Codex | `gpt-5.4` |
| Claude Code | `qwen3.5-plus` |

Skill 条件：

- `provided_skills`
- `no_skill`

## 结果矩阵

| Agent | Skill 条件 | DataCo | Portland | OR-Library |
| --- | --- | --- | --- | --- |
| Codex | `provided_skills` | passed `3/3` | passed `3/3` | failed, agent error / no outputs |
| Codex | `no_skill` | passed `3/3` | passed `3/3` | failed `2/3` |
| Claude Code | `provided_skills` | passed `3/3` | failed `0/3` | failed `2/3` |
| Claude Code | `no_skill` | failed `2/3` | failed `0/3` | failed `2/3` |

## Run 目录

| Agent | Skill | 任务 | Run |
| --- | --- | --- | --- |
| Codex | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-provided_skills-20260408T022324Z` |
| Codex | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-provided_skills-20260408T022653Z` |
| Codex | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-provided_skills-20260408T023025Z` |
| Codex | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-no_skill-20260408T023407Z` |
| Codex | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-no_skill-20260408T023743Z` |
| Codex | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-no_skill-20260408T024059Z` |
| Claude Code | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-provided_skills-20260408T024431Z` |
| Claude Code | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-provided_skills-20260408T024547Z` |
| Claude Code | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-provided_skills-20260408T024802Z` |
| Claude Code | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-no_skill-20260408T024911Z` |
| Claude Code | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-no_skill-20260408T025013Z` |
| Claude Code | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-no_skill-20260408T025133Z` |

## 主要观察

1. `dataco-control-tower-exception-review`
   - Codex 在 `provided_skills` 和 `no_skill` 下都通过 `3/3`。
   - Claude Code 在 `provided_skills` 下通过 `3/3`，在 `no_skill` 下退化到 `2/3`。
   - Claude 的失败是输出精度问题：`value_at_risk` 写成了带小数的字符串，如 `10.0`，而不是测试要求的整数文本 `10`。

2. `portland-sourcing-concentration-review`
   - Codex 在两种条件下都通过 `3/3`。
   - Claude Code 在两种条件下都失败 `0/3`。
   - 失败不是 schema 问题，而是采购判断与字符串保真度问题：
     - `provided_skills` 下把若干 category 的 `supply_risk`、`kraljic_quadrant`、`anti_pattern` 判断错了。
     - `no_skill` 下除判断偏差外，还出现供应商名标准化偏差，例如去掉了原始名称中的逗号。

3. `orlib-disruption-recovery-control`
   - 两个 agent 都能稳定通过 `recovery_schedule.csv` 和 `schedule_metrics.json`。
   - 稳定失败点都集中在 `bottleneck_report.json`。
   - Codex `provided_skills` 是 agent 运行失败，stderr 显示多次 stream reconnect，最终没有产出文件。
   - Codex `no_skill` 与 Claude 两种条件都把 `root_cause` 写成自然语言解释，而不是精确枚举值 `machine_load_plus_downtime`。
   - Claude 在两种条件下还会把 `decision_hierarchy` 写成列表，而不是单个枚举值 `flexibility_speed`。

## 初步结论

1. 这三项任务现在已经能明显区分不同 agent 的错误类型，不再只是旧补货任务里的单一 label mismatch。
2. DataCo 对 Claude 出现了可观察的 skill 差异：`provided_skills` 为 `3/3`，`no_skill` 为 `2/3`。
3. Portland 目前对 Claude 难度明显更高，说明采购分类和 anti-pattern 映射比 DataCo 的 control-tower 规则更容易暴露业务判断偏差。
4. OR-Library 继续显示一个稳定模式：排程和 metrics 较容易，瓶颈报告的枚举字段更难保持精确。
5. Codex 目前仍然在 DataCo / Portland 上对 `provided_skills` 与 `no_skill` 没有显著差异，说明这两个任务的 instruction 仍可能给得过于完整。

## 下一步

1. 补 `self_created_skills` 条件。
2. 对 DataCo 和 Portland 考虑进一步减少 instruction 中直接写出的 taxonomy，让 `provided_skills` 承担更多框架信息。
3. 为 `provided_skills` 增加更直接的 skill-use evidence，例如 `framework_trace.json`。
4. 记录并分析 OR-Library 上的枚举漂移问题，把“自然语言解释替代枚举值”作为一类专门错误。
