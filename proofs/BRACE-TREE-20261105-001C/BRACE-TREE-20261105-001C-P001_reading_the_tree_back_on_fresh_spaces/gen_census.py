#!/usr/bin/env python3
"""Generate fresh_census.json: every three-fold class of 23 to 26 points (untwisted and twisted), by the construction of
THREEFOLD-SURFACES-20261030-001B section 1 (census_lib.census, covers, decorate_pieces, classify) with the size bound raised from 22 to 26.
Each class is stored with its lines and, when twisted, its twisted incidence (line, point). Deterministic; about an hour.

    python3 -B gen_census.py          regenerate and compare with fresh_census.json
    python3 -B gen_census.py --write  write fresh_census.json
"""
import collections
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
for d in ("proofs/THREEFOLD-SPACES-20261030-001A/THREEFOLD-SPACES-20261030-001A-P001_three_fold_spaces_are_built_from_the_fano_plane",
          "proofs/THREEFOLD-GRAMMAR-20261030-001A/THREEFOLD-GRAMMAR-20261030-001A-P001_fano_leaves_and_planar_glue",
          "proofs/THREEFOLD-GRAMMAR-20261030-001B/THREEFOLD-GRAMMAR-20261030-001B-P001_census_with_doubled_incidences"):
    sys.path.insert(0, str(ROOT / d))
import census_lib as CE  # noqa: E402

LO, HI = 23, 26
out = []
for tw in (False, True):
    byN = collections.defaultdict(list)
    for n in range(1, 12):
        for H, c in CE.census(n, tw):
            for L in range(2, 2 * n + 1):
                if n + 6 * L > HI:
                    break
                if n + 6 * L < LO:
                    continue
                for Sset in CE.covers(H, L):
                    pts, lns = [p for k, p in Sset if k == 'P'], [i for k, i in Sset if k == 'L']
                    byN[n + 6 * L].append(CE.decorate_pieces(H, pts, lns, (0, 0)) if tw else (CE.decorate_pieces(H, pts, lns), None))
    for N in sorted(byN):
        cls = CE.classify([D for D, t in byN[N]], [t for D, t in byN[N]] if tw else None)
        for k, (H, cnt, t) in enumerate(cls):
            out.append({"name": ("twisted " if tw else "untwisted ") + f"{N}-point class {k}", "lines": [list(L) for L in H],
                        "twist": list(t) if t is not None else None})
        print(("twisted" if tw else "untwisted"), N, len(cls), flush=True)
text = json.dumps(out, indent=0) + "\n"
if "--write" in sys.argv:
    (HERE / "fresh_census.json").write_text(text)
    print("wrote", len(out), "classes")
else:
    same = (HERE / "fresh_census.json").exists() and json.loads((HERE / "fresh_census.json").read_text()) == json.loads(text)
    print("matches fresh_census.json:", same)
    sys.exit(0 if same else 1)
