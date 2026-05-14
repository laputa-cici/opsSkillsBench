from __future__ import annotations

import subprocess
from pathlib import Path

from adapters.common import AgentRunRequest, AgentRunResult, codex_command_name


def run_codex(request: AgentRunRequest) -> AgentRunResult:
    # Codex 采用非交互 exec 模式执行，日志写入本次运行目录。
    stdout_path = request.run_dir / "codex.stdout.log"
    stderr_path = request.run_dir / "codex.stderr.log"

    command = [
        codex_command_name(),
        "exec",
        request.prompt,
        "--skip-git-repo-check",
        "--sandbox",
        "workspace-write",
        "--cd",
        str(request.workdir),
        "--output-last-message",
        str(request.run_dir / "codex.last_message.txt"),
    ]

    if request.model:
        command.extend(["--model", request.model])

    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        completed = subprocess.run(command, cwd=str(request.workdir), stdout=stdout, stderr=stderr)

    return AgentRunResult(
        agent="codex",
        command=command,
        returncode=completed.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
