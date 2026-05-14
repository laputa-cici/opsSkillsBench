import csv
import json
from collections import defaultdict
from pathlib import Path
APP = Path('/app')
DATA = APP / 'data'
OUT = APP / 'output'

def _read_csv(path):
    with path.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def _expected():
    ops = {row['operation_id']: row for row in _read_csv(DATA / 'jobshop_instance.csv')}
    for row in ops.values():
        row['operation_index'] = int(row['operation_index'])
        row['processing_time'] = int(row['processing_time'])
    baseline = _read_csv(DATA / 'baseline_schedule.csv')
    for row in baseline:
        row['start'] = int(row['start'])
    downtime = _read_csv(DATA / 'machine_downtime.csv')
    for row in downtime:
        row['start'] = int(row['start'])
        row['end'] = int(row['end'])
    priority = {row['job_id']: row for row in _read_csv(DATA / 'customer_priority.csv')}
    for row in priority.values():
        row['due_date'] = int(row['due_date'])
    downtime_by_machine = defaultdict(list)
    for row in downtime:
        downtime_by_machine[row['machine']].append((row['start'], row['end']))

    def overlaps(start, end, windows):
        return any((start < win_end and end > win_start for win_start, win_end in windows))
    scheduled = []
    machine_available = defaultdict(int)
    job_available = defaultdict(int)
    for base in sorted(baseline, key=lambda row: (row['start'], row['operation_id'])):
        op = ops[base['operation_id']]
        machine = op['machine']
        duration = op['processing_time']
        start = max(machine_available[machine], job_available[op['job_id']])
        while overlaps(start, start + duration, downtime_by_machine[machine]):
            for win_start, win_end in downtime_by_machine[machine]:
                if start < win_end and start + duration > win_start:
                    start = win_end
                    break
        end = start + duration
        scheduled.append({'job_id': op['job_id'], 'operation_id': op['operation_id'], 'operation_index': str(op['operation_index']), 'machine': machine, 'start': str(start), 'end': str(end)})
        machine_available[machine] = end
        job_available[op['job_id']] = end
    return (scheduled, ops, downtime, priority)

def test_recovery_schedule():
    expected, _, _, _ = _expected()
    with (OUT / 'recovery_schedule.csv').open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        actual = list(reader)
        assert reader.fieldnames == ['job_id', 'operation_id', 'operation_index', 'machine', 'start', 'end']
    assert actual == expected
