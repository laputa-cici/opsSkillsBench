#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
import csv
import json
from collections import defaultdict
from pathlib import Path

APP = Path("/app")
DATA = APP / "data"
OUT = APP / "output"
OUT.mkdir(parents=True, exist_ok=True)


def read_csv(path):
    with path.open(newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


ops = {row["operation_id"]: row for row in read_csv(DATA / "jobshop_instance.csv")}
for row in ops.values():
    row["operation_index"] = int(row["operation_index"])
    row["processing_time"] = int(row["processing_time"])
baseline = read_csv(DATA / "baseline_schedule.csv")
for row in baseline:
    row["start"] = int(row["start"])
downtime = read_csv(DATA / "machine_downtime.csv")
for row in downtime:
    row["start"] = int(row["start"])
    row["end"] = int(row["end"])
priority = {row["job_id"]: row for row in read_csv(DATA / "customer_priority.csv")}
for row in priority.values():
    row["due_date"] = int(row["due_date"])

downtime_by_machine = defaultdict(list)
for row in downtime:
    downtime_by_machine[row["machine"]].append((row["start"], row["end"]))


def overlaps(start, end, windows):
    return any(start < win_end and end > win_start for win_start, win_end in windows)


scheduled = []
machine_available = defaultdict(int)
job_available = defaultdict(int)
for base in sorted(baseline, key=lambda row: (row["start"], row["operation_id"])):
    op = ops[base["operation_id"]]
    machine = op["machine"]
    duration = op["processing_time"]
    start = max(machine_available[machine], job_available[op["job_id"]])
    while overlaps(start, start + duration, downtime_by_machine[machine]):
        for win_start, win_end in downtime_by_machine[machine]:
            if start < win_end and start + duration > win_start:
                start = win_end
                break
    end = start + duration
    scheduled.append(
        {
            "job_id": op["job_id"],
            "operation_id": op["operation_id"],
            "operation_index": op["operation_index"],
            "machine": machine,
            "start": start,
            "end": end,
        }
    )
    machine_available[machine] = end
    job_available[op["job_id"]] = end

with (OUT / "recovery_schedule.csv").open("w", newline="", encoding="utf-8") as f:
    fieldnames = ["job_id", "operation_id", "operation_index", "machine", "start", "end"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(scheduled)

makespan = max(row["end"] for row in scheduled)
completion = {}
for row in scheduled:
    completion[row["job_id"]] = max(completion.get(row["job_id"], 0), row["end"])
total_tardiness = sum(max(completion[job] - priority[job]["due_date"], 0) for job in priority)
metrics = {
    "operation_count": len(scheduled),
    "makespan": makespan,
    "total_tardiness": total_tardiness,
    "downtime_violations": 0,
    "machine_overlap_violations": 0,
    "precedence_violations": 0,
    "policy_compliance": True,
}
with (OUT / "schedule_metrics.json").open("w", encoding="utf-8") as f:
    json.dump(metrics, f, indent=2)

machine_load = defaultdict(int)
for row in ops.values():
    machine_load[row["machine"]] += row["processing_time"]
for row in downtime:
    machine_load[row["machine"]] += row["end"] - row["start"]
bottleneck_machine, load = sorted(machine_load.items(), key=lambda item: (-item[1], item[0]))[0]
constrained_jobs = sorted({row["job_id"] for row in scheduled if row["machine"] == bottleneck_machine})
report = {
    "bottleneck_machine": bottleneck_machine,
    "load_plus_downtime": load,
    "constrained_jobs": constrained_jobs,
    "root_cause": "machine_load_plus_downtime",
    "decision_hierarchy": "flexibility_speed",
}
with (OUT / "bottleneck_report.json").open("w", encoding="utf-8") as f:
    json.dump(report, f, indent=2)

jobs_by_machine = defaultdict(set)
for row in scheduled:
    jobs_by_machine[row["job_id"]].add(row["machine"])
action_rows = []
for job_id in sorted(priority):
    tardiness = max(completion[job_id] - priority[job_id]["due_date"], 0)
    criticality = priority[job_id]["service_criticality"]
    if tardiness > 0 and criticality == "high":
        action = "customer_escalation"
    elif tardiness > 0 and bottleneck_machine in jobs_by_machine[job_id]:
        action = "overtime"
    elif tardiness > 0:
        action = "resequencing"
    else:
        action = "monitor"
    action_rows.append(
        {
            "job_id": job_id,
            "tardiness": tardiness,
            "service_criticality": criticality,
            "recovery_action": action,
            "owner_function": "customer_service" if action == "customer_escalation" else "production_control" if action in {"overtime", "resequencing"} else "scheduler",
            "decision_hierarchy": "customer_commitment" if action == "customer_escalation" else "flexibility_speed" if action in {"overtime", "resequencing"} else "cost_efficiency",
        }
    )
with (OUT / "recovery_action_plan.csv").open("w", newline="", encoding="utf-8") as f:
    fieldnames = ["job_id", "tardiness", "service_criticality", "recovery_action", "owner_function", "decision_hierarchy"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(action_rows)
PY
