"""Check the first far member of small fully funded starts, after round three."""
from collections import Counter
from itertools import product
import json
from random import Random
import sys
from time import process_time

from inference import comparison, groups, sharing


END = {
    "one": [[0, 1, 2]],
    "four-loose": [[0, 1, 2, 3]],
    "two": [[0, 1, 2], [0, 3, 4]],
    "two-share-two": [[0, 1, 2], [0, 1, 3]],
    "three-mutual": [[0, 1, 3], [0, 2, 4], [1, 2, 5]],
    "three-in-order": [[0, 1, 3], [0, 4, 5], [1, 6, 7]],
    "three-mutual-extra": [[0, 1, 3, 6], [0, 2, 4, 7], [1, 2, 5, 8]],
}
TAKES = ("sole", "oldest", "newest", "one-parent-step", "two-parent-steps")


def meeting(receiver, sender, steps):
    places = [list(row) for row in END[receiver]]
    owners = [0] * len(places)
    end = len(places)
    n = 1 + max(d for row in places for d in row)
    for row in END[sender]:
        places.append([n + d for d in row])
        owners.append(1)
    n += 1 + max(d for row in END[sender] for d in row)
    left = 0
    for i in range(steps):
        right = end
        if i < steps - 1:
            right = len(places)
            places.append([])
            owners.append(2)
        places.append([n, n + 1, n + 2])
        owners.append(2)
        places[left].extend([n, n + 3])
        places[right].extend([n + 1, n + 2, n + 4])
        n += 5
        left = right
    return places, owners


def small_starts(seed, number):
    rng = Random(seed)
    for i in range(number):
        size = rng.randrange(3, 7)
        side = rng.randrange(1, size)
        owners = [0] * side + [1] * (size - side)
        places = [[] for _ in range(size)]
        for d in range(size + rng.randrange(1, size + 1)):
            holders = rng.sample(range(size), rng.choices((2, 3), (4, 1))[0])
            for u in holders:
                places[u].append(d)
        if any(not row for row in places):
            continue
        _, meets = sharing(places)
        owed = Counter(u for q in groups(range(size), meets) for u in q)
        nxt = 1 + max(max(row) for row in places)
        for u, row in enumerate(places):
            h = max(3 - len(row), 1, owed[u]) + rng.randrange(2)
            row.extend(range(nxt, nxt + h))
            nxt += h
        yield str(i), places, owners


def longer_designs(later):
    if not later:
        for a, b in product(END, repeat=2):
            p, o = meeting(a, b, 3)
            for take in TAKES:
                yield ("three meetings", a, b, take, 1, 3, p, o)
    for a, b in product(END, repeat=2):
        p, o = meeting(a, b, 3)
        for take in TAKES:
            yield ("three meetings", a, b, take, 3, 3, p, o)
    for name, p, o in small_starts(20261126, 96):
        for take in TAKES:
            yield ("other starts", name, "", take, 3, 2, p, o)


def longer(pilot, later):
    counts = Counter()
    witness = []
    began = process_time()
    tried = 0
    for kind, a, b, take, when, span, p, o in longer_designs(later):
        if pilot and tried >= 5:
            break
        if process_time() - began > 20:
            break
        tried += 1
        try:
            row = comparison(take, when, span, p, o, nearest_rank=0)
        except ValueError as exc:
            counts["before setting: " + str(exc)] += 1
            continue
        if row.get("rounds") and not row["rounds"][-1]["same"]:
            witness.append({"kind": kind, "receiver": a, "sender": b, "places": p, "owners": o,
                            "reading": row})
            break
        counts[row.get("stop", row.get("observed", "no change in completed window"))] += 1
    return {"designs_read": tried, "counts": dict(counts), "witness": witness,
            "cpu_seconds": round(process_time() - began, 6)}


def run(mode):
    cases = [(a, b, t, d) for d in (3, 1) for a, b in product(END, repeat=2) for t in TAKES]
    if mode == "pilot":
        cases = cases[:5]
    counts = Counter()
    total = 0
    output = []
    started = process_time()
    for a, b, take, d in cases:
        if process_time() - started > 24:
            break
        places, owners = meeting(a, b, d)
        total += 1
        try:
            result = comparison(take, 3, 1, places, owners)
            if "observed" in result:
                counts[result["observed"]] += 1
            elif not result["rounds"]:
                counts["both ends available, " + result["stop"]] += 1
            elif result["rounds"][-1]["same"]:
                counts["unheard in round 4"] += 1
            else:
                counts["heard in round 4"] += 1
                output.append({"receiver": a, "sender": b, "meetings": d, "places": places,
                               "owners": owners, "result": result})
                if mode != "pilot":
                    break
        except ValueError as exc:
            counts["before setting, " + str(exc)] += 1
    return {"designs_read_in_listed_order": total, "designs_scheduled": len(cases),
            "counts": dict(counts), "witness": output, "cpu_seconds": round(process_time() - started, 6)}


if __name__ == "__main__":
    mode = sys.argv[1]
    if mode.startswith(("longer", "later")):
        result = longer(mode.endswith("pilot"), mode.startswith("later"))
    else:
        result = run(mode)
    print(json.dumps(result, indent=2))
