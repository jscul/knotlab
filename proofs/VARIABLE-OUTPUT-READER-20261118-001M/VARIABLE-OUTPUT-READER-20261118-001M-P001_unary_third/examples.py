"""Check the complementary last joins and a live nonlocal five-bit bond."""

from hashlib import sha256
from itertools import combinations
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent


def mask(items):
    return sum(1 << item for item in items)


def bits(word):
    while word:
        lowest = word & -word
        yield lowest.bit_length() - 1
        word ^= lowest


def replay(rows):
    """Use the original join criterion on each prefix, including the fresh counts."""
    holders = {}
    adjacency = []
    for site, row in enumerate(rows):
        assert len(set(row)) == len(row)
        parents = [holders[b][0] for b in row if b in holders]
        assert all(len(holders[b]) == 1 for b in row if b in holders)
        if site:
            assert len(parents) in (1, 2, 3) and len(set(parents)) == len(parents)
            assert all(adjacency[a] & adjacency[b] for a, b in combinations(parents, 2))
            assert len(parents) != 3 or not set.intersection(*(adjacency[a] for a in parents))
            assert len(row) - len(parents) == (3 if len(parents) == 1 else 2)
        else:
            assert len(row) == 3
        adjacency.append(set(parents))
        for parent in parents:
            adjacency[parent].add(site)
        for bit in row:
            holders.setdefault(bit, []).append(site)
    loose = sorted(b for b, sites in holders.items() if len(sites) == 1)
    menu = []
    for triple in combinations(loose, 3):
        a, b, c = (holders[bit][0] for bit in triple)
        if len({a, b, c}) != 3:
            continue
        x, y, z = (adjacency[site] for site in (a, b, c))
        if x & y and y & z and x & z and not x & y & z:
            menu.append(triple)
    return holders, loose, menu


def all_cuts(rows):
    """One ordinary shore per nonzero word, visiting by single-site changes."""
    stars = [mask(row) for row in rows]
    cut = 0
    for i in range(1, 1 << len(stars)):
        changed = (i & -i).bit_length() - 1
        cut ^= stars[changed]
        yield i ^ (i >> 1), cut


def connected(side, neighbors):
    seen = 0
    todo = side & -side
    while todo:
        vertex = todo & -todo
        todo ^= vertex
        seen |= vertex
        todo |= neighbors[vertex.bit_length() - 1] & side & ~seen
    return seen == side


def exact_table(rows):
    holders, _, _ = replay(rows)
    exterior = len(rows)
    neighbors = [0] * (exterior + 1)
    for endpoints in holders.values():
        a, b = endpoints if len(endpoints) == 2 else [endpoints[0], exterior]
        neighbors[a] |= 1 << b
        neighbors[b] |= 1 << a
    universe = (1 << (exterior + 1)) - 1
    table = {}
    for side, cut in all_cuts(rows):
        if connected(side, neighbors) and connected(universe ^ side, neighbors):
            size = cut.bit_count() - 1
            for pair in combinations(bits(cut), 2):
                table[pair] = min(table.get(pair, size), size)
    assert len(table) == len(holders) * (len(holders) - 1) // 2
    return [table[pair] for pair in sorted(table)]


def complementary(entry):
    prefix = entry['witness']['junction_supports']
    choices = [entry['source_inputs'], entry['other_inputs']]
    holders, loose, legal = replay(prefix)
    assert set(choices[0]).isdisjoint(choices[1]) and set(choices[0] + choices[1]) == set(loose)
    assert all(tuple(sorted(triple)) in legal for triple in choices)
    new = [len(holders), len(holders) + 1]
    left, right = ([*prefix, [*chosen, *new]] for chosen in choices)
    left_words, right_words = ({word for _, word in all_cuts(side)} for side in (left, right))
    assert left_words == right_words and len(left_words) == (1 << len(left)) - 1
    assert mask(left[-1]) ^ mask(right[-1]) == mask(loose)
    first, second = exact_table(left), exact_table(right)
    assert first == second and mask(left[-1]) not in {mask(r) for r in right}
    assert not replay(left)[2] and not replay(right)[2]
    wrong = left[-1].copy()
    wrong[0] = choices[1][0]
    assert mask(wrong) not in right_words
    mixed = [*prefix, wrong]
    mixed_table = exact_table(mixed)
    changed = sum(min(a, 5) != min(b, 5) for a, b in zip(first, mixed_table, strict=True))
    assert changed
    repeated_holder = tuple(sorted((choices[0][0], choices[1][0], choices[0][1])))
    assert repeated_holder not in legal
    return dict(width=len(holders) + 2, common_prefix=prefix, chosen=choices, new_outputs=new,
                legal_triples_before=legal, legal_triples_after=[replay(left)[2], replay(right)[2]],
                changed_pair_entries=sum(a != b for a, b in zip(first, second, strict=True)),
                pair_count=len(first), state_equation_rank=len(left), full_distances_row_major=first,
                identity_changes_last_junction=mask(left[-1]) not in {mask(r) for r in right},
                lawful_alternative=wrong, changed_through_four_on_lawful_alternative=changed,
                forbidden_repeated_holder=repeated_holder)


def proper_shore(record):
    rows = record['source']['junction_supports']
    holders, _, legal = replay(rows)
    assert legal == list(map(tuple, record['source']['legal_triples']))
    chosen = mask(record['cut']['shore_sites'])
    target = mask(record['cut']['cut_bits'])
    large = {}
    two_site_entering = []
    table = {}
    for side, cut in all_cuts(rows):
        size = cut.bit_count()
        assert size >= 3
        if size > 5:
            continue
        # A nonempty equation through five cannot be a disjoint union of two bonds.
        for pair in combinations(bits(cut), 2):
            table[pair] = min(table.get(pair, size), size)
        incoming = [b for b in bits(cut) if not side & (1 << holders[b][0])]
        if side.bit_count() >= 3:
            assert size == 5 and not incoming
            large[side] = cut
        elif side.bit_count() == 2 and incoming:
            two_site_entering.append(side)
    assert chosen in large and large[chosen] == target
    assert len(large) and two_site_entering
    assert all(a | b in large for a, b in combinations(large, 2))
    touched = set().union(*(set(bits(cut)) for cut in large.values()))
    protected = {}
    for i, row in enumerate(rows):
        old = [b for b in row if holders[b][0] != i]
        if len(old) == 3:
            safe = [b for b in old if b not in touched and holders[b][0] != 0]
            assert safe
            protected[i] = safe
    # A sufficient certificate entirely in the measured short rows for each star.
    pairs_forcing_stars = []
    for row in rows:
        star = set(row)
        size = len(star)
        for a, b in combinations(sorted(star), 2):
            if table.get((a, b)) != size:
                continue
            common = [c for c in holders if c in (a, b) or
                      (table.get(tuple(sorted((a, c))), 6) <= size and
                       table.get(tuple(sorted((b, c))), 6) <= size)]
            if set(common) == star:
                pairs_forcing_stars.append([a, b])
                break
        else:
            pairs_forcing_stars.append(None)
    return dict(width=len(holders), junctions=len(rows), shores_checked=(1 << len(rows)) - 1,
                proper_five_bond=list(bits(target)), legal_triples=legal, large_shores=len(large),
                nonseed_protected_inputs=protected, two_site_exception=list(bits(min(two_site_entering))),
                pairs_directly_forcing_stars=pairs_forcing_stars,
                direct_star_count=sum(pair is not None for pair in pairs_forcing_stars))


def main():
    data = json.loads((HERE / 'frontier.json').read_text())
    complementary_cases = [row['first_example'] for row in data['complementary_moves']
                           if row['moves_with_complement']]
    case, = complementary_cases
    return dict(frontier_sha256=sha256((HERE / 'frontier.json').read_bytes()).hexdigest(),
                first_complement=complementary(case),
                live_proper_shore=proper_shore(data['proper_five_bond_at_first_positive_with_two_prior_shrinks']))


if __name__ == '__main__':
    print(json.dumps(main(), indent=2))
