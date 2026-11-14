"""Bounded independent TOP-INFO R1 replay; one process and no network.

Run controls, pinning census subsets, or the nine new whole-main windows.
Every result is written immediately as JSONL inside this referee directory.
"""
from __future__ import annotations

import argparse
import collections
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
from pathlib import Path
import resource
import sys
import time

import pinning_window_core as c

EXP = Path('experiments/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/codex')
CENSUS = Path('artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz')


def population():
    data = c.read_json(EXP / 'results.json')['families']
    keys = {x['key'] for x in data}
    raw = (c.ROOT / CENSUS).read_bytes()
    c.READS[str(CENSUS)] = hashlib.sha256(raw).hexdigest()
    census = {}
    for line in gzip.decompress(raw).splitlines():
        row = json.loads(line)
        if row['key'] in keys:
            census[row['key']] = row
    return data, census


def write_record(stem, record):
    with (c.HERE / (stem + '.jsonl')).open('a') as handle:
        handle.write(json.dumps(record, separators=(',', ':')) + '\n')


def meta():
    return {'forbidden_TOP_python_opened_or_imported': False,
            'processes': 1, 'parallelism': False,
            'validation': 'V2 independently authored same-task AI referee; permitted older referee algorithms reused; no external replication',
            'sources': c.READS,
            'scripts': {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in
                        (c.HERE / 'pinning_window_core.py', c.HERE / 'pinning_window_audit.py')},
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def controls():
    started = time.monotonic()
    hiding_rows = []
    for ports in range(16):
        if ports in (0, 15):
            continue
        for x in (0, 1):
            # p,q,r,t are little-endian; 0011/1100 remain a complement pair.
            if (ports, x) not in ((12, 1), (3, 0)):
                hiding_rows.append(ports | (x << 4))
    hiding = c.Relation(tuple(range(5)), sum(1 << x for x in hiding_rows))
    check = hiding.pinning(range(4), (4,))
    assert check['plain_pinned'] and not check['bond_pinned']
    cross_bonds = []
    for size in range(1, 6):
        for support in itertools.combinations(range(5), size):
            if 4 in support and not hiding.shattered(support) and all(
                    hiding.shattered(support[:j] + support[j + 1:]) for j in range(size)):
                cross_bonds.append(support)
    assert len(hiding_rows) == 26 and not cross_bonds
    triples_x = [hiding.shattered(triple + (4,)) for triple in itertools.combinations(range(4), 3)]
    assert all(triples_x)

    exhaustive = 0
    # Every nonempty complement-closed relation on four distinctions: compare
    # the shattered-side statement directly with exhaustive cross bonds.
    for mask in range(1, 256):
        rows = [s for s in range(16) if (mask >> min(s, 15 ^ s)) & 1]
        rel = c.Relation(tuple(range(4)), sum(1 << s for s in rows))
        predicate = False
        for a in range(1, 4):
            T = tuple(j for j in range(2) if (a >> j) & 1)
            if not rel.shattered(T):
                continue
            for b in range(1, 4):
                D = tuple(2 + j for j in range(2) if (b >> j) & 1)
                if rel.shattered(D) and not rel.shattered(T + D):
                    predicate = True
        cross = rel.pinning((0, 1), (2, 3))['bond_pinned']
        assert cross == predicate
        exhaustive += 1

    fixtures = [
        ('main_S_own_carried', [[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 3, 3]]]]], 0),
        ('wrapper_own_carried', [[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 1, 3]]]],
                                  [3, 1, [['K', [0, 2, 3]], [0, [0, 3, 1]], [0, [1, 2, 3]]]]], 0),
        ('wrapper_start_constraints', [[3, 1, [['K', [0, 1, 3]], ['SELF', [0, 1, 3]]]],
                                         [3, 1, [['K', [0, 1, 3]], [0, [0, 1, 3]]]]], 0),
    ]
    fixture_results = []
    for name, raw, S in fixtures:
        w = c.WholeMain(raw, S)
        current = dict(w.starts)
        checks = []
        for _ in range(3):
            for q, path in current.items():
                checks.append(c.direct_check(w, q, path, explicit=True))
            following = {}
            for q, (entry, word) in current.items():
                for label in range(len(w.generators)):
                    following.setdefault(w.step(q, label), (entry, word + (label,)))
            current = following
        fixture_results.append({'name': name, 'raw': raw, 'S': S, 'checks': checks})

    # Wrong identity control: a repeated main-own argument is one distinction.
    w = c.WholeMain(fixtures[0][1], 0)
    q, path = next(iter(w.starts.items()))
    direct = c.Unfold(w, *path, explicit=True)
    assert direct.target[1] == direct.target[2] == 3
    with c.Solver(name='cadical195', bootstrap_with=direct.clauses) as solver:
        repeated = c.old.sat_projection(solver, (3, direct.target[1]))
        merged = c.old.sat_projection(solver, (3,))
        rejected = False
        try:
            c.old.verify_bond(solver, (3, direct.target[1]))
        except ValueError:
            rejected = True
    assert repeated == 0b1001 and merged == 0b11 and rejected

    # Wrong start control: erase the wrapper's K while retaining the child.
    raw = fixtures[2][1]
    correct = c.WholeMain(raw, 0)
    wrong_raw = json.loads(json.dumps(raw))
    wrong_raw[-1][2] = [x for x in wrong_raw[-1][2] if x[0] != 'K']
    wrong = c.WholeMain(wrong_raw, 0)
    cq, cp = next(iter(correct.starts.items()))
    wq = next(iter(wrong.starts))
    cl, cr = correct.relation(cq)
    wl, wr = wrong.relation(wq)
    assert cl == wl and cr != wr
    direct = c.Unfold(correct, *cp, explicit=True)
    mapping = correct.mapping(cq, direct.target)
    with c.Solver(name='cadical195', bootstrap_with=direct.clauses) as solver:
        actual = c.old.sat_projection(solver, tuple(mapping[x] for x in cl))
    assert actual == cr and actual != wr
    result = {'hiding': {'rows': hiding_rows, **check, 'cross_bonds': [],
                          'all_three_ports_with_x_full': triples_x},
              'Pprime_equivalence_exhaustive_four_distinction_relations': exhaustive,
              'fixtures': fixture_results,
              'wrong_identity_control': {'repeated_relation': [0, 3], 'merged_relation': [0, 1],
                                         'spurious_repeated_identity_bond_rejected': rejected},
              'wrong_start_control': {'correct_count': cr.bit_count(), 'wrong_count': wr.bit_count(),
                                      'wrong_start_rejected_by_raw_CNF': actual != wr},
              'seconds': time.monotonic() - started, **meta()}
    (c.HERE / 'pinning_window_results_controls.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'controls_passed': True, 'exhaustive_relations': exhaustive,
                      'fixture_projections': sum(len(x['checks']) for x in fixture_results),
                      'seconds': result['seconds']}), flush=True)


def pinning_record(rec, census):
    started = time.monotonic()
    w = c.old.Window(json.loads(rec['key']), census['S'])
    orb = c.orbit(w)
    pre, period = orb['preperiod'], orb['period']
    theirs = rec['pinning']
    assert (pre, period) == (theirs['preperiod'], theirs['period'])
    cache, phases = {}, []
    for phase, states in enumerate(orb['levels'][pre:]):
        for q in states:
            if q not in cache:
                labels, allowed = w.relation(q)
                rel = c.Relation(labels, allowed)
                roots = [j for j, label in enumerate(labels) if label < w.km]
                target = [j for j, label in enumerate(labels) if label >= w.km + 3]
                cache[q] = rel.pinning(roots, target)
        values = [cache[q] for q in states]
        row = {'phase': phase, 'word_s_mod_period': (pre + phase) % period,
               'absolute_depth_mod_period': (pre + phase + int(w.wrapper)) % period,
               'states': len(states),
               'plain_pinned': any(x['plain_pinned'] for x in values),
               'bond_pinned': any(x['bond_pinned'] for x in values),
               'pinned_states': sum(x['plain_pinned'] for x in values),
               'bond_pinned_states': sum(x['bond_pinned'] for x in values),
               'all_paths_plain_pinned': all(x['plain_pinned'] for x in values)}
        expected = next(x for x in theirs['residues'] if x['word_s_mod_period'] == row['word_s_mod_period'])
        for field in ('states', 'plain_pinned', 'bond_pinned', 'pinned_states', 'bond_pinned_states'):
            assert row[field] == expected[field], (rec['key_sha256'][:12], field, row, expected)
        phases.append(row)
    coarse_period = rec['R']['carried_period']
    coarse = []
    for residue in range(coarse_period):
        compatible = [x for x in phases if (x['word_s_mod_period'] - residue) % math.gcd(period, coarse_period) == 0]
        coarse.append({'carried_period': coarse_period, 'word_residue': residue,
                       'infinitely_many_plain_pinned_depths': any(x['plain_pinned'] for x in compatible),
                       'every_large_depth_plain_pinned': all(x['plain_pinned'] for x in compatible),
                       'infinitely_many_bond_pinned_depths': any(x['bond_pinned'] for x in compatible),
                       'every_large_depth_bond_pinned': all(x['bond_pinned'] for x in compatible)})
    return {'key_sha256': rec['key_sha256'], 'key': rec['key'], 'S': census['S'],
            'stratum': rec['stratum'], 'final_verdict': rec['final_verdict'],
            'wrapper': w.wrapper, 'preperiod': pre, 'period': period,
            'absolute_periodic_threshold': pre + int(w.wrapper),
            'unique_repeating_states': len(cache), 'phases': phases,
            'coarse_residue_quantifiers': coarse, 'all_producer_phase_flags_match': True,
            'plain_bond_difference_states': sum(x['plain_pinned'] != x['bond_pinned'] for x in cache.values()),
            'seconds': time.monotonic() - started}


def pinning(mode, limit=None):
    started = time.monotonic()
    data, census = population()
    if mode == 'growers':
        selected = [r for r in data if r['in_scope'] and r['final_verdict'] == 'growing']
    elif mode == 'orders':
        selected = [r for r in data if r['in_scope'] and r['stratum'] == 'O']
    else:
        candidates = [r for r in data if r['in_scope'] and r['stratum'] == 'I'
                      and r['pinning'].get('complete') and r['final_verdict'] != 'growing']
        selected = sorted(candidates, key=lambda r: hashlib.sha256(('R1PIN:' + r['key']).encode()).hexdigest())[:24]
        special = [r for r in candidates if r['pinning']['period'] > 1]
        selected += sorted(special, key=lambda r: (-r['pinning']['period'], census[r['key']]['s_block_size'], r['key_sha256']))[:8]
        selected = list({r['key']: r for r in selected}.values())
    selected.sort(key=lambda r: (census[r['key']]['s_block_size'], r['key_sha256']))
    if limit is not None:
        selected = selected[:limit]
    stem = 'pinning_window_results_' + mode
    (c.HERE / (stem + '.jsonl')).write_text('')
    results = []
    for i, rec in enumerate(selected):
        result = pinning_record(rec, census[rec['key']])
        write_record(stem, result)
        results.append(result)
        if i < 3 or (i + 1) % 25 == 0:
            print(json.dumps({'mode': mode, 'done': i + 1, 'total': len(selected),
                              'sha': rec['key_sha256'][:12], 'seconds': result['seconds']}), flush=True)
    summary = {'mode': mode, 'families': len(results), 'all_producer_phase_flags_match': True,
               'plain_bond_difference_states': sum(r['plain_bond_difference_states'] for r in results),
               'unique_repeating_states': sum(r['unique_repeating_states'] for r in results),
               'periodic_phases': sum(len(r['phases']) for r in results),
               'families_plain_pinned_every_phase': sum(all(p['plain_pinned'] for p in r['phases']) for r in results),
               'families_bond_pinned_every_phase': sum(all(p['bond_pinned'] for p in r['phases']) for r in results),
               'grower_pinned_violations': [r['key_sha256'] for r in results if r['final_verdict'] == 'growing'
                                           and any(p['plain_pinned'] or p['bond_pinned'] for p in r['phases'])],
               'coarse_weak_strong_disagreements': [r['key_sha256'] for r in results if any(
                   x['infinitely_many_plain_pinned_depths'] != x['every_large_depth_plain_pinned'] or
                   x['infinitely_many_bond_pinned_depths'] != x['every_large_depth_bond_pinned']
                   for x in r['coarse_residue_quantifiers'])],
               'seconds': time.monotonic() - started, **meta()}
    (c.HERE / (stem + '.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('sources', 'scripts')}), flush=True)


def winner(w, states):
    candidates = [(w.least_bond(q)['size'], q, path, w.least_bond(q)['support'])
                  for q, path in states.items() if w.least_bond(q)['size'] is not None]
    return min(candidates, key=lambda x: (x[0], x[1])) if candidates else None


def at_depth(w, depth):
    current = dict(w.starts)
    for _ in range(depth - w.start_depth):
        following = {}
        for q, (entry, word) in current.items():
            for label in range(len(w.generators)):
                following.setdefault(w.step(q, label), (entry, word + (label,)))
        current = following
    return current


def two_block_record(rec, census, full_projection=True):
    started = time.monotonic()
    w = c.WholeMain(json.loads(rec['key']), census['S'])
    orb = c.orbit(w)
    pre = orb['preperiod'] + w.start_depth
    period = orb['period']
    theirs = rec['two_block']
    assert (pre, period) == (theirs['preperiod'], theirs['period']), (pre, period, theirs['preperiod'], theirs['period'])
    levels = []
    for i, states in enumerate(orb['levels']):
        best = winner(w, states)
        row = {'word_depth': i + w.start_depth, 'states': len(states), 'U2': best[0] if best else '> 6'}
        expected = next(x for x in theirs['levels'] if x['s'] == row['word_depth'])
        assert (row['states'], row['U2']) == (expected['states'], expected['U2']), (rec['key_sha256'][:12], row, expected)
        levels.append(row)
    maximum = max(x['U2'] for x in levels[orb['preperiod']:] if isinstance(x['U2'], int))
    assert all(isinstance(x['U2'], int) for x in levels[orb['preperiod']:])
    assert maximum == theirs['maximum']
    # At least two complete eventual periods, and an early representative.
    depths = sorted(set([max(w.start_depth, 1), 2, 3] + list(range(pre, pre + 2 * period))))
    checks = []
    for depth in depths:
        states = at_depth(w, depth)
        best = winner(w, states)
        if best is None:
            continue
        size, q, path, support = best
        checks.append(c.direct_check(w, q, path, support, explicit=False,
                                     compare=full_projection))
    # Full branching is separately unfolded at word lengths one and two.
    explicit_checks = []
    for depth in (max(w.start_depth, 1), 2):
        states = at_depth(w, depth)
        best = winner(w, states)
        if best is None:
            continue
        size, q, path, support = best
        explicit_checks.append(c.direct_check(w, q, path, support, explicit=True,
                                              compare=full_projection))
    return {'key_sha256': rec['key_sha256'], 'key': rec['key'], 'S': census['S'],
            'wrapper': w.wrapper, 'main_block_size': w.main_size, 'S_block_size': w.size,
            'preperiod': pre, 'period': period, 'absolute_periodic_threshold': pre + int(w.wrapper),
            'maximum': maximum, 'levels': levels, 'all_producer_levels_match': True,
            'states_with_main_own_carried': sum(any(w.km <= x < w.width for x in q[1][w.width:])
                                                for q in w.bonds),
            'unique_states_checked': len(w.bonds), 'direct_checks': checks,
            'explicit_checks': explicit_checks, 'seconds': time.monotonic() - started,
            'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}


def two_block(limit=None, select=None):
    started = time.monotonic()
    data, census = population()
    selected = [r for r in data if r['in_scope'] and r['final_verdict'] == 'undecided'
                and r['two_block'].get('complete') and r['two_block'].get('verdict') == 'bounded']
    assert len(selected) == 9
    selected.sort(key=lambda r: (r['two_block']['top_width'] + r['two_block']['end_width'], r['key_sha256']))
    if select:
        selected = [r for r in selected if r['key_sha256'].startswith(select)]
    if limit:
        selected = selected[:limit]
    stem = 'pinning_window_results_twoblock' + ('_' + select if select else '')
    (c.HERE / (stem + '.jsonl')).write_text('')
    results = []
    for index, rec in enumerate(selected):
        result = two_block_record(rec, census[rec['key']])
        write_record(stem, result)
        results.append(result)
        print(json.dumps({'done': index + 1, 'sha': rec['key_sha256'][:12],
                          'bound': result['maximum'], 'preperiod': result['preperiod'],
                          'period': result['period'], 'states': result['unique_states_checked'],
                          'seconds': result['seconds']}), flush=True)
    summary = {'families': len(results), 'all_producer_levels_match': True,
               'direct_bonds': sum(len(r['direct_checks']) for r in results),
               'explicit_bonds': sum(len(r['explicit_checks']) for r in results),
               'projection_assignments': sum(x['full_projection_assignments'] for r in results
                                               for x in r['direct_checks'] + r['explicit_checks']),
               'all_bound_four': all(r['maximum'] == 4 for r in results),
               'seconds': time.monotonic() - started, **meta()}
    (c.HERE / (stem + '.json')).write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('sources', 'scripts')}), flush=True)


def hiding():
    started = time.monotonic()
    data, census = population()
    rec = next(r for r in data if r['key_sha256'].startswith('aab77be157e5'))
    w = c.old.Window(json.loads(rec['key']), census[rec['key']]['S'])
    orb = c.orbit(w)
    interesting = {}
    for states in orb['levels'][orb['preperiod']:]:
        for q, path in states.items():
            labels, allowed = w.relation(q)
            positions = tuple(j for j, x in enumerate(labels) if x < w.km or x >= w.km + 3)
            joint_labels = tuple(labels[j] for j in positions)
            joint = c.project_mask(allowed, positions)
            relation = c.Relation(joint_labels, joint)
            roots = [j for j, x in enumerate(joint_labels) if x < w.km]
            target = [j for j, x in enumerate(joint_labels) if x >= w.km + 3]
            info = relation.pinning(roots, target)
            if info['plain_pinned'] and not info['bond_pinned']:
                interesting.setdefault(q, (path, labels, allowed, joint_labels, joint, info))
    assert len(interesting) == 2
    records = []
    for q, (path, labels, expected, joint_labels, joint, info) in interesting.items():
        entry, word = path
        direct = c.old.DirectCNF(w)
        target_env = direct.all_copies(entry, word, len(word))
        mapping = c.old.label_actuals(w, q, target_env)
        with c.Solver(name='cadical195', bootstrap_with=direct.clauses) as solver:
            projected = c.old.sat_projection(solver, tuple(mapping[x] for x in labels))
            assert projected == expected
            actual = tuple(mapping[x] for x in joint_labels)
            exact_joint = c.old.sat_projection(solver, actual)
            assert exact_joint == joint
            # Exhaustive SAT all-subset test independent of the transfer's
            # shattered-side search and of its cached relation predicate.
            full = {}
            minimal = []
            for size in range(len(actual) + 1):
                for support in itertools.combinations(range(len(actual)), size):
                    actual_support = tuple(actual[j] for j in support)
                    mask = c.old.sat_projection(solver, actual_support)
                    full[support] = mask.bit_count() == 1 << size
                    if not full[support] and all(full[support[:j] + support[j + 1:]] for j in range(size)):
                        minimal.append({'positions': list(support), 'labels': [joint_labels[j] for j in support],
                                        'actual_ids': list(actual_support), 'allowed_count': mask.bit_count()})
            assert all(not (any(joint_labels[j] < w.km for j in x['positions']) and
                            any(joint_labels[j] >= w.km + 3 for j in x['positions'])) for x in minimal)
        records.append({'key_sha256': rec['key_sha256'], 'entry': entry, 'word': list(word),
                        'word_depth': len(word), 'absolute_depth': len(word) + int(w.wrapper),
                        'Q': {'J': hex(q[0]), 'partition': list(q[1])},
                        'all_copy_unfolding': True, 'variables': direct.n, 'copies': direct.block_count,
                        'window_projection_equal': True, 'joint_labels': list(joint_labels),
                        'joint_actual_ids': list(actual), 'joint_hex': hex(joint),
                        'joint_allowed_rows': [s for s in range(1 << len(joint_labels)) if (joint >> s) & 1],
                        **info, 'all_minimal_nonfull_supports_by_independent_SAT': minimal,
                        'subset_projections_checked': len(full), 'cross_bonds': [],
                        'literal_advisor_4_top_ports_1_target_relation': False,
                        'literal_comparison_reason': 'This family has three top ports and five target-own distinctions; it realises the generic hiding phenomenon, not the advisor five-variable relation with four top ports.'})
    result = {'family': rec['key_sha256'], 'preperiod': orb['preperiod'], 'period': orb['period'],
              'states_in_unique_eventual_Q_set': len(orb['levels'][orb['preperiod']]),
              'hidden_word_states': records, 'family_residue_plain_and_bond_flags_still_agree': True,
              'word_state_plain_and_bond_flags_differ': True,
              'seconds': time.monotonic() - started, **meta()}
    (c.HERE / 'pinning_window_results_hiding.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'hidden_word_states': len(records), 'seconds': result['seconds'],
                      'subset_projections': sum(x['subset_projections_checked'] for x in records)}), flush=True)


def Rrescues():
    started = time.monotonic()
    data, census = population()
    path = c.ROOT / 'research/READ-RULE-20261114-001/referee-R1/codex/coverage_run.py'
    spec = importlib.util.spec_from_file_location('earlier_read_referee_coverage', path)
    coverage = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(coverage)
    c.READS[str(path.relative_to(c.ROOT))] = hashlib.sha256(path.read_bytes()).hexdigest()
    digest_path = Path('artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz')
    digests = {r['key']: r for r in c.read_jsonl(digest_path)}
    records = []
    for prefix in ('432127c418b0', '981fdc202826'):
        rec = next(r for r in data if r['key_sha256'].startswith(prefix))
        w = c.old.Window(json.loads(rec['key']), census[rec['key']]['S'])
        syntax = coverage.parse_syntax(rec['key'], w.S)
        answer = coverage.family_r(w, syntax, digests[rec['key']], check_full=True)
        assert answer['exists_good_each_Q_residue']
        assert all(x['U'] <= 3 and x['some_state_survives'] for x in answer['residues'])
        # Pick one surviving literal reading in each refined Q phase and
        # independently verify it directly in the raw selected-word CNF.
        orb = c.orbit(w)
        certificates = []
        for phase in answer['residues']:
            s = phase['s']
            at = s if s < len(orb['levels']) else orb['preperiod'] + (s - orb['preperiod']) % orb['period']
            found = None
            for q, (entry, word) in orb['levels'][at].items():
                for local in syntax['candidates']:
                    if q[1][w.km + local[0]] >= w.km:
                        continue
                    local_rows = coverage.projected_local_rows(w, q, local)
                    info = coverage.triple_info(local_rows)
                    if info['exception']:
                        continue
                    direct = c.old.DirectCNF(w)
                    target = direct.selected_path(entry, word)
                    actual = tuple(target[j] for j in local)
                    with c.Solver(name='cadical195', bootstrap_with=direct.clauses) as solver:
                        projected = c.old.sat_projection(solver, actual)
                        assert projected == sum(1 << row for row in local_rows)
                        if info['triple_is_bond']:
                            support = actual
                        else:
                            support = actual[:2]
                        bond = c.old.verify_bond(solver, support)
                    found = {'phase': phase['Q_phase'], 'word': list(word), 'entry': entry,
                             'word_depth': len(word), 'absolute_depth': len(word) + int(w.wrapper),
                             'candidate': list(local), 'actual_ids': list(actual),
                             'triple_rows': list(local_rows), 'bond': bond}
                    break
                if found:
                    break
            assert found
            certificates.append(found)
        records.append({'key_sha256': rec['key_sha256'], 'key': rec['key'],
                        'S': w.S, 'wrapper': w.wrapper, 'coverage': answer,
                        'raw_CNF_phase_certificates': certificates})
    result = {'families': records, 'all_refined_Q_phases_R_bounded': True,
              'raw_CNF_certificates': sum(len(r['raw_CNF_phase_certificates']) for r in records),
              'seconds': time.monotonic() - started, **meta()}
    (c.HERE / 'pinning_window_results_Rrescues.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps({'R_families': 2, 'raw_CNF_certificates': result['raw_CNF_certificates'],
                      'seconds': result['seconds']}), flush=True)


def toponly():
    started = time.monotonic()
    data, census = population()
    records = []
    for prefix in ('fea4933ecaf1', 'fd60333c5872', '5ceea39607cb'):
        rec = next(r for r in data if r['key_sha256'].startswith(prefix))
        w = c.WholeMain(json.loads(rec['key']), census[rec['key']]['S'])
        orb = c.orbit(w)
        bonds = {}
        phases = []
        for phase, states in enumerate(orb['levels'][orb['preperiod']:]):
            best = None
            for q, path in states.items():
                if q not in bonds:
                    labels, allowed = w.relation(q)
                    use = tuple(j for j, x in enumerate(labels) if x < w.width or x >= w.width + 3)
                    trimmed_labels = tuple(labels[j] for j in use)
                    rel = c.Relation(trimmed_labels, c.project_mask(allowed, use))
                    roots = [j for j, x in enumerate(trimmed_labels) if x < w.km]
                    target = [j for j, x in enumerate(trimmed_labels) if x >= w.width + 3]
                    bonds[q] = rel.least_bond(roots, target)
                bond = bonds[q]
                if bond['size'] is not None and (best is None or bond['size'] < best[0]):
                    best = bond['size'], q, path, bond['support']
            cert = None
            if best:
                size, q, path, support = best
                cert = c.direct_check(w, q, path, support, explicit=False, compare=True)
                # Every permitted support member is allocated in main or c.
                assert all(x.get('main_port') is not None or x['absolute_depth'] in
                           (0, cert['absolute_depth']) for x in cert['bond_origins'])
            phases.append({'phase': phase, 'word_depth': orb['preperiod'] + w.start_depth + phase,
                           'top_only_U': best[0] if best else '> 6', 'certificate': cert})
        records.append({'key_sha256': rec['key_sha256'], 'key': rec['key'],
                        'S': w.S, 'main_block_size': w.width, 'S_block_size': w.size,
                        'preperiod': orb['preperiod'] + w.start_depth, 'period': orb['period'],
                        'phases': phases,
                        'top_only_bounded_every_phase': all(isinstance(x['top_only_U'], int) for x in phases),
                        'nonclaim': 'These are certified upper bounds using only main-allocated and target-allocated members, not claims that every least bond has those allocations.'})
        print(json.dumps({'top_only_family': prefix, 'preperiod': records[-1]['preperiod'],
                          'period': orb['period'], 'bounds': [x['top_only_U'] for x in phases]}), flush=True)
    result = {'families': records, 'seconds': time.monotonic() - started, **meta()}
    (c.HERE / 'pinning_window_results_toponly.json').write_text(json.dumps(result, indent=2) + '\n')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('mode', choices=('controls', 'growers', 'orders', 'identities', 'twoblock',
                                         'hiding', 'Rrescues', 'toponly', 'all'))
    parser.add_argument('--limit', type=int)
    parser.add_argument('--select')
    args = parser.parse_args()
    if args.mode == 'all':
        controls()
        for mode in ('growers', 'orders', 'identities'):
            pinning(mode)
        two_block()
        hiding()
        Rrescues()
        toponly()
    elif args.mode == 'controls':
        controls()
    elif args.mode == 'twoblock':
        two_block(args.limit, args.select)
    elif args.mode == 'hiding':
        hiding()
    elif args.mode == 'Rrescues':
        Rrescues()
    elif args.mode == 'toponly':
        toponly()
    else:
        pinning(args.mode, args.limit)


if __name__ == '__main__':
    main()
