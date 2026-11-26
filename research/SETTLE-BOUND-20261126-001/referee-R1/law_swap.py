"""Check whether changing the law supplies a second test on surviving starts."""
import argparse
from collections import Counter, defaultdict
from itertools import islice
import json
import time

from regrow import grow
from settling import HERE, STUDY, SMALL, READINGS, block_size, dimension, earliest, read_archive


def compare(size, limit):
    before = time.monotonic()
    nae = read_archive(STUDY / f"grown_g{size}_nae.jsonl.gz")
    parity = read_archive(STUDY / f"grown_g{size}_par.jsonl.gz")
    counts, exceptional = Counter(), defaultdict(list)
    for a, b in islice(zip(nae, parity, strict=True), limit):
        assert (a["index"], a["stars"]) == (b["index"], b["stars"])
        counts["paired starts"] += 1
        if a["M"] != b["M"]:
            counts["different M"] += 1
        identical = all(a[field] == b[field] for field in ("rows", "end", "kind", "knots", "M"))
        if identical:
            counts["identical saved growth, end, dimension or other label, knot total and M"] += 1
        if b["kind"].startswith("dim"):
            counts["parity dimension starts"] += 1
            if identical:
                counts["parity dimension starts with identical inputs to both readings and bound"] += 1
            else:
                exceptional["parity dimension with changed record"].append(b["index"])
        if not identical:
            counts[f"different records / {a['kind']} to {b['kind']}"] += 1
            if b["end"].startswith("closes"):
                end = len(b["rows"])
                assert end >= 1 and end <= len(a["rows"])
                if a["rows"][:end-1] == b["rows"][:-1]:
                    counts["differing records identical until the parity closing birth"] += 1
                assert a["rows"][end-1]["n"] == b["rows"][-1]["n"] == 1
                ap, bp = a["rows"][end-1]["sig1"][0][0], b["rows"][-1]["sig1"][0][0]
                assert ap[1] == bp[1] and ap[0][:2] == bp[0][:2] and bp[0][2] == 0 < ap[0][2]
                counts["differing records with same closing birth kind and parent signatures, different fresh count"] += 1
    return {"counts": counts, "exceptions": dict(exceptional), "elapsed seconds": round(time.monotonic()-before, 3)}


def small_starts(limit):
    """The original fit used not-all-equal. Check the same census under parity."""
    counts = Counter()
    offsets = {reading: Counter() for reading in READINGS}
    before = time.monotonic()
    for start in islice(read_archive(SMALL), limit):
        result = grow(start["stars"], "parity", rounds=20)
        counts["parity starts regrown"] += 1
        if result["end"].startswith(("stalls", "closes")):
            counts[result["end"].split()[0]] += 1
            continue
        rows = result["rows"]
        d = dimension([row["n"] for row in rows])
        assert d is not None
        counts["dimension starts"] += 1
        neighbours, _ = block_size(start)
        fresh = max(kind[2] for kind in rows[0]["sig0"])
        m = max(neighbours, fresh)
        for reading in READINGS:
            k = earliest([row[reading] for row in rows], d, 3)
            offsets[reading][k - m] += 1
    return {"counts": counts, "K minus M": offsets, "elapsed seconds": round(time.monotonic()-before, 3)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    data = {n: compare(n, 64 if args.pilot else None) for n in (5, 6)}
    data["calibration census under parity"] = small_starts(24 if args.pilot else None)
    (HERE / ("law_swap_pilot.json" if args.pilot else "law_swap.json")).write_text(json.dumps(data, indent=1) + "\n")
    print(json.dumps(data))


if __name__ == "__main__":
    main()
