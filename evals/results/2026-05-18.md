# Sabha Code — eval results (2026-05-18)

- **Candidate model:** `claude-sonnet-4-6`
- **Judge model:** `anthropic:claude-opus-4-7`
- **Question set:** v1 (30 questions)
- **Rubric version:** v3

## Summary

| Metric | Baseline | Sabha Code | Δ |
|---|---:|---:|---:|
| decisiveness | 3.23 | 4.47 | +1.24 |
| tradeoff named | 2.5 | 3.5 | +1.00 |
| concreteness | 3.5 | 4.23 | +0.73 |
| routing present | 0.0 | 1.0 | +1.00 |
| length discipline | 3.1 | 4.87 | +1.77 |
| total | 12.33 | 17.07 | +4.74 |

### Pairwise preference

- **Sabha Code preferred:** 28 / 30 (93.3%)
- **Baseline preferred:** 2 / 30 (6.7%)
- **Tie:** 0 / 30

## Per-question results

| id | role | role instr loaded | pairwise winner | Sabha Code total | Baseline total |
|---|---|---|---|---:|---:|
| `arch-01` | Architect | ✓ | **sabha_code** | 20 | 15 |
| `arch-02` | Architect | ✓ | **sabha_code** | 20 | 16 |
| `arch-03` | Architect | ✓ | **sabha_code** | 20 | 10 |
| `arch-04` | Architect | ✓ | **sabha_code** | 19 | 16 |
| `rev-01` | Reviewer | ✓ | **sabha_code** | 19 | 14 |
| `rev-02` | Reviewer | ✓ | **sabha_code** | 17 | 13 |
| `rev-03` | Reviewer | ✓ | **sabha_code** | 19 | 13 |
| `sec-01` | Security | ✓ | **sabha_code** | 18 | 15 |
| `sec-02` | Security | ✓ | **sabha_code** | 17 | 12 |
| `sec-03` | Security | ✓ | **sabha_code** | 18 | 12 |
| `perf-01` | Performance | ✓ | **sabha_code** | 18 | 17 |
| `perf-02` | Performance | ✓ | **sabha_code** | 17 | 14 |
| `perf-03` | Performance | ✓ | **sabha_code** | 13 | 9 |
| `qa-01` | QA | ✓ | **sabha_code** | 19 | 13 |
| `qa-02` | QA | ✓ | **sabha_code** | 14 | 9 |
| `qa-03` | QA | ✓ | **sabha_code** | 19 | 14 |
| `men-01` | Mentor | ✓ | **sabha_code** | 17 | 8 |
| `men-02` | Mentor | ✓ | **sabha_code** | 18 | 12 |
| `tl-01` | Tech Lead | ✓ | **sabha_code** | 17 | 13 |
| `tl-02` | Tech Lead | ✓ | **sabha_code** | 17 | 13 |
| `adv-01` | Performance | ✓ | **sabha_code** | 14 | 11 |
| `adv-02` | Architect | ✓ | **sabha_code** | 20 | 15 |
| `adv-03` | Reviewer | ✓ | **sabha_code** | 16 | 13 |
| `adv-04` | Security | ✓ | **baseline** | 19 | 16 |
| `adv-05` | QA | ✓ | **sabha_code** | 17 | 12 |
| `und-01` | Architect | ✓ | **sabha_code** | 9 | 9 |
| `und-02` | Performance | ✓ | **sabha_code** | 16 | 8 |
| `und-03` | Security | ✓ | **sabha_code** | 17 | 8 |
| `und-04` | QA | ✓ | **baseline** | 14 | 11 |
| `und-05` | Mentor | ✓ | **sabha_code** | 14 | 9 |
