"""Check the support of uniform not-all-equal finishes by projecting exact truth tables."""

import argparse
from collections import Counter
from itertools import combinations
import json
import os
import random
import subprocess
import sys
import time

from whole_parity import GROWTH, ROOT, counting_certificate, forbid, grow, mask, members


def truth_tables(final, all_scopes):
    names = sorted({d for row in final for d in row})
    index = {d: i for i, d in enumerate(names)}
    n = len(names)
    full_scope = (1 << n) - 1
    universe = (1 << (1 << n)) - 1
    ones = {d: universe // ((1 << (1 << index[d])) + 1) << (1 << index[d]) for d in names}
    raw = [mask(index[d] for d in row) for row in final]
    states = universe
    for row in final:
        all_one, all_zero = universe, universe
        for d in row:
            all_one &= ones[d]
            all_zero &= universe ^ ones[d]
        states &= universe ^ (all_one | all_zero)
    if not states:
        return None
    projections = {full_scope: states}

    def project(scope):
        if scope not in projections:
            missing = full_scope ^ scope
            step = missing & -missing
            parent = project(scope | step)
            if parent == universe:
                projections[scope] = universe
            else:
                one = ones[names[step.bit_length() - 1]]
                paired = ((parent & (universe ^ one)) << step) | ((parent & one) >> step)
                projections[scope] = parent | paired
        return projections[scope]

    def knot(scope):
        return (scope.bit_count() >= 3 and project(scope) != universe and
                all(project(scope ^ (1 << d)) == universe for d in members(scope)))

    def join(scopes):
        out = universe
        for scope in scopes:
            out &= project(scope)
        return out

    listed = {s for s in raw if knot(s)}
    listed_join = join(listed)
    all_knots = sorted(s for s in range(1, full_scope + 1) if knot(s)) if all_scopes or listed_join != states else None
    all_join = join(all_knots) if all_knots is not None else states
    small = [s for s in range(1, full_scope + 1) if s.bit_count() <= 2]
    with_small = all_join & join(small) if all_join != states else states
    assert join(raw) == states
    return dict(names=names, index=index, states=states, raw=raw, listed=listed, listed_join=listed_join,
                all_knots=all_knots, all_join=all_join, with_small=with_small, project=project, universe=universe)


def scan(census, indices, rounds, cap, prefixes):
    counts, smallest = Counter(), {}
    for num in indices:
        for arm in forbid.ARMS:
            stages = grow(census, num, arm, rounds, "nae", cap)
            for r in range(1, len(stages)) if prefixes else [len(stages) - 1]:
                if not r:
                    continue
                final = stages[r]
                width = len({d for row in final for d in row})
                if width > cap:
                    continue
                counts[(arm, "kept")] += 1
                t = truth_tables(final, False)
                if t is None:
                    counts[(arm, "empty")] += 1
                    continue
                counts[(arm, "every raw rule passes")] += t["listed"] == set(t["raw"])
                tests = {label: t[key] != t["states"] for label, key in
                         (("listed", "listed_join"), ("all", "all_join"), ("all_plus_one_and_two_place", "with_small"))}
                if tests["all"]:
                    old = truth_tables(stages[0], False)
                    tests["all_with_start_verified"] = old["listed"] == set(old["raw"])
                for label, failure in tests.items():
                    if failure:
                        counts[(arm, label + " fails")] += 1
                        key = (width, r, len(final), num, arm)
                        if label not in smallest or key < smallest[label]:
                            smallest[label] = key
    return {"counts": {f"{arm}, {label}": n for (arm, label), n in sorted(counts.items())},
            "smallest_by_distinctions_rounds_rules_index_arm": smallest}


def certificate(census, num, arm, rounds, canonical):
    stages = grow(census, num, arm, rounds, "nae")
    t = truth_tables(stages[-1], True)
    names, raw, states = t["names"], t["raw"], t["states"]
    word = lambda x: "".join(str((x >> k) & 1) for k in range(len(names)))
    scope_names = lambda s: [names[k] for k in members(s)]
    whole = range(1 << len(names))
    allowed = [x for x in whole if (states >> x) & 1]
    # Recheck every state directly from the original rules, independently of
    # the bit-parallel truth-table construction.
    assert allowed == [w for w in whole if all(0 < (w & s).bit_count() < s.bit_count() for s in raw)]
    old = truth_tables(stages[0], False)
    result = {"census_index_zero_based": num, "law": "not-all-equal", "arm": arm,
              "rounds": len(stages) - 1, "listed_rule_counts_in_order": [len(s) for s in stages],
              "distinctions_in_order": names, "listed_rules_in_birth_order": [scope_names(s) for s in raw],
              "allowed_states": len(allowed), "all_start_rules_pass": old["listed"] == set(old["raw"]),
              "counting_from_start": counting_certificate(stages, "nae", names),
              "start_rule_tests_in_order": [s in old["listed"] for s in old["raw"]],
              "all_unary_and_binary_projections_full": all(t["project"](s) == t["universe"] for s in range(1, 1 << len(names)) if s.bit_count() <= 2),
              "listed_knots": [scope_names(s) for s in sorted(t["listed"])],
              "all_knots": [scope_names(s) for s in t["all_knots"]],
              "nonempty_scopes_checked": (1 << len(names)) - 1}
    for label, scopes in (("raw_rules", raw), ("listed_knots", t["listed"]), ("all_knots", t["all_knots"])):
        scopes = sorted(set(scopes))
        local = {s: {w & s for w in allowed} for s in scopes}
        accepted = [w for w in whole if all(w & s in local[s] for s in scopes)]
        false = [w for w in accepted if not (states >> w) & 1]
        witness = min(false, key=word) if false else None
        joined = {pair for s in scopes for pair in combinations(members(s), 2)}
        failures, first = 0, None
        for a, b in combinations(range(len(names)), 2):
            if (a, b) in joined:
                continue
            for w in whole:
                if w & ((1 << a) | (1 << b)):
                    continue
                table = [[int((states >> (w | (u << a) | (v << b))) & 1) for v in (0, 1)] for u in (0, 1)]
                if table[0][0] * table[1][1] != table[0][1] * table[1][0]:
                    failures += 1
                    if first is None:
                        first = ([names[a], names[b]], word(w), table)
        result[label + "_product"] = {"states_in_join_of_projections": len(accepted), "forbidden_in_join": len(false),
            "forbidden_example": None if witness is None else word(witness),
            "allowed_extensions_of_its_local_patterns": None if witness is None else
                [[scope_names(s), word(min((w for w in allowed if w & s == witness & s), key=word))] for s in scopes],
            "pair_table_failures": failures, "first_pair_failure": first}
        if label == "all_knots":
            assert len(accepted) == t["all_join"].bit_count()
    if canonical:
        sys.path.insert(0, str(ROOT / "tools"))
        from knotlab.knots import check_knot
        from knotlab.relations import Relation
        stages_checked = []
        for stage in stages:
            stage_names = sorted({d for row in stage for d in row})
            clauses = [" ".join(sign + f"d{d}" for d in row) for row in stage for sign in ("", "-")]
            relation = Relation.from_cnf(clauses, [f"d{d}" for d in stage_names])
            flags = []
            for row in stage:
                shown = [f"d{d}" for d in row]
                if len(shown) < 3:
                    flags.append(False)
                else:
                    flags.append(check_knot(relation.project(shown), shown[:-1], shown[-1]).is_knot)
            stages_checked.append(flags)
        result["canonical_listed_verdicts_for_each_stage"] = stages_checked
        assert stages_checked[0] == result["start_rule_tests_in_order"]
        assert stages_checked[-1] == [s in t["listed"] for s in raw]
        failing = next(s for s in raw if s not in t["listed"] and s.bit_count() >= 3)
        places = scope_names(failing)
        cnf = "; ".join(" ".join(sign + f"d{d}" for d in row) for row in stages[-1] for sign in ("", "-"))
        args = ["-B", "-m", "knotlab", "check", "--cnf", cnf, "--loops", *[f"d{x}" for x in places[:-1]],
                "--contact", f"d{places[-1]}", "--witnesses", *[f"d{x}" for x in names if x not in places], "--json"]
        checked = json.loads(subprocess.check_output([str(ROOT / ".venv/bin/python"), *args], cwd=ROOT,
                              env=dict(os.environ, PYTHONPATH=str(ROOT / "tools"))))
        assert not checked["is_knot"]
        result["canonical_arguments"] = args
        result["canonical_failing_listed_scope"] = places
        result["canonical_result"] = {k: checked[k] for k in ("binding", "loss_on_erasure", "coexistence", "is_knot", "allowed")}
    return result


if __name__ == "__main__":
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--count", type=int, default=300)
    p.add_argument("--census", action="store_true")
    p.add_argument("--prefixes", action="store_true")
    p.add_argument("--case", type=int)
    p.add_argument("--arm", choices=forbid.ARMS, default="ordinary")
    p.add_argument("--rounds", type=int, default=2)
    p.add_argument("--cap", type=int, default=14)
    p.add_argument("--canonical", action="store_true")
    args = p.parse_args()
    census = json.loads((GROWTH / "starts.json").read_text())
    before = time.monotonic()
    if args.case is None:
        indices = (range(len(census)) if args.census else random.Random(20261129).sample(range(len(census)), 300))[:args.count]
        result = scan(census, indices, args.rounds, args.cap, args.prefixes)
        result.update(draws=len(indices), census_size=len(census), seed=None if args.census else 20261129,
                      rounds_cap=args.rounds, distinctions_cap=args.cap, includes_funded_prefixes=args.prefixes)
    else:
        result = certificate(census, args.case, args.arm, args.rounds, args.canonical)
    result["elapsed_seconds_excluding_import_and_census_load"] = round(time.monotonic() - before, 6)
    print(json.dumps(result, indent=2))
