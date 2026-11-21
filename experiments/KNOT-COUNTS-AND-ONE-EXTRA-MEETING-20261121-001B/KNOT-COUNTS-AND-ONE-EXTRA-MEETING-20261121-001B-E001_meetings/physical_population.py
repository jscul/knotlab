"""Exact four-cut physical population of decorated simple one-cycle founders."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import combinations
from math import comb, factorial
from pathlib import Path
from tempfile import NamedTemporaryFile
import gzip
import json
import os
import sys

import networkx as nx


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAF = HERE.parent.name
OUT = ROOT / 'artifacts' / LEAF / HERE.name
PRIOR = 'IDLE-PHASE-AND-TREE-CLOSURE-20261121-001B'
sys.path.insert(0, str(ROOT / 'experiments' / PRIOR / f'{PRIOR}-E001_trees'))
from representatives import shape_representatives
from representatives_audit import decoded, relabel
from representatives_growth import grow
from census_exact_rates import owners
from panels_sources import founder_check, width


LAWS = ('parity', 'nae')
SIZES = (6, 7, 8)


def edge_list(graph):
    return tuple(sorted(tuple(sorted(pair)) for pair in graph.edges()))


def uncoloured(n):
    buckets = defaultdict(list)
    raw_paths = 0
    for source in nx.nonisomorphic_trees(n):
        labelled = nx.convert_node_labels_to_integers(source, ordering='sorted')
        for a, b in combinations(range(n), 2):
            if labelled.has_edge(a, b):
                continue
            raw_paths += 1
            graph = labelled.copy()
            graph.add_edge(a, b)
            cycle, = nx.cycle_basis(graph)
            l = len(cycle)
            fingerprint = (l, tuple(sorted(d for _, d in graph.degree())))
            if not any(nx.is_isomorphic(graph, h) for h in buckets[fingerprint]):
                buckets[fingerprint].append(graph)
    found = [(key[0], g) for key, bucket in buckets.items() for g in bucket]
    return sorted(found, key=lambda t: (t[0], edge_list(t[1]))), raw_paths


def labelled_by_cycle(n, l):
    cyclic_orders = factorial(l - 1) // 2
    attachments = 1 if l == n else l * n ** (n - l - 1)
    return comb(n, l) * cyclic_orders * attachments


def projection_premise(graph):
    evidence = []
    for erased in sorted(graph):
        parts = []
        for members in nx.connected_components(graph.subgraph(set(graph) - {erased})):
            chosen = next(v for v in sorted(members) if graph.degree(v) <= 2)
            parts.append({'other_holders': tuple(sorted(members)), 'holder_with_a_private_name': chosen})
        evidence.append({'fixed_holder': erased, 'remaining_components': parts})
    return evidence


def check_named_founder(case, graph):
    rows = case['founder_rows']
    holding = owners(rows)
    assert tuple(sorted(v for v in holding.values() if len(v) == 2)) == case['edges'] == edge_list(graph)
    assert set(holding) == set(range(width(rows)))
    for h, (row, extra) in enumerate(zip(rows, case['extra'], strict=True)):
        assert len(row) >= 3
        loose = sum(len(holding[x]) == 1 for x in row)
        assert loose == max(0, 3 - graph.degree(h)) + extra


def literal_founder(rows):
    template = {'source_rows': rows, 'before_permutation': rows,
                'source_name_permutation': tuple(range(width(rows))),
                'source_holder_order_to_original': tuple(range(len(rows)))}
    check = {law: founder_check(template, law) for law in LAWS}
    assert all(v['lawful'] and v['essential'] for v in check.values())
    return check


def collect_outcomes(case, counts, examples):
    for law, m in case['laws'].items():
        ledger = decoded(case['founder_rows'], m)
        n = case['n']
        counts['funded_cuts'][law] += len(m['cuts'])
        counts['births'][law] += sum(len(c['births']) for c in m['cuts'])
        counts['largest_holders'][law] = max(counts['largest_holders'][law], len(ledger[-1]))
        counts['largest_distinctions'][law] = max(counts['largest_distinctions'][law], width(ledger[-1]))
        ending = (law, m['termination'], m['age'], m['terminal_arity'], m['positive'])
        counts['outcomes'][ending] += 1
        counts['distinct_mass_by_outcome'][ending] += case['mass_distinct']
        counts['edited_mass_by_outcome'][ending] += case['mass_edited']
        if m['terminal_arity'] is not None:
            assert m['terminal'] and law == 'parity'
            key = (n, case['cycle_length'], m['age'], m['terminal_arity'], m['positive'])
            examples['signed'].setdefault(key, case)
            case['independent_founder_lawfulness'] = literal_founder(case['founder_rows'])
            counts['literal_two_law_founder_gates'] += 1
            counts['pauli_incidence_agreement'] += 1
        certain = examples['by_size'].get((n, law))
        if certain is None or (not certain['laws'][law]['cuts'] and m['cuts']):
            examples['by_size'][n, law] = case


def empty_summary(n, delta):
    return {'n': n, 'raw_tree_edit_shape_paths': delta, 'simple_shapes_by_cycle': Counter(),
            'classes_by_cycle_and_flags': Counter(), 'labelled_holdings_by_cycle_and_flags': Counter(),
            'labelled_prior_histories_by_cycle_and_flags': Counter(), 'distinct_mass_by_cycle': Counter(),
            'edited_mass_by_cycle': Counter(), 'outcomes': Counter(), 'distinct_mass_by_outcome': Counter(),
            'edited_mass_by_outcome': Counter(), 'funded_cuts': Counter(), 'births': Counter(),
            'largest_holders': Counter(), 'largest_distinctions': Counter(), 'literal_two_law_founder_gates': 0,
            'pauli_incidence_agreement': 0}


def verify_mass(counts):
    n = counts['n']
    for l in range(3, n + 1):
        u = labelled_by_cycle(n, l)
        assert counts['distinct_mass_by_cycle'][l] == u * 4 ** n
        assert counts['edited_mass_by_cycle'][l] == l * u * 4 ** n
        for k in range(n + 1):
            assert counts['labelled_holdings_by_cycle_and_flags'][l, k] == u * comb(n, k)
            assert counts['labelled_prior_histories_by_cycle_and_flags'][l, k] == l * u * comb(n, k)
    prior_trees = n ** (n - 2) * (comb(n, 2) - (n - 1))
    assert sum(counts['edited_mass_by_cycle'].values()) == prior_trees * 4 ** n
    return counts


def represent_size(n, emit, examples):
    shapes, delta = uncoloured(n)
    counts = empty_summary(n, delta)
    projection_certificates = []
    for l, graph in shapes:
        counts['simple_shapes_by_cycle'][l] += 1
        projection_certificates.append({'edges': edge_list(graph), 'cycle_length': l,
                                        'source_projection_premise': projection_premise(graph)})
        for case in shape_representatives(n, graph):
            k = sum(case['extra'])
            case['cycle_length'] = l
            case['mass_distinct'] = case['mass']
            case['mass_edited'] = l * case['mass']
            counts['classes_by_cycle_and_flags'][l, k] += 1
            counts['labelled_holdings_by_cycle_and_flags'][l, k] += case['labelled']
            counts['labelled_prior_histories_by_cycle_and_flags'][l, k] += l * case['labelled']
            counts['distinct_mass_by_cycle'][l] += case['mass_distinct']
            counts['edited_mass_by_cycle'][l] += case['mass_edited']
            check_named_founder(case, graph)
            case['laws'] = {law: grow(case['founder_rows'], law) for law in LAWS}
            collect_outcomes(case, counts, examples)
            emit(case)
    verify_mass(counts)
    print(n, len(shapes), sum(counts['classes_by_cycle_and_flags'].values()), dict(counts['outcomes']),
          dict(counts['largest_holders']), dict(counts['largest_distinctions']), flush=True)
    counts['projection_certificates'] = projection_certificates
    return counts


def audit_ready(summary, controls, path):
    by_size = []
    for results in summary:
        cleaned = {}
        for key, reading in results.items():
            if isinstance(reading, Counter) and any(isinstance(k, tuple) for k in reading):
                cleaned[key] = [[list(key), count] for key, count in reading.items()]
            else:
                cleaned[key] = reading
        by_size.append(cleaned)
    return {'record_file': path.name, 'sha256': sha256(path.read_bytes()).hexdigest(),
            'size_summaries': by_size, 'named_relabel_checks': controls}


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    final = OUT / 'physical_population.json.gz'
    examples = {'by_size': {}, 'signed': {}}
    summaries = []
    with NamedTemporaryFile(dir=OUT, prefix='.physical_population.', delete=False) as scratch:
        try:
            with gzip.GzipFile(filename='', fileobj=scratch, mode='wb', mtime=0) as stream:
                stream.write(b'[\n')
                already = False

                def emit(row):
                    nonlocal already
                    if already:
                        stream.write(b',\n')
                    already = True
                    stream.write(json.dumps(row, sort_keys=True, separators=(',', ':')).encode())

                for n in SIZES:
                    summaries.append(represent_size(n, emit, examples))
                stream.write(b'\n]\n')
            scratch.flush()
            os.replace(scratch.name, final)
        finally:
            if os.path.exists(scratch.name):
                os.unlink(scratch.name)
    selected = {(r['id'], law): r for (_, law), r in examples['by_size'].items()}
    for r in examples['signed'].values():
        for law in LAWS:
            selected[r['id'], law] = r
    controls = [relabel(case, law) for (_, law), case in sorted(selected.items())]
    audit = audit_ready(summaries, controls, final)
    (OUT / 'physical_audit.json').write_text(json.dumps(audit, sort_keys=True, separators=(',', ':')) + '\n')
    print('complete', final.name, 'relabel replays', len(controls), flush=True)


if __name__ == '__main__':
    main()
