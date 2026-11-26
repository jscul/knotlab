"""Check changes directly from the incidence of distinctions at their holders."""

from collections import defaultdict, deque
from itertools import combinations

from replay_growth import binary_mask, elimination, incidence_of, insert, remainder


def wired(stage):
    """Use one auxiliary holder for loose distinctions in the parity calculation."""
    outside = len(stage)
    ends = {}
    for name, holders in incidence_of(stage).items():
        first, *other = holders
        ends[name] = (first, other[0] if other else outside)
    return ends, outside


def adjacency(ends, size):
    meeting = [defaultdict(list) for _ in range(size)]
    for name, (first, second) in ends.items():
        meeting[first][second].append(name)
        meeting[second][first].append(name)
    return meeting


def coordinate_parity(names, ends):
    syndrome = 0
    for name in names:
        first, second = ends[name]
        syndrome ^= (1 << first) | (1 << second)
    return syndrome


def new_kernels(ends, old):
    """Track distinction masks while eliminating their parity conditions."""
    basis = {}
    for name, (first, second) in ends.items():
        if name in old:
            continue
        image = (1 << first) | (1 << second)
        support = 1 << name
        while image and image.bit_length() in basis:
            row, combination = basis[image.bit_length()]
            image ^= row
            support ^= combination
        if image:
            basis[image.bit_length()] = image, support
        else:
            yield support


def distinct_parallel(meeting):
    for first, neighbors in enumerate(meeting):
        for second, names in neighbors.items():
            if first < second:
                for other in names[1:]:
                    yield names[0], other


def all_four(meeting, outside):
    """Span four-distinction changes by differences of two-step routes.

    Parallel distinctions are handled by a separate span of pairs. With
    that span present, one representative per two-step route suffices.
    """
    route = {}
    for through, neighbors in enumerate(meeting):
        if through == outside:
            continue
        for first, last in combinations(sorted(neighbors), 2):
            key = first, last
            via = neighbors[first][0], neighbors[last][0]
            other = route.setdefault(key, via)
            if via != other:
                yield other + via


def chronological_four(meeting, outside, ages):
    """Use one immediate common successor for each pair of children."""
    for holder, age in enumerate(ages):
        if not age:
            continue
        children = [child for child in meeting[holder] if child != outside and ages[child] == age + 1]
        for first, second in combinations(children, 2):
            next_holders = meeting[first].keys() & meeting[second].keys()
            successors = [k for k in next_holders if k == outside or ages[k] == age + 2]
            if successors:
                successor = min(successors)
                yield (
                    meeting[holder][first][0], meeting[holder][second][0],
                    meeting[first][successor][0], meeting[second][successor][0],
                )


def new_span(stage, old, ages):
    ends, outside = wired(stage)
    fresh_ends = {name: holders for name, holders in ends.items() if name not in old}
    restricted = adjacency(fresh_ends, outside + 1)
    whole = adjacency(ends, outside + 1)
    old_mask = binary_mask(old)
    dim = len(fresh_ends) - len(elimination(binary_mask(knot) & ~old_mask for knot in stage))
    pair_span = elimination(binary_mask(pair) for pair in distinct_parallel(restricted))
    inside = True
    shortest = True

    def add_four(choices, basis):
        nonlocal inside, shortest
        for support in choices:
            inside &= len(set(support)) == 4 and coordinate_parity(support, fresh_ends) == 0
            # The whole presentation gives a stricter shortest test than
            # the presentation with the start's distinctions removed.
            shortest &= any(
                len(whole[a][b]) == 1 and not whole[a].keys() & whole[b].keys()
                for a, b in (ends[name] for name in support)
            )
            insert(binary_mask(support), basis)

    for support in distinct_parallel(restricted):
        inside &= coordinate_parity(support, fresh_ends) == 0
    planned = pair_span.copy()
    add_four(chronological_four(restricted, outside, ages), planned)
    complete = pair_span.copy()
    add_four(all_four(restricted, outside), complete)
    return {
        "dim Z_new": dim,
        "rank of pairs and loops of four": len(planned),
        "inside Z_new": inside,
        "rank of all pairs and four-distinction changes": len(complete),
        "shortest in the full stage": shortest,
    }


def short_span(meeting, allowed_dim):
    """Use one shortest return and differences among all tied returns."""
    basis = elimination(binary_mask(pair) for pair in distinct_parallel(meeting))
    for first, neighbors in enumerate(meeting):
        for last, names in neighbors.items():
            if len(basis) == allowed_dim:
                return basis
            if first >= last or len(names) > 1:
                continue
            marked = 1 << names[0]
            lengths = {first: 0}
            representative = {first: 0}
            queue = [first]
            for holder in queue:
                length = lengths[holder]
                if last in lengths and length == lengths[last]:
                    break
                for nxt, available in meeting[holder].items():
                    step = 1 << available[0]
                    if step == marked or nxt in lengths:
                        continue
                    lengths[nxt] = length + 1
                    representative[nxt] = representative[holder] ^ step
                    queue.append(nxt)
            if last not in lengths:
                continue
            insert(marked ^ representative[last], basis)

            # Along the shortest return, each predecessor can replace the
            # final step of the reference prefix and share the same suffix.
            backwards = [last]
            seen = {last}
            for holder in backwards:
                if holder == first:
                    continue
                for prior, available in meeting[holder].items():
                    if lengths.get(prior, -1) != lengths[holder] - 1:
                        continue
                    for name in available:
                        step = 1 << name
                        if step != marked:
                            insert(representative[holder] ^ representative[prior] ^ step, basis)
                    if prior not in seen and not (len(available) == 1 and (1 << available[0]) == marked):
                        seen.add(prior)
                        backwards.append(prior)
    return basis


def upto_five_span(meeting, allowed_dim):
    """An allowed change of at most five distinctions is a sum of simple cycles."""
    basis = elimination(binary_mask(pair) for pair in distinct_parallel(meeting))
    for first, neighbors in enumerate(meeting):
        if len(basis) == allowed_dim:
            break
        queue = deque(
            (other, (first, other), 1 << names[0])
            for other, names in neighbors.items() if other > first
        )
        while queue and len(basis) < allowed_dim:
            holder, visited, trail = queue.pop()
            for other, names in meeting[holder].items():
                if other == first:
                    if len(visited) >= 3 and visited[1] < holder:
                        insert(trail ^ (1 << names[0]), basis)
                elif other > first and other not in visited and len(visited) < 5:
                    queue.append((other, visited + (other,), trail ^ (1 << names[0])))
    return basis


def origin_check(stage, old, literal=False):
    ends, outside = wired(stage)
    meeting = adjacency(ends, outside + 1)
    kernel = tuple(new_kernels(ends, old))
    dim = len(ends) - len(elimination(binary_mask(knot) for knot in stage))
    spans = {"SHORT": short_span(meeting, dim), "UPTO5": upto_five_span(meeting, dim)}
    if literal:
        compare_literal(ends, kernel, old, spans)
    return {
        "dim Z_new": len(kernel),
        **{key: all(not remainder(change, basis) for change in kernel) for key, basis in spans.items()},
        "class dimension": {key: dim - len(basis) for key, basis in spans.items()},
    }


def compare_literal(ends, kernel, old, actual):
    names = sorted(ends)
    allowed = []
    shortest = {}
    through_name = defaultdict(list)
    for amount in range(len(names) + 1):
        for support in combinations(names, amount):
            if coordinate_parity(support, ends):
                continue
            word = binary_mask(support)
            allowed.append(word)
            for name in support:
                limit = shortest.setdefault(name, amount)
                if amount == limit:
                    through_name[name].append(word)
    literal = {
        "SHORT": elimination(word for choices in through_name.values() for word in choices),
        "UPTO5": elimination(word for word in allowed if word.bit_count() <= 5),
    }
    for key, basis in literal.items():
        assert len(basis) == len(actual[key])
        assert all(not remainder(word, actual[key]) for word in basis.values())
    old_mask = binary_mask(old)
    assert sum(word & old_mask == 0 for word in allowed) == 1 << len(kernel)
