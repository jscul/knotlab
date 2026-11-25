"""A labelled check, outside the registered runs: PR Known 3's start-by-start table on the drafter's 64 starts
(random.Random(20261125).sample of the 3,376 in file order), 40 rounds, 50,000 knots, births read by KD 3.2, under the
seven laws of its table; with the start-by-start statements of Known 3.  Writes check_known3.json."""
from collections import Counter

import kwr
import readings as RD


def deg(v):
    if v is None:
        return 'ended'
    if v['verdict'] == 'POWER':
        return 'degree %d' % v['j']
    if v['verdict'] == 'ENDED':
        return 'ended'
    return RD.label(v)


def main():
    kwr.cap_memory(6)
    sc = sorted(kwr.scratch64())
    laws = ('L0', 'L9', 'L10', 'L6', 'L11', 'L7', 'L1')
    res = {}
    for i in sc:
        for lab in laws:
            g = kwr.Grown('census:%d' % i, kwr.make_law(lab), 40, parts_every_round=False)
            v = RD.read(g.births(), 1, ended=g.ended is not None, kind='b') if g.births() else None
            res['%d %s' % (i, lab)] = {'reading': deg(v), 'rounds': g.rounds_done, 'stop': g.stop}
    table = {lab: dict(Counter(res['%d %s' % (i, lab)]['reading'] for i in sc)) for lab in laws}
    ended0 = [i for i in sc if res['%d L0' % i]['reading'] == 'ended']
    st = {'L0 ended -> L9': dict(Counter(res['%d L9' % i]['reading'] for i in ended0)),
          'L0 degree 2': {str(i): {lab: res['%d %s' % (i, lab)]['reading'] for lab in laws} for i in sc
                          if res['%d L0' % i]['reading'] == 'degree 2'},
          'L9 degree 1 -> L6': dict(Counter(res['%d L6' % i]['reading'] for i in sc
                                            if res['%d L9' % i]['reading'] == 'degree 1')),
          'L9 degree 0 -> L6': dict(Counter(res['%d L6' % i]['reading'] for i in sc
                                            if res['%d L9' % i]['reading'] == 'degree 0'))}
    kwr.write_json(kwr.out_path('check_known3.json'), {'table': table, 'statements': st, 'runs': res})
    for lab in laws:
        print(lab, table[lab])
    for k, v in st.items():
        print(k, v)


if __name__ == '__main__':
    main()
