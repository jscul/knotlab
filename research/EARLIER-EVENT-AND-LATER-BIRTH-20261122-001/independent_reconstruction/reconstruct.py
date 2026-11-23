"""Reconstruct the frozen founder families from their written specifications.

Run with the workspace .venv/bin/python -B. Calls python-sat for full
not-all-equal projection checks. The ordinary growth implementation here
uses only physical holdings and does not import the investigators' code.
"""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, permutations, product
import gzip
import json
from pathlib import Path

from pysat.solvers import Minisat22


ANCHORS = ("A", "A'", "C", "C'")
PAIR_NAMES = ("RS", "RS'", "R'S", "R'S'")


@dataclass
class Stage:
    holdings: dict[str, set[str]]
    values: dict[str, int]

    def holders(self):
        result = defaultdict(set)
        for knot, distinctions in self.holdings.items():
            for distinction in distinctions:
                result[distinction].add(knot)
        return result

    def check_word(self, law):
        assert set(self.holders()) == self.values.keys()
        for distinctions in self.holdings.values():
            word = tuple(self.values[distinction] for distinction in distinctions)
            assert len(word) >= 3 and allows(word, law)


@dataclass
class Birth:
    name: str
    paid: dict[str, str]
    fresh: tuple[str, ...]
    demand: int


def allows(word, law):
    if law == "parity":
        return sum(word) % 2 == 0
    return len(set(word)) == 2


def founder(family, switches, neutral):
    e, f = switches[:2]
    if family == "direct":
        live = dict(zip((*ANCHORS, "K", "B"), (1, 1, 1, 1, 1, 3)))
        marker_counts = (3, 4, 5, 6, 7, 3)
        meetings = [(ANCHORS[1-e], "B"), (ANCHORS[3-f], "B"), ("K", "B")]
    else:
        w = switches[2]
        live = dict(zip((*ANCHORS, "P", "Q", "U"), (1, 1, 1, 1, 2, 2, 1)))
        marker_counts = (3, 4, 5, 6, 3, 4, 7)
        donors = ("P", "Q")
        a_family, c_family = (e, 1-e), (f, 1-f)
        meetings = list(zip(ANCHORS, (donors[index] for index in (*a_family, *c_family))))
        extra_anchor = ANCHORS[a_family.index(w)]
        meetings.extend([(extra_anchor, "U"), ("U", donors[w])])

    stage = Stage(defaultdict(set), {})

    def put(name, value, *holders):
        assert name not in stage.values
        stage.values[name] = value
        for holder in holders:
            stage.holdings[holder].add(name)

    for holder, available in live.items():
        for slot in range(available):
            put(f"open/{holder}/{slot}", 0, holder)

    witnesses = [f"w{i}" for i in range(len(meetings))]
    markers = [f"m{i}" for i in range(len(live))]
    for witness, endpoints in zip(witnesses, meetings):
        for role, holder in enumerate(endpoints):
            for slot in range(2):
                put(f"meet/{witness}/{role}/{slot}", 0, witness, holder)
    for marker, holder, count in zip(markers, live, marker_counts):
        for slot in range(3 if neutral else count):
            put(f"mark/{marker}/{slot}", int(slot < 2), marker, holder)
    spent = witnesses + markers
    for i, (a, b) in enumerate(zip(spent, spent[1:] + spent[:1])):
        for slot in range(2):
            put(f"cycle/{i}/{slot}", 1, a, b)

    owners = stage.holders()
    assert all(len(knots) in (1, 2) for knots in owners.values())
    reached = set()
    todo = [next(iter(stage.holdings))]
    while todo:
        knot = todo.pop()
        if knot not in reached:
            reached.add(knot)
            todo.extend(other for d in stage.holdings[knot] for other in owners[d] - reached)
    assert reached == stage.holdings.keys()
    return stage, live


def groups(witnessed):
    """Enumerate cliques by extending a set only with common neighbors."""
    members = set().union(*witnessed)
    adjacent = {
        member: set().union(*(block for block in witnessed if member in block)) - {member}
        for member in members
    }
    unheld = []
    pairs = []

    def extend(current, eligible):
        while eligible:
            addition = min(eligible)
            eligible.remove(addition)
            grown = current | {addition}
            if len(grown) == 2:
                pairs.append(grown)
            if len(grown) >= 3 and all(not grown <= block for block in witnessed):
                unheld.append(grown)
            extend(grown, eligible & adjacent[addition])

    extend(set(), members.copy())
    maximal = [group for group in unheld if not any(group < other for other in unheld)]
    return maximal + [pair for pair in pairs if not any(pair <= group for group in maximal)]


def step(stage, law, age, binding, first_ones=False):
    owners = stage.holders()
    loose = {
        knot: sorted(d for d in distinctions if owners[d] == {knot})
        for knot, distinctions in stage.holdings.items()
    }
    end = {knot for knot, distinctions in loose.items() if distinctions}
    witnessed = [
        set().union(*(owners[d] - {knot} for d in distinctions)) & end
        for knot, distinctions in stage.holdings.items()
    ]
    parents = [tuple(sorted(group)) for group in groups(witnessed)]
    demands = Counter(knot for group in parents for knot in group)
    assert all(demands[knot] <= len(available) for knot, available in loose.items())
    for knot, available in loose.items():
        parents.extend([(knot,)] * (len(available) - demands[knot]))
    parents.sort()
    children = defaultdict(list)
    for i, group in enumerate(parents):
        for knot in group:
            children[knot].append(i)

    paid = [dict() for _ in parents]
    for knot, roster in children.items():
        available = loose[knot]
        assert len(roster) == len(available)
        if knot in binding:
            # The fixed comparison allocates slot 0 to the A-family,
            # then C-family, then K where present. Shams permute those slots.
            def rank(i):
                group = parents[i]
                return next(j for j, roles in enumerate((ANCHORS[:2], ANCHORS[2:], ("K",)))
                            if any(role in group for role in roles))

            roster = sorted(roster, key=rank)
            available = [available[slot] for slot in binding[knot]]
        for i, distinction in zip(roster, available, strict=True):
            paid[i][knot] = distinction

    prospective = [set(roster) for roster in children.values()]
    next_demand = Counter(i for group in groups(prospective) for i in group)
    result = Stage(dict(stage.holdings), dict(stage.values))
    births = []
    for i, group in enumerate(parents):
        name = f"cut{age}/{i}"
        if law == "parity" and len(parents) == 1:
            fresh_count = 0
        else:
            fresh_count = max(next_demand[i], 3 - len(group), 1)
        fresh = tuple(f"new/{age}/{i}/{slot}" for slot in range(fresh_count))
        birth = Birth(name, paid[i], fresh, next_demand[i])
        assert result.values.keys().isdisjoint(fresh)
        result.holdings[name] = {*birth.paid.values(), *fresh}
        inherited = [result.values[d] for d in birth.paid.values()]
        if fresh:
            # One concrete extension for the raw witness, chosen uniformly
            # across arms. Structural results do not inspect these values.
            bit_order = (1, 0) if first_ones else (0, 1)
            bits = next(bits for bits in product(bit_order, repeat=len(fresh))
                        if allows((*inherited, *bits), law))
            result.values.update(zip(fresh, bits))
        births.append(birth)

    all_paid = [d for birth in births for d in birth.paid.values()]
    assert len(all_paid) == len(set(all_paid))
    assert set(all_paid) == {d for d, knots in owners.items() if len(knots) == 1}
    next_owners = result.holders()
    for birth in births:
        assert result.holdings[birth.name] == {*birth.paid.values(), *birth.fresh}
        for payer, distinction in birth.paid.items():
            assert next_owners[distinction] == {payer, birth.name}
        for distinction in birth.fresh:
            assert next_owners[distinction] == {birth.name}
    result.check_word(law)
    return result, births


def check_projections(stage, law):
    """Check whole-presentation projection against each declared local law."""
    variables = {d: i for i, d in enumerate(stage.values)}
    if law == "parity":
        # Eliminate distinctions outside the target first. The rows
        # supported on the target then give all projected parity equations.
        masks = {k: sum(1 << variables[d] for d in ds) for k, ds in stage.holdings.items()}
        for target in masks.values():
            basis = {}
            for row in masks.values():
                while row:
                    pivot = ((row & ~target) or row).bit_length() - 1
                    if pivot not in basis:
                        basis[pivot] = row
                        break
                    row ^= basis[pivot]
            assert {row for row in basis.values() if row & ~target == 0} == {target}
        return len(masks)
    clauses = [tuple(variables[d] + 1 for d in ds) for ds in stage.holdings.values()]
    checked = 0
    with Minisat22(bootstrap_with=[tuple(sign * i for i in clause)
                                  for clause in clauses for sign in (-1, 1)]) as solver:
        for clause in clauses:
            for word in product((-1, 1), repeat=len(clause)):
                assumptions = [sign * i for sign, i in zip(word, clause, strict=True)]
                assert solver.solve(assumptions=assumptions) == (len(set(word)) == 2)
                checked += 1
    return checked


def read_enrollment(stage, family):
    """Recover marked founder roles and first births from holdings alone."""
    owners = stage.holders()
    repeated = Counter(tuple(sorted(knots)) for knots in owners.values() if len(knots) == 2)
    original = {knot for knots, size in repeated.items() if size > 1 for knot in knots}
    roles = {}
    signature = [(1, n) for n in (3, 4, 5, 6, 7)]
    if family == "direct":
        names = (*ANCHORS, "K", "B")
        signature.append((3, 3))
    else:
        names = (*ANCHORS, "U", "P", "Q")
        signature.extend([(2, 3), (2, 4)])
    for name, (openings, largest) in zip(names, signature, strict=True):
        candidates = []
        for knot in original:
            holdings = stage.holdings[knot]
            original_loose = sum(len(owners[d] & original) == 1 for d in holdings)
            multiplicities = [size for knots, size in repeated.items()
                              if knot in knots and set(knots) <= original]
            if original_loose == openings and max(multiplicities) == largest:
                candidates.append(knot)
        assert len(candidates) == 1
        roles[name] = candidates[0]
    return roles, original


def reconstruct(family, switches, law, binding, neutral, projection, rename=False):
    source, live = founder(family, switches, neutral)
    source.check_word(law)
    knot_names = {k: k for k in source.holdings}
    distinction_names = {d: d for d in source.values}
    if rename:
        knot_names = {k: f"renamed-holder/{i}" for i, k in enumerate(reversed(knot_names))}
        distinction_names = {d: f"renamed-mark/{i:03}" for i, d in enumerate(distinction_names)}
        source = Stage(
            {knot_names[k]: {distinction_names[d] for d in ds} for k, ds in source.holdings.items()},
            {distinction_names[d]: bit for d, bit in source.values.items()},
        )
    binding = {knot_names[k]: slots for k, slots in binding.items()}
    anchor_names = [knot_names[k] for k in ANCHORS]
    stages = [source]
    cohorts = []
    for age in range(1, 4):
        # Renaming tests the same structural endpoint without tying the
        # check to a lexical allocation of its donor distinctions.
        following, births = step(stages[-1], law, age, binding if age == 1 else {},
                                 first_ones=family == "direct" and age == 1)
        if family == "direct" and age == 1:
            assert all(tuple(following.values[d] for d in birth.fresh) == (1, 1) for birth in births)
        cohorts.append(births)
        stages.append(following)
    projection_checks = [check_projections(stage, law) for stage in stages] if projection else []
    assert all(birth.fresh for cohort in cohorts for birth in cohort)
    first, second, _ = cohorts
    enrolled = [
        next(birth for birth in first if anchor in birth.paid)
        for anchor in anchor_names
    ]
    if not neutral:
        for stage in stages:
            roles, original = read_enrollment(stage, family)
            assert roles == {role: knot_names[role] for role in live}
            assert original == source.holdings.keys()
            if stage is not source:
                for anchor, birth in zip(anchor_names, enrolled, strict=True):
                    holders = stage.holders()[birth.paid[anchor]]
                    assert holders - original == {birth.name}
    first_roles = {birth.name: label for birth, label in zip(enrolled, ("R", "R'", "S", "S'"))}
    r, rp, s, sp = enrolled
    e, f = switches[:2]
    if family == "direct":
        payer = knot_names["B"]
        high_anchors = [anchor_names[1-e], anchor_names[3-f], knot_names["K"]]
        donor_first = [next(birth for birth in first if anchor in birth.paid) for anchor in high_anchors]
        first_roles[donor_first[-1].name] = "K_child"
        assert {birth.name for birth in first if payer in birth.paid} == {b.name for b in donor_first}
        assert all(set(birth.paid) == {payer, anchor}
                   for birth, anchor in zip(donor_first, high_anchors, strict=True))
        assert r.paid.keys() & s.paid.keys() == ({payer} if e and f else set())
        predicted = (bool(e * f), bool(e * (1-f)), bool((1-e) * f), bool((1-e) * (1-f)))
    else:
        donor_names = tuple(knot_names[name] for name in ("P", "Q"))
        extra_payer = knot_names["U"]
        for i, (anchor, role, donor) in enumerate(zip(anchor_names, enrolled, (e, 1-e, f, 1-f))):
            required = {anchor, donor_names[donor]}
            if i < 2 and donor == switches[2]:
                required.add(extra_payer)
            assert role.paid.keys() == required
        assert r.paid.keys() & s.paid.keys() == ({donor_names[e]} if e == f else set())
        predicted = (e == f, e != f, e != f, e == f)

    pairs = [(r, s), (r, sp), (rp, s), (rp, sp)]
    actual = []
    for a, b in pairs:
        containing = [birth for birth in second if {a.name, b.name} <= birth.paid.keys()]
        assert all(birth.paid.keys() == {a.name, b.name} for birth in containing)
        assert len(containing) <= 1
        actual.append(bool(containing))
        if containing:
            assert containing[0].paid[a.name] in a.fresh
            assert containing[0].paid[b.name] in b.fresh
    assert tuple(actual) == predicted
    first_owners = stages[1].holders()
    first_values = stages[1].values
    local_receipts = {}
    future = {}
    for role in enrolled:
        label = first_roles[role.name]
        expected_open = 2 if family == "direct" else 1
        assert len(role.fresh) == expected_open, (family, switches, label, role)
        assert len([birth for birth in second if role.name in birth.paid]) == expected_open
        assert set(role.fresh) == {birth.paid[role.name] for birth in second if role.name in birth.paid}
        local_receipts[label] = {
            "shared_values": sorted(first_values[d] for d in stages[1].holdings[role.name]
                                    if len(first_owners[d]) == 2),
            "loose_values": sorted(first_values[d] for d in stages[1].holdings[role.name]
                                   if len(first_owners[d]) == 1),
        }
        future[label] = sorted(
            tuple(sorted(first_roles.get(parent, parent) for parent in birth.paid))
            for birth in second if role.name in birth.paid
        )
    if family == "direct":
        sibling_names = {birth.name for birth in donor_first}
        sibling_births = [birth for birth in second if len(birth.paid.keys() & sibling_names) >= 2]
        assert {frozenset(birth.paid) for birth in sibling_births} == {
            frozenset(pair) for pair in combinations(sibling_names, 2)
        }
    else:
        assert all(len(partners) == 1 and len(partners[0]) == 2 for partners in future.values())

    return {
        "switches": switches,
        "law": law,
        "counts": [len(cohort) for cohort in cohorts],
        "parent_arity_counts": [dict(Counter(len(birth.paid) for birth in cohort)) for cohort in cohorts],
        "projection_checks": projection_checks,
        "target_pairs": dict(zip(PAIR_NAMES, actual)),
        "possible_common_witnesses_RS": sorted(r.paid.keys() & s.paid.keys()),
        "receipt": local_receipts,
        "next_parents": future,
        "enrollment": {first_roles[birth.name]: birth.name for birth in enrolled},
        "rounds": [[vars(birth) for birth in cohort] for cohort in cohorts],
    }


def primary_comparisons(cases, law):
    hi, move_r, move_s, both = (cases[law, "direct", bits] for bits in ((1, 1), (0, 1), (1, 0), (0, 0)))
    for arm in (hi, move_r, move_s, both):
        first = arm["rounds"][0]
        b_slots = {frozenset(birth["paid"].keys() - {"B"}): birth["paid"]["B"]
                   for birth in first if "B" in birth["paid"]}
        e, f = arm["switches"]
        assert b_slots == {frozenset({ANCHORS[1-e]}): "open/B/0",
                           frozenset({ANCHORS[3-f]}): "open/B/1",
                           frozenset({"K"}): "open/B/2"}
    assert hi["receipt"]["S"] == move_r["receipt"]["S"]
    assert hi["receipt"]["R"] == move_s["receipt"]["R"]
    assert hi["receipt"]["R"]["loose_values"] == move_r["receipt"]["R"]["loose_values"] == [1, 1]
    for arm, role in ((move_r, "S"), (move_s, "R")):
        original, diverted = (row["rounds"][0] for row in (hi, arm))
        lhs, rhs = (next(b["paid"] for b in first if b["name"] == row["enrollment"][role])
                    for first, row in ((original, hi), (diverted, arm)))
        assert lhs == rhs
    for e, f, w in product((0, 1), repeat=3):
        arm = cases[law, "balanced", (e, f, w)]
        move_extra = cases[law, "balanced", (e, f, 1-w)]
        move_target = cases[law, "balanced", (e, 1-f, w)]
        assert arm["target_pairs"] == move_extra["target_pairs"]
        assert {len(row["receipt"]["R"]["shared_values"]) for row in (arm, move_extra)} == {2, 3}
        assert arm["receipt"]["R"] == move_target["receipt"]["R"]
        assert arm["target_pairs"]["RS"] != move_target["target_pairs"]["RS"]
    balanced_hi = cases[law, "balanced", (0, 0, 1)]
    balanced_mask = cases[law, "balanced", (1, 0, 0)]
    assert balanced_hi["receipt"]["R"] == balanced_mask["receipt"]["R"]
    assert balanced_hi["receipt"]["S"] == balanced_mask["receipt"]["S"]
    assert balanced_hi["target_pairs"]["RS"] and not balanced_mask["target_pairs"]["RS"]
    for row in (balanced_hi, balanced_mask):
        assert next(b["paid"] for b in row["rounds"][0] if b["name"] == row["enrollment"]["S"]) == {
            "C": "open/C/0", "P": "open/P/1"
        }



def read_raw_stages(run):
    return [Stage({str(k): set(map(str, ds)) for k, ds in enumerate(level["holdings"])},
                  level["word"]) for level in run["levels"]]


def actual_births(previous, following):
    prior = previous.holders()
    added_knots = following.holdings.keys() - previous.holdings.keys()
    added_marks = following.values.keys() - previous.values.keys()
    paid, fresh = {}, {}
    assert previous.values == {d: following.values[d] for d in previous.values}
    assert previous.holdings == {k: following.holdings[k] for k in previous.holdings}
    for knot in added_knots:
        distinctions = following.holdings[knot]
        paid[knot] = {}
        fresh[knot] = distinctions & added_marks
        for distinction in distinctions - added_marks:
            (parent,) = prior[distinction]
            assert parent not in paid[knot]
            paid[knot][parent] = distinction
    assert Counter(d for receipt in paid.values() for d in receipt.values()) == Counter(
        d for d, knots in prior.items() if len(knots) == 1
    )
    assert sum(map(len, fresh.values())) == len(added_marks)
    return paid, fresh


def check_raw_record(cases):
    """Check the recorded names from holdings, with no recorded birth metadata."""
    root = Path(__file__).resolve().parents[3]
    record = (root / "artifacts/EARLIER-EVENT-AND-LATER-BIRTH-20261122-001B"
              / "EARLIER-EVENT-AND-LATER-BIRTH-20261122-001B-E001_matched_replay"
              / "physical_replay.json.gz")
    checked = Counter()
    examples, direct_sham = {}, {}
    with gzip.open(record, "rt") as raw:
        rows = json.load(raw)
    for row in rows:
        law = "not-all-equal" if row["law"] == "nae" else row["law"]
        family, switches = row["family"], tuple(row["switches"])
        base = cases[law, family, switches]
        runs = [(f"binding_{i}", run) for i, run in enumerate(row["runs"])]
        controls = ("neutral_markers", "coherent_relabelling", "alternate_word", "next_payment_sham")
        runs.extend((name, row[name]) for name in controls)
        for name, run in runs:
            source, first, second, third = read_raw_stages(run)
            source.check_word(law)
            raw_births = []
            for age, (previous, following) in enumerate(
                zip((source, first, second), (first, second, third), strict=True), 1
            ):
                following.check_word(law)
                obtained, fresh = actual_births(previous, following)
                _, reconstructed = step(previous, law, age, {})
                assert Counter((frozenset(paid), len(fresh[k])) for k, paid in obtained.items()) == (
                    Counter((frozenset(birth.paid), len(birth.fresh)) for birth in reconstructed)
                )
                raw_births.append((obtained, fresh))
            checked["complete_histories"] += 1
            if name == "neutral_markers":
                continue
            roles, originals = read_enrollment(third, family)
            assert originals == source.holdings.keys()
            earlier, fresh = raw_births[0]
            later, following_fresh = raw_births[1]
            r, rp, s, sp = [next(k for k, paid in earlier.items() if roles[anchor] in paid)
                            for anchor in ANCHORS]
            candidates = ((r, s), (r, sp), (rp, s), (rp, sp))
            assert {pair: any(set(members) == paid.keys() for paid in later.values())
                    for pair, members in zip(PAIR_NAMES, candidates, strict=True)} == base["target_pairs"]
            checked["enrolled_histories"] += 1
            if family == "direct" and switches == (1, 1) and name.startswith("binding_"):
                binding = row["bindings"][int(name.removeprefix("binding_"))]
                if binding == {"B": [1, 0, 2]}:
                    assert earlier[r][roles["B"]] == "64"
                    assert earlier[s][roles["B"]] == "63"
                    direct_sham[law] = {"donor_to_R": 64, "donor_to_S": 63, "target_still_funded": True}
            if name != "binding_0":
                continue
            labels = {v: k for k, v in roles.items()}
            keys = ("R", "R'", "S", "S'")
            receipts = {label: {labels[parent]: int(d) for parent, d in earlier[knot].items()}
                        for knot, label in zip((r, rp, s, sp), keys, strict=True)}
            later_target = next((child for child, paid in later.items() if paid.keys() == {r, s}), None)
            example = {
                "old_payments": receipts,
                "loose_after_first": {label: sorted(map(int, fresh[knot]))
                                      for knot, label in zip((r, rp, s, sp), keys, strict=True)},
                "target_paid": None,
            }
            if later_target is not None:
                example["target_paid"] = {label: int(later[later_target][knot])
                                          for label, knot in (("R", r), ("S", s))}
                onward = next(paid[later_target] for paid in raw_births[2][0].values()
                              if later_target in paid)
                assert onward in following_fresh[later_target]
                example["target_onward"] = int(onward)
            examples[law, family, switches] = example

    for law in ("parity", "not-all-equal"):
        high, move_r, move_s = [examples[law, "direct", bits] for bits in ((1, 1), (0, 1), (1, 0))]
        assert high["old_payments"]["R"] == move_s["old_payments"]["R"] == {"A": 58, "B": 63}
        assert high["old_payments"]["S"] == move_r["old_payments"]["S"] == {"C": 60, "B": 64}
        assert move_r["old_payments"]["R"] == {"A": 58}
        assert move_r["old_payments"]["R'"] == {"A'": 59, "B": 63}
        assert move_s["old_payments"]["S"] == {"C": 60}
        assert move_s["old_payments"]["S'"] == {"C'": 61, "B": 64}
        assert high["target_paid"] == {"R": 66, "S": 68}
        assert high["target_onward"] == 76
        assert move_r["target_paid"] is None and move_s["target_paid"] is None
        joint, switched = [examples[law, "balanced", bits] for bits in ((0, 0, 1), (1, 0, 0))]
        assert joint["old_payments"]["R"] == {"A": 82, "P": 86}
        assert switched["old_payments"]["R"] == {"A": 82, "Q": 88}
        assert joint["old_payments"]["S"] == switched["old_payments"]["S"] == {"C": 84, "P": 87}
        assert joint["loose_after_first"]["R"] == switched["loose_after_first"]["R"] == [92]
        assert joint["loose_after_first"]["S"] == switched["loose_after_first"]["S"] == [93]
        assert joint["target_paid"] == {"R": 92, "S": 93} and switched["target_paid"] is None
    assert len(direct_sham) == 2
    return {
        "coverage": dict(checked),
        "same_founder_direct_sham": direct_sham,
        "named_examples": [{"law": law, "family": family, "switches": switches, **example}
                           for (law, family, switches), example in examples.items()],
    }



def donor_bindings(family):
    if family == "direct":
        return [{"B": slots} for slots in permutations(range(3))]
    return [{"P": p, "Q": q} for p, q in product(permutations(range(2)), repeat=2)]


def one_cut_beyond():
    """Check a fourth cut for two selected fixed marked founders."""
    cases = {"direct": (1, 1), "balanced": (0, 0, 1)}
    extra = []
    for law in ("parity", "not-all-equal"):
        for family, switches in cases.items():
            profiles = []
            pair_count = 3 if family == "direct" else 6
            fixed_flips = ("open/A/0", "mark/m0/0", f"cycle/{pair_count}/0",
                           f"cycle/{pair_count + 1}/0", "mark/m2/0", "open/C/0")
            for binding in donor_bindings(family):
                for value_control in (False, True):
                    stage, _ = founder(family, switches, False)
                    if value_control:
                        for d in fixed_flips:
                            stage.values[d] ^= 1
                    stage.check_word(law)
                    for age in range(1, 5):
                        stage, births = step(stage, law, age, binding if age == 1 else {})
                    profiles.append({birth.name: [sorted(birth.paid), len(birth.fresh), birth.demand]
                                     for birth in births})
            assert all(profile == profiles[0] for profile in profiles)
            counts = Counter((len(parents), granted) for parents, granted, _ in profiles[0].values())
            extra.append({
                "family": family, "switches": switches, "law": law,
                "four_cut_histories": len(profiles),
                "fourth_cut_births": len(profiles[0]),
                "fourth_cut_arity_grant_counts": [
                    {"parent_count": arity, "fresh_grant": grant, "birth_count": count}
                    for (arity, grant), count in sorted(counts.items())
                ],
                "alternate_source_flips": fixed_flips,
                "fourth_cut_roster": profiles[0],
            })
    return extra


def main():
    cases = {}
    counts = Counter()
    for law in ("parity", "not-all-equal"):
        for family in ("direct", "balanced"):
            if family == "direct":
                settings = product((0, 1), repeat=2)
            else:
                settings = product((0, 1), repeat=3)
            bindings = donor_bindings(family)
            profiles = set()
            for switches in settings:
                base = reconstruct(family, switches, law, bindings[0], False, True)
                cases[law, family, switches] = base
                for neutral in (False, True):
                    for binding_index, binding in enumerate(bindings):
                        if not neutral and binding_index == 0:
                            row = base
                        else:
                            row = reconstruct(family, switches, law, binding, neutral,
                                              neutral and binding_index == 0)
                        assert row["target_pairs"] == base["target_pairs"]
                        assert row["next_parents"] == base["next_parents"]
                        for actual, expected in zip(row["rounds"], base["rounds"], strict=True):
                            assert [birth["paid"].keys() for birth in actual] == [
                                birth["paid"].keys() for birth in expected
                            ]
                            assert [len(birth["fresh"]) for birth in actual] == [
                                len(birth["fresh"]) for birth in expected
                            ]
                        for cut, n in enumerate(row["projection_checks"]):
                            counts[f"{law}_projection_tests_cut_{cut}"] += n
                        counts[f"{law}_{family}_{'neutral' if neutral else 'marked'}_runs"] += 1
                renamed = reconstruct(family, switches, law, {}, False, False, rename=True)
                assert renamed["target_pairs"] == base["target_pairs"]
                assert renamed["counts"] == base["counts"]
                assert renamed["parent_arity_counts"] == base["parent_arity_counts"]
                counts[f"{law}_{family}_renaming_checks"] += 1
                profiles.add(tuple(base["counts"]))
            assert len(profiles) == 1, (law, family, profiles)
        primary_comparisons(cases, law)
    for (_, family, switches), case in cases.items():
        other = cases["not-all-equal", family, switches]
        assert case["rounds"] == other["rounds"]

    result = {"coverage": dict(counts), "raw_replay_check": check_raw_record(cases),
              "fourth_cut_stress_check": one_cut_beyond(), "primary_rows": [
        {"family": family, **case} for (_, family, _), case in cases.items()
    ]}
    Path(__file__).with_name("results.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps(result["coverage"], indent=2))


if __name__ == "__main__":
    main()
