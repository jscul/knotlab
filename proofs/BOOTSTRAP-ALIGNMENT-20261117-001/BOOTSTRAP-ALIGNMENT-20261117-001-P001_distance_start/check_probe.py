"""Build the anonymous pair-probe observation and recover the original adjacency."""

from collections import Counter, defaultdict
from functools import lru_cache
from itertools import combinations, product
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import random
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
CUBIC = ROOT / "proofs/CUBIC-FROM-A-KNOT-20261117-001/CUBIC-FROM-A-KNOT-20261117-001-P001_local_growth"
POSITIONS = tuple(product((0, 1), repeat=3))
PAIRS = tuple(combinations(range(8), 2))
WIDTH = 8 + 2 * len(PAIRS)


@lru_cache(None)
def literal_rows():
    spec = importlib.util.spec_from_file_location("literal_betweennesses", CUBIC/"cut_control.py")
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    placed, rows, _ = source.seed_to_cube()
    order = [placed.index(point) for point in POSITIONS]
    return tuple(sorted(tuple(row[i] for i in order) for row in rows))


def names(seed):
    renamed = list(range(WIDTH))
    if seed:
        random.Random(seed).shuffle(renamed)
    return tuple(renamed)


def seed_fixture(seed):
    """Inputs used to grade the answer; their order does not enter recover_cube."""
    return names(seed)[:8], literal_rows()


class ProbeProjection:
    """Project actual seed rows and conservative B(p,a,q), B(p,b,q) extensions."""

    def __init__(self, old_rows, pairs, one_constraint=False):
        self.old_rows = old_rows
        self.domains = {}
        for j, (a, b) in enumerate(pairs):
            outcomes = []
            for old in old_rows:
                # Literal betweenness permits either middle if the ends differ.
                choices = {(p, q) for p, q in product((0, 1), repeat=2)
                           if (p != q or old[a] == p) and (one_constraint or p != q or old[b] == p)}
                outcomes.append(choices)
            self.domains[8 + 2*j] = outcomes
        self.all_old = (1 << len(old_rows)) - 1
        self.filters = [{v: sum(1 << i for i, row in enumerate(old_rows) if row[b] == v)
                         for v in (0, 1)} for b in range(8)]
        self.pair_filters = {
            start: {values: sum(1 << j for j, rows in enumerate(outcomes) if values in rows)
                    for values in product((0, 1), repeat=2)}
            for start, outcomes in self.domains.items()
        }
        assert all({p for p, q in domain} == {0,1} and {q for p, q in domain} == {0,1}
                   for domains in self.domains.values() for domain in domains)

    def project(self, support):
        """A one-ended probe has both values for each old row; probes factor over it."""
        positions = {bit: i for i, bit in enumerate(support)}
        old = [(position, self.filters[bit]) for bit, position in positions.items() if bit < 8]
        paired = [(positions[bit], positions[bit+1], self.pair_filters[bit]) for bit in support
                  if bit >= 8 and bit % 2 == 0 and bit + 1 in positions]
        allowed = set()
        for assignment in product((0, 1), repeat=len(support)):
            old_states = self.all_old
            for pos, table in old:
                old_states &= table[assignment[pos]]
            for left, right, table in paired:
                old_states &= table[assignment[left], assignment[right]]
            if old_states:
                allowed.add(assignment)
        return allowed

    def lifts(self):
        counts = [1] * len(self.old_rows)
        for domains in self.domains.values():
            for i, rows in enumerate(domains):
                counts[i] *= len(rows)
        return counts


def threshold_two(projection, width):
    links = {i: set() for i in range(width)}
    # Every single and pair must project freely before a missing triple
    # certifies a ternary bond. All relations here are nonempty.
    assert all(len(projection.project(support)) == 4 for support in combinations(range(width), 2))
    knots = 0
    for triple in combinations(range(width), 3):
        if len(projection.project(triple)) < 8:
            knots += 1
            for a, b in combinations(triple, 2):
                links[a].add(b)
                links[b].add(a)
    return links, knots


@lru_cache(None)
def literal_probe_graph():
    return threshold_two(ProbeProjection(literal_rows(), PAIRS), WIDTH)


def renamed_graph(graph, perm):
    return {perm[i]: {perm[j] for j in neighbors} for i, neighbors in graph.items()}


def recover_cube(graph):
    """Reader input is only the unnamed distance-two graph."""
    highest = max(map(len, graph.values()))
    old = {i for i, row in graph.items() if len(row) == highest}
    if len(old) != 8 or any(not (old - {i}) <= graph[i] for i in old):
        raise ValueError("The distance table lacks the expected eight originals")
    intervals = set()
    for i in graph.keys() - old:
        partners = graph[i] - old
        if len(partners) != 1:
            raise ValueError("A probe endpoint lacks a unique mate")
        mate = next(iter(partners))
        if graph[mate] & old != graph[i] & old:
            raise ValueError("Probe endpoints disagree on their old neighbors")
        intervals.add(frozenset(graph[i] & old))
    result = {i: set() for i in old}
    for edge in intervals:
        if len(edge) == 2:
            a,b = edge
            result[a].add(b)
            result[b].add(a)
    if any(len(row) != 3 for row in result.values()):
        raise ValueError("The two-place intervals do not give three neighbors at each original")
    return result


def measured_cube(seed):
    return recover_cube(renamed_graph(literal_probe_graph()[0], names(seed)))


def canonical_check(rows, variables):
    omitted = sorted(set(product((0, 1), repeat=len(variables))) - set(rows))
    clauses = [" ".join(("~" if bit else "") + n for n,bit in zip(variables,row)) for row in omitted]
    cnf = "; ".join(clauses) or f"{variables[0]} ~{variables[0]}"
    cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
           "--loops", *variables[:-1], "--contact", variables[-1], "--json"]
    report = json.loads(subprocess.check_output(cmd, env={**os.environ, "PYTHONPATH":str(ROOT/"tools")}))
    assert set(report["allowed"]) == {"".join(map(str,row)) for row in rows}
    return {"allowed_rows":len(rows), "passes":report["is_knot"]}


def main():
    graph, triples = literal_probe_graph()
    pair_model = ProbeProjection(literal_rows(), PAIRS)
    baseline = None
    for seed in (0, 113, 271):
        cube = measured_cube(seed)
        ids, old_rows = seed_fixture(seed)
        expected = {ids[i]: {ids[j] for j in range(8) if sum(a != b for a,b in zip(POSITIONS[i], POSITIONS[j])) == 1}
                    for i in range(8)}
        assert cube == expected
        if seed == 0:
            baseline = cube
    counts = Counter()
    for i,(a,b) in enumerate(PAIRS):
        p = 8+2*i
        between = {c for c in range(8)
                   if all(row[a] != row[b] or row[c] == row[a] for row in old_rows)}
        assert graph[p] & set(range(8)) == between
        assert graph[p+1] == graph[p] - {p+1} | {p}
        counts[len(between)] += 1
    assert counts == {2:12, 4:12, 8:4}
    lifts = pair_model.lifts()
    assert sorted(lifts) == sorted([3**28]*2 + [3**12 * 2**16]*6)

    wrong, _ = threshold_two(ProbeProjection(old_rows, PAIRS, one_constraint=True), WIDTH)
    try:
        recover_cube(wrong)
    except ValueError as exc:
        rejects = str(exc)
    else:
        raise AssertionError("One-sided probes unexpectedly recovered a cube")
    # For 000 and 011 the coordinate 001 is between; 100 is outside.
    i = PAIRS.index((0,3)); ends=(8+2*i,9+2*i)
    controls = [canonical_check(pair_model.project((ends[0], middle, ends[1])), ("p","m","q"))
                for middle in (0,1,4)]
    assert [r["passes"] for r in controls] == [True, True, False]
    return {"original_rows": len(old_rows), "distinctions_after_probe_round":WIDTH,
            "probe_pairs":len(PAIRS),"temporary_betweennesses":2*len(PAIRS),
            "full_two_bit_projections_checked":len(list(combinations(range(WIDTH),2))),
            "ternary_projections_checked":len(list(combinations(range(WIDTH),3))),
            "ternary_knots":triples,"degrees":dict(Counter(map(len,graph.values()))),
            "pairs_by_interval_size":dict(counts),
            "edges_read_on_unrenamed_fixture":sorted([a,b] for a,adj in baseline.items() for b in adj if a<b),
            "tested_namings":[0,113,271],"lifts_of_each_seed_row":lifts,
            "total_allowed_rows_with_probes":sum(lifts),"canonical_knot_controls":controls,
            "one_sided_probe_control":rejects,
            "source_row_builder_sha256":hashlib.sha256((CUBIC/"cut_control.py").read_bytes()).hexdigest()}


if __name__ == "__main__":
    print(json.dumps(main(),indent=2,sort_keys=True))
