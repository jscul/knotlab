"""Reconcile the independent audit lanes and bind the final deliverables.

Checks only the requested scientific surface. No producer Python is read.
"""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import itertools
import json
from pathlib import Path
import resource
import sys
import time

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
from recompute_census import build, incidence_analysis, shortest_levels, descending_reach


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def read(name):
    return json.loads((HERE / name).read_text())


def main():
    started = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (2300 * 1024**2, 2300 * 1024**2))
    census = read('census.json')
    assert census['processed'] == 1288
    assert census['acyclic_descriptions'] == 546
    assert census['cyclic_descriptions'] == 742
    assert not census['acyclic_outcome_mismatches']
    assert not census['acyclic_paths_without_descending_chain']
    expected = {
        ('chained', 'acyclic, chains at every s'): 299,
        ('chained', 'cyclic'): 158,
        ('no bond', 'acyclic, some s without a chain'): 170,
        ('no bond', 'cyclic'): 18,
        ('no join', 'acyclic, some s without a chain'): 77,
        ('no join', 'cyclic'): 106,
        ('direct', 'cyclic'): 100, ('other', 'cyclic'): 73,
        ('undecided', 'cyclic'): 264, ('dead', 'cyclic'): 23,
    }
    assert {(r['outcome'], r['structure']): r['count'] for r in census['cross_tab']} == expected
    assert census['ruler_shares'] == {
        'rulers': 457, 'ruler_weight': 605, 'acyclic_at_N9': 299,
        'acyclic_at_N9_weight': 394, 'theorem_a_all_depths': 117,
        'theorem_a_all_depths_weight': 221,
    }
    assert census['all_description_weight'] == 1423

    forest = read('forest_audit/results.json')
    assert forest['exhaustive']['counts']['forests'] == 1156
    assert forest['exhaustive']['counts']['pairs'] == 24276
    assert not forest['exhaustive']['violations']
    for field in ('T1_violations', 'level_formula_violations', 'chain_equivalence_violations'):
        assert forest['random'][field] == 0
    assert forest['random_exact_engine_crosschecks']['level_queries'] == 423
    assert not forest['random_exact_engine_crosschecks']['failures']

    tree = read('tree_audit/structural.json')['result']
    assert tree['descriptions'] == 120 and tree['patterns'] == 840 and tree['all_pass']
    exact = read('tree_audit/exact.json')['result']
    assert exact['searches'] == 24 and exact['undecided'] == 0 and exact['all_decided_agree']
    assert {r['N'] for r in exact['rows']} == {6, 7}
    assert all(r['search']['exact'] and r['search']['L'] == r['s'] + 2
               and r['fresh_brute_projection_check'] for r in exact['rows'])

    # The lead reruns the decisive missing-case counterexample itself.
    from fresh_search import search, levels
    detour = [(1, 3, 4), (3, 5, 6), (5, 7, 8)]
    assert incidence_analysis(detour, 15)['acyclic']
    assert shortest_levels(detour, 15, 1, [3])[0]['distance'] == 3
    assert not descending_reach(detour, 1, 2)[1]
    A, B = levels(1, 2)
    detour_search = search(detour, 15, A, B, cap=5, seconds=20)
    assert detour_search['exact'] and detour_search['L'] == 5

    # Bind retained certificates to independently rebuilt, deduplicated knots,
    # then recheck all proofs and every proper-projection model in the lead.
    spec = importlib.util.spec_from_file_location('audit_certificate_checker', HERE / 'breaking_audit/check_certificates.py')
    checker = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(checker)
    breaking = read('breaking_audit/summary.json')
    assert breaking['reported_breaks'] == 6 and breaking['serialized_inputs'] == 5
    assert breaking['all_five_claimed_vectors_match'] and breaking['all_five_have_actual_tree_siblings']
    assert breaking['missing_input'] == {'profile': [3, 3, 4], 'log_line': 64, 'key_present': False}
    profiles = []
    certificate_count = model_count = 0
    for number in range(1, 6):
        case = read(f'breaking_audit/case_{number}.json')
        knots = build(case['key'], 6)
        assert [list(k) for k in knots] == case['knots']
        profiles.append([r['L'] for r in case['levels']])
        assert profiles[-1] == case['claimed_L']
        base = checker.clauses(knots)
        for row in case['levels']:
            assert row['exact']
            cert = row['certificate']
            support = cert['support']
            assert len(support) == row['L']
            assert set(support) & set(row['A']) and set(support) & set(row['B'])
            units = [[v+1 if b else -v-1] for v, b in zip(support, cert['forbidden_assignment'])]
            proof = HERE / f"breaking_audit/case_{number}_s{row['s']}.drup"
            assert checker.check_proof(base + units, proof.read_text().splitlines())[0]
            expected_models = {(v, tuple(x for x in support if x != v), bits)
                               for v in support for bits in itertools.product((0, 1), repeat=len(support)-1)}
            observed_models = set()
            for model in cert['maximal_proper_projection_models']:
                values = model['model']
                assert len(values) == 127 and set(values) <= {0, 1}
                assert all(len({values[v] for v in knot}) == 2 for knot in knots)
                assert all(values[v] == b for v, b in zip(model['support'], model['assignment']))
                observed_models.add((model['removed'], tuple(model['support']), tuple(model['assignment'])))
                model_count += 1
            assert observed_models == expected_models
            certificate_count += 1
    assert certificate_count == 15 and model_count == 256

    checked_sources = {}
    for metadata in [forest, read('tree_audit/audit_summary.json'), breaking,
                     *(read(f'tree_audit/{name}.json') for name in ('structural', 'exact', 'controls', 'smoke'))]:
        for source, sha in metadata.get('source_sha256', {}).items():
            assert digest(ROOT / source) == sha, source
            checked_sources[source] = sha
    checked_sources.update(census['input_sha256'])
    for source, sha in checked_sources.items():
        assert digest(ROOT / source) == sha

    # Remove only the lead's superseded smoke output, which is not evidence.
    scratch = HERE / 'census_smoke.json'
    if scratch.exists():
        scratch.unlink()
    scripts = []
    json_files = []
    for path in sorted(HERE.rglob('*')):
        if path.is_file() and path.suffix == '.py':
            ast.parse(path.read_text(), filename=str(path))
            scripts.append(str(path.relative_to(HERE)))
        if path.is_file() and path.suffix == '.json' and path.name != 'audit_manifest.json':
            json.loads(path.read_text())
            json_files.append(str(path.relative_to(HERE)))
    exclude = {'brief_codex.md', 'codex_last_message.md', 'audit_manifest.json'}
    files = {str(p.relative_to(HERE)): {'sha256': digest(p), 'bytes': p.stat().st_size}
             for p in sorted(HERE.rglob('*')) if p.is_file() and p.name not in exclude}
    manifest = {
        'verdict': 'Confirmed with fixes',
        'scope_id': 'RULER-LEVEL-20261114-001',
        'provenance': 'V2 relative to producer; prior independent referee algorithms reused; same-task AI reviews, no external replication',
        'census': {k: v for k, v in census.items() if k not in ('rows', 'controls')},
        'lead_decisive_counterexample': detour_search,
        'lead_rechecked_breaking_profiles': profiles,
        'lead_rechecked_RUP_certificates': certificate_count,
        'lead_rechecked_proper_projection_models': model_count,
        'missing_sixth_input': breaking['missing_input'],
        'current_source_hashes_verified': checked_sources,
        'syntax_checked_scripts': scripts, 'parsed_json_files': json_files,
        'files_written': files,
        'elapsed_seconds': time.monotonic() - started,
        'peak_rss_MiB': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024,
        'restrictions': {'network_used': False, 'prohibited_producer_python_used': False,
                         'git_mutations': False, 'publishing': False,
                         'all_writes_within_designated_referee_directory': True},
    }
    (HERE / 'audit_manifest.json').write_text(json.dumps(manifest, indent=2) + '\n')
    print(json.dumps({'passed': True, 'scripts_parsed': len(scripts), 'json_files_parsed': len(json_files),
                      'certificates': certificate_count, 'models': model_count,
                      'files_retained': len(files), 'seconds': manifest['elapsed_seconds']}))


if __name__ == '__main__':
    main()
