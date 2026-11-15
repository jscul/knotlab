"""Check static rank, proof certificates, named cuts and strict clause deletion witnesses."""

from collections import Counter
from copy import deepcopy
from functools import cache
from hashlib import sha256
from itertools import combinations, combinations_with_replacement, product
import json
from pathlib import Path
from random import Random

from solver import minimum_proof_span, minimum_span, named_kernel


def raw(mask, offset=0):
    return ([[]] if offset else []) + [[i+1] for i in range(mask.bit_length()) if mask >> i & 1]


def read_form(form):
    counts = Counter(tuple(sorted(term)) for term in form)
    terms = [term for term, count in counts.items() if count % 2]
    assert all(len(term) <= 1 for term in terms)
    return frozenset(t[0] for t in terms if t), int(() in terms)


def generated(vectors):
    values = {0}
    for v in vectors:
        values |= {x ^ v for x in values}
    return frozenset(values)


@cache
def subspaces(n):
    spaces = {frozenset({0})}
    frontier = list(spaces)
    while frontier:
        space = frontier.pop()
        for v in range(1, 1 << n):
            if v not in space:
                bigger = space | frozenset(x ^ v for x in space)
                if bigger not in spaces:
                    spaces.add(bigger)
                    frontier.append(bigger)
    return sorted(spaces, key=len)


def oracle(n, pairs):
    for space in subspaces(n):
        if all(any(x in space for x in pair) for pair in pairs):
            return len(space).bit_length()-1
    return None


def verify_certificate(n, pairs, answer):
    basis = [read_form(f) for f in answer["basis"]]
    assert all(not offset and all(1 <= v <= n for v in form) for form, offset in basis)
    table = [frozenset()]
    for form, _ in basis:
        table.extend([term ^ form for term in table])
    assert len(set(table)) == len(table) == 2**answer["rank"]
    assert len(answer["coordinates"]) == len(answer["orientations"]) == len(answer["offsets"]) == len(pairs)
    assert len(set(answer["basis_gates"])) == len(basis) == len(answer["basis_gates"])
    for (slope, _), gate in zip(basis, answer["basis_gates"]):
        assert read_form(pairs[gate][answer["orientations"][gate]])[0] == slope
    for pair, side, mask, bit in zip(pairs, answer["orientations"], answer["coordinates"], answer["offsets"]):
        assert side in (0, 1) and 0 <= mask < len(table) and bit in (0, 1)
        assert read_form(pair[side]) == (table[mask], bit)


def test_oracles(tally):
    # A leading constant gate supplies one earlier name. Using it as a factor
    # is statically ineligible even when its value is already determined.
    first = ([[]], [])
    small = list(combinations_with_replacement((None, 0, 1, 2, 3), 2))
    rng = Random(70233)
    def check(n, pairs):
        normalized = [first]
        for i, pair in enumerate(pairs):
            normalized.append(tuple(([[n+1]] if x is None else raw(x, (i+j) % 2)) for j, x in enumerate(pair)))
        expected = oracle(n, pairs)
        answer = minimum_span(n, normalized)
        assert (None if answer is None else answer["rank"]) == expected
        if answer is not None:
            verify_certificate(n, normalized, answer)
            if expected:
                assert minimum_span(n, normalized, expected-1) is None
        return answer
    for pairs in product(small, repeat=3):
        check(2, pairs)
        tally["two_coordinate_ordered_three_gate_instances"] += 1
    for n in (3, 4, 5):
        for _ in range(42):
            pairs = [tuple(rng.choice((None, *range(1 << n))) for _ in range(2)) for _ in range(6)]
            answer = check(n, pairs)
            orientations = [generated(vs) for vs in product(*pairs) if None not in vs]
            optimum = min((len(s).bit_length()-1 for s in orientations), default=None)
            assert (None if answer is None else answer["rank"]) == optimum
            if answer is not None:
                basis = [sum(1 << (v-1) for v in read_form(f)[0]) for f in answer["basis"]]
                for assignment in range(1 << n):
                    bits = sum(((assignment & v).bit_count() % 2) << i for i,v in enumerate(basis))
                    predictions = [(bits & mask).bit_count() % 2 ^ c
                                   for mask,c in zip(answer["coordinates"],answer["offsets"])]
                    expected = [1]  # The zero-rank setup selects its constant-one factor.
                    for i, pair in enumerate(pairs):
                        side = answer["orientations"][i+1]
                        expected.append((assignment & pair[side]).bit_count() % 2 ^ ((i+side)%2))
                    assert predictions == expected
                    tally["input_assignments_replaying_selected_factors"] += 1
            tally["larger_instances_with_subspace_and_orientation_oracles"] += 1
    assert len(subspaces(5)) == 374
    tally["five_coordinate_subspaces"] = len(subspaces(5))


def orientation_controls(tally):
    rows = [(raw(4), raw(1,1)), (raw(2,1),raw(8)), (raw(16),raw(3))]
    answer = minimum_span(5,rows)
    verify_certificate(5,rows,answer)
    cost = {}
    for sides in product((0,1), repeat=3):
        labels = [read_form(row[side])[0] for row,side in zip(rows,sides)]
        assert len(set(labels)) == 3
        vectors = [sum(1 << (v-1) for v in label) for label in labels]
        cost[sides] = len(generated(vectors)).bit_length()-1
    assert [key for key,value in cost.items() if value == 2] == [(1,0,1)]
    assert cost[(0,0,0)] == cost[(1,1,1)] == 3 and answer["orientations"] == [1,0,1]
    tally["rank_two_orientations_among_eight"] = sum(rank==2 for rank in cost.values())
    for r in (1,2,3,4):
        nonzero = (1 << r)-1
        rows = [(raw(i), [[r+i]]) for i in range(1, nonzero+1)]
        result = minimum_span(r+nonzero, rows)
        assert result["rank"] == r and len({tuple(map(tuple,row[side])) for row,side in zip(rows,result["orientations"])}) == nonzero
        verify_certificate(r+nonzero, rows, result)
    tally["distinct_selected_slope_classes_at_rank_four"] = nonzero
    signed = [([], [])] + [(raw(s,c),[[3]]) for s,c in product((1,2,3),(0,1))]
    result = minimum_span(2,signed)
    assert result["rank"] == 2 and len({read_form(row[side]) for row,side in zip(signed[1:],result["orientations"][1:])}) == 6
    verify_certificate(2,signed,result)
    assert minimum_span(0,[])["rank"] == minimum_span(0,[([], [[]])])["rank"] == 0
    assert minimum_span(0,[([],[]),([[1]],[[1],[]])]) is None
    # Formally canceled older names become eligible. A true dependence on an
    # older name remains ineligible regardless of its defining equation.
    unnormalized = [([],[]), ([[2],[2],[1],[]], [[2]]), ([[1],[1]], [[3]])]
    answer = minimum_span(1, unnormalized)
    assert answer["rank"] == 1 and answer["offsets"] == [0,1,0]
    verify_certificate(1, unnormalized, answer)
    large = 10**10+7
    assert minimum_span(large,[([[large]], [[large],[]])])["rank"] == 1
    for bad in ([([[2],[2]],[])], [([[1,1]],[])]):
        try:
            minimum_span(1,bad)
        except ValueError:
            tally["malformed_factor_controls_rejected"] += 1
        else:
            raise AssertionError("invalid declaration accepted")
    bad = deepcopy(answer)
    bad["orientations"][1] ^= 1
    try:
        verify_certificate(1, unnormalized, bad)
    except AssertionError:
        tally["incorrect_certificates_rejected"] += 1
    else:
        raise AssertionError("incorrect orientation accepted")


def strict_chain(v, edges):
    """Actual strict input and an exact named refutation for a simple graph."""
    K = named_kernel()
    m = len(edges)
    y = list(range(v+1, v+m+2))
    z = list(range(v+m+2, v+2*m+2))
    vertices = sorted({k for e in edges for k in e})
    units = [*vertices,y[0],-y[-1]]
    cnf = []
    pads = []
    n = v+2*m+1
    for literal in units:
        a,b = n+1,n+2
        n += 2
        pads.append((a,b))
        cnf.extend([[literal, sa*a, sb*b] for sa,sb in product((1,-1), repeat=2)])
    for i,(u,w) in enumerate(edges):
        cnf.extend([[-y[i],-u,z[i]],[-z[i],-w,y[i+1]]])
    dag = K.Dag(n,cnf)
    unit_refs = {}
    for i,(literal,(a,b)) in enumerate(zip(units,pads)):
        refs = [dag.axiom(4*i+j) for j in range(4)]
        first,second = dag.resolve(refs[0], refs[1], b), dag.resolve(refs[2], refs[3], b)
        unit_refs[literal] = dag.resolve(first,second,a)
    current = unit_refs[y[0]]
    cuts = []
    for i,(u,w) in enumerate(edges):
        f,g = K.var(u),K.var(w)
        p = K.mul(f,g)
        name,definition = dag.define(f,g)
        t = K.var(name)
        def_atom = K.add(t,p)
        work = dag.multiply(unit_refs[u], K.add(f,K.ONE), g)
        product_true = dag.combine(work,unit_refs[w],K.add(p,g),K.add(g,K.ONE))
        name_true = dag.combine(product_true,definition,K.add(p,K.ONE),def_atom)
        at = 4*len(units)+2*i
        implication = dag.resolve(dag.axiom(at),dag.axiom(at+1),z[i])
        residual = dag.resolve(current,implication,y[i])
        residual = dag.multiply(residual,f,g)
        residual = dag.multiply(residual,g,f)
        residual = dag.contract(residual,p)
        passes = dag.combine(residual,definition,p,def_atom)
        cuts.append((len(dag.proof),name))
        current = dag.resolve(name_true,passes,name)
    dag.resolve(current,unit_refs[-y[-1]],y[-1])
    return n,cnf,dag.proof,(y,z,units,pads,cuts)


def check_deletions(v, edges, n, cnf, layout):
    y,z,units,pads,_ = layout
    for removed,clause in enumerate(cnf):
        values = [False]*(n+1)
        for u in range(1,v+1):
            values[u] = True
        if removed < 4*len(units):
            j = removed//4
            literal = units[j]
            if literal == y[0]:
                cut = 0
            elif literal == -y[-1]:
                cut = len(y)
            else:
                values[literal] = False
                cut = 1+next(i for i,e in enumerate(edges) if literal in e)
            for pad,occurrence in zip(pads[j],clause[1:]):
                values[pad] = occurrence < 0
        else:
            cut = (removed-4*len(units))//2+1
        for i,state in enumerate(y):
            values[state] = i < cut
        for i,((u,_),name) in enumerate(zip(edges,z)):
            values[name] = values[y[i]] and values[u]
            if removed == 4*len(units)+2*i:
                values[name] = False
        violated = [j for j,row in enumerate(cnf)
                    if not any(values[abs(lit)] == (lit>0) for lit in row)]
        assert violated == [removed]
    return len(cnf)


def min_cover(v, edges):
    for k in range(v+1):
        for candidate in combinations(range(1,v+1),k):
            if all(u in candidate or w in candidate for u,w in edges):
                return k
    raise AssertionError("full vertex set covers every edge")


def check_live_proof(n, cnf, proof, layout, tally):
    K = named_kernel()
    assert all(len(row)==len({abs(x) for x in row})==3 for row in cnf)
    assert K.ancestors(n,cnf,proof,include_declarations=False) == list(range(len(proof)))
    for index,name in layout[-1]:
        pivot = proof[index]
        assert pivot["rule"]=="combine" and pivot["coefficients"] == [1,1]
        assert pivot["chosen"] == [K.q.encode(K.literal(name)),K.q.encode(K.literal(-name))]
        tally["gate_outputs_used_as_opposite_pivots"] += 1
    tally["strict_named_refutations_verified"] += 1
    tally["largest_strict_refutation_nodes"] = max(tally["largest_strict_refutation_nodes"],len(proof))


def test_strict_sat_source(tally):
    # Max independent set on the constructed graph is a separate decision
    # method from checking source truth assignments.
    def graph(n, cnf):
        edges = [(2*i+1,2*i+2) for i in range(n)]
        for j, clause in enumerate(cnf):
            vertices = [2*n+3*j+1+i for i in range(3)]
            edges.extend(combinations(vertices,2))
            for lit,v in zip(clause,vertices):
                opposite = 2*(abs(lit)-1) + (2 if lit>0 else 1)
                edges.append((opposite,v))
        return 2*n+3*len(cnf),edges
    def independence_number(v, edges):
        adjacency = [0]*v
        for a,b in edges:
            adjacency[a-1] |= 1 << (b-1)
            adjacency[b-1] |= 1 << (a-1)
        @cache
        def best(mask):
            if not mask:
                return 0
            low = mask & -mask
            rest = mask ^ low
            return max(best(rest),1+best(rest & ~adjacency[low.bit_length()-1]))
        return best((1 << v)-1)
    all_eight = [tuple(s*i for s,i in zip(signs,(1,2,3))) for signs in product((-1,1),repeat=3)]
    for mask in range(256):
        cnf = [clause for i,clause in enumerate(all_eight) if mask >> i & 1]
        sat = any(all(any(((x>>(abs(lit)-1))&1)==(lit>0) for lit in clause) for clause in cnf) for x in range(8))
        v,edges = graph(3,cnf)
        rank = v-independence_number(v,edges)
        assert (rank <= 3+2*len(cnf)) == sat
        tally["strict_3sat_clause_subsets_vs_exact_vertex_cover"] += 1
        if mask in (127,255):
            n,formula,proof,events = strict_chain(v,edges)
            K = named_kernel()
            assert K.verify(n,formula,proof)["declarations"] == len(edges)
            check_live_proof(n,formula,proof,events,tally)
            tally["strict_source_single_clause_deletion_models"] += check_deletions(v,edges,n,formula,events)
            tally["composed_strict_3sat_to_live_proof_witnesses"] += 1
            tally["minimum_rank_on_seven_clause_source" if mask==127 else "minimum_rank_on_eight_clause_source"] = rank


def graph_controls(tally):
    for v in (4,5):
        universe = list(combinations(range(1,v+1),2))
        for flags in range(1 << len(universe)):
            edges = [e for i,e in enumerate(universe) if flags >> i & 1]
            expected = min_cover(v,edges)
            pairs = [([[u]],[[w]]) for u,w in edges]
            assert minimum_span(v,pairs)["rank"] == expected
            tally["coordinate_graphs_vs_exhaustive_vertex_cover"] += 1
            if v==5 and flags not in (0,1,(1 << len(universe))-1,0b1001011001):
                continue
            n,cnf,proof,layout = strict_chain(v,edges)
            result = minimum_proof_span(n,cnf,proof)
            assert result["rank"] == expected
            verify_certificate(n,pairs,result)
            check_live_proof(n,cnf,proof,layout,tally)
            tally["strict_source_single_clause_deletion_models"] += check_deletions(v,edges,n,cnf,layout)
            if v==5 and len(edges)==10:
                altered = deepcopy(proof)
                next(row for row in altered if row["rule"]=="define")["factors"][0] = []
                try:
                    minimum_proof_span(n,cnf,altered)
                except ValueError:
                    tally["malformed_proof_controls_rejected"] += 1
                else:
                    raise AssertionError("corrupted defining equation accepted")


def main():
    kernel = named_kernel()
    for path,digest in ((kernel.__file__,"d81e4f0e8dfc8b8260587d0b7f19672bfaef87827665c8689167b72100806929"),
                        (kernel.q.__file__,"84a7cdc149c8945061e8c46daaf9b3686cbcf4cee26f73b4e79c663bda25b71e")):
        assert sha256(Path(path).read_bytes()).hexdigest()==digest
    tally = Counter()
    test_oracles(tally)
    orientation_controls(tally)
    graph_controls(tally)
    test_strict_sat_source(tally)
    assert tally["strict_named_refutations_verified"] == 70
    assert tally["gate_outputs_used_as_opposite_pivots"] > 300
    assert tally["malformed_proof_controls_rejected"] == tally["incorrect_certificates_rejected"] == 1
    return {"status":"passed",**dict(sorted(tally.items()))}


if __name__ == "__main__":
    print(json.dumps(main(),indent=2,sort_keys=True))
