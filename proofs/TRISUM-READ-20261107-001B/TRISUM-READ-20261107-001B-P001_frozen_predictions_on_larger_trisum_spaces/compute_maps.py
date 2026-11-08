#!/usr/bin/env python3
"""Exact creation maps of ticket B's ten test spaces, with map_lib.exact_row; one gz json per space in map_cache/ (finished spaces are
skipped, so a stopped run resumes), then maps.json.gz.

    python3 -B compute_maps.py [workers]     (default 16; each worker peaks near 0.7 GB on the largest space)

The stored maps were computed by this procedure in three runs after the freeze; provenance.json records which engine and when."""
import gzip
import hashlib
import json
import os
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import map_lib as ML  # noqa: E402

ML.TR.engine()                                  # load the creation engine once, before the workers fork
CACHE = HERE / "map_cache"


def row(args):
    H, n, M = args
    out, ns = ML.exact_row(H, n, M)
    return M, {str(L): (None if v is None else [int(x) for x in v]) for L, v in out.items()}, ns


if __name__ == "__main__":
    workers = int(sys.argv[1]) if len(sys.argv) > 1 else 16
    frozen = json.loads((ML.A / "predictions.json").read_text())
    spaces = {sp["seed"]: sp for sp in json.loads((ML.A / "spaces.json").read_text())}
    CACHE.mkdir(exist_ok=True)
    t0 = time.time()
    with Pool(workers) as pool:
        for rec in frozen["spaces"]["test"]:
            sp = spaces[rec["seed"]]
            H, n = [tuple(l) for l in sp["lines"]], sp["points"]
            assert hashlib.sha256(json.dumps([list(l) for l in H]).encode()).hexdigest() == rec["lines sha256"]
            path = CACHE / ("seed%d.json.gz" % rec["seed"])
            if path.exists():
                continue
            rows = {}
            for M, out, nsol in pool.imap_unordered(row, [(H, n, M) for M in range(len(H))], chunksize=1):
                rows[str(M)] = {"row": out, "solutions": nsol}
            tmp = str(path) + ".tmp"
            with gzip.open(tmp, "wt") as f:
                json.dump({"seed": rec["seed"], "lines": [list(l) for l in H], "points": n, "rows": rows}, f)
            os.replace(tmp, path)
            print("seed", rec["seed"], "done", round(time.time() - t0, 1), "s", flush=True)
    maps = {str(r["seed"]): json.load(gzip.open(CACHE / ("seed%d.json.gz" % r["seed"]), "rt")) for r in frozen["spaces"]["test"]}
    with gzip.open(HERE / "maps.json.gz", "wt") as f:
        json.dump(maps, f, sort_keys=True)
    print("maps.json.gz written:", len(maps), "spaces")
