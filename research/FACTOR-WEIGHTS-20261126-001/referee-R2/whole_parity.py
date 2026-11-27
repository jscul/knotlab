"""Check which supports carry the uniform counting in the fixed parity sample.

The only imported study code builds the recorded growth from its census start.
All support tests, including comparisons with unlisted scopes, are rebuilt here.
Run from the repository root. The search prints to stdout.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
import os
from pathlib import Path
import random
import subprocess
import sys
import time


ROOT = Path(__file__).resolve().parents[3]
GROWTH = ROOT / "research/FORBID-EDITS-20261126-001"
sys.path.insert(0, str(GROWTH))
import forbid


def mask(places):
    return sum(1 << place for place in places)


def members(bits):
    return [place for place in range(bits.bit_length()) if bits & (1 << place)]


def span(equations):
    values = {0}
    for row in equations:
        if row not in values:
            values.update({row ^ old for old in values})
    return values


def dimension(space):
    return len(space).bit_length() - 1


def qualifying_supports(dual):
    # A projected even relation is constrained iff its scope contains a
    # nonzero dual word. K2 therefore requires an inclusion-minimal support.
    minimal = []
    for candidate in sorted(dual - {0}, key=lambda x: (x.bit_count(), x)):
        if not any(x & candidate == x for x in minimal):
            minimal.append(candidate)
    return [x for x in minimal if x.bit_count() >= 3]


def grow(census, index, arm, rounds=2, law="parity", width_cap=None):
    start = forbid.supports_of(census[index])
    stages = [start]
    for _ in range(rounds):
        if width_cap is not None and len(set().union(*map(set, stages[-1]))) > width_cap:
            break
        new, status, _ = forbid.grown(stages[-1], law, arm)
        if status != "funded":
            break
        stages.append(new)
    return stages


def shape(stages):
    return [len(stage) for stage in stages]


def counting_certificate(stages, law, names):
    """Rebuild TD §3 from each whole stage, with zero-weight losses retained."""
    by_name = {name: index for index, name in enumerate(names)}
    weights = {}
    stages_report = []
    previous_names = set()
    for stage in stages:
        active = sorted({d for row in stage for d in row})
        rules = [mask(by_name[d] for d in row) for row in stage]
        active_mask = mask(by_name[d] for d in active)
        words = []
        w = active_mask
        while True:
            if (all((w & s).bit_count() % 2 == 0 for s in rules) if law == "parity" else
                    all(0 < (w & s).bit_count() < s.bit_count() for s in rules)):
                words.append(w)
            if not w:
                break
            w = (w - 1) & active_mask
        if not stages_report:
            weights = {w: Fraction(1, len(words)) for w in words}
            stages_report.append({"allowed_states": len(words)})
        else:
            kept = mask(by_name[d] for d in previous_names)
            counts = Counter(w & kept for w in words)
            multiplicities = Counter(counts[w] for w in weights)
            weights = {w: weights[w & kept] / counts[w & kept] for w in words}
            stages_report.append({"allowed_states": len(words),
                "old_state_counts_by_number_of_completions": dict(sorted(multiplicities.items()))})
        previous_names = set(active)
    total = sum(weights.values())
    return {"stages": stages_report, "total_before_renormalizing": str(total),
            "weights_per_state_after_renormalizing": dict(sorted(Counter(str(v / total) for v in weights.values()).items())),
            "start_counting_is_uniform_after_renormalizing": len(set(weights.values())) == 1}


def screen(census, indices, rounds=2, cap=14, prefixes=False):
    counts = Counter()
    witnesses = {}
    for index in indices:
        for arm in forbid.ARMS:
            stages = grow(census, index, arm, rounds, width_cap=cap)
            for r in range(1, len(stages)) if prefixes else [len(stages) - 1]:
                final = stages[r]
                width = len({p for row in final for p in row})
                if r == 0 or width > cap:
                    continue
                counts[(arm, "kept")] += 1
                raw = {mask(row) for row in final}
                dual = span(raw)
                all_pass = set(qualifying_supports(dual))
                verified = raw & all_pass
                all_space = span(all_pass)
                verified_space = span(verified)
                unary = {x for x in dual if x.bit_count() == 1}
                binary = {x for x in dual if x.bit_count() == 2}
                with_unary = span(all_pass | unary)
                with_binary = span(all_pass | binary)
                assert span(all_pass | unary | binary) == dual
                start_rows = {mask(row) for row in stages[0]}
                start_all_pass = start_rows <= set(qualifying_supports(span(start_rows)))
                conditions = {
                    "listed": verified_space != dual, "all": all_space != dual,
                    "all_plus_unary_equations": with_unary != dual,
                    "all_plus_two_variable_parity_equations": with_binary != dual,
                    "all_with_open_distinctions": not unary and all_space != dual,
                    "all_with_open_distinctions_and_all_raw_arity_three_or_more":
                        not unary and min(len(row) for row in final) >= 3 and all_space != dual,
                    "all_with_start_verified": start_all_pass and all_space != dual,
                    "all_with_open_distinctions_and_start_verified":
                        not unary and start_all_pass and all_space != dual,
                }
                for label, failed in conditions.items():
                    if not failed:
                        continue
                    counts[(arm, label + " fails")] += 1
                    ranks = [dimension(dual), dimension(verified_space), dimension(all_space)]
                    case = (width, r, len(final), index, arm, ranks)
                    if label not in witnesses or case < witnesses[label]:
                        witnesses[label] = case
    return {"counts": {f"{arm}, {label}": n for (arm, label), n in sorted(counts.items())},
            "smallest_by_distinctions_rounds_rules_index_arm": witnesses}


def complement_rows(scope):
    places = members(scope)
    for values in product((0, 1), repeat=len(places)):
        if sum(values) % 2:
            yield " ".join(("-" if bit else "") + f"d{p}" for p, bit in zip(places, values))


def canonical_test(raw, names, scope):
    places = members(scope)
    clauses = "; ".join(clause for row in raw for clause in complement_rows(row))
    args = [str(ROOT / ".venv/bin/python"), "-B", "-m", "knotlab", "check",
            "--cnf", clauses, "--loops", *[f"d{x}" for x in places[:-1]],
            "--contact", f"d{places[-1]}", "--witnesses",
            *[f"d{x}" for x in names if x not in places], "--json"]
    env = dict(os.environ, PYTHONPATH=str(ROOT / "tools"))
    report = json.loads(subprocess.check_output(args, env=env, cwd=ROOT))
    return {"arguments": args[1:], **{k: report[k] for k in ("binding", "loss_on_erasure", "coexistence", "is_knot", "allowed")}}


def certificate(census, index, arm, rounds, canonical):
    stages = grow(census, index, arm, rounds)
    raw = [mask(row) for row in stages[-1]]
    names = sorted(set().union(*(set(row) for row in stages[-1])))
    full = [mask(name for bit, name in zip(bits, names) if bit) for bits in product((0, 1), repeat=len(names))]
    states = set(w for w in full if all((w & row).bit_count() % 2 == 0 for row in raw))
    assert states
    # Independently enumerate every distinct scope, all induced projections,
    # canonical minimum arity and all one-distinction erasures. Full scopes
    # need no examination of their proper parts.
    nonfull = set()
    knots = []
    for size in range(1, len(names) + 1):
        for subset in combinations(names, size):
            scope = mask(subset)
            if any((scope ^ (1 << d)) in nonfull for d in subset):
                nonfull.add(scope)
                continue
            if len({w & scope for w in states}) != 1 << size:
                nonfull.add(scope)
                if size >= 3:
                    knots.append(scope)
    assert set(knots) == set(qualifying_supports(span(raw)))
    listed = [scope for scope in raw if scope in knots]
    result = {"census_index_zero_based": index, "arm": arm, "law": "even parity",
              "rounds": len(stages) - 1, "listed_rule_counts_in_order": shape(stages),
              "distinctions_in_order": names, "listed_rules_in_birth_order": [members(s) for s in raw],
              "allowed_states": len(states), "scopes_checked_including_unlisted": (1 << len(names)) - 1,
              "listed_knots": [members(s) for s in listed], "all_knots": [members(s) for s in knots],
              "counting_from_start": counting_certificate(stages, "parity", names)}
    dual = span(raw)
    start_raw = {mask(row) for row in stages[0]}
    result.update(all_start_rules_pass=start_raw <= set(qualifying_supports(span(start_raw))),
                  fixed_distinctions=[members(s)[0] for s in sorted(dual) if s.bit_count() == 1],
                  two_variable_parity_equations=[members(s) for s in sorted(dual) if s.bit_count() == 2])
    if canonical:
        failing = next(s for s in raw if s not in knots and s.bit_count() >= 3)
        result["canonical_failing_listed_scope"] = members(failing)
        result["canonical_result"] = canonical_test(raw, names, failing)
        assert not result["canonical_result"]["is_knot"]
    for label, scopes in (("raw_rules", raw), ("listed_knots", listed), ("all_knots", knots)):
        projections = {s: {w & s for w in states} for s in scopes}
        accepted = [w for w in full if all(w & s in projections[s] for s in scopes)]
        false = [w for w in accepted if w not in states]
        def word(w):
            return "".join(str((w >> n) & 1) for n in names)
        example = min(false, key=word) if false else None
        result[label + "_product"] = {
            "states_in_join_of_projections": len(accepted), "forbidden_in_join": len(false),
            "forbidden_example": None if example is None else word(example),
            "allowed_extensions_of_its_local_patterns": None if example is None else
            [word(min((w for w in states if w & s == example & s), key=word)) for s in scopes],
        }
        joins = {(a, b) for s in scopes for a, b in combinations(members(s), 2)}
        failures = []
        for a, b in combinations(names, 2):
            if (a, b) in joins:
                continue
            rest_mask = mask(n for n in names if n not in (a, b))
            for rest in sorted({w & rest_mask for w in states}):
                table = [[int((rest | (u << a) | (v << b)) in states) for v in (0, 1)] for u in (0, 1)]
                if table[0][0] * table[1][1] != table[0][1] * table[1][0]:
                    failures.append(([a, b], word(rest), table))
        result[label + "_product"].update(pair_table_failures=len(failures), first_pair_failure=next(iter(failures), None))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--count", type=int, default=300)
    parser.add_argument("--census", action="store_true", help="take an ordered prefix of the entire census")
    parser.add_argument("--prefixes", action="store_true", help="also test intermediate funded rounds")
    parser.add_argument("--cap", type=int, default=14)
    parser.add_argument("--rounds", type=int, default=2)
    parser.add_argument("--case", type=int)
    parser.add_argument("--arm", choices=forbid.ARMS, default="ordinary")
    parser.add_argument("--canonical", action="store_true")
    args = parser.parse_args()
    census = json.loads((GROWTH / "starts.json").read_text())
    before = time.monotonic()
    if args.case is None:
        indices = (range(len(census)) if args.census else random.Random(20261129).sample(range(len(census)), 300))[:args.count]
        result = screen(census, indices, args.rounds, args.cap, args.prefixes)
        result.update(draws=len(indices), census_size=len(census), seed=None if args.census else 20261129,
                      rounds_cap=args.rounds, distinctions_cap=args.cap, includes_funded_prefixes=args.prefixes)
    else:
        result = certificate(census, args.case, args.arm, args.rounds, args.canonical)
    result["elapsed_seconds_excluding_import_and_census_load"] = round(time.monotonic() - before, 6)
    print(json.dumps(result, indent=2))
