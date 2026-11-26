"""Replay the made-mark pairs and audit the recorded comparison of knot laws."""

import argparse
import gzip
import json
import sys
from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ENGINE = (
    ROOT / "experiments/WHAT-A-BIRTH-CARRIES-20261125-001B"
    / "WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot"
)
sys.path.insert(0, str(ENGINE))
import eng


LAST_ROUND = 16
KNOT_CAP = 20_000
READINGS = ("name", "sig0", "sig1")
LAWS = ("nae", "parity")


def ring(size, loose):
    return [
        [(knot - 1) % size, knot, *range(size + knot * loose, size + (knot + 1) * loose)]
        for knot in range(size)
    ]


STARTS = {
    "two-touching": [[0, 1, 2], [0, 3, 4]],
    "chain3": [[0, 1, 2], [1, 3, 4], [3, 5, 6]],
    "ring5-bare": ring(5, 2),
    "ring7-bare": ring(7, 2),
    "ring5-eddy": ring(5, 3),
    "generator7": [
        [0, 1, 2, 9, 10, 11], [0, 1, 3], [4, 5, 12, 13, 14],
        [6, 7, 15, 16, 17], [2, 3, 4, 6, 18, 19, 20],
        [7, 8, 21, 22], [5, 8, 23, 24],
    ],
}


def ordinary(knot_law):
    return eng.Law("ORD", "CANCEL-WAIT", None, knot_law)


def make_start(start, change=None, at=None):
    places = [knot.copy() for knot in STARTS[start]]
    if change == "mark":
        places[at].append(1 + max(map(max, places)))
    elif change == "move":
        source, destination = at
        counts = Counter(d for knot in places for d in knot)
        moved = next(d for d in reversed(places[source]) if counts[d] == 1)
        places[source].remove(moved)
        places[destination].append(moved)
    return places


def check_connected_pairs(places):
    """Check the hypotheses for reading parity implication through loose distinctions."""
    holders = defaultdict(list)
    for knot, distinctions in enumerate(places):
        for d in distinctions:
            holders[d].append(knot)
    assert all(len(knots) <= 2 for knots in holders.values())
    meets = defaultdict(set)
    for knots in holders.values():
        if len(knots) == 2:
            first, second = knots
            meets[first].add(second)
            meets[second].add(first)
    reached = {0}
    pending = [0]
    while pending:
        new = meets[pending.pop()] - reached
        reached.update(new)
        pending.extend(new)
    assert len(reached) == len(places)


class PairReplay:
    """Keep only the three readings needed for a comparison of round births."""

    def __init__(self, state, names, signatures, symbols):
        self.state = state
        self.names = names
        self.signatures = signatures
        self.symbols = symbols

    @classmethod
    def start(cls, places):
        names = {knot: knot for knot in range(len(places))}
        signatures = {
            knot: ("start", 0, 0, len(distinctions))
            for knot, distinctions in enumerate(places)
        }
        return cls(eng.from_stars(places), names, signatures, {})

    def with_marks(self, knots):
        state = self.state.copy()
        signatures = self.signatures.copy()
        for knot in knots:
            new = state.n_distinctions
            state.places[knot].append(new)
            state.holders.append([knot])
            state.barred.append(False)
            state.maker.append(knot)
            signatures[knot] = (*signatures[knot][:-1], len(state.places[knot]))
        state.basis = {}
        for places in state.places:
            eng.basis_insert(state.basis, eng.row_of(places))
        return PairReplay(state, self.names.copy(), signatures, self.symbols)

    def grow(self, through):
        readings = {}
        guard = eng.Guard(100)
        while self.state.round < through:
            row = eng.play_round(self.state, ordinary("nae"), guard)
            assert row["births"] and self.state.n_knots <= KNOT_CAP
            seen = Counter()
            at_round = {reading: Counter() for reading in READINGS}
            for birth in row["births"]:
                knot, kind, parents = birth["id"], birth["kind"], birth["parents"]
                ancestry = kind, tuple(sorted(self.names[parent] for parent in parents))
                symbol = ancestry, seen[ancestry]
                seen[ancestry] += 1
                name = self.symbols.setdefault(symbol, self.state.n_start + len(self.symbols))
                size = len(self.state.places[knot])
                sig0 = kind, len(parents), birth["f"], size
                sig1 = (*sig0, tuple(sorted(self.signatures[parent] for parent in parents)))
                self.names[knot] = name
                self.signatures[knot] = sig0
                for reading, value in zip(READINGS, ((name, birth["f"], size), sig0, sig1)):
                    at_round[reading][value] += 1
            readings[row["round"]] = at_round
        return readings


def unmatched(base, changed):
    matched = (base & changed).total()
    return [changed.total() - matched, base.total() - matched]


def compare_pair_start(start, raw_pair, raw_single, smoke):
    replay = PairReplay.start(STARTS[start])
    prefix = replay.grow(2)
    made = [k for k, when in enumerate(replay.state.made) if when == 2]
    assert len(made) == raw_pair["made"] == 6
    all_pairs = list(combinations(made, 2))
    by_pair = {tuple(row["knots"]): row for row in raw_pair["pairs"]}
    assert len(raw_pair["pairs"]) == len(by_pair) and set(by_pair) == set(all_pairs)
    selected = all_pairs[:1] if smoke else all_pairs

    base = prefix | replay.with_marks(()).grow(LAST_ROUND)
    base_counts = [b["name"].total() for b in base.values()]
    assert base_counts == raw_pair["base counts"] == raw_single["base counts"]
    assert raw_pair["base_stop"] is None and raw_single["base_stop"] is None
    solo = {}
    raw_solo = {mark["knot"]: mark for mark in raw_single["marks"]}
    assert len(raw_single["marks"]) == raw_single["marked"] == len(made)
    assert set(raw_solo) == set(made)
    for knot in sorted({knot for pair in selected for knot in pair}):
        trajectory = replay.with_marks((knot,)).grow(LAST_ROUND)
        raw_mark = raw_solo[knot]
        assert raw_mark["stop"] is None and raw_mark["struck"] is None
        assert list(trajectory) == [r["round"] for r in raw_mark["rows"]]
        for row in raw_mark["rows"]:
            before, changed = base[row["round"]], trajectory[row["round"]]
            assert before["name"].total() == row["n"]
            assert changed["name"].total() == row["n'"]
            for reading in READINGS:
                assert unmatched(before[reading], changed[reading]) == row[reading]
        solo[knot] = trajectory[LAST_ROUND]

    counts = {reading: Counter() for reading in READINGS}
    checks = []
    before = base[LAST_ROUND]
    for first, second in selected:
        together = replay.with_marks((first, second)).grow(LAST_ROUND)[LAST_ROUND]
        runs = solo[first], solo[second], together
        damages = {r: [sum(unmatched(before[r], growth[r])) for growth in runs] for r in READINGS}
        expected = by_pair[first, second]
        assert expected["round"] == LAST_ROUND and expected["damage u, v, both"] == damages
        for reading, (u, v, both) in damages.items():
            if both < min(u, v):
                counts[reading]["below either single mark"] += 1
            if both < u + v:
                counts[reading]["below the sum of the single marks"] += 1
            elif both == u + v:
                counts[reading]["equal to the sum of the single marks"] += 1
            else:
                counts[reading]["above the sum of the single marks"] += 1
        checks.append({
            "knots": [first, second],
            "damage u, v, both": damages,
            "birth counts base, u, v, both": [b["name"].total() for b in (before, *runs)],
        })
    return {
        "round": LAST_ROUND,
        "single marks checked": len(solo),
        "single mark rounds checked": len(solo) * (LAST_ROUND - 2),
        "counts": {
            reading: {label: count[label] for label in (
                "below either single mark", "below the sum of the single marks",
                "equal to the sum of the single marks", "above the sum of the single marks",
            )}
            for reading, count in counts.items()
        },
        "pairs": checks,
    }


def key(row):
    at = row.get("at")
    return row["start"], row["change"], tuple(at) if isinstance(at, list) else at, row.get("round")


def scientific_fields(row):
    return {field: value for field, value in row.items() if field not in ("seconds", "knot law")}


def recorded_laws(jobs):
    """Compare every saved field and identify rounds cut off by the matched-window read."""
    expected = set()
    for start, places in STARTS.items():
        check_connected_pairs(places)
        counts = Counter(d for knot in places for d in knot)
        for knot, distinctions in enumerate(places):
            expected.add((start, "mark", knot, None))
            if any(counts[d] == 1 for d in distinctions):
                expected.update((start, "move", (knot, dest), None)
                                for dest in range(len(places)) if dest != knot)
        expected.add((start, "made", None, 2))
    assert len(expected) == 161

    by_law = {law: {} for law in LAWS}
    for row in jobs:
        if "knot law" in row and key(row) in expected:
            law_jobs = by_law[row["knot law"]]
            assert key(row) not in law_jobs
            law_jobs[key(row)] = row
    assert all(set(rows) == expected for rows in by_law.values())
    for case in expected:
        a, b = (scientific_fields(by_law[law][case]) for law in LAWS)
        assert json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True), case

    records = by_law["nae"].values()
    base_sizes, variant_sizes, tails = [], [], []
    cases = Counter()
    for row in records:
        start, change, at, round_made = key(row)
        if change in ("move", "mark"):
            check_connected_pairs(make_start(start, change, at))
        base = row["base counts"]
        base_sizes.extend(base)
        for variant in row.get("marks", [row]):
            cases[change] += 1
            series = variant["rows"]
            prefix = round_made or 0
            assert [r["round"] for r in series] == list(range(prefix + 1, prefix + len(series) + 1))
            assert [r["n"] for r in series] == base[prefix:prefix + len(series)]
            changed = [r["n'"] for r in series]
            variant_sizes.extend(changed)
            completed = prefix + len(series)
            knot_count = len(STARTS[start]) + sum(base[:prefix]) + sum(changed)
            stop = variant["stop"]
            if (stop is None and completed < LAST_ROUND) or (stop == "knots" and knot_count <= KNOT_CAP):
                tails.append((start, change, at, changed))

    # Ordinary growth and made marks preserve connectedness and at most two
    # holders per distinction: new knots take only loose ones, and fresh or
    # marked distinctions have a single holder when added.
    # Canceling every shared distinction in a sum of old knot rows requires
    # selecting its two holders together or omitting both. The only nonempty
    # such sum selects all old knots and gives all loose distinctions.
    # Distinct births each take a nonempty disjoint set, so no single birth can
    # take every loose distinction in a round with two or more births.
    assert min(base_sizes + variant_sizes) > 1
    result = {
        "paired jobs": len(expected),
        "jobs by change": dict(Counter(case[1] for case in expected)),
        "concrete variants by change": dict(cases),
        "excluded record fields": ["knot law", "seconds"],
        "base count entries per law": len(base_sizes),
        "variant count entries per law": len(variant_sizes),
        "base births across count entries per law": sum(base_sizes),
        "variant births across count entries per law": sum(variant_sizes),
        "minimum births in any saved count entry": min(base_sizes + variant_sizes),
        "recorded births eligible for parity closure": 0,
        "meaning of counts": "Entries include repeated base rounds. The first two rounds of each made mark are shared with its base.",
    }
    return result, sorted(tails)


def recount_variant_tail(tail):
    """Recover a few rounds omitted because the base reached its knot cap sooner."""
    start, change, at, prefix = tail
    assert change in ("mark", "move")
    by_law = {}
    for law in LAWS:
        state = eng.from_stars(make_start(start, change, at))
        guard = eng.Guard(100)
        counts = []
        while state.round < LAST_ROUND and state.n_knots <= KNOT_CAP:
            row = eng.play_round(state, ordinary(law), guard)
            assert len(row["births"]) > 1 and not row["closing"]
            counts.append(len(row["births"]))
        assert counts[:len(prefix)] == prefix
        by_law[law] = counts
    assert by_law["nae"] == by_law["parity"]
    return {
        "start": start, "change": change, "at": at,
        "new rounds": list(range(len(prefix) + 1, len(by_law["nae"]) + 1)),
        "new counts under both laws": by_law["nae"][len(prefix):],
    }


def closing_control():
    """Join three live parents, each pair meeting through a different common knot."""
    places = [
        [0, 5, 9], [1, 2, 10], [3, 4, 11],
        [0, 1, 6, 8], [2, 3, 6, 7], [4, 5, 7, 8],
    ]
    check_connected_pairs(places)
    result = {}
    for law in LAWS:
        state = eng.from_stars(places)
        guard = eng.Guard(100)
        result[law] = [
            [{field: b[field] for field in ("parents", "inputs", "implied", "f")}
             for b in eng.play_round(state, ordinary(law), guard)["births"]]
            for _ in range(2)
        ]
    assert result["parity"] == [[{"parents": (0, 1, 2), "inputs": [9, 10, 11], "implied": True, "f": 0}], []]
    assert result["nae"][0] == [{"parents": (0, 1, 2), "inputs": [9, 10, 11], "implied": False, "f": 1}]
    assert len(result["nae"][1]) == 1
    return {"start": places, "births by law and round": result}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    with gzip.open(HERE.parent / "runs.jsonl.gz", "rt") as source:
        jobs = [json.loads(line) for line in source]
    assert len(jobs) == 366 and all("not run" not in row for row in jobs)
    pairs = {}
    for start in ("two-touching", "chain3")[:1 if args.smoke else 2]:
        pair = next(j for j in jobs if j.get("knot law") == "nae" and key(j) == (start, "pair", None, 2))
        single = next(j for j in jobs if j.get("knot law") == "nae" and key(j) == (start, "made", None, 2))
        pairs[start] = compare_pair_start(start, pair, single, args.smoke)
    laws, tails = recorded_laws(jobs)
    selected = tails[-1:] if args.smoke else tails
    laws["recovered variant tails"] = [recount_variant_tail(row) for row in selected]
    laws["positive control"] = closing_control()
    result = {"made-mark pair replay": pairs, "knot-law comparison": laws}
    if args.output:
        args.output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    else:
        print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
