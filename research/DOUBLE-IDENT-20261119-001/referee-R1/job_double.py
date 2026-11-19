"""Shared-runner job for the referee's check of DOUBLE-IDENT-20261119-001 (own data, own classification, own relayed model, own
growth with the program's fresh rule; the touch census's arrangements and measured classes read from runs/touch-census as data; no
study code imported or run).

For each census arrangement (knots with their places, any number of distinctions shared by two knots):
- the data the growth reads: open_k = places - shared (with multiplicity), live knots, round-1 groups among the live knots with
  every knot a possible common neighbour (the referee's engine), d_k;
- the class: stall (d_k > open_k), (S3), (S4) on the underlying simple graph with every knot a possible common neighbour, the loose
  count (S6');
- X+ on these data: blocks N(w) restricted to live knots for every knot w, live or not; open - d pendant points with R(open) rays;
  relays on finite pieces when there are two or more pieces;
- part K (every eighth arrangement in the class with double touches, every simple one in the class, every one-loose one): the
  growth's keys per round to 6 (parents, fresh, the parents' keys; the program's rule: an implied junction gets exactly d) against
  the relayed model's (RELAY-IDENT-R1's relayed_keys); a one-loose start must close at round 1;
- part G (every arrangement in the class, one-loose and loose-free ones included): the growth class read off the pieces (finite:
  closes alone, relays otherwise; a tree core: its ray count; one cycle, all blocks pairs, no pendant point: 1; any other cycle:
  exponential) against the census's measured class.

  .venv/bin/python -B scripts/longrun.py launch research/DOUBLE-IDENT-20261119-001/referee-R1/job_double.py \\
      --out runs/referee-double --unit referee-double --workers 4 --case-timeout 3600 --case-mem 3G --mem-max 16G
"""
import itertools
import json
import sys
from collections import Counter, defaultdict
from fractions import Fraction
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for p in ("research/RELAY-IDENT-20261119-001/referee-R1", "research/CHAIN-IDENT-20261119-001/referee-R1",
          "research/RING-IDENT-20261119-001/referee-R1", "research/FIRST-KNOT-20261118-001/referee-R1",
          "research/TOUCH-CENSUS-20261118-001/referee-R1"):
    sys.path.insert(0, str(ROOT / p))
T = 6


def data(sizes, flat):
    import referee_first as RFK
    import job_ring as JR
    n = len(sizes)
    edges = []
    for (i, j), m in zip(itertools.combinations(range(n), 2), flat):
        edges += [(i, j)] * m
    sh = Counter(x for e in edges for x in e)
    nb = defaultdict(set)
    for a, b in edges:
        nb[a].add(b)
        nb[b].add(a)
    opn = [sizes[k] - sh[k] for k in range(n)]
    live = [k for k in range(n) if opn[k] >= 1]
    G = RFK.Start(JR.stars_of(n, edges, list(sizes)))
    groups = G.groups(live, None) if live else []
    d = Counter(x for g in groups for x in g)
    return n, edges, nb, opn, live, groups, d


def classify(sizes, flat):
    n, edges, nb, opn, live, groups, d = data(sizes, flat)
    if any(d[k] > opn[k] for k in live):
        return "stall"
    if any(len(g) > 2 for g in groups):
        return "out (S3)"
    if any(len(nb[a] & nb[b]) >= 2 for a, b in itertools.combinations(live, 2)):
        return "out (S4)"
    loose = sum(opn[k] for k in live)
    return "none" if loose == 0 else ("one loose" if loose == 1 else "in")


def build(sizes, flat, ray_len):
    """X+ in the dictionary form of CHAIN-IDENT-R1's plus(), from the census's own places."""
    n, edges, nb, opn, live, groups, d = data(sizes, flat)
    ls = set(live)
    blocks = [tuple(sorted(nb[w] & ls)) for w in range(n) if len(nb[w] & ls) >= 2]
    nxt = n
    pend = []
    for k in live:
        R = 0 if opn[k] >= 3 else (1 if opn[k] == 2 else 2)
        for _ in range(opn[k] - d[k]):
            o = nxt
            nxt += 1
            blocks.append((k, o))
            rays = []
            for _ in range(R):
                prev, pts = o, []
                for _ in range(ray_len):
                    blocks.append((prev, nxt))
                    pts.append(nxt)
                    prev = nxt
                    nxt += 1
                rays.append(pts)
            pend.append((k, o, R, rays))
    pendset = {p[1] for p in pend}
    core = [B for B in blocks if all(x < n or x in pendset for x in B)]
    parent = {}

    def find(x):
        while parent.setdefault(x, x) != x:
            x = parent[x]
        return x
    for B in core:
        for x in B[1:]:
            parent[find(x)] = find(B[0])
    comps = defaultdict(lambda: {"knots": set(), "points": set(), "blocks": 0, "inc": 0, "rays": 0, "pend": 0, "big": 0})
    for k in live:
        comps[find(k)]["knots"].add(k)
    for B in core:
        c = comps[find(B[0])]
        c["blocks"] += 1
        c["inc"] += len(B)
        c["points"] |= set(B)
        c["big"] += len(B) > 2 and all(x < n for x in B)
    for k, o, R, _ in pend:
        comps[find(k)]["rays"] += R
        comps[find(k)]["pend"] += 1
    return {"sizes": list(sizes), "edges": edges, "open": opn, "live": live, "d": d, "blocks": blocks, "npts": nxt, "pend": pend,
            "comps": comps, "find": find, "loose": sum(opn[k] for k in live)}


def grow_keys(sizes, edges, rounds):
    import job_relay as RL
    return RL.grow_keys(len(sizes), edges, list(sizes), rounds)


def predict(X):
    if X["loose"] <= 1:
        return 0
    pieces = [c for c in X["comps"].values() if c["knots"]]
    kinds = []
    for c in pieces:
        pts = c["points"] | c["knots"]
        cyc = c["inc"] - (len(pts) + c["blocks"]) + 1
        if cyc == 0:
            kinds.append(("finite", 0) if c["rays"] == 0 else ("rays", c["rays"]))
        elif cyc == 1 and c["pend"] == 0 and c["big"] == 0:
            kinds.append(("bare cycle", 1))
        else:
            kinds.append(("exp", None))
    if any(k == "exp" for k, _ in kinds):
        return "exp"
    if len(kinds) == 1 and kinds[0][0] == "finite":
        return 0
    return max([v for k, v in kinds if k != "finite"] + ([2] if any(k == "finite" for k, _ in kinds) else []))


def cases():
    rows = []
    for line in open(ROOT / "runs/touch-census/results.jsonl"):
        r = json.loads(line)
        if r.get("status") == "ok":
            rows += [[a["key"], a["dim"], a["outcome"]] for a in r["result"]["arrangements"]]
    rows.sort(key=lambda x: str(x[0]))
    for a in range(0, len(rows), 400):
        yield f"G-{a // 400:03d}", {"part": "G", "rows": rows[a:a + 400]}
    for a in range(0, len(rows), 150):
        yield f"K-{a // 150:03d}", {"part": "K", "rows": rows[a:a + 150]}


def run(case_id, p):
    import job_relay as RL
    out = []
    for i, (key, dim, outcome) in enumerate(p["rows"]):
        sizes, flat = key
        c = classify(sizes, flat)
        double = any(m >= 2 for m in flat)
        if p["part"] == "G":
            if c not in ("in", "one loose", "none"):
                out.append([c, double, None, None])
                continue
            X = build(sizes, flat, 2)
            D = predict(X)
            meas = "exp" if (dim is None and outcome in ("alive", "big", "timed")) or (dim is not None and dim >= 5) else \
                (dim if dim is not None else (0 if outcome == "closed" else outcome))
            out.append([c, double, str(D), str(meas)])
            continue
        # part K: a sample
        import zlib
        idx = zlib.crc32(str(key).encode()) % 8
        if not (c == "one loose" or (c == "in" and (not double or idx == 0))):
            continue
        X = build(sizes, flat, T + 3)
        a, counts = grow_keys(sizes, X["edges"], T)
        if c == "one loose":
            out.append({"key": key, "class": c, "closes at round 1": counts[:3] == [len(sizes), 1, "closed"] or
                        (len(counts) >= 3 and counts[2] == "closed"), "counts": counts})
            continue
        b = RL.relayed_keys(len(sizes), X, T + 1)
        bad = [t for t in range(T + 1) if {k: Fraction(v) for k, v in a.get(t, {}).items()} != {k: v for k, v in b.get(t, {}).items() if v}]
        out.append({"key": key, "class": c, "double": double, "agree": not bad, "rounds that differ": bad})
    return {"rows": out}
