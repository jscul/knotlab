"""Joint probability of attempted and actual exchanges and the one genuine R record."""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import combinations_with_replacement, product
import gzip
import json

from gate import archive, BASE, OUT


SOURCES=(510,563)
BANDS='EPBF'
WORDS=('II','IT','TI','TT')
MODES=('structural','pointwise')
SIDES=('00','01','10','11')


def mask(names):
    return sum(1<<d for d in names)


def read(word,names):
    return ''.join(str(word>>d&1) for d in names)


def allowed(n, ones, law):
    return ones%2==0 if law=='parity' else 0<ones<n


@cache
def words(law,paid,n):
    return tuple(''.join(x) for x in product('01',repeat=n)
                 if allowed(len(paid)+n,paid.count('1')+x.count('1'),law))


def clean(prob):
    return {k:str(v) for k,v in sorted(prob.items()) if v}


def dump(path,obj):
    content=(json.dumps(obj,sort_keys=True,separators=(',',':'))+'\n').encode()
    path.write_bytes(gzip.compress(content,compresslevel=9,mtime=0))


class Frame:
    def __init__(self,source,condition,law):
        case=source['cases'][condition][law]
        self.law=law
        self.route=condition
        self.births=[b for cut in case['cuts'] for b in cut['births']]
        self.banks={b['holder']:b for b in self.births}
        self.receiver=self.banks[294]
        self.affected=tuple(b['holder'] for b in case['cuts'][0]['births'] if set(b['consumed_names']) & set(SOURCES))
        assert len(self.affected)==2
        self.foreground=sorted(set(self.affected)|set(self.receiver['parents']))
        self.stars=source['original_stars']+[b['consumed_names']+b['fresh_names'] for b in self.births]
        self.rows=[(len(row),mask(row)) for row in self.stars]
        self.smask=mask(SOURCES)
        self.row_data=[(b['holder'],b['fresh_names'][-1],mask(b['consumed_names']),len(b['consumed_names'])+b['grant'])
                       for b in self.births]

    def full(self,old,assign):
        result=old
        for h,last,paid,n in self.row_data:
            if h in assign:
                marks=self.banks[h]['fresh_names']
                result |= mask(d for d,v in zip(marks,assign[h],strict=True) if v=='1')
            elif not allowed(n,(result&paid).bit_count(),self.law):
                result |= 1<<last
        assert self.legal(result)
        return result

    def legal(self,word):
        return all(allowed(n,(word & m).bit_count(),self.law) for n,m in self.rows)

    def factor(self,old):
        parent_words={h:words(self.law,read(old,self.banks[h]['consumed_names']),self.banks[h]['grant'])
                      for h in self.foreground}
        share=Fraction(1)
        for choices in parent_words.values():share/=len(choices)
        R=self.receiver
        spots=[self.banks[h]['fresh_names'].index(d) for h,d in zip(R['parents'],R['consumed_names'],strict=True)]
        # First sum the common-cause parent allocations, without discarding failed post-payment offers.
        counts=Counter(); example={}
        for choice in product(*(parent_words[h] for h in self.foreground)):
            allocations=dict(zip(self.foreground,choice,strict=True))
            can_late=all(allowed(len(self.stars[h]),read(old ^ self.smask,self.banks[h]['consumed_names']).count('1')
                                +allocations[h].count('1'),self.law) for h in self.affected)
            paid=''.join(allocations[h][i] for h,i in zip(R['parents'],spots,strict=True))
            counts[can_late,paid]+=1
            example.setdefault((can_late,paid),allocations)
        joint=Counter(); witnesses={}
        for (late,paid),number in counts.items():
            finish=words(self.law,paid,R['grant'])
            for z in finish:
                joint[late,z]+=number*share/len(finish)
                if (late,z) in witnesses:continue
                chosen=example[late,paid]|{R['holder']:z}
                full=self.full(old,chosen); flipped=full ^ self.smask
                assert self.legal(flipped)==late
                assert read(full,R['fresh_names'])==read(flipped,R['fresh_names'])==z
                assert read(full,self.stars[80])!=read(flipped,self.stars[80])
                assert read(full,self.stars[294])==read(flipped,self.stars[294])
                witnesses[late,z]={'before_late_checks':hex(full),'would_be_after_one_late':hex(flipped),
                                   'late_lawful':late,'chosen_foreground':chosen,'R_fresh':z}
        assert sum(joint.values())==1 and {z for _,z in joint}==set(words_all(3))
        return joint,witnesses


def words_all(n):
    return tuple(''.join(x) for x in product('01',repeat=n))


def outcome(request,bands,operation,eligible):
    # If a post-payment move succeeds, the inverse always returns to the known lawful previous word.
    return ''.join('I' if q=='I' else 'M' if (b=='E' or (operation=='pointwise' and eligible)) else 'U'
                   for q,b in zip(request,bands,strict=True))


def visible(joint):
    p=Counter()
    for (status,z),v in joint.items():p[z]+=v
    return p


def equal_odds(p,q):
    assert sum(p.values())==sum(q.values())==1
    total_variation=sum(abs(p.get(z,0)-q.get(z,0)) for z in set(p)|set(q))/2
    best=(1+total_variation)/2
    return {'total_variation':str(total_variation),'accuracy':str(best),
            'histories_certifying_left':sorted(set(p)-set(q)),'histories_certifying_right':sorted(set(q)-set(p))}


def report_events(joint):
    assert sum(joint.values())==1
    occurrence=Counter(); byword=defaultdict(Counter); any2=Counter(); fewer=Counter()
    for (status,z),weight in joint.items():
        occurrence[status]+=weight
        byword[z][status]+=weight
        (any2 if status=='MM' else fewer)[z]+=weight
    possible=set(occurrence)
    mass2=sum(any2.values(),Fraction()); massother=1-mass2
    posterior={z:str(any2[z]/sum(arms.values())) for z,arms in sorted(byword.items())}
    status_at_each_word={z:sorted(arms) for z,arms in sorted(byword.items())}
    best=sum(max(any2[z],fewer[z]) for z in byword)
    joint_best=sum(max(arms.values()) for arms in byword.values())
    conditional_two=clean({z:w/mass2 for z,w in any2.items()}) if mass2 else None
    conditional_fewer=clean({z:w/massother for z,w in fewer.items()}) if massother else None
    return {'actual_status_mass':clean(occurrence),'two_realized':str(mass2),'fewer_realized':str(massother),
            'best_two_vs_fewer_prior':str(max(mass2,massother)),'best_two_vs_fewer_given_R':str(best),
            'best_exact_status_given_R':str(joint_best),'posterior_two_at_each_history':posterior,
            'status_at_each_word':status_at_each_word,
            'any_record_excludes_globally_attainable_status':any(set(arms)!=possible for arms in byword.values()),
            'R_given_two_realized':conditional_two,'R_given_fewer_realized':conditional_fewer}


def digest(blob):
    return sha256(json.dumps(blob,sort_keys=True,separators=(',',':')).encode()).hexdigest()


def dedup(table,entry):
    key=digest(entry)[:22]
    if key in table:assert table[key]==entry
    else:table[key]=entry
    return key


def main():
    source=archive('growth.json.gz'); old_data=archive('whole_words.json.gz'); prior=archive('supports.json.gz')
    baseline={(x['law'],x['route'],x['side']):x['weighted'] for x in prior['projections'] if x['target']=='R'}
    data={'schema':'repeated-sends-joint-v1','status_alphabet':{'I':'idle','M':'actually transposed',
          'U':'unadmitted/refused, without a local announcement'},'factors':{},'joint_laws':{},'summaries':{},
          'launches':[],'comparisons':[],'observer':{},'baseline_hashes':{},'recoding':{}}
    proofs={'full_examples':{},'common_old':old_data['old_words']}
    readable=[]
    for law in ('parity','nae'):
        for mode in ('intact','interrupted','sham'):
            frame=Frame(source,mode,law)
            data['observer'][f'{law}-{mode}']={'local_intro_and_finish':source['cases'][mode][law]['receivers']['R']['local_clock'],
               'birth_finish_probability':'P(z,z)=P(z), P(z,z\u2032)=0 for z\u2032 different from z',
               'further_positive_finishes':0}
            for side in SIDES:
                common=int(old_data['old_words'][f'{law}-{side}']['common_before'],16)
                launch=f'{law}-{mode}-{side}'; factors={}
                for early in (0,1):
                    k=f'{launch}-{early}'; post=common ^ (frame.smask if early else 0)
                    assert read(post,SOURCES)==('10' if early else '01')
                    factor,witnesses=frame.factor(post);factors[early]=factor
                    data['factors'][k]={'actual_first_payment_a_b':read(post,SOURCES),
                         'after_payment_eligible_and_R_word':{f'{int(ok)}|{z}':str(w) for (ok,z),w in sorted(factor.items())}}
                    proofs['full_examples'][k]={f'{int(ok)}|{z}':val for (ok,z),val in witnesses.items()}
                    observed=Counter()
                    for (ok,z),num in factor.items():observed[z]+=num
                    assert clean(observed)==baseline[law,mode,side]['swap' if early else 'idle']
                for b0,b1 in combinations_with_replacement(BANDS,2):
                    band=b0+b1
                    for operation in MODES:
                        all_status={}
                        for request in WORDS:
                            early=sum(q=='T' and b=='E' for q,b in zip(request,band))%2
                            joint=Counter(); refs=defaultdict(list)
                            for (ok,z),v in factors[early].items():
                                status=outcome(request,band,operation,ok); joint[status,z]+=v
                                refs[status+'|'+z].append(f'{int(ok)}|{z}')
                            assert sum(joint.values())==1
                            all_status[request]=joint
                            jobj={'joint_P_actual_and_local':{status+'|'+z:str(w) for (status,z),w in sorted(joint.items())},
                                  'eligible_witness_references':{k:sorted(a) for k,a in sorted(refs.items())}}
                            data['launches'].append({'basis':launch,'bands':band,'class':operation,'request':request,
                                   'factor':f'{launch}-{early}','joint':dedup(data['joint_laws'],jobj)})
                        probs={q:visible(x) for q,x in all_status.items()}
                        eq=equal_odds(probs['II'],probs['TT'])
                        prior_score=Fraction(baseline[law,mode,side]['equal_prior_optimal_accuracy'])
                        mix=Counter()
                        for q in ('II','TT'):
                            for key,num in all_status[q].items():mix[key]+=num/2
                        details={'II_vs_TT':eq,'TI_vs_TT':equal_odds(probs['TI'],probs['TT']),
                                 'II_vs_IT':equal_odds(probs['II'],probs['IT']),'single_B307_accuracy':str(prior_score),
                                 'birth_alone':eq['accuracy'],'birth_plus_finish':eq['accuracy'],
                                 'gain_from_second_local_sample': '0',
                                 'full_vs_single_B307':str(Fraction(eq['accuracy'])-prior_score),
                                 'TT_actual_population':report_events(all_status['TT']),
                                 'II_TT_mixture_actual_population':report_events(mix)}
                        data['comparisons'].append({'basis':launch,'bands':band,'class':operation,
                                                   'summary':dedup(data['summaries'],details)})
                        if side=='00' and mode!='sham' and operation in MODES and band in ('EE','EP','PP'):
                            tt=details['TT_actual_population']
                            readable.append({'law':law,'route':mode,'bands':band,'class':operation,
                                 'II_vs_TT_accuracy':eq['accuracy'],'TT_status':tt['actual_status_mass'],
                                 'posterior_actual_2_given_word_within_TT':tt['posterior_two_at_each_history'],
                                 'true_two_class_accuracy_given_R_within_TT':tt['best_two_vs_fewer_given_R']})
    assert len(data['launches'])==1920 and len(data['comparisons'])==480
    for nm in ('growth.json.gz','supports.json.gz','whole_words.json.gz'):
        data['baseline_hashes'][nm]=sha256((BASE/nm).read_bytes()).hexdigest()
    data['recoding']={'rule':'a coherent physical recoding fixes the transported bank; reversing receiver slot order maps z to z[::-1] at both samples',
                      'checked_all_joint_laws':len(data['joint_laws'])}
    for tab in data['joint_laws'].values():
        raw=tab['joint_P_actual_and_local']; reversed_slots={k.split('|')[0]+'|'+k.split('|')[1][::-1]:v for k,v in raw.items()}
        assert len(reversed_slots)==len(raw) and sum(Fraction(x) for x in reversed_slots.values())==1
    dump(OUT/'joint.json.gz',data);dump(OUT/'witnesses.json.gz',proofs)
    (OUT/'archive_reference_summary.json').write_text(json.dumps(readable,indent=2,sort_keys=True)+'\n')
    print('Compared',len(data['launches']),'launches,',len(data['comparisons']),'repeated-intent cases.')


if __name__=='__main__':
    main()
