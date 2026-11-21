"""Exact uniform and inherited readings of the four-place source at age two."""
from collections import Counter
from fractions import Fraction
from itertools import combinations
from math import lcm
import gzip
import json
import os
from pathlib import Path
import sys

os.environ["OPENBLAS_NUM_THREADS"] = "1"
os.environ["OMP_NUM_THREADS"] = "1"
import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
PRIOR = "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001C"
PRIOR_CODE = ROOT / "experiments" / PRIOR / (PRIOR+"-E001_wider_meetings")
PRIOR_DATA = ROOT / "artifacts" / PRIOR / PRIOR_CODE.name
sys.path.insert(0, str(PRIOR_CODE))
from census_stages import advance, end_of, width


def words(rows):
    n = width(rows)
    bitwords = np.arange(1 << n, dtype=np.int64)
    legal = np.ones(len(bitwords), bool)
    for row in rows:
        mask = sum(1 << bit for bit in row)
        legal &= ((bitwords & mask) != 0) & ((bitwords & mask) != mask)
    bitwords = bitwords[legal]
    return 1 - 2*((bitwords[:, None] >> np.arange(n)) & 1)


def conditional_table(old_signs, latest, weights, mode):
    """Accumulate pair moments, integrating every final child exactly."""
    nold = old_signs.shape[1]
    roles = [(tuple(i for i in row if i < nold), tuple(i for i in row if i >= nold)) for row in latest]
    final_width = nold + sum(len(fresh) for _, fresh in roles)
    scale = lcm(*(2**len(fresh)-1 for _, fresh in roles))
    raw = np.zeros((len(old_signs), final_width), dtype=np.int64)
    raw[:, :nold] = scale*old_signs
    costs = np.ones(len(old_signs), dtype=np.int64)
    corrections = []
    for inputs, fresh in roles:
        a = 1 << len(fresh)
        mono = np.all(old_signs[:, inputs] == old_signs[:, inputs[0], None], axis=1)
        costs *= a - mono
        mean = -old_signs[:, inputs[0]]*mono*(scale//(a-1))
        for i in fresh:
            raw[:, i] = mean
        true_pair = -(scale*scale//(a-1))*mono
        corrections.append((fresh, true_pair))
    if mode == 'uniform':
        weights = costs
    moment = raw.T @ (weights[:, None]*raw)
    total = int(weights.sum())
    den = total*scale*scale
    for fresh, true_pair in corrections:
        val = int((weights*true_pair).sum())
        for i,j in combinations(fresh,2):
            moment[i,j] = moment[j,i] = val
    for i in range(final_width):
        moment[i,i] = den
    corr = [[Fraction(int(v),den) for v in row] for row in moment]
    return corr, Counter(map(int,costs)), total


def reading(c):
    n=len(c)
    return [(1-c[i][j])/2 for i,j in combinations(range(n),2)]


def report_constraints(c):
    pairs=reading(c); triples=[]; atom_den=1
    for i,j,k in combinations(range(len(c)),3):
        mono=(1+c[i][j]+c[i][k]+c[j][k])/4
        triples.append(mono)
        for b in (-1,1):
            for d in (-1,1):
                atom=(1+b*c[i][j]+d*c[i][k]+b*d*c[j][k])/8
                atom_den=lcm(atom_den,atom.denominator)
    role=[]
    for i,row in enumerate(c):
        v=min(row[j] for j in range(len(c)) if j!=i)
        other=[j for j,u in enumerate(row) if i!=j and u==v]
        triple_test=None
        if len(other)==3:
            triple_test=(1+sum(c[x][y] for x,y in combinations(other,2)))/4 + v
        role.append(dict(name=i,lowest=str(v),partners=other,implied_four_place_residual=str(triple_test) if triple_test is not None else None))
    return dict(fractions=list(map(str, pairs)),histogram=dict(sorted(Counter(map(str,pairs)).items())),minimum_triple_mono=str(min(triples)),maximum_triple_mono=str(max(triples)),forced_ternaries=sum(v==0 for v in triples),roles=role,
                lcm_individual_triple_word_denominator=atom_den,
                lcm_pair_denominator=lcm(*(x.denominator for x in pairs)),lcm_triple_denominator=lcm(*(x.denominator for x in triples)))


def roster(rows,law):
    status,nxt,births=advance(rows,law)
    end,loose=end_of(rows)
    return dict(status=status, live_supports=[[rows[h],sorted(names)] for h,names in sorted(loose.items())], parent_supports_and_fresh=[[sorted(rows[h] for h in p),f] for p,f in births], new_rows=nxt[len(rows):])


def target():
    founder=((0,1,2,3),)
    _,one,b1=advance(founder,'nae')
    _,two,b2=advance(one,'nae')
    signs=words(one)
    # Unary first births have a constant seven completions per old word.
    assert all(len(p)==1 and f==3 for p,f in b1)
    weights=np.ones(len(signs), dtype=np.int64)
    c1,costs,total=conditional_table(signs,two[len(one):],weights,'uniform')
    c2,costs2,inherited=conditional_table(signs,two[len(one):],weights,'inherited')
    assert costs==costs2
    with gzip.open(PRIOR_DATA/'census_stages.json.gz','rt') as f:
        found=json.load(f)['nae']
    idx=next(i for i,d in enumerate(found) if d['source_rows']==[[0,1,2,3]])
    with gzip.open(PRIOR_DATA/'census_rate_tables.json.gz','rt') as f:
        old=next(d for d in json.load(f)['nae']['records'] if d['source_index']==idx and d['age']==2)
    uniform=reading(c1); inherited_rates=reading(c2)
    assert total==old['allowed_states'] and uniform==[Fraction(v,total) for v in old['disagreement_counts']]
    deltas=[abs(u-v) for u,v in zip(uniform,inherited_rates,strict=True)]
    max_change=max(deltas)
    data=dict(source=founder,first_holders=one,observed_holders=two,old_states=len(signs),stage_states=total,
              conditional_extension_counts=dict(sorted(costs.items())),uniform=report_constraints(c1),inherited=report_constraints(c2),
              differing_entries=sum(x>0 for x in deltas),total_entries=len(deltas),max_difference=str(max_change),
              max_difference_pairs=[p for p,d in zip(combinations(range(len(c1)),2),deltas,strict=True) if d==max_change],
              old_marginal_under_inherited_equals_uniform_first=all(c2[i][j]==Fraction(int(signs[:,i]@signs[:,j]),len(signs)) for i,j in combinations(range(len(signs[0])),2)),
              uniform_crosscheck='identical to all archived exact counts',physical_next=roster(two,'nae'))
    (OUTPUT/'target.json').write_text(json.dumps(data,indent=2)+'\n')
    return data

if __name__=='__main__':
    d=target()
    print(d['stage_states'],d['differing_entries'],d['max_difference'],d['conditional_extension_counts'])
    for name in ('uniform','inherited'):
        t=d[name]
        print(name,t['lcm_pair_denominator'],t['lcm_triple_denominator'],t['minimum_triple_mono'])
        for ix in (0,4,16):
            print(t['roles'][ix])
