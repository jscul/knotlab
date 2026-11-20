"""Independent small source-subset proof for the first-layer triple changes."""

from collections import Counter
from hashlib import sha256
from itertools import combinations
import json

from side_cert import ARTIFACTS, Wired, checked_shore, orientations, sources


def connected_extension(old, inside, binary):
    """Retain only the least-cost binary links needed between old components."""
    parent = {v: v for v in inside}

    def root(v):
        while parent[v] != v:
            v = parent[v]
        return v

    for v in sorted(inside):
        for u in old.near[v].keys() & inside:
            parent[root(u)] = root(v)
    penalty = 0
    bridges = []
    for cost, child, a, b in binary:
        if a in inside and b in inside and root(a) != root(b):
            parent[root(a)] = root(b)
            bridges.append(child)
            penalty += cost
    if len({root(v) for v in inside}) == 1:
        return penalty, bridges
    return None


def minimize(old, first, marks, binary, ceiling):
    opens = old.near[old.outside]
    stars = [sum(1 << bit for bit in row) for row in old.stars]
    alternatives = []
    verified = []
    for pins in orientations(first, marks):
        inside = {v for v, c in pins.items() if c == 1}
        free = set(range(old.outside)) - pins.keys()
        base_open = sum(opens[v] for v in inside)
        budget = ceiling - len(marks) - base_open
        counts = Counter()
        best = None
        for size in range(budget // min(opens.values()) + 1):
            for chosen in combinations(sorted(free), size):
                if sum(opens[v] for v in chosen) > budget:
                    continue
                counts["within_opening_bound"] += 1
                side = inside.union(chosen)
                row = 0
                for v in side:
                    row ^= stars[v]
                initial = row.bit_count()
                if initial > ceiling:
                    continue
                counts["within_old_cut_bound"] += 1
                direct = connected_extension(old, side, binary)
                if direct is None:
                    counts["disconnected_for_all_child_choices"] += 1
                    continue
                extra, bridges = direct
                if initial + extra > ceiling:
                    counts["bridge_exceeds_budget"] += 1
                    continue
                counts["eligible"] += 1
                witness = checked_shore(first, marks, side.union(bridges))
                assert witness and witness["cost"] == initial + extra
                if best is None or witness["cost"] < best["cost"]:
                    best = witness
        alternatives.append({"pins": sorted(pins.items()), "counts": dict(counts),
                             "witness": best, "lower_cost": best["cost"] if best else ceiling + 1})
        if best:
            verified.append(best)
    return {"marks": list(marks), "orientations": alternatives,
            "min_cost": min(row["cost"] for row in verified)}


def run():
    result = {}
    for case in ("T4", "PT4"):
        spec = sources.cases()[case]
        s, r = spec["roles"]["seams"]
        rows = result[case] = {}
        for arm, state in sources.loads(spec).items():
            stages = sources.generate(spec, state, 1, sources.CAPS)
            age0, raw = next(stages)
            age1, grown = next(stages)
            assert age0 == 0 and age1 == 1
            old, first = Wired(raw["stars"]), Wired(grown["stars"])
            binary = []
            for birth in grown["births"]:
                p, f = len(birth["parents"]), len(birth["fresh"])
                assert p in (1, 2) and f >= p
                if p == 2:
                    binary.append((f - 2, birth["knot"], *birth["parents"]))
            binary.sort()
            targets = ((s, s + 1, s + 2), (r - 3, r - 2, r - 1))
            readings = []
            for marks in targets:
                actual = tuple(spec["roles"]["anchors"][i] for i in marks)
                assert all(s <= i < r for i in marks)
                row = minimize(old, first, actual, binary, 16)
                row["path_positions"] = marks
                readings.append(row)
            assert [row["min_cost"] for row in readings] == [
                14 + 2 * bool(int(arm) & 1), 14 + 2 * bool(int(arm) & 2)
            ]
            rows[arm] = {
                "literal_stars_sha256": sha256(json.dumps(grown["stars"], separators=(",", ":")).encode()).hexdigest(),
                "queries": readings,
            }
    return {"unit": "bond size", "ceiling": 16, "cases": result}


if __name__ == "__main__":
    output = ARTIFACTS / "side_cert_first.json"
    temporary = output.with_suffix(".tmp")
    temporary.write_text(json.dumps(run(), sort_keys=True, separators=(",", ":")) + "\n")
    temporary.replace(output)
