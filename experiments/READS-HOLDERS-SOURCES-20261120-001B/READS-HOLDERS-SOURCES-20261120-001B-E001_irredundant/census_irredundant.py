"""Census of connected starts with exact local laws and essential holders."""

import argparse
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import cache
import gzip
from itertools import combinations_with_replacement, permutations
import json
from math import factorial, prod
from pathlib import Path
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PRIOR = ROOT / 'experiments'
sys.path.insert(0, str(PRIOR / 'FOUR-READINGS-20261120-001C'
                       / 'FOUR-READINGS-20261120-001C-E001_embodied_settings'))
sys.path.insert(0, str(PRIOR / 'FOUR-READINGS-20261120-001B'
                       / 'FOUR-READINGS-20261120-001B-E001_state_growth'))
from census import presentations
from model import growth


LAWS = ('nae', 'parity')


def members(mask):
    while mask:
        bit = mask & -mask
        yield bit.bit_length() - 1
        mask ^= bit


def mask_of(items):
    return sum(1 << i for i in items)


def connected(supports):
    reached = supports[0]
    for _ in supports[1:]:
        for support in supports:
            if support & reached:
                reached |= support
    return all(reached & support for support in supports)


def accepts(word, support, law):
    within = word & support
    if law == 'nae':
        return within not in (0, support)
    return within.bit_count() % 2 == 0


@cache
def fibers(width, support):
    """Bitset of full words for each possible projected word."""
    groups = defaultdict(int)
    for word in range(1 << width):
        groups[word & support] |= 1 << word
    return groups


@cache
def accepts_mask(width, support, law):
    return sum(words for word, words in fibers(width, support).items()
               if accepts(word, support, law))


def laws_intersection(width, masks):
    result = (1 << (1 << width)) - 1
    for mask in masks:
        result &= mask
    return result


def projection_count(width, words, support):
    return sum(bool(words & group) for group in fibers(width, support).values())


def exact_projection(width, words, support, law):
    return (bool(words) and not words & ~accepts_mask(width, support, law)
            and projection_count(width, words, support)
            == sum(accepts(word, support, law) for word in fibers(width, support)))


def analyze(width, supports, law):
    masks = tuple(accepts_mask(width, support, law) for support in supports)
    words = laws_intersection(width, masks)
    if not all(exact_projection(width, words, support, law) for support in supports):
        return words, None
    deletions = []
    for i, support in enumerate(supports):
        without = laws_intersection(width, masks[:i] + masks[i + 1:])
        extra = without & ~words
        projected_extra = projection_count(width, without, support) > projection_count(width, words, support)
        assert projected_extra == bool(extra)
        deletions.append(next(members(extra), None))
    return words, tuple(deletions)


def physical_automorphisms(width, supports):
    """Count induced distinction permutations, including indistinct support occurrences."""
    incidence_counts = Counter(tuple(i for i, row in enumerate(supports) if row & (1 << bit))
                               for bit in range(width))
    holder_orders = sum(all(incidence_counts[tuple(sorted(order[i] for i in group))] == count
                            for group, count in incidence_counts.items())
                        for order in permutations(range(len(supports))))
    labeled = holder_orders * prod(factorial(count) for count in incidence_counts.values())
    fixed_names = prod(factorial(count) for count in Counter(supports).values())
    assert labeled % fixed_names == 0
    return labeled // fixed_names


def constraint_graph(width, candidate_supports):
    graph = nx.Graph()
    graph.add_nodes_from((i, {'kind': ('distinction',)}) for i in range(width))
    for support in candidate_supports:
        node = width + support
        graph.add_node(node, kind=('support', support.bit_count()))
        graph.add_edges_from((node, i) for i in members(support))
    return graph


def graph_match(left, right):
    return nx.vf2pp_isomorphism(left, right, node_label='kind')


def distinction_automorphisms(graph, width, keep_transports=False):
    """Orbit-stabilizer chain fixing earlier distinction names at each step."""
    fixed = graph.copy()
    order = 1
    transports = []
    for source in range(width - 1):
        marked = fixed.copy()
        pin = ('pinned distinction', source)
        marked.nodes[source]['kind'] = pin
        images = 1
        for target in range(source + 1, width):
            if fixed.degree(source) != fixed.degree(target):
                continue
            old_kind = fixed.nodes[target]['kind']
            fixed.nodes[target]['kind'] = pin
            matching = graph_match(marked, fixed)
            fixed.nodes[target]['kind'] = old_kind
            if matching is not None:
                images += 1
                if keep_transports:
                    transports.append(tuple(matching[i] for i in range(width)))
        order *= images
        fixed = marked
    return order, tuple(transports)


def move_mask(mask, mapping):
    return mask_of(mapping[i] for i in members(mask))


def has_loose(supports):
    return any(count == 1 for count in Counter(i for s in supports for i in members(s)).values())


def roster(supports, law):
    status, births = growth(tuple(tuple(members(support)) for support in supports), law)
    counted = Counter((tuple(sorted(supports[i] for i in parents)), fresh)
                      for parents, fresh in births)
    return status, tuple(sorted((parents, fresh, count)
                                for (parents, fresh), count in counted.items()))


def move_roster(record, move):
    status, births = record
    return status, tuple(sorted((tuple(sorted(move(p) for p in parents)), fresh, count)
                                for parents, fresh, count in births))


def unmarked_roster(record):
    active = sorted({p for parents, _, _ in record[1] for p in parents})
    return min(move_roster(record, dict(zip(active, renaming, strict=True)).__getitem__)
               for renaming in permutations(range(len(active))))


def roster_graph(graph, width, record):
    marked = graph.copy()
    for i, (parents, fresh, count) in enumerate(record[1], start=max(marked) + 1):
        marked.add_node(i, kind=('birth', fresh, count))
        marked.add_edges_from((i, width + support) for support in parents)
    return marked


@dataclass
class GrowthClass:
    roster: tuple
    graph: nx.Graph
    automorphisms: int


@dataclass
class Start:
    supports: tuple
    automorphisms: int
    deletions: tuple
    roster: tuple
    growth_class: int
    unmarked: tuple


@dataclass
class StateClass:
    words: int
    graph: nx.Graph
    automorphisms: int
    transports: tuple
    starts: list = field(default_factory=list)
    growths: list = field(default_factory=list)

    def growth_class(self, width, record):
        graph = roster_graph(self.graph, width, record)
        for i, entry in enumerate(self.growths):
            if record[0] == entry.roster[0] and graph_match(graph, entry.graph) is not None:
                return i
        order = distinction_automorphisms(graph, width)[0] if record[1] else self.automorphisms
        assert self.automorphisms % order == 0
        self.growths.append(GrowthClass(record, graph, order))
        return len(self.growths) - 1


def add_start(width, law, groups, supports, words, order, deletions):
    # This family is an exact representation of the relation. Every member
    # is implied by the states, and the family includes the actual supports.
    candidate_supports = tuple(s for s in range(1 << width)
                               if s.bit_count() >= 3 and exact_projection(width, words, s, law))
    assert set(supports) <= set(candidate_supports)
    graph = constraint_graph(width, candidate_supports)
    key = (words.bit_count(), tuple(sorted(s.bit_count() for s in candidate_supports)),
           tuple(sorted(graph.degree(i) for i in range(width))))
    for entry in groups[key]:
        mapping = graph_match(graph, entry.graph)
        if mapping is not None:
            break
    else:
        automorphisms, transports = distinction_automorphisms(graph, width, keep_transports=True)
        entry = StateClass(words, graph, automorphisms, transports)
        groups[key].append(entry)
        mapping = tuple(range(width))

    def move(value):
        return move_mask(value, mapping)

    assert entry.words == mask_of(move(word) for word in members(words))
    assert entry.automorphisms % order == 0
    aligned = tuple(sorted((move(support), move(word))
                           for support, word in zip(supports, deletions, strict=True)))
    aligned_supports, aligned_deletions = zip(*aligned, strict=True)
    record = roster(aligned_supports, law)
    entry.starts.append(Start(aligned_supports, order, aligned_deletions, record,
                              entry.growth_class(width, record), unmarked_roster(record)))


def raw_start(supports, record, deletion_words):
    return {'supports': [tuple(members(s)) for s in supports],
            'has_loose_distinction': has_loose(supports),
            'deletion_words': deletion_words,
            'status': record[0],
            'births': [{'parents': [tuple(members(s)) for s in parents],
                        'fresh': fresh, 'multiplicity': count}
                       for parents, fresh, count in record[1]]}


def state_readout(width, entry):
    named_states = factorial(width) // entry.automorphisms
    named_starts = sum(entry.automorphisms // s.automorphisms for s in entry.starts)
    named_growths = sum(entry.automorphisms // g.automorphisms for g in entry.growths)
    unmarked = len({s.unmarked for s in entry.starts})
    return {'state_words_hex': hex(entry.words), 'allowed_states': entry.words.bit_count(),
            'state_automorphisms': entry.automorphisms, 'named_states_in_orbit': named_states,
            'named_presentations_per_state': named_starts, 'named_rosters_per_state': named_growths,
            'state_matched_rosters': len(entry.growths), 'unmarked_rosters': unmarked,
            'growth_automorphisms': [g.automorphisms for g in entry.growths],
            'presentations': [dict(raw_start(s.supports, s.roster, s.deletions),
                                   presentation_automorphisms=s.automorphisms,
                                   state_matched_roster_id=s.growth_class + 1)
                              for s in entry.starts]}


def witness_pairs(entry):
    for i, left in enumerate(entry.starts):
        for j in range(i, len(entry.starts)):
            right = entry.starts[j]
            comparisons = []
            if i != j:
                comparisons.append((right.supports, right.roster, right.deletions, None))
            for transport in entry.transports:
                def move(value):
                    return move_mask(value, transport)

                aligned = tuple(sorted((move(s), move(w)) for s, w in
                                       zip(right.supports, right.deletions, strict=True)))
                supports, deletions = zip(*aligned, strict=True)
                if supports != left.supports:
                    comparisons.append((supports, move_roster(right.roster, move), deletions, transport))
            for supports, record, deletions, transport in comparisons:
                yield (
                    (len(left.supports), len(supports)),
                    {'left': raw_start(left.supports, left.roster, left.deletions),
                     'right': raw_start(supports, record, deletions),
                     'renaming_applied_to_right': transport},
                    {
                        'different_named_holdings': True,
                        'different_named_holdings_with_live_parent': has_loose(left.supports) or has_loose(supports),
                        'different_named_rosters': left.roster != record,
                        'different_holdings_up_to_renaming': i != j,
                        'different_state_matched_rosters': left.growth_class != right.growth_class,
                        'different_unmarked_rosters': left.unmarked != right.unmarked,
                        'same_terminal_outcome': left.roster[0] == record[0] != 'births',
                        'nonisomorphic_holdings_same_terminal': i != j and left.roster[0] == record[0] != 'births',
                    },
                )


def width_summary(width, records, counts):
    # Each relation orbit represents many different named relations. Its
    # permitted named presentations and rosters are counted by their stabilizers.
    totals = Counter(counts)
    maxima = Counter()
    for row in records:
        states = row['named_states_in_orbit']
        totals['named_state_classes'] += states
        totals['state_classes_up_to_renaming'] += 1
        totals['named_states_with_distinct_holdings'] += states * (row['named_presentations_per_state'] > 1)
        totals['named_states_with_distinct_holdings_and_unique_roster'] += states * (
            row['named_presentations_per_state'] > 1 and row['named_rosters_per_state'] == 1)
        totals['named_states_with_distinct_rosters'] += states * (row['named_rosters_per_state'] > 1)
        totals['state_orbits_with_distinct_holdings'] += len(row['presentations']) > 1
        totals['state_orbits_with_distinct_state_matched_rosters'] += row['state_matched_rosters'] > 1
        totals['state_orbits_with_distinct_unmarked_rosters'] += row['unmarked_rosters'] > 1
        totals['named_presentations_via_states'] += states * row['named_presentations_per_state']
        for field in ('named_presentations_per_state', 'named_rosters_per_state',
                      'state_matched_rosters', 'unmarked_rosters'):
            maxima[field] = max(maxima[field], row[field])
    assert totals['irredundant_named'] == totals.pop('named_presentations_via_states')
    assert sum(len(r['presentations']) for r in records) == totals['irredundant_up_to_renaming']
    return dict(totals, maxima=dict(maxima),
                worst_case_conditional_bits={key: (size - 1).bit_length() for key, size in maxima.items()})


def census_width(width):
    counts = {law: Counter(lawful_named=0, lawful_up_to_renaming=0, irredundant_named=0,
                           irredundant_up_to_renaming=0) for law in LAWS}
    grouped = {law: defaultdict(list) for law in LAWS}
    syntax = Counter(all_up_to_renaming=0, connected_up_to_renaming=0, connected_named=0)
    for count in range(1, 2 * width // 3 + 1):
        for rows, _ in presentations(width, count):
            syntax['all_up_to_renaming'] += 1
            supports = tuple(sorted(mask_of(row) for row in rows))
            if not connected(supports):
                continue
            order = physical_automorphisms(width, supports)
            named = factorial(width) // order
            syntax['connected_up_to_renaming'] += 1
            syntax['connected_named'] += named
            for law in LAWS:
                words, deletions = analyze(width, supports, law)
                if deletions is None:
                    continue
                counts[law]['lawful_named'] += named
                counts[law]['lawful_up_to_renaming'] += 1
                if None in deletions:
                    continue
                counts[law]['irredundant_named'] += named
                counts[law]['irredundant_up_to_renaming'] += 1
                add_start(width, law, grouped[law], supports, words, order, deletions)
    entries = {law: [entry for bucket in grouped[law].values() for entry in bucket] for law in LAWS}
    raw = {law: [state_readout(width, entry) for entry in entries[law]] for law in LAWS}
    summaries = {law: width_summary(width, raw[law], counts[law]) for law in LAWS}
    return dict(syntax), summaries, raw, entries


def direct_named(width):
    """Independent small denominator and exact named-class check without a quotient."""
    histograms = {law: Counter(lawful_named=0, irredundant_named=0) for law in LAWS}
    groups = {law: defaultdict(list) for law in LAWS}
    candidates = [mask for mask in range(1 << width) if mask.bit_count() >= 3]
    all_words = range(1 << width)
    syntax = 0
    for count in range(1, 2 * width // 3 + 1):
        for supports in combinations_with_replacement(candidates, count):
            if not all(sum((support >> i) & 1 for support in supports) in (1, 2) for i in range(width)):
                continue
            reached = {0}
            while more := {j for j in range(count) if j not in reached
                           and any(supports[i] & supports[j] for i in reached)}:
                reached.update(more)
            if len(reached) < count:
                continue
            syntax += 1
            for law in LAWS:
                failures = {word: tuple(i for i, s in enumerate(supports) if not accepts(word, s, law))
                            for word in all_words}
                words = tuple(w for w, failure in failures.items() if not failure)
                if not all({w & s for w in words} == {w & s for w in all_words if accepts(w, s, law)}
                           for s in supports):
                    continue
                histograms[law]['lawful_named'] += 1
                if set(range(count)) != {failure[0] for failure in failures.values() if len(failure) == 1}:
                    continue
                histograms[law]['irredundant_named'] += 1
                groups[law][words].append(roster(supports, law))
    for law, classes in groups.items():
        histograms[law].update(named_state_classes=len(classes),
                               named_states_with_distinct_holdings=sum(len(v) > 1 for v in classes.values()),
                               named_states_with_distinct_rosters=sum(len(set(v)) > 1 for v in classes.values()))
    return syntax, histograms


def update_minima(minima, width, entries):
    for state_id, entry in enumerate(entries, start=1):
        for holder_counts, pair, flags in witness_pairs(entry):
            rank = (width, max(holder_counts), sum(holder_counts))
            for key, found in flags.items():
                if not found:
                    continue
                if key not in minima or rank < minima[key]['width_max_holders_total_holders']:
                    minima[key] = {'width_max_holders_total_holders': rank, 'examples': {}}
                if rank == minima[key]['width_max_holders_total_holders']:
                    minima[key]['examples'].setdefault(state_id, pair)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--max-width', type=int, choices=range(3, 10), default=9)
    parser.add_argument('--no-write', action='store_true')
    args = parser.parse_args()
    archived = ROOT / 'artifacts/FOUR-READINGS-20261120-001C/FOUR-READINGS-20261120-001C-E001_embodied_settings'
    prior = json.loads((archived / 'census_summary.json').read_text())['by_size']
    summary = {'by_width': {}, 'minima': {law: {} for law in LAWS}, 'controls': {'direct_named_widths': []}}
    raw = {}
    for width in range(3, args.max_width + 1):
        syntax, results, records, entries = census_width(width)
        assert syntax['all_up_to_renaming'] == prior[str(width)]['structural']['presentations']
        if width <= 5:
            named_syntax, named = direct_named(width)
            assert named_syntax == syntax['connected_named']
            for law in LAWS:
                assert all(results[law][k] == v for k, v in named[law].items())
            summary['controls']['direct_named_widths'].append(width)
        summary['by_width'][width] = dict(syntax=syntax, laws=results)
        raw[width] = records
        for law in LAWS:
            update_minima(summary['minima'][law], width, entries[law])
        print(f'width {width}: {syntax["connected_up_to_renaming"]} connected, '
              + ', '.join(f'{law} {results[law]["irredundant_up_to_renaming"]} irredundant' for law in LAWS),
              flush=True)
    if not args.no_write:
        OUTPUT.mkdir(parents=True, exist_ok=True)
        (OUTPUT / 'census_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
        (OUTPUT / 'census_cases.json.gz').write_bytes(gzip.compress(json.dumps(raw).encode(), mtime=0))


if __name__ == '__main__':
    main()
