"""Exact local supports, full physical completions and optional conditional birth weights."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import product
from pathlib import Path
import gzip
import json
import os
import subprocess
import sys

from pysat.solvers import Minisat22
from growth import load, original_values, stars_at


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUT = ROOT / 'artifacts' / HERE.parent.name / HERE.name
SIDES = (515, 555)
SEND = (510, 563)
SPARE = 677
P_INPUT = (518, 523)
ROUTES = ('intact','interrupted','sham')
RECEIVERS = ('C','D','R','J')


def mask(names):
    return sum(1 << name for name in names)


def bits(word, names):
    return ''.join(str((word >> d) & 1) for d in names)


def setbank(names, values):
    return mask(d for d,v in zip(names,values,strict=True) if v == '1')


def lawful(n, k, law):
    return k % 2 == 0 if law == 'parity' else 0 < k < n


@cache
def fresh_words(law, paid, length):
    return tuple(''.join(w) for w in product('01', repeat=length)
                 if lawful(len(paid)+length, paid.count('1') + w.count('1'),law))


def parity_solution(rows, pins):
    table = {}
    for row, result in [(mask(row),0) for row in rows]+[(1<<d,v) for d,v in sorted(pins.items())]:
        while row:
            i = row.bit_length()-1
            if i not in table:
                table[i] = row, result
                break
            b, r = table[i]
            row ^= b
            result ^= r
        else:
            if result:
                return None
    out = 0
    for i, (w,r) in sorted(table.items()):
        if (out & w).bit_count()%2 != r:
            out |= 1 << i
    return out


def calibration(data, law, old_stars, side):
    archived = mask(d for d,v in original_values(data, law).items() if int(v))
    pins = {**dict(zip(SEND,(0,1))), **dict(zip(SIDES,map(int,side))),
            **{d:(archived >> d)&1 for d in (SPARE,*P_INPUT)}}
    if side == '00':
        candidate = archived
    elif law == 'parity':
        candidate = parity_solution(old_stars,pins)
    else:
        with Minisat22() as solver:
            for row in old_stars:
                solver.add_clause([d+1 for d in row])
                solver.add_clause([-d-1 for d in row])
            for d,v in sorted(pins.items()):
                solver.add_clause([d+1 if v else -d-1])
            candidate = mask(x-1 for x in solver.get_model() if x>0) if solver.solve() else None
    if candidate is not None:
        assert all((candidate>>d & 1)==v for d,v in pins.items())
        assert all(lawful(len(row),(candidate & mask(row)).bit_count(),law) for row in old_stars)
    return candidate


class Frame:
    def __init__(self,data,condition,law):
        self.law = law
        self.condition = condition
        self.case = data['cases'][condition][law]
        self.cuts = [x['births'] for x in self.case['cuts']]
        self.births = {b['holder']:b for cut in self.cuts for b in cut}
        self.stages = [stars_at(data,condition,law,i) for i in range(4)]
        self.all_rows = tuple((len(row),mask(row)) for row in self.stages[3])
        original_size = len(self.stages[0]); self.original_names = max(max(row) for row in self.stages[0])+1
        frontier = set(range(original_size))
        seen_names = set(range(self.original_names))
        for layer in self.cuts:
            layer_fresh = set()
            for b in layer:
                assert len(b['consumed_names'])==len(b['parents']) and set(b['parents'])<=frontier
                assert b['fresh_names'] and b['grant']==len(b['fresh_names'])
                assert not (set(b['fresh_names']) & (seen_names|layer_fresh))
                layer_fresh.update(b['fresh_names'])
            seen_names.update(layer_fresh)
            frontier = {b['holder'] for b in layer}
        self.ids = {key: next(b['holder'] for b in self.births.values()
                         if b['fresh_names']==self.case['receivers'][key]['fresh_names']) for key in RECEIVERS}
        self.masks = {h:mask(b['consumed_names']) for h,b in self.births.items()}
        self.new_masks = {h:mask(b['fresh_names']) for h,b in self.births.items()}

    def complete(self, old, overrides):
        word = old
        for births in self.cuts:
            for b in births:
                h = b['holder']
                count = (word & self.masks[h]).bit_count()
                size = len(b['consumed_names'])+b['grant']
                if h in overrides:
                    bank = overrides[h]
                    assert len(bank)==b['grant'] and lawful(size,count + bank.count('1'),self.law)
                    word |= setbank(b['fresh_names'],bank)
                elif not lawful(size,count,self.law):
                    word |= 1<<b['fresh_names'][-1]
        self.check(word)
        return word

    def check(self,word):
        assert all(lawful(n,(m & word).bit_count(),self.law) for n,m in self.all_rows)

    def options(self,h,old):
        b = self.births[h]
        return fresh_words(self.law,bits(old,b['consumed_names']),b['grant'])

    def readings(self,target,old):
        h = self.ids[target]
        b = self.births[h]
        if target in ('C','D'):
            legal = self.options(h,old)
            return {w:{h:w} for w in legal}, {w:Fraction(1,len(legal)) for w in legal}
        # Fixed complete old values make these two separate first-cut completions independent.
        choices = []
        support_paid = []
        for parent, paid_name in zip(b['parents'],b['consumed_names'],strict=True):
            p = self.births[parent]
            allowed_words = self.options(parent,old)
            i = p['fresh_names'].index(paid_name)
            choices.append((parent,i,allowed_words))
            support_paid.append({v[i] for v in allowed_words})
        assert b['parents'][0]!=b['parents'][1]
        projected = {w for a,c in product(*support_paid) for w in fresh_words(self.law,a+c,b['grant'])}
        witnesses = {}
        probability = Counter()
        for left,right in product(choices[0][2],choices[1][2]):
            paid = left[choices[0][1]] + right[choices[1][1]]
            new = fresh_words(self.law,paid,b['grant'])
            mass = Fraction(1,len(choices[0][2])*len(choices[1][2])*len(new))
            for w in new:
                witnesses.setdefault(w,{choices[0][0]:left, choices[1][0]:right, h:w})
                probability[w] += mass
        assert set(witnesses) == set(probability) == projected and sum(probability.values())==1
        return witnesses, dict(probability)


def overlap(left,right):
    a,b = set(left),set(right)
    return {'counts':[len(a),len(b)],'common':sorted(a&b),'exclusive_idle':sorted(a-b),
            'exclusive_swap':sorted(b-a),'union_size':len(a|b),'zero_error':not bool(a&b)}


def stats(first,second):
    assert sum(first.values()) == sum(second.values()) == 1
    delta = sum(abs(first.get(w,0)-second.get(w,0)) for w in set(first)|set(second))/2
    return {'total_variation':str(delta),'equal_prior_optimal_accuracy':str((1+delta)/2),
            'idle':{w:str(v) for w,v in sorted(first.items())},'swap':{w:str(v) for w,v in sorted(second.items())}}


def couple_primary(frame,target_word,old,standing,first_support):
    # The two altered first holders are also the two parents of an actual second birth.
    target = frame.births[frame.ids['R']]
    altered = [b for b in frame.cuts[0] if set(b['consumed_names']) & set(SEND)]
    assert len(altered)==2
    changed_ids = {b['holder'] for b in altered}
    meeting, = (b for b in frame.cuts[1] if set(b['parents'])==changed_ids)
    charge = tuple(meeting['consumed_names'])
    source_swap = mask(SEND)
    if frame.law == 'parity':
        base = frame.complete(old,first_support[target_word]); other = base^source_swap^mask(charge)
        frame.check(other)
        assert bits(base,target['fresh_names'])==bits(other,target['fresh_names'])==target_word
        assert bits(base,target['consumed_names'])==bits(other,target['consumed_names'])
        return base,other, {'equal_entire_fresh':False,'only_changed_fresh':charge,
                             'joint_second_payment':meeting['holder']}
    # A shared first-bank completion exists after either changed paid value. Enroll a common
    # first word at every changed holder and at R's parents, then impose the same local R word.
    first_ids = sorted(changed_ids | set(target['parents']))
    candidates = {h:sorted(set(frame.options(h,old)) & set(frame.options(h,standing))) for h in first_ids}
    assert all(candidates.values())
    for trial in product(*(candidates[h] for h in first_ids)):
        rows = dict(zip(first_ids,trial,strict=True))
        paid = ''.join(rows[p][frame.births[p]['fresh_names'].index(d)]
                       for p,d in zip(target['parents'],target['consumed_names'],strict=True))
        if target_word in fresh_words(frame.law,paid,target['grant']):
            rows[frame.ids['R']] = target_word
            base = frame.complete(old,rows); other = base^source_swap
            frame.check(other)
            assert bits(other,target['fresh_names'])==target_word
            return base,other, {'equal_entire_fresh':True,'only_changed_fresh':[], 'joint_second_payment':None}
    raise ValueError('Could not extend an identical fresh assignment across the matched sends')


def renamed_checks(frame,pair):
    from random import Random
    rows = frame.stages[-1]
    n_names = max(max(row) for row in rows)+1
    rng=Random(202611220307)
    remap=list(range(n_names)); rng.shuffle(remap)
    order=list(range(len(rows))); rng.shuffle(order)
    renamed=[None]*len(rows)
    for i, row in enumerate(rows):
        renamed[order[i]]=tuple(remap[d] for d in row)
    new_words=[mask(remap[i] for i in range(n_names) if w>>i&1) for w in pair]
    assert all(lawful(len(row),(word&mask(row)).bit_count(),frame.law)
               for row in renamed for word in new_words)
    for target,h in frame.ids.items():
        original=frame.births[h]['fresh_names']
        for rev in (False,True):
            ix=original[::-1] if rev else original
            assert [bits(w,ix) for w in pair]==[bits(w,[remap[d] for d in ix]) for w in new_words]
    return {'scope':'all whole law constraints, C/D/R/J full observed fresh words, both slot orientations',
            'complete_words':2,'seed':202611220307,'holders':len(order),'distinctions':n_names}


def canonical_knot(law):
    keys=('l','r','k')
    cnf=';'.join(' '.join(('~' if v=='1' else '')+d for v,d in zip(w,keys))
                 for w in product('01',repeat=3) if not lawful(3,w.count('1'),law))
    cmd=[sys.executable,'-B','-m','knotlab','check','--cnf',cnf,'--loops','l','r','--contact','k','--json']
    p=subprocess.run(cmd,env={**os.environ,'PYTHONPATH':str(ROOT/'tools')},capture_output=True,text=True,check=True)
    d=json.loads(p.stdout)
    assert d['is_knot'] and d['binding'] and d['loss_on_erasure'] and d['coexistence']
    return {'cnf':cnf,'allowed':d['allowed'],'K1_K2_K3':d['is_knot']}


def encoded(x):
    return (json.dumps(x,sort_keys=True,separators=(',',':'))+'\n').encode()


def main():
    data=load()
    report={'schema':'fresh-sender-supports-v1','laws':{},'background_inputs':{},'projections':[],
            'reader_local_clock':{},'unknown_reference_union':[],'recodings':[]}
    witness={'schema':'fresh-sender-witnesses-v1','old_words':{},'whole_extensions':[]}
    concrete=Counter()
    for law in ('parity','nae'):
        report['laws'][law]=canonical_knot(law)
        frames={mode:Frame(data,mode,law) for mode in ROUTES}
        report['reader_local_clock'][law]={}
        for mode,frame in frames.items():
            clocks={}
            for k in RECEIVERS:
                clock=frame.case['receivers'][k]['local_clock']
                assert len(clock)>=2 and clock[0]!=clock[-1]
                clocks[k]=clock
            report['reader_local_clock'][law][mode]=clocks
        assert report['reader_local_clock'][law]['intact']==report['reader_local_clock'][law]['interrupted']
        assert report['reader_local_clock'][law]['intact']==report['reader_local_clock'][law]['sham']
        pooled=defaultdict(lambda:[set(),set()])
        for side in ('00','01','10','11'):
            old=calibration(data,law,frames['intact'].stages[0],side)
            key=f'{law}-{side}'
            if old is None:
                report['background_inputs'][key]={'realizable':False}
                continue
            words=(old,old^mask(SEND))
            archived=mask(d for d,v in original_values(data,law).items() if int(v))
            report['background_inputs'][key]={'realizable':True,'old_changed_vs_archive':
                    [i for i in range(frames['intact'].original_names) if ((old^archived)>>i)&1],
                    'old_fixed_in_both_offers':hex(old),'side':side,'spare':bits(old,[SPARE]),
                    'P_paid':bits(old,P_INPUT)}
            witness['old_words'][key]={'common_before':hex(old),'sender_idle_and_swap':list(map(hex,words))}
            for mode,frame in frames.items():
                for target in RECEIVERS:
                    h=frame.ids[target]
                    b=frame.births[h]
                    both=[frame.readings(target,word) for word in words]
                    supports=[pair[0] for pair in both]
                    dist=[pair[1] for pair in both]
                    observation=overlap(*supports)
                    each=[]
                    for i in range(b['grant']):
                        each.append(overlap({w[i] for w in supports[0]},{w[i] for w in supports[1]}))
                    assert overlap({w[::-1] for w in supports[0]},{w[::-1] for w in supports[1]})['counts']==observation['counts']
                    report['projections'].append({'law':law,'side':side,'route':mode,'target':target,
                              'fresh_slots':b['fresh_names'],'support':observation,'individual':each,
                              'weighted':stats(*dist),'cancelled_later_birth_weight':True})
                    for i in (0,1):
                        pooled[mode,target][i].update(supports[i])
                    for shown in sorted(set(supports[0])|set(supports[1])):
                        whole=[]
                        coupling=None
                        if target=='R' and shown in supports[0] and shown in supports[1]:
                            left,right,coupling=couple_primary(frame,shown,*words,supports[0])
                            whole=[left,right]
                        else:
                            whole=[frame.complete(oldword,bank[shown]) if shown in bank else None
                                   for oldword,bank in zip(words,supports,strict=True)]
                        for i,w in enumerate(whole):
                            if w is not None:
                                assert (w&((1<<frame.original_names)-1))==words[i]
                                assert bits(w,b['fresh_names'])==shown
                                if target=='R' and whole[1-i] is not None:
                                    assert bits(w,frame.stages[-1][h])==bits(whole[1-i],frame.stages[-1][h])
                        witness['whole_extensions'].append({'law':law,'side':side,'route':mode,'target':target,
                               'fresh_value':shown,'same_prestate':key,'complete_reached':
                                     [hex(x) if x is not None else None for x in whole],'coupling':coupling})
                        concrete[law]+=sum(w is not None for w in whole)
                        if target=='R' and side=='00' and shown=='000' and None not in whole:
                            report['recodings'].append({'law':law,'route':mode,**renamed_checks(frame,whole)})
        for (mode,target),arms in sorted(pooled.items()):
            report['unknown_reference_union'].append({'law':law,'route':mode,'target':target,
                                                       'support':overlap(*arms)})
    # Intact and coherent-sham readings must match exactly, including probabilities.
    comp={(x['law'],x['side'],x['route'],x['target']):x for x in report['projections']}
    for (law,side,mode,target),row in comp.items():
        if mode=='intact':
            sham=comp[law,side,'sham',target]
            assert all(row[k]==sham[k] for k in ('support','individual','weighted'))
    report['whole_extensions_verified_per_law']=dict(concrete)
    for filename,obj in [('whole_words.json.gz',witness),('supports.json.gz',report)]:
        (OUT/filename).write_bytes(gzip.compress(encoded(obj),compresslevel=9,mtime=0))
    print(json.dumps({'whole_extensions':concrete,'cells':len(report['projections']), 'sha256':{
        p:sha256((OUT/p).read_bytes()).hexdigest() for p in ('whole_words.json.gz','supports.json.gz')}}))


if __name__=='__main__':
    main()
