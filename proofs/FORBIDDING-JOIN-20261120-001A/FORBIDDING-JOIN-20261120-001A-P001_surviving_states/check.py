"""Reconstruct the proof's small funded rounds and their exact state relations."""

from collections import Counter
from fractions import Fraction
from functools import cache
from hashlib import sha256
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys


FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
SETTINGS = tuple(product(range(2), repeat=2))


def mask(support):
    return sum(1 << bit for bit in support)


def satisfies(state, support_mask, law):
    bits = state & support_mask
    if law == "parity":
        return bits.bit_count() % 2 == 0
    if law == "NAE":
        return bits != 0 and bits != support_mask
    raise ValueError(law)


def allowed(supports, law):
    masks = [mask(s) for s in supports]
    return [w for w in range(1 << max(m.bit_length() for m in masks))
            if all(satisfies(w, m, law) for m in masks)]


def word(state, support):
    result = 0
    for bit in support:
        result = 2*result + ((state >> bit) & 1)
    return result


def groups(neighbours, live):
    """Literal exhaustive proposal rule on the tiny fixtures, independent of the growth engine."""
    candidates = {tuple(pair) for pair in combinations(live, 2)
                  if neighbours[pair[0]] & neighbours[pair[1]]}
    eligible = []
    for k in range(3, len(live)+1):
        for g in combinations(live, k):
            if (all(pair in candidates for pair in combinations(g, 2)) and
                    not set.intersection(*(neighbours[i] for i in g))):
                eligible.append(g)
    larger = [g for g in eligible if not any(set(g) < set(other) for other in eligible)]
    return sorted(larger) + sorted(pair for pair in candidates
                                   if not any(set(pair) <= set(g) for g in larger))


def planned_births(source, old, law):
    counts = Counter(bit for support in source for bit in support)
    loose = [[bit for bit in support if counts[bit] == 1] for support in source]
    old_neighbours = [{j for j, s in enumerate(source) if j != i and set(h) & set(s)}
                      for i, h in enumerate(source)]
    proposed = groups(old_neighbours, [i for i in range(len(source)) if loose[i]])
    spent = Counter(i for g in proposed for i in g)
    assert all(spent[i] <= len(loose[i]) for i in range(len(source)))
    proposed.extend((i,) for i in range(len(source)) for _ in range(len(loose[i])-spent[i]))
    next_groups = groups([set(g) for g in proposed], list(range(len(proposed))))
    demand = Counter(j for g in next_groups for j in g)
    plan = []
    for j, g in enumerate(proposed):
        take = tuple(loose[i].pop(0) for i in g)
        implied = all(satisfies(w, mask(take), law) for w in old)
        q = demand[j] if implied else max(1, 3-len(g), demand[j])
        plan.append((take, demand[j], q, implied))
    return plan


def fresh_count(p, q, mode):
    floor = max(0, 3-p)
    if mode == "ordinary":
        return q
    if mode == "one_fewer":
        return min(q, max(floor, q-1))
    if mode == "arity_floor":
        return min(q, floor)
    raise ValueError(mode)


@cache
def knotlab_verdict(k, actual):
    names = [f"v{i}" for i in range(k)]
    missing = set(range(1 << k)) - set(actual)
    clauses = []
    for code in sorted(missing):
        values = format(code, f"0{k}b")
        clauses.append(" ".join(("~" if v == "1" else "") + name for v, name in zip(values, names)))
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", *names[:-1], "--contact", names[-1], "--json"]
    run = subprocess.run(command, cwd=ROOT, capture_output=True, text=True, check=False,
                         env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")))
    if run.returncode not in (0, 1):
        raise RuntimeError(run.stderr)
    verdict = json.loads(run.stdout)
    assert set(actual) == {int(v, 2) for v in verdict["allowed"]}
    return [verdict["binding"], verdict["loss_on_erasure"], verdict["coexistence"]]


def projection(states, support, law):
    k = len(support)
    actual = tuple(sorted({word(w, support) for w in states}))
    specified = {w for w in range(1 << k) if satisfies(w, (1 << k)-1, law)}
    assert set(actual) <= specified
    missing = [format(w, f"0{k}b") for w in sorted(specified - set(actual))]
    return {"arity": k, "number_of_words": len(actual), "omitted": missing,
            "K1_K2_K3": knotlab_verdict(k, actual)}


def rank(rows):
    basis = {}
    for row in rows:
        while row and row.bit_length() in basis:
            row ^= basis[row.bit_length()]
        if row:
            basis[row.bit_length()] = row
    return len(basis)


def one_round(source, law, mode):
    nold = max(max(h) for h in source)+1
    old = allowed(source, law)
    assert all(not projection(old, s, law)["omitted"] for s in source)
    plan = planned_births(source, old, law)
    additions, records = [], []
    next_id = nold
    for take, demand, q, implied in plan:
        f = fresh_count(len(take), q, mode)
        additions.append(take + tuple(range(next_id, next_id+f)))
        records.append({"old_inputs": list(take), "p": len(take), "D": demand,
                        "q": q, "f": f, "pre_implied": implied})
        next_id += f
    stages = source + additions
    complete = allowed(stages, law)
    observed = Counter(w & ((1 << nold)-1) for w in complete)
    assert complete
    for w in old:
        lifts = 1
        for take, _, q, _ in plan:
            f = fresh_count(len(take), q, mode)
            if f == 0:
                lifts *= satisfies(w, mask(take), law)
            elif law == "parity":
                lifts *= 2**(f-1)
            else:
                lifts *= 2**f - (not satisfies(w, mask(take), law))
        assert lifts == observed[w]
    if law == "parity":
        old_rows = list(map(mask, source))
        zero = [mask(take) for take,_,q,_ in plan if fresh_count(len(take), q, mode) == 0]
        increment = rank(old_rows + zero) - rank(old_rows)
        assert len(observed) * 2**increment == len(old)
        # All of these first-round fixtures have one connected old holder presentation.
        assert increment == len(zero) - int(len(zero) == len(plan))
    return {"old_states": len(old), "old_survivors": len(observed), "complete_states": len(complete),
            "births": records, "projections": [projection(complete,s,law) for s in stages]}


def three_holders(extra):
    return [(0, 2, 3) + ((6,) if extra >= 1 else ()),
            (0, 1, 4) + ((7,) if extra >= 2 else ()), (1, 2, 5)]


def multiple_meeting(spare):
    labels = "habcdefguivz"
    names = ["habcdef"+("z" if spare else ""), "agu", "biv", "cdg", "efi"]
    return [tuple(labels.index(bit) for bit in s) for s in names]


def check_rounds():
    cases = {}
    for extra in range(3):
        for law in ("parity", "NAE"):
            case = {mode: one_round(three_holders(extra), law, mode)
                    for mode in ("ordinary", "one_fewer", "arity_floor")}
            pre, one, floor = (case[mode] for mode in ("ordinary", "one_fewer", "arity_floor"))
            assert pre["old_survivors"] == pre["old_states"]
            assert floor["births"][0]["D"] == extra
            if extra == 2:
                assert one["births"][0]["f"] == 1 and floor["births"][0]["f"] == 0
                assert one["old_survivors"] == pre["old_states"] > floor["old_survivors"]
            if law == "NAE":
                assert all(not p["omitted"] for arm in case.values() for p in arm["projections"])
            if law == "parity" and extra == 1:
                assert not floor["projections"][0]["K1_K2_K3"][1]
                assert not floor["projections"][-1]["K1_K2_K3"][1]
            cases[f"three_holders_{extra}_extra_{law}"] = case
    for spare in (False, True):
        case = {mode: one_round(multiple_meeting(spare), "NAE", mode)
                for mode in ("ordinary", "one_fewer", "arity_floor")}
        ordinary, rival = case["ordinary"], case["arity_floor"]
        assert case["one_fewer"] == rival
        assert ordinary["old_survivors"] == (1288 if spare else 640)
        assert rival["old_survivors"] == (966 if spare else 480)
        assert rival["projections"][0]["K1_K2_K3"] == [True, not spare, True]
        assert all(not p["omitted"] for p in rival["projections"][1:])
        if spare:
            assert rival["complete_states"] == 2898 and ordinary["complete_states"] == 6762
        cases["five_holders_with_spare" if spare else "five_holders"] = case
    return cases


def check_six_bit_nae():
    """All labelled sets of distinct ternary supports on six used variables of occurrence at most two."""
    triples = list(combinations(range(6), 3))
    tested = pin_tests = 0
    for size in range(2, 5):
        for supports in combinations(triples, size):
            occurrences = Counter(bit for support in supports for bit in support)
            if len(occurrences) != 6 or max(occurrences.values()) > 2:
                continue
            states = allowed(supports, "NAE")
            assert states
            for fixed_mask in range(64):
                if all((mask(s) & ~fixed_mask).bit_count() >= 2 for s in supports):
                    assert len({w & fixed_mask for w in states}) == 2**fixed_mask.bit_count()
                    pin_tests += 1
            for s in supports:
                if all(len(set(other)-set(s)) >= 2 for other in supports if other != s):
                    assert len({word(w,s) for w in states}) == 6
            tested += 1
    odd_binary = [(0,1), (1,2), (0,2)]
    fano = [tuple((i+j) % 7 for j in (0,1,3)) for i in range(7)]
    assert not allowed(odd_binary, "NAE") and not allowed(fano, "NAE")
    return {"presentations": tested, "fully_free_pin_sets": pin_tests,
            "outside_controls_allowed": [len(allowed(s,"NAE")) for s in (odd_binary,fano)]}


def parity_obstructions():
    ghz = [(0,2,4), (0,3,5), (1,2,5), (1,3,4)]
    square = [tuple(range(3*i,3*i+3)) for i in range(3)] + [tuple(range(i,9,3)) for i in range(3)]
    results = {}
    for name, rules, targets in (("GHZ", ghz, (0,1,1,1)), ("Mermin_Peres", square, (0,0,0,0,0,1))):
        n = max(max(r) for r in rules)+1
        signs = [tuple((s & mask(r)).bit_count()%2 for r in rules) for s in range(1 << n)]
        common = signs.count(targets)
        after_drop = [sum(all(a == b for j,(a,b) in enumerate(zip(row,targets)) if j != i)
                          for row in signs) for i in range(len(rules))]
        assert common == 0 and all(after_drop)
        results[name] = {"common": common, "after_each_omission": after_drop}
    return results


def controls():
    classical = Counter()
    for a0,a1,b0,b1 in product((-1,1),repeat=4):
        e = (a0*b0, a0*b1, a1*b0, a1*b1)
        for signs in product((-1,1),repeat=4):
            if signs.count(-1) % 2:
                classical[sum(s*v for s,v in zip(signs,e))] += 1
    assert set(classical) == {-2,2}
    mask_cases = []
    for p,t in ((Fraction(1,2),0), (Fraction(1,2),Fraction(1,4)), (Fraction(1,2),1),
                (Fraction(1,4),Fraction(1,2)), (0,1)):
        e, ma, mb = [], [], []
        for x,y in SETTINGS:
            table = Counter()
            for r,c in SETTINGS:
                table[r, r ^ (x*y*c)] += (p if r else 1-p)*(t if c else 1-t)
            e.append(sum((-1)**(a^b)*n for (a,b),n in table.items()))
            ma.append(sum(n for (a,b),n in table.items() if a))
            mb.append(sum(n for (a,b),n in table.items() if b))
        assert sum(e[:3])-e[3] == 2+2*t and len(set(ma)) == 1 and mb[3]-mb[1] == t*(1-2*p)
        mask_cases.append({"P_R_one":str(p), "flip":str(t), "correlations":list(map(str,e)),
                           "alice_one":list(map(str,ma)), "bob_one":list(map(str,mb))})
    e = []
    for x,y in SETTINGS:
        pair_a, pair_b = Counter(), Counter()
        products = []
        for r,s,m in product(range(2),repeat=3):
            left = (r,s)
            right = (r,1-s) if m == 0 or (x,y) == (0,0) else (s,r)
            pair_a[left] += 1
            pair_b[right] += 1
            products.append((-1)**(left[x]^right[y]))
        assert set(pair_a.values()) == set(pair_b.values()) == {2}
        e.append(Fraction(sum(products),len(products)))
    # Real Pauli axes (Z, X): the X coefficient carries an implicit sqrt(3).
    a_axes = ((1,0), (Fraction(1,2),Fraction(1,2)))
    b_axes = ((1,0), (Fraction(1,2),Fraction(-1,2)))
    assert e == [a_axes[x][0]*b_axes[y][0] + 3*a_axes[x][1]*b_axes[y][1] for x,y in SETTINGS]
    assert sum(e[:3])-e[3] == Fraction(5,2)
    return {"deterministic_oriented_CHSH": dict(sorted(classical.items())), "one_changed_rule":mask_cases,
            "quantum_compatible_external_control":{"correlations":list(map(str,e)), "CHSH":"5/2"}}


def run():
    return {"first_rounds":check_rounds(), "small_NAE":check_six_bit_nae(),
            "inconsistent_exact_context_families":parity_obstructions(), "setting_controls":controls()}


if __name__ == "__main__":
    computed = json.dumps(run(), indent=2)
    if sys.argv[1:] == ["--json"]:
        print(computed)
    elif sys.argv[1:]:
        raise SystemExit("Use --json to print recomputed results.")
    else:
        saved = json.loads((FAMILY / "result.json").read_text())
        if saved["checks"] != json.loads(computed):
            raise SystemExit("Recomputed scientific controls differ from the stored result.")
        for path, expected in saved["source_sha256"].items():
            if sha256((ROOT / path).read_bytes()).hexdigest() != expected:
                raise SystemExit(f"Source digest differs for {path}")
        print("PASS. Recomputed funded births, exact restrictions, canonical projections, survival and setting controls.")
