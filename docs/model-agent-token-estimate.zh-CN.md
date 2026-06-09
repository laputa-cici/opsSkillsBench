# 大模型与 Agent 测试 Token / 费用估算

更新日期：2026-06-09

本文估算 opsSkillsBench 后续开发与实验评测需要覆盖的 Agent / 大模型组合、token 用量和大致费用。这里采用**预算偏富裕、容错率较大**的口径：宁愿高估，也不要后续实验跑到一半因为 token 或费用预算不足而被迫缩矩阵。

价格会随时间、区域、batch、缓存、企业折扣和订阅方式变化。正式采购或论文实验前，需要以当日官方价格页重新冻结一次。

参考价格页：

- OpenAI API pricing: https://openai.com/api/pricing/
- Anthropic / Claude pricing: https://www.anthropic.com/pricing
- Google Gemini API pricing: https://ai.google.dev/gemini-api/docs/pricing
- Alibaba Cloud Model Studio pricing: https://www.alibabacloud.com/help/zh/model-studio/model-pricing
- OpenAI Codex: https://developers.openai.com/codex/
- Claude Code: https://docs.anthropic.com/en/docs/claude-code/overview
- Gemini CLI: https://github.com/google-gemini/gemini-cli
- Qwen Code: https://github.com/QwenLM/qwen-code

## 估算原则

本文件不按最低成本估算，而按“比较富裕、有较大容错率”的方式估算：

1. 单次运行 token 按偏高值估算，覆盖 agent 反复读取文件、重试、生成中间脚本、查看测试失败日志等情况。
2. 费用按标准实时推理单价估算，不默认使用 batch 50% 优惠、缓存折扣或企业折扣。
3. 正式矩阵之外额外预留 30% buffer，覆盖失败重跑、限流后重复执行、prompt 调整和临时补测。
4. 对于输出 token 价格较高的模型，单独估算输入/输出 token，而不是只看总 token。
5. 不把 legacy scenario task 作为论文主统计，但会给 smoke / integration 留预算。

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

目标实验规模建议按 100 个 atomic task 规划预算。当前 20 题主要用于 sanity / pilot，不建议直接作为最终论文矩阵。

## 需要覆盖的 Agent / 模型

建议保留 4 类 Agent / 模型组合：

| 类别 | 主要用途 | 建议模型 |
| --- | --- | --- |
| OpenAI / Codex 主线 | 主力 coding agent，对齐当前项目已有 Codex 工作流 | `gpt-5.5`, `gpt-5.4`, `gpt-5.4 mini` |
| Claude Code 主线 | 对比另一类成熟 coding agent | `Claude Opus 4.8`, `Claude Sonnet 4.6` |
| Gemini CLI 对照 | 多 provider agent 对照，观察不同工具栈稳定性 | `Gemini 3.1 Pro Preview`, `Gemini 3.5 Flash` |
| Qwen / 国产模型对照 | 延续历史 `qwen3.5-plus` 配置，验证性价比和中文/运营任务表现 | `qwen3.5-plus` |

最低可发表矩阵可以只保留 4 个模型：

1. `gpt-5.5`
2. `gpt-5.4 mini`
3. `Claude Sonnet 4.6`
4. `qwen3.5-plus`

更完整、更稳妥的矩阵建议保留 8 个模型：

1. `gpt-5.5`
2. `gpt-5.4`
3. `gpt-5.4 mini`
4. `Claude Opus 4.8`
5. `Claude Sonnet 4.6`
6. `Gemini 3.1 Pro Preview`
7. `Gemini 3.5 Flash`
8. `qwen3.5-plus`

## 评测条件

每个 Agent / 模型组合建议在三种 skill 条件下运行：

| 条件 | 用途 | token 特征 |
| --- | --- | --- |
| `no_skill` | 测 baseline，没有领域技能帮助时模型能否靠任务说明完成 | 文件读取少，但失败重试可能较多 |
| `provided_skills` | 测 benchmark 预置外部 skill 是否提升表现 | 会额外读取 1-3 个 skill，输入显著变高 |
| `self_created_skills` | 测 agent 自建技能、沉淀流程、复用经验的能力 | 首轮输出和文件操作最多，token 波动最大 |

## 单次 Task-run Token 假设

这里的 task-run 指一个模型在一个任务、一个 skill 条件、一次重复中的完整执行。

| 条件 | 输入 token/次 | 输出 token/次 | 合计 token/次 | 富裕预算值 |
| --- | ---: | ---: | ---: | ---: |
| `no_skill` | 40k-90k | 8k-20k | 50k-110k | 120k |
| `provided_skills` | 90k-180k | 12k-30k | 110k-220k | 240k |
| `self_created_skills` | 120k-260k | 25k-70k | 150k-330k | 360k |

三种条件平均后，后续统一用：

```text
单次 task-run 富裕预算 = 240k token
其中约 190k input token，50k output token
```

再加项目级 buffer：

```text
正式预算 = 原始估算 * 1.3
```

也就是说，一个模型完整跑 100 个 atomic task、3 个 skill 条件、3 次重复：

```text
100 tasks * 3 conditions * 3 repeats = 900 runs
900 runs * 240k token/run = 216M token
216M * 1.3 buffer ~= 281M token
```

拆分为：

```text
input: 100 * 3 * 3 * 190k * 1.3 ~= 222M input token
output: 100 * 3 * 3 * 50k * 1.3 ~= 59M output token
```

## 当前 20 题预算

### Sanity Matrix

用途：确认 runner、Agent 权限、三种 skill 条件和输出结构都能跑通。

配置：

- 20 个任务
- 2 个 Agent / 模型组合
- 3 个 skill 条件
- 2 次重复

计算：

```text
20 * 2 * 3 * 2 = 240 runs
240 * 240k = 57.6M token
加 30% buffer ~= 75M token
```

建议预算：约 75M token。

### Pilot Matrix

用途：在当前任务规模上初步比较模型差异，不作为最终论文结果。

配置：

- 20 个任务
- 4 个模型
- 3 个 skill 条件
- 3 次重复

计算：

```text
20 * 4 * 3 * 3 = 720 runs
720 * 240k = 172.8M token
加 30% buffer ~= 225M token
```

建议预算：约 225M token。

## 100 题正式实验预算

### 最低可发表矩阵

配置：

- 100 个 atomic task
- 4 个模型
- 3 个 skill 条件
- 3 次重复

计算：

```text
100 * 4 * 3 * 3 = 3,600 runs
3,600 * 240k = 864M token
加 30% buffer ~= 1.12B token
```

建议预算：约 1.1B token。

### 完整稳妥矩阵

配置：

- 100 个 atomic task
- 8 个模型
- 3 个 skill 条件
- 3 次重复

计算：

```text
100 * 8 * 3 * 3 = 7,200 runs
7,200 * 240k = 1.728B token
加 30% buffer ~= 2.25B token
```

建议预算：约 2.25B token。

## 模型价格假设

下表按 2026-06-09 查到的公开价格做估算。不同区域和模式可能不同，尤其是 Qwen、Gemini batch/flex、Claude prompt cache、OpenAI batch/cache。

| 模型 | 输入单价 / 1M token | 输出单价 / 1M token | 价格口径 |
| --- | ---: | ---: | --- |
| `gpt-5.5` | $5.00 | $30.00 | OpenAI 标准实时推理 |
| `gpt-5.4` | $2.50 | $15.00 | OpenAI 标准实时推理 |
| `gpt-5.4 mini` | $0.75 | $4.50 | OpenAI 标准实时推理 |
| `Claude Opus 4.8` | $5.00 | $25.00 | Anthropic API |
| `Claude Sonnet 4.6` | $3.00 | $15.00 | Anthropic API |
| `Gemini 3.1 Pro Preview` | $2.00 | $12.00 | Google Gemini 标准，按 <=200k prompt 估算 |
| `Gemini 3.5 Flash` | $1.50 | $9.00 | Google Gemini 标准 |
| `qwen3.5-plus` | $0.40 | $2.40 | Alibaba Cloud 国际模式，0-256K token 档，思考模式输出价 |

## 每个模型需要多少 Token、多少钱

下面按完整稳妥矩阵估算。默认每个主力模型跑：

```text
100 tasks * 3 skill conditions * 3 repeats = 900 runs
```

对低成本/冒烟模型 `gpt-5.4 mini` 和 `Gemini 3.5 Flash`，预算按 2 次重复估算：

```text
100 tasks * 3 skill conditions * 2 repeats = 600 runs
```

| 模型 | 计划 runs | 输入 token | 输出 token | 总 token | 估算费用 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.5` | 900 | 222M | 59M | 281M | ~$2,880 |
| `gpt-5.4` | 900 | 222M | 59M | 281M | ~$1,440 |
| `gpt-5.4 mini` | 600 | 148M | 39M | 187M | ~$287 |
| `Claude Opus 4.8` | 900 | 222M | 59M | 281M | ~$2,585 |
| `Claude Sonnet 4.6` | 900 | 222M | 59M | 281M | ~$1,551 |
| `Gemini 3.1 Pro Preview` | 900 | 222M | 59M | 281M | ~$1,152 |
| `Gemini 3.5 Flash` | 600 | 148M | 39M | 187M | ~$573 |
| `qwen3.5-plus` | 900 | 222M | 59M | 281M | ~$230 |

模型评测小计：

```text
总 token ~= 2.16B
模型 API 费用 ~= $10.7k
```

为了保持较大容错率，建议正式实验预算不要只按 $10.7k 准备，而是按：

```text
正式模型评测预算：$15k-$20k
```

这个区间覆盖：

1. 失败重跑。
2. 一些任务超过平均上下文。
3. 输出 token 比预期更多。
4. 少量临时补测。
5. 部分 provider 选择 priority / fast / higher-context 档位。

## 开发新增题预算

新增一个可运行 atomic task 通常包括：题目设计、数据切片、标准答案、pytest verifier、文档、oracle 回归、至少一次 Agent 试跑。

按富裕口径估算：

| 工作项 | token/题 |
| --- | ---: |
| 题目设计与数据 schema | 40k-100k |
| 生成/修改 oracle、测试、文档 | 100k-250k |
| 调试 verifier 与全量回归 | 50k-150k |
| Agent 试跑与修正 | 100k-300k |
| 合计 | 290k-800k |

如果目标从 16 个 atomic task 扩到 100 个，还需要新增约 84 个 atomic task：

```text
84 * 290k-800k ~= 24M-67M development token
```

建议开发预算：

```text
开发扩题 token：70M-100M
开发扩题费用：$2k-$5k
```

开发阶段建议主要使用 `gpt-5.4 mini`、`Claude Sonnet 4.6`、`qwen3.5-plus` 和本地 oracle，不要频繁用 `gpt-5.5` / `Claude Opus 4.8` 调 verifier。

## 总预算建议

| 阶段 | 目标 | token 预算 | 费用预算 |
| --- | --- | ---: | ---: |
| 当前 sanity matrix | 20 题、2 模型、3 条件、2 repeats | ~75M | ~$300-$1,000 |
| 当前 pilot matrix | 20 题、4 模型、3 条件、3 repeats | ~225M | ~$1,000-$3,500 |
| 扩题开发 | 从 16 atomic 扩到 100 atomic | 70M-100M | ~$2k-$5k |
| 100 题最低可发表矩阵 | 4 模型、3 条件、3 repeats | ~1.1B | ~$5k-$10k |
| 100 题完整稳妥矩阵 | 8 模型、3 条件、3 repeats | ~2.25B | ~$15k-$20k |

如果希望项目整体非常稳妥，建议准备：

```text
总 token 预算：2.5B-3.0B token
总费用预算：$25k-$35k
```

其中：

1. $15k-$20k 用于正式模型评测。
2. $2k-$5k 用于扩题开发和调试。
3. $5k-$10k 作为重跑、补测、模型升级、价格变动和临时实验 buffer。

## 推荐执行顺序

1. 当前 20 题先跑 sanity matrix，只验证链路和日志结构。
2. 扩题到 50 个 atomic task 后跑一次 pilot matrix，检查任务是否真的 skill-sensitive。
3. 扩题到 100 个 atomic task 后冻结任务、runner、skill、模型名和价格日期。
4. 正式矩阵优先跑 `gpt-5.5`、`Claude Sonnet 4.6`、`qwen3.5-plus`。
5. 确认主结果稳定后，再补 `gpt-5.4`、`Claude Opus 4.8`、`Gemini 3.1 Pro Preview`。
6. `gpt-5.4 mini` 和 `Gemini 3.5 Flash` 作为低成本模型对照，可少跑一次 repeat。

## 后续落地清单

1. 在 `scripts/run_benchmark_local.py` 的结果 JSON 中记录 `agent_version`、`model`、`skill_condition`、`repeat_index`、`prompt_token_estimate`、`completion_token_estimate`。
2. 增加 `docs/experiment-matrix.zh-CN.md`，正式冻结任务列表、模型列表、repeat 数和价格日期。
3. 给每个 task 增加 `paper_ready = false/true` 或等价字段，避免 prototype 题误入正式主实验。
4. 结果汇总脚本需要按输入 token、输出 token、总费用、是否重跑分别统计。
5. 每次正式实验前先跑 5 个任务的小矩阵，确认 agent 版本、模型名和计费记录都正确。
