"""Regrow the two state-identification witnesses with the general referee rule."""
import argparse
import json
from pathlib import Path
import resource
from time import perf_counter

from growth import advance

HERE = Path(__file__).resolve().parent


def verify(case):
    entries = sorted((int(k), tuple(row)) for k, row in case["start_rows"].items())
    tags = [key for key, _ in entries]
    supports = tuple(row for _, row in entries)
    stage, status, births = advance(supports)
    assert status == "funded" and len(births) == 3
    assignment = {}
    for birth in births:
        assert len(birth.parents) == 1 and not birth.implied and birth.demand == 0
        p = str(tags[birth.parents[0]])
        assert birth.inputs == (case["start_loose"][p],)
        expected = case["births"][p]
        assert len(birth.fresh) == len(expected["fresh"]) == 2
        assignment.update(zip(birth.fresh, expected["fresh"], strict=True))
    fresh = set(assignment)
    old = {x for row in supports for x in row}
    assert len(fresh) == 6 and old.isdisjoint(assignment.values())
    laws = list(supports)
    for b in births:
        laws.append(tuple(assignment.get(x, x) for x in stage[b.knot]))
    # Check the full row span, not just the rank or the count of allowed states.
    span = {0}
    for row in laws:
        mask = sum(1 << x for x in row)
        span |= {v ^ mask for v in span}
    return span


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--pilot", action="store_true")
    args = p.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (256 << 20, 256 << 20))
    start = perf_counter()
    data = json.loads((HERE / "metric_witness.json").read_text())
    cases = data["cases"][:1] if args.pilot else data["cases"]
    results = [verify(case) for case in cases]
    assert all(len(s) == 1 << 15 for s in results)
    if not args.pilot:
        assert results[0] == results[1]
    print(len(results), "presentations,", len(results[0]), "sums of laws in each,", round(perf_counter()-start, 5), "seconds")
