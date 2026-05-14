from __future__ import annotations

import json
import subprocess
from pathlib import Path

from adapters.common import AgentRunRequest, AgentRunResult, claude_command_name


def _extract_last_message(stdout_path: Path, last_message_path: Path) -> None:
    last_text = ""
    with stdout_path.open("r", encoding="utf-8") as stream:
        for line in stream:
            line = line.strip()
            if not line:
                continue
            try:
                event = json.loads(line)
            except json.JSONDecodeError:
                last_text = line
                continue

            if event.get("type") == "result" and isinstance(event.get("result"), str):
                last_text = event["result"]
                continue

            if event.get("type") != "assistant":
                continue

            message = event.get("message", {})
            if not isinstance(message, dict):
                continue
            for block in message.get("content", []):
                if isinstance(block, dict) and block.get("type") == "text":
                    last_text = block.get("text", last_text)

    last_message_path.write_text(last_text, encoding="utf-8")


def run_claude(request: AgentRunRequest) -> AgentRunResult:
    # Claude 采用 --print 非交互模式执行，允许其在工作目录内直接改文件。
    stdout_path = request.run_dir / "claude.stream.jsonl"
    stderr_path = request.run_dir / "claude.stderr.log"
    debug_path = request.run_dir / "claude.debug.log"
    last_message_path = request.run_dir / "claude.last_message.txt"

    command = [
        claude_command_name(),
        "--print",
        "--permission-mode",
        "bypassPermissions",
        "--output-format",
        "stream-json",
        "--verbose",
        "--include-hook-events",
        "--debug-file",
        str(debug_path),
        f"--add-dir={request.workdir}",
    ]

    if request.model:
        command.extend(["--model", request.model])

    command.append(request.prompt)

    with stdout_path.open("w", encoding="utf-8") as stdout, stderr_path.open("w", encoding="utf-8") as stderr:
        completed = subprocess.run(command, cwd=str(request.workdir), stdout=stdout, stderr=stderr)

    _extract_last_message(stdout_path, last_message_path)

    return AgentRunResult(
        agent="claude",
        command=command,
        returncode=completed.returncode,
        stdout_path=stdout_path,
        stderr_path=stderr_path,
    )
