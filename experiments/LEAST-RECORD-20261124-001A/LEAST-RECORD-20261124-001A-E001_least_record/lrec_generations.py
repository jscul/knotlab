"""Run 3 of LEAST-RECORD-20261124-001A: generations (deviations.md, item 17).

For every birth of every structure (every knot with parents of the last structure of each lineage, P1 and P2's and P3's;
and the knots made at mismatching births of P1's serial states): whether its parents have equal generations, and the
greatest difference between its generation and a parent's; by law and start, with the condition of each start.

    python -B lrec_generations.py       # writes artifacts/.../generations.json
"""
from __future__ import annotations

import resource
import time

import pfh_common as PC
import pfh_pop as PP
from pfh_struct import Struct


def births(T, extra_only=False):
    rows = []
    for x in range(T.n):
        ps = T.parents[x]
        if not ps:
            continue
        gp = [T.gen[p] for p in ps]
        rows.append({'knot': x, 'round': T.made[x] if T.made is not None else None, 'parents': list(ps),
                     'parent_generations': gp, 'generation': T.gen[x], 'equal': len(set(gp)) == 1,
                     'greatest_difference': T.gen[x] - min(gp)})
    return rows


def summarize(rows):
    uneq = [r for r in rows if not r['equal']]
    return {'births': len(rows), 'births_with_unequal_parents': len(uneq),
            'greatest_difference': max((r['greatest_difference'] for r in rows), default=None),
            'unequal_births': uneq[:60]}


def main():
    resource.setrlimit(resource.RLIMIT_AS, (8 << 30, 8 << 30))
    PC.check_frozen()
    t0 = time.time()
    out = {'P1_P2': [], 'P3': [], 'mismatch_births': []}
    for start, fam, rc in PC.gate_pairs():
        recs = []
        S0, rounds, ev = PP.p2_lineage(start, fam, rc, records=recs)
        holds, where = PP.condition(S0, recs)
        T = Struct.from_engine(rounds[-1])
        row = {'law': PC.LAW_NAMES[fam], 'law_short': PC.LAW_SHORT[fam], 'start': start, 'rounds': len(rounds),
               'knots': T.n, 'condition_holds': holds, 'condition_fails_at': where}
        row.update(summarize(births(T)))
        out['P1_P2'].append(row)
        print(PC.LAW_SHORT[fam], start, 'condition', holds, 'births', row['births'], 'unequal',
              row['births_with_unequal_parents'], 'greatest difference', row['greatest_difference'], flush=True)
    # knots made at mismatching births of P1's serial states
    for cid, start, fam, r in PP.serial_configs():
        SR = PP.SerialRun(cid, start, fam, r)
        for i, st in enumerate(SR.states):
            if st['extra'] is None:
                continue
            T = SR.struct(i)
            x = T.n - 1
            gp = [T.gen[p] for p in T.parents[x]]
            out['mismatch_births'].append({'run': cid, 'state': i, 'seeds': st['seeds'],
                                           'parents_reference_knots': [T.ref_id[p] for p in T.parents[x]],
                                           'parent_generations': gp, 'generation': T.gen[x],
                                           'equal': len(set(gp)) == 1,
                                           'greatest_difference': T.gen[x] - min(gp)})
    print('mismatch births', len(out['mismatch_births']), 'with unequal parents',
          sum(1 for m in out['mismatch_births'] if not m['equal']), flush=True)
    for short in PC.HOLD_LAWS:
        fam = PC.SHORT_LAW[short]
        for start in PC.P3_STARTS:
            S0, rounds, recs, ev = PP.p3_lineage(start, fam)
            holds, where = PP.condition(S0, recs)
            T = Struct.from_engine(rounds[-1])
            row = {'law': PC.LAW_NAMES[fam], 'law_short': short, 'start': start, 'rounds': len(rounds), 'knots': T.n,
                   'condition_holds': holds, 'condition_fails_at': where, 'events': ev}
            row.update(summarize(births(T)))
            out['P3'].append(row)
            print(short, start, 'condition', holds, 'births', row['births'], 'unequal',
                  row['births_with_unequal_parents'], 'greatest difference', row['greatest_difference'], flush=True)
    fails = [r for r in out['P1_P2'] if not r['condition_holds']]
    out['condition_fails_on'] = [(r['law_short'], r['start']) for r in fails + [r for r in out['P3'] if not r['condition_holds']]]
    out['moduli_for_run_6'] = {'%s %s' % (r['law_short'], r['start']): 2 * r['greatest_difference'] + 1 for r in fails}
    out['equal_generations_wherever_the_condition_holds'] = all(
        r['births_with_unequal_parents'] == 0 for r in out['P1_P2'] if r['condition_holds'])
    out['seconds'] = round(time.time() - t0, 1)
    PC.write_json(PC.OUT / 'generations.json', out)
    print('condition fails on', out['condition_fails_on'], 'moduli', out['moduli_for_run_6'],
          'equal generations where it holds', out['equal_generations_wherever_the_condition_holds'])


if __name__ == '__main__':
    main()
