"""Literal replay of the seven-knot predictions and a separate check of the four-law witness."""

import argparse
from collections import Counter, defaultdict
import itertools
import json
import os
from pathlib import Path
import resource
import subprocess
import sys
from time import perf_counter

from growth_rule import advance


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parent
TREE = ((0, 1, 2), (0, 3, 6), (1, 4, 7), (2, 5, 8), (3, 9, 10), (4, 11, 12), (5, 13, 14))
FUNDED_TREE = tuple(row + ((14 + i,) if 1 <= i <= 3 else ()) for i, row in enumerate(TREE))
RING = tuple(tuple(9 if x == 11 else x for x in row) for row in TREE)
SIGNS = "-0+"


def read_bits(state, names):
    return tuple((state >> x) & 1 for x in names)


def inspect_seven(rows, *, close_ring=False, augmented=False, portion=1):
    multiplicities = Counter(x for row in rows for x in row)
    names = sorted(multiplicities)
    boundary = tuple(x for x in names if multiplicities[x] == 1)
    mask_loose = sum(1 << x for x in boundary)
    masks = tuple(sum(1 << x for x in row) for row in rows)
    allowed = Counter()
    sign_counts = defaultdict(Counter)
    forcing = defaultdict(lambda: defaultdict(set))
    joint = defaultdict(set)
    arms = [(i + 6, 9 + 2*i, 10 + 2*i) for i in range(3)]
    if close_ring:
        arms = [tuple(9 if x == 11 else x for x in arm) for arm in arms]
    readings = {"original": arms}
    if augmented:
        readings["extended"] = [arm + (15+i,) for i, arm in enumerate(arms)]
    for word in range((1 << len(names)) // portion):
        # The ring's names skip 11. Retain the source names for comparisons.
        state = ((word & 2047) | ((word >> 11) << 12)) if close_ring else word
        if any((state & mask) in (0, mask) for mask in masks):
            continue
        allowed[state & mask_loose] += 1
        for label, blocks in readings.items():
            signs = []
            for i, block in enumerate(blocks):
                a, b, c, *extra = read_bits(state, block)
                nonzero = b == c and a != b and all(value == a for value in extra)
                sign = ("+" if a else "-") if nonzero else "0"
                signs.append(sign)
                forcing[label][f"{i} {sign}"].add((state >> i) & 1)
            triple = "".join(signs)
            sign_counts[label][triple] += 1
            joint[label].add((state & mask_loose, triple))
    if portion != 1:
        return {"allowed_in_pilot": sum(allowed.values())}
    allwords = set(itertools.product(SIGNS, repeat=3))
    result = {
        "states": sum(allowed.values()),
        "loose_distinctions": boundary,
        "loose_patterns": len(allowed),
        "loose_possible": 2**len(boundary),
        "missing_loose_patterns": [
            "".join(map(str, bits)) for bits in itertools.product((0, 1), repeat=len(boundary))
            if sum(value << x for value, x in zip(bits, boundary)) not in allowed
        ],
        "readings": {},
    }
    for label, blocks in readings.items():
        words = sign_counts[label]
        result["readings"][label] = {
            "carriers": blocks,
            "disjoint": sum(map(len, blocks)) == len(set(itertools.chain.from_iterable(blocks))),
            "multiplicities": dict(sorted(words.items())),
            "missing": sorted("".join(t) for t in allwords if "".join(t) not in words),
            "pair_support_sizes": [len({(s[a], s[b]) for s in words}) for a,b in itertools.combinations(range(3), 2)],
            "center_values_by_reading": {k: sorted(v) for k,v in sorted(forcing[label].items())},
            "distinct_joint_loose_word_and_reading": len(joint[label]),
        }
    return result


def canonical_birth(rows, carriers, omit):
    """Forget the actual seven distinctions in the source and carrier laws."""
    named = [f"d{x}" for x in range(7)]
    clauses = []
    for i, row in enumerate(rows):
        if i != omit:
            clauses.append(" ".join(named[x] for x in row))
            clauses.append(" ".join("~" + named[x] for x in row))
    for bit, carrier in zip("FGH", carriers, strict=True):
        for word in itertools.product((0, 1), repeat=len(carrier)):
            clause = [("~" if v else "") + named[x] for v, x in zip(word, carrier)]
            clause.append(("" if len(set(word)) == 1 else "~") + bit)
            clauses.append(" ".join(clause))
    query = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", "; ".join(clauses),
             "--loops", "F", "G", "--contact", "H", "--witnesses", *named, "--json"]
    checked = subprocess.run(query, cwd=HERE.parents[2], env={**os.environ, "PYTHONPATH": "tools"},
                             capture_output=True, check=True, text=True)
    return json.loads(checked.stdout)


def four_laws(pilot):
    # The old ring and its ordinary birth are rebuilt here by the literal
    # rule for this start: three parents, one input each, no later demand.
    old = ((0, 1, 3), (0, 2, 4), (1, 2, 5))
    stage = old + ((3, 4, 5, 6),)
    assert advance(old).supports == stage
    views = {}
    formal = {}
    carriers = ((0, 5), (2, 3), (1, 4, 6))
    for omit in (None, 0, 1, 2, 3):
        counts = Counter()
        for bits in itertools.product((0, 1), repeat=7):
            if all(i == omit or len({bits[x] for x in row}) == 2 for i, row in enumerate(stage)):
                # This numbering has opposite pairs (0,5), (1,4), (2,3).
                view = (bits[0] == bits[5], bits[2] == bits[3], bits[1] == bits[4] == bits[6])
                counts["".join(str(int(v)) for v in view)] += 1
        views[str(omit)] = dict(sorted(counts.items()))
        if not pilot or omit is None:
            check = canonical_birth(stage, carriers, omit)
            assert set(check["allowed"]) == set(counts)
            assert check["is_knot"] == (omit is None)
            formal[str(omit)] = check
    return {"supports": stage, "carriers": carriers, "by_omitted_law": views,
            "canonical_checks_forgetting_underlying_distinctions": formal}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1536*1024**2, 1536*1024**2))
    start = perf_counter()
    data = {
        key: inspect_seven(rows, close_ring=ring, augmented=aug, portion=32 if args.pilot else 1)
        for key, rows, ring, aug in (("tree", TREE, False, False), ("ring", RING, True, False),
                                    ("funded_tree", FUNDED_TREE, False, True))
    }
    data["independent_four_law_replay"] = four_laws(args.pilot)
    if not args.pilot:
        ref = json.loads((SOURCE / "t7.json").read_text())
        tree, ring, funded = (data[x] for x in ("tree", "ring", "funded_tree"))
        signs = tree["readings"]["original"]
        comparisons = {
            "N1 states": tree["states"],
            "N2 loose patterns": [tree["loose_patterns"], tree["loose_possible"]],
            "N3 triples of (g0, g1, g2)": len(signs["multiplicities"]),
            "N3 missing triples": [list(x) for x in signs["missing"]],
            "N3 pairs": signs["pair_support_sizes"],
            "N4 ring control: loose patterns": [ring["loose_patterns"], ring["loose_possible"]],
            "N4 ring control: states": ring["states"],
            "N5 T7 round 1": advance(TREE).status,
            "N5 T7 with 15, 16, 17: states": funded["states"],
            "N5 T7 with 15, 16, 17: loose patterns": [funded["loose_patterns"], funded["loose_possible"]],
            "N5 its round 1": advance(FUNDED_TREE).status,
            "N5 stage after one round: knots": len(advance(FUNDED_TREE).supports),
        }
        for key,value in comparisons.items():
            if value != ref[key]:
                raise AssertionError((key, value, ref[key]))
        data["archive_fields_matched"] = list(comparisons)
        data["archive_field_checked_in_growth_replay"] = sorted(ref.keys() - comparisons.keys())
        data["fresh_extension_certificate"] = [
            {"parents": b.parents, "inputs": b.inputs, "fresh": b.fresh} for b in advance(FUNDED_TREE).births
        ]
        views = data["independent_four_law_replay"]["by_omitted_law"]
        assert set(views["None"]) == {format(i,"03b") for i in range(8)} - {"001"}
        assert all(len(v)==8 for k,v in views.items() if k != "None")
        (HERE / "seven_counts.json").write_text(json.dumps(data, indent=2) + "\n")
    print(f"{'Pilot' if args.pilot else 'Complete'} {perf_counter()-start:.3f}s, peak {resource.getrusage(resource.RUSAGE_SELF).ru_maxrss} KiB")


if __name__ == "__main__":
    main()
