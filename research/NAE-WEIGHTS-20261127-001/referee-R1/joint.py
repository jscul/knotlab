"""Recount ring moments and test distant sign products under equal weighting."""

import argparse
import json
import resource
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import combinations
from math import prod
from pathlib import Path
from time import perf_counter


HERE = Path(__file__).resolve().parent


def coefficient(places):
    return Fraction(-1, 2 ** (places - 1) - 1)


def literal(knots, visible, observed, prefix=None, conditioned=None):
    """Visit full words independently of the sign expansion, retaining local reads."""
    names = sorted(set().union(*knots))
    bit = {name: 1 << i for i, name in enumerate(names)}
    masks = [sum(bit[name] for name in knot) for knot in knots]
    visible_bits = [bit[name] for name in visible]
    observed_mask = sum(bit[name] for name in observed)
    counts = Counter()
    local = [defaultdict(int) for _ in knots]
    size = 1 << len(names)
    for index in range(size if prefix is None else prefix):
        # An odd multiplier permutes the words and spreads pilot prefixes
        # across both values of the distinctions with large bit positions.
        word = (index * 2654435761) & (size - 1)
        if any((word & mask) in (0, mask) for mask in masks):
            continue
        visible_word = sum(1 << i for i, b in enumerate(visible_bits) if word & b)
        counts[visible_word] += 1
        sign_bit = 1 << ((word & observed_mask).bit_count() % 2)
        for k, (mask, readings) in enumerate(zip(masks, local)):
            fixed = word & mask
            readings[fixed] |= sign_bit
            if conditioned is not None:
                conditioned[k][fixed][visible_word] += 1
    return counts, [
        {status: list(readings.values()).count(flag)
         for flag, status in ((1, "only plus"), (2, "only minus"), (3, "both signs"))}
        for readings in local
    ]


def moment(counts, visible, observed):
    mask = sum(1 << visible.index(name) for name in observed)
    plus = sum(n for word, n in counts.items() if (word & mask).bit_count() % 2 == 0)
    minus = sum(counts.values()) - plus
    return {"plus": plus, "minus": minus, "mean": str(Fraction(plus - minus, plus + minus))}


def local_terms(knots, observed):
    """List all surviving terms, allowing every even subset at each knot.

    A shared distinction must be selected by an odd number of its holders
    when observed and by an even number otherwise. A loose distinction fixes
    its only holder's selection. Each nonempty even subset has the same
    coefficient at a not-all-equal knot of fixed arity.
    """
    holders = defaultdict(list)
    for index, knot in enumerate(knots):
        for name in knot:
            holders[name].append(index)
    assert all(len(indices) in (1, 2) for indices in holders.values())
    shared = [(name, *indices) for name, indices in holders.items() if len(indices) == 2]
    forced = Counter(indices[0] for name, indices in holders.items()
                     if name in observed and len(indices) == 1)
    factors = [coefficient(len(knot)) for knot in knots]
    terms = []
    for choice in range(1 << len(shared)):
        degrees = [forced[k] for k in range(len(knots))]
        for j, (name, first, second) in enumerate(shared):
            selected = (choice >> j) & 1
            degrees[first] += selected
            degrees[second] += selected ^ (name in observed)
        if any(degree % 2 for degree in degrees):
            continue
        weight = prod((factor for factor, degree in zip(factors, degrees) if degree), start=Fraction(1))
        terms.append({"places used at each knot": degrees, "weight": str(weight)})
    return terms


def total_weight(terms):
    return sum((Fraction(term["weight"]) for term in terms), start=Fraction())


def simple_routes(knots, first, last):
    """Routes may visit a distinction or its holder at most once."""
    result = []

    def visit(current, seen, route):
        if current == last:
            result.append(route)
            return
        for i, knot in enumerate(knots):
            if i in route or current not in knot:
                continue
            for following in knot:
                if following not in seen:
                    visit(following, seen | {following}, route + [i])

    visit(first, {first}, [])
    return [{"knot indices": route,
             "weight": str(prod(coefficient(len(knots[i])) for i in route))}
            for route in result]


def add_place(knots, position, name):
    return [(*knot, name) if i == position else knot for i, knot in enumerate(knots)]


def cases():
    four = [(0, 1, 10), (0, 2, 11), (1, 3, 12), (2, 3, 13)]
    three = [(0, 1, 10), (0, 2, 11), (1, 2, 12)]
    yield "recorded ring of three", three, [0, 1, 2], [0, 1], "ring"
    yield "edited ring of three from the earlier signed count", add_place(three, 2, 20), [0, 1, 2], [0, 1], "ring"
    yield "recorded ring of four", four, [0, 1, 2, 3], [0, 1], "ring"
    for position, label in [
        (2, "edited knot in the current check"),
        (3, "disjoint edited knot in the earlier signed count"),
        (0, "edit to the knot holding the measured pair"),
    ]:
        yield label, add_place(four, position, 20), [0, 1, 2, 3], [0, 1], "ring"

    for size in (5, 6):
        ring = [(i, (i + 1) % size, size + i) for i in range(size)]
        for edited in (False, True):
            knots = add_place(ring, size // 2, 2 * size) if edited else ring
            label = f"ring of {size}" + (" with disjoint edit" if edited else "")
            yield label, knots, list(range(size)), [0, 1], "ring"

    # Each selected distinction is held in its own three-place knot.
    for width in (4, 5, 6):
        middle = tuple(range(width))
        relays = [(i, i + width, i + 2 * width) for i in range(width)]
        visible = list(range(width, 2 * width))
        yield f"{width}-place knot with one relay per place", [middle, *relays], visible, visible[:4], "relays"

    ring = [(0, 1, 4, 5), (1, 2, 6), (2, 3, 7), (3, 0, 8)]
    ends = [(4, 9, 10), (5, 11, 12)]
    for edited in (False, True):
        knots = [*(add_place(ring, 2, 13) if edited else ring), *ends]
        label = "ring meeting the unique route" + (" with off-route edit" if edited else "")
        yield label, knots, [9, 11], [9, 11], "route"

    three_routes = [tuple(names) for names in ("zac", "zbf", "abw", "cdu", "dem", "efv")]
    yield "three routes with a disjoint ring contribution", three_routes, ["u", "v"], ["u", "v"], "route"
    longer = [*three_routes, tuple("uij"), tuple("vkl")]
    yield "three routes with both ends extended", longer, ["i", "k"], ["i", "k"], "route"


def check(label, knots, visible, observed, kind, pilot_only):
    names = set().union(*knots)
    word_count = 1 << len(names)
    # Sample whole words spread across the enumeration before the full count.
    pilot_words = min(2048, word_count // 8)
    before = perf_counter()
    sample_counts, _ = literal(knots, visible, observed, pilot_words)
    pilot_seconds = perf_counter() - before
    times = {"timed words": pilot_words, "total words": word_count,
             "timed seconds": pilot_seconds, "projected literal seconds": pilot_seconds * word_count / pilot_words}
    before = perf_counter()
    local_terms(knots, [])
    local_terms(knots, observed)
    terms_seconds = perf_counter() - before
    before = perf_counter()
    moment(sample_counts, visible, observed)
    if kind == "ring":
        local_terms(knots, observed)
    if kind in ("ring", "route"):
        simple_routes(knots, *observed)
    read_seconds = perf_counter() - before
    number_of_reads = 1 if kind == "route" else 1 << len(visible)
    times["projected seconds for expansions and reads"] = terms_seconds + number_of_reads * read_seconds
    if pilot_only:
        return times
    before = perf_counter()
    counts, local = literal(knots, visible, observed)
    times["actual literal seconds"] = perf_counter() - before
    positive = sum(counts.values())
    measured = moment(counts, visible, observed)
    normal_terms = local_terms(knots, [])
    normal = total_weight(normal_terms)
    terms = local_terms(knots, observed)
    predicted = total_weight(terms) / normal
    assert predicted == Fraction(measured["mean"]), label
    assert word_count * prod(1 - Fraction(2, 2 ** len(knot)) for knot in knots) * normal == positive, label
    row = {"knots": knots, "visible distinctions in bit order": visible,
           "observed sign product": observed, "allowed states": positive,
           "visible words attained": len(counts), "sign counts": measured,
           "visible word counts in binary integer order": [counts[i] for i in range(1 << len(visible))],
           "signs possible at fixed readings of each knot": local,
           "terms for the count": normal_terms, "terms for the sign product": terms, "time": times}
    return row, counts, normal


def ring_tests(knots, visible, counts, row, normal):
    # All products on the shared distinctions, including the odd and empty ones.
    matched, pairs = 0, []
    for width in range(len(visible) + 1):
        for observed in combinations(visible, width):
            value = moment(counts, visible, observed)
            exact = Fraction(value["mean"])
            assert total_weight(local_terms(knots, observed)) / normal == exact
            matched += 1
            if width == 2:
                routes = simple_routes(knots, *observed)
                assert len(routes) == 2
                assert total_weight(routes) / normal == exact
                pairs.append({"pair": observed, **value})
    row.update({"all shared sign products matched": matched,
                "two-route pair counts": pairs,
                "parity of all shared distinctions": moment(counts, visible, visible)})


def relay_tests(knots, visible, counts, row):
    # Summing a three-place relay conditioned on its arriving sign sends its
    # mean to minus one third of that sign. The middle knot contributes its
    # full, even-order coefficient exactly once, regardless of the order.
    core = coefficient(len(knots[0]))
    matched = 0
    for width in range(len(visible) + 1):
        for observed in combinations(visible, width):
            exact = Fraction(moment(counts, visible, observed)["mean"])
            expected = 1 if width == 0 else 0 if width % 2 else core * coefficient(3) ** width
            assert expected == exact
            matched += 1
    subset = row["observed sign product"]
    pairing = [moment(counts, visible, subset[:2]), moment(counts, visible, subset[2:])]
    row.update({"all visible sign products matched": matched, "two disjoint pair readings": pairing,
                "product of pair means": str(prod(Fraction(v["mean"]) for v in pairing)),
                "middle knot coefficient": str(core)})
    assert len(counts) == 2 ** len(visible)


def quartet_cases():
    # Each distinction joins two of the specified groups. Its name is its
    # position in the list of joins; the two corresponding knots hold it.
    groups = list(combinations(range(5), 2))
    joins = [(i, j) for i, j in combinations(range(10), 2) if not set(groups[i]).intersection(groups[j])]
    ten = [tuple(i for i, pair in enumerate(joins) if k in pair) for k in range(10)]
    yield "ten three-place knots made from disjoint pairs of five names", ten, [(0, 1, 3, 7), (0, 1, 3, 12)]

    joins = [(i, 7 + (i + offset) % 7) for i in range(7) for offset in (0, 1, 3)]
    fourteen = [tuple(i for i, pair in enumerate(joins) if k in pair) for k in range(14)]
    yield "fourteen three-place knots with joins at offsets zero, one and three", fourteen, [(0, 6, 3, 9), (0, 6, 3, 13)]

    joins = [(i, 4 + j) for i in range(4) for j in range(4)]
    eight = [tuple(i for i, pair in enumerate(joins) if k in pair) for k in range(8)]
    yield "two groups of four knots with one join for each pair across the groups", eight, [(0, 1, 6, 7), (0, 1, 6, 10)]


def projected_counts(counts, positions):
    projected = [0] * 2 ** len(positions)
    for word, number in counts.items():
        visible_word = sum(((word >> j) & 1) << k for k, j in enumerate(positions))
        projected[visible_word] += number
    return projected


def conditional_comparison(knots, tables, proper):
    names = sorted(set().union(*knots))
    rows = []
    for i, knot in enumerate(knots):
        positions = [names.index(name) for name in knot]
        first, second = (table[i] for table in tables)
        assert first.keys() == second.keys()
        readings = []
        for fixed in sorted(first):
            left, right = first[fixed], second[fixed]
            size = sum(left.values())
            assert size == sum(right.values())
            plus_a = sum(n for w, n in left.items() if w.bit_count() % 2 == 0)
            plus_b = sum(n for w, n in right.items() if w.bit_count() % 2 == 0)
            assert 0 < plus_a < size and 0 < plus_b < size
            same_proper = all(projected_counts(left, p) == projected_counts(right, p) for p in proper)
            word = "".join(str((fixed >> j) & 1) for j in positions)
            readings.append([word, size, plus_a, plus_b, same_proper])
        rows.append(readings)
    return rows


def check_quartets(knots, quartets, pilot):
    word_count = 1 << len(set().union(*knots))
    sample_words = min(2048, word_count // 8)
    subprojections = [positions for width in (1, 2, 3) for positions in combinations(range(4), width)]
    before = perf_counter()
    samples = [literal(knots, quartet, quartet, sample_words,
                       [defaultdict(Counter) for _ in knots])[0] for quartet in quartets]
    middle = perf_counter()
    for counts in samples:
        for positions in subprojections:
            projected_counts(counts, positions)
    timing = {"timed words per quartet": sample_words, "total words per quartet": word_count,
              "projected literal seconds": (middle - before) * word_count / sample_words,
              "projected seconds for expansions and reads": perf_counter() - middle}
    if pilot:
        return timing

    before = perf_counter()
    readings = []
    tables = []
    for quartet in quartets:
        table = [defaultdict(Counter) for _ in knots]
        counts, local = literal(knots, quartet, quartet, conditioned=table)
        tables.append(table)
        assert len(counts) == 16
        pair_sums = []
        for pair in combinations(range(4), 2):
            zero_zero, one_zero, zero_one, one_one = projected_counts(counts, pair)
            pair_sums.append(zero_zero + one_one - one_zero - zero_one)
        readings.append({
            "ordered distinctions": quartet, "allowed states": sum(counts.values()),
            "largest number of these distinctions held by a single knot":
            max(len(set(knot).intersection(quartet)) for knot in knots),
            "complete joint counts in binary integer order": [counts[word] for word in range(16)],
            "proper marginal counts": [projected_counts(counts, pos) for pos in subprojections],
            "pair sign sums": pair_sums,
            "four-sign counts": moment(counts, quartet, quartet), "signs at fixed readings of each knot": local,
        })
    first, second = readings
    assert first["proper marginal counts"] == second["proper marginal counts"]
    assert first["four-sign counts"] != second["four-sign counts"]
    assert all(local["only plus"] == local["only minus"] == 0
               for reading in readings for local in reading["signs at fixed readings of each knot"])
    conditional = conditional_comparison(knots, tables, subprojections)
    timing["actual seconds"] = perf_counter() - before
    return {"knots": knots, "proper marginal positions in listed order": subprojections,
            "all 14 nonempty proper marginal tables identical": True,
            "conditional row fields": ["fixed bits in the listed knot's order", "complete states",
                                       "first quartet even", "second quartet even", "all proper marginals coincide"],
            "conditional rows for each knot in listed order": conditional,
            "readings": readings, "time": timing}


def run(pilot):
    out = {}
    for label, knots, visible, observed, kind in cases():
        checked = check(label, knots, visible, observed, kind, pilot)
        if pilot:
            out[label] = checked
            continue
        row, counts, normal = checked
        if kind == "ring":
            ring_tests(knots, visible, counts, row, normal)
        elif kind == "relays":
            relay_tests(knots, visible, counts, row)
        else:
            routes = simple_routes(knots, *observed)
            row["simple routes between the pair"] = routes
            row["simple route sum divided by the complete count term"] = str(total_weight(routes) / normal)
            assert Fraction(row["sign counts"]["mean"]) != total_weight(routes) / normal
        out[label] = row
    quartets = {label: check_quartets(knots, choices, pilot) for label, knots, choices in quartet_cases()}
    if pilot:
        timings = [*out.values(), *quartets.values()]
        return {"pilot rows": out, "quartet pilots": quartets, "projected seconds for all literal counts":
                sum(row["projected literal seconds"] for row in timings),
                "projected seconds for expansions and reads":
                sum(row["projected seconds for expansions and reads"] for row in timings)}

    recorded = json.loads((HERE.parent / "weights.json").read_text())
    for key, label in (("ring of four", "recorded ring of four"),
                       ("ring of four, Bob's edit", "edited knot in the current check"),
                       ("ring of three", "recorded ring of three")):
        row = out[label]
        assert row["allowed states"] == recorded["W1r"][key]["states"]
        value = row["sign counts"]["mean"]
        assert value == recorded["W1r"][key]["exact mean of signs of 0 and 1"] == recorded["W1r"][key]["route formula"]
    four = out["recorded ring of four"]
    assert four["parity of all shared distinctions"]["plus"] == recorded["W3"]["even parity of the four shared distinctions"]
    assert four["allowed states"] == recorded["W3"]["states"]
    earlier = HERE.parents[1] / "SIGNED-COUNT-20261126-001" / "signed_out.jsonl"
    signed_counts = {row["case"]: row for row in map(json.loads, earlier.read_text().splitlines())}
    for key, setting, label in (
        ("ring of four", "no edit", "recorded ring of four"),
        ("ring of four", "Bob's edit", "disjoint edited knot in the earlier signed count"),
        ("ring of three", "no edit", "recorded ring of three"),
        ("ring of three", "Bob's edit", "edited ring of three from the earlier signed count"),
    ):
        archived = signed_counts[key][setting]
        assert archived["count"] == out[label]["allowed states"]
        assert archived["Alice's statistic"] == out[label]["sign counts"]["mean"]
    return {"weighting": "one count for each complete allowed state",
            "local expansion": "Choose an even subset at each knot. Its coefficient is one for the empty "
            "subset and -1/(2^(a-1)-1) for every nonempty even subset of an a-place knot. A term survives "
            "when the selections have odd total occurrence exactly at the observed distinctions. Divide "
            "the sum by the corresponding sum with no observed distinctions.",
            "check scope": "The three archived ring means and the parity count; targeted larger rings, "
            "many-place knots with relays and two kinds of starts with rings. No census or growth run.",
            "archive values matched": {"ring means": 3, "ring parity counts": 1,
                                       "ring means in the earlier signed count": 4},
            "quartet selection": "Exploratory choice. Four-distinction readings were grouped by their six pair "
            "means up to ordering, and compared by their four-sign means. The cases here are selected witnesses, "
            "with the order fixed in the code before their direct recount. They supply no frequency weighting.",
            "quartets with identical proper marginal tables": quartets,
            "memory cap bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
            "peak resident KiB": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss, "cases": out}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="time small prefixes of the full word counts")
    args = parser.parse_args()
    start = perf_counter()
    result = run(args.pilot)
    if args.pilot:
        print(json.dumps(result, indent=2))
    else:
        result["elapsed seconds including pilots and expansions"] = perf_counter() - start
        (HERE / "joint.json").write_text(json.dumps(result, indent=2) + "\n")
        print(f"{len(result['cases'])} ring and relay cases and three quartet comparisons checked "
              f"in {perf_counter() - start:.3f} seconds")
