"""Tests for connected cyclic meeting patterns. Uses only the standard library."""
import argparse
import itertools
import json
import resource
import time
from collections import deque
from pathlib import Path

HERE = Path(__file__).resolve().parent


def mask(items):
    return sum(1 << i for i in items)


def pivots(vectors):
    basis = {}
    for v in vectors:
        while v and v.bit_length() in basis:
            v ^= basis[v.bit_length()]
        if v:
            basis[v.bit_length()] = v
    return list(basis.values())


def kernel(rows, width):
    """Dependent subsets of columns give a basis of allowed changes."""
    reduced = {}
    free = []
    for i in range(width):
        col = mask(k for k, r in enumerate(rows) if i in r)
        witness = 1 << i
        while col and col.bit_length() in reduced:
            other, taken = reduced[col.bit_length()]
            col ^= other
            witness ^= taken
        if col:
            reduced[col.bit_length()] = col, witness
        else:
            free.append(witness)
    return free


def restrictions(vectors, names):
    selected = mask(names)
    return len(pivots(v & selected for v in vectors))


def legal_moves(rows):
    owners = {}
    for i, row in enumerate(rows):
        for x in row:
            owners.setdefault(x, []).append(i)
    links = {x: tuple(w if len(w) == 2 else [*w, len(rows)]) for x, w in owners.items()}
    adjacency = [[] for _ in range(len(rows) + 1)]
    for x, (a, b) in links.items():
        adjacency[a].append((b, x))
        adjacency[b].append((a, x))
    changes = set()
    for x, (a, b) in links.items():
        depth = {a: 0}
        predecessor = {}
        todo = deque([a])
        while todo:
            k = todo.popleft()
            if b in depth and depth[k] >= depth[b]:
                break
            for w, d in adjacency[k]:
                if d == x:
                    continue
                if w not in depth:
                    depth[w] = depth[k] + 1
                    todo.append(w)
                if depth[w] == depth[k] + 1:
                    predecessor.setdefault(w, []).append((k, d))
        if b in depth:
            paths = [(b, 1 << x)]
            while paths:
                k, v = paths.pop()
                if k == a:
                    changes.add(v)
                else:
                    paths.extend((w, v | (1 << d)) for w, d in predecessor[k])
    return changes


def pattern(n):
    rows = [[] for _ in range(n*n)]
    for i, j in itertools.product(range(n), repeat=2):
        k = n*i + j
        for x, target in ((2*k, n*((i+1) % n)+j), (2*k+1, n*i+(j+1) % n)):
            rows[k].append(x)
            rows[target].append(x)
    return rows


def stage(old, live, extra):
    """One loose distinction per named old holder. No two holders have a common neighbour."""
    rows = [r.copy() for r in old]
    friends = [{j for j, s in enumerate(old) if i != j and set(r) & set(s)}
               for i, r in enumerate(old)]
    assert all(not (friends[a] & friends[b]) for a, b in itertools.combinations(live, 2))
    assert len(live) >= 2
    next_name = max(x for r in rows for x in r) + 1
    for i, k in enumerate(live):
        rows[k].append(next_name+i)
    if extra:
        # Single-parent births, distinct parents. No subsequent shared-parent demand.
        # Each consumed input is open, so each birth needs two fresh distinctions.
        first = next_name + len(live)
        rows += [[next_name+i, first+2*i, first+2*i+1] for i in range(len(live))]
    return rows


def observe(rows, labels):
    width = max(x for r in rows for x in r) + 1
    allowed = kernel(rows, width)
    moves = legal_moves(rows)
    for row in rows:
        s = mask(row)
        assert all((s & v).bit_count() % 2 == 0 for v in moves)
    move_basis = pivots(moves)
    projected = [restrictions(allowed, r) for r in rows]
    read = [a - restrictions(move_basis, r) for r, a in zip(rows, projected)]
    def evaluated(x):
        return mask(i for i, f in enumerate(labels) if (x & f).bit_count() % 2)
    return {
        "knots": len(rows), "distinctions": width, "allowed_rank": len(allowed),
        "move_rank": len(move_basis), "distinct_shortest_changes": len(moves),
        "class_bits": len(allowed) - len(move_basis),
        "one_knot_read_ranks": read, "projection_ranks": projected,
        "all_supports_pass_K1_K3": all(a == len(r)-1 for r, a in zip(rows, projected)),
        "distinctions_reached_by_moves": len(set(i for i in range(width) if any((v >> i) & 1 for v in move_basis))),
        "two_named_parities_on_allowed_rank": len(pivots(map(evaluated, allowed))),
        "two_named_parities_on_moves_rank": len(pivots(map(evaluated, moves))),
    }


def study(n, live):
    rows = pattern(n)
    # Two parity reads, one for each addition modulo n with a carry.
    labels = [mask(2*(n*(n-1)+j) for j in range(n)), mask(2*(n*i+n-1)+1 for i in range(n))]
    src, end = (stage(rows, live, extra) for extra in (False, True))
    visits = [observe(r, labels) for r in (src, end)]
    assert all(a["all_supports_pass_K1_K3"] for a in visits)
    return {"order": n, "single_loose_holders": live, "source": visits[0], "grown": visits[1],
            "two_parity_supports": [[i for i in range(2*n*n) if f >> i & 1] for f in labels]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--pilot", action="store_true")
    args = ap.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1 << 30, 1 << 30))
    t = time.monotonic()
    # n=4 provides the control where a whole period ties a four-distinction change.
    cases = [(n, [0, 1]) for n in (5, 4, 6, 7)]
    cases += [(n, [0, 1, n*(n//2)+2]) for n in (5, 6, 7)]
    cases += [(n, [0, n*(n//2) + n//2]) for n in (5, 6, 7)]
    result = [study(n, slots) for n, slots in (cases[:1] if args.pilot else cases)]
    output = {"purpose": "Targeted start with two independent inherited parity reads. Successors add one modulo the chosen order to one of two indices.",
              "cases": result, "seconds": round(time.monotonic()-t, 5)}
    out = "periodic_pilot.json" if args.pilot else "periodic.json"
    (HERE/out).write_text(json.dumps(output, indent=2)+"\n")
    for row in result:
        print(row["order"],row["single_loose_holders"],
              [(s["class_bits"],max(s["one_knot_read_ranks"]),s["two_named_parities_on_moves_rank"]) for s in [row["source"],row["grown"]]])

if __name__ == "__main__":
    main()
