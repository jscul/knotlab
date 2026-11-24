"""Trace files for the comparisons made by the thread and by tickets B and C.

a1_trace.json: every run of A1 (Ring(n, 3), n = 3..16; the two added rules through 12 rounds, the three added rules
through 20, ordinary growth through 8), per round: members, parts, sorted h over members, sorted sizes of the
inclusion-maximal met sets, births, total fresh distinctions (and, extra, sorted k and the number of knots).

extra_trace.json: through round 8, D2(4, 3), D2(5, 3), DW(5, 3) under the two added rules, the three added rules and
(RATION-3, CANCEL-WAIT); Ring(5, 3) under (RATION-3, CANCEL-WAIT) and the two and three added rules; each round also
with the sorted list of births as [number of parents, fresh].
"""
from common import E, log, resources, write

RATION3_WAIT = E.Law('RATION-3', 'CANCEL-WAIT')
A1_LAWS = [('two added rules', E.TWO_ADDED, 12), ('three added rules', E.THREE_ADDED, 20),
           ('ordinary', E.ORDINARY, 8)]


def main():
    a1 = {'description': __doc__.strip().split('\n\n')[1], 'knot_cap': 6000, 'runs': {}}
    for lname, law, R in A1_LAWS:
        for n in range(3, 17):
            run = E.Run(E.ring(n, 3), law, R, knot_cap=6000)
            key = 'Ring(%d, 3) | %s' % (n, lname)
            a1['runs'][key] = {'start': 'Ring(%d, 3)' % n, 'law': law.to_dict(), 'law_name': lname, 'R': R,
                               'rounds_done': run.rounds_done, 'cut_off': run.cut_off, 'rows': run.trace()}
            log(key, 'rounds', run.rounds_done, 'knots', run.S.n_knots)
    a1['resources'] = resources()
    write('a1_trace.json', a1)

    ex = {'description': __doc__.strip().split('\n\n')[2], 'runs': {}}
    cases = []
    for name, start in (('D2(4, 3)', E.d2(4, 3)), ('D2(5, 3)', E.d2(5, 3)), ('DW(5, 3)', E.dw(5, 3))):
        for lname, law in (('two added rules', E.TWO_ADDED), ('three added rules', E.THREE_ADDED),
                           ('(RATION-3, CANCEL-WAIT)', RATION3_WAIT)):
            cases.append((name, start, lname, law))
    for lname, law in (('(RATION-3, CANCEL-WAIT)', RATION3_WAIT), ('two added rules', E.TWO_ADDED),
                       ('three added rules', E.THREE_ADDED)):
        cases.append(('Ring(5, 3)', E.ring(5, 3), lname, law))
    for name, start, lname, law in cases:
        run = E.Run(start, law, 8)
        key = '%s | %s' % (name, lname)
        ex['runs'][key] = {'start': name, 'law': law.to_dict(), 'law_name': lname, 'R': 8,
                           'rounds_done': run.rounds_done, 'rows': run.trace(with_births=True)}
        log(key, 'knots', run.S.n_knots)
    ex['resources'] = resources()
    write('extra_trace.json', ex)


if __name__ == '__main__':
    main()
