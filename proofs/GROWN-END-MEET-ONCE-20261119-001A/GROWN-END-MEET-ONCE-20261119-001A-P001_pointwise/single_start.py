from pathlib import Path
from itertools import combinations
from math import comb
import json
import sys

from check import all_readings, law


def audit_single(binary):
    cases = {}
    for arity in range(3, 8):
        system = law.C.S.from_junctions([list(range(arity))])
        counts, tested = [], []
        for age in range(1, arity+1):
            change = system.step(law.C.S.gf2(law.C.F.fewest), None)
            assert change and change['new'] == comb(arity,age)
            counts.append(change['new'])
            rows = [sorted(s) for s in system.bits_of]
            actual_loose = {x for x,holders in system.owner.items() if len(holders)==1}
            assert len(actual_loose) == (arity-age)*comb(arity,age)
            if not actual_loose or len(rows)>16 or len(system.owner)>63:
                continue
            _, table, _ = all_readings(binary,rows)
            predicted=set()
            for row in rows:
                predicted.update(combinations(row,2))
            if age==arity-1:
                predicted.update(combinations(sorted(actual_loose),2))
            assert min(table.values())==arity-1
            assert predicted=={xy for xy,v in table.items() if v==arity-1}
            tested.append({'age':age,'pairs':len(table),'pairs_at_minimum':len(predicted)})
        cases[arity]={'birth_counts':counts,'direct_pair_checks':tested}
    return cases

if __name__=='__main__':
    result=audit_single(Path(sys.argv[1]))
    print(json.dumps(result,indent=2))
