#!/usr/bin/env python3
"""Recompute the finite controls accompanying the symbolic proof."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys


FAMILY = Path(__file__).resolve().parent
ROOT = FAMILY.parents[2]
BITS = (0, 1)
SETTINGS = tuple(product(BITS, repeat=2))
ORIENTATIONS = tuple(
    signs for signs in product((-1, 1), repeat=4) if signs.count(-1) % 2 == 1
)


def lawful(values, law):
    if law == "parity":
        return sum(values) % 2 == 0
    if law == "not_all_equal":
        return len(set(values)) > 1
    raise ValueError(law)


def maximum_chsh(correlations):
    return max(sum(s * e for s, e in zip(signs, correlations)) for signs in ORIENTATIONS)


def check_native_triples_and_extensions():
    results = {}
    for law, arity in (("parity", 3), ("not_all_equal", 3), ("parity", 4)):
        names = list("ABCD"[:arity])
        states = tuple(product(BITS, repeat=arity))
        allowed = {state for state in states if lawful(state, law)}
        clauses = [
            " ".join(("~" if value else "") + name for name, value in zip(names, state))
            for state in states if state not in allowed
        ]
        verdicts = []
        for extra_clauses in ([], ["~A"]):
            command = [
                sys.executable, "-B", "-m", "knotlab", "check", "--cnf",
                "; ".join(clauses + extra_clauses), "--loops", *names[:-1],
                "--contact", names[-1], "--json",
            ]
            process = subprocess.run(
                command, cwd=ROOT, env=dict(os.environ, PYTHONPATH=str(ROOT / "tools")),
                check=False, capture_output=True, text=True,
            )
            if process.returncode not in (0, 1):
                raise RuntimeError(process.stderr)
            verdict = json.loads(process.stdout)
            expected = {s for s in allowed if not extra_clauses or s[0] == 0}
            assert {tuple(map(int, row)) for row in verdict["allowed"]} == expected
            verdicts.append(verdict["is_knot"])
        assert verdicts == [True, False]
        results[f"{law}_{arity}"] = {"allowed": len(allowed), "is_knot": verdicts[0],
                                    "pinned_control_is_knot": verdicts[1]}

    cases = 0
    for p, f, law in product((1, 2, 3), (1, 2, 3), ("parity", "not_all_equal")):
        for old in product(BITS, repeat=p):
            lifts = sum(lawful(old + fresh, law) for fresh in product(BITS, repeat=f))
            expected = 2 ** (f - 1) if law == "parity" else 2**f - (len(set(old)) == 1)
            assert lifts == expected > 0
            cases += 1
    results["old_value_cases_checked"] = cases
    return results


def check_selected_outer_events():
    center = (0, 1, 2)
    outer = ((0, 3, 4), (1, 5, 6), (2, 7, 8))
    results = {}
    for law in ("parity", "not_all_equal"):
        rows = [
            row for row in product(BITS, repeat=9)
            if all(lawful(tuple(row[i] for i in c), law) for c in (center, *outer))
        ]
        single = {t for t in product(BITS, repeat=3) if lawful(t, law)}
        for c in (center, *outer):
            assert {tuple(row[i] for i in c) for row in rows} == single
        counts = []
        for k in range(4):
            values = set()
            for choice in combinations(outer, k):
                values.add(sum(all(tuple(row[i] for i in c) == (1, 1, 0)
                                   for c in choice) for row in rows))
            assert len(values) == 1
            counts.append(values.pop())
        assert all(n > 0 for n in counts[:3]) and counts[3] == 0
        results[law] = {"states_extending_any_fixed_k_events_for_k_0_to_3": counts}
    return results


def check_contexts(contexts, targets):
    size = max(max(c) for c in contexts) + 1
    rows = list(product(BITS, repeat=size))
    local = [
        [t for t in product(BITS, repeat=len(c)) if sum(t) % 2 == target]
        for c, target in zip(contexts, targets)
    ]
    for i, j in combinations(range(len(contexts)), 2):
        shared = sorted(set(contexts[i]) & set(contexts[j]))
        marginals = []
        for side in (i, j):
            indices = [contexts[side].index(mark) for mark in shared]
            marginals.append(Counter(tuple(row[k] for k in indices) for row in local[side]))
        assert marginals[0] == marginals[1]
    checks = [
        tuple(sum(row[k] for k in context) % 2 for context in contexts)
        for row in rows
    ]
    common_count = checks.count(tuple(targets))
    assert common_count == 0
    omissions, repairs = [], []
    for i in range(len(contexts)):
        altered = tuple(bit ^ (pos == i) for pos, bit in enumerate(targets))
        repaired = [row for row, signs in zip(rows, checks) if signs == altered]
        dropped = [row for row, signs in zip(rows, checks)
                   if all(s == t for j, (s, t) in enumerate(zip(signs, targets)) if j != i)]
        assert repaired == dropped and len(repaired) == 2 ** (size - len(contexts) + 1)
        for j, c in enumerate(contexts):
            counts = Counter(tuple(row[k] for k in c) for row in repaired)
            support = set(t for t in product(BITS, repeat=len(c)) if sum(t) % 2 == altered[j])
            assert set(counts) == support and len(set(counts.values())) == 1
        omissions.append(len(dropped))
        repairs.append(len(repaired))
    return {"common_assignments": common_count, "local_events_per_context": list(map(len, local)),
            "agree_on_overlaps": True, "after_each_omission": omissions,
            "after_each_one_sign_repair": repairs}


def table_summary(tables):
    correlations = []
    marginals = []
    for xy in SETTINGS:
        cells = tables[xy]
        total = sum(cells.values())
        correlations.append(Fraction(sum((-1) ** (a ^ b) * n for (a, b), n in cells.items()), total))
        marginals.append(tuple(Fraction(sum(n for ab, n in cells.items() if ab[side]), total)
                               for side in (0, 1)))
    alice = max(abs(marginals[2*x][0] - marginals[2*x+1][0]) for x in BITS)
    bob = max(abs(marginals[y][1] - marginals[2+y][1]) for y in BITS)
    signed = sum(correlations[:3]) - correlations[3]
    return {"E": list(map(str, correlations)), "signed_S": str(signed),
            "maximum_CHSH": str(maximum_chsh(correlations)),
            "selected_marginal_TV_A_B": [str(alice), str(bob)]}


def check_bell_controls():
    single_state_scores = Counter()
    for a0, a1, b0, b1 in product((-1, 1), repeat=4):
        e = (a0*b0, a0*b1, a1*b0, a1*b1)
        assert maximum_chsh(e) == 2
        single_state_scores[sum(e[:3]) - e[3]] += 1
    masks = []
    for p, t in ((Fraction(1, 2), 0), (Fraction(1, 2), Fraction(1, 4)),
                 (Fraction(1, 2), 1), (Fraction(1, 4), Fraction(1, 2)), (0, 1)):
        tables = {}
        for x, y in SETTINGS:
            cells = Counter()
            for r, c in SETTINGS:
                cells[r, r ^ (x*y*c)] += (p if r else 1-p) * (t if c else 1-t)
            tables[x, y] = cells
        summary = table_summary(tables)
        assert Fraction(summary["signed_S"]) == 2 + 2*t
        assert list(map(Fraction, summary["selected_marginal_TV_A_B"])) == [0, abs(t*(1-2*p))]
        masks.append({"mask_one": str(p), "flip_probability": str(t), **summary})
    noisy = {(x,y): {(a,b): 7 if a ^ b == x*y else 1 for a,b in SETTINGS} for x,y in SETTINGS}
    compatible = sum(all(noisy[x,y][bits[x], bits[2+y]] > 0 for x,y in SETTINGS)
                     for bits in product(BITS, repeat=4))
    noisy_summary = table_summary(noisy)
    assert compatible == 16 and noisy_summary["signed_S"] == "3"
    return {"signed_scores_on_16_assignments": dict(sorted(single_state_scores.items())),
            "one_context_change": masks,
            "full_support_noise": {**noisy_summary, "compatible_support_assignments": compatible}}


def check_added_state_weight():
    rows = [
        (x, y, (a0,a1), (b0,b1)) for x,a0,a1,p,y,b0,b1,q in product(BITS, repeat=8)
        if lawful((x,a0,a1,p), "parity") and lawful((y,b0,b1,q), "parity")
    ]
    results = []
    for preferred, other in ((1,1), (3,1), (4,1), (5,1), (1,0)):
        endogenous = {xy: Counter() for xy in SETTINGS}
        external = {xy: Counter() for xy in SETTINGS}
        alice = {xy: Counter() for xy in SETTINGS}
        bob = {xy: Counter() for xy in SETTINGS}
        for x, y, a, b in rows:
            weight = preferred if a[x] ^ b[y] == x*y else other
            endogenous[x,y][a[x],b[y]] += weight
            alice[x,y][a] += weight
            bob[x,y][b] += weight
            for i, j in SETTINGS:
                external[i,j][a[i],b[j]] += weight
        for x,y in SETTINGS:
            assert len(alice[x,y]) == len(bob[x,y]) == 4
            assert set(alice[x,y].values()) == set(bob[x,y].values()) == {2*(preferred+other)}
        conditioned, intervened = map(table_summary, (endogenous, external))
        r = Fraction(preferred-other, preferred+other)
        assert Fraction(conditioned["signed_S"]) == 4*r
        assert Fraction(intervened["signed_S"]) == r
        results.append({"weights_preferred_other": [preferred, other], "conditional": conditioned,
                        "external": intervened, "full_pair_marginal_TV_A_B": [0, 0]})
    return results


def check_quantum_table():
    # Bob's integer matrices are sqrt(2) times his normalized observables.
    z = ((1, 0), (0, -1))
    x = ((0, 1), (1, 0))
    alice = (z, x)
    bob = tuple([[z[i][j] + s*x[i][j] for j in BITS] for i in BITS] for s in (1, -1))
    for b in bob:
        assert [[sum(b[i][j]*b[j][k] for j in BITS) for k in BITS] for i in BITS] == [[2,0],[0,2]]
    cells = {}
    for i,j in SETTINGS:
        # On |Phi+>, <A tensor B> = tr(transpose(A) B)/2.
        scaled = Fraction(sum(alice[i][m][n]*bob[j][m][n] for m,n in SETTINGS), 2)
        assert scaled == (-1)**(i*j)
        assert sum(alice[i][m][m] for m in BITS) == sum(bob[j][m][m] for m in BITS) == 0
        correlation = Fraction(2, 3)*scaled  # visibility/sqrt(2)
        cells[i,j] = {(a,b): (1 + (-1)**(a ^ b)*correlation)/4 for a,b in SETTINGS}
        assert all(cells[i,j][a,b] == Fraction(5 if a ^ b == i*j else 1, 12) for a,b in SETTINGS)
    return {"preferred_to_other_weight": "5:1", "visibility": "2 sqrt(2)/3",
            "preferred_pair_probability": "5/12", "other_pair_probability": "1/12",
            **table_summary(cells)}


def subspaces():
    zero = frozenset({0})
    seen, queue = {zero}, [zero]
    while queue:
        h = queue.pop()
        for v in set(range(16)) - h:
            enlarged = h | {w ^ v for w in h}
            if enlarged not in seen:
                seen.add(enlarged)
                queue.append(enlarged)
    return sorted(seen, key=lambda h: (len(h), sorted(h)))


def register_answer(pair, index, protocol):
    if protocol == "I":
        return (pair >> index) & 1
    return int(pair == 3*index)


def check_all_affine_register_laws():
    """One representative of every uniform affine law of four marked output bits given x,y."""
    laws_by_size = Counter()
    results = {name: Counter() for name in ("I", "II")}
    one_bit = {name: Counter() for name in ("I", "II")}
    hiding = coupled = 0
    for h in subspaces():
        reps = sorted({min(w ^ shift for w in h) for shift in range(16)})
        cosets = {shift: tuple(sorted(w ^ shift for w in h)) for shift in range(16)}
        counts = {}
        for shift, records in cosets.items():
            alice_pairs = Counter(word & 3 for word in records)
            bob_pairs = Counter(word >> 2 for word in records)
            for xy, protocol in product(SETTINGS, results):
                x, y = xy
                answers = [(register_answer(word & 3, x, protocol),
                            register_answer(word >> 2, y, protocol)) for word in records]
                counts[shift, xy, protocol] = (
                    sum(1 if a == b else -1 for a,b in answers),
                    sum(a for a,b in answers), sum(b for a,b in answers),
                    alice_pairs, bob_pairs,
                )
        for base, dx, dy in product(reps, repeat=3):
            shifts = [base ^ (dx if x else 0) ^ (dy if y else 0) for x,y in SETTINGS]
            laws_by_size[len(h)] += 1
            registers = [counts[s,xy,"I"] for s,xy in zip(shifts, SETTINGS)]
            hides = (all(registers[2*x][3] == registers[2*x+1][3] for x in BITS) and
                     all(registers[y][4] == registers[2+y][4] for y in BITS))
            hiding += hides

            ux = next((w for w in h if (dx ^ w) >> 2 == 0), None)
            vy = next((w for w in h if (dy ^ w) & 3 == 0), None)
            has_coupling = ux is not None and vy is not None
            assert hides == has_coupling
            if has_coupling:
                coupled += 1
                for (x,y), shift in zip(SETTINGS, shifts):
                    reproduced = []
                    for s in h:
                        a = (base ^ s ^ ((dx ^ ux) if x else 0)) & 3
                        b = (base ^ s ^ ((dy ^ vy) if y else 0)) >> 2
                        reproduced.append(a | (b << 2))
                    assert sorted(reproduced) == list(cosets[shift])

            for protocol, row in results.items():
                observed = [counts[s,xy,protocol] for s,xy in zip(shifts, SETTINGS)]
                chsh = maximum_chsh([v[0] for v in observed])
                answer_hides = (all(observed[2*x][1] == observed[2*x+1][1] for x in BITS) and
                                all(observed[y][2] == observed[2+y][2] for y in BITS))
                excess = chsh > 2 * len(h)
                row["excess"] += excess
                row["excess_hiding_full_registers"] += excess and hides
                row["excess_hiding_answers"] += excess and answer_hides
                if len(h) <= 2:
                    # Nonzero rank-one residual: each of the three form offsets has two representatives.
                    multiplicity = 1 if len(h) == 1 else 8
                    score = Fraction(chsh, len(h))
                    one_bit[protocol][f"maximum_{score}"] += multiplicity
                    one_bit[protocol]["excess_hiding_answers"] += multiplicity*(excess and answer_hides)
                    one_bit[protocol]["excess_hiding_full_registers"] += multiplicity*(excess and hides)
                assert not (excess and hides)
                if protocol == "II":
                    assert not (excess and answer_hides)
    assert sum(laws_by_size.values()) == 14137 and 0 < coupled == hiding < 14137
    assert results["I"]["excess_hiding_answers"] > 0
    return {"laws_by_residual_image_size": dict(sorted(laws_by_size.items())),
            "total_distinct_marked_conditional_laws": sum(laws_by_size.values()),
            "whole_register_invariant": hiding, "explicit_full_register_couplings": coupled,
            "protocols": results, "one_residual_bit_parameterizations": one_bit}


def run():
    ghz = [(0,2,4), (0,3,5), (1,2,5), (1,3,4)]
    square = [tuple(range(3*i,3*i+3)) for i in range(3)]
    square += [tuple(range(i,9,3)) for i in range(3)]
    return {
        "growth_and_knot_controls": check_native_triples_and_extensions(),
        "selected_outer_knot_events": check_selected_outer_events(),
        "GHZ": check_contexts(ghz, (0,1,1,1)),
        "Mermin_Peres_square": check_contexts(square, (0,0,0,0,0,1)),
        "bell_controls": check_bell_controls(),
        "added_conditional_state_weight": check_added_state_weight(),
        "quantum_realization_added_weight": check_quantum_table(),
        "affine_register_laws": check_all_affine_register_laws(),
    }


if __name__ == "__main__":
    computed = run()
    serialized = json.dumps(computed, indent=2)
    if sys.argv[1:] == ["--json"]:
        print(serialized)
    elif sys.argv[1:]:
        raise SystemExit("Use --json to print the recomputed controls.")
    else:
        stored = json.loads((FAMILY / "result.json").read_text())
        if json.loads(serialized) != stored["checks"]:
            raise SystemExit("Stored controls differ from recomputation.")
        for key, path in stored["source_files"].items():
            if sha256((ROOT / path).read_bytes()).hexdigest() != stored["sha256"][key]:
                raise SystemExit(f"Source digest differs for {path}")
        print("PASS. Recomputed growth, support, signed-context, weighting and 14,137 affine-register controls.")
