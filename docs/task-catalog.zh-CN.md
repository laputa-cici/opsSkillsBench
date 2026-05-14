# 当前任务总览（管理运营方向）

这份文档面向**不是管理运营领域专业人士**的读者，介绍当前工作空间中的 4 个任务分别在做什么、为什么这些任务贴近真实业务、任务数据从哪里来、输入输出是什么、提供了哪些 skill，以及主要在考察 agent 的什么能力。

可以把这 4 个任务理解成 4 类典型运营问题：

1. 补货：库存够不够，要不要下单补货。
2. 履约控制塔：哪些订单和运输线路有交付风险，应该触发什么动作。
3. 采购与供应商管理：某些采购品类是不是过于依赖单一供应商，采购策略是否合理。
4. 生产恢复：机器停机后，排程怎么修复，哪些订单需要升级处理。

---

## 1. `online-retail-replenishment-review`

状态：

- `runnable_smoke_not_skill_sensitive`

一句话理解：

- 这是一个**零售补货复盘任务**，目标是根据真实销售需求历史、当前库存和库存政策，生成一份标准化补货计划。

### 业务背景

在零售或电商场景里，企业每天都要回答一个很现实的问题：

- 哪些商品快断货了？
- 是否应该补货？
- 补多少才合理？
- 哪些缺货风险更紧急？

这类问题通常属于库存管理或 replenishment（补货）工作。它既有业务含义，也有明确公式，因此很适合做 deterministic benchmark。

### 任务具体内容

agent 需要读取每个 SKU 的日需求、当前库存和补货政策，计算：

- 平均日需求
- 补货点
- 推荐订货量
- 优先级
- 补货后库存覆盖天数

此外还要把高风险补货异常单独输出成 JSON。

### 数据来源

主数据集：

- UCI Online Retail II
- 参考说明：[online-retail source.md](/Users/cici/code/opsSkillsBench-main/tasks/online-retail-replenishment-review/source.md)

数据处理方式：

- 从真实交易记录中抽取 SKU 日需求历史。
- 再补充本地冻结的库存与补货政策字段，使任务可重复评分。

### 输入

- [daily_sku_demand.csv](/Users/cici/code/opsSkillsBench-main/tasks/online-retail-replenishment-review/environment/data/daily_sku_demand.csv)
- [current_inventory.csv](/Users/cici/code/opsSkillsBench-main/tasks/online-retail-replenishment-review/environment/data/current_inventory.csv)
- [inventory_policy.csv](/Users/cici/code/opsSkillsBench-main/tasks/online-retail-replenishment-review/environment/data/inventory_policy.csv)

### 输出

- [replenishment_plan.csv](/Users/cici/code/opsSkillsBench-main/.local_runtime/online-retail-replenishment-review/app/output/replenishment_plan.csv)
- `replenishment_exceptions.json`

### 提供的 skill

- [supply-chain-manager](/Users/cici/code/opsSkillsBench-main/tasks/online-retail-replenishment-review/environment/skills/supply-chain-manager/SKILL.md)

这个 skill 主要覆盖：

- 供应链与库存管理基本概念
- 补货点、安全库存、服务水平等框架

### 主要考察 agent 的方向

- 表格读取和聚合
- 基础库存管理公式
- 补货优先级判断
- 严格输出结构

### 目前的定位

这个任务虽然有真实外部数据来源，但在试跑里发现：

- 强模型即使不用 skill，也能靠说明和脚本稳定完成
- skill 条件没有带来明显区分

所以它现在更适合作为：

- runner 冒烟测试

而不是论文主任务。

---

## 2. `dataco-control-tower-exception-review`

状态：

- `runnable_external_source`

一句话理解：

- 这是一个**供应链履约控制塔任务**，目标是从订单与运输表现中找出高风险订单、线路风险和应对动作。

### 业务背景

“控制塔（control tower）”是供应链里很常见的概念。你可以把它理解成一个运营监控中心，负责持续回答这些问题：

- 哪些订单有延迟风险？
- 哪些运输线路（lane）表现变差了？
- 哪些客户会受影响？
- 现在应该通知客户、切换运输方式，还是发起承运商复盘？

这类工作并不只是“算晚了几天”，而是要把数据指标转成可执行的运营动作。

### 任务具体内容

agent 需要完成 3 件事：

1. 对每笔订单做风险分级  
   例如分成 `critical`、`high`、`monitor`

2. 给每笔订单分配 control-tower action  
   例如：
   - `mode_change`
   - `customer_notify`
   - `carrier_review`
   - `monitor`

3. 对线路层面输出风险登记与总览 summary  
   包括：
   - 哪些 lane 风险更大
   - 应用什么 mitigation
   - 整体 value at risk
   - action 分布

### 数据来源

主数据集：

- DataCo SMART Supply Chain
- 参考说明：[dataco source.md](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/source.md)
- provenance：[dataco provenance.md](/Users/cici/code/opsSkillsBench-main/sources/datasets/dataco-smart-supply-chain/provenance.md)

数据处理方式：

- 从原始订单和物流数据中构造订单快照
- 聚合出 lane scorecard
- 加入固定 customer commitment 与 control policy

### 输入

- [order_snapshot.csv](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/data/order_snapshot.csv)
- [carrier_lane_scorecard.csv](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/data/carrier_lane_scorecard.csv)
- [customer_commitments.csv](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/data/customer_commitments.csv)
- [control_policy.json](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/data/control_policy.json)

### 输出

- `control_tower_actions.csv`
- `lane_risk_register.json`
- `scorecard_summary.json`

### 提供的 skill

- [supply-chain-manager](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/skills/supply-chain-manager/SKILL.md)
- [logistics-manager](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/skills/logistics-manager/SKILL.md)
- [operations-manager](/Users/cici/code/opsSkillsBench-main/tasks/dataco-control-tower-exception-review/environment/skills/operations-manager/SKILL.md)

这些 skill 可以简单理解为：

- `supply-chain-manager`
  - 功能：提供供应链整体视角，比如服务、成本、韧性等决策框架。
  - 对任务的帮助：帮助 agent 理解为什么某些订单和线路风险要优先按客户服务或供应链韧性来处理。

- `logistics-manager`
  - 功能：提供运输、承运商、线路表现、物流服务水平等物流管理知识。
  - 对任务的帮助：帮助 agent 理解 `otif_rate`、线路风险、承运商复盘、运输方式切换等动作为什么合理。

- `operations-manager`
  - 功能：提供 KPI、流程控制、owner 分配、异常升级等运营管理知识。
  - 对任务的帮助：帮助 agent 把识别出的风险整理成可执行的 action、owner 和 summary，而不是只停留在分类层面。

### 主要考察 agent 的方向

- 从订单和 lane 数据识别履约风险
- 把风险指标映射成具体 action
- 使用框架字段而不是只输出数值
- 进行 risk register 和 summary 汇总
- 保持结构化输出的精确性

### 这个任务为什么重要

相比简单补货任务，它更接近真实运营分析师或 control-tower analyst 的工作：

- 不是只算公式
- 而是要把“延迟、OTIF、客户价值、线路表现”转成运营动作

因此它更有机会体现 skill 是否真的帮助了 agent。

---

## 3. `portland-sourcing-concentration-review`

状态：

- `runnable_external_source`

一句话理解：

- 这是一个**采购集中度与采购策略任务**，目标是判断某个采购品类是否过度依赖头部供应商，并给出采购策略与风险登记。

### 业务背景

组织在采购时，不只是问“花了多少钱”，还要问：

- 某个品类是不是太依赖某一家供应商？
- 这类采购是高风险还是低风险？
- 应该继续合作、重新招标，还是建立第二供应源？

这类问题在采购管理、供应商管理、sourcing strategy 里非常核心。

任务里用到的一个重要概念是 **Kraljic Matrix（克拉利奇矩阵）**。它把采购品类分成 4 类：

- `strategic`
- `leverage`
- `bottleneck`
- `non_critical`

这个矩阵的核心思想是：

- 一边看“这类采购花多少钱、业务影响多大”
- 一边看“供应风险高不高、替代难不难”

不同象限对应不同采购策略。

### 任务具体内容

agent 需要完成 3 件事：

1. 计算每个采购品类的 spend 和头部供应商占比
2. 为每个品类判定 Kraljic 象限和 sourcing strategy
3. 识别 procurement anti-pattern，并生成风险登记与行动计划

这里的 anti-pattern 例如：

- `single_sourcing`
- `price_only_focus`
- `supplier_fragmentation`

### 数据来源

主数据集：

- Open Contracting Data Registry / City of Portland procurement publication
- 参考说明：[portland source.md](/Users/cici/code/opsSkillsBench-main/tasks/portland-sourcing-concentration-review/source.md)
- provenance：[portland provenance.md](/Users/cici/code/opsSkillsBench-main/sources/datasets/portland-procurement/provenance.md)

数据处理方式：

- 从 OCDS CSV 表中抽取 awards、supplier、item classification、buyer bureau
- 映射成固定的 benchmark category
- 冻结阈值与策略映射，便于自动评分

### 输入

- [awards.csv](/Users/cici/code/opsSkillsBench-main/tasks/portland-sourcing-concentration-review/environment/data/awards.csv)
- [supplier_profile.csv](/Users/cici/code/opsSkillsBench-main/tasks/portland-sourcing-concentration-review/environment/data/supplier_profile.csv)
- [category_policy.json](/Users/cici/code/opsSkillsBench-main/tasks/portland-sourcing-concentration-review/environment/data/category_policy.json)

### 输出

- `kraljic_category_matrix.csv`
- `supplier_action_plan.csv`
- `procurement_risk_register.json`

### 提供的 skill

- [supply-chain-manager](/Users/cici/code/opsSkillsBench-main/tasks/portland-sourcing-concentration-review/environment/skills/supply-chain-manager/SKILL.md)
- [operations-manager](/Users/cici/code/opsSkillsBench-main/tasks/portland-sourcing-concentration-review/environment/skills/operations-manager/SKILL.md)

这些 skill 可以简单理解为：

- `supply-chain-manager`
  - 功能：提供采购策略、Kraljic 矩阵、供应商管理和采购 anti-pattern 等知识。
  - 对任务的帮助：帮助 agent 判断一个品类应该属于哪种采购象限，以及是否存在 `single_sourcing`、`price_only_focus` 等问题。

- `operations-manager`
  - 功能：提供运营执行、owner 分配、KPI 和后续跟进机制等知识。
  - 对任务的帮助：帮助 agent 把采购分析结果进一步转成行动计划、责任人和升级路径。

### 主要考察 agent 的方向

- spend aggregation
- top supplier concentration 分析
- Kraljic 分类
- anti-pattern 识别
- 将采购风险映射到 mitigation 和 follow-up
- 对字符串、枚举和 JSON 输出保持精确

### 这个任务为什么重要

这个任务比看起来更难，因为它不是简单财务汇总，而是要做“采购管理意义上的解释”：

- 同样是头部供应商占比高
- 有时意味着 `single_sourcing`
- 有时意味着 `price_only_focus`
- 有时又可能意味着类别本身是 `bottleneck`

这正是领域 skill 可能真正帮助 agent 的地方。

---

## 4. `orlib-disruption-recovery-control`

状态：

- `runnable_external_source`

一句话理解：

- 这是一个**制造排程恢复任务**，目标是在机器停机后，重新排出一份可行 schedule，并给出 bottleneck 报告和恢复动作。

### 业务背景

制造运营里有一个很常见的问题：

- 原计划已经排好了
- 结果某台机器突然停机
- 现在生产顺序要重排
- 同时还要判断哪些订单会延误、要不要加班、要不要通知客户

这类问题本质上是 job-shop scheduling（作业车间调度）里的 disruption recovery（中断恢复）。

它有两层难度：

1. 算法层  
   新排程必须满足机器约束、工序先后顺序、停机窗口约束

2. 运营决策层  
   哪台机器是瓶颈？哪些订单应升级？该采取 `overtime`、`resequencing` 还是 `customer_escalation`？

### 任务具体内容

agent 需要完成 4 件事：

1. 生成新的 `recovery_schedule.csv`
2. 计算 `schedule_metrics.json`
3. 输出 `bottleneck_report.json`
4. 给每个 job 输出 `recovery_action_plan.csv`

这里不仅要排程可行，还要输出管理语义：

- `root_cause`
- `decision_hierarchy`
- `owner_function`
- `skill_framework`

### 数据来源

主数据集：

- OR-Library Job Shop Scheduling
- 当前选用实例：`ft06`
- 参考说明：[orlib source.md](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/source.md)
- provenance：[orlib provenance.md](/Users/cici/code/opsSkillsBench-main/sources/datasets/orlib-jobshop/provenance.md)

数据处理方式：

- 从 OR-Library `jobshop1.txt` 解析 `ft06`
- 生成 baseline schedule
- 注入固定 downtime window
- 加入本地 due date、service criticality 和 recovery policy

### 输入

- [jobshop_instance.csv](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/data/jobshop_instance.csv)
- [baseline_schedule.csv](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/data/baseline_schedule.csv)
- [machine_downtime.csv](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/data/machine_downtime.csv)
- [customer_priority.csv](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/data/customer_priority.csv)
- [recovery_policy.json](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/data/recovery_policy.json)

### 输出

- `recovery_schedule.csv`
- `schedule_metrics.json`
- `bottleneck_report.json`
- `recovery_action_plan.csv`

### 提供的 skill

- [operations-manager](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/skills/operations-manager/SKILL.md)
- [supply-chain-manager](/Users/cici/code/opsSkillsBench-main/tasks/orlib-disruption-recovery-control/environment/skills/supply-chain-manager/SKILL.md)

当前还没有正式导入 `capacity-planning` skill，但它是候选方向。

这些 skill 可以简单理解为：

- `operations-manager`
  - 功能：提供瓶颈管理、约束思维、运营优先级和恢复控制等知识。
  - 对任务的帮助：帮助 agent 不只排出新 schedule，还能解释哪台机器是瓶颈、为什么要加班或升级客户沟通。

- `supply-chain-manager`
  - 功能：提供服务优先级、跨流程协同和供应链恢复视角。
  - 对任务的帮助：帮助 agent 理解为什么某些 job 要优先保护客户承诺，以及恢复动作背后的服务/成本权衡。

如果以后再导入 `capacity-planning` skill，这个任务在产能与瓶颈分析上会更完整。

### 主要考察 agent 的方向

- 排程可行性
- 约束满足
- downtime 避让
- makespan / tardiness 计算
- bottleneck 识别
- 恢复动作映射
- 保持管理枚举字段精确

### 这个任务为什么重要

这个任务很适合区分两类能力：

- 能不能排出一份“数学上可行”的 schedule
- 能不能把结果解释成“运营上可执行”的恢复方案

目前测试里也确实出现了这种现象：

- `recovery_schedule.csv` 和 `schedule_metrics.json` 往往较容易通过
- `bottleneck_report.json` 更容易失败，因为 agent 容易把枚举字段写成自然语言解释

---

## 整体对比

如果把 4 个任务放在一起看，它们分别代表了不同层级的运营管理问题：

| 任务 | 运营主题 | 更偏数据/公式 | 更偏框架/决策 |
| --- | --- | --- | --- |
| `online-retail-replenishment-review` | 库存补货 | 高 | 低 |
| `dataco-control-tower-exception-review` | 履约监控与异常动作 | 中 | 高 |
| `portland-sourcing-concentration-review` | 采购策略与供应商管理 | 中 | 高 |
| `orlib-disruption-recovery-control` | 生产恢复与瓶颈控制 | 高 | 高 |

从 benchmark 设计角度看：

- `online-retail-replenishment-review`
  - 更像链路冒烟测试
- `dataco-control-tower-exception-review`
  - 更适合观察 skill 对履约控制动作的帮助
- `portland-sourcing-concentration-review`
  - 更适合观察 skill 对采购分类和 anti-pattern 判断的帮助
- `orlib-disruption-recovery-control`
  - 更适合观察 agent 在“可行排程”和“管理解释”之间的差异

## 当前推荐的论文主任务

如果目标是写 management-operations 方向的 SkillBench 论文，当前最值得重点分析的是：

1. `dataco-control-tower-exception-review`
2. `portland-sourcing-concentration-review`
3. `orlib-disruption-recovery-control`

原因是这三个任务都已经是：

- 外部来源数据派生
- 可重复评分
- 有明确输入输出
- 有 task-local provided skills
- 更容易体现 skill 是否真的改变 agent 的行为
