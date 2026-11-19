"""Census small binary-third incidences and compare exact full and clipped tables."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
import argparse
import json
import subprocess
import sys


PROOFS = Path(__file__).resolve().parents[2]


def inherited(suffix, slug, filename):
    ticket = "VARIABLE-OUTPUT-READER-20261118-001" + suffix
    path = PROOFS / ticket / f"{ticket}-P001_{slug}" / filename
    spec = spec_from_file_location("binary_third_" + suffix, path)
    obj = module_from_spec(spec)
    spec.loader.exec_module(obj)
    return obj


previous = inherited("K", "third_three_fresh", "cases.py")
checker, algebra = previous.reader, previous.prior
exact, literal = checker.exact, checker.literal
bits, mask = checker.bits, checker.mask


@cache
def pairs(width):
    return tuple(combinations(range(width), 2))


@dataclass(frozen=True, slots=True)
class Fixture:
    neighbors: tuple
    loose: tuple
    extra: bool
    actions: tuple

    @property
    def sites(self):
        return len(self.loose)

    @property
    def width(self):
        return 2 * self.sites + 3 + self.extra

    @property
    def shrinks(self):
        return 7 + self.extra - sum(self.loose)

    def groups(self, counts):
        live = tuple(i for i, count in enumerate(self.loose) if count)
        for p in counts:
            for group in combinations(live, p):
                neighbors = [self.neighbors[i] for i in group]
                enough_witnesses = all(a & b for a, b in combinations(neighbors, 2))
                forbidden_common = p == 3 and neighbors[0] & neighbors[1] & neighbors[2]
                if enough_witnesses and not forbidden_common:
                    yield group

    def grow(self, group, fresh):
        newborn = self.sites
        touch = mask(group)
        added = 1 << newborn
        neighbors = tuple(value | (added if i in group else 0) for i, value in enumerate(self.neighbors))
        loose = tuple(n - (i in group) for i, n in enumerate(self.loose))
        extra = self.extra or (len(group), fresh) == (2, 3)
        return Fixture((*neighbors, touch), (*loose, fresh), extra, (*self.actions, (group, fresh)))

    def line(self):
        return " ".join(map(str, (self.sites, *self.neighbors, *self.loose))) + "\n"

    def history(self):
        # The native cut engine labels shared distinctions by site pairs and then loose ones by holder.
        rows = [[] for _ in self.loose]
        name = 0
        for i, j in pairs(self.sites):
            if self.neighbors[i] & (1 << j):
                rows[i].append(name)
                rows[j].append(name)
                name += 1
        for row, count in zip(rows, self.loose, strict=True):
            row.extend(range(name, name + count))
            name += count
        assert name == self.width
        return previous.named(rows)


def starters():
    seed = Fixture((0,), (3,), False, ())
    first = seed.grow((0,), 3)
    return tuple(first.grow((i,), 3) for i in (0, 1))


def color_incidence(fixture):
    matrix = tuple(tuple(row >> j & 1 for j in range(fixture.sites)) for row in fixture.neighbors)
    invariant, colors = exact.refine(matrix, fixture.loose)
    # Hash equality only requests a full isometry search. The search checks every incidence.
    return exact.ColoredMatrix(matrix, (hash(invariant),), colors)


def next_layer(layer):
    buckets = defaultdict(list)
    literal_keys = set()
    for owner in layer:
        for group in owner.groups((2, 3)):
            for h in (2, 3) if len(group) == 2 and not owner.extra else (2,):
                following = owner.grow(group, h)
                literal_key = following.extra, following.neighbors, following.loose
                if literal_key in literal_keys:
                    continue
                literal_keys.add(literal_key)
                color = color_incidence(following)
                bucket = buckets[following.extra, color.invariant]
                if not any(next(exact.isometries(old, color), None) is not None for old, _ in bucket):
                    bucket.append((color, following))
    return tuple(shape for bucket in buckets.values() for _, shape in bucket)


@dataclass(slots=True)
class Observation:
    fixture: Fixture
    entries: tuple
    history: tuple
    stars: frozenset
    menu: frozenset

    def matrix(self, cutoff):
        return checker.matrix(dict(zip(pairs(self.fixture.width), self.entries, strict=True)), cutoff)


def measured(fixtures, engine):
    if not fixtures:
        return []
    response = subprocess.run([engine], input="".join(f.line() for f in fixtures),
                              text=True, stdout=subprocess.PIPE, check=True).stdout.splitlines()
    records = []
    for shape, line in zip(fixtures, response, strict=True):
        ends = tuple(ord(encoded) - ord("!") for encoded in line)
        assert len(ends) == len(pairs(shape.width))
        history = shape.history()
        holders, neighbors = literal.incidence(history)
        menu = frozenset(mask(group) for group in literal.direct_triples(holders, neighbors))
        assert bool(menu) == bool(next(shape.groups((3,)), None))
        records.append(Observation(shape, ends, history, frozenset(mask(row) for _, row in history), menu))
    return records


def transport(words, mapping):
    return frozenset(mask(mapping[i] for i in bits(word)) for word in words)


def summary(history):
    trace = checker.replay(history)
    special = next((row for row in trace[3:] if len(row["fresh"]) == 3), None)
    return {"chronological_supports": [row["support"] for row in trace],
            "moves": [[row["operands"], row["fresh"], row["earlier_pair_witnesses"]] for row in trace],
            "third_three_fresh_parent_count": len(special["operands"]) if special else None}


def witness(left, right_history, mapping, cutoff=None):
    t_left, b_left, m_left = checker.measure(left.history, independent=True)
    t_right, b_right, m_right = checker.measure(right_history, independent=True)
    assert left.entries == tuple(t_left[pair] for pair in pairs(left.fixture.width))
    differences = [(pair, k, t_right[tuple(sorted(mapping[i] for i in pair))])
                   for pair, k in sorted(t_left.items()) if t_right[tuple(sorted(mapping[i] for i in pair))] != k]
    assert (not differences if cutoff is None else all(min(a, b) > cutoff for _, a, b in differences))
    image = transport(map(mask, m_left), mapping)
    right_menu = frozenset(map(mask, m_right))
    l_stars = transport(left.stars, mapping)
    r_stars = frozenset(mask(row) for _, row in right_history)
    right_only = sorted(right_menu - image)
    transported_only = sorted(image - right_menu)
    inverse = exact.inverse(mapping)
    if transported_only:
        mapped_mark = bits(transported_only[0])
        mark = tuple(sorted(inverse[i] for i in mapped_mark))
    elif right_only:
        mapped_mark = bits(right_only[0])
        mark = tuple(sorted(inverse[i] for i in mapped_mark))
    elif m_left:
        mark = min(m_left)
        mapped_mark = tuple(sorted(mapping[i] for i in mark))
    else:
        mark = mapped_mark = None

    def mark_minimum(marked, bonds):
        if marked is None:
            return None
        names = mask(marked)
        return min((bond.bit_count() for bond in bonds if bond & names == names), default=None)

    return {"width": left.fixture.width, "left": summary(left.history), "right": summary(right_history),
            "permutation": mapping, "compared_pairs": len(t_left),
            "moved_left_supports": [bits(word) for word in sorted(l_stars - r_stars)],
            "unmatched_right_supports": [bits(word) for word in sorted(r_stars - l_stars)],
            "left_menu": sorted(m_left), "right_menu": sorted(m_right),
            "transported_left_only": [bits(word) for word in transported_only],
            "right_only": [bits(word) for word in right_only],
            "marked_example": {"left": mark, "left_legal": mark in m_left,
                               "right": mapped_mark, "right_legal": mapped_mark in m_right,
                               "left_minimum_bond_size": mark_minimum(mark, b_left),
                               "right_minimum_bond_size": mark_minimum(mapped_mark, b_right)},
            "named_full_differences": differences,
            "left_K_upper_triangle": tuple(t_left[pair] for pair in sorted(t_left)),
            "right_K_upper_triangle": tuple(t_right[pair] for pair in sorted(t_right))}


def table_screen(records, cutoff, grade_stars):
    bins = defaultdict(list)
    counts = Counter(tables=len(records))
    first = first_self = first_empty = None
    for record in records:
        matrix = record.matrix(cutoff)
        quotient = exact.Quotient.make(matrix)
        bucket = bins[quotient.colored.invariant]
        if record.menu or grade_stars:
            _, _, generators = quotient.automorphisms()
            counts["self_generators" if record.menu else "empty_self_generators"] += len(generators)
            for image in generators:
                assert exact.disagreement(matrix, matrix, image) is None
                changed_menu = transport(record.menu, image) != record.menu
                changed_stars = grade_stars and transport(record.stars, image) != record.stars
                if changed_menu:
                    counts["opposing_self_generators"] += 1
                if changed_stars:
                    counts["star_changing_self_generators" if record.menu else "empty_star_changing_self_generators"] += 1
                if (changed_menu or changed_stars) and record.menu and first_self is None:
                    first_self = (record, record.history, image)
                    if first is None:
                        first = first_self
                if changed_stars and not record.menu and first_empty is None:
                    first_empty = (record, record.history, image)
        for other, other_matrix, other_quotient in bucket:
            live = bool(record.menu or other.menu)
            if not live and not grade_stars:
                continue
            counts["cross_candidates" if live else "empty_cross_candidates"] += 1
            found = next(exact.isometries(quotient.colored, other_quotient.colored), None)
            if found is None:
                continue
            image = quotient.lift(other_quotient, found)
            assert exact.disagreement(matrix, other_matrix, image) is None
            changed_menu = transport(record.menu, image) != other.menu
            if changed_menu:
                counts["opposing_cross_lifts"] += 1
            if grade_stars:
                assert transport(record.stars, image) != other.stars
                counts["same_table_distinct_incidences" if live else "empty_same_table_distinct_incidences"] += 1
            if first is None and live and (grade_stars or changed_menu):
                first = (record, other.history, image)
            if first_empty is None and not live:
                first_empty = (record, other.history, image)
        bucket.append((record, matrix, quotient))
    return dict(counts), first, first_self, first_empty


def unrestricted(observation):
    """Enumerate the full-table compatible spaces and literal rival support sets."""
    width = observation.fixture.width
    table = dict(zip(pairs(width), observation.entries, strict=True))
    physical = frozenset(algebra.span(observation.stars))
    pooled = {pair: k if k <= 5 else None for pair, k in table.items()}
    common, _, _, _ = algebra.force_from_table(pooled, width, 5)
    rank_five = algebra.rank(common)
    assert common <= physical
    if rank_five == observation.fixture.sites:
        alternatives = [physical]
    else:
        pooled = {pair: k if k <= 6 else None for pair, k in table.items()}
        common, residual, permissible, _ = algebra.force_from_table(pooled, width, 6)
        if not residual:
            assert common == physical
            alternatives = [physical]
        else:
            _, alternatives, _ = algebra.all_compatible_spaces(table, width, common, residual, permissible)
            assert physical in alternatives
            # At even width a unique ternary gives at least three three-fresh moves in any rival.
            alternatives = [code for code in alternatives if algebra.rank(code) <= observation.fixture.sites]

    counts = Counter(rank_five=rank_five, full_compatible_spaces=len(alternatives))
    for code in alternatives:
        if code == physical and observation.fixture.shrinks <= 2:
            counts["same_code_rigidity"] += 1
            continue
        histories, processed = previous.physical_realizations(code)
        counts["rival_search_prefixes"] += processed["reachable_prefix_sets"]
        counts["rival_search_realizations"] += len(histories)
        for history in histories:
            if frozenset(mask(row) for _, row in history) != observation.stars:
                return counts, (observation, history, tuple(range(width)))
    return counts, None


def advertised_lower_control():
    old = previous.load_source("frontier.json")["sharp_distance_four"]
    steps = list(map(tuple, old["junction_supports"]))
    steps[8] = (*steps[8], 25)
    history = previous.named(steps)
    table, _, menu = checker.measure(history, independent=True)
    signal = previous.transposition(table, menu, 26, tuple(old["transposition"]), tuple(old["legal_mark"]))
    assert signal["changed_entries"]["D3"] == 0 and signal["changed_entries"]["D4"] == 8
    assert signal["changed_entries"]["full"] == 24
    return {"literal_witness": summary(history), "legal_triples": sorted(menu), **signal}


def literal_width20_controls(records):
    deck = [(checker.grow(checker.SEED, ((0,), (i,)), (3, 3)), False) for i in (0, 1)]
    for _ in range(5):
        grown = []
        for history, special in deck:
            holders, neighbors = literal.incidence(history)
            live = sorted(site for site, _ in history if any(owners == [site] for owners in holders.values()))
            for p in (2, 3):
                for parents in combinations(live, p):
                    if not literal.legal(parents, neighbors):
                        continue
                    operands = tuple(min(bit for bit, owners in holders.items() if owners == [site]) for site in parents)
                    for h in (2, 3) if p == 2 and not special else (2,):
                        grown.append((checker.named_step(history, operands, h, len(holders)), special or h == 3))
        deck = grown

    indexed = defaultdict(list)
    for i, record in enumerate(records):
        axes = color_incidence(record.fixture)
        indexed[axes.invariant].append((i, axes))
        table, _, menu = checker.measure(record.history, independent=True)
        assert tuple(table[pair] for pair in pairs(20)) == record.entries
        assert frozenset(map(mask, menu)) == record.menu
    reached = set()
    count = 0
    for history, special in deck:
        if not special:
            continue
        count += 1
        holders, neighbors = literal.incidence(history)
        order = tuple(site for site, _ in history)
        graph = tuple(mask(i for i, key in enumerate(order) if key in neighbors[site]) for site in order)
        loose = tuple(sum(owners == [site] for owners in holders.values()) for site in order)
        shape = color_incidence(Fixture(graph, loose, True, ()))
        i, = (i for i, expected in indexed[shape.invariant] if next(exact.isometries(shape, expected), None) is not None)
        reached.add(i)
    assert reached == set(range(len(records)))
    return {"literal_histories_at_width_20": count, "distinct_physical_types": len(reached),
            "independent_pair_entries": len(records) * len(pairs(20))}


def run(last, engine, check_rivals):
    layer = starters()
    stages = []
    lower = lower_self = overlap = empty_control = None
    for depth in range(4, (last - 4) // 2 + 1):
        assert layer and all(f.sites == depth - 1 for f in layer)
        layer = next_layer(layer)
        present = [shape for shape in layer if shape.extra]
        tally = Counter((s.shrinks, bool(next(s.groups((3,)), None))) for s in present)
        width = 2 * depth + 4
        stats = {"width": width, "junctions": depth, "physical_types": len(present),
                 "counts_by_shrinks_and_nonempty_menu": [(shrinks, int(positive), number)
                                                         for (shrinks, positive), number in sorted(tally.items())]}
        critical = [shape for shape in present if shape.shrinks >= 2]
        if lower is None and any(positive for _, positive in tally):
            records = measured(present, engine)
            stats["D3_screen"], first, self_only, _ = table_screen(records, 4, False)
            if first:
                lower = witness(*first, cutoff=4)
            if self_only:
                lower_self = witness(*self_only, cutoff=4)
            if width == 20:
                stats["literal_validation"] = literal_width20_controls(records)
                stats["D4_screen"], bad_D4, _, _ = table_screen(records, 5, True)
                assert bad_D4 is None
            critical_records = [rec for rec in records if rec.fixture.shrinks >= 2]
        else:
            critical_records = measured(critical, engine)
        stats["full_screen"], first, _, empty = table_screen(critical_records, None, True)
        if first:
            overlap = {"rival_domain": "both in the binary-third family", "certificate": witness(*first)}
        if empty and empty_control is None:
            empty_control = witness(*empty)
        if check_rivals and overlap is None:
            audit = Counter()
            outcomes = Counter()
            for rec in critical_records:
                if rec.menu:
                    findings, match = unrestricted(rec)
                    outcomes[findings["rank_five"], findings["full_compatible_spaces"]] += 1
                    audit.update({k: v for k, v in findings.items() if k != "rank_five"})
                    if match:
                        overlap = {"rival_domain": "unrestricted mixed law", "certificate": witness(*match)}
                        break
            stats["unrestricted_from_positive_source"] = {"checked": sum(outcomes.values()),
                                                          "by_forced_rank_K5_and_compatible_spaces": [(*k, v) for k, v in sorted(outcomes.items())],
                                                          **audit}
        stages.append(stats)
        print(f"width {width}, {len(present)} types, {len(critical)} with at least two shrinks", file=sys.stderr, flush=True)
        if overlap:
            break
    return {"prediction_commit": "00f535dc3", "stages": stages, "first_D3_menu_witness": lower,
            "first_D3_self_witness": lower_self, "earliest_full_empty_menu_control": empty_control,
            "first_live_full_collision": overlap, "unrestricted_rivals_checked": check_rivals,
            "width26_lower_control": advertised_lower_control()}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--width", type=int, default=30)
    parser.add_argument("--within-family-only", action="store_true")
    args = parser.parse_args()
    if not 12 <= args.width <= 34 or args.width % 2:
        parser.error("maximum width must be even and between 12 and 34")
    with TemporaryDirectory(prefix="binary-third-census-") as directory:
        engine = Path(directory) / "measure"
        subprocess.run(["c++", "-std=c++20", "-O2", "-D_GLIBCXX_ASSERTIONS", "-pthread", Path(__file__).with_suffix(".cpp"),
                        "-o", engine], check=True)
        result = run(args.width, engine, not args.within_family_only)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
