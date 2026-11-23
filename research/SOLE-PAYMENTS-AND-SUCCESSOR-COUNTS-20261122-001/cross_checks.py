"""Cross-check the two frozen receivers against independent, finite controls.

The funding checks use the archived complete-cut operator. The value checks
encode every reached physical holding directly as clauses and use only the
previously archived payment names to specify the observations.
"""
from collections import Counter, defaultdict
from itertools import combinations, permutations, product
from pathlib import Path
from runpy import run_path
import json

from pysat.solvers import Solver

ROOT = Path(__file__).resolve().parents[2]
END_SOURCE = next((ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A").glob("*/end_operator.py"))
RECEIPTS = next((ROOT / "artifacts/QUIET-RETURNS-AND-SIGNAL-FRACTIONS-20261122-001B").glob("*/results.json"))
LAWS = ("parity", "nae")


def abstract_funding():
    engine = run_path(str(END_SOURCE))
    end_type, step = engine["End"], engine["step"]
    output = {}
    for law in LAWS:
        counts = Counter()
        for size in range(1, 5):
            population = tuple(range(size))
            subsets = [s for k in range(2, size + 1) for s in combinations(population, k)]
            witnesses = {engine["maximal_blocks"](s for i,s in enumerate(subsets) if (mask >> i) & 1)
                         for mask in range(1 << len(subsets))}
            for groups in sorted(witnesses):
                for supply in product((1,2),repeat=size):
                    end = end_type(dict(zip(population,supply)), groups)
                    result = step(end, law)
                    counts["abstract_ends"] += 1
                    if result.status != "extend":
                        counts[result.status] += 1
                        continue
                    counts["funded"] += 1
                    for child, parents in enumerate(result.parents):
                        if len(parents) != 2 or any(supply[p] != 1 for p in parents):
                            continue
                        counts["two_sole_payers"] += 1
                        a,b = parents
                        before = engine["neighbors"](end)
                        assert before[a] == {b} and before[b] == {a}
                        assert all(not set(parents).intersection(ps)
                                   for i,ps in enumerate(result.parents) if i != child)
                        if result.fresh[child] == 0:
                            assert law == "parity" and len(result.parents) == 1
                            counts["closed_on_joint_payment"] += 1
                        else:
                            assert result.fresh[child] == 1 and not engine["neighbors"](result.end)[child]
                            next_cut = step(result.end, law)
                            assert [p for p in next_cut.parents if child in p] == [(child,)]
                            counts["only_one_parent_on_next_payment"] += 1
        output[law] = dict(counts)
    return output


def clause_family(law, holdings):
    clauses = []
    for names in holdings:
        variables = [n + 1 for n in names]
        if law == "nae":
            clauses.extend([variables, [-v for v in variables]])
        else:
            for word in product((0,1), repeat=len(names)):
                if sum(word) % 2:
                    clauses.append([-v if bit else v for bit,v in zip(word,variables)])
    return clauses


def incidence(rows):
    owners = defaultdict(set)
    for h,row in enumerate(rows):
        for n in row:
            owners[n].add(h)
    return owners


def old_input_decoder(parent, root, rows):
    """Reach the other holders of the parent's marks in two coholding steps."""
    owners = incidence(rows)
    returned = []
    for mark in rows[parent]:
        other, = owners[mark] - {parent}
        if other == root or any(len(owners[n]) == 1 for n in rows[other]):
            continue
        returned.append(mark)
    return sorted(returned)


def pins(names,word):
    return [(n + 1) * (1 if z else -1) for n,z in zip(names,word)]


def raw_current_views(doc,law):
    data = doc["laws"][law]
    cohorts = data["named_funded_ordinary_cohorts"]
    quiet = data["continuous_valued_histories"]["quiet"]["actual_complete_words_by_consecutive_cut"]
    rows = list(doc["archived_five_odd_source"])
    for frame in cohorts[1:7]:
        for birth in frame["births"]:
            assert len(rows) == birth["knot"]
            rows.append(birth["paid"] + birth["fresh"])
    p = cohorts[5]["enrolled_holder"]
    r = cohorts[6]["enrolled_holder"]
    by_holder = {b["knot"]: b for frame in cohorts for b in frame["births"]}
    other, = set(by_holder[r]["parents"]) - {p}
    old = by_holder[p]["paid"]
    root_marks = rows[r]
    owners = incidence(rows)
    outside_sets = [sorted(set(rows[h]) - set(root_marks)) for h in (p,other)]
    assert all(len(s) == 3 for s in outside_sets)
    # In the raw one-contact observation each of these six exterior names has
    # one visible holder, one invisible holder and no other visible incidence.
    assert all(len(owners[n]) == 2 and len(owners[n].intersection((p,other,r))) == 1
               for s in outside_sets for n in s)
    q = tuple(map(int, quiet[6]))
    assert q[old[0]] == q[old[1]]
    choices = [sorted(set(permutations(q[n] for n in s))) for s in outside_sets]
    same_past = tuple(map(int, quiet[3]))
    fixed = pins(range(len(same_past)),same_past) + pins(root_marks,[q[n] for n in root_marks])
    clauses = clause_family(law,rows)
    clauses += [[old[0]+1,old[1]+1],[-old[0]-1,-old[1]-1]]
    tried = success = 0
    example = None
    with Solver(bootstrap_with=clauses) as solver:
        for pword,oword in product(*choices):
            tried += 1
            if solver.solve(assumptions=fixed + pins(outside_sets[0],pword) + pins(outside_sets[1],oword)):
                success += 1
                if example is None:
                    model = set(solver.get_model())
                    word = [int(n+1 in model) for n in range(len(q))]
                    example = {"whole_word_at_successor":"".join(map(str,word)), "earlier_signal_inputs":[word[n] for n in old],
                               "root_values":[word[n] for n in root_marks]}
    assert success and example is not None
    assert old_input_decoder(p,r,rows) == sorted(old)
    # Check the decoder directly again at every archived positive return with
    # its next actual payment available (no use of holder names in the rule).
    more = list(doc["archived_five_odd_source"])
    decoder_tests = 0
    for t,frame in enumerate(cohorts[1:], start=1):
        more.extend(b["paid"] + b["fresh"] for b in frame["births"])
        if t > 1 and (t-1) % 5 == 0:
            parent = cohorts[t-1]["enrolled_holder"]
            assert old_input_decoder(parent,frame["enrolled_holder"],more) == sorted(by_holder[parent]["paid"])
            decoder_tests += 1
    return dict(first_return=p, successor=r, root_marks=root_marks, earlier_input_marks=old,
                quiet_root_word=[q[n] for n in root_marks], lower_bound_assignments_checked=tried,
                lower_bound_assignments_realizable=success, example_with_other_predecessor_signal=example,
                two_contact_input_decodings=decoder_tests)


if __name__ == "__main__":
    doc = json.loads(RECEIPTS.read_text())
    print(json.dumps({"abstract_funding_controls": abstract_funding(),
                      "matched_one_contact_views": {law:raw_current_views(doc,law) for law in LAWS},
                      "meaning":"Exact coverage and existence checks, no probability weighting."},indent=2,sort_keys=True))
