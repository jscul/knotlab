#!/usr/bin/env python3
"""Checks for FAR-READ-20261106-001C: fresh spaces.

    python3 -B check.py --write    compute every fresh map (resuming from map_cache/), store maps.json.gz, write result.json
    python3 -B check.py            load maps.json.gz, recompute two rows of every space to confirm it, and verify result.json
    python3 -B check.py --rewrite  as the default, but write result.json
Run with the repository's .venv (numpy, networkx). Uses up to 22 processes."""
import os

for _v in ("OPENBLAS_NUM_THREADS", "OMP_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ.setdefault(_v, "1")

import collections  # noqa: E402
import hashlib  # noqa: E402
import json  # noqa: E402
import random  # noqa: E402
import sys  # noqa: E402
import time  # noqa: E402
from multiprocessing import Pool  # noqa: E402
from pathlib import Path  # noqa: E402

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import fresh_lib as FR  # noqa: E402

G, TL = FR.G, FR.G.TL
T0 = time.time()
OUT = {}


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print("PASS" if ok else "FAIL", name, json.dumps(info, default=str), round(time.time() - T0, 1), "s", flush=True)
    if not ok:
        sys.exit(1)


def judge_task(args):
    src, S, ex = args
    kind, c = FR.judge(S, ex)
    return "%s, %s" % (src, kind), c


def row_task(args):
    i, S, M = args
    M_, row, ns = G.TR.exact_row((S, M))
    return i, M, row


def describe(args):
    src, nm, S = args
    parts, types, lown, xs, atoms = FR.AT.atoms_of(S)
    return src, S.n, len(TL.solutions(S.H, S.s, S.n)), len(atoms)


if __name__ == "__main__":
    manifest = json.loads((HERE / "manifest.json").read_text())
    bad = {q: dg for q, dg in manifest["parent_bindings"].items() if hashlib.sha256((ROOT / q).read_bytes()).hexdigest() != dg}
    status = {q: json.loads((ROOT / q).read_text()).get("status") for q in manifest["parent_bindings"]
              if q.endswith(("manifest.json", "result.json")) and q.startswith("proofs/")}
    check("0 dependency artifacts bound by hash (ticket B's frozen rule included); upstream proofs Proved",
          not bad and all(s in ("Proved", "passed") for s in status.values()), {"mismatched": bad, "statuses": status})

    path = HERE / "maps.json.gz"
    with Pool(22) as pool:
        spaces, costs, dropped = FR.fresh_spaces(pool.imap)
        print(len(spaces), "spaces within the cost cap;", len(dropped), "beyond it", round(time.time() - T0, 1), "s", flush=True)
        # 1
        desc = list(pool.imap(describe, spaces, chunksize=2))
        if "--write" in sys.argv:
            # every row computed here; each space is checkpointed as soon as its rows are done, so a restart resumes
            cache = HERE / "map_cache"
            cache.mkdir(exist_ok=True)
            maps = [None] * len(spaces)
            for i, (src, nm, S) in enumerate(spaces):
                f = cache / ("%03d.json.gz" % i)
                if f.exists():
                    sp, mp = G.load_maps(f)
                    if [(x[0], x[1], x[2].H, x[2].s) for x in sp] == [(src, nm, S.H, S.s)]:
                        maps[i] = mp[0]
            pending = {i: {} for i in range(len(spaces)) if maps[i] is None}
            print(len(spaces) - len(pending), "spaces resumed from map_cache", flush=True)
            # the costliest spaces first, so the run is not left waiting on one large space at the end
            tasks = [(i, spaces[i][2], M) for i in sorted(pending, key=lambda i: -costs[i]) for M in range(len(spaces[i][2].H))]
            for i, M, row in pool.imap_unordered(row_task, tasks, chunksize=1):
                pending[i][M] = row
                if len(pending[i]) == len(spaces[i][2].H):
                    maps[i] = pending.pop(i)
                    G.save(cache / ("%03d.json.gz" % i), [spaces[i]], [maps[i]])
                    print("space %d done (%d left)" % (i, len(pending)), round(time.time() - T0, 1), "s", flush=True)
            G.save(path, spaces, maps)
            stored_spaces, maps = G.load_maps(path)
            confirmed = "all rows computed (checkpointed space by space)"
        else:
            stored_spaces, maps = G.load_maps(path)
            assert [(s[0], s[1], s[2].H, s[2].s) for s in stored_spaces] == [(s[0], s[1], s[2].H, s[2].s) for s in spaces]
            r = random.Random(0)
            sample = [(i, M) for i, (src, nm, S) in enumerate(spaces) for M in r.sample(range(len(S.H)), 2)]
            again = list(pool.imap(G.TR.exact_row, [(spaces[i][2], M) for i, M in sample], chunksize=1))
            mism = sum(row != maps[i][M] for (i, M), (M_, row, ns) in zip(sample, again))
            assert mism == 0, mism
            confirmed = "%d sampled rows recomputed, all equal" % len(sample)
        c1 = collections.Counter()
        for src, n, nsol, na in desc:
            c1["%s: spaces" % src] += 1
            c1["%s: knot spaces (no solutions)" % src] += nsol == 0
        pts = {src: (min(d[1] for d in desc if d[0] == src), max(d[1] for d in desc if d[0] == src)) for src in ("fresh plane", "fresh census")}
        ats = {src: (min(d[3] for d in desc if d[0] == src), max(d[3] for d in desc if d[0] == src)) for src in ("fresh plane", "fresh census")}
        check("1 the fresh spaces, fixed before any map was computed (within the cost cap), and their exact creation maps (maps.json.gz)",
              all(c1["%s: spaces" % s] == c1["%s: knot spaces (no solutions)" % s] for s in ("fresh plane", "fresh census")),
              {"spaces": dict(c1), "cost cap (solutions of the space minus its first line)": FR.CAP, "largest kept": max(costs),
               "beyond the cost cap": dropped, "points": pts, "Fano atoms": ats, "maps": confirmed,
               "maps.json.gz sha256": hashlib.sha256(path.read_bytes()).hexdigest()})

        rows = collections.defaultdict(collections.Counter)
        for kind, c in pool.imap(judge_task, [(src, S, ex) for (src, nm, S), ex in zip(spaces, maps)], chunksize=1):
            rows[kind].update(c)
    rows = {k: dict(v) for k, v in sorted(rows.items())}
    total = collections.Counter()
    for v in rows.values():
        total.update(v)
    # 2
    check("2 ticket B's frozen rule on the fresh spaces, against GLUE-READ C's two-stage rule and the source rule",
          total["spaces"] == len(spaces), {"by kind": rows, "all": dict(total)})
    # 3
    check("3 the far sides on the fresh spaces: no two lines of different atoms are indistinguishable far side by far side, while whether "
          "creation occurs fails to separate some; every Fano atom acts as one from outside",
          total["lines of two atoms indistinguishable far side by far side"] == 0 and
          total["atoms acting as one from outside"] == total["Fano atoms"],
          {k: total[k] for k in ("lines of two atoms indistinguishable by whether creation occurs",
                                 "lines of two atoms indistinguishable far side by far side", "atoms acting as one from outside",
                                 "Fano atoms")})

    OUT["seconds"] = round(time.time() - T0, 1)
    print("ALL OK", OUT["seconds"], "s")
    result = {"schema_version": 3, "artifact_id": manifest["artifact_id"], "kind": "proof", "ticket": manifest["ticket"],
              "proof": manifest["proof"], "status": "passed", "claim": manifest["claim"],
              "checks": {k: v for k, v in OUT.items() if k != "seconds"}}
    text = json.dumps(result, indent=1, sort_keys=True, default=str) + "\n"
    if "--write" in sys.argv or "--rewrite" in sys.argv:
        (HERE / "result.json").write_text(text)
    elif not (HERE / "result.json").exists() or json.loads((HERE / "result.json").read_text()) != json.loads(text):
        print("result.json does not match a fresh run; rerun with --write after review")
        sys.exit(1)
