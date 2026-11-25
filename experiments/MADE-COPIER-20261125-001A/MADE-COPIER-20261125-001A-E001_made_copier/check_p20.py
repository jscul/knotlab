"""P20's two clauses, on the smallest second pattern of the registered class that P6's case fails on (one member
holding two, ystart-one-2), under the case's law (COPY-LAW(CANCEL-OFFSHOOT), MET(NEWEST), parity); and, beside it, the
same reading on the case itself (ystart-three-222).

usage: python -B check_p20.py
"""
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def read(name):
    d = mc.design(name)
    law = mc.make_law('COPY-LAW(OFFSHOOT)', 'MET', 'NEWEST', 'parity')
    A = mc.grow(d, law)
    S0 = A.snap[0]
    nd0 = S0.n_distinctions
    out = {'design': name, 'rounds': A.rounds_done, 'knot fails': mc.knot_tests_A(A)['n_fails']}
    # round 3: the takes of births descended from X only
    S3 = A.snap[3]
    desc3 = mc.descent_map(S3, d.X, d.Y, 0)
    takes = []
    for b in A.records[2]['births']:
        if desc3.get(b['id']) == 'X only' and b['rule_takes']:
            for x in b['rule_takes']:
                mk = A.snap[2].holders[x][0] if A.snap[2].holders[x] else None
                takes.append({'birth': b['id'], 'kind': b['kind'], 'took': x,
                              'its maker': mk, 'maker descent': desc3.get(mk),
                              'made by a birth (not a start distinction)': x >= nd0})
    out['round 3: takes of births descended from X only'] = takes
    # after round 6: X's usable loose made distinctions and the start distinctions they are tied to
    S6 = A.snap[A.rounds_done]
    desc6 = mc.descent_map(S6, d.X, d.Y, 0)
    T = mc.ties_parity(S6)
    rows = []
    for f in range(nd0, S6.n_distinctions):
        if len(S6.holders[f]) != 1 or S6.barred[f]:
            continue
        if desc6.get(S6.holders[f][0]) != 'X only':
            continue
        tied = [x for x in T.members(f) if x < nd0]
        rows.append({'distinction': f, 'tied to start distinctions (names)': tied,
                     'their labels': [S0.labels[x] for x in tied]})
    out['after the last round: usable loose made distinctions descended from X only'] = rows
    return out


def main():
    C.cap_memory(6)
    one = read('ystart-one-2')
    three = read('ystart-three-222')
    t = one['round 3: takes of births descended from X only']
    c1 = len(t) == 3 and all(x['took'] == 17 for x in t) and all(x['maker descent'] == 'Y only' for x in t)
    rows = one['after the last round: usable loose made distinctions descended from X only']
    tied = [r['their labels'] for r in rows]
    starts = [r['tied to start distinctions (names)'] for r in rows]
    c2 = (len(rows) == 3 and all(len(x) == 1 for x in starts) and len({x[0] for x in starts}) == 3)
    out = {'clause 1 (all three takes of round 3 take Y\'s fresh distinction 17)': c1,
           'clause 2 (three usable loose made distinctions of X, tied to three different start distinctions)': c2,
           'their start distinctions (names, labels)': [(s, l) for s, l in zip(starts, tied)],
           'ystart-one-2': one, 'ystart-three-222 (the case, beside it)': three}
    C.write_json('check_p20.json', out)
    C.log('P20:', c1, c2, out['their start distinctions (names, labels)'])


if __name__ == '__main__':
    main()
