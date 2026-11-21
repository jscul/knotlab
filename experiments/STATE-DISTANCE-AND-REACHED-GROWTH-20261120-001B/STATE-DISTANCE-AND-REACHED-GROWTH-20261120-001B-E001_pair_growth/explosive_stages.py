"""Physical sources and complete globally funded cuts for the five-ring panel."""

from collections import Counter
from hashlib import sha256
from itertools import combinations_with_replacement, product
from math import factorial, prod
from pathlib import Path
from random import Random
import gzip
import json
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = HERE.parent.name
OUTPUT = ROOT / 'artifacts' / TICKET / HERE.name
PRIOR = 'CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C'
sys.path.insert(0, str(ROOT / 'experiments' / PRIOR / f'{PRIOR}-E001_wider_meetings'))
from census_exact_rates import components
from census_stages import LAWS, advance, connected_archive, disjoint_rows, Source, width
from census_replay import check_source
from census_verify_wider import native, replay_allocation


def write(name, payload):
    OUTPUT.mkdir(parents=True, exist_ok=True)
    raw = json.dumps(payload, indent=None, sort_keys=True).encode() + b'\n'
    path = OUTPUT / name
    path.write_bytes(gzip.compress(raw, mtime=0) if path.suffix == '.gz' else raw)


def read(name):
    with gzip.open(OUTPUT / name, 'rt') as stream:
        return json.load(stream)


def indexed_rings():
    """Meetings are indexed by their first holder, with second holder i+1."""
    for meeting, loose in product(product((1, 2), repeat=5), product((2, 3), repeat=5)):
        excess = sum(meeting) - 5
        extra = sum(loose) - 10
        if 1 <= extra and extra + excess <= 2:
            yield meeting, loose


def ring_images(ring):
    meeting, loose = ring
    for start, direction in product(range(5), (1, -1)):
        names = tuple((start + direction * i) % 5 for i in range(5))
        yield tuple(meeting[names[i if direction == 1 else (i + 1) % 5]] for i in range(5)), tuple(loose[i] for i in names)


def ring_source(ring, indexed_multiplicity=None):
    meeting, loose = ring
    rows = [[] for _ in meeting]
    at = 0
    for i, number in enumerate(meeting):
        names = list(range(at, at + number))
        rows[i].extend(names)
        rows[(i + 1) % 5].extend(names)
        at += number
    for row, number in zip(rows, loose, strict=True):
        row.extend(range(at, at + number))
        at += number
    if indexed_multiplicity is None:
        indexed_multiplicity = len(set(ring_images(ring)))
    assert 10 % indexed_multiplicity == 0
    automorphisms = (10 // indexed_multiplicity) * prod(factorial(c) for c in meeting + loose)
    return Source(at, tuple(tuple(sorted(row)) for row in rows), automorphisms)


def stages(source, law):
    old = source
    cuts = []
    # The third turn is read only as the next roster of the second observation.
    for _ in range(3):
        attempt, now, births = advance(old, law)
        replay_status, replay_rows, replay_births = native(old, law)
        assert (attempt, Counter(births)) == (replay_status, Counter(replay_births))
        if attempt == 'births':
            replay_allocation(old, now, replay_rows, births, replay_births)
        cuts.append((attempt, now, births))
        if attempt != 'births':
            break
        old = now
    tentative = []
    limits = [len(source)]
    for age, ((_, now, recorded), (next_status, _, next_births)) in enumerate(zip(cuts, cuts[1:]), start=1):
        limits.append(len(now))
        profile = sorted((tuple(sorted(now[h] for h in parents)), f) for parents, f in next_births)
        tentative.append({'age': age, 'width': width(now), 'rows': now, 'limits': tuple(limits),
                          'births': recorded, 'next_status': next_status, 'next_count': len(next_births),
                          'profile': profile})
    return {'source_rows': source, 'source_width': width(source),
            'attempts': [status for status, _, _ in cuts], 'stages': tentative}


def age_incidence(stage):
    """Colours identify source and the successive cohorts for replay only."""
    rows = stage['rows']
    holder_ages = {i: min(k for k, hi in enumerate(stage['limits']) if i < hi)
                   for i in range(len(rows))}
    graph = nx.Graph()
    for i, row in enumerate(rows):
        graph.add_node(('holder', i), role=('holder', holder_ages[i]))
        for x in row:
            graph.add_node(('name', x), role=('name',))
            graph.add_edge(('holder', i), ('name', x))
    return graph


def align_replay(reference, replay):
    assert (reference['width'], reference['next_count'], reference['next_status']) == (
        replay['width'], replay['next_count'], replay['next_status'])
    mapping = nx.vf2pp_isomorphism(age_incidence(reference), age_incidence(replay), node_label='role')
    assert mapping is not None
    name_map = tuple(mapping['name', x][1] for x in range(reference['width']))
    moved = sorted((tuple(sorted(tuple(sorted(name_map[x] for x in row)) for row in parents)), f)
                   for parents, f in reference['profile'])
    assert moved == replay['profile']
    return name_map


def sources(law, archive, check_legal=True):
    patterns = tuple(indexed_rings())
    counts = Counter(min(ring_images(ring)) for ring in patterns)
    rings = tuple((pattern, ring_source(pattern, count), count) for pattern, count in sorted(counts.items()))
    companions = tuple(source for n in range(3, 6) for source in archive[law][n])
    if check_legal:
        for source in (*(s for _, s, _ in rings), *companions):
            check_source(source.rows, law, source.width)
    physical = []
    ring_ids = {}
    for pattern, source, count in rings:
        ring_ids[pattern] = len(physical)
        physical.append({'family': 'ring', 'parts': (source,), 'ring_pattern': pattern,
                         'indexed_multiplicity': count})
    for (_, a, _), (_, b, _) in combinations_with_replacement(rings, 2):
        physical.append({'family': 'two_rings', 'parts': (a, b)})
    for (_, ring, _), companion in product(rings, companions):
        physical.append({'family': 'small_companion', 'parts': (ring, companion)})
    prepared = []
    for index, item in enumerate(physical):
        parts = item.pop('parts')
        record = stages(disjoint_rows(parts), law)
        assert all(len(group) > 0 for group, _ in components(record['source_rows']))
        aut = prod(p.automorphisms for p in parts) * prod(factorial(c) for c in Counter(parts).values())
        named, remainder = divmod(factorial(record['source_width']), aut)
        assert remainder == 0
        prepared.append(dict(id=index, part_widths=[p.width for p in parts],
                             named_source_multiplicity=named, **item, **record))
    return patterns, ring_ids, prepared


def fresh(law, patterns, ring_ids, source_records):
    digest = sha256(f'{TICKET}|{law}|explosive|fresh6438'.encode()).hexdigest()
    random = Random(int(digest, 16))
    samples = []
    for index in range(1, 65):
        pattern = random.choice(patterns)
        base = ring_source(pattern)
        renaming = list(range(base.width))
        random.shuffle(renaming)
        rows = tuple(tuple(sorted(renaming[i] for i in row)) for row in base.rows)
        target = stages(rows, law)
        source_id = ring_ids[min(ring_images(pattern))]
        reference = source_records[source_id]
        assert reference['attempts'] == target['attempts']
        for a, b in zip(reference['stages'], target['stages'], strict=True):
            b['canonical_source_stage_transport'] = align_replay(a, b)
        samples.append(dict(draw=index, indexed_pattern=pattern, permutation=renaming, source_id=source_id, **target))
    return {'seed_sha256': digest, 'draws': samples}


def physical_summary(records):
    families = Counter(r['family'] for r in records)
    widths = {str(age): dict(sorted(Counter(stage['width'] for r in records for stage in r['stages']
                                            if stage['age'] == age).items())) for age in (1, 2)}
    next_outcomes = {str(age): dict(sorted(Counter(f"{s['next_status']}:{s['next_count']}" for r in records
                                                   for s in r['stages'] if s['age'] == age).items()))
                     for age in (1, 2)}
    attempts = Counter('/'.join(r['attempts']) for r in records)
    max_width = max(int(v) for by_age in widths.values() for v in by_age)
    return dict(families=families, widths=widths, next_outcomes=next_outcomes,
                attempts=attempts, max_width=max_width)


def main():
    archive = connected_archive()
    output = {}
    for law in LAWS:
        indexed, ring_ids, records = sources(law, archive)
        summary = physical_summary(records)
        output[law] = {'sources': records, 'indexed_ring_count': len(indexed), 'physical': summary,
                       'samples': fresh(law, indexed, ring_ids, records)}
        print(law, summary, flush=True)
    write('explosive_stages.json.gz', output)


if __name__ == '__main__':
    main()
