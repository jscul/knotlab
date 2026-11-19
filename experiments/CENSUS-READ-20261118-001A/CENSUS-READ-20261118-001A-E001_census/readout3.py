"""CENSUS-READ-20261118-001A readout of pass 3 (exact tables): C0(a), C1-C6, N3-N5, and C7 against pass 1.
Run: .venv/bin/python -B readout3.py runs/census-exact runs/census-read  -> summary_exact.json beside the artifacts."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402

GOOD = ('exact', 'outside_swap', 'same_states')


def collect(out_dir):
    recs = load_results(out_dir)
    arrs, mixed = [], []
    for cid, r in sorted(recs.items()):
        if r['status'] != 'ok':
            continue
        if cid.startswith('census'):
            arrs.extend(r['result']['arrangements'])
        else:
            mixed.append(r['result'])
    return recs, arrs, mixed


def two(st):
    return st['max_shared'] >= 2


def rigid(st):
    return st['connectivity'] == 'three' and not two(st)


def least_rel(stages, rd, pick):
    rel = Counter()
    for a, st in stages:
        if st[rd] == 'exact' and pick(st):
            h = st.get(rd + '_least_horizon')
            rel['none' if h is None else h - (st['largest'] - 1)] += 1
    return {str(k): v for k, v in sorted(rel.items(), key=lambda kv: str(kv[0]))}


def main(exact_dir, side_dir):
    recs, arrs, mixed = collect(exact_dir)
    s = {'case_status': dict(Counter(r['status'] for r in recs.values())), 'arrangements': len(arrs),
         'mixed_seeds': len(mixed)}
    stages = [(a, st) for a in arrs for st in a['stages']]
    s['stages'] = len(stages)
    s['stages_over_14_junctions'] = sum(1 for a, st in stages if st['junctions'] > 14)
    s['outcomes'] = dict(Counter(a['outcome'] for a in arrs))
    s['connectivity_of_stages'] = dict(Counter(st['connectivity'] for a, st in stages))
    s['stages_sharing_two'] = sum(1 for a, st in stages if two(st))
    s['rigid_stages'] = sum(1 for a, st in stages if rigid(st))
    for rd in ('r1', 'r3', 'r3m', 'r3n'):
        s[f'{rd}_verdicts'] = dict(Counter(st[rd] for a, st in stages))
        s[f'{rd}_verdicts_rigid'] = dict(Counter(st[rd] for a, st in stages if rigid(st)))
        s[f'{rd}_verdicts_by_connectivity'] = {c: dict(Counter(st[rd] for a, st in stages if st['connectivity'] == c))
                                               for c in sorted({st['connectivity'] for a, st in stages})}
        s[f'{rd}_verdicts_sharing_two'] = dict(Counter(st[rd] for a, st in stages if two(st)))
    # frozen predictions on R3 (census naming)
    s['C1_r3_rigid_not_exact_or_swap'] = sum(1 for a, st in stages if rigid(st) and st['r3'] not in ('exact', 'outside_swap'))
    s['C1b_r3_misreads_no_pair_sharing_two'] = sum(1 for a, st in stages if not two(st) and st['r3'] == 'misread')
    arr_two = [a for a in arrs if any(two(st) for st in a['stages'])]
    s['C2_arrangements_sharing_two'] = len(arr_two)
    s['C2_of_those_with_an_r3_misread'] = sum(1 for a in arr_two if any(st['r3'] == 'misread' for st in a['stages']))
    s['C2_r3m_misread_stages'] = sum(1 for a, st in stages if st['r3m'] == 'misread')
    s['C3_r3_same_states_at_three_connected'] = sum(1 for a, st in stages if st['connectivity'] == 'three' and st['r3'] == 'same_states')
    s['C4_r3_rigid_least_minus_largest_less_one'] = least_rel(stages, 'r3', rigid)
    s['C4_r3_all_least_minus_largest_less_one'] = least_rel(stages, 'r3', lambda st: True)
    grown = [a for a in arrs if len(a['stages']) > 4]
    s['C6_arrangements_past_round_3'] = len(grown)
    s['C6_with_an_r1_misread'] = sum(1 for a in grown if any(st['r1'] == 'misread' for st in a['stages']))
    # names
    s['N3_r3n_stages_changed_by_renaming'] = sum(1 for a, st in stages if any(v != st['r3n'] for v in st['r3n_renamed']))
    s['N4_r3n_rigid_not_exact_or_swap'] = sum(1 for a, st in stages if rigid(st) and st['r3n'] not in ('exact', 'outside_swap'))
    s['N4_r3n_rigid_least_minus_largest_less_one'] = least_rel(stages, 'r3n', rigid)
    s['N5_r3_stages_changed_by_renaming'] = sum(1 for a, st in stages if any(v != st['r3'] for v in st['r3_renamed']))
    s['N5_fraction'] = round(s['N5_r3_stages_changed_by_renaming'] / max(1, len(stages)), 5)
    s['r3n_flags_total'] = dict(sum((Counter(st.get('r3n_flags', {})) for a, st in stages), Counter()))
    # the owner's question on the name-free reader, every exactly read stage
    s['r3n_all_least_minus_largest_less_one'] = least_rel(stages, 'r3n', lambda st: True)
    by_largest = defaultdict(Counter)
    for a, st in stages:
        if st['r3n'] == 'exact' and st.get('r3n_least_horizon') is not None:
            by_largest[st['largest']][st['r3n_least_horizon']] += 1
    s['r3n_least_horizon_by_largest'] = {str(k): dict(sorted(v.items())) for k, v in sorted(by_largest.items())}
    # what R3n's failures share
    for rd in ('r3', 'r3n'):
        mis = [(a, st) for a, st in stages if st[rd] == 'misread']
        s[f'{rd}_misreads'] = {
            'stages': len(mis), 'arrangements': len({json.dumps(a['key']) for a, st in mis}),
            'sharing_two': sum(1 for a, st in mis if two(st)),
            'connectivity': dict(Counter(st['connectivity'] for a, st in mis)),
            'min_distance': dict(Counter(st['min_distance'] for a, st in mis)),
            'round': dict(Counter(st['round'] for a, st in mis)),
            'largest': dict(Counter(st['largest'] for a, st in mis)),
            'junctions_over_14': sum(1 for a, st in mis if st['junctions'] > 14),
            'missed_extra': dict(Counter((st.get(rd + '_missed'), st.get(rd + '_extra')) for a, st in mis).most_common(8)),
            'examples': [[a['key'], st['round']] for a, st in mis[:6]]}
    nonmis = [(a, st) for a, st in stages if st['r3n'] == 'same_states']
    s['r3n_same_states_connectivity'] = dict(Counter(st['connectivity'] for a, st in nonmis))
    # mixed stages
    mst = [st for m in mixed for st in m['stages']]
    s['mixed_stages'] = len(mst)
    s['C0a_fresh_reader_verdicts'] = dict(Counter(st['fresh_reader'] for st in mst))
    for rd in ('r3', 'r3n'):
        s[f'C5_{rd}_mixed'] = dict(Counter(st[rd] for st in mst))
        s[f'C5_{rd}_on_fresh_misreads'] = dict(Counter(st[rd] for st in mst if st['fresh_reader'] == 'misread'))
    s['C5_mixed_connectivity'] = dict(Counter(st['connectivity'] for st in mst))
    # C7: pass 1 (side-limited) against pass 3 (exact), stage by stage
    _, side_arrs, _ = collect(side_dir)
    side = {(json.dumps(a['key']), st['round']): st for a in side_arrs for st in a['stages']}
    cmp = Counter()
    for a, st in stages:
        o = side.get((json.dumps(a['key']), st['round']))
        if o is None:
            cmp['missing_in_pass_1'] += 1
            continue
        big = 'over_14' if st['junctions'] > 14 else 'at_most_14'
        cmp[f'{big}_{"same" if o["r3"] == st["r3"] else "changed"}'] += 1
    s['C7_r3_pass1_vs_exact'] = dict(cmp)
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    (dest / 'summary_exact.json').write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2])
