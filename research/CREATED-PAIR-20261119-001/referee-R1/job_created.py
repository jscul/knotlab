"""Shared-runner job for the referee's check of CREATED-PAIR-20261119-001 (own growth, own full tables, own isometry enumeration
with no twin quotient and no WL colours; GROW-SMALL's origin.json and the study's literal created pair read as data; no study
code imported or run).

For each of GROW-SMALL's 87 pairs (both directions):
- both stages regrown from their starts by the referee's FIRST-KNOT-R1 engine with the program's rule (an implied junction gets
  exactly d, any other max(d, 3 - p, 1)), each junction tagged with the round it was added in;
- full tables by the referee's CENSUS-READ-R1 shore enumeration (exact: every stage here has at most 22 junctions);
- every isometry of the two full tables by the referee's own backtracking (joint colour refinement on the rows only, then
  forward checking on bit masks; twins are separate distinctions, so every isometry is a leaf), with a cap;
- per isometry: the junctions carried onto junctions, the junction map with round tags, whether the loose distinctions are kept,
  whether the growing end is kept (loose onto loose and every live junction onto a junction), whether the live junctions go onto
  live ones, and (control) whether the equation space is carried;
- separately and exactly, a search constrained to keep the loose distinctions (loose flag in the first colours): its count;
- E0: loose counts and the sizes of loose classes (by holder); the weight counts of both equation spaces;
- for the pairs where some isometry keeps all junctions but some: the unmatched junctions, live or closed, and their distance in
  the junction graph to the nearest live junction.
Part L: the study's literal created pair (junction_maps.py's A and B, read as data) through the same enumeration, so that the
junction maps can be compared label for label.

  .venv/bin/python -B scripts/longrun.py launch research/CREATED-PAIR-20261119-001/referee-R1/job_created.py \\
      --out runs/referee-created --unit referee-created --workers 4 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import json
import sys
from collections import Counter, defaultdict, deque
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/VARIABLE-OUTPUT-READER-20261118-001F/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/CENSUS-READ-20261118-001/referee-R1", "research/PARENT-RULE-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
ORIGIN = ROOT / "artifacts/GROW-SMALL-20261119-001A/GROW-SMALL-20261119-001A-E001_grow/origin.json"
CAP = 3_000_000
# the study's literal created pair (junction_maps.py), read as data
LIT_A = [[0, 1, 8], [0, 2, 3, 9], [2, 4, 10, 11], [4, 5, 12], [5, 6, 13, 14], [1, 6, 7, 15], [3, 7, 16, 17],
         [8, 10, 13, 16, 18, 19, 20], [9, 12, 15, 21], [11, 22, 23], [14, 24, 25], [17, 26, 27]]
LIT_B = [[0, 1, 2], [0, 3, 9, 10], [3, 4, 5, 11], [4, 6, 12, 13], [6, 7, 8, 14], [1, 7, 15, 16], [2, 5, 8, 17],
         [9, 12, 15, 17, 18, 19, 20], [11, 14, 21], [10, 22, 23], [13, 24, 25], [16, 26, 27]]


def floored(G, info, rng):
    return [i["d"] if i["implied"] else max(i["d"], 3 - i["p"], 1) for i in info]


# ---- the arrangement ----

def relabel(stars):
    labels = sorted({b for s in stars for b in s})
    idx = {b: i for i, b in enumerate(labels)}
    return [sorted(idx[b] for b in s) for s in stars], labels


def owners(S):
    own = defaultdict(list)
    for j, s in enumerate(S):
        for x in s:
            own[x].append(j)
    return own


def live(S):
    return sorted({js[0] for js in owners(S).values() if len(js) == 1})


def loose(S):
    return {x for x, js in owners(S).items() if len(js) == 1}


def rank(words):
    basis = {}
    for r in words:
        while r:
            p = r.bit_length() - 1
            if p not in basis:
                basis[p] = r
                break
            r ^= basis[p]
    return len(basis)


def weights(S):
    """Weight counts of the span of the junctions' equations (as subsets of distinctions)."""
    rows = []
    for s in S:
        r = sum(1 << x for x in s)
        for b in rows:
            r = min(r, r ^ b)
        if r:
            rows.append(r)
    c = Counter()
    span = [0]
    for b in rows:
        span += [w ^ b for w in span]
    for w in span:
        c[w.bit_count()] += 1
    return dict(sorted(c.items()))


def jgraph_dist(S, src):
    own = owners(S)
    nb = defaultdict(set)
    for js in own.values():
        if len(js) == 2:
            nb[js[0]].add(js[1])
            nb[js[1]].add(js[0])
    dist = {j: 0 for j in src}
    q = deque(src)
    while q:
        u = q.popleft()
        for v in nb[u]:
            if v not in dist:
                dist[v] = dist[u] + 1
                q.append(v)
    return dist


# ---- isometries, own enumeration ----

def colours(Ks, extra=None):
    """Joint colour refinement of the distinctions of several tables (rows only; 'extra' an optional first colour)."""
    n = len(Ks[0])
    col = [[(tuple(sorted(int(v) for v in K[x])), extra[i][x] if extra else 0) for x in range(n)] for i, K in enumerate(Ks)]
    while True:
        sig = [[(col[i][x], tuple(sorted((int(K[x][y]), col[i][y]) for y in range(n) if y != x))) for x in range(n)]
               for i, K in enumerate(Ks)]
        names = {s: k for k, s in enumerate(sorted({s for row in sig for s in row}))}
        new = [[names[s] for s in row] for row in sig]
        old = len({c for row in col for c in row})
        col = new
        if len({c for row in col for c in row}) == old:
            return col


def isometries(KA, KB, extra=None, cap=CAP):
    """Every bijection x -> y of distinctions with KB[y][y'] == KA[x][x'] (generator of lists), and whether the cap was hit."""
    n = len(KA)
    if len(KB) != n:
        return
    ca, cb = colours([KA, KB], extra)
    if sorted(ca) != sorted(cb):
        return
    vals = sorted({int(v) for v in KA.flatten()} | {int(v) for v in KB.flatten()})
    mask = {v: [sum(1 << w for w in range(n) if int(KB[w][y]) == v) for y in range(n)] for v in vals}
    cand0 = [sum(1 << y for y in range(n) if cb[y] == ca[x]) for x in range(n)]
    phi = [-1] * n
    count = [0]

    def rec(cand, used, todo):
        if not todo:
            count[0] += 1
            yield list(phi)
            return
        x = min(todo, key=lambda z: (cand[z] & ~used).bit_count())
        m = cand[x] & ~used
        rest = [z for z in todo if z != x]
        while m:
            low = m & -m
            y = low.bit_length() - 1
            m ^= low
            nc = cand[:]
            ok = True
            for z in rest:
                nc[z] &= mask[int(KA[z][x])][y]
                if not nc[z] & ~(used | low):
                    ok = False
                    break
            if not ok:
                continue
            phi[x] = y
            yield from rec(nc, used | low, rest)
            phi[x] = -1
            if count[0] >= cap:
                return
    yield from rec(cand0, 0, list(range(n)))


def table(stars):
    import referee_census as RC
    S, labels = relabel(stars)
    return RC.shore_table(S)[0], S, labels


def analyse(A, B, tagsA=None, tagsB=None, detail=False):
    """A, B: junction lists over 0..nb-1 (relabelled), with optional round tags."""
    KA, SA, la = table(A)
    KB, SB, lb = table(B)
    out = {"junctions": [len(SA), len(SB)], "distinctions": [len(la), len(lb)]}
    if len(la) != len(lb) or len(SA) != len(SB):
        out["isometries"] = 0
        return out
    n = len(la)
    LA, LB = loose(SA), loose(SB)
    oa, ob = owners(SA), owners(SB)
    out["E0"] = {"loose": [len(LA), len(LB)],
                 "loose classes": [sorted(Counter(oa[x][0] for x in LA).values()), sorted(Counter(ob[x][0] for x in LB).values())]}
    out["weight counts"] = [weights(SA), weights(SB)]
    out["weight counts equal"] = out["weight counts"][0] == out["weight counts"][1]
    starA = [sum(1 << x for x in s) for s in SA]
    starB = {sum(1 << x for x in s): j for j, s in enumerate(SB)}
    liveA, liveB = live(SA), set(live(SB))
    rb = rank(list(starB))
    jm = Counter()
    c = Counter()
    best = 0
    unmatched = Counter()
    distA = jgraph_dist(SA, liveA)
    n_iso = 0
    moved = Counter()
    for phi in isometries(KA, KB):
        n_iso += 1
        img = [sum(1 << phi[x] for x in s) for s in SA]
        jmap = tuple(starB.get(w) for w in img)
        k = sum(1 for j in jmap if j is not None)
        best = max(best, k)
        c[f"junctions kept {k}"] += 1
        kl = {phi[x] for x in LA} == LB
        c["keeps loose"] += kl
        ke = kl and all(jmap[j] is not None for j in liveA)
        c["keeps growing end"] += ke
        c["live onto live"] += all(jmap[j] is not None and jmap[j] in liveB for j in liveA)
        c["carries states"] += rank(list(starB) + img) == rb and rank(img) == rb
        if detail:
            jm[jmap] += 1
            free = [j for j in range(len(SA)) if jmap[j] is None]
            hit = set(jmap)
            freeB = [j for j in range(len(SB)) if j not in hit]
            if len(free) == 1:
                ia, jb = img[free[0]], sum(1 << x for x in SB[freeB[0]])
                moved[(free[0], freeB[0], tuple(x for x in range(n) if (ia & ~jb) >> x & 1),
                       tuple(x for x in range(n) if (jb & ~ia) >> x & 1))] += 1
        if k == len(SA) - 2:
            for j in range(len(SA)):
                if jmap[j] is None:
                    unmatched[(j in liveA, distA.get(j), kl)] += 1
        if n_iso >= CAP:
            c["capped"] = 1
            break
    out["isometries"] = n_iso
    out["counts"] = dict(c)
    out["most junctions kept"] = best
    out["unmatched at n-2 (live, distance to a live junction, keeps loose)"] = [[list(k), v] for k, v in sorted(unmatched.items(),
                                                                                                             key=str)]
    # exact, separately: isometries constrained to keep the loose distinctions
    ex = [[int(x in LA) for x in range(n)], [int(y in LB) for y in range(n)]]
    out["constrained search: isometries keeping loose"] = sum(1 for _ in isometries(KA, KB, extra=ex))
    if detail:
        out["junction maps"] = [{"map": list(k), "isometries": v,
                                 "tags": [[tagsA[j] if tagsA else None, tagsB[b] if (tagsB and b is not None) else None]
                                          for j, b in enumerate(k)]} for k, v in jm.items()]
        out["moved (A junction, B junction, image minus B's, B's minus image)"] = [[list(map(list, [k[:2], k[2], k[3]])), v]
                                                                                for k, v in moved.items()]
        out["stars"] = [SA, SB]
        out["loose"] = [sorted(LA), sorted(LB)]
    return out


def grow(start, rnd):
    import referee_first as RFK
    G = RFK.Start([list(s) for s in start])
    for _ in range(rnd):
        if G.step(floored, None, None) != "ok":
            return None, None
    return [sorted(b) for b in G.bits], list(G.round)


PARAMS = {}


def setup(params):
    PARAMS.update(params)


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [(f"P-{i:03d}", {"part": "P", "pair": p}) for i, p in enumerate(json.load(open(ORIGIN))["pairs"])]
    allc.append(("L-000", {"part": "L"}))
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "L":
        return {"literal": analyse(LIT_A, LIT_B, [0] * 7 + [1] * 5, [0] * 7 + [1] * 5, detail=True)}
    from job_parent_groups import stars_of
    q = p["pair"]
    created = q["kind"].startswith("created")
    st = []
    for _, gi, ell, rnd in q["starts"]:
        stage, tags = grow(stars_of(gi, ell), rnd)
        st.append((stage, tags))
    if any(s is None for s, _ in st):
        return {"kind": q["kind"], "stage": "growth ended early"}
    (A, ta), (B, tb) = st
    out = {"kind": q["kind"], "starts": q["starts"], "vertices": [len(A) + 1, len(B) + 1]}
    out["A to B"] = analyse(A, B, ta, tb, detail=created)
    out["B to A"] = analyse(B, A, tb, ta, detail=created)
    if created:
        out["rounds of junctions"] = [ta, tb]
    return out
