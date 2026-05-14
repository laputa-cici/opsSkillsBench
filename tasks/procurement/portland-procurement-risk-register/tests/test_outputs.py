import csv
import json
from collections import defaultdict
from pathlib import Path
APP = Path('/app')
DATA = APP / 'data'
OUT = APP / 'output'

def _expected():
    policy = json.loads((DATA / 'category_policy.json').read_text(encoding='utf-8'))
    with (DATA / 'awards.csv').open(newline='', encoding='utf-8') as f:
        awards = list(csv.DictReader(f))
    for row in awards:
        row['award_value'] = int(row['award_value'])
    with (DATA / 'supplier_profile.csv').open(newline='', encoding='utf-8') as f:
        profiles = {row['category']: row for row in csv.DictReader(f)}
    for row in profiles.values():
        row['supplier_count'] = int(row['supplier_count'])
        row['criticality_score'] = int(row['criticality_score'])
    by_category = defaultdict(list)
    for row in awards:
        by_category[row['category']].append(row)
    matrix_rows = []
    action_rows = []
    for category, rows in sorted(by_category.items()):
        profile = profiles[category]
        total_spend = sum((row['award_value'] for row in rows))
        supplier_spend = defaultdict(int)
        supplier_contracts = defaultdict(set)
        for row in rows:
            supplier_spend[row['supplier']] += row['award_value']
            supplier_contracts[row['supplier']].add(row['contract_type'])
        top_supplier = sorted(supplier_spend.items(), key=lambda item: (-item[1], item[0]))[0][0]
        share = round(supplier_spend[top_supplier] / total_spend, 3)
        spend_impact = 'high' if total_spend >= policy['spend_impact_threshold'] else 'low'
        supply_risk = 'high' if profile['criticality_score'] >= policy['high_supply_risk_criticality'] or profile['competition_flag'] == 'limited_competition' else 'low'
        if spend_impact == 'high' and supply_risk == 'high':
            quadrant = 'strategic'
        elif spend_impact == 'high':
            quadrant = 'leverage'
        elif supply_risk == 'high':
            quadrant = 'bottleneck'
        else:
            quadrant = 'non_critical'
        matrix_rows.append({'category': category, 'total_spend': str(total_spend), 'top_supplier': top_supplier, 'top_supplier_share': f'{share:.3f}', 'spend_impact': spend_impact, 'supply_risk': supply_risk, 'kraljic_quadrant': quadrant, 'sourcing_strategy': policy['quadrant_strategy'][quadrant]})
        concentration_flag = 'high' if share >= policy['high_concentration_share'] else 'normal'
        if concentration_flag == 'high' and profile['competition_flag'] == 'limited_competition':
            anti_pattern = 'single_sourcing'
        elif concentration_flag == 'high' and 'renewal' in supplier_contracts[top_supplier]:
            anti_pattern = 'price_only_focus'
        elif concentration_flag == 'normal' and profile['supplier_count'] >= 3:
            anti_pattern = 'supplier_fragmentation'
        else:
            anti_pattern = 'none'
        action_rows.append({'category': category, 'supplier': top_supplier, 'concentration_flag': concentration_flag, 'anti_pattern': anti_pattern, 'mitigation_code': policy['mitigation_by_antipattern'][anti_pattern], 'owner_function': 'category_manager' if quadrant in {'strategic', 'leverage'} else 'procurement', 'follow_up': {'strategic': 'quarterly_business_review', 'leverage': 'rfp_refresh', 'bottleneck': 'continuity_plan', 'non_critical': 'automate_catalog'}[quadrant]})
    return (matrix_rows, action_rows)

def test_procurement_risk_register():
    matrix, actions = _expected()
    matrix_by_category = {row['category']: row for row in matrix}
    risks = []
    for row in actions:
        if row['anti_pattern'] == 'none':
            continue
        quadrant = matrix_by_category[row['category']]['kraljic_quadrant']
        risks.append({'category': row['category'], 'supplier': row['supplier'], 'anti_pattern': row['anti_pattern'], 'mitigation_code': row['mitigation_code'], 'escalation_level': 1 if quadrant == 'strategic' else 2 if quadrant == 'bottleneck' else 3, 'evidence': f"top_supplier_share={matrix_by_category[row['category']]['top_supplier_share']}"})
    risks.sort(key=lambda row: (row['escalation_level'], row['category']))
    assert json.loads((OUT / 'procurement_risk_register.json').read_text(encoding='utf-8')) == {'risk_count': len(risks), 'risks': risks}
