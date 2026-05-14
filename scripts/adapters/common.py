from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
import shutil
import sys


@dataclass
class AgentRunRequest:
    # 任务名，例如 inventory-replenishment-plan。
    task_name: str
    # 被测模型名，例如 gpt-5.4 或 claude-sonnet-4-5。
    model: str | None
    # skill 条件：no_skill / provided_skills / self_created_skills。
    skill_condition: str
    # 用于执行 agent 的工作目录。
    workdir: Path
    # 实际要发送给 agent 的提示词。
    prompt: str
    # 本次运行产物目录。
    run_dir: Path


@dataclass
class AgentRunResult:
    # 适配器名，例如 codex 或 claude。
    agent: str
    # 执行命令，便于后续复现实验。
    command: list[str]
    # 子进程退出码。
    returncode: int
    # 标准输出日志路径。
    stdout_path: Path
    # 标准错误日志路径。
    stderr_path: Path


def resolve_executable(*candidates: str) -> str:
    # 按顺序查找可执行文件，兼容 Windows 与 macOS/Linux 的不同命名。
    for name in candidates:
        resolved = shutil.which(name)
        if resolved:
            return resolved
    joined = ", ".join(candidates)
    raise FileNotFoundError(f"Executable not found. Tried: {joined}")


def codex_command_name() -> str:
    # Windows 常见为 codex.exe，其它平台通常是 codex。
    if sys.platform.startswith("win"):
        return resolve_executable("codex.exe", "codex")
    return resolve_executable("codex")


def claude_command_name() -> str:
    # Claude 在不同平台上可能是 claude、claude.ps1 或包装脚本。
    if sys.platform.startswith("win"):
        return resolve_executable("claude", "claude.ps1")
    return resolve_executable("claude")
