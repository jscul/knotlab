"""Replay the source holdings and the first round at which each pair could be decided."""

import argparse
from collections import Counter, defaultdict
from itertools import combinations
import json
from pathlib import Path
import sys
from time import monotonic


HERE = Path(__file__).resolve().parent
RESEARCH = HERE.parents[1]
ENGINE = RESEARCH / "FORBID-EDITS-20261126-001"
PRIOR = RESEARCH / "READER-SPLIT-20261127-001" / "referee-R1"
CENSUS = RESEARCH.parent / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
sys.path.insert(0, str(ENGINE))
import forbid


def history(start):
    current = forbid.supports_of(start)
    stages = [current]
    while True:
        counts = Counter(d for knot in current for d in knot)
        if all(copies == 2 for copies in counts.values()):
            return ("grown closed" if len(stages) > 1 else "initially closed"), stages
        new, status, _ = forbid.grown(current, "parity", "ordinary")
        if status == "stalled":
            return "stalled", stages
        assert status == "funded"
        if len(stages) == 5:
            return "growing", stages
        if len(new) > 40:
            return "cut", stages
        stages.append(new)
        current = new


def columns(stages):
    # Holdings of older knots are permanent. Each distinction gets two dates:
    # first holder and second holder. One must have two holders at the later birth.
    holders = defaultdict(list)
    old = 0
    for t, stage in enumerate(stages):
        for k in range(old, len(stage)):
            for d in stage[k]:
                holders[d].append((t, k))
        old = len(stage)
    assert all(len(h) == 2 for h in holders.values())
    pairs = []
    # Test oddness independently. A dependency with sign one exists iff the
    # zero check column with sign one belongs to the span of the augmented columns.
    pivots = {}
    knots = len(stages[-1])
    for a, b in combinations(sorted(holders), 2):
        ((ta, u), (sa, v)), ((tb, w), (sb, x)) = holders[a], holders[b]
        if min(sa, sb) > max(ta, tb) or len({u, v, w, x}) < 4:
            continue
        pairs.append([a, b])
        col = int((u < w < v) != (u < x < v))
        for i in (u, v):
            for j in (w, x):
                col ^= 1 << (1 + knots * min(i, j) + max(i, j))
        while col:
            lead = col.bit_length()
            if lead not in pivots:
                pivots[lead] = col
                break
            col ^= pivots[lead]
    return pairs, 1 in pivots


def check_row(stages, record, pairs, odd):
    assert ([list(k) for k in stages[-1]], pairs, odd, len(stages) - 1) == (
        record["supports"], record["pairs"], record["odd"], record["round"])


def main(limit):
    start_time = monotonic()
    starts = json.loads((ENGINE / "starts.json").read_text())
    previous = {(r["population"], r["key"]): r for r in
                map(json.loads, (PRIOR / "rebuilt_inputs.jsonl").open())}
    outcomes = Counter()
    confirmed = set()
    for index, start in enumerate(starts[:limit]):
        outcome, stages = history(start)
        outcomes[outcome] += 1
        if outcome != "grown closed":
            continue
        pairs, odd = columns(stages)
        if odd:
            check_row(stages, previous["birth", index], pairs, odd)
            confirmed.add(index)
    expected = {key for pop, key in previous if pop == "birth" and (limit is None or key < limit)}
    assert confirmed == expected
    print(dict(outcomes), len(confirmed), round(monotonic() - start_time, 2), flush=True)
    if limit is not None:
        return
    census = json.loads(CENSUS.read_text())
    for index, row in enumerate(census):
        ends = row["sharing"]
        knots = [[d for d, pair in enumerate(ends) if i in pair]
                 for i in range(1 + max(max(pair) for pair in ends))]
        pairs, odd = columns([knots])
        check_row([knots], previous["type", index], pairs, odd)
    assert set(range(len(census))) == {key for pop, key in previous if pop == "type"}
    result = {"weighting": "one per archived census start, separately one per finished type",
              "start_roster": len(starts), "outcomes": outcomes, "grown_closed_attaining_odd": len(confirmed),
              "census_types_compared": len(census), "disagreements_in_holders_pairs_round_or_oddness": 0}
    (HERE / "birth_inputs.json").write_text(json.dumps(result, indent=1) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, help="Pilot on this prefix of census starts.")
    main(parser.parse_args().limit)
