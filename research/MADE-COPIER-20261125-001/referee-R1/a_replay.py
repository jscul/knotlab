"""Replay ticket A and check its cases from the frozen growth definitions."""

import argparse
from collections import Counter
from dataclasses import dataclass, replace
from itertools import combinations, permutations, product
import json

from a_recount import REGISTERED


STARTS = json.loads((REGISTERED / "starts.json").read_text())
DESIGNS = STARTS["designs"]
TAKE_LISTS = json.loads((REGISTERED / "take_lists.json").read_text())["lists"]
CHOICES = ("OLDEST", "NEWEST", "IN-TURN", "BY-COUNT")
KNOT_LAWS = ("parity", "nae")
DESCENT = ("neither", "X only", "Y only", "both")
PAIR_LIMIT = 20_000


@dataclass(frozen=True)
class Law:
    ration: str
    treatment: str
    taking: str
    choice: str
    knot_law: str
    hold: bool = False
    demand_before_taking: bool = False
    reverse_births: bool = False


@dataclass(frozen=True)
class State:
    knots: tuple
    parents: tuple
    barred: frozenset
    distinctions: int
    descent: tuple
    t: int = 0
    births: tuple = ()
    waits: frozenset = frozenset()


@dataclass(frozen=True)
class Birth:
    parents: tuple
    regular: tuple
    candidates: tuple
    ordinal: int
    extra: int | None = None
    fresh: tuple = ()


class Guard(Exception):
    pass


def start(design, naming=None, order=None, reverse_knots=False):
    labels = sorted({value for knot in design["stars"] for value in knot})
    mapped = naming if isinstance(naming, dict) else {label: label for label in labels}
    if order is None:
        order = sorted(labels, key=lambda label: mapped.get(str(label), label), reverse=naming == "names reversed")
    names = {label: i for i, label in enumerate(order)}
    knots = tuple(frozenset(names[v] for v in values) for values in design["stars"])
    if reverse_knots:
        knots = knots[::-1]
    barred = frozenset(names[v] for v in design.get("barred", []))
    return State(knots, ((),) * len(knots), barred, len(names), (0,) * len(knots))


def mark(state, x, y):
    return replace(state, descent=tuple((i in x) + 2 * (i in y) for i in range(len(state.knots))))


def holders(knots):
    result = {}
    for i, knot in enumerate(knots):
        for distinction in knot:
            result.setdefault(distinction, set()).add(i)
    return result


def usable(holding, barred):
    counts = {}
    for distinction, keepers in holding.items():
        if len(keepers) == 1 and distinction not in barred:
            counts.setdefault(next(iter(keepers)), []).append(distinction)
    return {name: sorted(places) for name, places in counts.items()}


def meets(knots, holding, who):
    return set().union(*(holding[v] for v in knots[who])) - {who}


def met_sets(knots, holding, members):
    family = set()
    incidences = 0
    for i in range(len(knots)):
        keep = frozenset(meets(knots, holding, i) & members)
        if len(keep) >= 2:
            family.add(keep)
            incidences += len(keep)
            if incidences > 2_000_000 or len(keep) * (len(keep) - 1) // 2 > PAIR_LIMIT:
                raise Guard
    return family


def peers_from(members, family, descent=(), mask=None):
    peers = {member: set() for member in members}
    count = 0
    for met in family:
        for a, b in combinations(sorted(met), 2):
            if b in peers[a]:
                continue
            if mask == "cross" and ((descent[a] & 1 and descent[b] & 2) or (descent[a] & 2 and descent[b] & 1)):
                continue
            if mask in ("X", "Y"):
                flag = 1 if mask == "X" else 2
                if bool(descent[a] & flag) != bool(descent[b] & flag):
                    continue
            peers[a].add(b)
            peers[b].add(a)
            count += 1
            if count > PAIR_LIMIT:
                raise Guard
    return peers


def maximal_sets(peers):
    remaining = set(peers)
    done = set()
    visits = 0

    def extend(included, candidates, excluded):
        nonlocal visits
        visits += 1
        if visits > 200_000:
            raise Guard
        if not (candidates or excluded):
            yield included
            return
        pivot = max(candidates | excluded, key=lambda member: len(peers[member] & candidates))
        for x in candidates - peers[pivot]:
            yield from extend(included | {x}, candidates & peers[x], excluded & peers[x])
            candidates.remove(x)
            excluded.add(x)

    yield from extend(frozenset(), remaining, done)


def groups(members, family, descent=(), mask=None):
    peers = peers_from(members, family, descent, mask)
    if not members:
        return []
    triples = [tuple(sorted(clique)) for clique in maximal_sets(peers)
               if len(clique) >= 3 and not any(clique <= met for met in family)]
    covered = {pair for clique in triples for pair in combinations(clique, 2)}
    pairs = [(a, b) for a in sorted(peers) for b in sorted(peers[a]) if a < b and (a, b) not in covered]
    if len(triples) + len(pairs) > 20_000:
        raise Guard
    return sorted(triples) + pairs


def basis(rows):
    pivots = {}
    for row in rows:
        while row:
            place = row.bit_length() - 1
            if place not in pivots:
                pivots[place] = row
                break
            row ^= pivots[place]
    return pivots


def reduce(row, pivots):
    for place, value in sorted(pivots.items(), reverse=True):
        if row & (1 << place):
            row ^= value
    return row


def bits(places):
    return sum(1 << place for place in places)


def mask_for(state, parents):
    flag = 0
    for parent in parents:
        flag |= state.descent[parent]
    return flag


def prepare(state, law, mask=None):
    holding = holders(state.knots)
    loose = usable(holding, state.barred)
    members = set(loose)
    groupings = groups(members, met_sets(state.knots, holding, members), state.descent, mask)
    owed = Counter(member for group in groupings for member in group)
    short = {member for member in members if owed[member] > len(loose[member])}
    join_sets = [group for group in groupings if not short.intersection(group)]
    kept = Counter(member for group in join_sets for member in group)
    retirement = frozenset(v for member in short for v in loose[member]) if law.treatment == "RETIRE" else frozenset()
    waits = frozenset(short) if law.treatment == "WAIT" else frozenset()
    births = list(join_sets)
    for member in sorted(members):
        if member in short:
            offshoots = len(loose[member]) if law.treatment == "OFFSHOOT" else 0
        else:
            offshoots = len(loose[member]) - (owed[member] if law.hold else kept[member])
        births.extend([(member,)] * offshoots)
    if law.reverse_births:
        births.reverse()
    used = Counter()
    ordinals = Counter()
    result = []
    for parents in births:
        regular = []
        for member in parents:
            position = used[member]
            if law.hold and len(parents) == 1 and member not in short:
                position += owed[member] - kept[member]
            regular.append(loose[member][position])
            used[member] += 1
        rest = set()
        if law.taking == "MET":
            common = set.intersection(*(meets(state.knots, holding, p) for p in parents)) - set(parents)
            rest = set().union(*(state.knots[knot] for knot in common))
        elif len(parents) == 1 and law.taking.startswith("STEPS-"):
            previous = set(parents)
            for _ in range(int(law.taking.split("-")[1])):
                previous = {p for q in previous for p in state.parents[q]}
            rest = set().union(*(state.knots[knot] for knot in previous))
        elif len(parents) == 1 and law.taking == "Q":
            rest = set(state.knots[parents[0]])
        if law.taking != "Q":
            rest.difference_update(set().union(*(state.knots[knot] for knot in parents)))
        candidates = tuple(sorted(v for v in rest if len(holding[v]) >= 2 and v not in regular))
        ordinal = ordinals[parents]
        ordinals[parents] += 1
        result.append(Birth(parents, tuple(regular), candidates, ordinal))
    return result, state.barred | retirement, waits


def stated_choice(birth, state, choice):
    options = birth.candidates
    if choice == "OLDEST":
        return options[0]
    if choice == "NEWEST":
        return options[-1]
    if choice == "BY-COUNT":
        return options[len(state.knots[birth.parents[0]]) % len(options)]
    if choice == "IN-TURN":
        return options[birth.ordinal % len(options)]
    raise ValueError(choice)


def finish(state, law, prepared, choices, mask=None):
    births, barred, waits = prepared
    cursor = iter(choices)
    births = [replace(birth, extra=next(cursor)) if birth.candidates else birth for birth in births]
    assert all(birth.extra is None or birth.extra in birth.candidates for birth in births)
    assert next(cursor, None) is None
    inputs = [frozenset(birth.regular + ((birth.extra,) if birth.extra is not None else ())) for birth in births]
    descent = state.descent + tuple(mask_for(state, birth.parents) for birth in births)
    if law.ration in ("CAP-3", "ONE-FEWER"):
        demand_knots = state.knots + tuple(frozenset(birth.regular) for birth in births) if law.demand_before_taking else state.knots + tuple(inputs)
        demand_holdings = holders(demand_knots)
        members = set(usable(demand_holdings, barred)) | set(range(len(state.knots), len(demand_knots)))
        demand = Counter(member for group in groups(members, met_sets(demand_knots, demand_holdings, members), descent, mask)
                         for member in group)
    else:
        demand = Counter()
        # The fold engine guards the demand roster even when this ration ignores demand.
        if births:
            demand_knots = state.knots + (tuple(frozenset(birth.regular) for birth in births)
                                           if law.demand_before_taking else tuple(inputs))
            demand_holdings = holders(demand_knots)
            members = set(usable(demand_holdings, barred)) | set(range(len(state.knots), len(demand_knots)))
            groups(members, met_sets(demand_knots, demand_holdings, members), descent, mask)
    pivots = basis(bits(q) for q in state.knots) if law.knot_law == "parity" else None
    new_knots = []
    fresh_next = state.distinctions
    completed = []
    for i, (birth, fields) in enumerate(zip(births, inputs), len(state.knots)):
        n = len(birth.parents) if law.ration == "FBP" else len(fields)
        if law.ration in ("FLOOR1", "FBP"):
            fresh = max(1, 3 - n)
        elif law.ration == "FLOOR0":
            fresh = max(0, 3 - n)
        else:
            q = max(demand[i], 3 - n, 1)
            fresh = min(q, 3) if law.ration == "CAP-3" else min(q, max(3 - n, 0, q - 1))
        if pivots is not None and reduce(bits(fields), pivots) == 0:
            fresh = 0
        own = tuple(range(fresh_next, fresh_next + fresh))
        fresh_next += fresh
        new_knots.append(fields | set(own))
        completed.append(replace(birth, fresh=own))
    return State(state.knots + tuple(new_knots), state.parents + tuple(birth.parents for birth in births),
                 barred, fresh_next, descent, state.t + 1, tuple(completed), waits)


def grow(design, law, rounds=6, naming=None, order=None, reverse_knots=False, bar=None, take_list=None, mask=None,
         knot_bound=500):
    x, y = design.get("X", []), design.get("Y", [])
    if reverse_knots:
        # This option is used only on the two-founder made designs.
        size = len(design["stars"][1]) - 1
        x, y = list(range(2 + size, 4 + size)), list(range(2, 2 + size))
    snapshots = [start(design, naming, order, reverse_knots)]
    stopped = None
    for t in range(rounds + 1):
        snapshot = snapshots[-1]
        if t == design["s"]:
            snapshot = mark(snapshot, x, y)
            if bar:
                holding = holders(snapshot.knots)
                barred = snapshot.barred | {v for member in design.get(bar, []) for v in snapshot.knots[member]
                                           if len(holding[v]) == 1}
                snapshot = replace(snapshot, barred=barred)
            snapshots[-1] = snapshot
        if t == rounds:
            break
        try:
            prepared = prepare(snapshot, law, mask if t >= design["s"] else None)
            births = prepared[0]
            if take_list is not None and t >= design["s"]:
                picked = take_list[t - design["s"]]
            else:
                picked = [stated_choice(birth, snapshot, law.choice) for birth in births if birth.candidates]
            after = finish(snapshot, law, prepared, picked, mask if t >= design["s"] else None)
        except Guard:
            stopped = t + 1
            break
        snapshots.append(after)
        if len(after.knots) > knot_bound:
            break
    return snapshots, stopped


def roster(state):
    holding = holders(state.knots)
    loose = usable(holding, state.barred)
    met = met_sets(state.knots, holding, set(loose))
    peers = peers_from(set(loose), met)
    unseen = set(loose)
    parts = []
    while unseen:
        pending = [min(unseen)]
        part = set()
        while pending:
            member = pending.pop()
            if member not in unseen:
                continue
            unseen.remove(member)
            part.add(member)
            pending.extend(peers[member] & unseen)
        parts.append(frozenset(part))
    return holding, loose, met, parts


def part_form(state, part, loose, met):
    marks = {i: (len(loose[i]), len(state.knots[i] & state.barred)) for i in part}
    maximal = {q & part for q in met if len(q & part) >= 2}
    maximal = {q for q in maximal if not any(q < p for p in maximal)}
    classes = [[i for i in sorted(part) if marks[i] == marker] for marker in sorted(set(marks.values()))]
    profile = tuple(sorted(marks.values()))
    # The copied forms have at most six members. Larger parts cannot match them.
    return profile, min(tuple(sorted(tuple(sorted(names[i] for i in met_set)) for met_set in maximal))
                        for bundle in product(*(permutations(group) for group in classes))
                        for names in ({old: i for i, old in enumerate(sum(bundle, ()))},))


def target_form(snapshot, role):
    _, loose, met, parts = roster(snapshot)
    group = frozenset(i for i, descent in enumerate(snapshot.descent) if descent == role)
    assert group in parts
    return part_form(snapshot, group, loose, met)


def parts_read(snapshots, origin, target):
    out = []
    for snapshot in snapshots[origin + 1:]:
        try:
            _, loose, met, parts = roster(snapshot)
        except Guard:
            continue
        count = Counter()
        for part in parts:
            if len(part) != len(target[0]) or max(part) < len(snapshots[origin].knots):
                continue
            if part_form(snapshot, part, loose, met) == target:
                count[tuple(sorted({DESCENT[snapshot.descent[i]] for i in part}))] += 1
        out.append({"round": snapshot.t, "all": sum(count.values()), "X only": count[("X only",)],
                    "Y only": count[("Y only",)]})
    return out


def meeting_round(snapshots, origin):
    for state in snapshots[origin + 1:]:
        try:
            _, _, _, parts = roster(state)
        except Guard:
            continue
        if any(mask_for(state, part) == 3 for part in parts):
            return state.t
    return None


def parity_columns(state):
    pivots = basis(bits(knot) for knot in state.knots)
    return [reduce(1 << place, pivots) for place in range(state.distinctions)]


def eligible_values(origin, owner):
    columns = parity_columns(origin)
    x_places = set().union(*(origin.knots[i] for i, flag in enumerate(origin.descent) if flag == 1))
    places = set().union(*(origin.knots[i] for i, flag in enumerate(origin.descent) if flag == owner))
    forbidden = {columns[place] for place in x_places} if owner == 2 else set()
    return {place for place in places if columns[place] and columns[place] not in forbidden}


def parity_values(snapshots, origin):
    first = snapshots[origin]
    wanted = eligible_values(first, 2)
    result = []
    for snapshot in snapshots[origin + 1:]:
        columns = parity_columns(snapshot)
        holding = holders(snapshot.knots)
        for reference in sorted(wanted):
            matched = []
            for fresh in range(first.distinctions, snapshot.distinctions):
                keepers = holding[fresh]
                if len(keepers) == 1 and fresh not in snapshot.barred and columns[fresh] == columns[reference]:
                    matched.append((fresh, DESCENT[snapshot.descent[next(iter(keepers))]]))
            if len(matched) >= 2 and any(item[1] in ("X only", "both") for item in matched):
                result.append({"round": snapshot.t, "place of Y": reference, "made distinctions": matched,
                               "number of holders before": len(holders(first.knots)[reference]),
                               "number of holders now": len(holding[reference])})
    return result


def parity_failures(state):
    knot_rows = [bits(q) for q in state.knots]
    rank = len(basis(knot_rows))
    return [i for i, row in enumerate(knot_rows) if not row or rank - len(basis(x & ~row for x in knot_rows)) != 1]


def start_nae_ties(state):
    from pysat.solvers import Solver

    formula = [[sign * (v + 1) for v in knot] for knot in state.knots for sign in (-1, 1)]
    with Solver(bootstrap_with=formula) as solver:
        assert solver.solve()
        # Global complementation makes each choice of sign representative.
        return [(a - 1, b - 1) for a, b in combinations(range(1, state.distinctions + 1), 2)
                if not solver.solve(assumptions=[a, b]) or not solver.solve(assumptions=[a, -b])]


def start_checks(limit):
    checks = []
    for name, design in DESIGNS.items():
        snapshots, _ = grow(design, Law("FLOOR1", "RETIRE", "MET", "OLDEST", "parity"), rounds=design["s"])
        at_start = snapshots[0]
        after_s = snapshots[-1]
        for state in [at_start, after_s] if design["s"] else [at_start]:
            claim = parity_columns(state)
            checks.append({"design": name, "round": state.t,
                           "parity tie pairs": list((a, b) for a, b in combinations(range(len(claim)), 2) if claim[a] == claim[b]),
                           "parity frozen": claim.count(0), "not-all-equal tie pairs": start_nae_ties(state)})
    thirds = []
    kinds = STARTS["third pattern"]["knots"]
    configurations = ((name, kind, whom, places) for name, kind in product(kinds, repeat=2) if name != kind
                      for whom, places in kinds[kind].items())
    for index, (name, kind, whom, places) in enumerate(configurations):
        if limit is not None and index >= limit:
            break
        design = DESIGNS[f"ystart-{name}"]
        supplied = start({**design, "stars": design["stars"] + places})
        columns = parity_columns(supplied)
        thirds.append({"second pattern": name, "third pattern": kind, "naming": whom, "parity frozen": columns.count(0),
                       "parity ties": len(columns) - len(set(columns)), "not-all-equal tie pairs": start_nae_ties(supplied)})
    return checks, thirds


def values_replay():
    law = Law("FLOOR1", "OFFSHOOT", "MET", "NEWEST", "parity")
    name = "ystart-three-222"
    design = DESIGNS[name]
    out = {}
    variants = {"as registered": {}, "Y barred": {"bar": "Y"}, "X barred": {"bar": "X"}, "X and Y masked": {"mask": "cross"}}
    variants.update({name: {"naming": renaming} for name, renaming in STARTS["renamings"][name].items()})
    for label, options in variants.items():
        snapshots, stopped = grow(design, law, **options)
        out[label] = {"last round": snapshots[-1].t, "guard at": stopped,
                      "passing pairs": parity_values(snapshots, design["s"]),
                      "failing knots": {state.t: parity_failures(state) for state in snapshots}}
    snapshots, stopped = grow(design, law, rounds=8)
    out["two subsequent users"] = {
        str(place): [[state.t, i] for state in snapshots[7:] for i, birth in enumerate(state.births, len(state.knots) - len(state.births))
                     if place in birth.regular or place == birth.extra]
        for place in (52, 53)}
    small = DESIGNS["ystart-one-2"]
    snapshots, _ = grow(small, law)
    after = snapshots[-1]
    loose = usable(holders(after.knots), after.barred)
    columns = parity_columns(after)
    out["one second-pattern member holding two"] = {
        "X-only extra takes in round 3": [birth.extra for i, birth in enumerate(snapshots[3].births,
                                                                               len(snapshots[3].knots) - len(snapshots[3].births))
                                         if snapshots[3].descent[i] == 1 and birth.extra is not None],
        "ties of X-only usable loose made distinctions to start distinctions in last round": {
            str(v): [q for q in range(snapshots[0].distinctions) if columns[q] == columns[v] and columns[v]]
            for i, places in loose.items() if after.descent[i] == 1 for v in places if v >= snapshots[0].distinctions
        },
    }
    return out


def form_replay(limit):
    name = "made-4"
    design = DESIGNS[name]
    result = []
    for knot_law, (taking, choice) in product(KNOT_LAWS, (("MET", "BY-COUNT"), ("STEPS-1", "NEWEST"), ("STEPS-1", "BY-COUNT"))):
        law = Law("FBP", "OFFSHOOT", taking, choice, knot_law)
        out = {"knot law": knot_law, "taking rule": taking, "choice": choice}
        variants = {"as registered": {}, "Y barred": {"bar": "Y"}, **{
            name: {"naming": renaming} for name, renaming in STARTS["renamings"][name].items()}}
        original, _ = grow(design, law, rounds=design["s"])
        target = target_form(original[-1], 2)
        for label, options in variants.items():
            snapshots, stopped = grow(design, law, **options)
            out[label] = {"last round": snapshots[-1].t, "guard at": stopped,
                          "part counts": parts_read(snapshots, design["s"], target),
                          "meeting round": meeting_round(snapshots, design["s"])}
        alone = STARTS["alone"][name]["X alone"]
        snapshots, _ = grow(alone, law)
        out["X alone"] = parts_read(snapshots, alone["s"], target)
        out["replacements"] = {}
        for size in (3, 5, 6):
            replacement = DESIGNS[f"made-{size}"]
            trial, _ = grow(replacement, law)
            own = target_form(trial[replacement["s"]], 2)
            out["replacements"][f"second pattern with {size} members holding two"] = {
                "counts against the original second pattern": parts_read(trial, replacement["s"], target),
                "counts against its own second pattern": parts_read(trial, replacement["s"], own),
            }
        if taking == "STEPS-1" and choice == "NEWEST":
            numberings = []
            # A normalized numbering is fixed by the name of the shared distinction,
            # which two remaining names belong to X, and which founder is listed first.
            configs = ((shared, x_names, reverse) for shared in range(7)
                       for x_names in combinations(set(range(7)) - {shared}, 2) for reverse in (False, True))
            for index, (shared, x_names, reverse) in enumerate(configs):
                if limit is not None and index >= limit:
                    break
                fixed = {shared: 0, **dict(zip(sorted(x_names), (1, 2)))}
                leftover = sorted(set(range(7)) - fixed.keys())
                fixed.update(zip(leftover, (3, 4, 5, 6)))
                order = [fixed[i] for i in range(7)]
                trial, stopped = grow(design, law, order=order, reverse_knots=reverse)
                counts = parts_read(trial, design["s"], target)
                numberings.append({"order": order, "founders reversed": reverse, "guard at": stopped,
                                   "first round with an X-only pair": next((row["round"] for row in counts if row["X only"] >= 2), None),
                                   "first meeting": meeting_round(trial, design["s"])})
            out["all numberings up to the start's symmetries"] = numberings
        result.append(out)
    return result


def lists_replay(limit):
    law = Law("FLOOR1", "OFFSHOOT", "MET", "OLDEST", "parity")
    out = []
    for row in TAKE_LISTS[:limit]:
        design = DESIGNS[row["design"]]
        snapshots, stopped = grow(design, law, rounds=row["s"] + len(row["take_list"]), take_list=row["take_list"])
        found = {(case["round"], case["place of Y"]): case["made distinctions"] for case in parity_values(snapshots, row["s"])}
        expected = all(found.get((row["round"], int(place))) == [tuple(pair) for pair in pairs] for place, pairs in row["two"].items())
        out.append({"index": row["index"], "design": row["design"], "guard at": stopped,
                    "gives the listed distinctions": expected,
                    "every knot passes": all(not parity_failures(state) for state in snapshots)})
    return out


def every_choice_controls():
    design = DESIGNS["made-2"]
    out = []
    for knot_law, treatment in product(KNOT_LAWS, ("RETIRE", "WAIT")):
        law = Law("FLOOR1", treatment, "MET", "OLDEST", knot_law)
        initial, _ = grow(design, law, rounds=1)
        states = [(initial[-1], (None, None))]
        for round_number in range(2, 6):
            step = []
            for state, ends in states:
                prepared = prepare(state, law)
                options = [birth.candidates for birth in prepared[0] if birth.candidates]
                for takes in product(*options):
                    after = finish(state, law, prepared, takes)
                    live = usable(holders(after.knots), after.barred)
                    new_ends = tuple(end if end is not None else round_number if not any(after.descent[i] & flag for i in live) else None
                                     for end, flag in zip(ends, (1, 2)))
                    step.append((after, new_ends))
            states = step
        counts = Counter(tuple(f"ended at {end}" if end else "every member left waits" for end in ends)
                         for _, ends in states)
        out.append({"knot law": knot_law, "treatment": treatment, "histories": len(states),
                    "final states": [{"pair": pair, "count": count} for pair, count in counts.items()],
                    "exchange invariant": all(count == counts[pair[::-1]] for pair, count in counts.items())})
    return out


def argument_checks():
    parity_example = start({"stars": [[0, 1, 2], [0, 1, 3]]})
    labels = parity_columns(parity_example)
    out = {"at most two holders need not imply no parity tie": {
        "knots": [sorted(knot) for knot in parity_example.knots], "loose distinctions tied": labels[2] == labels[3],
        "frozen": labels.count(0), "failing knots": parity_failures(parity_example)}}
    law = Law("FLOOR1", "OFFSHOOT", "STEPS-1", "OLDEST", "parity")
    initial = {"stars": [[0, 1, 2]], "barred": [1, 2], "s": 0}
    snapshots, _ = grow(initial, law, rounds=2)
    out["two fresh distinctions from later offshoots when an initial knot has two barred places"] = [
        {"round": state.t, "parents and fresh counts": [(birth.parents, len(birth.fresh)) for birth in state.births]}
        for state in snapshots[1:]]
    ordered = {"stars": [[0, 1, 2], [0, 3, 4], [1, 5, 6], [2, 7, 8, 9]], "s": 0}
    snapshots, _ = grow(ordered, replace(law, taking="MET"), rounds=1)
    out["fixed renaming of old loose names need not commute with the allocation"] = {
        "start": ordered["stars"], "automorphism of prior structure": [3, 4],
        "joins and their loose inputs": [(birth.parents, birth.regular) for birth in snapshots[1].births if len(birth.parents) > 1],
    }
    design = DESIGNS["made-3"]
    snapshots, _ = grow(design, Law("FLOOR0", "RETIRE", "STEPS-1", "NEWEST", "parity"), rounds=3)
    before, after = map(parity_columns, snapshots[2:4])
    y_births = [i for i in range(len(snapshots[2].knots), len(snapshots[3].knots)) if snapshots[3].descent[i] == 2]
    out["allowing an extra constraint on old distinctions, under FLOOR0"] = {
        "round": 3, "second pattern has this many members at round 1": 3,
        "new Y-only knots": {i: sorted(snapshots[3].knots[i]) for i in y_births},
        "0 frozen before and after": [before[0] == 0, after[0] == 0],
        "1 tied to 2 before and after": [before[1] == before[2], after[1] == after[2]],
        "failing knots before and after": [parity_failures(state) for state in snapshots[2:4]],
    }
    return out


def main():
    cli = argparse.ArgumentParser()
    cli.add_argument("--limit", type=int, help="time a prefix of each repeated check")
    limit = cli.parse_args().limit
    basics, thirds = start_checks(limit)
    result = {"run prefix": limit, "checked starts": basics, "checked third-pattern starts": thirds,
              "stated-rule values": values_replay(), "stated-rule form": form_replay(limit),
              "take lists": lists_replay(limit), "every-choice controls": every_choice_controls(),
              "argument checks": argument_checks()}
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
