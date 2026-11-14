"""Referee's own check of Codex's monotonicity counterexample (case 162021bb..., k0 = 1, s = 2) from the stored knot lists at N = 3 and
N = 4: least bond holding a level-1 and a level-3 distinction, members anywhere, by SAT projections (pysat), sizes 2 and 3."""
import itertools, json, sys
from pathlib import Path
from pysat.solvers import Glucose4
HERE = Path(__file__).resolve().parent
T = json.load(open(HERE / 'codex/brute_audit/actual_monotonicity_model_tables.json'))
lvl = lambda n: list(range(2**n - 1, 2**(n + 1) - 1))
def least(knots, nvars, A, B, cap):
    cl = []
    for a, b, c in knots:
        cl.append([a + 1, b + 1, c + 1]); cl.append([-(a + 1), -(b + 1), -(c + 1)])
    s = Glucose4(bootstrap_with=cl)
    memo = {}
    def full(sup):
        sup = tuple(sorted(sup))
        if sup not in memo:
            memo[sup] = all(s.solve(assumptions=[(v + 1) if b else -(v + 1) for v, b in zip(sup, bits)])
                            for bits in itertools.product((0, 1), repeat=len(sup)))
        return memo[sup]
    for size in range(2, cap + 1):
        for a in A:
            for b in B:
                others = [v for v in range(nvars) if v not in (a, b)]
                for extra in itertools.combinations(others, size - 2):
                    sup = (a, b) + extra
                    if not full(sup) and all(full(x) for x in itertools.combinations(sup, size - 1)):
                        return size, sorted(sup)
    return '> %d' % cap, None
out = {}
k0, s_ = T['k0'], T['s']
for lv in T['levels']:
    N = lv['N']; nv = 2**(N + 1) - 1
    out[N] = least(lv['knots'], nv, lvl(k0), lvl(k0 + s_), 3)
    print(N, len(lv['knots']), 'knots:', out[N], flush=True)
(HERE / 'referee_monotonicity_check.json').write_text(json.dumps({"case": T['case'], "k0": k0, "s": s_, "results": out}, indent=1))
