"""Shared-runner job for the referee's check of GROWN-END-MEET-ONCE-20261119-001 (Codex), with the referee's own code throughout:
its FIRST-KNOT-R1 engine with the program's rule, CENSUS-READ-R1's shore enumeration and GROW-SMALL-R1's full tables,
EXTEND-ROUND-R1's reading test and extension, CREATED-PAIR-R1's isometry search, HUNT-SHORTEN-R1's coset-representative search and
stage test.  Codex's starts and permutations are read from its artifacts as data; none of its code is run.

Parts:
- H: the seven-junction (age 1) and six-junction (age 2) histories of two_histories.json, and the three joint-minimum witnesses of
  reach_bound_threshold.json, and the nine-junction construction of structure.json: each regrown from its start; at the marked
  stage every reading-keeping table symmetry that does not carry the equations is extended through the referee's own next round;
  the failures, and the named swap's two entries.
- RD: the earlier meet-twice example (GROWN-END-SWAP's construct_6.json): every isometry of the current table fixing every
  distinction of every live junction; which extend (an isometry of the successor table agreeing on every old distinction); the
  Boolean "the pair can flip together with every other distinction fixed" read on all pairs; and the existence of a bond through
  {x, y, 15}, read on all pairs.
- CW: the two failures of Codex's census (widths 14 and 15, six starting junctions, age 2, 16 junctions), from census_results.json
  as data: each start regrown by the referee's engine; its age-2 stage and next stage compared with the literal ones (incidence
  isomorphism fixing the starting names); the literal permutation tested on the referee's own tables (an isometry? keeps the
  reading? carries the equations?); the two successor entries of the named old pair and its image; and the full stage test.
- X: the headline entries of the seven-junction history (the swap 0 1 a pointwise pair-table isometry at round 1; K(0,2), K(1,2)
  at rounds 1 and 2); on the meet-twice example the number of bonds holding {0,1} and {2,1} and the least bond through {0,1,15};
  single starting junctions of arity 3 to 9 (study 3 to 7) grown while stages have at most 14 junctions, every open stage's
  pointwise pair-table maps tested (GROWN-END-READING-R1's five tests).
- C (per starting width 3 to 14): the referee's own census of admissible starts: connected, every two junctions meeting at most
  once, every support of three or more, every support a bond (deleting the junction leaves the rest, with the exterior holder of the
  loose distinctions, connected); grown through every age while stages have at most 11 junctions (Codex's bound for no failure;
  its census runs to 16); at every open stage of age one or
  more every reading-keeping table symmetry not carrying the equations (one per holder-class coset) extended and checked.

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-END-MEET-ONCE-20261119-001/referee-R1/job_meet1.py \\
      --out runs/referee-meet1 --unit referee-meet1 --workers 4 --case-timeout 7200 --case-mem 3G --mem-max 14G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/HUNT-SHORTEN-20261119-001/referee-R1", "research/GROWN-END-SWAP-20261119-001/referee-R1",
          "research/EXTEND-ROUND-20261119-001/referee-R1", "research/CREATED-PAIR-20261119-001/referee-R1",
          "research/GROW-SMALL-20261119-001/referee-R1", "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/CENSUS-READ-20261118-001/referee-R1",
          "research/GROWN-PAIR-20261119-001/referee-R1", "research/MEET-ONCE-20261119-001/referee-R1",
          "research/PARENT-RULE-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ART = ROOT / "artifacts/GROWN-END-MEET-ONCE-20261119-001/GROWN-END-MEET-ONCE-20261119-001-E001_rounds"
SWAP = ROOT / "artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json"
CAPJ = 11
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def history(start, maxj=CAPJ, ages=40):
    """(age, stage, next, new junctions) for every round while the stage has at most maxj junctions."""
    import referee_first as RFK
    G = RFK.Start([list(s) for s in start])
    out = []
    for r in range(ages):
        stage = [sorted(b) for b in G.bits]
        if len(stage) > maxj:
            break
        nj = len(stage)
        if G.step(floored, None, None) != "ok":
            break
        nxt = [sorted(b) for b in G.bits]
        new = [{"j": j, "parents": sorted(G.parents[j]), "fresh": G.fresh[j]} for j in range(nj, len(nxt))]
        out.append((r, stage, nxt, new))
    return out


def test(stage, nxt, new):
    import job_selfpairs as SP
    return SP.test_stage(stage, nxt, new)


def live_of(stage):
    own = defaultdict(list)
    for j, s in enumerate(stage):
        for x in s:
            own[x].append(j)
    return any(len(v) == 1 for v in own.values())


def part_h():
    import job_swap as JS
    out = {}
    d = json.load(open(ART / "two_histories.json"))
    items = [("seven, age 1", d["seven_at_round_one"]), ("six, age 2", d["six_at_round_two"])]
    t = json.load(open(ART / "reach_bound_threshold.json"))
    for i, w in enumerate(t["joint_minimum_audit"]["failing_allocations"]):
        items.append((f"joint-minimum witness {i}", {"start": w["start"], "age": 1, "stages": [w["start"], w["current"], w["next"]]}))
    s9 = json.load(open(ART / "structure.json"))
    items.append(("construction, nine starting junctions", {"start": s9["start"], "age": 1}))
    for name, h in items:
        hist = history(h["start"], maxj=24, ages=(h["age"] or 1) + 1)
        row = {"starting junctions": len(h["start"])}
        if "stages" in h:
            lit = h["stages"]
            row["stages equal the literal (up to fresh names)"] = all(
                JS.same_up_to_fresh(hist[k][1], lit[k], {x for s in lit[k - 1] for x in s} if k else set())
                for k in range(min(len(lit), len(hist))) if k)
        found = []
        for age, stage, nxt, new in hist:
            if age < 1 or not live_of(stage):
                continue
            c = test(stage, nxt, new)
            nf = c.get("extensions that fail (a Claim B counterexample)", 0)
            found.append([age, len(stage), len({x for s in stage for x in s}), c.get("keep R, not the equations", 0), nf])
            if h.get("age") is not None and age > h["age"]:
                break
        row["stages tested (age, junctions, distinctions, reading-keeping non-equation symmetries, failing)"] = found
        out[name] = row
    return out


def part_rd():
    import job_created as JC
    import job_swap as JS
    import referee_census as RC
    d = json.load(open(SWAP))["a"]
    S, N = [sorted(s) for s in d["current"]], [sorted(s) for s in d["next"]]
    K1, l1, i1 = JS.table(S)
    K2, l2, i2 = JS.table(N)
    own = defaultdict(list)
    for j, s in enumerate(S):
        for x in s:
            own[x].append(j)
    live = sorted({v[0] for v in own.values() if len(v) == 1})
    fixed = sorted({x for j in live for x in S[j]})
    ex = [[(l1.index(x) + 1) if x in fixed else 0 for x in l1], [(l1.index(x) + 1) if x in fixed else 0 for x in l1]]
    isos = list(JC.isometries(K1, K1, extra=ex))
    old = set(l1)
    rows = [sum(1 << i1[x] for x in s) for s in S]

    def flip(x, y):
        """Can x and y flip together with every other distinction fixed: every equation holds both or neither."""
        m = (1 << i1[x]) | (1 << i1[y])
        return all(bin(r & m).count("1") != 1 for r in rows)
    # bonds of the current stage holding a given triple: from all bonds (shore enumeration of the support words)
    import itertools as it
    n = len(S)
    star = [sum(1 << i1[x] for x in s) for s in S]
    ownj = defaultdict(list)
    for k, s in enumerate(S):
        for x in s:
            ownj[x].append(k)
    nb = [set() for _ in range(n)]
    for x, ks in ownj.items():
        if len(ks) == 2:
            nb[ks[0]].add(ks[1])
            nb[ks[1]].add(ks[0])
    haslo = {ks[0] for x, ks in ownj.items() if len(ks) == 1}

    def connected(U):
        U = set(U)
        if not U:
            return False
        st, seen = [next(iter(U))], set()
        while st:
            u = st.pop()
            if u in seen:
                continue
            seen.add(u)
            st += [v for v in nb[u] if v in U and v not in seen]
        return seen == U
    bonds = []
    for r in range(1, n + 1):
        for U in it.combinations(range(n), r):
            O = set(range(n)) - set(U)
            if not connected(U):
                continue
            if O:
                # the other side with the exterior: connected if every component of O holds a loose distinction or O is connected
                comps = []
                rest = set(O)
                while rest:
                    st = [rest.pop()]
                    comp = set(st)
                    while st:
                        u = st.pop()
                        for v in nb[u]:
                            if v in rest:
                                rest.discard(v)
                                comp.add(v)
                                st.append(v)
                    comps.append(comp)
                if haslo:
                    if not all(c & haslo for c in comps):
                        continue
                elif len(comps) != 1:
                    continue
            w = 0
            for k in U:
                w ^= star[k]
            bonds.append(w)

    def in_bond(xs):
        m = sum(1 << i1[x] for x in xs)
        return any(b & m == m for b in bonds)
    pairs = list(it.combinations(l1, 2))
    res = Counter()
    keep = []
    for phi0 in isos:
        f = {l1[a]: l1[b] for a, b in enumerate(phi0)}
        ex2 = [[(l2.index(x) + 1) if x in old else 0 for x in l2], [0] * len(l2)]
        for x in old:
            ex2[1][l2.index(f[x])] = l2.index(x) + 1
        extends = next(iter(JC.isometries(K2, K2, extra=ex2, cap=1)), None) is not None
        keeps_flip = all(flip(x, y) == flip(f[x], f[y]) for x, y in pairs)
        keeps_tri = all(in_bond((x, y, 15)) == in_bond((f[x], f[y], f.get(15, 15))) for x, y in pairs if 15 not in (x, y))
        res["matchings fixing every live distinction"] += 1
        res["extend"] += extends
        res["keep the flip-together reading on every pair"] += keeps_flip
        res["keep the bond-through-{x,y,15} reading on every pair"] += keeps_tri
        res["flip reading agrees with extending"] += keeps_flip == extends
        res["triple reading agrees with extending"] += keeps_tri == extends
    res["flip(0,1), flip(2,1)"] = str((flip(0, 1), flip(2, 1)))
    res["a bond through {0,1,15}, through {2,1,15}"] = str((in_bond((0, 1, 15)), in_bond((2, 1, 15))))
    return dict(res)


def same_incidence(A, B, fixed):
    """Are two junction lists isomorphic as incidence structures with every name in fixed mapped to itself?"""
    import networkx as nx
    from networkx.algorithms import isomorphism as iso

    def g(S):
        G = nx.Graph()
        for j, s in enumerate(S):
            G.add_node(("j", j), t="j")
            for x in s:
                G.add_node(("d", x), t=("d", x) if x in fixed else "d")
                G.add_edge(("j", j), ("d", x))
        return G
    return nx.is_isomorphic(g(A), g(B), node_match=iso.categorical_node_match("t", None))


def part_cw():
    import job_extend as JE
    import job_swap as JS
    d = json.load(open(ART / "census_results.json"))
    out = {}
    for x in d["stages"]:
        if "witness" not in x:
            continue
        w = x["witness"]
        row = {"key": x["key"], "starting junctions": len(w["start"])}
        hist = history(w["start"], maxj=24, ages=3)
        fixed = {b for s in w["start"] for b in s}
        mine = [h for h in hist if h[0] == 2]
        row["referee's age-2 stage and next equal the literal"] = bool(mine) and same_incidence(mine[0][1], w["current"], fixed) \
            and same_incidence(mine[0][2], w["next"], fixed)
        # the literal permutation on the literal stages, with the referee's own tables
        cur, nxt = [sorted(s) for s in w["current"]], [sorted(s) for s in w["next"]]
        perm = {i: v for i, v in enumerate(w["old_movable_permutation"])}
        K1, l1, i1 = JS.table(cur)
        f = {b: perm.get(b, b) for b in l1}
        row["the permutation is an isometry of the stage table"] = all(
            K1[i1[a]][i1[b]] == K1[i1[f[a]]][i1[f[b]]] for a, b in itertools.combinations(l1, 2))
        R = JE.reading(cur)
        psi, whole, top = JE.keeps(f, cur, cur, R, R)
        row["keeps the reading"] = psi is not None and bool(top)
        own = JE.owners(cur)
        live = {v[0] for v in own.values() if len(v) == 1}
        row["fixes every distinction of every live junction"] = all(f[b] == b for j in live for b in cur[j])
        import job_selfpairs as SP
        idx = {b: i for i, b in enumerate(l1)}
        rows = [sum(1 << idx[b] for b in s) for s in cur]
        img = [sum(1 << idx[f[b]] for b in s) for s in cur]
        row["carries the equations"] = SP.rank(rows + img) == SP.rank(rows)
        K2, l2, i2 = JS.table(nxt)
        a, b = w["old_pair"]
        row["successor entries K(pair), K(image) (study's)"] = [[K2[i2[a]][i2[b]], K2[i2[f[a]]][i2[f[b]]]], w["successor_K"]]
        row["both old (no fresh naming can repair)"] = a in f and b in f
        if mine:
            c = test(mine[0][1], mine[0][2], mine[0][3])
            row["stage test"] = dict(c)
        out[str(x["key"])] = row
    return json.loads(json.dumps(out, default=int))


def part_x():
    sys.path.insert(0, str(ROOT / "research/GROWN-END-READING-20261119-001/referee-R1"))
    import job_ger as JG  # noqa: F401  (puts THREE-WAY-R1 and UNIQUE-TABLE-R1 on the path)
    import referee_three as R3
    out = {}
    d = json.load(open(ART / "two_histories.json"))["seven_at_round_one"]
    cur, nxt = [sorted(q) for q in d["stages"][1]], [sorted(q) for q in d["stages"][2]]
    S, nb = R3.relabel(cur)
    labels = sorted({x for q in cur for x in q})
    assert labels == list(range(nb))
    _, K, _ = R3.readings(S, nb)
    f = list(range(nb))
    f[0], f[1] = 1, 0
    own = defaultdict(list)
    for j, q in enumerate(cur):
        for x in q:
            own[x].append(j)
    live = {own[x][0] for x in own if len(own[x]) == 1}
    out["seven: swap 0 1 keeps every current pair reading"] = all(
        K[a][b] == K[f[a]][f[b]] for a, b in itertools.combinations(range(nb), 2))
    out["seven: current pairs"] = nb * (nb - 1) // 2
    out["seven: swap fixes every live distinction"] = all(f[x] == x for j in live for x in cur[j])
    S2, nb2 = R3.relabel(nxt)
    _, K2, _ = R3.readings(S2, nb2)
    out["seven: sizes K(0,2), K(1,2) at round 1 and at round 2"] = [[K[0][2], K[1][2]], [K2[0][2], K2[1][2]]]
    dd = json.load(open(SWAP))["a"]
    S6, nb6 = R3.relabel([sorted(q) for q in dd["current"]])
    bonds, K6, T6 = R3.readings(S6, nb6)
    held = lambda xs: [b for b in bonds if all(b >> x & 1 for x in xs)]  # noqa: E731
    out["meet twice: bonds holding {0,1}, {2,1}"] = [len(held((0, 1))), len(held((2, 1)))]
    out["meet twice: least bond through {0,1,15}, {2,1,15}"] = [T6[(0, 1, 15)], T6[(1, 2, 15)]]
    single = {}
    for a in range(3, 10):
        tot = Counter()
        for age, stage, nx_, new in history([list(range(a))], maxj=14):
            if age < 1 or not live_of(stage):
                continue
            c, bad, size = JG.five_tests(stage, nx_)
            tot["open stages"] += 1
            tot["pair-table maps"] += c.get("pair-table maps", 0)
            tot["extend"] += c.get("extend", 0)
            tot["carry the equations"] += c.get("carry the equations", 0)
        single[a] = dict(tot)
    out["single starts (open stages to 14 junctions; maps; extend; carry)"] = single
    return json.loads(json.dumps(out, default=int))


# ---- the census ----

def graphs(wmax):
    """Connected simple graphs (by vertex addition with any nonempty neighbour set) whose shared count plus arity deficits fit."""
    import networkx as nx
    def bound(G):
        return G.number_of_edges() + sum(max(0, 3 - d) for _, d in G.degree())
    level = [nx.empty_graph(1)]
    out = list(level)
    while level:
        found = defaultdict(list)
        for G in level:
            n = G.number_of_nodes()
            for r in range(1, n + 1):
                for S in itertools.combinations(range(n), r):
                    H = G.copy()
                    H.add_edges_from((n, s) for s in S)
                    if bound(H) > wmax:
                        continue
                    key = (tuple(sorted(d for _, d in H.degree())), nx.weisfeiler_lehman_graph_hash(H, iterations=4))
                    if any(nx.is_isomorphic(H, K) for K in found[key]):
                        continue
                    found[key].append(H)
        level = [K for v in found.values() for K in v]
        out += level
    return out


def admissible_starts(W, glist):
    import networkx as nx
    from networkx.algorithms import isomorphism as iso
    starts = []
    for G in glist:
        n, E = G.number_of_nodes(), G.number_of_edges()
        deg = dict(G.degree())
        need = [max(0, 3 - deg[v]) for v in range(n)]
        L = W - E
        if L < sum(need):
            continue
        reps = []
        for extra in itertools.combinations_with_replacement(range(n), L - sum(need)):
            loose = list(need)
            for v in extra:
                loose[v] += 1
            H = G.copy()
            for v in range(n):
                H.nodes[v]["l"] = loose[v]
            if any(nx.is_isomorphic(H, K, node_match=iso.categorical_node_match("l", 0)) for K in reps):
                continue
            reps.append(H)
            # every support a bond
            X = G.copy()
            if sum(loose):
                X.add_node("x")
                X.add_edges_from(("x", v) for v in range(n) if loose[v])
            ok = True
            for v in range(n):
                Y = X.copy()
                Y.remove_node(v)
                if Y.number_of_nodes() and not nx.is_connected(Y):
                    ok = False
                    break
            if not ok:
                continue
            stars = [[] for _ in range(n)]
            b = 0
            for u, v in sorted(G.edges()):
                stars[u].append(b)
                stars[v].append(b)
                b += 1
            for v in range(n):
                for _ in range(loose[v]):
                    stars[v].append(b)
                    b += 1
            starts.append(stars)
    return starts


def part_c(W):
    glist = graphs(W)
    starts = admissible_starts(W, glist)
    s = Counter()
    s["admissible starts"] = len(starts)
    fails = []
    for st in starts:
        for age, stage, nxt, new in history(st):
            if age < 1 or not live_of(stage):
                continue
            s["open stages"] += 1
            c = test(stage, nxt, new)
            s["reading-keeping symmetries not carrying the equations"] += c.get("keep R, not the equations", 0)
            nf = c.get("extensions that fail (a Claim B counterexample)", 0)
            s["failing symmetries"] += nf
            if nf:
                s["failing stages"] += 1
                fails.append({"start": st, "age": age, "junctions": len(stage), "distinctions": len({x for q in stage for x in q})})
            s["capped stages"] += bool(c.get("capped"))
    return {"counts": dict(s), "failures": fails}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [("H", {"part": "H"}), ("RD", {"part": "RD"}), ("CW", {"part": "CW"}), ("X", {"part": "X"})] + [(f"C-{w:02d}", {"part": "C", "w": w}) for w in range(14, 2, -1)]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "H":
        return part_h()
    if p["part"] == "RD":
        return part_rd()
    if p["part"] == "CW":
        return part_cw()
    if p["part"] == "X":
        return part_x()
    return part_c(p["w"])
