#!/usr/bin/env python3
"""After the run, descriptive (not frozen). The frozen census twisted knot 0's second member; in the closed chains and the two cycles
that member sits outside the cycle, so those cells were balanced (the twist undoes at that copy, T2) and tested only the null. This
reruns them with the twist on a member on the cycle (knot 0's first member, distinction 0, shared with the last knot of the chain; for
the two cycles, distinction 0 in knot 0 and in knot 3), with the frozen functions, to measure the cycle-length effect at 2, 3 and 6.

    .venv/bin/python3 -B after_run_on_cycle.py"""
import importlib.util
import json
import sys
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import twist_lib as W  # noqa: E402

spec = importlib.util.spec_from_file_location("twist_check", HERE / "check.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)


def job(B):
    m = B[0]
    reps = [g for g in W.conjugacy_classes(W.automorphisms(B)) if g != tuple(range(m))]
    rows = []
    for h in reps:
        for name, P, n in (("two sharing two", W.two_sharing_two(), 2), ("closed chain of 3", W.closed_chain(3), 3),
                           ("closed chain of 6", W.closed_chain(6), 6)):
            r = C.measure(B, P, {(0, 0): h}, n)
            r.update({"twist": list(h), "pattern": name})
            rows.append(r)
    pairs = [(a, b) for ai, a in enumerate(reps) for b in reps[ai:]][:6]
    for a, b in pairs:
        r = C.measure(B, W.two_cycles(), {(0, 0): a, (3, 0): b}, None)
        r.update({"twist": [list(a), list(b)], "pattern": "two cycles of 3"})
        rows.append(r)
    return {"block": [m, [list(e) for e in B[1]]], "rows": rows}


if __name__ == "__main__":
    bl = [(m, [tuple(e) for e in E]) for m, E in W.S.blocks()]
    el = C.eligible(bl)
    with Pool(12) as pool:
        rows = pool.map(job, el, chunksize=1)
    out = {"status": "descriptive, after the run", "rows": rows}
    (HERE / "result_after_run_on_cycle.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    import collections
    cnt = collections.Counter()
    for b in rows:
        by = collections.defaultdict(dict)
        for r in b["rows"]:
            if r["pattern"] != "two cycles of 3":
                by[json.dumps(r["twist"])][r["pattern"]] = (r["class"], r["lives"])
        for t, d in by.items():
            cnt[tuple(d[p][1] for p in ("two sharing two", "closed chain of 3", "closed chain of 6"))] += 1
    single = [r for b in rows for r in b["rows"] if r.get("advisor's exact condition (distance <= cycle length)") is not None]
    print("lives at (2, 3, 6):", dict(cnt))
    print("advisor's condition agrees:", sum(r["advisor's exact condition (distance <= cycle length)"] == r["lives"] for r in single), "of", len(single))
    print("classes:", collections.Counter((r["pattern"], r["class"]) for b in rows for r in b["rows"]))
    print("quotient equals measured (living):", sum(1 for b in rows for r in b["rows"] if r["lives"] and all(set(x["predicted (quotient) tied in the copy"]) == set(x.get("tied in the copy", [])) for x in r["roots"])), "of", sum(1 for b in rows for r in b["rows"] if r["lives"]))
