"""Gate for forget.py (BLOCK-REACH-20261116-001, the thread's own code, 2026-11-16).

(a) Window relations against SAT: for small-orbit census descriptions, depth N, a random orbit O_j at level j and a random descending
    path of r block steps to O_(j+r), the composed relation from forget.Steps (remaining depth N - j - 1) equals the projection onto
    (O_j, O_(j+r)) of the sub-pattern of every knot placed at an address under O_j and not under O_(j+r), computed by SAT from explicit
    addresses and placements.
(b) The bound against the census: for every small-orbit census description with a least r, every decided depth-9 value
    L_N(3, s), s = 1..4, is at least 1 + ceil(s/r)."""
import gzip
import itertools
import json
import math
import random
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from forget import Steps, compose, least_forget  # noqa: E402
from window_tree import WindowTree  # noqa: E402
from window_types import step_word  # noqa: E402
from gate_window_tree import orbits_by_level  # noqa: E402

CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'


def act(D, word, bits):
    ws, out = tuple(word), []
    for b in bits:
        c, ws = step_word(D.aut, ws, b)
        out.append(c)
    return tuple(out)


def window_relation_sat(tree, N, j, top_addrs, bottom_addrs):
    """Projection onto (O_j, O_(j+r)) of the knots placed under O_j and not under O_(j+r), by SAT."""
    D = tree.D
    r = len(bottom_addrs[0]) - j
    top, bottom = set(top_addrs), set(bottom_addrs)
    var, clauses = {}, []

    def v(a):
        if a not in var:
            var[a] = len(var) + 1
        return var[a]
    for a in top_addrs + bottom_addrs:
        v(a)
    for n in range(j, N + 1):
        for x in itertools.product((0, 1), repeat=n):
            if x[:j] not in top or (n >= j + r and x[:j + r] in bottom):
                continue
            for p in D.placements:
                mem = []
                for t in p:
                    wi, slot = divmod(t, 3)
                    if slot and n == N:
                        break
                    y = act(D, D.maps[D.slot_map[wi]], x)
                    mem.append(y if slot == 0 else y + (slot - 1,))
                else:
                    if len(set(mem)) == 3:
                        lits = [v(m) for m in mem]
                        clauses.append(lits)
                        clauses.append([-l for l in lits])
    out = set()
    allv = [var[a] for a in top_addrs] + [var[a] for a in bottom_addrs]
    with Cadical195(bootstrap_with=clauses) as s:
        for bits in itertools.product((0, 1), repeat=len(allv)):
            if s.solve(assumptions=[x if b else -x for x, b in zip(allv, bits)]):
                a = sum(b << i for i, b in enumerate(bits[:len(top_addrs)]))
                z = sum(b << i for i, b in enumerate(bits[len(top_addrs):]))
                out.add((a, z))
    return frozenset(out)


def gate_windows(keys, N=7, per=4, seed=20261116):
    rng = random.Random(seed)
    checked = mism = 0
    for key in keys:
        tree = WindowTree(key)
        st = Steps(tree)
        lv = orbits_by_level(tree, N, tree.feasible(N + 2))
        # child index map: level n orbit i -> list of (child index ci, level n+1 orbit index)
        kids = {}
        for n in range(N):
            idx = 0
            for i, (t, up, addrs) in enumerate(lv[n]):
                kids[(n, i)] = []
                for ci in range(len(tree.children[t])):
                    kids[(n, i)].append((ci, idx))
                    idx += 1
        for _ in range(per):
            r = rng.randint(1, 3)
            j = rng.randint(1, N - r)
            i = rng.randrange(len(lv[j]))
            t0 = lv[j][i][0]
            R = frozenset((x, x) for x in range(1 << tree.m[t0]))
            n, cur, t = j, i, t0
            for step in range(r):
                ci, nxt = rng.choice(kids[(n, cur)])
                c, S = st.rel(t, ci, N - n - 1)
                R = compose(R, S)
                n, cur, t = n + 1, nxt, c
            J = window_relation_sat(tree, N, j, lv[j][i][2], lv[n][cur][2])
            checked += 1
            if J != R:
                mism += 1
                print('MISMATCH', key, j, r, len(R), len(J), flush=True)
    return checked, mism


if __name__ == '__main__':
    recs = [json.loads(l) for l in gzip.open(CENSUS, 'rt')]
    small, rows = [], {}
    for rec in recs:
        if rec.get('union') != 'alive' or 'key' not in rec:
            continue
        f = least_forget(rec['key'])
        if not f['small_orbits']:
            continue
        rows[rec['case']] = (rec, f)
        small.append(rec['key'])
    rng = random.Random(7)
    sample = rng.sample(small, 25)
    checked, mism = gate_windows(sample)
    viol = []
    for cid, (rec, f) in rows.items():
        if f['r'] is None:
            continue
        for lvd in rec['levels']:
            L = lvd['L_N']
            if isinstance(L, int) and L < 1 + math.ceil(lvd['s'] / f['r']):
                viol.append((cid[:12], lvd['s'], L, f['r']))
    res = dict(window_relations_checked=checked, mismatches=mism, census_small_orbit=len(rows), census_violations=viol,
               passed=mism == 0 and not viol)
    json.dump(res, open(HERE / 'gate_forget.json', 'w'), indent=1)
    print(res)
