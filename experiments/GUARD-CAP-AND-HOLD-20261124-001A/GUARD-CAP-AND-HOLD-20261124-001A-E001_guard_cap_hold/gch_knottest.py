"""Run 5, the knot test.

1. Every knot of the reference structure after its last compared round (the gate's last round for the pair), for
   every start and law: parity by both methods of the reference engine (ranks and cut), and, for structures of up to
   600 knots, not-all-equal, with the births of every round under not-all-equal compared with parity's (parents, D,
   f, usable, barred).
2. Every knot made at a mismatch, in the structure in which it was made: the run's own structure, rebuilt with real
   distinctions from the least mismatching order of each run (births and barrings as listed), tested by both parity
   methods and, up to 600 knots, by not-all-equal.

    python -B gch_knottest.py        # reads gate.json and runs/*.json, writes knot_test.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import lr_core as C  # noqa: E402
import lr_reference as RF  # noqa: E402
from gch_configs import NAMES  # noqa: E402

E = RF.E
ART = HERE.parents[2] / 'artifacts' / 'GUARD-CAP-AND-HOLD-20261124-001A' / \
    'GUARD-CAP-AND-HOLD-20261124-001A-E001_guard_cap_hold'


def births_key(rec):
    return sorted((tuple(sorted(b['parents'])), b['D'], b['f'], b['usable'], b['barred']) for b in rec['births'])


def reference_tests():
    gate = json.loads((ART / 'gate.json').read_text())
    out = []
    for p in gate['pairs']:
        fam = NAMES[p['law']]
        rounds = p['rounds_checked']
        stars = C.start_stars(p['start'])
        S = E.from_stars(stars)
        Sn = E.from_stars(stars)
        lp = RF.ref_law(*fam)
        ln = RF.ref_law(*fam, knot_law='nae')
        same_births = True
        for t in range(rounds):
            S, rp = E.round_step(S, lp)
            Sn, rn = E.round_step(Sn, ln)
            if births_key(rp) != births_key(rn):
                same_births = False
        t0 = time.time()
        par = E.parity_knot_test(S)
        row = {'start': p['start'], 'law': p['law'], 'after_round': rounds, 'knots': S.n_knots,
               'parity_all_pass': par['all_pass'], 'parity_methods_disagree': par['disagree'],
               'parity_rank_fail': par['rank_fail'], 'parity_cut_fail': par['cut_fail']}
        if S.n_knots <= 600:
            nae = E.nae_knot_test(Sn)
            row.update({'nae_births_equal_parity': same_births, 'nae_all_pass': nae['all_pass'],
                        'nae_fail': nae['fail'], 'nae_sat_calls': nae['sat_calls']})
        else:
            row['nae'] = 'not run (more than 600 knots)'
        row['seconds'] = round(time.time() - t0, 2)
        out.append(row)
        print(row, flush=True)
    return out


def rebuild(stars, listing):
    """The run's own structure from a listing: births with their images and counts, barrings."""
    S = E.from_stars(stars)
    img = {u: u for u in range(S.n_knots)}
    last = None
    for row in listing:
        if 'barring' in row:
            if row.get('matches') is False:
                return S, None
            k = img[row['image']]
            for d in S.usable(k):
                S.barred[d] = True
            continue
        if row.get('allowed') is False:
            return S, None
        parents = [img[q] for q in row['parents_images']]
        taken = [S.usable(q)[0] for q in parents]
        x = S._new_knot(taken, parents, 0, 0)
        S._give_fresh(x, row['usable_fresh'], row['fresh'] - row['usable_fresh'])
        if row.get('matches_reference_knot') is not None:
            img[row['matches_reference_knot']] = x
        last = x
    return S, last


def mismatch_tests():
    out = []
    for f in sorted((ART / 'runs').glob('*.json')):
        x = json.loads(f.read_text())
        ld = x.get('least_differing_order')
        if not ld or not ld.get('listing'):
            continue
        rows = ld['listing']
        lastb = [r for r in rows if 'birth' in r]
        if not lastb or lastb[-1].get('matches_reference_knot') is not None:
            continue     # the order ends at a barring that mismatches: no knot is made there
        S, k = rebuild(C.start_stars(x['start']), rows)
        if k is None:
            continue
        par = E.parity_knot_test(S)
        row = {'run': x['id'], 'births': ld['births'], 'exact': ld.get('exact'), 'knot': k, 'knots': S.n_knots,
               'parity_rank_pass': k not in par['rank_fail'], 'parity_cut_pass': k not in par['cut_fail'],
               'parity_all_knots_pass': par['all_pass']}
        if S.n_knots <= 600:
            nae = E.nae_knot_test(S, knots=[k])
            row['nae_pass'] = nae['all_pass']
        out.append(row)
    return out


def main():
    t0 = time.time()
    res = {'reference': reference_tests()}
    res['mismatch_knots'] = mismatch_tests()
    res['summary'] = {
        'reference_structures': len(res['reference']),
        'reference_all_parity_pass': all(r['parity_all_pass'] for r in res['reference']),
        'reference_parity_methods_agree': all(not r['parity_methods_disagree'] for r in res['reference']),
        'reference_nae_tested': sum(1 for r in res['reference'] if 'nae_all_pass' in r),
        'reference_all_nae_pass': all(r.get('nae_all_pass', True) for r in res['reference']),
        'nae_births_equal_parity': all(r.get('nae_births_equal_parity', True) for r in res['reference']),
        'mismatch_knots_tested': len(res['mismatch_knots']),
        'mismatch_knots_parity_pass': sum(1 for r in res['mismatch_knots']
                                          if r['parity_rank_pass'] and r['parity_cut_pass']),
        'mismatch_knots_nae_pass': sum(1 for r in res['mismatch_knots'] if r.get('nae_pass')),
        'mismatch_structures_all_knots_parity_pass': sum(1 for r in res['mismatch_knots']
                                                         if r['parity_all_knots_pass']),
        'seconds': round(time.time() - t0, 1)}
    (ART / 'knot_test.json').write_text(json.dumps(res, indent=1, default=str) + '\n')
    print(res['summary'])


if __name__ == '__main__':
    main()
