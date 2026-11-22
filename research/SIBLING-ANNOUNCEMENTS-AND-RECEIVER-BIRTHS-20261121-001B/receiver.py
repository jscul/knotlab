"""Literal paid cells, ordinary posteriors, phase controls, and attainable-stage tests."""
import argparse
from collections import Counter, defaultdict
from fractions import Fraction as F
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
from math import prod
import json
from pathlib import Path
import sys

from paid_values import (COMPANIONS, PAIRS, ROOTS, TRIPLES, digits, local_legal,
                         sibling_guess, support_lifts, weighted_holdings)

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
PRIOR = ROOT / 'research/NEWBORN-TABLES-AND-THREE-DONOR-RETURNS-20261121-001A'
RIVALS = ROOT / 'experiments/FORBIDDING-JOIN-20261120-001B/FORBIDDING-JOIN-20261120-001B-E001_free_readings/rival_growth.py'
PARITY_PRIOR = ROOT / 'research/SPENT-PASTS-AND-TWO-SHARED-NAMES-20261121-001A/controls.py'
WRITER = ROOT / 'research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py'
ARMS = ('ordinary', 'one_fewer', 'arity_floor')


@cache
def load(path):
    name = 'receiver_study_' + path.stem
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def owner_map(stars):
    holders = defaultdict(list)
    for k, support in enumerate(stars):
        for b in support:
            holders[b].append(k)
    assert all(len(row) in (1, 2) for row in holders.values())
    return holders


@cache
def growth(k, law, policy, grant_from):
    p = (tuple(range(k)),)
    ages = []
    for age in range(1, 9):
        arm = policy if age >= grant_from else 'ordinary'
        next_stars, receipt = load(RIVALS).grow(p, law, arm, load(PRIOR / 'physical.py')._engine()[0])
        if next_stars is None:
            ages.append({'age': age, 'policy':arm, 'status':receipt['status'],
                         'shortages':receipt.get('shortages', {})})
            break
        owners = owner_map(p)
        nxtowners = owner_map(next_stars)
        for birth in receipt['births']:
            birth['actual_paid_parents'] = [[owners[b][0], b] for b in birth['inputs']]
            assert sorted(i for i,b in birth['actual_paid_parents']) == list(birth['parents'])
            assert all(len(owners[b])==1 and len(nxtowners[b])==2 for b in birth['inputs'])
            assert all(nxtowners[b]==[birth['knot']] for b in birth['fresh'])
        ages.append({'age':age, 'policy':arm, 'status':'funded', 'births':receipt['births'],
                     'stars':next_stars,'next_status':receipt['following_funding']['status']})
        p = next_stars
    return ages


def bind_history(k, law, policy, grant_from):
    ages = growth(k,law,policy,grant_from)
    birth1 = sorted(ages[0]['births'], key=lambda b:b['inputs'])
    roles = {b['knot']:i for i,b in enumerate(birth1)}
    focus = birth1[0]
    if len(ages)<2 or 'births' not in ages[1]:
        return {'ages':ages,'original_paid':focus['inputs'][0],'eligible_focal':len(focus['fresh'])==k-1,
                'pair_stage':None}
    pairs = {}
    for b in ages[1]['births']:
        key = tuple(sorted(roles[i] for i in b['parents']))
        assert key not in pairs and len(key)==2
        inputs = {roles[i]:n for i,n in b['actual_paid_parents']}
        pairs[key]={'holder':b['knot'],'x_ij':inputs[key[0]],'x_ji':inputs[key[1]],'y':b['fresh']}
    assert set(pairs)==set(combinations(range(k),2))
    xrow = {}
    for (i,j),b in pairs.items():
        xrow[i,j],xrow[j,i]=b['x_ij'],b['x_ji']
    for i, b in enumerate(birth1):
        assert set(b['fresh']) == {n for (a,j),n in xrow.items() if a==i}
    sibling={}
    for f in range(k):
        siblings = tuple(i for i in range(k) if i!=f)
        aimed = tuple(sorted(pairs[e]['holder'] for e in combinations(siblings,2)))
        if k!=4 or len(ages)<3 or 'births' not in ages[2]:
            continue
        actual = [b for b in ages[2]['births'] if tuple(b['parents'])==aimed]
        assert len(actual)==1
        child=actual[0]
        branch=[child['knot']]
        track=[]
        for step in ages[3:]:
            if 'births' not in step:
                break
            branch = [b['knot'] for b in step['births'] if set(branch).intersection(b['parents'])]
            track.append({'age':step['age'],'descendants':branch})
        sibling[str(f)]={'birth':child,'old_six':sorted(xrow[i,j] for i in siblings for j in siblings if i!=j),
                        'other_three_exterior':sorted(xrow[i,f] for i in siblings),
                        'focal_marks':sorted(xrow[f,j] for j in siblings),'descendants':track}
    accessible=[]
    for step in ages:
        if 'stars' not in step:
            continue
        owners=owner_map(step['stars'])
        accessible.append({'age':step['age'],'paid_u0_holders':owners[focus['inputs'][0]],
                           'focal_fresh_holders':{n:owners[n] for n in focus['fresh']},
                           'live_focal_marks':[n for n in focus['fresh'] if len(owners[n])==1]})
    return {'ages':ages,'F':birth1,'pairs':{digits(e):p for e,p in pairs.items()},
            'directed_x':{digits(e):v for e,v in xrow.items()},'sibling':sibling,'access':accessible,
            'eligible_focal':len(focus['fresh'])==k-1}


def parity(b):
    f=b['F']
    names=tuple(n for row in f for n in row['fresh'])
    pairs=tuple(b['pairs'][digits(e)] for e in combinations(range(3),2))
    xwords=[bits for bits in product((0,1),repeat=6) if sum(bits)%2==0]
    old = {x:tuple(x[i]^x[i+1] for i in (0,2,4)) for x in xwords}
    ys = {x:tuple(x[names.index(z['x_ij'])]^x[names.index(z['x_ji'])] for z in pairs) for x in xwords}
    charges={}
    for i,j in product(range(2),repeat=2):
        toggles=(i,2+j)
        def flip(x):
            return tuple(v^int(k in toggles) for k,v in enumerate(x))
        changes={tuple(a^v for a,v in zip(ys[x],ys[flip(x)])) for x in xwords}
        assert len(changes)==1
        dy=changes.pop()
        ports={}
        for h in product((0,1),repeat=3):
            phase=lambda a:(-1)**sum(i*j for i,j in zip(a,h))
            products=[phase(old[x])*phase(old[flip(x)]) for x in xwords]
            d=F(sum(products),32)
            assert d==(-1)**(h[0]+h[1])
            tag_records={
                'no_extra_tag': lambda x:(), 'unreturned_a0':lambda x:old[x][0],
                'unreturned_a2':lambda x:old[x][2], 'unreturned_a0_xor_a1':lambda x:old[x][0]^old[x][1],
                'returned_a0':lambda x:(), 'B01_new_value':lambda x:ys[x][0],
                'all_three_new_values':lambda x:ys[x]}
            moments={g:F(sum(v for x,v in zip(xwords,products) if tag(x)==tag(flip(x))),32)
                     for g,tag in tag_records.items()}
            assert moments['unreturned_a0']==0 and moments['unreturned_a2']==d
            ports[digits(h)]={'launch_chance':F(1,8),'XJ':d,'P_K101_if_sign_writer_supplied':(1+d)/2,
                              'tag_conditioned_XJ':moments}
        assert sum(v['launch_chance']*v['XJ'] for v in ports.values())==0
        charges[f'{i}{j}']={'actual_marks':[names[k] for k in toggles],'delta_y':dy,
                           'native_y01_changed':bool(dy[0]),'all_ports':ports}
    prior=load(PARITY_PRIOR).core_fixture('parity')['change_on_two_children']
    assert F(prior['retained_moment'])==0 and F(prior['all_clean_moment'])==charges['00']['all_ports']['000']['XJ']
    by_y=defaultdict(list)
    for x,y in ys.items():
        by_y[digits(y)].append(digits(x))
    assert all(len(v)==8 for v in by_y.values())
    for values in by_y.values():
        assert all({x[i] for x in values}=={'0','1'} for i in range(6))
    return {'physical_name_order':names,'paid_pair_order':[p['holder'] for p in pairs],
            'archived_toggle':'00','all_four_toggles':charges,'word_fibres_of_live_values':dict(by_y),
            'retained_zero':all(old[x] != old[tuple(v^int(k in (0,2)) for k,v in enumerate(x))] for x in xwords),
            'supplied_sign_keeper':{'positive_full':{'101':'1'},'negative_full':{'011':'1'},
                'either_singleton':{'101':'1/2','011':'1/2'},'retained':{'101':'1/2','011':'1/2'},
                'all_clean_at_000':{'101':'1'},'no_sign_or_keeper_write':{'110':'1'}},
            'reader_relaunch':{'age1':{'loose':names,'sign_permutation_supplied':True},
                'age2':{'loose':tuple(p['y'][0] for p in pairs),'old_marks_are_now_paid':True}}}


def tag_table(u, tag):
    vec=[int(w!=(0 if u==0 else 7)) for w in range(8)]
    gr=[[a*b*int(tag(i)==tag(j)) for j,b in enumerate(vec)] for i,a in enumerate(vec)]
    answer=load(PRIOR/'answers.py').joint(gr)
    return gr,answer


def gap(table,u):
    z=7*u
    lhs=sum(v for out,v in enumerate(table[7]) if out.bit_count()>=2)
    right=table[0][z]
    for mask in (1,2,4):
        right+=sum(v for out,v in enumerate(table[mask])
                   if out&mask and (out&(7^mask))!=(z&(7^mask)))
    return lhs-right


def nae_tables():
    cases={}
    for u in (0,1):
        cases[u]={}
        target,_=tag_table(u,lambda w:())
        for mode,fn in [('paid_u_only',lambda w:()),('one_focal_tag',lambda w:w%2),
                        ('whole_focal_tag',lambda w:w),('returned_focal_tag',lambda w:())]:
            g,q=tag_table(u,fn)
            cases[u][mode]={'gram':g,'eight_settings_eight_outcomes':q,'excess':gap(q,u),
                            'equals_target_gram':g==target}
        assert cases[u]['paid_u_only']['excess']==F(1,14)
    old=list(product((0,1),repeat=4))
    banks={u:tuple(r for r in range(8) if r!=(0 if u==0 else 7)) for u in (0,1)}
    counts={}
    total=sum(7**4 for _ in ROOTS)
    for h in old:
        data=defaultdict(lambda:[0]*8)
        for u in ROOTS:
            sign=(-1)**sum(a*b for a,b in zip(u,h))
            for a,b,c in product(*(banks[i] for i in u[1:])):
                vec=data[a,b,c]
                for w in banks[u[0]]:
                    vec[w]+=sign
        weight=sum(a*a for v in data.values() for a in v)
        events={}
        for v in (0,1):
            ext=(7*v,)*3
            amplitudes=data[ext]
            assert sum(a*a for a in amplitudes)==7
            outer=[[a*b for b in amplitudes] for a in amplitudes]
            assert outer==cases[v]['paid_u_only']['gram']
            events[v]={'exterior':digits((v,)*9),'amplitude_vector':amplitudes,
                       'joint_with_port':F(7,16*total),'given_port':F(7,weight)}
        counts[digits(h)]={'port':F(weight,16*total),'both_exteriors':events,
                           'neither_exterior_given_port':1-F(14,weight)}
    assert sum(x['port'] for x in counts.values())==1
    assert counts['0000']['both_exteriors'][0]['given_port']==F(1,50018)
    return {'on_u_only':cases,'full_retained_assignment_count':total,'ports_and_exterior':counts,
            'retained_P_u':F(1,2),'retained_P_each_exterior':F(7,total),
            'retained_neither_exterior':1-F(14,total),
            'ordinary_focal_one_fresh_given_u0':{'0':F(3,7),'1':F(4,7)},
            'ordinary_focal_one_fresh_given_u1':{'0':F(4,7),'1':F(3,7)},
            'ordinary_focal_homogeneous_probability':F(1,7),
            'ordinary_focal_triple_success':F(1,7)+F(6,7)/2}




def calibrated_writers(parity_data, ordinary_writer):
    """Apply normalized two-input projectors and the physical controller separately."""
    controller = ordinary_writer['actual_separately_supplied_controls']
    word_pairs = []
    for values in parity_data['word_fibres_of_live_values'].values():
        unused = set(values)
        while unused:
            x = min(unused)
            partner = ''.join(str(int(b)^int(i in (0,2))) for i,b in enumerate(x))
            assert x!=partner and partner in unused
            unused.remove(x); unused.remove(partner)
            word_pairs.append([x,partner])
    assert len(word_pairs)==16
    profiles={}
    for source,(a,b) in {'positive_full':(1,1),'negative_full':(1,-1),
                         'first_singleton':(1,0),'second_singleton':(0,1)}.items():
        den=2*(a*a+b*b)
        ports=tuple(F(n*n,den) for n in (a+b,a-b))
        assert sum(ports)==1
        modes={}
        for c in ('00','01','10','11'):
            dest=defaultdict(F)
            for outcome,p in enumerate(ports):
                dest[controller[f'{outcome}/{c}']['terminal']]+=p
            modes[c]=dict(dest)
        profiles[source]={'projected_plus_minus':ports,'writes_for_each_connectivity':modes}
    probabilities=profiles['positive_full']['projected_plus_minus']
    assert probabilities==(1,0) and profiles['first_singleton']['projected_plus_minus']==(F(1,2),F(1,2))
    orientation_copy={}
    for c in (0,1):
        terminal=controller[f'{c}/11']['terminal']
        projected=[]
        for bits in TRIPLES:
            if local_legal(c,bits):
                projected.append([digits(bits),terminal])
        assert len(projected)==7 and len({t for w,t in projected})==1
        orientation_copy[c]={'terminal_on_each_focal_word':projected,
                             'keeper_code_reused_on_second_read':terminal,
                             'conditional_kernel':'The external control receives only the paid c.',
                             'reading_while_focal_loose':1,
                             'new_native_funding_connection_to_paid_c':False}
    return {'sixteen_actual_J_pairs':word_pairs,'pair_profiles':profiles,
            'u_only_separate_supplied_write':orientation_copy}

def spent_focal_table(grant):
    """Retrospective reading on age-two spent focal names in the full uniform state."""
    from paid_values import fresh_choices
    endings={pair:set(fresh_choices(pair,grant)) for pair in product((0,1),repeat=2)}
    grams=[[[0]*8 for _ in range(8)] for _ in range(2)]
    for others in product(TRIPLES,repeat=3):
        eligible=Counter(u[0] for u in ROOTS if all(local_legal(c,row) for c,row in zip(u[1:],others)))
        if not eligible:
            continue
        dirs={(i,j):v for i,row in zip((1,2,3),others) for j,v in zip(COMPANIONS[i],row)}
        internal=prod(len(endings[dirs[i,j],dirs[j,i]]) for i,j in combinations((1,2,3),2))
        ext=[dirs[i,0] for i in (1,2,3)]
        for k,left in enumerate(TRIPLES):
            for l,right in enumerate(TRIPLES):
                shared=internal*prod(len(endings[a,z]&endings[b,z]) for a,b,z in zip(left,right,ext))
                for c,n in eligible.items():
                    if local_legal(c,left) and local_legal(c,right):
                        grams[c][k][l]+=n*shared
    result={}
    for c,g in enumerate(grams):
        total=sum(row[i] for i,row in enumerate(g))
        q=load(PRIOR/'answers.py').joint(g)
        result[c]={'full_conditional_mass':total,'gram':g,'eight_settings_eight_outcomes':q,
                   'excess':gap(q,c),'purity':F(sum(n*n for row in g for n in row),total**2)}
    return result

def physical_writer():
    m=load(WRITER)
    out={}
    for c in (0,1):
        start=m.encode(m.PAIR[0],q=c)
        for st in product((False,True),repeat=2):
            end,tr=m.write_keeper(start,stages=st)
            assert all(not m._failed_physical(w,law) for step in tr for w in (step['before'],step['after']) for law in m.LAW)
            out[f'{c}/{digits(map(int,st))}']={'ordinary_control':c,'terminal':m.decode(end)['keeper'],
                 'status':[step['status'] for step in tr],'before_after':[[step['before'],step['after']] for step in tr]}
    native=load(PRIOR/'physical.py')._engine()[0]
    stars=tuple(tuple(row) for row in m.SUBSTRATE.values())
    fail={law:load(RIVALS).grow(stars,law,'ordinary',native)[1] for law in m.LAW}
    assert all(x['status']=='stalled' and len(x['shortages'])==14 for x in fail.values())
    return {'actual_separately_supplied_controls':out,'whole_funding':fail,'physical_knots':len(stars)}




def exact_rival_closing_old_words(host):
    """Partition all old complete words by the actual four unfunded-in-fresh constraints."""
    import numpy as np
    pairs = [host['pairs'][digits(e)] for e in PAIRS]
    nas = tuple(n for b in pairs for n in b['y'])
    assert len(nas)==12 and len(set(nas))==12
    all_y=np.arange(1<<len(nas),dtype=np.uint16)
    ybits={n:((all_y>>k)&1).astype(np.int8) for k,n in enumerate(nas)}
    real_triples=host['ages'][2]['births']
    result={}
    for law in ('parity','nae'):
        v_bad=np.zeros(len(all_y),dtype=np.int8)
        for j,b in enumerate(real_triples):
            ys=sum(ybits[n] for n in b['inputs'])
            denied=ys%2!=0 if law=='parity' else (ys==0)|(ys==3)
            v_bad |= denied.astype(np.int8)<<j
        cells=[]
        for b in pairs:
            count=ybits[b['y'][0]]+ybits[b['y'][1]]
            cells.append({(i,j):((count+i+j)%2==0 if law=='parity'
                                  else (count+i+j>0)&(count+i+j<4))
                          for i,j in product((0,1),repeat=2)})
        hist=np.zeros(16,dtype=np.int64)
        for rows in product(TRIPLES,repeat=4):
            if law=='parity':
                roots=int(sum(sum(row) for row in rows)%2==0)
            else:
                roots=sum(all(local_legal(c,row) for c,row in zip(u,rows)) for u in ROOTS)
            if not roots: continue
            masks=[cells[i][rows[a][COMPANIONS[a].index(z)],rows[z][COMPANIONS[z].index(a)]]
                   for i,(a,z) in enumerate(PAIRS)]
            possible=np.logical_and.reduce(masks)
            hist+=roots*np.bincount(v_bad[possible],minlength=16)
        total=int(hist.sum())
        result[law]={'old_full_words':total,'surviving':int(hist[0]),
                    'failed_new_holder_mask_counts':hist.tolist(),
                    'new_holder_order_for_mask':[b['knot'] for b in real_triples]}
    assert result['nae']['old_full_words']==61954240
    return result

def independent_cut_agreement(hosts):
    archive = json.loads(gzip.decompress((HERE/'native.json.gz').read_bytes()))['cases']
    totals = Counter()
    for key, physical in hosts.items():
        width, law, arm, start = key.split('/')
        hist = arm
        if arm != 'ordinary' and start == 'from2':
            hist = 'ordinary_first__' + arm
        if arm != 'ordinary' and start == 'from3':
            if width == '3':
                continue  # These extra isolated-three restarts are available here only.
            hist = 'ordinary_second__' + arm
        case = archive['isolated_four' if width == '4' else 'isolated_three']['laws'][law]['histories']
        alternate = case[hist]['cuts']
        assert len(alternate)==len(physical['ages'])
        for ours, theirs in zip(physical['ages'],alternate,strict=True):
            assert ours['status']==theirs['status'] and ours['age']==theirs['age']
            totals['cut comparisons'] += 1
            if ours['status']!='funded':
                continue
            assert list(map(list,ours['stars']))==theirs['stars_after']
            for b,c in zip(ours['births'],theirs['births'],strict=True):
                assert b['knot']==c['holder'] and list(b['parents'])==c['parents']
                assert b['actual_paid_parents']==c['paid'] and list(b['fresh'])==c['fresh_names']
                assert b['D']==c['demand']
                assert b['q']==c['ordinary_grant'] and b['f']==c['grant']
                assert b['old_inputs_already_imply_law']==c['implied']
                totals['birth comparisons'] += 1
    return dict(totals)


def canonical_checks():
    frame = load(PRIOR/'physical.py')
    archive=json.loads(gzip.decompress((HERE/'native.json.gz').read_bytes()))['cases']
    laws=defaultdict(set)
    total=0
    failures=[]
    for source, details in archive.items():
        for law, data in details['laws'].items():
            for h in data['original_support_projections']:
                total+=1
                assert h['whole_canonical_relation']
                laws[law].add(len(h['scope']))
            for arm, hist in data['histories'].items():
                for age, projected in hist['support_projections_at_first_two_reached_cuts'].items():
                    for h in projected:
                        total+=1
                        if not h['whole_canonical_relation']:
                            failures.append([source,law,arm,age,h['holder'],len(h['allowed'])])
                for step in hist['cuts']:
                    for b in step['births']:
                        laws[law].add(len(b['consumed_names'])+b['grant'])
    cli={}
    for law, sizes in laws.items():
        cli[law]={}
        for n in sorted(sizes):
            allowed=tuple(w for w in range(1<<n) if (w.bit_count()%2==0 if law=='parity' else 0<w<(1<<n)-1))
            cli[law][n]=frame._canonical_check(n,allowed)
    return {'canonical_cli_by_law_and_actual_arity':cli,'actual_named_projections_checked':total,
            'narrowed_actual_projections':failures}

def main():
    cmd=argparse.ArgumentParser()
    cmd.add_argument('--verify',action='store_true',help='Recompute and byte-compare without rewriting the record.')
    args=cmd.parse_args()
    hosts={}
    for width, law, start in product((3,4),('parity','nae'),(1,2,3)):
        for arm in ARMS:
            hosts[f'{width}/{law}/{arm}/from{start}']=bind_history(width,law,arm,start)
    raw={'canonical_checks':canonical_checks(),'exact_from_second_rival_survival':exact_rival_closing_old_words(hosts['4/nae/ordinary/from1']),
         'native_cut_agreement':independent_cut_agreement(hosts),'isolated_paid_cuts':hosts,'parity':parity(hosts['3/parity/ordinary/from1']),
         'nae_measurements':nae_tables(),'weightings':{},'support_lifts':support_lifts(),
         'separate_physical_keeper':physical_writer(), 'sibling_receiver_value':sibling_guess(),
         'spent_focal_retrospective_uniform_complete':{g:spent_focal_table(g) for g in (1,2)}}
    raw['charged_writer_calibrations']=calibrated_writers(raw['parity'],raw['separate_physical_keeper'])
    for w in (1,2):
        raw['weightings'][w]=weighted_holdings(w)
    plain=json.dumps(raw,sort_keys=False,separators=(',',':'),default=str).encode()
    if args.verify:
        assert gzip.decompress((HERE/'receipts.json.gz').read_bytes())==plain
    else:
        encoded=gzip.compress(plain,compresslevel=9,mtime=0)
        (HERE/'receipts.json.gz').write_bytes(encoded)
    print('verified' if args.verify else 'wrote',len(plain),sha256(plain).hexdigest())


if __name__=='__main__':
    main()
