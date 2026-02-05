# Experiment Results Overview

## Summary

**Total experiments:** 120 battles (12 model pairs × 10 experiments each)
**Total attacker wins:** 25 (20.8%)
**Total defender wins:** 95 (79.2%)

---

## Results by Model Pair

| Pair | Attacker | Defender | A Wins | D Wins | Attack Success Rate |
|------|----------|----------|--------|--------|---------------------|
| pair_01 | qwen2.5-coder-7b | qwen2.5-coder-7b | 0 | 10 | 0% |
| pair_02 | qwen2.5-coder-7b | gigachat3-10b | 4 | 6 | 40% |
| pair_03 | qwen3-30b-MoE | qwen3-30b-MoE | 1 | 9 | 10% |
| pair_04 | gpt-oss-20b | qwen2.5-coder-7b | 3 | 7 | 30% |
| pair_05 | qwen2.5-coder-7b | gpt-oss-20b | 0 | 10 | 0% |
| pair_06 | qwen3-coder-30b | qwen2.5-coder-7b | 5 | 5 | 50% |
| pair_07 | qwen2.5-coder-7b | qwen3-coder-30b | 0 | 10 | 0% |
| pair_08 | qwen3-next-80b | qwen2.5-coder-7b | 4 | 6 | 40% |
| pair_09 | qwen2.5-coder-7b | qwen3-next-80b | 0 | 10 | 0% |
| pair_10 | qwen3-next-80b | qwen3-next-80b | 0 | 10 | 0% |
| pair_11 | qwen3-coder-30b | qwen3-coder-30b | 0 | 10 | 0% |
| pair_12 | gpt-oss-120b | gigachat3-10b | 8 | 2 | **80%** |

---

## Key Findings

### 1. Defender Model Size is Critical

**Larger defenders are significantly more resistant to attacks.**

| Defender Size | Battles | Attacker Wins | Success Rate |
|---------------|---------|---------------|--------------|
| Small (7-10B) | 60 | 24 | **40%** |
| Medium (20-30B) | 40 | 1 | 2.5% |
| Large (80B+) | 20 | 0 | 0% |

When the defender is a small model (7-10B parameters), attackers succeed 40% of the time. Medium and large defenders are nearly impervious.

### 2. Attacker Size Matters Less Than Expected

Larger attackers don't dramatically improve success rates against resistant defenders:

| Attacker vs Small Defender | Success Rate |
|----------------------------|--------------|
| 7B attacker (pair_01) | 0% |
| 20B attacker (pair_04) | 30% |
| 30B attacker (pair_06) | 50% |
| 80B attacker (pair_08) | 40% |
| 120B attacker (pair_12) | 80% |

The 120B model shows the strongest attack capability, but even 80B attackers don't outperform 30B coder models against the same 7B defender.

### 3. Model Architecture Affects Vulnerability

**gigachat3-10b is notably more vulnerable than qwen2.5-coder-7b:**

| Defender | Against 7B Attacker | Against Large Attacker |
|----------|---------------------|------------------------|
| qwen2.5-coder-7b | 0% success | 30-50% success |
| gigachat3-10b | 40% success | **80% success** |

Despite similar parameter counts, gigachat shows 2x higher vulnerability.

### 4. Same-Model Battles Favor Defenders

When identical models face each other, defenders almost always win:

| Same-Model Pair | Result |
|-----------------|--------|
| 7B vs 7B (pair_01) | 0-10 (Defender wins all) |
| 30B vs 30B (pair_03) | 1-9 (Defender wins 90%) |
| 30B-coder vs 30B-coder (pair_11) | 0-10 (Defender wins all) |
| 80B vs 80B (pair_10) | 0-10 (Defender wins all) |

This suggests that models can effectively "recognize" manipulation patterns from similar architectures.

### 5. Asymmetric Battles Show Clear Patterns

**Small attacker vs Large defender: 0% success** (pairs 05, 07, 09)
**Large attacker vs Small defender: 40-80% success** (pairs 04, 06, 08, 12)

The attacker needs a significant capability advantage to overcome defender resistance.

---

## Vulnerability Ranking

### Most Vulnerable Defenders (by success rate against them)
1. **gigachat3-10b** — 60% average attack success
2. **qwen2.5-coder-7b** — 24% average attack success
3. **gpt-oss-20b** — 0% attack success
4. **qwen3-coder-30b** — 0% attack success
5. **qwen3-next-80b** — 0% attack success

### Most Effective Attackers (by success rate)
1. **gpt-oss-120b** — 80% success (against gigachat3-10b)
2. **qwen3-coder-30b** — 50% success (against qwen2.5-coder-7b)
3. **qwen2.5-coder-7b** — 40% success (against gigachat3-10b)
4. **qwen3-next-80b** — 40% success (against qwen2.5-coder-7b)
5. **gpt-oss-20b** — 30% success (against qwen2.5-coder-7b)

---

## Conclusions

1. **Defense scales with model size.** Models 20B+ show near-complete resistance to social engineering attacks in this framework.

2. **Attack capability requires significant size advantage.** A 120B attacker can compromise a 10B defender 80% of the time, but an 80B attacker only achieves 40% against a 7B defender.

3. **Architecture matters.** Different model families show different vulnerability profiles even at similar sizes.

4. **Self-recognition provides protection.** Identical models rarely succeed in attacking each other, suggesting implicit pattern recognition.

5. **Small models in production need additional safeguards.** A 7-10B agent exposed to other AI systems has a 40-80% chance of being socially engineered by a capable attacker.

---

## Future Work

- Analyze specific attack techniques that succeeded
- Study attacker learning patterns across experiments
- Test with system prompts that explicitly warn about social engineering
- Evaluate multi-turn conversation dynamics
- Compare with human red-teaming results
