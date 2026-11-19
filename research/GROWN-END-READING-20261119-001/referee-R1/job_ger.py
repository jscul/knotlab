"""Shared-runner job for the referee's check of GROWN-END-READING-20261119-001 (Codex), with the referee's own code: its EXPLOSIVE-R1
grower (the program's rule), THREE-WAY-R1's bonds and readings (UNIQUE-TABLE-R1's minimal words), CREATED-PAIR-R1's isometry
search, GROW-SMALL-R1's tables and GROWN-END-MEET-ONCE-R1's census.  Codex's stages are read from its artifacts as data; none of
its code is run.

The marking is the study's: every distinction of every live junction fixed individually.  "Extends" means: some isometry of the
next pair table agrees with the map on every old distinction (the fresh names free).

Parts:
- BIG: the reached stage of 239 junctions built from the proof's text: counts; admissible start (connected, meet-once, places >= 3,
  every support a bond); growth by the referee's engine, three rounds; the index exchange (2 3) on names: fixes the growing end,
  the pair-flip relation, an automorphism of the graph with the two hubs identified and not of the split one; the image of h0's
  equation outside the stage's equation span, with an allowed four-or-fewer distinction certificate found by the referee's own
  solver; 105 distinction-disjoint h0-h1 routes (maximum flow); for every one of the 15,225 sets of one to three names on six
  indices of the identified core (with the deleted distinction e among them), a bond of size below 105 found by the referee's own
  search and verified (both shores connected, every mark crossing); the study's literal start compared with the referee's
  (isomorphic as junction graphs with loose counts) and its literal certificate checked on it.
- NAMED: the four named stages (three minimum meet-once arrangements; the repeated-meeting six-junction start): every pair-table
  isometry fixing the growing end pointwise, and for each whether it extends, keeps the flip relation, keeps the triple readings
  (least bond holding three, or none), keeps triple existence, carries the equations.
- FORM: random two-attachment decompositions (H and Q meeting in two junctions A, B, the exterior in Q), all bonds by enumeration:
  K(X u Y) = L_H(X) + L_Q(Y) for mixed marks, K(X) = min(B_H(X), L_H(X) + lambda) for marks in H, and lambda' <= lambda after a
  complete round grown in Q.
- EXW: the study's smallest stage where triple existence keeps an equation-changing map (eight junctions, 15 distinctions, one
  round from a six-junction start): regrown from the start; the five tests; the swap 5 6 on its entries; and its pair tables at the
  next three stages with every fresh name fixed.
- CEN-w: the referee's census of admissible meet-once starts of width w (GROWN-END-MEET-ONCE-R1's), stages of at most 11
  junctions: per stage every pair-table isometry fixing the end pointwise (at most 20,000), the same five tests; the claims are
  that every triple-keeping map carries the equations and extends.

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-END-READING-20261119-001/referee-R1/job_ger.py \\
      --out runs/referee-ger --unit referee-ger --workers 3 --case-timeout 14400 --case-mem 4G --mem-max 13G
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/GROWN-END-MEET-ONCE-20261119-001/referee-R1", "research/HUNT-SHORTEN-20261119-001/referee-R1",
          "research/GROWN-END-SWAP-20261119-001/referee-R1", "research/EXTEND-ROUND-20261119-001/referee-R1",
          "research/CREATED-PAIR-20261119-001/referee-R1", "research/GROW-SMALL-20261119-001/referee-R1",
          "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/GROWN-PAIR-20261119-001/referee-R1",
          "research/MEET-ONCE-20261119-001/referee-R1", "research/PARENT-RULE-20261119-001/referee-R1",
          "research/RING-IDENT-20261119-001/referee-R1", "research/THREE-WAY-20261119-001/referee-R1",
          "research/UNIQUE-TABLE-20261119-001/referee-R1", "research/EXPLOSIVE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ART = ROOT / "artifacts/GROWN-END-READING-20261119-001/GROWN-END-READING-20261119-001-E001_readings"
MEET = ROOT / "artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds"
SWAP = ROOT / "artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json"
PARAMS = {}
CAPJ = 11
CAPMAPS = 20000


def setup(params):
    PARAMS.update(params)


def rank(rows):
    basis = {}
    r = 0
    for x in rows:
        while x:
            p = x.bit_length() - 1
            if p not in basis:
                basis[p] = x
                r += 1
                break
            x ^= basis[p]
    return r


def owners(stars):
    own = defaultdict(list)
    for j, s in enumerate(stars):
        for x in s:
            own[x].append(j)
    return own


# ---- the reached stage of 239 junctions ----

N = 21
PAIRS = list(itertools.combinations(range(N), 2))
PID = {p: k for k, p in enumerate(PAIRS)}
H0, H1, UJ, VJ = N + len(PAIRS), N + len(PAIRS) + 1, N + len(PAIRS) + 2, N + len(PAIRS) + 3


def offset(p):
    t = (p[1] - p[0]) % N
    return min(t, N - t)


def core_names():
    """Names of the closed core: ('uw', i, pair) joins u_i and w_pair; ('y', pair) joins w_pair and its hub."""
    out = {}
    for p in PAIRS:
        w = N + PID[p]
        out[("uw", p[0], p)] = (p[0], w)
        out[("uw", p[1], p)] = (p[1], w)
        out[("y", p)] = (w, H0 if offset(p) <= 5 else H1)
    return out


E_NAME = ("uw", 0, (0, 1))


def big_start():
    names = core_names()
    s, t = names.pop(E_NAME)
    names[("sU",)] = (s, UJ)
    names[("tV",)] = (t, VJ)
    loose = {("lU", 0): UJ, ("lU", 1): UJ, ("lV", 0): VJ, ("lV", 1): VJ}
    labels = sorted(names, key=repr) + sorted(loose, key=repr)
    idx = {x: i for i, x in enumerate(labels)}
    stars = [[] for _ in range(VJ + 1)]
    for x, (a, b) in names.items():
        stars[a].append(idx[x])
        stars[b].append(idx[x])
    for x, a in loose.items():
        stars[a].append(idx[x])
    return [sorted(q) for q in stars], labels, idx


def sigma_name(x):
    tau = {2: 3, 3: 2}
    f = lambda i: tau.get(i, i)  # noqa: E731
    if x[0] == "uw":
        p = tuple(sorted((f(x[2][0]), f(x[2][1]))))
        return ("uw", f(x[1]), p)
    if x[0] == "y":
        return ("y", tuple(sorted((f(x[1][0]), f(x[1][1])))))
    return x


def wired(stars):
    """The junction graph with the exterior 'o' holding every loose distinction, as networkx MultiGraph keyed by distinction."""
    import networkx as nx
    G = nx.MultiGraph()
    G.add_nodes_from(range(len(stars)))
    for x, js in owners(stars).items():
        if len(js) == 2:
            G.add_edge(js[0], js[1], key=x)
        else:
            G.add_edge(js[0], "o", key=x)
    return G


def admissible(stars):
    import networkx as nx
    G = wired(stars)
    meet = Counter()
    for x, js in owners(stars).items():
        if len(js) == 2:
            meet[tuple(sorted(js))] += 1
    out = {"connected": nx.is_connected(G), "meets once": max(meet.values()) == 1, "places >= 3": min(len(s) for s in stars) >= 3}
    ok = True
    for v in range(len(stars)):
        Y = nx.Graph(G)
        Y.remove_node(v)
        if not nx.is_connected(Y):
            ok = False
            break
    out["every support a bond"] = ok
    return out


def small_bond_search():
    """For every set of one to three core names on indices 0..5, a bond of the identified core (closed; h0 = h1 = h) holding it,
    of size below 105: shores avoid h; each marked u-w name chooses its endpoint in the shore; the forced vertices are joined by
    a Steiner tree inside indices 0..6 avoiding the forced-out vertices; verified in the full identified core."""
    import networkx as nx
    from networkx.algorithms.approximation import steiner_tree
    names = core_names()
    H = "h"
    G = nx.MultiGraph()
    for x, (a, b) in names.items():
        a = H if a in (H0, H1) else a
        b = H if b in (H0, H1) else b
        G.add_edge(a, b, key=x)
    allowed = {i for i in range(7)} | {N + PID[p] for p in PAIRS if p[1] < 7}
    sub = nx.Graph(G.subgraph(allowed))
    six = [x for x in names if (x[0] == "uw" and x[2][1] < 6) or (x[0] == "y" and x[1][1] < 6)]
    simple = nx.Graph(G)
    worst = Counter()
    fails = []
    sizes = defaultdict(int)

    def endpoints(x):
        a, b = names[x]
        return (H if a in (H0, H1) else a, H if b in (H0, H1) else b)

    for k in (1, 2, 3):
        for X in itertools.combinations(sorted(six, key=repr), k):
            best = None
            opts = [((0, 1) if x[0] == "uw" else (0,)) for x in X]
            for ch in itertools.product(*opts):
                In, Out = set(), {H}
                for x, c in zip(X, ch):
                    a, b = endpoints(x)
                    if x[0] == "y":
                        In.add(a)
                    else:
                        u, w = (a, b) if isinstance(a, int) and a < N else (b, a)
                        In.add(u if c == 0 else w)
                        Out.add(w if c == 0 else u)
                if In & Out:
                    continue
                Ssub = sub.subgraph(set(sub) - Out)
                if len(In) == 1:
                    S = set(In)
                else:
                    comps = [c for c in nx.connected_components(Ssub) if In <= c]
                    if not comps:
                        continue
                    S = set(steiner_tree(Ssub.subgraph(comps[0]), list(In)).nodes())
                    S |= In
                rest = set(simple) - S
                if not nx.is_connected(simple.subgraph(rest)) or not nx.is_connected(simple.subgraph(S)):
                    continue
                cut = {key for v in S for _, b, key in G.edges(v, keys=True) if b not in S}
                if not set(X) <= cut:
                    continue
                if best is None or len(cut) < best:
                    best = len(cut)
            if best is None or best >= 105:
                fails.append([repr(x) for x in X])
            else:
                worst[k] = max(worst[k], best)
                sizes[k] += 1
    return {"mark sets with a bond below 105 (by number of marks)": dict(sizes), "largest exhibited bond (by number of marks)":
            dict(worst), "mark sets without one found": len(fails), "examples without one": fails[:5]}


def part_big():
    import networkx as nx
    import job_expl as JX
    out = {}
    stars, labels, idx = big_start()
    out["start junctions, distinctions"] = [len(stars), len(labels)]
    out["start admissible"] = admissible(stars)
    G = JX.grower([list(s) for s in stars])
    stages = [[list(s) for s in G.bits]]
    for _ in range(3):
        r = G.step(JX.floored, None, None)
        stages.append([sorted(s) for s in G.bits])
        if r != "ok":
            break
    out["stages (junctions, distinctions)"] = [[len(st), len({x for s in st for x in s})] for st in stages]
    out["round 1: new junctions (parents, fresh)"] = [[len(G.parents[j]), G.fresh[j]] for j in range(len(stars), len(stages[1]))]
    nb0 = len(labels)
    # sigma on indices of the stage (fresh names fixed)
    sig = {i: idx[sigma_name(x)] for i, x in enumerate(labels)}
    for k, st in enumerate(stages[1:], 1):
        allx = sorted({x for s in st for x in s})
        f = {x: sig.get(x, x) for x in allx}
        own = owners(st)
        live = [j for j, s in enumerate(st) if any(len(own[x]) == 1 for x in s)]
        rows = [sum(1 << x for x in s) for s in st]
        r0 = rank(rows)
        img = sum(1 << f[x] for x in st[H0])
        twinp = {(x, y) for x, y in itertools.combinations(allx, 2) if len(own[x]) == 1 and own[x] == own[y]}
        row = {"fixes every distinction of every live junction": all(f[x] == x for j in live for x in st[j]),
               "keeps the flip relation (pairs with the same holders)": {tuple(sorted((f[x], f[y]))) for x, y in twinp} == twinp,
               "image of h0's equation outside the span": rank(rows + [img]) > r0,
               "junction equations whose image is outside the span": sum(
                   rank(rows + [sum(1 << f[x] for x in s)]) > r0 for s in st)}
        holders = Counter(tuple(sorted(own[x])) for x in allx)
        twins = [h for h, c in holders.items() if c > 1]
        row["holder sets held by two or more distinctions (all one live junction's loose twins?)"] = [
            len(twins), all(len(h) == 1 and h[0] in live for h in twins)]
        if k == 1:
            # a certificate: d with every star even and the image odd (GF(2) solve), then a short one by random restarts
            nbx = len(allx)
            cert = solve_even(st, img, nbx)
            row["certificate found (size)"] = None if cert is None else bin(cert).count("1")
            if cert is not None:
                row["certificate: every star even, image odd"] = all(bin(cert & r).count("1") % 2 == 0 for r in rows) and \
                    bin(cert & img).count("1") % 2 == 1
            # a four-distinction certificate from the structure: two spokes at h0 and h1 and their two u-w names
            row["the referee's structural certificate"] = four_cert(st, labels, idx, f, rows, img)
        out[f"stage {k}"] = row
    # 105 disjoint h0-h1 routes, in the stage and in the bare split core
    W = nx.Graph()
    for x, js in owners(stages[1]).items():
        a, b = (js[0], js[1]) if len(js) == 2 else (js[0], "o")
        if W.has_edge(a, b):
            W[a][b]["capacity"] += 1
        else:
            W.add_edge(a, b, capacity=1)
    out["h0-h1 distinction-disjoint routes in the stage (max flow)"] = nx.maximum_flow_value(W, H0, H1)
    C = nx.Graph()
    for x, (a, b) in core_names().items():
        C.add_edge(a, b, capacity=1)
    out["h0-h1 routes in the bare split core"] = nx.maximum_flow_value(C, H0, H1)
    # sigma an automorphism of the identified core, not of the split one
    names = core_names()
    ident = lambda v: "h" if v in (H0, H1) else v  # noqa: E731

    def vmap(v):
        if v == "h" or v in (H0, H1):
            return v
        if v < N:
            return {2: 3, 3: 2}.get(v, v)
        p = PAIRS[v - N]
        return N + PID[tuple(sorted(({2: 3, 3: 2}.get(p[0], p[0]), {2: 3, 3: 2}.get(p[1], p[1]))))]
    out["sigma an automorphism of the identified core"] = all(
        {ident(vmap(a)), ident(vmap(b))} == {ident(c) for c in names[sigma_name(x)]} for x, (a, b) in names.items())
    out["sigma an automorphism of the split core"] = all(
        {vmap(a), vmap(b)} == set(names[sigma_name(x)]) for x, (a, b) in names.items())
    out["sigma fixes e"] = sigma_name(E_NAME) == E_NAME
    out["small bonds"] = small_bond_search()
    out["the study's literal start"] = literal_compare(stars)
    return out


def solve_even(stars, img, nb):
    """A vector d over the distinctions with every star even and img odd, or None (Gaussian elimination)."""
    rows = [sum(1 << x for x in s) for s in stars] + [img]
    rhs = [0] * len(stars) + [1]
    piv = {}
    order = []
    for r, b in zip(rows, rhs):
        for p in order:
            if r >> p & 1:
                r ^= piv[p][0]
                b ^= piv[p][1]
        if r == 0:
            if b:
                return None
            continue
        p = r.bit_length() - 1
        for q in order:
            if piv[q][0] >> p & 1:
                piv[q] = (piv[q][0] ^ r, piv[q][1] ^ b)
        piv[p] = (r, b)
        order.append(p)
    d = 0
    for p in order:
        if piv[p][1]:
            d |= 1 << p
    return d


def four_cert(st, labels, idx, f, rows, img):
    """Allowed differences on the four-distinction routes u_i - w_p - hub - w_q - u_i (p, q at the same hub): every star even;
    count those meeting the image of h0's equation oddly, and give one."""
    found, first = 0, None
    for i in range(N):
        ps = [p for p in PAIRS if i in p and p != (0, 1)]
        for p, q in itertools.combinations(ps, 2):
            if (offset(p) <= 5) != (offset(q) <= 5):
                continue
            c = [idx[("uw", i, p)], idx[("uw", i, q)], idx[("y", p)], idx[("y", q)]]
            d = sum(1 << x for x in c)
            if all(bin(d & r).count("1") % 2 == 0 for r in rows) and bin(d & img).count("1") % 2 == 1:
                found += 1
                if first is None:
                    first = [repr(labels[x]) for x in c]
    return {"four-distinction routes meeting the image oddly (every star even)": found, "one": first}


def literal_compare(mine):
    import networkx as nx
    from networkx.algorithms import isomorphism as iso
    d = json.load(open(ART / "graft_check.json"))["dense"]
    theirs = [sorted(s) for s in d["start"]]
    out = {"their start junctions, distinctions": [len(theirs), len({x for s in theirs for x in s})],
           "their start admissible": admissible(theirs)}

    def g(stars):
        own = owners(stars)
        G = nx.Graph()
        for j, s in enumerate(stars):
            G.add_node(j, l=sum(1 for x in s if len(own[x]) == 1), n=len(s))
        for x, js in own.items():
            if len(js) == 2:
                G.add_edge(*js)
        return G
    A, B = g(mine), g(theirs)
    out["degree and loose multisets agree"] = sorted((A.nodes[v]["n"], A.nodes[v]["l"]) for v in A) == sorted(
        (B.nodes[v]["n"], B.nodes[v]["l"]) for v in B)
    out["WL hashes agree"] = nx.weisfeiler_lehman_graph_hash(A, node_attr=None, iterations=5) == \
        nx.weisfeiler_lehman_graph_hash(B, node_attr=None, iterations=5)
    GM = iso.GraphMatcher(A, B, node_match=iso.categorical_node_match(["n", "l"], [0, 0]))
    import signal

    def alarm(*_):
        raise TimeoutError
    signal.signal(signal.SIGALRM, alarm)
    signal.alarm(900)
    try:
        out["isomorphic as junction graphs with places and loose counts"] = GM.is_isomorphic()
    except TimeoutError:
        out["isomorphic as junction graphs with places and loose counts"] = "undecided in 900 s"
    signal.alarm(0)
    cert = d["literal_allowed_state_rejecting_image_equation"]
    mc = d["marked_checks"][0]
    imgset = set(mc["image_not_in_equation_span"])
    cw = set(cert)
    out["their certificate meets every start support evenly"] = all(len(cw & set(s)) % 2 == 0 for s in theirs)
    out["their certificate meets their image equation oddly"] = len(cw & imgset) % 2 == 1
    out["their image equation has h0's size"] = len(imgset) == len(mine[H0])
    return out


# ---- named stages and census: the five tests ----

def five_tests(stage, nxt, cap=CAPMAPS):
    import numpy as np
    import job_created as JC
    import job_growsmall as GS
    import referee_three as R3
    olds = sorted({x for q in stage for x in q})
    fresh = sorted({x for q in nxt for x in q} - set(olds))
    ix = {x: i for i, x in enumerate(olds + fresh)}
    S = [sorted(ix[x] for x in q) for q in stage]
    Nn = [sorted(ix[x] for x in q) for q in nxt]
    nb = len(olds)
    _, K, T = R3.readings(S, nb)
    K = np.array(K)
    own = owners(S)
    live = [j for j, s in enumerate(S) if any(len(own[x]) == 1 for x in s)]
    fixed = sorted({x for j in live for x in S[j]})
    ex = [[(x + 1) if x in fixed else 0 for x in range(nb)]] * 2
    rows = [sum(1 << x for x in s) for s in S]
    rk = rank(rows)
    hold = {x: tuple(sorted(own[x])) for x in range(nb)}
    s = Counter()
    bad = []
    K2 = None
    maps = 0
    for phi in JC.isometries(K, K, extra=ex, cap=cap):
        maps += 1
        if maps > cap:
            s["capped"] = 1
            break
        f = list(phi)
        carries = rank(rows + [sum(1 << f[x] for x in q) for q in S]) == rk
        flip = all((hold[x] == hold[y]) == (hold[f[x]] == hold[f[y]]) for x, y in itertools.combinations(range(nb), 2)
                   if hold[x] == hold[y] or hold[f[x]] == hold[f[y]])
        tri = all(T[tuple(sorted((f[a], f[b], f[c])))] == v for (a, b, c), v in T.items())
        exist = all((T[tuple(sorted((f[a], f[b], f[c])))] is None) == (v is None) for (a, b, c), v in T.items())
        if carries:
            ext = True   # the equation-transport theorem (EXTEND-ROUND, refereed)
        else:
            if K2 is None:
                K2v, _, _, _ = GS.full_table([sorted(q) for q in Nn])
                K2 = np.array(K2v)
            n2 = len(K2)
            ex2 = [[(x + 1) if x < nb else 0 for x in range(n2)], [0] * n2]
            for x in range(nb):
                ex2[1][f[x]] = x + 1
            ext = next(iter(JC.isometries(K2, K2, extra=ex2, cap=1)), None) is not None
        s["pair-table maps"] += 1
        s["extend"] += ext
        s["carry the equations"] += carries
        for name, keep in (("flip", flip), ("triples", tri), ("triple existence", exist), ("triples and flip", tri and flip)):
            if keep:
                s[f"keep {name}"] += 1
                s[f"keep {name}: extend"] += ext
                s[f"keep {name}: carry the equations"] += carries
        if tri and (not carries or not ext):
            bad.append({"map": f, "carries": carries, "extends": ext})
    return dict(s), bad, {"junctions": len(S), "distinctions": nb}


def part_named():
    out = {}
    t = json.load(open(MEET / "reach_bound_threshold.json"))
    items = [(f"minimum meet-once arrangement {i + 1}", w["current"], w["next"], len(w["start"]))
             for i, w in enumerate(t["joint_minimum_audit"]["failing_allocations"])]
    d = json.load(open(SWAP))["a"]
    items.append(("repeated-meeting six-junction start", d["current"], d["next"], len(d["start"])))
    for name, cur, nxt, ns in items:
        c, bad, size = five_tests([sorted(q) for q in cur], [sorted(q) for q in nxt], cap=10 ** 6)
        out[name] = {"starting junctions": ns, "size": size, "counts": c, "triple-keeping maps that fail": bad[:3]}
    return out


def part_cen(W):
    import job_meet1 as JM
    glist = JM.graphs(W)
    starts = JM.admissible_starts(W, glist)
    s = Counter()
    s["admissible starts"] = len(starts)
    bad, exist_bad = [], []
    for st in starts:
        for age, stage, nxt, new in JM.history(st, maxj=CAPJ):
            if age < 1 or not JM.live_of(stage):
                continue
            s["open stages"] += 1
            c, b, size = five_tests(stage, nxt)
            for k, v in c.items():
                s[k] += v
            s["stages where every pair-table map extends"] += c.get("extend", 0) == c.get("pair-table maps", 0)
            s["stages where every triple-keeping map extends"] += c.get("keep triples: extend", 0) == c.get("keep triples", 0)
            if c.get("keep triple existence", 0) != c.get("keep triple existence: carry the equations", 0):
                s["stages where triple existence keeps an equation-changing map"] += 1
                exist_bad.append({"start": st, "age": age, "size": size})
                exist_bad = sorted(exist_bad, key=lambda x: (x["size"]["junctions"], x["size"]["distinctions"]))[:5]
            if b:
                bad.append({"start": st, "age": age, "size": size, "maps": b[:2]})
    return {"counts": dict(s), "triple-keeping maps that fail to carry or extend": bad[:10],
            "smallest stages where existence keeps an equation-changing map": exist_bad}


# ---- the two-attachment formulas ----

def part_form(seed, trials):
    """Random wired graphs split at two junctions A, B into H (no exterior) and Q (the exterior o inside), every bond enumerated."""
    import networkx as nx
    rng = random.Random(seed)
    s = Counter()
    bad = []
    for _ in range(trials):
        nh, nq = rng.randint(3, 6), rng.randint(2, 5)
        A, B = 0, 1
        Hv = [A, B] + list(range(2, nh))
        Qv = [A, B] + list(range(nh, nh + nq)) + ["o"]
        edges = []   # (name, a, b, piece)

        def rand_conn(vs, piece, extra):
            order = vs[:]
            rng.shuffle(order)
            for i in range(1, len(order)):
                edges.append((len(edges), order[i], rng.choice(order[:i]), piece))
            for _ in range(extra):
                a, b = rng.sample(vs, 2)
                edges.append((len(edges), a, b, piece))
        rand_conn(Hv, "H", rng.randint(1, 5))
        rand_conn(Qv, "Q", rng.randint(1, 4))
        V = sorted(set(Hv) | set(Qv), key=str)
        G = nx.MultiGraph()
        G.add_nodes_from(V)
        for x, a, b, _ in edges:
            G.add_edge(a, b, key=x)
        if not nx.is_connected(G):
            continue

        def cuts(vs, piece, need_sep=None, ident=None):
            """All (shore, word) with both shores connected inside the piece's subgraph."""
            sub = nx.MultiGraph()
            sub.add_nodes_from(vs)
            for x, a, b, p in edges:
                if piece is None or p == piece:
                    sub.add_edge(a, b, key=x)
            res = []
            vs = list(vs)
            for r in range(1, len(vs)):
                for S in itertools.combinations(vs, r):
                    S = set(S)
                    if need_sep is not None and not ((A in S) != (B in S)):
                        continue
                    if ident is not None and ((A in S) != (B in S)):
                        continue
                    R = set(vs) - S
                    if not nx.is_connected(sub.subgraph(S)) or not nx.is_connected(sub.subgraph(R)):
                        continue
                    res.append((S, frozenset(k for a, b, k in sub.edges(keys=True) if (a in S) != (b in S))))
            return res
        allb = cuts(V, None)
        Hc = cuts(Hv, "H", need_sep=True)
        Qc = cuts(Qv, "Q", need_sep=True)
        Bt = [w for S, w in allb if (A in S) == (B in S)]
        lam = min((len(w) for _, w in Qc), default=None)
        if lam is None or not Hc:
            continue
        Hx = [x for x, _, _, p in edges if p == "H"]
        Qx = [x for x, _, _, p in edges if p == "Q"]
        INF = 10 ** 6

        def K(X):
            return min((len(w) for _, w in allb if X <= w), default=INF)

        def L(cs, X):
            return min((len(w) for _, w in cs if X <= w), default=INF)

        def Bh(X):
            return min((len(w) for w in Bt if X <= w), default=INF)
        s["graphs"] += 1
        for k in (1, 2):
            for X in itertools.combinations(Hx, k):
                X = frozenset(X)
                lhs = K(X)
                rhs = min(Bh(X), L(Hc, X) + lam, INF)
                s["H marks checked"] += 1
                s["H marks: K = min(B_H, L_H + lambda)"] += lhs == rhs
                if lhs != rhs and len(bad) < 5:
                    bad.append(["H", sorted(X), lhs, rhs])
                for y in Qx:
                    Y = frozenset([y])
                    s["mixed checked"] += 1
                    v1, v2 = K(X | Y), L(Hc, X) + L(Qc, Y)
                    v2 = INF if v2 >= INF else v2
                    s["mixed: K = L_H + L_Q"] += v1 == v2
                    if v1 != v2 and len(bad) < 5:
                        bad.append(["mixed", sorted(X | Y), v1, v2])
    return {"counts": dict(s), "disagreements": bad}


def part_growth_lambda(seed, trials):
    """lambda' <= lambda after complete rounds grown in Q: random starts with a closed core H attached at s, t to a branch Q with
    live junctions; the referee's engine grows two rounds; the minimum s-t cut inside Q (wired, exterior in Q) never rises."""
    import networkx as nx
    import job_expl as JX
    rng = random.Random(seed)
    s = Counter()
    for _ in range(trials):
        # core: a random 2-connected-ish graph on 5-7 junctions, every junction three places or more, all shared; Q: s-U, t-V
        n = rng.randint(4, 7)
        e = [(i, (i + 1) % n) for i in range(n)]
        for _ in range(rng.randint(2, 7)):
            a, b = rng.sample(range(n), 2)
            if (a, b) not in e and (b, a) not in e:
                e.append((a, b))
        deg = Counter(x for ab in e for x in ab)
        if min(deg.values()) < 2:
            continue
        sT, tT = e[0]
        e = e[1:]
        U, V = n, n + 1
        e += [(sT, U), (tT, V)]
        stars = [[] for _ in range(n + 2)]
        for k, (a, b) in enumerate(e):
            stars[a].append(k)
            stars[b].append(k)
        nxt = len(e)
        for j in (U, V):
            for _ in range(rng.randint(2, 3)):
                stars[j].append(nxt)
                nxt += 1
        for j in range(n):
            while len(stars[j]) < 3:
                stars[j].append(nxt)   # a loose distinction would make the core live; skip such starts
                nxt += 1
        if any(len(stars[j]) != sum(1 for a, b in e if j in (a, b)) for j in range(n)):
            continue
        G = JX.grower([list(q) for q in stars])
        lams = []
        for r in range(3):
            own = owners(G.bits)
            Wg = nx.Graph()
            for x, js in own.items():
                a, b = (js[0], js[1]) if len(js) == 2 else (js[0], "o")
                if a < n and b != "o" and b < n:
                    continue   # core distinctions are not in Q
                if Wg.has_edge(a, b):
                    Wg[a][b]["capacity"] += 1
                else:
                    Wg.add_edge(a, b, capacity=1)
            lams.append(nx.maximum_flow_value(Wg, sT, tT) if sT in Wg and tT in Wg else 0)
            if G.step(JX.floored, None, None) != "ok":
                break
        s["growths"] += 1
        s["lambda never rises"] += all(b <= a for a, b in zip(lams, lams[1:]))
        s["lambda stays 1"] += all(x == 1 for x in lams)
    return dict(s)


EXW_START = [[0, 1, 2], [0, 3, 4], [5, 6, 9], [7, 8, 10], [1, 3, 5, 7, 11], [2, 4, 6, 8, 12]]
EXW_STAGE = [[0, 1, 2], [0, 3, 4], [5, 6, 9], [7, 8, 10], [1, 3, 5, 7, 11], [2, 4, 6, 8, 12], [9, 10, 13], [11, 12, 14]]


def part_exw():
    import job_meet1 as JM
    import job_swap as JS
    import referee_three as R3
    import job_selfpairs as SP
    out = {}
    h = JM.history(EXW_START, maxj=40, ages=5)
    st1 = h[0][2]
    import job_meet1 as J1
    out["round 1 equals the literal stage"] = J1.same_incidence(st1, EXW_STAGE, set(range(13)))
    c, bad, size = five_tests(h[1][1], h[1][2], cap=10 ** 6)
    out["five tests at the stage"] = {"size": size, "counts": c}
    S, nb = R3.relabel(EXW_STAGE)
    _, K, T = R3.readings(S, nb)
    f = list(range(nb))
    f[5], f[6] = 6, 5
    out["swap 5 6: keeps the 105 pair readings"] = all(K[a][b] == K[f[a]][f[b]] for a, b in itertools.combinations(range(nb), 2))
    out["swap 5 6: keeps existence on the 455 triples"] = all(
        (T[tuple(sorted((f[a], f[b], f[c])))] is None) == (v is None) for (a, b, c), v in T.items())
    out["sizes T(0,5,7), T(0,6,7)"] = [T[(0, 5, 7)], T[(0, 6, 7)]]
    rows = [sum(1 << x for x in q) for q in S]
    out["swap 5 6 carries the equations"] = SP.rank(rows + [sum(1 << f[x] for x in q) for q in S]) == SP.rank(rows)
    later = []
    for age, stage, nxt, new in h[1:4]:
        K2, l2, i2 = JS.table(nxt)
        g = {x: f[x] if x < nb else x for x in l2}
        later.append([len(nxt), len(l2), all(K2[i2[a]][i2[b]] == K2[i2[g[a]]][i2[g[b]]] for a, b in itertools.combinations(l2, 2))])
    out["later stages (junctions, distinctions, pair table kept with fresh names fixed)"] = later
    return out


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("BIG", {"part": "BIG"}), ("NAMED", {"part": "NAMED"}), ("FORM", {"part": "FORM"}), ("EXW", {"part": "EXW"})]
    allc += [(f"CEN-{w:02d}", {"part": "CEN", "w": w}) for w in range(16, 2, -1)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "BIG":
        r = part_big()
    elif p["part"] == "NAMED":
        r = part_named()
    elif p["part"] == "EXW":
        r = part_exw()
    elif p["part"] == "FORM":
        r = {"formulas": part_form(7, 400), "lambda under growth": part_growth_lambda(11, 300)}
    else:
        r = part_cen(p["w"])
    return json.loads(json.dumps(r, default=lambda o: int(o) if hasattr(o, "__int__") else str(o)))
