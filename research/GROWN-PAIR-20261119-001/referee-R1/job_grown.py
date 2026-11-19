"""Shared-runner job for the referee's check of GROWN-PAIR-20261119-001 (one group per case; own growth, tables and searches; the
groups' representatives and provenance read from other_states.json as data; no study code imported or run).

For each of the 152 other-state groups, for every pair of its representatives:
- provenance: the referee regrows each representative's start (census index -> key, from runs/census-exact5) to the recorded round
  with its own engine (FRESH-COUNT-R1 / FIRST-KNOT-R1) and checks the stage is the recorded arrangement (isomorphism);
- the start shares two distinctions between two knots; the two representatives come from different starts;
- the arrangements are not isomorphic; their exact tables (the referee's closed-aware shore enumeration) are isometric (the
  referee's exact twin-quotient search);
- states: is there a bijection of distinctions carrying one equation space onto the other?  Every such bijection preserves the
  table, so the search runs over table isometries only, with distinctions held by the same junctions taken in increasing order, and
  prunes as soon as a star's image leaves the other span: exact.
- the next stage and the one after (round + 1, + 2, from the same starts; at most 14 junctions): isometric tables? same states?

  .venv/bin/python -B scripts/longrun.py launch research/GROWN-PAIR-20261119-001/referee-R1/job_grown.py \\
      --out runs/referee-grown-pair --unit referee-grown-pair --workers 6 --case-timeout 900 --case-mem 2G --mem-max 16G
"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/NAE-GROWTH-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
OS = ROOT / "artifacts/GROWN-PAIR-20261119-001A/GROWN-PAIR-20261119-001A-E001_pairs/other_states.json"
KEYS = {}


def setup(params):
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            for a in r["result"]["arrangements"]:
                KEYS[a["index"]] = a["key"]


def cases():
    for i, g in enumerate(json.load(open(OS))["group_list"]):
        yield f"g{i:03d}", {"group": g, "keys": {str(ix): KEYS.get(ix) for rep in g["reps"] for ix, _ in rep["prov"]}}


def span(stars):
    basis = {}
    for S in stars:
        r = sum(1 << x for x in S)
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return basis


def in_span(basis, r):
    while r:
        p = r.bit_length() - 1
        if p not in basis:
            return False
        r ^= basis[p]
    return True


def relabel(stars):
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    return [sorted(idx[b] for b in s) for s in stars], len(labels)


def same_states(A, B, KA, KB, n, cap=2000000):
    """Exact: a bijection preserving the tables that carries span(A) onto span(B) (equal ranks; every A star's image in span B)."""
    from collections import defaultdict
    bB = span(B)
    if len(span(A)) != len(bB):
        return False, 0
    own = defaultdict(list)
    for j, s in enumerate(A):
        for b in s:
            own[b].append(j)
    sig = {b: tuple(sorted(own[b])) for b in range(n)}
    order = sorted(range(n), key=lambda b: (sig[b], b))
    prev = {order[i]: order[i - 1] for i in range(1, n) if sig[order[i]] == sig[order[i - 1]]}
    rowA = [sorted(KA[x]) for x in range(n)]
    rowB = [sorted(KB[y]) for y in range(n)]
    cand = {x: [y for y in range(n) if rowA[x] == rowB[y]] for x in range(n)}
    pos = {x: k for k, x in enumerate(order)}
    done_at = defaultdict(list)                       # star j is fully assigned when its last distinction (in order) is
    for j, s in enumerate(A):
        done_at[max(s, key=lambda b: pos[b])].append(j)
    img, used, steps = {}, set(), [0]

    def go(k):
        steps[0] += 1
        if steps[0] > cap:
            return None
        if k == n:
            return True
        x = order[k]
        for y in cand[x]:
            if y in used or (x in prev and y < img[prev[x]]):
                continue
            if any(KA[x][z] != KB[y][w] for z, w in img.items()):
                continue
            img[x] = y
            used.add(y)
            ok = all(in_span(bB, sum(1 << img[b] for b in A[j])) for j in done_at[x])
            if ok:
                r = go(k + 1)
                if r:
                    return True
                if r is None:
                    return None
            del img[x]
            used.discard(y)
        return False
    r = go(0)
    return r, steps[0]


def stage(key, rnd):
    import referee_first as RFK
    import referee_census as RC
    G = RFK.Start(RC.stars_of(tuple(map(tuple, key))))
    for _ in range(rnd):
        if G.step(RFK.fewest, None, None) != "ok":
            return None
    return [sorted(s) for s in G.bits]


def run(case_id, payload):
    import itertools
    import networkx as nx
    import referee_f as F
    import referee_census as RC
    g = payload["group"]
    keys = {int(k): v for k, v in payload["keys"].items()}

    def inc(stars):
        G = nx.Graph()
        for j, s in enumerate(stars):
            G.add_node(("j", j), k="j")
            for b in s:
                G.add_node(("b", b), k="b")
                G.add_edge(("j", j), ("b", b))
        return G
    NM = nx.algorithms.isomorphism.categorical_node_match("k", None)
    reps = g["reps"]
    out = {"distinctions": g["distinctions"], "reps": len(reps)}
    prov_ok, two_ok, starts = [], [], []
    for rep in reps:
        ix, rnd = rep["prov"][0]
        key = keys[ix]
        starts.append(ix)
        two_ok.append(max(key[1]) >= 2 if key[1] else False)
        st = stage(key, rnd)
        prov_ok.append(st is not None and nx.is_isomorphic(inc(st), inc(rep["stars"]), node_match=NM))
    out["regrown stage = recorded arrangement"] = prov_ok
    out["start has two knots sharing two"] = two_ok
    out["representatives from different starts"] = len(set(starts)) == len(starts)
    stars = [relabel(rep["stars"]) for rep in reps]
    tabs = [RC.shore_table(s)[0] for s, _ in stars]
    pairs = []
    for a, b in itertools.combinations(range(len(reps)), 2):
        (A, n), (B, _) = stars[a], stars[b]
        iso_arr = nx.is_isomorphic(inc(A), inc(B), node_match=NM)
        p = F.isometric(tabs[a], tabs[b])
        ss, steps = same_states(A, B, tabs[a], tabs[b], n) if p is not None else (None, 0)
        pairs.append({"arrangements isomorphic": iso_arr, "tables isometric": p is not None, "same states": ss, "search steps": steps})
    out["pairs"] = pairs
    nxt = {}
    for d in (1, 2):
        st = []
        for rep in reps:
            ix, rnd = rep["prov"][0]
            s = stage(keys[ix], rnd + d)
            st.append(s)
        if any(s is None or len(s) > 14 for s in st):
            nxt[f"round + {d}"] = "out of range (closed, stalled, or over 14 junctions)"
            continue
        rs = [relabel(s) for s in st]
        ts = [RC.shore_table(s)[0] for s, _ in rs]
        row = []
        for a, b in itertools.combinations(range(len(reps)), 2):
            p = F.isometric(ts[a], ts[b])
            ss = same_states(rs[a][0], rs[b][0], ts[a], ts[b], rs[a][1])[0] if p is not None else None
            row.append({"tables isometric": p is not None, "same states": ss})
        nxt[f"round + {d}"] = row
    out["next"] = nxt
    out["study: next tables isomorphic, next states agree"] = [g.get("next_tables_isomorphic"), g.get("next_states_agree")]
    return out
