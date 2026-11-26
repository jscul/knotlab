"""Compare the extension reader with literal assignments, changes and unrestricted cycle sets."""

import argparse
from collections import Counter
from itertools import combinations
import json
from pathlib import Path
import resource
from random import Random
from time import perf_counter

from cuts_reader import Incidence, bits, inspect, mask, normal, span, words
from cuts_rounds import larger_starts
from replay_growth import ARMS, grow, input_rows


HERE = Path(__file__).resolve().parent


def audit(rows):
    names = sorted({d for row in rows for d in row})
    index = {d: i for i, d in enumerate(names)}
    rows = tuple(tuple(index[d] for d in row) for row in rows)
    stage = Incidence(rows)
    profile = inspect(stage)
    checks = list(map(mask, rows))
    allowed = [w for w in range(1 << len(names)) if all((w & c).bit_count() % 2 == 0 for c in checks)]
    loose = mask(d for d in range(len(names)) if sum(d in r for r in rows) == 1)
    forced = [w for w in allowed if not (w & loose) and all((w & a).bit_count() % 2 == 0 for a in allowed)]
    assert set(forced) == set(words(stage.forced()))
    moves = set()
    for d in range(len(names)):
        choices = [w for w in allowed if w & (1 << d)]
        if choices:
            size = min(w.bit_count() for w in choices)
            moves.update(w for w in choices if w.bit_count() == size)
    generated = stage.projected_moves(stage.all_names)
    assert len(span(generated)) == len(span(moves))
    assert all(not normal(w, span(generated)) for w in moves)
    union = 0
    for word in forced:
        union |= word
    cycles = []
    for w in allowed:
        if not w or w & ~union:
            continue
        touched = [set(r) & set(bits(w)) for r in rows]
        used = [s for s in touched if s]
        if any(len(s) != 2 for s in used):
            continue
        occupied = set(used[0])
        while True:
            before = len(occupied)
            for s in used:
                if occupied & s:
                    occupied.update(s)
            if before == len(occupied):
                break
        if len(occupied) == w.bit_count():
            cycles.append(w)
    answer = {}
    for field, verified in (("all listed supports", False), ("only supports passing K1–K3", True)):
        accepted = []
        for cycle in cycles:
            if any((cycle & m).bit_count() % 2 for m in moves):
                continue
            zero = [a for a in allowed if (cycle & a).bit_count() % 2 == 0]
            one = [a for a in allowed if (cycle & a).bit_count() % 2]
            if not zero or not one:
                continue
            reads = False
            for row in checks:
                if verified and (row.bit_count() < 3 or
                                 len({a & row for a in allowed}) != 1 << (row.bit_count() - 1)):
                    continue
                if not {a & row for a in zero} & {a & row for a in one}:
                    reads = True
                    break
            if not reads:
                accepted.append(cycle)
        totals = Counter()
        for count in range(3, len(accepted) + 1):
            for selected in combinations(accepted, count):
                if any(a & b for a, b in combinations(selected, 2)):
                    continue
                image = {tuple((s & c).bit_count() % 2 for c in selected) for s in allowed}
                if any(sum(v) % 2 for v in image):
                    continue
                totals["complete"] += 1
                totals["minimal"] += int(len(image) == 1 << (count - 1))
        assert profile[field]["candidate cycles"] == len(accepted)
        assert profile[field]["complete splits"] == totals["complete"]
        assert profile[field]["minimal splits"] == totals["minimal"]
        answer[field] = dict(totals)
    return {"distinctions": len(names), "states enumerated": len(allowed), "shortest moves": len(moves),
            "forced sums including zero": len(forced), "unrestricted simple cycles in their union": len(cycles),
            "splits": answer}


def block_examples():
    checks = ((9, 5, 5, "ordinary"), (12, 175, 2, "one_fewer"))
    samples = []
    for size, index, age, arm in checks:
        source = Incidence(list(larger_starts(size, index + 1))[index])
        stage = source
        for _ in range(age):
            rows, status = grow(stage.supports, arm)
            assert status == "funded"
            stage = Incidence(rows)
        before = perf_counter()
        result = inspect(stage, source=source)
        assert result["used independent block constraints on possible label cycles"] and result["complete"]
        samples.append({"growth law": arm, "source knot count": size, "draw": index, "round": age,
                        "source supports": source.supports, "stage supports": stage.supports,
                        "result": result, "seconds": perf_counter() - before})
    return samples


def run(pilot):
    t = perf_counter()
    source_file = HERE.parents[1] / "FORBID-EDITS-20261126-001" / "starts.json"
    starts = json.loads(source_file.read_text())
    rng = Random(271105)
    records, skipped = [], 0
    for n in (3, 4, 5):
        roster = [(i, r) for i, r in enumerate(starts) if r[0] == n]
        for i, (_, meetings, loose) in rng.sample(roster, 16)[:1 if pilot else 16]:
            root = input_rows(meetings, loose)
            records.append({"start": f"census {i}", "stage": "source", **audit(root)})
            for arm in ARMS:
                rows, status = grow(root, arm)
                if status == "funded" and len({d for row in rows for d in row}) <= 14:
                    records.append({"start": f"census {i}", "stage": arm, **audit(rows)})
                elif status == "funded":
                    skipped += 1
    return {"pilot": pilot, "selection": "Sixteen archive positions sampled uniformly without replacement at each size 3, 4 and 5 with one generator seeded 271105. Read the source and every funded first round with up to 14 distinctions.",
            "literal comparisons": records, "funded comparisons over the limit": skipped,
            "seconds": perf_counter() - t}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    parser.add_argument("--block-pilot", action="store_true")
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024 ** 3, 2 * 1024 ** 3))
    if args.block_pilot:
        result = block_examples()
        filename = "cuts_block_pilot.json"
    else:
        result = run(args.pilot)
        filename = "cuts_literal_pilot.json" if args.pilot else "cuts_literal.json"
    (HERE / filename).write_text(json.dumps(result, indent=2) + "\n")
    print(filename)
