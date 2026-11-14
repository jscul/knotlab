"""Production per-call Boolean relations and exact length-set iteration.

A relation uses bit 8*parent_port_state + child_port_state. No identities
are removed: equal arguments restrict the table to their diagonal.
"""
from __future__ import annotations

from collections import deque
from functools import lru_cache

from inputs import load_paths
from limits import LimitReached


def encode_hex(relation):
    return f"0x{relation:016x}"


def per_call(prep, checkpoint=lambda: None, drop_side=None):
    paths = load_paths()
    flat = prep.flat(prep.S)
    if flat["k"] != 3:
        raise ValueError("the specified S does not have three ports")
    self_indices = [j for j, (callee, _) in enumerate(flat["calls"]) if callee == prep.S]
    results = []
    for call_index, flat_index in enumerate(self_indices):
        body = flat
        chosen = flat_index
        if drop_side is not None and drop_side != flat_index:
            body = dict(flat, calls=[call for j, call in enumerate(flat["calls"]) if j != drop_side])
            chosen -= drop_side < flat_index
        block = paths.Block(body, chosen, prep.G)
        relation = 0
        for incoming, outgoing in zip(block.incoming, block.outgoing):
            relation |= 1 << (8 * int(incoming) + int(outgoing))
        results.append(dict(call_index=call_index, flat_call_index=flat_index,
                            arguments=list(flat["calls"][flat_index][1]),
                            relation=relation, hex=encode_hex(relation)))
        checkpoint()
    return results


def rectangular(relation, size=8):
    row_mask = (1 << size) - 1
    reference = 0
    for left in range(size):
        row = (relation >> (size * left)) & row_mask
        if row:
            if reference and row != reference:
                return False
            reference = row
    return True


def compose(left, right, size=8):
    """Boolean matrix product: left then right."""
    row_mask = (1 << size) - 1
    rows = tuple((right >> (size * i)) & row_mask for i in range(size))
    result = 0
    for source in range(size):
        choices = (left >> (size * source)) & row_mask
        exits = 0
        while choices:
            bit = choices & -choices
            choices ^= bit
            exits |= rows[bit.bit_length() - 1]
        result |= exits << (size * source)
    return result


def nonrectangular_word(generators, levels, size, checkpoint):
    """Find a reachable cycle in the product graph after deleting rectangles."""
    vertices = {r for level in levels for r in level if not rectangular(r, size)}
    color, parent, first_letter = {}, {}, {}
    for letter, relation in enumerate(generators):
        if relation not in vertices or color.get(relation):
            continue
        first_letter[relation] = letter
        parent[relation] = None
        color[relation] = 1
        stack = [(relation, 0)]
        while stack:
            current, next_letter = stack[-1]
            if next_letter == len(generators):
                color[current] = 2
                stack.pop()
                continue
            stack[-1] = (current, next_letter + 1)
            target = compose(current, generators[next_letter], size)
            checkpoint()
            if target not in vertices:
                continue
            if color.get(target, 0) == 0:
                parent[target] = (current, next_letter)
                color[target] = 1
                stack.append((target, 0))
                continue
            if color[target] == 1:
                chain, edge_labels = [current], []
                cursor = current
                while parent[cursor] is not None:
                    predecessor, label = parent[cursor]
                    edge_labels.append(label)
                    chain.append(predecessor)
                    cursor = predecessor
                chain.reverse()
                edge_labels.reverse()
                start = chain.index(target)
                root_letter = first_letter[chain[0]]
                prefix = [root_letter] + edge_labels[:start]
                cycle = edge_labels[start:] + [next_letter]
                return dict(prefix=prefix, cycle=cycle,
                            prefix_product=encode_hex(target),
                            cycle_products=[encode_hex(r) for r in chain[start:]],
                            all_nonempty_prefixes_nonrectangular=True)
    raise AssertionError("nonrectangular products recur without a reachable product cycle")


def semigroup(generators, checkpoint=lambda: None, max_stored_products=250_000,
              max_levels=100_000, size=8):
    """Iterate the complete P_n sets until a set repeats, retaining least r.

    Explicit storage caps return no conclusion by raising LimitReached.
    Rectangular relations stay in the length sets, including after success.
    """
    generators = tuple(generators)
    if not generators:
        raise ValueError("no SELF generators")
    current = frozenset(generators)
    seen, levels = {}, []
    stored, least_r, certificate_products = 0, None, None
    repeated_checks = []
    while current not in seen:
        n = len(levels) + 1
        if n > max_levels:
            raise LimitReached("cap", f"P_n length-set cap {max_levels}")
        stored += len(current)
        if stored > max_stored_products:
            raise LimitReached("cap", f"stored P_n product cap {max_stored_products}")
        seen[current] = n
        levels.append(current)
        all_rectangular = all(rectangular(relation, size) for relation in current)
        repeated_checks.append(all_rectangular)
        if all_rectangular and least_r is None:
            least_r = n
            certificate_products = sorted(current)
        if least_r is not None and not all_rectangular:
            raise AssertionError("rectangularity failed to persist")
        nxt = set()
        for relation in current:
            for generator in generators:
                nxt.add(compose(relation, generator, size))
                if len(nxt) + stored > max_stored_products:
                    raise LimitReached("cap", f"P_n construction product cap {max_stored_products}")
                checkpoint()
        current = frozenset(nxt)
    repeat_start = seen[current]
    period = len(levels) + 1 - repeat_start
    in_repeat = repeated_checks[repeat_start - 1:]
    if least_r is not None:
        assert all(in_repeat), "repeating part includes a nonrectangular product after r"
    else:
        assert not any(in_repeat), "a repeating length set is all rectangular but r is absent"
    word = None if least_r is not None else nonrectangular_word(generators, levels, size, checkpoint)
    return dict(complete=True, r=least_r, recurring_word=word,
                P_r=None if certificate_products is None else [encode_hex(r) for r in certificate_products],
                length_set_sizes=list(map(len, levels)),
                all_rectangular_by_length=repeated_checks,
                repeat_start=repeat_start, period=period,
                repeat_all_rectangular=in_repeat, stored_products=stored,
                limits=dict(max_stored_products=max_stored_products, max_levels=max_levels))
