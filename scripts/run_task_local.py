from __future__ import annotations

import argparse
import csv
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


# 仓库内统一路径，确保所有运行产物都留在项目目录里。
REPO_ROOT = Path(__file__).resolve().parents[1]
TASKS_DIR = REPO_ROOT / "tasks"
RUNTIME_DIR = REPO_ROOT / ".local_runtime"
RESULTS_DIR = REPO_ROOT / ".local_results"


def runtime_root(task_name: str) -> Path:
    # 每个任务都使用独立的本地运行目录，避免互相污染。
    return RUNTIME_DIR / task_name


def app_root(task_name: str) -> Path:
    # 在仓库内使用统一的 /app 风格目录结构。
    return runtime_root(task_name) / "app"


def tests_root(task_name: str) -> Path:
    # 准备好的测试文件放在任务运行目录旁边，保证一次运行自包含。
    return runtime_root(task_name) / "tests"


def remove_if_exists(path: Path) -> None:
    # 统一处理文件和目录的清理逻辑。
    if path.exists():
        if path.is_dir():
            shutil.rmtree(path, onerror=handle_remove_readonly)
        else:
            path.unlink()


def handle_remove_readonly(func, path, exc_info) -> None:
    # Windows 下复制后的文件可能带只读属性，先放宽权限再重试删除。
    if not os.path.exists(path):
        return
    os.chmod(path, 0o700)
    try:
        func(path)
    except FileNotFoundError:
        # 并发清理时目标可能已被其他进程删掉，这种情况可安全忽略。
        return


def copy_tree_contents(src: Path, dst: Path) -> None:
    # 复制目录内容时不保留源文件元数据，减少 Windows 下重复运行时的权限问题。
    dst.mkdir(parents=True, exist_ok=True)
    for item in src.iterdir():
        target = dst / item.name
        if item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            target.write_bytes(item.read_bytes())


def task_dir(task_name: str) -> Path:
    # 根据任务名定位目录；如果不存在，就给出可用任务列表。
    path = TASKS_DIR / task_name
    if not path.exists():
        known = sorted(p.name for p in TASKS_DIR.iterdir() if p.is_dir())
        raise SystemExit(f"Unknown task '{task_name}'. Available tasks: {', '.join(known)}")
    return path


def all_task_names() -> list[str]:
    # 固定排序，方便批量运行结果在不同执行之间对比。
    return sorted(p.name for p in TASKS_DIR.iterdir() if p.is_dir())


def patch_text_paths(text: str, task_name: str) -> str:
    # 把任务里的绝对路径重写为仓库内的本地运行路径。
    app = app_root(task_name).as_posix()
    tests = tests_root(task_name).as_posix()
    text = text.replace("/app", app)
    text = text.replace("/tests", tests)
    text = text.replace("/logs/verifier", (runtime_root(task_name) / "logs" / "verifier").as_posix())
    return text


def prepare(task_name: str) -> None:
    # 把任务所需的数据和测试文件准备到本地运行目录中。
    task = task_dir(task_name)
    data_src = task / "environment" / "data"
    tests_src = task / "tests"

    app = app_root(task_name)
    data_dst = app / "data"
    output_dst = app / "output"
    tests_dst = tests_root(task_name)

    # 每次 prepare 都刷新输入、输出和测试目录，避免 benchmark 复用上一次运行的输出。
    remove_if_exists(data_dst)
    remove_if_exists(output_dst)
    remove_if_exists(tests_dst)
    data_dst.mkdir(parents=True, exist_ok=True)
    output_dst.mkdir(parents=True, exist_ok=True)
    tests_dst.mkdir(parents=True, exist_ok=True)

    # 原地刷新任务输入，确保重复运行时始终使用最新的数据和测试文件。
    if data_src.exists():
        copy_tree_contents(data_src, data_dst)
    for item in tests_src.iterdir():
        target = tests_dst / item.name
        if item.suffix == ".py":
            # 测试文件里会引用 /app，这里提前改写成仓库内的本地路径。
            target.write_text(patch_text_paths(item.read_text(encoding="utf-8"), task_name), encoding="utf-8")
        elif item.is_dir():
            shutil.copytree(item, target, dirs_exist_ok=True)
        else:
            target.write_bytes(item.read_bytes())

    print(f"[prepare] task={task_name}")
    print(f"[prepare] data -> {data_dst}")
    print(f"[prepare] output -> {output_dst}")
    print(f"[prepare] tests -> {tests_dst}")


def extract_embedded_python(solve_sh: Path) -> str:
    # 任务 oracle 把 Python 代码嵌在 heredoc 里，这里只提取代码主体。
    text = solve_sh.read_text(encoding="utf-8")
    match = re.search(r"python(?:3)?\s+-\s+<<'PY'\n(.*)\nPY\s*$", text, flags=re.S)
    if not match:
        raise SystemExit(f"Unsupported solve.sh format: {solve_sh}")
    return match.group(1)


def run_oracle(task_name: str) -> None:
    # 在仓库内的本地运行目录上执行任务自带的 oracle 解。
    task = task_dir(task_name)
    solve_sh = task / "solution" / "solve.sh"
    if not solve_sh.exists():
        raise SystemExit(f"Missing oracle script: {solve_sh}")

    code = patch_text_paths(extract_embedded_python(solve_sh), task_name)
    subprocess.run([sys.executable, "-c", code], check=True, cwd=str(REPO_ROOT))
    print(f"[oracle] completed for {task_name}")


def run_tests(task_name: str) -> None:
    # 直接对该任务准备好的测试文件执行 pytest。
    test_file = tests_root(task_name) / "test_outputs.py"
    if not test_file.exists():
        raise SystemExit(f"Missing prepared test file: {test_file}. Run prepare first.")
    subprocess.run(
        [sys.executable, "-m", "pytest", str(test_file), "-rA", "-p", "no:cacheprovider"],
        check=True,
        cwd=str(REPO_ROOT),
    )
    print("[test] passed")


def run_task(task_name: str, do_prepare: bool, do_oracle: bool, do_test: bool) -> dict:
    # 为每个任务记录结构化结果，便于后续批量汇总。
    result = {
        "task": task_name,
        "prepare": do_prepare or do_oracle,
        "oracle": do_oracle,
        "test": do_test,
        "status": "passed",
        "error": None,
        "runtime_dir": str(runtime_root(task_name)),
    }
    try:
        if do_prepare or do_oracle:
            prepare(task_name)
        if do_oracle:
            run_oracle(task_name)
        if do_test:
            run_tests(task_name)
    except subprocess.CalledProcessError as exc:
        # 保留命令级失败信息，避免批量运行时第一处报错就直接中断。
        result["status"] = "failed"
        result["error"] = f"Command failed with exit code {exc.returncode}"
    except Exception as exc:  # pragma: no cover - defensive CLI path
        result["status"] = "failed"
        result["error"] = str(exc)
    if result["status"] != "passed":
        print(f"[failed] task={task_name} error={result['error']}")
    return result


def write_summary(results: list[dict]) -> tuple[Path, Path]:
    # 同时写出机器可读的 JSON 和便于查看的 CSV 汇总。
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    ts = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    json_path = RESULTS_DIR / f"local-run-{ts}.json"
    csv_path = RESULTS_DIR / f"local-run-{ts}.csv"
    summary = {
        "generated_at_utc": ts,
        "repo_root": str(REPO_ROOT),
        "results": results,
        "passed": sum(1 for r in results if r["status"] == "passed"),
        "failed": sum(1 for r in results if r["status"] != "passed"),
    }
    json_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")

    with csv_path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=["task", "status", "prepare", "oracle", "test", "runtime_dir", "error"],
        )
        writer.writeheader()
        for row in results:
            writer.writerow(
                {
                    "task": row["task"],
                    "status": row["status"],
                    "prepare": row["prepare"],
                    "oracle": row["oracle"],
                    "test": row["test"],
                    "runtime_dir": row["runtime_dir"],
                    "error": row["error"] or "",
                }
            )

    return json_path, csv_path


def print_next_steps(task_name: str) -> None:
    # 对只执行 prepare 的情况，给出下一步人工操作提示。
    print("")
    print("Next steps:")
    print(f"1. Read: {task_dir(task_name) / 'instruction.md'}")
    print(f"2. Put outputs under: {app_root(task_name) / 'output'}")
    print(f"3. Run tests with: python scripts/run_task_local.py {task_name} --test")


def main() -> None:
    # 统一支持单任务运行和简单批量运行。
    parser = argparse.ArgumentParser(description="Run benchmark tasks locally.")
    parser.add_argument("task", nargs="?", help="Task directory name under tasks/")
    parser.add_argument("--all", action="store_true", help="Run the same action across all tasks.")
    parser.add_argument("--prepare", action="store_true", help="Prepare /app/data, /app/output, /tests for the task.")
    parser.add_argument("--oracle", action="store_true", help="Run the task's oracle solution after preparation.")
    parser.add_argument("--test", action="store_true", help="Run pytest against the prepared task.")
    parser.add_argument("--clean", action="store_true", help="Remove the local runtime folder for the selected task.")
    args = parser.parse_args()

    if not args.task and not args.all:
        raise SystemExit("Provide a task name or use --all.")

    # 批量模式下处理所有任务，否则只处理指定任务。
    targets = all_task_names() if args.all else [args.task]

    if args.clean:
        # 清理操作只作用于仓库内的本地运行目录。
        for task_name in targets:
            remove_if_exists(runtime_root(task_name))
            print(f"[clean] removed {runtime_root(task_name)}")
        return

    if not any([args.prepare, args.oracle, args.test]):
        # 默认只做 prepare，保证第一次本地使用时更稳妥。
        args.prepare = True

    results = []
    for task_name in targets:
        results.append(run_task(task_name, args.prepare, args.oracle, args.test))
        if args.prepare and not args.oracle and not args.test and not args.all:
            print_next_steps(task_name)

    if len(results) > 1 or args.test or args.oracle:
        json_path, csv_path = write_summary(results)
        print(f"[summary-json] {json_path}")
        print(f"[summary-csv] {csv_path}")

    # 只要本次运行里有任务失败，就返回非零退出码。
    failed = [r for r in results if r["status"] != "passed"]
    if failed:
        print("[result] failures detected")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
