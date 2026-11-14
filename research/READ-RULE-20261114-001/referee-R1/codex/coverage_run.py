"""Fresh READ referee coverage audit. Producer READ Python is never accessed.

Earlier CARRY referee Window supplies independently reconstructed finite-limit
and Q-transition algorithms. READ candidates, pendant syntax, carriage masks,
projections, quantifiers and recounts are newly implemented below.
"""
from __future__ import annotations

import argparse
import collections
import gc
import gzip
import hashlib
import importlib.util
import itertools
import json
import math
import resource
import sys
import time
from pathlib import Path

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/READ-RULE-20261114-001/referee-R1/codex'
OLD = ROOT / 'research/CARRY-BOUND-20261114-001/referee-R1/codex'
DATA = ROOT / 'experiments/READ-RULE-20261114-001B/READ-RULE-20261114-001B-E001_coverage/codex'
DIGEST = ROOT / 'artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz'
CENSUS = ROOT / 'artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz'
spec = importlib.util.spec_from_file_location('earlier_carry_referee_window', OLD / 'window_audit.py')
window = importlib.util.module_from_spec(spec)
spec.loader.exec_module(window)


def read_json(path):
    return json.loads(path.read_text())


def gzrows(path):
    with gzip.open(path, 'rt') as stream:
        for line in stream:
            if line.strip():
                yield json.loads(line)


def sha(path):
    with path.open('rb') as stream:
        return hashlib.file_digest(stream, 'sha256').hexdigest()


def projection(rows, positions):
    return {tuple((state >> j) & 1 for j in positions) for state in rows}


def triple_info(rows):
    """Positions p=0,x=1,z=2; rows are actual triple assignments."""
    rows = tuple(rows)
    px = projection(rows, (0, 1))
    pz = projection(rows, (0, 2))
    xz = projection(rows, (1, 2))
    full = {(0, 0), (0, 1), (1, 0), (1, 1)}
    opposite = {(0, 1), (1, 0)}
    exception = px == full and (pz == opposite or xz == opposite)
    pair_bond = len(px) == 2
    triple_bond = len(rows) < 8 and len(px) == len(pz) == len(xz) == 4
    return {'exception': exception, 'bond_through_p_x': pair_bond or triple_bond,
            'px': sorted(px), 'pz': sorted(pz), 'xz': sorted(xz),
            'px_tied': pair_bond, 'pz_opposite': pz == opposite,
            'xz_opposite': xz == opposite,
            'triple_is_bond': triple_bond}


def small_exact():
    pairs = ((1, 6), (2, 5), (3, 4))
    cases = []
    for subset in range(1, 8):
        rows = sorted(s for j, pair in enumerate(pairs) if subset >> j & 1 for s in pair)
        info = triple_info(rows)
        assert info['bond_through_p_x'] == (not info['exception'])
        cases.append({'allowed': rows, **info})
    p_cases = []
    for P in ({0, 3}, {1, 2}, {0, 1, 2, 3}):
        rows = [s for s in range(1, 7) if s & 3 in P]
        info = triple_info(rows)
        assert info['bond_through_p_x'] and not info['exception']
        p_cases.append({'P': sorted(P), 'allowed': rows, **info})
    # The forbidden empty relation breaks Fact 1, so must never enter the test.
    assert not tuple(s for s in () if s in range(1, 7))
    # An opposite z-p tie alone is not the exception when p-x is tied too.
    control = triple_info([3, 4])
    assert control['pz_opposite'] and control['px_tied'] and not control['exception']
    # NAE with z negated has equal (not opposite) killing ties: sign hypothesis matters.
    signed_rows = [0, 1, 6, 7]
    signed = triple_info(signed_rows)
    assert not signed['bond_through_p_x'] and not signed['exception']
    out = {'nonempty_complement_closed_NAE_relations': len(cases),
           'exception_relations': sum(c['exception'] for c in cases),
           'equivalence_passed_all': True, 'cases': cases, 'pendant_P_cases': p_cases,
           'empty_dead_relation_excluded': True,
           'opposite_tie_without_free_px_rejected_as_exception': control,
           'negated_NAE_outside_positive_hypothesis_detected': {'allowed': signed_rows, **signed}}
    (HERE / 'coverage_triples.json').write_text(json.dumps(out, indent=2) + '\n')
    return out


def parse_syntax(key, S):
    """Raw-key implementation, separate from earlier Window flattening."""
    raw = json.loads(key)
    defs = []
    for arity, own, body in raw:
        body = [(c, tuple(a)) for c, a in body]
        if any(c == 'SELF' and set(a) == {0, 1, 2} and len(a) == 3 for c, a in body):
            body.append(('K', (0, 1, 2)))
        defs.append((arity, own, body))
    recursive = {i for i, (_, _, body) in enumerate(defs) if any(c == 'SELF' for c, _ in body)}

    def flattened(which):
        next_id = defs[which][0]
        calls = []
        all_call_arguments = set()

        def visit(i, ports):
            nonlocal next_id
            arity, own, body = defs[i]
            env = tuple(ports) + tuple(range(next_id, next_id + own))
            next_id += own
            for callee, args in body:
                actual = tuple(env[j] for j in args)
                if callee != 'K':
                    all_call_arguments.update(actual)
                if callee == 'K':
                    calls.append(('K', actual))
                elif callee == 'SELF':
                    calls.append((i, actual))
                elif callee in recursive:
                    calls.append((callee, actual))
                else:
                    visit(callee, actual)
        visit(which, range(defs[which][0]))
        return next_id, calls, all_call_arguments

    size, calls, all_call_arguments = flattened(S)
    main = len(raw) - 1
    msize, main_calls, _ = flattened(main)
    knots = [a for c, a in calls if c == 'K']
    arguments = {v for c, a in calls if c != 'K' for v in a}
    occurrences = collections.Counter(v for a in knots for v in a)
    flattened_pendant = {v for v in range(3, size) if occurrences[v] == 1 and v not in arguments}
    pendant = {v for v in range(3, size) if occurrences[v] == 1 and v not in all_call_arguments}
    candidates = sorted({(k, x, z) for a in knots for k in a if k < 3
                         for x in a if x >= 3 and x != k
                         for z in a if z not in (k, x)})
    r1 = [c for c in candidates if c[2] in pendant]
    steps = [a for c, a in calls if c == S]
    mask = 7 if main == S else sum(1 << k for k in range(3)
                                   if any(c == S and a[k] < defs[main][0] for c, a in main_calls))
    masks, seen = [], {}
    while mask not in seen:
        seen[mask] = len(masks)
        masks.append(mask)
        mask = sum(1 << k for k in range(3)
                   if any(a[k] < 3 and mask >> a[k] & 1 for a in steps))
    mu = seen[mask]
    period = len(masks) - mu
    residues = []
    for s in range(mu, len(masks)):
        matches = [list(c) for c in r1 if masks[s] >> c[0] & 1]
        residues.append({'s': s, 'carried_mask': masks[s], 'covered': bool(matches), 'witnesses': matches})
    return {'size': size, 'calls': calls, 'knots': knots, 'pendant': sorted(pendant),
            'all_call_arguments_including_finite_helpers': sorted(all_call_arguments),
            'flattened_pendant_before_call_guard': sorted(flattened_pendant),
            'candidates': candidates, 'R1_candidates': r1,
            'R_mu': mu, 'R_period': period, 'R_masks': masks,
            'R1_residues': residues, 'R1_all': all(r['covered'] for r in residues),
            'R1_some': any(r['covered'] for r in residues)}


def q_orbit(w, expected_mu, expected_period):
    """No bond search: reconstruct reachable Q sets, retaining concrete words."""
    current = dict(w.starts)
    seen, levels = {}, []
    stored = 0
    while True:
        frozen = frozenset(current)
        if frozen in seen:
            mu = seen[frozen]
            assert (mu, len(levels) - mu) == (expected_mu, expected_period)
            return levels, mu, len(levels) - mu
        assert len(levels) < 2000 and stored + len(current) <= 200000
        seen[frozen] = len(levels)
        stored += len(current)
        levels.append(current)
        nxt = {}
        for q, (entry, word) in current.items():
            for label in range(len(w.generators)):
                nxt.setdefault(w.step(q, label), (entry, word + (label,)))
        current = nxt


def projected_local_rows(w, q, local):
    """Read only the target's local values after exact context filtering.

    If k is carried, p is literally local k. Existence of a context root
    assignment is exactly nonemptiness of a J column. Every actual identity
    restriction is already respected by that relation's construction.
    """
    J, _ = q
    image = 0
    for t in range(1 << w.km):
        image |= (J >> (8 * t)) & 255
    return tuple(sorted({sum(((b >> v) & 1) << j for j, v in enumerate(local))
                         for b in w.good if image >> (b & 7) & 1}))


def check_against_whole_window(w, q, local, rows):
    labels, mask = w.relation(q)
    actual = [q[1][w.km + v] if v < 3 else w.km + v for v in local]
    positions = [labels.index(v) for v in actual]
    other = set()
    while mask:
        bit = mask & -mask
        mask ^= bit
        s = bit.bit_length() - 1
        other.add(sum(((s >> pos) & 1) << j for j, pos in enumerate(positions)))
    assert sorted(other) == list(rows)


def family_r(w, syntax, digest, check_full=False):
    levels, mu, period = q_orbit(w, digest['preperiod'], digest['period'])
    candidates = syntax['candidates']
    Rmu, Rp = syntax['R_mu'], syntax['R_period']
    candidate_cache, records, all_q = {}, [], set()
    begin = max(mu, Rmu)
    lcm = math.lcm(period, Rp)
    strict_groups = collections.defaultdict(lambda: [dict(eligible=0, exceptions=0) for _ in candidates])
    group_any = collections.defaultdict(list)
    witnesses = []
    total_eligible, total_exceptions, total_full = 0, 0, 0
    for s in range(begin, begin + lcm):
        index = s if s < len(levels) else mu + (s - mu) % period
        current = levels[index]
        per_candidate = [dict(eligible=0, exceptions=0) for _ in candidates]
        good_any = False
        read_any = False
        for q, path in current.items():
            all_q.add(q)
            for ci, candidate in enumerate(candidates):
                k, x, z = candidate
                root = q[1][w.km + k]
                if root >= w.km:
                    continue
                read_any = True
                key = (q, candidate)
                if key not in candidate_cache:
                    rows = projected_local_rows(w, q, candidate)
                    assert rows and not ({0, 7} & set(rows))
                    assert {7 - t for t in rows} == set(rows)
                    info = triple_info(rows)
                    assert info['bond_through_p_x'] == (not info['exception'])
                    candidate_cache[key] = rows, info
                    # Whole-window enumerator is a separate representation.
                    if check_full:
                        check_against_whole_window(w, q, candidate, rows)
                        total_full += 1
                rows, info = candidate_cache[key]
                per_candidate[ci]['eligible'] += 1
                per_candidate[ci]['exceptions'] += info['exception']
                total_eligible += 1
                total_exceptions += info['exception']
                if not info['exception']:
                    good_any = True
                    if len(witnesses) < 3:
                        witnesses.append({'s': s, 'candidate': list(candidate), 'root': root,
                                          'entry': path[0], 'word': list(path[1]),
                                          'Q': {'J': hex(q[0]), 'partition': list(q[1])},
                                          'triple': list(rows), **info})
        strict = any(c['eligible'] and c['exceptions'] == 0 for c in per_candidate)
        # Match the producer's stronger grouping by the R_s residue.
        rphase = (s - Rmu) % Rp
        group_any[rphase].append(good_any)
        for c, addition in zip(strict_groups[rphase], per_candidate):
            c['eligible'] += addition['eligible']
            c['exceptions'] += addition['exceptions']
        U = digest['U_by_s'][index]
        assert not good_any or isinstance(U, int) and U <= 3, 'R-to-window gate failed'
        records.append({'s': s, 'Q_phase': (s - mu) % period, 'R_phase': rphase,
                        'states': len(current), 'eligible_reading': read_any,
                        'some_state_survives': good_any, 'strict_carried_state': strict,
                        'exception_only': read_any and not good_any, 'U': U,
                        'candidate_counts': per_candidate})
    strict_R = all(any(c['eligible'] and c['exceptions'] == 0 for c in group)
                   for group in strict_groups.values())
    return {'Q_mu': mu, 'Q_period': period, 'Q_states_in_repeating_part': len(all_q),
            'Q_level_counts': [len(level) for level in levels],
            'exists_good_each_Q_residue': all(r['some_state_survives'] for r in records),
            'exists_good_each_R_residue_union': all(any(g) for g in group_any.values()),
            'strict_each_Q_residue': all(r['strict_carried_state'] for r in records),
            'strict_each_R_residue': strict_R,
            'some_Q_residue_survives': any(r['some_state_survives'] for r in records),
            'some_exception_only_Q_residue': any(r['exception_only'] for r in records),
            'eligible_checks': total_eligible, 'exception_checks': total_exceptions,
            'whole_window_crosschecks': total_full, 'residues': records, 'witnesses': witnesses}


def tally(rows):
    return {'families': len(rows), 'draw_weight': sum(r['weight'] for r in rows)}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--limit', type=int)
    parser.add_argument('--skip-q', action='store_true')
    args = parser.parse_args()
    start = time.monotonic()
    controls = small_exact()
    digests = list(gzrows(DIGEST))
    keys = {r['key'] for r in digests}
    census = {r['key']: r for r in gzrows(CENSUS) if r['key'] in keys}
    assert set(census) == keys and len(digests) == 5964
    official = {r['key']: r for r in read_json(DATA / 'results.json')['families']}
    old_exc = {r['key'] for r in read_json(DATA / 'summary.json')['Q1']['exception_only_families']}
    output = HERE / ('coverage_smoke.jsonl' if args.limit else 'coverage_results.jsonl')
    mismatch = []
    all_rows = []
    for i, digest in enumerate(digests[:args.limit] if args.limit else digests):
        key = digest['key']
        syntax = parse_syntax(key, census[key]['S'])
        their = official[key]
        theirs_syn = their['carried']
        assert (syntax['R_mu'], syntax['R_period'], syntax['R_masks']) == (
            theirs_syn['preperiod'], theirs_syn['period'], theirs_syn['masks'])
        assert syntax['R1_all'] == their['R1']['all_residues']
        assert syntax['R1_some'] == their['R1']['some_residues']
        assert sorted(map(tuple, their['candidates'])) == syntax['candidates']
        rec = {k: digest[k] for k in ('key', 'key_sha256', 'weight', 'in_scope', 'wrapper', 'stratum', 'verdict', 'window_complete')}
        rec.update({'S': census[key]['S'], 'syntax': syntax})
        if digest['in_scope'] and digest['window_complete'] and not args.skip_q:
            w = window.Window(json.loads(key), census[key]['S'])
            rec['R'] = family_r(w, syntax, digest, key in old_exc or i < 20)
            # Check the stricter carried-state reading against official data;
            # do not consume that flag when computing our result.
            other_strict = all(r['carried_Q_applies'] for r in their['R']['residues'])
            if rec['R']['strict_each_R_residue'] != other_strict:
                mismatch.append({'key_sha256': digest['key_sha256'], 'kind': 'strict_R',
                                 'ours': rec['R']['strict_each_R_residue'], 'theirs': other_strict})
            del w
        else:
            rec['R'] = None
        all_rows.append(rec)
        with output.open('w' if i == 0 else 'a') as stream:
            stream.write(json.dumps(rec, sort_keys=True) + '\n')
        if i % 200 == 0:
            print(json.dumps({'completed': i + 1, 'seconds': round(time.monotonic() - start, 2),
                              'rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}), flush=True)
        if i % 50 == 0:
            gc.collect()
    inside = [r for r in all_rows if r['in_scope']]
    bounded = [r for r in inside if r['verdict'] == 'bounded']
    denominator = tally(bounded)
    sums = {}
    for name in ('exists_good_each_Q_residue', 'exists_good_each_R_residue_union',
                 'strict_each_Q_residue', 'strict_each_R_residue', 'some_Q_residue_survives'):
        success = [r for r in bounded if r['R'] is not None and r['R'][name]]
        n = tally(success)
        sums[name] = {**n, 'family_percent': 100 * n['families'] / max(1, denominator['families']),
                      'weight_percent': 100 * n['draw_weight'] / max(1, denominator['draw_weight'])}
    exception = [r for r in inside if r['R'] and r['R']['some_exception_only_Q_residue']]
    r1all = [r for r in inside if r['syntax']['R1_all']]
    r1bound = [r for r in bounded if r['syntax']['R1_all']]
    summary = {'population': tally(all_rows), 'in_scope': tally(inside), 'bounded_denominator': denominator,
               'R1_all_in_scope': tally(r1all), 'R1_bounded': tally(r1bound),
               'R1_bounded_weight_percent': 100 * sum(r['weight'] for r in r1bound) / max(1, denominator['draw_weight']),
               'R1_all_nonbounded': [{k: r[k] for k in ('key_sha256', 'key', 'verdict')} for r in r1all if r not in bounded],
               'R1_some_only': [{k: r[k] for k in ('key_sha256', 'key', 'verdict')} for r in inside
                                if r['syntax']['R1_some'] and not r['syntax']['R1_all']],
               'R_coverage': sums, 'R_unavailable_in_scope': tally([r for r in inside if r['R'] is None]),
               'exception_only_Q_residue_families': [{k: r[k] for k in ('key_sha256', 'key', 'verdict', 'wrapper')} for r in exception],
               'official_nine_exceptions_reconstructed': len(old_exc & {r['key'] for r in exception}),
               'strict_official_disagreements': mismatch,
               'theorem_quantifier_newly_covered': [{k: r[k] for k in ('key_sha256', 'key', 'verdict')} for r in inside if r['R']
                                                  and r['R']['exists_good_each_Q_residue'] and not r['R']['strict_each_R_residue']],
               'Q_vs_R_union_quantifier_disagreements': [r['key_sha256'] for r in inside if r['R']
                                                       and r['R']['exists_good_each_Q_residue'] != r['R']['exists_good_each_R_residue_union']],
               'triple_controls': {k: controls[k] for k in ('nonempty_complement_closed_NAE_relations', 'exception_relations', 'equivalence_passed_all')},
               'seconds': time.monotonic() - start, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
               'inputs_sha256': {str(p.relative_to(ROOT)): sha(p) for p in (DIGEST, CENSUS, OLD / 'window_audit.py',
                                                                          DATA / 'results.json', DATA / 'summary.json')},
               'script_sha256': sha(Path(__file__))}
    path = HERE / ('coverage_smoke_summary.json' if args.limit else 'coverage_summary.json')
    path.write_text(json.dumps(summary, indent=2) + '\n')
    print(json.dumps({k: v for k, v in summary.items() if k not in ('inputs_sha256', 'theorem_quantifier_newly_covered',
                                                                 'exception_only_Q_residue_families', 'R1_all_nonbounded', 'R1_some_only')}, indent=2))


if __name__ == '__main__':
    main()
