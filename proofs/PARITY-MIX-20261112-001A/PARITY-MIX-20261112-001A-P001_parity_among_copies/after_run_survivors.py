#!/usr/bin/env python3
"""After the run (descriptive; not frozen): the shape of the placements that keep a state, on 3 x 3 and 4 x 4. The star of a copy is
the set of the three knots (cells) that hold it. Is every surviving placement with 0 < k < nm a union of stars, the stars of the
copies all of whose knots are parity knots?

    .venv/bin/python3 -B after_run_survivors.py [--write]"""
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))


def stars(n, m):
    import parity_lib as L
    ks = L.knots(n, m)
    return {x: frozenset(c for c, k in enumerate(ks) if x in k) for x in range(n * m)}


def main():
    out = {}
    for part, n in (("p3", 3), ("p4", 4)):
        res = json.loads((HERE / ("result_%s.json" % part)).read_text())["checks"]["result"]
        import parity_lib as L
        st = stars(n, n)
        classes = L.translation_classes(n, n)
        for r in res["rows"]:
            rows = r["rows"]
            assert len(rows) == len(classes)
            tot = union = 0
            sizes = {}
            for (K, w), x in zip(classes, rows):
                if not x["state"] or len(K) in (0, n * n):
                    continue
                C = [c for c in range(n * n) if st[c] <= K]
                U = frozenset().union(*[st[c] for c in C]) if C else frozenset()
                tot += w
                if U == K:
                    union += w
                    sizes[len(C)] = sizes.get(len(C), 0) + w
            out.setdefault(part, {})[r["harmony"]] = {"surviving placements, 0 < k < nm": tot, "unions of stars": union,
                                                     "by number of parity-bound copies": sizes}
    print(json.dumps(out, indent=1))
    if "--write" in sys.argv:
        (HERE / "result_after_run_survivors.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
