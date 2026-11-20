"""Exact outcome tables, including all zero events, using independent integer Born traces."""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
import os
import subprocess
import sys

import networkx as nx
import numpy as np

from census import ROOT, save

WORDS = tuple(''.join(x) for x in product('01', repeat=3))
SIX = [[3*i+j for j in range(3)] for i in range(3)] + [[3*i+j for i in range(3)] for j in range(3)]


def state_word(x, star):
    return ''.join(str(x >> bit & 1) for bit in star)


def allowed(word, parity):
    return sum(map(int, word)) % 2 == parity


def ktest(words, width):
    k1 = len(words) < 1 << width
    k2 = all(len({w[:i] + w[i+1:] for w in words}) == 1 << (width-1) for i in range(width))
    return [k1, k2, bool(words)]


def canonical(stars, targets, support):
    clauses = []
    for star, sign in zip(stars, targets):
        for word in WORDS:
            if not allowed(word, sign):
                clauses.append(' '.join(('~' if val == '1' else '')+'x'+str(b) for b,val in zip(star,word)))
    names = ['x'+str(b) for b in support]
    cmd = [sys.executable, '-B', '-m', 'knotlab', 'check', '--cnf', ';'.join(clauses),
           '--contact', names[-1], '--loops', *names[:-1], '--json']
    env = dict(os.environ, PYTHONPATH=str(ROOT/'tools'))
    r = json.loads(subprocess.check_output(cmd, cwd=ROOT, env=env))
    return [r['binding'], r['loss_on_erasure'], r['coexistence']]


def parts():
    rowset = []
    for mask in range(64):
        ids = [u for u in range(6) if mask>>u & 1]
        stars = [SIX[u] for u in ids]
        signs = [int(u == 5) for u in ids]
        support = sorted(set().union(*map(set, stars))) if stars else []
        xs = [x for x in range(512) if all(allowed(state_word(x,s),d) for s,d in zip(stars,signs))]
        words = {state_word(x,support) for x in xs}
        gates = ktest(words,len(support))
        if support:
            assert gates == canonical(stars, signs, support)
        usages = []
        for u, star in enumerate(SIX):
            local = sorted({state_word(x,star) for x in xs})
            usages.append(dict(holder=u, imposed=u in ids, allowed=local, K123=ktest(local,3)))
        rowset.append(dict(retained=ids, active=support, ambient_models=len(xs), relation_models=len(words),
                           K123=gates, stars=usages))
    save('six_parts.json', rowset)
    return rowset


def tables(stars, first, second, odd, include_disjoint=True, synchronize=False, shared_bias=False):
    rows = []
    for u,v in product(first,second):
        a, b = stars[u], stars[v]
        shared = sorted(set(a)&set(b))
        if not shared and not include_disjoint or u == v and not synchronize:
            continue
        counts = []
        for x,y in product(WORDS,repeat=2):
            ok = allowed(x,u==odd) and allowed(y,v==odd) and all(x[a.index(h)]==y[b.index(h)] for h in shared)
            counts.append(int(ok) * (2 if shared_bias and shared and x[a.index(shared[0])]=='1' else 1))
        assert sum(counts)
        rows.append(dict(inputs=[u,v], shared=shared, numerator=counts, denominator=sum(counts)))
    return rows


def marginal(row, role):
    a = np.array(row['numerator'],dtype=int).reshape(8,8).sum(axis=1-role)
    return [Fraction(int(x),row['denominator']) for x in a]


def variation(rows):
    scores = []
    for role in range(2):
        vals = []
        for a,b in combinations(rows,2):
            if a['inputs'][role] == b['inputs'][role]:
                vals.append(sum(abs(x-y) for x,y in zip(marginal(a,role),marginal(b,role)))/2)
        scores.append(str(max(vals,default=Fraction(0))))
    return scores


def exact_born(rows):
    I=np.eye(2,dtype=np.int64)
    X=np.array([[0,1],[1,0]],dtype=np.int64)
    Z=np.diag([1,-1])
    YY=-np.kron(X@Z,X@Z)
    labels = [np.kron(X,I),np.kron(I,X),np.kron(X,X),np.kron(I,Z),np.kron(Z,I),
              np.kron(Z,Z),np.kron(X,Z),np.kron(Z,X),YY]
    I4=np.eye(4,dtype=np.int64)
    projectors = {}
    for u,s in enumerate(SIX):
        assert all(np.array_equal(labels[a]@labels[b],labels[b]@labels[a]) for a,b in combinations(s,2))
        assert np.array_equal(labels[s[0]]@labels[s[1]]@labels[s[2]],(-1 if u==5 else 1)*I4)
        for w in WORDS:
            mat=I4.copy()
            for h,ch in zip(s,w):
                mat=mat@(I4+(1-2*int(ch))*labels[h])
            assert np.array_equal(mat@mat,8*mat) and int(np.trace(mat)) in (0,8)
            projectors[u,w]=mat
    for row in rows:
        u,v=row['inputs']
        numerators = [int(np.trace(projectors[u,x].T @ projectors[v,y].T)) for x,y in product(WORDS,repeat=2)]
        assert [Fraction(x,4*8*8) for x in numerators] == [Fraction(x,row['denominator']) for x in row['numerator']]
        row['born_numerators_over_256']=numerators
    return labels


def classical(rows):
    scalar = []
    for state in range(512):
        won = [allowed(state_word(state,s),u==5) for u,s in enumerate(SIX)]
        scalar.append((sum(won),sum(won[u] and won[v] for u,v in product(range(3),range(3,6)))))
    choices=[[w for w in WORDS if allowed(w,u==5)] for u in range(6)]
    consistent=Counter()
    first_best = None
    for answers in product(*choices):
        good = sum(answers[u][SIX[u].index(h)] == answers[v][SIX[v].index(h)] for u,v,h in
                   ((u,v,next(iter(set(SIX[u])&set(SIX[v])))) for u,v in product(range(3),range(3,6))))
        consistent[good]+=1
        if good==8 and first_best is None: first_best=answers
    return dict(scalar_histograms={f'{a}_rules_{b}_pairs':c for (a,b),c in Counter(scalar).items()},
                scalar_best_rules=max(a for a,b in scalar),scalar_best_game=max(b for a,b in scalar),
                local_best=max(consistent), local_wins_histogram=consistent, local_eight_example=first_best)


def cube_game():
    ends=[(u,u^(1<<j)) for u in range(8) for j in range(3) if not(u>>j&1)]
    stars=[[h for h,p in enumerate(ends) if u in p] for u in range(8)]
    a=[u for u in range(8) if u.bit_count()%2==0]
    b=sorted(set(range(8))-set(a))
    return ends,stars,tables(stars,a,b,7)


def double_cover_control():
    ends=list(combinations(range(4),2))
    stars=[[i for i,p in enumerate(ends) if u in p] for u in range(4)]
    rows=tables(stars,range(4),range(4),3)
    sync=tables(stars,range(4),range(4),3,synchronize=True)
    variables=[(u,v) for u,v in product(range(4),repeat=2) if u!=v]
    a=[[variables.index((u, (ends[h][0]+ends[h][1])-u)) for h in stars[u]] for u in range(4)]
    b=[[variables.index(((ends[h][0]+ends[h][1])-u, u)) for h in stars[u]] for u in range(4)]
    solutions=[s for s in range(1<<12) if all(allowed(state_word(s,support),i%4==3) for i,support in enumerate(a+b))]
    for row in rows:
        u,v=row['inputs']
        freq=Counter((state_word(s,a[u]),state_word(s,b[v])) for s in solutions)
        assert [Fraction(freq[x,y],len(solutions)) for x,y in product(WORDS,repeat=2)] == [
               Fraction(c,row['denominator']) for c in row['numerator']]
    return dict(stars=stars, includes_equal=sync,distinct_only=rows,
                exact_local_hidden_states=solutions, hidden_variables=variables,
                TV_distinct=variation(rows), TV_with_equal=variation(sync))


def run_six():
    p=parts()
    six=tables(SIX,range(3),range(3,6),5)
    exact_born(six)
    biased=tables(SIX,range(3),range(3,6),5,shared_bias=True)
    classical_values=classical(six)
    print('six',classical_values,'bias',variation(biased))
    print('parts', Counter((len(r['retained']),tuple(r['K123']),r['ambient_models']) for r in p))
    return six,biased,classical_values


def run_comparison(six,biased,classical_values):
    ends,stars,cube=cube_game()
    k4=double_cover_control()
    fano=[s for s in combinations(range(1,8),3) if s[0]^s[1]^s[2]==0]
    def counts(stars,n):
        return sum(all(len(set(state_word(s,star)))>1 for star in stars) for s in range(1<<n))
    def degree_profile(stars):
        ds=Counter(x for s in stars for x in s)
        return sorted(ds.values())
    before = {i:degree_profile([s for j,s in enumerate(fano) if j!=i]) for i in range(7)}
    removed = {i:degree_profile([[v for v in s if v!=i] for s in fano]) for i in range(1,8)}
    markers = dict(fano=fano,fano_NAE_states=counts([[i-1 for i in s] for s in fano],7),
                   six_NAE_states=counts(SIX,9),Fano_minus_holder_degrees=before,
                   Fano_minus_distinction_degrees=removed,
                   Fano_remove_incident_rules=[s for s in fano if 1 not in s],
                   ring_transfer_controls=[dict(transfers=w,fixed=sum((i ^ (sum(w)%2))==i for i in (0,1)))
                                           for w in ([0,0,0],[0,0,1],[1,0,1])])
    d=dict(order=list(WORDS), six_sharing=SIX,six=six,six_TV=variation(six),biased_six=biased,
           biased_TV=variation(biased),classical=classical_values,cube_sharing=ends,
           cube_stars=stars,cube_all_pairs=cube,cube_TV=variation(cube),
           cube_promised_TV=variation([r for r in cube if r['shared']]),symmetric_four=k4,
           precedence='in every cell, the left output varies more slowly than the right output')
    save('games.json',d);save('marker_controls.json',markers)
    print('cube',len(cube),variation(cube),'K4 cover',len(k4['exact_local_hidden_states']),'six NAE',markers['six_NAE_states'])


if __name__=='__main__':
    run_comparison(*run_six())
