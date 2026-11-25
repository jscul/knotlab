"""Diagnostic after part 1 (deviations 30): which reading of "right on every structure" gives the scratch joint strata.
Re-runs only the census arm-W runs that have a closing birth (all others are unaffected by the closing knot's places)
and counts each run under three readings: (L) every place (deviations 10, the registered reading of this run);
(X1) the closing knot's own places left out (DH 3.2 step 5, "the place rule is not claimed at its places");
(X2) both places of every distinction the closing knot holds left out.  Writes part1_joint_closing.json.
"""
from __future__ import annotations

import gzip
import json
import os

from dh_common import OUT, write, log
import dh_engine as E
from dh_census import census


def readings(S, form):
    closing = {x for x in range(len(S.places)) if S.closing[x]}
    pr = E.place_rule(S, form, keep_wrong=10 ** 9)
    wl = pr['wrong_list']
    L = len(wl) == 0
    X1 = all(x in closing for (d, x, y, k) in wl)
    X2 = all(x in closing or y in closing for (d, x, y, k) in wl)
    return L, X1, X2, len(wl), sum(1 for (d, x, y, k) in wl if x in closing)


def main():
    with gzip.open(os.path.join(OUT, 'part1_runs.json.gz'), 'rt') as f:
        raw = json.load(f)
    C = census()
    out = {}
    for L_ in E.RELEASE_BASES:
        for form in E.FORMS:
            key = L_.name + '|' + form
            base_joint = 0
            gained_X1, gained_X2 = [], []
            for r in raw['census_rows']:
                if not r['kept']:
                    continue
                w = r['armw'][key]
                if w['right_on_every_structure']:
                    base_joint += 1
                    continue
                if not w['closing_births'] or w['every_round_checked'] if 'every_round_checked' in w else False:
                    pass
                if not w['closing_births']:
                    continue
                S, recs, end = E.grow(C[r['idx']][3], L_, form, 'parity', R=8, N=3000)
                if form == 'BB' and any(S.ret):
                    # with retiring, every round would need checking; the closing runs here are tiny, check each round
                    ok1 = ok2 = True
                    closing = {x for x in range(len(S.places)) if S.closing[x]}
                    for t in range(S.round + 1):
                        wl = E.place_rule(S, form, t=t, keep_wrong=10 ** 9)['wrong_list']
                        ok1 = ok1 and all(x in closing for (d, x, y, k) in wl)
                        ok2 = ok2 and all(x in closing or y in closing for (d, x, y, k) in wl)
                    X1, X2 = ok1, ok2
                else:
                    _, X1, X2, nw, nwc = readings(S, form)
                if X1:
                    gained_X1.append(r['idx'])
                if X2:
                    gained_X2.append(r['idx'])
            out[key] = {'joint_every_place (deviations 10)': base_joint,
                        'joint_closing_knot_own_places_left_out': base_joint + len(gained_X1),
                        'joint_both_places_of_closing_knot_left_out': base_joint + len(gained_X2),
                        'starts_gained_X1': gained_X1, 'starts_gained_X2': gained_X2}
            log(key, out[key]['joint_every_place (deviations 10)'], out[key]['joint_closing_knot_own_places_left_out'],
                out[key]['joint_both_places_of_closing_knot_left_out'])
    write('part1_joint_closing.json', {'by_law_form': out})


if __name__ == '__main__':
    main()
