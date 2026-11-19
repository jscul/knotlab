"""Referee R1 for CLUSTER-ALL-20261119-001.  The referee's own growth (the FIRST-KNOT-R1 engine, with its GF(2) implied-parity
test) against the rule's predictions; the rule itself (clusters.py) and the post hoc reading (dimension.py) are
the objects under test and are run read-only as such (labelled).

  ../../../.venv/bin/python -B referee_cluster.py <part> > referee_cluster_<part>.json      (from this directory)

Parts:
  sample    my growth to 20 rounds against clusters.series on: a random 600 of the 24,502 five-knot census arrangements (seed 19),
            300 six-knot samples (the study's stated sampler re-implemented, seeds 70000 + 7k), the two six-knot misses, and the
            twelve falsifiers; with the overlapping-sunflower falsifier's round-3 junctions and their ancestor sets.
  posthoc   the post hoc chain-count reading on every census arrangement: where the chain count differs from the rule's class
            (the study's own figure is 15,024 of 15,261), and what the differing ones are; and, on 300 growing arrangements, my
            own measured dimension (45 rounds) against the chain count.
"""
import itertools
import json
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
EXP = ROOT / "experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census"
sys.path.insert(0, str(EXP))
sys.path.insert(0, str(ROOT / "research/JOIN-GROWTH-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
import clusters as Cl  # noqa: E402  (the rule under test, read-only)
import dimension as Dm  # noqa: E402  (the post hoc reading under test, read-only)
import referee_touch as RT  # noqa: E402
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
import referee_first as RFK  # noqa: E402


def edges_of(key):
    sizes, flat = key
    e = []
    for (i, j), m in zip(itertools.combinations(range(len(sizes)), 2), flat):
        e += [(i, j)] * m
    return list(sizes), e


def my_growth(sizes, edges, rounds=20, maxj=20000):
    """The referee's full engine (FIRST-KNOT-R1: GF(2) implied parity, the fewest rule), which these small closing starts need:
    the lean engine gives an implied junction of demand zero fresh distinctions."""
    n = len(sizes)
    M = [[0] * n for _ in range(n)]
    for a, b in edges:
        M[a][b] += 1
        M[b][a] += 1
    G = RFK.Start(RT.stars(sizes, M))
    G.zero_demand = 0
    out = "alive"
    for _ in range(rounds):
        r = G.step(RFK.fewest, None, None)
        if r != "ok":
            out = r
            break
        if len(G.bits) > maxj:
            out = "cap"
            break
    return G, out


def compare(item):
    name, sizes, edges = item
    pred = Cl.series(sizes, edges, 21)
    G, out = my_growth(sizes, edges)
    c = G.counts()
    if pred is None:
        return {"case": name, "verdict": "out of scope"}
    if pred == "stall":
        return {"case": name, "verdict": "match" if out == "stall" else "miss", "mine": out}
    m = len(c) if out in ("closed", "stall") else len(c)
    ok = pred[:len(c)] == c and (out != "closed" or all(x == 0 for x in pred[len(c):len(c) + 3]))
    return {"case": name, "verdict": "match" if ok else "miss", "mine": out, "rounds": len(c) - 1,
            "first difference": next((t for t, (a, b) in enumerate(zip(pred, c)) if a != b), None), "zero demand": G.zero_demand}


def six(seed):
    rng = random.Random(seed)
    while True:
        sizes = [rng.randint(3, 5) for _ in range(6)]
        deg = [0] * 6
        M = [[0] * 6 for _ in range(6)]
        pairs = [(i, j) for i in range(6) for j in range(i + 1, 6)]
        for _ in range(rng.randint(5, 12)):
            i, j = rng.choice(pairs)
            if deg[i] < sizes[i] and deg[j] < sizes[j]:
                M[i][j] += 1
                M[j][i] += 1
                deg[i] += 1
                deg[j] += 1
        if RT.connected(6, M):
            e = [(i, j) for i in range(6) for j in range(i + 1, 6) for _ in range(M[i][j])]
            return sizes, e


def census_keys():
    keys = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for a in r["result"]["arrangements"]:
            keys.append((tuple(a["key"][0]), tuple(a["key"][1]), a["dim"]))
    return keys


def sunflower_detail():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cj", EXP / "job.py")
    job = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job)
    out = {}
    for name, (sizes, e) in job.falsifiers().items():
        if "overlap" not in name:
            continue
        G, o = my_growth(sizes, e, rounds=4)
        anc = {}
        for j in range(len(G.bits)):
            anc[j] = {j} if G.round[j] == 0 else set().union(*(anc[p] for p in G.parents[j]))
        r3 = [j for j in range(len(G.bits)) if G.round[j] == 3]
        byset = defaultdict(list)
        for j in r3:
            byset[frozenset(k for k in anc[j] if G.round[k] == 0)].append(j)
        out[name] = {"round-3 junctions": len(r3),
                     "start-knot sets carrying two or more round-3 junctions": [[sorted(s), [len(G.parents[j]) for j in js]] for s, js in byset.items() if len(js) > 1]}
    return out


def part_sample():
    import importlib.util
    spec = importlib.util.spec_from_file_location("cj", EXP / "job.py")
    job = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(job)
    five = [k for k in census_keys() if len(k[0]) == 5]
    rng = random.Random(19)
    pick = rng.sample(five, 600)
    items = [(f"five {list(a)} {list(b)}", *edges_of((a, b))) for a, b, _ in pick]
    items += [(f"six seed {70000 + 7 * k}", *six(70000 + 7 * k)) for k in range(300)]
    items += [(name, s, e) for name, (s, e) in job.falsifiers().items()]
    res = json.load(open(ROOT / "artifacts/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census/results.json"))
    for m in res["T3"]["misses"]:
        items.append((f"six miss seed {m['seed']}", *edges_of(m["key"])))
    with Pool(16) as pool:
        rows = pool.map(compare, items, chunksize=4)
    out = {}
    for grp in ("five", "six seed", "T4", "six miss"):
        rs = [r for r in rows if r["case"].startswith(grp)]
        out[grp] = {"cases": len(rs), "verdicts": dict(Counter(r["verdict"] for r in rs)),
                    "misses": [r for r in rs if r["verdict"] == "miss"]}
    out["overlapping sunflowers, my growth"] = sunflower_detail()
    return out


def _post(item):
    a, b, d = item
    sz, e = edges_of((a, b))
    g = Dm.growth_class(sz, e)
    ch = Dm.chains(sz, e)
    acyc = [c for c, cy in ch if not cy] if ch else []
    cyc = any(cy for c, cy in ch) if ch else False
    return [list(a), list(b)], d, g, (max(acyc) if acyc else None), cyc


def part_posthoc():
    keys = census_keys()
    with Pool(16) as pool:
        res = pool.map(_post, keys, chunksize=40)
    poly = [r for r in res if r[2] not in ("out", "unsettled", "exp", "stall")]
    bad = [r for r in poly if r[4] or r[3] != r[2]]
    kinds = Counter(("a piece has a cycle" if r[4] else "no cycle") + f", class {r[2]}, chain count {r[3]}" for r in bad)
    # my own dimension on 300 growing arrangements with a chain count
    rng = random.Random(45)
    grow = [r for r in poly if r[2] not in (0,)]
    pick = rng.sample(grow, min(300, len(grow)))
    with Pool(16) as pool:
        mine = pool.map(_mydim, pick, chunksize=4)
    return {"census arrangements": len(res), "polynomial (rule's class)": len(poly),
            "rule's class equals the census's dimension": sum(1 for r in poly if r[1] == r[2]),
            "chain count (largest over cycle-free pieces) equals the class, no piece with a cycle": len(poly) - len(bad),
            "the others, by kind": dict(kinds.most_common()),
            "examples of the others": bad[:12],
            "my own dimension (45 rounds) on 300 growing arrangements": dict(Counter(m["agree"] for m in mine)),
            "my dimension disagreements": [m for m in mine if m["agree"] != "my dimension = chain count"][:12]}


def _mydim(r):
    key, d, g, c, cyc = r
    sz, e = edges_of(key)
    G, out = my_growth(sz, e, rounds=45, maxj=60000)
    mine = RT.read_dim(G.counts(), out)
    return {"key": key, "census dim": d, "rule class": g, "chain count": c, "cycle": cyc, "my dim": mine,
            "agree": "my dimension = chain count" if mine == c and not cyc else ("my dimension = census, chain count differs" if mine == d else "my dimension differs from both")}


def seven(seed):
    """The referee's seven-knot sampler, one size past the study: sizes 3 to 5, 6 to 14 random touches within the sizes,
    connected."""
    rng = random.Random(seed)
    while True:
        sizes = [rng.randint(3, 5) for _ in range(7)]
        deg = [0] * 7
        M = [[0] * 7 for _ in range(7)]
        pairs = [(i, j) for i in range(7) for j in range(i + 1, 7)]
        for _ in range(rng.randint(6, 14)):
            i, j = rng.choice(pairs)
            if deg[i] < sizes[i] and deg[j] < sizes[j]:
                M[i][j] += 1
                M[j][i] += 1
                deg[i] += 1
                deg[j] += 1
        if RT.connected(7, M):
            e = [(i, j) for i in range(7) for j in range(i + 1, 7) for _ in range(M[i][j])]
            return sizes, e


def part_seven():
    items = [(f"seven seed {90000 + k}", *seven(90000 + k)) for k in range(int(__import__("os").environ.get("N7", "300")))]
    with Pool(int(__import__("os").environ.get("WORKERS", "10"))) as pool:
        rows = pool.map(compare, items, chunksize=2)
    grows = [r for r in rows if r["verdict"] != "out of scope" and r.get("mine") not in (None, "stall")]
    return {"cases": len(rows), "verdicts": dict(Counter(r["verdict"] for r in rows)),
            "in scope and not stalling": len(grows), "outcomes of my growth": dict(Counter(r.get("mine") for r in rows)),
            "misses": [r for r in rows if r["verdict"] == "miss"]}


if __name__ == "__main__":
    print(json.dumps({"sample": part_sample, "posthoc": part_posthoc, "seven": part_seven}[sys.argv[1]](), indent=1, default=str))
