"""Run item 1, the gate (LR section 4): this study's own complete rounds against the reference engine.

For every start and law of the runs, after each round 1 to R (R the largest last round any registered cutoff
needs, and at least 5, fewer where the growth has stopped), the incidence structure of knots and distinctions
of the two engines must be exactly isomorphic, knots coloured by round of birth and distinctions by barred
or not.  An isomorphism is accepted only after it has been verified edge by edge.  Five deliberately altered
controls must be rejected.

    python -B lr_gate.py            # writes artifacts/.../gate.json
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import lr_core as C
import lr_reference as RF
from lr_configs import gate_pairs

HERE = Path(__file__).resolve().parent
TICKET_C = HERE.parents[1] / 'RING-IN-BALANCE-20261123-001C' / 'RING-IN-BALANCE-20261123-001C-E001_no_round'
sys.path.insert(0, str(TICKET_C))
import iso  # noqa: E402  (ticket C's exact isomorphism test, read-only reuse)

OUT = HERE.parents[2] / 'artifacts' / HERE.parent.name / HERE.name


def graph_own(S, recolour=None):
    n = len(S.places)
    born = list(S.born)
    if recolour:
        for x, b in recolour.items():
            born[x] = b
    col = [iso.stable_int(('k', born[x])) for x in range(n)]
    adj = [[] for _ in range(n)]
    lev = list(born)
    for d, hs in enumerate(S.holders):
        j = len(col)
        col.append(iso.stable_int(('d', bool(S.barred[d]) and len(hs) == 1)))
        adj.append([])
        lev.append(None)
        for x in hs:
            adj[x].append(j)
            adj[j].append(x)
    return iso.Graph(col, adj, lev)


def graph_ref(S):
    n = S.n_knots
    col = [iso.stable_int(('k', S.made[x])) for x in range(n)]
    adj = [[] for _ in range(n)]
    lev = [S.made[x] for x in range(n)]
    for d, hs in enumerate(S.holders):
        j = len(col)
        col.append(iso.stable_int(('d', bool(S.barred[d]) and len(hs) == 1)))
        adj.append([])
        lev.append(None)
        for x in hs:
            adj[x].append(j)
            adj[j].append(x)
    return iso.Graph(col, adj, lev)


def compare(g1, g2):
    m = iso.isomorphism(g1, g2)
    return m is not None


def gate_pair(start, fam, rounds, max_knots=40000):
    stars = C.start_stars(start)
    law = RF.ref_law(*fam)
    Sr = RF.E.from_stars(stars)
    So = C.Str(stars)
    rows = []
    ok = True
    g0 = compare(graph_own(So), graph_ref(Sr))
    rows.append({'round': 0, 'iso': g0, 'knots': Sr.n_knots})
    ok &= g0
    for t in range(1, rounds + 1):
        Sr, rec = RF.E.round_step(Sr, law)
        C.own_round(So, *fam)
        t0 = time.time()
        same = compare(graph_own(So), graph_ref(Sr))
        rows.append({'round': t, 'iso': same, 'knots': Sr.n_knots, 'own_knots': len(So.places),
                     'births': rec['n_births'], 'seconds': round(time.time() - t0, 3)})
        ok &= same
        if rec.get('stopped') or Sr.n_knots > max_knots:
            break
    return ok, rows


def altered_controls():
    """Each altered control must be rejected at some round 1..5."""
    out = []

    def run(name, start, fam, mutate, rounds=5):
        stars = C.start_stars(start)
        law = RF.ref_law(*fam)
        Sr = RF.E.from_stars(stars)
        So = C.Str(stars)
        rejected_at = None
        for t in range(1, rounds + 1):
            Sr, rec = RF.E.round_step(Sr, law)
            g_own = mutate(So, t)
            if not compare(g_own, graph_ref(Sr)):
                rejected_at = t
                break
        out.append({'control': name, 'start': start, 'law': list(fam), 'rejected': rejected_at is not None,
                    'rejected_at_round': rejected_at})

    def hold(So, t):
        C.own_round(So, 'RATION-3', 'CANCEL-WAIT', release='HOLD')
        return graph_own(So)
    run('HOLD in place of RELEASE', 'D2(4,3)', ('RATION-3', 'CANCEL-WAIT'), hold)

    def plus_one(So, t):
        C.own_round(So, 'FLOOR1', 'CANCEL-RETIRE', fresh_override=lambda p, f: f + 1 if p >= 2 else f)
        return graph_own(So)
    run('join fresh count plus one', 'TWO-KNOT', ('FLOOR1', 'CANCEL-RETIRE'), plus_one)

    def recolour(So, t):
        C.own_round(So, 'RATION-3', 'CANCEL-WAIT')
        if t >= 2:
            x = len(So.places) - 1           # the last knot made gets the round of birth one less
            return graph_own(So, recolour={x: So.born[x] - 1})
        return graph_own(So)
    run('one knot coloured by a wrong round', 'Ring(5,3)', ('RATION-3', 'CANCEL-WAIT'), recolour)

    def flip_bar(So, t):
        C.own_round(So, 'FLOOR1', 'CANCEL-RETIRE')
        g = graph_own(So)
        if t >= 1:
            n = len(So.places)
            for d, hs in enumerate(So.holders):
                if len(hs) == 1 and not So.barred[d]:
                    g.col[n + d] = iso.stable_int(('d', True))     # one usable loose distinction shown barred
                    break
        return g
    run('one usable distinction shown barred', 'THREE-KNOT', ('FLOOR1', 'CANCEL-RETIRE'), flip_bar)

    def offshoot(So, t):
        C.own_round(So, 'RATION-3', 'CANCEL-OFFSHOOT')
        return graph_own(So)
    run('CANCEL-OFFSHOOT in place of CANCEL-WAIT', 'SCC', ('RATION-3', 'CANCEL-WAIT'), offshoot)
    return out


def main():
    t0 = time.time()
    res = {'pairs': [], 'controls': None}
    all_ok = True
    for (start, fam), cuts in sorted(gate_pairs().items()):
        Rmax = max(RF.RefData(C.start_stars(start), *fam, r).R for r in sorted(cuts))
        rounds = max(5, Rmax)
        ok, rows = gate_pair(start, fam, rounds)
        all_ok &= ok
        res['pairs'].append({'start': start, 'law': list(fam), 'cutoffs': sorted(cuts), 'R_max': Rmax,
                             'rounds_checked': rows[-1]['round'], 'pass': ok, 'rows': rows})
        print(start, fam, 'cutoffs', sorted(cuts), 'R', Rmax, 'rounds', rows[-1]['round'], 'PASS' if ok else 'FAIL',
              flush=True)
    res['controls'] = altered_controls()
    for c in res['controls']:
        print('control', c, flush=True)
    res['pass'] = all_ok and all(c['rejected'] for c in res['controls'])
    res['n_pairs'] = len(res['pairs'])
    res['n_structures_compared'] = sum(len(p['rows']) for p in res['pairs'])
    res['iso_stats'] = dict(iso.STATS)
    res['seconds'] = round(time.time() - t0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / 'gate.json').write_text(json.dumps(res, indent=1) + '\n')
    print('GATE', 'PASS' if res['pass'] else 'FAIL', res['n_pairs'], 'pairs', res['n_structures_compared'],
          'structures', res['seconds'], 's')


if __name__ == '__main__':
    main()
