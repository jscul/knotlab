"""Gate for marks.py (MARK-RATE-20261116-001, the thread's own code, 2026-11-16): every signature set that a real marking produces is in
the computed family. For small-orbit census rulers and half-rate descriptions with r0 = 0, depth N = 7, a random orbit O at level 2..4
and random marks: (up) marks outside O's proper subtree, O's own addresses allowed; the projection onto O of every knot placed outside
O's subtree, with the marks pinned, computed by SAT, must be empty or in U(type of O); (below) marks strictly inside O's proper
subtree; the projection onto O of every knot placed at O or below, with the marks pinned, must be empty or in below(type of O)."""
import gzip
import itertools
import json
import random
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'research/DIRECT-REACH-20261115-001/exploratory'))
from marks import Marks  # noqa: E402
from window_tree import WindowTree  # noqa: E402
from window_types import step_word  # noqa: E402
from gate_window_tree import orbits_by_level  # noqa: E402

N = 7


def act(D, word, bits):
    ws, out = tuple(word), []
    for b in bits:
        c, ws = step_word(D.aut, ws, b)
        out.append(c)
    return tuple(out)


def placed_knots(D):
    """(placing address, members) for every knot of P_N."""
    out = []
    for n in range(N + 1):
        for x in itertools.product((0, 1), repeat=n):
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
                        out.append((x, tuple(mem)))
    return out


def projection(knots, orbit, marks):
    var = {}

    def v(a):
        if a not in var:
            var[a] = len(var) + 1
        return var[a]
    cls = []
    for mem in knots:
        lits = [v(a) for a in mem]
        cls.append(lits)
        cls.append([-l for l in lits])
    for a in orbit:
        v(a)
    pin = [v(a) if b else -v(a) for a, b in marks.items()]
    out = set()
    with Cadical195(bootstrap_with=cls) as s:
        for bits in itertools.product((0, 1), repeat=len(orbit)):
            if s.solve(assumptions=pin + [v(a) if b else -v(a) for a, b in zip(orbit, bits)]):
                out.add(sum(b << i for i, b in enumerate(bits)))
    return frozenset(out)


if __name__ == '__main__':
    rows = json.load(open(ROOT / 'research/BLOCK-REACH-20261116-001/census_forget.json'))['rows']
    keys = {}
    for line in gzip.open(ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz', 'rt'):
        r = json.loads(line)
        if r['case'] in rows and rows[r['case']]['name'] in ('ruler', 'half-rate') and rows[r['case']]['r0'] == 0:
            keys[r['case']] = r['key']
    rng = random.Random(20261116)
    sample = rng.sample(sorted(keys), 30)
    checked = {'up': 0, 'below': 0}
    missing = []
    for cid in sample:
        tree = WindowTree(keys[cid])
        mk = Marks(tree)
        lv = orbits_by_level(tree, N, tree.feasible(N + 2))
        K = placed_knots(tree.D)
        allv = sorted({a for _, mem in K for a in mem})
        for _ in range(6):
            n = rng.randint(2, 4)
            i = rng.randrange(len(lv[n]))
            t, _, orbit = lv[n][i]
            orbit_set = set(orbit)
            under = lambda a: len(a) >= n and a[:n] in orbit_set
            # up: marks outside O's proper subtree (O itself allowed), knots placed outside O's subtree
            cand = [a for a in allv if not under(a) or len(a) == n]
            marks = {a: rng.randint(0, 1) for a in rng.sample(cand, min(len(cand), rng.randint(0, 3)))}
            X = projection([mem for x, mem in K if not under(x)], orbit, marks)
            checked['up'] += 1
            if X and X not in mk.U[t]:
                missing.append(('up', cid[:12], n, sorted(X)))
            # below: marks strictly under O, knots placed at O or below
            cand = [a for a in allv if under(a) and len(a) > n]
            marks = {a: rng.randint(0, 1) for a in rng.sample(cand, min(len(cand), rng.randint(0, 3)))}
            Y = projection([mem for x, mem in K if under(x)], orbit, marks)
            checked['below'] += 1
            if Y and Y not in mk.below(t):
                missing.append(('below', cid[:12], n, sorted(Y)))
    res = dict(descriptions=len(sample), checked=checked, missing=missing, passed=not missing)
    json.dump(res, open(HERE / 'gate_marks.json', 'w'), indent=1)
    print(res)
