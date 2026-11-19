"""Post hoc reading: the rule's long-horizon growth class of each start, compared with the touch census's measured dimension.
Polynomial of dimension d when the rule's per-round counts have (d-1)-th differences constant over rounds 120 to 160; exponential
when the per-round ratio at round 160 exceeds that at 120 less 0.002 and exceeds 1.01; closed; stall; out of scope."""
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clusters as Cl  # noqa: E402


def growth_class(sizes, e, N=161):
    p = Cl.series(sizes, e, N)
    if p is None:
        return 'out'
    if p == 'stall':
        return 'stall'
    if p[-1] == 0:
        return 0
    w = p[120:161]
    d = w
    for k in range(0, 8):
        if len(set(d)) == 1 and d[0] != 0:
            return k + 1
        d = [d[i + 1] - d[i] for i in range(len(d) - 1)]
    r1, r2 = p[120] / p[119], p[160] / p[159]
    if r2 > 1.01 and r2 > r1 - 0.002:
        return 'exp'
    return 'unsettled'


def chains(sizes, e):
    """Endless chains feeding each piece of the map (open = 2 pendant: one; open = 1 pendant: two; a relay: two), and whether a
    piece has a cycle; returns the largest chain count over pieces without a cycle and the cycle flags."""
    A = Cl.analyse(sizes, e)
    if not A['scope'] or A['stall']:
        return None
    live, blocks, pend = A['live'], A['blocks'], A['pend']
    parent = {k: k for k in live}

    def find(x):
        while parent[x] != x:
            parent[x] = parent[parent[x]]
            x = parent[x]
        return x
    for B in blocks:
        for v in B[1:]:
            parent[find(v)] = find(B[0])
    comps = {}
    for k in live:
        comps.setdefault(find(k), []).append(k)
    out = []
    for ks in comps.values():
        s = set(ks)
        cb = [B for B in blocks if B[0] in s]
        cyc = len(ks) + len(cb) - sum(len(B) for B in cb) != 1
        ch = sum(1 if kind == 1 else 2 if kind == 2 else 0 for k in ks for kind in pend[k])
        if not cyc and ch == 0 and len(comps) > 1:
            ch = 2                                   # the relay
        out.append((ch, cyc))
    return out
