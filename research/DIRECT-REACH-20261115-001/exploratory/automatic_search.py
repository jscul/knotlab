"""Search for an automatic state with k Moore states by SAT at depth N, then the all-level check (DIRECT-REACH-20261115-001,
exploratory, the thread's own code). A machine that passes `check_all_levels` proves the pattern alive at every depth."""
import sys
from pathlib import Path

from pysat.solvers import Cadical195
from pysat.card import CardEnc, EncType

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from automatic_life import check_all_levels, values_at_depth  # noqa: E402
from pattern import pattern  # noqa: E402


def search(key, k, N=7, tries=20):
    K = pattern(key, N)
    nv = (1 << (N + 1)) - 1
    top = [0]

    def new():
        top[0] += 1
        return top[0]
    D = [[[new() for _ in range(k)] for _ in (0, 1)] for _ in range(k)]
    O = [new() for _ in range(k)]
    R = [[new() for _ in range(k)] for _ in range(nv)]
    F = [new() for _ in range(nv)]
    cls = []
    for m in range(k):
        for a in (0, 1):
            cls.append(D[m][a])
            cls.extend([-D[m][a][x], -D[m][a][y]] for x in range(k) for y in range(x + 1, k))
    cls.append([R[0][0]])
    for v in range(nv):
        cls.extend([-R[v][x], -R[v][y]] for x in range(k) for y in range(x + 1, k))
        cls.append(R[v])
        for m in range(k):
            cls.append([-R[v][m], -O[m], F[v]])
            cls.append([-R[v][m], O[m], -F[v]])
        if 2 * v + 2 < nv:
            for a in (0, 1):
                c = 2 * v + 1 + a
                for m in range(k):
                    for m2 in range(k):
                        cls.append([-R[v][m], -D[m][a][m2], R[c][m2]])
    for a, b, c in K:
        x, y, z = F[a], F[b], F[c]
        cls.append([x, y, z])
        cls.append([-x, -y, -z])
    with Cadical195(bootstrap_with=cls) as s:
        for _ in range(tries):
            if not s.solve():
                return None, 'no machine with %d states at depth %d' % (k, N)
            model = set(x for x in s.get_model() if x > 0)
            delta = [[next(m2 for m2 in range(k) if D[m][a][m2] in model) for a in (0, 1)] for m in range(k)]
            out = [1 if O[m] in model else 0 for m in range(k)]
            M = (delta, out, 0)
            ok, info = check_all_levels(key, M)
            if ok:
                return M, info
            # block this machine
            s.add_clause([-D[m][a][delta[m][a]] for m in range(k) for a in (0, 1)] + [(-O[m] if out[m] else O[m]) for m in range(k)])
    return None, 'gave up after %d machines' % tries


if __name__ == '__main__':
    import json
    from window_types import population_D
    tally = {}
    results = {}
    for cid, key, prof, cls in population_D():
        found = None
        for k in (1, 2, 3, 4, 5, 6):
            M, info = search(key, k)
            if M is not None:
                found = dict(k=k, machine=M, configurations=info)
                # gate: the machine's values satisfy the depth-9 pattern
                v = values_at_depth(M, 9)
                assert all(len({v[a], v[b], v[c]}) == 2 for a, b, c in pattern(key, 9))
                break
        results[cid] = found
        tag = (str(prof), cls, found['k'] if found else None)
        tally[tag] = tally.get(tag, 0) + 1
        print(cid[:12], prof, cls, json.dumps(found), flush=True)
    json.dump(results, open(HERE / 'automatic_search.json', 'w'), indent=1)
    for t, v in sorted(tally.items(), key=str):
        print(t, v)
