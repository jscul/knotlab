"""Proof-order controls, raw truth tables and inconsistent-cycle extraction."""
from collections import deque, namedtuple
from itertools import combinations, product


Path = namedtuple("Path", "start end report")


def walk_cycle(h, arrivals, builder):
    """Consume edge IDs once. An incoming edge reaches the proof before its neighbors are merged."""
    if type(h) is not int or h < 3:
        raise ValueError("a simple cycle needs at least three checks")
    starts, ends, seen = {}, {}, set()
    output, trace = None, []
    joins = 0

    def forget(path):
        del starts[path.start]
        del ends[path.end]

    for e in arrivals:
        if type(e) is not int or not 0 <= e < h or e in seen:
            raise ValueError("invalid or repeated check")
        seen.add(e)
        u, v = e, (e+1) % h
        new = builder.edge(e)
        left, right = ends.get(u), starts.get(v)
        merges = 0
        if left is not None and left is right:
            if len(seen) != h:
                raise AssertionError("a proper subset cannot close a simple cycle")
            output = builder.close(left.report, new)
            forget(left)
        else:
            if left is not None:
                forget(left)
                new = builder.join(left.report, new)
                u = left.start
                merges += 1
            if right is not None:
                forget(right)
                new = builder.join(new, right.report)
                v = right.end
                merges += 1
            starts[u] = ends[v] = Path(u, v, new)
        joins += merges
        trace.append({"arrival": e, "joins": merges, "components": len(starts)})
    if len(seen) != h:
        raise ValueError("incomplete cycle")
    if starts or ends or joins != h-2:
        raise AssertionError("incorrect number of path deductions")
    return output, {"joins": joins, "peak_components": max(t["components"] for t in trace),
                    "events": trace}


def forbidden_count(k, charge):
    if type(k) is not int or k < 0 or charge not in (0, 1):
        raise ValueError("invalid number of surviving reports or charge")
    difference = 3 * 6**k + 2**k
    return (4 * 8**k - (1 if charge == 0 else -1) * difference) // 2


def prefix_costs(charges, arrivals):
    """Full-table size of one XOR consequence after each accepted addition."""
    exposed, current = set(), 0
    seen, rows = set(), []
    for e in arrivals:
        if type(e) is not int or not 0 <= e < len(charges) or e in seen:
            raise ValueError("invalid or repeated check")
        seen.add(e)
        exposed.symmetric_difference_update((e, (e+1) % len(charges)))
        current ^= charges[e]
        rows.append({"edge": e, "boundary": sorted(exposed), "charge": current,
                     "forbidden_rows": forbidden_count(len(exposed), current)})
    if len(seen) != len(charges):
        raise ValueError("incomplete cycle")
    return rows


def pair_fibers():
    """Exact Boolean evaluation matrix for all 37 squarefree monomials of degree <=2."""
    monomials = [(), *((i,) for i in range(8)), *combinations(range(8), 2)]
    pivots, counts = [{}, {}], [0, 0]
    for bits in product((0, 1), repeat=8):
        a, b, x, y, z, xx, yy, zz = bits
        value = (z & ((x & y) ^ (a & b))) ^ (zz & ((xx & yy) ^ (a & b)))
        row = sum(1 << j for j, m in enumerate(monomials) if all(bits[i] for i in m))
        if value and (1 ^ z) * (1 ^ zz):
            raise AssertionError("an odd assignment broke its quadratic consequence")
        counts[value] += 1
        basis = pivots[value]
        while row:
            col = row.bit_length() - 1
            if col not in basis:
                basis[col] = row
                break
            row ^= basis[col]
    return [{"value": i, "assignments": counts[i], "quadratic_rank": len(pivots[i]),
             "nullity": len(monomials)-len(pivots[i])} for i in (0, 1)]


def pair_graph(h, checks):
    """Return feasible report bits or an oriented list of original edge IDs with odd total charge."""
    if type(h) is not int or h < 0:
        raise ValueError("invalid report count")
    neighbors = [[] for _ in range(h)]
    pairs = set()
    for e, (u, v, c) in enumerate(checks):
        if (type(u) is not int or type(v) is not int or not 0 <= u < h
                or not 0 <= v < h or u == v or c not in (0, 1)):
            raise ValueError("invalid pair check")
        pair = (min(u, v), max(u, v))
        if pair in pairs:
            raise ValueError("expected a simple graph of pair checks")
        pairs.add(pair)
        neighbors[u].append((v, e, c))
        neighbors[v].append((u, e, c))

    def orient(e, start):
        return (e, checks[e][0] != start)

    label, parent = [None] * h, [None] * h
    for root in range(h):
        if label[root] is not None:
            continue
        label[root] = 0
        todo = deque([root])
        while todo:
            u = todo.popleft()
            for v, e, c in neighbors[u]:
                if label[v] is None:
                    label[v], parent[v] = label[u] ^ c, (u, e)
                    todo.append(v)
                    continue
                if label[v] == label[u] ^ c:
                    continue
                # Trace u and v to their first common tree ancestor.
                up, ancestor, mark = [], u, {u: 0}
                while parent[ancestor] is not None:
                    p, f = parent[ancestor]
                    up.append(orient(f, ancestor))
                    ancestor = p
                    mark[ancestor] = len(up)
                down, ancestor = [], v
                while ancestor not in mark:
                    p, f = parent[ancestor]
                    down.append(orient(f, p))
                    ancestor = p
                cycle = up[:mark[ancestor]] + list(reversed(down)) + [orient(e, v)]
                return {"cycle": cycle}
    return {"values": label}


def signed_model(encoded, values):
    """Extend feasible report bits to an assignment of every original and private strict bit."""
    if len(values) != len(encoded["triples"]) or any(v not in (0, 1) for v in values):
        raise ValueError("invalid report assignment")
    bits = [0] * (encoded["n"]+1)
    for v, (x, y, z) in zip(values, encoded["triples"]):
        bits[x], bits[y], bits[z] = 1, v, 1
    for block in encoded["blocks"]:
        if (values[block["i"]] ^ values[block["j"]]) != block["charge"]:
            raise ValueError("inconsistent reports")
        for row in block["rows"]:
            clause = row["clause"]
            def true(literal):
                return bool(bits[abs(literal)]) == (literal > 0)
            prefix = true(clause[0])
            for j, aux in enumerate(row["aux"]):
                prefix = prefix or true(clause[j+1])
                bits[aux] = int(not prefix)
    if not all(any(bool(bits[abs(l)]) == (l > 0) for l in clause) for clause in encoded["cnf"]):
        raise AssertionError("strict input does not accept the model")
    return bits


def graph_proof(cycle, builder):
    """Replay using the actual oriented blocks of the full strict formula."""
    if len(cycle) < 3:
        raise ValueError("expected a simple inconsistent cycle")
    e, reverse = cycle[0]
    path = builder.edge(e, reverse=reverse)
    for e, reverse in cycle[1:-1]:
        path = builder.join(path, builder.edge(e, reverse=reverse))
    e, reverse = cycle[-1]
    return builder.close(path, builder.edge(e, reverse=reverse))


def three_report_control():
    checks = [(0, 1, 2), (0, 3, 4), (1, 3, 5), (2, 4, 5)]
    charges = (0, 0, 0, 1)
    solutions_after_deletion = [0] * len(checks)
    solutions = 0
    for values in product((0, 1), repeat=6):
        failed = [i for i, row in enumerate(checks)
                  if sum(values[j] for j in row) % 2 != charges[i]]
        if not failed:
            solutions += 1
        elif len(failed) == 1:
            solutions_after_deletion[failed[0]] += 1
    pair_sums = [len(set(a) ^ set(b)) for a, b in combinations(checks, 2)]
    return {"three_report_checks": checks, "charges": charges, "solutions": solutions,
            "models_after_single_deletion": solutions_after_deletion, "pair_sum_supports": pair_sums}
