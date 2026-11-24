"""Run A2: Ring(n, 3), n = 5, 7, 9, 11, 13, 15, under the two and the three added rules, 12 rounds: the parity knot
test (ranks over GF(2) and the cut test) for every knot at every round (0 to 12), and the extension test for every
round.  Evidence for P6.  Writes a2.json."""
from common import E, log, resources, write
from knotcheck import ParityChecker

R = 12
CAP = 6000


def main():
    out = {'runs': {}}
    for lname, law in (('two', E.TWO_ADDED), ('three', E.THREE_ADDED)):
        for n in (5, 7, 9, 11, 13, 15):
            chk = ParityChecker(R)
            run = E.Run(E.ring(n, 3), law, R, knot_cap=CAP, hook=chk, hook_needs_before=R)
            key = 'Ring(%d,3)|%s' % (n, lname)
            out['runs'][key] = {'summary': run.summary(), 'check': chk.summary(), 'rows': chk.rows}
            s = chk.summary()
            log(key, 'knots', run.S.n_knots, 'pass', s['all_knots_pass'], 'agree', s['methods_agree'],
                'extend', s['all_rounds_extend'], 'knot-checks', s['knots_checked'], '%.1fs' % s['seconds'])
    out['resources'] = resources()
    write('a2.json', out)


if __name__ == '__main__':
    main()
