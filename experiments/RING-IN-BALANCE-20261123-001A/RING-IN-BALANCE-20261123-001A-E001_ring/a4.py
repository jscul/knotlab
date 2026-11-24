"""Run A4: Ring(n, 3), n = 5, 7, 9, under 70 laws (rations ORD, ONE-FEWER, FLOOR0, FLOOR1, RATION-2, RATION-3,
RATION-4, CAP-2, CAP-3, CAP-4, each with STALL, CANCEL-OFFSHOOT, CANCEL-WAIT, CANCEL-RETIRE, and with STALL,
CANCEL-WAIT, CANCEL-RETIRE under NO-OFFSHOOT), 16 rounds, cut off past 6,000 knots; the parity knot test (both methods)
and the extension test through round 6.  Evidence for P8.  Writes a4.json (or a4_n<n>.json with --ring n)."""
import argparse

from common import E, log, resources, write
from knotcheck import ParityChecker

R = 16
CAP = 6000
TEST_ROUNDS = 6


def run_one(n, law):
    chk = ParityChecker(TEST_ROUNDS)
    run = E.Run(E.ring(n, 3), law, R, knot_cap=CAP, hook=chk, hook_needs_before=TEST_ROUNDS)
    rets = run.find_returns()
    off = [r for r in rets if r['n_off'] > 0]
    return {'ring': n, 'law': law.to_dict(), 'summary': run.summary(),
            'has_return_giving_parts_off': bool(off),
            'first_return_giving_parts_off': ({k: off[0][k] for k in ('s', 't', 'period', 'part_size', 'n_off',
                                                                       'off_sizes')} if off else None),
            'returns': [{k: r[k] for k in ('s', 't', 'period', 'part_size', 'n_off', 'off_sizes')} for r in rets[:12]],
            'n_returns': len(rets),
            # descriptive: sizes and periods of every part that returns giving parts off
            'off_return_part_sizes': sorted({r['part_size'] for r in off}),
            'off_return_periods': sorted({r['period'] for r in off}),
            'off_return_first_s_by_size': {str(z): min(r['s'] for r in off if r['part_size'] == z)
                                           for z in sorted({r['part_size'] for r in off})},
            'closing_rounds': [rec['round'] for rec in run.records if rec['closing']],
            'knot_test': chk.summary(), 'knot_rows': chk.rows,
            'trace': [{k: row[k] for k in ('round', 'members', 'parts', 'births') if k in row} for row in run.trace()]}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ring', type=int, choices=(5, 7, 9))
    a = ap.parse_args()
    rings = (a.ring,) if a.ring else (5, 7, 9)
    out = {'runs': {}}
    for n in rings:
        for law in E.a4_laws():
            key = 'Ring(%d,3)|%s' % (n, law.name())
            v = run_one(n, law)
            out['runs'][key] = v
            log(key, v['summary']['kind'], 'rounds', v['summary']['rounds_done'], 'knots', v['summary']['knots'],
                'off' if v['has_return_giving_parts_off'] else '-', 'knots-pass', v['knot_test']['all_knots_pass'],
                'agree', v['knot_test']['methods_agree'], 'extend', v['knot_test']['all_rounds_extend'])
    out['resources'] = resources()
    write('a4.json' if not a.ring else 'a4_n%d.json' % a.ring, out)


if __name__ == '__main__':
    main()
