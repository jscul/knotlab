"""Deviations 44: X alone and Y alone for made-2-exchanged (D 4.6 for the made designs), under run 2's 144 laws.

usage: python -B run2_exchanged_alone.py
"""
import os
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402
import run2  # noqa: E402

mc.STARTS['alone']['made-2-exchanged'] = {
    'X alone': {'stars': [[0, 3, 4]], 'barred': [0], 'X': [1, 2], 's': 1},
    'Y alone': {'stars': [[0, 1, 2]], 'barred': [0], 'Y': [1, 2], 's': 1}}
KEYS = ('X_alone', 'Y_alone', 'T_iii', 'reading_iii', 'reading_iii_reverse')


def main():
    C.cap_memory(6)
    t0 = time.time()
    old = {tuple(r['job'][k] for k in ('base', 'take', 'choice', 'knot_law')): r['designs']['made-2-exchanged']
           for r in C.read_jsonl('run2.jsonl.gz')}
    out = C.JsonLines('run2_exchanged_alone.jsonl')
    same = 0
    for j in run2.jobs():
        kl = j['knot_law']
        law = mc.make_law(j['base'], j['take'], j['choice'], kl)
        d = mc.design('made-2-exchanged')
        A, view, ref = run2.run_design(d, law, kl)
        row, _ = run2.analyse(d, law, kl, A, view, ref, {}, seed=1000 * 5)
        o = old[(j['base'], j['take'], j['choice'], kl)]
        eq = all(row[k] == o[k] for k in ('rounds', 'knots', 'X_course', 'Y_course', 'takes', 'endings', 'values',
                                           'form'))
        same += eq
        out.write({'job': j, 'law': law.name(), 'run A as in run 2': eq, **{k: row.get(k) for k in KEYS}})
    out.close()
    C.log('made-2-exchanged alone:', same, 'of 144 runs A as in run 2;', round(time.time() - t0, 1), 's')


if __name__ == '__main__':
    main()
