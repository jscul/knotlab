"""Life at every depth from an automatic state (DIRECT-REACH-20261115-001, exploratory, the thread's own code).

A Moore automaton M reads an address from its first letter; its output is the address's value. M's values satisfy every knot of
the description at every level n (knots within a level, and knots joining n to n + 1) exactly when no reachable configuration of
the product below violates a knot; a state at every level is then a state of the pattern at every depth N, so the pattern is alive
at every depth. The product reads w letter by letter and tracks, for each placement's three terms, the run of the term's word and
M's run on its image, and which pairs of images have differed so far (LEVEL-RETURN-20261113-001B's prover, extended to terms that
append a letter). The search for M: residuals of a depth-N state, then the all-level check.
"""
import sys
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(Path(__file__).resolve().parent))
from window_types import words, step_word  # noqa: E402


def check_all_levels(key, M, max_configs=5_000_000):
    """M = (delta, out, start). Returns (True, configurations) or (False, counterexample)."""
    s, sw, d0, d1, placements = key
    aut = (tuple(sw), tuple(d0), tuple(d1))
    W = words(s)
    delta, out, start = M
    total = 0
    for p in sorted({tuple(sorted(t)) for t in placements}):
        terms = [divmod(t, 3) for t in p]
        init = (tuple(W[wi] for wi, _ in terms), (start,) * 3, (False,) * 3)
        seen, dq = {init}, deque([(init, ())])
        while dq:
            (runs, ms, div), path = dq.popleft()
            # the knot placed at this address, if its three members are distinct
            vals, distinct = [], []
            for (wi, slot), m in zip(terms, ms):
                vals.append(out[m] if slot == 0 else out[delta[m][slot - 1]])
            pairs = ((0, 1), (0, 2), (1, 2))
            for k, (i, j) in enumerate(pairs):
                si, sj = terms[i][1], terms[j][1]
                distinct.append((si == 0) != (sj == 0) or div[k] or (si != 0 and sj != 0 and si != sj))
            if all(distinct) and vals[0] == vals[1] == vals[2]:
                return False, dict(placement=p, address=''.join(map(str, path)), values=vals)
            for b in (0, 1):
                outs, nr = zip(*(step_word(aut, r, b) for r in runs))
                nm = tuple(delta[m][c] for m, c in zip(ms, outs))
                nd = tuple(div[k] or outs[i] != outs[j] for k, (i, j) in enumerate(pairs))
                cfg = (tuple(nr), nm, nd)
                if cfg not in seen:
                    seen.add(cfg)
                    dq.append((cfg, path + (b,) if len(path) < 40 else path))
                    if len(seen) > max_configs:
                        raise RuntimeError('too many configurations')
        total += len(seen)
    return True, total


def moore_from_state(f, N, depth=4):
    """A Moore automaton whose states are the residual classes of f (signatures on |x| <= N - depth - 1), or None."""
    L = N - depth - 1

    def sig(d, w):
        vals = []
        for e in range(L + 1):
            for x in range(1 << e):
                n = d + e
                vals.append(f[((w << e) | x) + (1 << n) - 1])
        return tuple(vals)

    cls, rep = {}, []
    for d in range(depth + 1):
        for w in range(1 << d):
            g = sig(d, w)
            if g not in cls:
                cls[g] = len(rep)
                rep.append((d, w))
    delta, out = [], []
    for d, w in rep:
        row = []
        for a in (0, 1):
            g = sig(d + 1, (w << 1) | a)
            if g not in cls:
                return None
            row.append(cls[g])
        delta.append(row)
        out.append(f[w + (1 << d) - 1])
    return delta, out, 0


def sample_states(K, nv, count, seed):
    import random
    from pysat.solvers import Cadical195
    sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
    from pattern import clauses
    rng, cnf, out = random.Random(seed), clauses(K), []
    for _ in range(count):
        with Cadical195(bootstrap_with=cnf) as s:
            s.configure({'lucky': 0, 'walk': 0, 'elim': 0, 'probe': 0})
            s.set_phases([v + 1 if rng.getrandbits(1) else -v - 1 for v in range(nv)])
            if not s.solve():
                return []
            m = set(x for x in s.get_model() if x > 0)
        out.append([1 if v + 1 in m else 0 for v in range(nv)])
    return out


def values_at_depth(M, N):
    delta, out, start = M
    vals, frontier = [out[start]], [start]
    for n in range(1, N + 1):
        frontier = [delta[m][a] for m in frontier for a in (0, 1)]
        vals.extend(out[m] for m in frontier)
    return vals


if __name__ == '__main__':
    import json
    sys.path.insert(0, str(ROOT / 'experiments/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/codex'))
    from pattern import pattern
    from window_types import population_D
    N = 9
    nv = (1 << (N + 1)) - 1
    tally = {}
    for cid, key, prof, cls in population_D():
        K = pattern(key, N)
        found = None
        tried = 0
        for f in sample_states(K, nv, 24, seed=int(cid[:8], 16)):
            M = moore_from_state(f, N)
            if M is None:
                continue
            tried += 1
            ok, info = check_all_levels(key, M)
            if ok:
                v = values_at_depth(M, N)       # gate: the machine's values satisfy the depth-N pattern
                assert all(len({v[a], v[b], v[c]}) == 2 for a, b, c in K)
                found = (len(M[1]), info)
                break
        tag = (str(prof), cls, found is not None)
        tally[tag] = tally.get(tag, 0) + 1
        print(cid[:12], prof, cls, 'machines tried', tried, 'automatic state' if found else 'none', found, flush=True)
    for k, v in sorted(tally.items()):
        print(k, v)
