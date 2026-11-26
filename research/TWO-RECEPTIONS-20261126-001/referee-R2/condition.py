"""Check three short histories from the written rules, including the projected parity relations.

Run with PYTHONPATH=tools .venv/bin/python -B and choose joined, passing, earlier or all.
The two census starts use the take across parts. The eight-knot start uses
the oldest eligible shared distinction.
"""

import argparse
from collections import Counter, deque
from contextlib import redirect_stdout
from io import StringIO
from itertools import combinations, product
import json
from resource import RUSAGE_SELF, getrusage
from time import process_time

from knotlab.cli import main as knotlab
from knotlab.relations import Relation


def joined_start(case):
    # Three knots. The first holds one loose distinction and shares once with
    # each of the other two, which hold two and three loose distinctions.
    # The three-loose end is the site. The sender consists of one knot.
    if case == "joined":
        rows = [[0, 1, 2], [0, 3, 4], [1, 5, 6, 7], [8, 9, 10]]
        left, sender, next_name = 2, 3, 11
    else:
        # Four knots, with only the second and fourth lacking a shared
        # distinction with each other. The site is the fourth; the sender is a stub.
        rows = [[0, 1, 2], [0, 3, 5], [1, 3, 4, 6, 7], [2, 4, 8, 9]]
        left, sender, next_name = 3, None, 10
    for meeting in range(3):
        right = sender
        if meeting < 2 or right is None:
            right = len(rows)
            rows.append([])
        d = next_name
        rows.append([d, d + 1, d + 2])
        rows[left].extend([d, d + 3])
        rows[right].extend([d + 1, d + 2, d + 4])
        left, next_name = right, d + 5
    return rows


EARLIER_START = [
    [10, 4, 5], [11, 6, 7], [2, 4, 5, 6, 7], [2, 0, 3, 8],
    [2, 1, 9], [0, 1, 3], [8, 12, 13], [9, 14, 15],
]


DESCRIPTIONS = {
    "joined": "Three-knot receiver sited at its end with three loose distinctions, one-knot sender, take across parts.",
    "passing": "Four-knot receiver with five shared pairs and loose counts 0, 1, 2, 2, sited at its fourth knot, "
               "a stub as sender, take across parts.",
    "earlier": "The eight-knot unjoined start with a three-holder distinction, oldest eligible local take.",
}


def meetings(rows):
    places = list(map(set, rows))
    return [{v for v, other in enumerate(places) if u != v and row & other}
            for u, row in enumerate(places)]


def groups(rows, members):
    """Enumerate subsets directly. Every common knot stays in the structure."""
    meets = meetings(rows)
    pairs = {p for p in combinations(sorted(members), 2) if any(set(p) <= m for m in meets)}
    larger = []
    for size in range(3, len(members) + 1):
        for q in combinations(sorted(members), size):
            if not all(p in pairs for p in combinations(q, 2)):
                continue
            if any(set(q) <= m for m in meets):
                continue
            if any(all(tuple(sorted((u, v))) in pairs for u in q) for v in set(members) - set(q)):
                continue
            larger.append(q)
    larger.sort()
    for group in larger:
        pairs.difference_update(combinations(group, 2))
    return larger + sorted(pairs)


def all_row_sums(rows):
    sums = {0: ()}
    for u, row in enumerate(rows):
        bits = sum(1 << d for d in row)
        sums.update({old ^ bits: subset + (u,) for old, subset in sums.items()})
    return sums


def weight(groups_):
    return Counter(u for group in groups_ for u in group)


def mask(places):
    return sum(1 << d for d in places)


def supported_equations(rows, visible):
    """Eliminate outside places first and track an explicit sum of old rows."""
    outside, inside = {}, {}
    for u, places in enumerate(rows):
        word, origin = mask(places), 1 << u
        while word:
            hidden = word & ~visible
            table = outside if hidden else inside
            pivot = (hidden or word).bit_length() - 1
            if pivot not in table:
                table[pivot] = (word, origin)
                break
            rule, source = table[pivot]
            word ^= rule
            origin ^= source
    return inside


def witness(basis, target):
    origin = 0
    while target:
        pivot = target.bit_length() - 1
        if pivot not in basis:
            return None
        rule, source = basis[pivot]
        target ^= rule
        origin ^= source
    return [u for u in range(origin.bit_length()) if origin & (1 << u)]


def check_projection(rows, inputs):
    """All old parity equations supported on the inputs govern their projection.

    Each other birth has a private fresh distinction. Its equation can be
    satisfied for every old word, so the same projection holds after the round.
    """
    inputs = sorted(inputs)
    visible = mask(inputs)
    basis = supported_equations(rows, visible)
    origin = witness(basis, visible)
    assert origin is not None
    basis_rows = [[d for d in inputs if rule & (1 << d)] for rule, _ in basis.values()]
    supported = set(all_row_sums(basis_rows)) - {0}
    minimal = sorted(b for b in supported if not any(c != b and b & c == c for c in supported))
    rules = [[d for d in inputs if b & (1 << d)] for b in minimal]
    assert set(all_row_sums(rules)) == supported | {0}
    result = {"input_places": inputs, "old_rows_whose_sum_is_the_input": origin,
              "nonzero_supported_row_sums": len(supported), "minimal_even_parity_rules": rules,
              "words_if_only_whole_parity": 1 << (len(inputs) - 1)}
    names = [f"d{d}" for d in inputs]
    if len(inputs) == 15:
        # Construct the actual projected relation. The ancillary minimum-width
        # search in the command enumerates clauses through width 15. Here the
        # same K1–K3 operations on the canonical Relation suffice.
        assert rules == [inputs]
        relation = Relation(tuple(names), frozenset(word for word in product((False, True), repeat=15)
                                                     if sum(word) % 2 == 0))
        projected = [relation.project(names[:i] + names[i + 1:]) for i in range(len(names))]
        k1, k2, k3 = not relation.is_full(), all(p.is_full() for p in projected), not relation.is_empty()
        result.update(words_on_input_places=len(relation.rows), K1=k1, K2=k2, K3=k3, is_knot=k1 and k2 and k3,
                      words_after_forgetting_each_place=[len(p.rows) for p in projected],
                      check="Direct K1–K3 on all words using the canonical finite Relation and its projections.")
        return result
    clauses = []
    for rule in rules:
        for word in product((0, 1), repeat=len(rule)):
            if sum(word) % 2:
                clauses.append(" ".join(("~" if bit else "") + f"d{d}" for d, bit in zip(rule, word)))
    cnf = "; ".join(clauses)
    args = ["check", "--cnf", cnf, "--loops", *names[:-1], "--contact", names[-1], "--json"]
    output = StringIO()
    with redirect_stdout(output):
        assert knotlab(args) == 0
    check = json.loads(output.getvalue())
    result.update(words_on_input_places=len(check["allowed"]), K1=check["binding"],
                  K2=check["loss_on_erasure"], K3=check["coexistence"], is_knot=check["is_knot"],
                  knotlab_arguments=args)
    return result


def advance(rows, case):
    meets = meetings(rows)
    counts = Counter(d for row in rows for d in row)
    stock = {u: deque(sorted(d for d in row if counts[d] == 1)) for u, row in enumerate(rows)}
    members = sorted(u for u in stock if stock[u])
    initial = groups(rows, members)
    owes = weight(initial)
    short = {u for u in members if owes[u] > len(stock[u])}
    kept = [group for group in initial if short.isdisjoint(group)]
    kept_owing = weight(kept)
    parents = kept + [(u,) for u in members if u not in short for _ in range(len(stock[u]) - kept_owing[u])]
    parts = {u: {u} for u in members}
    for group in initial:
        merged = set().union(*(parts[u] for u in group))
        for u in merged:
            parts[u] = merged
    born, inputs = {}, []
    for ps in parents:
        u = len(rows) + len(inputs)
        loose = [stock[p].popleft() for p in ps]
        taken = []
        if case != "earlier" and len(ps) == 1:
            taken = sorted({d for v in set(members) - parts[ps[0]] for d in rows[v] if counts[d] >= 2})
        if case == "earlier":
            sources = set.intersection(*(meets[p] for p in ps)) - set(ps)
            eligible = {d for v in sources for d in rows[v] if counts[d] >= 2}
            eligible.difference_update(*(rows[p] for p in ps))
            taken = [min(eligible)] if eligible else []
        taken_inputs = loose + taken
        target = mask(taken_inputs)
        implied = witness(supported_equations(rows, target), target) is not None
        born[u] = {"parents": ps, "loose_inputs": loose, "shared_inputs": taken, "implied": implied}
        inputs.append(taken_inputs)
    persisting = {u for u, remaining in stock.items() if remaining}
    assert persisting == short
    after = rows + inputs
    provisional_members = {*born, *persisting}
    provisional = groups(after, provisional_members)
    demand = weight(provisional)
    live = sorted(persisting)
    next_name = 1 + max(counts)
    funded_places = [list(row) for row in after]
    for u, record in born.items():
        fresh = 0 if record["implied"] else max(1, 3 - len(after[u]), demand[u])
        record.update(demand=demand[u], fresh=fresh)
        if fresh:
            live.append(u)
            funded_places[u].extend(range(next_name, next_name + fresh))
            next_name += fresh
    actual = groups(funded_places, live)
    owing = weight(actual)
    for u in set(live) & born.keys():
        born[u]["next_owing"] = owing[u]
    shortage = [u for u in live if u in born and owing[u] > born[u]["fresh"]]
    return funded_places, {"start_groups": initial, "start_waiting": sorted(short),
                           "start_parts": sorted({tuple(sorted(part)) for part in parts.values()}),
                           "births": born, "provisional_groups": provisional, "next_groups": actual,
                           "common_knots_of_all_provisional_members": [
                               u for u, m in enumerate(meetings(after)) if provisional_members <= m],
                           "common_knots_of_all_survivors": [
                               u for u, m in enumerate(meetings(after)) if set(live) <= m],
                           "short_newborns_on_next_roster": shortage}


def checked_history(case):
    start = EARLIER_START if case == "earlier" else joined_start(case)
    history, checked = [], []
    rows = start
    for step in range(1, (3 if case == "passing" else 1) + 1):
        previous = rows
        rows, record = advance(rows, case)
        history.append(record)
        if step == 1:
            checked.append([len(supported_equations(previous, mask(row))) for row in previous])
        checked.append([len(supported_equations(rows, mask(row))) for row in rows])
    born = record["births"]
    implied, = [u for u in born if born[u]["implied"]]
    projection = check_projection(previous, rows[implied])
    provisional, actual = record["provisional_groups"], record["next_groups"]
    demand, owing = weight(provisional), weight(actual)
    live = [u for u in born if born[u]["fresh"]]
    shortage = record["short_newborns_on_next_roster"]
    if case == "joined":
        assert len(provisional) == 43 and len(actual) == 33 and demand[implied] == 10
        assert all(owing[u] == demand[u] - 1 for u in live) and not shortage
        assert projection["words_on_input_places"] == 256 and not projection["is_knot"]
    elif case == "passing":
        assert implied == 34 and len(provisional) == 16 and len(actual) == 13 and demand[implied] == 8
        assert Counter(owing[u] - demand[u] for u in live) == {0: 8, -1: 3} and not shortage
        assert projection["words_on_input_places"] == 16384 and projection["is_knot"]
        assert all(rank == 1 for endpoint in checked for rank in endpoint)
    else:
        assert len(provisional) == 1 and len(actual) == 6 and demand[implied] == 1
        assert all(owing[u] == 3 and demand[u] == 1 for u in live) and len(shortage) == 4
        assert projection["words_on_input_places"] == 4 and projection["is_knot"]
    return {"description": DESCRIPTIONS[case], "start_places": start,
            "start_maximum_holders": max(Counter(d for row in start for d in row).values()),
            "rounds": history, "supported_constraint_counts_by_knot_at_each_endpoint": checked,
            "implied_id": implied, "implied_birth_projection": projection}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("case", choices=("joined", "passing", "earlier", "all"))
    choice = parser.parse_args().case
    start = process_time()
    cases = ("joined", "passing", "earlier") if choice == "all" else (choice,)
    result = {case: checked_history(case) for case in cases}
    result["cpu_seconds"] = round(process_time() - start, 6)
    result["peak_resident_kib"] = getrusage(RUSAGE_SELF).ru_maxrss
    print(json.dumps(result, indent=2))
