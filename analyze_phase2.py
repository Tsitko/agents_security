#!/usr/bin/env python3
"""Analyze Phase 2 results."""

import json
from pathlib import Path

checkpoints_dir = Path('checkpoints_2')
results = {}

for cp_file in checkpoints_dir.glob('pair_*_checkpoint.json'):
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
    
    results[pair_id] = {
        'name': data['pair_name'],
        'attacker': data['attacker_model'],
        'defender': data['defender_model'],
        'completed': data['completed_experiments'],
        'wins': wins,
        'results': data['results']
    }

# Print summary
print('=' * 80)
print('PHASE 2 RESULTS SUMMARY')
print('=' * 80)
print(f"{'Pair':<12} {'Name':<25} {'A':>4} {'D':>4} {'R':>4} {'E':>4} {'Total':>6}")
print('-' * 80)

total_a = total_d = total_r = total_e = 0
for pair_id in sorted(results.keys()):
    r = results[pair_id]
    w = r['wins']
    print(f"{pair_id:<12} {r['name']:<25} {w['attacker']:>4} {w['defender']:>4} {w['refused']:>4} {w['error']:>4} {r['completed']:>6}")
    total_a += w['attacker']
    total_d += w['defender']
    total_r += w['refused']
    total_e += w['error']

print('-' * 80)
grand_total = total_a + total_d + total_r + total_e
print(f"{'TOTAL':<38} {total_a:>4} {total_d:>4} {total_r:>4} {total_e:>4} {grand_total:>6}")
print(f"\nSuccess Rate: {total_a / (total_a + total_d) * 100:.1f}% (excluding refused)")
print(f"Refusal Rate: {total_r / grand_total * 100:.1f}%")

# Find small vs large upsets
print('\n' + '=' * 80)
print('UPSSET ANALYSIS: Small models beating large models')
print('=' * 80)

# pair_05: qwen2.5-coder-7b (attacker) vs openai/gpt-oss-20b (defender)
# pair_07: qwen2.5-coder-7b (attacker) vs qwen3-coder-30b (defender)
# pair_09: qwen2.5-coder-7b (attacker) vs qwen/qwen3-next-80b (defender)

upset_pairs = ['pair_05', 'pair_07', 'pair_09']
for pair_id in upset_pairs:
    if pair_id in results:
        r = results[pair_id]
        print(f"\n{pair_id}: {r['name']}")
        print(f"  Attacker: {r['attacker']}")
        print(f"  Defender: {r['defender']}")
        print(f"  Results: A={r['wins']['attacker']}, D={r['wins']['defender']}, R={r['wins']['refused']}")
        
        # Show individual battles
        for battle in r['results']:
            if battle['result'] == 'attacker_win':
                print(f"  [UPSET] {battle['battle_id']}: Attacker won in {battle['total_turns']} turns")

print('\n' + '=' * 80)
print('REFUSAL ANALYSIS')
print('=' * 80)

for pair_id in sorted(results.keys()):
    r = results[pair_id]
    if r['wins']['refused'] > 0:
        print(f"{pair_id}: {r['wins']['refused']} refusals out of {r['completed']}")
