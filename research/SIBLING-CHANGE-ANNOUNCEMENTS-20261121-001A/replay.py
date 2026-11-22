"""Mixed sibling flags, independently computed from paid-word amplitudes and exact integer costs."""
from collections import Counter
from contextlib import redirect_stdout
from fractions import Fraction as F
from functools import cache
import argparse
import gzip
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from io import StringIO
from itertools import combinations, product
import json
from pathlib import Path
import sys

from sibling_forms import B3, ZERO, birth_rows, chars, focal, form_at, histogram, integer, matrix, outer, plus, quantities, select, table, times, zerolabel

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
PRE=ROOT/'research/SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001A'
CHECK=PRE.with_name(PRE.name[:-1])/'price_check.py'
PREV=PRE/'announcement_evidence.json.gz'
OPT=PRE/'announcement_rules.py'
TARGET=F(1,28)
LAWS=('nae','parity')
MODES=('retained','clean')
ROWS=range(512)
FULL=(1,)*512


def load_module(name, path):
    spec=spec_from_file_location(name,path)
    mod=module_from_spec(spec)
    sys.modules[name]=mod
    spec.loader.exec_module(mod)
    return mod


def combined(rows,mask,key,h):
    return select(rows,mask,key,h)


def comp(mask):
    return tuple(1-x for x in mask)


def swapped(mask):
    return tuple(mask[i^1] for i in ROWS)


def complemented(mask):
    return tuple(mask[i^510] for i in ROWS)


def grade64():
    result={}
    for c in (0,1):
        vals=[]
        for a in product((0,1),repeat=6):
            z,x=a[::2],a[1::2]
            red=int(sum(x)>=2)-int(z==(c,c,c))-sum(x[i] and any(z[j]!=c for j in range(3) if j!=i) for i in range(3))
            vals.append(red)
        assert max(vals)==0
        result[c]=vals
    return result


def local_margins(q):
    for size in (1,2):
        for ids in combinations(range(3),size):
            prior={}
            for s,st in enumerate(B3):
                m=Counter()
                for ans,val in zip(B3,q[s],strict=True):
                    m[tuple(ans[i] for i in ids)]+=val
                same=tuple(st[i] for i in ids)
                assert m==prior.setdefault(same,m)


class FocalTables:
    """Index each exact matrix and its 64 cells, including zero-weight branches."""
    def __init__(self):
        self.ids={}
        self.rows=[]

    def index(self,law,form):
        key=law,form
        if key not in self.ids:
            t=table(law,form)
            w,v0=quantities(law,form,0); _,v1=quantities(law,form,1)
            assert min(x for r in t for x in r)>=0 and all(sum(r)==w for r in t)
            norm=[[x/w for x in r] for r in t] if w else None
            if norm:
                local_margins(norm)
            common=None
            if law=='parity' and norm and form[0]==form[2]:
                # A mixture of the two unanimous X product states has independent uniform Z values.
                common=[norm[7][x]/8 for z in range(8) for x in range(8)]
                assert sum(common)==1 and min(common)>=0
                for s in range(8):
                    observed=[F(0)]*8
                    for z in range(8):
                        for x in range(8):
                            observed[(z&(7^s))|(x&s)]+=common[8*z+x]
                    assert observed==norm[s]
            self.ids[key]=len(self.rows)
            self.rows.append({'law':law,'form':form,'raw_gram':matrix(law,form),'trace':w,
                              'setting_rows_raw':t,'conditional_table':norm,'raw_witness_by_orientation':(v0,v1),'parity_common_weights_if_present_Z_word_then_X_word':common,
                              'normalization':'Divide raw 64 cells by launch_denominator to get setting-conditional launch masses; divide by another eight for the joint choice and answer.'})
        return self.ids[key]

    def packet(self,law,g,den,c):
        ident=self.index(law,g)
        w,v=quantities(law,g,c)
        return {'table':ident,'raw_weight':w,'raw_witness':v,'I':v/w if w else None,
                'launch_mass':w/F(den),'launch_denominator':den,'setting_and_answer_denominator':8*den}


def word_reconciliation(rows,law,source,prior,table_store):
    gprev=prior['paid_and_loose_physical_evidence']['gram_library']
    former=prior['paid_and_loose_physical_evidence']['laws'][law]['rows']
    grams=source['gram_library'];probs=source['probability_library']
    literal=source['laws'][law]
    checked={}
    for i,(obj,phys) in enumerate(zip(rows,literal['rows'],strict=True)):
        assert phys['u']==f'{i//2:08b}' and phys['b']==i%2
        for mode in MODES:
            g=obj[mode]; w,v=quantities(law,g,0)
            assert phys[mode]['weight']==w and F(phys[mode]['wI0'])==v
        for form,idx in zip((obj['retained'],*obj['h']),[phys['retained']['gram'],*phys['character_grams']],strict=True):
            assert tuple(map(tuple,grams[idx]))==matrix(law,form)
            if idx not in checked:
                j=table_store.index(law,form); norm=table_store.rows[j]['conditional_table']
                assert (None if norm is None else [[str(x) for x in r] for r in norm])==probs[idx]
                checked[idx]=j
    # Undo the real two-port sum and difference analytically to recover every historical Z fibre.
    for u in range(256):
        u0,u1=rows[2*u]['paid_path_amplitudes'],rows[2*u+1]['paid_path_amplitudes']
        for t in (0,1):
            coeff=[(a+(-1)**t*b)//2 for a,b in zip(u0,u1,strict=True)]
            assert all(i in (0,1) for i in coeff)
            d=(sum(coeff[:8]),0,sum(coeff[8:]))
            ah,bh=chars(coeff[:8]+[0]*8),chars([0]*8+coeff[8:])
            q=tuple(outer(a,b) for a,b in zip(ah,bh,strict=True))
            f=former[2*u+t]
            for z,j in zip((d,*q),[f['retained']['gram'],*f['character_grams']],strict=True):
                assert matrix(law,z)==tuple(map(tuple,gprev[j]))
    original=prior['laws'][law]
    ctl=original['source_and_instrument_controls']
    prior_controls={}
    for mode in MODES:
        current=rows[0],rows[1]
        k=ctl[mode]['eight_ordinary_zero_plus_one_sibling_change']
        den=original['N']*(2 if mode=='retained' else 32)
        for b,key in enumerate(('coherent_plus','coherent_minus','diagonal_fair_accept')):
            z=(current[b][mode] if b<2 else (current[0]['sibling_tag_retained'] if mode=='retained' else current[0]['sibling_tag_h'][0]))
            packet=table_store.packet(law,z,den,0); other=k[key]
            assert 2*F(other['raw_trace'])==packet['raw_weight'] and packet['launch_mass']==F(other['launch_mass'])
            assert packet['I']==F(other['conditional_I']) if other['conditional_I'] is not None else packet['I'] is None
            assert matrix(law,z)==tuple(tuple(2*F(x) for x in rr) for rr in other['gram'])
        prior_controls[mode]={'old_all_Z_rates':{f:original['modes'][mode]['primary_and_controls_rules']['full/'+f]['per_initial_launch_rate'] for f in ('deterministic','randomized')},
                              'old_eight_Z_max_I':original['modes'][mode]['max_achieved_I_among_one_missing_coordinate_by_index'][-1]}
    return {'physical_table_ids_to_current_index':checked,'all_512_literal_and_old_Z_fibres_reconciled':True,
            'both_prior_change_ports_and_diagonal_reconciled':True,'ordinary_comparison':prior_controls}


def paired_source(law,rows,mask,mode,N,W,c,store):
    den=(2 if mode=='retained' else 32)*N
    no=comp(mask)
    def get(port,how,chosen=mask,h=0,d=den):
        return store.packet(law,select(rows,chosen,how,h),d,c)
    def trio(real_key,idx,launch,refusal_form,chosen=mask):
        a=get('go',real_key,chosen,idx,launch); b=get('decline',real_key,comp(chosen),idx,launch)
        f=store.packet(law,refusal_form,launch,c)
        assert a['launch_mass']+b['launch_mass']+f['launch_mass']==1
        elig=a['launch_mass']+b['launch_mass']
        return {'go':a,'eligible_decline':b,'source_refuses_before_announcement':f,
                'source_eligible':elig,'go_given_source_eligible':a['launch_mass']/elig if elig else None}
    all_d=select(rows,FULL,'retained')
    all_q=select(rows,FULL,'h',0)
    all_z_tag=select(rows,FULL,'sibling_tag_h',0)
    def refusal(w): return plus(times(16,all_d),times(-1,w)) if mode=='clean' else ZERO
    nominal=trio(mode,0,den,refusal(all_q))
    record={'nominal':nominal,
            'separate_source_status_and_announcement_banks':{'eligible go':('101','101'),'eligible decline':('101','011'),
             'source refuses':('011','110'),'disconnected public bank':'110 on every attempt; actual delivered go probability zero',
             'occupied bank':'an earlier 101 does not count as a new write',
             'delivery':'One supplied status and binary flag is delivered before the independent focal settings. Diagnostic continuations at actual failures carry separate source labels.'}}
    tagged_key='sibling_tag_retained' if mode=='retained' else 'sibling_tag_h'
    record['changed_sibling_previous_Z_physically_copied_and_ignored_or_diagonal_comparator']=trio(tagged_key,0,den,refusal(all_z_tag))
    record['changed_sibling_tag_coherently_returned_before_X']=nominal
    wrong=swapped(mask)
    record['input_Z_phase_at_fixed_X_and_fixed_mask']=trio(mode,0,den,refusal(all_q),wrong)
    # The phase exchanges the sign blocks for every paid history, not merely in distribution.
    for p in (0,1):
        for u in range(256):
            d,k=rows[2*u]['paid_path_amplitudes'],rows[2*u+1]['paid_path_amplitudes']
            physical=tuple((a+b)//2+(-1)**(p+1)*(a-b)//2 for a,b in zip(d,k,strict=True))
            assert physical==tuple(rows[2*u+(1-p)]['paid_path_amplitudes'])
    assert swapped(wrong)==tuple(mask)
    record['same_input_Z_phase_and_physically_reversed_mask']=nominal
    # Accepted and declined ledgers at every h, including the counterfactual application of this same mask on refused h.
    ports=[]
    for h in range(16):
        clean_go=select(rows,mask,'h',h);clean_no=select(rows,no,'h',h)
        d_go=select(rows,mask,'retained');d_no=select(rows,no,'retained')
        z_go=select(rows,mask,'sibling_tag_h',h); z_no=select(rows,no,'sibling_tag_h',h)
        tag_go=store.packet(law,d_go,32*N,c); tag_no=store.packet(law,d_no,32*N,c)
        assert tag_go['launch_mass']+tag_no['launch_mass']==F(1,16)
        port={'h':f'{h:04b}','normal_mask_go':store.packet(law,clean_go,32*N,c),
              'normal_mask_decline':store.packet(law,clean_no,32*N,c),'entire_port':store.packet(law,plus(clean_go,clean_no),32*N,c),
              'prior_changed_sibling_Z_tag_go':store.packet(law,z_go,32*N,c),'prior_changed_sibling_Z_tag_decline':store.packet(law,z_no,32*N,c),
              'spent_tag_left_go':tag_go,'spent_tag_left_decline':tag_no,
              'spent_tag_returned_matrices_and_masses':'same as the two normal_mask packets of this entry',
              'actual_clean_decision':'eligible' if not h else 'source refuses and announcement stays ready'}
        ports.append(port)
    for mask0 in (mask,no,FULL):
        assert plus(*(select(rows,mask0,'h',h) for h in range(16)))==times(16,select(rows,mask0,'retained'))
        assert plus(*(select(rows,mask0,'sibling_tag_h',h) for h in range(16)))==times(16,select(rows,mask0,'sibling_tag_retained'))
    if mode=='clean':
        record['all_plus_source_with_spent_copy_left_unread']=trio('retained',0,32*N,times(15,all_d))
        record['same_all_plus_source_after_coherent_return_of_spent_copy']=nominal
        t=record['all_plus_source_with_spent_copy_left_unread']
        assert t['source_eligible']==F(1,16) and t['go']==ports[0]['spent_tag_left_go'] and t['eligible_decline']==ports[0]['spent_tag_left_decline']
        assert nominal['go']==ports[0]['normal_mask_go'] and nominal['eligible_decline']==ports[0]['normal_mask_decline']
    record['diagnostic_same_mask_all_character_ports']=ports
    return record


def extra_controls(law,rows,mode,c,N,store):
    den=(2 if mode=='retained' else 32)*N
    return {'every_measured_sibling_singleton_sign_probability':('1/2','1/2'),
            'eight_zero_word_both_signs':[store.packet(law,rows[b][mode],den,c) for b in (0,1)],
            'none':store.packet(law,ZERO,den,c),'all':store.packet(law,select(rows,FULL,mode),den,c)}


def future_sibling(law,rows,mode,c,mask,N,store):
    # These two eight-word outcomes differ only by transposing names in the first sibling holder.
    # Fix the sign to plus. Both are always in the canonical declined branch.
    ids=[2*int(s,2) for s in ('00100001','01000001')]
    if c: ids=[i^510 for i in ids]
    l,r=(rows[i] for i in ids)
    assert all(mask[i]==0 for i in ids)
    assert l['paid_path_amplitudes']==r['paid_path_amplitudes'] and l[mode]==r[mode]
    # Identical full residual amplitudes mean the joint off-diagonal equals each diagonal.
    g=l[mode]; den=(2 if mode=='retained' else 32)*N
    w,_=quantities(law,g,c);assert w>0
    return {'conditional_on_two_word_span_with_same_decline':tuple(zerolabel(i) for i in ids),
            'diagnostic_span_price_per_initial_launch':2*w/den,'coarse_decline_followed_by_symmetric_pair_read_plus':1,
            'fine_(u,b)_copied_and_ignored_then_same_read_plus':F(1,2),'raw_surviving_offdiagonal_joint_block_before_fine_log':matrix(law,g),
            'raw_surviving_offdiagonal_joint_block_after_fine_log':matrix(law,ZERO),'denominator_before_conditional_normalization':den,
            'common_focal_reduced_table_of_the_two_protocols':store.packet(law,times(2,g),den,c)}


def controls_and_optima(law,rows,mode,c,opt,store):
    w,v=zip(*(quantities(law,row[mode],c) for row in rows),strict=True)
    N=int(sum(quantities(law,row['retained'],c)[0] for row in rows)//2)
    W=int(sum(quantities(law,row['clean'],c)[0] for row in rows)//2)
    den=(2 if mode=='retained' else 32)*N
    rules={}
    for key,view,fractional in [('deterministic','full',False),('randomized','full',True),('one_independent_fair_bit','independent_tenth_bit',False),
                                ('ignore_X_deterministic','eight',False),('ignore_X_randomized','eight',True)]:
        rule=opt(w,v,TARGET,view,fractional)
        weighted=rule['attained_weight']
        rule.update(per_launch_rate=weighted/F(den),per_prepared_rate=weighted/F(2*(N if mode=='retained' else W)),
                    positive_label_index_and_mask={zerolabel(i):z for i,z in enumerate(rule['mask']) if z})
        if key in ('deterministic','randomized'):
            mask=rule['mask']
            frac=[(i,x) for i,x in enumerate(mask) if 0<x<1]
            bits={}
            for i,x in frac:
                m=x.denominator;k=(m-1).bit_length()
                chance=w[i]/den; eb=F(k*2**k,m)
                bits[zerolabel(i)]={'pass_if_uniform_integer_below':x.numerator,'integer_from_zero_to':m-1,'bits_in_one_block':k,
                                     'reject_and_redraw_if_at_least':m,'eventual_decision_chance':1,'expected_bits_on_observation':eb,
                                     'original_chance_of_that_observation':chance,'expected_bits_per_initial_launch':chance*eb}
            rule['fresh_coins_for_canonical_mask']=bits
            rule['priced_transcript']=paired_source(law,rows,mask,mode,N,W,c,store)
            rule['later_sibling_control']=future_sibling(law,rows,mode,c,mask,N,store)
            assert rule['priced_transcript']['nominal']['go']['launch_mass']==rule['per_launch_rate']
        rules[key]=rule
    per_prefix=[(v[2*i]+v[2*i+1])/(w[2*i]+w[2*i+1]) for i in range(256) if w[2*i]+w[2*i+1]]
    assert rules['ignore_X_randomized']['attained_weight']==0
    return {'optima_and_controls':rules,'archive_and_no_read':extra_controls(law,rows,mode,c,N,store),
            'answer_both_signs_unread_best_eight_Z_I':max(per_prefix),
            'sibling_outcomes_with_zero_source_mass':tuple(zerolabel(i) for i,x in enumerate(w) if not x),
            'score_types_with_multiplicity':histogram(law,rows,mode,c),
            'base_control_eligible_before_sibling_announcement':F(1) if mode=='retained' else F(W,16*N)}


def compressed_certificate(law,rows):
    bins={}
    for i,row in enumerate(rows):
        u=f'{i//2:08b}'
        def block(word):
            return '0' if set(word)=={'0'} else '1' if set(word)=={'1'} else '*'
        first,second=sorted(block(u[z:z+3]) for z in (0,3))
        typ=first+second+'/'+block(u[6:])+'/'+('+' if i%2==0 else '-')
        terms={m:row[m] for m in MODES}
        if typ not in bins:
            bins[typ]={'representative':zerolabel(i),'multiplicity':0,'forms':terms,
                       'grade':{m:{'w':quantities(law,row[m],0)[0],'score':quantities(law,row[m],0)[1],
                                   '28d':28*quantities(law,row[m],0)[1]-quantities(law,row[m],0)[0]} for m in MODES}}
        assert terms==bins[typ]['forms']
        bins[typ]['multiplicity']+=1
    assert sum(q['multiplicity'] for q in bins.values())==512 and len(bins)==36
    return bins


def check_orientation(law,rows,experiments,store):
    # The ordinary global bit complement maps s to 15-s, u to 255-u
    # and may contribute (-1)^b to the signed sibling amplitude.
    for i,a in enumerate(rows):
        b=rows[i^510]
        assert all(q==(-1)**(i%2)*p for p,q in zip(a['paid_path_amplitudes'],reversed(b['paid_path_amplitudes']),strict=True))
        for j in ('retained','clean'):
            assert b[j]==tuple(reversed(a[j]))
        for h in range(16):
            assert a['h'][h]==tuple(reversed(b['h'][h]))
            sign=(-1)**((i%2)+h.bit_count())
            for cost in (0,1):
                def amp(k,d):
                    return sum(q*(-1)**(s&h).bit_count() for s,q in enumerate(k['paid_path_amplitudes']) if s>>3==d)
                assert amp(b,1-cost)==sign*amp(a,cost)
    cert={}
    for mode in MODES:
        by={}
        for form in ('deterministic','randomized'):
            a=experiments[mode]['0']['optima_and_controls'][form]; b=experiments[mode]['1']['optima_and_controls'][form]
            mask=complemented(a['mask'])
            assert a['per_launch_rate']==b['per_launch_rate']
            z=select(rows,mask,mode)
            assert z==tuple(reversed(select(rows,a['mask'],mode)))
            n=a['priced_transcript']['nominal']['go']
            p=store.packet(law,z,n['launch_denominator'],1)
            assert p['I']==n['I'] and p['launch_mass']==n['launch_mass']
            qa=store.rows[n['table']]['conditional_table'];qb=store.rows[p['table']]['conditional_table']
            if qa:
                assert all(qb[s][y]==qa[s][y^(7^s)] for s in range(8) for y in range(8))
            by[form]={'transported_c0_mask_in_c1_labels':{zerolabel(i):x for i,x in enumerate(mask) if x},
                     'coincides_with_separately_lexicographic_choice':list(mask)==b['mask'],'transported_table':p}
        cert[mode]=by
    return cert


def build():
    import physical
    phys=physical.run()
    previous=json.loads(gzip.decompress(PREV.read_bytes()))
    old_check=load_module('b300_separate_coordinator_prices',CHECK)
    buf=StringIO()
    with redirect_stdout(buf):
        old_check.main()
    opt=load_module('previous_full_flag_optimizer',OPT).optimize
    store=FocalTables()
    data={}
    for law in LAWS:
        rows=birth_rows(law)
        compare=word_reconciliation(rows,law,phys,previous,store)
        outcomes={m:{str(c):controls_and_optima(law,rows,m,c,opt,store) for c in (0,1)} for m in MODES}
        same=check_orientation(law,rows,outcomes,store)
        # The mixed-basis pair with the X answer forgotten is exactly the previous eight-bit record.
        for m in MODES:
            for c in (0,1):
                omit=outcomes[m][str(c)]['answer_both_signs_unread_best_eight_Z_I']
                assert omit==F(compare['ordinary_comparison'][m]['old_eight_Z_max_I'])
                for f in ('deterministic','randomized'):
                    ts=outcomes[m][str(c)]['optima_and_controls'][f]['priced_transcript']
                    dm=ts['changed_sibling_previous_Z_physically_copied_and_ignored_or_diagonal_comparator']['go']
                    assert dm['I'] is None or dm['I']<=omit
        data[law]={'underlying_N':phys['laws'][law]['N'],'underlying_W':phys['laws'][law]['W'],
                   'raw_units':'All sibling X weights carry the common 1/2 in the denominator. Integer launch denominators are 2N (retained) and 32N (each of 16 spent-character ports). Among already clean births the denominator is 2W.',
                   'matches_prior':compare,'modes':outcomes,'complement_transport':same,
                   'group_certificate_36_types':compressed_certificate(law,rows)}
    return {'schema_version':1,'local_outcome_order':'Lexicographic focal answers (0 means +), from ZZZ to XXX in binary order, after receiving the flag. The full sibling record is literal eight-bit ordinary string u and sign b in (+,-) order.',
            'physical_input':phys,'laws':data,'table_library':store.rows,'deterministic_focal_bound_on_all_six_sign_lists':grade64(),
            'previous_coordinator_check_stdout':buf.getvalue(),'reserve':'Pool no erasure ports to optimize their announcement. Per-port packets are priced for the same already-chosen mask.'}


def encode(obj):
    return json.dumps(obj,default=str,sort_keys=True,separators=(',',':')).encode()


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def persist(check):
    obj=build()
    data=gzip.compress(encode(obj),compresslevel=9,mtime=0)
    out=HERE/'sibling_change_evidence.json.gz'
    q=HERE/'receipt.json'
    files=[PREV,CHECK,OPT,*[HERE/name for name in ('physical.py','replay.py','sibling_forms.py','preregistration.md')]]
    receipt={'artifact':out.name,'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest(),
             'source_bindings':{str(path.relative_to(ROOT)):digest(path) for path in files},
             'additional_physical_inputs':obj['physical_input']['source_sha256'],
             'public_source_variants':obj['physical_input'].get('public_source_variants',{}),
             'validation':'Literal full-word amplitudes versus independently contracted paid and sibling factors; comparison of 512 retained and all 16 spent-character Grams, all focal setting and answer entries, nine physical placements and both fixed orientations. Scientific referee pending.'}
    raw=(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode()
    if check:
        assert out.read_bytes()==data, 'scientific evidence differs'
        assert q.read_bytes()==raw, 'source or receipt differs'
    else:
        out.write_bytes(data)
        q.write_bytes(raw)
    print('verified' if check else 'wrote',out.name,len(data),receipt['sha256'])
    for law in LAWS:
        for mode in MODES:
            opts=obj['laws'][law]['modes'][mode]['0']['optima_and_controls']
            print(law,mode,*(opts[k]['per_launch_rate'] for k in ('deterministic','randomized')))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true')
    group.add_argument('--check',action='store_true')
    persist(parser.parse_args().check)
