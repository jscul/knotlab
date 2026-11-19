"""Shared-runner job for the referee's check of WEIGHTINGS-20261119-001.

Own code throughout, except the study's samplers (weightlib.sample), which are run as the object under test and to regenerate the
study's own samples (same seeds as job.py); the study's per-sample records (runs/weightings) are read as data.  No study reader or
growth code is run.

Parts:
- W (one case per weighting and size): regenerate the 2,000 samples; the referee's own bare sizes (every knot given one open
  distinction, round-1 groups by the referee's engine, max(3, shared + demand)) against the sampled sizes (tree, tree+: equal;
  tree-sP: equal or one more); the referee's class and X+ reading (DOUBLE-IDENT-R1) against the study's record; regrowth of every
  in-class start read as three-or-more dimensional or exponential, and one in sixteen other in-class growers (crc32), the
  referee's growth against its relayed model, keys per round to 6.
- C: the configuration sampler at n = 3 and 4, 200,000 draws each, against the exact weights of labelled descriptions
  (1/3)^n * prod (s_i)_(deg_i) / prod m_ij!, over every connected description with no self-line.
- T: the tree sampler at n = 5 and 6 against the uniform law on labelled trees.
- H: the dead-hub start of posthoc.py: class, reading, regrowth against the relayed model to round 6, growth to round 25 and its
  exact minimal recurrence.
- L: the five-place lemma on every unlabelled tree of 3 to 18 knots (the study: 3 to 14): bare sizes, reading, and the lemma's
  steps (five places => no knot touches three non-leaves => a caterpillar => at most two leaves beside a knot of degree 2).

  .venv/bin/python -B scripts/longrun.py launch research/WEIGHTINGS-20261119-001/referee-R1/job_weight.py \\
      --out runs/referee-weightings --unit referee-weightings --workers 4 --case-timeout 7200 --case-mem 3G --mem-max 16G
"""
import importlib.util
import itertools
import json
import math
import random
import sys
import zlib
from collections import Counter
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/DOUBLE-IDENT-20261119-001/referee-R1", "research/RELAY-IDENT-20261119-001/referee-R1",
          "research/CHAIN-IDENT-20261119-001/referee-R1", "research/RING-IDENT-20261119-001/referee-R1",
          "research/FIRST-KNOT-20261118-001/referee-R1", "research/TOUCH-CENSUS-20261118-001/referee-R1",
          "research/BREAK-EDDIES-20261119-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
KINDS = ('tree', 'tree-s25', 'tree-s50', 'tree-s100', 'tree+', 'grow', 'config')
SIZES = (5, 6, 7, 8, 10, 12, 16, 20)
T = 6
PARAMS = {}


def setup(params):
    PARAMS.update(params)


def sampler():
    spec = importlib.util.spec_from_file_location(
        "w_sampler", ROOT / "experiments/WEIGHTINGS-20261119-001B/WEIGHTINGS-20261119-001B-E001_weights/weightlib.py")
    mod = importlib.util.module_from_spec(spec)
    sys.modules["w_sampler"] = mod
    spec.loader.exec_module(mod)
    return mod.sample                     # the object under test; nothing else of it is called


def flat_of(n, edges):
    c = Counter(tuple(sorted(e)) for e in edges)
    return [c[(a, b)] for a, b in itertools.combinations(range(n), 2)]


def my_bare(n, flat):
    import job_double as JD
    sh = Counter()
    for (a, b), m in zip(itertools.combinations(range(n), 2), flat):
        sh[a] += m
        sh[b] += m
    _, _, _, _, _, groups, d = JD.data([sh[k] + 1 for k in range(n)], flat)
    return [max(3, sh[k] + d[k]) for k in range(n)]


def read(sizes, flat):
    import job_double as JD
    c = JD.classify(sizes, flat)
    if c in ("in", "one loose", "none"):
        return c, str(JD.predict(JD.build(sizes, flat, 2)))
    return c, None


def regrow(sizes, flat):
    import job_double as JD
    import job_relay as RL
    n = len(sizes)
    X = JD.build(sizes, flat, T + 3)
    a, counts = RL.grow_keys(n, X["edges"], list(sizes), T)
    b = RL.relayed_keys(n, X, T + 1)
    bad = [t for t in range(T + 1) if {k: Fraction(v) for k, v in a.get(t, {}).items()} != {k: v for k, v in b.get(t, {}).items() if v}]
    return not bad, bad, counts


LABEL = {"0": "closes", "exp": "exponential"}


def part_w(kind, n):
    sample = sampler()
    cid = f"{kind}-n{n:02d}"
    rec = None
    for line in open(ROOT / "runs/weightings/results.jsonl"):
        r = json.loads(line)
        if r["case"] == cid:
            rec = r["result"]["samples"]
    rng = random.Random(f"weightings-{cid}")
    s = Counter()
    rows = []
    for i in range(2000):
        sizes, e = sample(kind, n, rng)
        flat = flat_of(n, e)
        if kind.startswith("tree"):
            mb = my_bare(n, flat)
            diff = [a - b for a, b in zip(sizes, mb)]
            s["bare sizes as stated"] += all(x == 0 for x in diff) if kind in ("tree", "tree+") else all(x in (0, 1) for x in diff)
        c, D = read(sizes, flat)
        lab = None if D is None else LABEL.get(D, f"dimension {D}")
        x = rec[i]
        mine = "out" if c.startswith("out") else c
        s["class equals the record"] += mine == x["cls"]
        s["reading equals the record"] += lab == x.get("growth")
        s["largest knot equals the record"] += max(sizes) == x["max_places"]
        hard = D == "exp" or (D not in (None, "0") and D != "exp" and int(D) >= 3)
        if c == "in" and D != "0":
            s["in-class growers"] += 1
            if max(sizes) <= 5:
                s["in-class growers, knots of at most five places"] += 1
                s["... of which three-or-more or exponential"] += hard
            pick = hard or zlib.crc32(f"{cid}-{i}".encode()) % 16 == 0
            if pick:
                ok, bad, counts = regrow(sizes, flat)
                key = "hard" if hard else "other"
                s[f"regrown {key}"] += 1
                s[f"regrown {key}, agree to round 6"] += ok
                if not ok:
                    rows.append({"i": i, "sizes": sizes, "flat": flat, "reading": lab, "rounds that differ": bad})
                if hard:
                    s[f"regrown hard: {lab}"] += 1
    return {"counts": dict(s), "disagreements": rows}


def exact_config(n):
    """Exact law of the configuration sampler's labelled descriptions: sizes uniform in {3,4,5}^n, a uniform partial matching of
    the places, conditioned on no self-line and connected."""
    pairs = list(itertools.combinations(range(n), 2))
    law = {}
    for sizes in itertools.product((3, 4, 5), repeat=n):
        for flat in itertools.product(range(6), repeat=len(pairs)):
            deg = Counter()
            for (a, b), m in zip(pairs, flat):
                deg[a] += m
                deg[b] += m
            if any(deg[k] > sizes[k] for k in range(n)):
                continue
            seen, st = {0}, [0]
            while st:
                u = st.pop()
                for (a, b), m in zip(pairs, flat):
                    if m and u in (a, b):
                        v = b if u == a else a
                        if v not in seen:
                            seen.add(v)
                            st.append(v)
            if len(seen) < n:
                continue
            w = Fraction(1, 3 ** n)
            for k in range(n):
                w *= math.perm(sizes[k], deg[k])
            for m in flat:
                w /= math.factorial(m)
            # a uniform partial matching: every matching has weight 1 / (number of partial matchings of the places)
            N = sum(sizes)
            total = sum(Fraction(math.factorial(N), math.factorial(N - 2 * m) * math.factorial(m) * 2 ** m) for m in range(N // 2 + 1))
            law[(sizes, flat)] = w / total
    Z = sum(law.values())
    return {k: v / Z for k, v in law.items()}


def part_c(n, draws=200000):
    sample = sampler()
    law = exact_config(n)
    rng = random.Random(f"referee-config-{n}")
    obs = Counter()
    for _ in range(draws):
        sizes, e = sample("config", n, rng)
        obs[(tuple(sizes), tuple(flat_of(n, e)))] += 1
    outside = sum(v for k, v in obs.items() if k not in law)
    chi2 = float(sum((obs.get(k, 0) - draws * float(p)) ** 2 / (draws * float(p)) for k, p in law.items()))
    tv = sum(abs(obs.get(k, 0) / draws - float(p)) for k, p in law.items()) / 2
    # the line-count law, exact against observed
    lines = Counter()
    for k, p in law.items():
        lines[sum(k[1])] += p
    obs_lines = Counter()
    for k, v in obs.items():
        obs_lines[sum(k[1])] += v
    return {"descriptions": len(law), "draws": draws, "draws outside the support": outside, "chi2": round(chi2, 1),
            "degrees of freedom": len(law) - 1, "total variation": round(tv, 4),
            "lines: exact / observed": {m: [round(float(p), 5), round(obs_lines[m] / draws, 5)] for m, p in sorted(lines.items())}}


def part_t(n, draws):
    sample = sampler()
    rng = random.Random(f"referee-tree-{n}")
    obs = Counter()
    for _ in range(draws):
        sizes, e = sample("tree", n, rng)
        obs[tuple(sorted(tuple(sorted(x)) for x in e))] += 1
    K = n ** (n - 2)
    exp = draws / K
    chi2 = sum((v - exp) ** 2 / exp for v in obs.values()) + (K - len(obs)) * exp
    return {"labelled trees": K, "seen": len(obs), "draws": draws, "chi2": round(chi2, 1), "degrees of freedom": K - 1}


def part_h():
    import job_double as JD
    import job_relay as RL
    import break_readout as BR
    e = [(0, 1), (0, 2), (0, 3), (1, 4), (2, 5), (3, 6), (4, 7), (5, 8), (6, 9)]
    sizes = [3, 5, 5, 5, 3, 3, 3, 3, 3, 3]
    n = len(sizes)
    flat = flat_of(n, e)
    c, D = read(sizes, flat)
    ok, bad, _ = regrow(sizes, flat)
    _, counts = RL.grow_keys(n, JD.data(sizes, flat)[1], list(sizes), 25, maxj=400000)
    num = [x for x in counts if isinstance(x, int)]
    rd = BR.read(num)
    rd = {k: v for k, v in rd.items() if not k.startswith("family")} if rd else rd
    return {"class": c, "reading": D, "bare sizes": my_bare(n, flat), "agree to round 6": ok, "counts": counts,
            "recurrence": rd, "second differences": [num[t] - 2 * num[t - 1] + num[t - 2] for t in range(2, len(num))]}


def part_l(n):
    import networkx as nx
    s = Counter()
    for Tr in nx.nonisomorphic_trees(n):
        e = sorted(tuple(sorted(x)) for x in Tr.edges())
        flat = flat_of(n, e)
        sizes = my_bare(n, flat)
        c, D = read(sizes, flat)
        deg = Counter(x for ed in e for x in ed)
        small = max(sizes) <= 5
        nonleaf = {k for k in range(n) if deg[k] >= 2}
        three = any(sum(1 for v in Tr[u] if v in nonleaf) >= 3 for u in range(n))
        spine_ok = all(sum(1 for v in Tr[u] if v in nonleaf) <= 2 for u in nonleaf) and nx.is_connected(Tr.subgraph(nonleaf)) \
            if nonleaf else True
        caterpillar = spine_ok and not three
        ray_leaves = sum(1 for k in range(n) if deg[k] == 1 and deg[next(iter(Tr[k]))] == 2)
        key = "at most five places" if small else "more than five"
        s[f"{key}: trees"] += 1
        s[f"{key}: {c} {D}"] += 1
        if small:
            s["five places: a knot touches three non-leaves"] += three
            s["five places: not a caterpillar"] += not caterpillar
            s["five places: more than two ray-leaves"] += ray_leaves > 2
            s["five places: three-or-more or exponential"] += D == "exp" or (D not in (None, "0") and int(D) >= 3)
        s["any size: a knot touching three non-leaves has six or more places"] += (not three) or any(
            sizes[u] >= 6 for u in range(n) if sum(1 for v in Tr[u] if v in nonleaf) >= 3)
    return {"n": n, "counts": dict(s)}


def cases():
    only = set(PARAMS["only"].split(",")) if PARAMS.get("only") else None
    allc = [(f"L-{n:02d}", {"part": "L", "n": n}) for n in range(18, 2, -1)]
    allc += [(f"W-{k}-n{n:02d}", {"part": "W", "kind": k, "n": n}) for n in sorted(SIZES, reverse=True) for k in KINDS]
    allc += [("C-3", {"part": "C", "n": 3}), ("C-4", {"part": "C", "n": 4}), ("T-5", {"part": "T", "n": 5, "draws": 100000}),
             ("T-6", {"part": "T", "n": 6, "draws": 400000}), ("H", {"part": "H"})]
    for cid, p in allc:
        if only is None or cid in only:
            yield cid, p


def run(case_id, p):
    if p["part"] == "W":
        return part_w(p["kind"], p["n"])
    if p["part"] == "C":
        return part_c(p["n"])
    if p["part"] == "T":
        return part_t(p["n"], p["draws"])
    if p["part"] == "H":
        return part_h()
    return part_l(p["n"])
