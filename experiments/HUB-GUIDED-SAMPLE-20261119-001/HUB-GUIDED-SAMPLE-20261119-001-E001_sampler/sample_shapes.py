"""Read literal group draws independently of their sampling weights or reported shapes."""
import argparse
import gzip
import json
from pathlib import Path
from group_profile import Stage, pack, members
from hub_greedy import decode_group


def run(source,dir_):
    report={}
    opener=gzip.open if source.suffix=='.gz' else open
    with opener(source,'rt') as f:
        if source.name.endswith('.json'):
            panels = json.load(f)['panels']
        else:
            panels = (record['result'] for line in f if (record:=json.loads(line)).get('status')=='ok')
        for data in panels:
            if not data.get('first_unread') or 'reverse' in data['label']:
                continue
            label=data['label']
            stage=Stage(dir_/(label+'.txt'))
            biggest=max(b.bit_count() for b in stage.blocks)
            examples=[]
            checked=0
            limit=12 if label.startswith('start-03-') else 3
            for rep in data['replicates']:
                for draw in rep['draws']:
                    if 'literal_group_bitset_zlib_base64' not in draw or not draw['large_join']:
                        continue
                    if checked==limit:break
                    bits=decode_group(draw)
                    sites=list(members(bits))
                    assert len(sites)==draw['size']
                    best,touch,_,cover=stage.covers(bits,sites)
                    assert best==draw['largest_block_intersection']
                    # Each disjoint noncandidate pair uses at least one name outside
                    # the largest block. This certificate is cheap for near-full blocks.
                    ceiling=min(len(sites),stage.n-biggest)
                    if stage.n>50000 and 4*ceiling < 3*len(sites):
                        lower=0;upper=ceiling;kind='largest-block bound'
                    else:
                        upper,pairs=stage.partners(sites)
                        lower=len(pairs); upper=min(ceiling,upper)
                        kind='literal replacement neighborhoods'
                    examples.append(dict(seed=rep['seed'],sample=draw['sample'],size=len(sites),
                                     largest_single=best,blocks_touched=touch,
                                     two_cover=cover[0] if cover else None,partner_lower=lower,partner_upper=upper,
                                     source=kind,fingerprint=draw['fingerprint']))
                    checked+=1
                if checked==limit:break
            stage.hood.cache_clear()
            report[label]=examples
    return report


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('source',type=Path); ap.add_argument('directory',type=Path); ap.add_argument('out',type=Path)
    args=ap.parse_args()
    data=run(args.source,args.directory)
    args.out.write_text(json.dumps(dict(weighting='First recorded successful group traces of the named stage-specific hub proposal. These witnesses are not an equal-group census.',stages=data),indent=1)+'\n')
    print([(k,len(v)) for k,v in data.items()])
