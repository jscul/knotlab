"""Rebuild the ordinary-growth incidence census from its frozen start roster.

Every reported lift is an unsigned permutation of distinctions. Equivalence
classes of lifts under relabelling within holder classes are counted exactly.
Initial distinction identities are retained for tracing across the first round.
"""

import argparse
from collections import Counter, defaultdict, deque
from functools import cache, lru_cache
import gzip
from itertools import permutations, product
from math import factorial
from pathlib import Path
import json
import random
import resource
import runpy
from time import monotonic


HERE = Path(__file__).resolve().parent
SOURCE = HERE.parents[1] / "FORBID-EDITS-20261126-001" / "forbid.py"
LAWS = ("parity", "nae")
SAMPLE_SEED = 2026112601
SAMPLE_SIZE = 100
DESIGNATED = 3097


def holder_classes(supports):
    holders = defaultdict(list)
    for knot, support in enumerate(supports):
        assert len(set(support)) == len(support)
        for distinction in support:
            holders[distinction].append(knot)
    assert set(holders) == set(range(len(holders)))
    classes = defaultdict(list)
    for distinction in sorted(holders):
        key = tuple(holders[distinction])
        assert 1 <= len(key) <= 2
        classes[key].append(distinction)
    return dict(sorted((key, tuple(group)) for key, group in classes.items()))


def knot_profiles(classes, knot_count):
    multiplicity = [[0] * knot_count for _ in range(knot_count)]
    for owners, group in classes.items():
        first, last = owners[0], owners[-1]
        multiplicity[first][last] = multiplicity[last][first] = len(group)

    labels = [0] * knot_count
    while True:
        profiles = [
            (labels[k], multiplicity[k][k],
             tuple(sorted((labels[j], value) for j, value in enumerate(row) if j != k)))
            for k, row in enumerate(multiplicity)
        ]
        name = {profile: i for i, profile in enumerate(sorted(set(profiles)))}
        refined = [name[profile] for profile in profiles]
        if refined == labels:
            break
        labels = refined

    return multiplicity, labels


def knot_involutions(classes, knot_count):
    multiplicity, labels = knot_profiles(classes, knot_count)

    def extend(mapping, unassigned):
        if not unassigned:
            if any(k != image for k, image in enumerate(mapping)):
                yield mapping
            return
        first = min(unassigned, key=lambda k: (labels.count(labels[k]), k))
        assigned = [k for k, image in enumerate(mapping) if image != -1]
        for other in sorted(unassigned):
            if labels[first] != labels[other]:
                continue
            if any(multiplicity[first][k] != multiplicity[other][mapping[k]] for k in assigned):
                continue
            extended = list(mapping)
            extended[first], extended[other] = other, first
            yield from extend(tuple(extended), unassigned - {first, other})

    yield from extend((-1,) * knot_count, set(range(knot_count)))


def knot_automorphisms(classes, knot_count):
    multiplicity, labels = knot_profiles(classes, knot_count)
    order = sorted(range(knot_count), key=lambda k: (labels.count(labels[k]), k))
    mapping = [-1] * knot_count

    def extend(assigned, remaining):
        if assigned == knot_count:
            yield tuple(mapping)
            return
        knot = order[assigned]
        for image in sorted(remaining):
            if labels[knot] != labels[image]:
                continue
            if any(multiplicity[knot][k] != multiplicity[image][mapping[k]] for k in order[:assigned]):
                continue
            mapping[knot] = image
            yield from extend(assigned + 1, remaining - {image})

    yield from extend(0, set(range(knot_count)))


def explicit_involutions(group):
    if not group:
        yield ()
        return
    first, *rest = group
    for tail in explicit_involutions(rest):
        yield ((first, first),) + tail
    for other in rest:
        for tail in explicit_involutions([d for d in rest if d != other]):
            yield ((first, other), (other, first)) + tail


def distinction_lifts(classes, knots, old_distinctions):
    options = []
    for owners, group in classes.items():
        target_owners = tuple(sorted(knots[k] for k in owners))
        if target_owners < owners:
            continue
        target_group = classes[target_owners]
        assert len(group) == len(target_group)
        retain_names = min(group + target_group) < old_distinctions
        if retain_names:
            assert max(group + target_group) < old_distinctions
        count = len(group)
        if owners != target_owners:
            images = permutations(target_group) if retain_names else (target_group,)
            weight = 1 if retain_names else factorial(count)
            options.append([
                (tuple(zip(group, image)) + tuple(zip(image, group)), weight)
                for image in images
            ])
        elif retain_names:
            options.append([(pairs, 1) for pairs in explicit_involutions(group)])
        else:
            choices = []
            for swapped in range(count // 2 + 1):
                image = list(group)
                for i in range(0, 2 * swapped, 2):
                    image[i], image[i + 1] = image[i + 1], image[i]
                weight = factorial(count) // (factorial(count - 2 * swapped) * 2**swapped * factorial(swapped))
                choices.append((tuple(zip(group, image)), weight))
            options.append(choices)

    for selection in product(*options):
        disposition = [-1] * sum(map(len, classes.values()))
        multiplicity = 1
        for pairs, weight in selection:
            multiplicity *= weight
            for distinction, image in pairs:
                disposition[distinction] = image
        assert all(image >= 0 and disposition[image] == d for d, image in enumerate(disposition))
        yield tuple(disposition), multiplicity


def ordered_lift(classes, knots, maximal=False):
    ordered = [-1] * sum(map(len, classes.values()))
    for owners, group in classes.items():
        target = tuple(sorted(knots[k] for k in owners))
        images = classes[target]
        if maximal and owners == target:
            images = list(images)
            for i in range(0, len(images) - 1, 2):
                images[i], images[i + 1] = images[i + 1], images[i]
        for distinction, image in zip(group, images, strict=True):
            ordered[distinction] = image
    return tuple(ordered)


def distinction_orbits(action):
    labels = {}
    columns = []
    higher = []
    for d, image in enumerate(action):
        representative = min(d, image)
        column = labels.setdefault(representative, len(labels))
        columns.append(1 << column)
        higher.append(d != representative)
    return tuple(columns), tuple(higher), len(labels)


def parity_count(supports, columns, negative, width):
    rows = {}
    for support in supports:
        mask = 0
        rhs = False
        for d in support:
            mask ^= columns[d]
            rhs ^= negative[d]
        while mask and (leading := mask.bit_length()) in rows:
            stored_mask, stored_rhs = rows[leading]
            mask ^= stored_mask
            rhs ^= stored_rhs
        if mask:
            rows[mask.bit_length()] = mask, rhs
        elif rhs:
            return 0
    return 1 << (width - len(rows))


@lru_cache(maxsize=2048)
def count_cnf(clauses, width):
    """Exact count by Shannon expansion, with units and free variables."""

    @cache
    def solve(rows):
        if not rows:
            return 1
        occurrences = Counter()
        active = 0
        unit = None
        for positive, negative in rows:
            mask = positive | negative
            active |= mask
            if mask == 0:
                return 0
            if mask.bit_count() == 1:
                unit = (mask, bool(positive))
                break
            while mask:
                bit = mask & -mask
                occurrences[bit] += 1
                mask ^= bit

        if unit is not None:
            bit, value = unit
            active = 0
            for positive, negative in rows:
                active |= positive | negative
            choices = (value,)
        else:
            bit = max(occurrences, key=lambda x: (occurrences[x], -x))
            choices = (False, True)

        count = 0
        for value in choices:
            remaining = set()
            used = 0
            for positive, negative in rows:
                if (positive if value else negative) & bit:
                    continue
                new_positive, new_negative = positive & ~bit, negative & ~bit
                remaining.add((new_positive, new_negative))
                used |= new_positive | new_negative
            dropped = (active & ~(bit | used)).bit_count()
            count += solve(tuple(sorted(remaining))) << dropped
        return count

    active = 0
    for positive, negative in clauses:
        active |= positive | negative
    result = solve(clauses) << (width - active.bit_count())
    solve.cache_clear()
    return result


def nae_count(supports, columns, negative, width):
    clauses = set()
    for support in supports:
        pos = neg = 0
        for d in support:
            if negative[d]:
                neg |= columns[d]
            else:
                pos |= columns[d]
        if not pos & neg:
            clauses.update(((pos, neg), (neg, pos)))
    return count_cnf(tuple(sorted(clauses)), width)


COUNTS = {"parity": parity_count, "nae": nae_count}


def state_counts(supports, law, action, total):
    columns, higher, width = distinction_orbits(action)
    fixed = COUNTS[law](supports, columns, (False,) * len(action), width)
    complement_fixed = 0
    if all(d != image for d, image in enumerate(action)):
        complement_fixed = COUNTS[law](supports, columns, higher, width)
    neither = total - fixed - complement_fixed
    assert neither >= 0
    return fixed, complement_fixed, neither


def independent_rows(words):
    pivots = {}
    for word in words:
        reduced = reduce_word(word, pivots)
        if reduced:
            pivots[reduced.bit_length() - 1] = reduced
    return pivots


def reduce_word(word, pivots):
    for i in sorted(pivots, reverse=True):
        if word & (1 << i):
            word ^= pivots[i]
    return word


def parity_kernel(row_basis, width):
    basis = []
    for d in range(width):
        if d in row_basis:
            continue
        word = 1 << d
        for pivot, row in sorted(row_basis.items()):
            if (row & word).bit_count() % 2:
                word |= 1 << pivot
        basis.append(word)
    return basis


def shortest_changes(supports, width):
    equations = independent_rows(sum(1 << d for d in s) for s in supports)
    basis = parity_kernel(equations, width)
    words = [0]
    for generator in basis:
        words += [w ^ generator for w in words]
    sizes = [w.bit_count() for w in words]
    selected = set()
    for d in range(width):
        flag = 1 << d
        shortest = width + 1
        tied = []
        for word, size in zip(words, sizes):
            if word & flag and size <= shortest:
                if size < shortest:
                    shortest = size
                    tied.clear()
                tied.append(word)
        selected.update(tied)
    moves = independent_rows(selected)
    return basis, moves


def exchanged_parts(classes, knots, distinctions, include_fixed_distinctions):
    """Find exchanged components or a chain ending at the partner knot."""
    moved = {k for k, image in enumerate(knots) if image != k}
    neighbors = {k: [] for k in moved}
    for owners, group in classes.items():
        if len(owners) != 2 or not set(owners) <= moved:
            continue
        a, b = owners
        for d in group:
            if include_fixed_distinctions or d != distinctions[d]:
                neighbors[a].append((b, d))
                neighbors[b].append((a, d))

    unseen = set(moved)
    components = []
    while unseen:
        first = min(unseen)
        todo = [first]
        seen = {first}
        while todo:
            for other, _ in neighbors[todo.pop()]:
                if other not in seen:
                    todo.append(other)
                    seen.add(other)
        unseen -= seen
        components.append(tuple(sorted(seen)))

    parts = []
    invariant = []
    for component in components:
        image = tuple(sorted(knots[k] for k in component))
        assert image in components
        if component < image:
            parts.append((component, image))
        elif component == image:
            invariant.append(component)

    witness = None
    for first in (k for component in invariant for k in component if k < knots[k]):
        target = knots[first]
        todo = deque([first])
        parent = {first: (None, None)}
        while target not in parent:
            k = todo.popleft()
            for other, d in sorted(neighbors[k]):
                if other not in parent:
                    parent[other] = (k, d)
                    todo.append(other)
        chain = [(target, None)]
        while target != first:
            target, d = parent[target]
            chain.append((target, d))
        witness_knots = tuple(k for k, _ in reversed(chain))
        witness_distinctions = tuple(d for _, d in reversed(chain) if d is not None)
        quotient = tuple(min(k, knots[k]) for k in witness_knots)
        candidate = (len(witness_distinctions), witness_knots, witness_distinctions, quotient)
        if witness is None or candidate < witness:
            witness = candidate
    return {
        "exchanged_components": parts,
        "invariant_components": invariant,
        "shortest_partner_chain": witness,
    }


def stages_census(supports, laws, origin=None):
    classes = holder_classes(supports)
    width = sum(map(len, classes.values()))
    empty_sign = (False,) * width
    columns = tuple(1 << d for d in range(width))
    total = {law: COUNTS[law](supports, columns, empty_sign, width) for law in laws}
    rows = []
    for knots in knot_involutions(classes, len(supports)):
        preserves_initial_knots = origin is None or all(k < origin[0] for k in knots[:origin[0]])
        retain_names_below = (width if origin is None else origin[1]) if preserves_initial_knots else 0
        preferred = ordered_lift(classes, knots)
        for action, multiplicity in distinction_lifts(classes, knots, retain_names_below):
            assert all(
                set(action[d] for d in support) == set(supports[knots[k]])
                for k, support in enumerate(supports)
            )
            fixed_knots = [k for k, image in enumerate(knots) if k == image]
            fixed_distinctions = [d for d, image in enumerate(action) if d == image]
            all_shared = exchanged_parts(classes, knots, action, include_fixed_distinctions=True)
            moved_shared = exchanged_parts(classes, knots, action, include_fixed_distinctions=False)
            counts = {law: state_counts(supports, law, action, total[law]) for law in laws}
            initial_action = None
            if origin is not None and preserves_initial_knots:
                original_knots = knots[:origin[0]]
                original_distinctions = action[:origin[1]]
                assert set(original_distinctions) == set(range(origin[1]))
                initial_action = (original_knots, original_distinctions)
            rows.append({
                "knots": knots, "distinctions": action, "multiplicity": multiplicity,
                "ordered_lift": action == preferred,
                "initial_action": initial_action,
                "fixed_knots": fixed_knots, "fixed_distinctions": fixed_distinctions,
                "counts": counts, "all_shared": all_shared, "moved_shared": moved_shared,
            })
    return {"supports": supports, "total": total, "actions": rows}


def brute_counts(supports, law, action):
    result = [0, 0, 0]
    width = len(action)
    masks = [sum(1 << d for d in support) for support in supports]
    for word in range(1 << width):
        if law == "parity":
            allowed = all((word & mask).bit_count() % 2 == 0 for mask in masks)
        else:
            allowed = all(0 < word & mask < mask for mask in masks)
        if allowed:
            image = sum(((word >> d) & 1) << other for d, other in enumerate(action))
            category = 0 if image == word else 1 if image == word ^ ((1 << width) - 1) else 2
            result[category] += 1
    return tuple(result)


def verify_controls():
    controls = (
        ((0, 1, 2), (0, 3, 4)),
        ((0, 1, 2), (3, 4, 5)),
        ((0, 1, 2, 3), (0, 1, 2, 3)),
        ((0, 3, 4), (0, 1, 5), (1, 2, 6), (2, 3, 7)),
    )
    control_swaps = 0
    for supports in controls:
        stage = stages_census(supports, LAWS, origin=(0, 0))
        width = max(d for support in supports for d in support) + 1
        expected = Counter()
        knot_perm = tuple(p for p in permutations(range(len(supports)))
                          if any(p[k] != k for k in p) and all(p[p[k]] == k for k in p))
        identity = tuple(range(width))
        for law in LAWS:
            assert stage["total"][law] == sum(brute_counts(supports, law, identity))
        for action in permutations(range(width)):
            if any(action[action[d]] != d for d in action):
                continue
            mapped = tuple(frozenset(action[d] for d in s) for s in supports)
            for knots in knot_perm:
                if not all(mapped[k] == frozenset(supports[knots[k]]) for k in knots):
                    continue
                expected[knots, tuple(brute_counts(supports, law, action) for law in LAWS)] += 1
        actual = Counter()
        for row in stage["actions"]:
            actual[row["knots"], tuple(row["counts"][law] for law in LAWS)] += row["multiplicity"]
        assert actual == expected
        control_swaps += sum(expected.values())
    return {"incidence_patterns": len(controls), "explicit_lifts": control_swaps}


def compare_rounds(base, stage):
    starting = {(row["knots"], row["distinctions"]): row for row in base["actions"]}
    continued = set()
    for row in stage["actions"]:
        restriction = row["initial_action"]
        if restriction is None:
            continue
        initial_knots, _ = restriction
        if all(k == image for k, image in enumerate(initial_knots)):
            continue
        initial = starting[restriction]
        continued.add(restriction)
        row["initial_partner_chain"] = {
            mode: initial[mode]["shortest_partner_chain"] is not None for mode in ("all_shared", "moved_shared")
        }
        for mode in ("all_shared", "moved_shared"):
            if row["initial_partner_chain"][mode]:
                assert row[mode]["shortest_partner_chain"] is not None
    stage["initial_knots_moved_actions_extended"] = len(continued)


def one_start(source, start):
    timings = Counter()
    supports = source["supports_of"](start)
    before = monotonic()
    base = stages_census(supports, LAWS)
    timings["round_0"] += monotonic() - before
    origin = len(supports), max(d for s in supports for d in s) + 1
    changed = defaultdict(list)
    status = {}
    before = monotonic()
    for law in LAWS:
        grown, status[law], _ = source["grown"](supports, law, "ordinary")
        if status[law] == "funded":
            changed[grown].append(law)
    timings["ordinary_growth"] += monotonic() - before
    stages = []
    before = monotonic()
    for grown, laws in changed.items():
        stage = stages_census(grown, laws, origin)
        compare_rounds(base, stage)
        stages.append(stage)
    timings["funded_round_1"] += monotonic() - before
    return {"round_0": base, "growth_status": status, "funded_round_1": stages}, timings


def add_totals(counter, stage, law):
    actions = stage["actions"]
    counter["stages"] += 1
    counter["stages_with_knot_moving_involution"] += bool(actions)
    counter["stage_state_count_sum"] += stage["total"][law]
    counter["ordered_lifts"] += sum(row["ordered_lift"] for row in actions)
    for row in actions:
        weight = row["multiplicity"]
        fixed, complement_fixed, neither = row["counts"][law]
        counter["lifts"] += weight
        counter["some_fixed_states" if fixed else "zero_fixed_states"] += weight
        counter["some_complement_fixed_states" if complement_fixed else "zero_complement_fixed_states"] += weight
        counter["some_neither_states" if neither else "zero_neither_states"] += weight
        counter["fixed_state_count_sum"] += fixed * weight
        counter["complement_fixed_state_count_sum"] += complement_fixed * weight
        counter["neither_state_count_sum"] += neither * weight
        counter["state_count_sum_over_lifts"] += stage["total"][law] * weight
        state_profile = f"fixed={int(bool(fixed))},complement_fixed={int(bool(complement_fixed))},neither={int(bool(neither))}"
        counter[f"state_profile {state_profile}"] += weight
        fixed_profile = f"knots={len(row['fixed_knots'])},distinctions={len(row['fixed_distinctions'])}"
        counter[f"fixed_support {fixed_profile}"] += weight
        for mode in ("all_shared", "moved_shared"):
            chain = row[mode]["shortest_partner_chain"]
            if chain is None:
                counter[f"{mode} exchanged_components_only"] += weight
            else:
                counter[f"{mode} partner_chain"] += weight
                counter[f"{mode} partner_chain_length {chain[0]}"] += weight
            if not row["fixed_knots"]:
                counter[f"{mode} no_fixed_knots {'partner_chain' if chain else 'exchanged_components_only'}"] += weight
            if not row["fixed_distinctions"]:
                counter[f"{mode} no_fixed_distinctions {'partner_chain' if chain else 'exchanged_components_only'}"] += weight
            if "initial_partner_chain" in row:
                before, after = int(row["initial_partner_chain"][mode]), int(chain is not None)
                counter[f"{mode} continued_partner_chain {before}->{after}"] += weight
        if row["initial_action"] is not None:
            counter["initial_knots_preserved_lifts"] += weight
            if "initial_partner_chain" in row:
                counter["initial_knots_moved_lifts"] += weight

    if "initial_knots_moved_actions_extended" in stage:
        counter["initial_knots_moved_actions_extended"] += stage["initial_knots_moved_actions_extended"]


def report_group(summary, case, group):
    for law in LAWS:
        totals = summary[group][law]
        add_totals(totals["round_0"], case["round_0"], law)
        totals["growth_status"][case["growth_status"][law]] += 1
        for stage in case["funded_round_1"]:
            if law in stage["total"]:
                add_totals(totals["funded_round_1"], stage, law)


def conjugacy_representatives(involutions, automorphisms):
    pending = set(involutions)
    inverses = []
    for action in automorphisms:
        inv = [-1] * len(action)
        for k, image in enumerate(action):
            inv[image] = k
        inverses.append(inv)
    while pending:
        action = min(pending)
        yield action
        for f, back in zip(automorphisms, inverses):
            pending.discard(tuple(f[action[k]] for k in back))


def structure(supports):
    classes = holder_classes(supports)
    width = sum(map(len, classes.values()))
    automorphisms = list(knot_automorphisms(classes, len(supports)))
    involutions = set(knot_involutions(classes, len(supports)))
    assert involutions == {p for p in automorphisms if any(k != p[k] for k in p) and all(p[p[k]] == k for k in p)}
    row_basis = independent_rows(sum(1 << d for d in support) for support in supports)
    lifts = {}
    kinds = Counter()
    for p in sorted(involutions):
        for name in ("min", "max"):
            q = ordered_lift(classes, p, maximal=(name == "max"))
            parts = exchanged_parts(classes, p, q, include_fixed_distinctions=False)
            components = sorted(list(parts["invariant_components"]) + [c for pair in parts["exchanged_components"] for c in pair])
            kind = "one" if parts["invariant_components"] else "two" if len(components) == 2 else "several"
            kinds[f"{name}:{kind}"] += 1
            lifts[p, name] = q, kind, [len(c) for c in components]
    return {
        "supports": supports, "D": width, "K": len(supports),
        "row_basis": row_basis, "parity_dim": width - len(row_basis),
        "auts": len(automorphisms), "involutions": involutions, "kinds": kinds,
        "representatives": list(conjugacy_representatives(involutions, automorphisms)),
        "lifts": lifts, "holder_classes": classes,
    }


def stages_through_two(source, start, law):
    current = start
    for _ in range(2):
        following, status, _ = source["grown"](current, law, "ordinary")
        if status != "funded":
            yield current, status
            return
        yield current, "grown"
        current = following
    yield current, "alive"


def replay_labels(stage, action, law, total):
    width = len(action)
    columns, higher, orbits = distinction_orbits(action)
    fixed, flipped, _ = state_counts(stage["supports"], law, action, total)
    moved = [d for d, other in enumerate(action) if d != other]
    partial = flipped
    if len(moved) < width:
        partial = COUNTS[law](stage["supports"], columns, higher, orbits)
    labels = {
        "N": total, "n_S": fixed, "n_A": flipped, "n_A_moved": partial,
        "fixed_distinctions": width - len(moved), "pairs": len(moved) // 2,
        "det": (-1) ** ((total - fixed) // 2),
    }
    if law == "parity":
        moved_mask = sum(1 << d for d in moved)
        labels["W1c is plus or minus W1"] = reduce_word(moved_mask, stage["row_basis"]) == 0
    return labels


def load_archived_structure():
    parent = HERE.parent
    with gzip.open(parent / "precount.jsonl.gz", "rt") as stream:
        precount = {}
        for line in stream:
            row = json.loads(line)
            key = tuple(row.pop(field) for field in ("start", "law", "round"))
            assert key not in precount
            precount[key] = row
    with gzip.open(parent / "census_results.jsonl.gz", "rt") as stream:
        results = {}
        for line in stream:
            block = json.loads(line)
            assert block["status"] == "ok"
            for row in block["result"]["rows"]:
                key = tuple(row.pop(field) for field in ("start", "law", "round"))
                assert key not in results
                if isinstance(row["classes"], list):
                    for action in row["classes"]:
                        del action["weightings"]
                results[key] = row
    with (parent / "named_classes.jsonl").open() as stream:
        quotient = {}
        for line in stream:
            row = json.loads(line)
            key = row.pop("start"), row.pop("round")
            assert key not in quotient
            quotient[key] = row
    return precount, results, quotient


def read_pairs(stage, action, kind, p):
    if kind != "two":
        count = sum(other != d for d, other in enumerate(action))
        return [count, count]
    pairs = exchanged_parts(stage["holder_classes"], p, action, include_fixed_distinctions=False)["exchanged_components"]
    first, second = pairs[0]
    return [
        sum(len(owners) * len(group) for owners, group in stage["holder_classes"].items() if set(owners) <= set(part))
        for part in (first, second)
    ]


def replay_quotient(stage):
    basis, moves = shortest_changes(stage["supports"], stage["D"])
    class_count = 1 << (len(basis) - len(moves))
    if class_count < 2:
        return None
    actions = []
    for p in stage["representatives"]:
        for name in ("min", "max"):
            q = stage["lifts"][p, name][0]
            same = True
            for word in basis:
                image = sum(1 << other for d, other in enumerate(q) if word & (1 << d))
                if reduce_word(image ^ word, moves):
                    same = False
                    break
            actions.append({"perm": list(p), "lift": name, "identity on the classes": same})
    return {"classes": class_count, "swaps": actions}


def record_growth_extensions(counter, earlier, later):
    previous_size = earlier["K"]
    extension = defaultdict(list)
    for p in later["involutions"]:
        if all(k < previous_size for k in p[:previous_size]):
            extension[p[:previous_size]].append(p)
    prior = earlier["involutions"]
    counter["stages_with_swap_and_next"] += bool(prior)
    counter["lost_all_swaps"] += bool(prior) and not later["involutions"]
    counter["prior_knot_actions"] += len(prior)
    counter["prior_knot_actions_without_extension"] += len(prior - extension.keys())

    later_holders = [None] * later["D"]
    for owners, group in later["holder_classes"].items():
        for d in group:
            later_holders[d] = owners
    for p in prior:
        for name in ("min", "max"):
            action = earlier["lifts"][p, name][0]
            counter[f"{name}_prior_distinction_lifts"] += 1
            if not any(
                all(tuple(sorted(g[k] for k in later_holders[d])) == later_holders[other] for d, other in enumerate(action))
                for g in extension[p]
            ):
                counter[f"{name}_prior_distinction_lifts_without_extension"] += 1


def replay(indices, source, starts, archive):
    precount, result, quotient = archive
    structural = defaultdict(Counter)
    labels = defaultdict(Counter)
    legal_next = defaultdict(Counter)
    classes = defaultdict(Counter)
    skipped = defaultdict(Counter)
    mismatch_counts = Counter()
    mismatch_examples = []
    cutoff_examples = []
    started = monotonic()
    timings = Counter()

    def compare(label, key, measured, recorded):
        if measured != recorded:
            mismatch_counts[label] += 1
            if len(mismatch_examples) < 20:
                mismatch_examples.append((label, key, measured, recorded))

    for index in indices:
        base = source["supports_of"](starts[index])
        structures = {}
        for law in LAWS:
            previous = None
            seen = set()
            before = monotonic()
            stages = list(stages_through_two(source, base, law))
            timings["growth"] += monotonic() - before
            for age, (support, status) in enumerate(stages):
                key = index, law, age
                seen.add(age)
                label = f"{law} round {age}"
                before = monotonic()
                if support not in structures:
                    structures[support] = structure(support)
                stage = structures[support]
                timings["incidence"] += monotonic() - before
                summary = structural[label]
                involutions = stage["involutions"]
                observed = {k: stage[k] for k in ("K", "D", "parity_dim", "auts", "kinds")}
                observed.update({"status": status, "truncated": False, "involutions": len(involutions)})
                compare("precount stage", key, observed, precount.get(key))
                summary["stages"] += 1
                summary[f"status {status}"] += 1
                summary["stages_with_swaps"] += bool(involutions)
                summary["individual_knot_actions"] += len(involutions)
                summary["representative_knot_actions"] += len(stage["representatives"])
                for kind, count in stage["kinds"].items():
                    summary[f"stage_has_{kind}"] += 1
                    summary[f"individual_knot_actions_{kind}"] += count
                if previous is not None:
                    record_growth_extensions(legal_next[f"{law} round {age-1} to {age}"], previous, stage)
                previous = stage
                recorded = result.get(key)
                compare("census stage presence", key, bool(involutions), recorded is not None)

                if law == "parity" and age < 2:
                    before = monotonic()
                    quot = replay_quotient(stage) if involutions else None
                    compare("shortest-change quotient", key, quot, quotient.get((index, age)))
                    if quot is not None:
                        q_summary = classes[str(quot["classes"])]
                        q_summary["stages"] += 1
                        q_summary["representative_knot_actions"] += len(quot["swaps"]) // 2
                        q_summary["min_max_lift_rows"] += len(quot["swaps"])
                        q_summary["rows_moving_a_class"] += sum(not row["identity on the classes"] for row in quot["swaps"])
                    timings["shortest_change_quotient"] += monotonic() - before

                if not involutions:
                    continue
                width = stage["D"]
                columns = tuple(1 << d for d in range(width))
                sign = (False,) * width
                if law == "nae" and width > 22:
                    compare("census cutoff", key, "not run: too many states", recorded and recorded["classes"])
                    skipped[label]["stages_excluded_by_width"] += 1
                    # Count every excluded round-1 stage and the smallest-width excluded round-2 stages.
                    if age == 1 or width == 23:
                        before = monotonic()
                        total = nae_count(support, columns, sign, width)
                        timings["cutoff_totals"] += monotonic() - before
                        skipped[label]["excluded_stages_counted"] += 1
                        if total <= 1 << 22:
                            skipped[label]["allowed_count_at_most_2_to_22"] += 1
                            if len(cutoff_examples) < 20:
                                cutoff_examples.append((index, age, width, total))
                    continue

                before = monotonic()
                total = COUNTS[law](support, columns, sign, width)
                observed_rows = []
                structural[label]["stages_run_for_weights"] += 1
                for p in stage["representatives"]:
                    for name in ("min", "max"):
                        action, kind, part_sizes = stage["lifts"][p, name]
                        if name == "max" and action == stage["lifts"][p, "min"][0]:
                            continue
                        stat = replay_labels(stage, action, law, total)
                        den = labels[label]
                        den["exact_representative_lift_rows"] += 1
                        den["fixed_nonempty"] += bool(stat["n_S"])
                        den["complement_fixed_nonempty"] += bool(stat["n_A"])
                        den["neither_nonempty"] += stat["n_S"] + stat["n_A"] < total
                        den["moved_complement_fixed_nonempty"] += bool(stat["n_A_moved"])
                        den["fixed_distinction_violation"] += bool(stat["n_A"] and stat["fixed_distinctions"])
                        if law == "parity":
                            den["odd_knot_violation"] += bool(stat["n_A"] and any(len(s) % 2 for s in support))
                        if stat["n_A"]:
                            den[f"complement_fixed_{name}_{kind}"] += 1
                        if stat["n_A_moved"]:
                            den[f"moved_complement_fixed_{name}_{kind}"] += 1
                        row = {
                            "perm": list(p), "lift": name, "kind": kind, "sides": part_sizes,
                            "readers": read_pairs(stage, action, kind, p),
                        }
                        if law != "parity" or stage["parity_dim"] <= 22:
                            den["rows_with_enumerated_archived_labels"] += 1
                            row["labels"] = stat
                        else:
                            den["parity_exact_rows_beyond_archive_enumeration"] += 1
                        observed_rows.append(row)
                if recorded and isinstance(recorded["classes"], list):
                    archived_rows = recorded["classes"]
                    if law == "nae":
                        for row in archived_rows:
                            row["labels"].pop("W1c is plus or minus W1", None)
                    compare("census representative rows", key, observed_rows, archived_rows)
                    compare("census number of swaps", key, len(involutions), recorded["swaps"])
                    compare("census sizes", key, [stage["K"], width, False], [recorded["K"], recorded["D"], recorded["truncated"]])
                timings["state_classes"] += monotonic() - before

            for age in set(range(3)) - seen:
                key = index, law, age
                compare("precount extra stage", key, None, precount.get(key))
                compare("census extra stage", key, None, result.get(key))
                if law == "parity" and age < 2:
                    compare("quotient extra stage", key, None, quotient.get((index, age)))

    return {
        "starts": len(indices), "stage_inclusion": "Every stage actually formed, even if growth stops there. Do not copy a terminal stage into later rounds.",
        "structure": structural, "p1_extensions": legal_next, "p2_state_classes": labels,
        "p9_shortest_change_quotient": classes,
        "nae_cutoff": skipped, "nae_cutoff_counterexample_index_round_width_allowed": cutoff_examples,
        "mismatch_counts": mismatch_counts, "mismatch_examples": mismatch_examples,
        "timing": {
            "elapsed_seconds": round(monotonic() - started, 6),
            "phase_seconds": {k: round(v, 6) for k, v in timings.items()},
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
    }


def save_output(destination, output):
    # Keep the exact blind-start records compact while leaving aggregate counts easy to scan.
    cases = output.pop("cases")
    with destination.open("w") as f:
        f.write(json.dumps(output, indent=2).removesuffix("\n}"))
        f.write(',\n  "cases": {\n')
        for line, (index, case) in enumerate(cases.items()):
            if line:
                f.write(",\n")
            f.write(f'    "{index}": {json.dumps(case, separators=(",", ":"))}')
        f.write("\n  }\n}\n")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write", action="store_true", help="write the complete census to its adjacent JSON file")
    mode.add_argument("--smoke", action="store_true", help="time the same computation on a small subset")
    mode.add_argument("--comparison-smoke", action="store_true", help="time a stratified subset of the archive comparison")
    mode.add_argument("--compare-full", action="store_true", help="compare the archive for all starts and add the result to the adjacent JSON file")
    args = parser.parse_args()

    begun = monotonic()
    source = runpy.run_path(str(SOURCE))
    assert SOURCE.with_name("starts.json").is_file()
    starts = source["census"]()
    destination = HERE / "census_rebuild.json"
    if args.comparison_smoke or args.compare_full:
        archive = load_archived_structure()
        trial = [0, 1, 17, 26, 87, 89, 99, 101, 127, 424, 1223, 1235, 3097, 4987, 7066, 7068]
        rng = random.Random(SAMPLE_SEED)
        trial.extend(rng.sample([i for i in range(len(starts)) if i not in trial], 80))
        indices = trial if args.comparison_smoke else range(len(starts))
        counts = replay(indices, source, starts, archive)
        counts["timing"]["elapsed_including_archive_read_seconds"] = round(monotonic() - begun, 6)
        if args.compare_full:
            output = json.loads(destination.read_text())
            output["post_read_full_replay"] = counts
            save_output(destination, output)
        print(json.dumps(counts, indent=2))
        return
    sample_frame = [i for i in range(100, len(starts)) if i != DESIGNATED]
    sample = sorted(random.Random(SAMPLE_SEED).sample(sample_frame, SAMPLE_SIZE))
    panels = {"prefix": list(range(100)), "designated": [DESIGNATED], "seeded_sample": sample}
    if args.smoke:
        panels["prefix"] = [0, 17, 99]
        panels["seeded_sample"] = [sample[0], sample[20], sample[-1]]

    controls = verify_controls()
    summary = defaultdict(lambda: {law: defaultdict(Counter) for law in LAWS})
    timings = Counter()
    records = {}
    slowest = []
    for group, indices in panels.items():
        for index in indices:
            before = monotonic()
            result, measured = one_start(source, starts[index])
            report_group(summary, result, group)
            report_group(summary, result, "combined")
            timings.update(measured)
            slowest.append((monotonic() - before, index))
            records[index] = result
    elapsed = monotonic() - begun
    output = {
        "coverage": {
            "source": "research/FORBID-EDITS-20261126-001/starts.json",
            "growth": "ordinary arm through research/FORBID-EDITS-20261126-001/forbid.py",
            "start_roster_size": len(starts), "panels": panels, "sample_seed": SAMPLE_SEED,
            "sample_weighting": "Uniform sample without replacement among roster indices 100 and above, excluding 3097.",
            "depth": "Round 0 for all tested starts. A round 1 stage is counted only if funded under that law.",
            "phase_coloring": "Stage involutions need not preserve birth round. An action is traced across rounds only if it preserves the initial knot set and moves an initial knot.",
            "state_laws": "Even parity and not-all-equal at every knot. Read each funded stage under its own growth law.",
        },
        "conventions": {
            "actions": "Count all involutive incidence permutations with a nonidentity knot action. Distinction permutations act on values without sign changes.",
            "representation": "The ordered lift matches sorted identifiers between exchanged holder classes and fixes each distinction in invariant holder classes. Each entry records a representative and its exact multiplicity; the ordered lift contributes once whether or not its class also includes other lifts.",
            "multiplicity": "Across exchanged holder classes of size m, count m! bijections. Within an invariant class count m! / ((m-2t)! 2^t t!) for t transpositions, since relabellings conjugate all such lifts. Initial distinctions are kept explicit when a lift preserves birth round.",
            "counts": ["fixed", "complement_fixed", "neither"],
            "complement_fixed": "An allowed state whose image under the distinction permutation equals its bitwise complement.",
            "state_count_sums": "Sums over labelled allowed states, equally weighted within each supported incidence lift and then added across lifts with their multiplicities.",
            "fixed_support": "Fixed knots and fixed distinctions are recorded independently.",
            "all_shared": "Remove fixed knots. Retain every shared distinction with both holders among the moved knots.",
            "moved_shared": "Remove fixed knots and use only moved shared distinctions with both holders among moved knots.",
            "partner_chain": "A chain of shared distinctions joining a moved knot to its partner. The recorded shortest witness gives the length, knots, shared distinctions, and knot-pair representatives. A connected component without such a chain is exchanged with a different component.",
        },
        "checks": controls,
        "timing": {
            "total_seconds_before_output": round(elapsed, 6),
            "phase_seconds": {phase: round(seconds, 6) for phase, seconds in timings.items()},
            "slowest_three_cases_seconds_then_index": [[round(sec, 6), i] for sec, i in sorted(slowest, reverse=True)[:3]],
            "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        },
        "totals": summary,
        "cases": records,
    }
    if args.write:
        save_output(destination, output)
    print(json.dumps({"timing": output["timing"], "totals": summary["combined"], "checks": controls}, indent=2))


if __name__ == "__main__":
    main()
