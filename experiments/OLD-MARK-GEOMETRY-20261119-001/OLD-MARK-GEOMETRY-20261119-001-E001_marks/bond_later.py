"""Certified later old-mark distances by branching on disconnected minimum cuts."""

from argparse import ArgumentParser
from collections import Counter
from hashlib import sha256
from heapq import heappop, heappush
from itertools import count, product
import json
from pathlib import Path

import numpy as np
from scipy.sparse import csr_matrix
from scipy.sparse.csgraph import breadth_first_order, maximum_flow

from bond_distances import (NAMED, OUTPUT, Wiring, bitset, literal_states_distances,
                            members, pair_groups, reached)
import sources


def held_ends(first, second, wiring):
    a, b = wiring.edge[first]
    c, d = wiring.edge[second]
    exterior = 1 << wiring.exterior
    for (u, v), (w, x) in product(((a, b), (b, a)), ((c, d), (d, c))):
        inside = (1 << u) | (1 << w)
        outside = exterior | (1 << v) | (1 << x)
        if not inside & outside:
            yield inside, outside


class PinFlow:
    def __init__(self, wiring):
        self.wiring = wiring
        self.n = wiring.total
        self.big = len(wiring.edge) + 1
        weighted = Counter(wiring.edge.values())
        self.u = np.array([u for u, v in weighted], dtype=np.int64)
        self.v = np.array([v for u, v in weighted], dtype=np.int64)
        self.weights = np.array(list(weighted.values()), dtype=np.int64)
        self.shape = (self.n + 2, self.n + 2)
        self.base = csr_matrix((np.tile(self.weights, 2),
                                (np.r_[self.u, self.v], np.r_[self.v, self.u])), shape=self.shape)
        self.evaluations = 0

    def minimum(self, must_include, must_exclude):
        """A feasible integer flow and a cut of the same value certify the relaxation."""
        self.evaluations += 1
        include = np.fromiter(members(must_include), dtype=np.int64)
        exclude = np.fromiter(members(must_exclude), dtype=np.int64)
        root, other = self.n, self.n + 1
        pinned = csr_matrix((np.full(len(include) + len(exclude), self.big, dtype=np.int64),
                             (np.r_[np.full(len(include), root, dtype=np.int64), exclude],
                              np.r_[include, np.full(len(exclude), other, dtype=np.int64)])),
                            shape=self.shape)
        capacity = self.base + pinned
        result = maximum_flow(capacity, root, other)
        flow = result.flow.astype(np.int64)
        residue = (capacity - flow).tocsr()
        residue.eliminate_zeros()
        value = int(result.flow_value)
        balance = np.asarray(flow.sum(axis=1)).ravel()
        assert (flow + flow.T).nnz == 0 and residue.data.min(initial=0) >= 0
        assert not balance[:self.n].any() and balance[root] == value == -balance[other]
        side = np.zeros(self.n + 2, dtype=bool)
        side[breadth_first_order(residue, root, return_predecessors=False)] = True
        assert not side[other] and side[include].all() and not side[exclude].any()
        assert value == int(self.weights[side[self.u] != side[self.v]].sum()) < self.big
        return value, bitset(np.flatnonzero(side[:self.n]).tolist())

    def flaw(self, mask, must_include, must_exclude):
        """Return the smallest boundary whose same-side membership needs repair."""
        wiring = self.wiring
        errors = []
        for inside, shore, pinned, forbidden in (
                (True, mask, must_include, must_exclude),
                (False, wiring.full ^ mask, must_exclude, must_include)):
            seed = shore & -shore
            connected = reached(seed, shore, wiring.neighbors)
            pending = shore ^ connected
            if not pending:
                continue
            while connected:
                # With positive weights, a disconnected component without a pin
                # could switch sides and strictly improve the relaxed minimum.
                assert connected & pinned and (shore ^ connected) & pinned
                outside_neighbors = 0
                for v in members(connected):
                    outside_neighbors |= wiring.neighbors[v]
                free = outside_neighbors & ~(shore | forbidden)
                errors.append((free.bit_count(), int(not inside), free, connected))
                seed = pending & -pending
                connected = reached(seed, pending, wiring.neighbors)
                pending ^= connected
        if not errors:
            return None
        _, opposite, free, _ = min(errors)
        return bool(opposite), free

    def solve(self, pair, witness, limit):
        """Keep the minimum open-subproblem bound if the branching budget expires."""
        wiring = self.wiring
        pair = tuple(pair)
        certificate = wiring.witness(witness, pair)
        best = len(certificate["distinctions"])
        waiting = []
        seq = count()
        start = self.evaluations

        def examine(must_include, must_exclude):
            nonlocal best, witness, certificate
            cost, proposed = self.minimum(must_include, must_exclude)
            if cost >= best:
                return
            flaw = self.flaw(proposed, must_include, must_exclude)
            if flaw is None:
                certificate = wiring.witness(proposed, pair, cost)
                best = cost
                witness = proposed
                return
            opposite, free = flaw
            if free:
                heappush(waiting, (cost, next(seq), must_include, must_exclude, opposite, free))

        for pins in sorted(set(held_ends(*pair, wiring))):
            examine(*pins)
        while waiting and waiting[0][0] < best:
            bound, _, must_include, must_exclude, opposite, free = waiting[0]
            if self.evaluations - start + free.bit_count() > limit:
                break
            heappop(waiting)
            if opposite:
                # First free boundary knot on the required side, with each
                # preceding choice pinned to the opposite side.
                for v in members(free):
                    at = 1 << v
                    examine(must_include, must_exclude | at)
                    must_include |= at
            else:
                for v in members(free):
                    at = 1 << v
                    examine(must_include | at, must_exclude)
                    must_exclude |= at
        lower = min(best, waiting[0][0]) if waiting else best
        return lower - 1, best - 1, witness, certificate, self.evaluations - start


def control():
    # Test all finite pairs, with deliberately nonminimal witnesses where possible.
    stars = [[0, 3, 4], [0, 1, 5], [1, 2, 6], [2, 3, 7]]
    wire = Wiring(stars)
    expected, legal, _ = literal_states_distances(stars)
    initial = {}
    for mask in range(1, 1 << wire.exterior):
        outside = wire.full ^ mask
        if (reached(mask & -mask, mask, wire.neighbors) != mask or
                reached(1 << wire.exterior, outside, wire.neighbors) != outside):
            continue
        cut = wire.witness(mask)["distinctions"]
        for i, a in enumerate(cut):
            for b in cut[i + 1:]:
                prior = initial.get((a, b), (0, 0))
                initial[a, b] = max(prior, (len(cut), mask))
    solver = PinFlow(wire)
    n_relaxations = 0
    for pair, (_, start) in initial.items():
        lower, upper, *_rest, n = solver.solve(pair, start, 400)
        assert lower == upper == expected[pair[0]][pair[1]]
        n_relaxations += n
    assert len(initial) == sum(isinstance(expected[i][j], int) for i in range(8) for j in range(i + 1, 8))
    return {"allowed_states": legal, "pairs": len(initial), "integer_relaxations": n_relaxations}


def initial_rows(first, occupied):
    load = next(arm for arm in first["assignments"].values() if frozenset(arm["occupied"]) == occupied)
    data = first["age_one_by_activity"][load["activity_id"]]
    return {(a, b): bitset(data["witnesses"][ix]["knots"]) for a, b, _, ix in data["pairs"]}


def frame_search(stars, seeds, limit):
    wire = Wiring(stars)
    solver = PinFlow(wire)
    rows, witnesses = [], {}
    for pair, mask in seeds.items():
        lo, hi, witness, cert, nflow = solver.solve(pair, mask, limit)
        seeds[pair] = witness
        if witness not in witnesses:
            witnesses[witness] = len(witnesses), cert
        rows.append([*pair, lo, hi, witnesses[witness][0], nflow])
    return {"knots": wire.n, "distinctions": len(wire.edge), "exact_pairs": sum(r[2] == r[3] for r in rows),
            "integer_relaxations": solver.evaluations,
            "pairs": rows, "witnesses": [entry[1] for entry in witnesses.values()]}


def read_later(spec, occupied, first, max_age, limit, full_age_two):
    original = initial_rows(first, occupied)
    path = spec["roles"]["anchors"]
    indices = list(NAMED)
    if len(spec["roles"]["seams"]) == 2:
        receiver = spec["roles"]["background"].index(spec["roles"]["seams"][1])
        indices.extend([(receiver - 2, receiver + 1), (receiver - 1, receiver)])
    labels = {tuple(sorted((path[i], path[j]))): f"{i},{j}" for i, j in indices}
    named = list(labels)
    early = [pair for group in pair_groups(spec).values() for pair in group] if full_age_two else named
    seeds = {p: original[p] for p in early}
    frames = {}
    stages = sources.generate(spec, occupied, max_age)
    while True:
        try:
            age, frame = next(stages)
        except StopIteration as stop:
            return {"frames": frames, "termination": stop.value}
        if age >= 2:
            if age == 3 and full_age_two:
                seeds = {p: seeds[p] for p in named}
            result = frame_search(frame["stars"], seeds, limit)
            frames[str(age)] = result
            print(spec["id"], len(occupied), age, f"{result['exact_pairs']}/{len(seeds)}",
                  result["integer_relaxations"],
                  [(labels[tuple(row[:2])], row[2], row[3]) for row in result["pairs"]
                   if tuple(row[:2]) in labels], flush=True)


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--cases", nargs="+", choices=["J1", "B", "J0", "J2", "C1", "T4", "T8"],
                        default=["J1"])
    parser.add_argument("--max-age", type=int, default=4)
    parser.add_argument("--flows-per-pair", type=int, default=1500)
    parser.add_argument("--full-age-two", action="store_true")
    parser.add_argument("--first", type=Path, default=OUTPUT / "bond_first.json")
    parser.add_argument("--out", type=Path, default=OUTPUT / "bond_later.json")
    args = parser.parse_args()
    if args.flows_per_pair < 4 or not 2 <= args.max_age <= 12:
        parser.error("Allow at least four relaxations per pair and last age from two through twelve.")
    with args.first.open() as handle:
        initial = json.load(handle)
    controls = control()
    result = {}
    for case in args.cases:
        spec = sources.cases()[case]
        result[case] = {}
        for code, names in sources.loads(spec).items():
            result[case][code] = read_later(spec, names, initial["cases"][case], args.max_age,
                                          args.flows_per_pair, args.full_age_two)
    out = {"schema": 1, "unit": "bond size minus one", "last_requested_age": args.max_age,
           "flows_per_pair": args.flows_per_pair, "full_age_two": args.full_age_two,
           "first_sha256": sha256(args.first.read_bytes()).hexdigest(), "controls": controls,
           "pair_columns": ["first", "second", "min", "max", "witness_index", "integer_relaxations"],
           "cases": result}
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(out, separators=(",", ":")) + "\n")


if __name__ == "__main__":
    main()
