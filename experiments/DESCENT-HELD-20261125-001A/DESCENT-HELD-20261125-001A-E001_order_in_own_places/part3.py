"""Part 3: M1, the ten lone-knot structures (DH 5.1-5.2; P1).  Writes part3.json.  Readings: deviations 18 (M1 law).

The structure: DH 4.4's part {the start knot, its first offshoot in DH 1.4's order} after round 1.  The renaming: searched
over every renaming of knots and distinctions that keeps every mark and which places are one distinction (a search over
all bijections of distinctions, pruned only by those constraints), then checked place by place.
"""
from __future__ import annotations

import time

from dh_common import LAWS_JSON, write, log
import dh_engine as E
from part2 import part_structure


def renamings(places, holders_in, barred):
    """Every renaming (pi on knots, sigma on distinctions) with sigma(places(u)) = places(pi(u)) and marks kept."""
    n = len(places)
    m = len(holders_in)
    import itertools
    out = []
    mark = {d: ('b' if d in barred else ('l' if len(holders_in[d]) == 1 else 's')) for d in holders_in}
    for pi in itertools.permutations(range(n)):
        if any(len(places[u]) != len(places[pi[u]]) for u in range(n)):
            continue
        sigma = {}
        used = set()
        ds = sorted(holders_in)

        def ok(d, e):
            if mark[d] != mark[e]:
                return False
            return sorted(pi[h] for h in holders_in[d]) == sorted(holders_in[e])

        def bt(i):
            if i == len(ds):
                out.append((pi, dict(sigma)))
                return
            d = ds[i]
            for e in ds:
                if e in used or not ok(d, e):
                    continue
                sigma[d] = e
                used.add(e)
                bt(i + 1)
                used.discard(e)
                del sigma[d]
        bt(0)
    return out


def case(ration, a, form):
    L = E.Law(ration, ration, 'CANCEL-WAIT', 'RELEASE')
    S, recs, end = E.grow([list(range(a))], L, form, 'parity', R=1, N=10 ** 9)
    x = recs[0]['new'][0]
    pl, hi, ba = part_structure(S, [0, x], 1)
    shared = [d for d, h in hi.items() if len(h) == 2]
    assert len(shared) == 1
    d0 = shared[0]
    rs = renamings(pl, hi, ba)
    swaps = [(pi, sg) for pi, sg in rs if pi == (1, 0) and sg[d0] == d0]
    # place by place: the offshoot's place to its parent (knot 1, distinction d0) goes to the start knot's place to its
    # child (knot 0, d0), and every place goes to a place of the same mark
    checked = 0
    for pi, sg in swaps:
        good = all(sg[d] in pl[pi[u]] for u in range(2) for d in pl[u]) and sg[d0] == d0
        checked += good
    return {'ration': ration, 'a': a, 'form': E.FORM_NAMES[form], 'F_1_a-1': E.fresh(ration, 1, a - 1),
            'offshoot_D': S.D[x], 'offshoot_places': len(S.places[x]), 'offshoot_barred': S.z[x], 's': S.s[x],
            'start_knot_places': len(pl[0]), 'renamings_of_the_structure': len(rs),
            'renamings_exchanging_the_two_knots': len(swaps), 'checked_place_by_place': checked,
            'exists': len(swaps) > 0}


def main():
    t0 = time.time()
    rows = []
    for ration, avals in LAWS_JSON['lone_knot_rations'].items():
        for a in avals:
            for form in (None,) + E.FORMS:
                rows.append(case(ration, a, form))
    base = [r for r in rows if r['form'] == 'base']
    forms = [r for r in rows if r['form'] != 'base']
    out = {'part': 3, 'cases': len(base), 'rows': rows,
           'base_exists': sum(r['exists'] for r in base), 'forms_exist': sum(r['exists'] for r in forms),
           'P1': all(r['exists'] for r in base) and not any(r['exists'] for r in forms),
           'seconds': round(time.time() - t0, 1)}
    write('part3.json', out)
    log('part 3', out['cases'], out['base_exists'], out['forms_exist'], out['P1'], out['seconds'])


if __name__ == '__main__':
    main()
