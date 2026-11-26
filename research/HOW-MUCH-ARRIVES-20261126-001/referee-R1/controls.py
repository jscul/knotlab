"""Regrow the controls for the two local readings. Run from any directory.

    .venv/bin/python -B research/HOW-MUCH-ARRIVES-20261126-001/referee-R1/controls.py

The short timing runs use the same starts, signatures and settings as the
full runs. Only the reference checks read the author's JSON; no other study
program is imported. A full run writes controls.json beside this file.
"""

import argparse
import gzip
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations
from pathlib import Path
import resource
from time import perf_counter

from growth import Ordinary, ring_start, row_start


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
READINGS = ("sig0", "sig1")
TWO = "two three-place knots sharing one distinction"
THREE = "three three-place knots in a row"
SEVEN = "bare row of seven knots"
FOUR_RING = "ring of four with two loose distinctions on each knot"
SIX_RING = "ring of six with one leftover distinction"
ADJACENT = "ring of five with two adjacent knots each keeping one leftover"
SEPARATED = "ring of five with two nonadjacent knots each keeping one leftover"
FIVE_BARE = "bare ring of five"
SEVEN_BARE = "bare ring of seven"
DIMENSION_TWO = (TWO, THREE, SEVEN, FOUR_RING, SIX_RING)
STARS = {
    TWO: [[0, 1, 2], [0, 3, 4]],
    THREE: [[0, 1, 2], [1, 3, 4], [3, 5, 6]],
    SEVEN: row_start(7),
    FOUR_RING: ring_start([2, 2, 2, 2]),
    SIX_RING: ring_start([2, 1, 1, 1, 1, 1]),
    ADJACENT: ring_start([3, 3, 2, 2, 2]),
    SEPARATED: ring_start([3, 2, 3, 2, 2]),
    FIVE_BARE: ring_start([2] * 5),
    SEVEN_BARE: ring_start([2] * 7),
}


def regrow(stars, rounds):
    growth = Ordinary(stars)
    counts = []
    local = []
    for _ in range(rounds):
        births = growth.step()
        counts.append(len(births))
        local.append({reading: Counter(getattr(b, reading) for b in births) for reading in READINGS})
    return counts, local


def group_check():
    """Three explicit tests, including an unmet four whose every triple is met."""
    from growth import groups

    # A group of four can have a common knot for each triple without having
    # one for all four. A met triple by itself should yield its three pairs.
    four = range(4)
    examples = [
        (list(combinations(four, 3)), [(0, 1, 2, 3)]),
        ([(0, 1, 2)], [(0, 1), (0, 2), (1, 2)]),
        ([(0, 1), (1, 2), (2, 0), (0, 3)], [(0, 1, 2), (0, 3)]),
    ]
    for met, expected in examples:
        if groups(met) != expected:
            raise AssertionError((met, expected, groups(met)))
    return len(examples)


def five_ring_clusters(loose, rounds):
    """Enumerate the published ring clusters, independently of the growth law.

    A cluster holding ring members consists of one consecutive run in join
    order, and any subset of the leftover members attached to that run. Its
    first member modulo five identifies each translate exactly once.
    """
    marked = tuple(loose[(2 * i) % 5] == 3 for i in range(5))
    sizes = {
        (start, length): sum(marked[(start + j) % 5] for j in range(length))
        for start in range(5) for length in range(1, rounds + 2)
    }

    def signature(start, length, kept):
        a = kept.bit_count()
        if length == 1 and a == 0:
            return ("start", 0, 0, 4 + marked[start])
        parents = a
        if length > 1:
            parents += 2 - (kept & 1) - (kept >> (length - 1))
        fresh = 2 + sizes[start, length] - a
        return ("offshoot" if parents == 1 else "join", parents, fresh, parents + fresh)

    profiles = []
    for t in range(1, rounds + 1):
        local = {reading: Counter() for reading in READINGS}
        for start in range(5):
            for length in range(1, t + 2):
                choose = t + 1 - length
                if choose > sizes[start, length]:
                    continue
                bits = [1 << j for j in range(length) if marked[(start + j) % 5]]
                for selected in combinations(bits, choose):
                    kept = sum(selected)
                    own = signature(start, length, kept)
                    parents = [signature(start, length, kept - bit) for bit in selected]
                    if length > 1 and not (kept & 1):
                        parents.append(signature((start + 1) % 5, length - 1, kept >> 1))
                    if length > 1 and not (kept >> (length - 1)):
                        parents.append(signature(start, length - 1, kept))
                    if own[1] != len(parents):
                        raise AssertionError((start, length, selected, parents))
                    local["sig0"][own] += 1
                    local["sig1"][own + (tuple(sorted(parents)),)] += 1
        profiles.append(local)
    return profiles


def check_ring_readings(runs):
    checks = {}
    for name, loose in ((ADJACENT, [3, 3, 2, 2, 2]), (SEPARATED, [3, 2, 3, 2, 2])):
        began = perf_counter()
        short = five_ring_clusters(loose, 12)
        pilot_seconds = perf_counter() - began
        began = perf_counter()
        grown = runs[name][1]
        clusters = five_ring_clusters(loose, len(grown))
        checks[name] = {
            "checked round signatures": len(grown) * 2,
            "mismatches": [[t, reading] for t, (g, c) in enumerate(zip(grown, clusters), 1)
                           for reading in READINGS if g[reading] != c[reading]],
            "pilot through round 12": {"seconds": round(pilot_seconds, 6), "births": short[-1]["sig0"].total()},
            "seconds through round 32": round(perf_counter() - began, 6),
            "two-parent births at t = 5l + 1, with respectively 2l+3 and 2l+4 fresh": [
                [5 * l + 1, row["sig0"][("join", 2, 2 * l + 3, 2 * l + 5)],
                 row["sig0"][("join", 2, 2 * l + 4, 2 * l + 6)]]
                for l, row in enumerate(grown[::5])
            ],
        }
    return checks


def compare(left, right, runs):
    left_counts, left_local = runs[left]
    right_counts, right_local = runs[right]
    readings = {}
    for reading in READINGS:
        rows = []
        final_witness = {}
        for t, (p, q, n, m) in enumerate(zip(left_local, right_local, left_counts, right_counts), 1):
            a, b = p[reading], q[reading]
            left_only, right_only = a - b, b - a
            lost, gained = left_only.total(), right_only.total()
            damage = lost + gained
            excess = damage - abs(n - m)
            frequencies = Fraction(sum(abs(m * a[k] - n * b[k]) for k in a.keys() | b.keys()), 2 * m * n)
            rows.append([t, n, m, lost, gained, damage, excess, str(frequencies)])
            if t == len(left_local):
                final_witness = {
                    name: [[list(k), v] for k, v in sorted(difference.items())]
                    for name, difference in (("left excess by kind", left_only), ("right excess by kind", right_only))
                }
        readings[reading] = {
            "rows": rows,
            "rounds with damage greater than the count gap": [r[0] for r in rows if r[6]],
            "equal-count rounds with damage": [r[0] for r in rows if r[1] == r[2] and r[5]],
            "last round with damage": max((r[0] for r in rows if r[5]), default=None),
            "last round with damage greater than count gap": max((r[0] for r in rows if r[6]), default=None),
            "final round signature differences": final_witness,
        }
    return {"left": left, "right": right, "readings": readings}


def compare_records(runs, pairs):
    labels = {"two-touching": TWO, "chain3": THREE}
    raw = {label: {"jobs by knot law": Counter(), "base counts compared": 0, "mismatches": []}
           for label in labels.values()}
    with gzip.open(STUDY / "runs.jsonl.gz", "rt") as source:
        for line_number, line in enumerate(source, 1):
            record = json.loads(line)
            if record.get("start") not in labels:
                continue
            label = labels[record["start"]]
            entry = raw[label]
            entry["jobs by knot law"][record["knot law"]] += 1
            counts = record["base counts"]
            if len(counts) != 16:
                entry["mismatches"].append({"line": line_number, "recorded rounds": len(counts)})
            for t, n in enumerate(counts, 1):
                entry["base counts compared"] += 1
                if runs[label][0][t - 1] != n:
                    entry["mismatches"].append([line_number, t, n, runs[label][0][t - 1]])
    control = json.loads((STUDY / "control.json").read_text())["unrelated starts"]
    label_for_control = labels | {"ring5-bare": FIVE_BARE, "ring7-bare": SEVEN_BARE}
    by_pair = {(p["left"], p["right"]): p for p in pairs}
    reference = []
    for recorded in control:
        left, right = (label_for_control[recorded[k]] for k in ("G", "G'"))
        p = by_pair[left, right]
        independent = {"n": runs[left][0], "n'": runs[right][0]}
        for reading in READINGS:
            independent[reading + " damage by round"] = [r[5] for r in p["readings"][reading]["rows"]]
        fields = {}
        for field, values in independent.items():
            old = recorded[field]
            fields[field] = {
                "recorded length": len(old),
                "regrown length": len(values),
                "compared": min(len(values), len(old)),
                "mismatches": [[t, x, y] for t, (x, y) in enumerate(zip(values, old), 1) if x != y],
            }
        reference.append({"left": left, "right": right, "fields": fields})
    return {"recorded 16-round base counts from every job on the two starts": raw,
            "recorded controls to round 32": reference}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Print the timing and count samples only.")
    args = parser.parse_args()
    # A single process, including Python's memory. Nothing is written during the pilots.
    cap = 1500 * 1024**2
    resource.setrlimit(resource.RLIMIT_AS, (cap, cap))
    checked = group_check()
    timing = {}
    for name, stars in STARS.items():
        timing[name] = {}
        for length in (6, 12):
            began = perf_counter()
            counts, _ = regrow(stars, length)
            timing[name][str(length)] = {"seconds": round(perf_counter() - began, 6),
                                         "last round births": counts[-1]}
    if args.pilot:
        print(json.dumps(timing, indent=2))
        return

    runs = {}
    for name, stars in STARS.items():
        began = perf_counter()
        runs[name] = regrow(stars, 32)
        timing[name]["32"] = {"seconds": round(perf_counter() - began, 6),
                              "last round births": runs[name][0][-1]}
    paired = [compare(a, b, runs) for a, b in combinations(DIMENSION_TWO, 2)]
    paired += [compare(ADJACENT, SEPARATED, runs), compare(FIVE_BARE, SEVEN_BARE, runs)]
    ring_check = check_ring_readings(runs)
    report = {
        "law": "Ordinary count under not-all-equal, simultaneous rounds, no extra takes, no short members.",
        "scope": "Three additional connected starts of dimension two; all ten pairs of five such starts. "
                 "Two nonisomorphic five-knot rings with the same proved exponential rate and the recorded pair of bare rings.",
        "selection": "The longer bare row exercises a relay. The four-ring repeats the ends of the three-knot row. "
                     "The six-ring was chosen to put a repeating pair beside a relay. The two five-rings differ "
                     "only in whether their knots keeping leftovers meet.",
        "sources": {
            "growth": ["publication/knotlab/INTUITIONS.md, lesson 8.1",
                       "research/RING-IN-BALANCE-20261123-001/definitions.md, One complete round",
                       "research/PARTS-MEET-AGAIN-20261124-001/definitions.md, sections 1.3 and 2.1"],
            "dimension of the rows": "proofs/RELAY-IDENT-20261119-001A/RELAY-IDENT-20261119-001A-P001_relays/proof.md, "
                                     "Theorem 5, Corollary 6 and validation for the row of seven; "
                                     "research/CHAIN-IDENT-20261119-001/chain_ident.md, The dimension.",
            "dimension of the four-ring": "Direct reduction. Each opposite pair joins through its two common knots "
                                          "and each of its members has two loose distinctions. An isolated knot with "
                                          "two loose distinctions makes exactly such a pair after one round. Thus "
                                          "each part is one round further along the same relay as a part of the "
                                          "two-touching start. They remain separate because each new knot meets only "
                                          "its parents among the old knots. The two parts each make t+2 births in round t.",
            "dimension of the six-ring": "Direct reduction using the alternating groups of three in "
                                         "research/BREAK-EDDIES-20261119-001/break_eddies.md and the relay in "
                                         "proofs/RELAY-IDENT-20261119-001A/RELAY-IDENT-20261119-001A-P001_relays/proof.md, "
                                         "Theorem 4, step 4. After round 1 one part is an isolated knot with one loose "
                                         "distinction; it makes k births in its kth later round. In the other part a join "
                                         "and an offshoot meet a common parent and hold one and two loose distinctions "
                                         "respectively. Each subsequent round makes one join of both and one offshoot of "
                                         "the second; these meet through that same second parent, so their holdings "
                                         "are again one and two. In round t >= 2 the count is (t-1)+2 = t+1. "
                                         "Within the repeating part the join with one fresh distinction persists in every round.",
            "two touching knots": "No common knot joins the two starts. Each separately makes two offshoots; from "
                                  "there each part is the preceding proof's relay shifted by one round. Every join "
                                  "of that relay has two parents and two fresh distinctions. Thus the six-ring carries "
                                  "a local kind absent from the two touching knots at every t >= 2.",
            "equal ring rate": "research/RING-CORES-20261119-001/ring_cores.md, Theorems 3 and 4; "
                               "publication/knotlab/INTUITIONS.md, lesson 8.7, A dial. Each five-ring has lap weight "
                               "y^5(1+y)^2 and exponential rate the positive root of x^7=(x+1)^2, about 1.2628. "
                               "Whether the two knots keeping a leftover meet distinguishes the starts under renaming. "
                               "The rate theorem gives no identity of either local reading.",
        },
        "same-rate rings beyond the checked rounds": {
            "evidence": "A deduction from the ring theorems after the finite comparison. All seven instances through "
                        "round 32 were also counted. This deduction concerns t = 5l+1 for all integers l >= 0.",
            "sources": ["proofs/RING-CORES-20261119-001A/RING-CORES-20261119-001A-P001_rings/proof.md, "
                        "Lemmas 1 and 2 and Theorem 3, steps 1 and 2",
                        "proofs/RING-IDENT-20261119-001A/RING-IDENT-20261119-001A-P001_identification/proof.md, "
                        "Theorem (a) and (b): parents and removable members, loose distinctions and available members",
                        "research/NAE-GROWTH-20261119-001/nae_growth.md, agreement with parity wherever it does not close. "
                        "Each cluster here has at least two available additions."],
            "argument": [
                "A birth of round t is a cluster of size t+1, a consecutive run of ring members in join order "
                "(two steps around the five-ring), together with selected members for leftover distinctions. "
                "If the run has M available leftover members and a are selected, there are 2+M-a possible "
                "additions, the two ends and the available leftovers. This is its fresh count.",
                "At t = 5l+1 the cluster has size 5l+2. If a >= 1 its run has length at most 5l+1, with M <= 2l+1 "
                "since each period of five carries two leftovers. Its fresh count is at most 2l+2.",
                "If a = 0 there are five runs of length 5l+2. Each has two parents, from deleting either end, "
                "and its leftover count is 2l plus the number in a consecutive pair after l full periods. "
                "Two knots adjacent in the start are nonadjacent in join order, and conversely.",
                "With the originally adjacent knots the five pairs contain one leftover four times and two zero times. "
                "With the originally nonadjacent knots the corresponding counts are two and one. Thus the numbers "
                "of two-parent joins with 2l+3 fresh distinguish the rings in one direction (4 versus 2), and those "
                "with 2l+4 fresh distinguish them in the other (0 versus 1). They force damage above the count gap "
                "on all these rounds. Every match under sig1 also matches under sig0, so this holds for both readings."
            ],
            "independent cluster checks": ring_check,
        },
        "starts": {name: {"distinctions of each knot": st, "births in rounds 1 through 32": runs[name][0]}
                   for name, st in STARS.items()},
        "comparison columns": ["round", "births on left", "births on right", "unmatched left", "unmatched right",
                               "damage", "damage above absolute count gap", "total variation with uniform weight per birth"],
        "comparison meaning": "Damage above the absolute count gap is twice the smaller unmatched count. "
                              "A positive value means the count difference alone cannot explain the local damage. "
                              "Total variation compares normalized local-kind counts exactly.",
        "comparisons": paired,
        "record agreement": compare_records(runs, paired),
        "checks": {"synthetic tests of the group rule": checked, "processes": 1,
                   "address limit MiB": 1500, "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
                   "pilot and full timings": timing},
    }
    (HERE / "controls.json").write_text(json.dumps(report, indent=1) + "\n")
    print(f"{len(runs)} starts, {len(paired)} comparisons, 32 rounds. {HERE / 'controls.json'}")


if __name__ == "__main__":
    main()
