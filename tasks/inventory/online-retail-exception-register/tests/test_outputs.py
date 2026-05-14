import json
import math
import pandas as pd

def _expected():
    daily = pd.read_csv('/app/data/daily_sku_demand.csv')
    inventory = pd.read_csv('/app/data/current_inventory.csv')
    policy = pd.read_csv('/app/data/inventory_policy.csv')
    avg = daily.groupby('sku', as_index=False)['demand_units'].mean().rename(columns={'demand_units': 'avg_daily_demand'})
    df = policy.merge(inventory, on='sku', how='left').merge(avg, on='sku', how='left')
    df['reorder_point_units'] = (df['avg_daily_demand'] * df['lead_time_days'] + df['safety_stock_units']).apply(math.ceil)

    def round_order(row):
        gap = row['reorder_point_units'] - row['on_hand_units']
        if gap <= 0:
            return 0
        pack_qty = int(math.ceil(gap / row['order_pack_size']) * row['order_pack_size'])
        return max(pack_qty, int(row['minimum_order_qty']))
    df['recommended_order_qty'] = df.apply(round_order, axis=1)
    df['current_days_of_cover'] = df['on_hand_units'] / df['avg_daily_demand']

    def priority(row):
        if row['current_days_of_cover'] <= row['lead_time_days']:
            return 'critical'
        if row['current_days_of_cover'] <= row['high_priority_cover_days']:
            return 'high'
        return 'monitor'
    df['priority_band'] = df.apply(priority, axis=1)
    df['expected_days_of_cover_after_order'] = (df['on_hand_units'] + df['recommended_order_qty']) / df['avg_daily_demand']
    return df

def test_exceptions_json():
    expected = _expected()
    exceptions = expected[(expected['recommended_order_qty'] > 0) & expected['priority_band'].isin(['critical', 'high'])].copy()
    severity = {'critical': 0, 'high': 1}
    exceptions['_severity'] = exceptions['priority_band'].map(severity)
    exceptions = exceptions.sort_values(['_severity', 'current_days_of_cover', 'sku'])
    with open('/app/output/replenishment_exceptions.json', encoding='utf-8') as f:
        payload = json.load(f)
    assert sorted(payload.keys()) == ['exception_count', 'exceptions']
    assert payload['exception_count'] == len(exceptions)
    assert len(payload['exceptions']) == len(exceptions)
    for actual, (_, exp) in zip(payload['exceptions'], exceptions.iterrows()):
        assert actual['sku'] == exp['sku']
        assert actual['priority_band'] == exp['priority_band']
        assert actual['days_of_cover'] == round(float(exp['current_days_of_cover']), 1)
        assert actual['recommended_order_qty'] == int(exp['recommended_order_qty'])
        if exp['priority_band'] == 'critical':
            assert actual['trigger_rule'] == 'current_days_of_cover <= lead_time_days'
        else:
            assert actual['trigger_rule'] == 'current_days_of_cover <= high_priority_cover_days'
