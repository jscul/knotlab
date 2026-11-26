"""Replay the reordering-sign test: the knot census, the growth fixtures and five readings of order freedom.

Swap rule S_s: distinctions are listed in order of creation; a listing's weight relative to a reference listing is s raised to
the number of pairs of distinctions that both hold 1 and whose relative order differs. Readings are the ordinary Z and the
real flip X, held fixed. Everything is exact: amplitudes are integers (or Gaussian integers for the Y benchmark).
"""

import argparse
import json
import random
import time
from fractions import Fraction
from itertools import combinations, permutations, product
from math import factorial
from pathlib import Path
from runpy import run_path

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
GROWTH = (ROOT / "artifacts/GROWTH-SIGN-LAW-20261125-001/GROWTH-SIGN-LAW-20261125-001-E001_growth_operations"
          / "check.py")
SEED = 20261126


# ---------------------------------------------------------------- listings and the swap rule

def inverted_pairs(listing, reference):
    """Pairs of items whose relative order differs between two listings of the same items."""
    rank = {item: i for i, item in enumerate(reference)}
    pos = [rank[item] for item in listing]
    return [(listing[i], listing[j]) for i, j in combinations(range(len(listing)), 2) if pos[i] > pos[j]]


def swap_count(word, listing, reference):
    """Direct count over the full listing: inverted pairs whose two distinctions both hold 1."""
    return sum(1 for u, v in inverted_pairs(listing, reference) if word[u] and word[v])


def sign_of(count, s):
    return s ** count


# ---------------------------------------------------------------- expectations on signed states

def expectation(state, flips, phase_strings=(), diag=None):
    """<psi| O |psi> / <psi|psi> for O = (flip pairs applied in sequence, each with a string evaluated on the current word),
    preceded by an optional diagonal factor diag(word) on the ket. Real amplitudes only."""
    norm = sum(a * a for a in state.values())
    total = 0
    for word, amp in state.items():
        w = list(word)
        phase = diag(word) if diag else 1
        if phase == 0:
            continue
        for flip, string in zip(flips, phase_strings or [()] * len(flips)):
            if string and sum(w[d] for d in string) % 2:
                phase = -phase
            for d in flip:
                w[d] ^= 1
        total += phase * amp * state.get(tuple(w), 0)
    return Fraction(total, norm)


def correlation(state, readers, T, strings=None):
    """c(T) = <X_T Z_rest> with logical readings: reader j = (x_j, flip set of j)."""
    flips = [readers[j][1] for j in sorted(T)]
    strs = [strings[j] for j in sorted(T)] if strings else None
    rest = [readers[j][0] for j in range(len(readers)) if j not in T]
    return expectation(state, flips, strs, diag=lambda w: (-1) ** (sum(w[x] for x in rest) % 2))


def even_sets(n):
    return [frozenset(c) for k in range(0, n + 1, 2) for c in combinations(range(n), k)]


def contradiction(state, readers, strings=None):
    """Full GHZ contradiction: every even-size c(T) is +-1 and T -> c(T)/c(empty) is not a character."""
    n = len(readers)
    sets = even_sets(n)
    c = {T: correlation(state, readers, T, strings) for T in sets}
    all_sharp = all(abs(v) == 1 for v in c.values())
    if not all_sharp:
        return {"all_correlations_sharp": False, "full_contradiction": False,
                "mixed_nonzero": sum(1 for T, v in c.items() if T and v != 0)}
    f = {T: c[T] / c[frozenset()] for T in sets}
    character = all(f[T ^ U] == f[T] * f[U] for T in sets for U in sets)
    return {"all_correlations_sharp": True, "full_contradiction": not character,
            "mixed_nonzero": sum(1 for T, v in c.items() if T and v != 0)}


def mermin3(c, best=True):
    """Mermin score <ZZZ> - <XXZ> - <XZX> - <ZXX>, maximised over X-outcome relabellings when best."""
    pairs = [frozenset(p) for p in ((0, 1), (0, 2), (1, 2))]
    scores = []
    for u in product((0, 1), repeat=3) if best else [(0, 0, 0)]:
        flip = lambda T: (-1) ** (sum(u[j] for j in T) % 2)
        scores.append(c[frozenset()] - sum(c[T] * flip(T) for T in pairs))
    return max(scores, key=abs)


# ---------------------------------------------------------------- probability tables for three readers

def table(state, readers, strings=None):
    """P(setting, outcome) for logical readers: Z projector on x_j, or (1 + (-1)^o X_j)/2."""
    out = {}
    for setting in product((0, 1), repeat=3):
        row = []
        changed = [j for j in range(3) if setting[j]]
        for outcome in product((0, 1), repeat=3):
            total = Fraction(0)
            for k in range(len(changed) + 1):
                for S in combinations(changed, k):
                    flips = [readers[j][1] for j in S]
                    strs = [strings[j] for j in S] if strings else None
                    zs = [(readers[j][0], outcome[j]) for j in range(3) if not setting[j]]
                    diag = lambda w, zs=zs: int(all(w[x] == o for x, o in zs))
                    sign = (-1) ** (sum(outcome[j] for j in S) % 2)
                    total += sign * expectation(state, flips, strs, diag)
            row.append(total / 2 ** len(changed))
        out[setting] = tuple(row)
    return out


def target():
    """The 64-cell three-reader table: scored settings give the required parity with 1/4 each; others 1/8."""
    out = {}
    for setting in product((0, 1), repeat=3):
        out[setting] = tuple(
            Fraction(1, 8) if sum(setting) % 2 else Fraction(int(sum(o) % 2 == int(any(setting))), 4)
            for o in product((0, 1), repeat=3))
    return out


def relabel(tab, u):
    return {s: tuple(tab[s][int("".join(str(o[j] ^ (u[j] & s[j])) for j in range(3)), 2)]
                     for o in product((0, 1), repeat=3)) for s in tab}


def match_target(tab):
    goal = target()
    exact = sum(tab[s][i] == goal[s][i] for s in goal for i in range(8))
    for u in product((0, 1), repeat=3):
        if relabel(tab, u) == goal:
            return {"exact_cells": exact, "matches_up_to_relabelling": True, "relabelling_u": list(u)}
    return {"exact_cells": exact, "matches_up_to_relabelling": False, "relabelling_u": None}


def win_rate(tab):
    goal = target()
    scored = [s for s in goal if sum(s) % 2 == 0]
    wins = [sum(tab[s][i] for i, o in enumerate(product((0, 1), repeat=3)) if goal[s][i]) for s in scored]
    return sum(wins) / 4


def y_benchmark():
    """++++ read with Z or Y (complex), Gaussian-integer amplitudes squared."""
    even = [w for w in product((0, 1), repeat=3) if sum(w) % 2 == 0]
    out = {}
    for setting in product((0, 1), repeat=3):
        row = []
        for outcome in product((0, 1), repeat=3):
            amp = 0
            for w in even:
                if any(not setting[j] and w[j] != outcome[j] for j in range(3)):
                    continue
                term = 1
                for j in range(3):
                    if setting[j] and w[j]:
                        term *= -1j * (-1) ** outcome[j]
                amp += term
            p = (amp * amp.conjugate()).real
            assert p == int(p)
            row.append(Fraction(int(p), 4 * 2 ** sum(setting)))
        out[setting] = tuple(row)
    return out


# ---------------------------------------------------------------- one parity knot read distinction by distinction

def knot_state(n, order, s):
    """Even words of n distinctions, signed by the listing `order` relative to the identity listing."""
    ident = list(range(n))
    return {w: sign_of(swap_count(w, list(order), ident), s)
            for w in product((0, 1), repeat=n) if sum(w) % 2 == 0}


def single_readers(n):
    return [(j, (j,)) for j in range(n)]


def prefix_suffix_reversals(n):
    return {tuple(list(reversed(range(p))) + list(reversed(range(p, n)))) for p in range(n)}


def polar_form_vanishes(order, n):
    """Polar form of q = sum over inverted pairs of w_i w_j on the even code, tested on a basis."""
    inv = inverted_pairs(list(order), list(range(n)))
    basis = [tuple(int(k in (0, i)) for k in range(n)) for i in range(1, n)]
    q = lambda w: sum(w[a] * w[b] for a, b in inv) % 2
    add = lambda u, v: tuple(a ^ b for a, b in zip(u, v))
    return all((q(add(u, v)) - q(u) - q(v)) % 2 == 0 for u in basis for v in basis)


def knot_census(n, s=-1):
    rows = []
    predicted = prefix_suffix_reversals(n)
    readers = single_readers(n)
    for order in permutations(range(n)):
        state = knot_state(n, order, s)
        verdict = contradiction(state, readers)
        parity = len(inverted_pairs(list(order), list(range(n)))) % 2
        rows.append((order, verdict["full_contradiction"], parity, polar_form_vanishes(order, n)))
    carried = {o for o, full, _, _ in rows if full}
    return {
        "n": n, "orders": len(rows), "orders_with_full_contradiction": len(carried),
        "equals_prefix_suffix_reversals": carried == predicted,
        "full_reversal_carries": tuple(reversed(range(n))) in carried,
        "full_reversal_is_odd": len(inverted_pairs(list(reversed(range(n))), list(range(n)))) % 2 == 1,
        "single_swap_carries": (1, 0, *range(2, n)) in carried,
        "odd_orders": sum(p for _, _, p, _ in rows),
        "parity_predicts_exactly": carried == {o for o, _, p, _ in rows if p},
        "nonvanishing_polar_form_orders": sum(1 for *_, v in rows if not v),
        "carried_orders_have_nonvanishing_polar_form": all(not v for o, full, _, v in rows if full),
    }


def reversal_lemma(n):
    """(-1)^(k(k-1)/2) = (-i)^k on even words, and the reversal-signed knot carries the full contradiction."""
    identity_holds = all((-1) ** (k * (k - 1) // 2) == ((-1j) ** k).real and ((-1j) ** k).imag == 0
                         for k in range(0, n + 1, 2))
    state = knot_state(n, tuple(reversed(range(n))), -1)
    reversal_is_quarter_turn = all(
        state[w] == round(((-1j) ** sum(w)).real) for w in state)
    return {"n": n, "identity": identity_holds, "reversal_sign_is_quarter_turn_per_occupied": reversal_is_quarter_turn,
            "full_contradiction": contradiction(state, single_readers(n))["full_contradiction"]}


# ---------------------------------------------------------------- growth fixtures

def load_growth():
    g = run_path(str(GROWTH))
    advance, _, _ = g["archives"]()
    return g, advance


def fixture(g, advance, source):
    case = g["ordinary_case"](source, advance)
    births = [(tuple(b["inherited"]), tuple(b["fresh"])) for b in case["births"]]
    grown = case["grown_holdings"]
    names = sorted(g["ownership"](grown))
    basis = g["allowed_basis"](grown)
    old = sorted(g["ownership"](source))
    return {"source": source, "births": births, "grown": grown, "names": names, "basis": basis, "old": old,
            "old_basis": g["allowed_basis"](source)}


def span(basis, names):
    words = {0}
    for b in basis:
        words |= {w ^ b for w in words}
    return [tuple((w >> d) & 1 for d in range(max(names) + 1)) for w in sorted(words)]


def listing_for(fx, order):
    """Old distinctions in index order, then each birth's fresh distinctions in commit order."""
    out = list(fx["old"])
    for i in order:
        out.extend(fx["births"][i][1])
    return out


def block_q(word, fx, order, reference_order):
    """Block formula: inverted pairs of births, times the parities of their fresh distinctions."""
    births = fx["births"]
    p = [sum(word[d] for d in fresh) % 2 for _, fresh in births]
    inv = inverted_pairs(list(order), list(reference_order))
    return sum(p[i] * p[j] for i, j in inv)


def parity_matrix(fx):
    """P[a][i]: parity of basis word a on birth i's fresh distinctions."""
    masks = [sum(1 << d for d in fresh) for _, fresh in fx["births"]]
    return np.array([[bin(u & m).count("1") % 2 for m in masks] for u in fx["basis"]], dtype=np.int64)


def polar_matrix(P, order, reference_order):
    """Polar form of the block quadratic form on the grown words, B = P A P^T mod 2, A the inverted-pair matrix."""
    m = P.shape[1]
    A = np.zeros((m, m), dtype=np.int64)
    for i, j in inverted_pairs(list(order), list(reference_order)):
        A[i, j] = A[j, i] = 1
    return tuple(((P @ A @ P.T) % 2).flatten().tolist())


def growth_fixture_census(fx, rng, s=-1):
    m = len(fx["births"])
    prod_order = tuple(range(m))
    words = span(fx["basis"], fx["names"])
    sample = words if len(words) <= 4096 else rng.sample(words, 256)
    gate_ok = True
    fresh_parity_ok = True
    for w in sample:
        for inh, fresh in fx["births"]:
            if sum(w[d] for d in inh) % 2 != sum(w[d] for d in fresh) % 2:
                fresh_parity_ok = False
    orders = list(permutations(range(m)))
    gate_orders = orders if len(orders) <= 720 else rng.sample(orders, 120)
    for order in gate_orders:
        listing, reference = listing_for(fx, order), listing_for(fx, prod_order)
        for w in sample:
            if swap_count(w, listing, reference) % 2 != block_q(w, fx, order, prod_order) % 2:
                gate_ok = False
    P = parity_matrix(fx)
    zero = polar_matrix(P, prod_order, prod_order)
    forms = {}
    for order in orders:
        forms.setdefault(polar_matrix(P, order, prod_order), []).append(order)
    nonremovable = sum(len(v) for k, v in forms.items() if any(k))
    # R2: coherent equal-weight and sign-weighted sums over all orders, on the old allowed words.
    old_words = span(fx["old_basis"], fx["old"])
    p_of = lambda w: [sum(w[d] for d in inh) % 2 for inh, _ in fx["births"]]
    survivors = sgn_survivors = 0
    brute = len(old_words) * len(orders) <= 300000
    assert brute or s == -1, "the closed formula is the s = -1 antisymmetrizer"
    formula_ok = True
    for w in old_words:
        p = p_of(w)
        k = sum(p)
        predicted = factorial(m) if (k <= 1 or s == 1) else 0
        if brute:
            total = sum(sign_of(sum(p[i] * p[j] for i, j in inverted_pairs(list(o), list(prod_order))), s)
                        for o in orders)
            sgn_total = sum((-1) ** (len(inverted_pairs(list(o), list(prod_order))) % 2)
                            * sign_of(sum(p[i] * p[j] for i, j in inverted_pairs(list(o), list(prod_order))), s)
                            for o in orders)
            formula_ok &= total == predicted
            sgn_survivors += sgn_total != 0
        survivors += predicted != 0
    return {
        "births": [[list(i), list(f)] for i, f in fx["births"]],
        "grown_words": len(words), "words_in_gate_sample": len(sample), "orders": len(orders),
        "orders_in_gate": len(gate_orders),
        "gate_direct_count_equals_block_formula": gate_ok,
        "fresh_parity_equals_inherited_parity": fresh_parity_ok,
        "production_polar_form_is_zero": not any(zero),
        "distinct_polar_forms_across_orders": len(forms),
        "orders_with_nonremovable_sign": nonremovable,
        "R2_old_allowed_words": len(old_words),
        "R2_surviving_words_equal_weight": survivors,
        "R2_formula_checked_by_brute_force": brute and formula_ok,
        "R2_surviving_words_sign_weight": sgn_survivors if brute else None,
    }


# ---------------------------------------------------------------- the three-reader experiment on the grown ternary

def ternary_experiment(fx, s=-1, reference_orders=None):
    """Block readers: reader j holds old distinction j and its child's fresh pair; logical X = X_x X_y."""
    m = len(fx["births"])
    assert m == 3 and fx["old"] == [0, 1, 2]
    words = span(fx["basis"], fx["names"])
    child_of = {inh[0]: fresh for inh, fresh in fx["births"]}
    block = [(j, (j, child_of[j][0])) for j in range(3)]
    alone = [(j, (j,)) for j in range(3)]
    out = {}
    for ref in reference_orders or [tuple(range(3))]:
        rows = {}
        for order in permutations(range(3)):
            listing, reference = listing_for(fx, order), listing_for(fx, ref)
            state = {w: sign_of(swap_count(w, listing, reference), s) for w in words}
            sets = even_sets(3)
            c = {T: correlation(state, block, T) for T in sets}
            tab = table(state, block)
            parity = len(inverted_pairs(list(order), list(ref))) % 2
            row = {
                "relative_inversions": len(inverted_pairs(list(order), list(ref))),
                "relative_order_odd": bool(parity),
                "correlations_ZZZ_XXZ_XZX_ZXX": [str(c[frozenset(t)]) for t in ((), (0, 1), (0, 2), (1, 2))],
                "product_P": str(c[frozenset()] * c[frozenset((0, 1))] * c[frozenset((0, 2))] * c[frozenset((1, 2))]),
                "full_contradiction": contradiction(state, block)["full_contradiction"],
                "target": match_target(tab),
                "win_rate_on_scored_settings": str(win_rate(tab)),
                "old_distinction_alone_win_rate": str(win_rate(table(state, alone))),
            }
            rows["".join("abc"[i] for i in order)] = row
            row["_c"] = c
        out["reference_" + "".join("abc"[i] for i in ref)] = rows
    return out


def order_blind(rows, which):
    """R1b: average the correlations over a set of orders the readers are not told; Mermin score."""
    picked = [r["_c"] for name, r in rows.items() if which(r)]
    avg = {T: sum(c[T] for c in picked) / len(picked) for T in picked[0]}
    return {"orders": len(picked),
            "average_ZZZ_XXZ_XZX_ZXX": [str(avg[frozenset(t)]) for t in ((), (0, 1), (0, 2), (1, 2))],
            "best_mermin_score": str(mermin3(avg)), "local_bound": 2, "quantum_value": 4}


def ternary_jw(fx, s=-1):
    """JW: the rule applied to the readings too. The flip of reader j picks up s for each distinction holding 1 strictly
    between x_j and y_j in the listing used. Compare two conventions (production listing with signed state, own listing
    with unsigned state); they must agree, and the question is whether tables differ across orders."""
    words = span(fx["basis"], fx["names"])
    child_of = {inh[0]: fresh for inh, fresh in fx["births"]}
    block = [(j, (j, child_of[j][0])) for j in range(3)]
    prod_listing = listing_for(fx, (0, 1, 2))
    tables, conv_ok, seq_ok = {}, True, True
    for order in permutations(range(3)):
        own = listing_for(fx, order)
        results = []
        for listing, signed in ((prod_listing, True), (own, False)):
            state = {w: sign_of(swap_count(w, own, listing), s) if signed else 1 for w in words}
            pos = {d: i for i, d in enumerate(listing)}
            strings = [tuple(d for d in listing if min(pos[j], pos[child_of[j][0]]) < pos[d]
                             < max(pos[j], pos[child_of[j][0]])) for j in range(3)]
            results.append(table(state, block, strings))
            # sequence check: the dressed flips are physical even operators and must commute
            for T in even_sets(3):
                if len(T) == 2:
                    a, b = sorted(T)
                    rest = [block[j][0] for j in range(3) if j not in T]
                    d = lambda w, rest=rest: (-1) ** (sum(w[x] for x in rest) % 2)
                    one = expectation(state, [block[a][1], block[b][1]], [strings[a], strings[b]], d)
                    two = expectation(state, [block[b][1], block[a][1]], [strings[b], strings[a]], d)
                    seq_ok &= one == two
        conv_ok &= results[0] == results[1]
        tables["".join("abc"[i] for i in order)] = results[0]
    distinct = {json.dumps({str(k): list(map(str, v)) for k, v in t.items()}) for t in tables.values()}
    return {"conventions_agree": conv_ok, "dressed_flips_commute": seq_ok,
            "distinct_tables_across_orders": len(distinct),
            "per_order": {name: {"target": match_target(t), "win_rate": str(win_rate(t))} for name, t in tables.items()}}


# ---------------------------------------------------------------- assembly

def strip(obj):
    if isinstance(obj, dict):
        return {k: strip(v) for k, v in obj.items() if not k.startswith("_")}
    return obj


def results():
    timing = {}
    t0 = time.perf_counter()
    rng = random.Random(SEED)
    out = {}
    # Gate: benchmark tables and the mutant.
    plus_minus = knot_state(3, (2, 1, 0), -1)
    mutant = knot_state(3, (2, 1, 0), +1)
    out["gate_benchmark"] = {
        "reversal_signs_on_000_011_101_110": [plus_minus[w] for w in ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0))],
        "signed_with_X": match_target(table(plus_minus, single_readers(3))),
        "positive_with_Y": match_target(y_benchmark()),
        "mutant_s_plus_one_with_X": match_target(table(mutant, single_readers(3))),
    }
    timing["gate_benchmark_s"] = round(time.perf_counter() - t0, 3)
    out["P1_reversal_lemma"] = [reversal_lemma(n) for n in range(3, 9)]
    timing["P1_s"] = round(time.perf_counter() - t0, 3)
    out["P2_knot_census"] = [knot_census(n) for n in (3, 4, 5, 6)]
    out["P2_knot_census_control_s_plus_one"] = [knot_census(n, +1)["orders_with_full_contradiction"] for n in (3, 4)]
    timing["P2_s"] = round(time.perf_counter() - t0, 3)
    g, advance = load_growth()
    sources = {
        "single_ternary": ((0, 1, 2),),
        "doubled_pair": ((0, 1, 2), (0, 1, 3)),
        "exact_three_ternary_cycle": ((0, 2, 3), (0, 1, 4), (1, 2, 5)),
        **{f"four_place_cycle_{n}": g["cycles"](n, 2) for n in (3, 5, 7)},
    }
    fixtures = {name: fixture(g, advance, src) for name, src in sources.items()}
    out["P3_growth_fixtures"] = {name: growth_fixture_census(fx, rng) for name, fx in fixtures.items()}
    out["P3_growth_fixtures_control_s_plus_one"] = {
        name: growth_fixture_census(fx, random.Random(SEED), s=+1)["R2_surviving_words_equal_weight"]
        for name, fx in fixtures.items() if name in ("single_ternary", "four_place_cycle_3")}
    timing["P3_fixtures_s"] = round(time.perf_counter() - t0, 3)
    ternary = fixtures["single_ternary"]
    refs = list(permutations(range(3)))
    exp = ternary_experiment(ternary, reference_orders=refs)
    prod = exp["reference_abc"]
    out["P3_ternary_experiment_reference_production"] = strip(prod)
    out["P3_ternary_reference_variation"] = {
        ref: {"orders_with_full_contradiction": sum(r["full_contradiction"] for r in rows.values()),
              "these_are_the_orders_odd_relative_to_the_reference": all(
                  r["full_contradiction"] == r["relative_order_odd"] for r in rows.values())}
        for ref, rows in exp.items()}
    control = ternary_experiment(ternary, s=+1)["reference_abc"]
    out["P3_ternary_control_s_plus_one"] = {k: {"full_contradiction": v["full_contradiction"],
                                                "win_rate": v["win_rate_on_scored_settings"]}
                                            for k, v in control.items()}
    out["P4_order_blind"] = {
        "odd_orders": order_blind(prod, lambda r: r["relative_order_odd"]),
        "all_orders": order_blind(prod, lambda r: True),
    }
    out["P5_coherent_sum"] = {name: {k: v for k, v in r.items() if k.startswith("R2")}
                              for name, r in out["P3_growth_fixtures"].items()}
    # R3: readers' records listed by the same rule in the same round, so the reference is the history's own listing.
    words = span(ternary["basis"], ternary["names"])
    child_of = {inh[0]: fresh for inh, fresh in ternary["births"]}
    block = [(j, (j, child_of[j][0])) for j in range(3)]
    r3 = {}
    for order in permutations(range(3)):
        own = listing_for(ternary, order)
        state = {w: sign_of(swap_count(w, own, own), -1) for w in words}
        r3["".join("abc"[i] for i in order)] = contradiction(state, block)
    out["P6_same_round_readers"] = r3
    out["P7_rule_applied_to_readings"] = ternary_jw(ternary)
    timing["total_s"] = round(time.perf_counter() - t0, 3)
    out["timing_seconds"] = timing
    return out


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="verify the saved exact receipt")
    args = parser.parse_args()
    data = results()
    timing = data.pop("timing_seconds")
    content = json.dumps(data, indent=2, sort_keys=True, default=str) + "\n"
    path = HERE / "results.json"
    if args.check:
        if path.read_text(encoding="utf-8") != content:
            raise SystemExit("results.json differs from the replay")
        print("results.json reproduced")
    else:
        path.write_text(content, encoding="utf-8")
        print(json.dumps(timing))


if __name__ == "__main__":
    main()
