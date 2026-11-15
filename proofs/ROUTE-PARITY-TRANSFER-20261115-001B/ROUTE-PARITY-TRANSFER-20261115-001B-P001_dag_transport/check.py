#!/usr/bin/env python3
"""Translate and independently verify explicit DAG refutations over F2."""

import argparse
import json
import runpy
import sys
from collections import Counter
from functools import cache
from itertools import product
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
HDW = (ROOT / "proofs/COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HDW"
       / "COMPRESSION-ROBUST-PROOF-COMPLEXITY-001HDW-P001_common_restriction_conversion/converter.py")
CORRIDORS = (ROOT / "proofs/TWO-RELAY-PADDING-20261115-001A"
             / "TWO-RELAY-PADDING-20261115-001A-P001_track_regrouping/check.py")
FALSE = (0, 1)


def require(test, message):
    if not test:
        raise ValueError(message)


def atom(literal):
    require(type(literal) is int and literal != 0, "variable literals need nonzero integer names")
    return (1 << (abs(literal) - 1), int(literal > 0))


def encode(rows):
    return [list(row) for row in sorted(set(rows))]


def signed_clause(lits):
    return encode(atom(lit) for lit in lits)


def equation(n, pair):
    require(isinstance(pair, (list, tuple)) and len(pair) == 2, "an equation needs a mask and a right side")
    m, b = pair
    require(type(m) is int and 0 <= m and m.bit_length() <= n and type(b) is int and b in (0, 1),
            "equation uses an undeclared variable or nonbinary value")
    return m, b


def validate_cnf(n, cnf):
    require(type(n) is int and n >= 0, "invalid variable count")
    for clause in cnf:
        require(all(type(lit) is int and 1 <= abs(lit) <= n for lit in clause), "axiom outside its roster")


def inconsistent(equations):
    # This verifier reduces by the lowest present variable. The imported HDW
    # producer instead uses a highest-variable echelon basis and row membership.
    pivots = {}
    for mask, value in equations:
        while mask:
            low = mask & -mask
            if low not in pivots:
                pivots[low] = (mask, value)
                break
            other, bit = pivots[low]
            mask ^= other
            value ^= bit
        if not mask and value:
            return True
    return False


def follows(premise, conclusion):
    if premise <= conclusion:
        return True
    negated = [(m, b ^ 1) for m, b in conclusion]
    return all(inconsistent([*negated, literal]) for literal in premise)


def verify(n, cnf, proof):
    """Check actual axiom IDs, earlier parents, each inference, and an empty final node."""
    validate_cnf(n, cnf)
    clauses, depths, used = [], [], Counter()
    for i, node in enumerate(proof):
        rule = node["rule"]
        row = frozenset(equation(n, pair) for pair in node["clause"])
        ids = node.get("parents", [])
        require(all(type(j) is int and 0 <= j < i for j in ids), "forward, negative or invalid parent ID")
        if rule == "axiom":
            ax = node.get("axiom")
            require(not ids and type(ax) is int and 0 <= ax < len(cnf) and row == frozenset(map(atom, cnf[ax])),
                    "initial line is not its cited CNF axiom")
            depth = 0
        elif rule == "weaken":
            require(len(ids) == 1 and follows(clauses[ids[0]], row), "invalid single-parent semantic weakening")
            depth = depths[ids[0]]
        elif rule == "resolve":
            require(len(ids) == 2, "resolution needs two parent IDs")
            left, right = (clauses[j] for j in ids)
            p = equation(n, node["pivot"])
            q = (p[0], p[1] ^ 1)
            require(p in left and q in right, "complementary resolution pivot is missing")
            required = (left - {p}) | (right - {q})
            # Contexts may already contain the pivot. With set-disjunction the
            # authorized children range from the exact deletion to retaining it.
            require(required <= row <= (required | {p, q}), "resolution result has an invalid side context")
            depth = 1 + max(depths[j] for j in ids)
        else:
            raise ValueError("unrecognized proof rule")
        clauses.append(row)
        depths.append(depth)
        used.update(ids)
    require(clauses and not clauses[-1], "a refutation must end in the empty clause")
    return {"lines": len(clauses), "resolution_depth": depths[-1], "shared_parents": sum(v > 1 for v in used.values())}


@cache
def hdw():
    return runpy.run_path(str(HDW))


def image_table(n, target_n, images):
    if isinstance(images, dict):
        require(len(images) == target_n, "the map needs exactly one image per target variable")
        require(all(i in images or str(i) in images for i in range(1, target_n + 1)),
                "a declared target variable has no image")
        ordered = [images[i] if i in images else images[str(i)] for i in range(1, target_n + 1)]
    else:
        require(len(images) in (target_n, target_n + 1), "image list has the wrong length")
        ordered = list(images) if len(images) == target_n else list(images[1:])
    result = []
    for lit in ordered:
        require(type(lit) is int and 1 <= abs(lit) <= n + 1, "invalid signed source literal or constant")
        if abs(lit) == n + 1:
            result.append((0, int(lit > 0)))
        else:
            result.append((1 << (abs(lit) - 1), int(lit < 0)))
    return tuple(result)


def translated(source_n, source_cnf, target_n, target_cnf, images, target_proof):
    before = verify(target_n, target_cnf, target_proof)
    validate_cnf(source_n, source_cnf)
    source_lookup = {frozenset(map(atom, row)): i for i, row in enumerate(source_cnf)}
    mapping = image_table(source_n, target_n, images)
    engine = hdw()
    substitute = cache(lambda row: engine["image_eq"](row, mapping))
    is_taut = cache(engine["taut"])

    def image_clause(clause):
        return frozenset(substitute(tuple(row)) for row in clause) - {FALSE}

    initial = []
    for axiom in target_cnf:
        # Ordinary raw CNF can have many large variable IDs. Pull each named
        # literal back directly, without allocating a dense target mask for it.
        new = set()
        for literal in axiom:
            mask, offset = mapping[abs(literal) - 1]
            new.add((mask, int(literal > 0) ^ offset))
        canonical = frozenset(new) - {FALSE}
        tautological = is_taut(canonical)
        require(tautological or canonical in source_lookup, "non-tautological target axiom image absent from exact source")
        initial.append(None if tautological else source_lookup[canonical])
    refs, output = [], []
    counts = Counter()
    for node in target_proof:
        child = image_clause(node["clause"])
        if is_taut(child):
            if node["rule"] == "resolve" and all(refs[j] is None for j in node["parents"]):
                counts["both_premises_tautological"] += 1
            counts["tautological_nodes_omitted"] += 1
            refs.append(None)
            continue
        rec = {"clause": encode(child)}
        if node["rule"] == "axiom":
            rec.update(rule="axiom", axiom=initial[node["axiom"]])
        elif node["rule"] == "weaken":
            ref = refs[node["parents"][0]]
            require(ref is not None, "tautological premise weakened to a non-tautology")
            rec.update(rule="weaken", parents=[ref[0]])
            counts["semantic_weakening"] += 1
        else:
            left, right = (refs[j] for j in node["parents"])
            pivot = substitute(tuple(node["pivot"]))
            opp = (pivot[0], pivot[1] ^ 1)
            if left is None or right is None:
                live = right if left is None else left
                require(live is not None, "two tautological parents cannot create a non-tautological conclusion")
                rec.update(rule="weaken", parents=[live[0]])
                counts["one_tautological_parent"] += 1
                counts["constant_pivot"] += int(pivot[0] == 0)
            else:
                require(pivot[0] and pivot in left[1] and opp in right[1], "live parents lost a pivot")
                minimal = (left[1] - {pivot}) | (right[1] - {opp})
                if minimal == child:
                    rec.update(rule="resolve", parents=[left[0], right[0]], pivot=list(pivot))
                    counts["canonical_resolution"] += 1
                else:
                    live = left if pivot in child else right
                    require(minimal < child and child <= (minimal | {pivot, opp}) and live[1] <= child,
                            "an aliased pivot failed the one-step weakening condition")
                    rec.update(rule="weaken", parents=[live[0]])
                    counts["retained_pivot_weakening"] += 1
        refs.append((len(output), child))
        output.append(rec)
    after = verify(source_n, source_cnf, output)
    require(after["lines"] <= before["lines"] and after["resolution_depth"] <= before["resolution_depth"],
            "transport exceeded its rule count or depth")
    return output, {"target": before, "source": after, "cases": dict(sorted(counts.items())),
                    "target_axioms": len(initial), "tautological_axiom_images": initial.count(None),
                    "source_axiom_indices_reached": sorted({i for i in initial if i is not None})}


def backtranslate(source_n, source_cnf, target_n, target_cnf, images, target_proof):
    return translated(source_n, source_cnf, target_n, target_cnf, images, target_proof)[0]


class Dag:
    """Construct explicit finite test proofs. Only identical axiom indices are shared."""

    def __init__(self, axioms):
        self.axioms = axioms
        self.proof = []
        self.initial = {}

    def ax(self, j):
        if j not in self.initial:
            self.initial[j] = len(self.proof)
            self.proof.append({"rule": "axiom", "axiom": j, "clause": signed_clause(self.axioms[j])})
        return self.initial[j]

    def weak(self, i, rows):
        self.proof.append({"rule": "weaken", "parents": [i], "clause": encode(rows)})
        return len(self.proof) - 1

    def res(self, i, j, pivot):
        a, b = (set(map(tuple, self.proof[q]["clause"])) for q in (i, j))
        opposite = (pivot[0], pivot[1] ^ 1)
        require(pivot in a and opposite in b, "fixture tried resolution on an absent pivot")
        out = (a - {pivot}) | (b - {opposite})
        self.proof.append({"rule": "resolve", "parents": [i, j], "pivot": list(pivot), "clause": encode(out)})
        return len(self.proof) - 1


def stress_fixture():
    # Source names x,y. Images: a,b -> x; v,d,e -> y; c -> not x; t,z -> 1,0.
    target = [[1], [-1], [-2], [4], [-5], [1, -2]]
    mapping = [1, 1, 2, 3, -3, -1, 2, 2]
    dag = Dag(target)
    a, v, t, b = (atom(i) for i in (1, 3, 4, 2))
    nv, nt, nb = (atom(-i) for i in (3, 4, 2))
    h = a[0] ^ v[0]
    pos = dag.ax(0)
    # a=1 entails (a+v=0) OR (v=0) without containing the initial literal.
    l = dag.weak(pos, [(h, 0), nv])
    r = dag.weak(pos, [(h, 1), a])
    joined = dag.res(l, r, (h, 0))
    recovered = dag.res(joined, dag.weak(pos, [v, a]), nv)
    ttl = dag.weak(dag.ax(3), [t, b])
    ttr = dag.weak(dag.ax(3), [t, nb])
    redundant_t = dag.res(ttl, ttr, b)
    saved = dag.res(redundant_t, dag.weak(recovered, [a, nt]), t)
    alias = dag.res(dag.weak(saved, [a, b]), dag.ax(2), b)
    # This three-equation tautology has no constant equation or complementary pair.
    affine_tautology = dag.weak(alias, [a, v, (h, 0)])
    child = dag.res(affine_tautology, dag.weak(alias, [(h, 1), a]), (h, 0))
    cleaned = dag.res(child, dag.weak(alias, [nv, a]), v)
    many = sum(1 << (i - 1) for i in (2, 4, 5, 6, 7, 8))
    dense_left = dag.weak(cleaned, [a, (many, 0)])
    dense_right = dag.weak(cleaned, [a, (many, 1)])
    both = dag.res(dense_left, dense_right, (many, 0))
    dag.res(both, dag.ax(1), a)
    return 2, [[1], [-1]], 8, target, mapping, dag.proof


def raw_fixture():
    # Real, fully switched two-relay template with one p corridor and one not-p corridor.
    corridors = runpy.run_path(str(CORRIDORS))
    base = runpy.run_path(str(corridors["BASE"]))
    schedule = corridors["StageSchedule"](base, [(1, 2), (1, 3)])
    pins = schedule.assumptions([(2, 3), (1, 3)])
    cnf = schedule.formula + [[v] for v in pins]
    width = max(abs(lit) for row in cnf for lit in row)
    initial_pin = {abs(v): len(schedule.formula) + i for i, v in enumerate(pins)}
    dag = Dag(cnf)

    @cache
    def slot(s):
        i = s * 4
        current = dag.ax(i)
        for j in range(1, 4):
            negative_guard, negative_witness, _ = cnf[i + j]
            unit = dag.ax(initial_pin[-negative_guard])
            binary = dag.res(unit, dag.ax(i + j), atom(-negative_guard))
            current = dag.res(current, binary, atom(-negative_witness))
        return current

    def displayed(s):
        return [row[-1] for row in cnf[s * 4 + 1:s * 4 + 4]]

    def endpoint(s):
        first = dag.res(slot(s), slot(s + 1), atom(displayed(s)[2]))
        second = dag.res(slot(s + 2), slot(s + 3), atom(displayed(s + 2)[2]))
        return dag.res(first, second, atom(displayed(s)[1]))

    def unconditional(e):
        s = 8 + 2 * e
        return dag.res(slot(s), slot(s + 1), atom(displayed(s)[2]))

    left, right = endpoint(0), endpoint(4)
    positive_j = dag.res(left, unconditional(schedule.caps[0]), atom(1))
    negative_k = dag.res(unconditional(schedule.caps[1]), right, atom(schedule.r + 1))
    claims = []
    for track, half in zip(schedule.positions, (1, 0)):
        conditional = 8 + 2 * track[0] + half
        head = displayed(conditional)[1]
        a = dag.res(positive_j, slot(conditional), atom(schedule.relays[0]))
        b = dag.res(unconditional(track[1]), negative_k, atom(schedule.relays[1]))
        claims.append(dag.res(a, b, atom(head)))
    dag.res(*claims, atom(schedule.pad_vars[1]))

    # Signed +/-2 encode the two constants for a one-variable source. Put the
    # drop on the first physical implication of both tracks and reuse one pad x.
    images = dict.fromkeys(range(1, width + 1), -2)
    images[1] = images[schedule.relays[0]] = 2
    images[schedule.pad_vars[1]] = 1
    for lit in pins:
        images[abs(lit)] = 2 if lit > 0 else -2
    for s in range(0, len(schedule.formula), 4):
        options = schedule.formula[s + 1:s + 4]
        mapped = [(images[abs(lit)] if lit > 0 else -images[abs(lit)]) for _, _, lit in options]
        chosen = next((i for i, (neg_guard, _, _) in enumerate(options)
                       if images[-neg_guard] == -2 or mapped[i] == 2), None)
        if chosen is None:
            chosen = next(i for i, lit in enumerate(mapped) if abs(lit) == 1)
        images[-options[chosen][1]] = 2
    return 1, [[1], [-1]], width, cnf, images, dag.proof


def truth_set(n, clause):
    return sum(1 << a for a in range(1 << n) if any((a & m).bit_count() % 2 == b for m, b in clause))


def truth_check_proof(n, cnf, proof):
    universe = (1 << (1 << n)) - 1
    values = []
    for node in proof:
        value = truth_set(n, node["clause"])
        if node["rule"] == "axiom":
            require(value == truth_set(n, signed_clause(cnf[node["axiom"]])), "source axiom truth set changed")
        else:
            common = universe
            for parent in node["parents"]:
                common &= values[parent]
            require(not common & ~value, "source inference loses a common model")
        values.append(value)
    return values[-1] == 0


def exhaustive_rules():
    # All subsets of the two-name nonconstant parity equations, with every
    # complement pivot and every choice of keeping its explicit side occurrences.
    equations = [(m, b) for m in (1, 2, 3) for b in (0, 1)]
    clauses = [frozenset(row for i, row in enumerate(equations) if mask & (1 << i)) for mask in range(64)]
    truth = [truth_set(2, c) for c in clauses]
    require(all(follows(c, d) == (truth[i] & ~truth[j] == 0)
                for i, c in enumerate(clauses) for j, d in enumerate(clauses)), "independent GF(2) verifier mismatch")
    counts = Counter()
    for images in product((-3, -2, -1, 1, 2, 3), repeat=2):
        table = image_table(2, 2, images)
        phi = [hdw()["image_eq"](row, table) for row in equations]
        for source_state in range(4):
            bits = [(int(i > 0) if abs(i) == 3 else (((source_state >> (abs(i) - 1)) & 1) ^ int(i < 0)))
                    for i in images]
            target_state = bits[0] + 2 * bits[1]
            for (mask, value), (new_mask, new_value) in zip(equations, phi):
                target_bit = (target_state & mask).bit_count() % 2
                require((target_bit == value) == ((source_state & new_mask).bit_count() % 2 == new_value),
                        "affine substitution failed independent Boolean evaluation")
                counts["assignment_equation_checks"] += 1
        # In the Boolean quotient a squared affine expression stays itself.
        # Distinct summands that are identified cancel over F2 instead.
        if images[0] == images[1]:
            require(phi[4] == (0, 0), "duplicated coefficients failed to cancel")
        if images[0] == -images[1]:
            require(phi[4] == (0, 1), "a term plus its negation failed to equal one")
        form = [frozenset(phi[k] for k in range(6) if mask & (1 << k)) - {FALSE} for mask in range(64)]
        image_truth = [truth_set(2, c) for c in form]
        for j in range(64):
            for k in range(64):
                if not truth[j] & ~truth[k]:
                    require(not image_truth[j] & ~image_truth[k], "semantic weakening failed after pullback")
                    counts["semantic_weakenings"] += 1
        for p in range(6):
            pbit, qbit = 1 << p, 1 << (p ^ 1)
            for a in range(64):
                if not a & pbit:
                    continue
                for b in range(64):
                    if not b & qbit:
                        continue
                    base = (a & ~pbit) | (b & ~qbit)
                    for c in {base, base | pbit, base | qbit, base | pbit | qbit}:
                        counts["resolution_contexts"] += 1
                        if image_truth[c] == 15:
                            continue
                        if image_truth[a] == 15 or image_truth[b] == 15:
                            live = b if image_truth[a] == 15 else a
                            require(image_truth[live] != 15 and not image_truth[live] & ~image_truth[c],
                                    "tautological parents created a stronger line")
                        else:
                            r = (form[a] - {phi[p]}) | (form[b] - {phi[p ^ 1]})
                            require(r == form[c] or form[a] <= form[c] or form[b] <= form[c],
                                    "one-line canonical transport failed on a non-tautological context")
                            if r != form[c]:
                                counts["single_weakening_repairs"] += 1
        counts["literal_maps"] += 1
    return dict(sorted(counts.items()))


def wide_control(n):
    # A proper clause with 2^n - 1 equations on the actual ancestry of empty.
    cnf = [[1]] + [[-i] for i in range(1, n + 1)]
    proof = Dag(cnf)
    wide = proof.weak(proof.ax(0), [(mask, 1) for mask in range(1, 1 << n)])
    node = proof.weak(wide, [atom(i) for i in range(1, n + 1)])
    for i in range(1, n + 1):
        node = proof.res(node, proof.ax(i), atom(i))
    output, stats = translated(n, cnf, n, cnf, list(range(1, n + 1)), proof.proof)
    require(stats["source"]["lines"] == stats["target"]["lines"] == 2 * n + 3,
            "identity map changed the dense-control node count")
    require(output[wide]["clause"] == proof.proof[wide]["clause"], "the live dense clause disappeared")
    require(truth_check_proof(n, cnf, output), "wide source control failed independent assignment verification")
    return {"variables": n, "nodes": len(output), "equations_on_widest_line": len(output[wide]["clause"]),
            "json_bytes": len(json.dumps(output, separators=(",", ":")).encode())}


def sharp_chain(n):
    cnf = [[1]] + [[-i, i + 1] for i in range(1, n)] + [[-n]]
    proof = Dag(cnf)
    ref = proof.ax(0)
    for i in range(1, n + 1):
        ref = proof.res(ref, proof.ax(i), atom(i))
    out, stats = translated(n, cnf, n, cnf, list(range(1, n + 1)), proof.proof)
    for omitted in range(n + 1):
        # First omitted makes every bit zero, last makes every bit one.
        assignment = (1 << omitted) - 1
        fails = [i for i, row in enumerate(cnf) if not any(
            bool(assignment & (1 << (abs(lit) - 1))) == (lit > 0) for lit in row)]
        require(fails == [omitted], "a chain clause was dispensable")
    require(stats["source"]["lines"] == 2 * n + 1 and truth_check_proof(n, cnf, out),
            "the identity projection missed the sharp bound")
    return {"variables": n, "essential_axioms": len(cnf), "minimal_nodes": len(out)}


def negative_controls():
    caught = []

    def reject(name, action):
        try:
            action()
        except ValueError:
            caught.append(name)
        else:
            raise ValueError("expected a rejection for " + name)

    # A malformed input step must not be hidden by a good-looking restricted image.
    bad = Dag([[1], [2]])
    i, j = bad.ax(0), bad.ax(1)
    bad.proof.append({"rule": "resolve", "parents": [i, j], "pivot": list(atom(1)), "clause": []})
    reject("two_tautological_images_are_not_an_empty_axiom",
           lambda: backtranslate(1, [], 2, bad.axioms, [2, 2], bad.proof))
    proof = Dag([[1], [-1], [1, 2]])
    left, right = proof.ax(0), proof.ax(1)
    proof.res(left, right, atom(1))
    reject("unused_axiom_image_is_only_a_consequence",
           lambda: backtranslate(2, [[1], [-1]], 2, proof.axioms, [1, 2], proof.proof))
    reject("missing_variable_image", lambda: backtranslate(2, [[1], [-1]], 2, proof.axioms, [1], proof.proof))
    swapped = Dag([[1], [-1]])
    a, na = swapped.ax(0), swapped.ax(1)
    swapped.weak(a, [atom(2)])
    swapped.res(a, na, atom(1))
    reject("unsound_target_weakening_disguised_by_alias", lambda: backtranslate(
        1, [[1], [-1]], 2, swapped.axioms, [1, 1], swapped.proof))
    altered = [dict(node) for node in proof.proof]
    altered[-1] = {**altered[-1], "parents": [0, len(altered)]}
    reject("forward_parent", lambda: verify(2, proof.axioms, altered))
    # Nodewise choices x=0 at the first parent and x=1 at the second would
    # purport to transport a contradiction over an empty, satisfiable source.
    reject("separate_substitutions_for_opposite_units", lambda: backtranslate(
        1, [], 1, [[1], [-1]], [2], proof.proof))
    return caught


def corpus():
    result = {"all_two_name_rules": exhaustive_rules(), "rejected_controls": negative_controls(),
              "wide_identity_controls": [wide_control(7), wide_control(8)],
              "sharp_chain_controls": [sharp_chain(n) for n in (1, 4, 9)]}
    for name, case in (("two_corridor_guarded_refutation", raw_fixture()), ("parity_DAG", stress_fixture())):
        n, source, target_n, target, images, proof = case
        out, stats = translated(*case)
        stats["target_variables"] = target_n
        stats["source_variables"] = n
        stats["target_proof_json_bytes"] = len(json.dumps(proof, separators=(",", ":")).encode())
        stats["source_proof_json_bytes"] = len(json.dumps(out, separators=(",", ":")).encode())
        stats["all_source_lines_truth_checked"] = truth_check_proof(n, source, out)
        require(stats["all_source_lines_truth_checked"] and stats["source_axiom_indices_reached"] == [0, 1],
                "finite source checks or exact axiom images failed")
        if name == "parity_DAG":
            require(all(stats["cases"].get(k, 0) for k in ("retained_pivot_weakening", "canonical_resolution",
                        "one_tautological_parent", "both_premises_tautological", "constant_pivot",
                        "semantic_weakening")), "an adverse parity-rule control was never exercised")
        else:
            require(stats["target"]["shared_parents"] > 0 and len(source) == 2
                    and len(target) - stats["tautological_axiom_images"] == 2,
                    "literal raw example lost its sharing or source clauses")
        result[name] = stats
    return result


def load_document(path):
    return json.load(sys.stdin) if path == "-" else json.loads(Path(path).read_text())


def main():
    # The documented local certificate format uses exact decimal integer masks.
    # Trusted proof inputs can span more variables than Python's default text cap.
    if hasattr(sys, "set_int_max_str_digits"):
        sys.set_int_max_str_digits(0)
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--translate", metavar="JSON", help="backtranslate a JSON proof package, using - for stdin")
    group.add_argument("--verify", metavar="JSON", help="verify {n,cnf,proof}, using - for stdin")
    group.add_argument("--emit", action="store_true", help="print reference counts without comparing")
    parser.add_argument("--expected", type=Path, default=Path(__file__).with_name("checks.json"))
    args = parser.parse_args()
    if args.translate:
        package = load_document(args.translate)
        out, stats = translated(**package)
        print(json.dumps({"n": package["source_n"], "cnf": package["source_cnf"], "proof": out, "stats": stats}))
        return
    if args.verify:
        doc = load_document(args.verify)
        print(json.dumps({"status": "passed", **verify(doc["n"], doc["cnf"], doc["proof"])}))
        return
    result = corpus()
    if args.emit:
        print(json.dumps(result, indent=2))
    else:
        require(json.loads(args.expected.read_text()) == result, "stored and independently recomputed data disagree")
        print(json.dumps({"status": "passed", **result}, sort_keys=True))


if __name__ == "__main__":
    main()
