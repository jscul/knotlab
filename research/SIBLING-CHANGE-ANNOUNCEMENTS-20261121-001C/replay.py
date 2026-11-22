"""Replay the one-way single-launch message calculation on the immutable B301 source."""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
from messages import (BASE, HERE, H, K, MODES, PAIRS, add, check_source, complement_mask, coordinate_subset,
                      display, mask_at_h, multiply, named_packets, one_collision, pack_mask, packet, pool, price,
                      rates, score, selected_packet, select_row, signed_table, sum_forms, unpack_mask)

ROOT=HERE.parents[1]
FREEZE='0dfeb24dc28fbf14ec8a6bfcfaa42b04f00b3ae6170dad4c1644c175e3c80c09'
B_OBS='bc93791c55734fe2a9f305cb77806b9eadb0653426ea2ea86e6b9129c8b90ae4'
B_RECEIPT='c42a8bfde0d55be3a0ce468d22097490507732d09ea5643305f7fe53fa1779db'
IDENTITY=tuple(H)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def json_bytes(x):
    def exact(v):
        if not isinstance(v,F):raise TypeError(type(v).__name__)
        return str(v)
    return json.dumps(x,default=exact,sort_keys=True,separators=(',',':')).encode()


def check_transported_charge(law,src,c0,den):
    """Complement only Z outputs, retaining the signed h and b records and their physical mass."""
    mask=complement_mask(c0['mask'])
    g=sum_forms(multiply(p,src[key]) for key,p in mask.items()); w,d=score(law,g,1)
    assert c0['weight']==w and c0['scaled_surplus']==d
    return {'go':packet(law,g,den,1),'transported_mask':'at the same message replace k by k xor 510; every missing entry is zero'}


def optimal_policy(law,cube,code,den,c):
    src=pool(cube,code); policies=price(law,src,c)
    return src,policies


def analyze_pairs(law,cube,den,mu):
    a,b=mu.numerator,mu.denominator
    single=[[b*w+a*d for g in row for w,d in [score(law,g,0)]] for row in cube]
    identity_dual=sum(max(v,0) for row in single for v in row)
    out=[]
    for pair in PAIRS:
        h,j=pair;code=one_collision(pair); src,rules=optimal_policy(law,cube,code,den,0)
        conflicts=[]
        for k,(v,t) in enumerate(zip(single[h],single[j],strict=True)):
            lost=max(0,v)+max(0,t)-max(0,v+t)
            if lost:
                assert v*t<0 and lost==min(abs(v),abs(t))
                conflicts.append([k,v,t,lost])
        gap=sum(z[3] for z in conflicts);upper=F(identity_dual-gap,b)
        assert upper==sum(max(F(0),w+mu*d) for g in src.values() for w,d in [score(law,g,0)])
        row={'collided_h':pair,'codeword_for_each_h':code,'nominal_visible_records':len(src),
             'nonzero_visible_records':sum(score(law,g,0)[0]>0 for g in src.values()),
             'common_multiplier':mu,'strict_conflict_list_k_two_scaled_line_values_and_loss':conflicts,
             'total_scaled_dual_collision_loss':gap,'common_dual_raw_upper':upper,'classes':{}}
        for mode,rule in rules.items():
            mark=selected_packet(law,src,rule,0,den)
            transported=check_transported_charge(law,src,rule,den)
            assert rule['weight']<=upper
            row['classes'][mode]={'c0':mark,'c1':transported}
        out.append(row)
    return out,F(identity_dual,b)


def charged_outputs(law,cube,code,den,c,policies):
    charged={}
    for method in MODES:
        policy=policies[method];mask=policy['mask']
        qq=named_packets(law,cube,code,mask,c,den)
        assert qq['go']['raw_weight']==policy['weight']
        bits=max(code).bit_length()
        bank_weights={3:0,5:0}
        null_rows=0
        for h in H:
            frame=tuple(5 if code[h]&(1<<i) else 3 for i in range(bits-1,-1,-1))
            incoming=sum((v==5)<<(bits-i-1) for i,v in enumerate(frame))
            for k,g in enumerate(cube[h]):
                trace=score(law,g,c)[0]; prob=mask.get(512*incoming+k,0)
                null_rows+=not trace
                for target,branch in ((5,prob),(3,1-prob)):
                    written=6^(6^target)
                    assert (6^target).bit_count()==2 and written==target
                    bank_weights[written]+=trace*branch
        assert bank_weights[5]==qq['go']['raw_weight'] and bank_weights[3]==qq['decline']['raw_weight']
        qq['physically_decoded_announcement_raw_traces']={'101_go':bank_weights[5],'011_decline':bank_weights[3],
                    'zero_full_record_rows':null_rows,'no_fresh_public_write_if_disconnected_or_missing_input':True}
        qq['used_decoder_mask']=pack_mask(mask,(max(code)+1)*512)
        qq['private_boundary']=[{'message':x//512,'sibling_k':x%512,'p':p} for x,p in mask.items() if p!=1]
        charged[method]=qq
    return charged


def isolate_boundary(law,cube,code,policy,den,c):
    mask=policy['mask'];partial=[(x,p) for x,p in mask.items() if p!=1]
    if not partial:return None
    assert len(partial)==1
    key,f=partial[0];m,k=divmod(key,512)
    branches=[]
    for value in (0,1):
        fixed=dict(mask);fixed[key]=value
        data=named_packets(law,cube,code,fixed,c,den)
        branches.append({'probability':(1-f,f)[value], 'go':data['go'],'decline':data['decline'],
                         'wrote_at_boundary':bool(value)})
    g=sum_forms(multiply(branch['probability'],branch['go']['p_t_q']) for branch in branches)
    assert score(law,g,c)==(policy['weight'],policy['scaled_surplus'])
    assert branches[0]['go']['scaled_surplus']>0>branches[1]['go']['scaled_surplus']
    # A sender's private bit can be made available to the receiver with a new symbol, but only at the boundary h.
    sources=[h for h in H if code[h]==m]
    assert len(sources)==1
    h0=sources[0];new=max(code)+1
    states=[]
    for h in H:
        states.append([(code[h],1-f),(new,f)] if h==h0 else [(code[h],F(1))])
    def decode(message,kk):
        if message==new:
            return 1 if kk==k else mask.get(512*m+kk,0)
        if message==m and kk==k:return 0
        return mask.get(512*message+kk,0)
    assert all(decode(m0,kk) in (0,1) for m0 in range(new+1) for kk in K)
    for h in H:
        assert sum(z[1] for z in states[h])==1
        for kk in K:
            assert sum(p*decode(symbol,kk) for symbol,p in states[h])==mask.get(512*code[h]+kk,0)
    paid_weight=sum(score(law,g,c)[0] for g in cube[h0])
    record_weight=score(law,cube[h0][k],c)[0]
    n=f.denominator;bits_draw=(n-1).bit_length();expected_bits=F(bits_draw*2**bits_draw,n)
    # Verify every symbol, including the seventeenth whose complete display is four ready-to-zero writes and one one.
    bits=new.bit_length(); frames=[[(5 if label&(1<<pos) else 3) for pos in range(bits-1,-1,-1)] for label in range(new+1)]
    assert len({tuple(row) for row in frames})==len(frames)
    for label,row in enumerate(frames):
        written=[6 ^ (6 ^ value) for value in row]
        assert all(value in (3,5) and (6^value).bit_count()==2 for value in written)
        assert sum((value==5) << (bits-i-1) for i,value in enumerate(written))==label
    return {'boundary_h':h0,'boundary_k':k,'p':f,'fixed_deterministic_decoder_branches':branches,
            'sender_only_split_code':{'reachable_symbols':len(frames),'symbol_frame_in_label_order':frames,
                    'fixed_width':bits,'h_conditional_symbol_distributions':states,
                    'per_original_probability_of_drawing_eraser_coin':F(paid_weight,den),
                    'per_original_probability_of_decoder_boundary':F(record_weight,den),
                    'extra_message_probability_per_original':f*paid_weight/den,
                    'fair_bits_per_exact_coin_draw':expected_bits,'bits_per_original_at_sender':expected_bits*paid_weight/den,
                    'bits_per_original_at_decoder_if_drawn_at_its_exact_boundary':expected_bits*record_weight/den,
                    'readback_at_writer':'Each original message uses its earlier lookup except that the previous fractional row declines. The extra message uses the split row and accepts only at its boundary where the previous row declines; it matches all its other earlier decisions.',
                    'tested_mask_rows':8192,'per_original_go':F(policy['weight'],den)},
            'ordinary_scratch_bank_projection_source':'Each separate ternary was tested under the applicable law in physical_displays. Every displayed output uses 101 or 011 from 110.',
            'integer_input_and_clean_numeraire':'Both branches are evaluated on all initial launches at the one common denominator.'}


def prior_subset_controls(law,cube,den,previous):
    out={}
    for J in H:
        code=coordinate_subset(J);src,rules=optimal_policy(law,cube,code,den,0)
        row={}
        for mode,policy in rules.items():
            expected=previous['laws'][law]['views']['mixed']['0']['subset_results'][f'{J:04b}']['priced'][mode]
            assert policy['weight']==F(expected['weight'])
            check_transported_charge(law,src,policy,den)
            row[mode]=F(policy['weight'],den)
        out[f'{J:04b}']={'h_message':code,'rates':row}
    return out


def evaluate(law,previous):
    cube,den,transports=check_source(law,previous)
    src,full=optimal_policy(law,cube,IDENTITY,den,0)
    full_raw={mode:rule['weight'] for mode,rule in full.items()}
    mu=(full['randomized']['certificate']['mu_for_28_times_surplus'] if full_raw['randomized'] else F(1))
    pairs,dual_identity=analyze_pairs(law,cube,den,mu)
    assert dual_identity==full_raw['randomized']
    best={}; winners={}
    for mode in MODES:
        vals=[F(row['classes'][mode]['c0']['go']['raw_weight']) for row in pairs]
        best[mode]=max(vals);winners[mode]=[row['collided_h'] for row,x in zip(pairs,vals,strict=True) if x==best[mode]]
    uniform=max(row['common_dual_raw_upper'] for row in pairs)
    assert uniform==best['randomized']
    charged={}; shared={};physical={}
    if full_raw['randomized']:
        assert all(x<min(full_raw.values()) for x in (uniform,*best.values()))
        assert winners['deterministic']==winners['randomized'] and len(winners['randomized'])==1
        witness=winners['randomized'][0]; code=one_collision(witness)
        assert [p['collided_h'] for p in pairs if p['common_dual_raw_upper']==uniform]==[witness]
        other=max(p['common_dual_raw_upper'] for p in pairs if p['collided_h']!=witness)
        assert other<best['deterministic']
        info={'all_proper_raw_convexified_upper_and_achieved':uniform,'raw_upper_if_excluding_unique_closest_pair':other,
              'all_proper_minus_full_seedless_original_rate':F(uniform-full_raw['deterministic'],den),
              'least_messages_primary':{'seedless_fixed':16,'decoder_randomized_fixed_encoder':16},
              'least_messages_two_numerical_targets_seedless_then_randomized':{
                 'deterministic_sender_and_decoder':[16,'impossible for any alphabet on this one-shot deterministic support'],
                 'deterministic_sender_and_decoder_private_seed':[16,16],
                 'jointly_shared_independent_seed':[16,16],
                 'eraser_only_private_seed_with_seedless_writer':[16,17]},
              'proper_encoder_only_seed_strict_upper':uniform,
              'proper_encoder_only_seed_constructive_lower':best['deterministic'],
              'basis_of_strictness':'Every deterministic lookup in an equality-compatible channel must induce the same unique 15-class partition up to naming. Independently pre-sampling possible messages per h then forces disjoint singleton outputs for those 15 classes. Any seedless decoder has integer raw weight.'}
        chosen={'identity':IDENTITY,'best_proper':code}
    else:
        assert all(x==0 for x in (*best.values(),*full_raw.values()))
        chosen={'identity':IDENTITY,'constant':(0,)*16};info={'all_proper_raw_convexified_upper_and_achieved':0,
                    'least_messages_all_classes_and_both_numerical_targets':1,'fixed_width':0,'positive_accepted_ensemble':False}
    for label,code in chosen.items():
        physical[label]=display(law,code)
        for c in (0,1):
            x,rr=optimal_policy(law,cube,code,den,c)
            mark=charged_outputs(law,cube,code,den,c,rr)
            assert all(mark[mode]['go']['raw_weight']==(full_raw[mode] if label=='identity' else best[mode]) for mode in MODES)
            charged[label+str(c)]=mark
            shared[label+str(c)]=isolate_boundary(law,cube,code,rr['randomized'],den,c)
    controls=prior_subset_controls(law,cube,den,previous)
    feedback={}
    for c in (0,1):
        _,pol=optimal_policy(law,cube,IDENTITY,den,c)
        for mode in MODES:
            transmitted=pol[mode]['mask']
            # If k is sent back, the sender itself can apply its complete (h,k) rule and send a binary flag.
            g=sum_forms(select_row(cube[h],{k:transmitted[512*h+k] for k in K if 512*h+k in transmitted}) for h in H)
            assert score(law,g,c)==(pol[mode]['weight'],pol[mode]['scaled_surplus'])
            feedback[f'{c}.{mode}']={'go':packet(law,g,den,c,True),'reverse_message':'k as nine bits; sender then computes go including independent random bit if required','two_possible_new_forward_symbols':True}
    return {'original_denominator':den,'full_raw_targets':full_raw,'full_go_rates':{m:F(w,den) for m,w in full_raw.items()},
            'smallest_proper_raw_certified_loss':{m:full_raw[m]-best[m] for m in MODES},
            'proper_best_raw':best,'proper_best_go_rates':{m:F(w,den) for m,w in best.items()},'proper_winning_pairs':winners,
            'proper_uniform_dual':mu,'uniform_dual_complete_raw_upper':dual_identity,
            'all_single_pair_tests_at_c0_and_transported_c1':pairs,'shared_or_noisy':info,
            'fully_priced_winners_c0_c1':charged,'shared_mixture_and_noisy_sender_constructions':shared,
            'charged_original_physical_displays':physical,'conditional_feedback_changed_resource':feedback,
            'coordinate_and_no_message_controls':controls,'address_transports':transports,
            'null_convention':'Unlisted mask cells are zero. The full predecessor retains every h,k including nulls. Conditional tables are undefined only when the corresponding selected trace vanishes.'}


def previous_suite():
    artifact=BASE/'all_erasure_evidence.json.gz';receipt=BASE/'receipt.json'
    assert digest(artifact)==B_OBS and digest(receipt)==B_RECEIPT
    assert digest(HERE/'preregistration.md')==FREEZE and (HERE/'preregistration.md').read_bytes()==(HERE/'design_candidate_1.md').read_bytes()
    return json.loads(gzip.decompress(artifact.read_bytes()))


def reconcile(primary, independent):
    for law,old in independent['laws'].items():
        new=primary[law]
        assert new['original_denominator']==old['launch_denominator']
        assert new['shared_or_noisy']['all_proper_raw_convexified_upper_and_achieved']==F(old['uniform_dual']['maximum_pair_bound_raw_weight'])
        for row in new['all_single_pair_tests_at_c0_and_transported_c1']:
            p,q=row['collided_h']; literal=old['pair_prices'][f'{p:04b}/{q:04b}']
            for mode in MODES:
                want=F(literal['prices'][mode]['raw_weight']); data=row['classes'][mode]
                assert data['c0']['go']['raw_weight']==data['c1']['go']['raw_weight']==want
            if law=='nae':
                assert row['common_dual_raw_upper']==F(literal['fractional_full_dual_upper'])
                assert len(row['strict_conflict_list_k_two_scaled_line_values_and_loss'])==literal['strict_opposite_dual_record_count']
        for mode in MODES:
            assert new['proper_best_raw'][mode]==F(old['best_proper'][mode]['best_proper_weight'])
            assert list(map(tuple,old['best_proper'][mode]['maximizing_pairs']))==new['proper_winning_pairs'][mode]
    return {'pair_law_decoder_prices_before_transport':480,'actual_orientation_comparisons':960,
            'all_canonical_signed_grams':16384,'signed_physical_addresses_tested_per_law':9}


def main():
    import audit
    parser=argparse.ArgumentParser(description=__doc__); action=parser.add_mutually_exclusive_group(required=True)
    action.add_argument('--check',action='store_true');action.add_argument('--write',action='store_true');opt=parser.parse_args()
    old=previous_suite();primary={law:evaluate(law,old) for law in ('nae','parity')};ind=audit.run()
    checks=reconcile(primary,ind)
    data={'laws':primary,'independent_literal_check':ind,'verified':checks,
          'source':'Same five paid holdings and same positive coherent complete-word support as the previous all-erasure record. Source receipt in this directory.',
          'units':'Go original rate W/L, charge D=28WI-W. Dividing a raw signed outcome cell by L gives its original probability at that setting. Divide by 8L to include the equally likely settings.',
          'individual_merger_reconstruction':'Read its contiguous 16-entry code and packed little-endian sure-go mask or exact partial entries; each true pair (h,k) is charged at the immutable physical B record even when h is hidden. All unlisted mask entries are zero, opposite c complements only ordinary k bits. Partial multiway search was unnecessary because of the actual strict one-collision upper.'}
    blob=bytearray(gzip.compress(json_bytes(data),compresslevel=9,mtime=0));blob[9]=255;blob=bytes(blob)
    path=HERE/'erasure_message_evidence.json.gz'; receipt=HERE/'receipt.json'
    sources=dict(ind['source_sha256'])
    for name in ('preregistration.md','design_candidate_1.md','design_reviews.json','replay.py','messages.py','audit.py'):
        q=HERE/name;k=str(q.relative_to(ROOT));assert sources.setdefault(k,digest(q))==digest(q)
    tag={'artifact':path.name,'sha256':hashlib.sha256(blob).hexdigest(),'bytes':len(blob),
         'source_bindings':sources,'public_source_variants':ind['public_source_variants'],'checks':checks,
         'source_contribution':0,'runtime':'Python standard library; unnetworked exact integer and rational replay, canonical gzip clock and OS byte.',
         'prospective_design_sha256':FREEZE,'scientific_referee':'pending'}
    js=(json.dumps(tag,sort_keys=True,indent=2)+'\n').encode()
    if opt.write:path.write_bytes(blob);receipt.write_bytes(js)
    else:
        assert path.read_bytes()==blob,'evidence differs'
        assert receipt.read_bytes()==js,'receipt differs'
    print(f"{path.name} {len(blob)} bytes {tag['sha256']}; receipt {hashlib.sha256(js).hexdigest()}")

if __name__=='__main__':main()
