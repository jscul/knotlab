"""Validate the strict examples, case-branch counts and stored primitive proof."""
from functools import reduce
import gzip
from hashlib import sha256
from itertools import product
import json
import operator
import os
from pathlib import Path
import sys

try:
    from pysat.solvers import Solver
except ModuleNotFoundError:
    choices = [p / ".venv" / "bin" / "python" for p in (*Path(__file__).resolve().parents, Path.cwd())]
    interpreter = next((p for p in choices if p.is_file()), None)
    if interpreter is None or str(interpreter) == sys.executable:
        raise
    os.execv(str(interpreter), [str(interpreter), "-B", str(Path(__file__).resolve()), *sys.argv[1:]])

import solver as S


HERE = Path(__file__).resolve().parent


def canon(value):
    return json.dumps(value, separators=(",", ":"), sort_keys=True).encode()


def digest(value):
    return sha256(canon(value)).hexdigest()


def rejects(action):
    try:
        action()
    except ValueError:
        return True
    raise AssertionError("an invalid deduction or source was accepted")


def strict_tests():
    tests, full_models = 0, 0
    for shape in ("star", "path"):
        for m in range(1, 5):
            good, bad = [S.encode(shape, m, c) for c in (0, 1)]
            assert good["n"] == bad["n"] == 5*m+1
            assert good["cnf"][:-4] == bad["cnf"][:-4]
            assert len(good["cnf"]) == len(bad["cnf"]) == 16*m-4
            for c, instance in enumerate((good,bad)):
                assert all(len(clause) == len(set(map(abs,clause))) == 3 for clause in instance["cnf"])
                with Solver(name="g3", bootstrap_with=instance["cnf"]) as solver:
                    assert solver.solve() == (c == 0)
                    for raw in product((0,1),repeat=m+1):
                        values = S.honest_assignment(instance,raw)
                        expected = reduce(operator.xor, (raw[i-1]&raw[j-1] for i,j in instance["edges"]), 0)
                        assert all(values[side["checksum"]] == expected for side in instance["sides"])
                        pins = [(i if x else -i) for i,x in enumerate(raw,1)]
                        assert solver.solve(assumptions=pins) == (c == 0)
                        holds = all(any(bool(values[abs(v)]) == (v > 0) for v in row) for row in instance["cnf"])
                        assert holds == (c == 0)
                        tests += 1
                        full_models += holds
    return {"pinned_SAT_comparisons":tests, "satisfying_total_assignments_tested":full_models}


def all_mismatch_searches():
    counts = {}
    for m in range(1,13):
        longest = cases = 0
        reached = set()
        for diffs in product((0,1),repeat=m):
            if sum(diffs)%2 == 0:
                continue
            found, questions = S.locate_difference(diffs)
            assert diffs[found] == 1 and len(questions) <= (m-1).bit_length()
            prefix = [0]
            for bit in diffs:
                prefix.append(prefix[-1]^bit)
            assert all(ans == prefix[lo]^prefix[hi] for lo,hi,ans in questions)
            longest = max(longest,len(questions))
            reached.add(found)
            cases += 1
        assert len(reached) == m and longest == (m-1).bit_length()
        counts[str(m)] = {"odd_vectors":cases, "max_queries_before_endpoint":longest}
    return counts


def certificate_files(save):
    instance = S.encode("path",3)
    dag, refs = S.refutation(instance)
    raw = {"variables":instance["n"],"cnf":instance["cnf"],"proof":dag.proof}
    trace = {**refs, "strict_clauses":len(instance["cnf"]), "proof_nodes":len(dag.proof),
             "digest_full_payload":digest(raw), "input_digest":digest(instance["cnf"]),
             "conclusion":dag.proof[refs["empty"]]}
    payload = HERE / "opposed_path3.json.gz"
    example = HERE / "trace.json"
    if save:
        with payload.open("xb") as handle:
            handle.write(gzip.compress(canon(raw),mtime=0))
        with example.open("x") as handle:
            handle.write(json.dumps(trace,indent=2)+"\n")
    stored = json.loads(gzip.decompress(payload.read_bytes()))
    assert stored == raw and json.loads(example.read_text()) == json.loads(canon(trace))
    stats = S.Q.verify(stored["variables"],stored["cnf"],stored["proof"])
    assert stats["lines"] == trace["proof_nodes"]
    wrong = S.encode("path",3,0)
    assert rejects(lambda: S.Q.verify(stored["variables"],wrong["cnf"],stored["proof"]))
    row = refs["first_quadratic_cancellation"]["row"]
    chosen = dag.proof[row]["chosen"][0]
    assert any(len(m) == 2 for m in chosen)
    changed = [*dag.proof]
    changed[row] = {**changed[row], "chosen":[[],changed[row]["chosen"][1]]}
    assert rejects(lambda: S.Q.verify(instance["n"],instance["cnf"],changed))
    return {"nodes":stats["lines"],"strict_clauses":len(stored["cnf"]),"first_cancel":row,
            "wrong_charge_rejected":True,"wrong_quadratic_operand_rejected":True}


def growth():
    rows = []
    for m in (1,2,3,7,15,31):
        for shape in ("star","path"):
            instance = S.encode(shape,m)
            dag, trace = S.refutation(instance)
            verified = S.Q.verify(instance["n"],instance["cnf"],dag.proof)
            all_axioms = [step["axiom"] for step in dag.proof if step["rule"] == "axiom"]
            assert set(all_axioms) == set(range(len(instance["cnf"])))
            assert trace["empty"] == len(dag.proof)-1 and dag.clauses[trace["empty"]] == ()
            assert "define" not in verified["rules"]
            r = 1 if shape == "star" else (m+1)//2
            matching = (m+2)//3
            low = 2 if shape == "star" else 2*matching
            upper = 2 if shape == "star" else S.block_cases(m,2)["leaf_upper"]
            rows.append({"shape":shape,"products_per_side":m, "strict_input_clauses":len(instance["cnf"]),
                         "strict_input_variables":instance["n"],"quadratic_nodes":verified["lines"],
                         "quadratic_max_width":verified["max_width"],"public_exact_cases":2**r,
                         "private_leaf_lower":low,"private_leaf_upper":upper})
    return rows


def changed_factorizations():
    # A path of length three is an inner product of two bit pairs in these four affine coordinates.
    transformed = set()
    for x,y,z,w in product((0,1),repeat=4):
        values=(y,x^z,z,w)
        transformed.add(values)
        assert (x*y ^ y*z ^ z*w) == (values[0]*values[1] ^ values[2]*values[3])
    assert len(transformed)==16
    return len(transformed)


def block_checks():
    tests = 0
    for width in range(1,9):
        # After the odd vertices are fixed the block parity is an explicit linear form in its even vertices.
        for bits in product((0,1),repeat=width+1):
            parity = sum(a*b for a,b in zip(bits,bits[1:])) % 2
            linear = sum(bits[i]*((bits[i-1] if i else 0) ^ (bits[i+1] if i<width else 0))
                         for i in range(0,width+1,2)) % 2
            assert parity == linear
            tests += 1
    for m in range(1,10):
        for size in (1,2,4,8):
            bounds = S.block_cases(m,size)
            for ds in product((0,1),repeat=m):
                if not sum(ds)%2:
                    continue
                groups = [sum(ds[j:j+size])%2 for j in range(0,m,size)]
                idx, questions = S.locate_difference(groups)
                assert groups[idx] == 1
                assert len(questions)+(bounds["block_lengths"][idx]+1)//2 <= bounds["depth_upper"]
    return {"linearization_tests":tests, "m31":{str(s):S.block_cases(31,s) for s in (1,2,4,8,16,31)}}


def factored_cases(save):
    rows = []
    for m in (2,4,8,16):
        source = S.encode("path",m,1,factor_right=True)
        left,right = source["sides"]
        left_pairs = {tuple(sorted(g["variables"][:2])) for g in left["products"]}
        right_pairs = {tuple(sorted(g["variables"][:2])) for g in right["products"]}
        assert left_pairs.isdisjoint(right_pairs)
        dag, trace = S.refutation(source)
        v = S.Q.verify(source["n"],source["cnf"],dag.proof)
        record = {"path_edges":m, "products_left":len(left_pairs), "products_right":len(right_pairs),
                  "coincident_product_arguments":0, "strict_clauses":len(source["cnf"]),
                  "proof_nodes":v["lines"],"empty":trace["empty"]}
        if m <= 4:
            for c in (0,1):
                instance = S.encode("path",m,c,factor_right=True)
                with Solver(name="g3",bootstrap_with=instance["cnf"]) as oracle:
                    for raw in product((0,1), repeat=m+1):
                        bits = S.honest_assignment(instance,raw)
                        l,r = (s["checksum"] for s in instance["sides"])
                        assert bits[l] == bits[r]
                        assert oracle.solve(assumptions=[(i if bit else -i) for i,bit in enumerate(raw,1)]) == (c==0)
        if m == 4:
            sample = {"variables":source["n"],"cnf":source["cnf"],"proof":dag.proof}
            path = HERE/"factored_path4.json.gz"
            if save:
                with path.open("xb") as handle:
                    handle.write(gzip.compress(canon(sample),mtime=0))
            stored = json.loads(gzip.decompress(path.read_bytes()))
            assert stored == sample
            S.Q.verify(stored["variables"],stored["cnf"],stored["proof"])
            record["first_distributive_step"] = trace["first_distributive_step"]
        rows.append(record)
    return rows


def main(save=False):
    import split_audit
    return {"status":"passed","source_and_models":strict_tests(),
            "portable_proof":certificate_files(save),"growth":growth(),
            "private_mismatch_search":all_mismatch_searches(),
            "partially_visible_prefixes":block_checks(),
            "no_duplicate_product_gate_control":factored_cases(save),
            "invertible_path_to_two_pairs_truth_tests":changed_factorizations(),
            "independent_affine_hull_checks":split_audit.run_checks()}


if __name__ == "__main__":
    if sys.argv[1:] not in ([],["--write-example"]):
        raise SystemExit("usage: check.py [--write-example]")
    print(json.dumps(main(bool(sys.argv[1:])),sort_keys=True,indent=2))
