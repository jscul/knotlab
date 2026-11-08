#!/usr/bin/env python3
"""Checks for GROWTH-LAW-20261107-001A: a beginning is a knot (a growth history under the knot test).

    python3 -B check.py          verify result.json against a fresh run
    python3 -B check.py --write  write result.json from a fresh run
Run with the repository's .venv (check 6 imports GROW-COIN-20261107-001A's growth library, which needs numpy). Single process,
under a minute. Every verdict is computed from allowed states; knotlab's check_knot cross-checks a sample."""
import collections
import hashlib
import itertools
import json
import random
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "tools"))
import growth_law_lib as G  # noqa: E402
from knotlab.knots import check_knot  # noqa: E402
from knotlab.relations import Relation  # noqa: E402

GC = ROOT / "proofs/GROW-COIN-20261107-001A/GROW-COIN-20261107-001A-P001_refinement_shares_its_coin_accretion_must_carry_it"

T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str)[:600], round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def knotlab_agrees(R, names):
    """knotlab's own K1-K3 on the shadow over names (the last name as contact)"""
    S = R.shadow(names)
    rel = Relation(S.names, frozenset(tuple(bool(r >> i & 1) for i in range(S.n)) for r in S.rows))
    return check_knot(rel, S.names[:-1], S.names[-1]).is_knot


def sources(n_knots, edges, r):
    parents = collections.Counter()
    for i, (a, b) in enumerate(edges):
        parents[b if r >> i & 1 else a] += 1
    return [v for v in range(n_knots) if parents[v] == 0]


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"] if q.endswith(".json")}
    check("0 dependency artifacts bound by hash; upstream proofs Proved", not bad and all(s in ("Proved", "passed") for s in status.values()),
          {"mismatched": bad, "statuses": status})

    # 1 the open-end rule's histories on the thread it grows
    rows = []
    ok = True
    for n in range(2, 8):
        births = G.open_end_histories(n)
        dist, edges = G.thread(n)
        H = G.history_relation(n, "seam")
        monotone = {sum(1 << i for i in range(a, n - 1)) for a in range(n)}
        one_beginning = all(len(sources(n, edges, r)) == 1 for r in H.rows)
        good = len(births) == 2 ** (n - 1) and set(H.rows) == monotone and one_beginning
        rows.append([n, len(births), len(H.rows), good])
        ok &= good
    check("1 the open-end rule's runs to n knots (n = 2..7): 2^(n-1) birth orders; their seam bits are the n monotone sequences, "
          "each with exactly one knot without a parent", ok, {"[n, birth orders, seam-bit histories, ok]": rows})

    # 2 Theorem 1 on a fixed substrate: the joint law is a product, and its knots are the thread's bonds
    rows = []
    ok = True
    for kind, ns in (("seam", range(2, 6)), ("pair", range(2, 5))):
        for n in ns:
            dist, edges = G.thread(n)
            X = G.parity_law(dist)
            H = G.history_relation(n, kind)
            J = G.product(H, X)
            ks = G.knots(J)
            groups = {"history": set(H.names), "state": set(X.names)}
            cls = collections.Counter(G.classify(J, T, groups) for T in ks)
            xk = {frozenset(J.names_of(T)) for T in ks if G.classify(J, T, groups) == ("state",)}
            sample = ks[len(ks) // 2]
            good = (set(cls) <= {("state",)} and xk == G.bonds(dist, edges) and G.is_2cnf(H) and not G.knots(H)
                    and knotlab_agrees(J, J.names_of(sample)))
            rows.append([kind, n, J.n, len(J.rows), dict((",".join(k), v) for k, v in cls.items()), good])
            ok &= good
    check("2 Theorem 1, fixed substrate: the joint law of the open-end rule's history (seam bits n <= 5, pair bits n <= 4) and the "
          "thread's states is a product; every knot is a bond of the thread; the history alone is 2-CNF with no knot", ok,
          {"[history bits, n, variables, rows, knots by kind, ok]": rows})

    # 3 control: a rule that reads a state makes knots that join the order to the states
    rows = []
    ok = True
    for n in (4, 5):
        R = G.state_reading_joint(n)
        ks = G.knots(R)
        groups = {"history": {v for v in R.names if v.startswith("h_")}, "state": {v for v in R.names if not v.startswith("h_")}}
        cross = [R.names_of(T) for T in ks if G.classify(R, T, groups) == ("history", "state")]
        rows.append([n, len(ks), len(cross), cross[:2]])
        ok &= len(cross) > 0 and knotlab_agrees(R, cross[0])
    check("3 control: a rule that reads a state (an inner knot grows right when its own open end is 1, left when 0) gives knots "
          "joining the order to the states", ok, {"[n, knots, crossing knots, examples]": rows})

    # 4 Theorem 1 with substrates that vary: forgotten pair bits free -> no order-state knot; set to 0 -> there are
    rows = {}
    R, groups = G.existence_joint("free")
    ks = G.knots(R)
    cls = collections.Counter(G.classify(R, T, groups) for T in ks)
    guards_ok = True
    for T in ks:
        if G.classify(R, T, groups) == ("existence", "state"):
            names = R.names_of(T)
            ex = [v for v in names if v.startswith("e_")]
            Rs = R.restrict({v: 1 for v in ex})
            guards_ok &= G.is_knot_set(Rs, [v for v in names if not v.startswith("e_")])
    per_sub = {str(s): sorted(set(G.classify(S, T, groups) for T in G.knots(S))) for s, S in G.substrate_restrictions(R)}
    staircase = [R.names_of(T) for T in ks if G.classify(R, T, groups) == ("existence", "order")]
    rows["forgotten pair bits free"] = {"knots by kind": dict((",".join(k), v) for k, v in cls.items()), "history-internal": staircase,
                                        "each fixed substrate": per_sub}
    Rz, _ = G.existence_joint("zero")
    kz = G.knots(Rz)
    clz = collections.Counter(G.classify(Rz, T, groups) for T in kz)
    rows["control, absent pair bits set to 0"] = {"knots by kind": dict((",".join(k), v) for k, v in clz.items()),
                                                 "example": [Rz.names_of(T) for T in kz if G.classify(Rz, T, groups) == ("order", "state")][:2]}
    ok = (("order", "state") not in cls and ("existence", "order", "state") not in cls and guards_ok and cls[("existence", "state")] > 0
          and all(k == [("state",)] for k in per_sub.values()) and clz[("order", "state")] > 0)
    check("4 Theorem 1, substrates that vary (sites -2..1, seed at 0): with forgotten variables free no knot meets the order and the "
          "states; the history meets them only as 'site grown -> its bond holds' (presence literals); in every fixed substrate all knots "
          "are bonds; control: absent pair bits set to 0 carry existence and knot with the states", ok, rows)

    # 5 Theorem 2: the local history is pairwise; time without loops has the world's cycles as its knots
    ring_rows, thread_rows = [], []
    ok = True
    for n in range(3, 11):
        E = G.ring_edges(n)
        loc = G.orientation_rel(n, E, lambda p: max(p) <= 1)
        beg = G.orientation_rel(n, E, lambda p: min(p) == 0)
        both = G.orientation_rel(n, E, lambda p: max(p) <= 1 and min(p) == 0)
        acyc = G.acyclic_orientations(n, E)
        good = (G.is_2cnf(loc) and not G.knots(loc) and len(loc.rows) == 2 and beg.rows == G.nae(beg.names).rows
                and beg.rows == acyc.rows and G.is_knot_set(beg, beg.names) and knotlab_agrees(beg, beg.names) and not both.rows)
        ring_rows.append([n, len(loc.rows), len(beg.rows), good])
        ok &= good
        P = [(i, i + 1) for i in range(n - 1)]
        locP = G.orientation_rel(n, P, lambda p: max(p) <= 1)
        goodP = G.is_2cnf(locP) and len(locP.rows) == n and all(len(sources(n, P, r)) == 1 for r in locP.rows)
        thread_rows.append([n, len(locP.rows), goodP])
        ok &= goodP
    graphs = {
        "K4": (4, [(0, 1), (0, 2), (0, 3), (1, 2), (1, 3), (2, 3)]),
        "prism": (6, [(0, 1), (1, 2), (2, 0), (3, 4), (4, 5), (5, 3), (0, 3), (1, 4), (2, 5)]),
        "K3,3": (6, [(a, b) for a in range(3) for b in range(3, 6)]),
        "cube": (8, [(a, b) for a in range(8) for b in range(8) if a < b and bin(a ^ b).count("1") == 1]),
        "Petersen": (10, [(i, (i + 1) % 5) for i in range(5)] + [(5 + i, 5 + (i + 2) % 5) for i in range(5)] + [(i, i + 5) for i in range(5)]),
    }
    graph_rows = []
    for name, (nv, E) in graphs.items():
        A = G.acyclic_orientations(nv, E)
        cyc = G.cycles_of(nv, E)
        chl = [c for c in cyc if G.chordless(c[0], E)]
        conj = set()
        for r in range(1 << len(E)):
            if all(len({(r >> e & 1) ^ (E[e] in flips) for e in seq}) == 2 for seq, flips in chl):
                conj.add(r)
        shadows = all(A.shadow([A.names[e] for e in seq]).rows == G.nae([A.names[e] for e in seq], {A.names[E.index(f)] for f in flips}).rows
                      and G.is_knot_set(A, [A.names[e] for e in seq]) for seq, flips in cyc)
        enum = None
        if len(E) <= 12:
            ks = {frozenset(A.names_of(T)) for T in G.knots(A)}
            enum = ks == {frozenset(A.names[e] for e in seq) for seq, _ in cyc}
        # a cycle with one more edge (not a cycle) is not a knot
        seq0 = cyc[0][0]
        extra = next(A.names[i] for i in range(len(E)) if i not in seq0)
        controls = (not G.is_knot_set(A, [A.names[e] for e in seq0] + [extra]))
        good = conj == set(A.rows) and shadows and controls and (enum is None or enum)
        graph_rows.append([name, len(E), len(A.rows), len(cyc), len(chl), enum, good])
        ok &= good
    L3 = G.linear_orders_rel(3)
    L4 = G.linear_orders_rel(4)
    k4 = G.knots(L4)
    lin_ok = L3.rows == G.nae(L3.names, {"b02"}).rows and G.is_knot_set(L3, L3.names) and len(k4) == 7 \
        and sorted(bin(T).count("1") for T in k4) == [3, 3, 3, 3, 4, 4, 4]
    ok &= lin_ok
    wrong = G.nae(L3.names).rows != L3.rows
    ok &= wrong
    check("5 Theorem 2: 'at most one parent' is 2-CNF with no knot; on a ring it allows only the two cyclic orientations, the "
          "beginning is NAE over every seam (a knot, knotlab agrees) and the two contradict; on a thread it gives exactly one beginning; "
          "the knots of 'time has no loop' are exactly the world's cycles (enumerated) and every cycle's shadow is NAE; three events' "
          "order is NAE_3, four events' has the 7 cycles of K4 as knots; controls: a cycle plus an edge, NAE with the wrong flip", ok,
          {"rings [n, local, beginning, ok]": ring_rows, "threads [n, local, ok]": thread_rows,
           "graphs [name, edges, acyclic orientations, cycles, chordless, knots == cycles, ok]": graph_rows,
           "linear orders": lin_ok, "control (wrong flip differs)": wrong})

    # 6 Theorem 3: Euler's count, in one and two dimensions
    rng = random.Random(20261107)
    one = {}
    ok = True
    for rule in ("open-end", "sprout", "close"):
        fails = threads = closes = broken = 0
        for _ in range(200):
            K, S, log, _ = G.grow_1d(rule, rng.randint(1, 40), rng)
            c = sum(1 for s in log if s[0] == "close")
            closes += c
            fails += (len(K) - len(S) != G.chi_steps_1d(log)) or G.cyclomatic(K, S) != c
            broken += (len(K) - len(S) != G.chi_steps_1d([("sprout",) if s[0] == "close" else s for s in log]))
            deg = collections.Counter(x for e in S for x in e)
            threads += all(deg[k] <= 2 for k in K) and G.cyclomatic(K, S) == 0
        one[rule] = {"runs": 200, "identity failures": fails, "closing moves": closes, "threads": threads,
                     "control: closes counted as sprouts, failures": broken}
        ok &= fails == 0
    ok &= one["open-end"]["threads"] == 200 and one["close"]["control: closes counted as sprouts, failures"] > 0
    sys.path.insert(0, str(GC))
    import growth_lib as GL  # noqa: E402
    two = []
    for m in range(1, 6):
        order, _ = GL.ring_order(m)
        _, log = GL.greedy_grow(order)
        tris = [order[0]] + [t for *_, t in log]
        kinds, tot = G.chi_steps_2d(tris)
        stuck = sum(G.disc_growth(tris, rng)[1] > 0 for _ in range(30))
        good = tot == 2 == G.euler_char(tris) and kinds["first"] == 1 and kinds["end"] == 1 and kinds["pinch"] == 0 and stuck == 0
        two.append(["K_%d" % m, len(tris), dict(kinds), tot, stuck, good])
        ok &= good
    for p, q in ((3, 3), (4, 4), (6, 6), (4, 6), (8, 8)):
        tris = G.flat_torus(p, q)
        adj = collections.defaultdict(list)
        for i, t in enumerate(tris):
            for e in itertools.combinations(t, 2):
                adj[frozenset(e)].append(i)
        seen, order, queue = {0}, [0], [0]
        while queue:
            i = queue.pop(0)
            for e in itertools.combinations(tris[i], 2):
                for j in adj[frozenset(e)]:
                    if j not in seen:
                        seen.add(j)
                        order.append(j)
                        queue.append(j)
        kinds, tot = G.chi_steps_2d([tris[i] for i in order])
        left = [G.disc_growth(tris, rng)[1] for _ in range(30)]
        good = tot == 0 == G.euler_char(tris) and kinds["pinch"] >= 2 and min(left) > 0
        two.append(["torus %dx%d" % (p, q), len(tris), dict(kinds), tot, [min(left), max(left)], good])
        ok &= good
    tris = G.flat_torus(4, 4)
    kinds, tot = G.chi_steps_2d(tris)
    mis = tot + kinds["pinch"]              # the control: count pinches as adds (change 0 instead of -1)
    ok &= kinds["pinch"] > 0 and mis != G.euler_char(tris)
    check("6 Theorem 3, Euler's count: one dimension (200 runs per rule): knots minus seams = 1 - closing moves, the open-end rule "
          "grows only threads; two dimensions: K_m (m <= 5) grows with one beginning, one end and no closing move (chi 2), and random "
          "disc growth never sticks (30 runs each); flat tori need closing moves (chi 0) and disc growth always sticks; controls fail",
          ok, {"one dimension": one, "two dimensions [surface, triangles, step kinds, total, disc growth stuck or left, ok]": two,
               "control (pinches counted as adds)": mis})

    # 7 Theorem 4: pumping
    pump = {}
    ok = True
    for k, nlaws in ((2, 3000), (3, 600)):
        N = G.pump_bound(1, k)
        st = collections.Counter()
        broken = 0
        for _ in range(nlaws):
            law = G.random_symmetric_law(k, rng, rng.uniform(0.25, 0.85))
            T = G.thread_lengths(law, k, N + 6)
            Rg = G.ring_lengths(law, k, N + 6)
            if T:
                st["laws with a thread"] += 1
            if T and not Rg:
                st["threads but no ring"] += 1
                st["longest thread with no ring"] = max(st["longest thread with no ring"], max(T))
            long_ = [n for n in T if n >= N]
            if long_:
                st["laws with a thread at the bound or longer"] += 1
                lab = G.labelled_thread(law, k, max(long_))
                ring = G.pump(lab, 1)
                if ring is not None and G.windows_ok(law, ring, ring=True) and len(ring) in Rg:
                    st["pumped ring valid"] += 1
                # control: glue the thread between two positions whose windows differ
                q = 3
                p = q + 3
                while p + 1 <= len(lab) - 1 and tuple(lab[q - 2: q + 1]) == tuple(lab[p - 2: p + 1]):
                    p += 1
                if p + 1 <= len(lab) - 1:
                    st["misglued rings tried"] += 1
                    broken += not G.windows_ok(law, lab[q - 1: p - 1], ring=True)
        pump["k=%d (bound %d, %d laws)" % (k, N, nlaws)] = dict(st)
        pump["k=%d control: misglued rings rejected" % k] = broken
        ok &= st["pumped ring valid"] == st["laws with a thread at the bound or longer"] > 0 and st["longest thread with no ring"] < N
        ok &= broken > 0
    counter = []
    for K in range(2, 13):
        law = G.counter_law(K)
        T = G.thread_lengths(law, K, 4 * K + 4)
        Rg = G.ring_lengths(law, K, 4 * K + 4)
        counter.append([K, max(T) if T else 0, len(Rg)])
        ok &= not Rg and (K < 3 or max(T) == 2 * K - 1)
    check("7 Theorem 4, pumping (radius 1): every random law with k = 2 or 3 labels that allows a thread at Theorem 4's bound or longer allows "
          "the ring built by the proof (windows checked); the counter control (labels 0..K-1, distance from a seed) allows threads up "
          "to 2K - 1 and no ring, so excluding rings costs labels that grow with the length", ok,
          {"random laws": pump, "counter [K, longest thread, rings]": counter})

    # 8 Proposition 5: the seam law allows every flat torus
    rows = []
    ok = True
    for p, q in ((3, 3), (3, 6), (4, 4), (6, 6), (5, 7), (8, 8)):
        tris = G.flat_torus(p, q)
        deg = collections.Counter(v for t in tris for v in t)
        # the faces two-colour: the triangle (a, b, d) of a cell is 'up', (a, d, c) 'down'; neighbours across an edge differ
        colour = {t: k % 2 for k, t in enumerate(tris)}
        edge_tris = collections.defaultdict(list)
        for t in tris:
            for e in itertools.combinations(t, 2):
                edge_tris[frozenset(e)].append(t)
        two_col = all(len(ts) == 2 and colour[ts[0]] != colour[ts[1]] for ts in edge_tris.values())
        digons = sum(1 for d in deg.values() if d == 4)
        good = set(deg.values()) == {6} and two_col and digons == 0 and G.euler_char(tris) == 0
        rows.append([p, q, len(tris), sorted(set(deg.values())), two_col, good])
        ok &= good
    check("8 Proposition 5: every flat torus (triangular lattice, p x q) is a two-kind surface whose co-lines all have three points, "
          "faces two-coloured, no digon; so the seam law's S1 is empty and the unmarked marking meets S2: the seam law allows every "
          "flat torus, and only growth's beginning (Theorem 3) or an aperiodic law excludes them", ok,
          {"[p, q, triangles, co-line degrees, two-coloured, ok]": rows})

    res = {"status": "passed", "checks": OUT, "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(res, indent=1, default=str) + "\n")
        print("wrote result.json")
    else:
        old = json.loads((HERE / "result.json").read_text())
        same = {k: v["info"] for k, v in old["checks"].items()} == json.loads(json.dumps({k: v["info"] for k, v in OUT.items()}, default=str))
        print("result.json reproduced" if same else "result.json DIFFERS")
        sys.exit(0 if same else 1)
