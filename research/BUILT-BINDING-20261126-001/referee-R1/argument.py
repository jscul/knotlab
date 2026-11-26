"""Check the fixed-start changes on later ordinary stages and one changed rule."""

import argparse
from collections import Counter, defaultdict, deque
from itertools import combinations, product
import json
from pathlib import Path
import resource
from time import perf_counter


HERE = Path(__file__).resolve().parent
STUDY = HERE.parent
OUTSIDE = -1


def word(names):
    return sum(1 << name for name in names)


class Basis:
    def __init__(self, words=()):
        self.pivots = {}
        for value in words:
            self.insert(value)

    def remainder(self, value):
        while value:
            pivot = value.bit_length() - 1
            if pivot not in self.pivots:
                break
            value ^= self.pivots[pivot]
        return value

    def insert(self, value):
        residual = self.remainder(value)
        if residual:
            self.pivots[residual.bit_length() - 1] = residual

    def __len__(self):
        return len(self.pivots)


def holdings(supports):
    at = defaultdict(list)
    for knot, names in enumerate(supports):
        assert len(names) == len(set(names))
        for name in names:
            at[name].append(knot)
    assert all(len(pair) in (1, 2) for pair in at.values())
    return at


def make_start(count, meetings, loose):
    supports = [[] for _ in range(count)]
    name = 0
    for a, b, multiplicity in meetings:
        for _ in range(multiplicity):
            supports[a].append(name)
            supports[b].append(name)
            name += 1
    for knot, number in enumerate(loose):
        supports[knot].extend(range(name, name + number))
        name += number
    return [tuple(row) for row in supports]


def initial_projection_checks(supports):
    laws = [word(row) for row in supports]
    old_rank = len(Basis(laws))
    return [
        old_rank - len(Basis(law & ~mask for law in laws))
        for mask in laws
    ]


def groups(witnesses):
    """Enumerate eligible subsets, keep the maximal ones, and cover the other pairs."""
    together = defaultdict(set)
    for knot, others in witnesses.items():
        for witness in others:
            together[witness].add(knot)
    pairs = {pair for group in together.values() for pair in combinations(sorted(group), 2)}
    candidates = defaultdict(set)
    for a, b in pairs:
        candidates[a].add(b)
        candidates[b].add(a)
    eligible = []

    def extend(chosen, later, common):
        for knot in sorted(later):
            new = (*chosen, knot)
            witnesses_left = common & witnesses[knot]
            if len(new) >= 3 and not witnesses_left:
                eligible.append(frozenset(new))
            remaining = {v for v in later & candidates[knot] if v > knot}
            if remaining:
                extend(new, remaining, witnesses_left)

    for knot in sorted(witnesses):
        extend((knot,), {v for v in candidates[knot] if v > knot}, witnesses[knot])
    maximal = []
    for group in sorted(eligible, key=len, reverse=True):
        if not any(group < larger for larger in maximal):
            maximal.append(group)
    big = sorted(tuple(sorted(group)) for group in maximal)
    covered = {pair for group in big for pair in combinations(group, 2)}
    return big + sorted(pairs - covered), pairs


def step(supports, suppress_groups=False):
    at = holdings(supports)
    loose = defaultdict(list)
    neighbours = defaultdict(set)
    for distinction, holders in at.items():
        if len(holders) == 1:
            loose[holders[0]].append(distinction)
        else:
            a, b = holders
            neighbours[a].add(b)
            neighbours[b].add(a)
    if not loose:
        return None, "closed"
    planned, required_pairs = groups({k: neighbours[k] for k in loose})
    if suppress_groups:
        planned = []
    uses = Counter(k for parents in planned for k in parents)
    if any(uses[k] > len(available) for k, available in loose.items()):
        return None, "stalled"
    for k, available in sorted(loose.items()):
        planned.extend([(k,)] * (len(available) - uses[k]))
    next_groups, _ = groups({i: set(parents) for i, parents in enumerate(planned)})
    demand = Counter(i for group in next_groups for i in group) if not suppress_groups else Counter()
    laws = Basis(word(row) for row in supports)
    pending = {k: iter(sorted(v)) for k, v in loose.items()}
    next_name = max(at) + 1
    births = []
    for index, parents in enumerate(planned):
        inputs = [next(pending[k]) for k in parents]
        implied = laws.remainder(word(inputs)) == 0
        fresh_count = demand[index] if implied else max(1, 3 - len(inputs), demand[index])
        if implied:
            assert demand[index] == 0
        fresh = tuple(range(next_name, next_name + fresh_count))
        next_name += fresh_count
        births.append((parents, tuple(inputs), fresh, implied))

    taken = [name for _, entry, _, _ in births for name in entry]
    assert sorted(taken) == sorted(name for names in loose.values() for name in names)
    represented = {pair for parents, _, _, _ in births for pair in combinations(parents, 2)}
    assert all(
        len(set(parents)) == len(inputs) and
        {at[name][0] for name in inputs} == set(parents)
        for parents, inputs, _, _ in births
    )
    for parents, inputs, fresh, _ in births:
        if fresh:
            continue
        connected = set(parents)
        todo = list(connected)
        while todo:
            others = neighbours[todo.pop()] - connected
            connected.update(others)
            todo.extend(others)
        assert set(inputs) == {name for k in connected for name in loose.get(k, [])}
        assert sum(bool(set(ps) & connected) for ps, _, _, _ in births) == 1
        assert all(len(loose[k]) == 1 for k in parents)
    return births, len(required_pairs - represented)


def names_by_meeting(at, selected):
    pairs = defaultdict(list)
    for d in sorted(selected):
        holders = tuple(at[d])
        if len(holders) == 1:
            holders = (OUTSIDE, holders[0])
        pairs[tuple(sorted(holders))].append(d)
    return pairs


def walks(meetings):
    result = defaultdict(dict)
    for (v, w), names in meetings.items():
        result[v][w] = names
        result[w][v] = names
    return result


def shortest_through(named, a, b, full):
    """Delete just the named distinction and search for the other way between its holders."""
    queue = deque([a])
    previous = {a: None}
    while queue:
        v = queue.popleft()
        for w, names in full[v].items():
            if w in previous:
                continue
            d = next((d for d in names if d != named), None)
            if d is None:
                continue
            previous[w] = (v, d)
            if w == b:
                change = [named]
                while w != a:
                    w, incoming = previous[w]
                    change.append(incoming)
                return tuple(change)
            queue.append(w)
    return ()


def stage_read(supports, age, original_names):
    at = holdings(supports)
    new = at.keys() - original_names
    old_mask = word(original_names)
    laws = [word(row) for row in supports]
    fixed_start_dim = len(new) - len(Basis(row & ~old_mask for row in laws))
    full = walks(names_by_meeting(at, at.keys()))
    pairs = names_by_meeting(at, new)
    reduced = walks(pairs)
    least = {}
    for (a, b), letters in pairs.items():
        for d in letters:
            least[d] = len(shortest_through(d, a, b, full))
    births_by_age = dict(enumerate(age))
    births_by_age[OUTSIDE] = max(age) + 1
    syndrome = {d: word(at[d]) for d in new}
    pair_rank = Basis()
    all_rank = Basis()
    proof_rank = Basis()
    counts = Counter()
    mixed_example = None
    for members in pairs.values():
        for a, b in combinations(members, 2):
            counts["pairs"] += 1
            assert min(least[a], least[b]) == 2 and syndrome[a] == syndrome[b]
            mask = word((a, b))
            pair_rank.insert(mask)
            all_rank.insert(mask)
            proof_rank.insert(mask)

    two_meetings = defaultdict(list)
    for v, reachable in reduced.items():
        for a, b in combinations(sorted(reachable), 2):
            two_meetings[a, b].append(v)
    for (a, b), middle in two_meetings.items():
        for i, j in combinations(sorted(middle), 2):
            if (a, b) >= (i, j):
                continue
            holders = (a, i, b, j)
            ordered = sorted(births_by_age[k] for k in holders)
            s = ordered[0]
            proof_cycle = ordered == [s, s + 1, s + 1, s + 2]
            for ds in product(reduced[a][i], reduced[i][b], reduced[b][j], reduced[j][a]):
                counts["four"] += 1
                assert len(set(ds)) == 4
                assert syndrome[ds[0]] ^ syndrome[ds[1]] ^ syndrome[ds[2]] ^ syndrome[ds[3]] == 0
                mask = word(ds)
                all_rank.insert(mask)
                if proof_cycle:
                    low = next(k for k, v in enumerate(holders) if births_by_age[v] == s)
                    assert least[ds[low - 1]] == least[ds[low]] == 4
                    counts["four with one earliest and one latest holder"] += 1
                    proof_rank.insert(mask)
                    lengths = [least[d] for d in ds]
                    if min(lengths) < 4:
                        counts["proof fours shortest through only some of their distinctions"] += 1
                        if mixed_example is None:
                            mixed_example = {"distinctions": list(ds), "least change sizes in that order": lengths}
    return {
        "knots": len(supports),
        "distinctions": len(at),
        "fixed-start dimension": fixed_start_dim,
        "pair rank": len(pair_rank),
        "pair and four rank": len(all_rank),
        "rank using only the proof's pairs and fours": len(proof_rank),
        "generators": dict(counts),
        "first four with a shorter change through one of its distinctions": mixed_example,
        "least full-stage change size through a fresh distinction": dict(sorted(Counter(least.values()).items())),
    }


def trajectory(start, rounds, suppress_groups=False):
    supports = list(start)
    age = [0] * len(start)
    original_names = set(holdings(start))
    assert all(c == 1 for c in initial_projection_checks(start))
    rows, birth_tables = [], []
    for t in range(1, rounds + 1):
        # For the changed law the first cut is ordinary. Suppress all groups after it.
        births, status = step(supports, suppress_groups and t > 1)
        if births is None:
            return rows, birth_tables, supports, status
        supports.extend(inputs + fresh for _, inputs, fresh, _ in births)
        age.extend([t] * len(births))
        reading = stage_read(supports, age, original_names)
        reading.update({
            "round": t,
            "births": len(births),
            "zero fresh births": sum(not fresh for _, _, fresh, _ in births),
            "common-neighbour pairs without a joint birth": status,
        })
        if not suppress_groups:
            assert status == 0
            assert reading["fixed-start dimension"] == reading["rank using only the proof's pairs and fours"]
        rows.append(reading)
        birth_tables.append(Counter((len(p), len(f), implied) for p, _, f, implied in births))
    return rows, birth_tables, supports, "round limit"


def archived_comparison(start, rounds, birth_tables):
    source = STUDY.parent / "FORBID-EDITS-20261126-001" / "starts.json"
    roster = json.loads(source.read_text())
    index = next(
        i for i, ds in enumerate(roster)
        if ds == [3, [[0, 1, 2], [0, 2, 2], [1, 2, 2]], [2, 2, 2]]
    )
    assert start == make_start(*roster[index])
    key = f"census {index}"

    def record(path):
        with (STUDY / path).open() as stream:
            for line in stream:
                row = json.loads(line)
                if row.get("start") == key:
                    return row
        raise ValueError(f"{key} missing from {path}")

    archived = record("frozen_premises_census.jsonl")
    assert len(archived["rounds"]) == 6
    comparable = min(6, len(rounds))
    for our, their in zip(rounds[:comparable], archived["rounds"][:comparable], strict=True):
        assert their["round"] == our["round"] and their["premises broken"] == {}
        assert their["span"]["inside Z_new"]
        assert their["span"]["dim Z_new"] == our["fixed-start dimension"]
        assert their["span"]["rank of pairs and loops of four"] == our["rank using only the proof's pairs and fours"]
    entries = record("closing_census_parity.jsonl")["births"]
    taken = 0
    for t, ours in enumerate(birth_tables[:3], start=1):
        theirs = Counter((r["p"], r["f"], r["implied"]) for r in entries if r["round"] == t)
        assert ours == theirs
        taken += sum(theirs.values())
    return {"key": key, "matched stage ranks": comparable,
            "matched birth records by round, parent count, fresh count and implication": taken}


def changed_law_control(rounds):
    start = make_start(1, [], [3])
    rows, _, stage, _ = trajectory(start, rounds, suppress_groups=True)
    assert rounds == 3
    through = 3  # The first fresh distinction of the first unary birth.
    at = holdings(stage)
    full = walks(names_by_meeting(at, at.keys()))
    shortest = shortest_through(through, *at[through], full)
    assert rows[0]["common-neighbour pairs without a joint birth"] == 0
    assert all(row["common-neighbour pairs without a joint birth"] > 0 for row in rows[1:])
    assert len(shortest) == 6 and all(d >= 3 for d in shortest)
    mask = word(shortest)
    assert all((word(r) & mask).bit_count() % 2 == 0 for r in stage)
    assert rows[-1]["pair and four rank"] < rows[-1]["fixed-start dimension"]
    return {"rule": "ordinary first round, then one unary birth per loose distinction, two fresh per birth",
            "rounds": rows, "distinction": through, "least change through it": list(shortest),
            "the change keeps all start values": True}


def run(pilot):
    def ring(n):
        return make_start(n, [(k, (k + 1) % n, 1) for k in range(n)], [2] * n)

    doubled_meetings = [(i, j, 2) for i, j in combinations(range(3), 2)]
    examples = [
        ("thirteen knots in a ring, two loose distinctions apiece", ring(13), 24),
        ("sixty-one knots in a ring, two loose distinctions apiece", ring(61), 8),
        ("three knots, each pair sharing two distinctions, two loose apiece", make_start(3, doubled_meetings, [2] * 3), 12),
        ("one three-place founder", make_start(1, [], [3]), 4),
    ]
    output = {}
    for label, start, target in examples:
        rows, births, _, end = trajectory(start, min(target, 2) if pilot else target)
        result = {"end": end, "stages": rows}
        if "each pair" in label:
            result["comparison with the study"] = archived_comparison(start, rows, births)
        output[label] = result
    output["control with common-neighbour coverage removed"] = changed_law_control(3)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    limit = 2 * 1024**3
    resource.setrlimit(resource.RLIMIT_AS, (limit, limit))
    start_time = perf_counter()
    results = run(args.pilot)
    if not args.pilot:
        (HERE / "argument.json").write_text(json.dumps(results, indent=2) + "\n")
    print(f"{'pilot' if args.pilot else 'full'}: {perf_counter() - start_time:.3f} seconds")
