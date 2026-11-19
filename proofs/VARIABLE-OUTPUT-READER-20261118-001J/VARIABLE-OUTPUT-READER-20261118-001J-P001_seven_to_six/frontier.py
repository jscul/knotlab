"""Close all single-ternary histories in which only the first two additions make three outputs."""

from collections import Counter, deque
from functools import lru_cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import chain, combinations, permutations, product
from pathlib import Path
import hashlib
import json
import sys

PROOFS = Path(__file__).resolve().parents[2]
path, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001G").glob("*/frontiers.py")
spec = spec_from_file_location("seven_boundary_predecessor", path)
old = module_from_spec(spec)
sys.modules[spec.name] = old
spec.loader.exec_module(old)


@lru_cache(maxsize=100_000)
def canon(front):
    """Group by invariant colors, then try every ordering within each group."""
    colors = []
    for site, count in enumerate(front.loose):
        sizes = sorted(group.bit_count() for group in front.retired if group & (1 << site))
        colors.append((count, front.adjacent[site].bit_count(), tuple(sizes)))
    classes = [tuple(i for i, color in enumerate(colors) if color == key)
               for key in sorted(set(colors))]
    orders = (tuple(chain.from_iterable(blocks))
              for blocks in product(*(permutations(group) for group in classes)))
    return min((front.restrict(order), order) for order in orders)


def step(front, parents, outputs):
    """Advance the anonymous frontier and forget exhausted holders."""
    new_site = len(front.loose)
    loose = [count - (site in parents) for site, count in enumerate(front.loose)]
    adjacent = list(front.adjacent)
    for parent in parents:
        adjacent[parent] |= 1 << new_site
    exhausted = [adjacent[site] for site, count in enumerate(loose) if count == 0]
    extended = old.Frontier((*loose, outputs), (*adjacent, old.mask(parents)),
                            (*front.retired, *exhausted))
    retained = [site for site, count in enumerate(loose) if count]
    return canon(extended.restrict((*retained, new_site)))[0]


def literal_snapshot(rows):
    users, adjacent = old.original_rule().incidence(dict(enumerate(rows)))
    loose = old.original_rule().loose_ports(users)
    active = tuple(sorted(loose))
    masks = {site: old.mask(i for i, holder in enumerate(active) if holder in neighbors)
             for site, neighbors in adjacent.items()}
    retired = {mask for site, mask in masks.items() if site not in loose and mask.bit_count() >= 2}
    raw = old.Frontier(tuple(len(loose[site]) for site in active),
                       tuple(masks[site] for site in active), tuple(sorted(retired)))
    front, order = canon(raw)
    return front, tuple(active[i] for i in order), loose


def advance(rows, parents, outputs):
    support = dict(enumerate(rows))
    users, _ = old.original_rule().incidence(support)
    loose = old.original_rule().loose_ports(users)
    taken = tuple(min(loose[site]) for site in parents)
    fresh = tuple(range(len(users), len(users) + outputs))
    # The inherited three-output predicate checks the same parent condition on the old system.
    assert old.original_rule().legal_local_move(support, taken, old.FRESH_FOR_PARENT_TEST)
    return (*rows, (*taken, *fresh))


def initial_histories():
    first = advance(((0, 1, 2),), (0,), 3)
    return [advance(first, (site,), 3) for site in (0, 1)]


def complementary(front, groups):
    for left in groups:
        for right in groups:
            uses = tuple(int(i in left) + int(i in right) for i in range(len(front.loose)))
            if uses == front.loose:
                return True
    return False


def run():
    representatives = {}
    queue = deque()
    for rows in initial_histories():
        front = literal_snapshot(rows)[0]
        if front not in representatives:
            representatives[front] = rows
            queue.append(front)

    transitions = {}
    histogram, menu_positive, triple_moves = Counter(), Counter(), Counter()
    complementary_count = 0
    first = {}
    while queue:
        front = queue.popleft()
        rows = representatives[front]
        independent, active, loose = literal_snapshot(rows)
        assert independent == front
        allowed = old.verify_literal_moves(rows, front, active, loose)
        parents_allowed = [parents for parents in sorted(allowed) if len(parents) >= 2]
        triples = [parents for parents in parents_allowed if len(parents) == 3]
        frontier_size = sum(front.loose)
        shrinks = 7 - frontier_size
        assert shrinks == sum(len(row) == 5 for row in rows)
        histogram[shrinks] += 1
        menu_positive[shrinks] += bool(triples)
        triple_moves[shrinks] += len(triples)
        if frontier_size == 6:
            complementary_count += complementary(front, triples)

        next_moves = []
        for parents in parents_allowed:
            next_front = step(front, parents, 2)
            expanded = advance(rows, tuple(active[i] for i in parents), 2)
            assert literal_snapshot(expanded)[0] == next_front
            next_moves.append((parents, next_front))
            if next_front not in representatives:
                representatives[next_front] = expanded
                queue.append(next_front)
                if len(parents) == 3:
                    first.setdefault(shrinks + 1, expanded)
        transitions[front] = next_moves

    indices = {state: i for i, state in enumerate(sorted(transitions))}
    receipt = []
    for state in sorted(transitions):
        moves = [(parents, indices[successor]) for parents, successor in transitions[state]]
        receipt.append([(state.loose, state.adjacent, state.retired), moves])
    digest = hashlib.sha256(json.dumps(receipt, separators=(",", ":")).encode()).hexdigest()
    distribution = [{"shrinking_joins": shrinks, "loose_bits": 7 - shrinks, "states": count,
                     "states_with_legal_triple": menu_positive[shrinks],
                     "unordered_three_parent_site_moves": triple_moves[shrinks]}
                    for shrinks, count in sorted(histogram.items())]
    return {"three_output_sites_after_seed": "Exactly the first two, both unary.",
            "reachable_states": len(transitions), "transitions": sum(map(len, transitions.values())),
            "fixed_point_sha256": digest, "distribution": distribution,
            "six_frontier_states_with_complementary_legal_triples": complementary_count,
            "maximum_shrinking_joins": max(histogram), "smallest_frontier": 7 - max(histogram),
            "first_histories_by_shrinking_joins": first, "all_moves_literal_replayed": True}


def sharp_radius():
    # Bits 19 and 20 belong to the same four-place holder. Only 19 was consumed by the last site.
    rows = ((0, 1, 2), (0, 3, 4, 5), (1, 6, 7, 8), (3, 6, 9, 10), (4, 7, 11, 12),
            (9, 11, 13, 14), (5, 13, 15, 16), (2, 15, 17, 18), (8, 17, 19, 20),
            (18, 14, 21, 22), (10, 16, 19, 23, 24))
    path, = (PROOFS / "VARIABLE-OUTPUT-READER-20261118-001I").glob("*/fixtures.py")
    spec = spec_from_file_location("small_equation_checks", path)
    check = module_from_spec(spec)
    spec.loader.exec_module(check)
    history = tuple((str(i), row) for i, row in enumerate(rows))
    check.literal.replay(history)
    legal = set(check.literal.direct_triples(*check.literal.incidence(history)))
    true_mark, image = (12, 20, 21), (12, 19, 21)
    assert true_mark in legal and image not in legal
    pairs = list(combinations(range(25), 2))
    table, _ = check.pair_minima(check.span(check.mask(row) for row in rows), pairs)
    perm = list(range(25))
    perm[19], perm[20] = 20, 19
    renamed = {pair: table[tuple(sorted((perm[pair[0]], perm[pair[1]])))] for pair in pairs}
    mismatches = {k: sum(min(table[p], k + 1) != min(renamed[p], k + 1) for p in pairs)
                  for k in (3, 4, 5)}
    assert mismatches[4] == 0 and mismatches[5] == 8
    return {"width": 25, "junction_supports": rows, "legal_mark": true_mark,
            "forbidden_image": image, "all_named_pairs": len(pairs), "transposition": [19, 20],
            "number_of_legal_marked_triples": len(legal), "changed_entries_by_K_cutoff": mismatches}


if __name__ == "__main__":
    print(json.dumps({"closure": run(), "sharp_distance_four": sharp_radius()}, indent=2))
