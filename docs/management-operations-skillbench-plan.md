# Management-Operations SkillBench Plan

Last updated: 2026-04-15

## 1. Objective

Build a benchmark for evaluating how external domain skills affect agent performance on deterministic management-operations tasks.

Core question:

```text
How much do domain skills improve agent completion of real operations tasks,
and can agents create reusable skills when no curated skill is provided?
```

## 2. Required Inputs to the Benchmark

The benchmark should be grounded in:

| Input type | Requirement |
| --- | --- |
| External skills | Skills should come from public skill markets or upstream repositories when license and content are usable. |
| Operations datasets | Datasets should come from public operations, supply-chain, procurement, retail, or scheduling sources. |
| Deterministic task slices | Each task should use a small committed slice derived from a documented source. |
| Provenance | Every task needs `source.md` with URLs, access date, license signal, and transformations. |

## 3. Skill Conditions

| Condition | Design |
| --- | --- |
| `no_skill` | Hide all task-local skills. Agent receives only task instructions and runtime files. |
| `provided_skills` | Expose vetted benchmark skills under the agent's expected skill path. |
| `self_created_skills` | Hide benchmark skills but allow the agent to create and persist its own procedural skills. |

## 4. Current Task Queue

| Task | Workflow | Dataset | Skill candidates | Status |
| --- | --- | --- | --- | --- |
| `online-retail-replenishment-review` | Inventory replenishment | UCI Online Retail II | `supply-chain-manager` | runnable smoke test only; not skill-sensitive enough for paper runs |
| `dataco-control-tower-exception-review` | Logistics exception control tower | DataCo SMART Supply Chain | `supply-chain-manager`, `logistics-manager`, `operations-manager` | runnable external-source task; raw DataCo derivation complete |
| `portland-sourcing-concentration-review` | Procurement sourcing concentration review | Open Contracting Portland | `supply-chain-manager`, `operations-manager`, `procurement-review` | runnable external-source task; raw Portland derivation complete |
| `orlib-disruption-recovery-control` | Manufacturing disruption recovery control | OR-Library Job Shop | `capacity-planning`, `operations-manager`, `supply-chain-manager` | runnable external-source task; `ft06` derivation complete |

## 5. Evaluation Matrix

Start with a small pilot:

| Dimension | Pilot |
| --- | --- |
| Tasks | 1-2 runnable external-source tasks |
| Agents | `Codex`, `Claude Code` |
| Models | 1-2 per agent |
| Skill conditions | `no_skill`, `provided_skills`, `self_created_skills` |
| Repetitions | 3 |

Scale after the first runnable task passes oracle and agent smoke tests.

## 6. Metrics

Primary metrics:

- Full task pass rate
- Test pass ratio
- Constraint feasibility rate
- Normalized deterministic score

Efficiency metrics:

- Wall-clock time
- Token usage when available
- Tool-call count
- Estimated cost

Skill metrics:

- Skill discovery/use rate
- Delta from `no_skill` to `provided_skills`
- Self-created skill success rate
- Reuse of self-created skills within or across runs

## 7. Task Definition of Done

A task is runnable when:

| Requirement | Done when |
| --- | --- |
| Source | `source.md` includes dataset and skill provenance. |
| Data | `environment/data/` contains a small deterministic slice. |
| Skills | `environment/skills/` contains verified external or clearly adapted skills. |
| Oracle | `solution/solve.sh` generates valid outputs. |
| Tests | `tests/test_outputs.py` verifies schemas, values, and constraints. |
| Runner | `scripts/run_task_local.py <task> --oracle --test` passes. |

## 8. Immediate Work Order

1. Treat `online-retail-replenishment-review` as a runner smoke test, not a paper-facing skill benchmark.
2. Continue the post-0414 iteration: keep Portland as the leading skill-sensitive task, tighten DataCo taxonomy boundaries, and decide whether OR-Library needs lightweight skill-evidence fields.
3. Add `self_created_skills` support and isolate self-created skill storage from benchmark-provided skills.
4. Decide whether to import an additional `capacity-planning` skill or continue using `operations-manager` for bottleneck reasoning.
5. Add tests that separately score numeric correctness, framework taxonomy, operational action mapping, and skill-evidence fields.

## 9. Pilot Run Log

| Date UTC | Task | Agent | Model | Skill condition | Result | Notes |
| --- | --- | --- | --- | --- | --- | --- |
| 2026-04-07T03:12:40Z | `online-retail-replenishment-review` | `codex` | `gpt-5.4` | `provided_skills` | failed, `2 passed / 1 failed` | Numeric CSV output passed; JSON `trigger_rule` semantic label did not match expected convention. See `docs/results/20260407-codex-provided-skills-online-retail.md`. |
| 2026-04-07T06:15:01Z | `online-retail-replenishment-review` | `codex` | `gpt-5.4` | `no_skill` | failed, `2 passed / 1 failed` | Same failure family as provided-skills run: numeric CSV output passed; JSON `trigger_rule` semantic label did not match expected convention. See `docs/results/20260407-codex-no-skill-online-retail.md`. |
| 2026-04-07T08:42:12Z | `online-retail-replenishment-review` | `claude` | `qwen3.5-plus` via Claude Code stream metadata; model argument was not explicit in this historical run | `provided_skills` | failed, `2 passed / 1 failed` | Numeric CSV output passed; JSON `trigger_rule` semantic label did not match expected convention. Execution trace captured in `claude.stream.jsonl`. See `docs/results/20260407-claude-provided-skills-online-retail.md`. |
| 2026-04-07T08:47:24Z | `online-retail-replenishment-review` | `claude` | `qwen3.5-plus` via Claude Code stream metadata; model argument was not explicit in this historical run | `no_skill` | failed, `2 passed / 1 failed` | Numeric CSV output passed; JSON `trigger_rule` used `days_of_cover` instead of expected `current_days_of_cover`. Execution trace captured in `claude.stream.jsonl`. See `docs/results/20260407-claude-no-skill-online-retail.md`. |
| 2026-04-07T14:37:40Z to 2026-04-07T15:06:56Z | 3 redesigned tasks | `codex`, `claude` | `gpt-5.4`, `qwen3.5-plus` via Claude Code stream metadata; Claude model argument was not explicit in this historical matrix | `provided_skills`, `no_skill` | 12-run matrix completed | See `docs/results/20260407-new-task-matrix.md`. |
| 2026-04-08T02:23:24Z to 2026-04-08T02:51:33Z | 3 external-source tasks | `codex`, `claude` | `gpt-5.4`, `qwen3.5-plus` | `provided_skills`, `no_skill` | 12-run matrix completed | See `docs/results/20260408-external-source-matrix.md`. |
| 2026-04-14T10:48:27Z to 2026-04-15T00:43:01Z | 3 external-source tasks after instruction/skill boundary iteration | `codex`, `claude` | `gpt-5.4`, `qwen3.5-plus` | `provided_skills`, `no_skill` | 12-run matrix completed | Portland became more skill-sensitive for Codex; DataCo showed taxonomy drift under both agents; OR-Library still did not separate Codex by skill condition. See `docs/results/20260414-instruction-boundary-iteration-matrix.md`. |
| 2026-04-15T04:35:53Z to 2026-04-15T05:06:45Z | 3 external-source tasks after removing task-level skill leakage | `codex`, `claude` | `gpt-5.4`, `qwen3.5-plus` | `provided_skills`, `no_skill` | 12-run matrix completed | Instruction text, output schema, and policy files no longer expose explicit skill framework labels. Portland remains skill-sensitive for Codex; OR-Library begins to separate Codex by skill condition. See `docs/results/20260415-clean-task-skill-leakage-matrix.md`. |
| 2026-04-15T06:57:19Z to 2026-04-15T07:36:27Z | 3 external-source tasks with neutral `no_skill` prompt | `codex`, `claude` | `gpt-5.4`, `qwen3.5-plus` | `provided_skills`, `no_skill` | 12-run matrix completed | `no_skill` prompt no longer mentions skills. Codex's Portland skill gap disappeared, suggesting earlier no-skill wording changed behavior. See `docs/results/20260415-neutral-no-skill-prompt-matrix.md`. |

Forward-looking convention:

- Codex runs should pass `--model gpt-5.4`.
- Claude Code runs should pass `--model qwen3.5-plus`; a smoke test on 2026-04-08 confirmed the explicit model argument works.

## 10. Redesign Decision After Pilot

The first four pilot runs show that `online-retail-replenishment-review` is not an adequate test of skill benefit. Agents solved the task by creating scripts under both `provided_skills` and `no_skill`, and the observed failures were output-label mismatches rather than domain decision failures.

Design decision:

- Keep `online-retail-replenishment-review` only as a runner smoke test.
- Do not tune its tests to manufacture a pass/fail distinction.
- Move the paper-facing benchmark toward tasks that require explicit operations frameworks, such as control-tower triage, sourcing strategy, risk registers, SOP phases, and service/cost/cash/resilience tradeoffs.
- Use `docs/task-redesign-after-pilot.md` as the redesign brief.
