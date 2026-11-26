"""Cross-check the constructed cycles with the general referee growth and independent readers."""
import argparse
from functools import reduce
from itertools import combinations
import json
from operator import xor
from pathlib import Path
import time

from carrier_check import basis, mask, moves_of, rem
from path_certificate import joint
from replay_growth import bicycle, grow

HERE = Path(__file__).resolve().parent


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--pilot',action='store_true')
    args = ap.parse_args()
    start = time.monotonic()
    recipes = json.loads((HERE/'construct_born.json').read_text())['preparations']
    output = []
    for label, record in recipes.items():
        current = tuple(tuple(s) for s in record['source supports'])
        original = current
        pairs = list(map(mask, record['ring-wise supports born in the first round']))
        total = reduce(xor,pairs)
        assert all(a&b==0 for a,b in combinations(pairs,2))
        stages = []
        for i,birthname in enumerate(['first ordinary births','second ordinary births','third ordinary births']):
            later,status = grow(current)
            assert status=='funded'
            expected = tuple(tuple(sorted(b['inputs']+b['fresh'])) for b in record[birthname])
            assert tuple(tuple(sorted(s)) for s in later[len(current):]) == expected
            stages.append(later)
            current = later
        current = stages[1]
        holders, shortest = moves_of(current)
        rows = list(map(mask,current))
        law_base = basis(rows)
        four = sorted(joint(rows,pairs))
        by_knot = [sorted(joint(rows,pairs,support)) for support in current]
        circuits = []
        for carrier in record['ring-wise supports born in the first round']:
            neighbors = {}
            for d in carrier:
                a,b = holders[d]
                neighbors.setdefault(a,[]).append(b)
                neighbors.setdefault(b,[]).append(a)
            seen, todo = set(), [next(iter(neighbors))]
            while todo:
                a=todo.pop()
                if a not in seen:
                    seen.add(a)
                    todo.extend(neighbors[a])
            circuits.append(len(seen)==len(neighbors) and all(len(v)==2 for v in neighbors.values()))
        assert all(circuits) and len(four)==4 and all(v==four for v in by_knot)
        assert rem(law_base,total)==0 and rem(basis(map(mask,original)),total)!=0
        assert all((c&m).bit_count()%2==0 for c in pairs for m in shortest)
        state_at_start = len(set().union(*original))-len(basis(map(mask,original)))
        _, start_moves = moves_of(original)
        result = {'preparation':label,'source_class_bits':state_at_start-len(basis(start_moves)),
                  'rounds_compared':len(stages),'knots_at_round_two':len(current),
                  'round_two_circuits_verified':circuits,'sum_in_B':rem(basis(bicycle(current)[-1]),total)==0,
                  'field_read_with_every_knot_fixed':all(v==four for v in by_knot),'allowed_triples':four,
                  'shortest_move_count':len(shortest)}
        assert result['sum_in_B']
        output.append(result)
        if args.pilot: break
    fname = 'cycle_certificate_pilot.json' if args.pilot else 'cycle_certificate.json'
    (HERE/fname).write_text(json.dumps({'cases':output,'seconds':round(time.monotonic()-start,3)},indent=2)+'\n')
    print(output)


if __name__=='__main__':
    main()
