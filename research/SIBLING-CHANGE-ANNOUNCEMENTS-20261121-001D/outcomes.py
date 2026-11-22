"""Complete original-launch census, physical pointer records and conditional focal matrices."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys

from keeper import (ACTIVE, ABC, DEF, OLD, TERNARY, X, at, digits, holdings, initial_old,
                    lawful, legal_roots, local, local_states, ready, receipt)

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EARLIER='NEWBORN-TABLES-AND-THREE-DONOR-RETURNS-20261121-001A'
spec=spec_from_file_location('old_joint_answers',ROOT/'research'/EARLIER/'answers.py')
answers=module_from_spec(spec)
spec.loader.exec_module(answers)


@cache
def extents(law):
    output=[]
    for values in product(local_states(law),repeat=3):
        paid=tuple(s for s,x in values)
        focal=tuple((u,tuple(i for i,row in enumerate(TERNARY) if lawful((u,*row),law)))
                    for u in (0,1) if lawful((u,*paid),law))
        output.append((values,paid,focal))
    return output


def cohort(law):
    correct=7 if law=='nae' else 4
    total=sum(len(row) for ext,paid,focals in extents(law) for c,row in focals)
    assert total==len(legal_roots(law))*correct**4
    return total


@cache
def config_list(law):
    cases=[]
    for m in (*ACTIVE,'none','single_F','single_H0','single_H1'):
        wiring='restricted' if m=='restricted' else 'complete'
        base=[m,law,law,wiring,(),True,True,True]
        cases.append((m,tuple(base)))
        if m not in ACTIVE or m=='passive':continue
        for tag, changes in [
                ('all_F_off',{4:(0,1,2)}),('F1_off',{4:(0,)}),('F2_off',{4:(1,)}),
                ('F3_off',{4:(2,)}),('comparison_off',{5:False}),('H_write_off',{6:False}),
                ('delivery_off',{7:False})]:
            x=base.copy()
            for j,v in changes.items():x[j]=v
            cases.append((f'{m}/{tag}',tuple(x)))
        if m not in ('restricted',):
            for triple in X:
                for n in triple:
                    x=base.copy();x[3]=f'missing{n}'
                    cases.append((f'{m}/missing{n}',tuple(x)))
        if law=='parity' and m in ('asymmetric','symmetric','some_motion','all_motion','restricted'):
            for decoder,code,label in [('nae','nae','literal_NAE'),('parity','nae','old_output_marking'),
                                       ('parity','xor','calibrated_XOR')]:
                x=base.copy();x[1]=decoder;x[2]=code
                cases.append((f'{m}/{label}',tuple(x)))
    # A passive register has no F offers; removing a contact must still forbid
    # the actual full nine-name conjunction.
    for row in X:
        for n in row:
            cases.append((f'passive/missing{n}',('passive',law,law,f'missing{n}',(),True,True,True)))
    return cases


def response(law,cfg,nonfocal):
    mode,dec,code,wire,off,com,write,relay=cfg
    return receipt(mode,law,dec,code,wire,off,com,write,relay,nonfocal)


def matrix(coeff,law,tag='none'):
    """Coefficients multiply the two orientation indicator vectors before normalization."""
    a,b,c=coeff
    v=[tuple(int(lawful((u,*z),law)) for z in TERNARY) for u in (0,1)]
    g=[[a*v[0][i]*v[0][j] + b*(v[0][i]*v[1][j]+v[1][i]*v[0][j]) + c*v[1][i]*v[1][j]
        for j in range(8)] for i in range(8)]
    if tag=='one_focal':
        g=[[n*int(i%2==j%2) for j,n in enumerate(row)] for i,row in enumerate(g)]
    return g


def gap(table, orientation):
    z=7*orientation
    lhs=sum(n for out,n in enumerate(table[7]) if out.bit_count()>=2)
    rhs=table[0][z]
    for mask in (1,2,4):
        rhs+=sum(n for out,n in enumerate(table[mask]) if out&mask and (out&(7^mask))!=(z&(7^mask)))
    return lhs-rhs


@cache
def table(coeff,law,tag='none'):
    g=matrix(coeff,law,tag)
    norm=sum(row[i] for i,row in enumerate(g))
    if not norm:return None
    rows=answers.joint(g)
    full={c:matrix((int(c==0),0,int(c==1)),law) for c in (0,1)}
    equivalent={str(c):all(norm*full[c][i][j]==g[i][j]*sum(full[c][k][k] for k in range(8))
                           for i,j in product(range(8),repeat=2)) for c in (0,1)}
    return {'trace':norm,'gram':g,'eight_settings_eight_outcomes':[[str(z) for z in row] for row in rows],
            'equals_orientation_pure':equivalent,'excess_against_each_c':[str(gap(rows,c)) for c in (0,1)]}


def gram_id(coeff,law,tag,registry):
    from math import gcd
    norm=gcd(*coeff)
    if not norm:return None
    key=(law,tuple(x//norm for x in coeff),tag)
    name=f'{law}/{key[1][0]},{key[1][1]},{key[1][2]}/{tag}'
    if name not in registry:registry[name]=table(key[1],law,tag)
    return name


def compact_record(raw):
    first,delivered,mov,q,dlts,scopes,k1,k2,l,h_reset,status=raw
    return (first,delivered,digits(mov),digits(q),''.join(map(digits,dlts)),'/'.join(scopes),
            digits(k1),digits(k2),digits(l),int(h_reset),'/'.join(status))


def case(law,cfg,registry):
    rows=extents(law)
    count=Counter();correct_by=Counter();by_focal=defaultdict(Counter)
    movement=Counter();cross=Counter();witness={};alphabet={}; codes=[]
    before_char=defaultdict(Counter);logged_char=defaultdict(Counter)
    compare=(*cfg[:4],(0,1,2),*cfg[5:])
    for ix,(ex,paid,fs) in enumerate(rows):
        raw=response(law,cfg,ex)
        native_compare=response(law,compare,ex)
        packed=compact_record(raw)
        if packed not in alphabet:alphabet[packed]=len(alphabet)
        codes.append(alphabet[packed])
        first,out,movers,qs,deltas,scopes,k1,k2,l,hr,st=raw
        ext=tuple(z for _,z in ex)
        for c,allowed in fs:
            mult=len(allowed)
            u=(c,*paid);uindex=int(digits(u),2)
            count[(c,out)]+=mult
            correct_by[c,'ready' if out=='ready' else 'correct' if int(out)==c else 'wrong']+=mult
            for zi in allowed:by_focal[digits(u)+'/'+digits(TERNARY[zi])][out]+=1
            movement[(c,out,sum(n>0 for n in movers),sum(movers))]+=mult
            cross[(c,native_compare[1],out,sum(n>0 for n in movers))]+=mult
            # Old u remains physically present in the retained read. Each allowed focal
            # word contributes the same exterior vector in its orientation sector.
            before_char[out,ext][uindex]+=1
            mode,dec,co,wi,off,com,w,relay=cfg
            logs=tuple(local(i,v,z,mode,law,dec,wi,off,com)[5] for i,(v,z) in enumerate(ex))
            logged_char[out,ext,logs,tuple(qs),tuple(deltas),first][uindex]+=1
            witness.setdefault(f'{c}/{first}/{out}/{sum(n>0 for n in movers)}',
                               {'exterior_index':ix,'u':digits(u),'x_nonfocal':list(map(digits,ext)),
                                'focal_words':list(digits(TERNARY[z]) for z in allowed),
                                'first_full_K':digits(k1),'restored_full_K':digits(k2),'actual_L':digits(l)})
    total=cohort(law)
    assert sum(count.values())==total
    num=7 if law=='nae' else 4
    tables={}
    for out in ('ready','0','1'):
        coeff=(count[0,out]//num,0,count[1,out]//num)
        assert all(v%num==0 for (c,o),v in count.items())
        tables[out]={'ordinary_launch_mass':sum(count[c,out] for c in (0,1)),
                     'no_focal_tag':gram_id(coeff,law,'none',registry),
                     'copied_focal_bit':gram_id(coeff,law,'one_focal',registry),
                     'returned_focal_bit':gram_id(coeff,law,'none',registry)}
    result={'complete_original_launches':total,'by_true_orientation_and_actual_L':
            {f'{c}/{out}':count[c,out] for c,out in product((0,1),('0','1','ready'))},
            'correct_ready_wrong':{f'{c}/{out}':correct_by[c,out] for c,out in product((0,1),('correct','ready','wrong'))},
            'by_orientation_port_number_of_original_siblings_moving_forward_nonidentity_swaps':
                {'/'.join(map(str,k)):v for k,v in sorted(movement.items())},
            'same_word_all_F_off_L_vs_present_L_by_orientation_and_true_moving_siblings':
                {'/'.join(map(str,k)):v for k,v in sorted(cross.items())},
            'actual_source_cells':{key:dict(val) for key,val in sorted(by_focal.items())},
            'retained_tables':tables, 'display_codes':[list(k) for k in alphabet],
            'one_code_per_nonfocal_input':codes, 'examples':witness}
    return result,before_char,logged_char


@cache
def sign_sums(pattern,h):
    summed=[0,0]
    for uidx in pattern:
        summed[uidx>>3]+=(-1)**((uidx&h).bit_count())
    return summed


def after_erasing(law,fragments,registry):
    # Physical old u signs are erased only after the frozen write and cleanup.
    buckets=defaultdict(Counter)
    for k,roots in fragments.items():
        assert all(v==1 for v in roots.values())
        buckets[k[0]][tuple(sorted(roots))]+=1
    out={}
    total=cohort(law); allmass=0
    for h in range(16):
        qs={}
        for k in ('ready','0','1'):
            co=[0,0,0]
            for roots,n in buckets[k].items():
                a,b=sign_sums(roots,h)
                co[0]+=n*a*a;co[1]+=n*a*b;co[2]+=n*b*b
            mat=matrix(co,law)
            trace=sum(row[i] for i,row in enumerate(mat))
            allmass+=trace
            qs[k]={'mass_per_initial_launch':str(F(trace,16*total)),
                   'focal_table':gram_id(tuple(co),law,'none',registry)}
        out[f'{h:04b}']=qs
    assert allmass==16*total
    return out


def readiness(law,wiring):
    hnames=tuple(n for n in holdings(wiring)[5] if 7<=n<16)
    total=cohort(law)
    def ext_type(flat):
        observed=[b for n,b in zip(range(7,16),flat) if n in hnames]
        return 'mixed' if min(observed)!=max(observed) else str(observed[0])
    types=Counter()
    for ex,_,fs in extents(law):
        typ=ext_type([b for _,row in ex for b in row])
        types[typ]+=sum(len(z) for c,z in fs)
    counts={}
    for tag in ('mixed','0','1'):
        n=0
        for abc,df in product(TERNARY,repeat=2):
            for k,s in product((0,1),repeat=2):
                if not lawful((*abc,*df,k),law) or not lawful((*df,s),law):continue
                if law=='parity': h=2**18
                else: h=2**19-int(tag!='mixed' and all(str(b)==tag for b in abc))
                n+=h
        counts[tag]=n
    legal=sum(types[t]*counts[t] for t in types)
    raw=total*2**27
    return {'raw_uniform_source_times_auxiliary':raw,'unrestricted_lawful_launches':legal,
            'lawful_nonready':legal-total,'invalid':raw-legal,'ready_original_launches':total,
            'ready_fraction_of_raw':str(F(total,raw)),'ready_fraction_among_uniform_lawful':str(F(total,legal)),
            'unrestricted_extensions_per_old_word_by_wired_exterior':counts}


def slack_proxies(law):
    from keeper import H_SLACK, Offer, Stage, READY, WRITE, PORT, guard
    out=Counter()
    for ex,paid,fs in extents(law):
        rows=tuple(row for _,row in ex)
        for c,z in fs:
            src=initial_old((c,*paid),(TERNARY[z[0]],*rows))
            word=ready(src,law,'complete'); h=(word>>H_SLACK)&1
            for mode in ('read_complemented_H_slack','attempt_read_u0_at_H','independent_external_q'):
                event=Stage(word,'complete')
                for answer,bit in ((0,1),(1,0)):
                    marks=(17,18) if answer==0 else (16,18)
                    if mode=='independent_external_q':
                        # Price the loading operation: start from an externally
                        # populated physical complementary Q1, never use it in primary.
                        qbit=30
                        if c:event.word|=1<<qbit;event.word&=~(1<<(qbit-1))
                        guards=((qbit,answer),)
                    else:guards=((H_SLACK,bit),) if mode=='read_complemented_H_slack' else ((0,answer),)
                    event.offer(Offer(5,marks,guards))
                dst=PORT[at(event.word,ABC)]
                out[mode,c,h,dst]+=len(z)
    return {'/'.join(map(str,k)):v for k,v in sorted(out.items())}


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--verify',action='store_true');ap.add_argument('--output',type=Path,default=HERE/'signal_records.json.gz')
    args=ap.parse_args()
    registry={}; out={'schema':1,'settings_order':'three focal places Z=0, X=1; binary lexical settings and outcomes',
        'packed_physical_fields':['first_K_code','delivered_L_code','forward_nonidentity_counts_F1_F2_F3',
            'three actual local messages (Q; the restricted comparator reads T0 directly)','six_delta_bits','five-status-presence flags [changed,equal,refused,disconnected,unsupported] for each F',
            'first_whole_K','final_whole_K','final_whole_L','ABC_returned_to_ready','H_write_offer'],
        'after_each_success':'Original nonfocal values and T,Q restored except where a sole literal F motion is intentionally left; both reads of L and inverse reset-and-redelivery are checked.',
        'fixed_ready_holds':holdings('complete'),'sources':{},'tables':registry}
    for law in ('nae','parity'):
        info={'original_launches':cohort(law),'ready_costs':{},'cases':{},'characters_after_writing':{},
              'per_input_index':[[list((u,digits(z))) for u,z in ex] for ex,p,f in extents(law)],
              'slack_and_external_control':slack_proxies(law)}
        for w in ('complete','restricted',*(f'missing{n}' for row in X for n in row)):
            info['ready_costs'][w]=readiness(law,w)
        for label,cfg in config_list(law):
            case_result,clean,logged=case(law,cfg,registry)
            info['cases'][label]=case_result
            if label in ACTIVE or label.endswith('all_F_off') or label.endswith('calibrated_XOR') or label=='none':
                info['characters_after_writing'][label]={
                    'cleaned_no_additional_path_copy':after_erasing(law,clean,registry),
                    'actual_F_offer_log_Q_and_T_retained':after_erasing(law,logged,registry)}
        out['sources'][law]=info
    raw=json.dumps(out,separators=(',',':'),default=str).encode()
    if args.verify:assert gzip.decompress(args.output.read_bytes())==raw
    else:args.output.write_bytes(gzip.compress(raw,compresslevel=6,mtime=0))
    print(('verified' if args.verify else 'wrote'),len(raw),sha256(raw).hexdigest())


if __name__=='__main__':main()
