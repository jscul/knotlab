"""Replays of disclosed numbers that differ from the registered runs' (brief: "replay the case and put the listing in
the outputs").  R0b's machinery control and the planted pair's own rates were disclosed at the scratch's bounds
(6 rounds, at most 300 knots); R0b runs at the registered bounds (dev 21).  Here both are read again at the scratch's
bounds, same seeds and calls.  Writes replay_disclosed.json."""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mcc  # noqa: E402
import study  # noqa: E402
import controls  # noqa: E402


def machinery(design, rounds, knots, n=100):
    d = mcc.STARTS_A['designs'][design]
    spec = mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'STEPS-1', 'parity')
    base = 'C|A|%s|FLOOR1|CANCEL-OFFSHOOT|STEPS-1|parity|0' % design
    g = mcc.Growth(d['stars'], spec, 'A|' + design, 0, rounds, knots, base=base)
    X, Y, s = tuple(d['X']), tuple(d['Y']), d['s']
    ref = g.ref(s, X, Y)
    out = {}
    for kind in ('BN', 'BY'):
        c = Counter()
        for i in range(n):
            Gc, _ = g.continuation(kind, s, X, Y, i)
            r = mcc.read_pairs(Gc.snaps, Gc.records, Gc.R, [ref], need_form=False)[0]
            c['met'] += int('Yown_val' in r.first)
            c['stopped'] += int(Gc.stop is not None)
        out[kind] = dict(c)
    return out


def planted_own(rounds, knots, n=100):
    pc = mcc.CASES_C['cases'][13]
    spec = mcc.Spec('FLOOR1', 'CANCEL-OFFSHOOT', 'MET', 'parity')
    g = mcc.Growth(mcc.start_by_id(pc['start'])['stars'], spec, pc['start'], 0, rounds, knots)
    X, Y, s = tuple(pc['X']), tuple(pc['Y']), pc['s']
    cnt = study.stage(g, s, {(X, Y): ['form']}, ('BN', 'BY', 'BX'), range(n))
    rt = study.rates_of(cnt[(X, Y)], 'form')
    return {'q1 (after the meeting)': rt['q1'], 'q1 at any round': rt['q1_any'], 'Y barred': rt['q0'],
            "Y's own, X barred": rt['qY'], 'continuations meeting, nothing barred': rt['meetings']['BN'],
            'stopped': rt['stopped']}


def main():
    out = {'disclosed': {'machinery (PC)': {'made-4': '78 of 100 with nothing barred, 0 with Y barred',
                                            'made-5': '86 of 100, 0'},
                         'planted pair (cases_c.json R0b)': mcc.CASES_C['R0b']['planted_case_pair'][
                             'scratch rates at 100 (c_rates_form)']}}
    for lab, (r, k) in (('scratch bounds (6 rounds, 300 knots)', (6, 300)),
                        ('registered bounds (8 rounds, 500 knots)', (8, 500))):
        out[lab] = {'machinery made-4': machinery('made-4', r, k), 'machinery made-5': machinery('made-5', r, k),
                    'planted pair, own rates (arm 3)': planted_own(r, k)}
        study.log(lab, out[lab])
    study.write_json('replay_disclosed.json', out)


if __name__ == '__main__':
    main()
