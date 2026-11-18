"""Test anonymous distance descriptions on every triple of every width-19 type."""

import json
from collections import Counter
from dataclasses import dataclass
from itertools import combinations, permutations
from random import Random

WIDTH = 19
TRIPLES = tuple(combinations(range(WIDTH), 3))
CUTOFFS = (2, 3, 4, 5, WIDTH)
MODES = ("internal", *(f"rows_{k}" for k in CUTOFFS), "to_other_distinctions",
         "three_rows_and_parity_at_four", "three_rows_and_count_at_four")


def matrix_from_pairs(pairs):
    """Use WIDTH for infinity. A finite bond distance is at most WIDTH - 1."""
    table = [bytearray(WIDTH) for _ in range(WIDTH)]
    assert len(pairs) == WIDTH * (WIDTH - 1) // 2
    for (i, j), value in pairs.items():
        table[i][j] = table[j][i] = WIDTH if value is None else value
    return tuple(bytes(row) for row in table)


@dataclass
class Fixture:
    history: tuple
    table: tuple
    legal: frozenset


class Descriptions:
    def __init__(self, table):
        self.table = table
        # Count infinity in the last bucket. Self-distance zero is omitted.
        full = tuple(tuple(row.count(i) for i in range(2, WIDTH + 1)) for row in table)
        self.profiles = {k: tuple(counts[:k - 1] for counts in full) for k in CUTOFFS}
        self.pairs_at_four = sum(counts[2] for counts in full) // 2

    def opposite(self, triple):
        a, b, c = triple
        return self.table[b][c], self.table[a][c], self.table[a][b]

    def row_key(self, triple, opposite, cutoff):
        profiles = self.profiles[cutoff]
        return tuple(sorted((distance, *profiles[i]) for i, distance in zip(triple, opposite)))

    def other_key(self, triple, opposite):
        """Use a single common ordering of the three bits for every outside bit."""
        decorated = tuple((opposite[j], *self.profiles[WIDTH][i]) for j, i in enumerate(triple))
        first = tuple(sorted(decorated))
        other = [j for j in range(WIDTH) if j not in triple]
        outside = []
        for order in permutations(range(3)):
            if tuple(decorated[i] for i in order) == first:
                a, b, c = (self.table[triple[i]] for i in order)
                outside.append(tuple(sorted((a[j], b[j], c[j]) for j in other)))
        return first, min(outside)

    def successive(self, triple):
        opposite = self.opposite(triple)
        yield tuple(sorted(opposite))
        for k in CUTOFFS:
            yield self.row_key(triple, opposite, k)
        rest = self.other_key(triple, opposite)
        yield rest
        yield rest, (self.pairs_at_four % 2,)
        yield rest, (self.pairs_at_four,)


def encode(mode, key):
    """Pack exact values. No hashing or rounding is used in catalogue equality."""
    if mode == "internal":
        return bytes(key).hex()
    if mode.startswith("rows_"):
        return bytes(n for endpoint in key for n in endpoint).hex()
    if mode == "to_other_distinctions":
        marked, global_counts = key, ()
    else:
        marked, global_counts = key
    endpoints, other = marked
    # The three endpoint histograms are determined by the 51 incident values.
    values = [endpoint[0] for endpoint in endpoints]
    values.extend(distance for column in other for distance in column)
    values.extend(global_counts)
    return bytes(values).hex()


class TripleReader:
    """Compile the published positive descriptions once, then accept only distance tables."""

    def __init__(self, catalogue):
        self.mode = catalogue["description"]
        assert self.mode in ("three_rows_and_parity_at_four", "three_rows_and_count_at_four")
        self.by_count = {}
        for code in catalogue["legal_keys"]:
            values = bytes.fromhex(code)
            assert len(values) == 52
            opposite = tuple(values[:3])
            columns = values[3:-1]
            # For endpoint i, the two other opposite entries are its internal distances.
            endpoints = []
            for i in range(3):
                row = bytes(d for j, d in enumerate(opposite) if i != j) + columns[i::3]
                endpoints.append((opposite[i], *(row.count(k) for k in range(2, WIDTH + 1))))
            key = tuple(sorted(endpoints))
            by_internal = self.by_count.setdefault(values[-1], {})
            by_rows = by_internal.setdefault(tuple(sorted(opposite)), {})
            by_rows.setdefault(key, set()).add(code)

    def read(self, table):
        """Use 0 on the diagonal and WIDTH for any infinite distance."""
        desc = Descriptions(table)
        tag = desc.pairs_at_four % 2 if self.mode == "three_rows_and_parity_at_four" else desc.pairs_at_four
        by_internal = self.by_count.get(tag)
        if by_internal is None:
            return set()
        found = set()
        for triple in TRIPLES:
            opp = desc.opposite(triple)
            by_rows = by_internal.get(tuple(sorted(opp)))
            if by_rows is None:
                continue
            permitted = by_rows.get(desc.row_key(triple, opp, WIDTH))
            if permitted is None:
                continue
            key = desc.other_key(triple, opp), (tag,)
            if encode(self.mode, key) in permitted:
                found.add(triple)
        return found


def location(fixture, triple):
    return {"history": fixture.history, "old_inputs": triple}


def short_counterexample(fixtures, here, triple, legal_here, global_example):
    good, legal = (here, legal_here) if legal_here is not None else global_example
    return {
        "in_the_same_table": here == good,
        "legal": location(fixtures[good], legal),
        "forbidden": location(fixtures[here], triple),
    }


def analyze(fixtures):
    legal_examples = [dict() for _ in MODES]
    for index, fixture in enumerate(fixtures):
        if fixture.legal:
            reader = Descriptions(fixture.table)
            for triple in sorted(fixture.legal):
                for level, key in enumerate(reader.successive(triple)):
                    legal_examples[level].setdefault(key, (index, triple))

    totals = [0] * len(MODES)
    negatives = [None] * len(MODES)
    legal_total = sum(len(f.legal) for f in fixtures)
    for index, fixture in enumerate(fixtures):
        reader = Descriptions(fixture.table)
        local = [dict() for _ in MODES]
        for triple in sorted(fixture.legal):
            for level, key in enumerate(reader.successive(triple)):
                local[level].setdefault(key, triple)
        for triple in TRIPLES:
            if triple in fixture.legal:
                continue
            for level, key in enumerate(reader.successive(triple)):
                if key not in legal_examples[level]:
                    break  # every later description contains this one
                totals[level] += 1
                seen = negatives[level]
                if seen is None or (not seen["in_the_same_table"] and key in local[level]):
                    negatives[level] = short_counterexample(
                        fixtures, index, triple, local[level].get(key), legal_examples[level][key])

    results = {name: {"legal_descriptions": len(legal_examples[i]),
                      "forbidden_triples_matching_a_legal_description": totals[i],
                      "example": negatives[i]}
               for i, name in enumerate(MODES)}
    sufficient = next((i for i, count in enumerate(totals) if count == 0), None)
    catalogue = None
    if sufficient is not None:
        name = MODES[sufficient]
        codes = sorted(encode(name, key) for key in legal_examples[sufficient])
        assert len(set(codes)) == len(legal_examples[sufficient])
        catalogue = {"description": name, "legal_keys": codes}
        reader = TripleReader(catalogue)
        for fixture in fixtures:
            assert reader.read(fixture.table) == fixture.legal
        # An actual positive control on a renamed physical fixture.
        example = next(f for f in fixtures if f.legal)
        mapping = list(range(WIDTH))
        Random(19019).shuffle(mapping)
        renamed = tuple(bytes(example.table[a][b] for b in mapping) for a in mapping)
        rename_back = {tuple(sorted(mapping[i] for i in t)) for t in reader.read(renamed)}
        assert rename_back == set(example.legal)
        assert reader.read(example.table) == set(example.legal)
        # Exchanging one legal and one forbidden input keeps the count but changes membership.
        mutated = set(example.legal)
        mutated.remove(min(mutated))
        mutated.add(next(t for t in TRIPLES if t not in example.legal))
        assert len(mutated) == len(example.legal) and rename_back != mutated
    return {"width": WIDTH, "physical_types": len(fixtures),
            "physical_types_with_a_legal_triple": sum(bool(f.legal) for f in fixtures),
            "triples_per_type": len(TRIPLES), "triples_checked": len(TRIPLES) * len(fixtures),
            "legal_triples_counting_each_type_once": legal_total,
            "modes_in_order": MODES, "results": results, "catalogue": catalogue}


def same_three_distances_example():
    # Each pair within either candidate triple is separately legal.
    import check_population
    import check_reverse

    checks = ((0, 1, 2), (0, 3, 4, 5), (1, 6, 7), (2, 8, 9),
              (3, 6, 10, 11, 12), (4, 8, 13, 14), (7, 9, 15, 16), (5, 17, 18))
    table, bonds, span = check_reverse.bond_table(checks)
    scout, _, rules = check_population.inherited()
    menu = scout.actual_menu(rules, dict(enumerate(checks)))
    good, bad = (10, 13, 15), (10, 13, 17)
    assert frozenset(good) in menu and frozenset(bad) not in menu
    assert good in check_reverse.triple_menu(checks) and bad not in check_reverse.triple_menu(checks)
    for triple in (good, bad):
        assert all(frozenset((i,)) in menu for i in triple)
        assert all(frozenset(pair) in menu for pair in combinations(triple, 2))
    distances = Descriptions(table)
    assert distances.opposite(good) == distances.opposite(bad) == (6, 7, 7)
    assert table[15].count(2) == 0 and table[17].count(2) == 2
    return {"checks": checks, "allowed_rows": (1 << WIDTH) // len(span), "minimal_supports": len(bonds),
            "legal_triple": good, "forbidden_triple": bad, "mutual_distances_of_both": (6, 7, 7),
            "all_candidate_inputs_loose": True, "all_candidate_pairs_legal": True,
            "distance_two_neighbors_of_15": [i for i, v in enumerate(table[15]) if v == 2],
            "distance_two_neighbors_of_17": [i for i, v in enumerate(table[17]) if v == 2]}


def replay_catalogue(catalogue):
    """Test the serialized reader on every independently generated and named incidence."""
    import check_reverse

    reader = TripleReader(catalogue)
    totals = {}
    for size in (7, 8, 9):
        population = with_triples = triple_count = 0
        for checks, _ in check_reverse.presentations(size, Counter()):
            table, _, _ = check_reverse.bond_table(checks)
            actual = check_reverse.triple_menu(checks)
            assert reader.read(table) == actual
            population += 1
            with_triples += bool(actual)
            triple_count += len(actual)
        totals[size] = {"physical_types": population, "with_legal_triples": with_triples,
                        "legal_triples": triple_count}
    return totals


def main():
    import check_population

    fixtures = [Fixture(record.fixture.history, matrix_from_pairs(record.table),
                        frozenset(tuple(sorted(t)) for t in record.menu if len(t) == 3))
                for record in check_population.width_records()]
    result = analyze(fixtures)
    result["same_three_distances_example"] = same_three_distances_example()
    if result["catalogue"] is not None:
        result["independent_reverse_replay"] = replay_catalogue(result["catalogue"])
    return result


if __name__ == "__main__":
    print(json.dumps(main(), indent=2, sort_keys=True))
