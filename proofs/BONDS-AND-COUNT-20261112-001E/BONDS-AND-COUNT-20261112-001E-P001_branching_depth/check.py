"""Direct finite controls for the endpoint and off-branch quantifiers of the depth proof."""
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys

ROOT = Path(__file__).resolve().parents[3]
TRIPLES = set(product((0, 1), repeat=3))


def transfer(relation, states):
    return {out for inc,out in relation if inc in states}


def local_ok(a, c, y):
    return len({a, c, y}) == 2


def verify_boundary_memory():
    # Build one step by laws and actual port identity, without the stated T formula.
    relation = set()
    for (a,b,c), (x,y) in product(TRIPLES,product((0,1),repeat=2)):
        if local_ok(a, c, y):
            relation.add(((a,b,c),(c,a,x)))
    for start in TRIPLES:
        state = {start}
        for expected in (2,4,8):
            state = transfer(relation,state)
            assert len(state) == expected
    # Independent explicit composition for arbitrary endpoint triples.
    bridges = sum(
        any((left, mid1) in relation and (mid1, mid2) in relation and (mid2, right) in relation
            for mid1,mid2 in product(TRIPLES,repeat=2))
        for left,right in product(TRIPLES,repeat=2)
    )
    assert bridges == 64
    return bridges


def separator_control():
    # An observed value in the immediate side child D(y,x,b) couples its y to the
    # original b. First, enumerate the actual projection over this child's w and
    # the incoming/outgoing ports, including all values of root y.
    restricted = {bit: set() for bit in (0,1)}
    for (a,b,c),(x,y,w) in product(TRIPLES, TRIPLES):
        if local_ok(a,c,y) and local_ok(y,b,w):
            restricted[w].add(((a,b,c),(c,a,x)))
    empty = {(inc,out) for rel in restricted.values() for inc,out in rel}
    count = 0
    for w,z,initial in product((0,1),(0,1),TRIPLES):
        front = transfer(restricted[w],{initial})
        if not front:
            continue
        for _ in range(3):
            front=transfer(empty,front)
        assert front == TRIPLES
        assert transfer(restricted[z],front) == transfer(restricted[z],TRIPLES)
        count += 1
    return count


def chain_projection(s):
    accepted = set()
    for carry in product((0,1), repeat=s+1):
        options = [(0,1) if carry[i] != carry[i+1] else (1-carry[i],) for i in range(s)]
        for private in product(*options):
            accepted.add((carry[0], *private, carry[-1]))
    return accepted


def check_knot(s, excluded):
    names = [f"x{i}" for i in range(s+2)]
    clauses = [" ".join(("~" if b else "")+name for name,b in zip(names,word)) for word in excluded]
    command = [sys.executable,"-B","-m","knotlab","check","--cnf","; ".join(clauses),
               "--loops",*names[:-1],"--contact",names[-1],"--json"]
    state=json.loads(subprocess.check_output(command,cwd=ROOT,text=True,
                                            env={**os.environ,"PYTHONPATH":str(ROOT/"tools")}))
    assert state["is_knot"]


def verify_mixed_chain(depth):
    # Allocate the root and the first-branch copies from their original port rule.
    a,b,c=0,1,2
    next_id=3
    copies=[]
    knots=[]
    endpoints_in_order=[c]
    for level in range(depth+1):
        x,y=next_id,next_id+1
        next_id+=2
        copies.append((a,b,c,x,y))
        knots.append((y,a,c))
        a,b,c=c,a,x
    if depth==1:
        _,_,_,x0,_=copies[0]
        target=copies[1][4]
        endpoints_in_order.extend([target,x0])
    else:
        if depth%2:
            endpoints_in_order.append(copies[1][4])
        for i in range(1 if depth%2==0 else 2,depth-2,2):
            a,b,c,x,y=copies[i]
            side_ports=(x,c,a)
            z=next_id
            next_id+=1
            knots.append((z,side_ports[0],side_ports[2]))
            endpoints_in_order.append(z)
        a,b,c,x,target=copies[depth]
        terminal_ports=(target,x,b)
        w=next_id
        next_id+=1
        knots.append((w,terminal_ports[0],terminal_ports[2]))
        endpoints_in_order.extend([w,target])
    all_ids=sorted({vertex for knot in knots for vertex in knot})
    index={v:i for i,v in enumerate(all_ids)}
    indexed=[tuple(index[v] for v in knot) for knot in knots]
    out=[index[v] for v in endpoints_in_order]
    allowed=set()
    for state in product((0,1),repeat=len(all_ids)):
        if all(not (state[i]==state[j]==state[k]) for i,j,k in indexed):
            allowed.add(tuple(state[j] for j in out))
    assert allowed==chain_projection((depth+1)//2)
    assert len(out)==(depth+1)//2+2
    return len(allowed)


def main():
    pairs=verify_boundary_memory()
    checked_sides=separator_control()
    sizes=[]
    for s in range(1,9):
        allowed=chain_projection(s)
        excluded=sorted(set(product((0,1),repeat=s+2))-allowed)
        assert len(excluded)==2 and all(b!=c for b,c in zip(*excluded))
        for i in range(s+2):
            assert len({w[:i]+w[i+1:] for w in allowed})==1<<(s+1)
        if s in (1,2,5):
            check_knot(s,excluded)
        sizes.append(len(allowed))
    occupancy_checks=0
    for s in range(1,13):
        for middle in product((0,1),repeat=s-1):
            bits=(1,*middle,1)
            if all(any(bits[i:i+3]) for i in range(len(bits)-2)):
                assert sum(bits) >= (s+2)//3+1
            occupancy_checks+=1
    print(json.dumps(dict(interface_pairs_after_three=pairs,side_bridges=checked_sides,
                          two_steps_nonfull=True,chain_allowed=sizes,canonical_knot_depths=[1,2,5],
                          occupied_patterns=occupancy_checks,
                          mixed_chain_projection_sizes=[verify_mixed_chain(s) for s in range(1,7)]),indent=2))


if __name__=="__main__":
    main()
