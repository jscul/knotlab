"""Source contraction, exact flag optima, full eight-setting and instrument checks."""
import argparse
from collections import Counter
from fractions import Fraction as F
from functools import cache
import gzip
import hashlib
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
from pathlib import Path

from announcement_rules import optimize

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[1]
EARLIER='NEWBORN-TABLES-AND-THREE-DONOR-RETURNS-20261121-001A'
PRIOR=ROOT/'research'/EARLIER/'newborn_evidence.json.gz'
EARLIER_CHECK=ROOT/'research'/EARLIER[:-1]/'newborn_check.py'
BITS=tuple(product((0,1),repeat=3))
OLD=tuple(product((0,1),repeat=4))
RANGE=range(8)
LAWS=('nae','parity')
MODES=('retained','clean')


def integer(word):
    return sum(b<<(len(word)-1-i) for i,b in enumerate(word))


def legal(bits, law):
    return len(set(bits))==2 if law=='nae' else sum(bits)%2==0


def outer(vectors):
    return [[sum(row[a]*row[b] for row in vectors) for b in RANGE] for a in RANGE]


def tr(g):
    return sum(g[i][i] for i in RANGE)


def as_key(g):
    return tuple(tuple(r) for r in g)


def proj_question(g):
    """Use signed observable moments, followed by binary inversion."""
    out=[]
    for s in RANGE:
        raw=[sum((-1)**(x&j&(7^s)).bit_count()*g[x][x^(s&j)] for x in RANGE) for j in RANGE]
        out.append(tuple(sum((-1)**(a&j).bit_count()*raw[j] for j in RANGE)/F(8) for a in RANGE))
    return tuple(out)


@cache
def table(g):
    return proj_question(g)


def expression(s,a,c=0):
    return (int(s==7 and a.bit_count()>=2)-int(s==0 and a==7*c)
            -int(s.bit_count()==1 and (s&a)!=0 and (a&(7^s))!=((7^s) if c else 0)))


def score(rows,c=0):
    return sum(expression(s,a,c)*rows[s][a] for s in RANGE for a in RANGE)


def marginal(d, names, s):
    out=Counter()
    for a in RANGE:
        out[tuple(BITS[a][i] for i in names)]+=d[s][a]
    return out


def test_nonsignalling(rows):
    for n in (1,2):
        for subset in combinations(range(3),n):
            by_settings={}
            for s in RANGE:
                own=tuple(BITS[s][i] for i in subset)
                m=marginal(rows,subset,s)
                assert m==by_settings.setdefault(own,m)


def laws(law):
    """Use each sibling triple's ordinary constraint to contract the original holding."""
    local=[tuple(int(legal((s,*x),law)) for x in BITS) for s in (0,1)]
    ext={v:tuple(i for i in (0,1) if legal((i,*v),law)) for v in BITS}
    rows=[]
    for r in product((0,1),repeat=9):
        domains=[ext[r[j:j+3]] for j in (0,3,6)]
        old=[s for s in OLD if legal(s,law) and all(x in dom for x,dom in zip(s[1:],domains))]
        g=as_key(outer([local[s[0]] for s in old]))
        cs={}
        for h in OLD:
            n=[sum((-1)**sum(i*j for i,j in zip(h,s))*local[s[0]][x] for s in old) for x in RANGE]
            cs[integer(h)]=as_key(outer([n]))
        assert all(sum(cs[h][i][j] for h in cs)==16*g[i][j] for i in RANGE for j in RANGE)
        t=tuple(sum(s[0]==u for s in old) for u in (0,1))
        rows.append({'old':tuple(map(integer,old)),'pair':t,'retained':g,'clean':cs[0],'ports':cs})
    return rows


def packet(g,launch_den,c=0):
    g=as_key(g); w=tr(g); raw=table(g)
    assert all(sum(r)==w for r in raw)
    assert min(i for r in raw for i in r)>=0
    ans=tuple(tuple(q/w for q in r) for r in raw) if w else None
    if ans: test_nonsignalling(ans)
    return {'gram':g,'raw_trace':w,'launch_mass':w/F(launch_den),
            'conditional_I':score(raw,c)/w if w else None,
            'conditional_8by8':ans,'per_launch_given_each_setting':[[q/F(launch_den) for q in r] for r in raw],
            'per_launch_joint_settings_and_outcomes':[[q/F(8*launch_den) for q in r] for r in raw],
            'no_answer_when_mass_zero':not bool(w)}


def combined(rows,mask,kind):
    factors=Counter()
    for entry,f in zip(rows,mask,strict=True):
        if f:
            g=entry['ports'][kind] if isinstance(kind,int) else entry[kind]
            factors[g]+=f
    return tuple(tuple(sum((f*g[a][b] for g,f in factors.items()),F(0))
                       for b in RANGE) for a in RANGE)


def add(*grams):
    return tuple(tuple(sum(g[i][j] for g in grams) for j in RANGE) for i in RANGE)


def mult(g,f):
    return tuple(tuple(f*x for x in r) for r in g)


def scalars(rows,mode,c):
    w=[tr(r[mode]) for r in rows]
    v=[score(table(r[mode]),c) for r in rows]
    return w,v


def compact(d):
    return json.dumps(d,sort_keys=True,separators=(',',':'),default=str).encode()


def signature(p):
    return hashlib.sha256(compact(p)).hexdigest()


def raw_cross(rows, law, left, right, mode):
    focal=[[int(legal((b,*x),law)) for x in BITS] for b in (0,1)]
    def f(row):
        return focal[OLD[row][0]]
    if mode=='retained':
        pairs=[(s,s) for s in rows[left]['old'] if s in rows[right]['old']]
    else:
        pairs=product(rows[left]['old'],rows[right]['old'])
    g=[[0]*8 for _ in RANGE]
    for a,b in pairs:
        u,v=f(a),f(b)
        for i in RANGE:
            for j in RANGE:
                g[i][j]+=u[i]*v[j]
    return as_key(g)


def pair_experiment(rows, law, mode, left, right, den):
    gl,gr=rows[left][mode],rows[right][mode]
    cross=raw_cross(rows,law,left,right,mode)
    diag=mult(add(gl,gr),F(1,2))
    cross_symmetric=mult(add(cross,tuple(zip(*cross))),F(1,2))
    joint=combined(rows,[1]*512,mode)
    outside=add(joint,mult(diag,-2))
    a=add(diag,cross_symmetric)
    b=add(diag,mult(cross_symmetric,-1))
    assert add(a,b,outside)==joint
    ledger={k:packet(g,den) for k,g in (('coherent_plus',a),('coherent_minus',b),
                            ('complementary_tuples_outside_pair',outside),
                            ('diagonal_fair_accept',diag),('diagonal_fair_reject_inside',diag),
                            ('diagonal_full_complement',add(diag,outside)),
                            ('coherent_full_complement',add(b,outside)))}
    ledger.update({'sibling_words':[f'{left:09b}',f'{right:09b}'],
                   'cross_matrix_on_full_fixed_source':cross,
                   'coarse_or_logged_pair_read_price':tr(diag)*2/F(den),
                   'same_ordinary_singleton_acceptance':'1/2 on each named pair member, zero elsewhere',
                   'denominator':den})
    return ledger


def reconstruction_controls(law, rows, N, W):
    out={}
    for mode in MODES:
        den=N if mode=='retained' else 16*N
        tests={}
        for name,flag in (('all',[1]*512),('none',[0]*512),('all_zero',[int(i==0) for i in range(512)]),
                          ('all_one',[int(i==511) for i in range(512)]),
                          ('all_zero_or_one_unannounced',[int(i in (0,511)) for i in range(512)])):
            signal=combined(rows,flag,mode)
            tests[name]=packet(signal,den)
        # The original spent value is a separate observed variable and cannot be read after clean erasure.
        if mode=='retained':
            for c in (0,1):
                v=[int(legal((c,*x),law)) for x in BITS]
                g=mult(as_key(outer([v])),sum(z['pair'][c] for z in rows))
                tests[f'paid_bit_{c}_public_stronger_observer']=packet(g,den,c)
        tests['eight_ordinary_zero_plus_one_sibling_change']=pair_experiment(rows,law,mode,0,1,den)
        tests['outside_fine_record_compare_same_decline_word']=pair_experiment(rows,law,mode,2,4,den)
        plus=tests['outside_fine_record_compare_same_decline_word']['coherent_plus']['launch_mass']
        merged=tests['outside_fine_record_compare_same_decline_word']['coarse_or_logged_pair_read_price']
        fair=tests['outside_fine_record_compare_same_decline_word']['diagonal_fair_accept']['launch_mass']
        assert plus==merged and 2*fair==merged
        tests['same_decline_flag_following_coarse_vs_logged_r']={
            'ready_source':'First select this two-word subspace before all settings, without writing its member.',
            'both_r_give_same_decline_in_canonical_primary_masks':True,
            'later_plus_if_only_coarse_decline_record':plus/merged,
            'later_plus_if_physical_word_record_was_made_then_ignored':fair/merged,
            'surviving_source_tensors':'K_j(r) rho(x,r;y,rprime) conjugate(K_j(rprime)) for a single square-root Kraus operator. Logging r sets every off-diagonal r!=rprime to zero after that copy is ignored.'}
        out[mode]=tests
    return out


def deterministics():
    vals={}
    for c in (0,1):
        values=[]
        for t in product((0,1),repeat=6):
            values.append(sum(expression(s,integer(tuple(t[2*i+b] for i,b in enumerate(BITS[s]))),c) for s in RANGE))
        assert max(values)==0
        vals[str(c)]={'maximum':max(values),'minimum':min(values),'list_order':'z0,x0,z1,x1,z2,x2 lex',
                      'all_64_values':values}
    return vals


def probability_common(gram,law):
    p=packet(gram,tr(gram))['conditional_8by8']; xrow=p[7]; zrow=p[0]
    m=sum(zrow[1:7])
    weights=[]
    for z in product((0,1),repeat=6):
        zi,xi=integer(z[::2]),integer(z[1::2])
        if law=='nae':
            q=((xrow[xi]-(m if xi==0 else 0))/2 if zi in (0,7) else m/6 if xi==0 else F(0))
        else:
            q=zrow[zi]*xrow[xi]
        weights.append(q)
    calc=[[F(0)]*8 for _ in RANGE]
    for word,p0 in zip(product((0,1),repeat=6),weights):
        for s,t in enumerate(BITS):
            calc[s][integer(tuple(word[2*i+b] for i,b in enumerate(t)))]+=p0
    if min(weights)>=0 and tuple(map(tuple,calc))==p: return weights
    raise AssertionError((law,'pooled table did not match its construction'))


def ports_and_writes(rows, law, f, mode, N, W, c):
    decline=[1-q for q in f]
    keep=combined(rows,f,'retained'); lost=combined(rows,decline,'retained')
    total_d=add(keep,lost); total_q=combined(rows,[1]*512,'clean')
    f0=combined(rows,f,mode); d0=combined(rows,decline,mode)
    den=N if mode=='retained' else 16*N
    branches={}
    for h in range(16):
        a=combined(rows,f,h); b=combined(rows,decline,h)
        branches[f'{h:04b}']={'if_predicate_queried_on_this_port_accept':packet(a,16*N,c),
                               'if_predicate_queried_on_this_port_decline':packet(b,16*N,c),
                               'unconditional_source_port':packet(add(a,b),16*N,c),
                               'actual_announcement_bank_when_clean_required':'go or decline' if h==0 else 'ready; source refusal',
                               'source_status_code':'101' if h==0 else '011',
                               'same_port_under_orthogonal_past_tag':{
                                   'masked_input_accept_mass':tr(keep)/F(16*N),
                                   'masked_input_decline_mass':tr(lost)/F(16*N)}}
    all_yes=add(*(branches[k]['if_predicate_queried_on_this_port_accept']['gram'] for k in branches))
    all_no=add(*(branches[k]['if_predicate_queried_on_this_port_decline']['gram'] for k in branches))
    assert all_yes==mult(keep,16) and all_no==mult(lost,16) and add(all_yes,all_no)==mult(total_d,16)
    source_failure=add(mult(total_d,16),mult(total_q,-1)) if mode=='clean' else mult(total_d,0)
    a=packet(f0,den,c);b=packet(d0,den,c);dead=packet(source_failure,den,c)
    assert a['launch_mass']+b['launch_mass']+dead['launch_mass']==1
    pool=[f[i]+f[511-i] for i in range(512)]
    assert max(pool)<=1
    pooled=combined(rows,pool,mode)
    output={
        'primary_accept':a,'source_pass_and_decline':b,'source_failure_bank_ready':dead,
        'retained_mode_or_clean_herald_probability':F(1) if mode=='retained' else F(W,16*N),
        'acceptance_given_eligible_source':tr(f0)/F(N if mode=='retained' else W),
        'overlapping_target_and_its_complement_orientation_support':sum(bool(v and f[511-i]) for i,v in enumerate(f)),
        'either_orientation_hidden':packet(pooled,den,c),
        'either_orientation_hidden_common_weights':probability_common(pooled,law) if tr(pooled) else None,
        'externally_picked_fair_orientation_unannounced':packet(mult(pooled,F(1,2)),den,c),
        'same_chosen_selection_unconditional_retained_tag':packet(keep,N,c),
        'same_chosen_selection_clean_with_orthogonal_tag_present':packet(keep,16*N,c),
        'same_chosen_selection_clean_with_tag_returned':packet(combined(rows,f,'clean'),16*N,c),
        'same_chosen_selection_diagonal_fixed_source':packet(as_key([[f0[i][j] if i==j else 0 for j in RANGE] for i in RANGE]),den,c),
        'character_launch_ledger':branches,
        'physical_indicator_banks':{
            'eligible_and_selected':{'source':'101','announcement':'101','delivered_go':a['launch_mass']},
            'eligible_but_declines':{'source':'101','announcement':'011','delivered_go':0,'mass':b['launch_mass']},
            'invalid_source':{'source':'011','announcement':'110','delivered_go':0,'mass':dead['launch_mass']},
            'public_writer_disconnected':{'source_status':'same as above','announcement':'110','actual_delivered_go':0,'computed_mask_would_pass':a['launch_mass']},
            'busy_announcement_bank_before_launch':{'initial':'101 with no reset','new_write':False,'delivered_fresh_go':0},
            'actual_transmission':'Supplied nondemolition control writes the chosen public binary word into a ready lawful ternary holding; copies to the three settings sites require their ready banks and a broadcast before choices.',
            'native_controls':'Fixed paid incidences and fixed law make the identical ordinary growth turn irrespective of value; birth is not the imposed register writer.'},
        'joint_state_rule':{'diagonal_binary_Kraus':'For mode state rho, accept multiplies each (r,rprime) block by sqrt(a(r)*a(rprime)); decline uses 1-a in both factors. Keep immutable paid tags where present.',
                            'fine_outcome_classical_coin':'With a literal Z read of r and independent seed, each original r block is classical after ignoring its log. The r-diagonal weight at each accepted/declined record is a(r) or 1-a(r). Reduced focal states are identical.',
                            'clean_failed':'Every externally observed nonzero spent-character h gives its recorded unnormalized signed branch. If hidden, pool all nonzero characters without interference.'}}
    return output


def symbolic_scores(rows,law):
    types={}
    for r,obj in enumerate(rows):
        a,b=obj['pair']
        entry=types.setdefault((a,b),{'count':0,'sample':f'{r:09b}','retained_w':tr(obj['retained']),
                                     'clean_w':tr(obj['clean']),'retained_v':score(table(obj['retained'])),
                                     'clean_v':score(table(obj['clean']))})
        entry['count']+=1
        if law=='nae':
            assert tr(obj['retained'])==7*(a+b)
            assert tr(obj['clean'])==7*a*a+12*a*b+7*b*b
            assert entry['retained_v']==F(a-4*b,2)
            assert entry['clean_v']==F(a*a+a*b-4*b*b,2)
    return {f'{a},{b}':j for (a,b),j in sorted(types.items())}


def all_results(rows,law):
    ens={}
    N=sum(tr(k['retained']) for k in rows);W=sum(tr(k['clean']) for k in rows)
    for mode in MODES:
        w,v=scalars(rows,mode,0); wc,vc=scalars(rows,mode,1)
        assert w==wc and list(reversed(w))==w and list(reversed(v))==vc
        d=F(1,28)
        rules={}; main={}
        for view in ('full','symmetric','eight','independent_tenth_bit','no_read'):
            for rand in ((False,) if view=='independent_tenth_bit' else (False,True)):
                key=f'{view}/'+('randomized' if rand else 'deterministic')
                opt=optimize(w,v,d,view,rand)
                f=opt['mask']; assert len(f)==512
                rules[key]=opt
                value=opt['attained_weight']
                rules[key]['per_initial_launch_rate']=value/F(N if mode=='retained' else 16*N)
                rules[key]['within_source_rate']=value/F(N if mode=='retained' else W)
                if view=='full':
                    main[key]=ports_and_writes(rows,law,f,mode,N,W,0)
                    reverse=tuple(reversed(f))
                    rotated=combined(rows,reverse,mode)
                    ok=packet(rotated,N if mode=='retained' else 16*N,1)
                    assert ok['conditional_I']==opt['conditional_I']
                    assert tr(rotated)==value
                    main[key]['transported_orientation_one_accept']=ok
        for rand in (False,True):
            label='old_excess_full/'+('randomized' if rand else 'deterministic')
            opt=optimize(w,v,F(1,14),'full',rand)
            value=opt['attained_weight']; opt['per_initial_launch_rate']=value/F(N if mode=='retained' else 16*N)
            rules[label]=opt
        eight=[]
        for hidden in range(9):
            bins={}
            for i in range(512):
                text=f'{i:09b}'; s=text[:hidden]+text[hidden+1:]
                g=bins.setdefault(s,[0,0]);g[0]+=w[i];g[1]+=v[i]
            mx=max(fq/F(sw) for sw,fq in bins.values() if sw)
            eight.append(mx)
        assert len(set(eight))==1
        ens[mode]={'primary_and_controls_rules':rules,'full_transcripts':main,
                   'max_achieved_I_among_one_missing_coordinate_by_index':eight,
                   'max_I_on_any_single_ordinary_word':max(fq/F(sw) for sw,fq in zip(w,v) if sw)}
    return {'N':N,'W':W,'clean_price':F(W,16*N),'types':symbolic_scores(rows,law),'modes':ens,
            'source_and_instrument_controls':reconstruction_controls(law,rows,N,W)}


def boundary_cost(rows, law, modes, N, W):
    result={}
    for mode in MODES:
        label=modes[mode]['primary_and_controls_rules']['full/randomized']
        f=label['mask']
        partial=[(i,p) for i,p in enumerate(f) if 0<p<1]
        if not partial:
            result[mode]={'necessary_boundary_draws':0,'delivered_go':0 if law=='parity' else None}
            continue
        assert len(partial)==1
        i,p=partial[0]
        n=p.denominator
        bits=(n-1).bit_length()
        # Independent groups of bits: reject values >=n and try again before settings.
        avg=F(bits*(1<<bits),n)
        den=N if mode=='retained' else 16*N
        chance=F(tr(rows[i][mode]),den)
        result[mode]={'boundary_word':f'{i:09b}','conditional_coin_probability':p,
                      'fresh_ordinary_counter_source':'Uniform independent bits, draw a fresh block until its integer is below denominator. Output go iff accepted integer is below numerator.',
                      'bits_per_block':bits,'expected_bits_on_boundary':avg,'chance_of_boundary_per_original_launch':chance,
                      'expected_bits_per_original_launch_for_this_realization':avg*chance,
                      'eventual_resolve_probability':1,'finite_worst_case_block_bound':False,
                      'clean_herald_chance':F(W,16*N),'original_launch_denominator':den}
    return result


def reconcile(literal, rows, law):
    src=literal['laws'][law]
    grams=[as_key(g) for g in literal['gram_library']]
    literal_prob=literal['probability_library']
    matched=set()
    for i,(a,b) in enumerate(zip(rows,src['rows'],strict=True)):
        assert i==b['r_index'] and b['r']==f'{i:09b}'
        assert a['old']==tuple(sorted(v for group in b['compatible_spent_by_focal_paid'] for v in group))
        for k in MODES:
            rec=b[k]; g=a[k]; w=tr(g); wI=score(table(g))
            assert g==grams[rec['gram']] and w==rec['weight'] and wI==F(rec['wI0'])
            assert wI-w/F(28)==-F(rec['loss'])
        for k,j in enumerate(b['character_grams']):
            assert a['ports'][k]==grams[j]
        matched.update(b['character_grams']);matched.update(b[k]['gram'] for k in MODES)
    for ident in matched:
        g=grams[ident];w=tr(g)
        assert ([[str(i/w) for i in r] for r in table(g)] if w else None)==literal_prob[ident]
    return {'rows_checked':len(rows),'retained_character_and_clean_matrices_per_row':17,
            'eight_setting_distributions_checked_per_word_and_matrix':True,
            'distinct_physical_grams_directly_reconciled':len(matched),
            'all_distinct_graded_grams':sorted(matched),'literal_projectors_vs_moment_inversion':True}


def evidence():
    import physical
    literal=physical.run()
    source={}
    spec=spec_from_file_location('independent_newborn_check',EARLIER_CHECK)
    prior_check=module_from_spec(spec)
    spec.loader.exec_module(prior_check)
    for law in LAWS:
        rows=laws(law)
        measure=all_results(rows,law)
        measure['separate_physical_comparison']=reconcile(literal,rows,law)
        assert (measure['N'],measure['W'])==(literal['laws'][law]['N'],literal['laws'][law]['W'])
        measure['boundary_coin_resources']=boundary_cost(rows,law,measure['modes'],measure['N'],measure['W'])
        for mode in MODES:
            compare=literal['laws'][law]['independent_primary_rates'][mode]
            for form in ('deterministic','randomized'):
                actual=measure['modes'][mode]['primary_and_controls_rules']['full/'+form]
                rival=compare[form]
                assert (actual['attained_weight'],actual['per_initial_launch_rate'],actual['within_source_rate'])==tuple(
                    F(rival[k]) for k in ('raw_accepted_weight','original_launch_acceptance','prepared_source_acceptance'))
            old_law='not-all-equal' if law=='nae' else law
            template=prior_check.newborn_matrix(4,old_law,mode=='clean')
            assert template==prior_check.direct_four(old_law,mode=='clean')
            m=combined(rows,[1]*512,mode)
            assert as_key([[template[x,y] for y in BITS] for x in BITS])==m
            old_table,total=prior_check.setting_table(template)
            assert [[old_table[s,z] for z in BITS] for s in BITS]==[[q/total for q in line] for line in table(m)]
            prior_check.answer_lists(old_table,old_law)
        measure['separate_physical_comparison']['previous_coordinator_four_place_direct_matrix_and_all_128_mode_probabilities_match']=True
        source[law]=measure
    return {'schema_version':1,'law_order':LAWS,
            'phase_and_word_order':'Labels and ordered answer bits increase in physical name order. Settings are ZZZ, ZZX, …, XXX. A zero X bit means plus. Tables give eight ordered answers per setting.',
            'paid_and_loose_physical_evidence':literal,'laws':source,
            'fixed_inequality_on_64_lists':deterministics()}


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def record(check):
    obj=evidence()
    raw=gzip.compress(compact(obj),compresslevel=9,mtime=0)
    out=HERE/'announcement_evidence.json.gz'
    src_paths=sorted([HERE/name for name in ('announcement_rules.py','physical.py','replay.py','preregistration.md')]+[PRIOR,EARLIER_CHECK])
    literal=obj['paid_and_loose_physical_evidence']
    receipt={'artifact':out.name,'scientific_referee':'pending','gzip_bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest(),
             'draws':'Finite physical words and exact rational probabilities; no Monte Carlo trials.',
             'project_files':{str(p.relative_to(ROOT)):hash_file(p) for p in src_paths},
             'separate_physical_sources':literal['source_sha256'],
             'public_checker_path_variants':literal['public_source_variants'],
             'recomputed_graded_conditions':'Two laws, 512 labelled siblings per law, retained and all 16 character branches, all eight settings and outcome words for every accepted or declined launch.'}
    output_bytes=(json.dumps(receipt,indent=2,sort_keys=True)+'\n').encode()
    receipt_path=HERE/'receipt.json'
    if check:
        assert out.read_bytes()==raw, 'evidence bytes differ'
        assert receipt_path.read_bytes()==output_bytes, 'receipt bytes differ'
    else:
        out.write_bytes(raw)
        receipt_path.write_bytes(output_bytes)
    print(f"{'verified' if check else 'wrote'} {out.name} {len(raw)} bytes {receipt['sha256']}")
    for law in LAWS:
        for mode in MODES:
            d=obj['laws'][law]['modes'][mode]['primary_and_controls_rules']
            print(law,mode,*(d['full/'+p]['per_initial_launch_rate'] for p in ('deterministic','randomized')))


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    group=parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--write',action='store_true')
    group.add_argument('--check',action='store_true')
    record(parser.parse_args().check)
