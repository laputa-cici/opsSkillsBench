# 原子题扩展清单

更新日期：2026-05-14

本清单参考 `docs/Operations领域适合做SkillsBench工作的题目建议.pdf`，把 Operations 领域的题目方向整理成可继续扩展的 atomic task backlog。当前已先把已有 4 个场景题拆成 12 个可运行原子题；后续扩题应继续沿用 `tasks/<problem-domain>/<task-id>/` 结构。

## 设计原则

1. 一个 atomic task 只考察一个明确决策面，例如风险分级、动作映射、供应商选择、排程可行性或风险登记。
2. 每个问题域可以有很多题，题目数量通过目录数增长，而不是把更多子问题塞进一个大题。
3. 新题仍然需要 deterministic verifier：允许业务语义复杂，但输出枚举、阈值、排序和计数必须可复现。
4. 新题优先复用公开数据集的小切片，并把 raw 数据保留在 ignored `sources/datasets/**/raw/`。

## 1. Inventory / 库存补货与缺货风险

PDF 建议场景：区域零售商每周根据历史需求、当前库存、在途订单和供应前置期决定补货、人工复核或加急处理。

推荐数据源：

- Store Item Demand Forecasting
- M5 Forecasting
- Rossmann Store Sales
- 现有 UCI Online Retail II 切片可继续做 smoke 或轻量变体

可新增 atomic tasks：

| Task idea | Checked output | Skill-sensitive surface |
| --- | --- | --- |
| `inventory/sku-demand-cleaning-flags` | `demand_quality_flags.csv` | 缺失、重复、负销量、日期连续性 |
| `inventory/promotion-spike-classifier` | `demand_spike_register.json` | promotion/spike/outlier 区分 |
| `inventory/abc-xyz-classification` | `sku_abc_xyz_matrix.csv` | ABC/XYZ 分类和重要性排序 |
| `inventory/safety-stock-reorder-point` | `inventory_policy_update.csv` | 安全库存、服务水平、reorder point |
| `inventory/inbound-eta-risk-cover` | `inbound_cover_assessment.csv` | 在途 ETA 是否覆盖缺货风险 |
| `inventory/expedite-review-action-map` | `inventory_action_plan.csv` | `NO_ACTION` / `REORDER` / `REVIEW` / `EXPEDITE` |
| `inventory/reason-code-register` | `inventory_reason_codes.json` | `LOW_STOCK`、`INBOUND_SUFFICIENT`、`EXPEDITE_RISK` 等原因标签 |

## 2. Fulfillment / 订单分配与履约优先级

PDF 建议场景：电商平台履约计划员根据订单、仓库库存、处理能力和配送时效决定分仓、拆单、加急或人工复核。

推荐数据源：

- Brazilian E-Commerce Public Dataset by Olist
- Instacart Market Basket Analysis
- Online Retail Dataset
- 现有 DataCo SMART Supply Chain 可继续扩展 control-tower 变体

可新增 atomic tasks：

| Task idea | Checked output | Skill-sensitive surface |
| --- | --- | --- |
| `fulfillment/order-data-quality-review` | `order_data_quality_flags.csv` | 取消订单、重复订单、异常需求、缺失仓库 |
| `fulfillment/nearest-feasible-dc` | `warehouse_assignment.csv` | 有库存且可履约仓库选择 |
| `fulfillment/capacity-aware-allocation` | `capacity_adjusted_assignment.csv` | 仓库剩余处理能力和负荷平衡 |
| `fulfillment/sla-risk-estimator` | `sla_risk_register.json` | 处理时间、运输时间、承诺送达约束 |
| `fulfillment/split-order-decision` | `split_order_plan.csv` | 单仓 vs 多仓拆单、拆单成本和包裹数 |
| `fulfillment/expedite-priority-queue` | `fulfillment_priority_queue.csv` | 急单、高价值订单、临近 SLA 优先级 |
| `fulfillment/allocation-reason-codes` | `allocation_reason_codes.json` | `NEAREST_FEASIBLE_DC`、`SPLIT_REQUIRED`、`CAPACITY_RISK`、`SLA_RISK` |

## 3. Scheduling / 生产排程与产能平衡

PDF 建议场景：制造企业生产计划员根据订单需求、机器产能、工序顺序和交期要求决定加工顺序、优先排产、延后或复核。

推荐数据源：

- OR-Library Job Shop Scheduling
- Taillard Flow Shop Scheduling Benchmark
- Kaggle Manufacturing Process Dataset

可新增 atomic tasks：

| Task idea | Checked output | Skill-sensitive surface |
| --- | --- | --- |
| `scheduling/work-order-data-review` | `work_order_quality_flags.csv` | 缺失工序、不可加工机器、异常加工时间 |
| `scheduling/operation-precedence-check` | `precedence_validation.json` | 工序依赖和同工单顺序 |
| `scheduling/bottleneck-resource-ranking` | `bottleneck_ranking.csv` | 机器负荷、利用率、约束资源 |
| `scheduling/due-date-risk-score` | `job_due_date_risk.csv` | 缓冲时间、剩余加工时间、交期风险 |
| `scheduling/finite-capacity-dispatch` | `finite_capacity_schedule.csv` | 机器可行性和有限产能 |
| `scheduling/setup-efficiency-grouping` | `setup_grouping_plan.csv` | 换型成本和批量集中排产 |
| `scheduling/job-action-reason-codes` | `job_action_plan.csv` | `SCHEDULE` / `EXPEDITE` / `DELAY` / `REVIEW` 与 reason code |

## 4. Procurement / 采购与供应商风险

PDF 建议场景：制造企业采购计划员根据物料需求、供应商价格、交付表现、质量表现和供应风险决定供应商、采购量、分单、加急或复核。

推荐数据源：

- Vendor Performance Dataset
- Procurement KPI Analysis Dataset
- SCMS Delivery History Dataset
- 现有 Portland procurement 切片可继续做采购策略和集中度变体

可新增 atomic tasks：

| Task idea | Checked output | Skill-sensitive surface |
| --- | --- | --- |
| `procurement/purchase-gap-calculation` | `purchase_gap.csv` | 需求、当前库存、在途和安全库存 |
| `procurement/supplier-scorecard-ranking` | `supplier_scorecard.csv` | 单价、交期、OTD、质量、取消率 |
| `procurement/total-cost-supplier-choice` | `supplier_recommendation.csv` | 总拥有成本而非最低单价 |
| `procurement/supply-risk-classifier` | `supply_risk_register.json` | 交期波动、质量风险、单一来源依赖 |
| `procurement/split-order-resilience-plan` | `split_order_plan.csv` | 多源采购与供应韧性 |
| `procurement/moq-capacity-contract-check` | `supplier_constraint_violations.csv` | MOQ、产能、合同上限 |
| `procurement/procurement-action-reason-codes` | `procurement_action_plan.csv` | `NO_ORDER` / `PLACE_ORDER` / `SPLIT_ORDER` / `EXPEDITE` / `REVIEW` |

## Suggested Next Build Order

1. `fulfillment/nearest-feasible-dc`
2. `fulfillment/capacity-aware-allocation`
3. `inventory/abc-xyz-classification`
4. `inventory/safety-stock-reorder-point`
5. `procurement/supplier-scorecard-ranking`
6. `procurement/supply-risk-classifier`
7. `scheduling/bottleneck-resource-ranking`
8. `scheduling/due-date-risk-score`

这些题都适合先做成小数据切片和单输出 verifier，再逐步扩成更多数据变体。
