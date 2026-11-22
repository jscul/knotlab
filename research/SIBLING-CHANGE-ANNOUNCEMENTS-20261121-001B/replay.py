"""All spent signs at the same preassigned sibling reading. Every true and hidden record is priced per original launch."""
import argparse
from collections import Counter
from fractions import Fraction as F
import gzip
import hashlib
import json
from pathlib import Path
from itertools import product
from signed_counts import ZERO, ROOT, allowed_old, chars, build_records, score, matrix, signed_table, add, multiply, sum_forms, keys_for, select
from select_flags import rates

HERE=Path(__file__).resolve().parent
AREC=HERE.with_name(HERE.name[:-1]+'A')
PARENT=HERE.with_name(HERE.name[:-1])
PRE=ROOT/'research/SIBLING-ANNOUNCEMENTS-AND-RECEIVER-BIRTHS-20261121-001A'
LAWS=('nae','parity')
VIEWS=('mixed','nine_z')
METHODS=('deterministic','randomized')
HS=tuple(range(16))
KS=tuple(range(512))
DIGITS=tuple(product((0,1),repeat=3))


def packet(law,g,den,c,full=False):
    w,d=score(law,g,c)
    v=F(d+w,28)
    obj={'coefficients_p_t_q':g,'w':w,'wI':v,'28d':d,'mass':w/F(den),'I':v/w if w else None,
         'passes_1_over_28':bool(w and d>=0),'original_denominator':den,'joint_setting_and_answer_denominator':8*den}
    if full:
        r=signed_table(law,g); assert all(sum(line)==w for line in r)
        assert min(z for line in r for z in line)>=0
        for j in (0,1):
            raw=(sum(r[7][a] for a in range(8) if a.bit_count()>=2)-r[0][7*j]
                 -sum(r[s][a] for s in (1,2,4) for a in range(8) if a&s and (a&(7^s))!=((7*j)&(7^s))))
            assert 28*raw-w==score(law,g,j)[1]
        obj.update(raw_gram=matrix(law,g),conditional_8_by_8=tuple(tuple(z/w for z in line) for line in r) if w else None)
    return obj


def subtract(x,y):
    return tuple(a-b for a,b in zip(x,y,strict=True))


def selected(block,indices):
    count=Counter()
    for k,a in indices.items():
        if a:count[block[k]]+=a
    return sum_forms(multiply(n,g) for g,n in count.items())


def split_rows(mask):
    by=[{} for _ in HS]
    for key,p in mask.items():by[key//512][key%512]=p
    return by


def port_packets(law,cube,selected_by_h,den,c,full=False):
    ports=[]
    for h in HS:
        whole=sum_forms(cube[h]); keep=selected(cube[h],selected_by_h[h]);lost=subtract(whole,keep)
        ports.append({'h':f'{h:04b}','go':packet(law,keep,den,c),'decline':packet(law,lost,den,c),
                      'whole_port':packet(law,whole,den,c)})
    yes=sum_forms(port['go']['coefficients_p_t_q'] for port in ports)
    no=sum_forms(port['decline']['coefficients_p_t_q'] for port in ports)
    result={'go':packet(law,yes,den,c,full),'decline':packet(law,no,den,c,full),'ports':ports}
    assert result['go']['mass']+result['decline']['mass']==1
    return result


def dummy_cube(law,cube):
    summed=[sum_forms([cube[h][k] for h in HS]) for k in KS]
    out=[]
    for h in HS:
        line=[]
        for k,whole in enumerate(summed):
            w=score(law,whole,0)[0]
            v=score(law,cube[h][k],0)[0]
            g=multiply(F(v,w),whole) if w else ZERO
            assert score(law,g,0)[0]==v
            line.append(g)
        out.append(line)
    return out


def tagged_cube(cube):
    one=[tuple(v//16 for v in sum_forms([cube[h][k] for h in HS])) for k in KS]
    assert all(multiply(16,one[k])==sum_forms([cube[h][k] for h in HS]) for k in KS)
    return (one,)*16


def struck_Z_cube(ordinary):
    return tuple(tuple(add(ordinary[h][k&~1],ordinary[h][k|1]) for k in KS) for h in HS)


def encode_selection(d):
    # Sorted real labels and exact fractional mask. Original subset labels have zeros in hidden h coordinates.
    answer={key:v for key,v in d.items() if key!='mask'}
    answer['sure_labels']=[i for i,p in d['mask'].items() if p==1]
    answer['partial_labels']={str(i):p for i,p in d['mask'].items() if p!=1}
    return answer


def price(d,den):
    return d['weight']/F(den)


def basis_subsets(law,basis,cube,den,c):
    family={}; study={}
    for J in HS:
        src=keys_for(cube,J)
        weights={i:score(law,g,c) for i,g in src.items()}
        m={}
        results={}
        for method in METHODS:
            rule=rates(weights,method)
            yes=select(src,rule['mask']); whole=sum_forms(src.values())
            assert score(law,yes,c)==(rule['weight'],rule['scaled_surplus'])
            packed=encode_selection(rule); packed.update(launch_acceptance=price(rule,den),
                     go=packet(law,yes,den,c,J==15),decline=packet(law,subtract(whole,yes),den,c,J==15))
            m[method]=packed
            if J in (0,15):results[method]=rule
        family[f'{J:04b}']={'shown_physical_paid_names':[i for i in range(4) if J&(8>>i)],
                            'physical_record_count':len(src),'nonzero_records':sum(w>0 for w,d in weights.values()),
                            'priced':m}
        if J in (0,15):study[J]=results
    minimal={}
    for method in METHODS:
        r={J:F(family[f'{J:04b}']['priced'][method]['launch_acceptance']) for J in HS}
        assert all(r[a]<=r[b] for a in HS for b in HS if a&b==a)
        hit=[a for a in HS if r[a]==r[15]]
        minimal[method]={'matching_subsets':[f'{a:04b}' for a in hit],
                         'inclusion_minimal':[f'{a:04b}' for a in hit if not any(b!=a and b&a==b for b in hit)],
                         'smallest_size':min(a.bit_count() for a in hit)}
    return family,study,minimal


def independent_per_h(law,cube,den,c,method):
    parts={};mask={}
    for h in HS:
        w={512*h+k:score(law,g,c) for k,g in enumerate(cube[h])}
        rule=rates(w,method);mask.update(rule['mask'])
        parts[f'{h:04b}']={'per_original':price(rule,den),'rule':encode_selection(rule)}
    tally=port_packets(law,cube,split_rows(mask),den,c,True)
    assert sum(x['per_original'] for x in parts.values())==tally['go']['mass']
    assert all(p['go']['w']==0 or p['go']['passes_1_over_28'] for p in tally['ports'])
    return {'go':tally['go'],'decline':tally['decline'],'per_h':parts}


def charged_coin(law,cube,den,mask):
    out=[]
    for key,p in mask.items():
        if p==1:continue
        h,k=divmod(key,512);n=p.denominator;bits=(n-1).bit_length()
        w=score(law,cube[h][k],0)[0]
        exp=F(bits*2**bits,n)
        out.append({'h':f'{h:04b}','k':k,'conditional_coin':p,'record_original_probability':F(w,den),
                    'independent_fair_bits_per_draw_block':bits,
                    'sample_uniform_integer_below':n,'accept_if_below':p.numerator,
                    'expected_bits_at_this_record':exp,'expected_bits_per_original_launch':exp*w/den})
    return out


def fixed_effects(law,basis,cubes,normalizers,controls,rule,c,hid):
    cube=cubes[basis]; den=normalizers[basis]
    mask=split_rows(rule['mask']);t=port_packets(law,cube,mask,den,c,True)
    dummy=port_packets(law,controls[basis]['dummy'],mask,den,c,True)
    tagged=port_packets(law,controls[basis]['tagged'],mask,den,c,True)
    z=port_packets(law,controls[basis]['struck_Z'],mask,den,c,True) if basis=='mixed' else t
    assert all(x[code]['mass']==y[code]['mass'] for code in ('go','decline','whole_port') for x,y in zip(t['ports'],dummy['ports'],strict=True))
    assert all(p['whole_port']['mass']==F(1,16) for p in tagged['ports'])
    D=controls[basis]['tagged'][0]
    eff=tuple(sum(x.get(k,0) for x in mask)/F(16) for k in KS)
    checkg=selected(D,{k:a for k,a in enumerate(eff) if a})
    assert multiply(16,checkg)==tagged['go']['coefficients_p_t_q']
    # Genuine conditional dummy labels have the actual frequencies. All h-dependence reduces
    # to a k-conditional coin since every dummy branch has the same conditional focal state.
    reff=[]
    for k in KS:
        ws=[score(law,cube[h][k],c)[0] for h in HS]
        total=sum(ws)
        reff.append(sum(mask[h].get(k,0)*w for h,w in enumerate(ws))/F(total) if total else F(0))
    hider=keys_for(cube,0)
    assert select(hider,{i:x for i,x in enumerate(reff) if x})==dummy['go']['coefficients_p_t_q']
    if rule['weight']>hid['weight']:
        assert not dummy['go']['passes_1_over_28']
    if basis=='mixed':
        equal=[{k:(m.get(k&~1,0)+m.get(k|1,0))/F(2) for k in KS if m.get(k&~1,0) or m.get(k|1,0)} for m in mask]
        ordinary=port_packets(law,cubes['nine_z'],equal,normalizers['nine_z'],c)
        assert z['go']['mass']==ordinary['go']['mass'] and z['go']['I']==ordinary['go']['I']
        assert z['go']['coefficients_p_t_q']==multiply(2,ordinary['go']['coefficients_p_t_q'])
    return {'actual':t,'replacement_h_independent_of_focal_state_at_fixed_k':dummy,
            'four_spent_values_physically_tagged_before_read':tagged,'prior_changing_sibling_Z_tag':z,
            'coherently_returned_tag_before_its_read':'All original conditional matrices and masses equal the actual packets of this same mask.',
            'dummy_label_effective_hidden_h_k_mask':reff,'uniform_spent_tag_effective_hidden_h_k_mask':eff,
            'needed_coin_for_primary':charged_coin(law,cube,den,rule['mask']),
            'sibling_Z_tag_nine_Z_view':'Identity when all nine physical questions were ordinary.',
            'pass_versus_criterion_at_same_numeric_mask':{label:pack['go']['passes_1_over_28'] for label,pack in zip(('true_h','dummy_h','spent_copy','changing_sibling_copy'),(t,dummy,tagged,z),strict=True)}}


def eight_known(cube,den,law,c):
    ids=(0,7) if c==0 else (510,505)
    selected0=[{i:1 for i in ids} for h in HS]
    x=port_packets(law,cube,selected0,den,c)
    ports=[h for h,row in enumerate(x['ports']) if row['go']['passes_1_over_28']]
    chosen=[p if h in ports else {} for h,p in enumerate(selected0)]
    final=port_packets(law,cube,chosen,den,c)
    if law=='nae':
        assert len(ports)==8 and final['go']['mass']==F(11,19208)
        assert ports==[h for h in HS if not h&1]
    return {'source':'Preceding deterministic two-sibling-record example at fixed orientation. Subset chosen from per-port threshold on that known mask.',
            'two_records_on_all_ports':x,'qualifying_true_h':ports,'earlier_lower_bound':final}


def basis_tests(law,basis,cubes,normalizers,controls,c):
    cube=cubes[basis];den=normalizers[basis]
    fam,e,r=basis_subsets(law,basis,cube,den,c)
    st={}
    for method in METHODS:
        strict=independent_per_h(law,cube,den,c,method)
        m=e[15][method]
        assert strict['go']['mass']<=price(m,den)
        st[method]={'stricter_each_h_must_meet_target':strict,
                    'primary_fixed_effects':fixed_effects(law,basis,cubes,normalizers,controls,m,c,e[0]['randomized'])}
    hidden=keys_for(cube,0)
    tw=rates({k:score(law,g,c) for k,g in hidden.items()},'randomized')
    # Retaining an actual s tag supplies 16 uniform subdivisions of each hidden k to a deterministic decoder.
    tagged_det=rates({512*h+k:score(law,controls[basis]['tagged'][h][k],c) for h in HS for k in KS},'deterministic')
    tagged_frac=rates({512*h+k:score(law,controls[basis]['tagged'][h][k],c) for h in HS for k in KS},'randomized')
    assert price(tagged_frac,den)==price(tw,den)
    all_inputs=sum_forms(sum_forms(row) for row in cube)
    zero=packet(law,ZERO,den,c,True)
    all_packet=packet(law,all_inputs,den,c,True)
    assert all_packet['mass']==1 and not all_packet['passes_1_over_28']
    correlated=port_packets(law,cube,[dict.fromkeys(KS,1) if not h&1 else {} for h in HS],den,c,True)
    return {'subset_results':fam,'minimal_subsets':r,'full_observer':st,
            'constant_go':{'go':all_packet,'decline':zero},'constant_decline':{'go':zero,'decline':all_packet},
            'h3_reused_as_if_private_coin':{'physical_source':'Use the paying name 3 true sign as the putative coin and announce its plus. This is a deterministic function of the existing h, correlates with the displayed record and supplies no fresh private randomness.',
                                            'actual_packets':correlated},
            'matched_dummy_randomized_optimum_by_hidden_flag_equivalence':price(tw,den),
            'uniform_spent_tag_calibration_with_new_best_mask':{'deterministic':price(tagged_det,den),'randomized':price(tagged_frac,den),
                  'deterministic_rule':encode_selection(tagged_det),'randomized_rule':encode_selection(tagged_frac)}}


def rational(value):
    if isinstance(value, F):
        return str(value)
    raise TypeError(type(value).__name__)


def canonical(obj):
    return json.dumps(obj, sort_keys=True, separators=(',', ':'), default=rational).encode()


def parity_common(g):
    """A six-sign joint law for any positive pair of even/odd amplitude templates."""
    w,_=score('parity',g,0)
    if not w:
        return None
    G=matrix('parity',g)
    outcomes=signed_table('parity',g)
    result=[G[z][z]*outcomes[7][x]/F(w*w) for z in range(8) for x in range(8)]
    assert min(result)>=0 and sum(result)==1
    for s,row in enumerate(outcomes):
        for ans,v in enumerate(row):
            assert sum(result[8*z+x] for z in range(8) for x in range(8) if (z&(7^s)|x&s)==ans)==v/w
    return result


def verify_basis(law,cube,basis,physical,all_tables):
    den=physical['launch_denominator']
    d={}
    for h in HS:
        for k,g in enumerate(cube[h]):
            idx=physical['gram_ids'][h][k]
            assert d.setdefault(g,idx)==idx
            gg=cube[h][k^(510 if basis=='mixed' else 511)]
            assert gg==(g[2],g[1],g[0])
    for g,idx in d.items():
        assert matrix(law,g)==tuple(map(tuple,all_tables['gram_library'][idx]))
        grad=all_tables['grade_library'][idx]
        w=grad['weight']
        for c in (0,1):
            assert score(law,g,c)==(w,28*F(grad['wI'+str(c)])-w)
        tab=signed_table(law,g)
        assert all(sum(row)==w for row in tab)
        predicted=[[str(v/w) for v in row] for row in tab] if w else None
        assert predicted==all_tables['probability_library'][idx]
    counts=Counter(g for row in cube for g in row)
    assert sum(n*score(law,g,0)[0] for g,n in counts.items())==den
    return {'types': [{'p_t_q':g,'gram_library_id':idx,'multiplicity':counts[g],
              'c0_trace_28_surplus':score(law,g,0), 'c1_trace_28_surplus':score(law,g,1),
              'common_Z_then_X_word_probabilities':parity_common(g) if law=='parity' else None}
              for g,idx in sorted(d.items())], 'separate_record_checks':sum(counts.values()),
            'null_and_defined': [sum(n for g,n in counts.items() if score(law,g,0)[0]==0),
                                 sum(n for g,n in counts.items() if score(law,g,0)[0]>0)]}


def verify_prices(rec,exact,c):
    for m in HS:
        one=rec['subset_results'][f'{m:04b}']; two=exact['subsets'][str(m)]
        assert one['nonzero_records']==two['reachable_records']
        for method in METHODS:
            rr=one['priced'][method]; chk=two[str(c)][method]
            assert rr['launch_acceptance']==F(chk['per_launch_rate']) and rr['weight']==F(chk['raw_weight'])
            assert rr['certificate']['lower_equals_upper_raw']==rr['weight']
    for method in METHODS:
        s=rec['full_observer'][method]['stricter_each_h_must_meet_target']
        a=exact['per_true_h'][str(c)][method]
        assert s['go']['mass']==F(a['per_launch_rate'])
        assert all(s['per_h'][f'{h:04b}']['per_original']==F(a['by_h'][h]['per_launch_rate']) for h in HS)


def verify_physical_tags(law,cubes,controls):
    """Copy s into four ready bits and explicitly return them by the inverse controlled flips."""
    old=[allowed_old(r,law) for r in product((0,1),repeat=9)]
    tag_after_write=[0 ^ s for s in HS]
    tag_after_inverse=[tag ^ s for s,tag in enumerate(tag_after_write)]
    assert len(set(tag_after_write))==16 and set(tag_after_inverse)=={0}
    for basis in VIEWS:
        for k in KS:
            if basis=='mixed':
                u,b=divmod(k,2)
                amplitudes=[plus+(-1)**b*minus for plus,minus in zip(old[2*u],old[2*u+1],strict=True)]
            else:
                amplitudes=old[k]
            paid_groups=[[0,0] for s in HS]
            for s,value in enumerate(amplitudes):
                paid_groups[tag_after_write[s]][s>>3]+=value
            # An orthogonal retained exit leaves squares per tag. Any h gives the
            # same matrix because the paid-sign phase is constant within each group.
            tagged=sum_forms((i*i,i*j,j*j) for i,j in paid_groups)
            signed_by_half=[chars(tuple(value if (s>>3)==half and tag_after_inverse[s]==0 else 0
                                          for s,value in enumerate(amplitudes))) for half in (0,1)]
            for h,(i,j) in enumerate(zip(*signed_by_half,strict=True)):
                assert controls[basis]['tagged'][h][k]==tagged
                assert cubes[basis][h][k]==(i*i,i*j,j*j)
    return {'copy_register_before':0,'copy_after_each_ordinary_s':tag_after_write,
            'copy_after_inverse_for_each_s':tag_after_inverse,'retained_and_returned_gram_checks_each':2*8192,
            'earlier_sibling_Z_copy':'its orthogonal t registers retain the two separate nine-Z matrices for each h,u,b; a resolved nine-Z read is unchanged.'}


def compile_study():
    import audit
    physical=audit.run()
    out={}
    for law in LAWS:
        record=physical['laws'][law]
        cubes={basis:build_records(law,basis) for basis in VIEWS}
        denominators={b:record['N']*(32 if b=='mixed' else 16) for b in VIEWS}
        controls={b:{'dummy':dummy_cube(law,g), 'tagged':tagged_cube(g),
                     'struck_Z':struck_Z_cube(cubes['nine_z']) if b=='mixed' else g} for b,g in cubes.items()}
        forms_by_view={}; analyses={}
        for b in VIEWS:
            p=record['views'][b]
            assert p['launch_denominator']==denominators[b]
            forms_by_view[b]=verify_basis(law,cubes[b],b,p,physical)
            analysis={}
            for c in (0,1):
                a=basis_tests(law,b,cubes,denominators,controls,c)
                verify_prices(a,p,c)
                analysis[str(c)]=a
            analyses[b]=analysis
        templates=[(1,0,0),(0,1,0),(0,0,1)]
        out[law]={'N':record['N'],'denominators':denominators,'views':analyses,'raw_record_types':forms_by_view,
                  'physical_tag_write_and_return':verify_physical_tags(law,cubes,controls),
                  'raw_templates_for_all_other_packets': [{'p_t_q':g,'raw_8_by_8_gram':matrix(law,g),
                         'raw_8_settings_by_8_ordered_answers':signed_table(law,g)} for g in templates],
                  'previous_fixed_two_record_mask':{str(c):eight_known(cubes['mixed'],denominators['mixed'],law,c) for c in (0,1)}}
    return {'schema':1,'laws':out,'literal_physical_audit':physical,
            'scope':'One fixed orientation/address/basis and one pre-settings classical bit on the stated positive coherent original source.',
            'packet_readout':'Sum each listed p,t,q times the three signed raw templates. Divide by the stated original denominator for joint outcome at a specified setting; divide again by eight to include its launch draw. For conditional cells divide raw cells by packet w, undefined at w=0.',
            'zero_labels':'Every null input label is retained, conventionally mapped to decline. A blind or occupied writer or absent source gives no fresh announcement; see physical bank cuts under literal_physical_audit.',
            'codebook':'h bit order s0,s1,s2,s3; k=2*u+b (+ first) or the ordinary nine-bit number. A subset mask uses zero padding only in the concealed positions. Encoded subset label=512*(h & J)+k. Unlisted attaining mask entries are zero.'}


def main():
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--check',action='store_true'); group.add_argument('--write',action='store_true')
    args=parser.parse_args(); record=compile_study()
    content=bytearray(gzip.compress(canonical(record),compresslevel=9,mtime=0))
    content[9]=255  # Canonical OS byte across CPython gzip implementations.
    content=bytes(content)
    path=HERE/'all_erasure_evidence.json.gz'; checksum=lambda x:hashlib.sha256(x).hexdigest()
    bound=dict(record['literal_physical_audit']['source_sha256'])
    for source in [HERE/name for name in ('signed_counts.py','select_flags.py','replay.py','audit.py','preregistration.md')]+[PARENT/'independent_rates.py']:
        name=str(source.relative_to(ROOT)); d=checksum(source.read_bytes());assert bound.setdefault(name,d)==d
    receipt={'artifact':path.name,'bytes':len(content),'sha256':checksum(content),'source_bindings':dict(sorted(bound.items())),
             'interpreter_verification':'Python standard library, no network; Python 3.13 byte-replayed with deterministic zero-time gzip and exact integer and rational operations.',
             'physical_public_variants':record['literal_physical_audit']['public_source_variants'],
             'advice_sha256':checksum((HERE/'design_reviews.json').read_bytes()),'source_contribution':0,'scientific_referee':'pending',
             'nominal_record_matrices_and_all_64_setting_answer_entries_checked':32768,
             'optimizer_cross_checks':'All 256 coarsening prices and 256 individual-true-port prices agree across independently implemented solvers; both orientations counted.'}
    receipt_data=(json.dumps(receipt,sort_keys=True,indent=2)+'\n').encode(); p0=HERE/'receipt.json'
    if args.write:
        path.write_bytes(content);p0.write_bytes(receipt_data)
    else:
        assert path.read_bytes()==content,'evidence differs from exact replay'
        assert p0.read_bytes()==receipt_data,'receipt differs from exact replay'
    print(f"{path.name} {len(content)} bytes SHA-256 {checksum(content)}; receipt {checksum(receipt_data)}")

if __name__=='__main__':main()
