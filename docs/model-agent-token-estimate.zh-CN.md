# 大模型与 Agent 测试 Token / 费用估算

更新日期：2026-06-10

本文估算 opsSkillsBench 后续开发与实验评测需要覆盖的 Agent / 大模型组合、token 用量和费用。上一版估算把“极端压力上限”写成了主预算口径，明显偏夸张；按同事实际试跑反馈，十几个题目跑一遍只花几块钱，这更接近日常/小规模测试的真实量级。

本版改成三档预算：

1. **实测校准口径**：用于日常试跑、十几个题目冒烟、小规模 sanity。
2. **正式实验宽裕口径**：用于 100 题、多个模型、三种 skill 条件、重复实验的主要预算。
3. **压力上限口径**：只作为风险提示，不作为默认采购预算。

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

## 结论先行

建议当前项目按下面预算准备：

| 用途 | 建议准备 |
| --- | ---: |
| 当前 20 题 sanity / pilot | $50-$300 |
| 扩题开发与零散调试 | $500-$1,500 |
| 100 题、4 个模型的最低可发表矩阵 | $1,000-$2,500 |
| 100 题、8 个模型的完整稳妥矩阵 | $2,500-$5,000 |
| 项目整体预留，含失败重跑和临时补测 | $5,000-$8,000 |

如果只是像同事那样“十几个题目跑一遍”，几块钱是合理的，尤其是在：

1. 只跑 1 个模型。
2. 只跑 1 个 skill 条件。
3. 不做 3 次重复。
4. 没有大量失败重跑。
5. 使用中低价模型或 provider 折扣。

上一版中 `$25k-$35k` 更像“所有强模型、长上下文、频繁失败重跑、无缓存折扣”的压力上限，不应作为默认预算。

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

目标实验规模建议按 100 个 atomic task 规划。当前 20 题主要用于 sanity / pilot，不建议直接作为最终论文矩阵。

## 需要覆盖的模型

建议分两档跑。

最低可发表矩阵：

| 模型 | 角色 |
| --- | --- |
| `gpt-5.5` 或当前 OpenAI 强模型 | Codex 主力强模型 |
| `gpt-5.4 mini` 或当前 OpenAI 经济模型 | 低成本对照 |
| `Claude Sonnet 4.6` 或当前 Sonnet | Claude Code 主力模型 |
| `qwen3.5-plus` 或当前 Qwen Plus | 国产/性价比对照 |

完整稳妥矩阵：

| 模型 | 角色 |
| --- | --- |
| `gpt-5.5` | OpenAI 强模型 |
| `gpt-5.4` | OpenAI 中高档模型 |
| `gpt-5.4 mini` | OpenAI 经济模型 |
| `Claude Opus 4.8` | Claude 强模型 |
| `Claude Sonnet 4.6` | Claude 主力模型 |
| `Gemini 3.1 Pro Preview` | Gemini Pro 对照 |
| `Gemini 3.5 Flash` | Gemini 经济模型 |
| `qwen3.5-plus` | Qwen 对照 |

## 评测条件

每个模型建议在三种 skill 条件下运行：

| 条件 | 用途 |
| --- | --- |
| `no_skill` | 测 baseline，没有领域技能帮助时模型能否靠任务说明完成 |
| `provided_skills` | 测 benchmark 预置外部 skill 是否提升表现 |
| `self_created_skills` | 测 agent 自建技能、沉淀流程、复用经验的能力 |

## 单次 Task-run Token 假设

这里的 task-run 指一个模型在一个任务、一个 skill 条件、一次重复中的完整执行。

按实测反馈和当前任务复杂度，默认不要用几百 k token 估算。更合理的三档是：

| 口径 | 输入 token/次 | 输出 token/次 | 合计 token/次 | 用途 |
| --- | ---: | ---: | ---: | --- |
| 实测校准 | 15k-30k | 2k-5k | 17k-35k | 十几个题目试跑、无大量失败 |
| 正式宽裕 | 35k | 7k | 42k | 主预算口径，已经比实测偏宽 |
| 正式宽裕 + 50% buffer | 52k | 10k | 62k | 本文费用表采用 |
| 压力上限 | 150k+ | 30k+ | 180k+ | 只用于异常风险提示 |

本文后续主预算统一采用：

```text
每个 task-run = 52k input token + 10k output token ~= 62k token
```

这个口径已经包含 50% 左右的冗余，适合正式实验预算；日常试跑一般会低于这个数。

## 为什么十几个题目只要几块钱

假设跑 15 个 task、1 个模型、1 个 skill 条件、1 次重复：

```text
15 runs * 62k token/run ~= 930k token
```

如果模型价格在每百万 token 几美元到十几美元之间，那么总费用就是几美元到十几美元。若使用经济模型、Qwen、Flash、mini 或缓存/折扣，费用会更低。因此同事实测“十几个题目几块钱”是合理的。

真正拉高预算的是完整矩阵：

```text
任务数 * 模型数 * skill 条件数 * 重复次数
```

例如 100 题、8 模型、3 条件、3 次重复，就是：

```text
100 * 8 * 3 * 3 = 7,200 runs
```

这和“十几个题目跑一遍”不是一个量级。

## 当前 20 题预算

### 日常 Sanity

配置：

- 20 个任务
- 1 个模型
- 1 个 skill 条件
- 1 次重复

计算：

```text
20 * 1 * 1 * 1 = 20 runs
20 * 62k ~= 1.24M token
```

建议费用：约 $3-$30，取决于模型。

### 小规模 Pilot

配置：

- 20 个任务
- 4 个模型
- 3 个 skill 条件
- 1 次重复

计算：

```text
20 * 4 * 3 * 1 = 240 runs
240 * 62k ~= 15M token
```

建议费用：约 $50-$300。

如果做 3 次重复：

```text
20 * 4 * 3 * 3 = 720 runs
720 * 62k ~= 45M token
```

建议费用：约 $150-$900。

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
3,600 * 62k ~= 223M token
```

建议费用：约 $1,000-$2,500。

### 完整稳妥矩阵

配置：

- 100 个 atomic task
- 8 个模型
- 3 个 skill 条件
- 3 次重复

计算：

```text
100 * 8 * 3 * 3 = 7,200 runs
7,200 * 62k ~= 446M token
```

建议费用：约 $2,500-$5,000。

## 模型价格假设

下表仍需在正式实验前按官方页面复核。这里保留的是预算计算用的近似价格，不作为采购报价。

| 模型 | 输入单价 / 1M token | 输出单价 / 1M token | 价格口径 |
| --- | ---: | ---: | --- |
| `gpt-5.5` | $5.00 | $30.00 | OpenAI 标准实时推理，需复核 |
| `gpt-5.4` | $2.50 | $15.00 | OpenAI 标准实时推理，需复核 |
| `gpt-5.4 mini` | $0.75 | $4.50 | OpenAI 标准实时推理，需复核 |
| `Claude Opus 4.8` | $5.00 | $25.00 | Anthropic API，需复核 |
| `Claude Sonnet 4.6` | $3.00 | $15.00 | Anthropic API，需复核 |
| `Gemini 3.1 Pro Preview` | $2.00 | $12.00 | Google Gemini 标准，需复核 |
| `Gemini 3.5 Flash` | $1.50 | $9.00 | Google Gemini 标准，需复核 |
| `qwen3.5-plus` | $0.40 | $2.40 | Alibaba Cloud / DashScope，需复核 |

## 每个模型需要多少 Token、多少钱

下面按 100 题、3 个 skill 条件、3 次重复估算：

```text
100 * 3 * 3 = 900 runs/model
900 * 52k input ~= 47M input token
900 * 10k output ~= 9M output token
```

| 模型 | 计划 runs | 输入 token | 输出 token | 总 token | 估算费用 |
| --- | ---: | ---: | ---: | ---: | ---: |
| `gpt-5.5` | 900 | 47M | 9M | 56M | ~$505 |
| `gpt-5.4` | 900 | 47M | 9M | 56M | ~$253 |
| `gpt-5.4 mini` | 900 | 47M | 9M | 56M | ~$76 |
| `Claude Opus 4.8` | 900 | 47M | 9M | 56M | ~$460 |
| `Claude Sonnet 4.6` | 900 | 47M | 9M | 56M | ~$276 |
| `Gemini 3.1 Pro Preview` | 900 | 47M | 9M | 56M | ~$202 |
| `Gemini 3.5 Flash` | 900 | 47M | 9M | 56M | ~$151 |
| `qwen3.5-plus` | 900 | 47M | 9M | 56M | ~$40 |

完整 8 模型小计：

```text
总 token ~= 448M
模型 API 费用 ~= $1,963
```

考虑到正式实验可能有失败重跑、临时补测、价格差异和上下文波动，建议不要只按 $2k 准备，而是按：

```text
完整 8 模型正式评测预算：$2,500-$5,000
```

如果只跑最低可发表 4 模型：

```text
建议预算：$1,000-$2,500
```

## 开发新增题预算

新增一个可运行 atomic task 通常包括：题目设计、数据切片、标准答案、pytest verifier、文档、oracle 回归、至少一次 Agent 试跑。

按实际开发节奏估算：

| 工作项 | token/题 |
| --- | ---: |
| 题目设计与数据 schema | 20k-60k |
| 生成/修改 oracle、测试、文档 | 50k-150k |
| 调试 verifier 与全量回归 | 20k-80k |
| Agent 试跑与修正 | 30k-120k |
| 合计 | 120k-410k |

如果目标从 16 个 atomic task 扩到 100 个，还需要新增约 84 个 atomic task：

```text
84 * 120k-410k ~= 10M-35M development token
```

建议开发费用：

```text
扩题开发：$500-$1,500
```

如果大量用强模型调题，可能上升到 $2k-$3k；但默认不建议这么做。开发阶段应尽量使用本地 oracle、低价模型和小批量 agent 试跑。

## 总预算建议

| 阶段 | 目标 | token 预算 | 费用预算 |
| --- | --- | ---: | ---: |
| 日常 sanity | 20 题、1 模型、1 条件、1 repeat | ~1M | ~$3-$30 |
| 当前 pilot | 20 题、4 模型、3 条件、1 repeat | ~15M | ~$50-$300 |
| 当前 pilot 加重复 | 20 题、4 模型、3 条件、3 repeats | ~45M | ~$150-$900 |
| 扩题开发 | 从 16 atomic 扩到 100 atomic | 10M-35M | ~$500-$1,500 |
| 100 题最低可发表矩阵 | 4 模型、3 条件、3 repeats | ~223M | ~$1,000-$2,500 |
| 100 题完整稳妥矩阵 | 8 模型、3 条件、3 repeats | ~446M | ~$2,500-$5,000 |

建议项目整体准备：

```text
总 token 预算：500M-800M token
总费用预算：$5,000-$8,000
```

这个预算已经包含比较大的容错率。除非出现大量失败重跑、任务复杂度显著上升、强模型价格提高，或者把所有模型都切到最贵档位，否则不需要按上一版 `$25k-$35k` 准备。

## 压力上限什么时候才需要考虑

只有以下情况同时出现时，费用才可能接近上一版的高预算：

1. 每个 task-run 都达到 180k-300k token。
2. 大量使用最贵模型，例如强模型/Opus 类模型全量重复。
3. 每个任务多次失败重跑。
4. 任务数据变大，agent 反复读取长文件。
5. 没有使用任何缓存、batch、折扣或低价模型。

这不应作为默认预算，只能作为极端风险说明。

## 后续落地清单

1. 在 `scripts/run_benchmark_local.py` 的结果 JSON 中记录 `agent_version`、`model`、`skill_condition`、`repeat_index`、`prompt_token_estimate`、`completion_token_estimate`。
2. 增加 `docs/experiment-matrix.zh-CN.md`，正式冻结任务列表、模型列表、repeat 数和价格日期。
3. 给每个 task 增加 `paper_ready = false/true` 或等价字段，避免 prototype 题误入正式主实验。
4. 结果汇总脚本需要按输入 token、输出 token、总费用、是否重跑分别统计。
5. 每次正式实验前先跑 5 个任务的小矩阵，确认 agent 版本、模型名和计费记录都正确。
