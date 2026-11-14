"""TOP-INFO independent arithmetic/provenance audit: data only, no study code.

The existing READ referee's full coverage records, if retained, are compared
against TOP; flags from TOP are tallied as supplied, not independently proved.
Fresh mathematical recomputation lives in the other referee scripts.
"""
from __future__ import annotations
import collections
import gzip
import hashlib
import json
import resource
import time
from pathlib import Path

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/TOP-INFO-20261114-001/referee-R1/codex'
TOP = Path('artifacts/TOP-INFO-20261114-001A/TOP-INFO-20261114-001A-E001_rule_check/results.json.gz')
CARRY = Path('artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz')
READ = Path('research/READ-RULE-20261114-001/referee-R1/codex')
REACH = Path('artifacts/REACH-CENSUS-20261113-001A/REACH-CENSUS-20261113-001A-E001_reach_census/families.jsonl.gz')
PATHS = Path('experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex/paths_full/results.jsonl')
READS = {}


def raw(path):
    path = Path(path)
    assert path.suffix != '.py'
    data = (ROOT / path).read_bytes()
    READS[str(path)] = hashlib.sha256(data).hexdigest()
    return gzip.decompress(data) if path.suffix == '.gz' else data


def load(path):
    return json.loads(raw(path))


def rows(path):
    return [json.loads(line) for line in raw(path).splitlines() if line.strip()]


def small(r):
    return {k: r.get(k) for k in ('key', 'key_sha256', 'weight', 'stratum', 'final_verdict')}


def tally(rs):
    return {'families': len(rs), 'draw_weight': sum(r['weight'] for r in rs),
            'by_stratum': dict(collections.Counter(r['stratum'] for r in rs))}


def flag(r, name):
    if name == 'R':
        f = r['R']
    else:
        f = r['pinning'].get(name, {})
    return f.get('every_residue')


def partition(rs):
    groups = {'R_every': [], 'pinning_only': [], 'neither_confirmed': [], 'unavailable': []}
    for r in rs:
        R, P = flag(r, 'R'), flag(r, 'bond_pinned')
        k = ('R_every' if R is True else 'pinning_only' if P is True else
             'neither_confirmed' if R is False and P is False else 'unavailable')
        groups[k].append(r)
    total = tally(rs)
    return {'denominator': total, 'groups': {
        k: {**tally(v), 'family_percent': 100*len(v)/len(rs),
            'weight_percent': 100*sum(r['weight'] for r in v)/total['draw_weight']}
        for k, v in groups.items()},
        'overlap_R_and_pinning': tally([r for r in rs if flag(r, 'R') is True and flag(r, 'bond_pinned') is True]),
        'unavailable_rows': [small(r) for r in groups['unavailable']]}


def main():
    start = time.monotonic()
    resource.setrlimit(resource.RLIMIT_AS, (1024**3, 1024**3))
    top = load(TOP)['families']
    assert len(top) == len({r['key'] for r in top}) == 5964
    digest = {r['key']: r for r in rows(CARRY)}
    reach = {r['key']: r for r in rows(REACH) if r['key'] in digest}
    inside = [r for r in top if r['in_scope']]
    bounded = [r for r in inside if r['final_verdict'].startswith('bounded')]
    pathdata = rows(PATHS)
    # Reuse previous referee's preserved record-level extraction of path
    # admissions; additionally retain and hash the source rows ourselves.
    oldscope = load(Path('research/CARRY-BOUND-20261114-001/referee-R1/codex/scope_audit.json'))
    pathadds = oldscope['path_additions']
    incomplete_path = {r['key'] for r in pathadds if not r['result_complete']}
    strict = [r for r in bounded if r['key'] not in incomplete_path]
    full_window_keys = {r['key'] for r in oldscope['capped_but_window_bounded']}
    assert len(full_window_keys) == 2
    full = bounded + [r for r in inside if r['key'] in full_window_keys]
    for r in top:
        assert r['weight'] == digest[r['key']]['weight']
        assert r['key_sha256'] == hashlib.sha256(r['key'].encode()).hexdigest()
    unknown = [r for r in inside if r['final_verdict'] == 'undecided']
    new_two = [r for r in unknown if r['two_block'].get('complete') and r['two_block'].get('verdict') == 'bounded']
    new_R = [r for r in unknown if flag(r, 'R') is True]
    assert len(new_two) == 9 and {r['key'] for r in new_R} == full_window_keys
    promoted = {r['key'] for r in new_two + new_R}
    assert not ({r['key'] for r in new_two} & full_window_keys)
    known_neither = [r for r in bounded if flag(r, 'R') is False and flag(r, 'bond_pinned') is False]
    pinonly = [r for r in bounded if flag(r, 'R') is False and flag(r, 'bond_pinned') is True]
    noR = [r for r in bounded if flag(r, 'R') is False]
    exc = {r['key'] for r in load(READ / 'coverage_summary.json')['exception_only_Q_residue_families']}
    strata = {
        'order': [r for r in noR if r['stratum'] == 'O'],
        'nine_exceptions': [r for r in noR if r['key'] in exc],
        'others': [r for r in noR if r['stratum'] != 'O' and r['key'] not in exc]}
    pin_diffs = [small(r) for r in top if r['pinning'].get('plain_pinned') != r['pinning'].get('bond_pinned')]
    order = [r for r in inside if r['stratum'] == 'O']
    order_fail = [r for r in order if flag(r, 'bond_pinned') is False]
    reference_comparison = {'available': False}
    prior = READ / 'coverage_results.jsonl'
    if (ROOT / prior).exists():
        reference = {r['key']: r for r in rows(prior)}
        mismatches = []
        compared = 0
        for r in inside:
            ref = reference[r['key']]['R']
            if ref is not None:
                compared += 1
                if bool(ref['exists_good_each_Q_residue']) != flag(r, 'R'):
                    mismatches.append({'sha': r['key_sha256'][:12],
                                       'old_Q': ref['exists_good_each_Q_residue'],
                                       'top_R': flag(r, 'R')})
        reference_comparison = {'available': True, 'compared': compared, 'mismatches': mismatches}
    result = {
        'scope': 'referee-only; no scientific lifecycle or publication mutations',
        'population': tally(top), 'in_scope': tally(inside),
        'advertised_outcomes': dict(collections.Counter(r['final_verdict'] for r in inside)),
        'strict_split': partition(strict), 'advertised_split': partition(bounded),
        'full_certificate_split': partition(full),
        'historical_counts': {name:{'bounded':len(rs),'growing':632,
             'undecided':len(inside)-len(rs)-632} for name,rs in
             (('strict_complete_row',strict),('advertised_primary_path_admission',bounded),
              ('all_valid_primary_certificates',full))},
        'path_additions': pathadds,
        'incomplete_path_admissions': [small(r) for r in bounded if r['key'] in incomplete_path],
        'R_rescues_already_certified_by_CARRY': [small(r) | {
            'Q_preperiod': digest[r['key']]['preperiod'], 'Q_period': digest[r['key']]['period'],
            'U_by_s': digest[r['key']]['U_by_s'], 'caps': digest[r['key']]['caps'],
            'absolute_threshold': digest[r['key']]['preperiod']+int(digest[r['key']]['wrapper'])}
            for r in new_R],
        'new_two_block_bounds': [small(r) | {'maximum': r['two_block']['maximum'],
            'preperiod': r['two_block']['preperiod'], 'period': r['two_block']['period'],
            'wrapper': r['two_block']['wrapper'], 'residues': r['two_block']['residues']}
            for r in new_two],
        'new_final_counts': {'bounded': len(bounded)+len(promoted),
            'growing': sum(r['final_verdict']=='growing' for r in inside),
            'undecided': len(unknown)-len(promoted)},
        'new_final_weights': {'bounded': sum(r['weight'] for r in bounded)+sum(r['weight'] for r in unknown if r['key'] in promoted),
            'growing': sum(r['weight'] for r in inside if r['final_verdict']=='growing'),
            'undecided': sum(r['weight'] for r in unknown if r['key'] not in promoted)},
        'no_R_confirmed': tally(noR), 'no_R_partition': {k:tally(v) for k,v in strata.items()},
        'pinning_only_rows': [small(r) for r in pinonly],
        'pinning_only_by_stratum':{s:tally([r for r in pinonly if r['stratum']==s]) for s in ('I','O','X','T')},
        'residual_65_covered_by_phasewise_R_or_pinning': [small(r) for r in known_neither
            if r['pinning']['residues'] and all(p['R_applies'] or p['bond_pinned'] for p in r['pinning']['residues'])],
        'middle_label_rows': [small(r) for r in known_neither],
        'plain_vs_bond_disagreements_in_supplied_flags': pin_diffs,
        'order': tally(order), 'order_not_pinned': [small(r) for r in order_fail],
        'comparison_with_earlier_referee_R_flags': reference_comparison,
        'path_source_rows': len(pathdata), 'inputs_sha256': READS,
        'seconds': time.monotonic()-start, 'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}
    assert len(inside)==5789 and len(bounded)==5074 and len(strict)==5072 and len(full)==5076
    assert len(known_neither)==65 and len(pinonly)==523
    assert len(noR)==588 and sum(len(v) for v in strata.values())==588
    assert result['advertised_split']['overlap_R_and_pinning']['families']==3515
    (HERE / 'counts_results.json').write_text(json.dumps(result, indent=2, sort_keys=True)+'\n')
    # Deterministic panel sorted by expanding cost; do not choose by the
    # location or size of a subsequently discovered bond.
    inputs = []
    for r in known_neither:
        rr = reach[r['key']]
        inputs.append(small(r) | {'S':rr['S'], 's_block_size':rr['s_block_size'],
            'main_block_size':rr['main_block_size'], 'wrapper':digest[r['key']]['wrapper'],
            'calls':digest[r['key']]['c'], 'period':digest[r['key']]['period'],
            'preperiod':digest[r['key']]['preperiod'], 'U_by_s':digest[r['key']]['U_by_s']})
    inputs.sort(key=lambda r:(r['s_block_size'],r['calls'],r['main_block_size'],r['key']))
    (HERE/'middle_inputs.json').write_text(json.dumps(inputs,indent=2,sort_keys=True)+'\n')
    print(json.dumps({k:result[k] for k in ('strict_split','advertised_split','full_certificate_split','new_final_counts','new_final_weights','no_R_confirmed','no_R_partition','comparison_with_earlier_referee_R_flags')},indent=2))
    print('smallest_middle',json.dumps([{k:r[k] for k in ('key_sha256','stratum','s_block_size','calls','wrapper','preperiod','period')} for r in inputs[:20]]))


if __name__ == '__main__':
    main()
