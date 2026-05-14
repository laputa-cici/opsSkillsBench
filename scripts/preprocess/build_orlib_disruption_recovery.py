#!/usr/bin/env python3
"""Build a disruption-recovery task slice from an OR-Library job-shop instance."""

from __future__ import annotations

import argparse
import csv
import json
from collections import defaultdict
from pathlib import Path


DEFAULT_RAW = Path("sources/datasets/orlib-jobshop/raw/jobshop1.txt")
DEFAULT_OUT = Path("tasks/orlib-disruption-recovery-control/environment/data")

RECOVERY_POLICY = {
    "allowed_actions": ["customer_escalation", "overtime", "resequencing", "monitor"],
    "service_priority": ["high", "medium", "low"],
    "bottleneck_method": "machine_load_plus_downtime_duration",
    "decision_hierarchy": ["customer_commitment", "cost_efficiency", "flexibility_speed"],
    "skill_frameworks": [
        "operations-manager:theory-of-constraints",
        "operations-manager:priority-hierarchy",
        "supply-chain-manager:plan-make-deliver",
    ],
}

SERVICE_CRITICALITY = {
    "J1": "high",
    "J2": "medium",
    "J3": "high",
    "J4": "medium",
    "J5": "low",
    "J6": "high",
}

ORDER_VALUE = {
    "J1": 12000,
    "J2": 7000,
    "J3": 15000,
    "J4": 8500,
    "J5": 4200,
    "J6": 11000,
}


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw", type=Path, default=DEFAULT_RAW)
    parser.add_argument("--out", type=Path, default=DEFAULT_OUT)
    parser.add_argument("--instance", default="ft06")
    return parser.parse_args()


def parse_instance(raw: Path, instance: str) -> list[list[tuple[int, int]]]:
    lines = raw.read_text(encoding="utf-8").splitlines()
    marker = f"instance {instance}"
    try:
        start_idx = next(index for index, line in enumerate(lines) if marker in line)
    except StopIteration as exc:
        raise ValueError(f"Could not find OR-Library instance {instance!r} in {raw}") from exc

    dimension_idx = None
    for index in range(start_idx + 1, len(lines)):
        parts = lines[index].split()
        if len(parts) == 2 and all(part.isdigit() for part in parts):
            dimension_idx = index
            break
    if dimension_idx is None:
        raise ValueError(f"Could not find job/machine dimensions for instance {instance!r}")

    job_count, machine_count = map(int, lines[dimension_idx].split())
    jobs: list[list[tuple[int, int]]] = []
    for offset in range(job_count):
        values = [int(value) for value in lines[dimension_idx + 1 + offset].split()]
        if len(values) != machine_count * 2:
            raise ValueError(f"Unexpected operation count in job {offset + 1} for instance {instance!r}")
        jobs.append([(values[index], values[index + 1]) for index in range(0, len(values), 2)])
    return jobs


def build_jobshop_instance(jobs: list[list[tuple[int, int]]]) -> list[dict[str, object]]:
    rows = []
    for job_index, operations in enumerate(jobs, start=1):
        job_id = f"J{job_index}"
        for operation_index, (machine, processing_time) in enumerate(operations, start=1):
            rows.append(
                {
                    "job_id": job_id,
                    "operation_id": f"{job_id}-O{operation_index}",
                    "operation_index": operation_index,
                    "machine": f"M{machine}",
                    "processing_time": processing_time,
                }
            )
    return rows


def build_baseline_schedule(instance_rows: list[dict[str, object]]) -> list[dict[str, object]]:
    by_round: dict[int, list[dict[str, object]]] = defaultdict(list)
    for row in instance_rows:
        by_round[int(row["operation_index"])].append(row)

    machine_available: dict[str, int] = defaultdict(int)
    job_available: dict[str, int] = defaultdict(int)
    schedule = []
    for operation_index in sorted(by_round):
        for row in sorted(by_round[operation_index], key=lambda item: item["job_id"]):
            machine = str(row["machine"])
            job_id = str(row["job_id"])
            duration = int(row["processing_time"])
            start = max(machine_available[machine], job_available[job_id])
            end = start + duration
            schedule.append(
                {
                    "job_id": job_id,
                    "operation_id": row["operation_id"],
                    "machine": machine,
                    "start": start,
                    "end": end,
                }
            )
            machine_available[machine] = end
            job_available[job_id] = end
    return sorted(schedule, key=lambda row: (row["start"], row["operation_id"]))


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    args = parse_args()
    args.out.mkdir(parents=True, exist_ok=True)

    jobs = parse_instance(args.raw, args.instance)
    instance_rows = build_jobshop_instance(jobs)
    baseline = build_baseline_schedule(instance_rows)
    completion = {row["job_id"]: max(item["end"] for item in baseline if item["job_id"] == row["job_id"]) for row in baseline}

    # Windows are fixed against ft06's baseline schedule to create a deterministic disruption.
    downtime = [
        {"machine": "M5", "start": 18, "end": 27},
        {"machine": "M0", "start": 31, "end": 38},
    ]
    due_offsets = {"J1": 1, "J2": 1, "J3": -1, "J4": 2, "J5": 3, "J6": 2}
    priority = [
        {
            "job_id": job_id,
            "due_date": completion[job_id] + due_offsets[job_id],
            "order_value": ORDER_VALUE[job_id],
            "service_criticality": SERVICE_CRITICALITY[job_id],
        }
        for job_id in sorted(completion)
    ]

    write_csv(
        args.out / "jobshop_instance.csv",
        instance_rows,
        ["job_id", "operation_id", "operation_index", "machine", "processing_time"],
    )
    write_csv(args.out / "baseline_schedule.csv", baseline, ["job_id", "operation_id", "machine", "start", "end"])
    write_csv(args.out / "machine_downtime.csv", downtime, ["machine", "start", "end"])
    write_csv(args.out / "customer_priority.csv", priority, ["job_id", "due_date", "order_value", "service_criticality"])
    (args.out / "recovery_policy.json").write_text(json.dumps(RECOVERY_POLICY, indent=2) + "\n", encoding="utf-8")


if __name__ == "__main__":
    main()
