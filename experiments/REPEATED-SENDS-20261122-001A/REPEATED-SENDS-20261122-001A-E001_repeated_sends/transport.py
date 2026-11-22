"""Transport the enrolled name banks and replay source/receiver counterfactual eligibility."""
from hashlib import sha256
from itertools import combinations_with_replacement
from random import Random
import gzip
import json

from gate import archive, OUT


def bits(word, row):
    return ''.join(str((word>>d)&1) for d in row)


def mask(names):
    return sum(1<<d for d in names)


def main():
    g=archive('growth.json.gz')
    with gzip.open(OUT/'witnesses.json.gz','rt') as f: witnesses=json.load(f)['full_examples']
    with gzip.open(OUT/'joint.json.gz','rt') as f: joint=json.load(f)
    cases=[]
    for law in ('parity','nae'):
        for route in ('intact','interrupted','sham'):
            record=g['cases'][route][law]
            stars=g['original_stars']+[b['consumed_names']+b['fresh_names'] for c in record['cuts'] for b in c['births']]
            n=1+max(max(row) for row in stars); rng=Random(20261122030702)
            names=list(range(n)); rng.shuffle(names)
            holders=list(range(len(stars)));rng.shuffle(holders)
            other=[None]*len(stars)
            for k,row in enumerate(stars):
                idx=[names[d] for d in row];other[holders[k]]=(mask(idx),len(idx))
            a,b=names[510],names[563];rz=[names[d] for d in record['receivers']['R']['fresh_names']]
            checks=0; successfully=0
            for key,examples in witnesses.items():
                if not key.startswith(f'{law}-{route}-'):continue
                for tag,item in examples.items():
                    w=int(item['before_late_checks'],16); word=mask(names[d] for d in range(n) if w>>d &1)
                    swap=word^(1<<a)^(1<<b)
                    def legal(target):
                        count=[((target & m).bit_count(),arity) for m,arity in other]
                        return all((k%2==0 if law=='parity' else 0<k<sz) for k,sz in count)
                    assert legal(word) and legal(swap)==item['late_lawful']
                    assert bits(word,rz)==bits(swap,rz)==item['R_fresh']
                    assert bits(word,rz[::-1])==item['R_fresh'][::-1]
                    checks+=1;successfully+=int(item['late_lawful'])
            cases.append({'law':law,'route':route,'whole_counterfactuals_transported':checks,'admitted_positive':successfully})
    # Scoring positions are not variables of the observer. F never promises an event after that attempt.
    clock={b:desc for b,desc in [('E','before any growth payment; R absent'),
             ('P','after the source paid and before R is born'), ('B','R already has the birth sample, before its sole finish'),
             ('F','R already has its terminal sample; no future local finish')]}
    schedules={p+q:{'first':clock[p],'second':clock[q],'initial_sample_precedes_second':q in 'BF',
                   'first_finish_precedes_second':q=='F','another_finish_available_after_first':False}
               for p,q in combinations_with_replacement('EPBF',2)}
    counts={}
    for field in ('TT_actual_population','II_TT_mixture_actual_population'):
        counts[field]=sum(bool(joint['summaries'][c['summary']][field]['any_record_excludes_globally_attainable_status'])
                          for c in joint['comparisons'])
    out={'transport_seed':20261122030702,'actual_replay':cases,'all_band_pairs':schedules,
         'any_record_excludes_globally_attainable_status_cells':counts,
         'joint_sha256':sha256((OUT/'joint.json.gz').read_bytes()).hexdigest()}
    (OUT/'transport.json').write_text(json.dumps(out,indent=2,sort_keys=True)+'\n')


if __name__=='__main__':main()
