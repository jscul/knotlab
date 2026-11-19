"""Referee R1 for SCALE-SHARE-20261119-001 (own code; the cluster rule's classifier scale.classify is the object the shares are
read with and is run read-only as such; the study's chains are not run).

  ../../../.venv/bin/python -B referee_scale.py <part> > referee_scale_<part>.json      (from this directory)

The state space S_n: labelled descriptions of n knots, sizes 3 to 5 and pair multiplicities, each knot's shared count at most its
size, connected.  The study's moves: one multiplicity +-1 (probability 0.7, a uniform pair) or one size +-1 (0.3, a uniform knot),
kept when the result is in S_n.

Parts:
  irreducible  exhaustively at n = 3, 4, 5: the multigraphs (sizes all 5) are connected under +-1 multiplicity moves inside S_n;
               with the size moves this makes the whole of S_n one class (argument in the report).  Also |S_n|.
  exact5       the exact labelled shares at n = 5: every census five-knot arrangement weighted by 5!/|Aut| (the referee's own
               brute-force automorphism count), checked to total |S_5|, classified by scale.classify; against the study's eight
               chains (per-chain shares from runs/scale-share), with a z-score from the between-chain spread.
  chains       per chain and n: the stall share and the growers' two-dimensional share, path starts against dense starts, and the
               effective sample size the between-chain spread implies; the P3 rates with standard errors.
  mine         the referee's own Metropolis chains (fresh code, its own random streams) at n = 5, 10, 20, classified by
               scale.classify, against the study's shares.
  spot         one size past the study's spot checks (6 to 12): at n = 10, 12 and 16, non-stalled samples of the referee's own
               chains grown 20 rounds by the referee's own engine (FIRST-KNOT-R1, exact GF(2) implied parity) against the rule's
               counts (clusters.series, read-only), round by round.
"""
import itertools
import json
import math
import os
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / "experiments/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares"
sys.path.insert(0, str(EXP))
import scale as S  # noqa: E402  (the classifier, read-only)

RUN = ROOT / "runs/scale-share/results.jsonl"
CLASSES = ("stall", "closes", "dimension 1", "dimension 2")


def base(c):
    return c.replace(" [break shape]", "")


# ---------------------------------------------------------------- the state space


def multigraphs(n):
    pairs = list(itertools.combinations(range(n), 2))
    deg = [0] * n
    cur = [0] * len(pairs)
    out = []

    def rec(k):
        if k == len(pairs):
            if connected(n, pairs, cur):
                out.append(tuple(cur))
            return
        a, b = pairs[k]
        for m in range(6):
            if deg[a] + m > 5 or deg[b] + m > 5:
                break
            deg[a] += m
            deg[b] += m
            cur[k] = m
            rec(k + 1)
            deg[a] -= m
            deg[b] -= m
        cur[k] = 0
    rec(0)
    return pairs, out


def connected(n, pairs, mult):
    adj = defaultdict(set)
    for (a, b), m in zip(pairs, mult):
        if m:
            adj[a].add(b)
            adj[b].add(a)
    seen, st = {0}, [0]
    while st:
        x = st.pop()
        for y in adj[x]:
            if y not in seen:
                seen.add(y)
                st.append(y)
    return len(seen) == n


def part_irreducible():
    out = {}
    for n in (3, 4, 5):
        pairs, Ms = multigraphs(n)
        idx = {M: i for i, M in enumerate(Ms)}
        parent = list(range(len(Ms)))

        def find(a):
            while parent[a] != a:
                parent[a] = parent[parent[a]]
                a = parent[a]
            return a
        for M in Ms:
            for k in range(len(pairs)):
                for s in (-1, 1):
                    m = M[k] + s
                    if m < 0:
                        continue
                    N = M[:k] + (m,) + M[k + 1:]
                    if N in idx:
                        parent[find(idx[M])] = find(idx[N])
        labelled = sum(math.prod(6 - max(3, sum(M[k] for k, p in enumerate(pairs) if i in p)) for i in range(n)) for M in Ms)
        out[f"n = {n}"] = {"multigraphs": len(Ms), "labelled descriptions |S_n|": labelled,
                           "classes under multiplicity moves (sizes 5)": len({find(i) for i in range(len(Ms))})}
    return out


# ---------------------------------------------------------------- exact five-knot shares


def census5():
    keys = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for a in r["result"]["arrangements"]:
            if len(a["key"][0]) == 5:
                keys.append((tuple(a["key"][0]), tuple(a["key"][1])))
    return keys


def matrix(sizes, flat):
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        M[i][j] = M[j][i] = m
    return M


def aut(sizes, M):
    n = len(sizes)
    return sum(1 for p in itertools.permutations(range(n))
               if all(sizes[p[i]] == sizes[i] for i in range(n)) and all(M[p[i]][p[j]] == M[i][j] for i in range(n) for j in range(n)))


def _cls5(key):
    sizes, flat = key
    M = matrix(sizes, flat)
    return key, math.factorial(5) // aut(sizes, M), base(S.classify(list(sizes), M))


def study_chains():
    per = defaultdict(list)
    for line in open(RUN):
        r = json.loads(line)
        if r.get("status") != "ok" or not r["case"].startswith("S-"):
            continue
        n, c = int(r["case"][3:5]), int(r["case"][-1])
        per[n].append((c, r["result"]["samples"]))
    return per


def part_exact5():
    keys = census5()
    with Pool(int(os.environ.get("WORKERS", "8"))) as pool:
        rows = pool.map(_cls5, keys, chunksize=50)
    tot = sum(w for _, w, _ in rows)
    sh = defaultdict(float)
    for _, w, c in rows:
        sh[c] += w / tot
    chains = sorted(study_chains()[5])
    per = []
    for c, s in chains:
        cnt = Counter(base(x["class"]) for x in s)
        per.append({k: cnt[k] / len(s) for k in CLASSES})
    pooled = {k: sum(p[k] for p in per) / len(per) for k in CLASSES}
    z = {}
    for k in CLASSES:
        v = [p[k] for p in per]
        sd = math.sqrt(sum((x - pooled[k]) ** 2 for x in v) / (len(v) - 1))
        se = sd / math.sqrt(len(v))
        z[k] = {"exact": round(sh[k], 5), "study's pooled": round(pooled[k], 5), "between-chain SE": round(se, 5),
                "z": round((pooled[k] - sh[k]) / se, 2) if se else None,
                "binomial SE if independent": round(math.sqrt(sh[k] * (1 - sh[k]) / 8000), 5)}
    study_ref = {"stall": 0.436, "closes": 0.125, "dimension 1": 0.081, "dimension 2": 0.358}
    chi_exact = sum((pooled[k] * 8000 - sh[k] * 8000) ** 2 / (sh[k] * 8000) for k in CLASSES)
    return {"census five-knot arrangements": len(keys), "labelled total (should be |S_5| = 2,590,792)": tot,
            "exact labelled shares by the rule": {k: round(v, 5) for k, v in sorted(sh.items())},
            "the study's reference shares (merge.py)": study_ref,
            "chi-square of the study's sample against the exact shares (4 classes, as merge.py)": round(chi_exact, 2),
            "per class": z}


# ---------------------------------------------------------------- the study's chains, per chain


def part_chains():
    out = {}
    for n, chains in sorted(study_chains().items()):
        rows = []
        for c, s in sorted(chains):
            cnt = Counter(base(x["class"]) for x in s)
            grow = sum(v for k, v in cnt.items() if k.startswith("dimension") or k.startswith("ring"))
            rows.append({"chain": c, "start": "dense" if c >= 4 else "path", "non-stall": 1 - cnt["stall"] / len(s),
                         "two-dim among growers": cnt["dimension 2"] / grow if grow else None})
        ns = [r["non-stall"] for r in rows]
        m = sum(ns) / len(ns)
        sd = math.sqrt(sum((x - m) ** 2 for x in ns) / (len(ns) - 1))
        se = sd / math.sqrt(len(ns))
        ess = m * (1 - m) / se ** 2 if se else None
        path = [r["non-stall"] for r in rows if r["start"] == "path"]
        dense = [r["non-stall"] for r in rows if r["start"] == "dense"]
        out[n] = {"non-stall per chain": [round(x, 4) for x in ns], "path starts (mean)": round(sum(path) / 4, 4),
                  "dense starts (mean)": round(sum(dense) / 4, 4), "pooled": round(m, 4), "between-chain SE": round(se, 4),
                  "effective sample size (of 8,000)": round(ess) if ess else None,
                  "rate -ln(non-stall)/n": round(-math.log(m) / n, 4),
                  "rate SE": round(se / m / n, 4)}
    r = {n: out[n]["rate -ln(non-stall)/n"] for n in out}
    e = {n: out[n]["rate SE"] for n in out}
    out["P3"] = {"steps 10-12, 12-16, 16-20": [round(r[b] - r[a], 4) for a, b in ((10, 12), (12, 16), (16, 20))],
                 "10 to 20": round(r[20] - r[10], 4), "SE of 10 to 20": round(math.sqrt(e[10] ** 2 + e[20] ** 2), 4)}
    return out


# ---------------------------------------------------------------- the referee's own chains


def is_conn(n, M):
    seen, st = 1, [0]
    while st:
        x = st.pop()
        for y in range(n):
            if M[x][y] and not seen >> y & 1:
                seen |= 1 << y
                st.append(y)
    return seen == (1 << n) - 1


def my_chain(args, keep_states=False):
    """Fresh Metropolis code: the same target (uniform on S_n) and move set, the referee's own stream (seed 'ref-n-k'), a start
    from a star-free random spanning tree, burn-in 400 n^2, thinning 30 n^2 proposals."""
    n, k, N = args
    rng = random.Random(f"ref-{n}-{k}")
    sizes = [5] * n
    M = [[0] * n for _ in range(n)]
    order = list(range(n))
    rng.shuffle(order)
    for t in range(1, n):            # a random tree whose degrees stay within 5: attach to a random earlier vertex of degree < 5
        cand = [order[s] for s in range(t) if sum(M[order[s]]) < 5]
        p = rng.choice(cand)
        M[order[t]][p] = M[p][order[t]] = 1
    pairs = [(i, j) for i in range(n) for j in range(i + 1, n)]
    deg = [sum(r) for r in M]
    out = []
    step = 0
    burn, thin = 400 * n * n, 30 * n * n
    while len(out) < N:
        step += 1
        if rng.random() < 0.7:
            i, j = pairs[rng.randrange(len(pairs))]
            d = 1 if rng.random() < 0.5 else -1
            m = M[i][j] + d
            if m >= 0 and deg[i] + d <= sizes[i] and deg[j] + d <= sizes[j]:
                M[i][j] = M[j][i] = m
                if d == -1 and m == 0 and not is_conn(n, M):
                    M[i][j] = M[j][i] = m + 1
                else:
                    deg[i] += d
                    deg[j] += d
        else:
            i = rng.randrange(n)
            s = sizes[i] + (1 if rng.random() < 0.5 else -1)
            if 3 <= s <= 5 and deg[i] <= s:
                sizes[i] = s
        if step > burn and step % thin == 0:
            c = base(S.classify(list(sizes), [r[:] for r in M]))
            if not keep_states:
                out.append(c)
            elif c != "stall":
                out.append((list(sizes), [r[:] for r in M]))
    return n, k, out


def _spot(args):
    n, k, N = args
    sys.path.insert(0, str(ROOT / "research/CLUSTER-ALL-20261119-001/referee-R1"))
    import referee_cluster as RC
    _, _, states = my_chain((n, k, N), keep_states=True)
    rows = []
    for sizes, M in states:
        sz, e = S.edges_of(sizes, M)
        rows.append(RC.compare((f"n{n} chain {k}", sz, e))["verdict"])
    return n, rows


def part_spot():
    ns = [int(x) for x in os.environ.get("NS", "10,12,16").split(",")]
    N = int(os.environ.get("NSAMP", "300"))
    with Pool(int(os.environ.get("WORKERS", "12"))) as pool:
        res = pool.map(_spot, [(n, 100 + k, N) for n in ns for k in range(4)], chunksize=1)
    out = {}
    for n in ns:
        v = [x for nn, rows in res if nn == n for x in rows]
        out[n] = {"non-stalled samples grown": len(v), "verdicts": dict(Counter(v))}
    return out


def part_mine():
    ns = [int(x) for x in os.environ.get("NS", "5,10,20").split(",")]
    N = int(os.environ.get("NSAMP", "1000"))
    chains = int(os.environ.get("CHAINS", "4"))
    with Pool(int(os.environ.get("WORKERS", "8"))) as pool:
        res = pool.map(my_chain, [(n, k, N) for n in ns for k in range(chains)], chunksize=1)
    study = json.load(open(ROOT / "artifacts/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/results.json"))["shares"]
    out = {}
    for n in ns:
        allc = [c for nn, k, cs in res if nn == n for c in cs]
        cnt = Counter(allc)
        per = [Counter(cs) for nn, k, cs in res if nn == n]
        ns_chain = [1 - p["stall"] / N for p in per]
        m = sum(ns_chain) / len(ns_chain)
        se = math.sqrt(sum((x - m) ** 2 for x in ns_chain) / (len(ns_chain) - 1)) / math.sqrt(len(ns_chain))
        cse = {}
        for c in ("closes", "dimension 1", "dimension 2"):
            v = [p[c] / N for p in per]
            mu = sum(v) / len(v)
            cse[c] = round(math.sqrt(sum((x - mu) ** 2 for x in v) / (len(v) - 1)) / math.sqrt(len(v)), 4)
        out[n] = {"samples": len(allc), "mine": {k: round(v / len(allc), 4) for k, v in sorted(cnt.items())},
                  "my between-chain SE by class": cse,
                  "study's": {k: round(v, 4) for k, v in sorted(study[str(n)]["labelled"].items())},
                  "non-stall: mine, study's, my between-chain SE": [round(m, 4), round(study[str(n)]["non_stall_labelled"], 4), round(se, 4)]}
    return out


if __name__ == "__main__":
    print(json.dumps({"irreducible": part_irreducible, "exact5": part_exact5, "chains": part_chains, "mine": part_mine,
                      "spot": part_spot}[sys.argv[1]](),
                     indent=1, default=str))
