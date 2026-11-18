"""Exact small projections of the literal cut/parity relation with two probes.

The factorization uses only the parity equations and the eight original rows.
No coordinates enter any query. Public projections pack the first requested
distinction in the least significant bit.
"""

from functools import cached_property
from itertools import combinations, product


CUT_ROWS = frozenset((0, 15, 51, 85, 170, 204, 240, 255))


def bits(word):
    while word:
        low = word & -word
        yield low.bit_length() - 1
        word ^= low


def pack(word, positions):
    return sum(((word >> position) & 1) << i for i, position in enumerate(positions))


class DistanceOracle:
    """A permanent snapshot plus at most two conservative betweenness probes.

    `checks` lists the supports of even parity equations. `originals` orders
    the eight columns of `old_rows` (default uses the literal cube order).
    All names may be arbitrary hashables. A probe is `(a, b, p, q)`, with
    permanent middles `a,b` and private fresh endpoints `p,q`.
    """

    def __init__(self, permanent, checks, originals, old_rows=None):
        self.permanent = tuple(permanent)
        self.indices = {name: i for i, name in enumerate(self.permanent)}
        originals = tuple(originals)
        if len(self.indices) != len(self.permanent):
            raise ValueError("Permanent names must be distinct")
        if len(originals) != 8 or len(set(originals)) != 8 or not set(originals) <= self.indices.keys():
            raise ValueError("Expected eight distinct originals among the permanent names")
        self.old_rows = CUT_ROWS if old_rows is None else frozenset(old_rows)
        if not self.old_rows or any(not 0 <= word < 256 for word in self.old_rows):
            raise ValueError("Expected a nonempty set of eight-bit original rows")
        marks = tuple(self.indices[name] for name in originals)
        mark_mask = sum(1 << i for i in marks)
        pivots = {}
        for check in checks:
            check = tuple(check)
            if not check or len(set(check)) != len(check):
                raise ValueError("A parity support must have distinct names")
            row = sum(1 << self.indices[name] for name in check)
            while row & ~mark_mask:
                pivot = (row & ~mark_mask).bit_length() - 1
                if pivot not in pivots:
                    pivots[pivot] = row
                    break
                row ^= pivots[pivot]
            else:
                if row:
                    raise ValueError("The parity cover constrains original words")

        # Write every permanent bit as a linear form on the original values
        # and an independent free parameter for each unpivoted nonoriginal.
        forms = [0] * len(self.permanent)
        for i, position in enumerate(marks):
            forms[position] = 1 << i
        free = [i for i, form in enumerate(forms) if not form and i not in pivots]
        for j, i in enumerate(free, start=8):
            forms[i] = 1 << j
        for i, row in sorted(pivots.items()):
            for j in bits(row ^ (1 << i)):
                forms[i] ^= forms[j]
        self.free_dimension = len(free)
        self._forms = tuple(form >> 8 for form in forms)
        self._offsets = tuple(sum((((form & row).bit_count() & 1) << i)
                                  for i, form in enumerate(forms)) for row in sorted(self.old_rows))
        self._middle_cache = {}

    def _ordinary_projection(self, positions):
        free_forms = tuple(self._forms[i] for i in positions)
        used = 0
        for form in free_forms:
            used |= form
        span = {0}
        full_size = 1 << len(positions)
        for j in bits(used):
            generator = sum(((form >> j) & 1) << i for i, form in enumerate(free_forms))
            if generator not in span:
                span |= {word ^ generator for word in span}
                if len(span) == full_size:
                    return frozenset(range(full_size))
        offsets = {pack(offset, positions) for offset in self._offsets}
        return frozenset(offset ^ word for offset in offsets for word in span)

    def _checked_probes(self, probes):
        probes = tuple(tuple(probe) for probe in probes)
        if len(probes) > 2:
            raise ValueError("At most two probes may be live")
        endpoints = set()
        for a, b, p, q in probes:
            if a == b or a not in self.indices or b not in self.indices:
                raise ValueError("The tested middles must be distinct permanent names")
            if p == q or {p, q} & (self.indices.keys() | endpoints):
                raise ValueError("Each probe must contribute two private fresh names")
            endpoints.update((p, q))
        return probes

    def project(self, support, probes=()):
        """Return the exact existential marginal on the ordered support."""
        support = tuple(support)
        if len(set(support)) != len(support):
            raise ValueError("A projection support must have distinct names")
        return self._project(support, self._checked_probes(probes))

    def _project(self, support, probes):
        if not probes:
            return self._ordinary_projection(tuple(self.indices[name] for name in support))
        displayed = {name: i for i, name in enumerate(support)}
        retained = [name for name in support if name in self.indices]
        known = self.indices.keys() | {end for probe in probes for end in probe[2:]}
        if not displayed.keys() <= known:
            raise ValueError("Unknown name in projection")
        needed = retained + [middle for a, b, p, q in probes if p in displayed and q in displayed
                             for middle in (a, b)]
        order = {name: i for i, name in enumerate(dict.fromkeys(needed))}
        permanent_rows = self._ordinary_projection(tuple(self.indices[name] for name in order))
        fibers = []
        for a, b, p, q in probes:
            ends = tuple(1 << displayed[end] for end in (p, q) if end in displayed)
            if len(ends) == 2:
                fibers.append((ends, 1 << order[a], 1 << order[b]))
            elif ends:
                fibers.append(((0, ends[0]), 0, 0))
        shown = [(1 << order[name], 1 << displayed[name]) for name in retained]
        result = set()
        for row in permanent_rows:
            offset = sum(out for bit, out in shown if row & bit)
            choices = []
            for ends, a, b in fibers:
                allows_equal = a and bool(row & a) == bool(row & b)
                equal = sum(ends) if row & a else 0
                choices.append((*ends, equal) if allows_equal else ends)
            result.update(offset | sum(ends) for ends in product(*choices))
        return frozenset(result)

    @cached_property
    def _permanent_bonds(self):
        groups = {}
        for i, form in enumerate(self._forms):
            groups.setdefault(form, []).append(i)
        zeros = groups.pop(0, ())

        def candidates():
            yield from combinations(zeros, 3)
            for group in groups.values():
                yield from combinations(group, 3)
                for pair in combinations(group, 2):
                    for zero in zeros:
                        yield (*pair, zero)
            masks = sorted(groups)
            for left, right in combinations(masks, 2):
                third = left ^ right
                if third > right and third in groups:
                    yield from product(groups[left], groups[right], groups[third])

        free_pairs = {}
        result = []
        for support in candidates():
            if len(self._ordinary_projection(support)) == 8:
                continue
            pairs = combinations(sorted(support), 2)
            for pair in pairs:
                if pair not in free_pairs:
                    free_pairs[pair] = len(self._ordinary_projection(pair)) == 4
                if not free_pairs[pair]:
                    break
            else:
                result.append(tuple(sorted(support)))
        return tuple(sorted(result))

    def _probe_middles(self, a, b):
        key = tuple(sorted((self.indices[a], self.indices[b])))
        if key not in self._middle_cache:
            result = []
            if {0, 3} <= self._ordinary_projection(key):
                for i in range(len(self.permanent)):
                    support = (*key, i)
                    # A tested identity always gives a constrained triple if
                    # both equal endpoint values are feasible. It is open.
                    if i in key:
                        result.append(i)
                    elif len(self._ordinary_projection((i,))) == 2:
                        rows = self._ordinary_projection(support)
                        if not {0, 3, 4, 7} <= rows:
                            result.append(i)
            self._middle_cache[key] = tuple(result)
        return self._middle_cache[key]

    def ternary_bonds(self, probes=()):
        """Return all exact K1–K3 supports of arity three."""
        probes = self._checked_probes(probes)
        permanent = tuple(tuple(self.permanent[i] for i in support)
                          for support in self._permanent_bonds)
        temporary = tuple((p, q, self.permanent[i]) for a, b, p, q in probes
                          for i in self._probe_middles(a, b))
        return permanent + temporary

    def threshold_two(self, probes=()):
        """Return the exact distance-two graph, including isolated names."""
        probes = self._checked_probes(probes)
        graph = {name: set() for name in self.permanent}
        for _, _, p, q in probes:
            graph[p] = set()
            graph[q] = set()
        for support in self.ternary_bonds(probes):
            for a, b in combinations(support, 2):
                graph[a].add(b)
                graph[b].add(a)
        return graph

    def probe_distance(self, a, b, probes, max_distance=4):
        """Return the true capped distance for a pair touching a live endpoint.

        None means above the requested cutoff, including infinity. Every
        minimal support using a probe endpoint also uses its mate.
        """
        probes = self._checked_probes(probes)
        ends = tuple(tuple(probe[2:]) for probe in probes)
        known = self.indices.keys() | {bit for pair in ends for bit in pair}
        if a == b or a not in known or b not in known or not 2 <= max_distance <= 5:
            raise ValueError("Expected distinct current names and cutoff 2 through 5")
        required_pairs = [pair for pair in ends if a in pair or b in pair]
        if not required_pairs:
            raise ValueError("This query requires an endpoint of a live probe")
        if b in self.threshold_two(probes)[a]:
            return 2
        required = tuple(dict.fromkeys((a, b, *(bit for pair in required_pairs for bit in pair))))
        permanent = tuple(bit for bit in self.permanent if bit not in required)
        optional = [()] + [pair for pair in ends if pair not in required_pairs]
        for size in range(max(4, len(required)), max_distance + 2):
            for mate_pair in optional:
                remaining = size - len(required) - len(mate_pair)
                if remaining < 0:
                    continue
                for extra in combinations(permanent, remaining):
                    support = required + mate_pair + extra
                    if len(self._project(support, probes)) == 1 << size:
                        continue
                    if all(len(self._project(support[:i] + support[i + 1:], probes)) == 1 << (size - 1)
                           for i in range(size)):
                        return size - 1
        return None


def literal_extensions(assigned, permanent, probes):
    """Slow truth-table reference, including the literal two clauses per probe."""
    endpoints = tuple(name for probe in probes for name in probe[2:])
    names = (*permanent, *endpoints)
    for word in assigned:
        values = {name: (word >> i) & 1 for i, name in enumerate(permanent)}
        for trial in product((0, 1), repeat=len(endpoints)):
            values.update(zip(endpoints, trial, strict=True))
            if all(values[p] != values[q] or values[p] == values[a] == values[b]
                   for a, b, p, q in probes):
                yield sum(values[name] << i for i, name in enumerate(names))


def small_regressions(seed):
    fixtures = (
        ("bare", 8, (), ((0, 1, 8, 9), (2, 3, 10, 11))),
        ("rooted", 10, ((0, 8, 9),), ((8, 9, 10, 11), (1, 8, 12, 13))),
        ("two_junctions", 12, ((0, 8, 9), (8, 4, 10, 11)),
         ((0, 10, 12, 13), (6, 11, 14, 15))),
        ("tie_and_fixed_distinction_control", 11, ((0, 8), (0, 9), (10,)), ((1, 8, 11, 12),)),
    )
    reports = {}
    for label, width, checks, probes in fixtures:
        gate_masks = [sum(1 << j for j in check) for check in checks]
        base = {word for word in range(1 << width) if word & 255 in CUT_ROWS and
                all((word & mask).bit_count() % 2 == 0 for mask in gate_masks)}
        rows = frozenset(literal_extensions(base, tuple(range(width)), probes))
        total = width + 2 * len(probes)
        oracle = DistanceOracle(range(width), checks, tuple(range(8)))
        assert (len(CUT_ROWS) << oracle.free_dimension) == len(base)
        assert oracle.project(range(width), probes) == base
        matrix, supports = seed.bond_table(rows, total)
        assert {frozenset(positions) for positions in supports if len(positions) == 3} == {
            frozenset(positions) for positions in oracle.ternary_bonds(probes)
        }
        projections = 0
        for size in range(4):
            for support in combinations(range(total), size):
                # Reverse the requested order to exercise exact bit placement.
                support = support[::-1]
                expected = frozenset(pack(word, support) for word in rows)
                assert oracle.project(support, probes) == expected, (label, support)
                projections += 1

        capped_pairs = beyond_cutoff = 0
        graph = oracle.threshold_two(probes)
        for a, b in combinations(range(total), 2):
            expected = matrix[a][b]
            assert (b in graph[a]) == (expected == 2), (label, a, b)
            if b >= width:
                capped = oracle.probe_distance(a, b, probes, max_distance=4)
                assert capped == (expected if expected is not None and expected <= 4 else None), (label, a, b)
                if capped is None:
                    beyond_cutoff += 1
                    through_five = oracle.probe_distance(a, b, probes, max_distance=5)
                    assert through_five == (5 if expected == 5 else None), (label, a, b)
                capped_pairs += 1
        if label == "bare":
            assert len(oracle.project((8, 9, 10, 11), probes)) == 16
            assert oracle.probe_distance(8, 10, probes, max_distance=3) is None
            assert oracle.probe_distance(8, 10, probes, max_distance=4) == 4
        if label == "tie_and_fixed_distinction_control":
            assert len(oracle.project((0, 8), probes)) == 2 and not graph[10]
            assert matrix[10][11] is None and oracle.probe_distance(10, 11, probes) is None

        names = {i: f"name-{(7 * i + 8) % 19}" for i in range(total)}
        named_checks = [tuple(names[i] for i in check) for check in reversed(checks)]
        named_probes = [tuple(names[i] for i in probe) for probe in reversed(probes)]
        renamed = DistanceOracle(tuple(names[i] for i in reversed(range(width))),
                                 named_checks, tuple(names[i] for i in range(8)))
        assert renamed.threshold_two(named_probes) == {
            names[a]: {names[b] for b in neighbors} for a, neighbors in graph.items()
        }
        assert renamed.project(tuple(names[i] for i in reversed(range(total))), named_probes) == {
            pack(word, reversed(range(total))) for word in rows
        }
        reports[label] = {"literal_rows": len(rows), "permanent_rows": len(base),
                          "individual_projections_checked": projections, "capped_pairs_checked": capped_pairs,
                          "pairs_above_four_checked_against_cutoff_five": beyond_cutoff,
                          "distance_two_pairs": sum(map(len, graph.values())) // 2}

    # Dropping the constraint on b would allow a=0, b=1, p=q=0.
    seed_oracle = DistanceOracle(range(8), (), range(8))
    probe = (0, 1, 8, 9)
    assert 2 in seed_oracle.project((0, 1)) and 2 not in seed_oracle.project(probe, (probe,))
    return reports


def cut_reference(aligned, model, support, probes):
    """Independent source check using the accepted component parity reference."""
    retained = tuple(sorted({name for name in support if isinstance(name, int)} |
                            {name for probe in probes for name in probe[:2]}))
    mask = sum(1 << i for i in retained)
    base = aligned.projected_rows(model, mask)
    extension_names = (*retained, *(name for probe in probes for name in probe[2:]))
    extract = tuple(extension_names.index(name) for name in support)
    return frozenset(pack(word, extract) for word in literal_extensions(base, retained, probes))


def large_regressions(aligned):
    data = aligned.short_supports(4)
    model = data.model
    stage = []
    source_order = sorted(range(len(model.vertices)), key=lambda i: (
        model.vertices[i] not in aligned.MARK_VERTICES, sum(model.vertices[i]), model.vertices[i]
    ))
    for size in (0, 1, 4, 8, 20, 35):
        entered = source_order[:size]
        checks = [tuple(bits(model.stars[i])) for i in entered]
        names = set(model.mark_bits) | {name for check in checks for name in check}
        oracle = DistanceOracle(sorted(names), checks, model.mark_bits, aligned.CUT_WORDS)
        mask = sum(1 << i for i in names)
        pure = {frozenset(bits(support)) for support in data.mixed
                if support.bit_count() == 3 and support & ~mask == 0}
        assert {frozenset(support) for support in oracle.ternary_bonds()} == pure

        a, b = model.mark_bits[:2]
        c = max(names - set(model.mark_bits), default=model.mark_bits[-1])
        probes = ((a, b, "p", "q"), (a, c, "u", "v"))
        reference = set(pure)
        projections = 0
        for a, b, p, q in probes:
            for distinct in sorted(names):
                support = (p, q, distinct)
                marginal = cut_reference(aligned, model, support, ((a, b, p, q),))
                assert oracle.project(support, probes) == marginal, (size, support)
                if len(marginal) < 8 and all(len({pack(row, positions) for row in marginal}) == 4
                                             for positions in combinations(range(3), 2)):
                    reference.add(frozenset(support))
                projections += 1
        assert {frozenset(support) for support in oracle.ternary_bonds(probes)} == reference

        # Both completed probes can condition on the shared middle. Opposite
        # equal-endpoint values give a missing state on the four endpoints.
        both_pairs = ("p", "q", "u", "v")
        cross = cut_reference(aligned, model, both_pairs, probes)
        assert cross == oracle.project(both_pairs, probes) and len(cross) < 16
        assert all(len({pack(word, support) for word in cross}) == 8
                   for support in combinations(range(4), 3))
        assert oracle.probe_distance("p", "u", probes, 4) == 3
        stage.append({"junctions": size, "permanent_distinctions": len(names),
                      "permanent_states": len(CUT_ROWS) << oracle.free_dimension,
                      "permanent_ternary_bonds": len(pure), "probed_ternary_bonds": len(reference),
                      "live_ternary_projections_checked": projections,
                      "cross_probe_bond_distance": 3, "cross_probe_projection_states": len(cross)})
    return stage


def main():
    from hashlib import sha256
    from importlib.util import module_from_spec, spec_from_file_location
    import json
    from pathlib import Path
    import sys

    root = Path(__file__).resolve().parents[3]
    sources = {
        "seed": "proofs/BOOTSTRAP-ALIGNMENT-20261117-001/"
                "BOOTSTRAP-ALIGNMENT-20261117-001-P001_distance_start/check_seed.py",
        "aligned": "proofs/ALIGNED-NEXT-JOIN-20261117-001/"
                   "ALIGNED-NEXT-JOIN-20261117-001-P001_aligned_reader/check_aligned.py",
    }
    modules = {}
    for name, path in sources.items():
        spec = spec_from_file_location(f"oracle_reference_{name}", root / path)
        module = module_from_spec(spec)
        sys.modules[spec.name] = module
        spec.loader.exec_module(module)
        modules[name] = module
    assert modules["seed"].seed_rows()[0] == CUT_ROWS
    result = {
        "input_sources": {path: sha256((root / path).read_bytes()).hexdigest() for path in sources.values()},
        "small_literal_regressions": small_regressions(modules["seed"]),
        "aligned_component_parity_regressions": large_regressions(modules["aligned"]),
        "reversed_packing_and_capped_probe_distances_checked": True,
        "erasure_and_missing_second_betweenness_control": True,
        "separate_cross_probe_distance_four_control": True,
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
