"""Shared-runner job for NATIVE-SPINE-20261119-001B-E001: three spine rules on the ten plastic-number eddies.

Each of the ten (BREAK-EDDIES population indices 28, 44, 52, 55, 56, 58, 61, 65, 66, 68) grows 24 rounds.  At every recurrent
round t (c(t) = c(t - 2) + c(t - 3)), rulelib's N, M and F are scored (perfect or not; ties, depth split, collisions), the full
relation's forced share is read (1 means its perfect matching is unique), and at rounds 10, 15 and 20 a degree-preserving shuffle
of the relation is tested for a perfect matching (seed = round)."""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import rulelib as RL  # noqa: E402

ROOT = HERE.parents[2]
POP = ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json'
TEN = [28, 44, 52, 55, 56, 58, 61, 65, 66, 68]


def cases():
    pop = json.loads(POP.read_text())
    for i in TEN:
        yield f'T-{i:03d}', {'start': pop[i], 'rounds': 24}


def run(case_id, payload):
    P = RL.S.grow(payload['start'], payload['rounds'], 40000)
    par, ch, br = RL.S.family(P)
    c = P.counts_by_round()
    rows = []
    for t in range(4, P.rounds + 1):
        if c[t] != c[t - 2] + c[t - 3]:
            continue
        rel = RL.relation(par, br, t)
        row = {'t': t, 'count': c[t]}
        for r in 'NMF':
            kept = RL.keep(rel, r)
            row[r] = dict(RL.is_perfect(kept, br, t), **RL.rule_stats(kept, rel))
        row['forced'] = RL.forced_fraction(rel)
        if t in (10, 15, 20):
            row['null_perfect'] = RL.shuffled_has_perfect(rel, seed=t)
        rows.append(row)
    return {'counts': c, 'rows': rows}
