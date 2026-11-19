"""Exact formation quotients before and after one output of the fourth site is used."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import permutations, product
import json
from math import prod
from pathlib import Path
import sys
from tempfile import TemporaryDirectory

PROOFS = Path(__file__).resolve().parents[2]
N_PATH, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001N").glob("*/frontier.py")
sys.path.insert(0, str(N_PATH.parent))
from table_tools import module

N = module(N_PATH, "bdf89c6d2fe4873c17d90e7d786f4c84329a971776ed8789f97384b3ca0ad4aa",
           "one_spent_output_predecessor")
sys.path.pop(0)
J, OLD, T = N.J, N.OLD, N.T
OTHER = -1
ROLE_NAMES = ("fourth_holder", "fourth_pair_witness", "child_holder", "child_pair_witness", "neither_direct")


@dataclass(frozen=True, slots=True)
class TaggedFrontier:
    frontier: OLD.Frontier
    fourth: int
    child: int
    retired_child: int
    reserved: int


@lru_cache(maxsize=150_000)
def normalize(frontier, fourth, child, retired_child, reserved):
    profiles = []
    for i, loose in enumerate(frontier.loose):
        retired_sizes = sorted(m.bit_count() for m in frontier.retired if m & (1 << i))
        profiles.append((loose, i == fourth, i == child, i == reserved, bool(retired_child & (1 << i)),
                         frontier.adjacent[i].bit_count(), tuple(retired_sizes)))
    classes = [tuple(i for i, profile in enumerate(profiles) if profile == kind)
               for kind in sorted(set(profiles))]
    best = min(
        (frontier.restrict(order), OLD.project(retired_child, order), order)
        for ranges in product(*(permutations(group) for group in classes))
        for order in [sum(ranges, ())]
    )
    front, retired, order = best
    at = {i: n for n, i in enumerate(order)}
    return TaggedFrontier(front, at.get(fourth, OTHER), at.get(child, OTHER),
                          retired, at.get(reserved, OTHER)), order


@lru_cache(maxsize=150_000)
def transition(state, parents, fourth_birth=False):
    front = state.frontier
    unborn = len(front.loose)
    loose = tuple(count - (i in parents) for i, count in enumerate(front.loose))
    adj = tuple(mask | ((1 << unborn) if i in parents else 0) for i, mask in enumerate(front.adjacent))
    retired = (*front.retired, *(adj[i] for i, count in enumerate(loose) if count == 0))
    keep = (*tuple(i for i, count in enumerate(loose) if count), unborn)
    outputs = 3 if fourth_birth else 2
    enlarged = OLD.Frontier((*loose, outputs), (*adj, OLD.mask(parents)), retired)
    fourth = unborn if fourth_birth else state.fourth
    child, child_row = state.child, state.retired_child
    if not fourth_birth and fourth in parents:
        assert front.loose[fourth] == 3 and child == OTHER and child_row == 0
        child = unborn
    if child != OTHER and child not in keep:
        child_row, child = adj[child], OTHER
    sub = enlarged.restrict(keep)
    assert fourth in keep and (state.reserved == OTHER or state.reserved in keep)
    at = {i: n for n, i in enumerate(keep)}
    nxt, order = normalize(sub, at[fourth], at.get(child, OTHER), OLD.project(child_row, keep),
                           at.get(state.reserved, OTHER))
    return nxt, tuple(keep[i] for i in order)


def advance(state, parents, fourth_birth=False):
    return transition(state, parents, fourth_birth)[0]


def snapshot(rows, fourth, child=OTHER, reserved=OTHER):
    front, names, loose = J.literal_snapshot(rows)
    at = {i: n for n, i in enumerate(names)}
    child_row = 0
    if child != OTHER and child not in at:
        neighbors = T.incidence(rows)[1][child]
        child_row = OLD.mask(i for i, live in enumerate(names) if live in neighbors)
    tagged, order = normalize(front, at[fourth], at.get(child, OTHER), child_row, at.get(reserved, OTHER))
    return tagged, tuple(names[i] for i in order), loose


@lru_cache(maxsize=150_000)
def choices(front):
    groups = tuple(p for p in OLD.possible_parents(front) if len(p) >= 2)
    return groups, tuple(p for p in groups if len(p) == 3)


@lru_cache(maxsize=100_000)
def menu_roles(state):
    front = state.frontier
    fourth_row = front.adjacent[state.fourth]
    child_row = state.retired_child if state.child == OTHER else front.adjacent[state.child]
    counts = Counter()
    for group in choices(front)[1]:
        mask = OLD.mask(group)
        mult = prod(front.loose[i] for i in group)
        direct = (state.fourth in group, (fourth_row & mask).bit_count() >= 2,
                  state.child in group, (child_row & mask).bit_count() >= 2)
        counts["legal_triples"] += mult
        for role, present in zip(ROLE_NAMES, (*direct, not any(direct)), strict=True):
            if present:
                counts[role] += mult
        if not (mask & (fourth_row | child_row)) and not any(direct):
            counts["nonadjacent_to_both"] += mult
    return counts


def remaining_choices(state, parents):
    # All old witnesses remain. The newborn forbids an old legal group
    # exactly when it meets all three of its holders.
    front = state.frontier
    return tuple((group, n) for group in choices(front)[1] if group != parents
                 if (n := prod(front.loose[i] - (i in parents) for i in group)))


def continuations_keeping_a_triple(next_state, order, persistent):
    # This one-step test also decides whether any longer continuation can
    # preserve a previously legal named mark: a lost mark cannot return.
    front = next_state.frontier
    after = tuple(tuple(sorted(order.index(i) for i in p)) for p, _ in persistent)
    for suffix in choices(front)[0]:
        if next_state.fourth in suffix or next_state.reserved in suffix:
            continue
        if any(p != suffix and all(front.loose[i] > (i in suffix) for i in p) for p in after):
            yield suffix


@dataclass(frozen=True, slots=True)
class Sample:
    previous: tuple
    move: tuple
    size: int
    following: tuple


def offer(best, key, previous, move, sites, following=()):
    if key not in best or sites < best[key].size:
        best[key] = Sample(previous, move, sites, following)


def all_starts(prior):
    _, _, depth, _ = prior
    buckets = defaultdict(dict)
    sources = {}
    bindings = Counter()
    for node, sites in depth.items():
        third, front = node
        if third == 0:
            continue
        old = TaggedFrontier(front, OTHER, OTHER, 0, OTHER)
        for parents in choices(front)[1]:
            state = advance(old, parents, fourth_birth=True)
            key = third, 0, state
            bindings[third] += 1
            if key not in sources:
                buckets[sites + 1][key] = (node, parents)
                sources[key] = sites + 1
            else:
                assert sources[key] <= sites + 1
    return buckets, dict(sorted(bindings.items()))


def initial_fixed(rows, fourth, reserved):
    state = snapshot(rows, fourth, reserved=reserved)[0]
    third = next(len(step["consumes"]) for step in T.replay(rows)[1:]
                 if len(step["fresh"]) == 3 and step["site"] not in (1, 2, fourth))
    return {len(rows): {(third, 0, state): (rows, fourth)}}


def measure_roles(stats, best, stage, third, arity, roles, node, parents, sites):
    rollup = stats[stage, third, arity]
    rollup["with_menu"] += bool(roles)
    for name, amount in roles.items():
        rollup["total_" + name] += amount
        rollup["with_" + name] += 1
        offer(best, (stage, third, arity, name), node, parents, sites)


def closure(buckets):
    incoming = {}
    linked = {}
    sizes = {}
    immediate_records = set()
    later_records = set()
    frontier_sizes = Counter()
    moves = Counter()
    patterns = Counter()
    live_by_shrinks = Counter()
    top = Counter()
    role_totals = defaultdict(Counter)
    best = {}
    level = min(buckets)
    last_base = max(buckets)
    current = []
    while level <= last_base or current:
        for node, seed in buckets.get(level, {}).items():
            if node not in sizes:
                sizes[node] = level
                incoming[node] = seed
                current.append(node)
        upcoming = []
        for node in current:
            assert sizes[node] == level
            third, arity, state = node
            front = state.frontier
            assert front.loose[state.fourth] == (2 if arity else 3)
            assert sum(front.loose) <= 10 - third
            frontier_sizes[third, arity, sum(front.loose)] += 1
            pre = menu_roles(state) if not arity else None
            for parents in choices(front)[0]:
                if state.reserved in parents or arity and state.fourth in parents:
                    continue
                next_state, order = transition(state, parents)
                next_arity = arity or (len(parents) if state.fourth in parents else 0)
                target = third, next_arity, next_state
                moves[third, arity, next_arity, len(parents)] += 1
                if target not in sizes:
                    sizes[target] = level + 1
                    linked[target] = node, parents
                    upcoming.append(target)
                if not next_arity:
                    continue
                if not arity:
                    immediate_records.add(target)
                    post = menu_roles(next_state)
                    persistent = remaining_choices(state, parents)
                    common = sum(n for _, n in persistent)
                    system = third, next_arity
                    patterns[(*system, bool(pre), bool(post), bool(common))] += 1
                    named = prod(front.loose[i] for i in parents)
                    top[(*system, "named_spending_choices")] += named
                    top[(*system, "spending_choice_and_survivor_pairs")] += named * common
                    offer(best, ("first_event", *system, f"{int(bool(pre))}{int(bool(post))}{int(bool(common))}"),
                          node, parents, level + 1)
                    measure_roles(role_totals, best, "before", *system, pre, node, parents, level)
                    measure_roles(role_totals, best, "after", *system, post, node, parents, level + 1)
                    shrinks = 10 - third - sum(front.loose)
                    if pre:
                        live_by_shrinks["before", *system, shrinks] += 1
                    if post:
                        live_by_shrinks["after", *system, shrinks + (next_arity == 3)] += 1
                    if common:
                        offer(best, ("first_event", *system, "same_triple"), node, parents, level + 1)
                        preserving = tuple(continuations_keeping_a_triple(next_state, order, persistent))
                        if preserving:
                            top[(*system, "spend_groups_with_preserving_continuation")] += 1
                            offer(best, ("through_later", *system, "same_triple"),
                                  node, parents, level + 2, preserving[0])
                elif target not in later_records:
                    later_records.add(target)
                    pattern = "later", third, arity
                    role_totals[pattern]["unique_records"] += 1
                    roles = menu_roles(next_state)
                    measure_roles(role_totals, best, *pattern, roles, node, parents, level + 1)
                    if roles:
                        shrinks = 10 - third - sum(next_state.frontier.loose)
                        live_by_shrinks[*pattern, shrinks] += 1
                        if arity == 3 and shrinks == 1:
                            c = next_state.child
                            used = 2 if c == OTHER else 2 - next_state.frontier.loose[c]
                            offer(best, ("sole_child_shrink", third, arity, str(used)), node, parents, level + 1)
        current = upcoming
        level += 1
    distinct_positive = defaultdict(Counter)
    for node in sizes:
        third, arity, state = node
        if arity and menu_roles(state):
            first, later = node in immediate_records, node in later_records
            assert first or later
            count = distinct_positive[third, arity, 10 - third - sum(state.frontier.loose)]
            count["immediate"] += first
            count["later"] += later
            count["both"] += first and later
            count["union"] += 1
    return {
        "frontier_sizes": frontier_sizes, "moves": moves, "role_totals": role_totals,
        "patterns": patterns, "positive_by_shrinks": live_by_shrinks, "totals": top, "best": best, "linked": linked,
        "roots": incoming, "distinct_positive": distinct_positive, "maximum_representative_sites": max(sizes.values()),
    }


def replay(sample, result, prior=None, reserve=OTHER):
    # The sample's final transition is kept even when the successor also has
    # a shorter proof through a different spending event.
    chain_back = [(sample.previous, sample.move)]
    node = sample.previous
    if sample.following:
        target = node[0], len(sample.move), advance(node[2], sample.move)
        chain_back.insert(0, (target, sample.following))
    while node in result["linked"]:
        previous, move = result["linked"][node]
        chain_back.append((previous, move))
        node = previous
    data, chosen = result["roots"][node]
    if prior is None:
        rows, fourth = data, chosen
    else:
        roots, trace, depth, _ = prior
        prefix = N.literal(data, roots, trace, depth)
        _, names, _ = J.literal_snapshot(prefix)
        rows = J.advance(prefix, tuple(names[i] for i in chosen), 3)
        fourth = len(prefix)
    child = OTHER
    for (third, arity, state), parents in reversed(chain_back):
        observed, names, slots = snapshot(rows, fourth, child, reserve)
        assert observed == state
        assert parents in OLD.verify_literal_moves(rows, state.frontier, names, slots)
        if state.fourth in parents:
            assert child == OTHER
            child = len(rows)
        expected = advance(state, parents)
        rows = J.advance(rows, tuple(names[i] for i in parents), 2)
        assert snapshot(rows, fourth, child, reserve)[0] == expected
    assert child != OTHER and fourth < child and len(rows) in (sample.size, sample.size + 1)
    events = T.replay(rows)
    high_outputs = events[fourth]["fresh"]
    assert len(high_outputs) == len(events[fourth]["consumes"]) == 3
    assert len(set(high_outputs) & set(events[child]["consumes"])) == 1
    users, _ = T.incidence(rows)
    assert sum(len(users[x]) == 1 for x in high_outputs) == 2
    assert tuple(i for i, event in enumerate(events[1:], 1) if len(event["fresh"]) == 3)[-1] == fourth
    if reserve != OTHER:
        assert len(J.literal_snapshot(rows)[2][reserve]) == 1
    return rows, fourth, child


def describe(rows, fourth, child, reserve=OTHER):
    before, after, current = rows[:child], rows[:child + 1], rows
    pre, post, now = (N.checked_menu(p) for p in (before, after, current))
    for body, c, menu in ((before, OTHER, pre), (after, child, post), (current, child, now)):
        abstract = menu_roles(snapshot(body, fourth, c, reserve)[0])
        assert len(menu) == abstract["legal_triples"]
        involved = set()
        for i, site in enumerate((fourth, c)):
            if site == OTHER:
                continue
            named = T.roles(body, site, menu)
            for role in ("holder", "pair_witness"):
                hits = {entry for entry, val in named.items() if role in val["roles"]}
                involved.update(hits)
                assert len(hits) == abstract[ROLE_NAMES[2 * i + (role == "pair_witness")]]
        assert len(set(menu) - involved) == abstract["neither_direct"]
    actual_spending = tuple(sorted(set(rows[fourth]) & set(rows[child])))
    assert len(actual_spending) == 1
    state, names, _ = snapshot(before, fourth, reserved=reserve)
    old_owners, _ = T.incidence(before)
    parents = tuple(sorted(names.index(old_owners[b][0]) for b in rows[child] if b in old_owners))
    assert sum(n for _, n in remaining_choices(state, parents)) == len(pre.keys() & post.keys())
    events = T.replay(rows)
    third, = tuple(step["site"] for step in events[3:fourth] if len(step["fresh"]) == 3)
    shrinking_steps = tuple(step["site"] for step in events
                            if len(step["consumes"]) == 3 and len(step["fresh"]) == 2)
    owners, _ = T.incidence(rows)
    used_child_outputs = tuple(b for b in events[child]["fresh"] if len(owners[b]) == 2)
    return {
        "width": T.width(rows), "junction_supports": rows, "third_site": third,
        "fourth_site": fourth, "spending_child": child, "shrinking_sites": shrinking_steps,
        "spent_spending_child_outputs": used_child_outputs,
        "spent_fourth_bit": actual_spending[0],
        "before_spending": sorted(pre), "immediately_after_spending": sorted(post), "current": sorted(now),
        "same_named_before_and_after": sorted(pre.keys() & post.keys()),
        "same_named_before_and_current": sorted(pre.keys() & now.keys()),
        "fourth_current_roles": sorted(T.roles(rows, fourth, now).items()),
        "child_current_roles": sorted(T.roles(rows, child, now).items()),
    }


def record_examples(result, prior=None, reserve=OTHER):
    samples = []
    report_index = {}
    for key, sample in sorted(result["best"].items()):
        rows, fourth, child = replay(sample, result, prior, reserve)
        fixture_key = rows, fourth, child
        if fixture_key not in report_index:
            report_index[fixture_key] = len(samples)
            samples.append(describe(rows, fourth, child, reserve))
        index = report_index[fixture_key]
        record = samples[index]
        label, third, arity, detail = key
        if label == "first_event":
            bits = [bool(record[field]) for field in (
                "before_spending", "immediately_after_spending", "same_named_before_and_after")]
            if detail == "same_triple":
                assert bits[-1]
            else:
                assert detail == "".join(str(int(b)) for b in bits)
        if label in ("later", "through_later", "sole_child_shrink"):
            assert child < len(rows) - 1
        if label == "through_later":
            assert record["same_named_before_and_current"]
        if label == "sole_child_shrink":
            assert record["shrinking_sites"] == (child,)
            assert int(detail) == len(record["spent_spending_child_outputs"])
        record.setdefault("minimum_cases", []).append({
            "stage": label, "third_parent_count": third, "spending_parent_count": arity,
            "case": detail, "stage_width": 2 * sample.size + 5,
        })
    return samples


def summarize(result, examples):
    return {
        "frontier_counts": [
            {"third_parents": third, "spending_parents": spend, "loose": loose, "states": count}
            for (third, spend, loose), count in sorted(result["frontier_sizes"].items())
        ],
        "transition_counts": [
            {"third_parents": third, "spending_parents_before": before, "spending_parents_after": after,
             "move_parents": move, "transitions": count}
            for (third, before, after, move), count in sorted(result["moves"].items())
        ],
        "first_spend_menu_patterns": [
            {"third_parents": third, "spending_parents": spend, "before": pre, "after": post,
             "actual_common_triple": common, "spending_groups": count}
            for (third, spend, pre, post, common), count in sorted(result["patterns"].items())
        ],
        "first_spend_named_counts": [
            {"third_parents": third, "spending_parents": spend, "quantity": label, "count": n}
            for (third, spend, label), n in sorted(result["totals"].items())
        ],
        "positive_by_shrinks": [
            {"stage": stage, "third_parents": third, "spending_parents": spend, "shrinks": shrinks, "count": count}
            for (stage, third, spend, shrinks), count in sorted(result["positive_by_shrinks"].items())
        ],
        "distinct_positive_final_records": [
            {"third_parents": third, "spending_parents": spend, "shrinks": shrinks, **counts}
            for (third, spend, shrinks), counts in sorted(result["distinct_positive"].items())
        ],
        "role_counts": [
            {"stage": stage, "third_parents": third, "spending_parents": spend, **tally}
            for (stage, third, spend), tally in sorted(result["role_totals"].items())
        ],
        "maximum_representative_sites": result["maximum_representative_sites"],
        "minimum_literal_examples": examples,
    }


def fixed_pair():
    left = (*N.WITNESS_PREFIX, (15, 23, 26, 28, 29, 30))
    right = (*N.WITNESS_PREFIX, (15, 23, 27, 28, 29, 30))
    fourth = len(N.WITNESS_PREFIX)
    results = {}
    for tag, reserved in (("one_history", OTHER), ("common_named_histories", 11)):
        starts = initial_fixed(left, fourth, reserved)
        assert tuple(starts[len(left)]) == tuple(initial_fixed(right, fourth, reserved)[len(right)])
        exact = closure(starts)
        examples = record_examples(exact, reserve=reserved)
        paired = []
        for example in examples:
            rows = example["junction_supports"]
            mapped = tuple(tuple(27 if x == 26 else 26 if x == 27 else x for x in row) for row in rows)
            suffix = rows[len(left):] if reserved != OTHER else mapped[len(left):]
            rival = (*right, *suffix)
            assert tuple(map(sorted, mapped)) == tuple(map(sorted, rival))
            picked = describe(rival, example["fourth_site"], example["spending_child"], reserved)
            paired.append({"left_example": len(paired), "right_current": picked["current"],
                           "right_same_named_before_and_current": picked["same_named_before_and_current"]})
        results[tag] = {**summarize(exact, examples), "right_literal_controls": paired}
    return results


def positive_scalar_control(binary, examples):
    example = min((e for e in examples if e["current"]), key=lambda e: e["width"])
    rows = example["junction_supports"]
    table, = T.all_tables(binary, (rows,))
    N.verify_parity_pairs(rows, table)
    return {
        "width": len(table), "full_K_upper_triangle_hex": T.table_upper(table).hex(),
        "junction_supports": rows, "actual_legal_triples": example["current"],
        "checkers": ["connected cuts", "support-minimal parity words"],
    }


def nonshrinking_pump(examples):
    example = next(entry for entry in examples if any(
        case["stage"] == "after" and case["case"] == "fourth_holder" and case["spending_parent_count"] == 2
        and case["third_parent_count"] == 1 for case in entry["minimum_cases"]))
    fourth, child = example["fourth_site"], example["spending_child"]
    preparation = ((11, 23, 25, 26), (17, 24, 27, 28), (25, 27, 29, 30), (26, 28, 31, 32))
    rows = (*example["junction_supports"], *preparation)
    start, names, _ = snapshot(rows, fourth, child)
    mark = (15, 19, 21)
    pair = (1, 2)
    moving_mask = OLD.mask(pair)
    assert T.width(rows) == 33 and mark in N.checked_menu(rows)
    assert (start.frontier.loose[1], start.frontier.loose[2]) == (2, 2)
    assert not any(start.frontier.adjacent[i] for i in pair)
    assert {m for m in start.frontier.retired if m & moving_mask} == {moving_mask}
    assert start.fourth not in pair and start.retired_child & moving_mask == 0 and start.child == OTHER
    fixed_holders = tuple(names[i] for i in (0, 3, 4))
    start_rows = rows
    rounds = []
    for _ in range(2):
        _, current_names, _ = snapshot(rows, fourth, child)
        selected = tuple(current_names[i] for i in pair)
        old_rows = rows
        for _ in range(2):
            rows = J.advance(rows, selected, 2)
            assert mark in N.checked_menu(rows)
        back, names, _ = snapshot(rows, fourth, child)
        assert back == start and tuple(names[i] for i in (0, 3, 4)) == fixed_holders
        rounds.append(rows[len(old_rows):])
    assert all(len(e["consumes"]) != 3 or len(e["fresh"]) != 2 for e in T.replay(rows))
    assert describe(rows, fourth, child)["current"] == describe(start_rows, fourth, child)["current"]
    return {
        "initial_junction_supports": start_rows, "initial_width": 33, "retained_mark": mark, "fourth_site": fourth,
        "spending_child": child, "moving_live_holders_at_start": pair, "width_increment": 4,
        "projected_frontier": {
            "loose_counts": start.frontier.loose, "adjacency": start.frontier.adjacent,
            "retired_neighborhoods": start.frontier.retired, "fourth_holder": start.fourth,
            "spending_child_retired_neighborhood": start.retired_child,
        },
        "two_literal_repetitions": rounds,
    }


def run(binary):
    prior = N.close_prefixes()
    roots, bindings = all_starts(prior)
    result = closure(roots)
    examples = record_examples(result, prior)
    return {
        "predecessor_fourth_birth_groups": bindings,
        **summarize(result, examples),
        "width_31_pair_continuations": fixed_pair(),
        "positive_scalar_control": positive_scalar_control(binary, examples),
        "nonshrinking_pump": nonshrinking_pump(examples),
    }


if __name__ == "__main__":
    with TemporaryDirectory(prefix="one-spent-output-") as work:
        binary = T.compiler(Path(work) / "bond_table")
        print(json.dumps(run(binary), indent=2))
