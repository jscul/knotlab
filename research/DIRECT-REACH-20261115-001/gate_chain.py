"""Gate for chain_ties.py (DIRECT-REACH-20261115-001, the thread's own code, 2026-11-16).

For every chain found by chain_ties.py (ties, constant-2) and chain_bounded3.py (L <= 3, constant-3):
(a) the windows from the type evolution equal the windows computed from explicit addresses (every address v at level k, every
    placement, members computed by acting with the maps on v; kept when all members lie in S_k ∪ S_k·{0,1}), for k = k0..9;
(b) every tie and every constrained triple the chain reports at levels up to 9 holds in the whole depth-9 pattern (SAT), and every
    deep pair reported free has two automatic states with different parities at its explicit addresses;
(c) every automatic state used satisfies the depth-12 pattern knot by knot.
"""
import itertools
import json
import sys
from pathlib import Path

from pysat.solvers import Cadical195

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(HERE / 'exploratory'))
sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
from chain_ties import Extended, initial_type, next_type, window_knots, run_anchored_machines  # noqa: E402
from window_types import Description, step_word, population_D  # noqa: E402
from automatic_life import values_at_depth  # noqa: E402
from pattern import pattern, clauses  # noqa: E402


def act(D, word, bits):
    ws, out = tuple(word), []
    for b in bits:
        c, ws = step_word(D.aut, ws, b)
        out.append(c)
    return tuple(out)


def explicit_knots(D, S):
    """Knots placed at level k (S's level) with all members in S ∪ S·{0,1}, as sorted variable triples (j, or n + 2j + b)."""
    n, k = len(S), len(S[0])
    index = {x: i for i, x in enumerate(S)}
    knots = set()
    for v in itertools.product((0, 1), repeat=k):
        for p in D.placements:
            mem = []
            for t in p:
                wi, slot = divmod(t, 3)
                y = act(D, D.maps[D.slot_map[wi]], v)
                j = index.get(y)
                if j is None:
                    break
                mem.append(j if slot == 0 else n + 2 * j + slot - 1)
            else:
                if len(set(mem)) == 3:
                    knots.add(tuple(sorted(mem)))
    return tuple(sorted(knots))


def aid(bits):
    return int(''.join(map(str, bits)) or '0', 2) + (1 << len(bits)) - 1


def forced(solver, lits):
    return not solver.solve(assumptions=lits)


def gate(key, chain, Ms, N=9):
    D = Description(key)
    E = Extended(D)
    S = [tuple(int(ch) for ch in x) for x in chain['S']]
    pre = [tuple(v) for v in chain['prefix']]
    cyc = [tuple(v) for v in chain['cycle']]
    k0 = chain['k0']
    T = initial_type(E, S)
    cur = list(S)
    window_ok = True
    for step in range(N - k0):
        c = pre[step] if step < len(pre) else cyc[(step - len(pre)) % len(cyc)]
        if window_knots(E, T) != explicit_knots(D, cur):
            window_ok = False
        T = next_type(E, T, c)
        cur = [x + (c[i],) for i, x in enumerate(cur)]
    # (b) claims against the whole depth-N pattern
    r = run_anchored_machines(E, S, pre, cyc, Ms)
    vals9 = [values_at_depth(M, N) for M in Ms]
    claims = bad = 0
    K = pattern(key, N)
    cur = list(S)
    with Cadical195(bootstrap_with=clauses(K)) as s:
        for step, h in enumerate(r['history']):
            c = pre[step] if step < len(pre) else cyc[(step - len(pre)) % len(cyc)]
            nxt = [x + (c[i],) for i, x in enumerate(cur)]
            if len(nxt[0]) > N:
                break
            for i, j, p in h['ties']:
                a, b = aid(S[i]) + 1, aid(nxt[j]) + 1
                claims += 1
                # a xor b == p forced: both assignments with a xor b != p impossible
                if not (forced(s, [-a, b if p == 0 else -b]) and forced(s, [a, -b if p == 0 else b])):
                    bad += 1
            for i, i2, j in h['triples']:
                a, b, z = aid(S[i]) + 1, aid(S[i2]) + 1, aid(nxt[j]) + 1
                claims += 1
                if all(s.solve(assumptions=[a if x else -a, b if y else -b, z if w else -z])
                       for x, y, w in itertools.product((0, 1), repeat=3)):
                    bad += 1
            for i, j, j2 in h['deep_triples']:
                a, b, z = aid(S[i]) + 1, aid(nxt[j]) + 1, aid(nxt[j2]) + 1
                claims += 1
                if all(s.solve(assumptions=[a if x else -a, b if y else -b, z if w else -z])
                       for x, y, w in itertools.product((0, 1), repeat=3)):
                    bad += 1
                # the deep pair's freeness: two machines with different parities at the explicit addresses
                if len({f[b - 1] ^ f[z - 1] for f in vals9}) != 2:
                    bad += 1
            cur = nxt
    # (c) machines against depth 12
    K12 = pattern(key, 12)
    life_ok = True
    for M in Ms:
        f = values_at_depth(M, 12)
        if not all(len({f[a], f[b], f[c]}) == 2 for a, b, c in K12):
            life_ok = False
    return dict(windows_equal=window_ok, claims=claims, false_claims=bad, machines_checked=len(Ms), machines_ok=life_ok)


if __name__ == '__main__':
    auto = json.load(open(HERE / 'exploratory/automatic_search.json'))
    keys = {cid: key for cid, key, _, _ in population_D()}
    out = {}
    for name in ('chain_ties_constant-2.json', 'chain_bounded3_constant-3.json'):
        p = HERE / name
        if not p.exists():
            continue
        for cid, row in json.load(open(p)).items():
            if not row.get('chain'):
                continue
            Ms = row.get('machines') or ([auto[cid]['machine']] if auto.get(cid) else [])
            g = gate(keys[cid], row['chain'], Ms)
            out[name + ':' + cid] = g
            print(name, cid[:12], g, flush=True)
    passed = all(g['windows_equal'] and g['false_claims'] == 0 and g['machines_ok'] for g in out.values())
    json.dump(dict(passed=passed, cases=out), open(HERE / 'gate_chain.json', 'w'), indent=1)
    print('passed', passed, 'cases', len(out), 'claims', sum(g['claims'] for g in out.values()))
