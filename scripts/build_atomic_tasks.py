from __future__ import annotations

import ast
import shutil
from dataclasses import dataclass
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"


@dataclass(frozen=True)
class AtomicTaskSpec:
    domain: str
    task_id: str
    parent_task: str
    title: str
    description: str
    test_names: tuple[str, ...]
    expected_outputs: tuple[str, ...]
    keywords: tuple[str, ...]
    difficulty: str
    status: str
    dataset_sources: tuple[str, ...]
    skill_candidates: tuple[str, ...]
    input_files: tuple[str, ...]
    output_notes: tuple[str, ...]


ATOMIC_TASKS = [
    AtomicTaskSpec(
        domain="inventory",
        task_id="online-retail-replenishment-schema",
        parent_task="online-retail-replenishment-review",
        title="Online Retail Replenishment Schema",
        description="Produce the replenishment plan file with the required SKU ordering and schema.",
        test_names=("test_replenishment_plan_schema_and_order",),
        expected_outputs=("/app/output/replenishment_plan.csv",),
        keywords=("operations", "inventory", "schema", "replenishment"),
        difficulty="easy",
        status="runnable_smoke_not_skill_sensitive",
        dataset_sources=("uci-online-retail-ii",),
        skill_candidates=("supply-chain-manager",),
        input_files=("/app/data/daily_sku_demand.csv", "/app/data/current_inventory.csv", "/app/data/inventory_policy.csv"),
        output_notes=("Write one row per SKU in inventory_policy.csv order.", "Use the exact replenishment_plan.csv columns from the parent task."),
    ),
    AtomicTaskSpec(
        domain="inventory",
        task_id="online-retail-replenishment-values",
        parent_task="online-retail-replenishment-review",
        title="Online Retail Replenishment Values",
        description="Compute average demand, reorder points, order quantities, priority bands, and post-order cover.",
        test_names=("test_replenishment_plan_values",),
        expected_outputs=("/app/output/replenishment_plan.csv",),
        keywords=("operations", "inventory", "replenishment", "calculation"),
        difficulty="medium",
        status="runnable_smoke_not_skill_sensitive",
        dataset_sources=("uci-online-retail-ii",),
        skill_candidates=("supply-chain-manager",),
        input_files=("/app/data/daily_sku_demand.csv", "/app/data/current_inventory.csv", "/app/data/inventory_policy.csv"),
        output_notes=("Compute the full replenishment_plan.csv values.", "Round demand and cover values to one decimal place."),
    ),
    AtomicTaskSpec(
        domain="inventory",
        task_id="online-retail-exception-register",
        parent_task="online-retail-replenishment-review",
        title="Online Retail Exception Register",
        description="Identify critical and high-priority replenishment exceptions from the replenishment rules.",
        test_names=("test_exceptions_json",),
        expected_outputs=("/app/output/replenishment_exceptions.json",),
        keywords=("operations", "inventory", "exceptions", "risk"),
        difficulty="medium",
        status="runnable_smoke_not_skill_sensitive",
        dataset_sources=("uci-online-retail-ii",),
        skill_candidates=("supply-chain-manager",),
        input_files=("/app/data/daily_sku_demand.csv", "/app/data/current_inventory.csv", "/app/data/inventory_policy.csv"),
        output_notes=("Write replenishment_exceptions.json with exception_count and sorted exceptions.", "Include trigger_rule labels exactly as specified."),
    ),
    AtomicTaskSpec(
        domain="fulfillment",
        task_id="dataco-order-risk-actions",
        parent_task="dataco-control-tower-exception-review",
        title="DataCo Order Risk Actions",
        description="Classify order-level delivery risk and map each order to a control-tower action.",
        test_names=("test_control_tower_actions",),
        expected_outputs=("/app/output/control_tower_actions.csv",),
        keywords=("operations", "logistics", "fulfillment", "control-tower"),
        difficulty="hard",
        status="runnable_external_source",
        dataset_sources=("dataco-smart-supply-chain",),
        skill_candidates=("supply-chain-manager", "logistics-manager", "operations-manager"),
        input_files=("/app/data/order_snapshot.csv", "/app/data/carrier_lane_scorecard.csv", "/app/data/customer_commitments.csv", "/app/data/control_policy.json"),
        output_notes=("Write control_tower_actions.csv sorted by order_id.", "Include risk_band, action_code, owner_function, decision_hierarchy, workflow_phase, reason_code, delay_days, and value_at_risk."),
    ),
    AtomicTaskSpec(
        domain="fulfillment",
        task_id="dataco-lane-risk-register",
        parent_task="dataco-control-tower-exception-review",
        title="DataCo Lane Risk Register",
        description="Build a lane-level risk register from carrier lane reliability and delay metrics.",
        test_names=("test_lane_risk_register",),
        expected_outputs=("/app/output/lane_risk_register.json",),
        keywords=("operations", "logistics", "risk-register", "carrier"),
        difficulty="medium",
        status="runnable_external_source",
        dataset_sources=("dataco-smart-supply-chain",),
        skill_candidates=("supply-chain-manager", "logistics-manager", "operations-manager"),
        input_files=("/app/data/carrier_lane_scorecard.csv", "/app/data/control_policy.json"),
        output_notes=("Write lane_risk_register.json with lane_count and sorted risks.", "Use the carrier_lane_failure taxonomy and escalation rules from the parent task."),
    ),
    AtomicTaskSpec(
        domain="fulfillment",
        task_id="dataco-scorecard-summary",
        parent_task="dataco-control-tower-exception-review",
        title="DataCo Scorecard Summary",
        description="Summarize control-tower risk counts, value at risk, lane count, and action distribution.",
        test_names=("test_scorecard_summary",),
        expected_outputs=("/app/output/scorecard_summary.json",),
        keywords=("operations", "logistics", "scorecard", "summary"),
        difficulty="medium",
        status="runnable_external_source",
        dataset_sources=("dataco-smart-supply-chain",),
        skill_candidates=("supply-chain-manager", "logistics-manager", "operations-manager"),
        input_files=("/app/data/order_snapshot.csv", "/app/data/carrier_lane_scorecard.csv", "/app/data/customer_commitments.csv", "/app/data/control_policy.json"),
        output_notes=("Write scorecard_summary.json.", "Compute risk-band counts, total value at risk, highest risk lane, and action_counts."),
    ),
    AtomicTaskSpec(
        domain="procurement",
        task_id="portland-kraljic-category-matrix",
        parent_task="portland-sourcing-concentration-review",
        title="Portland Kraljic Category Matrix",
        description="Classify procurement categories into Kraljic quadrants from spend impact and supply risk.",
        test_names=("test_kraljic_category_matrix",),
        expected_outputs=("/app/output/kraljic_category_matrix.csv",),
        keywords=("operations", "procurement", "kraljic", "sourcing"),
        difficulty="hard",
        status="runnable_external_source",
        dataset_sources=("open-contracting-portland",),
        skill_candidates=("supply-chain-manager", "operations-manager", "procurement-review"),
        input_files=("/app/data/awards.csv", "/app/data/supplier_profile.csv", "/app/data/category_policy.json"),
        output_notes=("Write kraljic_category_matrix.csv sorted by category.", "Include spend, top supplier share, impact, risk, quadrant, and sourcing strategy."),
    ),
    AtomicTaskSpec(
        domain="procurement",
        task_id="portland-supplier-action-plan",
        parent_task="portland-sourcing-concentration-review",
        title="Portland Supplier Action Plan",
        description="Map category concentration and procurement anti-patterns to supplier actions.",
        test_names=("test_supplier_action_plan",),
        expected_outputs=("/app/output/supplier_action_plan.csv",),
        keywords=("operations", "procurement", "supplier-management", "mitigation"),
        difficulty="hard",
        status="runnable_external_source",
        dataset_sources=("open-contracting-portland",),
        skill_candidates=("supply-chain-manager", "operations-manager", "procurement-review"),
        input_files=("/app/data/awards.csv", "/app/data/supplier_profile.csv", "/app/data/category_policy.json"),
        output_notes=("Write supplier_action_plan.csv sorted by category.", "Include concentration_flag, anti_pattern, mitigation_code, owner_function, and follow_up."),
    ),
    AtomicTaskSpec(
        domain="procurement",
        task_id="portland-procurement-risk-register",
        parent_task="portland-sourcing-concentration-review",
        title="Portland Procurement Risk Register",
        description="Create a procurement risk register for non-empty sourcing anti-patterns.",
        test_names=("test_procurement_risk_register",),
        expected_outputs=("/app/output/procurement_risk_register.json",),
        keywords=("operations", "procurement", "risk-register", "supplier-risk"),
        difficulty="hard",
        status="runnable_external_source",
        dataset_sources=("open-contracting-portland",),
        skill_candidates=("supply-chain-manager", "operations-manager", "procurement-review"),
        input_files=("/app/data/awards.csv", "/app/data/supplier_profile.csv", "/app/data/category_policy.json"),
        output_notes=("Write procurement_risk_register.json with risk_count and sorted risks.", "Evidence must use top_supplier_share=<share> with three decimals."),
    ),
    AtomicTaskSpec(
        domain="scheduling",
        task_id="orlib-recovery-schedule",
        parent_task="orlib-disruption-recovery-control",
        title="OR-Library Recovery Schedule",
        description="Repair a disrupted job-shop schedule while preserving precedence and avoiding downtime windows.",
        test_names=("test_recovery_schedule",),
        expected_outputs=("/app/output/recovery_schedule.csv",),
        keywords=("operations", "manufacturing", "scheduling", "capacity"),
        difficulty="hard",
        status="runnable_external_source",
        dataset_sources=("or-library-jobshop",),
        skill_candidates=("capacity-planning", "operations-manager", "supply-chain-manager"),
        input_files=("/app/data/jobshop_instance.csv", "/app/data/baseline_schedule.csv", "/app/data/machine_downtime.csv"),
        output_notes=("Write recovery_schedule.csv with one row per operation.", "Use baseline start and operation_id ordering as the dispatch sequence."),
    ),
    AtomicTaskSpec(
        domain="scheduling",
        task_id="orlib-schedule-metrics",
        parent_task="orlib-disruption-recovery-control",
        title="OR-Library Schedule Metrics",
        description="Compute schedule feasibility metrics, makespan, and total tardiness for the repaired schedule.",
        test_names=("test_schedule_metrics",),
        expected_outputs=("/app/output/schedule_metrics.json",),
        keywords=("operations", "manufacturing", "scheduling", "metrics"),
        difficulty="medium",
        status="runnable_external_source",
        dataset_sources=("or-library-jobshop",),
        skill_candidates=("capacity-planning", "operations-manager", "supply-chain-manager"),
        input_files=("/app/data/jobshop_instance.csv", "/app/data/baseline_schedule.csv", "/app/data/machine_downtime.csv", "/app/data/customer_priority.csv"),
        output_notes=("Write schedule_metrics.json.", "Report zero violation counts when the generated schedule is feasible."),
    ),
    AtomicTaskSpec(
        domain="scheduling",
        task_id="orlib-bottleneck-action-plan",
        parent_task="orlib-disruption-recovery-control",
        title="OR-Library Bottleneck Action Plan",
        description="Identify the bottleneck machine and map tardy jobs to recovery actions and owners.",
        test_names=("test_bottleneck_report_and_action_plan",),
        expected_outputs=("/app/output/bottleneck_report.json", "/app/output/recovery_action_plan.csv"),
        keywords=("operations", "manufacturing", "bottleneck", "recovery"),
        difficulty="hard",
        status="runnable_external_source",
        dataset_sources=("or-library-jobshop",),
        skill_candidates=("capacity-planning", "operations-manager", "supply-chain-manager"),
        input_files=("/app/data/jobshop_instance.csv", "/app/data/baseline_schedule.csv", "/app/data/machine_downtime.csv", "/app/data/customer_priority.csv", "/app/data/recovery_policy.json"),
        output_notes=("Write bottleneck_report.json and recovery_action_plan.csv.", "Use the operations-control taxonomy from the parent recovery task."),
    ),
]


def python_list(values: tuple[str, ...]) -> str:
    return "[" + ", ".join(f'"{value}"' for value in values) + "]"


def build_test_file(parent_test_file: Path, test_names: tuple[str, ...]) -> str:
    tree = ast.parse(parent_test_file.read_text(encoding="utf-8"))
    selected_nodes: list[ast.stmt] = []
    for node in tree.body:
        if isinstance(node, (ast.Import, ast.ImportFrom)):
            selected_nodes.append(node)
        elif isinstance(node, (ast.Assign, ast.AnnAssign)):
            selected_nodes.append(node)
        elif isinstance(node, ast.FunctionDef) and (node.name.startswith("_") or node.name in test_names):
            selected_nodes.append(node)
    module = ast.Module(body=selected_nodes, type_ignores=[])
    ast.fix_missing_locations(module)
    return ast.unparse(module) + "\n"


def render_task_toml(spec: AtomicTaskSpec) -> str:
    expected_outputs = python_list(spec.expected_outputs)
    dataset_sources = python_list(spec.dataset_sources)
    skill_candidates = python_list(spec.skill_candidates)
    keywords = python_list(spec.keywords)
    return f'''schema_version = "1.1"

[task]
name = "ops/{spec.domain}/{spec.task_id}"
description = "{spec.description}"
authors = [{{ name = "OpsSkillsBench", email = "support@example.com" }}]
keywords = {keywords}

[metadata]
domain = "operations-management"
problem_domain = "{spec.domain}"
difficulty = "{spec.difficulty}"
status = "{spec.status}"
atomic_task = true
parent_task = "{spec.parent_task}"
dataset_sources = {dataset_sources}
skill_candidates = {skill_candidates}
expected_outputs = {expected_outputs}
source_note = "Atomic task split from {spec.parent_task}; provenance and deterministic source slice are inherited from the parent task."

[agent]
timeout_sec = 300.0

[verifier]
timeout_sec = 300.0

[environment]
build_timeout_sec = 600.0
cpus = 1
memory_mb = 1024
allow_internet = false
skills_dir = "/opt/skills"
'''


def render_instruction(spec: AtomicTaskSpec) -> str:
    inputs = "\n".join(f"- `{path}`" for path in spec.input_files)
    outputs = "\n".join(f"- `{path}`" for path in spec.expected_outputs)
    notes = "\n".join(f"{idx}. {note}" for idx, note in enumerate(spec.output_notes, start=1))
    return f"""# {spec.title}

{spec.description}

This is an atomic task split from `{spec.parent_task}`. Complete only the requested output artifact(s), using the same deterministic rules and policy files as the parent task.

## Runtime Inputs

{inputs}

## Required Outputs

{outputs}

## Requirements

{notes}

Keep output values inside the task policy taxonomy where a policy file is provided. Do not run the bundled oracle solution.
"""


def render_task_design(spec: AtomicTaskSpec) -> str:
    outputs = "\n".join(f"- `{path}`" for path in spec.expected_outputs)
    return f"""# {spec.title}

This atomic task belongs to the `{spec.domain}` problem domain.

Parent task: `{spec.parent_task}`

## Purpose

{spec.description}

The task turns one previously nested verifier checkpoint into a standalone benchmark item, so benchmark reports count it as an individual task instead of a hidden sub-question inside a larger scenario.

## Checked Outputs

{outputs}

## Skill Sensitivity

The task keeps the parent task's external-source data and skill candidates, while narrowing the required output to a single operational decision surface. This makes it easier to scale the benchmark to many independent items and to analyze which decision surfaces benefit from provided skills.
"""


def render_source(spec: AtomicTaskSpec) -> str:
    return f"""# Source Inheritance

This atomic task is split from `{spec.parent_task}`.

It inherits the parent task's deterministic data slice, skill provenance, and oracle solution. See:

- `tasks/{spec.parent_task}/source.md`
- `tasks/{spec.parent_task}/environment/data/`
- `tasks/{spec.parent_task}/environment/skills/`

The atomic task owns only its narrowed instruction, metadata, and verifier.
"""


def copy_test_runner(parent: Path, target: Path) -> None:
    shutil.copy2(parent / "tests" / "test.sh", target / "tests" / "test.sh")


def build_atomic_tasks() -> None:
    for spec in ATOMIC_TASKS:
        parent = TASKS_DIR / spec.parent_task
        target = TASKS_DIR / spec.domain / spec.task_id
        if target.exists():
            shutil.rmtree(target)
        (target / "tests").mkdir(parents=True)
        copy_test_runner(parent, target)
        (target / "task.toml").write_text(render_task_toml(spec), encoding="utf-8")
        (target / "instruction.md").write_text(render_instruction(spec), encoding="utf-8")
        (target / "TASK_DESIGN.md").write_text(render_task_design(spec), encoding="utf-8")
        (target / "source.md").write_text(render_source(spec), encoding="utf-8")
        test_text = build_test_file(parent / "tests" / "test_outputs.py", spec.test_names)
        (target / "tests" / "test_outputs.py").write_text(test_text, encoding="utf-8")
        print(f"[atomic-task] {target.relative_to(REPO_ROOT)}")


if __name__ == "__main__":
    build_atomic_tasks()
