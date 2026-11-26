"""Recheck the three-parent intervention using shared growth and independent value and move tests."""
import argparse
from itertools import combinations
import json
from pathlib import Path
import sys
from time import monotonic

from carrier_check import mask, moves_of
from path_certificate import joint

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--pilot',action='store_true')
    args=ap.parse_args()
    then=monotonic()
    for family,folder in [('NAE-GROWTH-20261119-001B','NAE-GROWTH-20261119-001B-E001_nae'),
                          ('FORBIDDING-JOIN-20261120-001B','FORBIDDING-JOIN-20261120-001B-E001_free_readings')]:
        sys.path.insert(0,str(ROOT/'experiments'/family/folder))
    import naelib
    from rival_growth import grow
    example=json.loads((HERE/'construct_born.json').read_text())['preparations']
    recipe=next(iter(example.values()))
    original=[list(s) for s in recipe['source supports']]
    # Find the middle connecting knot independently from the saved descriptions.
    centers=[k for k,description in enumerate(recipe['original knots, in support order']) if description.endswith('extra knot 2')]
    assert len(centers)==3
    next_name=1+max(set().union(*original))
    for a,b in combinations(centers,2):
        original[a].append(next_name)
        original[b].append(next_name)
        next_name+=1
    ports=[]
    for k in centers:
        original[k].append(next_name)
        ports.append(next_name)
        next_name+=1
    labels=list(map(mask,recipe['ring-wise source-loose supports']))
    other=json.loads((HERE/'cuts_three.json').read_text())
    assert original==other['source supports']
    source_image=sorted(joint(list(map(mask,original)),labels))
    assert len(source_image)==8
    rows={}
    for arm in (['ordinary'] if args.pilot else ['ordinary','one_fewer','arity_floor']):
        stage,info=grow(tuple(map(tuple,original)),'parity',arm,naelib)
        assert info['status']=='funded'
        assert [list(x) for x in stage]==other['growth'][arm]['stage supports']
        laws=list(map(mask,stage))
        cut,=[k for k,s in enumerate(stage) if set(ports)<=set(s)]
        owners,moves=moves_of(stage)
        image=sorted(joint(laws,labels))
        images=[sorted(joint(laws,labels,s)) for s in stage]
        without=sorted(joint(laws[:cut]+laws[cut+1:],labels))
        rows[arm]={'stage_knots':len(stage),'stage_distinctions':len(owners),'birth':list(stage[cut]),
                   'allowed':image,'allowed_with_birth_removed':without,'shortest_moves':len(moves),
                   'changes_of_each_carrier':[sum((p&m).bit_count()%2 for m in moves) for p in labels],
                   'every_knot_fixed_to_zero_still_gives_full_joint_image':all(x==image for x in images)}
        assert len(without)==8
        if arm!='ordinary':
            assert len(image)==4 and all(x==image for x in images)
            assert rows[arm]['changes_of_each_carrier']==[0,0,0]
        else: assert image==source_image
    (HERE/('three_parent_certificate_pilot.json' if args.pilot else 'three_parent_certificate.json')).write_text(
        json.dumps({'source_joint_values':source_image,'growth':rows,'seconds':round(monotonic()-then,3)},indent=2)+'\n')
    print({arm:v['allowed'] for arm,v in rows.items()})


if __name__=='__main__':
    main()
