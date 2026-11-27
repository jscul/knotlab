"""Audit the one-founder transfer support and the scopes of its factors.

The reached states follow from the original unary transfer rule, with two
fresh distinctions per birth. No producer census or reader-split routine is
imported. All weighted comparisons use exact fractions.
"""

import argparse
from collections import Counter
from fractions import Fraction
from itertools import combinations, product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys


ROOT = Path(__file__).resolve().parents[3]
DISTINCTIONS = tuple(range(9))
FOUNDER = (0, 1, 2)
SIBLINGS = ((3, 4), (5, 6), (7, 8))
LISTED = (FOUNDER, *((i, *pair) for i, pair in enumerate(SIBLINGS)))
PREREGISTERED = tuple(sorted((j, *pair) for i, pair in enumerate(SIBLINGS)
                             for j in FOUNDER if j != i))
WORDS = tuple(product((0, 1), repeat=len(DISTINCTIONS)))


def project(word, scope):
    return tuple(word[d] for d in scope)


def bits(word):
    return "".join(map(str, word))


def in_listed_support(word):
    return all(sum(project(word, scope)) % 2 == 0 for scope in LISTED)


def reached(pair_lift):
    weights = {}
    for old in product((0, 1), repeat=len(FOUNDER)):
        if sum(old) % 2:
            continue
        options = []
        for paid in old:
            if paid:
                options.append(((0, 1), (1, 0)))
            elif pair_lift and any(old):
                options.append(((1, 1),))
            else:
                options.append(((0, 0),))
        lift_count = prod(map(len, options))
        for lift in product(*options):
            word = old + tuple(bit for pair in lift for bit in pair)
            assert word not in weights and in_listed_support(word)
            weights[word] = Fraction(1, 4 * lift_count)
    assert sum(weights.values()) == 1
    return weights


def classify(support):
    projections = {
        scope: {project(word, scope) for word in support}
        for size in range(len(DISTINCTIONS) + 1)
        for scope in combinations(DISTINCTIONS, size)
    }
    counts = Counter()
    knots = []
    for scope, allowed in projections.items():
        if not scope:
            continue
        full = len(allowed) == 2 ** len(scope)
        every_part_free = all(len(projections[rest]) == 2 ** len(rest)
                              for rest in combinations(scope, len(scope) - 1))
        counts[len(scope), "scopes checked"] += 1
        counts[len(scope), "full"] += full
        if allowed and not full and every_part_free:
            label = "knots" if len(scope) >= 3 else "constraints below three places"
            counts[len(scope), label] += 1
            if len(scope) >= 3:
                knots.append(scope)
    by_size = {
        size: {label: counts[size, label] for label in (
            "scopes checked", "full", "knots", "constraints below three places")}
        for size in range(1, len(DISTINCTIONS) + 1)
    }
    return projections, knots, by_size


def splits():
    for size in (1, 2):
        for unread in combinations(DISTINCTIONS, size):
            read = tuple(d for d in DISTINCTIONS if d not in unread)
            for left_size in range(1, len(read)):
                for left in combinations(read, left_size):
                    right = tuple(d for d in read if d not in left)
                    if left >= right:
                        continue
                    if not any(crosses(scope, left, right) for scope in LISTED):
                        yield left, right, unread


def crosses(scope, left, right):
    return bool(set(scope) & set(left) and set(scope) & set(right))


def conditional_dependence(weights, left, right, unread):
    conditioned = {}
    for word, mass in weights.items():
        c = project(word, unread)
        table = conditioned.setdefault(c, Counter())
        table[project(word, left), project(word, right)] += mass

    missing, unequal = None, None
    for c, table in sorted(conditioned.items()):
        row_sums, column_sums = Counter(), Counter()
        for (a, b), mass in table.items():
            row_sums[a] += mass
            column_sums[b] += mass
        total = sum(table.values())
        for a, b in product(sorted(row_sums), sorted(column_sums)):
            joint = table[a, b]
            expected = row_sums[a] * column_sums[b] / total ** 2
            if not joint and missing is None:
                missing = [bits(p) for p in (c, a, b)]
            if joint / total != expected and unequal is None:
                unequal = {
                    "unread left right patterns": [bits(p) for p in (c, a, b)],
                    "conditional joint weight": str(joint / total),
                    "product of conditional marginal weights": str(expected),
                }
    return {"missing conditional product pattern": missing, "conditional weight failure": unequal}


def canonical_check(scope, allowed):
    names = tuple(f"d{d}" for d in scope)
    excluded = sorted(set(product((0, 1), repeat=len(scope))) - allowed)
    # Each clause excludes its own joint state, so the CNF has the same support.
    clauses = [" ".join(("~" if bit else "") + name for bit, name in zip(word, names))
               for word in excluded]
    cnf = ";".join(clauses)
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", cnf,
               "--loops", *names[:-1], "--contact", names[-1], "--json"]
    result = subprocess.run(command, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")},
                            check=True, capture_output=True, text=True)
    report = json.loads(result.stdout)
    return {"scope": scope, "cnf": cnf, "contact place": scope[-1],
            **{key: report[key] for key in ("binding", "loss_on_erasure", "coexistence", "is_knot")}}


def factor_replay(scopes, projections, weights, scale, weighted_places=()):
    for word in WORDS:
        mass = scale
        for scope in scopes:
            local = project(word, scope)
            if local not in projections[scope]:
                mass = Fraction(0)
                break
            if scope in weighted_places:
                mass /= 2 ** local[0]
        assert mass == weights.get(word, 0), (scopes, word, mass)


def join_local_patterns(scopes, projections):
    return {word for word in WORDS if all(project(word, scope) in projections[scope] for scope in scopes)}


def local_witnesses(forbidden, support, scopes):
    witnesses = []
    for scope in scopes:
        local = project(forbidden, scope)
        witness = min(word for word in support if project(word, scope) == local)
        witnesses.append({"scope": scope, "local pattern": bits(local), "reached completion": bits(witness)})
    return witnesses


def certificates(classifications, weights):
    pair, minimum, finish = (classifications[key][0] for key in ("pair", "minimum", "finish"))
    pair_start, minimum_start, finish_once = (weights[key] for key in ("pair start", "minimum start", "finish"))
    pair_listed_join = join_local_patterns(LISTED, pair)
    pair_forbidden = tuple(int(d in {0, 1, 3, 5}) for d in DISTINCTIONS)
    assert pair_listed_join == set(finish_once) and pair_forbidden in pair_listed_join - pair_start.keys()
    minimum_knots = classifications["minimum"][1]
    minimum_knot_join = join_local_patterns(minimum_knots, minimum)
    minimum_forbidden = min(minimum_knot_join - minimum_start.keys())
    for scope in PREREGISTERED:
        assert set(map(bits, pair[scope])) == {"000", "001", "010", "101", "110", "111"}

    selected = [tuple((j, *siblings) for j, siblings in zip(js, SIBLINGS))
                for js in product(*(tuple(j for j in FOUNDER if j != i) for i in FOUNDER))]
    for inducing in [*selected, PREREGISTERED]:
        scopes = LISTED + inducing
        factor_replay(scopes, pair, pair_start, Fraction(1, 4), LISTED[1:])
        factor_replay(scopes, pair, weights["pair every reached state once"], Fraction(1, 13))
    factor_replay(LISTED, minimum, minimum_start, Fraction(1, 4), LISTED[1:])
    factor_replay(LISTED, minimum, weights["minimum every reached state once"], Fraction(1, 13))
    factor_replay(LISTED, finish, finish_once, Fraction(1, 32))

    return {
        "all-word comparisons per factorization": len(WORDS),
        "pair local support over four listed scopes alone": len(pair_listed_join),
        "unreached word admitted by four listed scopes": bits(pair_forbidden),
        "reached completions witnessing the pair lift's four local patterns": local_witnesses(
            pair_forbidden, pair_start, LISTED),
        "pair factors": {
            "listed scopes": LISTED,
            "equivalent selections of additional scopes": selected,
            "scope indicator rule": "Require even parity on all listed scopes. For each child, choose either other "
                                    "founder distinction and exclude 011 and 100 on it followed by the fresh pair.",
            "support reason": "Odd paid input forces a mixed pair. For even paid input the other two founder values "
                              "agree, and the additional scope forces each fresh value to equal that common value.",
            "start weighting": "Multiply by 1/4 and by 1/2 on each child scope whose old input is 1.",
            "every reached state once": "Multiply by 1/13."
        },
        "minimum factors": {
            "scope indicator rule": "Require even parity on the founder. On each listed child scope its reached "
                                    "patterns are 000, 101, and 110 in old-input-first order.",
            "weighting rule": "Use the same start factors or the same factor for every reached state once as above.",
            "support over all whole-support knots": len(minimum_knot_join),
            "unreached word admitted by all whole-support knots": bits(minimum_forbidden),
            "reached completions witnessing every local knot pattern": local_witnesses(
                minimum_forbidden, minimum_start, minimum_knots),
        },
        "record finish factors": "Require even parity on the four listed scopes and multiply by 1/32."
    }


def run(pilot):
    pair_start, minimum_start = reached(True), reached(False)
    finish_support = {word for word in WORDS if in_listed_support(word)}
    weights = {
        "pair start": pair_start,
        "pair every reached state once": dict.fromkeys(pair_start, Fraction(1, len(pair_start))),
        "minimum start": minimum_start,
        "minimum every reached state once": dict.fromkeys(minimum_start, Fraction(1, len(minimum_start))),
        "finish": dict.fromkeys(finish_support, Fraction(1, len(finish_support))),
    }
    source_weights = {"pair": pair_start, "minimum": minimum_start, "finish": weights["finish"]}
    classifications = {mode: classify(dist) for mode, dist in source_weights.items()}
    _, pair_knots, _ = classifications["pair"]
    assert set(LISTED + PREREGISTERED) <= set(pair_knots)

    canonical = {
        mode: [canonical_check(scope, local[scope]) for scope in (knots[:1] if pilot else knots)]
        for mode, (local, knots, _) in classifications.items()
    }
    assert all(check["is_knot"] for checks in canonical.values() for check in checks)
    minimum_projection = classifications["minimum"][0]
    minimum_controls = [canonical_check(scope, minimum_projection[scope])
                        for scope in (LISTED[1:2] if pilot else LISTED[1:])]
    assert all(check["binding"] and not check["loss_on_erasure"] for check in minimum_controls)

    rows = []
    for left, right, unread in splits():
        joins = {mode: [s for s in knots if crosses(s, left, right)]
                 for mode, (_, knots, _) in classifications.items()}
        preregistered = [s for s in joins["pair"] if s in PREREGISTERED]
        assert preregistered
        rows.append({"left": left, "right": right, "unread": unread, "crossing knots": joins,
                     "preregistered crossing knots": preregistered,
                     "conditioning checks": {name: conditional_dependence(dist, left, right, unread)
                                             for name, dist in weights.items()}})

    scope_details = {
        mode: [{"scope": scope, "allowed": sorted(map(bits, local[scope]))} for scope in knots]
        for mode, (local, knots, _) in classifications.items()
    }
    control_pair = SIBLINGS[0]
    marginal = [sum(weight for word, weight in minimum_start.items() if word[d]) for d in control_pair]
    both = sum(weight for word, weight in minimum_start.items() if all(word[d] for d in control_pair))
    containing_pair = [scope for scope in classifications["minimum"][1] if set(control_pair) <= set(scope)]
    assert len(minimum_projection[control_pair]) == 3 and not containing_pair and both != prod(marginal)
    counts = {
        "tested splits": len(rows),
        "crossed by a knot": {mode: sum(bool(row["crossing knots"][mode]) for row in rows)
                              for mode in classifications},
        "crossed by one of the six preregistered scopes": sum(bool(row["preregistered crossing knots"]) for row in rows),
        "preregistered coverage by scope": [
            {"scope": scope,
             "splits crossed": sum(scope in row["preregistered crossing knots"] for row in rows),
             "splits crossed solely by this preregistered scope": sum(
                 row["preregistered crossing knots"] == [scope] for row in rows)}
            for scope in PREREGISTERED
        ],
        "crossed by a knot disjoint from the unread distinctions": {
            mode: sum(any(set(scope).isdisjoint(row["unread"]) for scope in row["crossing knots"][mode])
                      for row in rows)
            for mode in classifications
        },
        "crossed by a preregistered scope disjoint from the unread distinctions": sum(
            any(set(scope).isdisjoint(row["unread"]) for scope in row["preregistered crossing knots"])
            for row in rows
        ),
        "smallest crossing scope size": {
            mode: dict(Counter(min(map(len, row["crossing knots"][mode]), default=0) for row in rows))
            for mode in classifications
        },
        "conditional support failures": {
            name: sum(bool(row["conditioning checks"][name]["missing conditional product pattern"]) for row in rows)
            for name in weights
        },
        "conditional weight failures": {
            name: sum(bool(row["conditioning checks"][name]["conditional weight failure"]) for row in rows)
            for name in weights
        },
    }
    return {
        "distinction order": DISTINCTIONS,
        "founder and its three listed child scopes": LISTED,
        "unread sizes": [1, 2],
        "source support counts": {mode: len(dist) for mode, dist in source_weights.items()},
        "pair and minimum reached assignments with start weights": {
            mode: {bits(w): str(p) for w, p in sorted(dist.items())}
            for mode, dist in source_weights.items() if mode != "finish"
        },
        "scope counts by size": {mode: result[2] for mode, result in classifications.items()},
        "knots by support": scope_details,
        "positive scopes checked canonically": canonical,
        "minimum listed children checked canonically": minimum_controls,
        "factors": certificates(classifications, weights),
        "split counts": counts,
        "splits": rows,
        "counterexample to correlation implying a knot": {
            "support": "minimum",
            "weighting": "start",
            "distinctions": control_pair,
            "allowed pair states": sorted(map(bits, minimum_projection[control_pair])),
            "individual occupied weights": [str(weight) for weight in marginal],
            "joint occupied weight": str(both),
            "covariance": str(both - prod(marginal)),
            "reason neither distinction can share a knot with the other": "Their constrained pair is a proper part "
                                                                        "of any candidate knot containing both."
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="Time one canonical check per support and one control.")
    args = parser.parse_args()
    result = run(args.pilot)
    if args.pilot:
        print(json.dumps({"scopes passing to canonical confirmation in full run": {
                              mode: len(knots) for mode, knots in result["knots by support"].items()},
                          "split counts": result["split counts"]}, indent=2))
    else:
        print(json.dumps(result, indent=2))
