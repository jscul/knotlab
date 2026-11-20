"""Exact whole-state enumeration for the preregistered two-register control.

Run from the checkout with .venv/bin/python -B path/to/embodied_control.py.
The output is written beside this file. No settings are supplied to the laws.
"""
from collections import Counter, deque
from fractions import Fraction
from functools import lru_cache
from itertools import combinations, product
from math import lcm
from pathlib import Path
import json
import os
import subprocess
import sys

import numpy as np


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
for family in (
    "NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae",
    "ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary",
):
    sys.path.insert(0, str(ROOT / "experiments" / family))

import end_operator
import naelib


REGISTER = ("X", "A0", "A1", "P", "Y", "B0", "B1")
SETTING_PAIRS = tuple(product(range(2), repeat=2))
REGISTER_WORDS = tuple(product(range(2), repeat=7))


def construction():
    names = list(REGISTER)
    knots = [list(range(4)), [4, 5, 6]]
    for prefix, initial, final in (("c", 1, 6), ("d", 2, 5)):
        rows = [[initial], [final], [], []]
        for i, j in combinations(range(4), 2):
            if (i, j) == (0, 1):
                continue
            distinction = len(names)
            names.append(f"{prefix}{i}{j}")
            rows[i].append(distinction)
            rows[j].append(distinction)
        knots.extend(rows)
    return names, knots


def first_round(start, law):
    compact = end_operator.step(end_operator.from_stars(start), law=law)
    source = naelib.S.from_junctions(start)
    rule = naelib.nae_rule if law == "nae" else naelib.parity_rule
    receipt = source.step(rule(naelib.F.fewest), cap=None)
    if receipt is None or not receipt["new"] or compact.status != "extend":
        raise AssertionError((law, receipt, compact))
    parents = [tuple(j for j, support in enumerate(start) if set(support) & set(new))
               for new in source.bits_of[len(start):]]
    assert tuple(parents) == compact.parents
    assert tuple(source.fresh[len(start):]) == compact.fresh
    assert tuple(source.demand_at_birth[len(start):]) == compact.demand
    return source.bits_of, dict(parents=parents, fresh=compact.fresh, demand=compact.demand,
                                new_knots=receipt["new"], status=compact.status)


def enumerate_states(knots, law):
    """Test every assignment against all displayed supports using integer Boolean operations."""
    masks = [sum(1 << bit for bit in support) for support in knots]
    n = max(max(support) for support in knots) + 1
    accepted = []
    for offset in range(0, 1 << n, 1 << 17):
        candidates = np.arange(offset, min(offset + (1 << 17), 1 << n), dtype=np.uint32)
        for mask in masks:
            masked = candidates & mask
            if law == "parity":
                keep = (np.bitwise_count(masked) & 1) == 0
            else:
                keep = (masked != 0) & (masked != mask)
            candidates = candidates[keep]
        accepted.append(candidates)
    return np.concatenate(accepted)


def codes(states, subset):
    answer = np.zeros(len(states), dtype=np.uint32)
    for bit in subset:
        answer = (answer << 1) | ((states >> bit) & 1)
    return answer


@lru_cache(maxsize=None)
def canonical_gate(arity, allowed):
    names = [f"q{i}" for i in range(arity)]
    clauses = []
    for word in range(1 << arity):
        if word not in allowed:
            bits = f"{word:0{arity}b}"
            clauses.append(" ".join(("~" if b == "1" else "") + n for b, n in zip(bits, names)))
    cnf = ";".join(clauses) if clauses else "q0 ~q0"
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
            "--loops", *names[:-1], "--contact", names[-1], "--json"]
    report = json.loads(subprocess.check_output(args, env=env, cwd=ROOT, text=True))
    assert set(report["allowed"]) == {f"{word:0{arity}b}" for word in allowed}
    return {key: report[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot")}


def quality_checks(knots, states, law):
    projections = []
    adjacency = {}
    for support in knots:
        for b in support:
            adjacency.setdefault(b, set()).update(set(support) - {b})
        words = tuple(map(int, np.unique(codes(states, support))))
        n = len(support)
        expected = [w for w in range(1 << n)
                    if (w.bit_count() % 2 == 0 if law == "parity" else 0 < w < (1 << n) - 1)]
        projections.append(dict(support=support, allowed_words=list(words),
                                full_stated_law=list(words) == expected, **canonical_gate(n, words)))
    separation = {}
    for a in (0, 1, 2):
        dist = {a: 0}
        todo = deque([a])
        while todo:
            current = todo.popleft()
            for neighbor in adjacency[current] - dist.keys():
                dist[neighbor] = dist[current] + 1
                todo.append(neighbor)
        for b in (4, 5, 6):
            separation[f"{REGISTER[a]},{REGISTER[b]}"] = dist.get(b)
    count_holders = Counter(v for s in knots for v in s)
    return dict(displayed_projections=projections, eligible=all(
        p["is_knot"] and p["full_stated_law"] for p in projections),
        max_holders=max(count_holders.values()),
        max_intersection=max(len(set(a) & set(b)) for a, b in combinations(knots, 2)),
        six_mark_steps=separation, minimum_six_mark_steps=min(separation.values()),
        minimum_four_mark_steps=min(separation[f"{a},{b}"] for a in ("A0", "A1") for b in ("B0", "B1")),
        eligible_at_two=min(separation.values()) >= 2, eligible_at_three=min(separation.values()) >= 3)


def bit_reading(pair, setting, protocol):
    if protocol == "I":
        return pair[setting]
    return int(pair == (setting, setting))


def tv(left, right):
    a, b = sum(left), sum(right)
    if not a or not b:
        return None
    return str(Fraction(sum(abs(x * b - y * a) for x, y in zip(left, right)), 2 * a * b))


def packed(bits):
    index = 0
    for bit in bits:
        index = 2 * index + bit
    return index


def compare_settings(register_counts, protocol, arm):
    cells = {}
    common_lambda = [0] * 16
    common_responses = [0] * 16
    common_six_marks = [0] * 64
    for (x, y) in SETTING_PAIRS:
        cell = dict(outputs=[0]*4, marked_pairs=[0]*16, possible_responses=[0]*16, six_marks=[0]*64,
                    alice={"selected":[0]*2, "marked_pair":[0]*4, "whole_bond":[0]*16},
                    bob={"selected":[0]*2, "marked_pair":[0]*4, "whole_bond":[0]*8})
        for word, count in zip(REGISTER_WORDS, register_counts):
            ax, a0, a1, pad, by, b0, b1 = word
            a_pair, b_pair = (a0, a1), (b0, b1)
            a = bit_reading(a_pair, x, protocol)
            b = bit_reading(b_pair, y, protocol)
            responses = tuple(bit_reading(pair, s, protocol) for pair in (a_pair, b_pair) for s in (0, 1))
            m = packed(a_pair + b_pair)
            q = packed(responses)
            z = packed((ax, *a_pair, by, *b_pair))
            if (x, y) == (0, 0):
                common_lambda[m] += count
                common_responses[q] += count
                common_six_marks[z] += count
            if arm == "endogenous" and (ax, by) != (x, y):
                continue
            cell["outputs"][2*a+b] += count
            cell["marked_pairs"][m] += count
            cell["possible_responses"][q] += count
            cell["six_marks"][z] += count
            for side, val, pair, bond in (("alice", a, a_pair, (ax,a0,a1,pad)),
                                          ("bob", b, b_pair, (by,b0,b1))):
                cell[side]["selected"][val] += count
                cell[side]["marked_pair"][packed(pair)] += count
                cell[side]["whole_bond"][packed(bond)] += count
        cells[x, y] = cell
    diagnostics = {}
    for side in ("alice", "bob"):
        diagnostics[side] = {}
        for domain in ("selected", "marked_pair", "whole_bond"):
            fixed = [((s, 0), (s, 1)) if side == "alice" else ((0, s), (1, s)) for s in (0, 1)]
            diagnostics[side][domain] = [tv(cells[c][side][domain],cells[d][side][domain]) for c,d in fixed]
    outputs = [c["outputs"] for c in cells.values()]
    totals = list(map(sum, outputs))
    correlations = [Fraction(a-b-c+d, total) if total else None
                    for (a,b,c,d), total in zip(outputs, totals)]
    signed = maximum = None
    if all(totals):
        signed = str(correlations[0] + correlations[1] + correlations[2] - correlations[3])
        maximum = str(max(sum(s*t for s,t in zip(signs, correlations))
                          for signs in product((-1,1), repeat=4) if signs.count(-1) % 2 == 1))
    return dict(output_counts=outputs, context_masses=totals,
                correlations=[str(e) if e is not None else None for e in correlations],
                signed_S=signed, max_CHSH=maximum, marginal_TV_fixed_own=diagnostics,
                marked_pair_histograms=[c["marked_pairs"] for c in cells.values()],
                TV_four_marks_from_common=[tv(c["marked_pairs"],common_lambda) for c in cells.values()],
                TV_four_potential_outputs_from_common=[tv(c["possible_responses"],common_responses)
                                                       for c in cells.values()],
                TV_six_marks_from_common=[tv(c["six_marks"],common_six_marks) for c in cells.values()])


def stage_result(knots, states, start_states, n_start, law):
    old = states & ((1 << n_start) - 1)
    counts = np.bincount(old, minlength=1 << n_start)
    retained = np.array_equal(np.flatnonzero(counts), start_states)
    assert retained
    multiplicities, frequencies = np.unique(counts[start_states], return_counts=True)
    by_count = {int(n): int(k) for n,k in zip(multiplicities, frequencies)}
    common_den = lcm(*by_count.keys())
    word_indices = codes(states, range(len(REGISTER)))
    weights = {}
    unit = np.ones(len(states), dtype=np.int64)
    for name, mass, denominator in (("U", unit, 1), ("L", common_den // counts[old], common_den),
                                    ("T", unit + ((states >> 1) & 1), 1)):
        table = np.zeros(len(REGISTER_WORDS), dtype=np.int64)
        np.add.at(table, word_indices, mass)
        raw = table.tolist()
        readings = {p: {arm: compare_settings(raw, p, arm) for arm in ("external", "endogenous")}
                    for p in ("I", "II")}
        weights[name] = dict(assignment_mass_divisor=denominator, total_mass_numerator=sum(raw),
                             register_counts=raw, readings=readings)
    return dict(distinctions=max(max(k) for k in knots)+1, knots=len(knots), complete_states=len(states),
                extensions_by_multiplicity=by_count, start_projection_exact=bool(retained),
                **quality_checks(knots, states, law), weights=weights)


def main():
    names, start = construction()
    result = dict(register_order=REGISTER, context_order=["00","01","10","11"],
                  output_order=["00","01","10","11"], names=names, start_supports=start,
                  gate_method="Global complete-state projection, CNF excluding its missing words, knotlab check (forgetting).",
                  fresh_labels="Distinctions 17 and above follow the ordinary stable assignment.",
                  weight_units="Raw weights divided by assignment_mass_divisor; normalize within each context for probabilities.",
                  stages={}, growth={})
    for law in ("parity", "nae"):
        grown, receipt = first_round(start, law)
        result["growth"][law] = dict(supports=grown[len(start):], **receipt)
        start_states = enumerate_states(start, law)
        result["stages"][law] = {}
        for stage, knots, states in ((0,start,start_states), (1,grown,enumerate_states(grown,law))):
            result["stages"][law][str(stage)] = stage_result(knots, states, start_states, len(names), law)
    target = HERE / "embodied_control.json"
    target.write_text(json.dumps(result, separators=(",",":"), sort_keys=True) + "\n")


if __name__ == "__main__":
    main()
