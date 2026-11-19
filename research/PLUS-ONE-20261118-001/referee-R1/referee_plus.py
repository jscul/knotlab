"""Referee R1 for PLUS-ONE-20261118-001 (own code; the study's linked.py, job.py and its census library are not imported).

  ../../../.venv/bin/python -B referee_plus.py <part> > referee_plus_<part>.json      (from this directory)

Growth: the referee's FIRST-KNOT-R1 engine under the fewest rule.  Dimension: the referee's TOUCH-CENSUS-R1 reader (junctions by
round; d + 1 for the least d whose d-th differences are constant and nonzero over the last 12 of 45 rounds).

Definitions, as the study states them (decision note and linked.py's docstring): a birth is a new one-parent junction of demand
1 whose parent is not itself a one-parent junction of demand 1; its partner is the other new junction of that round on the same
parent; births of one round with one partner form a class, and two sibling births are one class of two; two classes of one round
are linked when their partners share a neighbour or are neighbours.  Rule: the dimension is the largest, over rounds and linked
components, of the sum of the class sizes; births are read in the first 15 rounds.  Neighbourhoods are taken at round 15, as
the study's code does; the variant with neighbourhoods at the birth round is also reported.

Parts:
  census   every arrangement of TOUCH-CENSUS's run with a birth and a settled dimension (selected from runs/touch-census as the
           study does; 11,658 expected): the referee's own births, classes, links, rule and dimension, and the study's dimension.
  six      the 400 six-knot samples, drawn by the study's stated procedure with its seeds 50000 to 50399, grown and read by the
           referee.
"""
import json
import random
import sys
from collections import Counter, defaultdict
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/FIRST-KNOT-20261118-001/referee-R1"))
sys.path.insert(0, str(ROOT / "research/TOUCH-CENSUS-20261118-001/referee-R1"))
import referee_first as RFK  # noqa: E402
import referee_touch as RT  # noqa: E402


def grow_with_births(sizes, M, read_rounds=15, rounds=45, maxj=12000):
    G = RFK.Start(RT.stars(sizes, M))
    births = []
    snapshot = {}

    def rule(g, info, rng):
        ids = {i["j"] for i in info}
        rows = []
        for i in info:
            if i["p"] != 1 or i["d"] != 1:
                continue
            j = i["j"]
            parent = next(iter(g.parents[j]))
            if len(g.parents[parent]) == 1 and g.dem[parent] == 1:
                continue
            sib = sorted(x for x in ids if x != j and parent in g.parents[x])
            rows.append((j, sib[0] if sib else None, len(sib)))
        births.append(rows)
        return RFK.fewest(g, info, rng)
    outcome = "alive"
    for t in range(rounds):
        r = G.step(rule, None, None)
        if t + 1 == read_rounds or r != "ok" and not snapshot:
            snapshot = {k: set(v) for k, v in enumerate(G.nbr)}
        if r != "ok":
            outcome = r
            break
        if len(G.bits) > maxj:
            outcome = "big"
            break
    if not snapshot:
        snapshot = {k: set(v) for k, v in enumerate(G.nbr)}
    return G, outcome, births[:read_rounds], snapshot


def rule_of(births, nbr):
    big_class, big_sum, shapes, multi = 0, 0, [], 0
    for rows in births:
        if not rows:
            continue
        ids = {j for j, _, _ in rows}
        cls = {}
        for j, partner, ns in rows:
            multi += ns > 1
            key = frozenset((j, partner)) if partner in ids else partner
            cls.setdefault(key, set()).add(j)
        keys = list(cls)
        parts = {k: (list(k) if isinstance(k, frozenset) else [k]) for k in keys}

        def linked(a, b):
            return any(x is not None and y is not None and (nbr.get(x, set()) & nbr.get(y, set()) or x in nbr.get(y, set()))
                       for x in parts[a] for y in parts[b])
        root = {k: k for k in keys}

        def find(k):
            while root[k] != k:
                k = root[k]
            return k
        for a in range(len(keys)):
            for b in range(a + 1, len(keys)):
                if linked(keys[a], keys[b]):
                    root[find(keys[a])] = find(keys[b])
        sums, members = defaultdict(int), defaultdict(list)
        for k in keys:
            sums[find(k)] += len(cls[k])
            members[find(k)].append(k)
        for ks in members.values():
            if len(ks) >= 2:
                shapes.append([sorted(len(cls[k]) for k in ks), all(linked(x, y) for i, x in enumerate(ks) for y in ks[i + 1:])])
        big_class = max(big_class, max(len(v) for v in cls.values()))
        big_sum = max(big_sum, max(sums.values()))
    return big_class, big_sum, shapes, multi


def miss_shape(G, births, sizes, M):
    """For a miss: the rounds of its births, whether two round-1 births come from start knots sharing a distinction."""
    r1 = births[0] if births else []
    parents = sorted({next(iter(G.parents[j])) for j, _, _ in r1})
    start = [k for k in range(len(G.bits)) if G.round[k] == 0]
    share = [(a, b) for i, a in enumerate(parents) for b in parents[i + 1:] if a in start and b in start and M[a][b] > 0]
    return {"births by round": [len(r) for r in births], "round-1 birth parents (start knots)": parents,
            "pairs of those start knots sharing a distinction": share}


def one_census(row):
    sizes, flat = row["key"]
    s, M = RT.key_to(sizes, flat)
    G, outcome, births, nbr15 = grow_with_births(s, M)
    dim = RT.read_dim(G.counts(), outcome)
    bc, bs, sh, multi = rule_of(births, nbr15)
    out = {"key": row["key"], "study dim": row["dim"], "referee dim": dim, "largest class": bc, "linked sum": bs, "shapes": sh,
           "births with two or more siblings": multi, "any birth (referee)": any(births)}
    if dim != bs or row["dim"] != bs:
        out["miss shape"] = miss_shape(G, births, s, M)
    return out


def select():
    out = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") != "ok":
            continue
        for a in r["result"]["arrangements"]:
            if a.get("any_birth") and a.get("dim") is not None:
                out.append(a)
    return out


def summarize(rows, dim_key):
    s = [r for r in rows if isinstance(r[dim_key], int)]
    m = sum(1 for r in s if r[dim_key] == r["linked sum"])
    over = sum(1 for r in s if r["linked sum"] > r[dim_key])
    unlinked = [r for r in s if r["linked sum"] == r["largest class"] and r[dim_key] > r["linked sum"]]
    other = [r for r in s if r[dim_key] != r["linked sum"] and r not in unlinked and not r["linked sum"] > r[dim_key]]
    return {"arrangements with a settled dimension": len(s), "rule matches": m, "overshoots (rule above dimension)": over,
            "misses (rule below dimension)": len(unlinked) + len(other), "... of which unlinked (dimension = largest class + 1)":
            sum(1 for r in unlinked if r[dim_key] == r["largest class"] + 1)}


def part_census():
    sel = select()
    with Pool(20) as pool:
        rows = pool.map(one_census, sel, chunksize=8)
    shapes = Counter((tuple(x[0]), x[1]) for r in rows for x in r["shapes"])
    misses = [r for r in rows if isinstance(r["study dim"], int) and r["study dim"] != r["linked sum"]]
    return {"selected (any birth, settled dimension in the census run)": len(sel),
            "referee and study dimensions agree": sum(1 for r in rows if r["referee dim"] == r["study dim"]),
            "against the study's dimension": summarize(rows, "study dim"),
            "against the referee's dimension": summarize(rows, "referee dim"),
            "linked components (class sizes, clique)": {str(k): v for k, v in shapes.items()},
            "births with two or more siblings (partner ambiguous)": sum(r["births with two or more siblings"] for r in rows),
            "misses against the study's dimension": [{k: r[k] for k in ("key", "study dim", "referee dim", "largest class", "linked sum", "miss shape")} for r in misses]}


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
            return sizes, M


def one_six(seed):
    sizes, M = six(seed)
    G, outcome, births, nbr15 = grow_with_births(sizes, M)
    dim = RT.read_dim(G.counts(), outcome)
    bc, bs, sh, multi = rule_of(births, nbr15)
    out = {"seed": seed, "sizes": sizes, "outcome": outcome, "dim": dim, "any birth": any(births), "largest class": bc,
           "linked sum": bs, "shapes": sh}
    if isinstance(dim, int) and any(births) and dim != bs:
        out["miss shape"] = miss_shape(G, births, sizes, M)
    return out


def part_six():
    with Pool(20) as pool:
        rows = pool.map(one_six, range(50000, 50400))
    settled = [r for r in rows if r["any birth"] and isinstance(r["dim"], int) and r["outcome"] in ("alive", "big")]
    return {"samples": len(rows), "outcomes (outcome, dimension)": {str(k): v for k, v in Counter((r["outcome"], r["dim"]) for r in rows).most_common()},
            "settled and growing with a birth": len(settled),
            "rule matches": sum(1 for r in settled if r["dim"] == r["linked sum"]),
            "overshoots": sum(1 for r in settled if r["linked sum"] > r["dim"]),
            "misses": [r for r in settled if r["dim"] != r["linked sum"]],
            "linked components": {str(k): v for k, v in Counter((tuple(x[0]), x[1]) for r in rows for x in r["shapes"]).items()}}


if __name__ == "__main__":
    print(json.dumps({"census": part_census, "six": part_six}[sys.argv[1]](), indent=1, default=str))
