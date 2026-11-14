"""Gate cases on the shared runner, plus their exact coverage aggregation.

This script never starts a service, changes a tracker, or computes P1--P5.
"""
from __future__ import annotations

import argparse
from collections import Counter, defaultdict
from itertools import product
import json
from pathlib import Path
import random
import sys
sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import inputs
import window
import scope as scope_module

_records = None
_phase = "families"
_bond_sample = "bond_sample.json"


SyntaxPreparation = scope_module.SyntaxPreparation


def selections(records):
    negative = sorted((key for key, r in records.items() if r["verdict"] == "certified"),
                      key=inputs.carry_order)[:300]
    brute = []
    for key in sorted(inputs.population(records), key=inputs.carry_order):
        prep = SyntaxPreparation(key)
        if scope_module.scope(prep)["in_scope"] and scope_module.identity_cycle(prep):
            brute.append(key)
            if len(brute) == 50:
                break
    if len(negative) != 300 or len(brute) != 50:
        raise ValueError("gate selection has insufficient families")
    return negative, brute


def setup(params):
    global _records, _phase, _bond_sample
    if set(params) - {"phase", "bond_sample"}:
        raise ValueError("only phase and bond_sample are supported")
    _phase = params.get("phase", "families")
    _bond_sample = params.get("bond_sample", "bond_sample.json")
    if _phase not in ("families", "bonds"):
        raise ValueError("unknown gate phase")
    _records = inputs.load_records()
    inputs.verify_sources()


def cases():
    if _phase == "bonds":
        selection = json.loads(inputs.permitted(HERE / _bond_sample).read_text())
        for i, item in enumerate(selection["bonds"]):
            yield f"bond:{i:03d}", item
        return
    yield "scope", dict(kind="scope")
    for name in ("pendant", "port_only", "dead_carriage", "forgetting"):
        yield "synthetic:" + name, dict(kind="synthetic", name=name)
    negative, brute = selections(_records)
    for key in negative:
        yield "negative:" + inputs.carry_order(key), dict(kind="negative", key=key)
    for key in brute:
        yield "brute:" + inputs.carry_order(key), dict(kind="brute", key=key)


def synthetic_key(name):
    controls = {
        # Usual() appends the required port-only knot to a permuting SELF call.
        "pendant": [[3, 2, [["K", [0, 3, 4]], ["SELF", [0, 1, 2]]]]],
        "port_only": [[3, 3, [["K", [0, 1, 2]], ["K", [3, 4, 5]], ["SELF", [0, 1, 2]]]]],
        # Port 0 occurs only in its self-carriage. Ports 1,2,3 form the knot.
        "dead_carriage": [[3, 3, [["K", [1, 2, 3]], ["SELF", [0, 4, 5]]]]],
        "forgetting": [[3, 3, [["K", [0, 3, 4]], ["SELF", [3, 4, 5]]]]],
    }
    return json.dumps(controls[name], separators=(",", ":"))


def scope_gate():
    reference = json.loads(inputs.INVENTORY.read_text())
    mismatches = []
    small = []
    all_scope = defaultdict(Counter)
    certified_wrappers = Counter()
    for key, result in _records.items():
        if not (result["c"] == 1 and not result["chain"]) and result["verdict"] != "certified":
            continue
        prep = SyntaxPreparation(key)
        flags = scope_module.scope(prep)
        if result["c"] == 1 and not result["chain"]:
            small.append(dict(key=key, verdict=result["verdict"], r=result.get("r"), **flags))
        if result["verdict"] == "certified":
            if flags["wrapper"]:
                certified_wrappers["all"] += 1
                certified_wrappers["chain" if result["chain"] else "nonchain"] += 1
            group = "chain" if result["chain"] else "c>=2" if result["c"] >= 2 else "c=1 other"
            count = all_scope[group]
            count["families"] += 1
            count["other_own" if flags["other_own_types"] else "no_other_own"] += 1
            if flags["delaying_types"]:
                count["other_recursion_can_delay_S"] += 1
                if not flags["other_own_types"]:
                    count["no_other_own_but_delayed_S"] += 1
    counts = {}
    for name in ("all", "certified", "non-forgetting"):
        rs = small if name == "all" else [r for r in small if r["verdict"] == name]
        counts[name] = dict(families=len(rs), other_own=sum(bool(r["other_own_types"]) for r in rs),
                            other_own_from_S=sum(r["other_own_from_S"] for r in rs),
                            other_own_from_main=sum(r["other_own_from_main"] for r in rs),
                            no_other_own=sum(not r["other_own_types"] for r in rs),
                            wrapper_main=sum(r["wrapper"] for r in rs),
                            other_own_r_counts=dict(Counter(str(r["r"]) if r["r"] is not None else "null"
                                                           for r in rs if r["other_own_types"])))
    actual = dict(summary=dict(families=len(small), certified=sum(r["verdict"] == "certified" for r in small),
                               counts=counts), certified_wrappers=dict(certified_wrappers),
                  all_certificate_scope={k: dict(v) for k, v in all_scope.items()})
    for name, value in actual.items():
        if value != reference[name]:
            mismatches.append(dict(field=name, actual=value, expected=reference[name]))
    # Also compare every directly recorded predicate, not counts alone.
    by_key = {r["key"]: r for r in small}
    for row in reference["families"]:
        actual_row = by_key[row["key"]]
        for old, new in (("has_other_own", "other_own_types"),
                         ("has_other_own_from_S", "other_own_from_S"),
                         ("has_other_own_from_main", "other_own_from_main")):
            if row[old] != bool(actual_row[new]):
                mismatches.append(dict(key=row["key"], predicate=old))
    return dict(kind="scope", passed=not mismatches, actual=actual, mismatches=mismatches)


def negative_live(prep, calls, w, max_r=8):
    """Step 9 after knot-seeded liveness, without running G."""
    dead = window.dead_positions(prep)
    live = [j for j in range(3) if j not in dead[prep.S]]
    if not w.get("complete"):
        return dict(complete=False, certified=False, r=None, dead_positions=dead, live_S=live,
                    skipped="window incomplete/ambiguous")
    def project_mask(mask):
        answer = 0
        for value in range(8):
            if mask >> value & 1:
                answer |= 1 << window.reduce_state(value, live)
        return answer
    G = sum(int(v) << j for j, v in enumerate(prep.G[prep.S]))
    images = sorted({project_mask(A) for A in w["context_images"]})
    generators = [window.reduce_relation(c["relation"], live) for c in calls]
    return dict(window.trimmed_gap(generators, images, project_mask(G), size=1 << len(live), max_r=max_r),
                dead_positions=dead, live_S=live)


def run(case_id, payload):
    kind = payload.get("kind", "bond")
    if kind == "scope":
        return scope_gate()
    if kind == "synthetic":
        name = payload["name"]
        key = synthetic_key(name)
        result = window.run_family(key)
        w = result["window"]
        g = result.get("growth", {})
        if name == "pendant":
            passed = w["complete"] and all(row["U"] == 3 for row in w["levels"])
        elif name == "port_only":
            passed = w["complete"] and w["verdict"] == "none"
        elif name == "dead_carriage":
            passed = w["complete"] and w["verdict"] == "none" and g.get("G", {}).get("certified", False)
        else:
            passed = g.get("G2", {}).get("certified", False)
        return dict(kind=kind, name=name, passed=passed, result=result)
    key = payload["key"]
    if kind == "negative":
        result = window.run_family(key, _records[key], include_growth=False)
        prep = window.paths.Preparation(json.loads(key))
        calls = window.relations.per_call(prep)
        w = result["window"]
        r = _records[key]["r"]
        G = sum(int(v) << j for j, v in enumerate(prep.G[prep.S]))
        g2 = (window.trimmed_gap([c["relation"] for c in calls], w["context_images"], G, max_r=r)
              if w.get("complete") else dict(certified=False, skipped="window incomplete/ambiguous"))
        g2_live = negative_live(prep, calls, w, max_r=r)
        failures = []
        computed = list(w.get("levels", []))
        if w.get("complete"):
            computed.append(dict(s=w["repeat_at"], U=w["U_at_repeat"]))
        for row in computed:
            lower = 2 + ((row["s"] - int(prep.main != prep.S)) // r)
            if isinstance(row["U"], int) and row["U"] < lower:
                failures.append(dict(s=row["s"], U=row["U"], lower=lower))
        complete = bool(w.get("complete")) and bool(g2.get("complete")) and bool(g2_live.get("complete"))
        return dict(kind=kind, key=key, passed=complete and not failures and
                    bool(g2.get("certified") or g2_live.get("certified")),
                    lower_bound_failures=failures, r=r, G2=g2, G2_live=g2_live, result=result)
    prep = window.paths.Preparation(json.loads(key))
    if kind == "brute":
        import brute
        family_result = window.run_family(key, _records[key], include_growth=False)
        calls = window.relations.per_call(prep)
        starts = window.start_states(prep)
        differences, pool, count = [], [], 0
        for s in range(4):
            for entry, start in enumerate(starts):
                for word in product(range(len(calls)), repeat=s):
                    state = start
                    for i in word:
                        state = window.step(state, calls[i], prep.k)
                    projected = window.project_state(prep, state)
                    explicit = brute.project_word(prep, word, entry_index=entry)
                    if explicit.get("status", "ok") != "ok":
                        differences.append(dict(entry_index=entry, word=list(word), explicit=explicit))
                        continue
                    count += 1
                    if projected["labels"] != explicit["labels"] or projected["allowed"] != explicit["allowed"]:
                        differences.append(dict(entry_index=entry, word=list(word), window=projected, brute=explicit))
                    bond = window.window_bond(prep, state)
                    for witness in bond["least_bonds"]:
                        pool.append(dict(key=key, entry_index=entry, word=list(word),
                                         members=witness["members"], size=bond["g"]))
        return dict(kind=kind, key=key, passed=not differences, comparisons=count,
                    differences=differences, bond_pool=pool, result=family_result)
    if kind == "bond":
        import brute
        checked = brute.recheck_bond(prep, payload["word"], payload["members"],
                                     entry_index=payload.get("entry_index"))
        return dict(kind="bond", passed=bool(checked.get("passed")), witness=payload, check=checked)
    raise ValueError(f"unknown gate kind: {kind}")


def latest(path):
    sys.path.insert(0, str(inputs.ROOT / "scripts"))
    from longrun import load_results
    return load_results(path)


def freeze_bonds(gate_results, target=None):
    records = latest(gate_results)
    _, expected_keys = selections(inputs.load_records())
    expected = {"brute:" + inputs.carry_order(k) for k in expected_keys}
    if not expected.issubset(records):
        raise ValueError("all 50 brute families must finish before freezing the 200 bonds")
    pool = []
    for case in sorted(expected):
        row = records[case]
        if row["status"] != "ok":
            raise ValueError("brute comparison has a runner failure; cannot freeze bonds")
        value = row["result"]
        if not value.get("passed"):
            raise ValueError("brute comparison failed; preserve failure before selecting bonds")
        pool.extend(value["bond_pool"])
    if len(pool) < 200:
        raise ValueError(f"only {len(pool)} recorded least bonds; cannot draw 200 without an unspecified replacement rule")
    chosen = random.Random(20261114).sample(pool, 200)
    target = inputs.permitted(HERE / target) if target is not None else HERE / "bond_sample.json"
    if target.exists():
        raise FileExistsError("preserve existing bond sample")
    inputs.dump(target, dict(seed=20261114, pool_size=len(pool), sampling="without replacement",
                             source_sha256=inputs.digest(Path(gate_results) / "results.jsonl"), bonds=chosen))


def aggregate(families, bonds=None, smoke=None, negative_live_results=None):
    recs = latest(families)
    setup({})
    expected = {case for case, _ in cases()}
    missing = sorted(expected - set(recs))
    groups = defaultdict(list)
    errors = []
    for case, rec in recs.items():
        if rec["status"] != "ok":
            errors.append(dict(case=case, status=rec["status"], error=rec.get("error")))
        else:
            groups[rec["result"]["kind"]].append(rec["result"])
    live_coverage = dict(expected=300, completed=0, status="not_supplied")
    if negative_live_results:
        live_records = latest(negative_live_results)
        by_key = {r["result"]["key"]: r["result"] for r in live_records.values() if r["status"] == "ok"}
        for row in groups["negative"]:
            if row["key"] not in by_key:
                row["passed"] = False
                continue
            live = by_key[row["key"]]["G2_live"]
            row["G2_live"] = live
            row["passed"] = (bool(row["result"]["window"].get("complete")) and
                             bool(row["G2"].get("complete")) and bool(live.get("complete")) and
                             not row["lower_bound_failures"] and
                             bool(row["G2"].get("certified") or live.get("certified")))
        live_coverage = dict(expected=300, completed=len(by_key),
                             statuses=dict(Counter(r["status"] for r in live_records.values())),
                             certified=sum(r["G2_live"].get("certified", False) for r in by_key.values()),
                             status="complete" if len(by_key) == 300 else "incomplete")
    result = dict(expected_cases=len(expected), finished_cases=len(recs), missing=missing, runner_errors=errors)
    result["negative_live_coverage"] = live_coverage
    for kind, number in (("scope", 1), ("synthetic", 4), ("negative", 300), ("brute", 50)):
        rs = groups[kind]
        result[kind] = dict(expected=number, completed=len(rs), passed=len(rs) == number and all(r["passed"] for r in rs),
                            failures=[r for r in rs if not r["passed"]])
    result["d_bonds"] = dict(expected=200, completed=0, passed=False, status="not_run")
    if bonds:
        br = latest(bonds)
        checks = [r["result"] for r in br.values() if r["status"] == "ok"]
        result["d_bonds"] = dict(expected=200, completed=len(checks), passed=len(checks) == 200 and
                                  all(r["passed"] for r in checks), failures=[r for r in checks if not r["passed"]])
    measured = [r["result"] for kind in ("negative", "synthetic", "brute")
                for r in groups[kind] if "result" in r]
    if smoke:
        measured.extend(r["result"] for r in latest(smoke).values() if r["status"] == "ok")
    for name in ("gate_a", "gate_b", "gate_e"):
        available = [r for r in measured if name != "gate_b" or
                     r[name].get("complete") or r["window"].get("complete")]
        unavailable = [r["key"] for r in measured if r not in available]
        failures = [r["key"] for r in available if not r[name]["passed"]]
        result[name] = dict(checked=len(available), passed=bool(available) and not failures and not unavailable,
                            available_passed=bool(available) and not failures,
                            failures=failures, unavailable=unavailable)
    result["passed"] = not missing and not errors and all(result[n]["passed"] for n in
                       ("scope", "synthetic", "negative", "brute", "d_bonds", "gate_a", "gate_b", "gate_e"))
    inputs.dump(HERE / "gates.json", result)
    print(json.dumps({n: v.get("passed") for n, v in result.items() if isinstance(v, dict)}))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    freeze = sub.add_parser("freeze-bonds")
    freeze.add_argument("--families", type=Path, required=True)
    freeze.add_argument("--output", type=Path)
    report = sub.add_parser("summarize")
    report.add_argument("--families", type=Path, required=True)
    report.add_argument("--bonds", type=Path)
    report.add_argument("--smoke", type=Path)
    report.add_argument("--negative-live", type=Path)
    args = parser.parse_args()
    if args.command == "freeze-bonds":
        freeze_bonds(args.families, args.output)
    else:
        aggregate(args.families, args.bonds, args.smoke, args.negative_live)


if __name__ == "__main__":
    main()
