"""Check the deterministic census, including the histories omitted at the cap."""

import argparse
import json
import random
import resource
from collections import Counter, defaultdict
from itertools import chain, combinations
from pathlib import Path
from time import monotonic

from core import (
    State,
    basis,
    closing_cost,
    commutation,
    first_natural_failure,
    history,
    indicator,
    outerplanar,
    read_starts,
    regenerated_starts,
    remainder,
    sharing_graph,
    three_in_one_block,
)


HERE = Path(__file__).resolve().parent
ARCHIVE = HERE.parent
NATURAL = "natural rule: first round without a state"
WHOLE_ODD = "whole choices attain odd"
BIRTH_ODD = "birth choices attain odd"
A1 = "A1 no knot holds a decidable pair"
A3 = "A3 one implied birth closes the whole"
A5 = "A5 round-1 closure: birth equals whole"


def odd_witness(rows, cost, pivots, pairs):
    """Set one free bit surviving cost reduction and solve the pivot bits."""
    free_cost = remainder(cost, pivots)
    if not free_cost:
        return None
    choice = free_cost & -free_cost
    for pivot in sorted(pivots, reverse=True):
        if (pivots[pivot] & choice).bit_count() % 2:
            choice |= 1 << pivot
    assert all((row & choice).bit_count() % 2 == 0 for row in rows)
    assert (cost & choice).bit_count() % 2 == 1
    return [pair for index, pair in enumerate(pairs) if choice & (1 << index)]


def interleaving_cost(state, pairs):
    """Compare the product sorting cost with scores from occurrence positions."""
    positions = defaultdict(list)
    for position, distinction in enumerate(chain.from_iterable(state.knots)):
        positions[distinction].append(position)
    cost = 0
    for index, (d, e) in enumerate(pairs):
        a, b = positions[d]
        c, f = positions[e]
        if a < c < b < f or c < a < f < b:
            cost |= 1 << index
    return cost


def check_order(state, pairs, rows, cost, pivots):
    """Exhaust the exchanging knot pairs, with each pair listed consecutively."""
    order = tuple(range(len(state.knots)))
    for (left, right), row in zip(combinations(order, 2), rows, strict=True):
        rest = tuple(knot for knot in order if knot not in (left, right))
        before = closing_cost(state, pairs, (left, right) + rest)
        after = closing_cost(state, pairs, (right, left) + rest)
        assert before ^ after == row
        assert remainder(cost ^ before, pivots) == 0
    assert cost == interleaving_cost(state, pairs)
    return len(rows)


def check_transition(before, after, births):
    """Check each new knot's input implication directly against old parity rows."""
    previous_rows = basis(indicator(knot) for knot in before.knots)
    loose = {d for d, ids in before.holders.items() if len(ids) == 1}
    use = Counter()
    implied = []
    assert [birth["knot"] for birth in births] == list(range(len(before.knots), len(after.knots)))
    for birth in births:
        new_knot = birth["knot"]
        distinctions = set(after.knots[new_knot])
        inputs = distinctions & before.holders.keys()
        fresh = distinctions - inputs
        parents = {before.holders[d][0] for d in inputs}
        assert inputs and len(parents) == len(inputs)
        assert inputs == set(birth["inputs"]) and fresh == set(birth["fresh"])
        assert parents == set(birth["parents"]) and len(fresh) == birth["f"]
        assert all(after.holders[d] == (new_knot,) for d in fresh)
        use.update(inputs)
        is_implied = remainder(indicator(inputs), previous_rows) == 0
        assert is_implied == bool(birth["old_inputs_already_imply_law"])
        if is_implied:
            implied.append(new_knot)
        assert bool(fresh) != is_implied
    assert use == Counter(loose)
    return after.closed == bool(implied) and (not implied or len(births) == len(implied) == 1)


def has_nonzero_choice(state):
    """A homogeneous count, including the inherited signs of a closed start."""
    inherited_signs = state.closed and state.round == 0
    pairs = state.birth_pairs
    knots = len(state.knots)
    if len(pairs) > knots * (knots - 1) // 2 + inherited_signs:
        return True
    rows = list(commutation(state, pairs))
    if inherited_signs:
        rows.append(closing_cost(state, pairs))
    return len(pairs) > len(basis(rows))


def initial_closed(state, start, natural, audit):
    pairs = state.birth_pairs
    rows = tuple(commutation(state, pairs))
    pivots = basis(rows)
    cost = closing_cost(state, pairs)
    free_cost = remainder(cost, pivots)
    audit["initially closed"]["starts"] += 1
    audit["initially closed"]["commuting choices can have odd cost"] += bool(free_cost)
    audit["initially closed"]["natural checks commute"] += natural is None
    audit["initially closed"]["natural checks commute and cost is odd"] += natural is None and cost.bit_count() % 2
    if free_cost and "initially closed odd witness" not in audit:
        audit["initially closed odd witness"] = {
            "start": start,
            "knots": state.knots,
            "failing pairs": odd_witness(rows, cost, pivots, pairs),
        }


def lost_closure(growth, row, whole_rows, whole_cost, whole_pivots):
    closed = growth.states[-1]
    forbidden = set(closed.whole_pairs) - set(closed.birth_pairs)
    closing = growth.births[-1][0]
    histories = []
    for pair in sorted(forbidden):
        first, second = pair
        round_at_decision = closed.distinction_round[first]
        assert round_at_decision == closed.distinction_round[second]
        decision = growth.states[round_at_decision]
        next_round = growth.states[round_at_decision + 1]
        at_decision = tuple(decision.holders[d] for d in pair)
        after_decision = tuple(next_round.holders[d] for d in pair)
        assert all(len(ids) == 1 for ids in at_decision) and at_decision[0] != at_decision[1]
        assert all(len(ids) == 2 for ids in after_decision) and not set(after_decision[0]) & set(after_decision[1])
        histories.append({
            "pair": pair,
            "decision round": round_at_decision,
            "holders at decision": at_decision,
            "holders in next round": after_decision,
        })
    return {
        "start": row["start"],
        "closing round": closed.round,
        "knots": len(closed.knots),
        "closing knot places": len(closed.knots[closing["knot"]]),
        "closing knot parents": len(closing["parents"]),
        "three parents in one block": row["three parents in one block"],
        "forbidden pairs": len(forbidden),
        "their birth rounds": sorted({item["decision round"] for item in histories}),
        "closing knot inputs": closing["inputs"],
        "closing parent ids": closing["parents"],
        "forbidden pair histories": histories,
        "example odd whole choice": odd_witness(whole_rows, whole_cost, whole_pivots, closed.whole_pairs),
    }


def recount(start, supports, rounds, audit):
    growth = history(supports, rounds=rounds)
    states = growth.states
    last = states[-1]
    row = {"start": start, "end": growth.end, "rounds": growth.attempted_round, "knots": growth.attempted_knots}
    a1 = True
    first_failure = None
    failing_knots = None
    a3 = True
    earlier = None
    pass_label = "within-cap prefix of cut starts" if growth.end == "cut" else "uncut histories"
    for state, births in zip(states, growth.births, strict=True):
        audit["rounds checked"][pass_label] += 1
        audit["pair decision classes"].update(state.decision_counts)
        for category, pair in state.decision_examples.items():
            if category not in audit["pair decision examples"]:
                audit["pair decision examples"][category] = {
                    "start": start,
                    "round": state.round,
                    "pair": pair,
                    "birth rounds": tuple(state.distinction_round[d] for d in pair),
                    "holders": tuple(state.holders[d] for d in pair),
                    "eligible": pair in state.birth_pairs,
                }
        eligible = set(state.birth_pairs)
        has_coheld_eligible = any(
            pair in eligible for knot in state.knots for pair in combinations(sorted(knot), 2)
        )
        if has_coheld_eligible:
            audit["A1 violations"].append((start, state.round))
            a1 = False
        if has_nonzero_choice(state):
            audit["rounds allowing a nonzero choice"][pass_label] += 1
        if first_failure is None:
            failing_knots = first_natural_failure(state, earlier)
            if failing_knots is not None:
                first_failure = state.round
        if earlier is None:
            sharing = sharing_graph(state)
            seen = {0}
            pending = [0]
            while pending:
                other = set(sharing[pending.pop()]) - seen
                seen.update(other)
                pending.extend(other)
            assert len(seen) == len(state.knots)
        else:
            transition_ok = check_transition(earlier, state, births)
            audit["funded transitions checked"][pass_label] += 1
            audit["births whose old implication was checked"][pass_label] += len(births)
            if not transition_ok:
                audit["A3 violations"].append((start, state.round))
            a3 = a3 and transition_ok
        earlier = state

    audit["natural first failure by ending status"][growth.end][str(first_failure)] += 1
    if growth.end == "cut":
        row["note"] = "cut above the knot cap: not run"
        audit["cut prefixes"].append({
            "start": start,
            "attempted round": growth.attempted_round,
            "attempted knots": growth.attempted_knots,
            "last checked round": last.round,
            "last checked knots": len(last.knots),
            "first failure in checked prefix": first_failure,
            "failing knots": failing_knots,
        })
        return row

    row.update({A1: a1, "funded rounds": last.round, NATURAL: first_failure})
    if not last.closed:
        return row
    if last.round == 0:
        row["closed at round 0"] = True
        initial_closed(last, start, first_failure, audit)
        return row

    whole = last.whole_pairs
    local = last.birth_pairs
    missing_at_birth = set()
    for decision in states:
        newly_loose = [
            d for d in sorted(decision.holders)
            if decision.distinction_round[d] == decision.round and len(decision.holders[d]) == 1
        ]
        missing_at_birth.update(combinations(newly_loose, 2))
    omitted = set(whole) - set(local)
    if omitted != set(whole) & missing_at_birth:
        audit["closure pair restriction disagreements"].append(start)
    audit["whole-only pairs across closures"] += len(omitted)
    whole_rows = tuple(commutation(last, whole))
    whole_pivots = basis(whole_rows)
    local_pivots = basis(commutation(last, local))
    whole_cost = closing_cost(last, whole)
    local_cost = closing_cost(last, local)
    audit["A4 knot exchanges checked"] += check_order(last, whole, whole_rows, whole_cost, whole_pivots)

    row.update({
        "closing round": last.round,
        A3: a3,
        "outerplanar": outerplanar(last),
        "unheld pairs": len(whole),
        "locally decidable pairs": len(local),
        WHOLE_ODD: bool(remainder(whole_cost, whole_pivots)),
        "whole choices: free directions": len(whole) - len(whole_pivots),
        BIRTH_ODD: bool(remainder(local_cost, local_pivots)),
        "birth choices: free directions": len(local) - len(local_pivots),
        "three parents in one block": three_in_one_block(states[-2], growth.births[-1][0]["parents"]),
    })
    assert whole_rows and len(local) <= len(whole)
    assert all((r.bit_count() % 2 == 0) for r in commutation(last, local)) == (first_failure is None)
    if last.round == 1:
        row[A5] = whole == local
    if first_failure is None:
        row["natural rule closing sign"] = "odd" if local_cost.bit_count() % 2 else "even"
    if row[WHOLE_ODD] and not row[BIRTH_ODD]:
        audit["losses"].append(lost_closure(growth, row, whole_rows, whole_cost, whole_pivots))
    return row


def compare(rows, filename):
    with (ARCHIVE / filename).open() as source:
        old = [json.loads(line) for line in source]
    if len(rows) != len(old):
        raise ValueError(f"{filename} has {len(old)} rows, recount made {len(rows)}")
    differences = []
    for current, archived in zip(rows, old, strict=True):
        archived.pop("random local rule runs", None)
        if current != archived:
            differences.append({
                "start": current["start"],
                "fields": {
                    key: {"recount": current.get(key), "archive": archived.get(key)}
                    for key in sorted(current.keys() | archived.keys())
                    if key not in current or key not in archived or current[key] != archived[key]
                },
            })
    return {"rows checked": len(rows), "differences": differences}


def check_losses(audit):
    old = json.loads((ARCHIVE / "posthoc_losses.json").read_text())["cases"]
    fields = set().union(*(record.keys() for record in old))
    recounted = [{key: item[key] for key in fields} for item in audit["losses"]]
    return {"rows checked": len(old), "archived fields agree": old == recounted}


def audit_counts():
    return {
        "rounds checked": Counter(),
        "funded transitions checked": Counter(),
        "births whose old implication was checked": Counter(),
        "rounds allowing a nonzero choice": Counter(),
        "pair decision classes": Counter(),
        "pair decision examples": {},
        "A1 violations": [],
        "A3 violations": [],
        "A4 knot exchanges checked": 0,
        "closure pair restriction disagreements": [],
        "whole-only pairs across closures": 0,
        "natural first failure by ending status": defaultdict(Counter),
        "cut prefixes": [],
        "initially closed": Counter(),
        "losses": [],
    }


def summarize(rows, audit):
    closures = [row for row in rows if "closing round" in row]
    funded = [row for row in rows if row.get("funded rounds", 0) > 0]
    by_round = defaultdict(Counter)
    for row in closures:
        counts = by_round[str(row["closing round"])]
        counts["closures"] += 1
        counts["not outerplanar"] += not row["outerplanar"]
        counts["whole odd"] += row[WHOLE_ODD]
        counts["birth odd"] += row[BIRTH_ODD]
        counts["natural rule keeps a state"] += row[NATURAL] is None
        counts["natural rule closes odd"] += row.get("natural rule closing sign") == "odd"
        counts["free directions lost (sum)"] += row["whole choices: free directions"] - row["birth choices: free directions"]
    later = [row for row in closures if row["closing round"] > 1]
    lemma = [row for row in later if row["three parents in one block"]]
    other = [row for row in later if not row["three parents in one block"] and row[WHOLE_ODD]]
    for key in ("pair decision classes", "pair decision examples"):
        audit[key] = {" / ".join(category): audit[key][category] for category in sorted(audit[key])}
    return {
        "starts": len(rows),
        "ending status": Counter(row["end"] for row in rows),
        "funded starts within cap": len(funded),
        "natural failures among funded starts within cap": sum(row[NATURAL] is not None for row in funded),
        "grown closures": len(closures),
        "counts by closing round": by_round,
        "A3 passes at closures": sum(row[A3] for row in closures),
        "A5 passes at round-1 closures": sum(row.get(A5, False) for row in closures),
        "whole odd and outerplanarity disagreements": [row["start"] for row in closures if row[WHOLE_ODD] == row["outerplanar"]],
        "later closures with three closing parents in one block": [row["start"] for row in lemma],
        "birth odd at later closures with three closing parents in one block": sum(row[BIRTH_ODD] for row in lemma),
        "other later closures with whole odd": len(other),
        "birth odd at other later closures with whole odd": sum(row[BIRTH_ODD] for row in other),
        **audit,
    }


def mixed_age_loose_control():
    """Exercise the holding test where full-round funding would bar the input."""
    start = State(((0, 1, 2), (0, 3, 4), (3, 7, 8)))
    end = State(start.knots + ((2, 5, 6), (4, 9, 10)), start)
    expected = {
        (1, 7): False,
        (0, 7): True,
        (5, 9): False,
        (1, 5): False,
        (2, 5): False,
        (0, 5): True,
    }
    assert all((pair in end.birth_pairs) == allowed for pair, allowed in expected.items())
    return [{"pair": pair, "eligible": allowed} for pair, allowed in expected.items()]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int)
    parser.add_argument("--regenerate-starts", action="store_true")
    args = parser.parse_args()
    began = monotonic()
    starts = read_starts()
    source_seconds = None
    if args.regenerate_starts:
        assert starts == regenerated_starts()
        source_seconds = monotonic() - began
    control = mixed_age_loose_control()
    main_audit = audit_counts()
    main_rows = [recount(start, supports, 4, main_audit) for start, supports in enumerate(starts[:args.limit])]
    main_summary = summarize(main_rows, main_audit)
    if args.limit is not None:
        print(json.dumps({
            "seconds": round(monotonic() - began, 3),
            "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
            "checked prefix": main_summary,
        }, indent=2))
        return

    prior_to_supplement = monotonic()
    growing = [row["start"] for row in main_rows if row["end"] == "growing"]
    selected = random.Random(20261127).sample(growing, 200)
    past_audit = audit_counts()
    past_rows = [recount(start, starts[start], 5, past_audit) for start in selected]
    past_summary = summarize(past_rows, past_audit)
    result = {
        "weighting": "One vote per census start. The fifth-round supplement samples without replacement.",
        "starts regenerated in identical order": args.regenerate_starts,
        "source regeneration seconds": None if source_seconds is None else round(source_seconds, 3),
        "four-round census": main_summary,
        "fifth-round supplement": past_summary,
        "replay comparisons": {
            "results.jsonl": compare(main_rows, "results.jsonl"),
            "past.jsonl": compare(past_rows, "past.jsonl"),
            "posthoc_losses.json": check_losses(main_audit),
        },
        "mixed-age loose control outside ordinary growth": control,
        "four-round seconds including census source": round(prior_to_supplement - began, 3),
        "total seconds": round(monotonic() - began, 3),
        "peak KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
    }
    (HERE / "census.json").write_text(json.dumps(result, indent=2) + "\n")
    for section, result_rows in result["replay comparisons"].items():
        print(section, result_rows)
    print("Run seconds", result["total seconds"], "Peak KiB", result["peak KiB"])


if __name__ == "__main__":
    main()
