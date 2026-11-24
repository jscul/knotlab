"""Self-checks of ticket C's engine. Usage: python -B selfcheck.py [engine|bbb|determinism|all]

engine:      the group rule against a deliberately naive implementation on random rosters; met sets
             against a naive computation on random structures; the exact matcher against networkx;
             the sameness tests (renamed copies accepted, copies with one distinction moved
             rejected); part-round ALL-IN-TURN against complete rounds for 8 rounds; the induced
             structure of a longer run against R complete rounds.
bbb:         the birth-by-birth engine's incremental parts against a full recomputation after every
             move, and the hand-sized trace d2_4_trace.txt.
determinism: reruns of C1, C2 and C3 pieces give identical output.
"""

import json
import os
import random
import sys
from itertools import combinations
from types import SimpleNamespace

import growth as g
import iso
import part_round as pr

HERE = os.path.dirname(os.path.abspath(__file__))
ART = os.path.join(HERE, "..", "..", "..", "artifacts", "RING-IN-BALANCE-20261123-001C",
                   "RING-IN-BALANCE-20261123-001C-E001_no_round")
ART = os.path.normpath(ART)


# ------------------------------------------------------------------------------- naive group rule
def naive_groups(members, family):
    """The definition read literally, by enumerating every subset."""
    def joinable(u, v):
        return any(u in M and v in M for M in family)

    sets = []
    for r in range(3, len(members) + 1):
        for T in combinations(members, r):
            if all(joinable(u, v) for u, v in combinations(T, 2)) and not any(set(T) <= M for M in family):
                sets.append(frozenset(T))
    maxi = [T for T in sets if not any(T < U for U in sets)]
    pairs = [frozenset((u, v)) for u, v in combinations(members, 2)
             if joinable(u, v) and not any({u, v} <= T for T in maxi)]
    out = maxi + pairs
    out.sort(key=lambda G: (len(G), sorted(G)))
    return out


def check_group_rule(trials=4000, seed=1):
    rng = random.Random(seed)
    big = 0
    for t in range(trials):
        n = rng.randint(2, 9)
        members = list(range(n))
        fam = set()
        for _ in range(rng.randint(1, 8)):
            k = rng.randint(2, min(5, n))
            fam.add(frozenset(rng.sample(members, k)))
        a = g.compute_groups(fam)
        b = naive_groups(members, fam)
        assert a == b, (t, sorted(map(sorted, fam)), a, b)
        big += sum(1 for G in a if len(G) >= 3)
    return {"trials": trials, "groups_of_three_or_more_seen": big, "agree": True}


def random_structure(rng):
    """Random small structure: knots with shared and loose distinctions."""
    nk = rng.randint(2, 8)
    stars = [[] for _ in range(nk)]
    d = 0
    for _ in range(rng.randint(1, 12)):
        a, b = rng.sample(range(nk), 2)
        stars[a].append(d)
        stars[b].append(d)
        d += 1
    for k in range(nk):
        for _ in range(rng.choice([0, 0, 1, 2, 3])):
            stars[k].append(d)
            d += 1
    stars = [s for s in stars if s]
    return g.from_stars(stars) if stars else None


def check_met_sets(trials=3000, seed=2):
    rng = random.Random(seed)
    for t in range(trials):
        S = random_structure(rng)
        if S is None:
            continue
        S.check()
        mem = S.members
        naive = {}
        for x in range(S.nknots()):
            ys = frozenset(y for y in mem if y != x and set(S.places[x]) & set(S.places[y]))
            if len(ys) >= 2:
                naive[x] = ys
        assert g.met_sets(S, mem) == naive, t
        # groups from the structure agree with the naive rule too
        fam = set(naive.values())
        assert g.compute_groups(fam) == naive_groups(sorted(mem), fam)
    return {"trials": trials, "agree": True}


def check_matcher(trials=600, seed=3):
    import networkx as nx
    rng = random.Random(seed)
    agree = 0
    for t in range(trials):
        n = rng.randint(1, 11)
        p = rng.random()
        G1 = nx.gnp_random_graph(n, p, seed=rng.randrange(10**9))
        cols = [rng.randint(0, 2) for _ in range(n)]
        if rng.random() < 0.5:
            perm = list(range(n))
            rng.shuffle(perm)
            G2 = nx.relabel_nodes(G1, {i: perm[i] for i in range(n)})
            cols2 = [0] * n
            for i in range(n):
                cols2[perm[i]] = cols[i]
        else:
            G2 = nx.gnp_random_graph(n, p, seed=rng.randrange(10**9))
            cols2 = [rng.randint(0, 2) for _ in range(n)]
        a = iso.Graph(cols, [sorted(G1.neighbors(v)) for v in range(n)])
        b = iso.Graph(cols2, [sorted(G2.neighbors(v)) for v in range(n)])
        for v in range(n):
            G1.nodes[v]["c"] = cols[v]
            G2.nodes[v]["c"] = cols2[v]
        truth = nx.is_isomorphic(G1, G2, node_match=lambda x, y: x["c"] == y["c"])
        mine = iso.isomorphism(a, b) is not None
        assert truth == mine, t
        if truth:
            assert iso.graph_hash(a) == iso.graph_hash(b)
        agree += 1
    return {"trials": trials, "agree": agree}


# ------------------------------------------------------------------------------- sameness (G(c))
def export(S, colour):
    stars = [list(S.places[k]) for k in range(S.nknots())]
    cols = [colour(k) for k in range(S.nknots())]
    barred = {d for d in range(len(S.holders)) if S.barred[d]}
    return stars, cols, barred


def graph_of(stars, cols, barred):
    places = stars
    nd = 1 + max((d for s in stars for d in s), default=-1)
    ns = SimpleNamespace(places=places, barred=[d in barred for d in range(nd)])
    return g.structure_graph(ns, range(len(stars)), lambda k: cols[k])


def renamed(stars, cols, barred, rng):
    nk = len(stars)
    kperm = list(range(nk))
    rng.shuffle(kperm)
    ds = sorted({d for s in stars for d in s})
    dperm = ds[:]
    rng.shuffle(dperm)
    dmap = dict(zip(ds, dperm))
    new_stars = [None] * nk
    new_cols = [None] * nk
    for k in range(nk):
        st = [dmap[d] for d in stars[k]]
        rng.shuffle(st)
        new_stars[kperm[k]] = st
        new_cols[kperm[k]] = cols[k]
    return new_stars, new_cols, {dmap[d] for d in barred}


def moved(stars, cols, barred, rng, kind):
    """Move one distinction from knot X to a knot Y of the same colour and the same number of
    places, so that the multiset of place counts in that colour changes (the copy is then
    certainly not the same structure)."""
    holders = {}
    for k, s in enumerate(stars):
        for d in s:
            holders.setdefault(d, []).append(k)
    cands = []
    for d, hs in holders.items():
        if (kind == "loose") != (len(hs) == 1):
            continue
        for X in hs:
            for Y in range(len(stars)):
                if Y not in hs and cols[Y] == cols[X] and len(stars[Y]) == len(stars[X]):
                    cands.append((d, X, Y))
    if not cands:
        return None
    d, X, Y = rng.choice(sorted(cands))
    new = [list(s) for s in stars]
    new[X].remove(d)
    new[Y].append(d)
    return new, list(cols), set(barred)


def check_sameness(seed=4):
    rng = random.Random(seed)
    out = []
    cases = []
    for start, law, R in [("D2(5,3)", g.TWO, 6), ("Ring(5,3)", g.THREE, 5), ("D2(4,3)", g.THREE, 7),
                          ("Ring(5,3)", g.TWO, 7)]:
        S, _ = g.complete_rounds(start, law, R)
        cases.append((f"{start} {law.name} after {R} rounds", S, lambda k, S=S: S.born[k]))
    S7 = g.make_start("GEN7")
    cases.append(("seven-knot generator", S7, lambda k: 0))
    for name, S, colour in cases:
        stars, cols, barred = export(S, colour)
        base = graph_of(stars, cols, barred)
        rec = {"structure": name, "knots": len(stars), "renamed_accepted": 0, "renamed_trials": 0,
               "moved_rejected": 0, "moved_trials": 0}
        for _ in range(5):
            r = renamed(stars, cols, barred, rng)
            rec["renamed_trials"] += 1
            if iso.same(base, graph_of(*r)):
                rec["renamed_accepted"] += 1
        for kind in ("loose", "shared"):
            for _ in range(5):
                m = moved(stars, cols, barred, rng, kind)
                if m is None:
                    continue
                rec["moved_trials"] += 1
                gm = graph_of(*m)
                if not iso.same(base, gm):
                    rec["moved_rejected"] += 1
                # also the exact test alone, without the hash
                assert iso.isomorphism(base, gm) is None
        out.append(rec)
    # rosters (the sameness of parts): renamed copies accepted, a changed h or a moved member rejected
    rost = []
    for start, law, R in [("D2(5,3)", g.TWO, 1), ("D2(5,3)", g.TWO, 0), ("Ring(5,3)", g.THREE, 2)]:
        S, _ = g.complete_rounds(start, law, R) if R else (g.make_start(start), None)
        mem = sorted(S.members)
        fam = g.roster_family(S, set(mem))
        mx = [sorted(M) for M in g.maximal_sets(fam)]
        hk = {u: (S.h(u), S.nbar[u]) for u in mem}

        def rgraph(mem, mx, hk):
            idx = {u: i for i, u in enumerate(mem)}
            col = [iso.stable_int(("m",) + hk[u]) for u in mem]
            adj = [[] for _ in mem]
            for M in mx:
                j = len(col)
                col.append(iso.stable_int(("M",)))
                adj.append([])
                for u in M:
                    adj[idx[u]].append(j)
                    adj[j].append(idx[u])
            return iso.Graph(col, adj)

        base = rgraph(mem, mx, hk)
        assert iso.graph_hash(base) == iso.graph_hash(g.roster_graph(S, mem))
        acc = 0
        for _ in range(5):
            perm = mem[:]
            rng.shuffle(perm)
            ren = dict(zip(mem, perm))
            acc += iso.same(base, rgraph(sorted(perm), [sorted(ren[u] for u in M) for M in mx],
                                         {ren[u]: hk[u] for u in mem}))
        u = rng.choice(mem)
        hk2 = dict(hk)
        hk2[u] = (hk[u][0] + 1, hk[u][1])
        rej_h = not iso.same(base, rgraph(mem, mx, hk2))
        rost.append({"roster": f"{start} {law.name} after {R} rounds", "members": len(mem),
                     "renamed_accepted": acc, "renamed_trials": 5, "changed_h_rejected": rej_h})
    ok = all(r["renamed_accepted"] == r["renamed_trials"] and r["moved_rejected"] == r["moved_trials"]
             and r["moved_trials"] > 0 for r in out) and all(
        r["renamed_accepted"] == 5 and r["changed_h_rejected"] for r in rost)
    return {"structures": out, "rosters": rost, "pass": ok}


# ------------------------------------------------------------------------------- the round
def check_part_vs_complete():
    keys = ["members", "parts", "h_sorted", "maximal_met_set_sizes_sorted", "births", "fresh_total",
            "births_sorted"]
    out = []
    for start in ["Ring(5,3)", "D2(4,3)", "D2(5,3)", "DW(5,3)", "D2(6,3)", "Ring(7,3)"]:
        for law in [g.TWO, g.THREE]:
            run = pr.PartRoundRun(start, law, "ALL-IN-TURN")
            tr = run.run_sweeps(8)
            S, h = g.complete_rounds(start, law, 8)
            trace_ok = all(all(a[k] == b[k] for k in keys) for a, b in zip(tr, h)) and len(tr) == len(h)
            g1 = g.structure_graph(run.S, range(run.S.nknots()), lambda k: run.S.born[k])
            g2 = g.structure_graph(S, range(S.nknots()), lambda k: S.born[k])
            iso_ok = iso.isomorphism(g1, g2) is not None
            run.S.check()
            S.check()
            out.append({"start": start, "law": law.name, "trace_equal": trace_ok, "structures_same": iso_ok})
    return {"cases": out, "pass": all(c["trace_equal"] and c["structures_same"] for c in out)}


def check_induced_equals_rounds():
    out = []
    for start, law in [("D2(5,3)", g.TWO), ("Ring(5,3)", g.THREE), ("D2(4,3)", g.TWO)]:
        S_long, _ = g.complete_rounds(start, law, 9)
        for R in (2, 5, 6):
            S_R, _ = g.complete_rounds(start, law, R)
            a = g.structure_graph(S_long, [k for k in range(S_long.nknots()) if S_long.born[k] <= R],
                                  lambda k: S_long.born[k])
            b = g.structure_graph(S_R, range(S_R.nknots()), lambda k: S_R.born[k])
            out.append({"start": start, "law": law.name, "R": R, "same": iso.isomorphism(a, b) is not None})
    return {"cases": out, "pass": all(c["same"] for c in out)}


def engine_checks():
    res = {}
    res["group_rule_vs_naive"] = check_group_rule()
    res["met_sets_vs_naive"] = check_met_sets()
    res["matcher_vs_networkx"] = check_matcher()
    res["sameness"] = check_sameness()
    res["part_round_all_in_turn_vs_complete_rounds"] = check_part_vs_complete()
    res["induced_vs_R_rounds"] = check_induced_equals_rounds()
    return res


if __name__ == "__main__":
    what = sys.argv[1] if len(sys.argv) > 1 else "all"
    os.makedirs(ART, exist_ok=True)
    out = {}
    if what in ("engine", "all"):
        out["engine"] = engine_checks()
    if what in ("bbb", "all"):
        import selfcheck_bbb
        out["bbb"] = selfcheck_bbb.bbb_checks(ART)
    if what in ("determinism", "all"):
        import selfcheck_bbb
        out["determinism"] = selfcheck_bbb.determinism_checks()
    path = os.path.join(ART, f"selfcheck_{what}.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=1, sort_keys=True)
    print(json.dumps(out, indent=1, sort_keys=True)[:6000])
    print("written", path)
