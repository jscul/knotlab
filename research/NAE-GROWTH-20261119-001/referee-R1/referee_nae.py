"""Referee R1 for NAE-GROWTH-20261119-001 (own code; the study's naelib, bondlib, job, merge and posthoc_b are not imported or
run; part B's stages are read from runs/nae-growth as data).

  ../../../.venv/bin/python -B referee_nae.py <part> > referee_nae_<part>.json      (from this directory)

Parts:
  lemma    T2's lemma in the form T2 uses it, by brute force: every connected multigraph (parallel lines allowed, pendant lines as
           lines to points of degree one) on up to 5 points and 7 lines that is not an odd cycle has a 2-colouring of its lines with
           both colours at every point of degree at least two; and T2's conclusion itself on random junction systems.
  partb    part B recomputed: distinct presentations; the parity tables by the referee's own shore enumeration (all stages) and the
           not-all-equal tables by its own brute force over minimal non-free sets (a sample), against the recorded ones; the
           collisions under each law by an exact table isometry (the twin quotient of the referee's 001F code); for every
           collision, the same-states question decided exactly (a search over all table isometries, modulo the permutations of
           distinctions held by the same junctions, which keep the states); redundant junctions; next joins.
  growth   the cheapest growth under both laws with the referee's own engine (FRESH-COUNT-R1 / FIRST-KNOT-R1), not-all-equal's
           implication tested by a different SAT solver (Glucose 4, all-0 and all-1 assumptions): a random 3,000 of the census and
           1,000 six-knot arrangements (one size past the census).
"""
import itertools
import json
import os
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

import networkx as nx
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1"))
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
import referee_f as F  # noqa: E402
INF = F.INF
RUN = ROOT / "runs/nae-growth/results.jsonl"


# ---------------------------------------------------------------- the lemma


def colourable(npts, lines):
    """Is there a 0/1 colouring of the lines with both colours at every point of degree >= 2?"""
    deg = Counter(p for l in lines for p in l)
    need = [p for p in range(npts) if deg[p] >= 2]
    for c in range(1 << len(lines)):
        seen = defaultdict(set)
        for k, (a, b) in enumerate(lines):
            v = c >> k & 1
            seen[a].add(v)
            seen[b].add(v)
        if all(len(seen[p]) == 2 for p in need):
            return True
    return False


def is_odd_cycle(npts, lines):
    deg = Counter(p for l in lines for p in l)
    return len(lines) == npts and npts % 2 == 1 and all(deg[p] == 2 for p in range(npts))


def conn(npts, lines):
    adj = defaultdict(set)
    for a, b in lines:
        adj[a].add(b)
        adj[b].add(a)
    seen, st = {0}, [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == npts


def part_lemma():
    out = {}
    for npts in range(1, 6):
        pairs = list(itertools.combinations(range(npts), 2))
        tested = fails = odd = 0
        for m in range(0, 8):
            for lines in itertools.combinations_with_replacement(pairs, m):
                if not conn(npts, list(lines)) or (npts > 1 and not lines):
                    continue
                tested += 1
                if is_odd_cycle(npts, list(lines)):
                    odd += 1
                    fails += colourable(npts, list(lines))      # an odd cycle should NOT be colourable
                    continue
                fails += not colourable(npts, list(lines))
        out[f"{npts} points"] = {"connected multigraphs, up to 7 lines": tested, "odd cycles among them": odd,
                                 "exceptions to the lemma (incl. a colourable odd cycle)": fails}
    # T2's conclusion on random junction systems: every distinction in at most two junctions, every junction >= 3 places; a set X
    # of loose distinctions, at most one per junction, leaving every junction >= 2 places: some NAE state has X all equal.
    rng = random.Random(7)
    tried = bad = 0
    sharp = strong_bad = 0
    strong = Counter()
    for _ in range(3000):
        nj = rng.randint(2, 6)
        sizes = [rng.randint(3, 5) for _ in range(nj)]
        stars = [[] for _ in range(nj)]
        b = 0
        free = [list(range(s)) for s in sizes]           # places still unassigned
        slots = [(j, k) for j in range(nj) for k in range(sizes[j])]
        rng.shuffle(slots)
        used = set()
        for (j, k) in slots:
            if (j, k) in used:
                continue
            used.add((j, k))
            partners = [(j2, k2) for (j2, k2) in slots if j2 != j and (j2, k2) not in used]
            if partners and rng.random() < 0.5:
                j2, k2 = rng.choice(partners)
                used.add((j2, k2))
                stars[j].append(b)
                stars[j2].append(b)
            else:
                stars[j].append(b)
            b += 1
        n = b
        if n > 16:
            continue
        S = nae_states(n, stars)
        own = defaultdict(list)
        for j, s in enumerate(stars):
            for x in s:
                own[x].append(j)
        loose = defaultdict(list)
        for x, js in own.items():
            if len(js) == 1:
                loose[js[0]].append(x)
        holders = [j for j in loose]
        for r in range(1, min(3, len(holders)) + 1):
            for P in itertools.combinations(holders, r):
                X = [loose[j][0] for j in P]
                tried += 1
                mask = sum(1 << x for x in X)
                ok = bool(np.any((S & mask) == 0) or np.any((S & mask) == mask))
                bad += not ok
        # the stronger form (G5): any set X leaving every junction at least two places is free (all patterns on X); sharpness:
        # sets leaving some junction exactly one place
        for _ in range(12):
            X = [x for x in range(n) if rng.random() < 0.35]
            if not X:
                continue
            keep = min(len(st_) - len(set(st_) & set(X)) for st_ in stars)
            proj = np.zeros(len(S), dtype=np.int64)
            for i, x in enumerate(X):
                proj |= ((S >> x) & 1) << i
            free_ = np.count_nonzero(np.bincount(proj, minlength=1 << len(X))) == 1 << len(X)
            strong[keep >= 2] += 1
            if keep >= 2 and not free_:
                strong_bad += 1
            if keep == 1 and not free_:
                sharp += 1
    out["T2 on random junction systems"] = {"sets tested (one loose distinction from each of 1 to 3 junctions)": tried,
                                            "implied (should be 0)": bad,
                                            "stronger form: random sets leaving every junction two places, tested": strong[True],
                                            "... not free (should be 0)": strong_bad,
                                            "sets leaving some junction one place, tested": strong[False],
                                            "... not free (the form is sharp if > 0)": sharp}
    return out


# ---------------------------------------------------------------- states, tables


def nae_states(n, stars):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for S in stars:
        m = sum(1 << b for b in S)
        v = s & m
        ok &= (v != 0) & (v != m)
    return s[ok]


def parity_states(n, stars):
    s = np.arange(1 << n, dtype=np.int64)
    ok = np.ones(1 << n, dtype=bool)
    for S in stars:
        c = np.zeros(1 << n, dtype=np.int64)
        for b in S:
            c ^= (s >> b) & 1
        ok &= c == 0
    return s[ok]


def nae_table(n, st):
    """K matrix (least minimal non-free set through each pair) by the referee's own search: sets by size, a set tested only when
    no smaller non-free set lies inside it."""
    K = np.full((n, n), INF, dtype=np.int64)
    np.fill_diagonal(K, 0)
    nonfree = []
    for k in range(1, n + 1):
        for comb in itertools.combinations(range(n), k):
            m = sum(1 << b for b in comb)
            if any(f & m == f for f in nonfree):
                continue
            proj = np.zeros(len(st), dtype=np.int64)
            for i, b in enumerate(comb):
                proj |= ((st >> b) & 1) << i
            if np.count_nonzero(np.bincount(proj, minlength=1 << k)) < (1 << k):
                nonfree.append(m)
                for x, y in itertools.combinations(comb, 2):
                    if K[x][y] > k:
                        K[x][y] = K[y][x] = k
    return K


def parity_table(stars, n):
    return F.bond_table(stars, n)[0]


def recorded_K(rec, n):
    """The study's table (D, 0 = in no bond) as a K matrix."""
    K = np.full((n, n), INF, dtype=np.int64)
    np.fill_diagonal(K, 0)
    for (x, y), d in zip(itertools.combinations(range(n), 2), rec):
        K[x][y] = K[y][x] = INF if d == 0 else d + 1
    return K


# ---------------------------------------------------------------- presentations


def inc_graph(stars):
    G = nx.Graph()
    for j, s in enumerate(stars):
        G.add_node(("j", j), kind="j")
        for b in s:
            G.add_node(("b", b), kind="b")
            G.add_edge(("j", j), ("b", b))
    return G


NM = nx.algorithms.isomorphism.categorical_node_match("kind", None)


def join_graph(stars, parents):
    G = inc_graph(stars)
    for i, ps in enumerate(parents):
        G.add_node(("n", i), kind="n")
        for j in ps:
            G.add_edge(("n", i), ("j", j))
    return G


def load_stages():
    st = []
    for line in open(RUN):
        r = json.loads(line)
        if r.get("status") != "ok" or not r["case"].startswith("B-"):
            continue
        for a in r["result"]["arrangements"]:
            for s in a["stages"]:
                st.append({"key": a["key"], "round": s["round"], "stars": s["stars"], "bits": s["bits"],
                           "next": s["next_parents"], "rec": {law: s[law]["table"] for law in ("parity", "nae")},
                           "rec_red": {law: s[law]["redundant"] for law in ("parity", "nae")}})
    return st


def distinct(st):
    reps, by = [], defaultdict(list)
    for i, s in enumerate(st):
        G = inc_graph(s["stars"])
        h = (s["bits"], len(s["stars"]), nx.weisfeiler_lehman_graph_hash(G, node_attr="kind"))
        if any(nx.is_isomorphic(G, st[k]["_g"], node_match=NM) for k in by[h]):
            continue
        s["_g"] = G
        by[h].append(i)
        reps.append(i)
    return reps


def same_states(sa, starsA, sb, KA, KB, n, cap=None):
    """Exact: is there a bijection of distinctions, preserving the tables (every state-preserving bijection does), carrying the
    states sa onto sb?  Searched over all table isometries, with the images of distinctions held by the same junctions in A taken
    in increasing order (permuting such distinctions keeps A's stars, hence its states)."""
    if len(sa) != len(sb):
        return False, 0
    sbs = np.sort(sb)
    own = defaultdict(list)
    for j, s in enumerate(starsA):
        for b in s:
            own[b].append(j)
    sig = {b: tuple(sorted(own[b])) for b in range(n)}
    order = sorted(range(n), key=lambda b: (sig[b], b))
    prev = {}
    for i in range(1, n):
        if sig[order[i]] == sig[order[i - 1]]:
            prev[order[i]] = order[i - 1]
    rowA = [sorted(KA[x]) for x in range(n)]
    rowB = [sorted(KB[y]) for y in range(n)]
    cand = {x: [y for y in range(n) if rowA[x] == rowB[y]] for x in range(n)}
    img = {}
    used = set()
    leaves = [0]

    def go(k):
        if k == n:
            leaves[0] += 1
            m = np.zeros(len(sa), dtype=np.int64)
            for x, y in img.items():
                m |= ((sa >> x) & 1) << y
            return bool(np.array_equal(np.sort(m), sbs))
        x = order[k]
        for y in cand[x]:
            if y in used:
                continue
            if x in prev and y < img[prev[x]]:
                continue
            if any(KA[x][z] != KB[y][w] for z, w in img.items()):
                continue
            img[x] = y
            used.add(y)
            if go(k + 1):
                return True
            del img[x]
            used.discard(y)
        return False
    return go(0), leaves[0]


def redundant(n, stars, law):
    f = parity_states if law == "parity" else nae_states
    full = len(f(n, stars))
    return sum(len(f(n, stars[:j] + stars[j + 1:])) == full for j in range(len(stars)))


def _tables(args):
    """Both tables by the referee's brute force over minimal non-free sets of the allowed states, on every presentation; the parity
    table also by its shore enumeration where a loose distinction exists (the shore method needs the exterior)."""
    i, s, _ = args
    n = s["bits"]
    Kp = nae_table(n, parity_states(n, s["stars"]))
    Kn = nae_table(n, nae_states(n, s["stars"]))
    owners = Counter(b for S in s["stars"] for b in S)
    has_loose = any(c == 1 for c in owners.values())
    out = {"i": i, "parity agrees": bool((Kp == recorded_K(s["rec"]["parity"], n)).all()),
           "nae agrees": bool((Kn == recorded_K(s["rec"]["nae"], n)).all()), "has loose": has_loose,
           "shore agrees": bool((parity_table(s["stars"], n) == Kp).all()) if has_loose else None}
    return out, (Kp, Kn)


def _collision(args):
    a, b, law, KA, KB = args
    n = a["bits"]
    f = parity_states if law == "parity" else nae_states
    ss, leaves = same_states(f(n, a["stars"]), a["stars"], f(n, b["stars"]), KA, KB, n)
    red = redundant(n, a["stars"], law) > 0 or redundant(n, b["stars"], law) > 0
    sj = nx.is_isomorphic(join_graph(a["stars"], a["next"]), join_graph(b["stars"], b["next"]), node_match=NM)
    return {"a": [a["key"], a["round"]], "b": [b["key"], b["round"]], "same states": ss, "leaves searched": leaves,
            "redundant": red, "same next joins": sj, "bits": n}


def part_partb():
    st = load_stages()
    reps = distinct(st)
    R = [{k: v for k, v in st[i].items() if k != "_g"} for i in reps]
    W = int(os.environ.get("WORKERS", "10"))
    with Pool(W) as pool:
        res = pool.map(_tables, [(i, R[i], None) for i in range(len(R))], chunksize=8)
    Ks = {r["i"]: k for r, k in res}
    out = {"stages": len(st), "distinct presentations": len(R),
           "parity tables (brute force) equal to the recorded ones": sum(r["parity agrees"] for r, _ in res),
           "not-all-equal tables (brute force) equal to the recorded ones": sum(r["nae agrees"] for r, _ in res),
           "presentations with a loose distinction": sum(r["has loose"] for r, _ in res),
           "... shore enumeration equal to the brute force": sum(bool(r["shore agrees"]) for r, _ in res)}
    for law in ("nae", "parity"):
        K = {i: Ks[i][0 if law == "parity" else 1] for i in range(len(R))}
        buckets = defaultdict(list)
        for i in range(len(R)):
            buckets[(R[i]["bits"], F.invariant(K[i]))].append(i)
        pairs = []
        for idx in buckets.values():
            for i, k in itertools.combinations(idx, 2):
                if F.isometric(K[i], K[k]) is not None:
                    pairs.append((i, k))
        with Pool(W) as pool:
            rows = pool.map(_collision, [(R[i], R[k], law, K[i], K[k]) for i, k in pairs], chunksize=1)
        inv = {x for p in pairs for x in p}
        kinds = Counter((("same states" if r["same states"] else "different states"),
                         ("redundant junction" if r["redundant"] else "no redundant junction"),
                         ("same next joins" if r["same next joins"] else "different next joins")) for r in rows)
        out[law] = {"collisions": len(pairs), "presentations in a collision": len(inv),
                    "presentations with a table no other shares": len(R) - len(inv),
                    "share unique": round((len(R) - len(inv)) / len(R), 4),
                    "kinds": {" / ".join(k): v for k, v in sorted(kinds.items())},
                    "largest isometry search (leaves)": max((r["leaves searched"] for r in rows), default=0),
                    "different-states examples": [r for r in rows if not r["same states"]][:3]}
    return out


# ---------------------------------------------------------------- growth under both laws


def nae_fewest(G, info, rng):
    from pysat.solvers import Glucose4
    if not info:
        return []
    first = min(i["j"] for i in info)
    s = Glucose4()
    for j in range(first):
        bits = G.bits[j]
        s.add_clause([b + 1 for b in bits])
        s.add_clause([-(b + 1) for b in bits])
    try:
        for i in info:
            old = G.bits[i["j"]]
            a0 = s.solve(assumptions=[-(b + 1) for b in old])
            a1 = s.solve(assumptions=[b + 1 for b in old])
            i["implied"] = not a0 and not a1
            if i["implied"]:
                G.nae_implied = getattr(G, "nae_implied", 0) + 1
    finally:
        s.delete()
    return [0 if (i["implied"] and i["d"] == 0) else max(i["d"], 3 - i["p"], 1) for i in info]


def grow(sizes, edges, law, rounds=14, maxj=3000):
    import referee_cluster as RC
    import referee_first as RFK
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RC.RT.stars(sizes, M))
    out = "alive"
    implied_parity = []
    for _ in range(rounds):
        if law == "parity":
            r = G.step(lambda G_, info, rng: (implied_parity.extend((G_.rounds, i["p"], i["d"]) for i in info if i["implied"]),
                                             RFK.fewest(G_, info, rng))[1], None, None)
        else:
            r = G.step(nae_fewest, None, None)
        if r != "ok":
            out = r
            break
        if len(G.bits) > maxj:
            out = "cap"
            break
    return G.counts(), out, implied_parity, getattr(G, "nae_implied", 0)


def _both(item):
    name, sizes, edges = item
    cp, op, imp, _ = grow(sizes, edges, "parity")
    cn, on, _, nimp = grow(sizes, edges, "nae")
    row = {"case": name, "parity": [op, len(cp) - 1], "nae": [on, len(cn) - 1], "nae implied": nimp}
    if not imp:
        row["verdict"] = "identical" if (cp == cn and op == on) else "differs"
    elif len(imp) == 1 and op == "closed" and imp[0][0] == len(cp) - 1 and imp[0][2] == 0:
        T = len(cp) - 1
        first = 1 if imp[0][1] >= 2 else 2
        want = [first + k for k in range(len(cn) - T - 1)]
        row["verdict"] = "relay as predicted" if (cn[:T + 1] == cp and cn[T + 1:] == want and on in ("alive", "cap")) else "relay differs"
        row["tail"] = cn[T + 1:T + 6]
    else:
        row["verdict"] = "parity implied elsewhere"
    return row


def part_growth():
    import referee_cluster as RC
    keys = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for a in r["result"]["arrangements"]:
            keys.append((tuple(a["key"][0]), tuple(a["key"][1])))
    rng = random.Random(23)
    pick = rng.sample(keys, int(os.environ.get("NCENSUS", "3000")))
    items = [(f"census {list(a)} {list(b)}", *RC.edges_of((a, b))) for a, b in pick]
    items += [(f"six seed {80000 + k}", *RC.six(80000 + k)) for k in range(int(os.environ.get("NSIX", "1000")))]
    with Pool(int(os.environ.get("WORKERS", "10"))) as pool:
        rows = pool.map(_both, items, chunksize=4)
    out = {}
    for grp in ("census", "six"):
        rs = [r for r in rows if r["case"].startswith(grp)]
        out[grp] = {"starts": len(rs), "verdicts": dict(Counter(r["verdict"] for r in rs)),
                    "not-all-equal junctions implied": sum(r["nae implied"] for r in rs),
                    "relay tails (first five rounds)": dict(Counter(str(r.get("tail")) for r in rs if "tail" in r).most_common(4)),
                    "others": [r for r in rs if r["verdict"] not in ("identical", "relay as predicted")][:5]}
    return out


if __name__ == "__main__":
    print(json.dumps({"lemma": part_lemma, "partb": part_partb, "growth": part_growth}[sys.argv[1]](), indent=1, default=str))
