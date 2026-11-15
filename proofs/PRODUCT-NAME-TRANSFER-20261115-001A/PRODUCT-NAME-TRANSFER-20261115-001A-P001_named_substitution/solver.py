"""Sequential Boolean product names in syntactic degree-two resolution."""

from collections import Counter
from functools import cache
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
OLD = "QUADRATIC-ROUTE-TRANSFER-20261115-001A"
old_file = ROOT / "proofs" / OLD / (OLD + "-P001_quadratic_substitution") / "solver.py"
spec = spec_from_file_location("checked_base_quadratic_solver", old_file)
q = module_from_spec(spec)
spec.loader.exec_module(q)
ZERO, ONE = q.ZERO, q.ONE
var, add, mul, literal, signed_clause = q.var, q.add, q.mul, q.literal, q.signed_clause


def affine(raw, live):
    form = q.polynomial(raw,live)
    q.require(all(len(term) <= 1 for term in form), "a product definition factor must be affine")
    return form


class Dag(q.Dag):
    def __init__(self, n, cnf, *, convention="multiset"):
        q.validate_cnf(n,cnf)
        super().__init__(cnf,convention=convention)
        self.n = n
        self.live = n

    def emit(self, rule, atoms, **fields):
        atoms = tuple(atoms)
        if rule == "define":
            name = fields["variable"]
            q.require(type(name) is int and name==self.live+1 and not fields.get("parents")
                      and len(fields["factors"])==2 and len(atoms)==1,"malformed fresh declaration")
            f,g = (affine(raw,self.live) for raw in fields["factors"])
            q.require(q.checked_poly(atoms[0],name)==q.add(q.var(name),q.mul(f,g)),"wrong defining equation")
        else:
            for expression in mentioned_forms({"rule":rule,"clause":atoms,**fields}):
                q.checked_poly(expression,self.live)
            if rule == "boolean":
                q.require(1 <= fields["variable"] <= self.live,"excluded-middle variable is not yet available")
        node = super().emit(rule,atoms,**fields)
        if rule == "define":
            self.live += 1
        return node

    def define(self, f, g):
        f, g = affine(f,self.live), affine(g,self.live)
        name = self.live + 1
        ref = self.emit("define",(q.add(q.var(name),q.mul(f,g)),),variable=name,
                        factors=[q.encode(f),q.encode(g)])
        return name, ref


def mentioned_forms(node):
    yield from node["clause"]
    if node["rule"] in ("multiply","contract"):
        yield node["chosen"]
    if node["rule"] == "multiply":
        yield node["multiplier"]
    if node["rule"] == "combine":
        yield from node["chosen"]


def scan_declarations(n, cnf, proof):
    """Check the complete causal language before any ambient-roster proof check."""
    q.validate_cnf(n,cnf)
    known = n
    declared_at = {}
    dependencies = []
    levels = {}
    for i,node in enumerate(proof):
        ids = node.get("parents",[])
        q.require(all(type(j) is int and 0 <= j < i for j in ids), "bad parent before declaration checking")
        rule = node["rule"]
        if rule == "define":
            v = node["variable"]
            q.require(type(v) is int and v == known+1 and not ids, "definition must introduce the next fresh name")
            q.require(len(node["factors"]) == 2 and len(node["clause"]) == 1,
                      "declaration needs two factors and one defining equation")
            f,g = (affine(a,known) for a in node["factors"])
            expected = q.add(q.var(v),q.mul(f,g))
            q.require(q.checked_poly(node["clause"][0],v) == expected, "incorrect formal defining equation")
            names = {name for form in (f,g) for term in form for name in term}
            levels[v] = 1 + max((levels.get(u,0) for u in names),default=0)
            dependencies.append(tuple(sorted(declared_at[u] for u in names if u>n)))
            declared_at[v] = i
            known = v
        else:
            if rule == "axiom":
                j = node.get("axiom")
                q.require(type(j) is int and 0 <= j < len(cnf), "ordinary axiom must cite the genuine input CNF")
            if rule == "boolean":
                v = node["variable"]
                q.require(type(v) is int and 1 <= v <= known, "Boolean default before its variable exists")
            names = set()
            for raw in mentioned_forms(node):
                # Inspect written support as well as reduced terms, including a
                # multiplier that disappears from the result because f is zero.
                for term in raw:
                    for v in term:
                        q.require(type(v) is int and 1 <= v <= known, "undeclared name in a proof expression")
                        if v>n:
                            names.add(v)
            dependencies.append(tuple(sorted(declared_at[v] for v in names)))
    return known, declared_at, dependencies, max(levels.values(),default=0)


def ancestors(n, cnf, proof, *, include_declarations=True):
    """Indices needed for the final line, with implicit name declarations on by default."""
    _,_,declarations,_ = scan_declarations(n,cnf,proof)
    q.require(proof,"empty proof")
    seen = set()
    todo = [len(proof)-1]
    while todo:
        i = todo.pop()
        if i in seen:
            continue
        seen.add(i)
        todo.extend(proof[i].get("parents",[]))
        if include_declarations:
            todo.extend(declarations[i])
    return sorted(seen)


def verify(n, cnf, proof, *, convention="multiset", strict_set=False):
    """Validate definitions and apply the terminal syntactic kernel to all ordinary rules."""
    final_n, declared, dependencies, depth = scan_declarations(n,cnf,proof)
    if not declared:
        stats = q.verify(n,cnf,proof,convention=convention,strict_set=strict_set)
    else:
        # The extra empty premise is local to the inference checker. It may
        # stand in only for already validated definitions. Input axiom IDs and
        # parent IDs were range-checked before this disjoint renumbering.
        shadow = [{"rule":"axiom","axiom":len(cnf),"clause":[]}]
        for node in proof:
            if node["rule"] == "define":
                shadow.append({"rule":"weaken","parents":[0],"clause":node["clause"]})
            else:
                shadow.append({**node,"parents":[i+1 for i in node.get("parents",[])]})
        q.verify(final_n,[*cnf,[]],shadow,convention=convention,strict_set=strict_set)
        q.require(proof and not proof[-1]["clause"], "the genuine proof must end in empty")
        counts = Counter(row["rule"] for row in proof)
        refs = Counter(j for row in proof for j in row.get("parents",[]))
        stats = {"lines":len(proof),"rules":dict(sorted(counts.items())),"shared_parents":sum(v>1 for v in refs.values()),
                 "max_width":max(len(q.clause((q.polynomial(f) for f in row["clause"]),convention)) for row in proof)}
    return {**stats,"base_variables":n,"declarations":len(declared),"final_variables":final_n,
            "maximum_definition_depth":depth,"declaration_references":sum(map(len,dependencies))}


def translated(source_n, source_cnf, target_n, target_cnf, images, target_proof, *, convention="multiset"):
    before = verify(target_n,target_cnf,target_proof,convention=convention)
    q.validate_cnf(source_n,source_cnf)
    base = q.image_map(source_n,target_n,images)
    plans = q.axiom_plans(source_n,source_cnf,target_cnf,base)
    d = before["declarations"]
    # The old external sentinel +(n+1) denotes one, while the first fresh
    # internal source variable really is n+1. Preserve both meanings.
    target_const = source_n+1
    ext_const = source_n+d+1
    extended = [v if abs(v) != target_const else (ext_const if v>0 else -ext_const) for v in base]
    extended.extend(range(source_n+1,source_n+d+1))
    project = q.substitution(source_n+d,extended)
    out = Dag(source_n,source_cnf,convention=convention)
    refs, repairs = [], Counter()

    @cache
    def source_leaf(i):
        start = out.axiom(i)
        end = out.contract_all(start)
        repairs["source_duplicate_contractions"] += end-start
        return end

    def image(raw):
        return project(q.polynomial(raw))

    for node in target_proof:
        rule = node["rule"]
        parents = [refs[i] for i in node.get("parents",[])]
        child = q.clause((image(f) for f in node["clause"]),convention)
        if rule == "define":
            v,ref = out.define(*(image(f) for f in node["factors"]))
            q.require(v == source_n + node["variable"]-target_n and out.clauses[ref] == child,
                      "the fresh source definition is not the full image")
        elif rule == "axiom":
            kind,i = plans[node["axiom"]]
            ref = source_leaf(i) if kind == "axiom" else out.true() if kind == "true" else out.boolean(i)
        elif rule == "true":
            ref = out.true()
        elif rule == "boolean":
            v = extended[node["variable"]-1]
            ref = out.true() if abs(v)==ext_const else out.boolean(abs(v))
        elif rule == "weaken":
            ref = out.weaken(parents[0],child)
        elif rule == "multiply":
            ref = out.multiply(parents[0],image(node["chosen"]),image(node["multiplier"]))
        elif rule == "contract":
            ref = out.contract(parents[0],image(node["chosen"]))
        elif rule == "delete_false":
            ref = out.delete_false(parents[0])
        else:
            f,g = map(image,node["chosen"])
            ref = out.combine(*parents,f,g,*node["coefficients"])
        if out.clauses[ref] != child:
            initial = rule in ("axiom","true","boolean")
            q.require(initial or (convention=="set" and rule!="define"), "illegal noninitial repair")
            ref = out.weaken(ref,child)
            repairs["axiom_weakening" if initial else "set_context_weakening"] += 1
        refs.append(ref)
    if refs[-1] != len(out.proof)-1:
        q.require(not out.clauses[refs[-1]],"final reference is not empty")
        out.weaken(refs[-1],())
    after = verify(source_n,source_cnf,out.proof,convention=convention,strict_set=True)
    old_seeds = sum(key[0] != "boolean" or key[1] <= source_n for key in out.seeds)
    bound = min(2*before["lines"]-d,before["lines"]+old_seeds+repairs["set_context_weakening"])
    bound += repairs["source_duplicate_contractions"]
    q.require(after["lines"] <= bound and after["declarations"] == d and
              after["maximum_definition_depth"] == before["maximum_definition_depth"],
              "named transport changed declaration depth, count, or exceeded its node bound")
    return out.proof, {"target":before,"source":after,"old_source_seeds":old_seeds,"verified_node_bound":bound,
                       "axiom_images":dict(sorted(Counter(k for k,_ in plans).items())),"repairs":dict(sorted(repairs.items()))}


def backtranslate(source_n, source_cnf, target_n, target_cnf, images, target_proof, *, convention="multiset"):
    return translated(source_n,source_cnf,target_n,target_cnf,images,target_proof,convention=convention)[0]
