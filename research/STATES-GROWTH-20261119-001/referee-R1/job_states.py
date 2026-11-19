"""Shared-runner job for the referee's joint check of STATES-GROWTH-20261119-001, MANY-VALUED-20261119-001 and
DROPPED-JUNCTION-20261119-001 (own code; stages, starts and the studies' records read as data; no study code imported or run).

Parts (case prefixes):
- B-*: NAE-GROWTH's 2,715 part-B stages (runs/nae-growth, as data).  For each: the allowed states under not-all-equal (the
  referee's NAE-GROWTH-R1 code); M(S), every minimal not-all-equal constraint, of any size, by a down-closure over all 2^n sets
  (a set is invalid when it lies inside some state or inside its complement; M is the minimal valid sets); the same cut at one
  place above the largest knot, as statelib.nae_core does; the verdict (saturated, sharpened, undefined) both ways; redundant knots.
- D: parity's same-state pairs among the distinct presentations: tables by the referee's brute force, exact isometry, an exact
  search for a renaming carrying the states (it returns the renaming); for each same-state pair, the completed systems (junctions
  and 'out'), three-connectivity by the referee's own test (no cut of at most two points, at least four points), an isomorphism
  of the completed systems that induces the renaming on the lines (Whitney's statement), and a plain isomorphism (the study's).
- T-*: every census arrangement of one to four knots (1,939), grown 6 rounds while at most 18 distinctions, by the cheapest growth
  under not-all-equal (the referee's engine: complete rounds, the fewest counts, implication by SAT) and by the states-only growth
  (on M(S) when M(S) is the presentation; else the admissible irredundant presentations drawn from M(S), grown when unique up to
  renaming), counts compared round by round; redundant knots recorded.
- X: MANY-VALUED's exceptional start, by hand.
- P-*: DROPPED-JUNCTION's starts (runs/dropped-junction, as data): the completed system and every dropped choice, rebuilt by the
  referee; each choice's parity states compared with the original's (equal spans of the junction equations); each grown by the
  referee's engine under parity (30 rounds or 30,000 junctions) and its first 20 counts compared with the study's.

  .venv/bin/python -B scripts/longrun.py launch research/STATES-GROWTH-20261119-001/referee-R1/job_states.py \\
      --out runs/referee-states --unit referee-states --workers 3 --case-timeout 3600 --case-mem 4G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/NAE-GROWTH-20261119-001/referee-R1", "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1",
          "research/CLUSTER-ALL-20261119-001/referee-R1", "research/LOOP-CATALOGUE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
BMAX, ROUNDS = 18, 6


# ---------------------------------------------------------------- minimal constraints

def minimal_nae(n, st):
    """Every minimal set of distinctions on which no allowed state is constant (any size >= 2), as sorted tuples."""
    N = 1 << n
    bad = np.zeros(N, dtype=bool)                      # bad[m]: m lies inside a state or inside a state's complement
    full = N - 1
    bad[st] = True
    bad[full ^ st] = True
    for b in range(n):                                 # down-closure: every subset of a bad set is bad
        bit = 1 << b
        idx = np.arange(N)
        hi = idx[(idx & bit) != 0]
        bad[hi ^ bit] |= bad[hi]
    valid = ~bad
    minimal = valid.copy()
    idx = np.arange(N)
    for b in range(n):
        bit = 1 << b
        has = (idx & bit) != 0
        minimal[has] &= ~valid[idx[has] ^ bit]
    out = []
    for m in np.nonzero(minimal)[0]:
        m = int(m)
        if m.bit_count() >= 2:
            out.append(tuple(x for x in range(n) if m >> x & 1))
    return sorted(out)


def verdict(stars, core):
    P = sorted(tuple(sorted(x)) for x in stars)
    if P == sorted(core):
        return "saturated"
    held = Counter(b for S in core for b in S)
    if all(len(S) >= 3 for S in core) and all(v <= 2 for v in held.values()):
        return "sharpened"
    return "undefined"


def n_redundant(n, stars):
    import referee_nae as RN
    full = len(RN.nae_states(n, stars))
    return sum(len(RN.nae_states(n, stars[:j] + stars[j + 1:])) == full for j in range(len(stars)))


# ---------------------------------------------------------------- presentations from M(S)

def presentations(n, st, pool, cap=200000):
    """Admissible (three places or more, every distinction held once or twice), irredundant sets of members of `pool` allowing
    exactly the states st.  Backtracking over the pool in order, every distinction held at most twice."""
    import referee_nae as RN
    target = np.sort(st)
    pool = sorted(set(tuple(sorted(x)) for x in pool if len(x) >= 3))
    found, steps = [], [0]
    held = [0] * n

    def ok(Q):
        if min(held) < 1:
            return False
        s = np.sort(RN.nae_states(n, [list(x) for x in Q]))
        if len(s) != len(target) or not np.array_equal(s, target):
            return False
        return not any(len(RN.nae_states(n, [list(x) for x in Q if x != y])) == len(target) for y in Q)

    def go(i, Q):
        steps[0] += 1
        if steps[0] > cap:
            return
        if i == len(pool):
            if Q and ok(Q):
                found.append(list(Q))
            return
        S = pool[i]
        if all(held[b] < 2 for b in S):
            for b in S:
                held[b] += 1
            go(i + 1, Q + [S])
            for b in S:
                held[b] -= 1
        go(i + 1, Q)
    go(0, [])
    return found, steps[0] > cap


def iso_classes(pres):
    import networkx as nx
    nm = nx.algorithms.isomorphism.categorical_node_match("k", None)
    graphs, classes = [], []
    for p in pres:
        G = nx.Graph()
        for j, S in enumerate(p):
            G.add_node(("j", j), k="j")
            for b in S:
                G.add_node(("b", b), k="b")
                G.add_edge(("j", j), ("b", b))
        for i, H in enumerate(graphs):
            if nx.is_isomorphic(G, H, node_match=nm):
                classes[i].append(p)
                break
        else:
            graphs.append(G)
            classes.append([p])
    return classes


def renumber(stars):
    bits = sorted({b for s in stars for b in s})
    m = {b: i for i, b in enumerate(bits)}
    return [sorted(m[b] for b in s) for s in stars]


def nae_step(stars):
    """One round of the cheapest growth under not-all-equal (the referee's engine), from these stars as a start."""
    import referee_first as RFK
    import referee_nae as RN
    G = RFK.Start([list(s) for s in stars])
    r = G.step(RN.nae_fewest, None, None)
    if r != "ok":
        return None, r
    new = sum(1 for j in range(len(G.bits)) if G.round[j] == 1)
    return renumber(G.bits), new


# ---------------------------------------------------------------- parts

def part_b(rows):
    import referee_nae as RN
    out = []
    for s in rows:
        n = s["bits"]
        stars = s["stars"]
        st = RN.nae_states(n, stars)
        M = minimal_nae(n, st)
        cap = max(len(x) for x in stars) + 1
        Mc = [S for S in M if len(S) <= cap]
        out.append({"i": s["i"], "n": n, "junctions": len(stars), "verdict": verdict(stars, M), "verdict at the cut": verdict(stars, Mc),
                    "constraints above the cut": len(M) - len(Mc), "redundant": n_redundant(n, stars)})
    return {"stages": out}


def part_t(keys):
    import referee_nae as RN
    import referee_touch as RT
    out = []
    for key in keys:
        sizes, flat = key
        k = len(sizes)
        Mx = [[0] * k for _ in range(k)]
        for (i, j), m in zip(itertools.combinations(range(k), 2), flat):
            Mx[i][j] = Mx[j][i] = m
        stars = renumber(RT.stars(list(sizes), Mx))
        cheap, so = stars, stars
        verdicts, agree, red, npres = [], [], False, []
        for t in range(ROUNDS):
            n = 1 + max(x for s in so for x in s)
            if n > BMAX:
                break
            st = RN.nae_states(n, so)
            red = red or n_redundant(n, so) > 0
            M = minimal_nae(n, st)
            v = verdict(so, M)
            use = so
            if v != "saturated":
                pres, capped = presentations(n, st, M)
                cls = iso_classes(pres)
                npres.append([t, len(pres), len(cls), capped, v])
                if len(cls) != 1:
                    verdicts.append(f"{v}: {'several' if cls else 'none'}")
                    break
                use = cls[0][0]
                v = f"{v}: unique"
            verdicts.append(v)
            nxt_s, ns = nae_step(use)
            nxt_c, nc = nae_step(cheap)
            agree.append(ns == nc)
            if nxt_s is None or nxt_c is None:
                break
            so, cheap = nxt_s, nxt_c
        out.append({"key": key, "verdicts": verdicts, "agree": agree, "redundant": red, "presentations": npres})
    return {"trajectories": out}


def part_x():
    import referee_nae as RN
    A = [[0, 1, 2], [3, 4, 5], [0, 3, 6], [1, 2, 4, 5, 6]]
    Bp = [[0, 1, 2], [3, 4, 5], [0, 3, 6], [1, 2, 4, 5]]
    sa, sb = np.sort(RN.nae_states(7, A)), np.sort(RN.nae_states(7, Bp))
    core_holds = bool(all(((s >> 1 & 1) + (s >> 2 & 1) + (s >> 4 & 1) + (s >> 5 & 1)) % 4 != 0 for s in sa))
    M = minimal_nae(7, sa)

    def grow(stars, rounds=4):
        import referee_first as RFK
        G = RFK.Start([list(s) for s in stars])
        res = []
        for _ in range(rounds):
            r = G.step(RN.nae_fewest, None, None)
            if r != "ok":
                res.append(r)
                break
            res.append(sum(1 for j in range(len(G.bits)) if G.round[j] == G.rounds))
        return res
    held = Counter(b for S in A for b in S)
    pres, _ = presentations(7, sa, M)
    pres2, _ = presentations(7, sa, sorted(set(map(tuple, M)) | {tuple(x) for x in A}))
    return {"states A / B": [len(sa), len(sb)], "same states": bool(np.array_equal(sa, sb)),
            "NAE(1, 2, 4, 5) holds on A's states": core_holds, "minimal constraints": M,
            "(1, 2, 4, 5, 6) minimal": (1, 2, 4, 5, 6) in M, "A: holders per distinction": dict(held),
            "grow A": grow(A), "grow B": grow(Bp),
            "presentations from M": pres, "presentations from M and A's knots": pres2}


def part_p(rows):
    import referee_first as RFK
    import referee_loop as RL

    def completed(stars):
        own = defaultdict(list)
        for j, s in enumerate(stars):
            for b in s:
                own[b].append(j)
        return [(js[0], js[1] if len(js) == 2 else "out") for b, js in sorted(own.items())]

    def rechoice(stars, v):
        lines = completed(stars)
        keep = [p for p in list(range(len(stars))) + ["out"] if p != v]
        ix = {p: i for i, p in enumerate(keep)}
        new = [[] for _ in keep]
        for b, (x, y) in enumerate(lines):
            for p in (x, y):
                if p != v:
                    new[ix[p]].append(b)
        return new

    def span(stars):
        basis = {}
        for s in stars:
            r = sum(1 << b for b in s)
            while r:
                p = r.bit_length() - 1
                if p not in basis:
                    basis[p] = r
                    break
                r ^= basis[p]
        return basis

    def same_span(a, b):
        A, B = span(a), span(b)
        if len(A) != len(B):
            return False
        for r in B.values():
            while r:
                p = r.bit_length() - 1
                if p not in A:
                    return False
                r ^= A[p]
        return True
    import referee_touch as RT
    out = []
    for r in rows:
        k = len(r["sizes"])
        Mx = [[0] * k for _ in range(k)]
        for a, b in r["edges"]:
            Mx[a][b] += 1
            Mx[b][a] += 1
        stars = RT.stars(r["sizes"], Mx)
        res = []
        for ch in r["choices"]:
            v = "out" if ch["drop"] == "out" else int(ch["drop"])
            S = rechoice(stars, v)
            same = same_span(stars, S)
            if any(len(s) == 0 for s in S):
                res.append({"drop": ch["drop"], "same states": same, "note": "a junction with no distinction"})
                continue
            G = RFK.Start([list(s) for s in S])
            outc = "alive"
            for _ in range(30):
                q = G.step(RFK.fewest, None, None)
                if q != "ok":
                    outc = q
                    break
                if len(G.bits) > 30000:
                    outc = "cap"
                    break
            c = G.counts()
            res.append({"drop": ch["drop"], "same states": same, "smallest junction": min(len(s) for s in S),
                        "counts equal (first 20)": c[:20] == ch["counts"][:20], "class (referee)": RL.classify(c, outc),
                        "class (study)": ch["class"], "counts": c[:12]})
        out.append({"name": r["name"], "choices": res})
    return {"starts": out}


def part_d():
    import networkx as nx
    import referee_f as F
    import referee_nae as RN
    st = RN.load_stages()
    reps = RN.distinct(st)
    R = [st[i] for i in reps]
    K = [RN.nae_table(s["bits"], RN.parity_states(s["bits"], s["stars"])) for s in R]
    buckets = defaultdict(list)
    for i, s in enumerate(R):
        buckets[(s["bits"], F.invariant(K[i]))].append(i)

    def renaming(i, k):
        a, b = R[i], R[k]
        n = a["bits"]
        sa, sb = RN.parity_states(n, a["stars"]), np.sort(RN.parity_states(n, b["stars"]))
        if len(sa) != len(sb):
            return None
        rowA = [sorted(K[i][x]) for x in range(n)]
        rowB = [sorted(K[k][y]) for y in range(n)]
        cand = {x: [y for y in range(n) if rowA[x] == rowB[y]] for x in range(n)}
        own = defaultdict(list)
        for j, S in enumerate(a["stars"]):
            for x in S:
                own[x].append(j)
        sig = {x: tuple(sorted(own[x])) for x in range(n)}
        order = sorted(range(n), key=lambda x: (sig[x], x))   # twins (same holders) together: their images in increasing order
        prev = {order[t]: order[t - 1] for t in range(1, n) if sig[order[t]] == sig[order[t - 1]]}
        img, used = {}, set()

        def go(t):
            if t == n:
                m = np.zeros(len(sa), dtype=np.int64)
                for x, y in img.items():
                    m |= ((sa >> x) & 1) << y
                return bool(np.array_equal(np.sort(m), sb))
            x = order[t]
            for y in cand[x]:
                if y in used or (x in prev and y < img[prev[x]]) or any(K[i][x][z] != K[k][y][w] for z, w in img.items()):
                    continue
                img[x] = y
                used.add(y)
                if go(t + 1):
                    return True
                del img[x]
                used.discard(y)
            return False
        return dict(img) if go(0) else None

    def completed(stars):
        own = defaultdict(list)
        for j, s in enumerate(stars):
            for b in s:
                own[b].append(j)
        G = nx.MultiGraph()
        G.add_nodes_from(list(range(len(stars))) + ["out"])
        for b, js in own.items():
            G.add_edge(js[0], js[1] if len(js) == 2 else "out", key=b)
        return G

    def three_connected(G):
        H = nx.Graph(G)
        V = list(H.nodes)
        if len(V) < 4 or not nx.is_connected(H):
            return False
        for c in itertools.chain(itertools.combinations(V, 1), itertools.combinations(V, 2)):
            Hc = H.copy()
            Hc.remove_nodes_from(c)
            if not nx.is_connected(Hc):
                return False
        return True

    def labelled_iso(Ga, Gb, sigma):
        """A bijection of points under which every line b of Ga goes to the line sigma(b) of Gb."""
        ends_a = {b: (u, v) for u, v, b in Ga.edges(keys=True)}
        ends_b = {b: (u, v) for u, v, b in Gb.edges(keys=True)}
        A = nx.Graph()
        for b, (u, v) in ends_a.items():
            A.add_node(("p", u), k="p")
            A.add_node(("p", v), k="p")
            A.add_node(("l", sigma[b]), k=("l", sigma[b]))
            A.add_edge(("p", u), ("l", sigma[b]))
            A.add_edge(("p", v), ("l", sigma[b]))
        B = nx.Graph()
        for b, (u, v) in ends_b.items():
            B.add_node(("p", u), k="p")
            B.add_node(("p", v), k="p")
            B.add_node(("l", b), k=("l", b))
            B.add_edge(("p", u), ("l", b))
            B.add_edge(("p", v), ("l", b))
        return nx.is_isomorphic(A, B, node_match=nx.algorithms.isomorphism.categorical_node_match("k", None))
    rows = []
    for idx in buckets.values():
        for i, k in itertools.combinations(idx, 2):
            if F.isometric(K[i], K[k]) is None:
                continue
            sig = renaming(i, k)
            if sig is None:
                rows.append({"same states": False})
                continue
            Ga, Gb = completed(R[i]["stars"]), completed(R[k]["stars"])
            rows.append({"same states": True, "three-connected": [three_connected(Ga), three_connected(Gb)],
                         "plain isomorphism": nx.is_isomorphic(Ga, Gb), "isomorphism inducing the renaming": labelled_iso(Ga, Gb, sig),
                         "nx three-connected": [nx.node_connectivity(nx.Graph(Ga)) >= 3 if Ga.number_of_nodes() >= 4 else False,
                                                nx.node_connectivity(nx.Graph(Gb)) >= 3 if Gb.number_of_nodes() >= 4 else False]})
    return {"distinct presentations": len(R), "table collisions": len(rows), "pairs": rows}


def cases():
    import referee_nae as RN
    st = RN.load_stages()
    rows = [{"i": i, "bits": s["bits"], "stars": s["stars"]} for i, s in enumerate(st)]
    for a in range(0, len(rows), 300):
        yield f"B-{a // 300:02d}", {"part": "B", "rows": rows[a:a + 300]}
    yield "D", {"part": "D"}
    keys = []
    for line in open(ROOT / "runs/census-exact5/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok" and r["case"].startswith("census"):
            keys += [a["key"] for a in r["result"]["arrangements"] if len(a["key"][0]) <= 4]
    keys = sorted(keys)
    for a in range(0, len(keys), 100):
        yield f"T-{a // 100:02d}", {"part": "T", "keys": keys[a:a + 100]}
    yield "X", {"part": "X"}
    drows = []
    for line in open(ROOT / "runs/dropped-junction/results.jsonl"):
        r = json.loads(line)
        if r["status"] == "ok":
            drows += r["result"]["starts"]
    eddies = [r for r in drows if not r["name"].startswith("S-")]
    sample = [r for r in drows if r["name"].startswith("S-")][::5]
    for a in range(0, len(eddies), 4):
        yield f"P-e{a // 4:02d}", {"part": "P", "rows": eddies[a:a + 4]}
    for a in range(0, len(sample), 6):
        yield f"P-s{a // 6:02d}", {"part": "P", "rows": sample[a:a + 6]}


def run(case_id, p):
    part = p["part"]
    if part == "B":
        return part_b(p["rows"])
    if part == "D":
        return part_d()
    if part == "T":
        return part_t(p["keys"])
    if part == "X":
        return part_x()
    return part_p(p["rows"])
