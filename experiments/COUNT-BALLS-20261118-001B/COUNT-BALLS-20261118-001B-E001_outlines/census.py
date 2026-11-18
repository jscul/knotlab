"""Growth against orders on grown split bases: does the ball growth of the disagreement count, read without names, determine
the number of orders?

Populations (all from the line of three, admitted extensions of STATE-RULES-20261117-001B's engine, unchanged, with up to
three betweenness knots per step):
- cheap: the cheapest extensions (fewest states), every tie followed (the growth CUBE-DOUBLING-20261118-001 proves);
- one-split: every extension that adds at most two states (at most one new split), which contains every fewest-state rule.

Readings of a base, all invariant under renaming its distinctions:
- (a) profile: the multiset over distinctions of the sorted row of disagreement counts to the others (equivalently the ball
  sizes at every count), the growth of the count's balls from every start;
- (b) profile with N;
- (c) state profile: the multiset over states of the sorted row of Hamming distances to the other states (states within r
  disagreements of a state).
Targets: k, the least number of colours of the splits' crossing graph (the record's number of orders), and lam, Eppstein's
lattice dimension."""
import itertools
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / "experiments/STATE-RULES-20261117-001B/STATE-RULES-20261117-001B-E001_rules"))
import rules as R  # noqa: E402

pc = int.bit_count


def reachable(pop, nmax):
    canon = R.Canon()
    n, st = R.seed("line")
    level = {canon.cid(st, n)}
    out = {n: sorted(level)}
    while n < nmax:
        nxt = set()
        for c in level:
            s, nn, _ = canon.reps[c]
            ext = R.extensions(list(s), nn, 3)
            if not ext:
                continue
            N = len(s)
            if pop == "cheap":
                low = min(pc(a0) + pc(a1) for (a0, a1) in ext)
                keep = [x for x in ext if pc(x[0]) + pc(x[1]) == low]
            elif pop == "one-split":
                keep = [x for x in ext if pc(x[0]) + pc(x[1]) <= N + 2]
            else:
                raise ValueError(pop)
            for (a0, a1) in keep:
                nxt.add(canon.cid(R.apply(list(s), nn, a0, a1), nn + 1))
        n += 1
        level = nxt
        out[n] = sorted(level)
    return canon, out


def chromatic(sp, full, limit=10):
    s = len(sp)
    adj = [set() for _ in range(s)]
    for i, j in itertools.combinations(range(s), 2):
        if R.crosses(sp[i], sp[j], full):
            adj[i].add(j)
            adj[j].add(i)
    if not any(adj):
        return 1
    for k in range(2, limit + 1):
        if R.colourable(s, adj, k):
            return k
    return None


def readings(states, n):
    states = list(states)
    full = (1 << n) - 1
    sp = R.splits(states, n)
    Z, O = R.columns(states, n)
    rows = tuple(sorted(tuple(sorted(pc(Z[u] & O[v]) + pc(O[u] & Z[v]) for v in range(n) if v != u)) for u in range(n)))
    srows = tuple(sorted(tuple(sorted(pc(a ^ b) for b in states if b != a)) for a in states))
    return {"k": chromatic(sp, full), "lam": R.lattice_dimension(sp, full), "N": len(states),
            "a": rows, "b": (rows, len(states)), "c": srows}


def determination(canon, classes, n):
    """For each reading, the groups of classes it cannot tell apart, and whether k and lam are constant on each."""
    rd = {c: readings(canon.reps[c][0], n) for c in classes}
    out = {}
    for key in ("a", "b", "c"):
        groups = {}
        for c, r in rd.items():
            groups.setdefault(r[key], []).append(c)
        bad_k = [g for g in groups.values() if len({rd[c]["k"] for c in g}) > 1]
        bad_l = [g for g in groups.values() if len({rd[c]["lam"] for c in g}) > 1]
        ex = None
        for g in bad_k + bad_l:
            ex = [{"states": list(canon.reps[c][0]), "k": rd[c]["k"], "lam": rd[c]["lam"], "N": rd[c]["N"]} for c in g[:2]]
            break
        out[key] = {"groups": len(groups), "multi": sum(len(g) > 1 for g in groups.values()),
                    "fail_k": len(bad_k), "fail_lam": len(bad_l), "example": ex}
    kl = {}
    for r in rd.values():
        kl[f"{r['k']},{r['lam']}"] = kl.get(f"{r['k']},{r['lam']}", 0) + 1
    return {"classes": len(classes), "k_lam": kl, "readings": out}


# ---------- explicit split bases (settled statements, checked) ----------

def split_base(points, splits):
    """States of a base whose states are the given splits (sets of point indices), their complements and the constants."""
    n = len(points)
    full = (1 << n) - 1
    st = {0, full}
    for S in splits:
        m = sum(1 << i for i in S)
        st |= {m, full ^ m}
    return sorted(st), n


def box(sides):
    pts = list(itertools.product(*[range(s) for s in sides]))
    sp = [[i for i, p in enumerate(pts) if p[ax] <= c] for ax, s in enumerate(sides) for c in range(s - 1)]
    return pts, split_base(pts, sp)


def tree(edges, m):
    """Split base of a tree on m points given by its edges."""
    import networkx as nx
    T = nx.Graph()
    T.add_nodes_from(range(m))
    T.add_edges_from(edges)
    sp = []
    for u, v in edges:
        T.remove_edge(u, v)
        sp.append(sorted(nx.node_connected_component(T, u)))
        T.add_edge(u, v)
    return list(range(m)), split_base(list(range(m)), sp)


def count_row(states, n, u):
    Z, O = R.columns(list(states), n)
    return [pc(Z[u] & O[v]) + pc(O[u] & Z[v]) for v in range(n)]


def layers(states, n, u):
    """Number of distinctions at each count from u."""
    row = count_row(states, n, u)
    out = {}
    for v, c in enumerate(row):
        if v != u:
            out[c] = out.get(c, 0) + 1
    return dict(sorted(out.items()))
