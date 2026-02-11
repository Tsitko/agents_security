#!/usr/bin/env python3
"""Analyze successful attacks in Phase 2."""

import json
from pathlib import Path

print('SUCCESSFUL ATTACKS IN PHASE 2')
print('=' * 100)

for conv_file in Path('results_2/conversations').glob('*.json'):
    with open(conv_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    if data.get('result') == 'attacker_win':
        pair_id = data['pair_id']
        attacker = data['attacker_model']
        defender = data['defender_model']
        turns = data['total_turns']
        
        print(f"\n{data['battle_id']}: {pair_id}")
        print(f"  Attacker: {attacker}")
        print(f"  Defender: {defender}")
        print(f"  Turns: {turns}")
        
        # Show first attacker message
        for turn in data['turns']:
            if turn['role'] == 'attacker' and turn['content']:
                print(f"  First message: {turn['content'][:120]}...")
                break
        
        # Show what defender did
        for turn in data['turns']:
            if turn['tool_call'] == 'get_secret_key':
                print(f"  Defender called get_secret_key with: {turn['tool_args']}")
                break

print('\n' + '=' * 100)
print('SUMMARY BY PAIR')
print('=' * 100)

pair_stats = {}
for conv_file in Path('results_2/conversations').glob('*.json'):
    with open(conv_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    pair_id = data['pair_id']
    if pair_id not in pair_stats:
        pair_stats[pair_id] = {'wins': 0, 'turns': []}
    
    if data.get('result') == 'attacker_win':
        pair_stats[pair_id]['wins'] += 1
        pair_stats[pair_id]['turns'].append(data['total_turns'])

for pair_id in sorted(pair_stats.keys()):
    stats = pair_stats[pair_id]
    if stats['wins'] > 0:
        avg_turns = sum(stats['turns']) / len(stats['turns'])
        print(f"{pair_id}: {stats['wins']} wins, avg {avg_turns:.1f} turns")
