"""Check returned witnesses against the guarded clauses in the unswapped order."""
from collections import defaultdict, deque
from importlib.util import module_from_spec, spec_from_file_location
from itertools import chain, product
from pathlib import Path
from random import Random
import json
import os
import sys


def load_file(path, key):
    spec = spec_from_file_location(key, path)
    module = module_from_spec(spec)
    sys.modules[key] = module
    spec.loader.exec_module(module)
    return module


def private_decision(middles, pads, raw):
    """When pads are private, each partially enabled implication can be released locally."""
    assert len(set(pads)) == len(pads)
    stages = len(middles)//2
    if not all(raw[:12]) or not all(raw[12:24]):
        return True
    links = defaultdict(list)
    for b, name in enumerate(middles):
        left, mid, right = (0,b//2), (1,name), (0,b//2+1)
        for side, (tail, head) in enumerate(((left,mid),(mid,right))):
            start = 24 + 12*b + 6*side
            if all(raw[start:start+6]):
                links[tail].append(head)
    seen = {(0,0)}
    pending = deque(seen)
    while pending:
        tail = pending.popleft()
        for head in links[tail]:
            if head not in seen:
                seen.add(head)
                pending.append(head)
    return (0,stages) not in seen


def path_case(d, nested):
    middles, pads = nested.upper_schedule(list(range(d))*2)
    flags = [0]*len(pads)
    for i in range(d):
        incoming, outgoing = (i, i+d) if i%2 == 0 else (i+d, i)
        flags[4*incoming] = flags[4*outgoing+1] = 3
    return middles, pads, nested.packed(flags)


def path_checks(reader, nested, base, oracle):
    released_guards = split_names = 0
    examples = []
    for d in (3,5,7,9,11):
        mids, pads, raw = path_case(d, nested)
        group = reader.prepare(mids, pads)
        assert len(group.removed) == d-1
        assert group.witness(raw) is None and not private_decision(mids, pads, raw)
        cnf, guards, _ = nested.raw_layout(mids,pads,base)
        def pins(v):
            return [g if bit else -g for g,bit in zip(guards,v)]
        with oracle(name="g3",bootstrap_with=cnf) as solver:
            assert not solver.solve(assumptions=pins(raw))
            for i in range(len(raw)):
                if raw[i]:
                    off = bytearray(raw)
                    off[i] = 0
                    assert private_decision(mids,pads,off) and solver.solve(assumptions=pins(off))
                    released_guards += 1
        for i in range(d):
            separated = list(mids)
            separated[2*(d+i)] = max(mids) + 1
            clauses, new_guards, _ = nested.raw_layout(separated,pads,base)
            assert private_decision(separated,pads,raw)
            with oracle(name="g3",bootstrap_with=clauses) as solver:
                assert solver.solve(assumptions=[g if bit else -g for g,bit in zip(new_guards,raw)])
            split_names += 1
        examples.append({"doubled_names":d, "stages":2*d, "minimum_removed":len(group.removed)})
    return {"examples":examples,"active_single_guard_deletions_restoring_sat":released_guards,
            "single_identity_splits_restoring_sat":split_names}


def compiler_certificates(compiler):
    rows = []
    for n in (0,1,3,5,6):
        catalog = compiler.clauses_on(n)
        for schedule in (catalog, catalog[:2*n]):
            stages, _ = compiler.compile_stages(n, schedule)
            positions = defaultdict(list)
            for j, branches in enumerate(stages):
                for name, _, _ in branches:
                    positions[name].append(j)
            paired = [(("feedback","source"),("endpoint",0)), (("feedback","sink"),("endpoint",1))]
            for x in range(1,n+1):
                for side, v in enumerate((x,-x)):
                    paired.append((("feedback",v), ("wire",2*(x-1),side)))
                paired.append((("wire",2*x-1,0), ("wire",2*x-1,1)))
            assert len(set(chain.from_iterable(paired))) == 2*len(paired)
            assert len(paired) == 3*n+2
            for v,w in paired:
                a,b = positions[v]
                c,e = positions[w]
                assert len({a,b,c,e}) == 4 and ((a<c<b) != (a<e<b))
            rows.append({"variables":n,"stages":len(stages),"disjoint_obstructions":len(paired)})
    return rows


def mixed_case(d, nested):
    mids, pads, prefix = path_case(d,nested)
    m, p = max(mids)+1, max(pads)+1
    for _ in range(d):
        mids.extend((m,m+1))
        pads.extend((p,p+1,p,p+2))
        m,p = m+2,p+3
    # The lower outgoing pads of mirror stages give one genuinely nested suffix.
    for j in range(d//2):
        pads[8*d+4*(d-1-j)+3] = pads[8*d+4*j+3]
    raw = prefix + nested.packed([1,3,2,3]*d)[24:]
    return mids,pads,raw


def mixed_checks(reader, nested, base, oracle):
    counts = {}
    tested_sat = tested_unsat = essential = split_pads = 0
    rng = Random(21)
    for d in (1,3,5,7,9,11):
        m,p,raw = mixed_case(d,nested)
        boundaries = list(reader.independent_blocks(m,p))
        assert [(i,j) for i,j,*_ in boundaries] == [(0,2*d),(2*d,3*d)]
        assert len(reader.prepare(m,p).removed) == d-1
        polarities = defaultdict(set)
        for i,pad in enumerate(p):
            a,b = 24+6*i, 27+6*i
            pair = (all(raw[a:b]), all(raw[b:b+3]))
            if pair[0] != pair[1]:
                polarities[pad].add(pair)
        assert sum(len(s)==2 for s in polarities.values())==d
        active = [i for i,v in enumerate(raw) if v]
        def vectors():
            yield raw
            for i in active:
                off = bytearray(raw)
                off[i]=0
                yield off
        check = nested.compare(m,p,vectors(),base,oracle,reader.solve_by_blocks)
        assert check["sat_witnesses"]==len(active) and check["unsat"]==1
        tested_sat += check["sat_witnesses"]
        tested_unsat += check["unsat"]
        essential += len(active)
        counts[str(d)]={"stages":3*d,"exceptions":d-1,"mixed_pads":d,"independent_blocks":2}
        for j in range(d):
            separated = list(p)
            separated[8*d+4*j+2] = max(p)+1
            check = nested.compare(m,separated,[raw],base,oracle,reader.solve_by_blocks)
            assert check["sat_witnesses"] == 1
            split_pads += 1
        def varied():
            for _ in range(48):
                vector = nested.packed([rng.randrange(4) for _ in p])
                for i in range(len(vector)):
                    if rng.randrange(24)==0:
                        vector[i] ^= 1
                yield vector
        check = nested.compare(m,p,varied(),base,oracle,reader.solve_by_blocks)
        tested_sat += check["sat_witnesses"]
        tested_unsat += check["unsat"]
    # Generic fallback: internal and cross-stage pad and middle joins with other
    # blocks on either side; a block algorithm must preserve every shared name.
    for r in (2,3,5,7):
        m,p = nested.deep_layout(r)
        raw = (nested.packed([rng.randrange(4) for _ in p],s,t)
               for _ in range(32) for s,t in product((0,1),repeat=2))
        check = nested.compare(m,p,raw,base,oracle,reader.solve_by_blocks)
        tested_sat += check["sat_witnesses"]
        tested_unsat += check["unsat"]
    return {"cases":counts, "individually_essential_guards":essential,
            "single_mixed_pad_splits_restoring_sat":split_pads,
            "raw_sat_witnesses":tested_sat,"raw_unsatisfiable":tested_unsat}


def main():
    from pysat.solvers import Solver
    folder = Path(__file__).resolve().parent
    reader = load_file(folder/"solver.py", "route_grouping_reader")
    previous = reader.PREVIOUS
    def old(ticket, slug):
        return reader.ROOT / "proofs" / ticket / (ticket+"-P001_"+slug) / "check.py"
    nested = load_file(old(previous+"D","nested_pair_grouping"), "route_group_predecessor")
    base = load_file(nested.BASE, "original_guarded_cnf")
    compiler = load_file(old(previous+"C","pairwise_sharing"), "guarded_pair_compiler")
    rng = Random(51061)
    totals = [0,0]
    def compare(m,p,vectors):
        group = reader.prepare(m,p)
        counts = nested.compare(m,p,vectors,base,Solver,lambda _m,_p,raw:group.witness(raw))
        totals[0] += counts["sat_witnesses"]
        totals[1] += counts["unsat"]
        return counts
    for m in nested.small_partitions(2):
        for p in nested.small_partitions(4):
            compare(m,p,(nested.packed(f,s,t) for f in product(range(4),repeat=4)
                         for s,t in product((0,1),repeat=2)))
    one_stage_total = sum(totals)
    # The empty word still has the two endpoint units on the same boundary.
    for s,t in product((0,1),repeat=2):
        raw = nested.packed([],s,t)
        answer = reader.solve([],[],raw)
        by_blocks = reader.solve_by_blocks([],[],raw)
        assert (by_blocks is not None) == (answer is not None)
        if by_blocks is not None:
            assert (not s or by_blocks[0][0]) and (not t or not by_blocks[0][0])
        assert (answer is not None) == (not s or not t)
        if answer is not None:
            assert len(answer[0]) == 1 and (not s or answer[0][0]) and (not t or not answer[0][0])
    m = [0,1,0,1]
    p = list(range(8))
    group = reader.prepare(m,p)
    assert sum(group.swaps) == 1 and not group.removed
    wrong_guard_vector = None
    for flags in product((0,3),repeat=8):
        v = nested.packed(flags)
        right = private_decision(m,p,v)
        wrong = nested.solve(group.middles,group.pads,v) is not None
        if right != wrong:
            wrong_guard_vector = list(flags)
            break
    assert wrong_guard_vector is not None
    compare(m,p,(nested.packed(flags) for flags in product((0,3),repeat=8)))
    for r in (3,5,8,10):
        m,p = nested.deep_layout(r//2)
        if r%2:
            m.extend((len(m),len(m)+1))
            p.extend(range(len(p),len(p)+4))
        for j in range(0,r,3):
            a,b = 2*j,4*j
            m[a:a+2] = reversed(m[a:a+2])
            p[b:b+4] = p[b+2:b+4] + p[b:b+2]
        def vectors():
            yield nested.packed([0]*len(p))
            yield nested.packed([3]*len(p))
            for _ in range(128):
                raw = nested.packed([rng.randrange(4) for _ in p])
                for i in range(24,len(raw)):
                    if not raw[i] and rng.randrange(6)==0:
                        raw[i]=1
                if rng.randrange(8)==0:
                    raw[rng.randrange(24)]=0
                yield raw
        compare(m,p,vectors())
    return {"status":"passed", "one_stage_decisions":one_stage_total,
            "raw_checked_sat_witnesses":totals[0], "raw_checked_unsatisfiable":totals[1],
            "wrong_guard_block_control":wrong_guard_vector, "empty_guard_choices":4,
            "live_easy_family":path_checks(reader,nested,base,Solver),
            "combined_readers":mixed_checks(reader,nested,base,Solver),
            "compiler_certificates":compiler_certificates(compiler)}


if __name__ == "__main__":
    root = Path(__file__).resolve().parents[3]
    python = root/".venv/bin/python"
    if python.exists() and Path(sys.prefix).resolve() != python.parent.parent.resolve():
        os.execv(str(python),[str(python),"-B",str(Path(__file__).resolve())])
    print(json.dumps(main(),sort_keys=True))
