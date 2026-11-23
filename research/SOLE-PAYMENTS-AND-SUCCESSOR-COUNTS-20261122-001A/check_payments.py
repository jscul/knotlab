"""Independently reconstruct the registered sole-payment comparisons."""

from argparse import ArgumentParser
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from hashlib import sha256
from itertools import combinations, product
from pathlib import Path
from random import Random
from subprocess import run
import json
import os
import sys

import networkx as nx
from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
FREEZE = HERE / "preregistration.md"
FREEZE_SHA256 = "6c0fb07f1c9c54351addd62a2251c5e956835e24cd204df1cc65b27ee047a963"
OPERATOR = ROOT / ("experiments/ORDINARY-DYNAMICS-20261120-001A/"
                   "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary")
sys.path.insert(0, str(OPERATOR))
from end_operator import from_stars, step

LAWS = ("parity", "nae")
A, X, M, Y, B, S, T, Z = range(8)
DEPTH = 8


def build_source(meetings, capacity, ones_per_meeting):
    stars = [[] for _ in capacity]
    paid_between = {}
    private = {}
    word = {}
    for left, right, shared in meetings:
        names = tuple(range(len(word), len(word) + shared))
        paid_between[frozenset((left, right))] = names
        stars[left].extend(names)
        stars[right].extend(names)
        word.update((d, int(offset < ones_per_meeting)) for offset, d in enumerate(names))
    for holder, count in enumerate(capacity):
        private[holder] = tuple(range(len(word), len(word) + count))
        stars[holder].extend(private[holder])
        word.update(dict.fromkeys(private[holder], 0))
    return tuple(map(tuple, stars)), word, paid_between, private


def sole_source(remote_loose):
    meetings = [(A, X, 4), (X, M, 3), (M, Y, 3), (Y, B, 3)]
    capacity = [1, 0, 2, 0, 1]
    if remote_loose:
        meetings.extend(((M, S, 3), (S, T, 3), (T, Z, 3)))
        capacity.extend((0, 0, remote_loose))
    return build_source(meetings, capacity, 2)


def change_between(word, between, private, route):
    """Switch two initially loose values while preserving every founder parity."""
    changed = word.copy()
    flipped = [private[route[0]][0], private[route[-1]][0]]
    flipped.extend(between[frozenset((left, right))][0] for left, right in zip(route, route[1:]))
    for d in flipped:
        changed[d] ^= 1
    return changed, flipped


def holdings(stars):
    owners = defaultdict(list)
    ordinary = nx.Graph()
    ordinary.add_nodes_from(range(len(stars)))
    for holder, support in enumerate(stars):
        assert len(support) == len(set(support))
        for d in support:
            owners[d].append(holder)
    loose = defaultdict(list)
    for d, who in owners.items():
        if len(who) == 1:
            loose[who[0]].append(d)
        else:
            assert len(who) == 2
            ordinary.add_edge(*who)
    assert nx.is_connected(ordinary)
    return owners, ordinary, {k: tuple(sorted(ds)) for k, ds in loose.items()}


def complete_groups(live, blocks):
    """Derive groups from complete subsets of the witnessed neighbor relation."""
    witnessed = nx.Graph()
    witnessed.add_nodes_from(live)
    for block in blocks:
        witnessed.add_edges_from(combinations(block, 2))
    larger = sorted(tuple(sorted(clique)) for clique in nx.find_cliques(witnessed)
                    if len(clique) >= 3 and not any(set(clique) <= block for block in blocks))
    covered = {pair for group in larger for pair in combinations(group, 2)}
    pairs = sorted(tuple(sorted(edge)) for edge in witnessed.edges)
    groups = tuple(larger + [pair for pair in pairs if pair not in covered])
    return groups, tuple(sorted(tuple(sorted(component)) for component in nx.connected_components(witnessed)))


def groups_at(ordinary, loose):
    blocks = [set(ordinary[k]).intersection(loose) for k in ordinary]
    return complete_groups(loose, blocks)


def reconstruct_plan(stars, law):
    _, ordinary, loose = holdings(stars)
    candidate, components = groups_at(ordinary, loose)
    uses = Counter(k for group in candidate for k in group)
    assert all(uses[k] <= len(ds) for k, ds in loose.items())
    parents = candidate + tuple((k,) for k, ds in sorted(loose.items()) for _ in range(len(ds) - uses[k]))
    children = defaultdict(set)
    for child, group in enumerate(parents):
        for k in group:
            children[k].add(child)
    next_groups, _ = complete_groups(range(len(parents)), list(children.values()))
    counts = Counter(k for group in next_groups for k in group)
    demand = tuple(counts[k] for k in range(len(parents)))
    implied = law == "parity" and len(parents) == 1
    fresh = tuple(0 if implied else max(demand[k], 3 - len(group), 1) for k, group in enumerate(parents))
    reference = step(from_stars(stars), law)
    assert reference.status == ("extend" if loose else "closed")
    assert (reference.parents, reference.demand, reference.fresh, reference.implied) == (parents, demand, fresh, implied)
    return loose, parents, fresh, demand, components, implied


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple
    paid: tuple
    fresh: tuple

    def record(self):
        return {"knot": self.knot, "parents": self.parents, "paid": self.paid, "fresh": self.fresh}


@dataclass(frozen=True)
class Cut:
    stars: tuple
    births: tuple
    demand: tuple
    components: tuple
    implied: bool


def reconstruct_delivery(older, newer, law):
    """Check a given physical delivery, without trusting the producer's roster or names."""
    assert newer[:len(older)] == older
    owners, _, loose = holdings(older)
    _, parents, fresh, _, _, _ = reconstruct_plan(older, law)
    pending = Counter(zip(parents, fresh, strict=True))
    spent, issued = [], []
    births = []
    for k in range(len(older), len(newer)):
        support = newer[k]
        actual = {}
        born = []
        for d in support:
            if d in owners:
                assert len(owners[d]) == 1
                parent, = owners[d]
                assert parent not in actual
                actual[parent] = d
            else:
                born.append(d)
        group = tuple(sorted(actual))
        paid = tuple(actual[p] for p in group)
        assert pending[group, len(born)] > 0, "unrecognized parent roster or fresh grant"
        pending[group, len(born)] -= 1
        spent.extend(paid)
        issued.extend(born)
        births.append(Birth(k, group, paid, tuple(born)))
    assert not +pending
    assert len(issued) == len(set(issued))
    assert sorted(spent) == sorted(d for ds in loose.values() for d in ds)
    return tuple(births)


def grow(stars, law, reverse=False):
    loose, parent_lists, fresh, demand, _, implied = reconstruct_plan(stars, law)
    owners, _, _ = holdings(stars)
    pools = {k: iter(ds[::-1] if reverse else ds) for k, ds in loose.items()}
    next_name = max(owners) + 1
    grown = list(stars)
    for parents, count in zip(parent_lists, fresh, strict=True):
        paid = tuple(next(pools[k]) for k in parents)
        grown.append((*paid, *range(next_name, next_name + count)))
        next_name += count
    target = tuple(grown)
    births = reconstruct_delivery(stars, target, law)
    _, ordinary, open_names = holdings(target)
    _, components = groups_at(ordinary, open_names)
    return Cut(target, births, demand, components, implied)


def words(size):
    return product((0, 1), repeat=size)


def lawful(word, law):
    return sum(word) % 2 == 0 if law == "parity" else 0 < sum(word) < len(word)


@cache
def forbidden(law, size):
    if law == "nae":
        return (tuple([0] * size), tuple([1] * size))
    return tuple(row for row in words(size) if not lawful(row, law))


def provisions(stars, law):
    return [[d + 1 if b == 0 else -(d + 1) for d, b in zip(row, blocked, strict=True)]
            for row in stars for blocked in forbidden(law, len(row))]


def assumptions(values):
    return [d + 1 if bit else -(d + 1) for d, bit in values.items()]


def projection(solver, scope, fixed=()):
    return tuple(values for values in words(len(scope))
                 if solver.solve(assumptions=[*fixed, *assumptions(dict(zip(scope, values, strict=True)))]))


def validate_word(stars, word, law):
    assert set(word) == {d for row in stars for d in row}
    assert all(lawful(tuple(word[d] for d in row), law) for row in stars)


def verify_projections(stars, law, requested, arities):
    counts = {}
    with Minisat22(bootstrap_with=provisions(stars, law)) as solver:
        for k in requested:
            row = stars[k]
            allowed = projection(solver, row)
            implied = tuple(a for a in words(len(row)) if lawful(a, law))
            assert allowed == implied
            counts[k] = len(allowed)
            arities.add(len(row))
            if len(row) == 2:
                assert law == "parity" and allowed == ((0, 0), (1, 1))
    return counts


def allowed_bank(birth, old_word, law):
    paid = tuple(old_word[d] for d in birth.paid)
    return tuple(fresh for fresh in words(len(birth.fresh)) if lawful(paid + fresh, law))


def complete(older, cut, values, law, prescribed=None):
    """Fill every fresh bank, checking that fixed actual older values are retained."""
    prescribed = prescribed or {}
    result = values.copy()
    for birth in cut.births:
        options = allowed_bank(birth, values, law)
        desired = prescribed.get(birth.knot, options[0])
        assert desired in options
        result.update(zip(birth.fresh, desired, strict=True))
    assert all(result[d] == value for d, value in values.items())
    validate_word(older, values, law)
    validate_word(cut.stars, result, law)
    return result


def conditional(stars, older_values, scopes, law):
    with Minisat22(bootstrap_with=provisions(stars, law)) as solver:
        fixed = assumptions(older_values)
        return {key: projection(solver, names, fixed) for key, names in scopes.items()}


def founder_mark(stars):
    owners, _, loose = holdings(stars)
    sizes = Counter(tuple(row) for row in owners.values() if len(row) == 2)
    meeting, = [pair for pair, count in sizes.items() if count == 4]
    mark, = [k for k in meeting if len(loose.get(k, ())) == 1]
    return mark


def picked_receipt(first, second, a, b, m):
    left, = [c for c in first.births if set(c.parents) == {a, m}]
    right, = [c for c in first.births if set(c.parents) == {b, m}]
    receiver, = [c for c in second.births if set(c.parents) == {left.knot, right.knot}]
    assert len(left.fresh) == len(right.fresh) == 1
    assert set(receiver.paid) == {left.fresh[0], right.fresh[0]}
    return left, right, receiver


def receipt_panel(stars, original_word, law, first, second, a=A, b=B, m=M):
    left, right, receipt = picked_receipt(first, second, a, b, m)
    validate_word(stars, original_word, law)
    one, two = left.fresh + right.fresh
    projected = conditional(first.stars, original_word, {"both_payer_banks": (one, two)}, law)["both_payer_banks"]
    independent = tuple(product((w[0] for w in allowed_bank(left, original_word, law)),
                                (w[0] for w in allowed_bank(right, original_word, law))))
    assert projected == independent
    return_rows = []
    selected = None
    for bits in projected:
        new_word = complete(stars, first, original_word, law, {left.knot: bits[:1], right.knot: bits[1:]})
        paid = tuple(new_word[d] for d in receipt.paid)
        choices = conditional(second.stars, new_word, {"fresh": receipt.fresh}, law)["fresh"]
        assert choices == allowed_bank(receipt, new_word, law)
        result = complete(first.stars, second, new_word, law)
        if selected is None:
            selected = result
        return_rows.append({"payer_values": bits, "receipt_inputs": paid, "signal": int(paid[0] != paid[1]),
                            "receipt_fresh_words": choices, "old_word_preserved": True})
    return {"first_cohort_paid_values": [[original_word[d] for d in c.paid] for c in (left, right)],
            "original_word": sorted(original_word.items()), "payers": [left.record(), right.record()],
            "receiver": receipt.record(), "conditional_truth_table": return_rows}, selected


def exchange_siblings(cut, parent):
    a, b = [child for child in cut.births if child.parents == (parent,)]
    assert len(a.fresh) == len(b.fresh) == 2
    renamed_holders = {a.knot: b.knot, b.knot: a.knot}
    renamed_slots = {a.paid[0]: b.paid[0], b.paid[0]: a.paid[0]}
    for x, y in zip(a.fresh, b.fresh, strict=True):
        renamed_slots.update({x: y, y: x})
    for k, support in enumerate(cut.stars):
        expected = cut.stars[renamed_holders.get(k, k)]
        assert {renamed_slots.get(d, d) for d in support} == set(expected)
    return {"parent": parent, "equivalent_children": [a.knot, b.knot],
            "transported_distinctions": sorted(renamed_slots.items()), "all_other_holders_fixed": True}


def enrollment(cuts, original):
    current = original
    banks = {}
    rows = []
    for age, cut in enumerate(cuts, 1):
        children = [child for child in cut.births if current in child.parents]
        if not children:
            rows.append({"age": age, "predecessor": current, "status": "no child"})
            break
        chosen = min(children, key=lambda child: (len(child.parents) != 2, child.knot))
        rows.append({"age": age, "predecessor": current, "children": [c.knot for c in children],
                     "chosen": chosen.knot, "return": len(chosen.parents) == 2,
                     "payer_fresh_counts": [banks.get(p) for p in chosen.parents],
                     "selection": "unique" if len(children) == 1 else "supplied structural choice"})
        banks.update((child.knot, len(child.fresh)) for child in cut.births)
        current = chosen.knot
    return rows


def continue_from_designated_slot(states, receipt, values):
    unary, = [child for child in states[2].births if child.parents == (receipt.knot,)]
    assert len(unary.fresh) == 2
    slot = unary.fresh[0]
    siblings = [child for child in states[3].births if child.parents == (unary.knot,)]
    left, = [child for child in siblings if child.paid == (slot,)]
    right, = [child for child in siblings if child != left]
    receiver = right
    endpoint = left
    tail = []
    for age, cut in enumerate(states[4:], 5):
        pair = {receiver.knot, endpoint.knot}
        next_receiver, = [child for child in cut.births if set(child.parents) == pair]
        next_endpoint, = [child for child in cut.births if child.parents == (endpoint.knot,)]
        payer_counts = [len(endpoint.fresh), len(receiver.fresh)]
        assert len(next_receiver.parents) == 2 and payer_counts == [2, 2]
        observed = [values[d] for d in next_receiver.paid]
        tail.append({"age": age, "receiver_birth": next_receiver.record(),
                     "continued_endpoint": next_endpoint.record(), "payer_fresh_counts": payer_counts,
                     "paid_values": observed, "signal": int(observed[0] != observed[1])})
        receiver, endpoint = next_receiver, next_endpoint
    return {"one_supplied_distinction": slot, "unary_handoff": unary.record(),
            "left_child": left.record(), "other_child": right.record(), "subsequent_returns": tail}


def course(source, starting, law, arities, remote):
    first = grow(source, law)
    second = grow(first.stars, law)
    quiet_read, selected = receipt_panel(source, starting, law, first, second)
    assert selected is not None
    projections = [verify_projections(source, law, range(len(source)), arities)]
    previous = source
    parts = {A: "clock", M: "clock", B: "clock"}
    if remote:
        parts[Z] = "remote"
    states = [first, second]
    latest = second.stars
    values = selected
    for _ in range(2, DEPTH):
        following = grow(latest, law)
        states.append(following)
        if not following.births:
            break
        values = complete(latest, following, values, law)
        latest = following.stars
    records = []
    for age, cut in enumerate(states, 1):
        for child in cut.births:
            assert all(parent < len(previous) for parent in child.parents)
            branch, = {parts[p] for p in child.parents}
            parts[child.knot] = branch
        assert all(len({parts[k] for k in component}) == 1 for component in cut.components)
        projections.append(verify_projections(cut.stars, law, (c.knot for c in cut.births), arities))
        records.append({"age": age, "births": [child.record() for child in cut.births], "next_demand": cut.demand,
                        "loose_components": cut.components, "implied": cut.implied,
                        "loose_names": holdings(cut.stars)[2]})
        previous = cut.stars
    paths = enrollment(states, A)
    quiet_read.update(source=source, completed_cuts=records, projections=projections, external_enrollment=paths,
                      complete_reached_word=sorted(values.items()))
    _, _, receiver = picked_receipt(first, second, A, B, M)
    assert set(parts[p] for p in receiver.parents) == {"clock"}
    assert second.implied == (law == "parity" and remote == 0)
    assert any(component == (receiver.knot,) for component in second.components) == bool(receiver.fresh)
    scope = {"paid_pair": receiver.paid}
    before = conditional(first.stars, {}, scope, law)["paid_pair"]
    after = conditional(second.stars, {}, scope, law)["paid_pair"]
    assert before == after == (((0, 0), (1, 1)) if second.implied else tuple(words(2)))
    quiet_read["unconditioned_paid_projection"] = {"before_receipt": before, "after_receipt": after}
    if receiver.fresh:
        unary, = [child for child in states[2].births if receiver.knot in child.parents]
        assert unary.parents == (receiver.knot,) and len(unary.fresh) == 2
        quiet_read["intrinsic_enrollment_symmetry"] = {"age": 4, **exchange_siblings(states[3], unary.knot)}
        quiet_read["continued_from_designated_slot"] = continue_from_designated_slot(states, receiver, values)
    else:
        assert not states[2].births and not states[2].components
        quiet_read["closure_paid_projection"] = before
    return quiet_read, states


def positional_renaming(source, states, law, word):
    count = len(states[-1].stars)
    ds = sorted({d for row in states[-1].stars for d in row})
    bits = ds[:]
    rng = Random(20261122001)
    rng.shuffle(bits)
    bit_names = dict(zip(ds, bits, strict=True))
    names = list(range(count))
    ranges = [(0, len(source)), *[(len(cut.stars) - len(cut.births), len(cut.stars)) for cut in states]]
    for first, stop in ranges:
        indices = names[first:stop]
        rng.shuffle(indices)
        names[first:stop] = indices

    def rename(stars):
        renamed = [None] * len(stars)
        for k, support in enumerate(stars):
            renamed[names[k]] = tuple(bit_names[d] for d in support)
        return tuple(renamed)

    source_new = rename(source)
    assert founder_mark(source_new) == names[A]
    validate_word(source_new, {bit_names[d]: word[d] for d in {d for row in source for d in row}}, law)
    older = source_new
    for cut in states:
        newer = rename(cut.stars)
        actual = {birth.knot: birth for birth in reconstruct_delivery(older, newer, law)}
        for b in cut.births:
            mapped = actual[names[b.knot]]
            assert dict(zip(mapped.parents, mapped.paid, strict=True)) == {
                names[p]: bit_names[d] for p, d in zip(b.parents, b.paid, strict=True)
            }
            assert set(mapped.fresh) == {bit_names[d] for d in b.fresh}
        older = newer
    validate_word(older, {bit_names[d]: bit for d, bit in word.items()}, law)
    return {"renamed_source": source_new, "holder_transport": names,
            "distinction_transport": sorted(bit_names.items()), "word_transport_verified": True,
            "positive_cuts": sum(bool(c.births) for c in states)}


def wrong_grant(source, first, law):
    corrupted = list(first.stars)
    target = first.births[0].knot
    corrupted[target] = (*corrupted[target], max(d for s in corrupted for d in s) + 1)
    try:
        reconstruct_delivery(source, tuple(corrupted), law)
    except AssertionError as error:
        assert str(error) == "unrecognized parent roster or fresh grant"
        return {"rejected": True, "changed_knot": target, "reason": str(error)}
    raise AssertionError("wrong grant accepted")


def five_founders(law, arities):
    meetings = [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 3)]
    source, quiet, _, _ = build_source(meetings, [2] * 5, 1)
    verify_projections(source, law, range(len(source)), arities)
    stars = source
    phases = (0, 2, 4, 1, 3)
    initial = grow(source, law)
    cuts = [initial]
    for _ in range(5):
        following = grow(cuts[-1].stars, law)
        cuts.append(following)
    phase_holders = [phases]
    for cut in cuts:
        old = phase_holders[-1]
        roster = {frozenset(b.parents): b for b in cut.births}
        current = [roster[frozenset(pair)] for pair in zip(old, old[1:] + old[:1], strict=True)]
        assert len(cut.births) == 5 and all(len(b.fresh) == 2 for b in current)
        phase_holders.append(tuple(b.knot for b in current))
        verify_projections(cut.stars, law, (c.knot for c in cut.births), arities)
    selected_return = next(b for b in cuts[4].births if b.knot == phase_holders[5][0])
    payer = next(b for b in cuts[3].births if b.knot == phase_holders[4][1])
    paid = next(d for p, d in zip(selected_return.parents, selected_return.paid, strict=True) if p == payer.knot)
    state = quiet
    for age, cut in enumerate(cuts[:3], 1):
        state = complete(stars, cut, state, law, {b.knot: (age % 2,) * 2 for b in cut.births})
        stars = cut.stars
    first_signals = []
    for signal in (0, 1):
        alternatives = allowed_bank(payer, state, law)
        choice = next(bank for bank in alternatives if bank[payer.fresh.index(paid)] == signal)
        banks = {b.knot: (0, 0) for b in cuts[3].births}
        banks[payer.knot] = choice
        now = complete(stars, cuts[3], state, law, banks)
        later = complete(cuts[3].stars, cuts[4], now, law)
        paid_values = tuple(later[d] for d in selected_return.paid)
        assert int(paid_values[0] != paid_values[1]) == signal
        first_signals.append({"signal": signal, "payer_choice": choice, "paid_values": paid_values})

    # Two binary receivers can share a payer, so both outputs may be jointly constrained.
    common = next(b for b in initial.births if b.knot == phase_holders[1][0])
    children = [b for b in cuts[1].births if common.knot in b.parents]
    assert len(children) == 2 and all(len(b.parents) == 2 for b in children)
    direct = {b.knot: b for b in initial.births}
    fixed = quiet.copy()
    for child in children:
        other, = set(child.parents) - {common.knot}
        actual_paid = child.paid[child.parents.index(other)]
        grant = direct[other]
        companion = next(bank for bank in allowed_bank(grant, quiet, law) if bank[grant.fresh.index(actual_paid)] == 0)
        fixed.update(zip(grant.fresh, companion, strict=True))
    names = tuple(child.paid[child.parents.index(common.knot)] for child in children)
    pair = conditional(cuts[1].stars, fixed, {"signals": names}, law)["signals"]
    assert pair == (((0, 0), (1, 1)) if law == "parity" else ((0, 1), (1, 0), (1, 1)))
    return {"source": source, "source_word": sorted(quiet.items()), "phase_holders": phase_holders,
            "first_return": selected_return.record(), "first_return_values": first_signals,
            "simultaneous_read": {"common_payer": common.record(), "receivers": [c.record() for c in children],
                                  "fixed_old_values": sorted(fixed.items()), "allowed_signal_pairs": pair}}


def knot_checks(law, arities):
    reports = {}
    for arity in sorted(arities):
        if arity == 2:
            reports[arity] = {"projection": ["00", "11"], "classification": "implied two-input equality"}
            continue
        labels = [f"d{i}" for i in range(arity)]
        cnf = ";".join(" ".join(neg + x for neg, x in zip(("~" if v else "" for v in row), labels, strict=True))
                       for row in forbidden(law, arity))
        cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
               "--loops", *labels[:-1], "--contact", labels[-1], "--json"]
        result = run(cmd, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                     check=True, capture_output=True, text=True)
        report = json.loads(result.stdout)
        assert all(report[k] for k in ("binding", "loss_on_erasure", "coexistence", "is_knot"))
        expected = ["".join(map(str, row)) for row in words(arity) if lawful(row, law)]
        assert report["allowed"] == expected
        reports[arity] = {"binding": report["binding"], "loss_on_erasure": report["loss_on_erasure"],
                          "coexistence": report["coexistence"], "is_knot": report["is_knot"],
                          "allowed_word_count": len(expected)}
    return reports


def study():
    assert sha256(FREEZE.read_bytes()).hexdigest() == FREEZE_SHA256
    cases = {}
    arities = {law: set() for law in LAWS}
    for law in LAWS:
        arms = {}
        for remote in (0, 1, 2):
            key = str(remote)
            source, quiet, between, private = sole_source(remote)
            assert founder_mark(source) == A
            original, states = course(source, quiet, law, arities[law], remote)
            first, second = states[:2]
            alternate_first = grow(source, law, reverse=True)
            alternate_second = grow(alternate_first.stars, law, reverse=True)
            new_read, _ = receipt_panel(source, quiet, law, alternate_first, alternate_second)
            assert original["conditional_truth_table"] == new_read["conditional_truth_table"]
            assert original["payers"][0]["paid"] != new_read["payers"][0]["paid"]
            route = (A, X, M, S, T, Z) if remote else (A, X, M, Y, B)
            changed, flipped = change_between(quiet, between, private, route)
            for tested_law in LAWS:
                validate_word(source, quiet, tested_law)
                validate_word(source, changed, tested_law)
            different, _ = receipt_panel(source, changed, law, first, second)
            if law == "nae":
                assert {row["payer_values"][0] for row in different["conditional_truth_table"]} == {0, 1}
            else:
                assert all(row["signal"] == int(remote > 0) for row in different["conditional_truth_table"])
            arms[key] = {"quiet": original, "reverse_binding": new_read,
                         "changed": {"flipped": flipped, **different},
                         "renamed_binding": positional_renaming(source, states, law, dict(original["complete_reached_word"]))}
            if remote == 0:
                arms[key]["wrong_grant"] = wrong_grant(source, first, law)
            if remote == 1:
                fixed, flipped = change_between(quiet, between, private, (A, X, M))
                first_value, _ = receipt_panel(source, fixed, law, first, second)
                other_binding, _ = receipt_panel(source, fixed, law, alternate_first, alternate_second)
                assert first_value["original_word"] == other_binding["original_word"]
                assert first_value["first_cohort_paid_values"] != other_binding["first_cohort_paid_values"]
                arms[key]["binding_with_distinct_founding_bits"] = {
                    "flipped": flipped, "ascending": first_value, "descending": other_binding,
                }
        arms["five_founders"] = five_founders(law, arities[law])
        cases[law] = arms
    return {"preregistration_sha256": FREEZE_SHA256, "maximum_complete_depth": DEPTH,
            "laws": cases, "native_knot_checks": {law: knot_checks(law, arities[law]) for law in LAWS}}


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path)
    output = parser.parse_args().out
    payload = json.dumps(study(), separators=(",", ":"), sort_keys=True) + "\n"
    if output:
        output.write_text(payload)
    else:
        print(payload, end="")


if __name__ == "__main__":
    main()
