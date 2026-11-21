"""Independent bounded reconstruction of B250 from the original incidences.

The production compiler uses one column per physical flip. This check instead
solves on coordinates of the space of allowed translations, then constructs
integer matrices and separate physical recorder controls. The archive is read
only in the comparison at the end. Run with the repository's .venv Python.
"""
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
from pathlib import Path
import argparse
import json
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SIX = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8))
SIDES_SIX = ((0, 1, 2), (3, 4, 5))


def cube():
    meetings = [(v, v ^ (1 << k)) for v in range(8) for k in range(3) if v < v ^ (1 << k)]
    return tuple(tuple(i for i, ends in enumerate(meetings) if v in ends) for v in range(8))


SIDES_EIGHT = ((0, 3, 5, 6), (1, 2, 4, 7))


def bit(x, k):
    return (x >> k) & 1


def xor(values):
    answer = 0
    for x in values:
        answer ^= x
    return answer


def reduce_row(pivots, row):
    for k in sorted(pivots, reverse=True):
        if bit(row, k):
            row ^= pivots[k]
    return row


def cycle_coordinates(holders):
    """Give each named incidence its coordinate in the homogeneous words."""
    n = max(max(h) for h in holders) + 1
    checks = tuple(sum(1 << e for e in h) for h in holders)
    words = [w for w in range(1 << n) if all((w & c).bit_count() % 2 == 0 for c in checks)]
    pivots = {}
    generators = []
    for w in words:
        row = reduce_row(pivots, w)
        if row:
            pivots[row.bit_length() - 1] = row
            generators.append(w)
    assert len(words) == 2 ** len(generators)
    coords = [tuple(i for i, g in enumerate(generators) if bit(g, e)) for e in range(n)]
    return words, coords, len(generators)


def solve_cycle_device(holders, odd, reversal=None):
    words, coords, rank = cycle_coordinates(holders)
    n = len(coords)
    variables = rank**2 + n
    constant = 1 << variables
    physical = [[sum(1 << (rank*i+j) for i in left for j in right)
                 for right in coords] for left in coords]
    signs = [1 << (rank**2 + i) for i in range(n)]
    eq = [physical[e][e] for e in range(n)]
    for h, held in enumerate(holders):
        eq.extend(physical[e][f] ^ physical[f][e] for e, f in combinations(held, 2))
        sign = int(h == odd) ^ int(reversal is not None and reversal[0] == h and reversal[1] in held)
        eq.append(xor(signs[e] for e in held) ^ xor(physical[e][f] for e, f in combinations(sorted(held), 2)) ^ (constant if sign else 0))

    pivots = {}
    def impose(equation):
        """With the high bit reserved for the constant, try to impose one equation."""
        row = reduce_row(pivots, equation)
        lhs = row & (constant-1)
        if not lhs:
            return not bool(row & constant)
        pivots[lhs.bit_length()-1] = row
        return True
    if not all(impose(row) for row in eq):
        return None
    def least_value(row):
        if impose(row):
            return 0
        assert impose(row ^ constant)
        return 1
    masks = [sum(least_value(row) << f for f, row in enumerate(column)) for column in physical]
    phases = [least_value(row) for row in signs]
    return words, masks, phases


def word_at(held, assignment):
    return ''.join(str(bit(assignment, e)) for e in held)


def integer_projectors(holders, device, reversed_occurrence=None):
    words, masks, signs = device
    size = len(words)
    ix = {w: i for i, w in enumerate(words)}
    identity = np.eye(size, dtype=np.int64)
    observables = []
    for e, (mask, sign) in enumerate(zip(masks, signs, strict=True)):
        matrix = np.zeros_like(identity)
        for w in words:
            matrix[ix[w ^ mask], ix[w]] = (-1) ** (bit(w,e) ^ sign)
        assert np.array_equal(matrix.T, matrix) and np.array_equal(matrix @ matrix, identity)
        observables.append(matrix)
    complete = {}
    for h, held in enumerate(holders):
        for e, f in combinations(held, 2):
            assert np.array_equal(observables[e] @ observables[f], observables[f] @ observables[e])
        for triple in product(range(2), repeat=3):
            out = identity
            for value, e in zip(triple, held, strict=True):
                s = (-1) ** (value ^ int((h,e) == reversed_occurrence))
                out = out @ (identity + s * observables[e])
            assert np.array_equal(out @ out, 8*out)
            complete[h, ''.join(map(str,triple))] = out
        assert np.array_equal(sum(complete[h, out] for out in WORDS), 8*identity)
    return observables, complete


WORDS = tuple(''.join(map(str,p)) for p in product(range(2),repeat=3))


def fresh_tables(sides, operators, dimension, mode='coherent'):
    tables = {}
    for a,b in product(*sides):
        cell = []
        for left,right in product(WORDS,repeat=2):
            p,q = operators[a,left],operators[b,right]
            if mode == 'coherent':
                v = Fraction(int(np.sum(p*q)), 64*dimension)
            elif mode == 'diagonal':
                v = Fraction(int(np.sum(p.diagonal()*q.diagonal())), 64*dimension)
            else:
                v = Fraction(int(np.trace(p))*int(np.trace(q)), 64*dimension**2)
            cell.append(v)
        assert sum(cell) == 1
        tables[a,b] = cell
    return tables


def success(holders, odd, tables):
    wins = []
    for (a,b),cell in tables.items():
        common = set(holders[a]) & set(holders[b])
        prob = sum(v for (x,y),v in zip(product(WORDS, repeat=2),cell,strict=True)
                   if x.count('1')%2 == (a==odd) and y.count('1')%2 == (b==odd)
                   and all(x[holders[a].index(e)] == y[holders[b].index(e)] for e in common))
        wins.append(prob)
    return sum(wins)/len(wins)


def held_reader_sweep(holders, odd, sides, observables, dimension):
    """Discard earlier local outcomes by their exact non-selective channels.

    Stable repeated remote measurement can be performed once. The correlation
    of the remote sign with the later local sign vanishes if an earlier local
    joint measurement dephases that observable.
    """
    by_orientation = {}
    for role in (0,1):
        for backward in (False,True):
            order = tuple(reversed(sides[role])) if backward else sides[role]
            mismatches = Counter()
            prior = []
            for h in order:
                for k in sides[1-role]:
                    for e in set(holders[h]) & set(holders[k]):
                        mat = observables[e].copy()
                        for f in reversed(prior):
                            rotated = observables[f] @ mat @ observables[f]
                            assert np.all((mat+rotated) % 2 == 0)
                            mat = (mat+rotated)//2
                        corr = Fraction(int(np.trace(mat @ observables[e])), dimension)
                        mismatches[k] += (1-corr)/2
                prior.extend(holders[h])
            by_orientation[role,backward] = dict(mismatches)
    return by_orientation


def tagged_tables(holders, sides, observed, dimension, tag_left, tag_right):
    """Read the first slot after an orthogonal tag in the two controlled arms.

    Given a reported outcome, the tagged first effect is I/2. Tracing that
    tag removes precisely the first restriction; the later factors commute.
    """
    def eff(h,w,tag):
        if not tag:
            return observed[h,w]
        flipped = str(1-int(w[0]))+w[1:]
        other = observed[h,flipped]
        total = observed[h,w] + other
        assert np.all(total % 2 == 0)
        return total // 2
    tables={}
    for a,b in product(*sides):
        tables[a,b]=[Fraction(int(np.sum(eff(a,x,tag_left)*eff(b,y,tag_right))),64*dimension)
                     for x,y in product(WORDS,repeat=2)]
        assert sum(tables[a,b])==1
    return tables


def local_controls(holders):
    n = max(max(h) for h in holders)+1
    weights = {}
    for name in ('even','nae'):
        allowed = [w for w in range(1<<n) if all(
            (word_at(h,w).count('1')%2==0 if name=='even' else len(set(word_at(h,w)))>1) for h in holders)]
        weights[name]=(len(allowed), len(allowed) if name=='even' else 1<<n)
    return weights


def literal_held_sweep(holders, sides, odd):
    """Exact projection of an Alice sweep when Bob holds one fixed answer.

    The holders on a side have disjoint marks. Alice draws a uniform triple
    at each turn, restricted only by the fixed Bob triple where they meet.
    Every permitted Alice transcript has the same number of extensions.
    """
    results = {}
    for observer in (0, 1):
        active, fixed = sides[observer], sides[1-observer]
        all_words = [w for w in range(1 << (1+max(max(h) for h in holders)))
                     if all(word_at(holders[h], w).count('1') % 2 == (h == odd) for h in active)]
        supports = {k: {w for w in all_words if word_at(holders[k], w).count('1') % 2 == (k == odd)}
                    for k in fixed}
        sizes = {len(s) for s in supports.values()}
        assert len(sizes) == 1
        size, = sizes
        distances = {Fraction(len(supports[j] - supports[k]), size) for j,k in combinations(fixed, 2)}
        assert distances == {Fraction(1,2)}
        results[observer] = (len(all_words), size, '1/2')
    return results


def physical_control():
    family = ROOT/'experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'
    sys.path.insert(0,str(family))
    import naelib
    holds = ((0,1,2),(0,3,4))
    observations = {}
    for name in ('parity', 'nae'):
        maker = naelib.parity_rule if name=='parity' else naelib.nae_rule
        outputs = {}
        examples = [('one keeper', ((0,1,2),)), ('two overlapping holders', holds),
                    ('funded two-parent birth', ((0,1,2),(1,3,4),(2,5,6)))]
        for lawlabel,rows in examples:
            traces=set()
            lawful_count=0
            for w in range(1 << (max(max(h) for h in rows)+1)):
                values=[word_at(h,w) for h in rows]
                lawful=all(word.count('1')%2==0 if name=='parity' else len(set(word))>1 for word in values)
                if not lawful:
                    continue
                lawful_count += 1
                stage=naelib.J.S.from_junctions([list(h) for h in rows])
                orig=len(stage.bits_of)
                original_owners={v:tuple(i for i,h in enumerate(rows) if v in h)
                                 for h in rows for v in h}
                stage.step(maker(naelib.F.fewest), None)
                trace=[]
                for j in range(orig,len(stage.bits_of)):
                    inputs=[v for v in stage.bits_of[j] if v in original_owners]
                    assert all(len(original_owners[v]) == 1 for v in inputs)
                    parents=tuple(sorted(original_owners[v][0] for v in inputs))
                    assert len(parents)==stage.parents[j]
                    trace.append((parents,tuple(stage.bits_of[j]),stage.fresh[j]))
                traces.add(tuple(trace))
            assert len(traces)==1
            common=next(iter(traces))
            if lawlabel=='funded two-parent birth':
                assert any(parents==(1,2) for parents,_,_ in common)
            outputs[lawlabel]=(lawful_count,len(common))
        observations[name]=outputs
    relations = {'parity': lambda w:w.count('1')%2==0, 'nae':lambda w:len(set(w))>1}
    for name,allowed in relations.items():
        forbidden=[w for w in WORDS if not allowed(w)]
        clauses=[' '.join(('~' if digit=='1' else '')+var for digit,var in zip(w,'xyz',strict=True)) for w in forbidden]
        import os
        result=subprocess.run([sys.executable,'-B','-m','knotlab','check','--cnf',';'.join(clauses),
                               '--loops','x','y','--contact','z','--json'],env={**os.environ,'PYTHONPATH':str(ROOT/'tools')},
                              check=True,capture_output=True,text=True)
        assert json.loads(result.stdout)['is_knot']
        assert all(allowed(w) for w in ('110','101','011'))
    return observations


def compare_archive(derived):
    p=next((ROOT/'artifacts/FOUR-READINGS-20261120-001A').glob('*/games.json'))
    published=json.loads(p.read_bytes())
    assert published['order']==list(WORDS)
    for i,(key,tables) in enumerate(zip(('six','cube_all_pairs'),derived,strict=True)):
        differences={}
        for row in published[key]:
            inputs=tuple(row['inputs'])
            theirs=[Fraction(num,row['denominator']) for num in row['numerator']]
            diff=sum(x!=y for x,y in zip(tables[inputs],theirs,strict=True))
            if diff:differences[inputs]=diff
        print(key,'entry differences indexed by setting pair',differences)
        if i==0:assert not differences
        else:assert differences == {(0,1):16}


def check_known_classification(outcomes):
    """Apply the external classification only after the compiler has finished."""
    import networkx as nx
    for holders, strict in zip((SIX, cube()), outcomes, strict=True):
        pattern = nx.Graph()
        pattern.add_nodes_from(range(len(holders)))
        for mark in {e for h in holders for e in h}:
            a,b = (i for i,h in enumerate(holders) if mark in h)
            pattern.add_edge(a,b)
        planar, _ = nx.check_planarity(pattern)
        assert nx.is_connected(pattern)
        assert strict == (not planar)
        print('Independent known-classification check: holders',len(holders),'planar',planar,'strict accepted',strict)


def main():
    arg=argparse.ArgumentParser(description=__doc__)
    arg.add_argument('--compare-archive',action='store_true',help='compare only after deriving both predictions')
    args=arg.parse_args()
    results=[]
    strict_results=[]
    for name,holders,sides in [('six',SIX,SIDES_SIX),('eight',cube(),SIDES_EIGHT)]:
        odd=len(holders)-1
        original=solve_cycle_device(holders,odd)
        strict_results.append(original is not None)
        admitted=[(max(i for i,h in enumerate(holders) if e in h),e) for e in range(max(max(h) for h in holders)+1)]
        minimum=[None] if original is not None else [end for end in admitted if solve_cycle_device(holders,odd,end) is not None]
        assert minimum
        reversed_end=minimum[0]
        run=original or solve_cycle_device(holders,odd,reversed_end)
        data,flips,phase=run
        observables, projections=integer_projectors(holders,run,reversed_end)
        tables=fresh_tables(sides,projections,len(data)); results.append(tables)
        print(name, 'strict accepted',original is not None,'source dimension',len(data),'minimum calibrations',minimum)
        print('compiled changes',flips,'signs',phase)
        for mode in ('coherent','diagonal','independent'):
            law=fresh_tables(sides,projections,len(data),mode=mode)
            print(mode, 'mean game success',str(success(holders,odd,law)))
        print('branch tag, left/right/both win shares',*[str(success(holders,odd,tagged_tables(holders,sides,projections,len(data),a,b))) for a,b in [(1,0),(0,1),(1,1)]])
        if original:
            print('fixed opponent sweep expected mismatches',held_reader_sweep(holders,odd,sides,observables,len(data)))
        print('literal shared decision: own sweep possibilities, support at fixed opposite question, pairwise TV',
              literal_held_sweep(holders,sides,odd))
        print('lawful controls (accepted, preherald words)',local_controls(holders))
    print('Two-holder controls',local_controls(((0,1,2),(0,3,4))))
    print('Ordinary birth counts independent of every admissible preword',physical_control())
    if args.compare_archive:
        compare_archive(results)
        check_known_classification(strict_results)


if __name__=='__main__':
    main()
