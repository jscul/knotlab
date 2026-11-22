"""Funded old-state extension and full paid-input projections for the physical knots."""
from collections import Counter
from itertools import product
from pathlib import Path
import gzip
import json

from growth import load, stars_at


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT/'artifacts'/HERE.parent.name/HERE.name
PRIOR = 'TWO-SENDS-AND-GROWN-KEEPERS-20261122-001A'
OLD = ROOT/'artifacts'/PRIOR/(PRIOR+'-E001_two_sends')/'ordinary.json'


def allowed(n, count, law):
    return count%2 == 0 if law=='parity' else 0<count<n


def main():
    bounds = json.loads(OLD.read_text())['actual_ordinary_cuts']['intact']
    data = load()
    out = {}
    for mode,cases in data['cases'].items():
        out[mode] = {}
        for law,case in cases.items():
            earned={}
            input_rows=0
            newborns=0
            for layer,cut in enumerate(case['cuts']):
                archived={b['holder']:b for b in bounds[law][0]['births']}
                for b in cut['births']:
                    assert b['grant'] >= 2
                    if layer==0:
                        p=b['consumed_names']
                        if mode=='interrupted':
                            p=[{510:677,677:510}.get(d,d) for d in p]
                        prior=archived[b['holder']]
                        assert p==prior['consumed_names'] and prior['input_projection']==list(range(1<<len(p)))
                    else:
                        assert len(set(b['parents']))==len(b['parents'])
                        for donor,name in zip(b['parents'],b['consumed_names'],strict=True):
                            prior=earned[donor]
                            assert name in prior['fresh_names'] and len(prior['fresh_names'])>=2
                            # All prior paid inputs may already be fixed. For either new target value,
                            # the remaining new marks of this distinct parent complete its local law.
                            k=prior['grant']; m=len(prior['consumed_names'])
                            for old_count, target in product(range(m+1),(0,1)):
                                assert any(allowed(k+m,old_count+target+remainder,law) for remainder in range(k))
                    input_rows+=1<<len(b['parents']); newborns+=1
                    earned[b['holder']]=b
            stars=stars_at(data,mode,law,3)
            arities=Counter(map(len,stars))
            assert min(arities)>=3
            out[mode][law]={'whole_holders':len(stars),'newborns_with_full_paid_input_projection':newborns,
                  'exact_binary_paid_input_rows_covered':input_rows,'arities':dict(sorted(arities.items())),
                  'allowed_rows_by_arity':{n:2**(n-1) if law=='parity' else 2**n-2 for n in sorted(arities)},
                  'single_name_erasure_at_each_arity':{n:2**(n-1) for n in sorted(arities)}}
    (OUT/'lawfulness.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')
    print('Projected every paid-input combination through the third genuine cut in six cases.')


if __name__=='__main__':
    main()
