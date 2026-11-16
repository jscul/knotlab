"""Lower bound L >= 3 at every depth from automatic states (DIRECT-REACH-20261115-001, the thread's own code, 2026-11-16).

An automatic state is a Moore machine M (states, two transitions, an output bit, a start state) whose values f(w) = out(M after reading
w from the first letter) satisfy every knot of the description at every level; exploratory/automatic_life.py checks this by a product
automaton. Each such f restricts to a state of the depth-N pattern for every N, and so does its complement.

For an address x at the top level k and machines M_1..M_r, the pair (x, y) is free in every depth-N pattern (N >= |y|) as soon as two
machines disagree on f_i(x) xor f_i(y): one gives x = y, the other x != y, and complements give the other two patterns. The machines'
joint configuration at y is computed by reading y, so the set of joint configurations at the levels below k is finite and found by a
layered search that stops when a layer repeats. If at none of them the parity vector (f_i(x) xor out_i)_i is constant, no address
below level k is tied to x at any depth. With this for every x at level k, no two-member bond meets level k and any deeper level, so
L_N(k, s) >= 3 for every s >= 1 and every N >= k + s.
"""
import json
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE / 'exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from automatic_life import check_all_levels, values_at_depth  # noqa: E402
from pattern import pattern  # noqa: E402


def machines(key, kmax=4, N=7, want=8, tries=60):
    """Up to `want` distinct automatic states with at most kmax Moore states (each passing the all-level check)."""
    K = pattern(key, N)
    nv = (1 << (N + 1)) - 1
    found, signatures = [], set()
    for k in range(1, kmax + 1):
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
                    break
                model = set(x for x in s.get_model() if x > 0)
                delta = [[next(m2 for m2 in range(k) if D[m][a][m2] in model) for a in (0, 1)] for m in range(k)]
                out = [1 if O[m] in model else 0 for m in range(k)]
                M = (delta, out, 0)
                # block this machine's values on the depth-N addresses (and their complement)
                vals = [1 if F[v] in model else 0 for v in range(nv)]
                s.add_clause([-F[v] if vals[v] else F[v] for v in range(nv)])
                s.add_clause([F[v] if vals[v] else -F[v] for v in range(nv)])
                sig = tuple(values_at_depth(M, 10))
                csig = tuple(1 - b for b in sig)
                if sig in signatures or csig in signatures:
                    continue
                ok, _ = check_all_levels(key, M)
                if ok:
                    found.append(M)
                    signatures.add(sig)
                    if len(found) >= want:
                        return found
    return found


def joint_layers(Ms, max_depth=400):
    """Layers of joint configurations (q_1..q_r) by depth until a layer repeats; returns (layers, start, period)."""
    layer = frozenset([tuple(M[2] for M in Ms)])
    layers, seen = [], {}
    for d in range(max_depth):
        if layer in seen:
            return layers, seen[layer], d - seen[layer]
        seen[layer] = d
        layers.append(layer)
        layer = frozenset(tuple(M[0][q][a] for M, q in zip(Ms, cfg)) for cfg in layer for a in (0, 1))
    raise RuntimeError('no repeat')


def separated(Ms, k):
    """For every x at level k: no configuration at any depth > k makes the parity vector constant. Returns (ok, worst x)."""
    layers, start, period = joint_layers(Ms)
    below = set()
    for d in range(k + 1, max(len(layers), k + 1 + period + start) + period + 1):
        idx = d if d < len(layers) else start + (d - start) % period
        below |= layers[idx]
    outs = {tuple(M[1][q] for M, q in zip(Ms, cfg)) for cfg in below}
    vals = [values_at_depth(M, k) for M in Ms]
    bad = []
    for y in range((1 << k) - 1, (1 << (k + 1)) - 1):
        vx = tuple(v[y] for v in vals)
        nvx = tuple(1 - b for b in vx)
        if vx in outs or nvx in outs:
            bad.append(y)
    return not bad, bad


if __name__ == '__main__':
    from window_types import population_D
    which = sys.argv[1] if len(sys.argv) > 1 else 'constant-3'
    prof_of = {'constant-2': [2] * 4, 'constant-3': [3] * 4, 'half-rate': [3, 3, 4, 4]}
    wt = json.load(open(HERE / 'exploratory/window_tree_census.json'))['cases']
    rows = {}
    for cid, key, prof, cls in population_D():
        if which != 'all' and prof != prof_of[which]:
            continue
        Ms = machines(key)
        res = dict(profile=prof, relative_class=cls, bounded_orbits='k3' in wt[cid], machines=len(Ms))
        if len(Ms) >= 2:
            for k in (2, 3):
                ok, bad = separated(Ms, k)
                res['k%d' % k] = dict(separated=ok, unseparated_top_addresses=bad)
        res['machine_list'] = Ms
        rows[cid] = res
        print(cid[:12], prof, cls, 'bounded' if res['bounded_orbits'] else 'growing', 'machines', len(Ms),
              {k: res[k]['separated'] for k in ('k2', 'k3') if k in res}, flush=True)
    json.dump(rows, open(HERE / ('separation_%s.json' % which), 'w'), indent=1)
    for b in (True, False):
        sub = [r for r in rows.values() if r['bounded_orbits'] == b]
        print('bounded' if b else 'growing', len(sub), 'separated at k=3:', sum(1 for r in sub if r.get('k3', {}).get('separated')))
