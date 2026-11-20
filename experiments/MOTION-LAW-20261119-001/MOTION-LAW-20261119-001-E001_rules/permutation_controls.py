"""Check distinct equivariant commuting permutations of physical allowed states."""

from itertools import product
import json

from sources import DATA, cases, source_and_stage


def local_pools(stars):
    owners = {}
    for v, row in enumerate(stars):
        for bit in row:
            owners.setdefault(bit, []).append(v)
    result = []
    for v, row in enumerate(stars):
        leaves = tuple(bit for bit in row if len(owners[bit]) == 1)
        neighbours = {w for bit in row for w in owners[bit] if w != v}
        if len(leaves) == 2:
            result.append((frozenset(len(stars[w]) for w in neighbours), leaves))
    return result


def apply(state, thresholds, pools):
    updated = set(state)
    for signature, leaves in pools:
        if signature & thresholds and len(state.intersection(leaves)) == 1:
            updated.symmetric_difference_update(leaves)
    return frozenset(updated)


def two_knots(k):
    stars = [[0, 1, 2], [0] + list(range(3, k+2))]
    sites = local_pools(stars)
    distinct = 0
    count = 0
    for word in product((0, 1), repeat=k+2):
        state = frozenset(i for i, flag in enumerate(word) if flag)
        if any(len(state.intersection(row)) % 2 for row in stars):
            continue
        changed = apply(state, {k}, sites)
        assert all(len(changed.intersection(row)) % 2 == 0 for row in stars)
        assert apply(changed, {k}, sites) == state
        assert apply(state, {k+1}, sites) == state
        assert apply(changed, {k+1}, sites) == apply(apply(state, {k+1}, sites), {k}, sites)
        count += 1
        distinct += changed != state
    assert count == 2**k and distinct > 0
    return dict(arity=k, allowed_assignments=count, assignments_changed=distinct)


def guarded_pools(stars, selected_size):
    """Change both loose members when a shared value at a selected neighbor is one."""
    places = [set(row) for row in stars]
    pools = []
    for v, row in enumerate(places):
        other = [w for w in range(len(places)) if w != v and row & places[w]]
        loose = row - set().union(*(places[w] for w in other))
        if len(loose) == 2:
            witnesses = set().union(*(row & places[w] for w in other if len(places[w]) == selected_size))
            pools.append((loose, witnesses))
    return pools


def guarded_change(state, pools):
    updated = set(state)
    for pair, witnesses in pools:
        if state & witnesses:
            updated.symmetric_difference_update(pair)
    return updated


def different_after_renaming(k):
    # The centre has two loose distinctions and shares one with each outside knot.
    stars = [[0, 1, 2, 3], [0, *range(4, k+3)], [1, *range(k+3, 2*k+2)]]
    assert list(map(len, stars)) == [4, k, k]
    pools = guarded_pools(stars, k)
    other = guarded_pools(stars, k+1)
    state = {0, 1, 4, k+3}
    moved = guarded_change(state, pools)
    assert len(moved) == 6 and guarded_change(state, other) == state
    assert guarded_change(moved, pools) == state and guarded_change(set(), pools) == set()
    assert all(len(q.intersection(row)) % 2 == 0 for q in (state, moved) for row in stars)
    tested = 0
    if k <= 6:
        for word in product((0, 1), repeat=2*k+2):
            x = {i for i, bit in enumerate(word) if bit}
            if all(len(x.intersection(row)) % 2 == 0 for row in stars):
                y = guarded_change(x, pools)
                assert all(len(y.intersection(row)) % 2 == 0 for row in stars)
                assert guarded_change(y, pools) == x and guarded_change(y, other) == y
                tested += 1
        assert tested == 2**(2*k-1)
    return dict(neighbor_size=k, source_knots=3, support_before=len(state), support_after=len(moved),
                all_assignments_exhausted=tested)


def main():
    observed = {}
    for spec in cases():
        _, reader = source_and_stage(spec)
        pools = local_pools(reader.stars)
        observed[spec["id"]] = dict(two_loose_pools=len(pools),
                                    adjacent_arities=sorted(set().union(*(s for s, _ in pools))))
    examples = [two_knots(k) for k in range(4, 11)]
    result = dict(two_knot_controls=examples, reached_motion_stages=observed,
                  different_after_forgetting_names=[different_after_renaming(k) for k in range(5, 11)])
    (DATA / "permutation_controls.json").write_text(json.dumps(result, indent=2)+"\n")
    print("Exhaustive allowed states on two-knot controls:", sum(v["allowed_assignments"] for v in examples))


if __name__ == "__main__":
    main()
