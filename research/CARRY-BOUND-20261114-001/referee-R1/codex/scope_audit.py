"""Independent CARRY-BOUND-R1 scope, denominator, and wording audit.

Only the assigned scientific input list is opened. No study Python is opened or
imported. The structural predicates below are freshly authored; the semantics
of usual() are the explicit rule in the permitted earlier referee helper.
Output ownership: this directory's scope_* files only. Standard library only.
"""
from __future__ import annotations

import collections
import gzip
import hashlib
import json
import math
from pathlib import Path
import resource
import sys
import time

resource.setrlimit(resource.RLIMIT_AS, (768 * 1024**2, 768 * 1024**2))
ROOT = Path(__file__).resolve().parents[4]
OUT = Path(__file__).with_suffix('.json')
CENSUS = Path('artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz')
ART = Path('artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window')
EXP = Path('experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex')
OLD = Path('research/CENSUS-FORGET-20261114-001/referee-R1/codex')
READS = {}


def read(path):
    assert path.suffix != '.py'
    data = (ROOT / path).read_bytes()
    READS[str(path)] = hashlib.sha256(data).hexdigest()
    return gzip.decompress(data) if path.suffix == '.gz' else data


def load(path):
    return json.loads(read(path))


def lines(path):
    return [json.loads(line) for line in read(path).splitlines() if line.strip()]


def stream_lines(path):
    with (ROOT / path).open('rb') as handle:
        digest = hashlib.file_digest(handle, 'sha256')
    READS[str(path)] = digest.hexdigest()
    opener = gzip.open if path.suffix == '.gz' else open
    with opener(ROOT / path, 'rt') as handle:
        for line in handle:
            if line.strip():
                yield json.loads(line)


def usual(raw):
    result = []
    for arity, own, raw_calls in raw:
        calls = [(callee, tuple(args)) for callee, args in raw_calls]
        if any(c == 'SELF' and sorted(a) == [0, 1, 2] for c, a in calls):
            calls.append(('K', (0, 1, 2)))
        result.append((arity, own, calls))
    return result


def structure(key, S):
    defs = usual(json.loads(key))
    main = len(defs) - 1
    holding = {i for i, (_, _, calls) in enumerate(defs)
               if any(c == 'SELF' for c, _ in calls)}
    own_cache = {}

    def inline_own(i):
        if i not in own_cache:
            own_cache[i] = defs[i][1] + sum(inline_own(c) for c, _ in defs[i][2]
                                          if isinstance(c, int) and c not in holding)
        return own_cache[i]

    def reaches(start):
        seen, pending = set(), [start]
        while pending:
            i = pending.pop()
            if i in seen:
                continue
            seen.add(i)
            pending.extend(c for c, _ in defs[i][2] if isinstance(c, int))
        return seen

    reached = reaches(S) | reaches(main)
    others = sorted((reached & holding) - {S})
    other_own = [i for i in others if inline_own(i)]
    delay = [i for i in others if S in reaches(i)]
    # Occurrences, not merely distinct names, determine chain membership.
    counters = []
    for i, (_, _, calls) in enumerate(defs):
        count = collections.Counter()
        for c, _ in calls:
            if c == 'SELF':
                count[i] += 1
            elif isinstance(c, int):
                assert c < i
                count.update(counters[c])
        counters.append(count)
    chain = counters[S] == {S: 1} and counters[main] == {S: 1}
    return {'in_scope': not other_own and not delay, 'S': S, 'main': main,
            'other_own': other_own, 'delaying_types': delay,
            'other_own_details': {str(i): inline_own(i) for i in other_own},
            'chain': chain, 'defs': defs, 'holding': holding,
            'S_counter': dict(counters[S]), 'main_counter': dict(counters[main])}


def flatten(defs, holding, i):
    nextvar, calls = defs[i][0], []

    def visit(j, actual):
        nonlocal nextvar
        arity, own, body = defs[j]
        assert len(actual) == arity
        local = list(range(nextvar, nextvar + own))
        nextvar += own
        env = list(actual) + local
        for c, args in body:
            mapped = tuple(env[a] for a in args)
            if c == 'K':
                calls.append(('K', mapped))
            elif c == 'SELF':
                calls.append((j, mapped))
            elif c in holding:
                calls.append((c, mapped))
            else:
                visit(c, mapped)
    visit(i, tuple(range(defs[i][0])))
    return nextvar, calls


def syntactic(info):
    defs, holding, S, main = (info[k] for k in ('defs', 'holding', 'S', 'main'))
    _, body = flatten(defs, holding, S)
    _, main_body = flatten(defs, holding, main)
    calls = [args for c, args in body if c == S]
    graph = {(j, k) for args in calls for k, j in enumerate(args) if j < 3}
    reach = set(graph)
    while True:
        new = reach | {(a, c) for a, b in reach for b2, c in reach if b == b2}
        if new == reach:
            break
        reach = new
    identity_cycle = any(a == b for a, b in reach)
    mask = 7 if main == S else sum(1 << k for k in range(3)
                                  if any(c == S and args[k] < defs[main][0]
                                         for c, args in main_body))
    masks, seen = [], {}
    while mask not in seen:
        seen[mask] = len(masks)
        masks.append(mask)
        mask = sum(1 << k for k in range(3)
                   if any(j < 3 and (mask >> j) & 1
                          for args in calls for k2, j in enumerate(args) if k2 == k))
    preperiod, period = seen[mask], len(masks) - seen[mask]
    meeting = {k for c, args in body if c == 'K' and any(x >= 3 for x in args)
               for k in args if k < 3}
    # Least fixed point of liveness; knots are the seeds, calls propagate it.
    live = [set() for _ in defs]
    while True:
        after = [set(x) for x in live]
        for i, (arity, _, calls_i) in enumerate(defs):
            for c, args in calls_i:
                positions = range(len(args)) if c == 'K' else live[i if c == 'SELF' else c]
                after[i].update(args[k] for k in positions if args[k] < arity)
        if after == live:
            break
        live = after
    return {'identity_cycle': identity_cycle, 'preperiod': preperiod,
            'period': period, 'masks': masks, 'meeting': sorted(meeting),
            'live_S': sorted(live[S])}


def at(sequence, preperiod, period, s):
    return sequence[s if s < len(sequence) else preperiod + (s - preperiod) % period]


def p3_explanation(record, syn):
    if record['caps'] or not record['window_complete']:
        return None
    wp, wq = record['preperiod'], record['period']
    sp, sq = syn['preperiod'], syn['period']
    meeting = sum(1 << k for k in syn['meeting'])
    begin = max(wp, sp)
    missing = False
    for s in range(begin, begin + math.lcm(wq, sq)):
        u = at(record['U_by_s'], wp, wq, s)
        if not isinstance(u, int):
            missing = True
            if at(syn['masks'], sp, sq, s) & meeting:
                return False
    assert missing
    return True


def tally(records):
    return {'families': len(records), 'draws': sum(x['weight'] for x in records)}


def outcome(record):
    return record['verdict'] if record['verdict'] in ('bounded', 'growing') else 'undecided'


def partition(records, classifier=outcome):
    return {label: tally([x for x in records if classifier(x) == label])
            for label in ('bounded', 'growing', 'undecided')}


def fraction(n, d):
    return {'numerator': n, 'denominator': d, 'percent': 100 * n / d}


def main():
    started = time.monotonic()
    digest = lines(ART / 'window_digest.jsonl.gz')
    assert len(digest) == len({r['key'] for r in digest}) == 5964
    records = {r['key']: r for r in digest}
    census = {r['key']: r for r in stream_lines(CENSUS) if r['class'] == 'grows'}
    assert len(census) == 12772 and set(records) <= set(census)
    earlier = load(OLD / 'target_inventory.json')
    earlier_share = load(OLD / 'chain_share_audit.json')
    summary = load(ART / 'summary.json.gz')
    for name in ('carry_bound.md', 'preregistration.md', 'codex_spec.md',
                 'codex_spec2.md', 'advisor_review_answer.md', 'advisor_review2_answer.md'):
        read(Path('research/CARRY-BOUND-20261114-001') / name)
    paths = lines(EXP / 'paths_full/results.jsonl')
    path_sample = load(EXP / 'sample.json')
    infos, syns = {}, {}
    for key, row in census.items():
        infos[key] = structure(key, row['S'])
    scope_errors, syntax_errors = [], []
    for key, rec in records.items():
        info = infos[key]
        if info['in_scope'] != rec['in_scope']:
            scope_errors.append(key)
        assert not info['chain']
        syn = syntactic(info)
        syns[key] = syn
        exp = rec['syntactic_carried']
        if (syn['identity_cycle'] != (rec['stratum'] == 'I')
                or syn['preperiod'] != exp['preperiod']
                or syn['period'] != exp['period']
                or syn['masks'] != exp['masks']
                or syn['meeting'] != exp['knot_meeting_positions']
                or syn['live_S'] != rec['live_S']):
            syntax_errors.append({'key_sha256': rec['key_sha256'], 'fresh': syn,
                                  'recorded': exp, 'recorded_live': rec['live_S']})
    assert not scope_errors and not syntax_errors
    # Test the old inventory on every recorded c=1 nonchain, not just CARRY's subset.
    old_scope_errors = []
    for rec in earlier['families']:
        fresh = infos[rec['key']]
        if bool(fresh['other_own']) != rec['has_other_own']:
            old_scope_errors.append(rec['key'])
        old_defs = {x['definition']: x['inlined_own'] for x in rec['other_definitions']}
        for i, count in fresh['other_own_details'].items():
            assert old_defs[int(i)] == count
    assert not old_scope_errors
    inside = [r for r in digest if infos[r['key']]['in_scope']]
    outside = [r for r in digest if not infos[r['key']]['in_scope']]
    reasons = {}
    for own, delay in ((True, False), (False, True), (True, True)):
        rs = [r for r in outside if bool(infos[r['key']]['other_own']) == own
              and bool(infos[r['key']]['delaying_types']) == delay]
        reasons[f'other_own={own},delayed_S={delay}'] = tally(rs)
    grow = [r for r in inside if outcome(r) == 'growing']
    assert len(grow) == 632
    assert all(r['G_r'] for r in grow)
    assert all(not (at(syns[r['key']]['masks'], syns[r['key']]['preperiod'],
                       syns[r['key']]['period'], s)
                    & sum(1 << k for k in syns[r['key']]['live_S']))
               for r in grow
               for s in range(syns[r['key']]['preperiod'],
                              syns[r['key']]['preperiod'] + syns[r['key']]['period']))
    cap_bounded = [r for r in inside if r['caps'] and r['window_verdict'] == 'bounded']
    assert len(cap_bounded) == 2 and all(r['verdict'] == 'undecided' for r in cap_bounded)
    assert all(r['window_complete'] and all(u == 3 for u in r['U_by_s']) for r in cap_bounded)
    # Bound only through complete every-residue path certificates; path growth is not promoted.
    path_bound = []
    for line_number, row in enumerate(paths, 1):
        assert row['status'] == 'ok'
        p = row['result']
        if p.get('path_class') == 'bounded':
            assert p['eventually_bounded'] is True
            assert p['exact_eventual_boundedness']['missing_residues'] == []
            r = records[row['case']]
            assert r['in_scope'] and outcome(r) == 'undecided'
            path_bound.append({'key_sha256': r['key_sha256'], 'key': r['key'],
                               'source_line': line_number,
                               'stratum': r['stratum'], 'weight': r['weight'],
                               'wrapper': r['wrapper'], 'window_verdict': r['window_verdict'],
                               'window_caps': r['caps'], 'period': p['period'],
                               'result_complete': p['complete'], 'result_status': p['status'],
                               'result_stage': p['stage'],
                               'onset_depth': p['onset_depth'],
                               'uniform_cost_bound': p['uniform_cost_bound']})
    path_keys = {p['key'] for p in path_bound}
    strict_path_keys = {p['key'] for p in path_bound if p['result_complete'] and p['result_status'] == 'done'}
    assert len(path_keys) == 7
    final = lambda r: 'bounded' if r['key'] in path_keys else outcome(r)
    all_math_keys = path_keys | {r['key'] for r in cap_bounded}
    all_math = lambda r: 'bounded' if r['key'] in all_math_keys else outcome(r)
    final_inside, final_all = partition(inside, final), partition(digest, final)
    assert final_inside == {'bounded': {'families': 5074, 'draws': 5136},
                            'growing': {'families': 632, 'draws': 634},
                            'undecided': {'families': 83, 'draws': 83}}
    cap_no_window = [r for r in inside if final(r) == 'undecided'
                     and not r['window_complete']]
    no_certificate = [r for r in inside if final(r) == 'undecided'
                      and r['window_complete'] and not r['caps']]
    assert len(cap_no_window) == 70 and len(no_certificate) == 11
    chains = {key for key, info in infos.items() if info['chain']}
    assert len(chains) == 5190 and not chains & set(records)
    old_nonchain = set(census) - chains - set(records)
    assert len(old_nonchain) == 1618
    old_excluded = {key for key in old_nonchain if not infos[key]['in_scope']}
    assert len(old_excluded) == 188
    old_eligible = old_nonchain - old_excluded
    assert len(old_eligible) == 1430
    assert old_excluded == {r['key'] for r in earlier['all_certified_with_other_own']} | {
        r['key'] for r in earlier['all_certified_with_delayed_S']}
    inherited = earlier_share['supplemental_corrected_bound']
    old_draws = inherited['chain_draws'] + len(old_eligible)
    assert old_draws == inherited['conditional_conservative_lower_tally'] == 7063
    total_draws = earlier_share['raw_data']['first_ray_growth_draws']
    assert total_draws == 13279 == old_draws + len(old_excluded) + sum(r['weight'] for r in digest)
    census_split = {
        'growing': fraction(old_draws + final_all['growing']['draws'], total_draws),
        'bounded': fraction(final_all['bounded']['draws'], total_draws),
        'undecided': fraction(final_all['undecided']['draws'] + len(old_excluded), total_draws)}
    assert [census_split[k]['numerator'] for k in ('growing', 'bounded', 'undecided')] == [7697, 5265, 317]
    I = [r for r in inside if r['stratum'] == 'I']
    O = [r for r in inside if r['stratum'] == 'O']
    P1_num = sum(r['weight'] for r in I if outcome(r) == 'bounded')
    P1_den = sum(r['weight'] for r in I)
    I_unknown = sum(r['weight'] for r in I if outcome(r) == 'undecided')
    O_num = sum(r['weight'] for r in O if outcome(r) == 'bounded')
    residual = [r for r in I if outcome(r) != 'bounded']
    p3 = [(r, p3_explanation(r, syns[r['key']])) for r in residual]
    P3_num = sum(r['weight'] for r, flag in p3 if flag is True)
    P3_den = sum(r['weight'] for r, _ in p3)
    P3_unknown = sum(r['weight'] for r, flag in p3 if flag is None)
    assert (P1_num, P1_den, I_unknown, O_num, len(O), P3_num, P3_den, P3_unknown) == (5029, 5751, 88, 91, 93, 648, 722, 74)
    weighted_strata = {}
    for label in ('I', 'T', 'O', 'X'):
        rs = [r for r in inside if r['stratum'] == label]
        weighted_strata[label] = {'population': tally(rs), 'window_stage': partition(rs),
                                  'after_paths': partition(rs, final)}
    completed_bound = [r for r in digest if outcome(r) == 'bounded']
    thresholds = {'max_window_preperiod': max(r['preperiod'] for r in completed_bound),
                  'max_window_absolute_depth_threshold': max(r['preperiod'] + r['wrapper'] for r in completed_bound),
                  'window_preperiod_by_wrapper': {str(w): max(r['preperiod'] for r in completed_bound if r['wrapper'] == w) for w in (False, True)},
                  'max_window_bound': max(max(r['U_by_s'][r['preperiod']:r['preperiod']+r['period']]) for r in completed_bound),
                  'max_path_onset_depth': max(p['onset_depth'] for p in path_bound),
                  'max_path_bound': max(p['uniform_cost_bound'] for p in path_bound),
                  'growth_r_count': dict(sorted(collections.Counter(r['G_r'] for r in grow).items()))}
    controls = {}
    try:
        assert sum(census_split[k]['numerator'] for k in census_split) == total_draws + 1
    except AssertionError:
        controls['wrong_total_13280_rejected'] = True
    try:
        assert P1_den == len(I)
    except AssertionError:
        controls['families_as_draw_denominator_rejected'] = True
    bad_key = sorted(old_excluded)[0]
    controls['outside_scope_lower_bound_rejected'] = not infos[bad_key]['in_scope']
    controls['outside_scope_example'] = {'key': bad_key, 'other_own': infos[bad_key]['other_own'],
                                         'delaying_types': infos[bad_key]['delaying_types']}
    assert controls['wrong_total_13280_rejected'] and controls['families_as_draw_denominator_rejected']
    assert controls['outside_scope_lower_bound_rejected']
    early_gap = next(r for r in completed_bound
                     if any(not isinstance(u, int) or u > 4 for u in r['U_by_s'][:r['preperiod']]))
    result = {'scope': 'CARRY-BOUND-20261114-001 R1 points 3-6',
              'validation': 'V2 independent same-task structural recount and certificate aggregation; validity of window/path/gap certificates is inherited, not reproved here.',
              'population': tally(digest), 'in_scope': tally(inside), 'out_of_scope': tally(outside),
              'scope_mismatches': scope_errors, 'syntax_mismatches': syntax_errors,
              'earlier_inventory_rows_rechecked': len(earlier['families']),
              'earlier_inventory_overlap_with_CARRY': sum(r['key'] in records for r in earlier['families']),
              'earlier_inventory_mismatches': old_scope_errors,
              'scope_exclusion_reasons': reasons, 'window_stage_inside': partition(inside),
              'window_stage_all': partition(digest), 'after_paths_inside': final_inside,
              'after_paths_all': final_all, 'strata': weighted_strata,
              'strict_complete_path_additions': len(strict_path_keys),
              'strict_complete_paths_inside': partition(inside, lambda r: 'bounded' if r['key'] in strict_path_keys else outcome(r)),
              'strict_complete_paths_census_split': {
                  'growing': census_split['growing'],
                  'bounded': fraction(final_all['bounded']['draws'] - len(path_keys - strict_path_keys), total_draws),
                  'undecided': fraction(census_split['undecided']['numerator'] + len(path_keys - strict_path_keys), total_draws)},
              'all_primary_mathematical_certificates_inside': partition(inside, all_math),
              'all_primary_mathematical_certificates_census_split': {
                  'growing': census_split['growing'],
                  'bounded': fraction(final_all['bounded']['draws'] + sum(r['weight'] for r in cap_bounded), total_draws),
                  'undecided': fraction(census_split['undecided']['numerator'] - sum(r['weight'] for r in cap_bounded), total_draws)},
              'remaining_inside': {'incomplete_capped_windows': tally(cap_no_window),
                                   'complete_without_bound_or_growth': tally(no_certificate),
                                   'capped_but_window_bounded': tally(cap_bounded)},
              'capped_but_window_bounded': cap_bounded, 'path_additions': path_bound,
              'path_sample_records': len(paths), 'frozen_sample_data_keys': list(path_sample),
              'previous_tally': {'chains_families': len(chains), 'chains_draws_inherited': inherited['chain_draws'],
                                  'eligible_certified_nonchains': len(old_eligible),
                                  'excluded_certified_nonchains': len(old_excluded),
                                  'growth_draws': old_draws},
              'census_split': census_split,
              'P1': fraction(P1_num, P1_den),
              'P1_sensitivity': fraction(P1_num, P1_den - I_unknown),
              'P2_I_minus_O_percentage_points': 100 * (P1_num / P1_den - O_num / len(O)),
              'P3': fraction(P3_num, P3_den),
              'P3_unknown_weight': P3_unknown,
              'P3_sensitivity': fraction(P3_num, P3_den - P3_unknown),
              'P5': fraction(sum(r['weight'] for r in grow), sum(r['weight'] for r in inside)),
              'thresholds': thresholds, 'controls': controls,
              'growth_wrapper_families': sum(r['wrapper'] for r in grow),
              'caps_by_kind': dict(collections.Counter(c for r in digest for c in r['caps'])),
              'early_window_gap_example': {k: early_gap[k] for k in ('key_sha256', 'wrapper', 'preperiod', 'period', 'U_by_s')},
              'limits': ['Draw weights are inherited from CARRY digest and the earlier permitted referee tally; the raw draw file was outside this lane\'s allowed inputs.',
                         'I identity-cycle labels and carried/read positions are rederived; T/O/X labels are inherited.',
                         'The global correction log was outside allowed input scope; correction verdicts can be assessed only from the permitted carry note descriptions.',
                         'Finite direct readings and path-growing labels never certify growth of the free bond.',
                         'No uniform whole-stratum theorem is proved by finite census replay.'],
              'inputs_sha256': READS, 'script_sha256': hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              'interpreter': sys.executable, 'seconds': time.monotonic() - started,
              'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              'address_space_limit_bytes': 768 * 1024**2}
    OUT.write_text(json.dumps(result, indent=2, sort_keys=True) + '\n')
    print(json.dumps({k: result[k] for k in ('population', 'in_scope', 'out_of_scope', 'after_paths_inside', 'census_split', 'thresholds', 'seconds', 'peak_rss_kib')}, indent=2))


if __name__ == '__main__':
    main()
