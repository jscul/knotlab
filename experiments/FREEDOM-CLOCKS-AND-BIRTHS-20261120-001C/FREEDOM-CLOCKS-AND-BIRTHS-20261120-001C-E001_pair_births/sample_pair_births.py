"""Exact finite competitor pools and independently seeded draws under the frozen weightings."""
from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from pathlib import Path
from random import Random
import gzip
import json
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
OUT=ROOT/'artifacts'/HERE.parent.name/HERE.name
OLD='READS-HOLDERS-SOURCES-20261120-001B'
sys.path.insert(0,str(ROOT/'experiments'/OLD/(OLD+'-E001_irredundant')))
from controls import deletions, interval, lawful, next_stage
from model import build, growth, nae_counts, parity_counts, width
from census_rates import canonical_pair_table


def serialized(value):
    return json.dumps(value,separators=(',',':'))


def digest(value):
    return sha256(serialized(value).encode()).hexdigest()


def load_large():
    previous='THREE-READERS-AND-GROWTH-20261120-001A'
    data=json.loads((ROOT/'artifacts'/previous/(previous+'-E001_three_readers')/'samples.json').read_text())
    result={k:tuple(map(tuple,data['cases'][k]['stars'])) for k in ('archive03','partnered')}
    for code in product((1,2),repeat=5):
        meetings=[(i,(i+1)%5) for i,q in enumerate(code) for _ in range(q)]
        result['cycle'+''.join(map(str,code))]=build(meetings,[3]*5)
    return result


def compiled(law,rows,large):
    small={}
    for i,row in enumerate(rows):
        entry=dict(row)
        entry['id']='small'+str(i)
        entry['source_arity']=entry['source_width']
        entry['meeting_count']=sum(map(len,entry['source_rows']))-entry['source_width']
        entry['holder_count']=len(entry['source_rows'])
        entry['pool']='small'
        if entry['first_status']=='births':
            entry['key']=serialized(entry['table_key'])
        small[entry['id']]=entry
    extra={}
    for key,raw in large.items():
        valid=lawful(raw,law)
        necessary=all(deletions(raw,law)[0])
        assert valid and necessary,(key,law)
        funded,reached,first=next_stage(raw,law)
        assert funded=='births',(key,law)
        nf,nb=growth(reached,law)
        extra[key]={'id':key,'pool':'explosive','source_rows':raw,'source_width':width(raw),'first_status':funded,
                    'stage_rows':reached,'stage_width':width(reached),'first_birth_count':len(first),
                    'next_status':nf,'next_birth_count':len(nb),'labelled_source_multiplicity':1}
    groups=defaultdict(list)
    for item in (*small.values(),*extra.values()):
        if item['first_status']=='births':
            groups[item['stage_width']].append(item)
    widths={}
    for n,records in groups.items():
        counts={r['next_birth_count'] for r in records}
        small_keys=defaultdict(set)
        for row in records:
            if row['pool']=='small':
                small_keys[row['key']].add(row['next_birth_count'])
        widths[str(n)]={'next_counts':sorted(counts),
                        'small_sources':sum(r['pool']=='small' for r in records),
                        'explosive_configurations':sum(r['pool']=='explosive' for r in records)}
        for row in records:
            if row['pool']=='small':
                row['small_birth_counts']=sorted(small_keys[row['key']])
        if len(counts)==1:
            for row in records:
                row['pooled_birth_counts']=sorted(counts)
                row['certificate']='width_alone'
            continue
        keys=defaultdict(set)
        for row in records:
            if row['pool']=='explosive':
                # No huge counts are needed when the observed width fixes the
                # integer before inspecting a single entry of the pair table.
                assert len(row['stage_rows'])<=20 or law=='parity',(n,row['id'])
                total,rates=(nae_counts if law=='nae' else parity_counts)(row['stage_rows'])
                row['key']=serialized(canonical_pair_table(n,total,rates).key)
                row['total_words']=total
            keys[row['key']].add(row['next_birth_count'])
        for row in records:
            row['pooled_birth_counts']=sorted(keys[row['key']])
            row['certificate']='complete_pair_table'
    return small,extra,widths


def sample(rng,rows,panel):
    if panel=='explosive':
        key=rng.choice(('cycle','archive03','partnered'))
        if key=='cycle':
            key+=''.join(str(rng.choice((1,2))) for _ in range(5))
        return rows[key]
    available=defaultdict(list)
    for source in rows.values():
        excess=source['meeting_count']-(source['holder_count']-1)
        if excess==(0 if panel=='tree' else 1):
            available[source['source_width']].append(source)
    n=rng.choice(sorted(available))
    choices=available[n]
    cutoff=rng.randrange(sum(r['labelled_source_multiplicity'] for r in choices))
    for row in choices:
        cutoff-=row['labelled_source_multiplicity']
        if cutoff<0:
            return row
    raise AssertionError('empty source choice')


def main():
    with gzip.open(OUT/'census_cases.json.gz','rt') as f:
        old_cases=json.load(f)
    large=load_large()
    report={}
    for law in ('nae','parity'):
        small,extra,widths=compiled(law,old_cases[law],large)
        panels={}
        for panel in ('tree','extra','explosive'):
            seed=sha256(f'FREEDOM-CLOCKS-AND-BIRTHS-20261120-001C|{law}|{panel}|202611203589'.encode()).digest()
            rng=Random(int.from_bytes(seed,'big'))
            draws=[]
            for i in range(128):
                row=sample(rng,extra if panel=='explosive' else small,panel)
                old_perm=list(range(row['source_width']))
                rng.shuffle(old_perm)
                record={'draw':i+1,'id':row['id'],'source_permutation':old_perm,'first_status':row['first_status']}
                if row['first_status']=='births':
                    stage_perm=list(range(row['stage_width']))
                    rng.shuffle(stage_perm)
                    record.update(stage_permutation_sha=digest(stage_perm),stage_width=row['stage_width'],
                                  next_count=row['next_birth_count'],pooled_birth_counts=row['pooled_birth_counts'],
                                  certificate=row['certificate'])
                    if row['pool']=='small':record['small_birth_counts']=row['small_birth_counts']
                draws.append(record)
            funded=[r for r in draws if r['first_status']=='births']
            decided=sum(len(d['pooled_birth_counts'])==1 for d in funded)
            decided_small=sum(len(d['small_birth_counts'])==1 for d in funded if 'small_birth_counts' in d)
            panels[panel]={'initial_draws':len(draws),'funded':len(funded),'initial_statuses':dict(Counter(r['first_status'] for r in draws)),
                           'decided_pooled':decided,'interval_pooled':interval(decided,len(funded)),
                           'decided_small_only':None if panel=='explosive' else decided_small,
                           'width_only_decisions':sum(d['certificate']=='width_alone' for d in funded),
                           'draws':draws}
        def brief(row):
            return {k:v for k,v in row.items() if k in ('id','source_width','stage_width','first_birth_count','first_status','next_status','next_birth_count','pooled_birth_counts','small_birth_counts','certificate','total_words','source_rows')}
        report[law]={'widths':widths,'large_support':[brief(row) for row in extra.values()],'panels':panels}
    result=OUT/'sample_pair_births.json'
    result.write_text(serialized(report)+'\n')
    for law,items in report.items():
        print(law,[(p,v['initial_draws'],v['funded'],v['decided_pooled'],v['decided_small_only']) for p,v in items['panels'].items()])


if __name__=='__main__':
    main()
