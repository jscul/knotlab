"""families.py PART OUT.jsonl: the frozen test of BUILT-BINDING-20261126-001 (README.md, "Frozen").

PART built      the built ring families: R = 3 or 4 rings of n = 4, 5, 6 or 7 knots, attachments split or paired,
                links double or detour (connecting knots holding no loose distinction); ordinary parity growth, rounds
                1 to 3; at each round t >= 2 the per-ring carriers born in round t - 1 (repro.run_rings), and at every
                round 0 to 3 the start's per-ring loose groups
PART controls   on the same families: one loose distinction at one connecting knot; links removed (each connecting
                knot's link places made loose)
PART nae        the built families grown under not-all-equal: the same carrier rule, joint values by a solver
PART cuts       the referee's modification (repro_cuts) on every R = 3 family with a detour link, both cuts and the
                ordinary count
PART sampled    fresh sampled starts of 9 to 12 knots (forbid.sampled, the extension's weighting with at most 30
                distinctions, 100 each, seed 20261212 + n): on every stage of rounds 1 to 3, whether every class fact
                is a function of the start's values (origin_scan.stage_check), and every binding by the cycle test
                (built.judge, both readings) with its origin"""
import sys, json, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repro as RP, built as BU, origin_scan as OS
forbid = RP.forbid


def members():
    for R, n, attach, link in itertools.product((3, 4), (4, 5, 6, 7), ('split', 'paired'), ('double', 'detour')):
        yield '%d rings of %d, %s, %s' % (R, n, attach, link), dict(R=R, n=n, attach=attach, link=link)


def start_groups(label, S, rings, loose, law='parity', arm='ordinary', rounds=3):
    rec = {'family': label, 'law': law, 'arm': arm, 'rounds': []}; st = S
    for t in range(0, rounds + 1):
        if t:
            nxt, status, births = forbid.grown(st, law, arm)
            if status != 'funded': rec['rounds'].append({'round': t, 'end': status}); break
            st = nxt
        if len({x for r in st for x in r}) > 500: rec['rounds'].append({'round': t, 'end': 'not read'}); break
        r = RP.analyse(S, st, loose) if law == 'parity' else RP.nae_tuples(st, loose)
        r['round'] = t; rec['rounds'].append(r)
    return rec


if __name__ == '__main__':
    part, out = sys.argv[1], sys.argv[2]
    with open(out, 'w') as f:
        def put(r): f.write(json.dumps(r) + '\n'); f.flush()
        if part in ('built', 'controls', 'nae'):
            for label, kw in members():
                if part != 'controls': variants = [('', {})]
                elif kw['link'] == 'detour': variants = [(' + one loose at the middle knot of a detour', {'middle_loose': True}),
                                                         (' + links made loose', {'link': 'apart'})]
                else: variants = [(' + one loose at a connecting knot', {'one_connector_loose': True}),
                                  (' + links made loose', {'link': 'apart'})]
                for tag, extra in variants:
                    S, rings, loose = RP.rings_start(**{**kw, **extra})
                    law = 'nae' if part == 'nae' else 'parity'
                    put({'part': part, 'new carriers': RP.run_rings(label + tag, S, rings, law=law)})
                    put({'part': part, 'start groups': start_groups(label + tag, S, rings, loose, law=law)})
                    if part == 'built':               # the control where the origin test must fail: a birth's own law
                        nxt, status, births = forbid.grown(S, 'parity', 'ordinary')
                        b = next(b for b in births if b['f'] >= 2)
                        c = RP.analyse(S, nxt, [[b['fresh'][0]], list(b['fresh'][1:]), list(b['inputs'])])
                        put({'part': 'origin control', 'family': label, 'tuples': c['tuples'], 'one rule': c['one rule'],
                             'origin': c['origin']['each carrier a function of the start values'], 'facts SHORT': c['SHORT']})
        elif part == 'cuts':
            for label, kw in members():
                if kw['R'] != 3 or kw['link'] != 'detour': continue
                S, rings, loose = RP.rings_start(**kw, link_middles=True)
                for arm in ('ordinary', 'one_fewer', 'arity_floor'):
                    put({'part': part, 'start groups': start_groups(label + ', middles joined', S, rings, loose, arm=arm)})
        else:
            for n in (9, 10, 11, 12):
                for j, s in enumerate(forbid.sampled(n, 100, 20261212 + n, max_distinctions=30)):
                    S = forbid.supports_of(s); st = S; rows = []
                    for t in range(0, 4):
                        if t:
                            nxt, status, births = forbid.grown(st, 'parity', 'ordinary')
                            if status != 'funded': rows.append({'round': t, 'end': status}); break
                            st = nxt
                        if len({x for r in st for x in r}) > 300: rows.append({'round': t, 'end': 'not read'}); break
                        r = OS.stage_check(S, st) if t else {}
                        names, idx, short = BU.MC.moves_of(st); _, idx2, up = BU.T2.moves_upto(st, 5)
                        for tag, mv, ix in (('SHORT', short, idx), ('UPTO5', up, idx2)):
                            jd = BU.judge(st, mv, ix); found = []
                            for b in jd['bindings']:
                                a = RP.analyse(S, st, b['parts as distinctions'])
                                found.append({'parts': b['parts'], 'tuples': a['tuples'], 'one rule': a['one rule'], 'origin': a['origin']})
                            r['bindings, ' + tag] = found
                        r['round'] = t; rows.append(r)
                    put({'part': part, 'start': 'sampled %d-%d' % (n, j), 'rounds': rows})
