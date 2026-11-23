"""Census of population P1: the four constructions of the shape benchmark.

Cubic to depth 6 or 20,000 knots, pinwheel to depth 5, polygonal control (substitution 'periodic') to depth 8,
bounded-bond windows 1 to 4.  Constructors are GROWTH-STATISTICS-20261121-001A `sources.py` (read, not changed).
One JSON line per stage (a depth or window), then one line per construction.

Run from the repo root:  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""
import json
import signal
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import lib  # noqa: E402

SOURCES_PY = lib.EXP / "GROWTH-STATISTICS-20261121-001A/GROWTH-STATISTICS-20261121-001A-E001_blind/sources.py"
KNOT_CAP = 20000
PER_PATTERN_SECONDS = 150


class Slow(Exception):
    pass


def _alarm(signum, frame):
    raise Slow()


def build(src, name, depth):
    if name == "cubic":
        return src.cubic_pattern(depth)[0]
    if name in ("pinwheel", "periodic"):
        r = src.planar_pattern(name, depth)
        return r[0] if isinstance(r, tuple) else r
    return src.fold_pattern(depth, depth)


def main():
    src = lib.load_module("p1_sources", SOURCES_PY)
    plan = {"cubic": range(0, 7), "pinwheel": range(1, 6), "periodic": range(1, 9), "bounded_bond": range(1, 5)}
    stage_lines, construction_lines = [], []
    signal.signal(signal.SIGALRM, _alarm)
    t_start = time.time()
    for name, depths in plan.items():
        first_fail, seen, last_reached, note = None, [], None, None
        for depth in depths:
            t0 = time.time()
            signal.alarm(PER_PATTERN_SECONDS)
            try:
                p = build(src, name, depth)
                if len(p.knots) > KNOT_CAP:
                    note = f"stopped before depth {depth}: {len(p.knots)} knots exceed {KNOT_CAP}"
                    signal.alarm(0)
                    break
                stars = [tuple(k) for k in p.knots]
                row = lib.stage_row(stars, len(stars))
                max_holders = max((len(o) for o in p.owners), default=0)
                row.update({"kind": "stage", "population": "P1", "construction": name, "depth": depth,
                            "max_holders_of_a_distinction": max_holders,
                            "seconds": round(time.time() - t0, 2)})
                if row["T"] == "fail" and first_fail is None:
                    first_fail = depth
                    ub, why = lib.upper_removal_bound(stars, None, max_links=600, max_removals=300)
                    row["upper_bound"], row["upper_bound_note"] = ub, why
                seen.append((depth, row["T"]))
                last_reached = depth
                stage_lines.append(row)
            except Slow:
                note = f"depth {depth} not built within {PER_PATTERN_SECONDS} s"
                break
            finally:
                signal.alarm(0)
        monotone = all(not (a[1] == "fail" and b[1] == "pass") for a, b in zip(seen, seen[1:]))
        construction_lines.append({"kind": "construction", "population": "P1", "construction": name,
                                   "depths_reached": [d for d, _ in seen], "verdicts": dict(seen),
                                   "first_failing_depth": first_fail, "monotone": monotone, "note": note})
    lib.dump(lib.OUT / "p1_census.jsonl", stage_lines + construction_lines)
    print(json.dumps({"seconds": round(time.time() - t_start, 1), "constructions": construction_lines}, indent=1))


if __name__ == "__main__":
    main()
