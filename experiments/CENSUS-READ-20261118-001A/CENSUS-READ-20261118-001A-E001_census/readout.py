"""CENSUS-READ-20261118-001A readout: scores C0(a) and C1-C6 from the shared runner's results.
Run: .venv/bin/python -B readout.py runs/census-read  -> summary.json beside the artifacts."""
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'scripts'))
from longrun import load_results  # noqa: E402


def main(out_dir):
    recs = load_results(out_dir)
    status = Counter(r['status'] for r in recs.values())
    arrs, mixed = [], []
    for cid, r in sorted(recs.items()):
        if r['status'] != 'ok':
            continue
        res = r['result']
        if cid.startswith('census'):
            arrs.extend(res['arrangements'])
        else:
            mixed.append(res)
    s = {'case_status': dict(status), 'arrangements': len(arrs), 'mixed_seeds': len(mixed)}
    stages = [(a, st) for a in arrs for st in a['stages']]
    s['stages'] = len(stages)
    s['outcomes'] = dict(Counter(a['outcome'] for a in arrs))
    two = lambda st: st['max_shared'] >= 2  # noqa: E731
    for rd in ('r1', 'r3', 'r3m'):
        s[f'{rd}_verdicts'] = dict(Counter(st[rd] for a, st in stages))
        s[f'{rd}_verdicts_one_shared'] = dict(Counter(st[rd] for a, st in stages if not two(st)))
        s[f'{rd}_verdicts_shares_two'] = dict(Counter(st[rd] for a, st in stages if two(st)))
    good = ('exact', 'outside_swap', 'same_states')
    rigid = lambda st: st['connectivity'] == 'three' and not two(st)  # noqa: E731
    s['connectivity_of_stages'] = dict(Counter(st['connectivity'] for a, st in stages))
    for rd in ('r3', 'r3m'):
        s[f'{rd}_verdicts_by_connectivity'] = {c: dict(Counter(st[rd] for a, st in stages if st['connectivity'] == c))
                                               for c in sorted({st['connectivity'] for a, st in stages})}
    # C1: rigid stages (3-connected, no pair sharing two): exact or outside swap
    s['C1_rigid_stages'] = sum(1 for a, st in stages if rigid(st))
    s['C1_r3_rigid_not_exact_or_swap'] = sum(1 for a, st in stages if rigid(st) and st['r3'] not in ('exact', 'outside_swap'))
    # C1b: every stage with no pair sharing two: same allowed states
    s['C1b_r3_misreads_no_pair_sharing_two'] = sum(1 for a, st in stages if not two(st) and st['r3'] == 'misread')
    # C2: R3m same allowed states everywhere; R3 misreads in most arrangements sharing two
    arr_two = [a for a in arrs if any(two(st) for st in a['stages'])]
    s['C2_arrangements_sharing_two'] = len(arr_two)
    s['C2_of_those_with_an_r3_misread'] = sum(1 for a in arr_two if any(st['r3'] == 'misread' for st in a['stages']))
    s['C2_r3m_misread_stages'] = sum(1 for a, st in stages if st['r3m'] == 'misread')
    # C3: at 3-connected stages every same-state non-exact output is an outside swap
    s['C3_r3_same_states_at_three_connected'] = sum(1 for a, st in stages if st['connectivity'] == 'three' and st['r3'] == 'same_states')
    s['C3_r3m_same_states_at_three_connected'] = sum(1 for a, st in stages if st['connectivity'] == 'three' and st['r3m'] == 'same_states')
    swaps = [st for a, st in stages if st['r3'] == 'outside_swap']
    s['outside_swaps_r3'] = len(swaps)
    s['outside_swap_loose_minus_largest'] = dict(Counter(st['loose'] - st['largest'] for st in swaps))
    # C4: least horizon at rigid exactly read stages; also everywhere
    for rd in ('r3', 'r3m'):
        for scope, pick in (('rigid', rigid), ('all', lambda st: True)):
            rel = Counter()
            nonmono = 0
            for a, st in stages:
                if st[rd] == 'exact' and pick(st):
                    h = st.get(rd + '_least_horizon')
                    rel['none' if h is None else h - (st['largest'] - 1)] += 1
                    nonmono += not st.get(rd + '_monotone', True)
            s[f'C4_{rd}_{scope}_least_horizon_minus_largest_less_one'] = {str(k): v for k, v in sorted(rel.items(), key=lambda kv: str(kv[0]))}
            s[f'C4_{rd}_{scope}_nonmonotone_stages'] = nonmono
    by_largest = defaultdict(Counter)
    for a, st in stages:
        if st['r3'] == 'exact' and st.get('r3_least_horizon') is not None:
            by_largest[st['largest']][st['r3_least_horizon']] += 1
    s['C4_r3_least_horizon_by_largest'] = {str(k): dict(v) for k, v in sorted(by_largest.items())}
    # C5 and C0(a)
    mst = [st for m in mixed for st in m['stages']]
    s['mixed_stages'] = len(mst)
    s['C0a_fresh_reader_verdicts'] = dict(Counter(st['fresh_reader'] for st in mst))
    s['C5_r3_verdicts_mixed'] = dict(Counter(st['r3'] for st in mst))
    s['C5_r3m_verdicts_mixed'] = dict(Counter(st['r3m'] for st in mst))
    s['C5_r3_on_the_fresh_misreads'] = dict(Counter(st['r3'] for st in mst if st['fresh_reader'] == 'misread'))
    s['C5_mixed_connectivity'] = dict(Counter(st['connectivity'] for st in mst))
    # C6
    grown = [a for a in arrs if len(a['stages']) > 4]
    s['C6_arrangements_past_round_3'] = len(grown)
    s['C6_with_an_r1_misread'] = sum(1 for a in grown if any(st['r1'] == 'misread' for st in a['stages']))
    # what the R3 misreads share
    mis = [(a, st) for a, st in stages if st['r3'] == 'misread']
    s['r3_misreads'] = {
        'stages': len(mis), 'arrangements': len({tuple(map(tuple, a['key'])) for a, st in mis}),
        'shares_two': sum(1 for a, st in mis if two(st)), 'connectivity': dict(Counter(st['connectivity'] for a, st in mis)),
        'table_complete': sum(1 for a, st in mis if st['table_complete']), 'min_distance_hist': dict(Counter(st['min_distance'] for a, st in mis)),
        'round_hist': dict(Counter(st['round'] for a, st in mis)), 'largest_hist': dict(Counter(st['largest'] for a, st in mis)),
        'knots_hist': dict(Counter(a['knots'] for a, st in mis))}
    mis_m = [(a, st) for a, st in stages if st['r3m'] == 'misread']
    s['r3m_misreads'] = {
        'stages': len(mis_m), 'arrangements': len({tuple(map(tuple, a['key'])) for a, st in mis_m}),
        'shares_two': sum(1 for a, st in mis_m if two(st)), 'connectivity': dict(Counter(st['connectivity'] for a, st in mis_m)),
        'table_complete': sum(1 for a, st in mis_m if st['table_complete']), 'min_distance_hist': dict(Counter(st['min_distance'] for a, st in mis_m)),
        'round_hist': dict(Counter(st['round'] for a, st in mis_m)), 'examples': [a['key'] for a, st in mis_m[:5]]}
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'summary.json').write_text(json.dumps(s, indent=1))
    print(json.dumps(s, indent=1))


if __name__ == '__main__':
    main(sys.argv[1])
