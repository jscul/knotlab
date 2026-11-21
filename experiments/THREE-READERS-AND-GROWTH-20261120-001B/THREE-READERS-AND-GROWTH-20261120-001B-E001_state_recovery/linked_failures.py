"""Two odd residual obstructions in one live presentation, with one or two common names."""
import json
from reconstruct import AllowedReader, OUT, violated
from sample_recovery import deletions, lawful, mask_of, next_stage, one_word_for_each_target, width


def control(extra):
    bridge=(12,14) if extra else (12,)
    rows=((0,1,2,*bridge,13),(0,3,4),(1,3,5),(2,4,5),
          (6,7,8,*bridge),(6,9,10),(7,9,11),(8,10,11))
    n=width(rows)
    assert lawful(rows,'nae') and all(deletions(rows,'nae')[0])
    excluded=0
    for h in rows:
        excluded |= violated(n,mask_of(h))
    state=((1<<(1<<n))-1)^excluded
    arm,covers=AllowedReader(n,state).recover()
    expected=tuple(sorted(mask_of(r) for r in rows))
    assert covers=={expected} and arm=='loose'
    misses=[i for i,w in enumerate(one_word_for_each_target(rows)) if w is None]
    assert misses==[0,4]
    funding,_,births=next_stage(rows,'nae')
    assert funding=='births' and len(births)==1
    return {'rows':rows,'names':n,'states':state.bit_count(),'bridge_multiplicity':len(bridge),
            'failed_single_word_rows':misses,'state_reader_output':arm,'exactly_recovered':True,
            'funding':funding,'births':births}


if __name__=='__main__':
    data=[control(False),control(True)]
    (OUT/'linked_failures.json').write_text(json.dumps(data,indent=2)+'\n')
    print([(d['names'],d['states'],d['births']) for d in data])
