#!/usr/bin/env python3
"""Analyze refusal cases in Phase 2."""

import json
from pathlib import Path

print('PHASE 2 REFUSAL ANALYSIS')
print('=' * 80)

cp_file = Path('checkpoints_2/pair_02_checkpoint.json')
with open(cp_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

for r in data['results']:
    if r['result'] == 'attacker_refused':
        print(f"\n{r['battle_id']}:")
        print(f"  Details: {r['details']}")
        
        # Load conversation
        conv_file = Path(f"results_2/conversations/{r['battle_id']}.json")
        if conv_file.exists():
            with open(conv_file, 'r', encoding='utf-8') as cf:
                conv = json.load(cf)
            if conv['turns']:
                first_turn = conv['turns'][0]
                print(f"  First turn: '{first_turn['content'][:80]}...'")

print('\n' + '=' * 80)
print('Checking learning summaries for retry success...')
print('=' * 80)

for summary_file in Path('results_2/summaries').glob('pair_*_summary.txt'):
    with open(summary_file, 'r', encoding='utf-8') as f:
        content = f.read()
    if 'refused' in content.lower() or 'refusal' in content.lower():
        print(f"\n{summary_file.name}:")
        print(content[:300])
