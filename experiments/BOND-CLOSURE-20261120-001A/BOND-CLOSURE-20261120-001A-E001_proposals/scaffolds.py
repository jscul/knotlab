"""Exact projected NAE bonds and ordinary step controls for the closing pair."""

from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path
from random import Random
from tempfile import NamedTemporaryFile

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "scaffolds.json"
ORDINARY = (ROOT / "experiments" / "ORDINARY-DYNAMICS-20261120-001A"
            / "ORDINARY-DYNAMICS-20261120-001A-E001_ordinary" / "rulers.py")
NAE = (ROOT / "experiments" / "NAE-GROWTH-20261119-001B"
       / "NAE-GROWTH-20261119-001B-E001_nae" / "bondlib.py")


def load_module(path):
    spec = spec_from_file_location(path.stem, path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def elements(mask):
    while mask:
        chosen = mask & -mask
        yield chosen
        mask ^= chosen


class LiteralRelation:
    """One bit for each literal assignment, indexed by its packed Boolean word."""

    def __init__(self, stars, law="nae"):
        self.names = tuple(sorted(set().union(*map(set, stars))))
        self.position = {name: i for i, name in enumerate(self.names)}
        self.width = len(self.names)
        self.names_mask = (1 << self.width) - 1
        full = (1 << (1 << self.width)) - 1

        self.zeros = {}
        for coordinate in elements(self.names_mask):
            block = (1 << coordinate) - 1
            shift = coordinate * 2
            while shift < 1 << self.width:
                block |= block << shift
                shift *= 2
            self.zeros[coordinate] = block

        self.allowed = full
        for row in stars:
            values = self.mask(row)
            if law == "nae":
                all_zero = all_one = full
                for coordinate in elements(values):
                    zeros = self.zeros[coordinate]
                    all_zero &= zeros
                    all_one &= full ^ zeros
                forbidden = all_zero | all_one
            elif law == "parity":
                forbidden = 0
                for coordinate in elements(values):
                    forbidden ^= full ^ self.zeros[coordinate]
            else:
                raise ValueError(law)
            self.allowed &= full ^ forbidden
        assert self.allowed

    def mask(self, names):
        return sum(1 << self.position[name] for name in names)

    def forget(self, assignments, coordinate):
        # Move rows with this coordinate set onto the rows with the coordinate clear.
        return (assignments | (assignments >> coordinate)) & self.zeros[coordinate]

    def project(self, names):
        result = self.allowed
        for coordinate in elements(self.names_mask ^ self.mask(names)):
            result = self.forget(result, coordinate)
        return result

    def patterns(self, names):
        packed = self.project(names)
        positions = tuple(1 << self.position[name] for name in names)
        return tuple(
            row for row in product((0, 1), repeat=len(positions))
            if packed & (1 << sum(bit * position for bit, position in zip(row, positions)))
        )

    def bonds(self):
        # Every removed set is reached by forgetting coordinates in decreasing order.
        constrained = bytearray(1 << self.width)

        def descend(rows, keep, may_forget):
            if rows.bit_count() == 1 << keep.bit_count():
                return  # All smaller projections are free as well.
            constrained[keep] = 1
            while may_forget:
                coordinate = 1 << (may_forget.bit_length() - 1)
                may_forget ^= coordinate
                descend(self.forget(rows, coordinate), keep ^ coordinate, may_forget)

        descend(self.allowed, self.names_mask, self.names_mask)
        return {
            tuple(self.names[bit.bit_length() - 1] for bit in elements(keep))
            for keep in range(1, 1 << self.width)
            if constrained[keep] and all(not constrained[keep ^ bit] for bit in elements(keep))
        }


def owners(stars):
    result = defaultdict(list)
    for holder, row in enumerate(stars):
        assert len(row) == len(set(row))
        for mark in row:
            result[mark].append(holder)
    assert all(1 <= len(holders) <= 2 for holders in result.values())
    return result


def holder_graph(stars, shared=None):
    graph = [set() for _ in stars]
    if shared is None:
        shared = [pair for pair in owners(stars).values() if len(pair) == 2]
    for a, b in shared:
        graph[a].add(b)
        graph[b].add(a)
    return graph


def steps(graph, start):
    reached = {start: 0}
    pending = deque([start])
    while pending:
        node = pending.popleft()
        for neighbor in graph[node]:
            if neighbor not in reached:
                reached[neighbor] = reached[node] + 1
                pending.append(neighbor)
    return reached


def ordinary_readings(stars):
    holding = owners(stars)
    loose = {mark: row[0] for mark, row in holding.items() if len(row) == 1}
    graph = holder_graph(stars)
    live = set(loose.values())
    end = {v: {w for w in live - {v} if graph[v] & graph[w]} for v in live}
    distinctions = {mark: set().union(*(stars[v] for v in row)) - {mark}
                    for mark, row in holding.items()}
    rows = []
    for a, b in combinations(sorted(loose), 2):
        v, w = loose[a], loose[b]
        holder = steps(graph, v)[w]
        through_knots = steps(distinctions, a)[b]
        assert through_knots == holder + 1
        rows.append({"marks": (a, b), "end_steps": steps(end, v).get(w),
                     "holder_steps": holder, "distinction_steps": through_knots})
    return rows


def projection_fragments(stars):
    """Remove doubled meetings, keeping both named distinctions at each incident knot."""
    shared = defaultdict(list)
    for mark, row in owners(stars).items():
        if len(row) == 2:
            shared[tuple(row)].append(mark)
    graph = holder_graph(stars, [pair for pair, marks in shared.items() if len(marks) != 2])
    remaining = set(range(len(stars)))
    components = []
    while remaining:
        component = tuple(sorted(steps(graph, min(remaining))))
        remaining.difference_update(component)
        components.append((component, LiteralRelation(tuple(stars[i] for i in component))))
    for (_, a), (_, b) in combinations(components, 2):
        intersection = sorted(set(a.names) & set(b.names))
        for table in (a, b):
            assert table.project(intersection).bit_count() == 1 << len(intersection)
    return components


def all_bonds(fragments):
    # The free intersections ensure no bond of one fragment contains a bond of another.
    return set().union(*(relation.bonds() for _, relation in fragments))


def minima(bonds, arity):
    values = {}
    for bond in sorted(bonds, key=lambda row: (len(row), row)):
        for read in combinations(bond, arity):
            values.setdefault(read, len(bond) - 1)
    return values


def nae_solver(stars):
    clauses = []
    for row in stars:
        clauses.extend([[d + 1 for d in row], [-d - 1 for d in row]])
    return Minisat22(bootstrap_with=clauses)


def sat_patterns(solver, marks):
    return tuple(
        row for row in product((0, 1), repeat=len(marks))
        if solver.solve(assumptions=[(d + 1) if b else -(d + 1) for d, b in zip(marks, row)])
    )


def sat_checks(stars, bonds):
    """Independent literal NAE checks on all displayed bonds and their maximal proper subsets."""
    proper = {read for bond in bonds for read in combinations(bond, len(bond) - 1)}
    with nae_solver(stars) as solver:
        assert solver.solve()
        for row in stars:
            allowed = sat_patterns(solver, row)
            assert len(allowed) == (1 << len(row)) - 2
            assert all(0 < sum(values) < len(row) for values in allowed)
        for bond in bonds:
            assert len(sat_patterns(solver, bond)) < 1 << len(bond)
        for read in proper:
            assert len(sat_patterns(solver, read)) == 1 << len(read)
    return {"literal_stars": len(stars), "bonds": len(bonds), "distinct_maximal_proper_subsets": len(proper)}


def widths(ordinary, source, reached, marks, first, small):
    if small:
        nae1, _, _ = ordinary.step(source, nae=True)
        assert nae1 == reached
        nae2, next_births, _ = ordinary.step(reached, nae=True)
        target, = (r for r in next_births if r["spent"] == marks)
        expected_fresh = len(target["fresh"])
        assert expected_fresh == 1
    else:
        nae2 = None
        expected_fresh = 1
        with nae_solver(source) as solver:
            for birth in first:
                inputs = birth["spent"]
                assert len(sat_patterns(solver, inputs)) == 1 << len(inputs)
                # The first cohort has only ordinary pairs and the optional offshoot.
                assert len(birth["fresh"]) == max(3 - len(inputs), birth["raw_demand"], 1)
        with nae_solver(reached) as solver:
            assert len(sat_patterns(solver, marks)) == 1 << len(marks)

    def partial_status(stars, used):
        holding = owners(stars)
        loose = tuple(sorted(d for d, row in holding.items() if len(row) == 1))
        with nae_solver(stars) as solver:
            return {"loose": loose, "all_loose_used": set(used) == set(loose),
                    "proposal_patterns": sat_patterns(solver, used),
                    "loose_patterns": sat_patterns(solver, loose)}

    result = partial_status(reached, marks)
    result["nae_next_fresh"] = expected_fresh
    result["nae_implied"] = not any(sum(row) in (0, len(marks)) for row in result["proposal_patterns"])
    assert not result["nae_implied"]
    if nae2 is not None:
        states = [LiteralRelation(literal) for literal in (source, reached, nae2)]
        result["allowed_state_counts"] = [table.allowed.bit_count() for table in states]
        for old, new in zip(states[:-1], states[1:], strict=True):
            assert new.project(old.names) == old.allowed
    return result


def small_cross_check(archive, stars, bonds, law):
    table = LiteralRelation(stars, law)
    rows = archive.states(table.width, stars, law)
    assert len(rows) == table.allowed.bit_count()
    values = table.allowed.to_bytes((1 << table.width) // 8, "little")
    for row in rows.tolist():
        assert values[row >> 3] & (1 << (row & 7))
    pairs = minima(bonds, 2)
    archived_pairs = archive.table(table.width, rows, kmax=table.width)
    assert all(pairs.get(marks, table.width) == d for marks, d in archived_pairs.items())
    return {"allowed_rows": len(rows), "all_pair_readings": len(archived_pairs)}


def small_wired_cut_bonds(ordinary, stars):
    links = ordinary.encode_links(stars)
    exterior = len(stars)
    graph = [set() for _ in range(exterior + 1)]
    for a, b in links.values():
        graph[a].add(b)
        graph[b].add(a)
    whole = set(range(exterior + 1))
    bonds = set()
    for support in range(1, 1 << exterior):
        side = {i for i in range(exterior) if support & (1 << i)}
        outside = whole - side
        inward = [neighbors & side for neighbors in graph]
        outward = [neighbors & outside for neighbors in graph]
        if set(steps(inward, min(side))) == side and set(steps(outward, exterior)) == outside:
            bonds.add(tuple(sorted(d for d, (a, b) in links.items() if (a in side) != (b in side))))
    return bonds


def finite_rows(values):
    return [(*marks, value) for marks, value in sorted(values.items())]


def measurement(ordinary, archive, length, extra):
    source, _ = ordinary.source(length, extra)
    reached, first, _ = ordinary.step(source)
    marks = tuple(next(iter(birth["fresh"])) for birth in first if len(birth["parents"]) == 2)
    assert len(marks) == 3
    if length is None:
        fragments = [(tuple(range(len(reached))), LiteralRelation(reached))]
        parity = LiteralRelation(reached, "parity").bonds()
        parity_receipt = small_cross_check(archive, reached, parity, "parity")
        assert parity == small_wired_cut_bonds(ordinary, reached)
        parity_receipt["connected_cut_bonds"] = len(parity)
    else:
        fragments = projection_fragments(reached)
        parity = parity_receipt = None
    bonds = all_bonds(fragments)
    sat = sat_checks(reached, bonds)
    pairs, triples = minima(bonds, 2), minima(bonds, 3)
    nae_receipt = small_cross_check(archive, reached, bonds, "nae") if length is None else None
    common = set(marks)
    direct = ordinary_readings(reached)
    for row in direct:
        if set(row["marks"]) <= common:
            assert tuple(row[k] for k in ("end_steps", "holder_steps", "distinction_steps")) == (1, 2, 3)
    _, next_births, _ = ordinary.step(reached)
    target, = (row for row in next_births if row["spent"] == marks)
    verdict = widths(ordinary, source, reached, marks, first, length is None)
    assert verdict["all_loose_used"] == (not extra)
    assert len(target["fresh"]) == int(extra)

    result = {"source": source, "first_reached": reached, "marks": marks,
              "parent_support_names": sorted({d for r in first if len(r["parents"]) == 2
                                                for d in reached[r["knot"]]}),
              "proposal": verdict, "parity_next_fresh": len(target["fresh"]),
              "independent_sat": sat, "archived_nae_check": nae_receipt, "archived_parity_check": parity_receipt,
              "fragments": [{"holders": holders, "distinctions": table.names} for holders, table in fragments],
              "bonds": sorted(bonds, key=lambda bond: (len(bond), bond)),
              "bond_sizes": dict(sorted(Counter(map(len, bonds)).items())),
              "finite_pair_minima": finite_rows(pairs), "finite_triple_minima": finite_rows(triples),
              "proposal_pair_minima": [pairs.get(row) for row in combinations(marks, 2)],
              "proposal_triple_minimum": triples.get(marks),
              "ordinary_loose_pairs": direct}
    if parity is not None:
        parity_pairs = minima(parity, 2)
        result["parity_proposal_pair_minima"] = [parity_pairs.get(row) for row in combinations(marks, 2)]
        result["parity_proposal_triple_minimum"] = minima(parity, 3).get(marks)
        first_parent = next(birth for birth in first if len(birth["parents"]) == 2)
        proper_bond = tuple(sorted(reached[first_parent["knot"]]))
        superset = tuple(sorted(set(marks) | set(proper_bond)))
        projected = fragments[0][1].patterns(superset)
        assert len(projected) < 1 << len(superset)
        assert proper_bond in bonds and superset not in bonds
        result["nonprimitive_superset_control"] = {
            "support": superset, "proper_bond": proper_bond, "allowed_patterns": len(projected)
        }
    return result, pairs, triples


def finite_ball(names, roots, pairs, radius):
    return {
        d for d in names
        if d in roots or any(pairs.get(tuple(sorted((d, root))), float("inf")) <= radius for root in roots)
    }


def on_names(bonds, names):
    """Complete bond-size deck on the supplied subset, including singleton minima."""
    values = {}
    for bond in sorted(bonds, key=len):
        shown = sorted(set(bond) & names)
        for k in range(1, len(shown) + 1):
            for subset in combinations(shown, k):
                values.setdefault(subset, len(bond))
    return values


def compare_two_arms(base, extended):
    b, bp, bt = base
    e, ep, et = extended
    common_names = set(owners(b["source"]))
    match = {name: name for name in common_names}
    match.update(zip(b["marks"], e["marks"]))
    bnames = sorted(owners(b["first_reached"]))
    enames = sorted(owners(e["first_reached"]))
    assert set(match) == set(bnames) and set(match.values()) <= set(enames)
    assert len(match.values()) == len(set(match.values()))
    readouts = []
    # The complete finite radius range saturates at the largest finite reading.
    for r in range(max((*bp.values(), *ep.values()), default=0) + 1):
        left = finite_ball(bnames, b["marks"], bp, r)
        right = finite_ball(enames, e["marks"], ep, r)
        same_roster = {match[d] for d in left} == right
        counts = []
        histogram_agreement = []
        for arity, primary, other in ((2, bp, ep), (3, bt, et)):
            same = sum(
                primary.get(marks) == other.get(tuple(sorted(match[d] for d in marks)))
                for marks in combinations(sorted(left), arity)
            ) if same_roster else None
            counts.append((same, sum(1 for _ in combinations(left, arity))))
            histogram_agreement.append(
                Counter(primary.get(row) for row in combinations(sorted(left), arity))
                == Counter(other.get(row) for row in combinations(sorted(right), arity))
            )
        readouts.append({"radius": r, "base": sorted(left), "extended": sorted(right),
                         "same_roster_under_common_map": same_roster,
                         "equal_pair_entries": counts[0], "equal_triple_entries": counts[1],
                         "pair_histograms_agree": histogram_agreement[0],
                         "triple_histograms_agree": histogram_agreement[1]})
    parent_names = b["parent_support_names"]
    assert sorted(match[d] for d in parent_names) == e["parent_support_names"]
    decks = [on_names(arm["bonds"], set(arm["parent_support_names"])) for arm in (b, e)]
    same = {}
    for k in range(1, len(parent_names) + 1):
        same[str(k)] = sum(
            decks[0].get(subset) == decks[1].get(tuple(sorted(match[d] for d in subset)))
            for subset in combinations(parent_names, k)
        )
    return {"common_names": sorted(match.items()), "finite_balls": readouts,
            "equal_parent_support_subsets_by_order": same}


def recoding_control(base, length):
    data, pairs, triples = base
    stars = data["first_reached"]
    names = sorted(owners(stars))
    rng = Random(20261120007)
    shuffled = [d * 7 + 101 for d in names]
    rng.shuffle(shuffled)
    encoded = dict(zip(names, shuffled))
    reordered = [tuple(encoded[d] for d in row) for row in stars]
    rng.shuffle(reordered)
    fragments = ([(tuple(range(len(stars))), LiteralRelation(reordered))]
                 if length is None else projection_fragments(reordered))
    changed = all_bonds(fragments)
    assert changed == {tuple(sorted(encoded[d] for d in row)) for row in data["bonds"]}
    for k, old in [(2, pairs), (3, triples)]:
        assert minima(changed, k) == {tuple(sorted(encoded[d] for d in row)): value for row, value in old.items()}
    return sorted(encoded.items())


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=OUT)
    args = parser.parse_args()
    ordinary, archive = load_module(ORDINARY), load_module(NAE)
    result = {}
    for key, length in (("four_knot_source", None), ("doubled_interior_length_four", 4)):
        base = measurement(ordinary, archive, length, extra=False)
        extended = measurement(ordinary, archive, length, extra=True)
        comparison = compare_two_arms(base, extended)
        if length is not None:
            for row in comparison["finite_balls"]:
                assert row["same_roster_under_common_map"]
                assert row["equal_pair_entries"][0] == row["equal_pair_entries"][1]
                assert row["equal_triple_entries"][0] == row["equal_triple_entries"][1]
            n = len(base[0]["parent_support_names"])
            assert sum(comparison["equal_parent_support_subsets_by_order"].values()) == (1 << n) - 1
        result[key] = {"base": base[0], "extra": extended[0], "comparison": comparison,
                       "base_recoding": recoding_control(base, length)}
    result["units"] = "Smallest primitive nonfree projection size minus one. Absent pair/triple rows are infinite."
    result["ball"] = "Union of finite pair bond balls rooted at the three proposal inputs, with the roots retained."
    args.out.parent.mkdir(parents=True, exist_ok=True)
    with NamedTemporaryFile("w", dir=args.out.parent, delete=False) as out:
        temporary = Path(out.name)
        json.dump(result, out, separators=(",", ":"))
        out.write("\n")
    temporary.replace(args.out)


if __name__ == "__main__":
    main()
