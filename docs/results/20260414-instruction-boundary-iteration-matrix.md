# 题面边界重划后的正式矩阵记录

运行日期：`2026-04-14` 到 `2026-04-15`

## 本轮改动

本轮没有直接照搬经管领域专家的意见，而是有选择地做了三项调整：

1. 保留 deterministic 规则
   - 输入输出 schema
   - 数值公式
   - 排序和硬阈值
2. 收回 instruction 中过于直接的高层管理映射
   - `owner_function`
   - `decision_hierarchy`
   - `reason_code`
   - `anti_pattern`
   - `follow_up`
   - `root_cause`
3. 让这些高层字段更多依赖 task-local skills 中已有的运营框架，但仍要求输出值落在 policy 允许的 taxonomy 内

同时顺手修复了一个 harness 小问题：

- [run_task_local.py](/Users/cici/code/opsSkillsBench-main/scripts/run_task_local.py) 的 runtime 清理逻辑现在会忽略“文件已被其他进程删除”的情况，避免并发清理时直接报错。

## 覆盖范围

本轮测试覆盖 3 个主任务：

| 任务 | 数据来源 |
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
| Codex | `provided_skills` | failed `1/3` | passed `3/3` | passed `3/3` |
| Codex | `no_skill` | failed `2/3` | failed `1/3` | passed `3/3` |
| Claude Code | `provided_skills` | failed `1/3` | failed `0/3` | failed `1/3` |
| Claude Code | `no_skill` | failed `2/3` | failed `0/3` | failed `2/3` |

## Run 目录

| Agent | Skill | 任务 | Run |
| --- | --- | --- | --- |
| Codex | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-provided_skills-20260414T104827Z` |
| Codex | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/codex-no_skill-20260414T104912Z` |
| Claude Code | `provided_skills` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-provided_skills-20260414T105222Z` |
| Claude Code | `no_skill` | `dataco-control-tower-exception-review` | `.benchmark_runs/claude-no_skill-20260414T105803Z` |
| Codex | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-provided_skills-20260414T110000Z` |
| Codex | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/codex-no_skill-20260414T140518Z` |
| Claude Code | `provided_skills` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-provided_skills-20260414T154940Z` |
| Claude Code | `no_skill` | `portland-sourcing-concentration-review` | `.benchmark_runs/claude-no_skill-20260414T155149Z` |
| Codex | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-provided_skills-20260414T173341Z` |
| Codex | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/codex-no_skill-20260414T224144Z` |
| Claude Code | `provided_skills` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-provided_skills-20260415T004110Z` |
| Claude Code | `no_skill` | `orlib-disruption-recovery-control` | `.benchmark_runs/claude-no_skill-20260415T004301Z` |

## 主要观察

### 1. Portland 这题被明显拉开了

- Codex 在 `provided_skills` 下仍然 `3/3`，但在 `no_skill` 下掉到 `1/3`。
- 这说明采购框架、anti-pattern 和 follow-up 逻辑从 instruction 收回之后，Portland 开始具备更明显的 skill-sensitive 特征。
- `no_skill` 下最常见的错误是：
  - 把 `supplier_fragmentation` 误判成 `none` 或 `single_sourcing`
  - 把 `owner_function`、`follow_up` 写成更自然语言化的运营建议
  - 风险登记中的 `escalation_level` 也更容易脱离测试要求

### 2. DataCo 出现了“skill 可能把模型带偏”的现象

- Codex：`provided_skills` 为 `1/3`，`no_skill` 为 `2/3`
- Claude：`provided_skills` 为 `1/3`，`no_skill` 为 `2/3`
- 也就是说，DataCo 这题在本轮不是“用了 skill 更好”，而是“用了 skill 后更容易把 `reason_code`、`decision_hierarchy`、`lane risk framing` 写成更专业但不符合 frozen taxonomy 的表达”。
- 这说明 DataCo 当前收得有点过头：
  - task 仍然 deterministic
  - 但高层字段约束不够清楚
  - 结果是模型开始输出“看起来更像 control tower 语言”的文本，而不是测试要求的精确枚举

### 3. OR-Library 对 Codex 依然不够敏感

- Codex 在 `provided_skills` 和 `no_skill` 下都通过 `3/3`。
- 说明即使把 `root_cause`、`decision_hierarchy`、`skill_framework` 的说明收了一部分，Codex 仍然能从数据和现有任务结构中恢复出正确输出。
- 这题目前对 Claude 仍然有难度：
  - `provided_skills` 为 `1/3`
  - `no_skill` 为 `2/3`
- Claude 的稳定失败点仍然是把 `bottleneck_report.json` 写成“解释性对象”而不是精确枚举：
  - `root_cause` 写成自然语言
  - `decision_hierarchy` 写成列表
  - `skill_framework` 写成多个框架组成的列表

## 与上一轮相比的结论

和 [20260408-external-source-matrix.md](/Users/cici/code/opsSkillsBench-main/docs/results/20260408-external-source-matrix.md) 相比，这一轮最重要的变化不是平均分数提升，而是任务分化更明显了：

1. Portland
   - 从“Codex 两种条件都 3/3”变成“Codex 只有 provided_skills 保持 3/3”
   - 说明这题的 instruction/skill 边界调整是有效的

2. DataCo
   - 从“Codex 两种条件都 3/3”变成“两种条件都掉分，且 provided_skills 更容易偏离 frozen taxonomy”
   - 说明这题需要下一轮做更细的边界校准，而不是继续简单地把规则从 instruction 往 skill 里搬

3. OR-Library
   - 对 Codex 仍然没有拉开 skill 差距
   - 说明这题的瓶颈报告虽然难，但可能还不够“必须依赖 skill”

## 本轮判断

如果按“这轮迭代是否有价值”来评估，我的判断是：

- **有价值**
- 但不是因为整体分数变好了
- 而是因为我们第一次比较清楚地看到了三种不同状态：

1. **边界调整有效**
   - Portland
2. **边界调整过度，开始把模型带向自由发挥**
   - DataCo
3. **边界调整影响有限**
   - OR-Library 对 Codex

## 下一步建议

1. 优先继续打磨 Portland
   - 它目前最像真正有希望进入论文主结果的 skill-sensitive 任务
2. 回调 DataCo
   - 不要继续收 instruction
   - 而是把 `reason_code` / `decision_hierarchy` / `lane risk framing` 的 frozen taxonomy 再收紧一点
3. 对 OR-Library 引入更明确的 skill-use evidence
   - 例如增加一个轻量的结构化 trace，而不是继续只靠枚举字段
4. 再进入 `self_created_skills`
   - 当前 `provided_skills` / `no_skill` 的边界已经更清楚，下一步更适合开始测“agent 能否自己总结出可复用 procedure”
