"""Check birth legality of the reported odd minima outside the census-start roster."""

import gzip
import json
from collections import Counter, defaultdict
from itertools import combinations
from operator import xor
from functools import reduce

from birth import HERE, RESEARCH, build_cells, can_close_odd, forbid, holdings, pairs_at_birth, reader_kind


def check_row(row, knots, eligible, stats, readers=None):
    cells = build_cells(knots, eligible)
    whole_sign = reduce(xor, (c.column for c in cells), 0)
    assert (bool(cells) and whole_sign < 2) == row["whole closure a carrier"]
    assert row["whole closure sign"] == (whole_sign if cells and whole_sign < 2 else None)
    legal = [c for c in cells if c.legal]
    natural = reduce(xor, (c.column for c in legal), 0)
    stats["rows"] += 1
    stats["rows where birth excludes a finished candidate"] += len(eligible) < len(cells)
    stats["finished candidates"] += len(cells)
    stats["birth-eligible candidates"] += len(eligible)
    stats["whole closure closes odd with all finished candidates"] += whole_sign == 1
    stats["whole closure closes odd with all eligible candidates"] += natural == 1
    stats["some eligible choice closes odd"] += can_close_odd(legal)
    odd = [m for m in row["minimal carriers"] if m["sign"]]
    strict = False
    legal_min = False
    forbidden = []
    for m in odd:
        mask = sum(1 << i for i in m["set"])
        selected = [c for c in cells if c.owners & mask == c.owners]
        assert len(selected) == m["cells"] and reduce(xor, (c.column for c in selected), 0) == 1
        for size in range(4, len(m["set"])):
            for subset in combinations(m["set"], size):
                submask = sum(1 << i for i in subset)
                smaller = [c for c in selected if c.owners & submask == c.owners]
                assert not smaller or reduce(xor, (c.column for c in smaller), 0) > 1
        is_legal = all(c.legal for c in selected)
        split = reader_kind(selected, knots)
        assert (split == "strict" and m["kind"] == "four mutually meeting knots") or (split == "no split" and m["cells"] == 6)
        strict |= split == "strict" and is_legal
        legal_min |= is_legal
        if not is_legal:
            forbidden.append({"set": m["set"], "forbidden pairs": [c.pair for c in selected if not c.legal]})
        stats["reported odd minimal sets"] += 1
        stats["reported odd minimal sets, birth eligible"] += is_legal
        stats["reported odd minimal sets, strict reader split"] += split == "strict"
        stats["reported odd minimal sets, no reader split"] += split == "no split"
    stats["rows with a reported odd minimum"] += bool(odd)
    stats["rows with an eligible reported odd minimum"] += legal_min
    stats["rows with an eligible strictly splitting odd minimum"] += strict
    if readers is not None and odd and not strict:
        stats["rows with only nonsplitting minima, another choice splits"] += readers["general"]
        stats["rows with only nonsplitting minima, no other choice splits"] += not readers["general"]
    return forbidden


def finished_types(rows):
    census = RESEARCH.parent / "artifacts/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules/census.json"
    holds = json.loads(census.read_text())
    with (RESEARCH / "READER-SPLIT-20261127-001/census_types.jsonl").open() as handle:
        readers = {r["type"]: r for r in map(json.loads, handle)}
    assert len(readers) == len(holds) == len(rows)
    by_size = defaultdict(Counter)
    for row in rows:
        index = row["type"]
        raw = holds[index]
        knots = [[] for _ in range(raw["n"])]
        for d, (u, v) in enumerate(raw["sharing"]):
            knots[u].append(d)
            knots[v].append(d)
        # The finished types declare every unheld pair eligible. They have no birth history.
        eligible, _, _ = pairs_at_birth([knots])
        assert not check_row(row, knots, eligible, by_size[len(knots)], readers[index])
    return dict(sorted(by_size.items()))


def sampled_closures(rows, name):
    by_round = defaultdict(Counter)
    forbidden = []
    if name == "extension":
        roster = forbid.extension()
    else:
        roster = [s for n in (6, 7, 8) for s in forbid.sampled(n, 10000, 20261200 + n)]
    for row in rows:
        index = row["start index"]
        stages = [forbid.supports_of(roster[index])]
        for _ in range(row["rounds"]):
            assert any(len(owners) == 1 for owners in holdings(stages[-1]).values())
            next_stage, status, _ = forbid.grown(stages[-1], "parity", "ordinary")
            assert status == "funded"
            stages.append(next_stage)
        knots = stages[-1]
        assert len(knots) == row["knots"]
        eligible, _, first_natural_failure = pairs_at_birth(stages)
        result = check_row(row, knots, eligible, by_round[row["rounds"]])
        if result:
            forbidden.append({"sampled start index": index, "round": row["rounds"], "odd minima": result})
        by_round[row["rounds"]]["full natural choice keeps a state"] += first_natural_failure is None
    return {"by closing round": dict(sorted(by_round.items())), "birth-forbidden odd minima": forbidden}


def main():
    by_population = defaultdict(list)
    with gzip.open(HERE.parent / "rows.jsonl.gz", "rt") as handle:
        for row in map(json.loads, handle):
            by_population[row["population"]].append(row)
    result = {
        "weighting": "One vote per census type or sampled start. One per subset per type or sampled closure in minimum counts.",
        "scope": "All reported odd minimal subsets of the additional rosters rechecked for eligibility, sign, split, and absence of a smaller whole-choice set. The finished types have no birth history and allow all unheld pairs.",
        "finished types by number of knots": finished_types(by_population["census types"]),
    }
    for name in ("extension", "second sample"):
        result[name] = sampled_closures(by_population[name], name)
    (HERE / "birth_other.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
