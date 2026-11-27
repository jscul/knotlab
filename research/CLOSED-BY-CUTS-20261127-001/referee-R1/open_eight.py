"""Screen open stages for the eight lower clauses with six disjoint carriers."""
import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from itertools import combinations, islice, permutations, product
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

import numpy as np

from growth_replay import LAWS, advance, census_starts, holders, loose, stages

RESEARCH = Path(__file__).resolve().parents[2]
SOURCE = RESEARCH / "UPPER-GROWN-20261127-001" / "referee-R1"
sys.path.insert(0, str(SOURCE))
from large_cores import members, partial_certificates
from large_search import screen

TRANSVERSALS = tuple(product((0, 1), (2, 3), (4, 5)))


def normalized(supports):
    """Normalize distinction labels while preserving each knot's index."""
    ownership = sorted((tuple(knots), x) for x, knots in holders(supports).items())
    new_supports = [[] for _ in supports]
    for name, (knots, _) in enumerate(ownership):
        for knot in knots:
            new_supports[knot].append(name)
    return tuple(map(tuple, new_supports))


def roster(args):
    records = defaultdict(list)
    counts = Counter()
    coverage = Counter()
    starts = census_starts()
    for law in LAWS:
        for index, start in enumerate(starts):
            for turn, supports in stages(start, law, args.through):
                if turn == 0 or not loose(supports):
                    continue
                counts[law, "all formed open"] += 1
                n = len(holders(supports))
                if n < 12:
                    counts[law, "fewer than 12 distinctions"] += 1
                    continue
                coverage[len(supports), n] += 1
                if len(supports) > args.max_knots or n > args.max_distinctions:
                    counts[law, "outside size bounds"] += 1
                    continue
                counts[law, "within size bounds"] += 1
                if args.case is not None and (index, turn) != tuple(args.case):
                    continue
                label = {"law": law, "census start": index, "round": turn}
                records[normalized(supports)].append((label, supports))
    order = sorted(records, key=lambda supports: (
        -len(supports), -len(holders(supports)),
        records[supports][0][0]["census start"], records[supports][0][0]["round"],
        records[supports][0][0]["law"],
    ))
    return order, records, {
        "census starts per law": len(starts),
        "through round": args.through,
        "maximum knots searched": args.max_knots,
        "maximum distinctions searched": args.max_distinctions,
        "selected census entry and round": args.case,
        "coverage counts": {law: {kind: count for (who, kind), count in counts.items() if who == law}
                            for law in LAWS},
        "open stages with at least twelve distinctions by knot and distinction counts": [
            (h, n, count) for (h, n), count in sorted(coverage.items())
        ],
        "distinct normalized systems within size bounds": len(order),
    }


def structural_boxes(signed_triples, readings):
    """Every box has two disjoint opposite transversals and some matching."""
    lookup = set(signed_triples)
    footprints = {
        triple: sum(readings[index][0] for index in triple) for triple in signed_triples
    }
    seen = set()
    for first, second in combinations(sorted(lookup), 2):
        if footprints[first] & footprints[second]:
            continue
        for matching in permutations(second):
            pairs = tuple(zip(first, matching, strict=True))
            if not all(tuple(sorted(pick)) in lookup for pick in product(*pairs)):
                continue
            key = tuple(sorted(tuple(sorted(pair)) for pair in pairs))
            if key in seen:
                continue
            seen.add(key)
            yield tuple((tuple(members(readings[index][0])), readings[index][1])
                        for pair in key for index in pair)


def literal(supports, carriers, *, prefix=None):
    """Read all raw states, or a prefix for timing only."""
    names = sorted(holders(supports))
    names = sorted(set(names) | {x for carrier, _ in carriers for x in carrier})
    columns = {name: i for i, name in enumerate(names)}
    full = 1 << len(names)
    states = np.arange(min(prefix, full) if prefix is not None else full, dtype=np.uint32)
    bits = {name: ((states >> index) & 1).astype(bool) for name, index in columns.items()}

    def agree(carrier):
        value = np.ones(len(states), dtype=bool)
        for member in carrier[1:]:
            value &= bits[carrier[0]] == bits[member]
        return value

    def encode(columns):
        encoded = np.zeros(len(states), dtype=np.uint32)
        for column in columns:
            encoded = (encoded << 1) | column
        return encoded

    def image(word, keep, size):
        counts = np.bincount(word[keep], minlength=1 << size)
        return {f"{code:0{size}b}": int(count) for code, count in enumerate(counts) if count}

    failures = np.zeros(len(states), dtype=np.uint32)
    for support in supports:
        failures += agree(support)
    allowed = failures == 0
    signed = [agree(carrier) == bool(sign) for carrier, sign in carriers]
    lower_words = [encode(signed[index] for index in pick) for pick in TRANSVERSALS]
    upper = [signed[index] != signed[index + 1] for index in (0, 2, 4)]
    upper_word = encode(upper)
    lower_images = [image(word, allowed, 3) for word in lower_words]
    upper_image = image(upper_word, allowed, 3)
    same_knot_both_values = []
    for support in supports:
        fixing = encode(bits[member] for member in support)
        same_knot_both_values.append([
            int(len(np.intersect1d(fixing[allowed & read], fixing[allowed & ~read])))
            for read in signed
        ])
    lower_both_upper_values = [[
        int(len(np.intersect1d(word[allowed & read], word[allowed & ~read])))
        for read in upper
    ] for word in lower_words]
    deletes = [int(np.count_nonzero((failures == 1) & agree(support) & (upper_word == 7)))
               for support in supports]
    results = {
        "enumerated assignments": len(states),
        "full enumeration": len(states) == full,
        "allowed source states": int(np.count_nonzero(allowed)),
        "six signed reading words": image(encode(signed), allowed, 6),
        "eight lower images in signed values": lower_images,
        "upper image": upper_image,
        "source knot fixes admitting both lower reading values": same_knot_both_values,
        "lower triple fixes admitting both upper reading values": lower_both_upper_values,
        "restored upper 111 assignments by source law deletion": deletes,
    }
    seven = {f"{code:03b}" for code in range(7)}
    expected = results["full enumeration"] and all(set(values) == seven for values in lower_images)
    unread = all(min(row) > 0 for row in same_knot_both_values)
    results["strict eight-clause form"] = expected and unread
    results["upper seven-word knot"] = results["full enumeration"] and set(upper_image) == seven
    return results


def removed_cohort(supports, carriers):
    tests = literal(supports, carriers)
    return {
        "upper image": tests["upper image"],
        "eight lower images in signed values": tests["eight lower images in signed values"],
        "strict eight-clause form": tests["strict eight-clause form"],
    }


def search_control(supports, start_size, limit):
    triples, readings, _, stats = screen(supports)
    counts = Counter()
    birth_vectors = Counter()
    for candidate in islice(structural_boxes(triples, readings), limit):
        counts["structural candidates"] += 1
        tested = literal(supports, candidate)
        if not tested["strict eight-clause form"]:
            continue
        counts["strict boxes"] += 1
        if not tested["upper seven-word knot"]:
            continue
        counts["upper seven-word knots"] += 1
        restored = tested["restored upper 111 assignments by source law deletion"]
        counts["all source laws essential"] += all(restored)
        birth_vectors[tuple(sorted(restored[start_size:]))] += 1
    return {
        "screen": stats,
        "candidate prefix": limit,
        "counts": counts,
        "restored upper 111 assignments by birth deletions": [
            {"counts": pair, "boxes": count} for pair, count in sorted(birth_vectors.items())
        ],
    }


def built_control(args):
    old = json.loads((SOURCE / "open_witness.json").read_text())
    start = tuple(map(tuple, old["start"]))
    carriers = tuple((tuple(row), 1) for row in old["six_disjoint_carriers"])
    output = {"start": start, "carriers and signs": carriers, "census member": start in census_starts(),
              "start loose distinctions": loose(start), "laws": {}}
    cached_checks = {}
    cached_searches = {}
    if args.screen_control:
        output["start search"] = search_control(start, len(start), args.limit)
    for law in LAWS:
        first = advance(start, law)
        assert first.status == "funded" and loose(first.supports)
        assert first.supports == tuple(map(tuple, old["grown_supports"]))
        if first.supports not in cached_checks:
            cached_checks[first.supports] = literal(first.supports, carriers, prefix=args.assignment_prefix)
        checks = cached_checks[first.supports]
        if checks["full enumeration"]:
            assert checks["strict eight-clause form"] and checks["upper seven-word knot"]
            assert all(checks["restored upper 111 assignments by source law deletion"])
            before = removed_cohort(start, carriers)
            assert "111" in before["upper image"]
        output["laws"][law] = {
            "round": 1,
            "stage supports": first.supports,
            "stage loose distinctions": loose(first.supports),
            "births": [asdict(birth) for birth in first.births],
            "checks": checks,
        }
        if checks["full enumeration"]:
            output["laws"][law]["without birth laws, retaining their carrier distinctions"] = before
        if args.screen_control:
            if first.supports not in cached_searches:
                cached_searches[first.supports] = search_control(first.supports, len(start), args.limit)
            output["laws"][law]["search"] = cached_searches[first.supports]
    return output


def run(args, out):
    order, records, info = roster(args)
    stop = len(order) if args.limit is None else args.first + args.limit
    selected = order[args.first:stop]
    print(json.dumps({"roster": info, "first": args.first, "selected": len(selected)}),
          file=out, flush=True)
    if args.roster_only:
        return
    for number, key in enumerate(selected, start=args.first):
        started = perf_counter()
        cases = records[key]
        supports = cases[0][1]
        triples, readings, _, stats = screen(supports)
        count = 0
        witnesses = []
        strict = 0
        knot = 0
        for carriers in structural_boxes(triples, readings):
            count += 1
            checks = literal(supports, carriers)
            if not checks["strict eight-clause form"]:
                continue
            strict += 1
            if not checks["upper seven-word knot"]:
                continue
            knot += 1
            old_size = len(census_starts()[cases[0][0]["census start"]])
            previous_size = next(len(prev) for turn, prev in stages(
                census_starts()[cases[0][0]["census start"]], cases[0][0]["law"], through=cases[0][0]["round"] - 1)
                if turn == cases[0][0]["round"] - 1)
            restored = checks["restored upper 111 assignments by source law deletion"]
            witnesses.append({
                "representative": cases[0][0],
                "start supports": census_starts()[cases[0][0]["census start"]],
                "stage supports": supports,
                "stage loose distinctions": loose(supports),
                "carriers and signs": carriers,
                "any birth law essential": any(restored[old_size:]),
                "latest birth law essential": any(restored[previous_size:]),
                "reads born distinctions": sorted({name for carrier, _ in carriers for name in carrier}
                                                   - holders(supports[:old_size]).keys()),
                "without any birth laws": removed_cohort(supports[:old_size], carriers),
                "without latest birth laws": removed_cohort(supports[:previous_size], carriers),
                "checks": checks,
            })
        print(json.dumps({
            "order": number,
            "cases": [label for label, _ in cases],
            "knots": len(supports),
            "distinctions": len(holders(supports)),
            "loose distinctions": len(loose(supports)),
            "screen": stats,
            "structural candidates": count,
            "strict boxes": strict,
            "verified upper knots": knot,
            "witnesses": witnesses,
            "seconds": round(perf_counter() - started, 5),
        }), file=out, flush=True)
        if args.stop_on_success and knot:
            break
        if partial_certificates.cache_info().currsize > 60_000:
            partial_certificates.cache_clear()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--control", action="store_true")
    parser.add_argument("--screen-control", action="store_true")
    parser.add_argument("--assignment-prefix", type=int)
    parser.add_argument("--roster-only", action="store_true")
    parser.add_argument("--through", type=int, default=6)
    parser.add_argument("--max-knots", type=int, default=12)
    parser.add_argument("--max-distinctions", type=int, default=22)
    parser.add_argument("--case", nargs=2, type=int, metavar=("ENTRY", "ROUND"))
    parser.add_argument("--first", type=int, default=0)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--stop-on-success", action="store_true")
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()
    started = perf_counter()
    with args.out.open("w") as out:
        if args.control:
            print(json.dumps(built_control(args)), file=out)
        else:
            run(args, out)
        print(json.dumps({"peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                          "seconds total": round(perf_counter() - started, 5)}), file=out)


if __name__ == "__main__":
    main()
