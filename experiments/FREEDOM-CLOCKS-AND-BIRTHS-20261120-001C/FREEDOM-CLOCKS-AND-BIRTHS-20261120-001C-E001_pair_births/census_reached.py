"""Exhaust the pair tables and next births at the first reached census stages."""

from collections import Counter, defaultdict
from dataclasses import dataclass, field
from functools import cache
import gzip
from itertools import combinations, groupby
import json
from math import factorial
from pathlib import Path
import sys

from census_incidence import automorphisms, incidence_family, matching
from census_rates import canonical_pair_table, pair_symmetries


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
PREVIOUS = 'READS-HOLDERS-SOURCES-20261120-001B'
OLD_FAMILY = f'{PREVIOUS}-E001_irredundant'
LAWS = ('nae', 'parity')
sys.path.insert(0, str(ROOT / 'experiments' / PREVIOUS / OLD_FAMILY))
from controls import next_stage
from model import growth, mask_of, nae_counts, parity_bonds, parity_counts, reduced, width


def named_rows(rows, mapping=None):
    if mapping is None:
        return tuple(sorted(tuple(sorted(r)) for r in rows))
    return tuple(sorted(tuple(sorted(mapping[i] for i in r)) for r in rows))


def relation_key(rows, law):
    # Reached NAE sources are open and have unique lawful irredundant
    # holdings by the preceding all-size classification.
    return named_rows(rows) if law == 'nae' else reduced(map(mask_of, rows))


def relation_supports(rows, law):
    if law == 'nae':
        return tuple(map(mask_of, rows))
    return tuple(sorted(parity_bonds(rows)))


@dataclass
class IsomorphismClasses:
    buckets: dict = field(default_factory=lambda: defaultdict(list))
    orders: list = field(default_factory=list)

    def identify(self, size, supports):
        family = incidence_family(size, supports)
        signature = family.signature
        for index, other in self.buckets[signature]:
            if matching(family, other) is not None:
                return index, self.orders[index]
        index = len(self.orders)
        self.orders.append(automorphisms(family))
        self.buckets[signature].append((index, family))
        return index, self.orders[index]


@dataclass
class TableClass:
    automorphisms: int
    reached_width: int
    states: IsomorphismClasses = field(default_factory=IsomorphismClasses)
    presentations: IsomorphismClasses = field(default_factory=IsomorphismClasses)
    sources: list = field(default_factory=list)


def from_archive():
    archived = ROOT / 'artifacts' / PREVIOUS / OLD_FAMILY / 'census_cases.json.gz'
    with gzip.open(archived, 'rt') as data:
        book = json.load(data)
    sources = {law: [] for law in LAWS}
    for source_width in range(3, 9):
        for law in LAWS:
            for state in book[str(source_width)][law]:
                for row in state['presentations']:
                    supports = tuple(tuple(r) for r in row['supports'])
                    multiplicity = factorial(source_width) // row['presentation_automorphisms']
                    sources[law].append((source_width, supports, multiplicity))
    return sources


def as_pairs(size, counts):
    return dict(zip(combinations(range(size), 2), counts, strict=True))


@cache
def count_pairs(rows, law):
    return nae_counts(rows) if law == 'nae' else parity_counts(rows)


def reached_case(source_width, source_rows, multiplicity, law, tables):
    first_status, reached, births = next_stage(source_rows, law)
    result = {'law': law, 'source_width': source_width, 'source_rows': source_rows,
              'labelled_source_multiplicity': multiplicity, 'first_status': first_status}
    if first_status != 'births':
        assert first_status in ('closed', 'stall')
        return result
    n = width(reached)
    next_status, following = growth(reached, law)
    total, counts = count_pairs(reached, law)
    profile = canonical_pair_table(n, total, counts)
    table = tables.setdefault(profile.key, TableClass(profile.automorphisms, n))
    assert table.automorphisms == profile.automorphisms
    if law == 'nae':
        assert next_status == 'births' and all(f > 0 for _, f in births)
    state, state_order = table.states.identify(n, relation_supports(reached, law))
    physical, physical_order = table.presentations.identify(n, tuple(map(mask_of, reached)))
    assert profile.automorphisms % state_order == 0 and state_order % physical_order == 0
    if law == 'nae':
        assert state_order == physical_order and state == physical
    result.update(first_birth_count=len(births), first_births=births, stage_width=n, stage_rows=reached,
                  next_status=next_status, next_birth_count=len(following), next_births=following,
                  table_key=profile.key, table_order=profile.order, table_automorphisms=profile.automorphisms,
                  state_type_within_table=state, state_automorphisms=state_order,
                  physical_type_within_table=physical, physical_automorphisms=physical_order,
                  total_words=total, pair_counts=tuple(counts[i, j] for i, j in combinations(range(n), 2)))
    table.sources.append(result)
    return result


def alternatives(table, source_limit):
    sources = [s for s in table.sources if s['source_width'] <= source_limit]
    if not sources:
        return None
    states = {s['state_type_within_table']: s['state_automorphisms'] for s in sources}
    presentations = {s['physical_type_within_table']: s['physical_automorphisms'] for s in sources}
    same_state = defaultdict(set)
    for source in sources:
        same_state[source['state_type_within_table']].add(source['next_birth_count'])
    return {'named_tables': factorial(table.reached_width) // table.automorphisms,
            'state_types': len(states), 'physical_types': len(presentations),
            'named_states_per_table': sum(table.automorphisms // a for a in states.values()),
            'named_presentations_per_table': sum(table.automorphisms // a for a in presentations.values()),
            'next_outcomes': sorted({(s['next_status'], s['next_birth_count']) for s in sources}),
            'same_states_different_birth_counts': any(len(counts) > 1 for counts in same_state.values())}


def counts_at_bound(source_limit, sources, tables):
    outcomes = Counter((s['first_status'] for s in sources if s['source_width'] <= source_limit))
    named = Counter()
    for s in sources:
        if s['source_width'] <= source_limit:
            named[s['first_status']] += s['labelled_source_multiplicity']
    tally = Counter(table_types=0, named_tables=0, state_types=0, named_states=0,
                    physical_types=0, named_presentations=0,
                    table_types_with_named_state_ambiguity=0, table_types_with_state_type_ambiguity=0,
                    table_types_with_named_holding_ambiguity=0, table_types_with_physical_type_ambiguity=0,
                    table_types_with_birth_count_ambiguity=0, table_types_with_next_outcome_ambiguity=0,
                    table_types_with_same_states_and_different_birth_counts=0,
                    named_tables_with_state_ambiguity=0, named_tables_with_birth_count_ambiguity=0,
                    named_tables_with_next_outcome_ambiguity=0)
    for table in tables.values():
        data = alternatives(table, source_limit)
        if data is None:
            continue
        status, state_types, physical_types = data['next_outcomes'], data['state_types'], data['physical_types']
        count_ambiguity = len({count for _, count in status}) > 1
        outcome_ambiguity = len(status) > 1
        state_ambiguity = data['named_states_per_table'] > 1
        q = data['named_tables']
        tally.update(table_types=1, named_tables=q, state_types=state_types,
                     named_states=q * data['named_states_per_table'], physical_types=physical_types,
                     named_presentations=q * data['named_presentations_per_table'],
                     table_types_with_named_state_ambiguity=state_ambiguity,
                     table_types_with_state_type_ambiguity=state_types > 1,
                     table_types_with_named_holding_ambiguity=data['named_presentations_per_table'] > 1,
                     table_types_with_physical_type_ambiguity=physical_types > 1,
                     table_types_with_birth_count_ambiguity=count_ambiguity,
                     table_types_with_next_outcome_ambiguity=outcome_ambiguity,
                     table_types_with_same_states_and_different_birth_counts=data['same_states_different_birth_counts'],
                     named_tables_with_state_ambiguity=q * state_ambiguity,
                     named_tables_with_birth_count_ambiguity=q * count_ambiguity,
                     named_tables_with_next_outcome_ambiguity=q * outcome_ambiguity)
    return {'source_types_by_first_outcome': outcomes, 'named_sources_by_first_outcome': named,
            'reached_tables_and_relations': tally}


def inverse(order):
    destination = [0] * len(order)
    for new, old in enumerate(order):
        destination[old] = new
    return tuple(destination)


def witness_arm(source, recoding=None, map_to_table=None):
    if map_to_table is None:
        map_to_table = inverse(source['table_order'])
    if recoding is not None:
        map_to_table = tuple(map_to_table[i] for i in recoding)
    return {'source_rows': source['source_rows'], 'first_births': source['first_births'],
            'reached_rows_in_common_names': named_rows(source['stage_rows'], map_to_table),
            'recode_reached_names': map_to_table, 'allowed_word_count': source['total_words'],
            'next_status': source['next_status'], 'next_birth_count': source['next_birth_count']}


def within_type_witness(law, source, physical=False):
    n, total = source['stage_width'], source['total_words']
    counts = as_pairs(n, source['pair_counts'])
    def key(rows):
        return named_rows(rows) if physical else relation_key(rows, law)

    states = key(source['stage_rows'])
    for reordering in pair_symmetries(n, total, counts):
        other = named_rows(source['stage_rows'], reordering)
        if key(other) != states:
            assert all(counts[i, j] == counts[tuple(sorted((reordering[i], reordering[j])))]
                       for i, j in counts)
            return witness_arm(source, reordering)
    raise AssertionError('The extra table symmetries must move some named state set')


def state_transport(left, right, law):
    n = left['stage_width']
    a = incidence_family(n, relation_supports(right['stage_rows'], law))
    b = incidence_family(n, relation_supports(left['stage_rows'], law))
    transport = {old: new for i, j in enumerate(matching(a, b))
                 for old, new in zip(a.distinctions[i], b.distinctions[j], strict=True)}
    assert relation_key(left['stage_rows'], law) == relation_key(named_rows(right['stage_rows'], transport), law)
    canonical = inverse(left['table_order'])
    return tuple(canonical[transport[i]] for i in range(n))


def minima(law, tables):
    chosen = {}

    def consider(label, key, a, b):
        rank = (max(a['source_width'], b['source_width']), a['stage_width'],
                len(a['source_rows']) + len(b['source_rows']))
        if label not in chosen or rank < chosen[label][0]:
            chosen[label] = (rank, key, a, b)

    for key, table in tables.items():
        data = alternatives(table, 8)
        if data['named_states_per_table'] == data['named_presentations_per_table'] == len(data['next_outcomes']) == 1:
            continue
        for a in table.sources:
            if a['state_automorphisms'] < a['table_automorphisms']:
                consider('different_named_states', key, a, a)
            if a['physical_automorphisms'] < a['table_automorphisms']:
                consider('different_named_holdings', key, a, a)
        for a, b in combinations(table.sources, 2):
            if a['state_type_within_table'] != b['state_type_within_table']:
                consider('different_state_types', key, a, b)
                consider('different_named_states', key, a, b)
            if a['physical_type_within_table'] != b['physical_type_within_table']:
                consider('different_physical_types', key, a, b)
                consider('different_named_holdings', key, a, b)
            if a['next_birth_count'] != b['next_birth_count']:
                consider('different_next_birth_counts', key, a, b)
                if a['state_type_within_table'] == b['state_type_within_table']:
                    consider('same_states_different_next_birth_counts', key, a, b)
            if a['next_status'] != b['next_status']:
                consider('different_next_status', key, a, b)
    result = {}
    for label, (rank, key, left, right) in chosen.items():
        if left is right:
            second = within_type_witness(law, left, physical=label == 'different_named_holdings')
        elif label == 'same_states_different_next_birth_counts':
            second = witness_arm(right, map_to_table=state_transport(left, right, law))
        else:
            second = witness_arm(right)
        result[label] = {'least_source_bound': rank[0], 'minimum_order': rank,
                         'table_key': key, 'arms': (witness_arm(left), second)}
    return result


def summarize(law, records, tables):
    by_bound = {bound: counts_at_bound(bound, records, tables) for bound in range(3, 9)}
    table_cases = [{'table_key': key, 'automorphisms': table.automorphisms, **alternatives(table, 8)}
                   for key, table in tables.items()]
    return {'through_source_width': by_bound, 'minima': minima(law, tables), 'tables': table_cases}


def main():
    sources = from_archive()
    summary = {}
    raw = {}
    for law, items in sources.items():
        tables = {}
        records = []
        for n, same_width in groupby(items, key=lambda entry: entry[0]):
            records.extend(reached_case(*source, law, tables) for source in same_width)
            print(law, 'completed source width', n, flush=True)
        raw[law] = records
        summary[law] = summarize(law, records, tables)
        print(law, summary[law]['through_source_width'][8], flush=True)
        print(law, 'minima', {k: v['least_source_bound'] for k, v in summary[law]['minima'].items()}, flush=True)
    OUTPUT.mkdir(exist_ok=True, parents=True)
    (OUTPUT / 'census_summary.json').write_text(json.dumps(summary, indent=2) + '\n')
    (OUTPUT / 'census_cases.json.gz').write_bytes(gzip.compress(json.dumps(raw).encode(), mtime=0))


if __name__ == '__main__':
    main()
