"""Compress whole context effects, verify exact readouts, and exhibit different instruments."""
from fractions import Fraction as F
from itertools import combinations, product
import json
import numpy as np
from study_io import allowed, family, write


def integer_matrix(question, dimension):
    flip,read,sign=question
    words=np.arange(dimension)
    coeff=np.array([sign*(-1)**int(x&read).bit_count() for x in words])
    op=np.zeros((dimension,dimension),dtype=np.int64);op[words ^ flip,words]=coeff
    assert np.array_equal(op,op.T)
    return op


def context(words, dimension, questions, answer_order, archive):
    n=len(words);size=len(questions); scale=1<<size
    ident=np.eye(dimension,dtype=np.int64);ops=[integer_matrix(q,dimension) for q in questions]
    assert all(np.array_equal(x @ y,y @ x) for x,y in combinations(ops,2))
    projected={():ident}
    for op in ops:
        # Each full-space signed permutation applies by reindexing rows with their coefficients.
        perm=np.argmax(abs(op),axis=1); signs=op[np.arange(dimension),perm].reshape((-1,1))
        projected={old+(a,):row+a*signs*row[perm,:] for old,row in projected.items() for a in (1,-1)}
    mat=[projected[v] for v in answer_order]; sub=[v[np.ix_(words,words)] for v in mat]
    assert np.array_equal(sum(sub),scale*np.eye(n,dtype=np.int64))
    margins=[(np.eye(n,dtype=np.int64)+op[np.ix_(words,words)]) for op in ops]
    pairs=[]
    for j,k in combinations(range(size),2):
        x,y=margins[j],margins[k];c=x @ y - y @ x
        if np.any(c):
            u,v=map(int,np.argwhere(c)[0]);pairs.append([j,k,words[u],words[v],int(c[u,v])])
    numer=[];unsharp=0
    for full,b in zip(mat,sub):
        vector=full[:,words].sum(axis=1)
        count=int(b.sum()); assert int(vector @ vector)==scale*count and count>=0
        numer.append(count)
        assert np.array_equal(b,b.T)
        unsharp+=not np.array_equal(b @ b,scale*b)
    den=n*scale
    assert all(F(x,den)==F(y,archive['denominator']) for x,y in zip(numer,archive['numerators'],strict=True))
    return dict(denominator=den,numerators=numer,nonprojective_effects=unsharp,
        noncommuting_individual_plus_effects_times_four=pairs,complete=True)


def local_witnesses(stars,law,marks):
    words=allowed(stars,law);width=1+max(map(max,stars)); masks=[sum(1<<b for b in row) for row in marks]
    reports=[]
    for mask in masks:
        local=[b for b in range(width) if mask>>b&1]; options=range(1<<len(local));witness=[]
        def lift(x):return sum(((x>>i)&1)<<b for i,b in enumerate(local))
        for a,b in product(options,repeat=2):
            if a==b:continue
            for w in sorted(words):
                if w&mask!=lift(a):continue
                y=w^lift(a)^lift(b)
                neighborhood=[s for s in words if s&~mask==w&~mask]
                # To force each off-diagonal matrix element to vanish on the actual positive preparation,
                # either the entire conditional local input is unique, or all other terms are absent.
                if y not in words and len(neighborhood)==1:
                    witness.append([a,b,w,y]);break
        reports.append(dict(marks=local,unique_input_forbids=witness,off_diagonal_total=len(options)*(len(options)-1)))
    return reports


def run():
    out={};numbers={}
    split=family('READS-HOLDERS-SOURCES-20261120-001A','artifacts');source=json.loads((split/'alternate_law.json').read_text())
    tri=json.loads((family('THREE-READERS-AND-GROWTH-20261120-001A','artifacts')/'lead.json').read_text());
    for law in ('parity','nae'):
        knots=[[0,1,2],[3,4,5]];w=sorted(allowed(knots,law)); six=source[law]['2']['six'];table=[]
        for row in six['rows']:
            i,j=row['settings'];questions=six['alice'][i]+six['bob'][j]
            report=context(w,64,questions,list(product((1,-1),repeat=6)),row)
            table.append(dict(settings=[i,j],**report))
        out['six/'+law]=dict(rows=table,Bob_local=local_witnesses(knots,law,[[2,5]]))
        numbers['six/'+law]=[9,576,sum(r['nonprojective_effects'] for r in table),sum(bool(r['noncommuting_individual_plus_effects_times_four']) for r in table)]
        knots=[[0,1,2]];w=sorted(allowed(knots,law));table=[]
        for row in tri[law]['attachments']['0']['rows']:
            spec=row['settings'];questions=[(0,1<<i,1) if r else (1<<i,0,1) for i,r in enumerate(spec)]
            answer=[tuple((-1)**((j>>i)&1) for i in range(3)) for j in range(8)]
            table.append(dict(settings=spec,**context(w,8,questions,answer,row)))
        out['ternary/'+law]=dict(rows=table,single_reader=local_witnesses(knots,law,[[0],[1],[2]]))
        numbers['ternary/'+law]=[8,64,sum(r['nonprojective_effects'] for r in table),sum(bool(r['noncommuting_individual_plus_effects_times_four']) for r in table)]
    assert all(len(r['unique_input_forbids'])==r['off_diagonal_total'] for law in ('parity','nae') for r in out['ternary/'+law]['single_reader'])
    assert len(out['six/parity']['Bob_local'][0]['unique_input_forbids'])==12
    write('compressed_effects.json',dict(summary=numbers,columns=['settings','compared_entries','nonprojective_effects','settings_with_noncommuting_binary_marginals'],entries=out))
    return numbers
