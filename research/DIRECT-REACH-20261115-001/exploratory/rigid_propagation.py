"""Where a description's tie classes are huge (a rigid or nearly rigid pattern), does level n force level n + 1?

DIRECT-REACH-20261115-001, exploratory, the thread's own code. For a population-D description: one state at depth N; the number of
distinct residuals x -> f(w x) of that state (|w| <= 4, read on the levels below) as a first sign of an automatic state; and, for
each level n < N, how many level-(n + 1) addresses unit propagation forces once level n is fixed to the state's values, using only
the knots that lie in levels n and n + 1 (a slice of the pattern). If the slice forces all of level n + 1 at every n and the state is
automatic, rigidity at every depth reduces to a finite check.
"""
import json
import sys
from pathlib import Path

import numpy as np
from pysat.solvers import Cadical195

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from pattern import pattern, clauses, level  # noqa: E402


def one_state(K, nv, seed=0):
    with Cadical195(bootstrap_with=clauses(K)) as s:
        if not s.solve():
            return None
        m = set(x for x in s.get_model() if x > 0)
    return [1 if v + 1 in m else 0 for v in range(nv)]


def unit_propagate(knots, fixed):
    """NAE unit propagation: a knot with two members fixed equal forces the third to differ."""
    val = dict(fixed)
    changed = True
    while changed:
        changed = False
        for a, b, c in knots:
            vs = [val.get(a), val.get(b), val.get(c)]
            unk = [x for x, v in zip((a, b, c), vs) if v is None]
            known = [v for v in vs if v is not None]
            if len(unk) == 1 and known[0] == known[1]:
                val[unk[0]] = 1 - known[0]
                changed = True
            elif not unk and known[0] == known[1] == known[2]:
                return None
    return val


def addr_of(i):
    n = level(i)
    return n, i - (1 << n) + 1


def residuals(f, N, depth=4):
    """Number of distinct functions x -> f(w x) over |x| <= N - depth, for |w| <= depth."""
    out = set()
    for d in range(depth + 1):
        for w in range(1 << d):
            vals = []
            for e in range(N - depth + 1):
                for x in range(1 << e):
                    n = d + e
                    y = (w << e) | x
                    vals.append(f[y + (1 << n) - 1])
            out.add(tuple(vals))
    return len(out)


def analyse(key, N=9):
    K = pattern(key, N)
    nv = (1 << (N + 1)) - 1
    f = one_state(K, nv)
    if f is None:
        return dict(alive=False)
    lv = np.array([level(i) for i in range(nv)])
    forced = []
    for n in range(N):
        sl = [tuple(map(int, r)) for r in K if lv[r[0]] >= n and lv[r[2]] <= n + 1]
        fixed = {i: f[i] for i in range(nv) if lv[i] == n}
        val = unit_propagate(sl, fixed)
        forced.append(sum(1 for i in range(nv) if lv[i] == n + 1 and i in val))
    return dict(alive=True, residuals=residuals(f, N), forced_next=forced, level_sizes=[1 << (n + 1) for n in range(N)])


if __name__ == '__main__':
    base = ROOT / 'experiments/DIRECT-REACH-20261115-001A/DIRECT-REACH-20261115-001A-E001_direct_reach/codex/case_results/D'
    for path in sorted(base.glob('*.json')):
        r = json.load(open(path))
        prof = [x['L_N'] for x in r['census']['levels']]
        sizes = sorted((len(c) for c in r['ties']['classes']), reverse=True)
        a = analyse(r['key'])
        print(path.name[:12], prof, 'classes', len(sizes), sizes[:4], json.dumps(a), flush=True)
