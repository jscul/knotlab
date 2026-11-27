"""Audit exact flipping sizes and the scale-five class facts from reconstructed stages.

A distinction carries one or two incidences. Add an auxiliary holder for all loose
distinctions. The allowed changes are exactly the even subgraphs of this multigraph,
since the parity equation at the auxiliary holder is implied by all the other ones.
The calculation uses only those incidences and the supplied parity support.
"""

import argparse
import hashlib
import itertools
import json
import random
import resource
import time
from collections import Counter, deque
from pathlib import Path


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
PREDECESSOR = STUDY.parent / "BUILT-BINDING-20261126-001" / "referee-R1" / "ring_counts.json"


def indices(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


class BinarySpan:
    def __init__(self, masks=()):
        self.pivots = {}
        for mask in masks:
            self.add(mask)

    def __iter__(self):
        return iter(self.pivots.values())

    def __len__(self):
        return len(self.pivots)

    def _reduce(self, mask):
        while mask:
            row = self.pivots.get(mask.bit_length())
            if row is None:
                break
            mask ^= row
        return mask

    def __contains__(self, mask):
        return self._reduce(mask) == 0

    def add(self, mask):
        mask = self._reduce(mask)
        if not mask:
            return False
        self.pivots[mask.bit_length()] = mask
        return True


class Incidence:
    def __init__(self, supports):
        self.names = tuple(sorted({d for law in supports for d in law}))
        self.index = {d: i for i, d in enumerate(self.names)}
        self.distinction_count = len(self.names)
        self.auxiliary = len(supports)
        holders = [[] for _ in self.names]
        for knot, law in enumerate(supports):
            if len(law) != len(set(law)):
                raise ValueError(f"repeated distinction in knot {knot}")
            for distinction in law:
                holders[self.index[distinction]].append(knot)
        self.neighbors = [[] for _ in range(len(supports) + 1)]
        self.holders = []
        for i, incidence in enumerate(holders):
            if len(incidence) == 1:
                incidence.append(self.auxiliary)
            if len(incidence) != 2:
                raise ValueError(f"distinction {self.names[i]} has {len(incidence)} holders")
            a, b = incidence
            self.holders.append((a, b))
            self.neighbors[a].append((b, i))
            self.neighbors[b].append((a, i))
        self.law_masks = tuple(self.mask(law) for law in supports)
        self.laws = BinarySpan(self.law_masks)

    def mask(self, support):
        mask = 0
        for distinction in support:
            mask ^= 1 << self.index[distinction]
        return mask

    def least(self, support):
        return self.least_mask(self.mask(support))

    def least_mask(self, support):
        """Shortest odd closed walk, using breadth-first search in two parity copies.

        Every odd closed walk contains an odd simple cycle after cancelling repeated
        distinctions and decomposing into simple cycles. A least odd cycle goes through
        a marked distinction, so testing one holder of each marked distinction suffices.
        """
        if support in self.laws:
            return None
        roots = set()
        for index in indices(support):
            a, b = self.holders[index]
            roots.add(b if b == self.auxiliary else a)
        best = self.distinction_count + 1
        for root in roots:
            even = root * 2
            odd = even + 1
            length = [-1] * (2 * len(self.neighbors))
            length[even] = 0
            queue = deque([even])
            while queue:
                current = queue.popleft()
                next_length = length[current] + 1
                if next_length >= best:
                    break
                for holder, index in self.neighbors[current // 2]:
                    next_parity = (current & 1) ^ ((support >> index) & 1)
                    target = holder * 2 + next_parity
                    if length[target] < 0:
                        length[target] = next_length
                        queue.append(target)
                if length[odd] >= 0:
                    best = length[odd]
                    break
            if best == 2:
                break
        if best > self.distinction_count:
            raise AssertionError("nonconstant parity without an odd simple cycle")
        return best

    def move_span(self, maximum):
        """Span every allowed change of at most the supplied number of distinctions.

        Root a shortest-path tree in each holder, through depth floor(maximum/2).
        For a simple cycle C of length l, any root on C has enough depth to reach
        every holder on C. For consecutive holders u,v the tree depth sum is at
        most l-1. The fundamental cycle from uv and the two tree paths has at most
        l distinctions. Adding these fundamental cycles for all uv in C cancels the
        tree paths and recovers C. Parallel distinctions give cycles of length two.
        """
        span = BinarySpan()
        if maximum < 2:
            return span
        depth_limit = maximum // 2
        for root in range(len(self.neighbors)):
            depth = [-1] * len(self.neighbors)
            depth[root] = 0
            paths = [0] * len(self.neighbors)
            queue = deque([root])
            while queue:
                current = queue.popleft()
                if depth[current] == depth_limit:
                    continue
                for holder, index in self.neighbors[current]:
                    if depth[holder] < 0:
                        depth[holder] = depth[current] + 1
                        paths[holder] = paths[current] ^ (1 << index)
                        queue.append(holder)
            for index, (a, b) in enumerate(self.holders):
                if depth[a] >= 0 and depth[b] >= 0:
                    cycle = paths[a] ^ paths[b] ^ (1 << index)
                    if cycle and cycle.bit_count() <= maximum:
                        span.add(cycle)
        return span


def sums_of(masks):
    sums = [0]
    for mask in masks:
        sums += [value ^ mask for value in sums]
    return sums


def archived_value(exact, cap):
    if exact is None or exact <= cap:
        return exact
    return f"more than {cap}"


def controls():
    """Compare shortest walks and rooted spans to literal subset enumeration."""
    rng = random.Random(20261126)
    examples = [((0, 1, 2), (1, 2, 3)), ((2, 4), (4, 6), (6, 2)),
                ((0, 1), (1, 2), (3, 4), (4, 5)), ((0,),)]
    for _ in range(24):
        supports = [[] for _ in range(5)]
        for distinction in range(10):
            for holder in rng.sample(range(5), rng.choice((1, 2, 2))):
                supports[holder].append(10 * distinction + 1)
        examples.append(tuple(tuple(law) for law in supports))
    support_checks = 0
    span_checks = 0
    for supports in examples:
        model = Incidence(supports)
        changes = [mask for mask in range(1 << model.distinction_count)
                   if all((mask & row).bit_count() % 2 == 0 for row in model.law_masks)]
        for support in range(1 << model.distinction_count):
            expected = min((z.bit_count() for z in changes if (z & support).bit_count() % 2), default=None)
            assert model.least_mask(support) == expected, (supports, support)
            support_checks += 1
        for cap in range(model.distinction_count + 1):
            expected = BinarySpan(z for z in changes if z.bit_count() <= cap)
            found = model.move_span(cap)
            assert len(expected) == len(found) and all(z in expected for z in found), (supports, cap)
            span_checks += 1

    caps = []
    for size in (39, 40, 41):
        model = Incidence(tuple((i, (i + 1) % size) for i in range(size)))
        exact = model.least((0,))
        assert exact == size and model.least((0, 1)) is None
        caps.append({"one cyclic allowed change of size": size, "exact minimum": exact,
                     "at cap 40": archived_value(exact, 40), "fixed parity at cap 40": None})
    assert [row["at cap 40"] for row in caps] == [39, 40, "more than 40"]
    return {"small incidence patterns": len(examples), "least flip comparisons": support_checks,
            "short move span comparisons": span_checks, "cap convention on known minima": caps}


def project_moves(source, model, moves):
    """Keep source distinctions, with positions in the source's own sorted ordering."""
    source_positions = tuple(model.index[d] for d in source.names)
    if source_positions == tuple(range(len(source_positions))):
        old = (1 << len(source_positions)) - 1
        projected = BinarySpan(move & old for move in moves)
    else:
        projected = BinarySpan(sum(((move >> j) & 1) << i for i, j in enumerate(source_positions))
                               for move in moves)
    assert all(not (move & law).bit_count() % 2 for move in projected for law in source.law_masks)
    return projected


def archive(which, pilot):
    from growth import families, load_starts, stages

    path = STUDY / f"frozen_{which}.jsonl"
    rows = [json.loads(line) for line in path.read_text().splitlines()]
    starts = zip(load_starts(which), rows, strict=True)
    if pilot:
        starts = itertools.islice(starts, 2)
    counts = Counter()
    sizes = Counter()
    ends = Counter()
    nonfamily_dims = Counter()
    mismatches = []
    examples = {}
    for (name, supports), record in starts:
        assert (name, len(supports)) == (record["start"], record["knots"])
        counts["starts"] += 1
        _, family_supports = families(supports)
        family_count = len(family_supports)
        assert family_count == record["families"]
        source = Incidence(supports)
        before, first = None, None
        scale_five = {}
        for (round_number, stage, status, _), row in zip(stages(supports), record["rounds"], strict=True):
            assert round_number == row["round"]
            if status != "stage":
                ends[status] += 1
                if row.get("end") != status:
                    mismatches.append([name, round_number, "end status", row.get("end"), status])
                continue
            counts["stages"] += 1
            model = source if round_number == 0 else Incidence(stage)
            masks = [model.mask(support) for support in family_supports]
            selections = sums_of(masks)
            minima = [None] + [model.least_mask(mask) for mask in selections[1:]]
            if before is None:
                first = minima
            for selection, minimum in enumerate(minima[1:], 1):
                counts["all family selections"] += 1
                if minimum is None:
                    counts["fixed family selections"] += 1
                else:
                    counts["nonconstant family selections"] += 1
                if before is None:
                    continue
                if (before[selection] is None) != (minimum is None):
                    mismatches.append([name, round_number, "fixed status changed", selection,
                                       before[selection], minimum])
                if minimum is None or before[selection] is None or first[selection] is None:
                    continue
                counts["nonconstant family selections compared between rounds"] += 1
                change = minimum - before[selection]
                if change < 2 or minimum < first[selection] + 2 * round_number:
                    mismatches.append([name, round_number, "T(iii) growth below bound", selection,
                                       first[selection], before[selection], minimum])
                if change == 2:
                    counts["nonconstant family selections grew by exactly two"] += 1
                elif change > 2:
                    counts["nonconstant family selections grew by more than two"] += 1

            singletons = [minima[1 << i] for i in range(family_count)]
            counts["archived family minima"] += len(singletons)
            counts["nonconstant archived family minima"] += sum(value is not None for value in singletons)
            sizes.update("fixed" if value is None else str(value) for value in singletons)
            encoded = [archived_value(value, 40) for value in singletons]
            if encoded != row.get("least flips"):
                mismatches.append([name, round_number, "family minima", row.get("least flips"), encoded])

            if round_number >= 2:
                changes = model.move_span(5)
                dimension = model.distinction_count - len(model.laws) - len(changes)
                projected = project_moves(source, model, changes)
                dimension_old = source.distinction_count - len(source.laws) - len(projected)
                if dimension != dimension_old:
                    mismatches.append([name, round_number, "class facts outside the source span", dimension,
                                       dimension_old])
                scale_five[round_number] = (dimension, projected)
                if round_number == 2:
                    counts["additional round-two scale-five dimensions"] += 1
                else:
                    membership = [mask not in model.laws and all(not (mask & z).bit_count() % 2 for z in changes)
                                  for mask in masks]
                    expected = all(membership) if family_count >= 2 else None
                    counts["archived scale-five dimensions"] += 1
                    counts["archived scale-five membership verdicts"] += expected is not None
                    counts["scale-five nonconstant family membership checks"] += sum(v is not None for v in singletons)
                    if expected is not None and not expected:
                        mismatches.append([name, round_number, "T4 class fact membership", membership])
                    if (row.get("UPTO5 class facts"), row.get("every l_A a class fact")) != (dimension, expected):
                        mismatches.append([name, round_number, "T4 archive comparison", row, [dimension, expected]])
                    family_span = BinarySpan(itertools.chain(model.laws, masks))
                    extra = dimension + len(model.laws) - len(family_span)
                    nonfamily_dims[str(extra)] += 1
                    if extra and "scale five above family span" not in examples:
                        examples["scale five above family span"] = {"start": name, "round": round_number,
                                                                   "class fact rank": dimension,
                                                                   "rank of family parities modulo laws": dimension - extra}
            before = minima
        if 3 in scale_five:
            d2, projected2 = scale_five[2]
            d3, projected3 = scale_five[3]
            counts["additional paired round-two and round-three dimensions"] += 1
            same_span = len(projected2) == len(projected3) and all(mask in projected2 for mask in projected3)
            if d2 == d3 and same_span:
                counts["paired round-two and round-three identical source class spaces"] += 1
            else:
                mismatches.append([name, "round-two and round-three source class spaces changed", d2, d3])
        if 3 in scale_five and 4 in scale_five:
            counts["paired round-three and round-four dimensions"] += 1
            d3, projected3 = scale_five[3]
            d4, projected4 = scale_five[4]
            if d3 != d4:
                mismatches.append([name, "T4 dimension change", d3, d4])
            if len(projected3) == len(projected4) and all(mask in projected3 for mask in projected4):
                counts["paired round-three and round-four identical source class spaces"] += 1
            else:
                mismatches.append([name, "source class spaces changed"])
    return {"archive sha256": hashlib.sha256(path.read_bytes()).hexdigest(), "counts": dict(counts),
            "least flip frequency": dict(sizes), "ends": dict(ends),
            "scale-five class fact rank in excess of family span frequency": dict(nonfamily_dims),
            "examples": examples, "differences": mismatches}


def built_ring_minima(pilot):
    """Recompute the claimed ring and attachment flipping sizes on the built starts."""
    from growth import families, ring_start, stages

    archive_path = STUDY / "frozen_scale_read.jsonl"
    scale_rows = {row["family"]: row for row in map(json.loads, archive_path.read_text().splitlines())}
    pairs = list(itertools.product((3, 4), (4, 5, 6, 7), ("split", "paired"), ("double", "detour")))
    if pilot:
        pairs = [pairs[0], pairs[4], pairs[8], pairs[-1]]
    cases = []
    differences = []
    counts = Counter()
    for number, size, attachment, link in pairs:
        label = f"{number} rings of {size}, {attachment}, {link}"
        supports, rings, loose = ring_start(number, size, attachment, link)
        _, family_supports = families(supports)
        original = Incidence(supports)
        ring_knots = {knot for ring in rings for knot in ring}
        connector_knots = sorted(set(range(len(supports))) - ring_knots)
        attachments = {knot: tuple(d for d in supports[knot]
                                  if any(owner in ring_knots for owner in original.holders[original.index[d]]))
                       for knot in connector_knots}
        attachments = {knot: value for knot, value in attachments.items() if value}
        assert all(len(value) == 2 for value in attachments.values())
        case = {"start": label, "connector attachment supports": attachments, "rounds": []}

        # The source record cites all 32 ring patterns through round 3. The
        # separate large-scale read needs round 4 only for the three-ring starts.
        for round_number, stage, status, _ in stages(supports, rounds=4 if number == 3 else 3, cap=1000):
            if status != "stage":
                differences.append([label, round_number, "unexpected stop", status])
                continue
            model = Incidence(stage)
            ring_flips = [model.least(support) for support in loose]
            connector_flips = {knot: model.least(support) for knot, support in attachments.items()}
            case["rounds"].append({"round": round_number, "distinctions": model.distinction_count,
                                   "least ring flips": ring_flips, "least connector attachment flips": connector_flips})
            counts["built ring minimum measurements"] += len(ring_flips)
            counts["built connector attachment minimum measurements"] += len(connector_flips)
            if round_number <= 3:
                counts["built ring minimum measurements in conjecture B citation"] += len(ring_flips)
                if ring_flips != [5 + 2 * round_number] * number:
                    differences.append([label, round_number, "conjecture B ring minima", ring_flips])
            if label == "3 rings of 5, split, double":
                expected = [5, 7, 9, 11, 12][round_number]
                counts["preadvertised attachment minimum measurements"] += len(connector_flips)
                if set(connector_flips.values()) != {expected} or ring_flips != [5 + 2 * round_number] * number:
                    differences.append([label, round_number, "exploratory flipping-size claim",
                                        ring_flips, connector_flips])
            if number == 3 and round_number == 4:
                row = scale_rows[label]
                if "end" in row:
                    counts["size-cap omissions checked separately"] += 1
                    if model.distinction_count <= 300 or row["end"] != f"not read: {model.distinction_count} distinctions":
                        differences.append([label, "scale size cap", row["end"], model.distinction_count])
                    continue
                flips = [model.least(support) for support in family_supports]
                case["scale-read family minima"] = flips
                counts["archived scale-read family minima"] += len(flips)
                scale = min(value for value in flips if value is not None) - 1
                if row["least flips"] != flips or row["scale"] != scale or model.distinction_count > 300:
                    differences.append([label, "scale minimum or cap", row, flips, scale, model.distinction_count])
        cases.append(case)
    return {"counts": dict(counts), "measurements": cases, "differences": differences,
            "scale archive sha256": hashlib.sha256(archive_path.read_bytes()).hexdigest(),
            "predecessor record sha256": hashlib.sha256(PREDECESSOR.read_bytes()).hexdigest()}


def main():
    from growth import SETS

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Check a small exact roster through the same entry point")
    parser.add_argument("--out", type=Path, help="Write JSON here instead of standard output")
    args = parser.parse_args()
    if args.pilot and args.out:
        parser.error("the pilot prints to standard output")
    start = time.monotonic()
    checked = controls()
    results = {which: archive(which, args.pilot) for which in SETS}
    built = built_ring_minima(args.pilot)
    elapsed = time.monotonic() - start
    peak = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    if args.pilot:
        print(json.dumps({"controls": checked, "archives": {k: v["counts"] for k, v in results.items()},
                          "built ring audit": built["counts"], "seconds": round(elapsed, 3),
                          "maximum resident KiB": peak}, indent=2))
    else:
        totals = Counter()
        for row in results.values():
            totals.update(row["counts"])
        report = {"controls": checked, "archives": results, "totals": dict(totals), "built ring audit": built,
                  "maximum resident KiB": peak, "elapsed seconds": round(elapsed, 3), "processes": 1}
        encoded = json.dumps(report, indent=2) + "\n"
        if args.out:
            args.out.write_text(encoded)
            print(json.dumps({"totals": totals, "built ring audit": built["counts"], "seconds": round(elapsed, 3),
                              "maximum resident KiB": peak}, indent=2))
        else:
            print(encoded, end="")
    differences = sum(len(result["differences"]) for result in results.values()) + len(built["differences"])
    if differences:
        raise SystemExit(f"{differences} differences, recorded in the output")


if __name__ == "__main__":
    main()
