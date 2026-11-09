"""RESCUE-GENUS-20261109-001A-E001: how on-time regular maps of higher genus reach their rings (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    the census; writes artifacts/RESCUE-GENUS-20261109-001A/RESCUE-GENUS-20261109-001A-E001_closest_routes/
                                   run/result.json

Every map is a network of equally spaced rule-60 rings with law (12, 12) contacts, built by PLAIN-TIME-20261108-001A's plain_lib from a
generating pair (x, y) of a group, merged by readings as that census did. For one target contact (the rotations act transitively on
contacts), the directed distance and the exact number of shortest routes from every contact, by breadth-first search; for every ring not
holding the target, its closest contacts and how they are reached: all by one route, one by a single route and another by several, or
none by a single route (on time if one of them has an odd count, late otherwise)."""
from __future__ import annotations

import collections
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "experiments/PLAIN-TIME-20261108-001A/PLAIN-TIME-20261108-001A-E001_map_census"))
import plain_lib as P  # noqa: E402

OUT = ROOT / "artifacts" / "RESCUE-GENUS-20261109-001A" / "RESCUE-GENUS-20261109-001A-E001_closest_routes" / "run"
SEEN = ["A 4", "S 4", "SL(2,p) 3", "GL(2,p) 3", "PSL(2,p) 5", "PGL(2,p) 5", "SL(2,p) 5", "S 5", "PSL(2,p) 7", "PGL(2,p) 7",
        "SL(2,p) 7", "A 6", "GL(2,p) 5", "S 6", "PSL(2,p) 11", "PGL(2,p) 11", "PSL(2,p) 13", "PGL(2,p) 13", "PSL(2,p) 17", "A 7",
        "PSL(2,p) 19", "PSL(2,p) 23", "PSL(2,p) 29"]
NEW = ["PSL(2,p) 31", "PSL(2,p) 37", "PGL(2,p) 17", "PGL(2,p) 19", "SL(2,p) 11", "GL(2,p) 7", "S 7"]


def classify(n, out, rc, target):
    inn = [[] for _ in range(n)]
    for d in range(n):
        for e in out[d]:
            inn[e].append(d)
    dist, cnt = [None] * n, [0] * n
    dist[target], cnt[target] = 0, 1
    order, q = [target], collections.deque([target])
    while q:
        a = q.popleft()
        for b in inn[a]:
            if dist[b] is None:
                dist[b] = dist[a] + 1
                q.append(b)
                order.append(b)
    for b in order[1:]:
        cnt[b] = sum(cnt[e] for e in out[b] if dist[e] == dist[b] - 1)
    cls, odd_counts = collections.Counter(), []
    for cs in rc:
        if target in cs:
            continue
        dr = min(dist[e] for e in cs)
        cl = [cnt[e] for e in cs if dist[e] == dr]
        single, tied = [c for c in cl if c == 1], [c for c in cl if c > 1]
        if not tied:
            cls["all closest by one route"] += 1
        elif single:
            cls["one closest by one route, another tied"] += 1
        elif any(c % 2 for c in tied):
            cls["closest tied, an odd count"] += 1
            odd_counts.append(sorted(cl))
        else:
            cls["late"] += 1
    ties = [dist[e] for e in range(n) if cnt[e] >= 2]
    return dict(cls), max(dist), min(ties) if ties else None, odd_counts


def group_rows(name):
    G, gens = P.group(name)
    rows, seen = [], {}
    for x, y in P.generating_pairs(G, gens):
        n, out, rc, target, m, f = P.group_map(G, x, y)
        genus = (2 - (len(rc) - n + len(G) // f)) // 2
        if genus < 2:
            continue
        v = P.verdicts(n, out, rc, target)
        row = {"family": "group", "name": name, "order": len(G), "m": m, "f": f, "genus": genus, "rings": len(rc), "contacts": n, **v}
        key = json.dumps(row, sort_keys=True)
        if key in seen:
            rows[seen[key]]["maps"] += 1
            continue
        cls, diam, first_tie, odd = classify(n, out, rc, target)
        row.update({"maps": 1, "closest": cls, "first tie": first_tie, "odd tied counts": odd,
                    "on time": v["rings late"] == 0 and v["rings never"] == 0, "roster": "new" if name in NEW else "seen"})
        seen[key] = len(rows)
        rows.append(row)
    return rows


def main():
    t0 = time.time()
    with Pool(16) as pool:
        rows = [r for rs in pool.imap_unordered(group_rows, SEEN + NEW) for r in rs]
    out = {"experiment": "RESCUE-GENUS-20261109-001A-E001", "rows": sorted(rows, key=lambda r: (r["roster"], r["name"], r["rings"], r["m"], r["f"]))}
    for roster in ("seen", "new"):
        rs = [r for r in rows if r["roster"] == roster]
        on = [r for r in rs if r["on time"]]
        tot = collections.Counter()
        for r in on:
            tot.update(r["closest"])
        out[roster] = {
            "maps": len(rs), "on time": len(on),
            "H1 counterexamples (on-time maps with a ring none of whose closest contacts has one route)":
                [[r["name"], r["m"], r["f"], r["genus"], r["rings"], r["odd tied counts"]] for r in on if r["closest"].get("closest tied, an odd count")],
            "on-time ring-target pairs by how their closest contacts are reached": dict(tot),
            "on-time maps using a tied closest contact beside a single one": sum(1 for r in on if r["closest"].get("one closest by one route, another tied")),
            "H2 counterexamples (late maps with diameter at most first tie + 2)":
                [[r["name"], r["m"], r["f"], r["genus"], r["rings"]] for r in rs if not r["on time"] and r["first tie"] is not None and r["diameter"] <= r["first tie"] + 2],
            "maps with diameter at most first tie + 2": sum(1 for r in rs if r["first tie"] is not None and r["diameter"] <= r["first tie"] + 2)}
    out["seconds"] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "rows"}, indent=1))


if __name__ == "__main__":
    main()
