"""Exact affine decision for a single graph-product checksum, over F2.

A point packs R_0,...,R_(n-1), T, then the independent witness bits W.
An equation (mask, rhs) means parity(mask & point) == rhs. Each graph is
simple and undirected. Product bits are computed from reports in edge order.
"""

from itertools import combinations


def normalized_edges(n, edges):
    if type(n) is not int or n < 0:
        raise ValueError("the number of reports must be a nonnegative integer")
    result = []
    seen = set()
    for edge in edges:
        u, v = edge
        if type(u) is not int or type(v) is not int or not (0 <= u < n and 0 <= v < n):
            raise ValueError("edge endpoints must be report indices")
        key = tuple(sorted((u, v)))
        if u == v or key in seen:
            raise ValueError("the graph must be simple")
        result.append(key)
        seen.add(key)
    return tuple(result)


def path(n):
    if type(n) is not int or n < 0:
        raise ValueError("invalid path size")
    return [(i, i + 1) for i in range(n - 1)]


def star(n):
    if type(n) is not int or n < 0:
        raise ValueError("invalid star size")
    return [(0, i) for i in range(1, n)]


def parity(mask):
    return mask.bit_count() % 2


def products(report, edges):
    return sum(((report >> u) & (report >> v) & 1) << i
               for i, (u, v) in enumerate(edges))


def bit_rank(vectors):
    pivots = {}
    for vector in vectors:
        if type(vector) is not int or vector < 0:
            raise ValueError("vectors must be nonnegative bit masks")
        while vector:
            column = vector.bit_length() - 1
            if column not in pivots:
                pivots[column] = vector
                break
            vector ^= pivots[column]
    return len(pivots)


def polar_rank(n, edges):
    rows = [0] * n
    for u, v in normalized_edges(n, edges):
        rows[u] |= 1 << v
        rows[v] |= 1 << u
    return bit_rank(rows)


def affine_space(width, restrictions):
    """Return None or (offset, tuple of independent directions) for all rows."""
    if type(width) is not int or width < 0:
        raise ValueError("invalid affine system width")
    rows = list(restrictions)
    for mask, rhs in rows:
        if type(mask) is not int or not 0 <= mask < (1 << width) or rhs not in (0, 1):
            raise ValueError("a row needs an in-range bit mask and a Boolean right-hand side")
    pivots = {}
    for mask, rhs in rows:
        while mask:
            pivot = mask.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (mask, rhs)
                break
            old_mask, old_rhs = pivots[pivot]
            mask ^= old_mask
            rhs ^= old_rhs
        if not mask and rhs:
            return None
    ordered = sorted(pivots)

    def complete(free_bits, homogeneous):
        point = free_bits
        for pivot in ordered:
            mask, rhs = pivots[pivot]
            value = parity(mask & point) ^ (0 if homogeneous else rhs)
            point |= value << pivot
        return point

    free = (i for i in range(width) if i not in pivots)
    return complete(0, False), tuple(complete(1 << i, True) for i in free)


def decide(n, edges, restrictions=(), free_witnesses=0):
    """Decide arbitrary affine rows on (R,T,W) when T is one quadratic total.

    Return a complete packed witness for SAT. For UNSAT indicate either an
    inconsistent affine system or a unit residual on its affine parameter
    space. The certificate in the latter case gives the offset, directions
    and number of basis-coordinate points checked.
    """
    edges = normalized_edges(n, edges)
    if type(free_witnesses) is not int or free_witnesses < 0:
        raise ValueError("invalid independent witness count")
    space = affine_space(n + 1 + free_witnesses, restrictions)
    if space is None:
        return {"status": "unsat", "certificate": "inconsistent affine rows", "points_tested": 0}
    offset, directions = space

    def candidates():
        yield offset
        for vector in directions:
            yield offset ^ vector
        for left, right in combinations(directions, 2):
            yield offset ^ left ^ right

    tested = 0
    for point in candidates():
        tested += 1
        report = point & ((1 << n) - 1)
        edge_values = products(report, edges)
        total = (point >> n) & 1
        if parity(edge_values) == total:
            return {"status": "sat", "point": point, "report": report, "products": edge_values,
                    "total": total, "witness": point >> (n + 1),
                    "affine_dimension": len(directions), "points_tested": tested}
    return {"status": "unsat", "certificate": "constant-one Boolean quadratic",
            "offset": offset, "directions": list(directions), "affine_dimension": len(directions),
            "points_tested": tested}


def reduce_3cnf(variable_count, clauses):
    """Reduce 3-CNF to a fixed path with affine rows on reports and individual products.

    A returned sparse row (indices, rhs) adds the indicated bits in F2. Packed
    positions are all reports, followed by all path products, followed by T.
    Report indices 0 through variable_count-1 carry the original assignment.
    Literals in the source use ordinary signed, one-based DIMACS indices.
    """
    if type(variable_count) is not int or variable_count < 0:
        raise ValueError("invalid number of original variables")
    clauses = tuple(tuple(clause) for clause in clauses)
    reports = variable_count + 4 * len(clauses)
    rows = []
    for slot, clause in enumerate(clauses):
        if len(clause) != 3 or any(type(literal) is not int or
                                   not 1 <= abs(literal) <= variable_count for literal in clause):
            raise ValueError("each clause must have three valid signed literals")
        start = variable_count + 4 * slot
        for position, literal in zip((start, start + 1, start + 3), clause):
            rows.append(((position, abs(literal) - 1), int(literal > 0)))
        rows.append(((start + 2, reports + start), 0))
        rows.append(((reports + start + 2,), 0))
    return {"variables": variable_count, "clauses": clauses, "reports": reports,
            "edges": tuple(path(reports)), "rows": tuple(rows),
            "total_index": reports + max(0, reports - 1)}


def extend_3cnf(instance, original):
    """Return the unique graph point meeting the affine wiring before zero pins."""
    variables = instance["variables"]
    if type(original) is not int or not 0 <= original < 1 << variables:
        raise ValueError("assignment outside the original variables")
    report = original
    for slot, clause in enumerate(instance["clauses"]):
        false = [((original >> (abs(literal) - 1)) & 1) ^ int(literal > 0)
                 for literal in clause]
        start = variables + 4 * slot
        for index, value in enumerate((false[0], false[1], false[0] & false[1], false[2])):
            report |= value << (start + index)
    edge_values = products(report, instance["edges"])
    return report | (edge_values << instance["reports"]) | (parity(edge_values) << instance["total_index"])


def decide_star(n, restrictions=(), free_witnesses=0):
    """Allow linear restrictions on all star coordinates R,P,T,W, in that order."""
    edges = star(n)
    if type(free_witnesses) is not int or free_witnesses < 0:
        raise ValueError("invalid independent witness count")
    total_index = n + len(edges)
    rows = list(restrictions)
    total_mask = ((1 << (len(edges) + 1)) - 1) << n
    for center in (0, 1) if n else (0,):
        branch = rows + [(total_mask, 0)]
        if n:
            branch.append((1, center))
        for j, (_, leaf) in enumerate(edges):
            mask = 1 << (n + j)
            if center:
                mask |= 1 << leaf
            branch.append((mask, 0))
        space = affine_space(total_index + 1 + free_witnesses, branch)
        if space is not None:
            return {"status": "sat", "point": space[0], "center": center}
    return {"status": "unsat"}


def quadratic_signed_sum(dimension, value):
    """Compute sum (-1)^value(u) for a promised degree-at-most-two Boolean function."""
    constant = value(0)
    linear = 0
    neighbors = [0] * dimension
    single = [value(1 << i) for i in range(dimension)]
    for i in range(dimension):
        linear |= (constant ^ single[i]) << i
        for j in range(i):
            if constant ^ single[i] ^ single[j] ^ value((1 << i) | (1 << j)):
                neighbors[i] |= 1 << j
                neighbors[j] |= 1 << i
    active = (1 << dimension) - 1
    factor = 1
    for i in range(dimension):
        if not (active >> i) & 1 or not neighbors[i] & active:
            continue
        available = neighbors[i] & active
        j = (available & -available).bit_length() - 1
        active ^= (1 << i) | (1 << j)
        a, b = neighbors[i] & active, neighbors[j] & active
        a0, b0 = (linear >> i) & 1, (linear >> j) & 1
        # Summing (-1)^(xy + x A + y B) over x,y gives 2*(-1)^(A B).
        constant ^= a0 & b0
        linear ^= (b if a0 else 0) ^ (a if b0 else 0) ^ (a & b)
        for h in range(dimension):
            if (active >> h) & 1:
                row = (b if (a >> h) & 1 else 0) ^ (a if (b >> h) & 1 else 0)
                neighbors[h] ^= row & ~(1 << h)
        factor *= 2
    if linear & active:
        return 0
    return (-1 if constant else 1) * factor * (1 << active.bit_count())


def count_product_rows(n, edges, restrictions=(), free_witnesses=0):
    """Count assignments for arbitrary affine rows on R,P,T,W in 2^k poly(input).

    k is the rank of their product coefficients after replacing T by sum(P).
    Each reports-and-witnesses assignment gives one ambient graph point.
    """
    edges = normalized_edges(n, edges)
    if type(free_witnesses) is not int or free_witnesses < 0:
        raise ValueError("invalid independent witness count")
    total_index = n + len(edges)
    lower = (1 << n) - 1
    all_edges = (1 << len(edges)) - 1
    pivots = {}
    affine = []
    for mask, rhs in restrictions:
        if type(mask) is not int or not 0 <= mask < 1 << (total_index + 1 + free_witnesses) or rhs not in (0, 1):
            raise ValueError("invalid full-coordinate affine row")
        quadratic = (mask >> n) & all_edges
        if (mask >> total_index) & 1:
            quadratic ^= all_edges
        linear = (mask & lower) | ((mask >> (total_index + 1)) << n)
        while quadratic:
            pivot = quadratic.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = (quadratic, linear, rhs)
                break
            old_quadratic, old_linear, old_rhs = pivots[pivot]
            quadratic ^= old_quadratic
            linear ^= old_linear
            rhs ^= old_rhs
        if not quadratic:
            affine.append((linear, rhs))
    independent = tuple(pivots.values())
    space = affine_space(n + free_witnesses, affine)
    if space is None:
        return {"count": 0, "product_rank": len(independent), "scalar_sums": 0}
    offset, directions = space
    dimension = len(directions)

    def unpack(params):
        point = offset
        while params:
            bit = params & -params
            point ^= directions[bit.bit_length() - 1]
            params ^= bit
        return point

    numerator = 0
    for choice in range(1 << len(independent)):
        q, linear, rhs = 0, 0, 0
        for i, (qi, li, bi) in enumerate(independent):
            if (choice >> i) & 1:
                q ^= qi
                linear ^= li
                rhs ^= bi

        def residual(params):
            point = unpack(params)
            return rhs ^ parity(linear & point) ^ parity(q & products(point & lower, edges))

        numerator += quadratic_signed_sum(dimension, residual)
    divisor = 1 << len(independent)
    if numerator < 0 or numerator % divisor:
        raise ArithmeticError("the signed sums did not give a nonnegative count")
    return {"count": numerator // divisor, "product_rank": len(independent),
            "scalar_sums": divisor, "affine_dimension": dimension}
