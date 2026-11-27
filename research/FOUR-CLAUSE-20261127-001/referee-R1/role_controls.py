"""Test every choice of both/either on the held-out witness's three frozen pairs."""
import argparse
from itertools import combinations, product
import json
from pathlib import Path
from time import perf_counter

from witness_checks import CARRIERS_5260, CENSUS, FOUR, States, advance, mixed, supports_of

HERE=Path(__file__).resolve().parent


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--pilot',action='store_true')
    args=parser.parse_args()
    begin=perf_counter()
    start=supports_of(json.loads(CENSUS.read_text())[5260])
    stage=advance(advance(start).supports).supports
    st=States(stage)
    lower=[st.agreement(c) for c in CARRIERS_5260]
    fixes=[st.cells(st.allowed,[lower[i] for i in clause]) for clause in FOUR]
    six=list(product((0,1),repeat=6))
    output=[]
    for choices in list(product(('either','both'), repeat=3))[:1 if args.pilot else 8]:
        def apply(values):
            return tuple((values[2*j] & values[2*j+1]) if choice=='both' else (values[2*j] | values[2*j+1])
                         for j,choice in enumerate(choices))
        upper=apply(lower)
        cells=st.cells(st.allowed,upper)
        determined=sum(mixed(f,u)==0 for f in fixes for u in upper)
        free=all(len({(w[i],w[j]) for w in cells})==4 for i,j in combinations(range(3),2))
        enough=[]
        for count in range(5):
            for subset in combinations(FOUR,count):
                if not any(all(apply(w)) and all(not all(w[i] for i in clause) for clause in subset) for w in six):
                    enough.append(subset)
            if enough:
                break
        all_hold=upper[0]&upper[1]&upper[2]
        restored=[(st.obey(j for j in range(len(stage)) if j!=k)&all_hold).bit_count()
                  for k in range(len(stage))] if '111' not in cells else None
        output.append({'choices':choices,'upper_words':sorted(cells),'pairs_free':free,
                       'determinations_out_of_12_named_bond_tests':determined,'minimum_named_clauses_to_exclude_111':len(enough[0]) if enough else None,
                       'number_minimum_clause_sets':len(enough),'restorations_by_single_law_deletion':restored})
    filename='role_controls_pilot.json' if args.pilot else 'role_controls.json'
    (HERE/filename).write_text(json.dumps(output,indent=2)+'\n')
    print([(r['choices'],len(r['upper_words']),r['pairs_free'],r['determinations_out_of_12_named_bond_tests'],r['minimum_named_clauses_to_exclude_111']) for r in output],round(perf_counter()-begin,4))

if __name__=='__main__':
    main()
