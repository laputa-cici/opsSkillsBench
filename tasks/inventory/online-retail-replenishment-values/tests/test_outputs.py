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

def test_replenishment_plan_values():
    expected = _expected()
    actual = pd.read_csv('/app/output/replenishment_plan.csv')
    expected_by_sku = expected.set_index('sku')
    for _, row in actual.iterrows():
        exp = expected_by_sku.loc[row['sku']]
        assert abs(float(row['avg_daily_demand']) - round(float(exp['avg_daily_demand']), 1)) < 1e-09
        assert int(row['reorder_point_units']) == int(exp['reorder_point_units'])
        assert int(row['recommended_order_qty']) == int(exp['recommended_order_qty'])
        assert row['priority_band'] == exp['priority_band']
        assert abs(float(row['expected_days_of_cover_after_order']) - round(float(exp['expected_days_of_cover_after_order']), 1)) < 1e-09
