"""Independent literal replay of the two specified addressed edits.

Usage: .venv/bin/python -B addressed.py --pilot
       .venv/bin/python -B addressed.py --output addressed.json

Old assignments are enumerated outright, then grouped only on distinctions
used by the edits, births, or reader records. Each birth receives its own
fresh distinctions. Given the old values, all combinations of its allowed
fresh assignments with the other births' allowed assignments are possible.
"""

import argparse
from collections import Counter
from dataclasses import asdict, dataclass
from fractions import Fraction
from functools import cache
import gzip
from itertools import combinations, product
import json
from math import lcm, prod
from pathlib import Path
from random import Random
from resource import RUSAGE_SELF, getrusage
from time import perf_counter, process_time


HERE = Path(__file__).resolve().parent
LAWS = ("nae", "parity")
GRANTS = ("ordinary", "one_fewer", "arity_floor")
SETTINGS = ("00", "01", "10", "11")
PLACEMENTS = (
    (1007, 7, 7, ((3, 6), (2, 0))),
    (699, 6, 699, ((5, 0), (3, 2))),
)


def mask(names):
    answer = 0
    for name in names:
        answer |= 1 << name
    return answer


def word(state, names):
    return sum(((state >> name) & 1) << i for i, name in enumerate(names))


def values(state, width):
    return tuple((state >> i) & 1 for i in range(width))


def permits(ones, size, law):
    if law == "parity":
        return ones % 2 == 0
    return 0 < ones < size


def accepts(state, support, law):
    return permits((state & support).bit_count(), support.bit_count(), law)


def allowed_states(width, constraints, law):
    """Literal enumeration of every old Boolean assignment."""
    if law == "parity":
        return [
            state for state in range(1 << width)
            if all((state & support).bit_count() % 2 == 0 for support in constraints)
        ]
    sizes = tuple((support, support.bit_count()) for support in constraints)
    return [
        state for state in range(1 << width)
        if all(0 < (state & support).bit_count() < size for support, size in sizes)
    ]


def connected(count, meetings):
    reached = {0}
    for _ in range(count):
        for a, b in meetings:
            if a in reached or b in reached:
                reached.update((a, b))
    return len(reached) == count


def regenerate(count, accepted_index):
    rng = Random(20261126 + count)
    pairs = tuple(combinations(range(count), 2))
    accepted = 0
    while True:
        meetings = tuple(pair for pair in pairs if rng.random() < 1 / 3)
        multiplicities = tuple(rng.randrange(1, 3) for _ in meetings)
        loose = tuple(rng.randrange(3) for _ in range(count))
        if sum(multiplicities) + sum(loose) > 18 or not connected(count, meetings):
            continue
        holders = [[] for _ in range(count)]
        distinction = 0
        for (a, b), multiplicity in zip(meetings, multiplicities):
            for _ in range(multiplicity):
                holders[a].append(distinction)
                holders[b].append(distinction)
                distinction += 1
        for holder, count_loose in zip(holders, loose):
            holder.extend(range(distinction, distinction + count_loose))
            distinction += count_loose
        if any(len(holder) < 3 for holder in holders):
            continue
        if accepted == accepted_index:
            return tuple(map(tuple, holders))
        accepted += 1


def groups(live, witness_sets):
    """Enumerate the complete-round groups by subsets of the small roster."""
    pairs = {
        pair for pair in combinations(live, 2)
        if any(set(pair) <= witness for witness in witness_sets)
    }
    maximal = []
    for size in range(len(live), 2, -1):
        for candidate in combinations(live, size):
            members = set(candidate)
            if any(members <= existing for existing in maximal):
                continue
            if all(pair in pairs for pair in combinations(candidate, 2)):
                if all(not members <= witness for witness in witness_sets):
                    maximal.append(members)
    covered = {pair for group in maximal for pair in combinations(sorted(group), 2)}
    return sorted(tuple(sorted(group)) for group in maximal) + sorted(pairs - covered)


@dataclass(frozen=True)
class Birth:
    parents: tuple
    inputs: tuple
    demand: int
    ordinary: int
    fresh: int


def growth(edited, width, law, grant):
    supports = tuple(map(set, edited))
    occurrences = Counter(x for holder in edited for x in holder)
    loose = {i: [x for x in holder if occurrences[x] == 1] for i, holder in enumerate(edited)}
    live = [i for i in loose if loose[i]]
    if not live:
        return "closed", ()
    witnesses = [
        {j for j in live if i != j and holder & supports[j]}
        for i, holder in enumerate(supports)
    ]
    roster = groups(live, witnesses)
    owed = Counter(parent for parents in roster for parent in parents)
    if any(owed[i] > len(loose[i]) for i in live):
        return "stalled", ()
    for i in live:
        roster.extend([(i,)] * (len(loose[i]) - owed[i]))
    payments = {i: iter(loose[i]) for i in live}
    inputs = [tuple(next(payments[parent]) for parent in parents) for parents in roster]
    assert sorted(x for row in inputs for x in row) == sorted(x for xs in loose.values() for x in xs)
    next_witnesses = [{j for j, parents in enumerate(roster) if i in parents} for i in live]
    demand = Counter(
        j for group in groups(list(range(len(roster))), next_witnesses) for j in group
    )

    births = []
    constraints = tuple(map(mask, edited))
    for j, (parents, paid) in enumerate(zip(roster, inputs)):
        floor = max(0, 3 - len(parents))
        ordinary = max(demand[j], floor, 1)
        if ordinary > demand[j]:
            input_mask = mask(paid)
            # Grants use implication by the edited knots alone. Preparation
            # is kept also by the original knots when enumerating the tables.
            counterexample = any(
                not accepts(state, input_mask, law)
                and all(accepts(state, support, law) for support in constraints)
                for state in range(1 << width)
            )
            if not counterexample:
                ordinary = demand[j]
        grant_limits = {
            "ordinary": ordinary,
            "one_fewer": max(floor, ordinary - 1),
            "arity_floor": floor,
        }
        births.append(Birth(parents, paid, demand[j], ordinary, min(ordinary, grant_limits[grant])))
    return "funded", tuple(sorted(births, key=lambda b: (b.parents, tuple(sorted(b.inputs)))))


@cache
def fresh_words(law, inputs_size, inputs_ones, count_fresh):
    return tuple(
        a for a in range(1 << count_fresh)
        if permits(inputs_ones + a.bit_count(), inputs_size + count_fresh, law)
    )


def fresh_choices(law, birth, state):
    return fresh_words(law, len(birth.inputs), (state & mask(birth.inputs)).bit_count(), birth.fresh)


def layout(edited, births, own):
    held = tuple(dict.fromkeys(x for holder in own for x in edited[holder]))
    visible = tuple(b for b in births if set(own).intersection(b.parents))
    foreign = tuple(
        x for b in visible for x, parent in zip(b.inputs, b.parents) if parent not in own
    )
    assert len(set(held + foreign)) == len(held) + len(foreign)
    named_shape = tuple((b.parents, b.inputs, b.fresh) for b in visible)
    archived_shape = tuple((b.parents, tuple(sorted(b.inputs)), b.fresh) for b in visible)
    anonymous_shape = tuple(
        (b.parents, tuple(x if parent in own else None for x, parent in zip(b.inputs, b.parents)), b.fresh)
        for b in visible
    )
    return {
        "held": held,
        "outside inputs": foreign,
        "births": visible,
        "archive shape": archived_shape,
        "declared shape": named_shape,
        "shape without outside input names": anonymous_shape,
    }


def prepared_states(edited, marks, projected, law):
    """Reapply both edited constraints to each enumerated base projection."""
    additions = marks[2:]
    addition_bits = tuple(mask(x for x, v in zip(additions, pair) if v) for pair in product((0, 1), repeat=2))
    edit_masks = [mask(holder) for holder in edited if any(x in holder for x in additions)]
    for state, multiplicity in projected.items():
        for add in addition_bits:
            full = state | add
            if all(accepts(full, support, law) for support in edit_masks):
                yield full, multiplicity


def accumulate(projected, edited, births, layouts, marks, law):
    mark_mask = mask(marks)
    visible_masks = [mask(l["held"] + l["outside inputs"]) for l in layouts]
    kernels = [
        (mask(b.inputs), tuple(len(fresh_words(law, len(b.inputs), ones, b.fresh))
                               for ones in range(len(b.inputs) + 1)))
        for b in births
    ]
    read_u, read_s = Counter(), Counter()
    record_u, record_s = [Counter(), Counter()], [Counter(), Counter()]
    prepared = 0
    for state, multiplicity in prepared_states(edited, marks, projected, law):
        prepared += multiplicity
        count = prod(count_by_ones[(state & used).bit_count()] for used, count_by_ones in kernels)
        if not count:
            continue
        reading = state & mark_mask
        extended = count * multiplicity
        read_u[reading] += extended
        read_s[reading] += multiplicity
        for i, visible in enumerate(visible_masks):
            local = state & visible
            record_u[i][local] += extended
            record_s[i][local] += multiplicity
    reading = {
        weight: Counter({word(state, marks): count for state, count in table.items()})
        for weight, table in (("U", read_u), ("S", read_s))
    }
    return prepared, reading, {"U": record_u, "S": record_s}


def reader_tables(raw_u, raw_s, record, law):
    """Recover both exact record distributions from the visible old values.

    Full records have the same conditional fresh law whenever the ordered
    visible old values and the shape agree. Therefore their total variation
    equals that of the visible old values. The archived records forget the
    outside input values, which requires summing over them after including
    the fresh values. Integer scaling keeps these sums exact under S.
    """
    held = record["held"]
    names = held + record["outside inputs"]
    declared = {
        weight: {word(state, names): count for state, count in raw.items()}
        for weight, raw in (("U", raw_u), ("S", raw_s))
    }
    seen = record["births"]
    choices_by_projection = {
        state: tuple(fresh_choices(law, b, state) for b in seen) for state in raw_s
    }
    local_fresh_count = {
        state: prod(map(len, choices)) for state, choices in choices_by_projection.items()
    }
    scale_s = lcm(*set(local_fresh_count.values()))
    stored_u, stored_s = Counter(), Counter()
    for state, choices in choices_by_projection.items():
        u, remainder = divmod(raw_u[state], local_fresh_count[state])
        assert not remainder
        s = raw_s[state] * (scale_s // local_fresh_count[state])
        held_word = word(state, held)
        for fresh in product(*choices):
            index = len(held)
            key = held_word
            for b, a in zip(seen, fresh):
                key |= a << index
                index += b.fresh
            stored_u[key] += u
            stored_s[key] += s
    assert stored_u.total() == raw_u.total() and stored_s.total() == raw_s.total() * scale_s
    return {
        "U": {"declared": declared["U"], "stored": dict(stored_u)},
        "S": {"declared": declared["S"], "stored": dict(stored_s)},
    }


def tv(left, right):
    left_total, right_total = sum(left.values()), sum(right.values())
    denominator = left_total * right_total
    differences = {
        sign: left.get(sign, 0) * right_total - right.get(sign, 0) * left_total
        for sign in left.keys() | right.keys()
    }
    distance = Fraction(sum(map(abs, differences.values())), 2 * denominator)
    if not distance:
        return distance, None
    witness = max(differences, key=lambda sign: (abs(differences[sign]), -sign))
    return distance, (
        witness,
        Fraction(left.get(witness, 0), left_total),
        Fraction(right.get(witness, 0), right_total),
    )


def comparison(first, second, first_table, second_table, kind, width):
    if first != second:
        return {
            "total variation": "1",
            "shape changed": True,
            "births exclusive to far zero": [birth for birth in first if birth not in second],
            "births exclusive to far one": [birth for birth in second if birth not in first],
            "probabilities of the far-zero shape": ["1", "0"],
        }
    distance, witness = tv(first_table, second_table)
    result = {"total variation": str(distance), "shape changed": False}
    if witness is not None:
        state, p, q = witness
        result["witness"] = {"event": kind, "ordered values": values(state, width), "probabilities": [str(p), str(q)]}
    return result


def pair_histogram(table, i):
    counts = Counter()
    for state, count in table.items():
        pair = ((state >> i) & 1) | (((state >> (2 + i)) & 1) << 1)
        counts[pair] += count
    return counts


def marginals(table):
    result = {}
    for i, mark in enumerate(("first reader old", "second reader old", "first reader added", "second reader added")):
        p = Fraction(sum(count for state, count in table.items() if (state >> i) & 1), table.total())
        kind = {Fraction(1, 2): "fair", Fraction(0): "fixed at zero", Fraction(1): "fixed at one"}.get(p, "biased")
        result[mark] = {"probability of one": str(p), "classification": kind}
    return result


def reading_report(histogram):
    return {
        "joint reading probabilities": {
            "".join(map(str, values(state, 4))): str(Fraction(count, histogram.total()))
            for state, count in sorted(histogram.items())
        },
        "individual marginals": marginals(histogram),
    }


def correlation(table, a, b):
    signed = sum(count * (1 - 2 * (((state >> a) ^ (state >> b)) & 1)) for state, count in table.items())
    return Fraction(signed, table.total())


def scores(readings):
    result = {}
    for label, a, b in (("fixed old values", 0, 1), ("added values", 2, 3)):
        correlators = {s: correlation(readings[s], a, b) for s in SETTINGS}
        best = max(
            sum(flag * value for flag, value in zip(signs, correlators.values()))
            for signs in product((-1, 1), repeat=4) if prod(signs) == -1
        )
        result[label] = {"CHSH": str(best), "correlations": {s: str(value) for s, value in correlators.items()}}
    return result


def outward_layout(record):
    return {key: value for key, value in record.items() if key != "births"}


def outside_name_transport(first, second, base, marks):
    """Check the precise forgetting comparison for these two placements."""
    if first["declared shape"] == second["declared shape"]:
        return None
    assert first["shape without outside input names"] == second["shape without outside input names"]
    changes = [
        (a, b) for a, b in zip(first["outside inputs"], second["outside inputs"]) if a != b
    ]
    assert len(changes) == 1
    a, b = changes[0]
    rename = {a: b, b: a}
    assert all(name not in rename for name in first["held"] + marks)
    # The old constraint supports are sets. The given spending order can
    # still distinguish the two loose names at this outside parent.
    assert all({rename.get(name, name) for name in holder} == set(holder) for holder in base)
    assert tuple(
        (parents, tuple(rename.get(name, name) for name in inputs), fresh)
        for parents, inputs, fresh in first["declared shape"]
    ) == second["declared shape"]
    return changes[0]


def parity_event(index, first, second, tables):
    """Read the witness using the outside input's role in the same birth."""
    own = (2, 3) if index == 1007 else (3, 4)
    answer = []
    for record, table in zip((first, second), tables):
        outside, = record["outside inputs"]
        terms = own + (outside,)
        order = record["held"] + record["outside inputs"]
        parity_mask = mask(order.index(x) for x in terms)
        kept = sum(count for word, count in table.items() if (word & parity_mask).bit_count() % 2 == 0)
        answer.append({"terms": terms, "probability of even parity": str(Fraction(kept, sum(table.values())))})
    assert [x["probability of even parity"] for x in answer] == ["1/2", "1"]
    return answer


def measured_case(index, base, readers, law, grant, projected, first_new, marks):
    evidence, distributions = {}, {}
    for setting in SETTINGS:
        edited = list(base)
        for i, reader in enumerate(readers):
            holder = reader[int(setting[i])]
            edited[holder] += (first_new + i,)
        status, births = growth(edited, first_new + 2, law, grant)
        layouts = tuple(layout(edited, births, own) for own in readers)
        prepared, readings, records = accumulate(projected, edited, births, layouts, marks, law)
        assert readings["U"].total() > 0 and readings["S"].total() > 0
        distributions[setting] = {
            "readings": readings,
            "complete records": [
                reader_tables(records["U"][i], records["S"][i], record, law)
                for i, record in enumerate(layouts)
            ],
            "layouts": layouts,
        }
        owners = [{i for i, rd in enumerate(readers) if set(rd).intersection(b.parents)} for b in births]
        shared_births = sum(len(group) > 1 for group in owners)
        zero_fresh = dict(Counter(
            "shared" if len(group) > 1 else str(next(iter(group))) if group else "middle"
            for b, group in zip(births, owners) if b.fresh == 0
        ))
        evidence[setting] = {
            "status": status,
            "prepared assignments": prepared,
            "surviving prepared assignments": readings["S"].total(),
            "complete allowed assignments": readings["U"].total(),
            "births": [asdict(b) for b in births],
            "shared births": shared_births,
            "zero-fresh births by reader": zero_fresh,
            "reader layouts": [outward_layout(record) for record in layouts],
            "marked readings": {weight: reading_report(readings[weight]) for weight in ("U", "S")},
        }

    response = {}
    for weight in ("U", "S"):
        readings = {s: t["readings"][weight] for s, t in distributions.items()}
        weight_result = {"scores": scores(readings), "readers": []}
        for i in range(2):
            reader_result = []
            for own in ("0", "1"):
                left, right = ("".join(s) for s in product("01", repeat=2) if s[i] == own)
                first, second = distributions[left], distributions[right]
                l1, l2 = first["layouts"][i], second["layouts"][i]
                r1, r2 = first["complete records"][i][weight], second["complete records"][i][weight]
                assert l1["held"] == l2["held"]
                stored_width = len(l1["held"]) + sum(b.fresh for b in l1["births"])
                full_width = len(l1["held"]) + len(l1["outside inputs"])
                joint_tv, _ = tv(pair_histogram(readings[left], i), pair_histogram(readings[right], i))
                comparisons = {
                    "stored": comparison(l1["archive shape"], l2["archive shape"], r1["stored"], r2["stored"],
                                         "stored record", stored_width),
                    "declared": comparison(l1["declared shape"], l2["declared shape"], r1["declared"], r2["declared"],
                                           "holder and outside input values", full_width),
                    "without outside input names": comparison(
                        l1["shape without outside input names"], l2["shape without outside input names"],
                        r1["declared"], r2["declared"], "holder and outside input values by parent role", full_width,
                    ),
                }
                transport = outside_name_transport(l1, l2, base, marks)
                if transport is not None:
                    comparisons["without outside input names"]["outside input transposition"] = transport
                    if law == "parity" and grant != "ordinary":
                        comparisons["without outside input names"]["even parity witness"] = parity_event(
                            index, l1, l2, (r1["declared"], r2["declared"]),
                        )
                reader_result.append({
                    "own setting": own,
                    "far settings zero and one": [left, right],
                    "joint old and added total variation": str(joint_tv),
                    "record comparisons": comparisons,
                })
            weight_result["readers"].append(reader_result)
        response[weight] = weight_result
    return {"start": index, "law": law, "grant": grant, "settings": evidence, "weightings": response}


def conditional_witness(base, permitted, row):
    """Find one kept old state with unequal conditional fresh laws."""
    parents = (2, 5) if row["start"] == 1007 else (2, 4)
    contexts = ("00", "10")
    births = []
    for setting in contexts:
        record, = [birth for birth in row["settings"][setting]["births"] if birth["parents"] == parents]
        births.append(Birth(**record))
    first, second = births
    a, b = mask(first.inputs), mask(second.inputs)
    state = next(state for state in permitted if not a & state and (b & state).bit_count() == 1)
    width = max(x for holder in base for x in holder) + 1
    choices = [fresh_choices("nae", birth, state) for birth in births]
    return {
        "start": row["start"],
        "law": "nae",
        "grant": "ordinary",
        "own reader": 1,
        "own setting": 0,
        "far settings zero and one": contexts,
        "old distinctions with value one": [d for d in range(width) if (state >> d) & 1],
        "added values": [0, 0],
        "birth parents": parents,
        "inputs by parent": [birth.inputs for birth in births],
        "input values by parent": [[(state >> x) & 1 for x in birth.inputs] for birth in births],
        "number of allowed fresh words": [len(options) for options in choices],
        "probability all fresh values are zero given the prepared state (U and S)": [
            str(Fraction(int(0 in options), len(options))) for options in choices
        ],
    }


def maximum_movement(reader, record):
    comparisons = [own["record comparisons"][record] for own in reader]
    return {
        "largest total variation": str(max(Fraction(c["total variation"]) for c in comparisons)),
        "in the shape of its births": any(c["shape changed"] for c in comparisons),
    }


def key(row):
    return row["start"], row["law"], row.get("grant", row.get("arm"))


def compare_archives(rows, starts):
    """Read saved evidence only after rebuilding the requested cases."""
    rebuilt = {key(row): row for row in rows}
    starts = {item["index"]: item for item in starts}
    diffs = []
    matched = set()
    with gzip.open(HERE.parent / "contact_runs.jsonl.gz", "rt") as source:
        for line in source:
            archived = json.loads(line)
            if archived["source"] != "extension" or key(archived) not in rebuilt:
                continue
            row = rebuilt[key(archived)]
            matched.add(key(row))
            assert archived["readers"] == json_lists(starts[row["start"]]["readers"])
            fields = {
                "kind": "shared birth, read" if any(s["shared births"] for s in row["settings"].values()) else "read",
                "status": {s: case["status"] for s, case in row["settings"].items()},
            }
            for weight, details in row["weightings"].items():
                fields[weight] = {
                    "record moves": [maximum_movement(rd, "stored") for rd in details["readers"]],
                    "score": str(max(Fraction(x["CHSH"]) for x in details["scores"].values())),
                    "single unchanged": all(
                        own["joint old and added total variation"] == "0"
                        for reader in details["readers"] for own in reader
                    ),
                }
            for field, expected in fields.items():
                if archived[field] != expected:
                    diffs.append({"case": key(row), "field": field, "rebuilt": expected, "archived": archived[field]})
    assert matched == rebuilt.keys()

    predecessor = HERE.parents[1] / "FORBID-EDITS-20261126-001"
    checked = {}
    for family in ("xcount", "xrun"):
        found = set()
        for index, start in starts.items():
            offset = index // 1000 * 1000
            with gzip.open(predecessor / f"{family}_E2_{offset}.jsonl.gz", "rt") as source:
                for line in source:
                    saved = json.loads(line)
                    if saved["start"] != index or saved["readers"] != json_lists(start["readers"]):
                        continue
                    if key(saved) not in rebuilt:
                        continue
                    row = rebuilt[key(saved)]
                    found.add(key(row))
                    expected = {
                        "supports": json_lists(start["supports"]),
                        "retained of old": {
                            s: [details["surviving prepared assignments"], details["prepared assignments"]]
                            for s, details in row["settings"].items()
                        },
                        "zero-fresh births": {
                            s: details["zero-fresh births by reader"] for s, details in row["settings"].items()
                        },
                    }
                    if family == "xrun":
                        for weight, info in row["weightings"].items():
                            expected[weight] = {
                                "scores": {"fixed old value": info["scores"]["fixed old values"]["CHSH"],
                                           "added value": info["scores"]["added values"]["CHSH"]},
                                "single unchanged": all(
                                    own["joint old and added total variation"] == "0"
                                    for reader in info["readers"] for own in reader
                                ),
                                "record unchanged": all(
                                    maximum_movement(reader, "stored")["largest total variation"] == "0"
                                    for reader in info["readers"]
                                ),
                            }
                    for field, result in expected.items():
                        if saved[field] != result:
                            diffs.append({"case": key(row), "file family": family, "field": field,
                                          "rebuilt": result, "archived": saved[field]})
        checked[family] = {
            "rows compared": len(found),
            "missing exact reader order": sorted(rebuilt.keys() - found),
        }
    return {"contact rows compared": len(matched), "predecessor": checked, "differences": diffs}


def json_lists(value):
    return json.loads(json.dumps(value))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--pilot", action="store_true")
    mode.add_argument("--output", type=Path)
    args = parser.parse_args()
    start_wall, start_cpu = perf_counter(), process_time()
    starts, rows, witnesses = [], [], []
    selection = PLACEMENTS[:1] if args.pilot else PLACEMENTS
    for index, knot_count, within_size, readers in selection:
        base = regenerate(knot_count, within_size)
        n = max(x for support in base for x in support) + 1
        occurrences = Counter(x for support in base for x in support)
        old_marks = tuple(next(x for x in base[rd[0]] if occurrences[x] == 1) for rd in readers)
        marks = old_marks + (n, n + 1)
        all_used = mask(
            [x for x, count in occurrences.items() if count == 1]
            + [x for rd in readers for i in rd for x in base[i]]
        )
        starts.append({
            "index": index, "knots": knot_count, "within-size draw index": within_size, "draw seed": 20261126 + knot_count,
            "supports": base, "readers": readers, "marked distinctions": marks,
        })
        for law in (LAWS[:1] if args.pilot else LAWS):
            permitted = allowed_states(n, tuple(map(mask, base)), law)
            projected = Counter(state & all_used for state in permitted)
            for grant in (GRANTS[:1] if args.pilot else GRANTS):
                row = measured_case(index, base, readers, law, grant, projected, n, marks)
                rows.append(row)
                if law == "nae" and grant == "ordinary":
                    witnesses.append(conditional_witness(base, permitted, row))

    archive = None if args.pilot else compare_archives(rows, starts)
    usage = {
        "wall seconds": round(perf_counter() - start_wall, 6),
        "CPU seconds": round(process_time() - start_cpu, 6),
        "peak resident KiB": getrusage(RUSAGE_SELF).ru_maxrss,
    }
    print(json.dumps({
        "rows": len(rows), "settings": sum(len(row["settings"]) for row in rows), "starts": starts,
        "conditional witnesses": witnesses, "usage": usage, "archive": archive,
    }))
    if args.output:
        result = {"starts": starts, "conditional witnesses": witnesses, "rows": rows,
                  "comparison": archive, "usage": usage}
        args.output.write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
