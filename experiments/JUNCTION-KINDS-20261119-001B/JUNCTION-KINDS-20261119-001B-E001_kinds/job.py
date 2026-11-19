"""Shared-runner job for JUNCTION-KINDS-20261119-001B-E001: kinds of junction, out-shares and ancestor spines.

Population (30 starts, one case each):
- T: the ten break-shape eddies whose round-weight, read from every factor of the counts' minimal recurrence, is y^2 (1 + y)
  (BREAK-EDDIES' population indices 28, 44, 52, 55, 56, 58, 61, 65, 66, 68), lags (2, 3);
- Q: the fifteen whose corrected W is y^4 (1 + y)^2 (same rate, another W), lags (2, 3) for the count check;
- C: the catalogue's five minimal eddies, each with its own lags from its W (C-0, C-1: y^5 (1 + y); C-2, C-3: y^7 (1 + y);
  C-4: y^4 (1 + y)).
Each start grows to 26 rounds or 40,000 junctions (the catalogue to 40 rounds).  Recorded per round: counts; distinct out-shares;
distinct sum-equitable kinds of depth 6; at every round t where c(t) = c(t - l1) + c(t - l2) (for the catalogue, whose counts
carry a constant part, every round past the lags), the spine relation's maximum matching (all exact-depth ancestors) and its
single-chain version; for T and Q, the interval types and the biregular type sets (up to 3 of the 10 most frequent types) on the
first half of the rounds tested, then tested on the second half."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import spinelib as S  # noqa: E402

ROOT = HERE.parents[2]
POP = ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json'
CAT = ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json'
FULL = ROOT / 'artifacts/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/posthoc_full.json'
TEN = [28, 44, 52, 55, 56, 58, 61, 65, 66, 68]
CAT_LAGS = {0: (5, 6), 1: (5, 6), 2: (7, 8), 3: (7, 8), 4: (4, 5)}


def cases():
    pop = json.loads(POP.read_text())
    full = json.loads(FULL.read_text())
    q = sorted(int(s['case'][2:]) for s in full['starts'] if s.get('full_W') == 'y^4 (1+y)^2')
    for i in TEN:
        yield f'T-{i:03d}', {'group': 'T', 'start': pop[i], 'lags': [2, 3], 'rounds': 26}
    for i in q:
        yield f'Q-{i:03d}', {'group': 'Q', 'start': pop[i], 'lags': [2, 3], 'rounds': 26}
    for i, c in enumerate(json.loads(CAT.read_text())):
        yield f'C-{i}', {'group': 'C', 'start': c, 'lags': list(CAT_LAGS[i]), 'rounds': 40}


def run(case_id, payload):
    st, lags = payload['start'], tuple(payload['lags'])
    P = S.grow(st, payload['rounds'], 40000)
    par, ch, br = S.family(P)
    c = P.counts_by_round()
    T = P.rounds
    s = S.out_shares(P, ch)
    shares = [len({s[j] for j in br[t]}) for t in range(1, T)]          # rounds whose children are all grown
    k = S.sum_kinds(P, ch, 6)
    kinds = [len({k[j] for j in br[t]}) for t in range(1, T - 6 + 1)]
    l1, l2 = lags
    if payload['group'] == 'C':
        # the catalogue's counts carry a constant part (a factor x - 1), so no round has c(t) = c(t - l1) + c(t - l2): every round
        # past the lags is tested for a matching that saturates the smaller side
        rounds = list(range(l2 + 1, T + 1))
    else:
        rounds = [t for t in range(l2 + 1, T + 1) if c[t] == c[t - l1] + c[t - l2]]
    d = [c[t] - c[t - 2] - c[t - 3] for t in range(3, T + 1)]
    hall = []
    for t in rounds:
        a = S.spine(P, par, br, t, lags)
        b = S.spine(P, par, br, t, lags, only_single=True)
        hall.append({'t': t, 'left': a['left'], 'right': a['right'], 'matched': a['matched'], 'single_matched': b['matched']})
    out = {'counts': c, 'lags': list(lags), 'shares': shares, 'kinds': kinds, 'd': d, 'recurrence_rounds': rounds, 'hall': hall}
    if len(rounds) >= 4 and payload['group'] != 'C':
        rels = {t: S.typed_relation(P, par, br, t, lags) for t in rounds}
        freq = Counter(ty for rel in rels.values() for *_, ty in rel)
        types = [ty for ty, _ in freq.most_common(10)]
        half = rounds[len(rounds) // 2 - 1]
        first = {t: r for t, r in rels.items() if t <= half}
        second = {t: r for t, r in rels.items() if t > half}
        good = S.biregular_sets(first, br, lags, types, 3)
        out['types'] = len(freq)
        out['spines_first_half'] = [[str(x) for x in Tt] + [e] for Tt, e in good]
        out['spines_both_halves'] = [[str(x) for x in Tt] + [e] for Tt, e in good
                                     if S.biregular_sets(second, br, lags, list(Tt), len(Tt))]
    return out
