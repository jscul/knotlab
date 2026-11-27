"""Direct truth-table checks for the six readings and single-law removals."""

import argparse
import json
import resource
import time
from itertools import product

from step_readings import DEFINING, HERE, NAMED, StageCheck, chain_carriers, open_rows


def intersection(sets, universe):
    answer = universe
    for item in sets:
        answer &= item
    return answer


def columns(n):
    states = 1 << n
    result = []
    for j in range(n):
        half = 1 << j
        data = ((1 << half) - 1) << half
        width = 2 * half
        while width < states:
            data |= data << width
            width *= 2
        result.append(data)
    return result


def raw_check(supports, chain, carriers):
    names = sorted({x for knot in supports for x in knot})
    universe = (1 << (1 << len(names))) - 1
    raw = dict(zip(names, columns(len(names))))

    def equal(group):
        return intersection((raw[x] for x in group), universe) | intersection((~raw[x] for x in group), universe)

    def fixes(group):
        for word in product((0, 1), repeat=len(group)):
            yield intersection((v if w else ~v for w, v in zip(word, group)), universe)

    source = [universe ^ equal(knot) for knot in supports]
    allowed = intersection(source, universe)
    reads = [equal(group) for group in carriers]

    def image(bits):
        return sum(1 << k for k, part in enumerate(fixes(bits)) if part & allowed)

    upper = [[(a & b) if i == role else (a | b) for i, (a, b) in enumerate(zip(reads[::2], reads[1::2]))]
             for role in range(3)]
    missing_targets = [intersection(group, universe) for group in upper]
    restores = []
    for law in chain:
        without = intersection(source[:law] + source[law + 1:], universe)
        restores.append(sum(1 << role for role, target in enumerate(missing_targets) if target & without))
    source_failures = [[] for _ in reads]
    for i, knot in enumerate(supports):
        groups = [allowed & f for f in fixes([raw[x] for x in knot])]
        for j, value in enumerate(reads):
            if not any(g & value and g & ~value for g in groups):
                source_failures[j].append(i)
    return {"allowed_states": allowed.bit_count(), "possible_raw_assignments": 1 << len(names),
            "image": image(reads), "lower": [image([reads[i] for i in idx]) for idx in DEFINING],
            "upper": list(map(image, upper)), "source_failures": source_failures, "restore": restores}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    start = time.perf_counter()
    bare = [tuple(range(2 * i, 2 * i + 3)) for i in range(8)]
    chain = list(range(8))
    cases = [
        ("bare eight-knot chain", bare, chain, NAMED),
        ("one extra law breaks a lower triple", bare + [(0, 1, 5)], chain, NAMED),
        ("one extra law leaves four lower triples intact and removes an upper word", bare + [(0, 1, 15)], chain, NAMED),
        ("two extra laws leave the lower and upper words intact and make two removals insufficient",
         bare + [(0, 1, 17), (3, 5, 17)], chain, NAMED),
    ]
    first = next(open_rows(HERE / "step_stages.jsonl.gz"))
    chain = first["chains"][2]
    stage = first["supports"]
    cases.append(("third chain on the fourth grown round of the three-knot census entry 2",
                  stage, chain, chain_carriers(stage, chain)))
    if args.pilot:
        cases = cases[:1]
    results = []
    for title, stage, chain, carriers in cases:
        exact = raw_check(stage, chain, carriers)
        checks = StageCheck(stage)
        try:
            check = checks.check(chain)
        finally:
            checks.close()
        for key in ("image", "lower", "upper", "restore"):
            assert exact[key] == check[key], (title, key, exact[key], check[key])
        assert exact["source_failures"] == [list(laws) for laws in check["source_failures"]]
        results.append({"control": title, **exact, "frozen": check["frozen"], "every_law": check["every_law"]})
    if not args.pilot:
        assert results[0]["frozen"] and results[0]["every_law"]
        assert min(results[1]["lower"]) != 127
        assert all(x == 127 for x in results[2]["lower"]) and min(results[2]["upper"]) != 127
        assert results[3]["frozen"] and not results[3]["every_law"]
        assert results[4]["frozen"] and results[4]["every_law"]
    output = {"controls": results, "wall_seconds": time.perf_counter() - start,
              "peak_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    suffix = "_pilot" if args.pilot else ""
    (HERE / f"step_controls{suffix}.json").write_text(json.dumps(output, indent=2) + "\n")
    print(output["wall_seconds"], output["peak_kib"])


if __name__ == "__main__":
    main()
