"""Shared-runner job for the referee's check of GROWN-END-SWAP-20261119-001 (Codex), with the referee's own code: its FIRST-KNOT-R1
engine with the program's complete-round rule, CENSUS-READ-R1's shore enumeration for full tables, EXTEND-ROUND-R1's reading test
and extension, and CREATED-PAIR-R1's isometry search.  The study's start and permutation are read from construct_6.json, 7 and 11
as data; none of its code is run.

Part X (each construct): grow the start two complete rounds; compare both stages with the literal ones (up to the names of fresh
distinctions); full tables of the reached stage and of its successor; the swap: an isometry of the reached table? does it keep the
reading R (loose onto loose, live stars onto live stars, F onto F) and carry the equations? the extension and its check on the
successor table; whether any isometry of the successor table agrees with the swap on the old distinctions; the 24 permutations of
the four middle distinctions on both tables.
Part C: every touch-census start regrown to 14 junctions; whether any census stage is isomorphic (as an arrangement) to the
reached ten-junction stage.

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-END-SWAP-20261119-001/referee-R1/job_swap.py \\
      --out runs/referee-swap --unit referee-swap --workers 2 --case-timeout 3600 --case-mem 3G --mem-max 8G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/HUNT-SHORTEN-20261119-001/referee-R1", "research/EXTEND-ROUND-20261119-001/referee-R1",
          "research/CREATED-PAIR-20261119-001/referee-R1", "research/GROW-SMALL-20261119-001/referee-R1",
          "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/GROWN-PAIR-20261119-001/referee-R1",
          "research/MEET-ONCE-20261119-001/referee-R1", "research/PARENT-RULE-20261119-001/referee-R1",
          "research/RING-IDENT-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ART = ROOT / "artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached"
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


def table(stars):
    import referee_census as RC
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    K, _ = RC.shore_table([[idx[b] for b in s] for s in stars])
    return K, labels, idx


def same_up_to_fresh(mine, theirs, old):
    """Equal as junction lists, the fresh names matched by a bijection respecting the junction order of each new junction set."""
    if len(mine) != len(theirs):
        return False
    a = sorted(tuple(sorted(x for x in s if x in old)) + (len([x for x in s if x not in old]),) for s in mine)
    b = sorted(tuple(sorted(x for x in s if x in old)) + (len([x for x in s if x not in old]),) for s in theirs)
    return a == b


def part_x(name):
    import referee_first as RFK
    import job_extend as JE
    import job_created as JC
    d = json.load(open(ART / name))
    key = "a" if "a" in d else list(d)[0]
    start, current, nxt = d[key]["start"], d[key]["current"], d[key]["next"]
    perm = {a: b for a, b in d["permutation"]}
    out = {"construct": name, "start junctions": len(start)}
    G = RFK.Start([list(s) for s in start])
    r1 = G.step(floored, None, None)
    st1 = [sorted(b) for b in G.bits]
    r2 = G.step(floored, None, None)
    st2 = [sorted(b) for b in G.bits]
    old0 = {x for s in start for x in s}
    out["round 1 equals the literal (up to fresh names)"] = r1 == "ok" and same_up_to_fresh(st1, current, old0)
    old1 = {x for s in current for x in s}
    out["round 2 equals the literal (up to fresh names)"] = r2 == "ok" and same_up_to_fresh(st2, nxt, old1)
    # tables on the literal names
    S, N = [sorted(s) for s in current], [sorted(s) for s in nxt]
    K1, l1, i1 = table(S)
    K2, l2, i2 = table(N)
    n1 = len(l1)
    full = {x: perm.get(x, x) for x in l1}
    out["distinctions (reached, successor)"] = [n1, len(l2)]
    out["the swap is an isometry of the reached table (all pairs)"] = all(
        K1[i1[x]][i1[y]] == K1[i1[full[x]]][i1[full[y]]] for x, y in itertools.combinations(l1, 2))
    out["pairs in the reached table"] = n1 * (n1 - 1) // 2
    R = JE.reading(S)
    psi, whole, top = JE.keeps(full, S, S, R, R)
    out["keeps the reading (F whole / maximal members)"] = [psi is not None and whole, psi is not None and top]
    out["psi on live junctions is the identity"] = psi is not None and all(psi[u] == u for u in psi)
    rows = [sum(1 << i1[x] for x in s) for s in S]
    img = [sum(1 << i1[full[x]] for x in s) for s in S]
    import job_selfpairs as SP
    out["carries the equations"] = SP.rank(rows + img) == SP.rank(rows)
    out["carries every junction onto a junction"] = {frozenset(full[x] for x in s) for s in S} == {frozenset(s) for s in S}
    # the extension through the referee's own round
    Sx, Nx, oldx = JE.relabel_pair(S, N)
    # relabel_pair renames to 0..; map the swap through it
    labs = sorted({b for s in N for b in s})
    ren = {b: i for i, b in enumerate(labs)}
    fullx = {ren[x]: ren[full[x]] for x in l1}
    new = []
    own = JE.owners(Sx)
    for j in range(len(Sx), len(Nx)):
        parents = sorted({own[x][0] for x in Nx[j] if x in oldx})
        new.append({"j": j, "parents": parents, "fresh": len([x for x in Nx[j] if x not in oldx])})
    A = {"S": Sx, "N": Nx, "old": oldx, "new": new, "own": own}
    Rx = JE.reading(Sx)
    psix, _, topx = JE.keeps(fullx, Sx, Sx, Rx, Rx)
    phi2 = JE.extend(fullx, psix, A, A) if psix is not None else None
    out["extension defined"] = phi2 is not None
    if phi2 is not None:
        n2 = len(labs)
        bad = [(labs[x], labs[y]) for x, y in itertools.combinations(range(n2), 2) if K2[i2[labs[x]]][i2[labs[y]]] !=
               K2[i2[labs[phi2[x]]]][i2[labs[phi2[y]]]]]
        out["extension is an isometry of the successor table"] = not bad
        out["pairs that fail under the extension"] = [list(map(int, p)) for p in bad]
    g = lambda T, ii, a, b: int(T[ii[a]][ii[b]])  # noqa: E731
    out["K (bond size) of 0,1 and 2,1: reached / successor"] = [[g(K1, i1, 0, 1), g(K1, i1, 2, 1)], [g(K2, i2, 0, 1), g(K2, i2, 2, 1)]]
    # any isometry of the successor table agreeing with the swap on old distinctions?
    oldl = [x for x in l2 if x in old1]
    ex = [[(l2.index(x) + 1) if x in old1 else 0 for x in l2], [0] * len(l2)]
    for x in oldl:
        ex[1][l2.index(full.get(x, x))] = l2.index(x) + 1
    hit = next(iter(JC.isometries(K2, K2, extra=ex, cap=1)), None)
    out["an isometry of the successor table agrees with the swap on every old distinction"] = hit is not None
    # the 24 permutations of the four middle distinctions
    mid = [0, 1, 2, 3]
    good1 = good2 = 0
    for pm in itertools.permutations(mid):
        f = {x: x for x in l2}
        f.update(dict(zip(mid, pm)))
        ok1 = all(K1[i1[x]][i1[y]] == K1[i1[f[x]]][i1[f[y]]] for x, y in itertools.combinations(l1, 2))
        ok2 = all(K2[i2[x]][i2[y]] == K2[i2[f[x]]][i2[f[y]]] for x, y in itertools.combinations(l2, 2))
        good1 += ok1
        good2 += ok1 and ok2
    out["permutations of 0..3 kept by the reached table / and by the successor table (identity on the rest)"] = [good1, good2]
    out["junctions meeting twice in the start"] = sum(1 for v in Counter(tuple(ks) for ks in owners_of(start).values() if len(ks) == 2).values() if v >= 2)
    return out


def owners_of(J):
    own = defaultdict(list)
    for k, s in enumerate(J):
        for x in s:
            own[x].append(k)
    return own


def canon_hash(stars):
    import networkx as nx
    g = nx.Graph()
    for j, s in enumerate(stars):
        g.add_node(("j", j), k="j")
        for x in s:
            g.add_node(("b", x), k="b")
            g.add_edge(("j", j), ("b", x))
    return nx.weisfeiler_lehman_graph_hash(g, node_attr="k", iterations=6), g


def part_c():
    import networkx as nx
    import job_ring as JR
    import job_selfpairs as SP
    d = json.load(open(ART / "construct_6.json"))
    target = [sorted(s) for s in d["a"]["current"]]
    h0, g0 = canon_hash(target)
    s = Counter()
    found = []
    for key in SP.census():
        sizes, flat = key
        n = len(sizes)
        edges = []
        for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
            edges += [(i, j)] * m
        for r, stage, nx_, new in SP.stages(JR.stars_of(n, edges, list(sizes))):
            if len(stage) != len(target):
                continue
            s["census stages of ten junctions"] += 1
            h, g = canon_hash(stage)
            if h == h0 and nx.is_isomorphic(g, g0, node_match=lambda a, b: a["k"] == b["k"]):
                found.append([key, r])
    s["isomorphic to the reached ten-junction stage"] = len(found)
    return {"counts": dict(s), "found": found[:5]}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [(f"X-{n}", {"part": "X", "name": f"construct_{n}.json"}) for n in (6, 7, 11)] + [("C", {"part": "C"})]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "X":
        return part_x(p["name"])
    return part_c()
