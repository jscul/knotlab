"""Shared-runner job for the referee's check of JUNCTION-KINDS-20261119-001 (own growth, own shares, own kinds, an independent
matcher, own interval types; the starts read from the study's population files as data; no study code imported or run).

For each of the study's 30 starts (T: the ten plastic-number starts; Q: the fifteen y^4 (1 + y)^2 starts; C: the catalogue's five,
with their lags), grown by the referee's engine (complete rounds, fewest counts, GF(2) implication) to the study's rounds or MAXJ
junctions:
- counts, against the study's;
- out-shares s(j) = sum over children c of 1/p(c), p(c) its number of parents; distinct values per round (rounds whose children
  are all grown);
- sum-equitable kinds of depth 6 (kind_0 one class; kind_h(j) the totals of share j sends into each kind_{h-1} class), distinct
  per round;
- T and C: at every round where c(t) = c(t - l1) + c(t - l2) (C: every round past the lags), a maximum matching of round t into
  the ancestors at exact depths l1 and l2 (networkx's Hopcroft-Karp, an independent matcher), and its single-chain version;
- T: interval types (the unfolded parent-chain shape between a junction and its ancestor), and every subset of them (all of them
  when there are at most 10 types) tested for a regular spine: every junction of round t with e typed ancestors and every
  junction of rounds t - l1, t - l2 with e typed descendants, one e for every round tested; on the first half of the recurrent
  rounds, and on all.

  .venv/bin/python -B scripts/longrun.py launch research/JUNCTION-KINDS-20261119-001/referee-R1/job_kinds.py \\
      --out runs/referee-kinds --unit referee-kinds --workers 3 --case-timeout 3600 --case-mem 4G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
MAXJ = 45000
CASES = {}


def setup(params):
    for line in open(ROOT / "runs/junction-kinds/results.jsonl"):
        r = json.loads(line)
        CASES[r["case"]] = r["result"]
    for line in open(ROOT / "runs/junction-kinds/job.json"):
        pass


def cases():
    pop = json.loads((ROOT / "experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks/population.json").read_text())
    cat = json.loads((ROOT / "experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue/catalogue.json").read_text())
    for c in sorted(CASES):
        g = c[0]
        st = cat[int(c[2:])] if g == "C" else pop[int(c[2:])]
        yield c, {"group": g, "start": {"sizes": st["sizes"], "edges": st["edges"]}, "lags": CASES[c]["lags"],
                  "rounds": 40 if g == "C" else 26, "study counts": CASES[c]["counts"]}


def run(case_id, p):
    import networkx as nx
    import referee_first as RFK
    import referee_touch as RT
    st = p["start"]
    n0 = len(st["sizes"])
    M = [[0] * n0 for _ in range(n0)]
    for a, b in st["edges"]:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(st["sizes"], M))
    for _ in range(p["rounds"]):
        if G.step(RFK.fewest, None, None) != "ok" or len(G.bits) > MAXJ:
            break
    T = G.rounds
    c = G.counts()
    n = len(G.bits)
    par = [sorted(G.parents[j]) if G.round[j] > 0 else [] for j in range(n)]
    ch = [[] for _ in range(n)]
    for j in range(n):
        for q in par[j]:
            ch[q].append(j)
    br = defaultdict(list)
    for j in range(n):
        br[G.round[j]].append(j)
    out = {"counts equal to the study's": c == p["study counts"][:len(c)], "rounds": T}
    s = [sum((Fraction(1, len(par[x])) for x in ch[j]), Fraction(0)) for j in range(n)]
    out["out-shares (distinct per round)"] = [len({s[j] for j in br[t]}) for t in range(1, T)]
    kind = [0] * n
    tab = {}
    for h in range(1, 7):
        new = []
        for j in range(n):
            if G.round[j] + h <= T:
                tot = defaultdict(Fraction)
                for x in ch[j]:
                    tot[kind[x]] += Fraction(1, len(par[x]))
                new.append(tab.setdefault((h, tuple(sorted(tot.items()))), len(tab)))
            else:
                new.append(-1)
        kind = new
    out["kinds of depth 6 (distinct per round)"] = [len({kind[j] for j in br[t]}) for t in range(1, T - 6 + 1)]
    if p["group"] == "Q":
        return out
    l1, l2 = p["lags"]

    def anc(j, k):
        cur = Counter({j: 1})
        for _ in range(k):
            nxt = Counter()
            for x, m in cur.items():
                for q in par[x]:
                    nxt[q] += m
            cur = nxt
        return cur
    rounds = list(range(l2 + 1, T + 1)) if p["group"] == "C" else [t for t in range(l2 + 1, T + 1) if c[t] == c[t - l1] + c[t - l2]]
    hall = []
    for t in rounds:
        res = {}
        for single in (False, True):
            B = nx.Graph()
            left = [("L", j) for j in br[t]]
            right = [("R", l, a) for l in (l1, l2) for a in br[t - l]]
            B.add_nodes_from(left, bipartite=0)
            B.add_nodes_from(right, bipartite=1)
            for j in br[t]:
                for l in (l1, l2):
                    for a, m in anc(j, l).items():
                        if not single or m == 1:
                            B.add_edge(("L", j), ("R", l, a))
            mt = nx.algorithms.bipartite.hopcroft_karp_matching(B, top_nodes=left)
            size = sum(1 for u in left if u in mt)
            res["single" if single else "all"] = size
            if not single:
                ok = all(mt[u][0] == "R" and u in B[mt[u]] for u in left if u in mt)
                res["matching valid"] = ok and len({mt[u] for u in left if u in mt}) == size
        hall.append({"t": t, "left": len(br[t]), "right": len(br[t - l1]) + len(br[t - l2]), **res})
    out["recurrence rounds"] = rounds
    out["matchings"] = hall
    if p["group"] != "T" or len(rounds) < 4:
        return out
    memo = {}

    def itype(j, a, k):
        key = (j, a, k)
        if key not in memo:
            if k == 0:
                memo[key] = ()
            else:
                memo[key] = tuple(sorted(itype(q, a, k - 1) for q in par[j] if a in anc_cache(q, k - 1)))
        return memo[key]
    acache = {}

    def anc_cache(j, k):
        if (j, k) not in acache:
            acache[(j, k)] = anc(j, k)
        return acache[(j, k)]
    rel = {}
    for t in rounds:
        rel[t] = [(j, l, a, (l, itype(j, a, l))) for j in br[t] for l in (l1, l2) for a in anc_cache(j, l)]
    freq = Counter(ty for t in rounds for *_, ty in rel[t])
    types = [ty for ty, _ in freq.most_common()]
    pool = types if len(types) <= 10 else types[:10]
    maxs = len(pool) if len(types) <= 10 else 4

    def regular(Ts, rr):
        es = set()
        for t in rr:
            dl, dr = Counter(), Counter()
            for j, l, a, ty in rel[t]:
                if ty in Ts:
                    dl[j] += 1
                    dr[(l, a)] += 1
            es |= {dl.get(j, 0) for j in br[t]} | {dr.get((l, a), 0) for l in (l1, l2) for a in br[t - l]}
            if len(es) != 1 or 0 in es:
                return False
        return True
    half = rounds[:len(rounds) // 2]
    good_half = [T_ for size in range(1, maxs + 1) for T_ in itertools.combinations(pool, size) if regular(set(T_), half)]
    out["types"] = len(types)
    out["subsets tested"] = sum(1 for size in range(1, maxs + 1) for _ in itertools.combinations(pool, size))
    out["regular on the first half"] = len(good_half)
    out["regular on all rounds"] = sum(1 for T_ in good_half if regular(set(T_), rounds))
    return out
