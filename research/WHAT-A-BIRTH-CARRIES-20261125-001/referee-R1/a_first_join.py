"""Reconstruct the first join for every registered marked start through round two."""
import argparse
from collections import Counter
from itertools import combinations, product
import json
from pathlib import Path
from time import perf_counter

from b_growth import Law, grow, bar

HERE = Path(__file__).resolve().parent


def recount(smoke=False):
    numbers = json.loads((HERE.parent.with_name(HERE.parent.name+'A') / 'numberings.json').read_text())
    totals = Counter()
    cells = {}
    for h, choice, knot_law in product((3,4), ('OLDEST','NEWEST'), ('nae','parity')):
        law = Law('ORD','CANCEL-RETIRE','MET',knot_law,choice)
        starts = numbers['made_class'][f'made-{h}']
        out = Counter()
        for nu, stars in enumerate(starts[:1] if smoke else starts):
            initial = grow(stars,law,rounds=1)
            x_parent = next(i for i,places in enumerate(stars) if len(places)==3)
            common, = set(stars[0]) & set(stars[1])
            first_births = initial.steps[1].births.values()
            x = tuple(b.knot for b in first_births if b.parents == (x_parent,))
            y = tuple(b.knot for b in first_births if b.parents == (1-x_parent,))
            for a in range(h+1):
                for subset in combinations(y,a):
                    last = 3 if stars == numbers['registered'][f'made-{h}'] and a >= h-1 and choice == 'OLDEST' else 2
                    run = bar(initial,1,set(y)-set(subset),law,rounds=last)
                    step = run.steps[2]
                    births = list(step.births.values())
                    j, = (b for b in births if b.parents == x)
                    y_births = {b.knot for b in births if set(b.parents) & set(y)}
                    x_others = {b.knot for b in births if b.kind=='offshoot' and set(b.parents) & set(x)}
                    m = a*(h-1)-a*(a-1)//2
                    expected = y_births | x_others
                    out['marked_starts'] += 1
                    good = (len(x_others)==2 and len(y_births)==m and j.takes==(common,)
                            and set(j.candidates)=={common} and j.demand==2+m and not j.implied
                            and len(j.fresh)==2+m and len(run.states[2].knots[j.knot].places)==5+m
                            and all(len(g)==2 for g in j.demand_partners)
                            and {k for g in j.demand_partners for k in g}-{j.knot}==expected)
                    out['first_join_all_checks_pass'] += good
                    if stars == numbers['registered'][f'made-{h}']:
                        out['registered_numbering'] += 1
                        out['all_second_round_births_take_shared'] += all(b.takes == (common,) for b in births)
                    if last==3:
                        joins = [b for b in run.steps[3].births.values() if b.kind=='join']
                        out['registered_oldest_all_or_all_but_one'] += 1
                        out['all_third_round_joins_take_1'] += bool(joins) and all(b.takes==(1,) for b in joins)
                    if knot_law=='nae' and h==4 and choice=='NEWEST' and nu>=185:
                        out['outside_original_main_run'] += 1
                        out['outside_original_first_join_pass'] += good
        cells[f'{h} loose, {choice}, {knot_law}'] = out
        totals.update(out)
    return {'totals': totals, 'by_setting': cells}


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--smoke',action='store_true')
    args = parser.parse_args()
    t = perf_counter()
    table = recount(args.smoke)
    print(table['totals'], 'seconds', round(perf_counter()-t,3))
    if not args.smoke:
        (HERE/'a_first_join.json').write_text(json.dumps(table,indent=2)+'\n')
