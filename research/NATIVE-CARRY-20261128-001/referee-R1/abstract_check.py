"""Count finite meeting patterns and their whole choices from their holder lists."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import lru_cache
from itertools import combinations, permutations, product
import json
from math import comb, factorial
from pathlib import Path
import random
import resource
import time


HERE = Path(__file__).resolve().parent
K4 = "four mutually meeting knots"
K23 = "two knots each meeting the same three"


@lru_cache(maxsize=None)
def pairs(n):
    return tuple(combinations(range(n), 2))


def matrix(n, meetings):
    values = [[0] * n for _ in range(n)]
    for (a, b), count in meetings:
        values[a][b] = values[b][a] = count
    return tuple(map(tuple, values))


def canonical(m):
    """An exact relabelling key by refinement and individualization."""
    def search(parts):
        while True:
            refined = []
            for part in parts:
                groups = defaultdict(list)
                for u in part:
                    signature = tuple(tuple(sorted(m[u][v] for v in p)) for p in parts)
                    groups[signature].append(u)
                refined.extend(tuple(groups[key]) for key in sorted(groups))
            if len(refined) == len(parts):
                break
            parts = refined
        choices = [(len(part), i) for i, part in enumerate(parts) if len(part) > 1]
        if not choices:
            order = [part[0] for part in parts]
            return bytes(m[order[a]][order[b]] for a, b in pairs(len(m)))
        _, i = min(choices)
        part = parts[i]
        checked = []
        keys = []
        for u in part:
            # Swapping a pair with identical meetings to every third knot is
            # an exact symmetry fixing all other knots.
            if any(all(m[u][w] == m[v][w] for w in range(len(m)) if w not in (u, v))
                   for v in checked):
                continue
            checked.append(u)
            rest = tuple(v for v in part if v != u)
            keys.append(search(parts[:i] + [(u,), rest] + parts[i + 1:]))
        return min(keys)

    return search([tuple(range(len(m)))])


def extend(previous, maximum):
    """Deleting a knot with least total always gives a member of the preceding size."""
    n = len(next(iter(previous.values()))) + 1
    extensions = tuple((weights, sum(weights))
                       for weights in product(range(maximum + 1), repeat=n - 1))
    result = {}
    tried = 0
    for m in previous.values():
        totals = tuple(map(sum, m))
        for weights, total in extensions:
            if any(total > d + weight for d, weight in zip(totals, weights)):
                continue
            larger = tuple(row + (w,) for row, w in zip(m, weights)) + (weights + (0,),)
            tried += 1
            key = canonical(larger)
            if key not in result:
                result[key] = larger
    return result, tried


def orbit_total(n, colours):
    """Burnside's lemma counts classes without using any generated representative."""
    positions = {p: i for i, p in enumerate(pairs(n))}
    fixed = 0
    for order in permutations(range(n)):
        remaining = set(range(len(positions)))
        cycles = 0
        while remaining:
            pos = next(iter(remaining))
            cycles += 1
            while pos in remaining:
                remaining.remove(pos)
                u, v = pairs(n)[pos]
                pos = positions[tuple(sorted((order[u], order[v])))]
        fixed += colours ** cycles
    return fixed // factorial(n)


@dataclass(frozen=True)
class Cell:
    a: int
    b: int
    c: int
    d: int
    copies: int
    knots: int
    cross: int


def build_cells(m):
    cells = []
    n = len(m)
    coverage = [[0] * n for _ in range(n)]
    for h, i, j, k in combinations(range(n), 4):
        mask = (1 << h) + (1 << i) + (1 << j) + (1 << k)
        for a, b, c, d in ((h, i, j, k), (h, j, i, k), (h, k, i, j)):
            copies = m[a][b] * m[c][d]
            if not copies:
                continue
            cross = 0
            for s, t in ((a, c), (a, d), (b, c), (b, d)):
                u, v = sorted((s, t))
                coverage[u][v] += copies
                cross |= 1 << (n * u + v)
            cells.append(Cell(a, b, c, d, copies, mask, cross))
    return cells, coverage


def formula_errors(m, coverage):
    totals = tuple(map(sum, m))
    errors = 0
    for u, v in pairs(len(m)):
        value = ((totals[u] - m[u][v]) * (totals[v] - m[u][v])
                 - sum(a * b for a, b in zip(m[u], m[v])))
        errors += coverage[u][v] != value
    return errors


def sign(cells, order):
    # Each cell contributes one precisely when exactly one holder of the
    # second distinction lies between the holders of the first.
    rank = {u: i for i, u in enumerate(order)}
    value = 0
    for cell in cells:
        if cell.copies % 2:
            left, right = sorted((rank[cell.a], rank[cell.b]))
            value ^= (left < rank[cell.c] < right) ^ (left < rank[cell.d] < right)
    return value


def word_sign(m, order):
    # Multiply in knot order, then cancel equal distinctions. Moving a copy
    # past a distinction with disjoint holders costs one change of sign.
    held = [{u, v} for u, v in pairs(len(m)) for _ in range(m[u][v])]
    word = [i for knot in order for i, h in enumerate(held) if knot in h]
    cost = 0
    while word:
        first = word.pop(0)
        stop = word.index(first)
        cost += sum(held[first].isdisjoint(held[other]) for other in word[:stop])
        del word[stop]
    return cost % 2


def nonempty_commuting(cells):
    cross = 0
    for c in cells:
        if c.copies % 2:
            cross ^= c.cross
    return bool(cells) and not cross


def subsets(cells, n):
    """Every nonempty commuting subset and its sign, with no pruning."""
    found = {}
    for size in range(4, n + 1):
        for subset in combinations(range(n), size):
            mask = sum(1 << u for u in subset)
            choice = [c for c in cells if c.knots & mask == c.knots]
            if nonempty_commuting(choice):
                found[mask] = sign(choice, subset)
    return found


def minima(found):
    return {s: value for s, value in found.items()
            if all(t == s or t & s != t for t in found)}


def active_pattern(m, cells):
    used = {(a, b) for c in cells for a, b in ((c.a, c.b), (c.c, c.d))}
    active = matrix(len(m), [(pair, m[pair[0]][pair[1]]) for pair in used])
    inert = sum(m[a][b] for a, b in pairs(len(m)) if (a, b) not in used)
    return active, inert


def named_patterns():
    a = matrix(4, [(p, 1) for p in pairs(4)])
    b = matrix(5, [((u, v), 1) for u in (0, 1) for v in (2, 3, 4)])
    return {a: K4, b: K23}


KIND_KEYS = {canonical(m): kind for m, kind in named_patterns().items()}


def kind(active):
    if len(active) not in (4, 5):
        return "other"
    return KIND_KEYS.get(canonical(active), "other")


def listing(m):
    return [[u, v, m[u][v]] for u, v in pairs(len(m)) if m[u][v]]


def checked_orders(m, cells, coverage, rng):
    n = len(m)
    base = list(range(n))
    first = sign(cells, base)
    orders = [base, rng.sample(base, n), rng.sample(base, n)]
    for i in range(n - 1):
        swapped = base.copy()
        swapped[i], swapped[i + 1] = swapped[i + 1], swapped[i]
        assert sign(cells, swapped) ^ first == coverage[i][i + 1] % 2
        orders.append(swapped)
    # An arbitrary pair can be next to each other in some order. Check its
    # exchange there, even when the candidates do not commute.
    for u, v in pairs(n):
        rest = [w for w in base if w not in (u, v)]
        before = sign(cells, [u, v] + rest)
        after = sign(cells, [v, u] + rest)
        assert before ^ after == coverage[u][v] % 2
    for order in orders:
        assert sign(cells, order) == word_sign(m, order)
        if nonempty_commuting(cells):
            assert sign(cells, order) == first
    return len(orders)


def no_interleavings(cells, n):
    # Circular order with one knot fixed. A zero count is the literature's
    # outerplanarity criterion for a simple meeting pattern.
    for rest in permutations(range(1, n)):
        order = (0, *rest)
        rank = {u: i for i, u in enumerate(order)}
        for c in cells:
            left, right = sorted((rank[c.a], rank[c.b]))
            if (left < rank[c.c] < right) ^ (left < rank[c.d] < right):
                break
        else:
            return list(order)
    return None


def audit_size(classes, n, doubled, rng):
    rows = []
    stats = Counter()
    example = None
    for key, m in classes.items():
        if doubled and (2 not in key or not all(map(any, m))):
            continue
        stats["patterns"] += 1
        stats["patterns with an isolated knot"] += not all(map(any, m))
        cells, coverage = build_cells(m)
        stats["formula comparisons"] += comb(n, 2)
        assert not formula_errors(m, coverage)
        base = list(range(n))
        assert sign(cells, base) == word_sign(m, base)
        stats["whole choices checked by word cancellation"] += 1
        if not nonempty_commuting(cells):
            continue
        whole_sign = sign(cells, base)
        stats["whole-choice sets"] += 1
        stats["odd whole-choice sets"] += whole_sign
        stats["orders on whole-choice sets"] += checked_orders(m, cells, coverage, rng)
        stats["pair exchanges on whole-choice sets"] += comb(n, 2)
        found = subsets(cells, n)
        smallest = minima(found)
        if whole_sign and not any(smallest.values()):
            stats["odd whole sets with only even minimal sets"] += 1
            if example is None:
                example = {"knots": n, "meetings": listing(m), "cells": sum(c.copies for c in cells),
                           "all whole subsets": {str(mask): s for mask, s in found.items()}}
        if len(found) != 1:
            continue
        active, inert = active_pattern(m, cells)
        used = [m[a][b] for a, b in pairs(n) if active[a][b]]
        observed = [coverage[a][b] for a, b in pairs(n)]
        row = {"key": key.hex(), "meetings": listing(m), "knots": n, "distinctions": sum(key),
               "kind": kind(active), "cells": sum(c.copies for c in cells), "sign": whole_sign,
               "inert distinctions": inert, "active repeated meeting": max(used) > 1,
               "max coverage": max(observed), "covered twice": set(observed) <= {0, 2}}
        if not doubled and n <= 7:
            order = no_interleavings(cells, n)
            row["order with zero interleavings"] = order
            assert order is None or not whole_sign
        rows.append(row)
    return rows, dict(sorted(stats.items())), example


def fixtures():
    patterns = {kind: m for m, kind in named_patterns().items()}
    patterns["ring of five with a knot meeting all five"] = matrix(
        6, [((u, (u + 1) % 5), 1) for u in range(5)] + [((u, 5), 1) for u in range(5)])
    patterns["ring of four"] = matrix(4, [((u, (u + 1) % 4), 1) for u in range(4)])
    patterns["ring of three with a separate meeting"] = matrix(
        5, [((0, 1), 1), ((1, 2), 1), ((0, 2), 1), ((3, 4), 1)])
    doubled = matrix(4, [((0, 1), 2), ((2, 3), 1)])
    patterns["doubled meeting with a separate meeting"] = doubled
    patterns["same pattern reduced modulo two"] = matrix(4, [((2, 3), 1)])
    patterns["four mutually meeting knots with one meeting tripled"] = matrix(
        4, [(pair, 3 if pair == (0, 1) else 1) for pair in pairs(4)])
    patterns["two knots each meeting the same three, with two distinctions between two of the three"] = matrix(
        5, [((u, v), 1) for u in (0, 1) for v in (2, 3, 4)] + [((2, 3), 2)])
    # The literature's Petersen graph, realized on the two-element subsets
    # of five symbols. Disjoint subsets meet.
    labels = list(combinations(range(5), 2))
    patterns["the literature's Petersen graph"] = matrix(
        10, [((a, b), 1) for a, b in pairs(10) if set(labels[a]).isdisjoint(labels[b])])
    output = {}
    for name, m in patterns.items():
        n = len(m)
        cells, coverage = build_cells(m)
        assert not formula_errors(m, coverage)
        orders = checked_orders(m, cells, coverage, random.Random(n))
        full = (1 << n) - 1
        found = subsets(cells, n)
        smallest = minima(found)
        active, _ = active_pattern(m, cells)
        row = {"knots": n, "cells": sum(c.copies for c in cells), "whole": full in found,
               "sign": found.get(full), "whole minimal": full in smallest,
               "all nonempty commuting subsets": len(found), "minimal sets": len(smallest),
               "subsets of at least four knots tested": sum(comb(n, k) for k in range(4, n + 1)),
               "kind": kind(active), "orders tested by cancellation": orders,
               "pair exchanges tested": comb(n, 2)}
        if n <= 5:
            row["meetings"] = listing(m)
            row["whole subsets"] = [{"knots": [u for u in range(n) if mask >> u & 1],
                                     "sign": value, "minimal": mask in smallest}
                                    for mask, value in found.items()]
        if n == 10:
            row["proper subsets of size at least four tested"] = row["subsets of at least four knots tested"] - 1
            row["proper subsets of size below four have no cell"] = sum(comb(n, k) for k in range(4))
            row["largest number of shared neighbours"] = max(
                sum(bool(m[u][w] and m[v][w]) for w in range(n)) for u, v in pairs(n))
            row["maximum mutually meeting subset"] = max(
                k for k in range(1, n + 1)
                if any(all(m[u][v] for u, v in combinations(s, 2)) for s in combinations(range(n), k)))
        output[name] = row
    return output


def verify_archive(rows, classes):
    # The comparison happens after the new classification. The catalogue is
    # used as an independent cross-check through seven knots.
    import networkx as nx

    atlas = defaultdict(set)
    for g in nx.graph_atlas_g():
        if 4 <= len(g) <= 7:
            atlas[len(g)].add(canonical(matrix(len(g), [(p, 1) for p in g.edges])))
    for n, keys in atlas.items():
        assert keys == classes[n].keys()
    seen = set()
    by_key = {(r["knots"], r["key"]): r for r in rows}
    for stored in json.loads((HERE.parent / "abstract.json").read_text()):
        if "graph" in stored:
            g = nx.from_graph6_bytes(stored["graph"].encode())
            m = matrix(len(g), [(p, 1) for p in g.edges])
        else:
            m = matrix(stored["knots"], [((a, b), k) for a, b, k in stored["pattern"]])
        key = (len(m), canonical(m).hex())
        assert key not in seen
        seen.add(key)
        r = by_key[key]
        for field in ("cells", "sign", "inert distinctions", "max coverage", "covered twice"):
            assert r[field] == stored[field], (key, field)
        assert r["active repeated meeting"] == stored["doubled"]
        assert r["distinctions"] == stored["edges"]
        assert r["kind"] == {"K_{2,3}": K23}.get(stored["kind"], stored["kind"])
        assert stored["order independent"] and stored["formula agrees"]
    assert seen == by_key.keys()
    return {"simple catalogue classes through seven matched": sum(map(len, atlas.values())),
            "archived minimal patterns matched individually": len(seen)}


def lifts(simple_odd):
    # A simple odd whole set on a proper subset survives when the meetings
    # are lifted with the same parities. The same holds for a simple even
    # whole set because every one of its cells also survives.
    output = []
    for row in simple_odd:
        n = row["knots"]
        nonzero = {(u, v) for u, v, _ in row["meetings"]}
        absent = [p for p in pairs(n) if p not in nonzero]
        tally = Counter()
        keys = set()
        for weights in product((0, 2), repeat=len(absent)):
            m = matrix(n, [(p, 1) for p in nonzero] + list(zip(absent, weights)))
            cells, _ = build_cells(m)
            found = subsets(cells, n)
            assert found[(1 << n) - 1] == 1
            tally["labelled lifts"] += 1
            if len(found) == 1:
                active, _ = active_pattern(m, cells)
                tally["labelled lifts still minimal"] += 1
                tally[kind(active)] += 1
                keys.add(canonical(m))
        output.append({"simple meetings": row["meetings"], **tally,
                       "minimal lifts up to relabelling": len(keys),
                       "minimal lift keys": sorted(k.hex() for k in keys)})
    return output


def run(through):
    rng = random.Random(485031)
    simple = {1: {b"": ((0,),)}}
    doubled = {1: {b"": ((0,),)}}
    for family, bound, limit in ((simple, 1, through), (doubled, 2, 5)):
        for n in range(2, limit + 1):
            start = time.monotonic()
            family[n], candidates = extend(family[n - 1], bound)
            print(f"multiplicity <= {bound}, {n} knots: {candidates} accepted extensions, "
                  f"{len(family[n])} classes, {time.monotonic() - start:.2f}s", flush=True)
    output = {"weighting": "one per meeting pattern up to relabelling in each stated size and source",
              "formula": "integer coverage by four-holder partitions versus the degree product minus common holders",
              "sign": "cancellation in the literal repeated-distinction word versus interleaving parity",
              "random order seed": 485031, "simple": {}, "at least one doubled meeting": {},
              "abstract fixtures": fixtures()}
    rows = []
    for size in range(4, through + 1):
        for name, family, repeated in (("simple", simple, False),
                                       ("at least one doubled meeting", doubled, True)):
            if size not in family:
                continue
            start = time.monotonic()
            accepted, counts, example = audit_size(family[size], size, repeated, rng)
            check_total = orbit_total(size, 3 if repeated else 2)
            assert check_total == len(family[size])
            output[name][size] = {"classes before any exclusions": len(family[size]),
                                  "independent number from Burnside's lemma": check_total, "counts": counts,
                                  "minimal": accepted, "odd full with only even minima example": example}
            if size <= 7:
                rows.extend(accepted)
            print(f"{name}, {size} knots: {counts}, {len(accepted)} minimal, "
                  f"{time.monotonic() - start:.2f}s", flush=True)
    if through >= 7:
        output["archive comparison"] = verify_archive(rows, simple)
    all_odd = [r for group in output["simple"].values() for r in group["minimal"] if r["sign"]]
    output["all multiplicity-zero-one-two lifts of simple odd minima"] = lifts(all_odd)
    return output


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--through", choices=(5, 6, 7, 8), type=int, default=8)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (2 * 1024**3, 2 * 1024**3))
    result = run(args.through)
    if args.output:
        args.output.write_text(json.dumps(result, indent=2) + "\n")
