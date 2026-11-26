"""Rebuild the eight registered controls, including the counts that fail on the bare rings."""

import argparse
import gzip
import json
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from math import comb
from time import monotonic

from lemma_checks import HERE, INPUT, RAW, holder_neighbors, search, sizes
from regrow_engine import Growth


def given_control(stars, sources, upto, expected):
    adj = holder_neighbors(stars)
    for u in sources:
        assert sizes(adj, u, upto) == [expected(r) for r in range(upto + 1)]
    return {'knots':len(stars),'sources':len(sources),'through_step':upto}


def gate_candidates(arrays, end):
    valid = []
    for j in range(4):
        for a in range(4,end//8+1):
            # Any longer qualifying interval contains the shorter interval starting at the same a.
            def qualifies(h):
                ratios = [Fraction(h[r],r**j) for r in range(a,8*a+1)]
                return max(ratios) <= 2*min(ratios)
            if all(qualifies(h) for h in arrays):
                valid.append([j,a])
    return valid


def ordered_counts(values):
    counts = [0,0,0]
    for i,(left,key_left,count_left) in enumerate(values):
        counts[2] += comb(count_left,2)
        for right,key_right,count_right in values[i+1:]:
            comparison = (left - right)*(key_left - key_right)
            counts[0 if comparison > 0 else 1 if comparison < 0 else 2] += count_left*count_right
    return counts


def tree_checks(stars):
    adj = holder_neighbors(stars)
    root_steps = search(adj, [0])
    assert len(root_steps) == len(stars) and sum(map(len,adj)) == 2*(len(stars)-1)
    assert all(len(adj[u]) == (1 if level == 12 else 3) for u,level in root_steps.items())
    H = sizes(adj,0,12)
    assert H == [3*2**r-2 for r in range(13)]
    increments = [b-a for a,b in zip(H,H[1:])]
    assert all(b==2*a for a,b in zip(increments,increments[1:]))
    leaves = [u for u,row in enumerate(adj) if len(row)==1]
    steps = search(adj,[leaves[0]])
    profile = Counter(steps[u] for u in leaves[1:])
    # The rooted declarations above give two identical continuations at every non-root internal knot,
    # hence the same profile at every leaf. Each unordered pair occurs twice among ordered pairs.
    multiplicities = {d:len(leaves)*n//2 for d,n in profile.items()}
    assert sum(multiplicities.values()) == comb(len(leaves),2)
    # Pin the two route bits of one three-place NAE rule and sum over its third bit. Away from
    # the route, flipping every bit pairs completions of the two boundary values, so their factors cancel.
    local = [[0,0],[0,0]]
    for a,b,c in product(range(2),repeat=3):
        if len({a,b,c})>1:
            local[a][b] += 1
    assert local == [[1,2],[2,1]]
    signs = {}
    for d in multiplicities:
        w0,w1 = 1,0
        for _ in range(d+1):
            w0,w1 = w0*local[0][0]+w1*local[1][0], w0*local[0][1]+w1*local[1][1]
        signs[d] = Fraction(w0-w1,w0+w1)
        assert signs[d] == Fraction(-1,3)**(d+1)
    order = ordered_counts([(abs(signs[d]),-d,m) for d,m in multiplicities.items()])
    reverse = ordered_counts([(abs(signs[d]),d,m) for d,m in multiplicities.items()])
    assert order[0]>0 and order[1]==0 and reverse==[0,order[0],order[2]]
    mixed = ordered_counts([(2,1,1),(1,2,1),(0,0,1),(2,3,1)])
    assert all(n>0 for n in mixed) and sum(mixed)==6
    return {'knots':len(stars),'leaves':len(leaves),'root_counts':H,'increments':increments,
            'leaf_pairs':sum(multiplicities.values()),'by_steps':multiplicities,
            'kappa_by_steps':{k:str(v) for k,v in signs.items()}, 'ordered_concordant_discordant_tied':order,
            'reversed_steps':reverse,'four_item_mixed_control':mixed,
            'known_tie':str(signs[4]),'production_control_6':'Product checked; full-order counts derived from symmetry. The strict scorer was bypassed.',
            'production_control_7':'The scorer received two equal values on each key.'}


def six_regular(pilot, sources):
    n = 99
    def d(i,j):
        return (j%n)*n+i%n
    knots = [[d(i,j),d(i+1,j),d(i,j+1)] for i in range(n) for j in range(n)]
    knots.extend([d(i+1,j),d(i,j+1),d(i+1,j+1)] for i in range(n) for j in range(n))
    return given_control(knots,sources[:1] if pilot else sources,32,lambda r:6*r*r+6*r+1)


def fixed_three(pilot):
    growth = Growth([[0,1,2]],'L8')
    rounds = 8 if pilot else 65
    births = [growth.step() for _ in range(rounds)]
    assert births == [comb(t+2,2) for t in range(1,rounds+1)]
    H = sizes(holder_neighbors(growth.places),0,rounds)
    assert H == [comb(r+3,3) for r in range(rounds+1)]
    return {'rounds':rounds,'births':births,'history':H}


def comb_check(stars,pilot):
    adj = holder_neighbors(stars)
    sources = list(range(64)) + [127+64*i for i in range(64)] + [95+64*i for i in range(64)]
    ns = [sources[0],sources[64]] if pilot else sources
    H = [sizes(adj,u,63) for u in ns]
    assert H[0] == [comb(r+2,2) for r in range(64)]
    assert all(h == [r+1 for r in range(64)] for u,h in zip(ns,H) if u in sources[64:128])
    test = gate_candidates(H,63)
    assert test==[]
    return {'knots':len(stars),'sources':len(ns),'common_exponent_and_starting_step':test}


def bare_rings(named,pilot):
    tab = {}
    for n in (5,7,9,11,15,21,33):
        g = Growth(named[f'Ring({n},2)'],'L0')
        for _ in range(3*n):
            assert g.step()==n
        adj = holder_neighbors(g.places)
        baseline = [2*r*r+2*r+1 if r<=(n-1)//2 else 0 for r in range(3*n+1)]
        for r in range((n-1)//2+1,len(baseline)):
            baseline[r] = baseline[r-1]+(n+1 if r<=n-1 else n)
        assert all(sizes(adj,u,3*n)==baseline for u in range(1 if pilot else n))
        made = [u for u,t in enumerate(g.birth_rounds) if n<=t<=2*n]
        if pilot:
            made = [made[0],made[-1]]
        frozen = repaired = 0
        first = None
        for u in made:
            t = g.birth_rounds[u]
            ell = 3*n-t
            H = sizes(adj,u,ell)
            expected = [2*r*r+2*r+1 if r<n else n*(2*r+1) for r in range(ell+1)]
            corrected = [old if r<=t else n*(t+r+1) for r,old in enumerate(expected)]
            frozen += H==expected
            repaired += H==corrected
            if H!=expected and first is None:
                r = next(r for r,(a,b) in enumerate(zip(H,expected)) if a!=b)
                first = {'born_in_round':t,'first_different_step':r,'observed':H[r],'frozen':expected[r]}
        assert repaired==len(made) and frozen < repaired
        tab[n] = {'rounds':g.round,'start_sources':1 if pilot else n,'made_sources':len(made),
                  'frozen_formula_passes':frozen,'amended_formula_passes':repaired,'one_counterexample':first}
        early = sizes(adj,n,2)[2]
        tab[n]['first_round_birth_at_two_steps'] = {'observed':early,'n_times_t_plus_r_plus_one':n*4}
        assert early != n*4
    return tab


def ring_33_disclosure(named,pilot):
    n = 33
    wanted = {}
    with gzip.open(RAW/'run2.jsonl.gz','rt') as stream:
        for line in stream:
            rec = json.loads(line)
            if rec['start']!=f'Ring({n},2)' or rec['law']!='L0' or rec['kind'] not in ('named','bare ring'):
                continue
            for name in ('at_T','at_2T'):
                cut = rec[name]
                sources = cut['classes']['b']+cut['classes']['c']
                wanted[cut['round']] = {u:cut['H'][str(u)][:33] for u in sources}
    g = Growth(named['Ring(33,2)'],'L0')
    report = {}
    for horizon,samples in sorted(wanted.items()):
        while g.round < horizon:
            assert g.step()==n
        adj = holder_neighbors(g.places)
        bad = 0
        for u,saved in samples.items():
            # The supplied sample identifies the source. Each of the n knots born in its round
            # has the same count by the cyclic renaming, independently of birth numbering.
            h = sizes(adj,u,32)
            assert h == saved
            ratios = [Fraction(h[r],r*r) for r in range(4,33)]
            bad += max(ratios)>2*min(ratios)
        report[horizon] = {'made_sources':len(samples),'fail_factor_two_on_4_to_32':bad}
        if pilot:
            break
    return report


def main(pilot):
    frozen = json.loads((INPUT/'named_starts.json').read_text())
    saved = json.loads((RAW/'run0_controls.json').read_text())['controls']
    controls = frozen['controls']
    ring = given_control(controls['R_400'],list(range(1 if pilot else 400)),64,lambda r:2*r+1)
    ring['exponents_on_first_eightfold_range'] = sorted({j for j,_ in gate_candidates([[2*r+1 for r in range(65)]],64)})
    weave = six_regular(pilot,saved['W_99']['sources'])
    weave['exponents_on_first_eightfold_range'] = sorted({j for j,_ in gate_candidates([[6*r*r+6*r+1 for r in range(33)]],32)})
    assert ring['exponents_on_first_eightfold_range']==[1] and weave['exponents_on_first_eightfold_range']==[2]
    order = tree_checks(controls['T_12'])
    official = saved['order_controls']['comparisons_over_every_pair_of_leaf_pairs']
    assert order['ordered_concordant_discordant_tied'] == [official[k] for k in ('concordant','discordant','tied')]
    bare = bare_rings(frozen['named_starts'],pilot)
    if not pilot:
        for n,row in bare.items():
            rec = saved['bare_rings'][str(n)]
            assert row['made_sources']==rec['made_checked'] and row['frozen_formula_passes']==rec['made_registered_whole_range']
            assert row['amended_formula_passes']==rec['made_registered_then_n(t+r+1)_beyond_t']
    return {'ring_of_400':ring,'branching_and_leaf_order':order,'six_regular':weave,
            'fixed_three':fixed_three(pilot),'comb':comb_check(controls['comb_64_64'],pilot),
            'bare_rings':bare,'ring_33_disclosed_counts':ring_33_disclosure(frozen['named_starts'],pilot)}


if __name__=='__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot',action='store_true')
    args = parser.parse_args()
    began = monotonic()
    result = main(args.pilot)
    if not args.pilot:
        (HERE/'lemma_controls.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'seconds':round(monotonic()-began,3),'six_regular':result['six_regular'],
                      'max_ring_sources':result['bare_rings'][33]['made_sources']}))
