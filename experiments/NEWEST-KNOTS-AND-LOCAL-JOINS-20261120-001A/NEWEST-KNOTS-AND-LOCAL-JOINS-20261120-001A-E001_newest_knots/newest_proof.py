"""Read the target from signed pair fractions and test all proposed latest families."""

from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import comb, isqrt
from pathlib import Path
import gzip
import json


TICKET = "NEWEST-KNOTS-AND-LOCAL-JOINS-20261120-001A"
ROOT = Path(__file__).resolve().parents[3]
OUT = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_newest_knots"


def read_table(reading):
    rates = json.loads((OUT / f"target_{reading}.json").read_text())
    n = (1 + isqrt(1 + 8 * len(rates))) // 2
    assert comb(n, 2) == len(rates)
    c = [[Fraction(int(i == j)) for i in range(n)] for j in range(n)]
    for (i, j), rate in zip(combinations(range(n), 2), rates, strict=True):
        c[i][j] = c[j][i] = 1 - 2 * Fraction(rate)
    return c


def twins(c, i, j, carrier):
    return all(c[i][k] == c[j][k] for k in carrier - {i, j})


def local_options(c, carrier):
    options = set()
    for i in carrier:
        m = min(c[i][j] for j in carrier - {i})
        h = frozenset({i} | {j for j in carrier if c[i][j] == m})
        f = frozenset(j for j in h if twins(c, i, j, carrier))
        old = h - f
        if m >= 0 or len(h) < 3 or not old:
            continue
        if any(twins(c, x, y, carrier) for x, y in combinations(old, 2)):
            continue
        if len(old) <= 2 and any(len(old) * (2 ** len(f) - 1) * c[i][z] != -sum(c[u][z] for u in old)
                                 for z in carrier - f):
            continue
        options.add((h, f, old))
    return sorted(options, key=lambda option: tuple(sorted(option[0])))


def ordinary_groups(parent_sets):
    names = list(range(len(parent_sets)))
    candidates = []
    for size in range(2, len(names) + 1):
        for group in combinations(names, size):
            if not all(parent_sets[i] & parent_sets[j] for i, j in combinations(group, 2)):
                continue
            if size == 2 or not set.intersection(*(parent_sets[i] for i in group)):
                candidates.append(frozenset(group))
    return [tuple(sorted(g)) for g in candidates if not any(g < other for other in candidates)]


def partition_old(c, carrier, selections):
    loose = set().union(*(inputs for _, _, inputs in selections))
    classes = {frozenset({i} | {j for j in loose - {i} if c[i][j] < 0 and twins(c, i, j, carrier)})
               for i in loose}
    if sum(map(len, classes)) != len(loose):
        return None
    return sorted(classes, key=min)


def possible_parents(c, carrier, selections, classes):
    loose = set.union(*(set(e) for e in classes))
    options = []
    for siblings in classes:
        x = min(siblings)
        m = min(c[x][z] for z in carrier - {x})
        if m >= 0 or any(c[x][z] != m for z in siblings - {x}):
            return None
        allowed = {z for z in carrier - loose if c[x][z] == m}
        for h, f, ins in selections:
            if ins & siblings:
                if len(ins & siblings) > 1:
                    return None
                allowed.difference_update(h)
        if len(allowed) + len(siblings) < 3:
            return None
        options.append((siblings, frozenset(allowed)))
    return options


def price_both(selections, classes):
    parents = [{i for i, siblings in enumerate(classes) if siblings & ins} for _, _, ins in selections]
    if any(len(p) != len(ins) for p, (_, _, ins) in zip(parents, selections, strict=True)):
        return None
    groups = ordinary_groups(parents)
    demand = Counter(i for group in groups for i in group)
    births = groups.copy()
    for i, (_, f, ins) in enumerate(selections):
        if len(f) != max(3-len(ins), 1, demand[i]):
            return None
        births.extend([(i,)] * (len(f)-demand[i]))
    later = ordinary_groups([set(group) for group in births])
    next_demand = Counter(i for group in later for i in group)
    return [(group, max(3-len(group), 1, next_demand[i])) for i, group in enumerate(births)]


def inspect(c, options):
    n = len(c)
    carrier = set(range(n))
    funnel = Counter()
    survivors = []
    for size in range(1, len(options) + 1):
        for subset in combinations(range(len(options)), size):
            selected = [options[i] for i in subset]
            funnel["nonempty"] += 1
            if sum(len(h) for h, _, _ in selected) != len(set.union(*(set(h) for h, _, _ in selected))):
                continue
            funnel["disjoint"] += 1
            old = carrier - set.union(*(set(f) for _, f, _ in selected))
            classes = partition_old(c, old, selected)
            if not classes:
                continue
            opts = possible_parents(c, old, selected, classes)
            if not opts:
                continue
            funnel["possible_prior_companions"] += 1
            births = price_both(selected, classes)
            if births is None:
                continue
            funnel["formation_prices"] += 1
            survivors.append({"indices": subset, "prior_companion_options": [[sorted(s), sorted(a)] for s, a in opts],
                              "next_roster": [[[sorted(selected[i][0]) for i in group], q] for group, q in births]})
    return funnel, survivors


def equal_mass(c, names):
    assert len(names) in (2, 3)
    return (1 + sum(c[i][j] for i, j in combinations(names, 2))) / 2 ** (len(names) - 1)


def extrema(row):
    m = min(row.values())
    return -m, sorted(i for i, value in row.items() if value == m)


def exclude_singletons(c, options, survivors):
    n = set(range(len(c)))
    remaining = []
    details = []
    for branch in survivors:
        if len(branch["indices"]) != 1:
            remaining.append(branch)
            continue
        _, f, inputs = options[branch["indices"][0]]
        old = n - f
        if len(inputs) > 1:
            x = 5
            assert x in inputs
            m, companions = extrema({i: c[x][i] for i in old - {x}})
            lower = equal_mass(c, companions)
            assert lower > m
            details.append({"indices": branch["indices"], "preceding_loose": x,
                            "entire_companion_constant_mass": str(m), "possible_companions": companions,
                            "minimum_constant_mass": str(lower)})
            continue
        x, = inputs
        count, companions = extrema({i: c[x][i] for i in old - {x}})
        assert len(companions) == 4
        proper_masses = {str(equal_mass(c, subset)) for size in (2, 3)
                         for subset in combinations(companions, size)}
        assert all(Fraction(prob) > count for prob in proper_masses)
        reduced = old - {x}
        earlier_x = 3
        earlier_mass, earlier_companions = extrema({i: c[earlier_x][i] for i in reduced - {earlier_x}})
        assert earlier_x in companions and set(earlier_companions) <= set(companions) - {earlier_x}
        freed = 5
        assert freed in companions
        corrected = {i: (c[freed][i] - c[x][i]) / (1 + count) for i in reduced - {freed}}
        small_mass, possible = extrema(corrected)
        constant = equal_mass(c, possible)
        lower = constant / (1 + count)
        assert lower > small_mass
        details.append({"indices": branch["indices"], "preceding_loose": x,
                        "entire_companion_constant_mass": str(count), "forced_companions": companions,
                        "proper_two_three_masses": sorted(proper_masses),
                        "earlier_reached_obstruction": {"previous_loose": earlier_x,
                            "constant_mass": str(earlier_mass), "all_minimizers": earlier_companions},
                        "uniform_source_erasure": {"freed": freed, "possible_companions": possible,
                            "inferred_constant_mass": str(small_mass), "pre_erasure_constant": str(constant),
                            "post_erasure_lower_bound": str(lower)}})
    assert len(remaining) == 1
    return details, remaining[0]


def bit_columns(names):
    all_words = (1 << (1 << len(names))) - 1
    ones = {}
    for i, x in enumerate(sorted(names)):
        width = 1 << i
        repeat = all_words // ((1 << (2 * width)) - 1)
        ones[x] = (((1 << width) - 1) << width) * repeat
    return all_words, ones


def common(on, selectors):
    for s in selectors:
        on &= s
    return on


def verify_realization(c, selected, family):
    source = [set(s) | set(a) for s, a in family["prior_companion_options"]]
    old = set().union(*source)
    old_loose = {x for x in old if sum(x in h for h in source) == 1}
    assert old_loose == set().union(*(ins for _, _, ins in selected))
    assert all(len(h & old_loose) >= 2 for h in source)
    parents = [{i for i, h in enumerate(source) if h & inputs} for _, _, inputs in selected]
    source_witnesses = [{j for j, other in enumerate(source) if j != i and other & h}
                        for i, h in enumerate(source)]
    proposed = ordinary_groups(source_witnesses)
    for i, h in enumerate(source):
        cost = sum(i in group for group in proposed)
        assert cost <= len(old_loose & h)
        proposed.extend([(i,)] * (len(old_loose & h) - cost))
    assert sorted(proposed) == sorted(tuple(sorted(q)) for q in parents)
    all_words, pos = bit_columns(old)
    neg = {x: all_words ^ mask for x, mask in pos.items()}
    words = all_words
    for h in source:
        words &= ~(common(all_words, (pos[x] for x in h)) | common(all_words, (neg[x] for x in h)))
    n = words.bit_count()
    sign = {x: (words & pos[x], words & neg[x], 1) for x in old}
    sibling_pairs = {}
    for _, fresh, inputs in selected:
        with_ones = common(words, (pos[x] for x in inputs))
        with_zeroes = common(words, (neg[x] for x in inputs))
        denominator = 2 ** len(fresh) - 1
        for x in fresh:
            sign[x] = (with_zeroes, with_ones, denominator)
        for pair in combinations(sorted(fresh), 2):
            sibling_pairs[pair] = Fraction(-(with_ones | with_zeroes).bit_count(), n * denominator)
    for a, b in combinations(range(len(c)), 2):
        if (a, b) in sibling_pairs:
            value = sibling_pairs[a, b]
        else:
            ap, am, da = sign[a]
            bp, bm, db = sign[b]
            value = Fraction((ap & bp).bit_count() + (am & bm).bit_count()
                             - (ap & bm).bit_count() - (am & bp).bit_count(), n * da * db)
        assert c[a][b] == value
    return {"source": [sorted(h) for h in source], "uniform_source_words": n,
            "ordinary_first_parent_sets": [sorted(q) for q in parents],
            "inherited_rates_reconstructed": comb(len(c), 2)}


def small_source_checks():
    prefix = "READS-HOLDERS-SOURCES-20261120-001B"
    later = "THREE-READERS-AND-GROWTH-20261120-001B"
    with gzip.open(ROOT / "artifacts" / prefix / f"{prefix}-E001_irredundant" / "census_cases.json.gz", "rt") as f:
        census = json.load(f)
    with gzip.open(ROOT / "artifacts" / later / f"{later}-E001_state_recovery" / "census_cases.json.gz", "rt") as f:
        census["10"] = json.load(f)
    audit = Counter()
    for width, table in census.items():
        names = set(range(int(width)))
        all_words, pos = bit_columns(names)
        disagree = {(i, j): pos[i] ^ pos[j] for i in names for j in names}
        for case in table["nae"]:
            words = int(case["state_words_hex"], 16)
            total = words.bit_count()
            c = [[total - 2 * (words & disagree[i, j]).bit_count() for j in sorted(names)] for i in sorted(names)]
            for pres in case["presentations"]:
                holders = list(map(set, pres["supports"]))
                counts = Counter(x for h in holders for x in h)
                loose = {x for x, count in counts.items() if count == 1}
                audit["source_presentations"] += 1
                for i, j in combinations(sorted(loose), 2):
                    same = any({i, j} <= h for h in holders)
                    equal_rows = twins(c, i, j, names)
                    assert (equal_rows and c[i][j] < 0) == same
                    if equal_rows and not same:
                        assert c[i][j] > 0
                        audit["different_holder_twins"] += 1
                    audit["same_holder_pairs" if same else "different_holder_pairs"] += 1
                forbidden = [common(all_words, (pos[x] for x in h)) | common(all_words, (all_words ^ pos[x] for x in h))
                             for h in holders]
                for i, h in enumerate(holders):
                    if len(h & loose) != 1:
                        continue
                    x, = h & loose
                    env = common(all_words, (~bad for j, bad in enumerate(forbidden) if j != i))
                    nenv = env.bit_count()
                    for y in h - {x}:
                        for z in names - {x, y}:
                            numerator = nenv - 2 * (env & disagree[y, z]).bit_count()
                            assert numerator * (total - c[x][y]) == nenv * (c[y][z] - c[x][z])
                            audit["erased_holder_pair_identities"] += 1
    return dict(audit)


def main():
    c = read_table("inherited")
    options = local_options(c, set(range(len(c))))
    funnel, survivors = inspect(c, options)
    ruled_out, last = exclude_singletons(c, options, survivors)
    selected = [options[i] for i in last["indices"]]
    witness = verify_realization(c, selected, last)
    record = {"width": len(c), "options": [[sorted(z) for z in opt] for opt in options],
              "funnel": dict(funnel), "after_funding": survivors, "older_exclusions": ruled_out,
              "sole_roster": last, "realization": witness, "small_source_checks": small_source_checks()}
    (OUT / "newest_proof.json").write_text(json.dumps(record, indent=2) + "\n")
    print(dict(funnel), [r["indices"] for r in survivors])


if __name__ == "__main__":
    main()
