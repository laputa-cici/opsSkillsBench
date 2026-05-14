from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path

from adapters.claude_adapter import run_claude
from adapters.codex_adapter import run_codex
from adapters.common import AgentRunRequest
from run_task_local import all_task_names, app_root, inherited_asset_dir, prepare, run_tests, runtime_root, task_dir


# benchmark 级结果统一放在项目目录内，便于后续论文实验归档。
BENCHMARK_RESULTS_DIR = Path(__file__).resolve().parents[1] / ".benchmark_runs"
REPO_ROOT = Path(__file__).resolve().parents[1]


def agent_workdir(task_name: str, skill_condition: str) -> Path:
    # no_skill 条件下尽量把 agent 限制在 runtime /app 内，避免它顺手读取仓库里的 task-local skills。
    # provided_skills 条件保留仓库根目录，因为 prompt 会显式暴露 task-local skill 路径。
    if skill_condition == "provided_skills":
        return REPO_ROOT
    return app_root(task_name)


def build_prompt(task_name: str, skill_condition: str, run_dir: Path) -> str:
    # 根据任务说明和 skill 条件拼出一份明确、可复现实验的 agent prompt。
    task_path = task_dir(task_name)
    instruction_path = task_path / "instruction.md"
    instruction_text = instruction_path.read_text(encoding="utf-8").strip()

    runtime_data_dir = app_root(task_name) / "data"
    runtime_output_dir = app_root(task_name) / "output"
    skills_dir = inherited_asset_dir(task_path, "environment/skills")
    agent_artifacts_dir = run_dir / "agent_artifacts"
    agent_artifacts_dir.mkdir(parents=True, exist_ok=True)

    skill_block = ""
    if skill_condition == "no_skill":
        skill_block = ""
    elif skill_condition == "provided_skills":
        skill_block = (
            f"You may use the task-local skill files under: {skills_dir}\n"
            "Use them if they help you complete the task."
        )
    elif skill_condition == "self_created_skills":
        skill_block = (
            "Do not use any prebuilt task skill files.\n"
            f"You may create your own notes, procedures, or skill files under: {agent_artifacts_dir}\n"
            "If you create such files, reuse them during the task if helpful."
        )
    else:
        raise ValueError(f"Unsupported skill_condition: {skill_condition}")

    skill_section = f"\nSkill condition:\n{skill_block}\n" if skill_block else ""

    return f"""Task name: {task_name}

Task instruction:
{instruction_text}

Runtime data directory:
{runtime_data_dir}

Runtime output directory:
{runtime_output_dir}

Important requirements:
- Read inputs from the runtime data directory above.
- Write final task outputs into the runtime output directory above.
- Do not run the bundled oracle solution.
- Finish the task directly by editing or creating files in the workspace.
- When you are done, stop after producing the required outputs.
{skill_section}
"""


def run_agent(agent: str, request: AgentRunRequest):
    # 根据 agent 名分发到对应适配器。
    if agent == "codex":
        return run_codex(request)
    if agent == "claude":
        return run_claude(request)
    raise ValueError(f"Unsupported agent: {agent}")


def run_single(task_name: str, agent: str, model: str | None, skill_condition: str, run_root: Path) -> dict:
    # 单次 benchmark run：prepare -> 调 agent -> test -> 记录结果。
    prepare(task_name)

    task_run_dir = run_root / task_name
    task_run_dir.mkdir(parents=True, exist_ok=True)

    prompt = build_prompt(task_name, skill_condition, task_run_dir)
    (task_run_dir / "prompt.txt").write_text(prompt, encoding="utf-8")

    request = AgentRunRequest(
        task_name=task_name,
        model=model,
        skill_condition=skill_condition,
        workdir=agent_workdir(task_name, skill_condition),
        prompt=prompt,
        run_dir=task_run_dir,
    )

    start = time.time()
    agent_result = run_agent(agent, request)
    elapsed = round(time.time() - start, 3)

    test_status = "not_run"
    test_error = None
    if agent_result.returncode == 0:
        try:
            run_tests(task_name)
            test_status = "passed"
        except Exception as exc:  # pragma: no cover - CLI integration path
            test_status = "failed"
            test_error = str(exc)
    else:
        test_status = "skipped"

    result = {
        "task": task_name,
        "agent": agent,
        "model": model,
        "skill_condition": skill_condition,
        "agent_returncode": agent_result.returncode,
        "test_status": test_status,
        "test_error": test_error,
        "elapsed_sec": elapsed,
        "command": agent_result.command,
        "stdout_log": str(agent_result.stdout_path),
        "stderr_log": str(agent_result.stderr_path),
        "prompt_file": str(task_run_dir / "prompt.txt"),
        "runtime_dir": str(runtime_root(task_name)),
    }

    (task_run_dir / "result.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result


def write_run_summary(results: list[dict], run_root: Path) -> Path:
    # 把整个 benchmark run 的汇总信息写成 JSON，供后续统计分析使用。
    summary = {
        "generated_at_utc": datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ"),
        "results": results,
        "passed": sum(1 for r in results if r["test_status"] == "passed"),
        "failed": sum(1 for r in results if r["test_status"] != "passed"),
    }
    summary_path = run_root / "summary.json"
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    return summary_path


def main() -> None:
    # 第一版 runner 先支持 codex / claude，两者共享同一套 prepare 和 verify 流程。
    parser = argparse.ArgumentParser(description="Run benchmark tasks against local agent CLIs.")
    parser.add_argument("--agent", required=True, choices=["codex", "claude"])
    parser.add_argument("--model", default=None, help="Optional model name passed through to the agent CLI.")
    parser.add_argument(
        "--skill-condition",
        default="provided_skills",
        choices=["no_skill", "provided_skills", "self_created_skills"],
    )
    parser.add_argument("--task", default=None, help="Task name under tasks/.")
    parser.add_argument("--all", action="store_true", help="Run all tasks.")
    args = parser.parse_args()

    if not args.task and not args.all:
        raise SystemExit("Provide --task <task-name> or use --all.")

    targets = all_task_names() if args.all else [args.task]

    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    run_root = BENCHMARK_RESULTS_DIR / f"{args.agent}-{args.skill_condition}-{ts}"
    run_root.mkdir(parents=True, exist_ok=True)

    results = []
    for task_name in targets:
        print(f"[benchmark] task={task_name} agent={args.agent} skill_condition={args.skill_condition}")
        results.append(run_single(task_name, args.agent, args.model, args.skill_condition, run_root))

    summary_path = write_run_summary(results, run_root)
    print(f"[benchmark-summary] {summary_path}")

    failed = [r for r in results if r["test_status"] != "passed"]
    if failed:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
