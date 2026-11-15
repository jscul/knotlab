"""Regroup signed report checks by ordinary binary resolution on the original strict CNF."""
from collections import Counter
from itertools import product
from hashlib import sha256
import json
from pathlib import Path
import runpy


ROOT = Path(__file__).resolve().parents[3]
SOURCE = "SHARED-REPORT-CANCELLATION-20261115-001A"
A = runpy.run_path(str(ROOT / "proofs" / SOURCE / (SOURCE + "-P001_strict_checks") / "solver.py"))
Q = A["Q"]
BITS3 = tuple(product((0, 1), repeat=3))


def report(a, b, state):
    x, y, z = BITS3[state]
    return z & ((x & y) ^ (a & b))


def state_id(bits):
    x, y, z = bits
    return (x << 2) | (y << 1) | z


def exclusion(variables, bits):
    return tuple(sorted(-v if b else v for v, b in zip(variables, bits, strict=True)))


def forbidden(charge):
    for a, b, left, right in product((0, 1), (0, 1), range(8), range(8)):
        if report(a, b, left) ^ report(a, b, right) != charge:
            yield a, b, left, right


class ResolutionDag:
    """Signed literal sets with explicit input axiom, both parents, and the positive-parent pivot."""
    def __init__(self, n, cnf):
        self.n = n
        self.cnf = cnf
        self.clauses = []
        self.steps = []
        self._axioms = {}
        self._deductions = {}

    def axiom(self, i):
        if type(i) is not int or not 0 <= i < len(self.cnf):
            raise ValueError("input clause index outside the original CNF")
        if i not in self._axioms:
            self._axioms[i] = len(self.steps)
            self.steps.append(("axiom", i))
            self.clauses.append(tuple(sorted(set(self.cnf[i]))))
        return self._axioms[i]

    def resolve(self, left, right, pivot):
        key = left, right, pivot
        existing = self._deductions.get(key)
        if existing is not None:
            return existing
        pos, neg = set(self.clauses[left]), set(self.clauses[right])
        if pivot not in pos or -pivot not in neg:
            raise ValueError("specified complementary pivot absent")
        pos.remove(pivot)
        neg.remove(-pivot)
        i = len(self.steps)
        self._deductions[key] = i
        self.steps.append(("resolve", left, right, pivot))
        self.clauses.append(tuple(sorted(pos | neg)))
        return i


class _PolynomialRows:
    def __init__(self, dag):
        self.dag = dag

    def __getitem__(self, i):
        return Q.signed_clause(self.dag.clauses[i])


class _StrictRowSink:
    """Run A's genuine row-lift function verbatim and record its ordinary resolutions."""
    def __init__(self, dag):
        self.cnf = dag.cnf
        self.clauses = _PolynomialRows(dag)
        self.axiom = dag.axiom
        self.resolve = dag.resolve


def verify_resolution(dag):
    """Check the exact signed clause at each step from genuine source clauses."""
    Q.validate_cnf(dag.n, dag.cnf)
    if len(dag.steps) != len(dag.clauses):
        raise ValueError("mismatched clause and deduction lists")
    rows, uses = [], set()
    counts = Counter()
    for i, (step, row) in enumerate(zip(dag.steps, dag.clauses, strict=True)):
        rule = step[0]
        if rule == "axiom" and len(step) == 2:
            j = step[1]
            if type(j) is not int or not 0 <= j < len(dag.cnf):
                raise ValueError("invalid genuine axiom reference")
            expected = frozenset(dag.cnf[j])
        elif rule == "resolve" and len(step) == 4:
            p, q, lit = step[1:]
            if any(type(j) is not int or not 0 <= j < i for j in (p, q)) or type(lit) is not int or lit == 0:
                raise ValueError("invalid resolution references")
            if lit not in rows[p] or -lit not in rows[q]:
                raise ValueError("resolution operand lacks the claimed pivot")
            expected = frozenset(v for parent, omit in ((p, lit), (q, -lit)) for v in rows[parent] if v != omit)
            uses.update((p, q))
        else:
            raise ValueError("unexpected ordinary proof rule")
        if tuple(sorted(expected)) != row:
            raise ValueError("displayed resolvent has incorrect literal set")
        rows.append(expected)
        counts[rule] += 1
    if not rows or rows[-1]:
        raise ValueError("refutation must end with empty")
    return {"nodes":len(rows), "axioms":counts["axiom"], "resolutions":counts["resolve"],
            "max_width":max(map(len, rows)), "all_nodes_live":len(uses) == len(rows)-1}


def quadratic_node_count(dag):
    """Exact primitive cost without serializing: two steps plus one per duplicated side literal."""
    total = 0
    for step in dag.steps:
        if step[0] == "axiom":
            total += 1
        else:
            _, p, q, lit = step
            duplicates = (set(dag.clauses[p]) - {lit}) & (set(dag.clauses[q]) - {-lit})
            total += 2 + len(duplicates)
    return total


def quadratic_steps(dag):
    """Generate a complete standard unnamed multiset degree-two certificate without saving its JSON."""
    verify_resolution(dag)
    translated = []
    count = 0
    for i, step in enumerate(dag.steps):
        if step[0] == "axiom":
            yield {"rule":"axiom", "axiom":step[1], "clause":[Q.encode(p) for p in Q.signed_clause(dag.clauses[i])]}
            translated.append(count)
            count += 1
            continue
        _, p, q, pivot = step
        # The terminal builder supplies the primitive combination, false deletion and contractions.
        fragment = Q.Dag(dag.cnf)
        fragment.clauses = [Q.signed_clause(dag.clauses[p]), Q.signed_clause(dag.clauses[q])]
        fragment.proof = [None, None]
        final = fragment.resolve(0, 1, pivot)
        if fragment.clauses[final] != Q.signed_clause(dag.clauses[i]):
            raise ValueError("quadratic expansion disagrees with the signed resolvent")
        refs = [translated[p], translated[q]]
        for row in fragment.proof[2:]:
            yield {**row, "parents":[refs[parent] for parent in row["parents"]]}
            refs.append(count)
            count += 1
        translated.append(refs[-1])


def verify_quadratic(dag):
    return Q.verify(dag.n, dag.cnf, quadratic_steps(dag))


class PathTable:
    """Complete forbidden endpoint rows for a directed, contiguous proper path in one cycle."""
    def __init__(self, owner, left, direction, length, charge, rows, event):
        self.owner = owner
        self.left = left
        self.direction = direction
        self.length = length
        self.right = owner.advance(left, direction, length)
        self.charge = charge
        self.rows = rows
        self.event = event

    @property
    def walk(self):
        return tuple(self.owner.advance(self.left, self.direction, i) for i in range(self.length + 1))

    def flipped(self):
        rows = {(a,b,v,u):ref for (a,b,u,v),ref in self.rows.items()}
        return PathTable(self.owner, self.right, -self.direction, self.length, self.charge, rows, self.event)


def resolve_cube(dag, leaves, pivots):
    """Zero precedes one in each coordinate, so the first child contains the positive pivot."""
    level = leaves
    for pivot in reversed(pivots):
        level = [dag.resolve(level[i], level[i+1], pivot) for i in range(0, len(level), 2)]
    if len(level) != 1:
        raise ValueError("incomplete cube of resolution leaves")
    return level[0]


class PathBuilder:
    """Accumulate only the checks requested so far, joining adjacent derived tables on demand."""
    def __init__(self, encoded, *, cycle_edges=None, middle_order=(2, 0, 1)):
        self.encoded = encoded
        self.middle_order = tuple(middle_order)
        if sorted(self.middle_order) != [0,1,2]:
            raise ValueError("a permutation of the three middle bits is required")
        triples, blocks = encoded["triples"], encoded["blocks"]
        original = [encoded["a"], encoded["b"], *(x for triple in triples for x in triple)]
        if any(len(t) != 3 for t in triples) or len(set(original)) != 2+3*len(triples):
            raise ValueError("shared bits and private triples must have distinct names")
        cycle = tuple((e,False) for e in range(len(blocks))) if cycle_edges is None else tuple(cycle_edges)
        self.h = len(cycle)
        if self.h < 3:
            raise ValueError("at least three distinct edges are needed")
        ends = []
        self._directions = {}
        for e, backwards in cycle:
            if (type(e) is not int or not 0 <= e < len(blocks) or e in self._directions
                    or type(backwards) not in (bool,int) or backwards not in (0,1)):
                raise ValueError("invalid or repeated original cycle edge")
            i, j = blocks[e]["i"], blocks[e]["j"]
            if any(type(v) is not int or not 0 <= v < len(triples) for v in (i,j)) or i == j:
                raise ValueError("invalid original report label")
            ends.append((j,i) if backwards else (i,j))
            self._directions[e] = -1 if backwards else 1
        self._vertices = tuple(p for p,_ in ends)
        if len(set(self._vertices)) != self.h or any(q != self._vertices[(j+1)%self.h] for j,(_,q) in enumerate(ends)):
            raise ValueError("the selected original edges do not form an ordered simple cycle")
        self._positions = {v:i for i,v in enumerate(self._vertices)}
        self.dag = ResolutionDag(encoded["n"], encoded["cnf"])
        self._sink = _StrictRowSink(self.dag)
        self._edges = {}
        self.events = []
        self.finished = False

    def advance(self, vertex, direction, length):
        return self._vertices[(self._positions[vertex] + direction * length) % self.h]

    def _variables(self, i, j):
        item = self.encoded
        return (item["a"], item["b"], *item["triples"][i], *item["triples"][j])

    def _record(self, kind, first, **facts):
        self.events.append({"op":kind, "first_node":first, "after_node":len(self.dag.steps), **facts})
        return len(self.events)-1

    def edge(self, e, *, reverse=False):
        if self.finished or type(e) is not int or e not in self._directions:
            raise ValueError("invalid edge arrival")
        if e not in self._edges:
            block = self.encoded["blocks"][e]
            i, j = block["i"], block["j"]
            variables = self._variables(i, j)
            d = block["charge"]
            if tuple(block["variables"]) != variables or d not in (0,1):
                raise ValueError("input check has a different labeled scope")
            rows = {}
            first = len(self.dag.steps)
            for row in block["rows"]:
                bits = tuple(row["bits"])
                if len(bits)!=8 or any(v not in (0,1) for v in bits):
                    raise ValueError("malformed forbidden tuple")
                a,b = bits[:2]
                key = a,b,state_id(bits[2:5]),state_id(bits[5:])
                if key in rows or report(a,b,key[2]) ^ report(a,b,key[3]) == d:
                    raise ValueError("incorrect forbidden row for the check")
                ref = A["lift_row"](self._sink, row)
                if self.dag.clauses[ref] != exclusion(variables, bits):
                    raise ValueError("strict row is attached to a different original tuple")
                rows[key] = ref
            if set(rows) != set(forbidden(d)):
                raise ValueError("input check is missing a forbidden tuple")
            ev = self._record("edge", first, edge=e, left=i, right=j, charge=d, rows=len(rows))
            self._edges[e] = PathTable(self,i,self._directions[e],1,d,rows,ev)
        table = self._edges[e]
        return table.flipped() if reverse else table

    def join(self, left, right):
        if (self.finished or left.owner is not self or right.owner is not self or left.right != right.left
                or left.direction != right.direction or left.length+right.length >= self.h):
            raise ValueError("a join needs adjacent disjoint proper paths of this cycle")
        first = len(self.dag.steps)
        pivots = tuple(self.encoded["triples"][left.right][j] for j in self.middle_order)
        mids = []
        for bits in BITS3:
            xyz = [0,0,0]
            for pos, value in zip(self.middle_order, bits):
                xyz[pos] = value
            mids.append(state_id(xyz))
        charge = left.charge ^ right.charge
        variables = self._variables(left.left, right.right)
        rows = {}
        for a,b,u,w in forbidden(charge):
            leaves = []
            for v in mids:
                l = left.rows.get((a,b,u,v))
                r = right.rows.get((a,b,v,w))
                if (l is None) == (r is None):
                    raise ValueError("a forbidden tuple must fail exactly one child")
                leaves.append(r if l is None else l)
            ref = resolve_cube(self.dag, leaves, pivots)
            if self.dag.clauses[ref] != exclusion(variables, (a,b,*BITS3[u],*BITS3[w])):
                raise ValueError("join failed to recover the full endpoint row")
            rows[a,b,u,w] = ref
        ev = self._record("join",first,parents=[left.event,right.event],left=left.left,middle=left.right,
                          right=right.right,direction=left.direction,length=left.length+right.length,
                          charges=[left.charge,right.charge],charge=charge,rows=len(rows))
        return PathTable(self,left.left,left.direction,left.length+right.length,charge,rows,ev)

    def close(self, path, closing):
        if self.finished or path.owner is not self or closing.owner is not self:
            raise ValueError("closing tables must belong to this unfinished proof")
        if closing.left == path.right:
            closing = closing.flipped()
        if (path.left != closing.left or path.right != closing.right or path.direction == closing.direction
                or path.length+closing.length != self.h or len(self._edges) != self.h):
            raise ValueError("closing requires the two complementary intervals of the complete cycle")
        if path.charge == closing.charge:
            raise ValueError("even total charge admits a model")
        first = len(self.dag.steps)
        leaves = []
        for key in product((0,1),(0,1),range(8),range(8)):
            l, r = path.rows.get(key), closing.rows.get(key)
            if (l is None) == (r is None):
                raise ValueError("closing checks do not give disjoint complete exclusions")
            leaves.append(r if l is None else l)
        node = resolve_cube(self.dag, leaves, self._variables(path.left,path.right))
        if node != len(self.dag.steps)-1 or self.dag.clauses[node]:
            raise ValueError("empty is not the last actual proof node")
        self._record("close",first,parents=[path.event,closing.event],left=path.left,right=path.right,rows=256)
        self.finished = True
        stats = verify_resolution(self.dag)
        return self.dag, {**stats, "edges":self.h, "strict_clauses":len(self.dag.cnf),
                          "quadratic_nodes":quadratic_node_count(self.dag),
                          "middle_order":list(self.middle_order), "events":list(self.events)}


def prove_tree(encoded, tree, closing, *, reverse=False, middle_order=(2,0,1)):
    """Evaluate an ordered adjacent parenthesization of absolute original edge IDs."""
    builder = PathBuilder(encoded, middle_order=middle_order)
    if type(closing) is not int or not 0 <= closing < builder.h:
        raise ValueError("invalid closing edge")
    pending, values = [(tree, False)], []
    while pending:
        value, done = pending.pop()
        if type(value) is int:
            if value == closing:
                raise ValueError("closing edge used inside the open path")
            values.append(builder.edge(value, reverse=reverse))
        elif isinstance(value, (tuple,list)) and len(value)==2:
            if done:
                right, left = values.pop(), values.pop()
                values.append(builder.join(left, right))
            else:
                pending.extend(((value,True),(value[1],False),(value[0],False)))
        else:
            raise ValueError("a grouping is an edge ID or an ordered pair of groupings")
    if len(values) != 1:
        raise ValueError("incomplete parenthesization")
    return builder.close(values[0], builder.edge(closing, reverse=reverse))


def path_plan(h, grouping="left", *, start=0, reverse=False):
    if type(h) is not int or h<3 or type(start) is not int or not 0<=start<h:
        raise ValueError("invalid cycle size or original start vertex")
    order = [(start-i-1)%h if reverse else (start+i)%h for i in range(h)]
    items, closing = order[:-1], order[-1]
    if grouping == "left":
        tree = items[0]
        for item in items[1:]:
            tree = tree, item
    elif grouping == "balanced":
        def balanced(lo, hi):
            if hi-lo == 1:
                return items[lo]
            mid = (lo+hi)//2
            return balanced(lo,mid), balanced(mid,hi)
        tree = balanced(0,len(items))
    else:
        raise ValueError("unknown path grouping")
    return tree, closing


def path_refutation(charges, grouping="left", *, start=0, reverse=False, tree=None, middle_order=(2,0,1)):
    charges = tuple(charges)
    encoded = A["encode_cycle"](charges)
    if grouping == "optimal":
        plan, closing, _ = optimal_plan(charges, start=start, reverse=reverse, middle_order=middle_order)
    else:
        plan, closing = path_plan(len(charges), grouping, start=start, reverse=reverse)
    return prove_tree(encoded, plan if tree is None else tree, closing, reverse=reverse, middle_order=middle_order)


def lift_public(encoded, public):
    """Use the original private splitting variables and check the full resulting strict model."""
    n = encoded["n"]
    if len(public) != encoded["public_n"] + 1 or any(b not in (0,1) for b in public[1:]):
        raise ValueError("a complete original public assignment is required")
    model = list(public) + [0] * (n + 1 - len(public))
    def truth(lit):
        return model[abs(lit)] == int(lit > 0)
    for block in encoded["blocks"]:
        for row in block["rows"]:
            clause = row["clause"]
            if not any(truth(lit) for lit in clause):
                raise ValueError("public state violates an original forbidden row")
            waiting = not truth(clause[0])
            for lit, aux in zip(clause[1:6], row["aux"], strict=True):
                waiting = waiting and not truth(lit)
                model[aux] = int(waiting)
    if not all(any(truth(lit) for lit in clause) for clause in encoded["cnf"]):
        raise ValueError("failed to satisfy the actual strict formula")
    return tuple(model)


def even_model(encoded, *, shared=(0,0), first_report=0):
    """Return a checked model for A's ordered even cycle at the supplied shared values."""
    if len(shared) != 2 or any(v not in (0,1) for v in (*shared, first_report)):
        raise ValueError("shared and first-report values are Boolean")
    h = len(encoded["triples"])
    if len(encoded["blocks"]) != h:
        raise ValueError("expected the original ordered cycle")
    a,b = shared
    public = [0] * (encoded["public_n"] + 1)
    public[encoded["a"]], public[encoded["b"]] = a,b
    value = first_report
    for i, block in enumerate(encoded["blocks"]):
        if (block["i"], block["j"]) != (i, (i+1)%h):
            raise ValueError("expected the original ordered cycle")
        assignment = (0,0,0) if not value else ((0,0,1) if a & b else (1,1,1))
        for name, v in zip(encoded["triples"][i], assignment, strict=True):
            public[name] = v
        value ^= block["charge"]
    if value != first_report:
        raise ValueError("odd total charge has no model")
    return lift_public(encoded, public)


def join_cost(c, d, *, middle_order=(2,0,1), primitive=False):
    """Count distinct ordinary resolutions, or their primitive nodes, at a fresh middle vertex."""
    order = tuple(middle_order)
    if sorted(order)!=[0,1,2] or c not in (0,1) or d not in (0,1):
        raise ValueError("expected two charges and a permutation of the middle bits")
    cost = 0
    for a,b in product((0,1), repeat=2):
        observations = [report(a,b,v) for v in range(8)]
        weight = [observations.count(0), observations.count(1)]
        forbidden_pairs = sum(weight[x]*weight[1^x^c^d] for x in (0,1))
        for depth in range(3):
            for prefix in product((0,1), repeat=depth):
                allowed = [v for v in range(8) if all(BITS3[v][order[j]] == bit for j,bit in enumerate(prefix))]
                children = [{observations[v] for v in allowed if BITS3[v][order[depth]] == b} for b in (0,1)]
                values = children[0] | children[1]
                if len(values) == 2:
                    node_count = forbidden_pairs
                else:
                    t, = values
                    node_count = weight[1^t^c] + weight[1^t^d]
                # Two structural steps plus both shared literals, the fixed middle prefix,
                # and three repeated literals for each endpoint side retained by both children.
                unit_cost = 4+depth+3*len(children[0] & children[1]) if primitive else 1
                cost += node_count * unit_cost
    return cost


def optimal_plan(charges, *, start=0, reverse=False, middle_order=(2,0,1)):
    """Minimize the ordinary node count in this ordered endpoint-table construction."""
    charges = tuple(charges)
    if any(c not in (0,1) for c in charges):
        raise ValueError("Boolean charges required")
    _, closing = path_plan(len(charges), start=start, reverse=reverse)
    h = len(charges)
    entries = [(start-i-1)%h if reverse else (start+i)%h for i in range(h-1)]
    parity = [0]
    for e in entries:
        parity.append(parity[-1] ^ charges[e])
    costs = {(i,i+1):0 for i in range(h-1)}
    trees = {(i,i+1):e for i,e in enumerate(entries)}
    weights = {(c,d):join_cost(c,d,middle_order=middle_order) for c,d in product((0,1),repeat=2)}
    for width in range(2,h):
        for i in range(h-width):
            j = i+width
            value, mid = min((costs[i,q]+costs[q,j]+weights[parity[i]^parity[q],parity[q]^parity[j]], q)
                             for q in range(i+1,j))
            costs[i,j] = value
            trees[i,j] = trees[i,mid], trees[mid,j]
    return trees[0,h-1], closing, costs[0,h-1]


def cnf_digest(cnf):
    """Hash the compact JSON of each original clause followed by one newline, in input order."""
    result = sha256()
    for row in cnf:
        result.update(json.dumps(row, separators=(",",":")).encode() + b"\n")
    return result.hexdigest()


def certificate_text(dag):
    """One genuine axiom or signed resolution per line, with implicit zero-based node IDs."""
    verify_resolution(dag)
    lines = [f"signed-resolution-v1 {dag.n} {len(dag.cnf)} {cnf_digest(dag.cnf)}"]
    for rule, *arguments in dag.steps:
        tag = "a" if rule == "axiom" else "r"
        lines.append(tag + " " + " ".join(map(str, arguments)))
    return "\n".join(lines)+"\n"


def read_certificate(encoded, text):
    """Read the signed parent list independently of the path constructor and verify its final empty."""
    lines = text.splitlines()
    header = ["signed-resolution-v1",str(encoded["n"]),str(len(encoded["cnf"])),cnf_digest(encoded["cnf"])]
    if not lines or lines[0].split() != header:
        raise ValueError("certificate is bound to a different original CNF")
    d = ResolutionDag(encoded["n"],encoded["cnf"])
    for i, raw in enumerate(lines[1:]):
        fields = raw.split()
        if not fields:
            raise ValueError("empty instruction")
        args = list(map(int, fields[1:]))
        if fields[0] == "a" and len(args) == 1 and 0 <= args[0] < len(d.cnf):
            row = set(d.cnf[args[0]])
            step = ("axiom",args[0])
        elif fields[0] == "r" and len(args) == 3:
            p,q,lit = args
            if not (0 <= p < i and 0 <= q < i and lit in d.clauses[p] and -lit in d.clauses[q]):
                raise ValueError("invalid signed resolution in stored certificate")
            row = (set(d.clauses[p])-{lit}) | (set(d.clauses[q])-{-lit})
            step = ("resolve",p,q,lit)
        else:
            raise ValueError("malformed stored instruction")
        d.steps.append(step)
        d.clauses.append(tuple(sorted(row)))
    verify_resolution(d)
    return d
