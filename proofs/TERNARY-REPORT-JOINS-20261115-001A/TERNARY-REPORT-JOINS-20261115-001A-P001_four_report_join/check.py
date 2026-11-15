"""Independently audit every source block, boundary projection and saved primitive proof line."""

from array import array
from collections import Counter
from copy import deepcopy
import gzip
from hashlib import sha256
from itertools import product
import json
import os
from pathlib import Path
import sys

import solver as S

try:
    from pysat.solvers import Solver
except ModuleNotFoundError:
    runtime = S.ROOT / ".venv" / "bin" / "python"
    if sys.prefix == str(runtime.parent.parent) or not runtime.is_file():
        raise
    os.execv(str(runtime), [str(runtime), "-B", str(Path(__file__).resolve()), *sys.argv[1:]])

HERE = Path(__file__).resolve().parent
MASKS = list(product((0, 1), repeat=4))
SHARED = (1, 2, 3, 4)


def require(condition, message):
    if not condition:
        raise ValueError(message)


def key(bits):
    return "".join(map(str, bits))


def digest(content):
    return sha256(content).hexdigest()


def raw_report(a, b, xyz):
    x, y, z = xyz
    return int(bool(z) and (bool(x and y) != bool(a and b)))


def audit_source(source):
    blocks, cnf = source["blocks"], source["cnf"]
    private = set()
    row_counts = []
    owners = bytearray()
    for j, block in enumerate(blocks):
        rows = {r["bits"]: r for r in block["rows"]}
        expected = set()
        for bits in product((0, 1), repeat=11):
            reports = [raw_report(*bits[:2], bits[i:i + 3]) for i in (2, 5, 8)]
            if sum(reports) % 2 != block["charge"]:
                expected.add(bits)
        require(set(rows) == expected, "an allowed or forbidden input tuple was misclassified")
        for bits, row in rows.items():
            long = tuple(-v if bit else v for v, bit in zip(block["variables"], bits))
            require(row["clause"] == long and row["start"] == len(owners), "source row indexing")
            aux = row["aux"]
            require(len(set(aux)) == 8 and not private.intersection(aux), "reused private variable")
            require(all(v > source["public_n"] for v in aux), "private variable overlaps originals")
            private.update(aux)
            chain = [(*long[:2], aux[0])]
            for i in range(7):
                chain.append((-aux[i], long[i + 2], aux[i + 1]))
            chain.append((-aux[7], *long[-2:]))
            raw = cnf[row["start"]:row["start"] + 9]
            require([tuple(c) for c in raw] == chain, "source ternaries differ from the literal chain")
            require(all(len(set(map(abs, clause))) == 3 for clause in raw), "repeated strict-CNF variable")
            owners.extend([1 << j] * 9)
        row_counts.append(len(rows))
    require(row_counts == [696, 696, 696, 1352], "four source row counts")
    require(len(owners) == len(cnf) == 30960 and len(private) == 27520, "unexpected strict encoding size")
    require(source["n"] == source["public_n"] + len(private) == 27540, "incorrect declared variable count")
    return row_counts, owners


def expected_guarded(source, ids, bits, charge):
    # An encoded polynomial represents the equation that its value equals zero.
    guards = []
    terms = []
    if charge:
        terms.append(())
    if sum(bits) % 2 == 1:
        terms.append((1, 2))
    for i, bit in zip(ids, bits):
        x, y, z = source["triples"][i]
        guards.append(((z,),) if bit else ((), (z,)))
        if bit:
            terms.append((x, y))
    return tuple(sorted((*guards, tuple(sorted(terms)))))


def decoded(row):
    return tuple(sorted(tuple(sorted(tuple(t) for t in f)) for f in row["clause"]))


def evaluate(f, values):
    return sum(all(values[v] for v in term) for term in f) % 2


def audit_certificate(source, owners, trace):
    require(digest(S.kernel_path.read_bytes()) == "84a7cdc149c8945061e8c46daaf9b3686cbcf4cee26f73b4e79c663bda25b71e",
            "the advertised primitive checker changed")
    requires = set(trace["selector_exclusions"])
    for family in [*trace["child_roots"], *trace["summary_roots"].values()]:
        requires.update(family.values())
    examples = {}
    for example in trace["examples"]:
        entries = [example["summary"]]
        for branch in example["branches"]:
            entries.extend([*branch["children"], branch["sum"], branch["contract"]])
        for index, wire in entries:
            requires.add(index)
            examples[index] = wire
    requires.add(trace["empty"][0])
    found = {}
    origin = bytearray()
    first, second, axiom = (array("i") for _ in range(3))
    cert = HERE / "four-check-proof.jsonl.gz"
    with gzip.open(cert, "rt", encoding="utf-8") as stream:
        header = json.loads(next(stream))
        require(header == {"n": source["n"], "cnf": source["cnf"]}, "certificate declares a different CNF")
        require(trace["source_sha256"] == digest(json.dumps(header["cnf"], separators=(",", ":")).encode()),
                "trace strict input digest")
        def instructions():
            for i, line in enumerate(stream):
                row = json.loads(line)
                parents = row.get("parents", [])
                ax = row.get("axiom", -1)
                used = owners[ax] if ax != -1 else 0
                for p in parents:
                    used |= origin[p]
                origin.append(used)
                first.append(parents[0] if parents else -1)
                second.append(parents[1] if len(parents) == 2 else -1)
                axiom.append(ax)
                if i in requires:
                    found[i] = row
                yield row
        result = S.Q.verify(header["n"], header["cnf"], instructions(), convention="multiset")
    require(requires == found.keys(), "missing traced primitive node")
    require(result["lines"] == trace["proof_nodes"] and result["rules"] == trace["rule_counts"]
            and result["max_width"] == trace["max_width"], "saved trace differs from checked rules or counts")
    require(all(found[i] == wire for i, wire in examples.items()), "saved trace excerpt differs from its wire row")
    require(found[trace["empty"][0]] == trace["empty"][1] and found[trace["empty"][0]]["clause"] == [],
            "the traced last row does not close")
    def ancestors(node):
        pending, seen, axioms = [node], set(), set()
        while pending:
            i = pending.pop()
            if i in seen:
                continue
            seen.add(i)
            if axiom[i] >= 0:
                axioms.add(axiom[i])
            if first[i] >= 0:
                pending.append(first[i])
            if second[i] >= 0:
                pending.append(second[i])
        return seen, axioms
    live, inputs = ancestors(trace["empty"][0])
    require(len(live) == trace["live_nodes"] == len(origin) and len(inputs) == trace["live_source_axioms"] == len(owners),
            "an advertised live inference or source clause does not reach the empty clause")
    for e in trace["examples"]:
        _, inputs = ancestors(e["summary"][0])
        counted = [sum(r["start"] in inputs for r in b["rows"]) for b in source["blocks"]]
        require(counted == e["ancestral_forbidden_rows_by_block"] and 9 * sum(counted) == len(inputs)
                and len(inputs) == e["ancestral_strict_clauses"], "strict ancestry in the worked trace")
        sample = e["sample_ancestral_input"]
        start = sample["row"]["start"]
        require(all(i in inputs for i in range(start, start + 9)) and
                source["cnf"][start:start + 9] == sample["strict_clauses"], "sample source chain is detached")
    for j, (block, family) in enumerate(zip(source["blocks"], trace["child_roots"])):
        for bits in product((0, 1), repeat=3):
            i = family[key(bits)]
            require(origin[i] & ~(1 << j) == 0 and
                    decoded(found[i]) == expected_guarded(source, block["indices"], bits, block["charge"]),
                    "child trace leaked another check or changed its equation")
    actual = {}
    for side, charge, allowed in [("left", 0, 3), ("right", 1, 12)]:
        actual[side] = {}
        for bits in MASKS:
            i = trace["summary_roots"][side][key(bits)]
            row = decoded(found[i])
            expect = expected_guarded(source, SHARED, bits, charge)
            require(origin[i] & ~allowed == 0 and row == expect, "wrong four-report value or outside source used")
            actual[side][bits] = row
    for i, bits in zip(trace["selector_exclusions"], MASKS):
        expect = tuple(sorted((((source["triples"][j][2],),) if b else ((), (source["triples"][j][2],)))
                              for j, b in zip(SHARED, bits)))
        require(decoded(found[i]) == expect, "changed selector-exclusion root")
    return result, actual


def audit_join(source, actual):
    allowed = Counter()
    witness_masks = {"left": set(), "right": set()}
    extensions = {"left": set(), "right": set()}
    surviving = [source["triples"][i] for i in SHARED]
    all_middle = list(product((0, 1), repeat=3))
    for bits in product((0, 1), repeat=14):
        a, b, *data = bits
        triples = [tuple(data[i:i + 3]) for i in range(0, 12, 3)]
        reports = [raw_report(a, b, xyz) for xyz in triples]
        r1, r2, r3, r4 = reports
        sigma = tuple(xyz[2] for xyz in triples)
        values = {1: a, 2: b}
        for ids, xyz in zip(surviving, triples):
            values.update(zip(ids, xyz))
        possible = [raw_report(a, b, xyz) for xyz in all_middle]
        for side, child_pairs in [("left", (r1 ^ r2, r3 ^ r4)), ("right", (r1 ^ r3, r2 ^ r4 ^ 1))]:
            extension = any(m == child_pairs[0] and m == child_pairs[1] for m in possible)
            displayed = any(evaluate(f, values) == 0 for f in actual[side][sigma])
            require(displayed == extension, "fixed shared originals gave different child and exported truth")
            allowed[side] += extension
            if extension:
                extensions[side].add(sigma)
            else:
                witness_masks[side].add(sigma)
    require(allowed == {"left": 10144, "right": 6240}, "four-report projection population")
    require(witness_masks["left"] == set(MASKS) - {(0, 0, 0, 0)} and witness_masks["right"] == set(MASKS),
            "the fixed full-selector encoding contains an unexpected redundant row")
    require(extensions["left"] == set(MASKS) and extensions["right"] == set(MASKS) - {(0, 0, 0, 0)},
            "selector feasibility differs from the projected report")
    return dict(allowed), {s: len(masks) for s, masks in witness_masks.items()}


def audit_raw_sat(source):
    samples = {}
    for side, block_ids, charge in [("left", (0, 1), 0), ("right", (2, 3), 1)]:
        raw = []
        for j in block_ids:
            b = source["blocks"][j]
            raw.extend(source["cnf"][b["rows"][0]["start"]:b["rows"][-1]["start"] + 9])
        results = Counter()
        with Solver(name="cadical195", bootstrap_with=raw) as solver:
            for bits in MASKS:
                first_on = next((i for i, bit in enumerate(bits) if bit), None)
                for common in (0, 1):
                    for changed in ([None, first_on] if first_on is not None else [None]):
                        values = {1: common, 2: common}
                        targets = []
                        for j, bit in enumerate(bits):
                            xyz = (int(j == changed), int(j == changed), bit)
                            targets.append(raw_report(common, common, xyz))
                            values.update(zip(source["triples"][j + 1], xyz))
                        pins = [v if bit else -v for v, bit in values.items()]
                        answer = solver.solve(assumptions=pins)
                        require(answer == (sum(targets) % 2 == charge), "SAT on the exact two strict blocks")
                        results["sat" if answer else "unsat"] += 1
        samples[side] = dict(results)
    # Every charge vector has a direct raw witness exactly when its total is even.
    # Enumerate the six report bits independently, then pin a raw witness for each even charge.
    outcomes = Counter()
    for charges in product((0, 1), repeat=4):
        entries = [r for r in product((0, 1), repeat=6)
                   if all(sum(r[i] for i in ids) % 2 == c for ids, c in zip(S.SUPPORTS, charges))]
        require(bool(entries) == (sum(charges) % 2 == 0), "incorrect global charge parity control")
        if entries:
            control = S.four_check_source(charges)
            pins = [-1, -2]
            for xyz, bit in zip(control["triples"], entries[0]):
                pins += [xyz[0], xyz[1], xyz[2] if bit else -xyz[2]]
            with Solver(name="cadical195", bootstrap_with=control["cnf"]) as solver:
                require(solver.solve(assumptions=pins), "even charge lacks its actual strict-CNF witness")
        outcomes["even_sat" if entries else "odd_inconsistent"] += 1
    for final_charge in (0, 1):
        full = source if final_charge else S.four_check_source((0, 0, 0, 0))
        with Solver(name="cadical195", bootstrap_with=full["cnf"]) as solver:
            require(solver.solve() == (final_charge == 0), "unrestricted raw strict-CNF charge flip")
    return samples, dict(outcomes)


def audit_mutations(source, trace):
    example = next(e for e in trace["examples"] if e["side"] == "left" and e["mask"] == "1010")
    branch = example["branches"][1]
    local = [{"rule": "axiom", "axiom": 0, "clause": []}]
    for _, parent in branch["children"]:
        local.append({"rule": "weaken", "parents": [0], "clause": parent["clause"]})
    result = deepcopy(branch["sum"][1])
    result["parents"] = [1, 2]
    local += [result, local[0]]
    # This local mutation harness reuses the authenticated parent *values*.
    # The empty harness premise never enters the actual published proof.
    S.Q.verify(source["n"], [[]], local)
    result["coefficients"][1] = 0
    try:
        S.Q.verify(source["n"], [[]], local)
    except ValueError as rejected:
        require("formal rule result" in str(rejected), "mutation rejected for an unrelated error")
    else:
        raise ValueError("a dropped selected contribution survived")
    xyzs = [(0, 0, 1)] + [(0, 0, 0)] * 3
    require(sum(raw_report(1, 1, xyz) for xyz in xyzs) % 2 == 1, "missing ab term failed to change truth")
    for c in (0, 1):
        parity = sum(raw_report(0, 0, (x, y, z)) ^ c for x, y, z in product((0, 1), repeat=3)) % 2
        require(parity == 1, "the three-bit isolated report failed the degree-three control")
    return {"altered_sum_coefficient_rejected_at": branch["sum"][0], "missing_ab_flips_singleton": True,
            "both_charges_odd_on_single_report_cube": True}


def main():
    source = S.four_check_source()
    counts, owners = audit_source(source)
    trace = json.loads((HERE / "trace.json").read_text())
    kernel, actual = audit_certificate(source, owners, trace)
    child_end = max(node for roots in trace["child_roots"] for node in roots.values()) + 1
    left_end = max(trace["summary_roots"]["left"].values()) + 1
    right_end = max(trace["summary_roots"]["right"].values()) + 1
    intervals = [child_end, left_end - child_end, right_end - left_end, kernel["lines"] - right_end]
    require(intervals == [135808, 176, 176, 160], "source derivation, both joins, or closure changed size")
    allowed, essential = audit_join(source, actual)
    raw, charges = audit_raw_sat(source)
    mutations = audit_mutations(source, trace)
    print(json.dumps({"status": "passed", "strict_forbidden_rows": counts, "strict_cnf_variables": source["n"],
                      "raw_clause_count": len(owners), "proof_nodes": kernel["lines"],
                      "primitive_nodes_by_phase": dict(zip(("derive_children", "join_left", "join_right", "close"), intervals)),
                      "last_empty_row": trace["empty"][0], "shared_parents": kernel["shared_parents"],
                      "max_proof_width": kernel["max_width"], "rules": kernel["rules"],
                      "final_ancestral_input_clauses": trace["live_source_axioms"], "final_ancestral_nodes": trace["live_nodes"],
                      "source_pure_child_rows": 32, "source_pure_summary_rows": 32, "selector_exclusions": 16,
                      "original_boundary_assignments_per_side": 2**14, "projected_allowed": allowed,
                      "individually_necessary_full_mask_rows": essential, "raw_strict_pair_queries": raw,
                      "all_charge_controls": charges, "unrestricted_cadical_models_0000_0001": [True, False], "mutations": mutations,
                      "certificate_sha256": digest((HERE / "four-check-proof.jsonl.gz").read_bytes())},
                     indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
