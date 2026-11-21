"""Apply the prospectively specified order to completed historical observations."""
from collections import Counter
from pathlib import Path
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
LEAF=HERE.parent.name
OUT=ROOT/'artifacts'/LEAF/HERE.name
WIDE='CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C'
OLD='STATE-DISTANCE-AND-REACHED-GROWTH-20261120-001B'
HISTORY=ROOT/'artifacts'/WIDE/(WIDE+'-E001_wider_meetings')
PREV=ROOT/'artifacts'/OLD/(OLD+'-E001_pair_growth')
sys.path.insert(0,str(ROOT/'experiments'/WIDE/HISTORY.name))
from census_stages import advance, owners
from multiple_meetings import classify_stage, load_catalogue

def read(path):
    with (gzip.open(path,'rt') if path.suffix=='.gz' else path.open()) as file:
        return json.load(file)

def save(path, obj):
    path.write_text(json.dumps(obj,indent=2)+'\n')

def choose():
    old=read(PREV/'role_screen.json.gz')
    founders=read(HISTORY/'census_stages.json.gz')['nae']
    rate={(x['source_index'],x['age']):x for x in read(HISTORY/'census_rate_tables.json.gz')['nae']['records']}
    detailed=[]
    for rec in old:
        i,a,n=rec['source_index'],rec['age'],rec['width']
        source=founders[i]
        if n<=28 or source['source_components']!=1 or not rec['extra_spent_indices']:
            continue
        # The prior unconditional positive-age certificate concerns the
        # connected 28-name table. Its extension beyond 28 requires disjoint
        # pieces and a component promise. No connected eligible candidate
        # here has such a previously published all-reached-rival certificate.
        detailed.append(((n,source['source_width'],a,i),rec))
    detailed.sort(key=lambda p:p[0])
    key,rec=detailed[0]
    n,s,a,i=key
    record=founders[i]
    stage=record['stages'][a-1]
    rs=rate[i,a]
    rows=tuple(map(tuple,stage['rows']))
    previous=tuple(map(tuple,record['source_rows']))
    limits=[len(previous)]
    for index in range(a):
        _,previous,_=advance(previous,'nae')
        if index+1<a: limits.append(len(previous))
    assert previous==rows
    _,_,births=advance(rows,'nae')
    result=dict(selected_key=key,source=record['source_rows'],physical_stage=rows,holder_cut_limits=limits,
       original_name_count=s,reached_name_count=n,age=a,scope='connected historical source and physical reached stage; rivals include all genuine reached stages',
       previous_candidates=rec,older_conditional_class=classify_stage(rows,load_catalogue(),'nae'),
       uniform_word_count=rs['allowed_states'],uniform_disagreements=rs['disagreement_counts'],
       reference_named_roster=[(sorted(rows[h] for h in p),f) for p,f in births],
       actual_loose=sorted(x for x,hs in owners(rows).items() if len(hs)==1),
       eligible_count=len(detailed),minimum_width_ties=[k for k,_ in detailed if k[0]==n],
       widths=dict(sorted(Counter(k[0] for k,_ in detailed).items())),archived_cases=len(old))
    save(OUT/'selection.json',result)
    print(key,len(detailed),result['minimum_width_ties'],rec['extra_spent_indices'])

if __name__=='__main__':choose()
