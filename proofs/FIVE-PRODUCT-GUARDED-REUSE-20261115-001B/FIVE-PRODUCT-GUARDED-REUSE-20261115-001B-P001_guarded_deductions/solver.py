"""Guarded affine deductions for the explicit five-product evaluator pair.

Each visible state packs x0,...,x5,s,u,v into the low nine bits. A guard is a
list of pairs (mask, value), imposing the selected bit parity. A proof node
has either one affine equation as its claim or None (contradiction).
"""
from collections import Counter
from functools import cache
from itertools import product


ALL = (1 << 512) - 1
S, U, V = 64, 128, 256


def indices(table):
    while table:
        point = table & -table
        yield point.bit_length() - 1
        table ^= point


def parity(v):
    return v.bit_count() % 2


def ensure(test, explanation):
    if not test:
        raise ValueError(explanation)


def equation(pair):
    mask, val = pair
    ensure(type(mask) is int and 0 <= mask < 512 and type(val) is int and val in (0,1),
           "equation must use only the nine displayed coordinates and a Boolean value")
    return mask,val


@cache
def equation_points(mask, val):
    equation((mask,val))
    return sum(1 << state for state in range(512) if parity(state & mask) == val)


def guard_points(rows):
    out = ALL
    for row in rows:
        out &= equation_points(*equation(row))
    return out


def outputs(x, masks):
    adjacent = x & (x >> 1)
    return tuple(parity(adjacent & mask) for mask in (31,*masks))


def evaluator_sets(masks, charge):
    ensure(len(masks)==2 and all(type(i) is int and 0 <= i < 32 for i in masks), "invalid fixed masks")
    ensure(type(charge) is int and charge in (0,1), "invalid terminal charge")
    left = right = 0
    for state in range(512):
        x, s, u, v = state & 63, (state >> 6)&1, (state >> 7)&1, (state >> 8)&1
        q,a,b = outputs(x,masks)
        if (s,u,v) == (q,a,b):
            left |= 1 << state
        if s == q ^ charge:
            right |= 1 << state
    return {"left":left,"right":right}


@cache
def hull(points):
    if not points:
        return 0
    origin = (points & -points).bit_length()-1
    span = {0}
    for x in indices(points):
        v = x ^ origin
        if v not in span:
            span |= {w ^ v for w in span}
    return sum(1 << (w ^ origin) for w in span)


def saturate(space, sides):
    trace = [space.bit_count()]
    evaluations = support_visits = 0
    while space:
        rich, plain = space & sides["left"], space & sides["right"]
        support_visits += rich.bit_count() + plain.bit_count()
        evaluations += 2
        after = hull(rich) & hull(plain)
        if after == space:
            break
        space = after
        trace.append(space.bit_count())
    return space,trace,evaluations,support_visits


@cache
def translation(masks, delta):
    ensure(type(delta) is int and 0 < delta < 64, "nontrivial translation requires six input bits")
    out = []
    for state in range(512):
        x = state & 63
        original, moved = outputs(x,masks),outputs(x ^ delta,masks)
        correction = sum((a^b) << (6+i) for i,(a,b) in enumerate(zip(original,moved)))
        out.append(state ^ delta ^ correction)
    ensure(len(set(out))==512 and all(out[out[w]]==w for w in range(512)), "translation not an involution")
    offset = out[0]
    slopes = [out[1 << i] ^ offset for i in range(9)]
    for w in range(512):
        expected = offset
        for i in indices(w):
            expected ^= slopes[i]
        ensure(expected==out[w], "proposed translation is not affine")
    return tuple(out)


def sequential(space, sides, first):
    """Alternate whole-side affine restrictions; stop at empty or two consecutive stable checks."""
    order = (first, "left" if first == "right" else "right")
    operations = visits = stable = 0
    while space and stable < 2:
        points = space & sides[order[operations % 2]]
        visits += points.bit_count()
        after = hull(points)
        operations += 1
        stable = stable + 1 if after == space else 0
        space = after
    return space,operations,visits


def move(points, mapping):
    return sum(1 << mapping[w] for w in indices(points))


def verify(proof, charge=None):
    nodes = proof["nodes"]
    masks = tuple(proof["masks"])
    charge = proof["charge"] if charge is None else charge
    sides = evaluator_sets(masks,charge)
    guards,claims,dependencies = [],[],[]
    counts = Counter()
    terminal_traces, uses, routes = [],[],[]
    support_visits = source_calls = hull_calls = hull_visits = xor_adds = 0
    order_totals = {side:[0,0] for side in ("right","left")}
    for i,node in enumerate(nodes):
        kind, G = node["rule"],guard_points(node["guard"])
        claim = None if node.get("claim") is None else equation(node["claim"])
        refs = node.get("parents",[])
        ensure(all(type(j) is int and 0 <= j < i for j in refs), "cyclic or forward proof reference")
        counts[kind] += 1
        if kind == "source":
            ensure(not refs and claim is not None and node["side"] in sides, "invalid evaluator source")
            actual = G & sides[node["side"]]
            ensure(actual and not(actual & ~equation_points(*claim)), "claimed equation fails on guarded evaluator")
            source_calls += 1
            support_visits += actual.bit_count()
        elif kind == "cancel":
            ensure(refs and claim is None, "affine contradiction requires premises")
            lhs = rhs = 0
            for j in refs:
                ensure(claims[j] is not None and not(G & ~guards[j]), "affine premise guard not entailed")
                l,b = claims[j]
                lhs ^= l
                rhs ^= b
            ensure((lhs,rhs)==(0,1), "cited equations do not XOR to 0=1")
            xor_adds += len(refs)-1
        elif kind == "terminal":
            ensure(not refs and claim is None, "expected a whole-cell terminal")
            stopped,trace,ops,visits = saturate(G,sides)
            ensure(not stopped, "terminal cell remains live")
            hull_calls += ops
            hull_visits += visits
            terminal_traces.append(trace)
            for first in order_totals:
                final,calls,seen = sequential(G,sides,first)
                ensure(final==stopped, "local saturation schedules disagree")
                order_totals[first][0] += calls
                order_totals[first][1] += seen
        elif kind == "rich_route":
            ensure(len(refs)==1 and claim is None and nodes[refs[0]]["rule"] == "terminal",
                   "a guarded terminal reference needs a directly checked terminal proof")
            actual = G & sides["left"]
            target = guards[refs[0]]
            ensure(actual and not (actual & ~target), "the rich evaluator does not establish the terminal guard")
            refined = G & target
            routes.append({"node":i,"terminal":refs[0],"rich_points_checked":actual.bit_count(),
                           "additional_independent_guard_equations":G.bit_count().bit_length()-refined.bit_count().bit_length()})
        elif kind == "split":
            ensure(len(refs)==2 and claim is None and all(claims[j] is None for j in refs), "invalid split")
            q,_ = equation((node["query"],0))
            for b,j in enumerate(refs):
                ensure(guards[j] == (G & equation_points(q,b)) and guards[j], "wrong or empty split branch")
        elif kind == "discharge":
            ensure(len(refs)==1 and claim is not None and claims[refs[0]] is None, "invalid discharge")
            m,b = claim
            ensure(guards[refs[0]] == (G & equation_points(m,b^1)), "discharge does not refute the opposite")
        elif kind == "use":
            ensure(len(refs)==2 and claim is None, "invalid lemma application")
            lemma,rest = refs
            ensure(claims[lemma] is not None and claims[rest] is None, "expected an affine lemma and a contradiction")
            ensure(not(G & ~guards[lemma]), "literal lemma guard not entailed by the current context")
            allowed = equation_points(*claims[lemma])
            ensure(guards[rest] == (G & allowed), "continuation uses the wrong affine conclusion")
            before = saturate(G,sides)[0]
            uses.append({"node":i,"lemma":lemma,"live_points_before":before.bit_count(),
                         "live_points_excluded_by_lemma":(before & ~allowed).bit_count(),
                         "saturated_live_points_after":saturate(G & allowed,sides)[0].bit_count()})
        elif kind == "translate":
            ensure(proof.get("translations",False) and len(refs)==1 and claim is None and claims[refs[0]] is None,
                   "affine transport is disabled or malformed")
            mapping = translation(masks,node["delta"])
            ensure(all(move(T,mapping)==T for T in sides.values()), "map fails to preserve a whole evaluator")
            ensure(move(guards[refs[0]],mapping) == G, "wrong transported guard")
        else:
            raise ValueError(f"unknown proof rule {kind}")
        guards.append(G)
        claims.append(claim)
        dependencies.append(refs)
    ensure(nodes and guards[-1]==ALL and claims[-1] is None, "last node must refute the full ambient guard")
    weights = [0]*len(nodes)
    weights[-1] = 1
    for i in reversed(range(len(nodes))):
        for j in dependencies[i]:
            weights[j] += weights[i]
    ensure(all(weights), "unreachable proof node")
    expanded = Counter()
    for node,weight in zip(nodes,weights):
        expanded[node["rule"]] += weight
    return {"nodes":len(nodes),"rules":dict(sorted(counts.items())),"parent_references":sum(map(len,dependencies)),
            "unfolded_nodes":sum(weights),"unfolded_rules":dict(sorted(expanded.items())),
            "unfolded_parent_references":sum(w*len(refs) for w,refs in zip(weights,dependencies)),
            "source_checks":source_calls,"source_support_visits":support_visits,"xor_additions":xor_adds,
            "terminal_side_hull_calls":hull_calls,"terminal_support_visits":hull_visits,
            "terminal_traces":terminal_traces,"literal_lemma_uses":uses,"rich_routes":routes,
            "sequential_calls_then_support_visits":order_totals,
            "rich_route_support_visits":sum(info["rich_points_checked"] for info in routes)}


class Builder:
    def __init__(self, masks=(1,6), translations=False):
        self.proof = {"masks":list(masks),"charge":1,"translations":translations,"nodes":[]}

    def add(self, rule, G, claim=None, refs=(), **detail):
        self.proof["nodes"].append({"rule":rule,"guard":list(G),"claim":claim,"parents":list(refs),**detail})
        return len(self.proof["nodes"])-1


def fixed(values):
    return [(1 << (2*i),v) for i,v in enumerate(values)]


def term_mask(i,b):
    # First term x0*x1, second x2*(x1+x3), third x4*(x3+x5).
    outputs_and_partners = ((U,2),(V,2^8),(S^U^V,8^32))
    out,partner = outputs_and_partners[i]
    return out ^ (partner if b else 0)


def total_mask(values):
    mask = S
    for i,b in enumerate(values):
        if b:
            mask ^= (2,2^8,8^32)[i]
    return mask


def source_certificate(mode):
    """mode = 'global', 'prefix', or 'direct'. Prefix facts use only current-branch guards."""
    ensure(mode in ("global","prefix","direct","two_groups"),"unknown factoring mode")
    b = Builder()
    facts = {}
    if mode == "global":
        for i,v in product(range(3),range(2)):
            facts[i,v] = b.add("source",[(1 << (2*i),v)],(term_mask(i,v),0),side="left")

    if mode == "two_groups":
        for v,w in product(range(2),repeat=2):
            rhs_odd = (2 if v else 0) ^ (10 if w else 0)
            facts[0,v,w] = b.add("source",fixed((v,w)),(U^V^rhs_odd,0),side="left")
        for w in (0,1):
            facts[1,w] = b.add("source",[(16,w)],(term_mask(2,w),0),side="left")

    def recur(values,local):
        G = fixed(values)
        if len(values)==3:
            if mode=="direct":
                premises = [b.add("source",G,(total_mask(values),0),side="left")]
            elif mode=="global":
                premises = [facts[i,v] for i,v in enumerate(values)]
            elif mode=="two_groups":
                premises = [facts[0,values[0],values[1]],facts[1,values[2]]]
            else:
                premises = local
            right = b.add("source",G,(total_mask(values),1),side="right")
            return b.add("cancel",G,refs=premises+[right])
        kids = []
        i = len(values)
        for v in (0,1):
            child = values+(v,)
            inherited = list(local)
            if mode=="prefix":
                inherited.append(b.add("source",fixed(child),(term_mask(i,v),0),side="left"))
            kids.append(recur(child,inherited))
        return b.add("split",G,refs=kids,query=1 << (2*i))

    recur((),[])
    return b.proof


def literal_certificate(learn=True, masks=(1,6)):
    b = Builder(masks)
    def finish(G,remaining):
        if not remaining:
            return b.add("terminal",G)
        first,*rest = remaining
        children = [finish(G+[(first,val)],rest) for val in (0,1)]
        return b.add("split",G,refs=children,query=first)
    if not learn:
        finish([], [16,4,1])
        return b.proof
    # G pins x4=0. Refute the opposite (x0=1) and discharge its assumption.
    G = [(16,0)]
    counter = finish(G+[(1,1)],[4])
    lemma = b.add("discharge",G,(1,0),[counter])
    kids = []
    for val in (0,1):
        H = G+[(4,val)]
        rest = b.add("terminal",H+[(1,0)])
        kids.append(b.add("use",H,refs=[lemma,rest]))
    left = b.add("split",G,refs=kids,query=4)
    right = finish([(16,1)],[4,1])
    b.add("split",[],refs=[left,right],query=16)
    return b.proof


def translated_certificate(masks=(1,6)):
    b = Builder(masks,True)
    root = b.add("terminal",fixed((0,0,0)))
    for i in (2,1,0):
        G = fixed((0,)*i)
        delta = 1 << (2*i)
        mirror = b.add("translate",G+[(delta,1)],refs=[root],delta=delta)
        root = b.add("split",G,refs=[root,mirror],query=delta)
    return b.proof


def unfold(proof):
    """Duplicate every citation and rebuild a literal tree of proof nodes."""
    b = Builder(proof["masks"],proof.get("translations",False))
    b.proof["charge"] = proof["charge"]
    def copy_node(i):
        node = proof["nodes"][i]
        children = [copy_node(j) for j in node["parents"]]
        b.proof["nodes"].append(dict(node, parents=children))
        return len(b.proof["nodes"])-1
    copy_node(len(proof["nodes"])-1)
    return b.proof


def six_terminal_certificate(shared=True, route=True):
    """Three conflicts per x4 setting; the middle one receives two actual reached branches."""
    b = Builder()
    children = []
    for c in (0,1):
        scope = [(16,c)]
        z = S ^ ((8^32) if c else 0)
        d, h = 2^8, U^2^8
        choices = ([(8,0),(z,0)],
                   [(2,1),(z^1,0)],
                   [(d,1),(z^4,0)])
        terminal = {}
        fork = []
        for value, query, targets in ((0,z^8,(0,1)),(1,d,(1,2))):
            H = scope+[(h,value)]
            pair = []
            for answer,target in enumerate(targets):
                here = H+[(query,answer)]
                if route:
                    if target not in terminal or not shared:
                        terminal[target] = b.add("terminal",scope+choices[target])
                    pair.append(b.add("rich_route",here,refs=[terminal[target]]))
                else:
                    pair.append(b.add("terminal",here))
            fork.append(b.add("split",H,refs=pair,query=query))
        children.append(b.add("split",scope,refs=fork,query=h))
    b.add("split",[],refs=children,query=16)
    return b.proof


def unequal_live_certificate(specialized=False):
    """A derived literal used on two saturated guards of different dimensions."""
    b = Builder()
    def T(g):
        return b.add("terminal",g)
    def last(g,q):
        return b.add("split",g,refs=[T(g+[(q,0)]),T(g+[(q,1)])],query=q)
    G = [(V,0)]
    C = G+[(1,1)]
    lemma = None
    if not specialized:
        h=S^U
        counter = b.add("split",C,refs=[last(C+[(h,0)],16),T(C+[(h,1)])],query=h)
        lemma = b.add("discharge",G,(1,0),[counter])
    kids = []
    for y in (0,1):
        H=G+[(4,y)]
        positive=last(H+[(1,0)],16)
        if specialized:
            negative=last(H+[(1,1)],16)
            kids.append(b.add("split",H,refs=[positive,negative],query=1))
        else:
            kids.append(b.add("use",H,refs=[lemma,positive]))
    yes=b.add("split",G,refs=kids,query=4)
    other=[(V,1)]
    no=b.add("split",other,refs=[last(other+[(1,e)],16) for e in (0,1)],query=1)
    b.add("split",[],refs=[yes,no],query=V)
    return b.proof
