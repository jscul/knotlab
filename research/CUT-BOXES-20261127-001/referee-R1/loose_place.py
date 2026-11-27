"""Add one loose distinction to a source knot and explicitly place it in a lower carrier."""
import argparse
from collections import Counter
from itertools import product
import json
from pathlib import Path
import time

from upper_check import HERE, TruthTable, as_box
from witness_states import canonical

SOURCE = HERE.parents[1] / "RING-BOND-20261127-001/referee-R1/layer_witness.json"


def lower_images(table, box):
    res = []
    for triple in product(*box):
        image = ["".join(map(str, bits)) for bits in product((0, 1), repeat=3)
                 if table.forbidden_states([(r[0], b) for r, b in zip(triple, bits)])]
        res.append(image)
    return res


def source_tests(table, knots, readings):
    # Individual input flips and single-knot unreadability on allowed states.
    import numpy as np
    allowed = np.ones(len(table.states), dtype=bool)
    for knot in knots:
        mask = sum(1 << x for x in knot)
        v = table.states & mask
        allowed &= (v != 0) & (v != mask)
    states = table.states[allowed]
    flips, fixes = [], []
    for carrier in readings:
        m = sum(1 << x for x in carrier)
        bits = states & m
        agrees = (bits == 0) | (bits == m)
        counts = []
        for x in carrier:
            changed = states ^ (1 << x)
            b = changed & m
            different = agrees != ((b == 0) | (b == m))
            counts.append(int(np.count_nonzero(allowed[changed] & different)) // 2)
        flips.append(counts)
        fixes.append([len(set((states[agrees] & sum(1 << x for x in k)).tolist()) &
                          set((states[~agrees] & sum(1 << x for x in k)).tolist())) for k in knots])
    return flips, fixes


def audit(limit):
    previous = json.loads(SOURCE.read_text())
    base = previous["source_knots_not_all_equal"]
    original = previous["lower_carriers_in_A0_A1_B0_B1_C0_C1_order"]
    counts, positives = Counter(), []
    for q in range(limit):
        knots = [k.copy() for k in base]
        knots[q].append(18)
        table = TruthTable(knots)
        for i, c in enumerate(original):
            for removed in [*c, None]:
                name = "append" if removed is None else "replace"
                readings = [r.copy() for r in original]
                readings[i] = [x for x in c if x != removed] + [18]
                box = as_box([[(readings[j], 1), (readings[j + 1], 1)] for j in (0, 2, 4)])
                counts[name + "_checked"] += 1
                if any(table.forbidden_states(triple) for triple in product(*box)):
                    continue
                images = lower_images(table, box)
                if not all(len(image) == 7 for image in images):
                    continue
                missing, needed = table.upper(box)
                flips, fixes = source_tests(table, knots, readings)
                if missing == ["111"] and all(min(k) > 0 for k in flips + fixes):
                    counts[name + "_box"] += 1
                    counts[name + "_all_laws_needed"] += len(needed) == 12
                    six_words = sum(bool(table.forbidden_states(tuple(zip(map(tuple, readings), values))))
                                    for values in product((0, 1), repeat=6))
                    positives.append({"six_words": six_words, "changed_knot": q, "changed_carrier": i, "removed": removed,
                                      "carriers": readings, "allowed": table.allowed.bit_count(),
                                      "upper_missing": missing, "essential_laws": needed,
                                      "minimum_member_flip_pairs": min(map(min, flips)),
                                      "minimum_unread_fixes": min(map(min, fixes))})
        table.equal.cache_clear()
    return {"source": str(SOURCE.relative_to(HERE.parents[2])), "source_knots": base,
            "fresh_distinction": 18, "counts": counts, "positives": positives,
            "canonical_common_lower_and_upper_measured_image": canonical(["~A ~B ~C"], ["A", "B", "C"])}


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--limit", type=int, default=12)
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    start = time.monotonic()
    result = audit(args.limit)
    result["elapsed_seconds"] = round(time.monotonic() - start, 4)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(result["counts"], result["elapsed_seconds"])
