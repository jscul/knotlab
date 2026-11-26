"""Recount the named growth checks and match the frozen witnesses."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import lru_cache
import gzip
from itertools import combinations, permutations, product
import json
from math import factorial, gcd
from pathlib import Path

import networkx as nx


ROOT = Path(__file__).resolve().parents[3]
TICKET = "DESCENT-HELD-20261125-001A"
INPUT = ROOT / "research" / TICKET
DATA = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_order_in_own_places"
FORMS = ("base", "PU", "PB", "BB")
KNOT_LAWS = ("parity", "nae")
FORM_NAMES = {
    "base": "base", "PU": "NEXT3-PLACES (usable)",
    "PB": "NEXT3-PLACES (barred)", "BB": "NEXT3-BARRED",
}
CONDITIONS = ("a", "bprime", "c", "d")
KINDS = ("parent", "child", "start", "other")


def read(path):
    if path.suffix == ".gz":
        with gzip.open(path, "rt") as stream:
            return json.load(stream)
    return json.loads(path.read_text())


@dataclass(frozen=True)
class Law:
    ration: str
    treatment: str = "CANCEL-OFFSHOOT"
    release: str = "RELEASE"
    fillers: bool = False

    @classmethod
    def from_row(cls, row):
        return cls(row["ration"], row["treatment"], row["release"],
                   "FILLERS" in row.get("extras", []))

    def fresh(self, parents, demand):
        ordinary = max(demand, 3 - parents, 1)
        style, _, limit = self.ration.partition("-")
        if style == "CAP":
            return min(ordinary, int(limit))
        if style == "RATION":
            return max(int(limit), 3 - parents)
        if self.ration == "ONE-FEWER":
            return min(ordinary, max(3 - parents, 0, ordinary - 1))
        if self.ration == "FLOOR0":
            return max(3 - parents, 0)
        if self.ration == "FLOOR1":
            return max(3 - parents, 1)
        assert self.ration == "ORD", self.ration
        return ordinary


@dataclass
class Birth:
    knot: int
    round: int
    parents: tuple
    taken: tuple
    steps: int
    demand: int
    base_fresh: int
    added: int
    barred: int
    closing: bool
    unmet_addition: int
    parent_count_cardinality: int

    @property
    def parents_differ(self):
        return self.parent_count_cardinality > 1


@dataclass
class Round:
    number: int
    births: list = field(default_factory=list)
    retired: dict = field(default_factory=dict)
    short: set = field(default_factory=set)
    short_all_loose: set = field(default_factory=set)
    members_with_barred: int = 0
    waited: set = field(default_factory=set)
    end: str | None = None


@dataclass
class Growth:
    places: list
    n_start: int
    holders: dict
    depth: list
    barred: set
    barred_now: list
    next_distinction: int
    births: dict = field(default_factory=dict)
    retired: dict = field(default_factory=dict)
    rounds: list = field(default_factory=list)
    rosters: list = field(default_factory=list)

    @classmethod
    def from_stars(cls, stars):
        holders = defaultdict(list)
        for knot, places in enumerate(stars):
            for distinction in places:
                holders[distinction].append(knot)
        assert all(len(pair) in (1, 2) for pair in holders.values())
        return cls([tuple(row) for row in stars], len(stars), holders,
                   [0] * len(stars), set(), [0] * len(stars), max(holders) + 1)

    def member_places(self):
        return {
            knot: loose
            for knot, places in enumerate(self.places)
            if (loose := [
                d for d in places if len(self.holders[d]) == 1 and d not in self.barred
            ])
        }

    def count(self, knot, form):
        return self.barred_now[knot] if form == "BB" else len(self.places[knot])

    def birth_counts(self):
        return [len(round_.births) for round_ in self.rounds]

    def parents_by_round(self):
        return [tuple(birth.parents for birth in round_.births) for round_ in self.rounds]


def met_sets(holders, members, proposed=()):
    met = defaultdict(set)
    meetings_between_members = False
    for pair in holders.values():
        if len(pair) == 2:
            x, y = pair
            if x in members:
                met[y].add(x)
            if y in members:
                met[x].add(y)
            meetings_between_members |= x in members and y in members
    for child, parents in proposed:
        for parent in parents:
            met[parent].add(child)
            if parent in members:
                met[child].add(parent)
    return {frozenset(group) for group in met.values() if len(group) >= 2}, meetings_between_members


@lru_cache(maxsize=2048)
def groups_from_met(family):
    joinable = nx.Graph()
    pairs = set()
    for group in family:
        pairs.update(combinations(sorted(group), 2))
    joinable.add_edges_from(pairs)
    large = [
        tuple(sorted(group))
        for group in nx.find_cliques(joinable)
        if len(group) >= 3 and not any(met.issuperset(group) for met in family)
    ]
    for group in large:
        pairs.difference_update(combinations(group, 2))
    return tuple(sorted([*large, *pairs]))


def added_count(counts, initial, parents_swap):
    target = None
    if len(counts) == 1:
        target = next(iter(counts)) + 1
    if len(counts) == 2 and parents_swap:
        lower = next(c for c in counts if (c + 1) % 3 in counts)
        target = lower + 2
    return 0 if target is None else (target - initial) % 3


def one_round(growth, law, form, knot_law, number, parents_swap, closing_swap, all_loose):
    frame = Round(number)
    loose = growth.member_places()
    if not loose:
        frame.end = "stopped"
        return frame

    family, _ = met_sets(growth.holders, loose)
    groups = groups_from_met(frozenset(family))
    owing = Counter(knot for group in groups for knot in group)
    frame.short = {knot for knot, places in loose.items() if owing[knot] > len(places)}
    frame.short_all_loose = {
        knot for knot in loose if owing[knot] > len(loose[knot]) + growth.barred_now[knot]
    }
    frame.members_with_barred = sum(growth.barred_now[knot] > 0 for knot in loose)
    short = frame.short_all_loose if all_loose else frame.short
    if short and law.treatment == "STALL":
        frame.end = "stalled"
        return frame

    recipes = []
    cancelled_places = Counter()
    for group in groups:
        if short.intersection(group):
            cancelled_places.update(group)
        else:
            recipes.append((group, tuple(loose[knot].pop() for knot in group)))
    for knot in sorted(loose):
        available = loose[knot]
        keep = min(len(available), cancelled_places[knot]) if law.release == "HOLD" else 0
        if knot in short:
            keep = 0
            if law.treatment == "CANCEL-WAIT":
                frame.waited.add(knot)
                continue
            if law.treatment == "CANCEL-RETIRE":
                frame.retired[knot] = len(available)
                growth.retired[knot] = (number, len(available))
                growth.barred.update(available)
                growth.barred_now[knot] += len(available)
                available.clear()
                continue
        while len(available) > keep:
            recipes.append(((knot,), (available.pop(),)))

    if not recipes:
        if not frame.retired:
            frame.end = "jammed"
        return frame

    first_knot = len(growth.places)
    recipes = [(first_knot + i, parents, taken) for i, (parents, taken) in enumerate(recipes)]
    remaining = {knot for knot, places in loose.items() if places}
    post_family, _ = met_sets(growth.holders, remaining,
                              ((child, parents) for child, parents, _ in recipes))
    next_groups = groups_from_met(frozenset(post_family))
    demands = Counter(knot for group in next_groups for knot in group)
    closing = (knot_law == "parity" and len(recipes) == 1
               and not remaining and not growth.barred)
    for knot, parents, taken in recipes:
        demand = demands[knot]
        parent_count = len(parents)
        finite_counts = {growth.count(parent, form) % 3 for parent in parents}
        step = 1 + max(growth.depth[parent] for parent in parents)
        base_fresh = law.fresh(parent_count, demand)
        if closing and not closing_swap:
            base_fresh = 0
        base_barred = max(0, base_fresh - demand) if law.fillers else 0
        initial_count = base_barred if form == "BB" else parent_count + base_fresh
        proposed = added_count(finite_counts, initial_count, parents_swap) if form != "base" else 0
        added = 0 if closing and not closing_swap else proposed
        fresh = base_fresh + added
        if form == "PU":
            barred = max(0, fresh - demand) if law.fillers else 0
        else:
            barred = base_barred + added
        fresh_distinctions = tuple(range(growth.next_distinction, growth.next_distinction + fresh))
        growth.next_distinction += fresh
        for distinction in taken:
            growth.holders[distinction].append(knot)
        for distinction in fresh_distinctions:
            growth.holders[distinction].append(knot)
        if barred:
            growth.barred.update(fresh_distinctions[-barred:])
        growth.places.append(taken + fresh_distinctions)
        growth.depth.append(step)
        growth.barred_now.append(barred)
        birth = Birth(knot, number, parents, taken, step, demand, base_fresh, added, barred,
                      closing, proposed if closing else 0, len(finite_counts))
        growth.births[knot] = birth
        frame.births.append(birth)
    return frame


def roster(growth):
    members = growth.member_places()
    family, members_meet = met_sets(growth.holders, members)
    maximal = {group for group in family if not any(group < other for other in family)}
    counts = {knot: (len(places), growth.barred_now[knot]) for knot, places in members.items()}
    return counts, maximal, members_meet


def grow(stars, law, form="base", knot_law="parity", rounds=8, limit=3000,
         parents_swap=False, closing_swap=False, stop_on_empty=False,
         all_loose=False, save_rosters=False):
    growth = Growth.from_stars(stars)
    if save_rosters:
        growth.rosters.append(roster(growth))
    for index in range(1, rounds + 1):
        frame = one_round(growth, law, form, knot_law, index, parents_swap,
                          closing_swap, all_loose)
        growth.rounds.append(frame)
        if save_rosters:
            growth.rosters.append(roster(growth))
        if frame.end:
            break
        if stop_on_empty and not frame.births:
            frame.end = "jammed"
            break
        if len(growth.places) > limit:
            frame.end = "N"
            break
    if not growth.rounds[-1].end:
        growth.rounds[-1].end = "R"
    return growth


def shared_places(growth):
    for distinction, holders in growth.holders.items():
        if len(holders) != 2:
            continue
        older, younger = holders
        if younger in growth.births:
            round_ = growth.births[younger].round
            yield younger, older, distinction, "parent", round_
            yield older, younger, distinction, "child", round_
        else:
            yield older, younger, distinction, "start", 0
            yield younger, older, distinction, "start", 0


def observed(growth, form, round_, places):
    counts = {x: growth.count(x, form) for x in range(len(growth.places))}
    retired = {x: n for x, (at, n) in growth.retired.items() if at <= round_}
    if form == "BB":
        for x, (at, n) in growth.retired.items():
            if at > round_:
                counts[x] -= n
    tally = {kind: [0, 0] for kind in KINDS}
    actual_failures = set()
    predicted_failures = set()
    retire_kinds = Counter()
    for x, y, distinction, kind, formed in places:
        if formed > round_:
            continue
        delta = (retired.get(y, 0) - retired.get(x, 0)) % 3
        wrong = ((counts[x] - counts[y]) % 3 == 1) != (kind == "parent")
        expected = delta in {"parent": (1, 2), "child": (1,), "start": (2,)}[kind]
        key = (x, distinction)
        if wrong:
            actual_failures.add(key)
        if expected:
            predicted_failures.add(key)
        tally[kind][wrong] += 1
        if x in retired or y in retired:
            retire_kinds[f"{kind}:delta={delta}"] += 1
            if x in retired and y in retired:
                retire_kinds[f"both:{kind}:delta={delta}"] += 1
    return tally, actual_failures, predicted_failures, retire_kinds


def inspect(growth, form, retiring):
    births = list(growth.births.values())
    disagreeing = [
        birth for birth in births if len({growth.depth[x] % 3 for x in birth.parents}) > 1
    ]
    first_disagreement = disagreeing[0].round if disagreeing else None
    first_births = [b for b in disagreeing if b.round == first_disagreement]
    first_steps = [b for b in births if len({growth.depth[x] for x in b.parents}) > 1]
    contacts = list(shared_places(growth))
    a = form == "BB" or not any(
        (growth.count(x, form) - growth.count(y, form)) % 3
        for x, y, _, kind, _ in contacts if kind == "start"
    )
    c = form != "BB" or all(n % 3 == 0 for _, n in growth.retired.values())
    closing = [birth for birth in births if birth.closing]
    d = not any(birth.unmet_addition for birth in closing)
    last = len(growth.rounds)
    tally, _, _, retirement_types = observed(growth, form, last, contacts)
    formula = []
    first_wrong = None
    formula_applies = form == "BB" and retiring and a and not disagreeing and d
    if form == "BB" and retiring:
        for round_ in range(last + 1):
            _, actual, predicted, _ = observed(growth, form, round_, contacts)
            if actual and first_wrong is None:
                first_wrong = round_
            if formula_applies:
                formula.append({
                    "round": round_, "wrong": len(actual), "predicted": len(predicted),
                    "equal": actual == predicted,
                })
    else:
        first_wrong = min((
            formed for x, y, _, kind, formed in contacts
            if ((growth.count(x, form) - growth.count(y, form)) % 3 == 1)
            != (kind == "parent")
        ), default=None)
    return {
        "rounds": sum(bool(frame.births or frame.retired) for frame in growth.rounds),
        "rounds_run": last, "knots": len(growth.places), "end": growth.rounds[-1].end,
        "births": growth.birth_counts(), "a": a, "bprime": not disagreeing,
        "b": not first_steps, "c": c, "d": d,
        "greatest": max((b.steps - growth.depth[x] for b in births for x in b.parents), default=0),
        "bprime_first_round": first_disagreement,
        "bprime_first_births": [b.knot for b in first_births],
        "bprime_first_birth_details": [
            {"knot": b.knot, "parents": list(b.parents), "parent_steps": [
                growth.depth[x] for x in b.parents
            ]} for b in first_births
        ],
        "first_disagreeing_births_all_counted": all(b.parents_differ for b in first_births),
        "first_round_with_a_wrong_place": first_wrong,
        "right_on_every_structure": first_wrong is None,
        "place_rule_last_by_kind": tally,
        "wrong_last": sum(pair[1] for pair in tally.values()),
        "counted_step3": sum(b.parents_differ for b in births) if form != "base" else 0,
        "bprime_births": len(disagreeing),
        "closing_births": len(closing),
        "closing_hyp_s": [b.unmet_addition for b in closing],
        "retired_knots": len(growth.retired),
        "retirement_kinds": dict(retirement_types),
        "s_positive": sum(b.added > 0 for b in births),
        "new_knots": len(births),
        "s_sum": sum(b.added for b in births),
        "P6_rows": formula,
    }


def law_from_name(text):
    return Law(*text.split("/"))


def parity_projection_rank(growth, knot, round_):
    """Dimension of the restrictions implied on the chosen knot's places."""
    places = set(growth.places[knot])
    outside = nx.Graph()
    outside.add_nodes_from(
        k for k in range(len(growth.places))
        if k < growth.n_start or growth.births[k].round <= round_
    )
    forced_zero = set()
    for d, holders in growth.holders.items():
        if d in places:
            continue
        present = [holder for holder in holders if holder in outside]
        if len(present) == 2:
            outside.add_edge(*present)
        if len(present) == 1:
            forced_zero.update(present)
    pivots = {}
    for component in nx.connected_components(outside):
        if component & forced_zero:
            continue
        row = sum((sum(h in component for h in growth.holders[d]) % 2) << bit
                  for bit, d in enumerate(sorted(places)))
        while row:
            high = row.bit_length() - 1
            if high not in pivots:
                pivots[high] = row
                break
            row ^= pivots[high]
    return len(pivots)


def hand_comparison(cases):
    out = {}
    for key, case in cases.items():
        if key == "H1_two_knot":
            forms = {form: case["forms"][FORM_NAMES[form]] for form in FORMS}
            law = law_from_name(case["base"])
        elif key.startswith(("W1_", "W2_", "W2b_")):
            forms = {"base": case["rounds"]}
            law = law_from_name(case["law"])
        else:
            continue
        for form, snapshots in forms.items():
            growth = grow(case["stars"], law, form, rounds=len(snapshots))
            actual = []
            disagreement = []
            for frame in growth.rounds:
                birth_rows = [{
                    "knot": b.knot, "parents": list(b.parents),
                    "parents_parent_steps": [growth.depth[x] for x in b.parents],
                    "parent_steps": b.steps, "places": len(growth.places[b.knot]),
                    "p": len(b.parents), "F": b.base_fresh,
                    "s": b.added, "barred_at_birth": b.barred,
                } for b in frame.births]
                actual.append({"round": frame.number, "new_knots": birth_rows,
                               "short_members_that_waited": sorted(frame.waited)})
                disagreement.extend({
                    "round": frame.number, "knot": b["knot"], "parents": b["parents"],
                    "parent_steps_of_each_parent": b["parents_parent_steps"],
                } for b in birth_rows if len(set(b["parents_parent_steps"])) > 1)
            out[f"{key}|{form}"] = {
                "equal": actual == snapshots, "births": growth.birth_counts(),
                "births_with_unequal_parents": disagreement,
            }
    return out


def close_hand(stars):
    results = []
    for ration, form, swapped in product(("FLOOR0", "FLOOR1", "ORD"), FORMS[1:], (False, True)):
        growth = grow(stars, Law(ration), form, rounds=1, closing_swap=swapped)
        birth, = growth.rounds[0].births
        results.append({
            "ration": ration, "form": form, "swapped": swapped,
            "parents": birth.parents, "F": birth.base_fresh, "s": birth.added,
            "barred": birth.barred,
            "place_rule_after_round_1": observed(growth, form, 1, shared_places(growth))[0],
            "parity_ranks_after_round_1": [
                parity_projection_rank(growth, x, 1) for x in range(len(growth.places))
            ],
        })
    return results


def two_retirements():
    """One shared distinction joins two start knots that retire by different amounts."""
    stars = [[0, 1, 2, 3], [0, 4, 5], [1, 4, 6, 7], [2, 8, 9], [3, 10, 11]]
    growth = grow(stars, Law("FLOOR1", "CANCEL-RETIRE"), "BB")
    actual = inspect(growth, "BB", True)
    _, actual_fails, predicted_fails, _ = observed(
        growth, "BB", 1, list(shared_places(growth))
    )
    return {
        "start_places": stars, "retired_amount_by_knot": growth.rounds[0].retired,
        "new_knots": actual["new_knots"],
        "all_start_knots_pass_parity": all(
            parity_projection_rank(growth, k, 0) == 1 for k in range(len(stars))
        ),
        "wrong_places_after_round_1": sorted(actual_fails),
        "predicted_wrong_places_after_round_1": sorted(predicted_fails),
        "both_retired_one_shared_distinction": {
            name: count for name, count in actual["retirement_kinds"].items()
            if name.startswith("both:")
        },
    }


def raw_planted(rows):
    tested = [row for row in rows if row.get("x") is not None]
    return {
        "eligible": len(rows), "exercised": len(tested), "skipped": len(rows) - len(tested),
        "literal_matches": sum(r["equal"] for r in tested),
        "arithmetic_matches": sum(r["changed_equals_formula"] for r in tested),
        "exercised_where_conditions_hold": sum(all(r["conditions"].values()) for r in tested),
        "literal_matches_where_conditions_hold": sum(
            r["equal"] and all(r["conditions"].values()) for r in tested
        ),
        "literal_failures": [
            (r["start"], r["law"], r["form"]) for r in tested if not r["equal"]
        ],
    }


def planted(growth, form, info):
    if len(growth.rounds) < 2 or not growth.rounds[1].births:
        return None
    x = growth.rounds[1].births[0].knot
    actual = set()
    literal = set()
    formula = set()
    for holder, other, distinction, kind, _ in shared_places(growth):
        if x not in (holder, other):
            continue
        change = int(holder == x) - int(other == x)
        original = growth.count(holder, form) - growth.count(other, form)
        after = original + change
        if (original % 3 == 1) != (after % 3 == 1):
            actual.add((holder, distinction))
        if (holder == x and kind == "parent") or other == x:
            literal.add((holder, distinction))
        if original % 3 in (1, (1 - change) % 3):
            formula.add((holder, distinction))
    return {
        "x": x, "changed": len(actual), "predicted": len(literal),
        "equal": actual == literal, "changed_equals_formula": actual == formula,
        "conditions": {cond: info[cond] for cond in CONDITIONS},
        "extra_changed": sorted(actual - literal), "missing": sorted(literal - actual),
    }


def compare_keys(key, actual, expected, fields, issues):
    for name in fields:
        if actual[name] != expected[name]:
            issues.append([key, name, actual[name], expected[name]])


def numberings_roster_count(starts):
    counts = {}
    for name, start in starts.items():
        distinctions = {d for row in start for d in row}
        if len(distinctions) <= 6:
            counts[name] = factorial(len(start)) * factorial(len(distinctions))
    return counts


def meeting_signature(growth):
    meetings = Counter()
    loose = Counter()
    for d, holder in growth.holders.items():
        if len(holder) == 2:
            meetings[tuple(sorted(holder))] += 1
        else:
            loose[holder[0], d in growth.barred] += 1
    return meetings, loose


def exercise_numberings(starts, laws, limit_per_start):
    """Check explicit bijections between independently grown numbered structures."""
    totals = {}
    for name, start in starts.items():
        distinctions = sorted({d for row in start for d in row})
        if len(distinctions) > 6:
            continue
        identity = tuple(range(len(start)))
        source = {}
        tried = 0
        failures = []
        for law, form in product(laws, FORMS[1:]):
            original = grow(start, laws[law], form, rounds=4)
            source[law, form] = original, meeting_signature(original)
        for knots in permutations(identity):
            for labels in permutations(distinctions):
                if limit_per_start is not None and tried >= limit_per_start:
                    break
                tried += 1
                recode = dict(zip(distinctions, labels))
                renamed = [sorted(recode[d] for d in start[k]) for k in knots]
                for law, form in source:
                    original, (meetings_before, loose_before) = source[law, form]
                    current = grow(renamed, laws[law], form, rounds=4)
                    mapping = dict(enumerate(knots))
                    compatible = original.birth_counts() == current.birth_counts()
                    if compatible:
                        for old_frame, new_frame in zip(original.rounds, current.rounds):
                            roster_by_parents = defaultdict(list)
                            for b in reversed(old_frame.births):
                                roster_by_parents[b.parents].append(b.knot)
                            for b in new_frame.births:
                                matched = tuple(sorted(mapping[p] for p in b.parents))
                                if not roster_by_parents[matched]:
                                    compatible = False
                                    break
                                mapping[b.knot] = roster_by_parents[matched].pop()
                            if not compatible:
                                break
                    if compatible:
                        meetings_after, loose_after = meeting_signature(current)
                        recoded_meetings = {
                            tuple(sorted(mapping[k] for k in pair)): n
                            for pair, n in meetings_after.items()
                        }
                        recoded_loose = {
                            (mapping[k], barred): n for (k, barred), n in loose_after.items()
                        }
                        compatible = (meetings_before == recoded_meetings
                                      and loose_before == recoded_loose)
                    if not compatible:
                        failures.append((knots, labels, law, form))
        totals[name] = {"numberings": tried, "runs": tried * len(source), "failures": failures}
    return totals


def lone_cases(laws_file, raw):
    out = []
    for ration, starts in laws_file["lone_knot_rations"].items():
        for a, form in product(starts, FORMS):
            growth = grow([range(a)], Law(ration), form, rounds=1)
            b = growth.births[1]
            offshoot_places = len(growth.places[b.knot])
            exchangers = factorial(a - 1) ** 2 if a == offshoot_places and not b.barred else 0
            fixed = factorial(a - 1) * factorial(offshoot_places - 1 - b.barred) * factorial(b.barred)
            out.append({
                "ration": ration, "a": a, "form": FORM_NAMES[form],
                "F_1_a-1": Law(ration).fresh(1, a - 1),
                "offshoot_D": b.demand, "offshoot_places": offshoot_places,
                "offshoot_barred": b.barred, "s": b.added, "start_knot_places": a,
                "renamings_of_the_structure": fixed + exchangers,
                "renamings_exchanging_the_two_knots": exchangers,
                "checked_place_by_place": exchangers, "exists": bool(exchangers),
            })
    return {
        "replayed": len(out), "equal_to_raw": out == raw["rows"],
        "base_with_exchange": sum(r["exists"] and r["form"] == "base" for r in out),
        "count_forms_with_exchange": sum(r["exists"] and r["form"] != "base" for r in out),
        "rows": out,
    }


def roster_parts(snapshot):
    counts, family, _ = snapshot
    graph = nx.Graph()
    graph.add_nodes_from(counts)
    for member_set in family:
        first, *others = member_set
        graph.add_edges_from((first, n) for n in others)
    return [frozenset(part) for part in nx.connected_components(graph)]


def incidence(snapshot, part, depths=None):
    counts, family, _ = snapshot
    graph = nx.Graph()
    for knot in part:
        label = ("knot", *counts[knot])
        if depths is not None:
            label += (depths[knot],)
        graph.add_node(knot, label=label)
    for i, met in enumerate(group for group in family if group <= part):
        group_id = ("meeting", i)
        graph.add_node(group_id, label=("meeting", len(met)))
        graph.add_edges_from((group_id, knot) for knot in met)
    return graph


def first_return(growth, numbering_report=None, max_part=None, source=None):
    snapshots = growth.rosters
    ancestors = {x: {x} for x in range(growth.n_start)}
    for x, birth in growth.births.items():
        ancestors[x] = {x}.union(*(ancestors[p] for p in birth.parents))
    parts = [roster_parts(snap) for snap in snapshots]
    for s, snap in enumerate(snapshots):
        if snap[2]:
            continue
        if source is not None and s != source[0]:
            continue
        for t in range(s + 1, len(snapshots)):
            for before, after in product(parts[s], parts[t]):
                if source is not None and before != source[1]:
                    continue
                if max_part is not None and len(before) > max_part:
                    continue
                if len(before) != len(after) or any(not before & ancestors[y] for y in after):
                    continue
                one = incidence(snap, before)
                two = incidence(snapshots[t], after)
                matcher = nx.algorithms.isomorphism.GraphMatcher(
                    one, two, node_match=lambda x, y: x["label"] == y["label"]
                )
                rename = next(matcher.isomorphisms_iter(), None)
                if rename is None:
                    continue
                differences = {growth.depth[rename[x]] - growth.depth[x] for x in before}
                min_before = min(growth.depth[x] for x in before)
                min_after = min(growth.depth[y] for y in after)
                q = min_after - min_before
                one = incidence(snap, before, {x: growth.depth[x] + q for x in before})
                two = incidence(snapshots[t], after, dict(enumerate(growth.depth)))
                depth_preserving = nx.is_isomorphic(
                    one, two, node_match=lambda x, y: x["label"] == y["label"]
                )
                archive_rename_valid = None
                if numbering_report:
                    archive_rename = dict(numbering_report)
                    counts0, met0, _ = snap
                    counts1, met1, _ = snapshots[t]
                    archive_rename_valid = (
                        set(archive_rename) == before and set(archive_rename.values()) == after
                        and all(counts0[x] == counts1[y] for x, y in archive_rename.items())
                        and {frozenset(archive_rename[x] for x in group)
                             for group in met0 if group <= before}
                        == {group for group in met1 if group <= after}
                    )
                return {
                    "s": s, "t": t, "period": t - s, "part_members": len(before),
                    "members_at_start": sorted(before), "members_at_return": sorted(after),
                    "counts_at_start": sorted(snap[0][x] for x in before),
                    "counts_at_return": sorted(snapshots[t][0][y] for y in after),
                    "parent_steps_at_start": sorted(growth.depth[x] for x in before),
                    "parent_steps_at_return": sorted(growth.depth[y] for y in after),
                    "q": next(iter(differences)) if len(differences) == 1 else None,
                    "some_renaming_with_common_q": q if depth_preserving else None,
                    "members_agree_in_parent_steps_counted_in_threes": (
                        len({growth.depth[x] % 3 for x in before}) == 1
                    ),
                    "archive_renaming_valid": archive_rename_valid,
                }
    return None


def ring_returns(raw, starts, laws):
    rows = []
    for row in raw["rows"]:
        form = next(f for f, label in FORM_NAMES.items() if label == row["form"])
        growth = grow(starts[row["start"]], laws[row["law"]], form,
                      rounds=14, limit=float("inf"), save_rosters=True)
        actual = first_return(growth, row["first_return"]["renaming_found"])
        rows.append({
            "start": row["start"], "law": row["law"], "form": row["form"],
            "birth_counts_agree": growth.birth_counts() == row["births"],
            "knot_counts_agree": len(growth.places) == row["knots"],
            "returns": actual,
            "return_summary_agrees": actual and all(
                row["first_return"][field] == actual[field]
                for field in ("s", "t", "period", "part_members", "q",
                              "some_renaming_with_common_q",
                              "members_agree_in_parent_steps_counted_in_threes")
            ),
        })
    by_key = {(r["start"], r["law"], r["form"]): r for r in rows}
    formula = []
    for start, law, form in by_key:
        if form == "base":
            continue
        base = by_key[start, law, "base"]["returns"]
        actual = by_key[start, law, form]["returns"]
        predicted = base["period"] * 3 // gcd(3, base["q"])
        formula.append({"start": start, "law": law, "form": form, "predicted": predicted,
                        "observed": actual["period"], "agrees": predicted == actual["period"]})
    return {"rows": rows, "formula": formula}


def condition_recount(rows):
    totals = {key: Counter() for key in ("P3", "P4", "P5", "P6")}
    unique_starts = defaultdict(set)
    misses = []
    for start, law, form, row in rows:
        a, bprime, c, d = (row[cond] for cond in CONDITIONS)
        check = {
            "P3": a and bprime and c and d,
            "P4": a and not bprime and c and d,
            "P5": form in ("PU", "PB") and not a,
            "P6": form == "BB" and law in ("F1R", "H-F1R") and a and bprime and d,
        }
        for prediction, applies in check.items():
            if applies != (row[prediction] is not None):
                misses.append((start, law, form, prediction, "applies"))
            if not applies:
                continue
            counter = totals[prediction]
            unique_starts[prediction].add(start)
            counter["eligible"] += 1
            counter["no_birth"] += not row["new_knots"]
            counter["no_shared_place"] += not any(
                sum(count) for count in row["place_rule_last_by_kind"].values()
            )
            counter["with_retirement"] += bool(row["retired_knots"])
            counter["retirement_changes_count_in_threes"] += not c
            counter["with_wrong_shared_place"] += not row["right_on_every_structure"]
            counter["recorded_failures"] += not row[prediction]
            counter[f"form_{form}"] += 1
            if prediction == "P4":
                counter["archived_wrong_round_matches_first_disagreement_round"] += (
                    row["first_round_with_a_wrong_place"] == row["bprime_first_round"]
                )
            if prediction == "P5":
                counter["wrong_at_a_place_between_start_knots"] += (
                    row["place_rule_last_by_kind"]["start"][1] > 0
                )
    for key, counts in totals.items():
        counts["distinct_starts"] = len(unique_starts[key])
    return {"counts": totals, "mismatched_conditions": misses}


def exact_h3(summary, growths):
    reference = growths["base"]
    close = next((b.round for b in reference.births.values() if b.closing), None)
    cut = close or len(reference.rounds)
    compared = {}
    for form in ("PB", "BB"):
        actual = growths[form]
        compared[form] = {
            "through_round": cut,
            "agree": actual.parents_by_round()[:cut] == reference.parents_by_round()[:cut],
            "base_closes_at": close,
            "prefix_has_birth": bool(reference.births),
            "has_mark_before_base_closes": bool(close and any(
                b.round < close and b.added > 0 for b in actual.births.values()
            )),
            "goes_on_after_base_closes": bool(close and any(
                b.round > close for b in actual.births.values()
            )),
            "end": actual.rounds[-1].end,
        }
        assert summary[form]["base_closes_at"] == close
    return compared


def base_row(growth):
    status = inspect(growth, "base", False)
    return {
        "counted": not status["b"], "bprime_fails": not status["bprime"],
        "greatest": status["greatest"], "rounds": status["rounds"],
        "knots": status["knots"], "end": status["end"],
        "births": status["births"], "closing_births": status["closing_births"],
        "rounds_run": status["rounds_run"],
    }


NAMED_FIELDS = (
    *CONDITIONS, "b", "greatest", "bprime_first_round", "bprime_first_births",
    "place_rule_last_by_kind", "wrong_last", "right_on_every_structure",
    "first_round_with_a_wrong_place", "counted_step3", "bprime_births",
    "closing_births", "closing_hyp_s", "retired_knots", "s_positive",
    "new_knots", "s_sum", "P6_rows", "rounds", "rounds_run", "knots", "end", "births",
)


def named_runs(starts, laws, raw4, raw8, raw0, case_limit):
    raw_close_and_parents = {
        (r["start"], r["law"], r["form"], r["knot_law"]): r for r in raw8["named"]
    }
    raw_stopping = {(r["start"], r["law"], r["knot_law"]): r for r in raw8["stopping"]}
    raw_plant = {(r["start"], r["law"], r["form"]): r for r in raw0["c_planted_error"]["runs"]}
    raw_short = {(r["start"], r["law"], r["form"]): r for r in raw0["f_shortness"]["runs"]}
    assert len(raw_close_and_parents) == 924
    assert len(raw_stopping) == 392
    assert len(raw_plant) == 308
    assert len(raw_short) == 462
    issues = []
    h3 = {}
    usable = Counter()
    retirement = Counter()
    comparisons = Counter()
    exercised_at_least_two_counts = Counter()
    closing_verdict_changes = []
    first_after_base_keys = {"PB": 0, "BB": 0}
    compared_stopping = set()
    for row in raw4["runs"][:case_limit]:
        start, law_name, knot_law = (row[k] for k in ("start", "law", "knot_law"))
        stars = starts[start]
        law = laws[law_name]
        retiring = law.treatment == "CANCEL-RETIRE"
        key = (start, law_name, knot_law)
        growths = {form: grow(stars, law, form, knot_law) for form in FORMS}
        expected = row["forms"]
        base = growths["base"]
        compare_keys(key, base_row(base), expected["base"], base_row(base).keys(), issues)
        comparisons["part4_base_growths"] += 1
        h3["|".join(key)] = exact_h3(expected, growths)
        usable["birth_counts_equal"] += base.birth_counts() == growths["PU"].birth_counts()
        usable["parent_lists_equal"] += base.parents_by_round() == growths["PU"].parents_by_round()
        stop = grow(stars, law, knot_law=knot_law, stop_on_empty=True)
        compare_keys(key, base_row(stop), raw_stopping[key]["first_round_with_no_birth"],
                     raw_stopping[key]["first_round_with_no_birth"].keys(), issues)
        comparisons["part8_named_stopping_growths"] += 1
        compared_stopping.add(key)
        for form in FORMS[1:]:
            run = growths[form]
            info = inspect(run, form, retiring)
            compare_keys((*key, form), info, expected[form], NAMED_FIELDS, issues)
            comparisons["part4_count_form_growths"] += 1
            if expected[form]["P4"] is True and not info["first_disagreeing_births_all_counted"]:
                issues.append([(*key, form), "P4_first_disagreeing_birth_missing"])
            if expected[form]["P4"] is True:
                comparisons["P4_first_wrong_at_first_disagreeing_round"] += (
                    info["bprime_first_round"] == info["first_round_with_a_wrong_place"]
                )
            if (expected[form]["P6"] is True) and not info["P6_rows"]:
                issues.append([(*key, form), "P6_missing"])
            if info["P6_rows"]:
                retirement["runs"] += 1
                retirement["round_views"] += len(info["P6_rows"])
                retirement["exact_set_matches"] += sum(r["equal"] for r in info["P6_rows"])
                retirement.update(info["retirement_kinds"])
            swapped_branch = grow(stars, law, form, knot_law, parents_swap=True)
            swap_expected = raw_close_and_parents[start, law_name, form, knot_law]
            swap_info = inspect(swapped_branch, form, retiring)
            compare_keys((*key, form), swap_info, swap_expected["parents_differ_swap"],
                         [f for f in swap_expected["parents_differ_swap"] if f in swap_info], issues)
            comparisons["part8_named_parents_differ_growths"] += 1
            exercised_at_least_two_counts["registered_some_two"] += any(
                b.parent_count_cardinality == 2 for b in run.births.values()
            )
            exercised_at_least_two_counts["registered_some_three"] += any(
                b.parent_count_cardinality == 3 for b in run.births.values()
            )
            exercised_at_least_two_counts["actually_changed_births"] += (
                run.parents_by_round() != swapped_branch.parents_by_round()
            )
            swapped_close = grow(stars, law, form, knot_law, closing_swap=True)
            close_expected = swap_expected["closing_swap"]
            ended = inspect(swapped_close, form, retiring)
            compare_keys((*key, form), ended, close_expected,
                         ("knots", "end", "closing_births"), issues)
            if info["right_on_every_structure"] != ended["right_on_every_structure"]:
                closing_verdict_changes.append({
                    "start": start, "law": law_name, "knot_law": knot_law, "form": form,
                    "registered_right": info["right_on_every_structure"],
                    "swap_right": ended["right_on_every_structure"],
                    "first_wrong_round_registered": info["first_round_with_a_wrong_place"],
                    "first_wrong_round_swapped": ended["first_round_with_a_wrong_place"],
                    "registered_births": info["births"], "swap_births": ended["births"],
                })
            close_events = [b for b in swapped_close.births.values() if b.closing]
            checked = []
            for b in close_events:
                rank = parity_projection_rank(swapped_close, b.knot, b.round)
                checked.append({
                    "knot": b.knot, "round": b.round, "F": b.base_fresh,
                    "s": b.added, "fails_parity_after_its_round": rank != 1,
                })
                comparisons["part8_parity_closing_knots_tested"] += 1
                comparisons["part8_parity_closing_knots_failed"] += rank != 1
            if checked != close_expected.get("closing_knots", []):
                issues.append([(*key, form), "closing swap births", checked,
                               close_expected.get("closing_knots", [])])
            comparisons["part8_named_closing_growths"] += 1
            if knot_law == "parity":
                short_expected = raw_short[start, law_name, form]
                alt_changes = False
                try:
                    alt = grow(stars, law, form, all_loose=True)
                    alt_changes = alt.parents_by_round() != run.parents_by_round()
                except IndexError:
                    alt_changes = True
                short_info = {
                    "rounds": len(run.rounds),
                    "member_rounds_holding_barred_places": sum(
                        r.members_with_barred for r in run.rounds
                    ),
                    "rounds_where_all_loose_reading_gives_another_short_set": sum(
                        r.short != r.short_all_loose for r in run.rounds
                    ),
                    "all_loose_engine_gives_other_births": alt_changes,
                }
                compare_keys((*key, form), short_info, short_expected, short_info.keys(), issues)
                comparisons["part0_shortness_growths"] += 1
                if form in ("PB", "BB"):
                    actual_plant = planted(run, form, info)
                    expected_plant = raw_plant[start, law_name, form]
                    if actual_plant is None:
                        if not expected_plant.get("skipped"):
                            issues.append([(*key, form), "planted error should skip"])
                    else:
                        compare_keys((*key, form), actual_plant, expected_plant,
                                     ("x", "changed", "predicted", "equal",
                                      "changed_equals_formula", "conditions"), issues)
                    comparisons["part0_planted_error_candidates"] += 1

    for key, expected in raw_stopping.items():
        if case_limit is not None or key in compared_stopping:
            continue
        start, law_name, knot_law = key
        changed = grow(starts[start], laws[law_name], knot_law=knot_law, stop_on_empty=True)
        recorded = grow(starts[start], laws[law_name], knot_law=knot_law)
        for outcome, actual in (("registered", recorded), ("first_round_with_no_birth", changed)):
            compare_keys(key, base_row(actual), expected[outcome], expected[outcome].keys(), issues)
        comparisons["part8_named_stopping_growths"] += 1
    h3_cases = {"compared": 0, "failures": [], "vacant_prefixes": 0, "base_closes": 0,
                "later_birth": 0, "prior_annotation": 0, "closes_with_no_later_birth": []}
    for key, records in h3.items():
        for form, check in records.items():
            h3_cases["compared"] += 1
            specific = (key, form, check)
            if not check["agree"]:
                h3_cases["failures"].append(specific)
            h3_cases["vacant_prefixes"] += not check["prefix_has_birth"]
            h3_cases["base_closes"] += check["base_closes_at"] is not None
            h3_cases["prior_annotation"] += check["has_mark_before_base_closes"]
            h3_cases["later_birth"] += check["goes_on_after_base_closes"]
            if check["base_closes_at"] and not check["goes_on_after_base_closes"]:
                h3_cases["closes_with_no_later_birth"].append(specific)
            if check["goes_on_after_base_closes"]:
                first_after_base_keys[form] += 1
    h3_cases["later_birth_by_form"] = first_after_base_keys
    return {
        "comparisons": comparisons, "raw_disagreements": issues, "H3": h3_cases,
        "usable_form": usable, "retirement_formula": retirement,
        "parents_differ_swap": exercised_at_least_two_counts,
        "closing_swap_whole_run_verdict_changes": closing_verdict_changes,
    }


def raw_swap_counts(raw, census, bases, case_limit):
    out = {}
    census_lookup = {r["idx"]: r for r in census if r["kept"]}
    kept_sets = []
    data = raw["census_parents_differ_swap"]
    armw_keys = {f"{law}|{form}" for law, form in product(bases[:7], FORMS[1:])}
    for block in ("rows", "finished_beyond_prefix"):
        counts = Counter()
        seen = set()
        for row in data[block][:case_limit]:
            idx = row["idx"]
            assert idx not in seen and set(row["runs"]) == armw_keys
            assert (idx < data["prefix_starts"]) == (block == "rows")
            seen.add(idx)
            registered = census_lookup[idx]["armw"]
            for key, swapped in row["runs"].items():
                old = registered[key]
                counts["cases"] += 1
                counts["old_parent_counts_differ_at_some_birth"] += old["counted_step3"] > 0
                for metric in ("place_rule_last_by_kind", "right_on_every_structure", "knots", "end"):
                    counts[metric + "_differs"] += old[metric] != swapped[metric]
        counts["starts"] = len(seen)
        kept_sets.append(seen)
        out[block] = counts
    seen = kept_sets[0] | kept_sets[1]
    assert not kept_sets[0] & kept_sets[1]
    if case_limit is None:
        assert set(census_lookup) - seen == set(data["not_run"])
    out["unfinished_census_indices"] = data["not_run"]
    named = Counter()
    wrong_by_kind = {kind: [0, 0] for kind in KINDS}
    for row in raw["named"][:case_limit]:
        named["parent_rule_cases"] += 1
        old, new = row["registered"], row["parents_differ_swap"]
        named["old_parent_counts_differ_at_some_birth"] += old["counted_step3"] > 0
        for key in ("place_rule_last_by_kind", "right_on_every_structure", "births", "end"):
            named[key + "_differs"] += old[key] != new[key]
        for kind in KINDS:
            wrong_by_kind[kind][0] += old["place_rule_last_by_kind"][kind][1]
            wrong_by_kind[kind][1] += new["place_rule_last_by_kind"][kind][1]
        closing = row["closing_swap"]
        named["parity_cases"] += row["knot_law"] == "parity"
        named["closing_swap_changes"] += bool(closing["closing_births"])
        named["closing_swap_later_birth"] += bool(closing.get("grows_after_closing"))
        named["closing_swap_knots"] += len(closing.get("closing_knots", []))
        named["closing_swap_failed_knots"] += sum(
            k["fails_parity_after_its_round"] for k in closing.get("closing_knots", [])
        )
    stopping = Counter()
    for row in raw["stopping"][:case_limit]:
        stopping["cases"] += 1
        for key, metric in row["registered"].items():
            stopping[f"{key}_differs"] += metric != row["first_round_with_no_birth"][key]
    out["named"] = dict(named)
    out["named_final_wrong_places_by_kind"] = wrong_by_kind
    out["named_stopping"] = dict(stopping)
    return out


def gate_stars(name, starts):
    if name in starts:
        return starts[name]
    assert name.startswith("D2(") and name.endswith(",3)")
    count = int(name[3:-3])
    members = [
        sorted([(4 * i + offset) % (4 * count) for offset in (-2, -1, 0, 1)])
        + list(range(4 * count + 3 * i, 4 * count + 3 * i + 3))
        for i in range(count)
    ]
    return members + [list(range(4 * i, 4 * i + 4)) for i in range(count)]


def gate_comparison(raw0, starts, laws):
    from_local_round = next((ROOT / "artifacts/LOCAL-ROUND-20261123-001A").glob("*/gate.json"))
    frozen_pairs = read(from_local_round)["pairs"]
    covered_pairs = raw0["a_gate"]["pairs"]
    assert {
        (r["start"], *r["law"], "RELEASE") for r in frozen_pairs
    } == {(r["start"], *r["law"]) for r in covered_pairs}
    out = {}
    for kind, rows in (
        ("frozen", covered_pairs),
        ("extra_hold", raw0["a_gate"]["extra_HOLD_against_own_round"]["pairs"]),
    ):
        issues = []
        for row in rows:
            name, law = row["start"], row["law"]
            growth = grow(gate_stars(name, starts), Law(*law))
            births = growth.birth_counts()
            if births != [r["births"] for r in row["rows"]]:
                issues.append((name, law, births, [r["births"] for r in row["rows"]]))
        out[kind] = {"pairs": len(rows), "rounds": sum(len(r["rows"]) for r in rows),
                     "differences": issues}
    issues = []
    for row in raw0["d_holding_runs"]["runs"]:
        start, law = row["start"], row["law"]
        growth = grow(starts[start], laws[law], rounds=6)
        actual = base_row(growth)
        if actual["births"] != row["recorded"] or actual["counted"]:
            issues.append((start, law, actual))
    out["earlier_holding_cases"] = {"pairs": len(raw0["d_holding_runs"]["runs"]),
                                    "differences": issues}
    return out


def period_challenge(starts, laws):
    """Search small named cases for one failure of the stated return formula."""
    checked = 0
    for start, law_name in product(starts, ("F1O", "F1R", "H-F1R", "H-F1O", "C3W", "C3WF")):
        law = laws[law_name]
        base = grow(starts[start], law, rounds=8, save_rosters=True)
        first = first_return(base, max_part=25)
        if first is None:
            continue
        q = first["q"]
        if q is None or not first["members_agree_in_parent_steps_counted_in_threes"]:
            continue
        predicted = first["period"] * 3 // gcd(3, q)
        outcomes = {}
        for form in ("PB", "BB"):
            marked = grow(starts[start], law, form, rounds=8, save_rosters=True)
            actual = first_return(marked, max_part=25,
                                  source=(first["s"], frozenset(first["members_at_start"])))
            checked += 1
            outcomes[form] = actual
        if any(actual is not None and actual["period"] != predicted for actual in outcomes.values()):
            return {"tested": checked, "counterexample": {
                "start": start, "start_places": starts[start], "law": law_name,
                "base_first_return": first, "marked_first_returns": outcomes,
                "predicted_period": predicted,
            }}
    return {"tested": checked, "counterexample": None}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true",
                        help="use leading cases at the same growth bounds")
    parser.add_argument("--full-numberings", action="store_true",
                        help="grow on every numbering (default: at most 24 per small start)")
    args = parser.parse_args()
    if args.pilot and args.full_numberings:
        parser.error("the pilot uses a numbering prefix")
    starts = {name: row["stars"] for name, row in read(INPUT / "starts.json")["starts"].items()}
    cases = read(INPUT / "hand_cases.json")
    laws_file = read(INPUT / "laws.json")
    laws = {row["name"]: Law.from_row(row) for row in laws_file["recorded"] + laws_file["holding"]}
    bases = [row["name"] for row in laws_file["recorded"] + laws_file["holding"] if row["base"]]
    raw = {i: read(DATA / f"part{i}.json") for i in (0, 3, 4, 6)}
    raw[8] = read(DATA / "part8.json.gz")
    census = read(DATA / "part1_runs.json.gz")["census_rows"]
    limit = 4 if args.pilot else None
    expected4 = set(product(starts, bases, KNOT_LAWS))
    ids4 = [(r["start"], r["law"], r["knot_law"]) for r in raw[4]["runs"]]
    assert len(ids4) == len(set(ids4)) and set(ids4) == expected4
    assert all(tuple(r["forms"]) == FORMS for r in raw[4]["runs"])
    ids8 = [(r["start"], r["law"], r["knot_law"], r["form"]) for r in raw[8]["named"]]
    assert len(ids8) == len(set(ids8)) and set(ids8) == {(*row, f) for row, f in product(ids4, FORMS[1:])}
    assert {
        (r["start"], r["law"], r["form"]) for r in raw[6]["rows"]
    } == set(product(("Ring(5,3)", "Ring(7,3)"), ("C3W", "C3WF"),
                     (FORM_NAMES[f] for f in ("base", "PB", "BB"))))
    archive_count = numberings_roster_count(starts)
    assert {k: n * 15 for k, n in archive_count.items()} == {
        k: v["runs"] for k, v in raw[0]["g_numberings"]["by_start"].items()
    }
    numbering_limit = None if args.full_numberings else (2 if args.pilot else 24)
    part0 = {
        "gate": gate_comparison(raw[0], starts, laws),
        "hand_cases": hand_comparison(cases),
        "closing_hand_case": close_hand(cases["T_triangle_closing"]["stars"]),
        "planted_error_from_rows": raw_planted(raw[0]["c_planted_error"]["runs"]),
        "numbering_counts_from_frozen_roster": {k: n * 15 for k, n in archive_count.items()},
        "numbering_replays": exercise_numberings(
            starts, {name: laws[name] for name in bases[:5]}, numbering_limit
        ),
        "larger_start_numberings_not_run": [
            key for key in read(INPUT / "numberings_registered.json")["lists"] if key not in archive_count
        ],
    }
    part4 = named_runs(starts, laws, raw[4], raw[8], raw[0], limit)
    from_named = [
        (r["start"], r["law"], form, r["forms"][form])
        for r in raw[4]["runs"] for form in FORMS[1:]
    ]
    from_census = [
        (r["idx"], *key.split("|"), run)
        for r in census if r["kept"] for key, run in r["armw"].items()
    ]
    part4["P3_to_P6_from_rows"] = {
        "named": condition_recount(from_named),
        "census": condition_recount(from_census),
    }
    part4["cost_when_added_distinctions_are_barred"] = {}
    for form in ("PB", "BB"):
        rows = [r["forms"][form] for r in raw[4]["runs"]]
        part4["cost_when_added_distinctions_are_barred"][form] = {
            "new_knots": sum(r["new_knots"] for r in rows),
            "knots_receiving_added_distinctions": sum(r["s_positive"] for r in rows),
            "added_distinctions": sum(r["s_sum"] for r in rows),
            "runs_without_birth": sum(not r["new_knots"] for r in rows),
        }
    output = {
        "pilot": args.pilot,
        "part0": part0, "part3": lone_cases(laws_file, raw[3]),
        "part4": part4, "part6": ring_returns(raw[6], starts, laws),
        "part8": raw_swap_counts(raw[8], census, bases, limit),
    }
    if not args.pilot:
        output["return_formula_challenge"] = period_challenge(starts, laws)
        output["two_retirements_at_one_shared_distinction"] = two_retirements()
    print(json.dumps(output, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
