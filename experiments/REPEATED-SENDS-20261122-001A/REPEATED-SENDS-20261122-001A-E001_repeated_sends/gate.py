"""Read the continuing holder across the three actual old cuts and prove its stopping condition."""
from collections import defaultdict
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR = 'HIDDEN-SENDER-MARKS-20261122-001A'
BASE = ROOT / 'artifacts' / PRIOR / (PRIOR + '-E001_hidden_sends')
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
GROWTH_DIGEST = 'f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a'


def archive(name):
    with gzip.open(BASE / name, 'rt') as f:
        return json.load(f)


def owners(stars):
    out = defaultdict(list)
    for h, row in enumerate(stars):
        for d in row:
            out[d].append(h)
    return out


def main():
    assert sha256((BASE/'growth.json.gz').read_bytes()).hexdigest() == GROWTH_DIGEST
    source=archive('growth.json.gz')
    rows=[]
    for mode,laws in source['cases'].items():
        for law,case in laws.items():
            r=case['receivers']['R']; marked=r['fresh_names']; assert marked==[1754,1755,1756]
            stages=[source['original_stars']]
            for layer in case['cuts']:
                previous=owners(stages[-1]); paid=[]; updated=list(stages[-1]); new=set()
                for b in layer['births']:
                    assert all(previous[d]==[h] for d,h in zip(b['consumed_names'],b['parents'],strict=True))
                    assert set(b['fresh_names']).isdisjoint(previous) and new.isdisjoint(b['fresh_names'])
                    assert len(updated)==b['holder'];updated.append(b['consumed_names']+b['fresh_names'])
                    paid.extend(b['consumed_names']);new.update(b['fresh_names'])
                assert len(paid)==len(set(paid));stages.append(updated)
            owned=[owners(s) for s in stages]
            observed=[]
            for k,stage in enumerate(stages):
                if 294>=len(stage):continue
                assert stage[294]==[949,957,*marked] and not set(stage[294]) & {510,563}
                peers=[[h for h in owned[k][d] if h!=294] for d in marked]
                observed.append(peers)
            assert observed==[[[],[],[]],[[631],[633],[634]]]
            physically_possible=[{d:owned[k][d] for d in (510,563)} for k in range(4)]
            assert physically_possible[0]=={510:[80],563:[80]}
            assert physically_possible[1]==physically_possible[2]==physically_possible[3]
            rows.append({'law':law,'route':mode,'growth_holder_counts':[len(s) for s in stages],
                         'source_owners_by_stage':physically_possible,'R_full_holding':stages[-1][294],
                         'R_fresh_others_by_stage':observed,'positive_finishes':1,
                         'local_clock':r['local_clock'],'second_positive_finish':False})
    record={'basis_sha256':GROWTH_DIGEST,'cases':rows,'new_group_input':'only singly held paid distinctions',
            'fixed_holder_rule':'original holdings persist; fresh names are granted only to the new holder',
            'continuation_scope':'after the first local payment all three R names have two holders and cannot be paid again; the enrolled source never addresses an R name'}
    (OUT/'receiver_gate.json').write_text(json.dumps(record,indent=2,sort_keys=True)+'\n')
    print('Verified six unchanged R holdings, six positive first finishes, zero possible second finishes.')


if __name__=='__main__':
    main()
