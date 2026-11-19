"""CENSUS-READ-20261118-001A readout of pass 5 (Amendment 5: exact tables v2, R3 and R3n v2, renamings, horizons, symmetries).
Run: .venv/bin/python -B readout5.py runs/census-exact5  -> summary_pass5.json beside the artifacts."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def two(st):
    return st['max_shared'] >= 2


def rigid(st):
    return st['connectivity'] == 'three' and not two(st)


def sym(st):
    s = st.get('symmetry', {})
    if s.get('twins_across_junctions') or s.get('search') == 'moves':
        return 'moves'
    return s.get('search', 'not_checked')


def band(st):
    n = st['junctions']
    return 'at_most_14' if n <= 14 else ('15_to_40' if n <= 40 else '41_to_120')


def least_rel(stages, rd, pick):
    rel = Counter()
    for a, st in stages:
        if st[rd] == 'exact' and pick(st):
            h = st.get(rd + '_least_horizon')
            rel['none' if h is None else h - (st['largest'] - 1)] += 1
    return {str(k): v for k, v in sorted(rel.items(), key=lambda kv: str(kv[0]))}


def split(stages, rd, keyf):
    out = defaultdict(Counter)
    for a, st in stages:
        out[keyf(st)][st[rd]] += 1
    return {k: dict(v) for k, v in sorted(out.items())}


def main(out_dir):
    recs = load_results(out_dir)
    arrs, mixed = [], []
    for cid, r in sorted(recs.items()):
        if r['status'] != 'ok':
            continue
        (arrs.extend(r['result']['arrangements']) if cid.startswith('census') else mixed.append(r['result']))
    s = {'case_status': dict(Counter(r['status'] for r in recs.values())), 'arrangements': len(arrs),
         'arrangements_sampled_beyond_40': sum(1 for a in arrs if a['sampled_beyond_40']), 'mixed_seeds': len(mixed)}
    stages = [(a, st) for a in arrs for st in a['stages']]
    s['stages'] = len(stages)
    s['stages_by_band'] = dict(Counter(band(st) for a, st in stages))
    s['outcomes'] = dict(Counter(a['outcome'] for a in arrs))
    s['arrangements_whose_start_shares_two'] = sum(1 for a in arrs if two(a['stages'][0]))
    s['connectivity_of_stages'] = dict(Counter(st['connectivity'] for a, st in stages))
    s['stages_sharing_two'] = sum(1 for a, st in stages if two(st))
    s['rigid_stages'] = sum(1 for a, st in stages if rigid(st))
    s['symmetry_of_stages'] = dict(Counter(sym(st) for a, st in stages))
    for rd in ('r3', 'r3n'):
        s[f'{rd}_verdicts'] = dict(Counter(st[rd] for a, st in stages))
        s[f'{rd}_verdicts_no_pair_sharing_two'] = dict(Counter(st[rd] for a, st in stages if not two(st)))
        s[f'{rd}_verdicts_rigid'] = dict(Counter(st[rd] for a, st in stages if rigid(st)))
        s[f'{rd}_by_connectivity_no_sharing_two'] = split([(a, st) for a, st in stages if not two(st)], rd, lambda st: st['connectivity'])
        s[f'{rd}_by_symmetry_no_sharing_two'] = split([(a, st) for a, st in stages if not two(st)], rd, sym)
        s[f'{rd}_by_band_no_sharing_two'] = split([(a, st) for a, st in stages if not two(st)], rd, band)
        s[f'{rd}_by_round_no_sharing_two'] = split([(a, st) for a, st in stages if not two(st)], rd, lambda st: st['round'])
    s['r3n_no_sharing_two_symmetry_fixes_rigid'] = dict(Counter(st['r3n'] for a, st in stages
                                                             if not two(st) and sym(st) == 'fixes' and st['connectivity'] == 'three'))
    s['r3n_no_sharing_two_symmetry_fixes_any'] = split([(a, st) for a, st in stages if not two(st) and sym(st) == 'fixes'], 'r3n',
                                                       lambda st: st['connectivity'])
    # frozen predictions (post-hoc on the corrected instruments)
    s['C1_r3_rigid_not_exact_or_swap'] = sum(1 for a, st in stages if rigid(st) and st['r3'] not in ('exact', 'outside_swap'))
    s['C1b_r3_misreads_no_pair_sharing_two'] = sum(1 for a, st in stages if not two(st) and st['r3'] == 'misread')
    arr_two = [a for a in arrs if any(two(st) for st in a['stages'])]
    s['C2_arrangements_sharing_two'] = len(arr_two)
    s['C2_of_those_with_an_r3_misread'] = sum(1 for a in arr_two if any(st['r3'] == 'misread' for st in a['stages']))
    s['C3_r3_same_states_at_three_connected'] = sum(1 for a, st in stages if st['connectivity'] == 'three' and st['r3'] == 'same_states')
    s['C3_r3n_same_states_at_three_connected'] = sum(1 for a, st in stages if st['connectivity'] == 'three' and st['r3n'] == 'same_states')
    s['C4_r3_rigid_least_minus_largest_less_one'] = least_rel(stages, 'r3', rigid)
    s['N3_r3n_stages_changed_by_renaming'] = sum(1 for a, st in stages if any(v != st['r3n'] for v in st['r3n_renamed']))
    s['N4_r3n_rigid_not_exact_or_swap'] = sum(1 for a, st in stages if rigid(st) and st['r3n'] not in ('exact', 'outside_swap'))
    s['N4_r3n_rigid_least_minus_largest_less_one'] = least_rel(stages, 'r3n', rigid)
    s['N5_r3_stages_changed_by_renaming'] = sum(1 for a, st in stages if any(v != st['r3'] for v in st['r3_renamed']))
    s['N5_fraction'] = round(s['N5_r3_stages_changed_by_renaming'] / max(1, len(stages)), 5)
    s['r3n_flags_total'] = dict(sum((Counter(st.get('r3n_flags', {})) for a, st in stages), Counter()))
    # the owner's question: how far must the reader look, against the largest junction
    for rd in ('r3', 'r3n'):
        s[f'{rd}_all_least_minus_largest_less_one'] = least_rel(stages, rd, lambda st: True)
        by_largest = defaultdict(Counter)
        for a, st in stages:
            if st[rd] == 'exact' and st.get(rd + '_least_horizon') is not None:
                by_largest[st['largest']][st[rd + '_least_horizon']] += 1
        s[f'{rd}_least_horizon_by_largest'] = {str(k): dict(sorted(v.items())) for k, v in sorted(by_largest.items())}
    # what the misreads share
    for rd in ('r3', 'r3n'):
        mis = [(a, st) for a, st in stages if st[rd] == 'misread']
        s[f'{rd}_misreads'] = {
            'stages': len(mis), 'sharing_two': sum(1 for a, st in mis if two(st)),
            'no_sharing_two_by_connectivity': dict(Counter(st['connectivity'] for a, st in mis if not two(st))),
            'no_sharing_two_by_symmetry': dict(Counter(sym(st) for a, st in mis if not two(st))),
            'min_distance': dict(Counter(st['min_distance'] for a, st in mis)),
            'missed_extra_no_sharing_two': {f'{m}/{e}': c for (m, e), c in Counter(
                (st.get(rd + '_missed'), st.get(rd + '_extra')) for a, st in mis if not two(st)).most_common(10)},
            'examples_rigid_symmetry_fixes': [[a['key'], st['round']] for a, st in mis
                                             if rigid(st) and sym(st) == 'fixes'][:6]}
    mst = [st for m in mixed for st in m['stages']]
    s['mixed_stages'] = len(mst)
    s['C0a_fresh_reader_verdicts'] = dict(Counter(st['fresh_reader'] for st in mst))
    for rd in ('r3', 'r3n'):
        s[f'C5_{rd}_mixed'] = dict(Counter(st[rd] for st in mst))
        s[f'C5_{rd}_on_fresh_misreads'] = dict(Counter(st[rd] for st in mst if st['fresh_reader'] == 'misread'))
    s['C5_mixed_connectivity'] = dict(Counter(st['connectivity'] for st in mst))
    s['C5_mixed_symmetry'] = dict(Counter(sym(st) for st in mst))
    s['C5_r3n_mixed_by_symmetry'] = {k: dict(Counter(st['r3n'] for st in mst if sym(st) == k)) for k in sorted({sym(st) for st in mst})}
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    (dest / 'summary_pass5.json').write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
