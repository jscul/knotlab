"""Exploratory feel for Class B (addressed knots), not a registered result.
Binary invertible Mealy automata with s states; knots {x, a(x), b(x)} (rule R2) or {q1 x, q2 x, q3 x} (R1, s = 3),
degenerate triples dropped. Fates at levels 1..N by SAT; interface growth = knots meeting both first-letter halves."""
import itertools, sys, collections
from pysat.solvers import Minisat22

N = int(sys.argv[1]) if len(sys.argv) > 1 else 10


def act(aut, q, x, n):
    """apply state q to word x (int, n bits, first letter = most significant)."""
    sw, d0, d1 = aut
    y = 0
    for i in range(n - 1, -1, -1):
        b = (x >> i) & 1
        y = (y << 1) | (b ^ sw[q])
        q = d0[q] if b == 0 else d1[q]
    return y


def knots(aut, states, n):
    out = set()
    for x in range(1 << n):
        t = tuple(x if q is None else act(aut, q, x, n) for q in states)
        if len(set(t)) == 3:
            out.add(tuple(sorted(t)))
    return out


def alive(K, n):
    if not K:
        return True
    s = Minisat22()
    for a, b, c in K:
        s.add_clause([a + 1, b + 1, c + 1]); s.add_clause([-a - 1, -b - 1, -c - 1])
    r = s.solve(); s.delete(); return r


def interface(K, n):
    h = 1 << (n - 1)
    return sum(1 for k in K if len({v >= h for v in k}) == 2)


def run(s, rule):
    fates = collections.Counter(); prof = collections.Counter(); iface = collections.Counter()
    for sw in itertools.product((0, 1), repeat=s):
        for d0 in itertools.product(range(s), repeat=s):
            for d1 in itertools.product(range(s), repeat=s):
                aut = (sw, d0, d1)
                if rule == "R2":
                    choices = [(None, a, b) for a in range(s) for b in range(a + 1, s)] + [(None, a, a) for a in []]
                else:
                    choices = [(0, 1, 2)]
                for st in choices:
                    life = []; ifs = []; nk = []
                    for n in range(1, N + 1):
                        K = knots(aut, st, n)
                        nk.append(len(K)); life.append(alive(K, n)); ifs.append(interface(K, n) if n > 1 else 0)
                    if sum(nk) == 0:
                        fates["no knots at any level"] += 1; continue
                    first = next(i for i, v in enumerate(nk) if v)
                    L = life[first:]
                    if all(L): f = "alive at every level read"
                    elif not any(L): f = "dead from its first knots"
                    elif L[-1] is False and any(L): f = "lives a while then dies"
                    else: f = "dies then lives again"
                    fates[f] += 1
                    prof["".join("1" if v else "0" for v in life)] += 1
                    # interface growth class within N: bounded if max over last half <= max over first half
                    a, b = max(ifs[1:N // 2 + 1]), max(ifs[N // 2:])
                    g = "none" if b == 0 else ("bounded" if b <= max(a, 1) else ("grows" ))
                    iface[(f, g)] += 1
    return fates, prof, iface


if __name__ == "__main__":
    for s, rule in ((2, "R2"), (3, "R2"), (3, "R1")):
        f, p, i = run(s, rule)
        print("== s =", s, rule, dict(f))
        print("   interface x fate:", dict(i))
        print("   top life profiles:", p.most_common(8))
        sys.stdout.flush()
