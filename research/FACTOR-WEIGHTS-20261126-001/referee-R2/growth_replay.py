"""Audit ordered birth records and check the denominators in two growth engines."""

import argparse
from collections import Counter
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from math import prod
from pathlib import Path
import random
import resource
import sys
from time import perf_counter
from unittest.mock import patch

from pysat.solvers import Solver


ROOT = Path(__file__).resolve().parents[3]
RESEARCH = ROOT / "research"
FORBID = RESEARCH / "FORBID-EDITS-20261126-001"
WAIT = RESEARCH / "SHORT-AGAIN-20261126-001"
THREE_KNOT_START = ((0, 2, 3), (0, 1, 4), (1, 2, 5))
FOUR_KNOT_START = ((0, 3, 4), (0, 1, 5), (1, 2, 6), (2, 3, 7))
ROUNDS = 6
CANONICAL_BOUND = 600
WAIT_BOUND = 3000
WORD_SAMPLES = 8
JOINT_FRESH_LIMIT = 10
LOCAL_FRESH_LIMIT = 7
SEED = 20261130
FIELDS = (
    "round", "knots", "distinctions", "births", "fresh", "takes",
    "births_taking_with_exactly_two_prior_holders", "highest_holder_count",
    "zero_fresh", "zero_fresh_with_counterstate", "cancelled_groups",
    "waiting_knots", "retired_knots", "barred_now", "sampled_prefixes",
    "sampled_prefixes_with_no_completion", "local_counts_tested",
    "joint_counts_tested", "allowed",
)


def load(path, name):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def mask(names):
    return sum(1 << name for name in names)


def allowed(law, ones, width):
    return (ones % 2 == 0) if law == "parity" else (0 < ones < width)


def clauses(scope):
    row = [d + 1 for d in scope]
    return (row, [-x for x in row])


def reduce_row(row, basis):
    while row and row.bit_length() - 1 in basis:
        row ^= basis[row.bit_length() - 1]
    return row


def add_basis(scope, basis):
    row = reduce_row(mask(scope), basis)
    if row:
        basis[row.bit_length() - 1] = row


def sample_start(names, law, solver, basis, rng):
    states = []
    for _ in range(WORD_SAMPLES):
        if law == "parity":
            state = sum((1 << d) for d in names if d not in basis and rng.getrandbits(1))
            for pivot, equation in sorted(basis.items()):
                if (state & equation).bit_count() % 2:
                    state |= 1 << pivot
        else:
            order = sorted(names)
            rng.shuffle(order)
            assumptions = []
            state = 0
            for d in order:
                sign = d + 1 if rng.getrandbits(1) else -(d + 1)
                if not solver.solve(assumptions=assumptions + [sign]):
                    sign = -sign
                assumptions.append(sign)
                if sign > 0:
                    state |= 1 << d
        states.append(state)
    return states


def joint_count(law, old_ones, births, fresh):
    pos = {d: i for i, d in enumerate(fresh)}
    rows = [(old, mask(pos[d] for d in b["fresh"]), len(b["scope"])) for old, b in zip(old_ones, births)]
    return sum(
        all(allowed(law, old + (bits & use).bit_count(), width) for old, use, width in rows)
        for bits in range(1 << len(fresh))
    )


def extend_sample(law, state, births, rng):
    fresh = [d for b in births for d in b["fresh"]]
    old_ones = [(state & b["input_mask"]).bit_count() for b in births]
    denominators = []
    local_tests = 0
    extension = state
    for ones, birth in zip(old_ones, births):
        scope, inputs, private = birth["scope"], birth["inputs"], birth["fresh"]
        width, p, f = len(scope), len(inputs), len(private)
        if not private:
            count = int(allowed(law, ones, width))
        elif law == "parity":
            count = 1 << (f - 1)
        else:
            count = (1 << f) - int(ones == 0) - int(ones == p)
        denominators.append(count)
        if f <= LOCAL_FRESH_LIMIT:
            verified = [
                bits for bits in range(1 << f)
                if allowed(law, ones + bits.bit_count(), width)
            ]
            assert len(verified) == count
            local_tests += 1
            if not verified:
                continue
            chosen = rng.choice(verified)
        else:
            chosen = rng.getrandbits(f)
            while not allowed(law, ones + chosen.bit_count(), width):
                chosen = rng.getrandbits(f)
        extension |= mask(d for i, d in enumerate(private) if (chosen >> i) & 1)
        assert allowed(law, (extension & birth["scope_mask"]).bit_count(), width)

    size = prod(denominators)
    joint_tests = int(len(fresh) <= JOINT_FRESH_LIMIT)
    if joint_tests:
        assert joint_count(law, old_ones, births, fresh) == size
    return extension if size else None, local_tests, joint_tests


def birth_record(raw, scope, index):
    inputs, fresh = tuple(raw["inputs"]), tuple(raw["fresh"])
    assert len(inputs) == raw["p"] and inputs and len(fresh) == raw["f"]
    assert tuple(scope) == inputs + fresh and len(set(scope)) == len(scope)
    return {
        "id": index, "inputs": inputs, "fresh": fresh, "scope": tuple(scope),
        "input_mask": mask(inputs), "scope_mask": mask(scope),
    }


def canonical_rounds(forbid, start, law, arm):
    current = start
    for index in range(1, ROUNDS + 1):
        grown, status, raw = forbid.grown(current, law, arm)
        if status != "funded":
            assert grown == current and not raw
            return status
        old_count = len(current)
        assert grown[:old_count] == current and len(grown) == old_count + len(raw)
        expected_loose = Counter(d for d, n in Counter(d for k in current for d in k).items() if n == 1)
        assert Counter(d for b in raw for d in b["inputs"]) == expected_loose
        births = []
        for i, b in enumerate(raw, start=old_count):
            assert b["knot"] == i and tuple(b["inputs"]) == tuple(sorted(b["inputs"]))
            births.append(birth_record(b, grown[i], i))
        current = grown
        yield index, len(grown), births, {"highest_holder_count": 2}
        if len(grown) > CANONICAL_BOUND:
            return "knot cap after round"
    return "round cap"


def audit_waiting(before, after, record):
    assert after.round == before.round + 1 == record["round"]
    assert after.places[:before.n_knots] == before.places
    assert after.n_knots == before.n_knots + len(record["births"])
    acts = Counter(record["act"].values())
    ordered_holders = [list(h) for h in before.holders]
    fresh_owner = {}
    births = []
    paid = {u: [] for u in record["members"]}
    stats = Counter()
    first_take = None
    short = set(record["short"])
    cancelled = [g for g in record["groups"] if short.intersection(g)]
    assert cancelled == record["cancelled"]
    joins = [g for g in record["groups"] if not short.intersection(g)]
    assert [b["parents"] for b in record["births"] if b["kind"] == "join"] == joins
    assert all(b["kind"] == "join" for b in record["births"][:len(joins)])
    for i, b in enumerate(record["births"], start=before.n_knots):
        assert b["id"] == i and b["inputs"] == b["loose"] + b["takes"]
        assert after.parents[i] == tuple(sorted(b["parents"]))
        assert len(b["loose"]) == len(b["parents"])
        for parent, distinction in zip(b["parents"], b["loose"]):
            assert before.holders[distinction] == [parent] and not before.barred[distinction]
            paid[parent].append(distinction)
        third_holder = False
        for d in b["takes"]:
            assert tuple(before.holders[d]) == b["take_holders"][d] and len(before.holders[d]) >= 2
            assert d not in b["loose"]
            if len(ordered_holders[d]) == 2:
                third_holder = True
                if first_take is None:
                    first_take = {
                        "birth": i, "distinction": d, "prior_holders": ordered_holders[d][:],
                        "inputs": b["inputs"], "fresh": b["fresh"],
                    }
        stats["births_taking_with_exactly_two_prior_holders"] += third_holder
        stats["takes"] += len(b["takes"])
        for d in b["inputs"]:
            ordered_holders[d].append(i)
        for d in b["fresh"]:
            assert d == before.n_distinctions + len(fresh_owner)
            fresh_owner[d] = i
        births.append(birth_record(b, after.places[i], i))
    assert after.holders == ordered_holders + [[owner] for owner in fresh_owner.values()]
    assert after.maker == before.maker + list(fresh_owner.values())
    expected_barred = set()
    for u, seen in paid.items():
        usable, act = before.usable(u), record["act"][u]
        if act in ("wait", "retire"):
            assert not seen
            expected = usable if act == "wait" else []
            assert after.usable(u) == expected
            if act == "retire":
                expected_barred.update(usable)
        else:
            kept = record["kept_by"].get(u, [])
            assert seen + kept == usable and after.usable(u) == kept
    assert expected_barred == set(record["barred_now"])
    assert all(after.barred[d] == (before.barred[d] or d in expected_barred) for d in range(before.n_distinctions))
    assert not any(after.barred[before.n_distinctions:])
    stats.update(highest_holder_count=max(map(len, after.holders)), cancelled_groups=len(cancelled),
                 waiting_knots=acts["wait"], retired_knots=acts["retire"], barred_now=len(expected_barred))
    if first_take is not None:
        stats["first_third_holder"] = first_take
    return births, dict(stats)


def waiting_rounds(ring, stars, roles, law):
    trace = []
    play = ring.eng.play_round

    def capture(state, selected, guard):
        rec = play(state, selected, guard)
        trace.append(rec)
        return rec

    growth = ring.Growth(stars, roles, law)
    assert growth.snaps[0].places == [list(scope) for scope in stars]
    with patch.object(ring.eng, "play_round", capture):
        growth.run(ROUNDS, WAIT_BOUND)
    assert len(growth.snaps) - 1 == len(trace) == len(growth.rows)
    for before, after, rec in zip(growth.snaps, growth.snaps[1:], trace):
        births, stats = audit_waiting(before, after, rec)
        yield after.round, after.n_knots, births, stats
    return growth.stop or "round cap"


def check_history(case, start, law, rounds):
    names = {d for scope in start for d in scope}
    all_scopes = [(mask(scope), len(scope)) for scope in start]
    start_q = len(names)
    basis = {}
    rng = random.Random(f"{SEED}/{case}")
    with Solver() as solver:
        for scope in start:
            if law == "parity":
                add_basis(scope, basis)
            else:
                solver.append_formula(clauses(scope))
        live = law == "parity" or solver.solve()
        samples = sample_start(names, law, solver, basis, rng) if live else []
        for word in samples:
            assert all(allowed(law, (word & mask(k)).bit_count(), len(k)) for k in start)
        rows = []
        witnesses = {}
        while True:
            try:
                index, knot_count, births, stats = next(rounds)
            except StopIteration as stop:
                return {
                    "case": case, "start_knots": len(start), "start_distinctions": start_q,
                    "stop": stop.value, "rounds": rows, "witnesses": witnesses,
                }
            new = set()
            zero = 0
            loss = 0
            for b in births:
                assert set(b["inputs"]) <= names
                private = set(b["fresh"])
                assert not (private & (names | new))
                new.update(private)
                if not private:
                    zero += 1
                    counterstate = None
                    if law == "parity":
                        is_filter = bool(reduce_row(b["input_mask"], basis))
                    else:
                        ls = [d + 1 for d in b["inputs"]]
                        is_filter = live and (
                            solver.solve(assumptions=ls) or solver.solve(assumptions=[-x for x in ls])
                        )
                        if is_filter and "first_loss" not in witnesses:
                            model = solver.get_model()
                            counterstate = mask(x - 1 for x in model if x > 0 and x - 1 in names)
                            assert all(allowed(law, (counterstate & old).bit_count(), width)
                                       for old, width in all_scopes)
                            assert not allowed(law, (counterstate & b["input_mask"]).bit_count(), len(b["inputs"]))
                    if is_filter:
                        loss += 1
                        witnesses.setdefault("first_loss", {
                            "round": index, "birth": b["id"], "inputs": b["inputs"],
                            "old_state_bitmask_hex": hex(counterstate) if counterstate is not None else None,
                        })
            if "first_third_holder" in stats:
                witnesses.setdefault("first_third_holder", {"round": index, **stats["first_third_holder"]})
            extensions, locals_tested, joints_tested = [], 0, 0
            for state in samples:
                extension, local, joint = extend_sample(law, state, births, rng)
                if extension is not None:
                    extensions.append(extension)
                locals_tested += local
                joints_tested += joint
            for b in births:
                all_scopes.append((b["scope_mask"], len(b["scope"])))
                if law == "parity":
                    add_basis(b["scope"], basis)
                else:
                    solver.append_formula(clauses(b["scope"]))
            if loss:
                live = law == "parity" or solver.solve()
            assert live or not extensions
            names.update(new)
            row = dict(stats, round=index, knots=knot_count, distinctions=len(names), births=len(births),
                       fresh=len(new), zero_fresh=zero, zero_fresh_with_counterstate=loss, allowed=live,
                       sampled_prefixes=len(samples), sampled_prefixes_with_no_completion=len(samples) - len(extensions),
                       local_counts_tested=locals_tested, joint_counts_tested=joints_tested)
            rows.append([row.get(field, 0) for field in FIELDS])
            samples = extensions


def check_three_knot_start(forbid, ring):
    expected = [state for state in range(1 << 6)
                if all(allowed("nae", (state & mask(k)).bit_count(), len(k)) for k in THREE_KNOT_START)]
    reference = []
    for arm in forbid.ARMS:
        grown, status, records = forbid.grown(THREE_KNOT_START, "nae", arm)
        assert status == "funded" and len(records) == 1
        reference.append((arm, records[0], grown[-1]))
    state = ring.eng.from_stars(THREE_KNOT_START)
    rec = ring.eng.play_round(state, ring.law_of("REC-ONE-FEWER"), ring.eng.Guard(ring.bench.MULT))
    assert len(rec["births"]) == 1
    reference.append(("REC-ONE-FEWER", rec["births"][0], state.places[-1]))
    summaries = {}
    for label, b, scope in reference:
        cooked = birth_record(b, scope, 3)
        counts = Counter()
        for word in expected:
            old_ones = [(word & cooked["input_mask"]).bit_count()]
            count = joint_count("nae", old_ones, [cooked], list(cooked["fresh"]))
            counts[count] += 1
        summaries[label] = {"inputs": b["inputs"], "fresh": b["fresh"], "completion_counts": counts}
    return {"start": THREE_KNOT_START, "allowed": len(expected), "variants": summaries}


def all_cases(forbid, ring, pilot):
    census_path = FORBID / "starts.json"
    assert census_path.is_file()
    census = forbid.census()
    selected = random.Random(SEED).sample(range(len(census)), 4 if pilot else 32)
    starts = [("three knots sharing in pairs", THREE_KNOT_START), ("four knots sharing in succession", FOUR_KNOT_START)]
    starts.extend((f"census start {i}", forbid.supports_of(census[i])) for i in selected)
    groups = {}
    t0 = perf_counter()
    rows = []
    for (label, start), law, arm in product(starts, forbid.LAWS, forbid.ARMS):
        rows.append(check_history(["canonical", label, law, arm], start, law, canonical_rounds(forbid, start, law, arm)))
    groups["canonical"] = {"cases": rows, "seconds": perf_counter() - t0}

    t0 = perf_counter()
    distances = [1] + random.Random(SEED).sample(range(2, 9), 2)
    rows = []
    for steps, receiver, join, ration in product(distances[:1] if pilot else distances, ("ring", "stub"),
                                                 ("meeting", "share"), ring.LAWS):
        stars, roles = ring.bench.build("source", receiver, steps, None, join)
        law = ring.law_of(ration)
        rows.append(check_history(["waiting", "source", receiver, steps, join, ration], stars, "nae",
                                  waiting_rounds(ring, stars, roles, law)))
    groups["waiting"] = {"cases": rows, "seconds": perf_counter() - t0}

    t0 = perf_counter()
    rows = []
    stars = ring.bench.STARS["source"]
    roles = ["A"] * len(stars)
    for knot_law, treatment in product(("nae", "parity"), ring.eng.TREATMENTS[:2] if pilot else ring.eng.TREATMENTS):
        law = ring.eng.Law("FLOOR1", treatment, "MET", knot_law, "OLDEST")
        rows.append(check_history(["taking", "bare source", law.name()], stars, knot_law,
                                  waiting_rounds(ring, stars, roles, law)))
    groups["taking"] = {"cases": rows, "seconds": perf_counter() - t0}
    return groups, len(census), selected, distances[:1] if pilot else distances


def summarize(rows):
    checks = Counter()
    round_count = Counter()
    peak = Counter()
    for case in rows:
        for record in case["rounds"]:
            r = dict(zip(FIELDS, record))
            round_count[r["round"]] += 1
            for field in ("knots", "distinctions", "highest_holder_count"):
                peak[field] = max(peak[field], r[field])
            for field in FIELDS[3:-1]:
                if field != "highest_holder_count":
                    checks[field] += r[field]
            checks["empty_rounds"] += r["births"] == 0
            checks["rounds_losing_states"] += r["zero_fresh_with_counterstate"] > 0
    return {"histories": len(rows), "rounds": sum(round_count.values()), "by_round": round_count,
            "peak": peak, "checks": checks, "stops": Counter(case["stop"] for case in rows)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true")
    args = parser.parse_args()
    t0 = perf_counter()
    ring = load(WAIT / "ring_line.py", "ring_line")
    forbid = load(FORBID / "forbid.py", "forbid")
    groups, census_count, selection, distances = all_cases(forbid, ring, args.pilot)
    controls = check_three_knot_start(forbid, ring)
    sources = [Path(m.__file__).resolve() for m in
               (ring, ring.rations, ring.bench, ring.eng, forbid, forbid.ENGINE, forbid.ENGINE.J.F)]
    sources += [Path(forbid.grow.__code__.co_filename).resolve(), FORBID / "starts.json"]
    for group in groups.values():
        group["summary"] = summarize(group["cases"])
        if args.pilot:
            del group["cases"]
    result = {
        "seed": SEED,
        "sampling": {
            "census": "uniform without replacement",
            "words_per_history": WORD_SAMPLES,
            "parity_start": "uniform over allowed states",
            "nae_start": "random order of distinctions, fair choice at each extendible prefix",
            "completion": "uniform given the old state at each birth; stop that state on a zero denominator",
        },
        "pilot": args.pilot, "census_rows_read": census_count, "census_rows_replayed": selection,
        "ring_steps_replayed": distances, "maximum_rounds": ROUNDS,
        "knot_caps": {"canonical": CANONICAL_BOUND, "waiting_and_taking": WAIT_BOUND},
        "full_stage_enumeration_fresh_limit": JOINT_FRESH_LIMIT,
        "single_birth_enumeration_fresh_limit": LOCAL_FRESH_LIMIT,
        "sources_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in sources},
        "round_fields": FIELDS, "groups": groups, "exact_three_knot_control": controls,
        "peak_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
        "address_space_bytes": resource.getrlimit(resource.RLIMIT_AS)[0],
        "seconds": perf_counter() - t0,
    }
    print(json.dumps(result, separators=(",", ":")))


if __name__ == "__main__":
    main()
