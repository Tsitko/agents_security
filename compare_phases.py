#!/usr/bin/env python3
"""Compare Phase 1 and Phase 2 results."""

import json
from pathlib import Path

def load_phase(checkpoints_dir):
    results = {}
    for cp_file in Path(checkpoints_dir).glob('pair_*_checkpoint.json'):
        with open(cp_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        pair_id = data['pair_id']
        
        wins = {'attacker': 0, 'defender': 0, 'refused': 0, 'error': 0}
        for r in data['results']:
            result = r.get('result', '')
            if result == 'attacker_win':
                wins['attacker'] += 1
            elif result in ['defender_win', 'max_turns', 'attacker_quit']:
                wins['defender'] += 1
            elif result == 'attacker_refused':
                wins['refused'] += 1
            else:
                wins['error'] += 1
        
        results[pair_id] = wins
    return results

phase1 = load_phase('checkpoints')
phase2 = load_phase('checkpoints_2')

print('=' * 100)
print('PHASE 1 vs PHASE 2 COMPARISON')
print('=' * 100)
print(f"{'Pair':<12} {'Phase 1 A/D':>12} {'Rate':>8} | {'Phase 2 A/D/R':>18} {'Rate':>8} | {'Change':>10}")
print('-' * 100)

for pair_id in sorted(phase1.keys()):
    p1 = phase1[pair_id]
    p2 = phase2.get(pair_id, {'attacker': 0, 'defender': 0, 'refused': 0})
    
    p1_total = p1['attacker'] + p1['defender']
    p1_rate = p1['attacker'] / p1_total * 100 if p1_total > 0 else 0
    
    p2_total = p2['attacker'] + p2['defender']
    p2_rate = p2['attacker'] / p2_total * 100 if p2_total > 0 else 0
    
    change = p2_rate - p1_rate
    change_str = f"{change:+.1f}%"
    
    p1_str = f"{p1['attacker']}/{p1['defender']}"
    p2_str = f"{p2['attacker']}/{p2['defender']}/{p2['refused']}"
    
    print(f"{pair_id:<12} {p1_str:>12} {p1_rate:>7.0f}% | {p2_str:>18} {p2_rate:>7.0f}% | {change_str:>10}")

print('\n' + '=' * 100)
print('SUMMARY')
print('=' * 100)

p1_total_a = sum(p['attacker'] for p in phase1.values())
p1_total_d = sum(p['defender'] for p in phase1.values())
p1_rate = p1_total_a / (p1_total_a + p1_total_d) * 100

p2_total_a = sum(p['attacker'] for p in phase2.values())
p2_total_d = sum(p['defender'] for p in phase2.values())
p2_total_r = sum(p.get('refused', 0) for p in phase2.values())
p2_rate = p2_total_a / (p2_total_a + p2_total_d) * 100 if (p2_total_a + p2_total_d) > 0 else 0

print(f"Phase 1: {p1_total_a} wins / {p1_total_d} losses = {p1_rate:.1f}% success rate")
print(f"Phase 2: {p2_total_a} wins / {p2_total_d} losses / {p2_total_r} refused = {p2_rate:.1f}% success rate (excl. refused)")
print(f"Change: {p2_rate - p1_rate:+.1f} percentage points")
print(f"Refusal rate in Phase 2: {p2_total_r / 120 * 100:.1f}%")
