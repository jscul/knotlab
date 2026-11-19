"""Exhaust the local shortest-word conditions on three four-place blocks."""

from collections import Counter
from functools import cache
from itertools import combinations, product
from math import comb
import json
import sys


PROXY = "outside_seed"


def members(word):
    while word:
        bit = word & -word
        word ^= bit
        yield bit.bit_length() - 1


def mask(indices):
    return sum(1 << index for index in indices)


@cache
def bell(n):
    if n == 0:
        return 1
    return sum(comb(n - 1, k) * bell(k) for k in range(n))


class Block:
    def __init__(self, name, left, right, missing=()):
        self.name = name
        self.sides = (left, right)
        self.sites = (*left, *right)
        edges = [(a, b) for a, b in product(left, right) if (a, b) not in missing]
        neighbors = {site: {other for edge in edges if site in edge for other in edge if other != site}
                     for site in self.sites}
        self.edges = edges
        self.neighbors = neighbors
        self.holders = (*edges, *((site,) for site in self.sites for _ in range(4 - len(neighbors[site]))), ())
        self.names = (*map("".join, edges),
                      *(f"{site}:{i}" for site in self.sites for i in range(4 - len(neighbors[site]))), PROXY)
        assert len(self.names) == len(self.holders) == len(set(self.names))
        self.proxy = 1 << (len(self.names) - 1)
        self.ports = tuple(tuple(i for i, ends in enumerate(self.holders) if len(ends) == 1 and ends[0] in side)
                           for side in self.sides)
        self.stars = {site: mask(i for i, ends in enumerate(self.holders) if site in ends) for site in self.sites}
        assert all(word.bit_count() == 4 for word in self.stars.values())
        translations = {0}
        for word in self.stars.values():
            translations |= {old ^ word for old in translations}
        self.translations = tuple(sorted(translations))
        assert len(self.translations) == 1 << len(self.sites)
        self.local = tuple(mask(j for j, right in enumerate(self.holders)
                                if any(a == b or b in neighbors[a] for a, b in product(left, right)))
                           for left in self.holders)

    def named(self, word):
        return tuple(self.names[i] for i in members(word))

    def simple(self, group):
        return len({self.holders[i][0] for i in group}) == len(group)

    def partitions(self, slots):
        if not slots:
            yield ()
            return
        first, *rest = slots
        for amount in range(len(rest) + 1):
            for others in combinations(rest, amount):
                group = (first, *others)
                if self.simple(group):
                    for further in self.partitions(tuple(i for i in rest if i not in others)):
                        yield (group, *further) if others else further

    def seed_placements(self):
        yield ()
        for side in self.ports:
            for used in range(1, 4):
                for slots in combinations(side, used):
                    if self.simple(slots):
                        yield slots

    def exteriors(self, seed):
        side_slots = [tuple(i for i in side if i not in seed) for side in self.ports]
        for left, right in product(*(tuple(self.partitions(side)) for side in side_slots)):
            yield (*left, *right)

    def exterior_count(self, seed):
        total = 1
        for side in self.ports:
            used = Counter(self.holders[i][0] for i in side if i not in seed)
            assert all(count <= 2 for count in used.values())
            m = sum(count == 2 for count in used.values())
            n = sum(used.values())
            total *= sum((-1) ** k * comb(m, k) * bell(n - k) for k in range(m + 1))
        return total


def local_cosets(block):
    counted = set()
    pool = []
    sizes = Counter()
    for subset in combinations(range(len(block.names)), 6):
        candidate = mask(subset)
        if candidate in counted:
            continue
        orbit = tuple(candidate ^ translation for translation in block.translations)
        minimum = min(word.bit_count() for word in orbit)
        ties = tuple(sorted(word for word in orbit if word.bit_count() == 6))
        counted.update(ties)
        sizes[(bool(candidate & block.proxy), minimum)] += len(ties)
        if minimum == 6:
            assert all((word & site).bit_count() <= 2 for word in ties for site in block.stars.values())
            pool.append(ties)
    assert len(counted) == comb(len(block.names), 6)
    assert sum(sizes.values()) == len(counted)
    return pool, {"without_seed_proxy": {k: v for (proxy, k), v in sorted(sizes.items()) if not proxy},
                  "with_seed_proxy": {k: v for (proxy, k), v in sorted(sizes.items()) if proxy}}


def exterior_test(block, seed, groups):
    seed_mask = mask(seed) | block.proxy
    outside = tuple(mask(group) for group in groups if len(group) > 2)
    close = list(block.local)
    for group in groups:
        whole_group = mask(group)
        for i in group:
            close[i] |= whole_group

    def failure(word, check_pairs=True):
        if (word & seed_mask).bit_count() > 1:
            return "seed_overlap", None
        if any((word & group).bit_count() > 2 for group in outside):
            return "outside_holder_overlap", None
        if check_pairs:
            remaining = word & ~seed_mask
            while remaining:
                bit = remaining & -remaining
                remaining ^= bit
                a = bit.bit_length() - 1
                far = remaining & ~close[a]
                if far:
                    b = (far & -far).bit_length() - 1
                    return "pair_exceeds_six", (block.names[a], block.names[b])
        return None

    return failure


def classify(block, pool):
    counts = {size: Counter() for size in range(4)}
    without_proxy = [ties for ties in pool if not (ties[0] & block.proxy)]
    examples = {}
    for seed in block.seed_placements():
        totals = counts[len(seed)]
        totals["seed_placements"] += 1
        available = pool if len(seed) < 3 else without_proxy
        models = tuple(block.exteriors(seed))
        assert len(models) == len(set(models)) == block.exterior_count(seed)
        totals["outside_models"] += len(models)
        totals["minimal_model_word_pairs"] += len(models) * sum(map(len, available))
        for groups in models:
            failure = exterior_test(block, seed, groups)
            for ties in available:
                verdicts = tuple(failure(word) for word in ties)
                passed = verdicts.count(None)
                if not passed:
                    continue
                totals["initially_compatible"] += passed
                if passed == len(ties):
                    totals["surviving_words"] += len(ties)
                    if "survivor" not in examples:
                        examples["survivor"] = describe(block, seed, groups, ties[0])
                elif "initial_pass_lost_by_translation" not in examples:
                    good = next(word for word, verdict in zip(ties, verdicts, strict=True) if verdict is None)
                    bad, (kind, pair) = next((word, verdict) for word, verdict in zip(ties, verdicts, strict=True)
                                              if verdict is not None)
                    examples["initial_pass_lost_by_translation"] = {
                        **describe(block, seed, groups, good), "translated_word": block.named(bad),
                        "obstruction": kind, "obstructing_pair": pair,
                        "sites_added": translation_sites(block, good ^ bad),
                    }
    for n in counts:
        for key in ("surviving_words", "initially_compatible"):
            counts[n][key] += 0
    return {n: dict(totals) for n, totals in counts.items()}, examples


def describe(block, seed, groups, word):
    return {"word": block.named(word), "seed_ports": tuple(block.names[i] for i in seed),
            "outside_holder_groups": [tuple(block.names[i] for i in group) for group in groups]}


def translation_sites(block, difference):
    for length in range(len(block.sites) + 1):
        for sites in combinations(block.sites, length):
            result = 0
            for site in sites:
                result ^= block.stars[site]
            if result == difference:
                return sites
    raise AssertionError(difference)


def literal_control(block, pool):
    """Cross-check one exterior by set operations, with no compiled pair masks."""
    seed = ()
    groups = max(block.exteriors(seed), key=lambda groups: max(map(len, groups), default=0))
    lookup = [set(group) for group in groups]

    def relational(word, test_pairs):
        selected = set(members(word))
        if any(len(selected & group) > 2 for group in lookup):
            return False
        if not test_pairs:
            return True
        selected.discard(block.proxy.bit_length() - 1)
        for a, b in combinations(selected, 2):
            if any({a, b} <= group for group in lookup):
                continue
            if not any(x == y or y in block.neighbors[x] for x in block.holders[a] for y in block.holders[b]):
                return False
        return True

    fast = exterior_test(block, seed, groups)
    initial = final = 0
    relaxed = None
    for ties in pool:
        results = [relational(word, True) for word in ties]
        assert results == [fast(word) is None for word in ties]
        initial += sum(results)
        final += len(ties) if all(results) else 0
        if relaxed is None and not all(results) and all(relational(word, False) for word in ties):
            assert all(fast(word, False) is None for word in ties)
            relaxed = describe(block, seed, groups, ties[0])
    assert relaxed is not None, "pair-test control must fail once pair checks are restored"
    return {"initial_passes": initial, "final_survivors": final,
            "word_admitted_after_dropping_pair_test": relaxed}


def examine(block):
    pool, distribution = local_cosets(block)
    by_seed, examples = classify(block, pool)
    totals = Counter()
    for row in by_seed.values():
        totals.update(row)
    result = {"block": block.name, "internal_meetings": block.edges, "slot_order": block.names,
              "four_place_stars": {site: block.named(word) for site, word in block.stars.items()},
              "local_translations": len(block.translations), "minimum_weight_distribution": distribution,
              "locally_minimal_cosets": len(pool), "locally_minimal_words": sum(map(len, pool)),
              "by_seed_ports": by_seed, "totals": dict(totals), "examples": examples,
              "every_partition_count_cross_checked_by_inclusion_exclusion": True,
              "independent_set_pair_control": literal_control(block, pool)}
    print(f"{block.name}: {totals['outside_models']} models, {totals['initially_compatible']} initial passes, "
          f"{totals['surviving_words']} survivors", file=sys.stderr, flush=True)
    return result


def main():
    blocks = (Block("K2,3", "ab", "xyz"), Block("K2,4", "ab", "wxyz"),
              Block("K3,3 minus two nonincident meetings", "abc", "xyz", (("a", "x"), ("b", "y"))))
    print(json.dumps([examine(block) for block in blocks], indent=2))


if __name__ == "__main__":
    main()
