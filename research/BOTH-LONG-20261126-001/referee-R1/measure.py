"""Exact read and change distances for a finite list of parity knots."""
from collections import defaultdict, deque
import numpy as np


def bits(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def parity(a, b):
    return (a & b).bit_count() % 2


def independent(words):
    rows = {}
    for w in words:
        while w:
            p = w.bit_length() - 1
            if p not in rows:
                rows[p] = w
                break
            w ^= rows[p]
    return rows


def kernel(rows, count):
    reduced = independent(rows)
    basis = []
    for i in range(count):
        if i not in reduced:
            w = 1 << i
            for p, row in sorted(reduced.items()):
                w |= parity(w, row) << p
            basis.append(w)
    return basis


def combinations_of(basis):
    """Enumerate a binary span in reflected order, including zero."""
    w = 0
    yield w
    for i in range(1, 1 << len(basis)):
        w ^= basis[(i & -i).bit_length() - 1]
        yield w


def incidence(knots, pinned):
    owners = defaultdict(list)
    for i, knot in enumerate(knots):
        assert len(set(knot)) == len(knot)
        for d in knot:
            owners[d].append(i)
    assert all(len(v) in (1, 2) for v in owners.values())
    names = sorted(d for d, v in owners.items() if len(v) == 2 or not pinned)
    pairs = []
    for d in names:
        v = owners[d]
        pairs.append((v[0], v[1] if len(v) == 2 else len(knots)))
    rows = [0] * len(knots)
    adj = [[] for _ in range(len(knots) + int(not pinned))]
    for j, (a, b) in enumerate(pairs):
        rows[a] |= 1 << j
        if b < len(knots):
            rows[b] |= 1 << j
        adj[a].append((b, j))
        adj[b].append((a, j))
    return names, pairs, rows, adj


def moves_through(pairs, adj):
    """Remove one distinction, then follow every shortest return to its other holder."""
    moves = set()
    ties = []
    for j, (a, b) in enumerate(pairs):
        depth = {a: 0}
        q = deque([a])
        while q:
            u = q.popleft()
            if u == b:
                break
            for v, k in adj[u]:
                if k != j and v not in depth:
                    depth[v] = depth[u] + 1
                    q.append(v)
        stack = [(b, 1 << j)] if b in depth else []
        count = 0
        while stack:
            u, w = stack.pop()
            if u == a:
                moves.add(w)
                count += 1
                continue
            for v, k in adj[u]:
                if k != j and depth.get(v) == depth[u] - 1:
                    stack.append((v, w | (1 << k)))
        ties.append(count)
    return moves, max(ties, default=0)


def signed_return(adj, character, forbidden=None):
    """Breadth first search of holder and accumulated parity, from each holder."""
    best = None
    for start in range(len(adj)):
        queue = deque([(start, 0, 0)])
        seen = {(start, 0)}
        while queue:
            u, s, w = queue.popleft()
            for v, k in adj[u]:
                if k == forbidden:
                    continue
                t = s ^ ((character >> k) & 1)
                if (v, t) in seen:
                    continue
                seen.add((v, t))
                new = w ^ (1 << k)
                if v == start and t == 1:
                    if best is None or new.bit_count() < best.bit_count():
                        best = new
                    queue.clear()
                    break
                queue.append((v, t, new))
    return best


def minimum_label(pairs, character):
    """Minimize |character + sum of chosen holder rows| by binary variable elimination."""
    if not pairs:
        return 0, 0, 0
    degree = defaultdict(int)
    for a, b in pairs:
        degree[a] += 1
        degree[b] += 1
    fixed = max(degree, key=degree.get)
    factors = []
    for j, (a, b) in enumerate(pairs):
        c = (character >> j) & 1
        scope = tuple(sorted({a, b} - {fixed}))
        table = [c, 1 - c] if len(scope) == 1 else [[c, 1 - c], [1 - c, c]]
        factors.append((scope, np.array(table, dtype=np.int32)))
    variables = set(degree) - {fixed}
    max_width = 0
    choices = []
    while variables:
        neighbours = {v: set() for v in variables}
        for scope, _ in factors:
            for v in scope:
                neighbours[v].update(scope)
        v = min(variables, key=lambda u: (len(neighbours[u]), u))
        joint = tuple(sorted(neighbours[v]))
        max_width = max(max_width, len(joint))
        if len(joint) > 22:
            raise ValueError("referee memory limit on a minimization table")
        terms = []
        keep = []
        for scope, table in factors:
            if v in scope:
                terms.append(table.reshape(tuple(2 if u in scope else 1 for u in joint)))
            else:
                keep.append((scope, table))
        summed = sum(terms)
        remaining = tuple(u for u in joint if u != v)
        axis = joint.index(v)
        choices.append((v, remaining, summed.argmin(axis=axis)))
        keep.append((remaining, summed.min(axis=axis)))
        factors = keep
        variables.remove(v)
    assignment = {fixed: 0}
    for v, scope, best_bit in reversed(choices):
        assignment[v] = int(best_bit[tuple(assignment[u] for u in scope)])
    witness = character
    for j, (a, b) in enumerate(pairs):
        witness ^= (assignment[a] ^ assignment[b]) << j
    optimum = sum(int(t) for _, t in factors)
    assert witness.bit_count() == optimum
    return optimum, max_width, witness


def enumerate_changes(space, count, moves, characters):
    """Independent two-pass check of every per-distinction tie and the least change."""
    seen_by_size = defaultdict(int)
    for w in combinations_of(space):
        seen_by_size[w.bit_count()] |= w
    by_size = {}
    seen = 0
    for size, union in sorted(seen_by_size.items()):
        by_size[size] = union & ~seen
        seen |= union
    found = set()
    best = None
    for w in combinations_of(space):
        size = w.bit_count()
        if by_size.get(size, 0) & w:
            found.add(w)
        if (best is None or size < best) and any(parity(w, z) for z in characters):
            best = size
    assert found == moves
    return best


def measure(knots, pinned, old_names=(), enum_limit=22):
    names, pairs, laws, adj = incidence(knots, pinned)
    count = len(names)
    space = kernel(laws, count)
    moves, most_ties = moves_through(pairs, adj)
    move_basis = independent(sorted(moves))
    assert all(not any(parity(w, r) for r in laws) for w in moves)
    labels = kernel(moves, count)
    # Restrict each move-invariant parity to the allowed changes.
    # An independent set of these restrictions detects every nonzero class.
    chars = []
    signatures = []
    for z in labels:
        sig = sum(parity(z, w) << i for i, w in enumerate(space))
        if len(independent([*signatures, sig])) > len(signatures):
            signatures.append(sig)
            chars.append(z)
    assert len(chars) == len(space) - len(move_basis)
    changes = [signed_return(adj, z) for z in chars]
    best = min(changes, key=int.bit_count) if changes else None
    dc = best.bit_count() if best is not None else None
    if best is not None:
        assert all(not parity(best, row) for row in laws) and any(parity(best, z) for z in chars)
    read_results = [minimum_label(pairs, z) for z in combinations_of(chars) if z]
    read_winner = min(read_results, default=None)
    dr = read_winner[0] if read_winner is not None else None
    if read_winner is not None:
        witness = read_winner[2]
        assert all(not parity(witness, h) for h in moves) and any(parity(witness, v) for v in space)
    change_enum = len(space) <= enum_limit
    label_enum = len(labels) <= enum_limit
    if change_enum:
        assert enumerate_changes(space, count, moves, chars) == dc
    if label_enum:
        # Each invariant parity already vanishes on the moves. Test one
        # representative of each independent class direction.
        evaluations = []
        representatives = []
        for s in space:
            sig = sum(parity(z, s) << i for i, z in enumerate(chars))
            if len(independent([*evaluations, sig])) > len(evaluations):
                evaluations.append(sig)
                representatives.append(s)
        assert len(representatives) == len(chars)
        direct = min((w.bit_count() for w in combinations_of(labels)
                      if any(parity(w, v) for v in representatives)), default=None)
        assert direct == dr
    out = dict(knots=len(knots), distinctions=count, allowed_rank=len(space), move_rank=len(move_basis),
               classes=1 << len(chars), moves=len(moves), max_ties=most_ties,
               read=dr, change=dc, allowed_enumerated=(1 << len(space)) if change_enum else 0,
               invariant_parities_enumerated=(1 << len(labels)) if label_enum else 0,
               largest_read_table_variables=max((v for _, v, _ in read_results), default=0))
    if read_winner is not None:
        out['least_read_distinctions'] = [names[i] for i in bits(read_winner[2])]
        out['least_change_distinctions'] = [names[i] for i in bits(best)]
    if old_names:
        old = sum(1 << names.index(d) for d in old_names)
        old_allowed = all(not parity(old, row) for row in laws)
        old_changes = old_allowed and any(parity(old, z) for z in chars)
        old_labels = all(not parity(old, w) for w in moves) and any(parity(old, v) for v in space)
        out.update(old_allowed=old_allowed, old_changes_class=old_changes, old_labels_class=old_labels)
        # A change or label of the same size may use a different set of distinctions.
        if old_changes and dc == len(old_names):
            alternatives = [signed_return(adj, z, forbidden=names.index(old_names[0])) for z in chars]
            alt = next((w for w in alternatives if w is not None and w.bit_count() == dc), None)
            if alt is not None:
                out['another_least_change'] = [names[i] for i in bits(alt)]
    return out
