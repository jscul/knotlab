#!/usr/bin/env python3
"""Referee SHIFT-COUNT-R1: the one base with a forced but uncertified second direction (sample 137 at r = 4; directions (0, 1) and
(0, -1)). Search ticket A's family (sets of 2 to 4 cells of [0, 2]^2 holding the origin, every pattern with first value 0, multiples
k = 1 .. 4) for a pattern forced along k d in a 61 x 61 window, and try to certify it with ref_shiftcount.py's certificates (tori, and
two-way eventually periodic states in three frames with periods from the spans upward).

    python3 -B ref_137.py      (writes result_137.json)"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import ref_shiftcount as S  # noqa: E402

BOX = [(x, y) for x in range(3) for y in range(3)]


def main():
    K = S.kinds_of(137, 4)
    out = {"kinds": K, "found": []}
    for d in ((0, 1), (0, -1)):
        for size in (2, 3, 4):
            for rest in itertools.combinations([c for c in BOX if c != (0, 0)], size - 1):
                A = [(0, 0)] + list(rest)
                for q in itertools.product((0, 1), repeat=size - 1):
                    p = (0,) + q
                    for k in range(1, 5):
                        t = (k * d[0], k * d[1])
                        for sigma in (0, 1):
                            if S.window_forces(K, A, p, t, sigma):
                                fix = list(zip(A, p)) + [((c[0] + t[0], c[1] + t[1]), v ^ sigma) for c, v in zip(A, p)]
                                c1 = S.carried(K, fix, d)
                                free = [S.carried(K, list(zip(A, (0,) + qq)), d) for qq in itertools.product((0, 1), repeat=size - 1)]
                                out["found"].append({"d": d, "A": A, "p": p, "k": k, "sigma": sigma, "image carried": c1,
                                                     "A free": all(free), "free by": sorted(set(map(str, free)))})
                                print(out["found"][-1], flush=True)
                                if c1 and all(free):
                                    out["certified"] = out["found"][-1]
                                    (HERE / "result_137.json").write_text(json.dumps(out, indent=1) + "\n")
                                    return
    (HERE / "result_137.json").write_text(json.dumps(out, indent=1) + "\n")


if __name__ == "__main__":
    main()
