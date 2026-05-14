# Task Redesign After First Pilot

Last updated: 2026-04-07

## Diagnosis

The first runnable task, `online-retail-replenishment-review`, is not skill-sensitive enough.

Observed pilot results:

| Agent | Skill condition | Result pattern |
| --- | --- | --- |
| Codex | `provided_skills` | Solved by creating a script; no meaningful evidence of skill use. |
| Codex | `no_skill` | Solved by creating a script; same failure family as `provided_skills`. |
| Claude Code | `provided_skills` | Solved by creating a script; execution trace shows direct data processing. |
| Claude Code | `no_skill` | Solved by creating a script; same failure family as `provided_skills`. |

Conclusion:

The current task mostly tests deterministic CSV processing. It does not force the agent to use domain skill content such as supply-chain hierarchy, Kraljic segmentation, supplier scorecards, SOPs, risk documentation, or Plan-Source-Make-Deliver-Return workflow mapping.

## Redesign Principle

A management-operations SkillBench task should not be a pure ETL/math task. It should require the agent to:

1. Select an applicable operations framework.
2. Apply that framework to noisy but deterministic business data.
3. Produce machine-checkable decisions, not just prose.
4. Explain or encode framework evidence in a verifiable output.
5. Balance multiple operational objectives such as service, cost, cash, resilience, and sustainability.

The benchmark should still be reproducible: all framework-driven choices must map to frozen rules in tests.

## Skill-Sensitive Task Pattern

Use this structure for redesigned tasks:

| Layer | Purpose | Example checked output |
| --- | --- | --- |
| Data calculation | Prevent trivial hallucination and test data handling. | Demand, delivery delay, supplier share, OTIF, CV, value at risk. |
| Framework selection | Force use of skill concepts. | `framework_layer`, `decision_hierarchy`, `kraljic_quadrant`, `risk_type`. |
| Operational decision | Convert analysis to action. | `action_code`, `owner_function`, `control_plan`, `escalation_level`. |
| Risk/SOP evidence | Make skill use auditable. | `skill_reference`, `anti_pattern`, `sop_phase`, `mitigation_code`. |
| Deterministic scoring | Preserve benchmark repeatability. | Exact enum sets, ranking, counts, thresholded rules. |

## Redesigned Task Candidates

### 1. `retail-sop-replenishment-control`

Dataset:

- UCI Online Retail II derived SKU demand history.

Provided skills:

- `supply-chain-manager`
- Optional later: public `demand-forecasting` skill if a licensable upstream package is found.

Why this is better than the current replenishment task:

- The task becomes a control-tower review, not just a reorder quantity calculation.
- The agent must classify each SKU exception using skill concepts:
  - supply-chain hierarchy: `service`, `cost`, `cash`, `resilience`, `sustainability`
  - workflow phase: `plan`, `source`, `make`, `deliver`, `return`
  - inventory strategy: `A`, `B`, `C`
  - risk type: `demand_surge`, `excess_inventory`, `stockout`, `forecast_ignorance`
  - SOP action: `expedite`, `rebalance_policy`, `review_safety_stock`, `monitor`

Proposed inputs:

| File | Description |
| --- | --- |
| `daily_sku_demand.csv` | Online Retail II-derived demand by SKU/date. |
| `sku_financials.csv` | Unit cost, unit margin, annualized value, holding cost rate. |
| `inventory_policy.csv` | Lead time, service target, minimum order, pack size. |
| `supplier_terms.csv` | Supplier count, lead-time reliability, MOQ, payment terms. |
| `control_policy.json` | Frozen scoring rules and allowed enum values. |

Proposed outputs:

| File | Why it is skill-sensitive |
| --- | --- |
| `inventory_control_plan.csv` | Combines demand math with ABC policy, service/cash tradeoff, and action code. |
| `supply_chain_risk_register.json` | Requires risk taxonomy, mitigation code, workflow phase, and hierarchy priority. |
| `framework_trace.json` | Records which skill framework concepts were applied to each decision. |

Scoring examples:

- `abc_class` must match value-share thresholds.
- `policy_action` must match frozen combinations of stockout risk, value class, lead-time reliability, and cash exposure.
- `hierarchy_priority` must follow service-first rules for stockout risk and cash-first rules for excess A-items.
- `framework_trace` must reference allowed framework concepts from `supply-chain-manager`.

Expected skill effect:

- `provided_skills` should improve framework-field accuracy and risk/action consistency.
- `no_skill` may still compute quantities, but should miss or vary on framework taxonomy.

### 2. `dataco-control-tower-exception-review`

Dataset:

- DataCo SMART Supply Chain, which includes structured supply-chain data and clickstream data for provisioning, production, sales, and commercial distribution.

Provided skills:

- `supply-chain-manager`
- Public `logistics-manager` candidate from SkillsMP / `theneoai/awesome-skills`
- Public `operations-manager` candidate from SkillsMP / `theneoai/awesome-skills`

Proposed inputs:

| File | Description |
| --- | --- |
| `order_snapshot.csv` | DataCo-derived orders with promised/actual delivery, shipping mode, order value, category, market, customer segment. |
| `carrier_lane_scorecard.csv` | Derived lane-level delay, cost, and reliability aggregates. |
| `customer_commitments.csv` | Service target and escalation rules by customer segment. |
| `control_policy.json` | Frozen mapping from delay risk and value exposure to actions. |

Proposed outputs:

| File | Why it is skill-sensitive |
| --- | --- |
| `control_tower_actions.csv` | Requires delivery exception triage, mode escalation, owner assignment, and service/cost tradeoff. |
| `lane_risk_register.json` | Requires risk documentation and mitigation classification. |
| `scorecard_summary.json` | Requires supplier/carrier scorecard logic and OTIF/perfect-order-style metrics. |

Scoring examples:

- `action_code` must distinguish `expedite`, `carrier_review`, `customer_notify`, `mode_change`, and `monitor`.
- `decision_hierarchy` must prioritize service for premium/high-value delayed orders and cost for low-value non-critical orders.
- `risk_type` must match deterministic combinations of lane delay, value at risk, and customer segment.
- `scorecard_summary` must compute OTIF and rank lanes by risk-adjusted value.

Expected skill effect:

- `provided_skills` should improve the choice of owner/action/risk taxonomy.
- `no_skill` may compute delay counts but should struggle with supply-chain control-tower decisions.

### 3. `portland-sourcing-concentration-review`

Dataset:

- City of Portland procurement data from the Open Contracting Data Registry.

Provided skills:

- `supply-chain-manager`
- Public `operations-manager` candidate
- Optional future `procurement-review` skill after license verification

Proposed inputs:

| File | Description |
| --- | --- |
| `awards.csv` | Supplier/category/award value/date derived from Portland OCDS data. |
| `supplier_profile.csv` | Supplier count, incumbency, bureau exposure, contract type. |
| `category_policy.json` | Frozen thresholds for supplier concentration and supply risk. |

Proposed outputs:

| File | Why it is skill-sensitive |
| --- | --- |
| `kraljic_category_matrix.csv` | Requires spend-impact and supply-risk segmentation. |
| `supplier_action_plan.csv` | Requires sourcing strategy by quadrant, not just aggregation. |
| `procurement_risk_register.json` | Requires anti-pattern and mitigation mapping such as single sourcing or price-only focus. |

Scoring examples:

- `kraljic_quadrant` must match frozen spend-impact and supplier-risk rules.
- `sourcing_strategy` must match the quadrant:
  - strategic: `partnership_development`
  - leverage: `competitive_bidding`
  - bottleneck: `ensure_supply_and_buffer`
  - non_critical: `process_efficiency`
- `anti_pattern` must match deterministic supplier concentration and award history conditions.

Expected skill effect:

- `provided_skills` should improve quadrant and sourcing strategy mapping.
- `no_skill` may aggregate spend but should be less consistent on procurement strategy taxonomy.

### 4. `orlib-disruption-recovery-control`

Dataset:

- OR-Library Job Shop Scheduling, using a small instance such as `ft06`.

Provided skills:

- Public `capacity-planning` candidate if licensable.
- Public `operations-manager` candidate.
- `supply-chain-manager` only as a broad planning/control-tower support skill.

Proposed inputs:

| File | Description |
| --- | --- |
| `jobshop_instance.txt` | OR-Library-derived job routes and processing times. |
| `baseline_schedule.csv` | Initial schedule. |
| `machine_downtime.csv` | Disruption windows. |
| `customer_priority.csv` | Due dates and service criticality. |
| `recovery_policy.json` | Frozen constraints and allowed recovery levers. |

Proposed outputs:

| File | Why it is skill-sensitive |
| --- | --- |
| `recovery_schedule.csv` | Requires feasibility under disruption. |
| `bottleneck_report.json` | Requires bottleneck and service/cost tradeoff classification. |
| `recovery_action_plan.csv` | Requires dispatching/recovery action choices and owner assignment. |

Scoring examples:

- Schedule feasibility remains exact and deterministic.
- `bottleneck_machine` must match deterministic load/slack calculation.
- `recovery_action` must follow policy such as `split_lot`, `overtime`, `resequencing`, or `customer_escalation`.

Expected skill effect:

- Skill benefit should appear in bottleneck/action classification, not only in schedule feasibility.

## Harness Changes Needed

The task redesign should be paired with harness improvements:

1. `no_skill` must physically hide or omit `environment/skills`, not only instruct the agent not to use it.
2. `provided_skills` should expose only the selected public skill(s), not all task-local skills.
3. Runner should record skill access evidence when the agent CLI exposes file/tool traces.
4. Tests should separate:
   - numeric correctness
   - framework taxonomy correctness
   - operational action correctness
   - skill evidence correctness
5. A task should not be frozen if `provided_skills` and `no_skill` runs show identical behavior and identical failure modes.

## Immediate Recommendation

Do not iterate on the current `online-retail-replenishment-review` tests as the primary paper task.

Use it only as a runner smoke test and replace the first paper-facing task with:

```text
dataco-control-tower-exception-review
```

Reason:

- DataCo is closer to end-to-end supply-chain operations than a single retail transaction table.
- It naturally supports service, cost, logistics, fulfillment, customer segment, and delay-risk decisions.
- It can use multiple public skills: `supply-chain-manager`, `logistics-manager`, and `operations-manager`.
- It is easier to design skill-sensitive outputs that remain deterministic and verifiable.
