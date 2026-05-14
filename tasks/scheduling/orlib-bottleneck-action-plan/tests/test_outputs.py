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

def test_bottleneck_report_and_action_plan():
    scheduled, ops, downtime, priority = _expected()
    machine_load = defaultdict(int)
    for row in ops.values():
        machine_load[row['machine']] += row['processing_time']
    for row in downtime:
        machine_load[row['machine']] += row['end'] - row['start']
    bottleneck_machine, load = sorted(machine_load.items(), key=lambda item: (-item[1], item[0]))[0]
    expected_report = {'bottleneck_machine': bottleneck_machine, 'load_plus_downtime': load, 'constrained_jobs': sorted({row['job_id'] for row in scheduled if row['machine'] == bottleneck_machine}), 'root_cause': 'machine_load_plus_downtime', 'decision_hierarchy': 'flexibility_speed'}
    assert json.loads((OUT / 'bottleneck_report.json').read_text(encoding='utf-8')) == expected_report
    completion = {}
    jobs_by_machine = defaultdict(set)
    for row in scheduled:
        completion[row['job_id']] = max(completion.get(row['job_id'], 0), int(row['end']))
        jobs_by_machine[row['job_id']].add(row['machine'])
    expected_actions = []
    for job_id in sorted(priority):
        tardiness = max(completion[job_id] - priority[job_id]['due_date'], 0)
        criticality = priority[job_id]['service_criticality']
        if tardiness > 0 and criticality == 'high':
            action = 'customer_escalation'
        elif tardiness > 0 and bottleneck_machine in jobs_by_machine[job_id]:
            action = 'overtime'
        elif tardiness > 0:
            action = 'resequencing'
        else:
            action = 'monitor'
        expected_actions.append({'job_id': job_id, 'tardiness': str(tardiness), 'service_criticality': criticality, 'recovery_action': action, 'owner_function': 'customer_service' if action == 'customer_escalation' else 'production_control' if action in {'overtime', 'resequencing'} else 'scheduler', 'decision_hierarchy': 'customer_commitment' if action == 'customer_escalation' else 'flexibility_speed' if action in {'overtime', 'resequencing'} else 'cost_efficiency'})
    with (OUT / 'recovery_action_plan.csv').open(newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        actual = list(reader)
        assert reader.fieldnames == ['job_id', 'tardiness', 'service_criticality', 'recovery_action', 'owner_function', 'decision_hierarchy']
    assert actual == expected_actions
