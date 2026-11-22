"""Replay the one archived X4 spare pair and its actual next payments."""

from collections import Counter, defaultdict, deque
from dataclasses import asdict, dataclass
from gzip import compress
from hashlib import sha256
from itertools import combinations, permutations
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
SOURCE_DIR = ROOT / "research/SPARE-AND-NEXT-PAYMENT-20261122-001"
DESIGN = SOURCE_DIR / "design_candidate.md"
DESIGN_HASH = "f47bc4c776b56fc98974cbd5d5b2b6f47b28f5a7a3099f2fbf4d2ba503c1d6ff"
ARCHIVE, = (ROOT / "artifacts/COPIES-AND-MEETINGS-20261120-001A").glob("*/mediator.json")
OPERATOR, = (ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A").glob("*/end_operator.py")
END = run_path(str(OPERATOR))
LAWS = ("parity", "nae")
SIZE_CAP = 9
RIGHT_END = 5
EDIT_HOLDER = 4
MAX_BIRTHS = 1024


@dataclass(frozen=True)
class Birth:
    knot: int
    parents: tuple
    paid: tuple
    fresh: tuple
    demand: int

    @property
    def holding(self):
        return self.paid + self.fresh


@dataclass
class History:
    source: tuple
    stages: dict
    cohorts: dict
    multiple_groups: dict
    roles: dict
    origins: dict
    lineages: dict
    pure: dict


def owners(holdings):
    incidence = defaultdict(list)
    for knot, holding in enumerate(holdings):
        assert len(holding) == len(set(holding))
        for mark in holding:
            incidence[mark].append(knot)
    assert all(len(holding) in (1, 2) for holding in incidence.values())
    return {mark: tuple(held) for mark, held in incidence.items()}


def loose_marks(incidence):
    loose = defaultdict(list)
    for mark, held in sorted(incidence.items()):
        if len(held) == 1:
            loose[held[0]].append(mark)
    return dict(loose)


def witness_sets(incidence, live):
    shared = defaultdict(set)
    for held in incidence.values():
        if len(held) == 2:
            x, y = held
            shared[x].add(y)
            shared[y].add(x)
    return {older: family & live for older, family in shared.items() if len(family & live) >= 2}


def candidate_groups(live, blocks):
    """Enumerate actual maximal groups independently of the archived pivot search."""
    neighbors = {knot: set() for knot in live}
    for group in blocks:
        for a, b in combinations(sorted(group), 2):
            neighbors[a].add(b)
            neighbors[b].add(a)
    triples_or_more = []
    for a in sorted(live):
        above = sorted(b for b in neighbors[a] if a < b)
        for rank in range(2, len(above) + 1):
            for rest in combinations(above, rank):
                group = (a, *rest)
                if not all(b in neighbors[c] for b, c in combinations(rest, 2)):
                    continue
                if set.intersection(*(neighbors[knot] for knot in group)):
                    continue
                if not any(set(group) <= block for block in blocks):
                    triples_or_more.append(group)
    covered = {pair for group in triples_or_more for pair in combinations(group, 2)}
    pairs = {(a, b) for a in live for b in neighbors[a] if a < b}
    return tuple(sorted(triples_or_more) + sorted(pairs - covered))


def next_groups_from_parents(parent_groups, first_id):
    cohorts = defaultdict(set)
    for child, group in enumerate(parent_groups, first_id):
        for parent in group:
            cohorts[parent].add(child)
    candidate_witnesses = tuple(held for held in cohorts.values() if len(held) >= 2)
    return candidate_groups(range(first_id, first_id + len(parent_groups)), candidate_witnesses)


def append_cut(holdings, law):
    incidence = owners(holdings)
    loose = loose_marks(incidence)
    blocks = tuple(witness_sets(incidence, loose.keys()).values())
    multiple = candidate_groups(loose, blocks)
    used = Counter(parent for group in multiple for parent in group)
    assert multiple == END["proposals"](END["from_stars"](holdings))
    assert all(used[parent] <= len(bank) for parent, bank in loose.items())
    unary = tuple((parent,) for parent in sorted(loose) for _ in range(len(loose[parent]) - used[parent]))
    all_groups = multiple + unary
    nominal_plan = END["step"](END["from_stars"](holdings), law, max_births=MAX_BIRTHS)
    assert nominal_plan.status == "extend" and not nominal_plan.implied and not nominal_plan.shortages
    assert nominal_plan.parents == all_groups
    next_groups = next_groups_from_parents(all_groups, len(holdings))
    demand = Counter(parent for group in next_groups for parent in group)
    queues = {parent: iter(bank) for parent, bank in loose.items()}
    top = max(incidence) + 1
    births = []
    for i, parents in enumerate(all_groups):
        child = len(holdings) + i
        grant = max(demand[child], 3 - len(parents), 1)
        assert (demand[child], grant) == (nominal_plan.demand[i], nominal_plan.fresh[i])
        paid = tuple(next(queues[parent]) for parent in parents)
        fresh = tuple(range(top, top + grant))
        births.append(Birth(child, parents, paid, fresh, demand[child]))
        top += grant
    assert all(next(queue, None) is None for queue in queues.values())
    grown = holdings + tuple(birth.holding for birth in births)
    new_owners = owners(grown)
    for row in births:
        assert all(incidence[name] == (p,) and new_owners[name] == (p, row.knot)
                   for p, name in zip(row.parents, row.paid, strict=True))
        assert all(name not in incidence and new_owners[name] == (row.knot,) for name in row.fresh)
    return grown, tuple(births), multiple


def replay(source, law, fixed_roles):
    count = len(source)
    history = History(source, {1: source}, {}, {}, dict(enumerate(range(count))),
                      {i: {i} for i in range(count)}, {i: set() for i in range(count)}, {})
    for size in range(2, SIZE_CAP + 1):
        holdings, births, groups = append_cut(history.stages[size - 1], law)
        history.stages[size] = holdings
        history.cohorts[size] = births
        history.multiple_groups[size] = groups
        roles_before = set()
        for row in births:
            signature = tuple(sorted(history.roles[parent] for parent in row.parents))
            role = fixed_roles.setdefault(signature, count + len(fixed_roles))
            if role in roles_before:
                raise ValueError(f"Ambiguous parent-role matching at size {size}: {signature}")
            roles_before.add(role)
            history.roles[row.knot] = role
            history.origins[row.knot] = set().union(*(history.origins[p] for p in row.parents))
            roots = {"left"} if size == 2 and row.parents == (0,) else (
                {"right"} if size == 2 and row.parents == (RIGHT_END,) else set())
            history.lineages[row.knot] = roots or set().union(*(history.lineages[p] for p in row.parents))
            inherited_purity = {history.pure.get(p) for p in row.parents}
            if roots or (len(inherited_purity) == 1 and None not in inherited_purity):
                history.pure[row.knot] = next(iter(roots or inherited_purity))
        assert all(sum(history.pure.get(b.knot) == end for b in births) == 1 for end in ("left", "right"))
    return history


def old_shape_parent_keys(shape, loaded):
    """Read the predecessor's archived interval/deletion identification as a check."""
    first, last, marked = shape
    parents = {(first, last, False)} if marked else set()
    for a, b in ((first + 1, last), (first, last - 1)):
        if a <= b and a <= RIGHT_END and b >= 0 and (not marked or a <= EDIT_HOLDER <= b):
            parents.add((a, b, marked))
    assert loaded or not marked
    return parents


def archived_shapes(history, loaded):
    indices = {i: (i, i, False) for i in range(RIGHT_END + 1)}
    for size, rows in history.cohorts.items():
        patterns = {(a, a + size - 1, False) for a in range(1 - size, RIGHT_END + 1)}
        if loaded:
            patterns.update((a, a + size - 2, True) for a in range(EDIT_HOLDER - size + 2, EDIT_HOLDER + 1))
        by_parent = {frozenset(old_shape_parent_keys(pattern, loaded)): pattern for pattern in patterns}
        assert len(by_parent) == len(patterns) == len(rows)
        actual = {row.knot: by_parent[frozenset(indices[p] for p in row.parents)] for row in rows}
        assert set(actual.values()) == patterns
        indices.update(actual)
    return indices


def lawful(law, bits):
    n = sum(bits)
    return n % 2 == 0 if law == "parity" else 0 < n < len(bits)


def lawful_world(law, word, holdings):
    return all(lawful(law, tuple(word[mark] for mark in held)) for held in holdings)


def launch_world(law, holdings):
    incidence = owners(holdings)
    world = dict.fromkeys(incidence, 0)
    if law == "nae":
        private = loose_marks(incidence)
        for holder, marks in enumerate(holdings):
            if holder in private:
                assert len(private[holder]) >= 2
                world[private[holder][1]] = 1
            else:
                # The exhausted source witnesses have disjoint holdings.
                assert all(all(k <= RIGHT_END for k in incidence[mark] if k != holder) for mark in marks)
                world[marks[0]] = 1
    assert lawful_world(law, world, holdings)
    return world


def materialize(law, prefix, old_holdings, rows):
    word = dict(prefix)
    holdings = dict(enumerate(old_holdings))
    incidence = owners(old_holdings)
    paid_now = set()
    for birth in rows:
        paid = tuple(word[mark] for mark in birth.paid)
        assert birth.knot not in holdings and not paid_now.intersection(birth.paid)
        assert all(incidence[mark] == (p,) for p, mark in zip(birth.parents, birth.paid, strict=True))
        assert not set(birth.fresh).intersection(word)
        if law == "parity":
            bank = (sum(paid) % 2, *((0,) * (len(birth.fresh) - 1)))
        else:
            bit = 1 if not any(paid) else 0
            bank = (bit,) * len(birth.fresh)
        assert lawful(law, paid + bank)
        word.update(zip(birth.fresh, bank, strict=True))
        paid_now.update(birth.paid)
        holdings[birth.knot] = birth.holding
    assert paid_now == {mark for mark, held in incidence.items() if len(held) == 1}
    assert all(word[mark] == value for mark, value in prefix.items())
    published_holdings = tuple(holdings[knot] for knot in sorted(holdings))
    assert lawful_world(law, word, published_holdings)
    return word, published_holdings


def values(word):
    assert set(word) == set(range(len(word)))
    return "".join(str(word[i]) for i in range(len(word)))


def ancestry(history, knot):
    return {"source_holders": sorted(history.origins[knot]), "releases": sorted(history.lineages[knot]),
            "pure_release": history.pure.get(knot)}


def described_birth(history, size, row, indices):
    before, after = (owners(history.stages[stage]) for stage in (size - 1, size))
    payment_rows = []
    for parent, mark in zip(row.parents, row.paid, strict=True):
        payment_rows.append({"payer": parent, "payer_audit_role": history.roles[parent], "distinction": mark,
                             "physical_owners_before": before[mark], "physical_owners_after": after[mark],
                             "payer_ancestry": ancestry(history, parent)})
    return {**asdict(row), "audit_matched_role": history.roles[row.knot], "archived_role": indices[row.knot],
            "ancestry": ancestry(history, row.knot), "payments": payment_rows}


def child_map(rows, history):
    return {history.roles[row.knot]: row for row in rows}


def match_and_select(archive, histories, indices):
    left, right = histories
    matches = {}
    for expected in archive["by_size"]:
        size = expected["size"]
        rows = [h.cohorts[size] for h in histories]
        by_role = [child_map(r, h) for r, h in zip(rows, histories, strict=True)]
        common = by_role[0].keys() & by_role[1].keys()
        assert by_role[0].keys() == common
        for role in common:
            assert indices[0][by_role[0][role].knot] == indices[1][by_role[1][role].knot]
        assert [len(r) for r in rows] == expected["births"]
        mixed = [[b for b in r if h.lineages[b.knot] == {"left", "right"}]
                 for r, h in zip(rows, histories, strict=True)]
        assert [len(r) for r in mixed] == expected["both_launches"]
        assert [sum(len(b.fresh) for b in r) for r in mixed] == expected["fresh_on_both_launches"]
        increased = sum("left" in left.lineages[by_role[0][p].knot]
                        and len(by_role[0][p].fresh) < len(by_role[1][p].fresh) for p in common)
        assert increased == expected["A_inclusive_old_price_increases"]
        matches[size] = {"matched": {p: [by_role[0][p].knot, by_role[1][p].knot] for p in sorted(common)},
                         "loaded_only": [by_role[1][p].knot for p in sorted(by_role[1].keys() - common)]}
    focused = []
    for i, history in enumerate(histories):
        focal, = (b for b in history.cohorts[8] if history.lineages[b.knot] == {"left", "right"})
        known = archive["first_mixed"][i]
        assert (focal.knot, list(focal.parents), list(focal.paid), list(focal.fresh)) == (
            known["knot"], known["parents"], known["consumed"], known["fresh"])
        focused.append(focal)
    assert left.roles[focused[0].knot] == right.roles[focused[1].knot]
    new_joint, = (b for b in right.cohorts[9] if b.knot in matches[9]["loaded_only"]
                  and right.lineages[b.knot] == {"left", "right"})
    return matches, focused, new_joint


def local_holding(history, focal):
    held = owners(history.stages[8])
    after = owners(history.stages[9])
    read = {"held": len(focal.holding), "inherited_shared": sum(len(held[m]) == 2 for m in focal.holding),
            "own_singly_held": sum(len(held[m]) == 1 for m in focal.holding)}
    assert read["inherited_shared"] == len(focal.paid) and read["own_singly_held"] == len(focal.fresh)
    assert all(held[m] == after[m] for m in focal.paid)
    assert all(held[m] == (focal.knot,) and after[m][0] == focal.knot and len(after[m]) == 2 for m in focal.fresh)
    return {"name_free_read_at_birth": read, "inherited_owners_across_next_cut": {n: after[n] for n in focal.paid},
            "fresh_owners_at_birth": {m: held[m] for m in focal.fresh},
            "fresh_owners_after_next_cut": {m: after[m] for m in focal.fresh}}


def witnessed_payment_group(rows, group):
    by_newborn = {row.knot: row for row in rows}
    witness_rows = []
    for x, y in combinations(group, 2):
        left, right = by_newborn[x], by_newborn[y]
        common = sorted(set(left.parents) & set(right.parents))
        assert common
        witness_rows.append({"participants": (x, y), "older_witness_payments": [
            {"holder": p, "paid_to_first": left.paid[left.parents.index(p)],
             "paid_to_second": right.paid[right.parents.index(p)]} for p in common]})
    whole_witnesses = set.intersection(*(set(by_newborn[h].parents) for h in group))
    if len(group) > 2:
        assert not whole_witnesses
    return {"participants": group, "pairwise_older_witnesses": witness_rows,
            "one_older_holder_witnesses_the_whole_group": sorted(whole_witnesses)}


def h_forecast(history, focal):
    size8 = history.cohorts[8]
    future = next_groups_from_parents(tuple(b.parents for b in size8), size8[0].knot)
    assert future == history.multiple_groups[9]
    participates = [g for g in future if focal.knot in g]
    spending = [row for row in history.cohorts[9] if focal.knot in row.parents]
    floor = max(1, 3 - len(focal.parents))
    assert focal.demand == len(participates)
    assert len(focal.fresh) == max(floor, focal.demand)
    unary_surplus = len(focal.fresh) - focal.demand
    assert unary_surplus == sum(b.parents == (focal.knot,) for b in spending)
    assert {row.paid[row.parents.index(focal.knot)] for row in spending} == set(focal.fresh)
    assert len(spending) == focal.demand + unary_surplus == len(focal.fresh)
    return {"full_prospective_multiple_parent_roster": future, "through_H_before_its_grant": participates,
            "eligible_group_count": focal.demand, "arity_based_fresh_minimum": floor,
            "actual_fresh_grant": len(focal.fresh), "unary_surplus": unary_surplus,
            "witnesses_for_groups_through_H": [witnessed_payment_group(size8, group) for group in participates],
            "actual_next_payment_slots": {row.knot: row.paid[row.parents.index(focal.knot)] for row in spending}}, spending


def pure_opportunities(history):
    opportunities = {}
    for root in ("left", "right"):
        before, = (row for row in history.cohorts[8] if history.pure.get(row.knot) == root)
        after, = (row for row in history.cohorts[9] if history.pure.get(row.knot) == root)
        assert after.parents == (before.knot,)
        through = [row for row in history.cohorts[9] if before.knot in row.parents]
        opportunities[root] = {"size_eight_pure_holder": before.knot, "size_nine_pure_child": after.knot,
                               "all_size_nine_children_taking_a_payment_from_pure_holder": [asdict(r) for r in through],
                               "ordinary_parent_roles_for_these_opportunities": [
                                   {"roles": sorted(history.roles[p] for p in r.parents), "grant": len(r.fresh)} for r in through]}
    return opportunities


def deficient_control(law, history, focal):
    end = END["from_stars"](history.stages[8])
    assert end.opens[focal.knot] == len(focal.fresh) and len(focal.fresh) > 1
    lower = dict(end.opens)
    lower[focal.knot] -= 1
    hypothetical = END["End"](lower, end.blocks)
    assert END["proposals"](end) == END["proposals"](hypothetical)
    plan = END["step"](hypothetical, law, max_births=MAX_BIRTHS)
    assert plan.status == "stall" and plan.shortages == ((focal.knot, 1),) and not plan.parents
    return {"status": plan.status, "one_less_H_supply": lower[focal.knot], "shortages": plan.shortages,
            "all_size_nine_births_suppressed": len(history.cohorts[9]), "both_pure_children_suppressed": True,
            "ordinary_reached_history": False}


def reallocated(rows, focal, slots, assignment):
    assigned = dict(zip((b.knot for b in slots), assignment, strict=True))
    different = []
    for birth in rows:
        if birth.knot not in assigned:
            different.append(birth)
            continue
        paid = list(birth.paid)
        paid[birth.parents.index(focal.knot)] = assigned[birth.knot]
        different.append(Birth(birth.knot, birth.parents, tuple(paid), birth.fresh, birth.demand))
    return tuple(different)


def coherent_control(law, final_word, final_supports, prior_holding, focal, final_read):
    high = max(final_word)
    rename = {old: high - old for old in final_word}
    new_word = {rename[old]: bit for old, bit in final_word.items()}
    new_holdings = tuple(tuple(rename[old] for old in held) for held in final_supports)
    new_prefix = tuple(tuple(rename[old] for old in held) for held in prior_holding)
    assert lawful_world(law, new_word, new_holdings)
    assert END["from_stars"](new_prefix) == END["from_stars"](prior_holding)
    orig_owners, new_owners = owners(final_supports), owners(new_holdings)
    assert all(orig_owners[old] == new_owners[new] for old, new in rename.items())
    held = new_prefix[focal.knot]
    read = {"held": len(held), "inherited_shared": sum(len(owners(new_prefix)[m]) == 2 for m in held)}
    read["own_singly_held"] = read["held"] - read["inherited_shared"]
    assert read == final_read
    return {"global_distinction_renaming": f"new_id={high}-old_id", "anonymous_read": read,
            "H_inherited_and_fresh_roles_transported": held,
            "H_transported_fresh_owners_final": {rename[mark]: new_owners[rename[mark]] for mark in focal.fresh},
            "reapplied_raw_identifier_sort": False}


def payment_path(history, ancestor, target):
    births = {row.knot: row for rows in history.cohorts.values() for row in rows}
    remaining = deque([(target, [])])
    seen = {target}
    while remaining:
        child, path = remaining.popleft()
        if child == ancestor:
            return list(reversed(path))
        if child in births:
            row = births[child]
            for payer, mark in zip(row.parents, row.paid, strict=True):
                if payer not in seen:
                    seen.add(payer)
                    remaining.append((payer, [*path, {"payer": payer, "recipient": child, "distinction": mark}]))
    return None


def allocations(law, history, focal, slots, added, local_read):
    prefix = launch_world(law, history.source)
    prefix_log = {"1": values(prefix)}
    for size in range(2, 9):
        prefix, holdings = materialize(law, prefix, history.stages[size - 1], history.cohorts[size])
        assert holdings == history.stages[size]
        prefix_log[str(size)] = values(prefix)
    assert len({prefix[i] for i in focal.fresh}) == 1
    rows = history.cohorts[9]
    old = history.stages[8]
    before = owners(old)
    primary = tuple(b.paid[b.parents.index(focal.knot)] for b in slots)
    original_world, original_holdings = materialize(law, prefix, old, rows)
    assert original_holdings == history.stages[9]
    main_owners = owners(original_holdings)
    all_alternatives = []
    for assignment in permutations(focal.fresh):
        changed = reallocated(rows, focal, slots, assignment)
        assert [(r.knot, r.parents, r.fresh, r.demand) for r in changed] == [
            (r.knot, r.parents, r.fresh, r.demand) for r in rows]
        new_world, new_holdings = materialize(law, prefix, old, changed)
        assert new_holdings[:len(old)] == old
        assert new_world == original_world
        current_owners = owners(new_holdings)
        changes = [mark for mark in before if current_owners[mark] != main_owners[mark]]
        assert set(changes) <= set(focal.fresh)
        assert bool(changes) == (assignment != primary)
        all_alternatives.append({"sham": assignment == primary,
                                 "H_to_size_nine_child": {r.knot: m for r, m in zip(slots, assignment, strict=True)},
                                 "changed_real_coholdings": {m: (main_owners[m], current_owners[m]) for m in changes},
                                 "size_nine_births": len(rows), "both_pure_opportunities_preserved": True,
                                 "complete_size_nine_value_word": values(new_world),
                                 "replay_size_eight_prefix_pointwise_fixed": True})
    special = added.knot if added is not None else slots[0].knot
    reordered = sorted(rows, key=lambda r: r.knot != special)
    first_world, first_holdings = materialize(law, prefix, old, reordered)
    last_world, last_holdings = materialize(law, prefix, old, reversed(reordered))
    assert first_world == last_world == original_world and first_holdings == last_holdings == original_holdings
    assert len(all_alternatives) in (2, 6) and sum(r["sham"] for r in all_alternatives) == 1
    if added is not None:
        original_mark = added.paid[added.parents.index(focal.knot)]
        assert any(row["H_to_size_nine_child"][special] != original_mark for row in all_alternatives)
    return {"fixed_lawful_value_word_each_size_before_change": prefix_log,
            "order_of_bits_in_each_word": "ascending physical distinction ID, starting with zero",
            "common_value_on_H_fresh_distinctions": prefix[focal.fresh[0]],
            "all_actual_allocation_bijections": all_alternatives,
            "coherent_naming_sham": coherent_control(law, original_world, original_holdings, old, focal, local_read),
            "fixed_plan_order_control": {"same_completed_cut": True, "tested_recipient": special,
                                         "first_write_order": [r.knot for r in reordered],
                                         "last_write_order": [r.knot for r in reversed(reordered)]}}


def report_law(law, archived):
    sources = [tuple(map(tuple, source)) for source in archived["sources"]]
    plain, loaded = sources
    extra = archived["edit"]["new_distinction"]
    assert archived["edit"]["holders"] == [EDIT_HOLDER]
    assert all(new == ((*old, extra) if i == EDIT_HOLDER else old)
               for i, (old, new) in enumerate(zip(plain, loaded, strict=True)))
    assert all(launch_world(law, loaded)[mark] == bit for mark, bit in launch_world(law, plain).items())
    fixed_roles = {}
    histories = [replay(source, law, fixed_roles) for source in sources]
    indices = [archived_shapes(h, loaded=bool(i)) for i, h in enumerate(histories)]
    matches, focused, new_joint = match_and_select(archived, histories, indices)
    assert focused[1].knot in new_joint.parents
    common_recipient_roles = set()
    report = {"cross_history_matches": matches, "arms": {}}
    for i, (history, focal, lookup) in enumerate(zip(histories, focused, indices, strict=True)):
        forecasts, slots = h_forecast(history, focal)
        local = local_holding(history, focal)
        arm_added = new_joint if i else None
        common_roles = {history.roles[b.knot] for b in slots if b != arm_added}
        if i:
            assert common_recipient_roles == common_roles
        else:
            common_recipient_roles = common_roles
        report["arms"]["loaded" if i else "plain"] = {
            "H_birth": described_birth(history, 8, focal, lookup), "H_local_holding_and_actual_owners": local,
            "H_eligible_roster_and_funding": forecasts, "both_pure_opportunities": pure_opportunities(history),
            "size_eight_roster": [described_birth(history, 8, b, lookup) for b in history.cohorts[8]],
            "size_nine_roster": [described_birth(history, 9, b, lookup) for b in history.cohorts[9]],
            "allocation_controls": allocations(law, history, focal, slots, arm_added, local["name_free_read_at_birth"]),
            "one_short_diagnostic": deficient_control(law, history, focal),
        }
    report["two_common_H_recipient_roles"] = sorted(common_recipient_roles)
    report["differing_size_nine_common_descendant"] = described_birth(histories[1], 9, new_joint, indices[1])
    payers_without_H = tuple(p for p in new_joint.parents if p != focused[1].knot)
    assert payers_without_H not in histories[1].multiple_groups[9]
    assert len(common_recipient_roles) == 2
    report["whole_H_payment_interruption"] = {
        "differing_group_is_required_by_frozen_witness_data": new_joint.parents in histories[1].multiple_groups[9],
        "H_supply_fully_spent_in_required_groups": True, "ordinary_selective_null_found": False,
        "other_two_payers_have_separate_group_without_H": False,
        "omitting_H_slot_leaves_one_of_its_distinctions_unspent": True,
    }
    edit_owners = {size: owners(stars)[extra] for size, stars in histories[1].stages.items()}
    assert edit_owners[1] == (EDIT_HOLDER,)
    assert len(edit_owners[2]) == 2 and all(held == edit_owners[2] for size, held in edit_owners.items() if size >= 2)
    first_spare_spender, = (b for b in histories[1].cohorts[2] if extra in b.paid)
    assert first_spare_spender.parents == (EDIT_HOLDER,) and extra not in new_joint.paid
    older_witness = witnessed_payment_group(histories[1].cohorts[8], payers_without_H)
    joined_through_spare, = older_witness["one_older_holder_witnesses_the_whole_group"]
    affected_destinations = (*payers_without_H, joined_through_spare)
    paths = {k: payment_path(histories[1], first_spare_spender.knot, k) for k in affected_destinations}
    assert all(paths.values())
    report["source_edit"] = {"initial_loose_distinction": extra, "its_owners_by_size": edit_owners,
                             "its_actual_size_two_recipient": asdict(first_spare_spender),
                             "actual_paths_from_spare_recipient_to_other_payers_and_their_older_witness": paths,
                             "source_X4_payments_plain_then_loaded": [
                                 [asdict(b) for b in h.cohorts[2] if EDIT_HOLDER in b.parents] for h in histories]}
    trace = {name: {"source": h.source, "cohorts": {size: [asdict(b) for b in rows] for size, rows in h.cohorts.items()}}
             for name, h in zip(("plain", "loaded"), histories, strict=True)}
    return report, trace


def main():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_HASH
    archive = json.loads(ARCHIVE.read_text())["both_laws"]
    results, traces = {}, {}
    for law in LAWS:
        results[law], traces[law] = report_law(law, archive[law]["near_right_spare"])
    assert traces["parity"] == traces["nae"]
    report = {"schema": "spare-and-next-payment-physical-v1",
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in (DESIGN, ARCHIVE, OPERATOR)}, "laws": results}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "results.json").write_text(json.dumps(report, sort_keys=True, indent=2) + "\n")
    packed = json.dumps(traces, sort_keys=True, separators=(",", ":")).encode()
    (OUTPUT / "physical_trace.json.gz").write_bytes(compress(packed, mtime=0))
    print(OUTPUT)


if __name__ == "__main__":
    main()
