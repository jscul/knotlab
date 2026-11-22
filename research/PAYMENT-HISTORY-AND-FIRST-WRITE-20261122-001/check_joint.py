"""Condition each whole static cut on its complete old word and compare all fresh fibres.

The paid rosters used here are the archived quiet three-loose founder's three
cuts. The primary replay reconstructs each from the actual growth planner.
"""
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, permutations, product
import json
from pathlib import Path

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
spec = spec_from_file_location("exact_star_relation", HERE.parent / "WRITTEN-BIT-AND-JOIN-VETO-20261122-001" / "verify.py")
relations = module_from_spec(spec)
spec.loader.exec_module(relations)
CONFIG = (("parity","zero",(0,0,0)), ("nae","lex",(1,1,0)), ("nae","opposite",(1,1,0)))


def signed(names, word):
    return [(i+1) * (1 if bit else -1) for i,bit in zip(names,word,strict=True)]


def clauses(stars, law):
    return [[(row[abs(v)-1]+1) * (1 if v>0 else -1) for v in bad]
            for row in stars for bad in relations.local_cnf(len(row),law)]


def words(width):
    return tuple(product((0,1),repeat=width))


def inspect(old, ref, paid, fresh, law, extension):
    all_paid = sum(paid, ())
    all_fresh = sum(fresh, ())
    counts = Counter(d for row in old for d in row)
    assert Counter(all_paid) == Counter(d for d,count in counts.items() if count==1)
    assert len(set(all_fresh)) == len(all_fresh) and not set(all_fresh).intersection(counts)
    assert all_fresh == tuple(range(len(ref), len(ref)+len(all_fresh)))
    new = old + tuple(p + f for p,f in zip(paid,fresh,strict=True))
    relations.check_board(new,law)
    permitted, transported = [], []
    for p,f in zip(paid,fresh,strict=True):
        inherited = tuple(ref[d] for d in p)
        allowed = tuple(w for w in words(len(f)) if relations.lawful(inherited+w,law))
        if law=="parity":
            candidate=(0,)*len(f)
        elif extension=="opposite" and len(set(inherited))==1:
            candidate=(1-inherited[0],)*len(f)
        else:
            candidate=min(allowed)
        assert candidate in allowed
        permitted.append(allowed)
        transported.append(candidate)
    ref_fresh = sum(transported, ())
    prefix = signed(range(len(ref)),ref)
    joint = set()
    with Minisat22(bootstrap_with=clauses(new,law)) as solver:
        for w in words(len(all_fresh)):
            if solver.solve(assumptions=prefix+signed(all_fresh,w)):
                joint.add(w)
    # Equality with the full product establishes every focal fibre even when
    # the other newborns' legal values have been fixed independently.
    assert joint == {sum(tuple(bank),()) for bank in product(*permitted)}
    assert ref_fresh in joint
    return new,ref+ref_fresh,dict(paid=paid,fresh=fresh,
        inherited=[tuple(ref[d] for d in p) for p in paid],
        fresh_reference=transported,allowed_banks=permitted,joint_support_size=len(joint))


def parity_closure(old, paid):
    with Minisat22(bootstrap_with=clauses(old,"parity")) as solver:
        allowed = [w for w in words(len(paid)) if solver.solve(assumptions=signed(paid,w))]
    assert allowed and all(sum(w)%2==0 for w in allowed)
    return allowed


def replay(law, extension, initial):
    source=((0,1,2),)
    relations.check_board(source,law)
    banks1=((3,4),(5,6),(7,8))
    pairs=tuple(combinations(range(3),2))
    counts=[Counter(), Counter(), Counter()]
    example=None
    for order in permutations(range(3)):
        named=tuple((d,) for d in order)
        old1,ref1,one=inspect(source,initial,named,banks1,law,extension)
        counts[0][one["joint_support_size"]]+=1
        for allocated in product(*(permutations(bank) for bank in banks1)):
            slots=[iter(bank) for bank in allocated]
            paid=tuple(tuple(next(slots[i]) for i in pair) for pair in pairs)
            owners=[{i for i,row in enumerate(old1) if set(p).intersection(row)} for p in paid]
            assert all(a&b for a,b in combinations(owners,2))
            assert all(set(a).isdisjoint(b) for a,b in combinations(paid,2))
            old2,ref2,two=inspect(old1,ref1,paid,((9,),(10,),(11,)),law,extension)
            counts[1][two["joint_support_size"]]+=1
            terminal_paid=((9,10,11),)
            last=((),) if law=="parity" else ((12,),)
            _,_,three=inspect(old2,ref2,terminal_paid,last,law,extension)
            counts[2][three["joint_support_size"]]+=1
            more=parity_closure(old2,terminal_paid[0]) if law=="parity" else None
            if example is None:
                example={"first":one,"second":two,"third":three,"all_old_parity_words_projected_on_closing_paid_set":more}
    assert [sum(group.values()) for group in counts] == [6,48,48]
    return {"counts_by_joint_support_size":list(map(dict,counts)),"example":example}


if __name__=="__main__":
    cases={law+"-"+extension:replay(law,extension,initial) for law,extension,initial in CONFIG}
    out={"cases":cases,"method":"Full-board SAT with every old value and exact physical binding fixed; compare the full new truth table with the product of lawful local banks.",
         "projected_full_board_knot_supports":dict(relations.PROJECTIONS),"canonical_support_types":relations.KNOT_CHECKS}
    print(json.dumps(out,indent=2,sort_keys=True))

