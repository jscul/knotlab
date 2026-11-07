#!/usr/bin/env python3
"""Generate census22.json: every three-fold class of at most 22 points (untwisted and twisted), by the construction of
THREEFOLD-SURFACES-20261030-001B section 1 (census_lib.census, covers, decorate_pieces, classify). Each class is stored with its lines and,
when twisted, its twisted incidence (line, point). Deterministic.

    python3 -B gen_census22.py          regenerate and compare with census22.json
    python3 -B gen_census22.py --write  write census22.json
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
import threefold_lib as T  # noqa: E402
import census_lib as C  # noqa: E402

spaces = {False: [("Fano (7)", T.FANO, None)], True: []}
for tw in (False, True):
    byN = collections.defaultdict(list)
    for n in range(1, 11):
        for H, c in C.census(n, tw):
            for L in range(2, 2 * n + 1):
                if n + 6 * L > 22:
                    break
                for Sset in C.covers(H, L):
                    pts, lns = [p for k, p in Sset if k == 'P'], [i for k, i in Sset if k == 'L']
                    byN[n + 6 * L].append(C.decorate_pieces(H, pts, lns, (0, 0)) if tw else (C.decorate_pieces(H, pts, lns), None))
    for N in sorted(byN):
        cls = C.classify([D for D, t in byN[N]], [t for D, t in byN[N]] if tw else None)
        for k, (H, cnt, t) in enumerate(cls):
            spaces[tw].append((f"{N}-point class {k}", H, t))
out = [{"name": ("twisted " if tw else "untwisted ") + nm, "lines": [list(l) for l in H], "twist": list(t) if t is not None else None}
       for tw in (False, True) for nm, H, t in spaces[tw]]
text = json.dumps(out) + "\n"
if "--write" in sys.argv:
    (HERE / "census22.json").write_text(text)
    print("wrote", len(out), "classes")
else:
    same = (HERE / "census22.json").exists() and json.loads((HERE / "census22.json").read_text()) == json.loads(text)
    print("matches census22.json:", same, len(out), "classes")
    sys.exit(0 if same else 1)
