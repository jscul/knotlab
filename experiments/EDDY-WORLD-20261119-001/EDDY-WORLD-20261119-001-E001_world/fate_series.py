"""Count unrooted marked-point clusters of the frozen sources by exact series."""

import json
from collections import deque
from decimal import Decimal, localcontext
from itertools import combinations
from pathlib import Path


HERE = Path(__file__).resolve().parent
DATA = HERE.parents[2] / "artifacts" / HERE.parent.name / HERE.name
LIMIT = 64


def multiply(a, b, n):
    return [sum(a[i] * b[k - i] for i in range(k + 1)) for k in range(n + 1)]


class Source:
    def __init__(self, case):
        self.n = len(case["sizes"])
        self.nodes = set(range(self.n))
        neighbors = [set() for _ in case["sizes"]]
        for u, v in case["meetings"]:
            assert u != v and v not in neighbors[u]
            neighbors[u].add(v)
            neighbors[v].add(u)
        self.blocks = [tuple(sorted(row)) for row in neighbors if len(row) >= 2]
        self.opens = [arity - len(row) for arity, row in zip(case["sizes"], neighbors)]
        assert min(self.opens) >= 1 and min(case["sizes"]) >= 3
        self.demand = [sum(len(row) - 1 for row in self.blocks if p in row)
                       for p in range(self.n)]
        self.spares = [self.opens[p] - self.demand[p] for p in range(self.n)]
        assert min(self.spares) >= 0
        # Every candidate pair has one witness, and every candidate triple is held.
        common = {(a, b): neighbors[a] & neighbors[b] for a, b in combinations(range(self.n), 2)}
        assert max(map(len, common.values())) <= 1
        for a, b, c in combinations(range(self.n), 3):
            if common[a, b] and common[a, c] and common[b, c]:
                assert neighbors[a] & neighbors[b] & neighbors[c]

    def factor(self, p, n):
        rays = max(0, 3 - self.opens[p])
        # Omit the pendant, or include it with an initial segment on each of its rays.
        if rays == 0:
            one = [1, 1] + [0] * (n - 1)
        elif rays == 1:
            one = [1] * (n + 1)
        else:
            assert rays == 2
            one = [1] + list(range(1, n + 1))
        answer = [1] + [0] * n
        for _ in range(self.spares[p]):
            answer = multiply(answer, one, n)
        return answer

    def pieces(self):
        remaining = set(self.nodes)
        parts = []
        while remaining:
            nodes = {min(remaining)}
            old = None
            while nodes != old:
                old = nodes.copy()
                for row in self.blocks:
                    if nodes.intersection(row):
                        nodes.update(row)
            blocks = [row for row in self.blocks if nodes.intersection(row)]
            rank = sum(len(row) - 1 for row in blocks) - len(nodes) + 1
            rays = sum(self.spares[p] * max(0, 3 - self.opens[p]) for p in nodes)
            assert rank or rays  # no relay in these ten sources
            parts.append({"point_ids": sorted(nodes), "rank": rank, "rays": rays})
            remaining -= nodes
        return parts

    def count(self, allowed, n=LIMIT):
        """Restrict original point labels; preserve full-source blocks and pendant data."""
        points = sorted(allowed)
        blocks = [tuple(p for p in row if p in allowed) for row in self.blocks]
        blocks = [row for row in blocks if len(row) >= 2]
        values = [self.factor(p, n) for p in points]
        factor = dict(zip(points, range(len(values))))
        ports = {}
        for b, row in enumerate(blocks):
            for p in row:
                ports[p, b] = len(values)
                values.append([1] + [0] * n)
        products, nodes = {}, []

        def product(factors):
            acc = factors[0]
            for v in factors[1:]:
                key = tuple(sorted((acc, v)))
                if key not in products:
                    products[key] = len(values)
                    values.append([0] * (n + 1))
                    nodes.append((products[key], *key))
                acc = products[key]
            return acc

        def body(p, excluded):
            return product([factor[p]] + [ports[q, b] for b, row in enumerate(blocks)
                                          if b != excluded and p in row for q in row if q != p])

        rhs = [(uid, body(p, b)) for (p, b), uid in ports.items()]
        rooted = [body(p, None) for p in points]
        for k in range(n + 1):
            if k:
                for uid, expr in rhs:
                    values[uid][k] = values[expr][k - 1]
            for node, a, b in nodes:
                values[node][k] = sum(values[a][i] * values[b][k - i] for i in range(k + 1))
        result = [0] + [sum(values[r][k] for r in rooted) for k in range(n)]
        # A core cluster is a tree of blocks. Sum over marked ordinary points,
        # subtracting k-1 at every block containing k>=2 selected points.
        for b, row in enumerate(blocks):
            for k in range(2, len(row) + 1):
                for subset in combinations(row, k):
                    poly = [1] + [0] * n
                    for p in subset:
                        poly = multiply(poly, [0] + values[ports[p, b]][1:], n)
                    for i, count in enumerate(poly):
                        result[i] -= (k - 1) * count
        assert all(v >= 0 for v in result)
        return result[1:]  # index t represents cluster size t+1


def rate(k, arms, extra=0):
    with localcontext() as ctx:
        ctx.prec = 55
        lo, hi = Decimal(0), Decimal(1)
        for _ in range(150):
            z = (lo + hi) / 2
            left = z**5 * (1 + z)**k * (1 + z**extra if extra else 1)
            if left < (1 - z)**arms:
                lo = z
            else:
                hi = z
        return str(round(2 / (lo + hi), 12))


def meeting_distance(stars, starts, targets):
    first = {}
    neighbors = [set() for _ in stars]
    for p, row in enumerate(stars):
        for bit in row:
            if bit in first:
                q = first[bit]
                neighbors[p].add(q)
                neighbors[q].add(p)
            else:
                first[bit] = p
    queue = deque((p, 0) for p in starts)
    visited = set(starts)
    while queue:
        p, dist = queue.popleft()
        if p in targets:
            return dist
        for q in neighbors[p] - visited:
            visited.add(q)
            queue.append((q, dist + 1))
    raise ValueError("separated physical components")


def main():
    inputs = json.loads((HERE / "inputs.json").read_text())["cases"]
    literal = json.loads((DATA / "stages.json").read_text())["cases"]
    report, counts = {}, {}
    for case in inputs:
        name, roles = case["id"], case["roles"]
        source = Source(case)
        counts[name] = full = source.count(source.nodes)
        checks = {"full": (source.nodes, full)}
        if roles["background"]:
            domain = set(roles["background"])
            checks["background"] = (domain, source.count(domain))
        rings = [set(row) for row in roles["rings"]]
        for i, ring in enumerate(rings):
            checks[f"ring_{i + 1}"] = (ring, source.count(ring))
        two_ring = {}
        if len(rings) == 2:
            background = set(roles["background"])
            domains = [source.nodes - (ring - background) for ring in rings]
            singles = [source.count(domain) for domain in domains]
            assert all(result == counts["J1"] for result in singles)
            both = [f - x - y + b for f, x, y, b in zip(full, *singles, counts["B"])]
            first = next(t for t, value in enumerate(both) if value)
            two_ring = {"both_exclusive_by_age": both, "first_age": first, "first_count": both[first],
                        "physical_growing_separation_by_age": [], "physical_seam_separation_by_age": [],
                        "lower_rate_beta": rate(1, 4, int(name[1:]) // 2 + 1)}
            assert first == int(name[1:]) // 2 + 1 and both[first] == 4
        matches = 0
        for stage in literal[name]["stages"].values():
            t = stage["age"]
            origin = stage["source_coordinate_maps"]["ancestry"]
            born = [set(origin[v]) for v in stage["born"]]
            for domain, result in checks.values():
                assert sum(s <= domain for s in born) == result[t], (name, t, sorted(domain))
                matches += 1
            if two_ring:
                assert sum(all(s & (ring - background) for ring in rings) for s in born) == both[t]
                matches += 1
                carriers = [{p for p in stage["born"] if set(origin[p]) <= ring and set(origin[p]) - background}
                            for ring in rings]
                gap = meeting_distance(stage["stars"], *carriers)
                first_seam, second_seam = roles["seams"]
                seam_gap = meeting_distance(stage["stars"], {first_seam}, {second_seam})
                d = int(name[1:])
                assert seam_gap == d and gap == d + 2 * max(t, 1)
                two_ring["physical_growing_separation_by_age"].append(gap)
                two_ring["physical_seam_separation_by_age"].append(seam_gap)
        if name.startswith("J") or name.startswith("T"):
            assert checks["background"][1] == counts["B"]
            for i, spares in enumerate(roles["ring_spares"]):
                assert checks[f"ring_{i + 1}"][1] == counts[f"R{len(spares)}"]
        if name == "B":
            assert full == [17 + 2 * t for t in range(LIMIT)]
        if name == "R0":
            assert full == [5] * LIMIT
        if name == "C1":
            assert checks["background"][1] == counts["B"]
            assert all(2 * full[t] == 5 * t * t + 17 * t + 34 for t in range(3, LIMIT))
        report[name] = {"opens": source.opens, "demand": source.demand, "leftovers": source.spares,
                        "pieces": source.pieces(), "births_by_age": full, "literal_stages": len(literal[name]["stages"]),
                        "literal_count_comparisons": matches, **two_ring}
        if name.startswith(("R", "J")):
            report[name]["rate"] = rate(int(name[1:]), 4 if name.startswith("J") else 0)
    result = {"size_convention": "coefficient of z^(age+1)", "series_through_age": LIMIT - 1,
              "cases": report}
    (DATA / "fate_series.json").write_text(json.dumps(result, indent=2) + "\n")


if __name__ == "__main__":
    main()
