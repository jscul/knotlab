"""Explicit syntactic Res(PC_2/F2) DAG builder, verifier, and literal backtranslation."""

from collections import Counter
from functools import cache
from itertools import chain, product


ZERO = ()
ONE = ((),)


def require(test, message):
    if not test:
        raise ValueError(message)


def var(i):
    require(type(i) is int and i >= 1, "invalid variable")
    return ((i,),)


def polynomial(monomials, n=None):
    """Canonical sparse formal polynomial. Repeated factors in a term are significant."""
    support = set()
    for term in monomials:
        term = tuple(term)
        require(all(type(i) is int and i > 0 and (n is None or i <= n) for i in term),
                "invalid polynomial variable")
        term = tuple(sorted(term))
        support.symmetric_difference_update((term,))
    return tuple(sorted(support))


def add(f, g):
    return polynomial(chain(f, g))


def mul(f, g):
    return polynomial(tuple(a) + tuple(b) for a in f for b in g)


def literal(lit):
    require(type(lit) is int and lit != 0, "invalid signed CNF literal")
    return add(ONE, var(lit)) if lit > 0 else var(-lit)


def signed_clause(lits):
    return tuple(sorted(literal(lit) for lit in lits))


def encode(f):
    return [list(term) for term in f]


def clause(atoms, convention):
    require(convention in ("multiset", "set"), "unknown context convention")
    return tuple(sorted(set(atoms) if convention == "set" else atoms))


def removes(row, f):
    require(f in row, "selected occurrence absent from parent")
    index = row.index(f)
    return row[:index] + row[index+1:]


def checked_poly(raw, n):
    f = polynomial(raw, n)
    require(all(len(term) <= 2 for term in f), "displayed polynomial has degree above two")
    return f


class Dag:
    """Construct primitive steps. The resolve and contract_all methods expand into these steps."""

    def __init__(self, cnf, *, convention="multiset"):
        require(convention in ("multiset", "set"), "unknown context convention")
        self.cnf = cnf
        self.convention = convention
        self.proof = []
        self.clauses = []
        self.seeds = {}

    def emit(self, rule, atoms, **fields):
        value = clause(atoms, self.convention)
        require(all(all(len(term) <= 2 for term in f) for f in value), "output degree above two")
        self.proof.append({"rule": rule, "clause": [encode(f) for f in value], **fields})
        self.clauses.append(value)
        return len(self.proof) - 1

    def seed(self, key, rule, atoms, **fields):
        if key not in self.seeds:
            self.seeds[key] = self.emit(rule, atoms, **fields)
        return self.seeds[key]

    def axiom(self, i):
        require(type(i) is int and 0 <= i < len(self.cnf), "invalid input axiom")
        return self.seed(("axiom", i), "axiom", signed_clause(self.cnf[i]), axiom=i)

    def true(self):
        return self.seed(("true",), "true", (ZERO,))

    def boolean(self, i):
        return self.seed(("boolean", i), "boolean", (var(i), add(ONE, var(i))), variable=i)

    def weaken(self, node, full_target_clause):
        target = clause((polynomial(f) for f in full_target_clause), self.convention)
        require(Counter(self.clauses[node]) <= Counter(target), "weakening discarded an occurrence")
        return self.emit("weaken", target, parents=[node])

    def multiply(self, node, distinguished, multiplier):
        f, g = polynomial(distinguished), checked_poly(multiplier, None)
        return self.emit("multiply", (*removes(self.clauses[node], f), mul(f, g)),
                         parents=[node], chosen=encode(f), multiplier=encode(g))

    def combine(self, left, right, chosen_l, chosen_r, alpha=1, beta=1):
        require(type(alpha) is int and type(beta) is int and alpha in (0, 1) and beta in (0, 1),
                "invalid F2 scalar")
        f, g = polynomial(chosen_l), polynomial(chosen_r)
        result = add(f if alpha else ZERO, g if beta else ZERO)
        return self.emit("combine", (*removes(self.clauses[left], f), *removes(self.clauses[right], g), result),
                         parents=[left, right], chosen=[encode(f), encode(g)], coefficients=[alpha, beta])

    def delete_false(self, node):
        return self.emit("delete_false", removes(self.clauses[node], ONE), parents=[node])

    def contract(self, node, repeated_poly):
        f, row = polynomial(repeated_poly), self.clauses[node]
        require(row.count(f) >= (2 if self.convention == "multiset" else 1), "nothing to contract")
        result = removes(row, f) if self.convention == "multiset" else row
        return self.emit("contract", result, parents=[node], chosen=encode(f))

    def contract_all(self, node):
        for f, copies in Counter(self.clauses[node]).items():
            for _ in range(copies - 1):
                node = self.contract(node, f)
        return node

    def resolve(self, left, right, signed_pivot):
        """Ordinary resolution followed by primitive false deletion and duplicate contractions."""
        ref = self.combine(left, right, literal(signed_pivot), literal(-signed_pivot))
        return self.contract_all(self.delete_false(ref))


def validate_cnf(n, cnf):
    require(type(n) is int and n >= 0, "invalid variable roster")
    for row in cnf:
        require(all(type(v) is int and 1 <= abs(v) <= n for v in row), "CNF literal outside declared roster")


def verify(n, cnf, proof, *, convention="multiset", strict_set=False):
    """Independent rule checker: count side occurrences and compare formal coefficients."""
    validate_cnf(n, cnf)
    require(convention in ("multiset", "set"), "unknown context convention")
    rows, uses, rules = [], Counter(), Counter()
    expected_arity = {"axiom": 0, "true": 0, "boolean": 0, "weaken": 1, "contract": 1,
                      "delete_false": 1, "multiply": 1, "combine": 2}
    for index, step in enumerate(proof):
        rule = step["rule"]
        ids = step.get("parents", [])
        require(rule in expected_arity and len(ids) == expected_arity[rule], "unknown rule or incorrect arity")
        require(all(type(i) is int and 0 <= i < index for i in ids), "invalid parent reference")
        rows_of_parents = [rows[i] for i in ids]
        value = Counter(clause((checked_poly(f, n) for f in step["clause"]), convention))
        optional = []
        if rule == "axiom":
            j = step.get("axiom")
            require(type(j) is int and 0 <= j < len(cnf), "invalid source axiom ID")
            expected = Counter(signed_clause(cnf[j]))
        elif rule == "true":
            expected = Counter([ZERO])
        elif rule == "boolean":
            i = step.get("variable")
            require(type(i) is int and 1 <= i <= n, "invalid excluded-middle variable")
            expected = Counter([((i,),), ((), (i,))])
        elif rule == "weaken":
            require(rows_of_parents[0] <= value, "invalid syntactic weakening")
            expected = value
        elif rule == "contract":
            f = checked_poly(step["chosen"], n)
            expected = rows_of_parents[0].copy()
            require(expected[f] >= (2 if convention == "multiset" else 1), "contraction lacks two copies")
            if convention == "multiset":
                expected[f] -= 1
        else:
            selected = ([ONE] if rule == "delete_false" else
                        [checked_poly(f, n) for f in step["chosen"]] if rule == "combine" else
                        [checked_poly(step["chosen"], n)])
            require(len(selected) == len(ids), "incorrect number of selected atoms")
            expected = Counter()
            for parent, f in zip(rows_of_parents, selected):
                require(parent[f] > 0, "selected atom absent from the proof parent")
                side = parent.copy()
                side[f] -= 1
                expected.update(side)
            if rule == "combine":
                scalars = step["coefficients"]
                require(len(scalars) == 2 and all(type(a) is int and a in (0, 1) for a in scalars),
                        "invalid linear-combination scalars")
                terms = Counter(t for a, f in zip(scalars, selected) if a for t in f)
                expected[tuple(sorted(t for t in terms if terms[t] % 2))] += 1
            elif rule == "multiply":
                g = checked_poly(step["multiplier"], n)
                terms = Counter(tuple(sorted(a + b)) for a, b in product(selected[0], g))
                result = tuple(sorted(t for t in terms if terms[t] % 2))
                require(all(len(t) <= 2 for t in result), "formal product exceeds the degree cap")
                expected[result] += 1
            optional = selected
        if convention == "set":
            needed = set(+expected)
            permitted = needed if strict_set else needed | set(optional)
            require(needed <= set(value) <= permitted, "invalid set side contexts or rule result")
        else:
            require(value == +expected, "invalid exact occurrence counts or formal rule result")
        rows.append(value)
        uses.update(ids)
        rules[rule] += 1
    require(rows and not rows[-1], "refutation must end with the empty clause")
    return {"lines": len(rows), "rules": dict(sorted(rules.items())),
            "shared_parents": sum(count > 1 for count in uses.values()),
            "max_width": max(sum(c.values()) for c in rows)}


def image_map(n, target_n, images):
    if isinstance(images, dict):
        require(len(images) == target_n and all(i in images or str(i) in images for i in range(1, target_n + 1)),
                "map must cover every target variable")
        result = [images[i] if i in images else images[str(i)] for i in range(1, target_n + 1)]
    else:
        require(len(images) in (target_n, target_n + 1), "wrong length of the literal image list")
        result = list(images) if len(images) == target_n else list(images[1:])
    require(all(type(v) is int and 1 <= abs(v) <= n + 1 for v in result), "invalid signed literal image")
    return result


def substitution(n, images):
    values = [(ONE if v > 0 else ZERO) if abs(v) == n+1 else (var(v) if v > 0 else add(ONE, var(-v)))
              for v in images]

    @cache
    def image(f):
        result = ZERO
        for term in f:
            monomial = ONE
            for i in term:
                monomial = mul(monomial, values[i-1])
            result = add(result, monomial)
        return result

    return image


def axiom_plans(source_n, source_cnf, target_cnf, table):
    """Check every literal axiom image and identify an actual syntactic seed."""
    lookup = {}
    for i, row in enumerate(source_cnf):
        key = frozenset(row)
        if key not in lookup or len(row) < len(source_cnf[lookup[key]]):
            lookup[key] = i
    plans = []
    const = source_n + 1
    for row in target_cnf:
        named = {table[abs(v)-1] * (1 if v > 0 else -1) for v in row}
        if const in named:
            plan = ("true", 0)
        elif any(-v in named for v in named):
            plan = ("boolean", min(abs(v) for v in named if -v in named))
        else:
            key = frozenset(named - {-const})
            require(key in lookup, "non-tautological image is not an exact source CNF clause")
            plan = ("axiom", lookup[key])
        plans.append(plan)
    return plans


def translated(source_n, source_cnf, target_n, target_cnf, images, target_proof, *, convention="multiset"):
    before = verify(target_n, target_cnf, target_proof, convention=convention)
    validate_cnf(source_n, source_cnf)
    table = image_map(source_n, target_n, images)
    project = substitution(source_n, table)
    plans = axiom_plans(source_n, source_cnf, target_cnf, table)
    const = source_n + 1
    out = Dag(source_cnf, convention=convention)
    refs, repairs = [], Counter()

    @cache
    def source_seed(i):
        node = out.axiom(i)
        end = out.contract_all(node)
        repairs["source_duplicate_contractions"] += len(source_cnf[i])-len(set(source_cnf[i])) if convention == "multiset" else 0
        return end

    for step in target_proof:
        rule = step["rule"]
        target = clause((project(polynomial(f)) for f in step["clause"]), convention)
        parents = [refs[i] for i in step.get("parents", [])]
        if rule == "axiom":
            kind, i = plans[step["axiom"]]
            ref = source_seed(i) if kind == "axiom" else out.true() if kind == "true" else out.boolean(i)
        elif rule == "true":
            ref = out.true()
        elif rule == "boolean":
            v = abs(table[step["variable"]-1])
            ref = out.true() if v == const else out.boolean(v)
        elif rule == "weaken":
            ref = out.weaken(parents[0], target)
        elif rule == "contract":
            ref = out.contract(parents[0], project(polynomial(step["chosen"])))
        elif rule == "delete_false":
            ref = out.delete_false(parents[0])
        elif rule == "multiply":
            ref = out.multiply(parents[0], project(polynomial(step["chosen"])), project(polynomial(step["multiplier"])))
        else:
            f, g = (project(polynomial(p)) for p in step["chosen"])
            ref = out.combine(*parents, f, g, *step["coefficients"])
        if out.clauses[ref] != target:
            require(rule in ("axiom", "true", "boolean") or convention == "set",
                    "multiset inference failed to commute with substitution")
            ref = out.weaken(ref, target)
            repairs["axiom_weakening" if rule in ("axiom", "true", "boolean") else "set_context_weakening"] += 1
        refs.append(ref)
    # An input empty axiom may be reused as the final target node after other
    # lines. Keep its occurrence last, as required by an explicit refutation.
    if refs[-1] != len(out.proof)-1:
        require(not out.clauses[refs[-1]], "last reference is not empty")
        out.weaken(refs[-1], ())
    after = verify(source_n, source_cnf, out.proof, convention=convention, strict_set=True)
    source_seeds = len(out.seeds)
    bound = min(2*before["lines"], before["lines"] + source_seeds + repairs["set_context_weakening"])
    bound += repairs["source_duplicate_contractions"]
    require(after["lines"] <= bound, "transport exceeded the node bound")
    return out.proof, {"target": before, "source": after, "repairs": dict(sorted(repairs.items())),
                       "distinct_source_seeds": source_seeds, "verified_node_bound": bound,
                       "axiom_images": dict(sorted(Counter(kind for kind, _ in plans).items()))}


def backtranslate(source_n, source_cnf, target_n, target_cnf, images, target_proof, *, convention="multiset"):
    return translated(source_n, source_cnf, target_n, target_cnf, images, target_proof, convention=convention)[0]
