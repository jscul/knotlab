"""Audit shortest six-bit equations on the repeated six-site components."""

from collections import Counter, defaultdict
from dataclasses import dataclass
from itertools import combinations, product
import json
from pathlib import Path


SIDES = ("twb", "pqc")
SITES = "".join(SIDES)
INTERNAL = tuple(a + b for a, b in product(*SIDES) if a + b != "bc")
PORT_SITE = {
    "t.in": "t", "w.free": "w", "b.y": "b", "b.free": "b",
    "p.free": "p", "q.r": "q", "c.r": "c", "c.free": "c",
}
SEED_PROXY = "outside_seed"
NAMES = (*INTERNAL, *PORT_SITE, SEED_PROXY)
INDEX = {bit: i for i, bit in enumerate(NAMES)}
HOLDERS = {**{bit: tuple(bit) for bit in INTERNAL},
           **{bit: (site,) for bit, site in PORT_SITE.items()}}
MEETINGS = {frozenset(edge) for edge in INTERNAL}
K6_LOCAL = frozenset(
    (INDEX[a], INDEX[b]) for a, b in combinations(HOLDERS, 2)
    if any(u == v or frozenset((u, v)) in MEETINGS for u, v in product(HOLDERS[a], HOLDERS[b]))
)


def mask(names):
    return sum(1 << INDEX[name] for name in names)


def named(word):
    return tuple(name for i, name in enumerate(NAMES) if word >> i & 1)


STARS = {site: mask(bit for bit, holders in HOLDERS.items() if site in holders) for site in SITES}
TRANSLATIONS = [((), 0)]
for site, star in STARS.items():
    TRANSLATIONS += [((*sites, site), word ^ star) for sites, word in TRANSLATIONS]
assert len(TRANSLATIONS) == len({word for _, word in TRANSLATIONS}) == 64
assert all(star.bit_count() == 4 for star in STARS.values())


@dataclass(frozen=True)
class Candidate:
    word: int
    # Bits of each weight-six translate in observation order.
    ties: tuple[tuple[tuple[str, ...], int, tuple[int, ...]], ...]


def candidates():
    distributions = {5: Counter(), 6: Counter()}
    pool = []
    for bits in combinations(NAMES, 6):
        word = mask(bits)
        window = tuple((sites, word ^ translation) for sites, translation in TRANSLATIONS)
        minimum = min(translated.bit_count() for _, translated in window)
        distributions[6 - (SEED_PROXY in bits)][minimum] += 1
        if minimum == 6:
            pool.append(Candidate(word, tuple(
                (sites, translated, tuple(i for i in range(len(NAMES)) if translated >> i & 1))
                for sites, translated in window if translated.bit_count() == 6
            )))
    return tuple(pool), {k: dict(sorted(v.items())) for k, v in distributions.items()}


class Exterior:
    def __init__(self, seed_slots, groups):
        seed = (*seed_slots, SEED_PROXY)
        self.seed_mask = mask(seed)
        self.seed_indices = {INDEX[bit] for bit in seed}
        self.groups = tuple(mask(group) for group in groups if len(group) > 2)
        self.compatible = K6_LOCAL | {
            tuple(sorted((INDEX[a], INDEX[b]))) for group in groups for a, b in combinations(group, 2)
        }
        self.description = {"seed_ports_in_component": seed_slots, "outside_holder_groups": groups}

    def failure(self, word, indices):
        if (word & self.seed_mask).bit_count() > 1:
            return "seed_overlap", None
        if any((word & group).bit_count() > 2 for group in self.groups):
            return "outside_holder_overlap", None
        seed_free = (i for i in indices if i not in self.seed_indices)
        for a, b in combinations(seed_free, 2):
            if (a, b) not in self.compatible:
                return "pair_exceeds_six", (NAMES[a], NAMES[b])
        return None


def grade(pool, exterior):
    stats = Counter()
    counterexample = None
    first_disqualified_tie = None
    for item in pool:
        _, word, indices = item.ties[0]
        assert word == item.word
        first = exterior.failure(word, indices)
        if first is not None:
            stats["initial_" + first[0]] += 1
            continue
        stats["initial_pass"] += 1
        conflicts = {}
        for sites, alternate, names in item.ties:
            failure = exterior.failure(alternate, names)
            if failure is not None:
                conflicts.setdefault(failure[0], {
                    "xor_sites": sites, "translated_word": named(alternate), "pair_if_any": failure[1],
                })
        for kind in conflicts:
            stats["tied_" + kind] += 1
        if conflicts and first_disqualified_tie is None:
            first_disqualified_tie = {"word": named(word), "first_failure_by_kind": conflicts}
        if not conflicts:
            stats["final_survivors"] += 1
            if counterexample is None:
                counterexample = named(word)
    return stats, first_disqualified_tie, counterexample


def partitions(slots):
    if not slots:
        yield ()
        return
    first, *rest = slots
    for count in range(len(rest) + 1):
        for others in combinations(rest, count):
            group = (first, *others)
            if len({PORT_SITE[bit] for bit in group}) == len(group):
                remaining = tuple(bit for bit in rest if bit not in others)
                for following in partitions(remaining):
                    # Single slots need no common-holder fact in the test.
                    yield (group, *following) if len(group) > 1 else following


def all_exteriors(seed_slots):
    sides = tuple(tuple(bit for bit, site in PORT_SITE.items() if site in side and bit not in seed_slots)
                  for side in SIDES)
    for left, right in product(*(partitions(slots) for slots in sides)):
        yield Exterior(seed_slots, (*left, *right))


STAT_NAMES = (
    "initial_seed_overlap", "initial_outside_holder_overlap", "initial_pair_exceeds_six",
    "initial_pass", "tied_seed_overlap", "tied_outside_holder_overlap", "tied_pair_exceeds_six",
    "final_survivors",
)


def report(stats):
    return {name: stats[name] for name in STAT_NAMES}


def grade_exteriors(pool, seed_slots):
    stats = Counter()
    exteriors = tuple(all_exteriors(seed_slots))
    assert len(exteriors) == len({entry.description["outside_holder_groups"] for entry in exteriors})
    if len(seed_slots) == 3:
        pool = tuple(item for item in pool if not item.word & mask((SEED_PROXY,)))
    for exterior in exteriors:
        grade_counts, _, survivor = grade(pool, exterior)
        assert survivor is None, (exterior.description, survivor)
        stats.update(grade_counts)
    return {"outside_models": len(exteriors), "locally_minimal_model_word_pairs": len(exteriors) * len(pool),
            **report(stats)}


def all_seed_placements():
    yield ()
    for side in SIDES:
        slots = tuple(bit for bit, site in PORT_SITE.items() if site in side)
        for count in range(1, 4):
            for group in combinations(slots, count):
                if len({PORT_SITE[bit] for bit in group}) == count:
                    yield group


def unrestricted_exterior_models(pool):
    totals = {n: Counter() for n in range(4)}
    for seed in all_seed_placements():
        subtotal = totals[len(seed)]
        subtotal["seed_placements"] += 1
        subtotal.update(grade_exteriors(pool, seed))
    return {n: dict(stats) for n, stats in totals.items()}


def literal_profiles():
    """Check the projected component labels against each archived history."""
    path = Path(__file__).with_name("families.json")
    cases = json.loads(path.read_text())["nonshrinking_intersecting_cycles"]
    checks = 0
    labeled_examples = []
    for row in cases:
        history = tuple(map(set, row["history"]))
        users = defaultdict(set)
        for site, support in enumerate(history):
            for bit in support:
                users[bit].add(site)
        for i in range(row["blocks"]):
            start = 1 + 8 * i
            at = dict(zip("tpqwbcry", range(start, start + 8), strict=True))
            component = {at[site] for site in SITES}
            assert all(len(history[site]) == 4 for site in component)
            assert len(history[at["r"]]) == len(history[at["y"]]) == 5
            projection = {}
            for a, b in combinations(SITES, 2):
                joint = history[at[a]] & history[at[b]]
                if frozenset((a, b)) in MEETINGS:
                    assert len(joint) == 1
                    projection[a + b] = next(iter(joint))
                else:
                    assert not joint
            for slot, site in PORT_SITE.items():
                outside_bits = [bit for bit in history[at[site]] if len(users[bit] & component) == 1]
                if len(outside_bits) == 1:
                    (projection[slot],) = outside_bits
                else:
                    assert len(outside_bits) == 2 and site in ("b", "c")
                    exterior = at["y" if site == "b" else "r"]
                    linked, = (bit for bit in outside_bits if exterior in users[bit])
                    projection[slot] = linked if slot.endswith((".y", ".r")) else next(
                        bit for bit in outside_bits if bit != linked
                    )
            assert len(set(projection.values())) == 16
            groups = defaultdict(set)
            for slot in PORT_SITE:
                for site in users[projection[slot]] - component:
                    assert len(history[site]) != 4
                    groups[site].add(slot)
            assert {frozenset(group) for group in groups.values() if len(group) > 1} == {
                frozenset(("q.r", "c.r"))
            }
            assert {slot for slot, bit in projection.items() if bit in history[0]} == (
                {"t.in"} if i == 0 else set()
            )
            checks += 1
            if row["blocks"] == 2:
                labeled_examples.append(projection)
    return {"archived_histories": len(cases), "components_projected": checks,
            "named_first_and_later_examples": labeled_examples}


def run():
    pool, distributions = candidates()
    n = sum(sum(by_weight.values()) for by_weight in distributions.values())
    raw = {}
    widened = {}
    for state, seed in (("first", ("t.in",)), ("later", ())):
        literal = Exterior(seed, (("q.r", "c.r"),))
        stats, failure, survivor = grade(pool, literal)
        assert survivor is None, survivor
        assert stats["initial_pass"] > 0
        raw[state] = {"outside": literal.description, **report(stats), "example_failing_at_tie": failure}
        widened[state] = grade_exteriors(pool, seed)

    # If the seed-free pair test is removed, the later control word continues
    # to satisfy local minimum weight and every modeled holder cap.
    without_pair_test = Exterior((), (("q.r", "c.r"),))
    without_pair_test.compatible = frozenset(combinations(range(len(NAMES)), 2))
    control = next(item for item in pool if named(item.word) == tuple(raw["later"]["example_failing_at_tie"]["word"]))
    assert all(without_pair_test.failure(word, indices) is None for _, word, indices in control.ties)
    return {
        "names": NAMES,
        "four_place_stars": {site: named(star) for site, star in STARS.items()},
        "six_subsets": n, "local_translations": len(TRANSLATIONS),
        "subsets_times_translations": n * len(TRANSLATIONS),
        "minimum_local_coset_weight_by_number_of_component_bits": distributions,
        "words_with_local_minimum_six": len(pool),
        "literal_source_projection_checks": literal_profiles(),
        "literal_projection_counts": raw,
        "all_simple_bipartite_outside_partitions": widened,
        "all_simple_bipartite_partitions_at_every_seed_placement": unrestricted_exterior_models(pool),
        "positive_control_when_seed_free_pair_test_is_removed": named(control.word),
        "counts_note": "Tied rejection counts can overlap across different translations of the same word.",
    }


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
