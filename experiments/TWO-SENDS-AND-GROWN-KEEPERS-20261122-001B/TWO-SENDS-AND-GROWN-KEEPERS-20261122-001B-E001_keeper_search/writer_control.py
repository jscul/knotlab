"""Replay the supplied two-offer writer on the funded D(3,4,1) presentation."""

import argparse
from collections import Counter, defaultdict
from fractions import Fraction as Q
from functools import cache
import gzip
from hashlib import sha256
from importlib.util import find_spec, module_from_spec, spec_from_file_location
from io import BytesIO
from itertools import product
import json
from math import prod
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
RECIPE = (3, 4, 1)
FOUNDING = (tuple(range(7)), (0, 1, 2, 7))
SHARED = (0, 1, 2)
PAID = 3
READY, ZERO_ANSWER, ONE_ANSWER = (int(word, 2) for word in ("1100", "1010", "0110"))
LAWS = ("parity", "nae")
WEIGHTS = ("uniform_complete", "chronological")
VIEWS = ("terminal_only", "supplied_ready_then_terminal", "before_after_audit")
KINDS = ("ready", "zero", "one", "other")
PRE = ROOT / "research/TWO-SENDS-AND-GROWN-KEEPERS-20261122-001B/preregistration.md"
PRE_HASH = "03c11954b1f90ce364229e838dfbbcd8b63bdeb3cd76cb78482bae22fa1e78eb"
ENGINE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py"
END = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
ROUTES = ROOT / "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A/ordinary_routes.py"
OUTPUT = ROOT / "artifacts" / HERE.relative_to(ROOT / "experiments") / "writer_control.json.gz"


def _load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@cache
def _ancestors():
    growth = _load("b303_control_ordinary", ENGINE)
    end = _load("b303_control_end", END)
    ancestry = (growth.J, growth.J.fastlib, growth.S, growth.F)
    return growth, end, tuple(Path(m.__file__).resolve() for m in ancestry)


def _bits(index, width):
    return tuple((index >> j) & 1 for j in reversed(range(width)))


def _read(word, names):
    return sum(((word >> n) & 1) << j for j, n in enumerate(reversed(names)))


def _mask(names):
    return sum(1 << n for n in names)


def _embed(index, names):
    return sum(t << n for t, n in zip(_bits(index, len(names)), names, strict=True))


def _owners(rows):
    out = {}
    for name in sorted({n for row in rows for n in row}):
        out[name] = tuple(h for h, row in enumerate(rows) if name in row)
    assert all(len(held) in (1, 2) for held in out.values())
    return out


def _allowed(index, width, law):
    return index.bit_count() % 2 == 0 if law == "parity" else index not in (0, (1 << width) - 1)


def _legal(word, rows, law):
    return all(_allowed(_read(word, row), len(row), law) for row in rows)


def _founding(law):
    words, outside = [], {}
    for word in range(1 << 8):
        failed = tuple(h for h, row in enumerate(FOUNDING) if not _allowed(_read(word, row), len(row), law))
        if failed:
            outside[word] = failed
        else:
            words.append(word)
    return words, outside


def _turn(law, words):
    engine, independent, _ = _ancestors()
    seed = engine.S.from_junctions(FOUNDING)
    compact = independent.step(independent.from_stars(FOUNDING), law, max_births=64)
    if compact.status != "extend":
        return {"status": compact.status, "ordinary_offers": (), "reached": FOUNDING}
    assert len(compact.parents) <= 64 and seed.groups_among(seed.live) == []

    def finite_nae_implication(presentation, info, rng):
        # On this fixed first turn the pinned old support is all 256 candidate old words.
        # Checking both constant assignments on the paid names implements the archived NAE flag.
        for entry in info:
            paid = presentation.bits_of[entry["j"]][:entry["p"]]
            entry["implied"] = all(_allowed(_read(w, paid), len(paid), "nae") for w in words)
        return engine.F.fewest(presentation, info, rng)

    actual = (engine.parity_rule(engine.F.fewest) if law == "parity" else
              engine.nae_rule(engine.F.fewest) if find_spec("pysat") is not None else finite_nae_implication)
    metadata = []

    def observe(presentation, proposals, rng):
        grants = actual(presentation, proposals, rng)
        for entry, grant in zip(proposals, grants, strict=True):
            parents = tuple(_owners(FOUNDING)[n][0] for n in presentation.bits_of[entry["j"]])
            paid = tuple(presentation.bits_of[entry["j"]])
            assert len(paid) == entry["p"]
            if law == "nae":
                expected = all(_allowed(_read(w, paid), len(paid), law) for w in words)
            else:
                expected = all(_read(w, paid).bit_count() % 2 == 0 for w in words)
            assert expected == entry["implied"]
            metadata.append({"holder": entry["j"], "paid_names": paid, "true_parents": parents,
                             "lookahead_demand": entry["d"], "fresh_grant": grant, "implied": entry["implied"]})
        return grants

    result = seed.step(observe, rng=None)
    reached = tuple(tuple(s) for s in seed.bits_of)
    assert result is not None and result["new"] == len(metadata) == len(compact.parents) and seed.rounds == 1
    before, after = _owners(FOUNDING), _owners(reached)
    assert reached[:2] == FOUNDING and tuple(before) == tuple(range(8))
    assert tuple(m["true_parents"] for m in metadata) == tuple(compact.parents)
    assert tuple(m["fresh_grant"] for m in metadata) == tuple(compact.fresh)
    assert tuple(m["lookahead_demand"] for m in metadata) == tuple(compact.demand)
    for birth in metadata:
        holder = birth["holder"]
        paid = birth["paid_names"]
        fresh = reached[holder][len(paid):]
        assert fresh and all(after[n] == (holder,) and n not in before for n in fresh)
        assert all(after[n] == (*before[n], holder) and len(before[n]) == 1 for n in paid)
        birth["fresh_names"] = fresh
        birth["holder_age"] = seed.round_of[holder]
    assert sorted(n for m in metadata for n in m["paid_names"]) == [n for n, hs in before.items() if len(hs) == 1]
    focal = next((b for b in metadata if b["paid_names"] == (PAID,) and b["true_parents"] == (0,)), None)
    if focal is None or focal["fresh_grant"] != 3:
        return {"status": "focal_refusal", "reached": reached, "births": metadata}
    assert PAID not in FOUNDING[1] and focal["holder"] != 1
    assert after[PAID] == (0, focal["holder"])
    assert all(after[n] == (focal["holder"],) for n in focal["fresh_names"])
    return {"status": "funded", "founding": FOUNDING, "reached": reached, "births": metadata,
            "focal": focal, "old_owners": before, "reached_owners": after, "actual_funded_attempt": 1,
            "original_holder_birth_order": (0, 0), "native_value_offers_in_the_growth_step": (),
            "compact_and_named_ordinary_turn_agree": True}


@cache
def _canonical(width, allowed):
    names = tuple(f"v{i}" for i in range(width))
    clauses = [" ".join(("~" if t else "") + n for t, n in zip(_bits(w, width), names, strict=True))
               for w in range(1 << width) if w not in allowed]
    args = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
            "--loops", *names[:-1], "--contact", names[-1], "--json"]
    raw = subprocess.check_output(args, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT / "tools")})
    result = json.loads(raw)
    assert sorted(int(x, 2) for x in result["allowed"]) == list(allowed)
    assert all(result[k] for k in ("binding", "coexistence", "loss_on_erasure", "is_knot"))
    return {"K1": result["binding"], "K2": result["loss_on_erasure"], "K3": result["coexistence"], "canonical": result["is_knot"]}


def _projection(witnesses, names, law):
    actual = tuple(sorted(witnesses))
    width = len(names)
    assert width >= 3 and actual == tuple(w for w in range(1 << width) if _allowed(w, width, law))
    deletion = tuple(len({w & ~(1 << i) for w in actual}) for i in range(width))
    assert all(n == (1 << (width - 1)) for n in deletion)
    return {"names": names, "allowed_words": tuple(f"{w:0{width}b}" for w in actual),
            "projection_cardinalities_after_each_erasure": deletion, **_canonical(width, actual)}


@cache
def _extensions(paid_value, paid_count, fresh_count, law):
    return tuple(f for f in range(1 << fresh_count)
                 if _allowed((paid_value << fresh_count) | f, paid_count + fresh_count, law))


def _funded_words(law, turn, original):
    rows, births = turn["reached"], turn["births"]
    fresh_names = tuple(n for b in births for n in b["fresh_names"])
    assert len(fresh_names) == len(set(fresh_names)) and not (set(fresh_names) & set(range(8)))
    focal_at = births.index(turn["focal"])
    factors = []
    projections = [set() for _ in rows]
    for old in original:
        buckets = []
        for h, names in enumerate(rows[:2]):
            projections[h].add(_read(old, names))
        for b in births:
            paid, fresh = b["paid_names"], b["fresh_names"]
            bit_index = _read(old, paid)
            choices = _extensions(bit_index, len(paid), len(fresh), law)
            assert choices
            projections[b["holder"]].update((bit_index << len(fresh)) | f for f in choices)
            buckets.append(choices)
        count = prod(map(len, buckets))
        assert count and len(buckets[focal_at]) >= 4
        factors.append((old, tuple(buckets), count))
    report = tuple(_projection(values, names, law) for values, names in zip(projections, rows, strict=True))
    return factors, focal_at, report


def _keeper_class(code):
    return {READY: "ready", ZERO_ANSWER: "zero", ONE_ANSWER: "one"}.get(code, "other")


def _answer(code):
    return {ZERO_ANSWER: 0, ONE_ANSWER: 1}.get(code)


def _put_back(word, source_name, split_name):
    return word | (((word >> source_name) & 1) << split_name)


def _device(rows, paid, focal, shared):
    ownership = _owners(rows)
    assert paid in rows[0] and not any(n in rows[0] or n in rows[1] for n in focal)
    operands = ((shared[1], shared[2]), (shared[0], shared[2]))
    support = []
    for pair in operands:
        a, b = pair
        assert a in rows[0] and b in rows[0] and paid not in pair and not (set(focal) & set(pair))
        support.append(ownership[a] == ownership[b] == (0, 1) and set(pair) <= set(rows[1]))
    return {"rows": rows, "keeper": rows[1], "paid": paid, "focal": focal, "operands": operands,
            "supported": tuple(support), "ownership": ownership}


def _offer(word, apparatus, guard, enabled_schedule=True, connected=True):
    paid = apparatus["paid"]
    actual_u = _read(word, (paid,))
    names = apparatus["operands"][guard]
    supported = apparatus["supported"][guard]
    delivered = enabled_schedule and connected
    eligible = delivered and supported and actual_u == guard
    changed = eligible and _read(word, names) in (1, 2)
    after = word ^ _mask(names) if changed else word
    assert _read(after, (paid,)) == actual_u
    disposition = ("not_offered" if not enabled_schedule else "undelivered" if not connected else
                   "unsupported" if not supported else "guard_refused" if not eligible else
                   "fired" if changed else "equal_operands_idle")
    return after, {"guard_name": paid, "required_paid_value": guard, "actual_paid_value_at_P": actual_u,
                   "operands": names, "offered": enabled_schedule, "delivered_to_P": delivered,
                   "incidence_supported": supported, "guard_satisfied": actual_u == guard,
                   "enabled": eligible, "changed": changed, "kind": disposition, "old_input": word, "old_output": after}


def _apply(word, apparatus, agenda, connected=True, reverse=False):
    calls = []
    for sign in ((1, 0) if reverse else (0, 1)):
        word, call = _offer(word, apparatus, sign, agenda[sign], connected)
        calls.append(call)
    return word, calls


def _transport(word, image):
    return sum(1 << new for old, new in image.items() if word >> old & 1)


def _record(before, after, calls, apparatus, law):
    initial = _read(before, apparatus["keeper"])
    terminal = _read(after, apparatus["keeper"])
    u = _read(before, (apparatus["paid"],))
    assert _read(after, (apparatus["paid"],)) == u
    assert _legal(before, apparatus["rows"][:2], law) and _legal(after, apparatus["rows"][:2], law)
    assert all(_read(before, names) == _read(after, names) for names in (apparatus["focal"],))
    return {"paid_value_physically_read_in_P": u, "before_old_word": before, "after_old_word": after,
            "actual_keeper_before": f"{initial:04b}", "actual_keeper_terminal": f"{terminal:04b}",
            "actual_initial_readiness": initial == READY, "physical_keeper_changed": initial != terminal,
            "marked_terminal_class": _keeper_class(terminal), "two_scheduled_calls": calls}


def _histories(law, turn, factors):
    focal = turn["focal"]["fresh_names"]
    apparatus = _device(turn["reached"], PAID, focal, SHARED)
    unborn = _device(FOUNDING, PAID, (), SHARED)
    assert apparatus["supported"] == unborn["supported"] == (True, True)
    assert set(apparatus["keeper"]).isdisjoint((PAID, *focal))
    assert all(b["paid_names"][0] not in SHARED for b in turn["births"])
    image = {n: max(apparatus["ownership"]) - n for n in apparatus["ownership"]}
    translated_rows = tuple(tuple(image[n] for n in names) for names in turn["reached"])
    translated = _device(translated_rows, image[PAID], tuple(image[n] for n in focal), tuple(image[n] for n in SHARED))
    assert all(tuple(apparatus["ownership"][s]) == translated["ownership"][t] for s, t in image.items())
    split_name = 1 + max(apparatus["ownership"])
    split_rows = tuple(tuple(split_name if h == 1 and n == SHARED[2] else n for n in names)
                       for h, names in enumerate(turn["reached"]))
    split = _device(split_rows, PAID, focal, SHARED)
    assert split["supported"] == (False, False)
    assert apparatus["ownership"][SHARED[2]] == (0, 1)
    assert split["ownership"][SHARED[2]] == (0,) and split["ownership"][split_name] == (1,)
    assert tuple(sorted(set(split["rows"][0]) & set(split["rows"][1]))) == SHARED[:2]

    schedules = {
        "no_offers": ((False, False), True),
        "zero_guard_only": ((True, False), True),
        "one_guard_only": ((False, True), True),
        "both_guarded_offers": ((True, True), True),
        "disconnected_offers": ((True, True), False),
    }
    by_mode = {mode: [] for mode in schedules}
    for mode in ("split_shared_name", "transported_names", "reversed_scorer_labels"):
        by_mode[mode] = []
    repeat = []
    source = {old for old, _, _ in factors}
    for old, choices, _count in factors:
        for mode, (agenda, connection) in schedules.items():
            after, trial = _apply(old, apparatus, agenda, connection)
            assert after in source
            # Every paid value and all choices in its old-conditioned fresh product are still the same.
            assert all(_read(old, b["paid_names"]) == _read(after, b["paid_names"]) for b in turn["births"])
            assert all(all(_allowed((_read(after, birth["paid_names"]) << len(birth["fresh_names"])) | index,
                                    len(turn["reached"][birth["holder"]]), law) for index in support)
                       for birth, support in zip(turn["births"], choices, strict=True))
            record = _record(old, after, trial, apparatus, law)
            by_mode[mode].append(record)
        primary = by_mode["both_guarded_offers"][-1]
        after = primary["after_old_word"]
        before_birth, prior_calls = _apply(old, unborn, (True, True))
        assert before_birth == after and prior_calls == primary["two_scheduled_calls"]
        returned, inverse_calls = _apply(after, apparatus, (True, True), reverse=True)
        reoffered, repeated_calls = _apply(returned, apparatus, (True, True))
        blind_reapply, blind_calls = _apply(after, apparatus, (True, True))
        assert returned == old == blind_reapply and reoffered == after
        repeat.append({"initial_old_word": old, "first_delivery_old_word": after,
                       "first_and_idle_reread": (primary["actual_keeper_terminal"],) * 2,
                       "inverse": inverse_calls, "returned_old_word": returned,
                       "keeper_after_inverse": f"{_read(returned, apparatus['keeper']):04b}",
                       "new_delivery": repeated_calls, "new_delivery_old_word": reoffered,
                       "blind_reapplication": blind_calls, "blind_reapplication_old_word": blind_reapply,
                       "retains_same_fresh_completion_and_actual_u": True})

        when_split = _put_back(old, SHARED[2], split_name)
        cut_after, cut_calls = _apply(when_split, split, (True, True))
        assert cut_after == when_split and not any(o["enabled"] for o in cut_calls)
        detached = _record(when_split, cut_after, cut_calls, split, law)
        assert detached["actual_keeper_before"] == primary["actual_keeper_before"]
        by_mode["split_shared_name"].append(detached)

        recoded = _transport(old, image)
        recoded_after, recoded_calls = _apply(recoded, translated, (True, True))
        assert recoded_after == _transport(after, image)
        renamed = _record(recoded, recoded_after, recoded_calls, translated, law)
        for k in ("paid_value_physically_read_in_P", "actual_keeper_before", "actual_keeper_terminal", "physical_keeper_changed"):
            assert renamed[k] == primary[k]
        by_mode["transported_names"].append(renamed)
        by_mode["reversed_scorer_labels"].append(primary)

    for mode, trials in by_mode.items():
        assert len({r["before_old_word"] for r in trials}) == len({r["after_old_word"] for r in trials}) == len(source), mode
    for record in by_mode["both_guarded_offers"]:
        if record["actual_initial_readiness"]:
            u = record["paid_value_physically_read_in_P"]
            assert record["physical_keeper_changed"] and int(record["actual_keeper_terminal"], 2) == (ZERO_ANSWER, ONE_ANSWER)[u]
    devices = {
        "original_named": apparatus,
        "transported_names": {"physical_name_image": image, "apparatus": translated},
        "split_shared_name": {"still_distinct_P_and_K_names": (SHARED[2], split_name),
                              "matched_input_lift_copies_the_old_value_at_the_split_only": True,
                              "apparatus": split,
                              "lawful_matched_physical_source_and_no_supported_offer": True},
    }
    return by_mode, repeat, devices


def _denominators(factors):
    N = sum(n for _, _, n in factors)
    M = len(factors)
    result = {
        "uniform_complete": [Q(n, N) for _, _, n in factors],
        "chronological": [Q(1, M) for _ in factors],
    }
    for probabilities in result.values():
        assert sum(probabilities) == 1
    return N, M, result


def _category(value, reverse):
    kind = _keeper_class(value)
    if reverse and kind in ("zero", "one"):
        return "one" if kind == "zero" else "zero"
    return kind


def _announcements(trial, reverse):
    kind = _category(int(trial["actual_keeper_terminal"], 2), reverse)
    ready = trial["actual_initial_readiness"]
    changed = trial["physical_keeper_changed"]
    paid = trial["paid_value_physically_read_in_P"]
    answer = {"zero": 0, "one": 1}.get(kind)
    # The supplied readiness instrument reads this actual original K word
    # before either offer. P's instructions never consult its record.
    observed_ready = trial["actual_keeper_before"] == "1100"
    assert observed_ready == ready
    before_after = kind if ready and changed and answer == paid else "refused"
    return (kind, kind if observed_ready else "refused", before_after)


def _confusion(factors, trials, masses):
    cells = {(u, ready, name, changed): [] for u, ready, name, changed in product(
        (0, 1), (False, True), KINDS, (False, True))}
    by_terminal = defaultdict(list)
    for i, trial in enumerate(trials):
        u, r, c, changed = (trial[k] for k in (
            "paid_value_physically_read_in_P", "actual_initial_readiness", "marked_terminal_class", "physical_keeper_changed"))
        cells[u, r, c, changed].append(i)
        by_terminal[trial["actual_keeper_terminal"]].append(i)

    def packet(indices):
        return {"full_word_count": sum(factors[i][2] for i in indices),
                "founding_word_count": len(indices),
                **{weight: str(sum((wealth[i] for i in indices), Q(0))) for weight, wealth in masses.items()}}

    all_cells = [{"true_u_at_P": u, "initially_ready": ready, "terminal_word_class": terminal, "changed_at_K": changed, **packet(indices)}
                 for (u, ready, terminal, changed), indices in cells.items()]
    assert sum(p["full_word_count"] for p in all_cells) == sum(n for _, _, n in factors)
    for weight in masses:
        assert sum(Q(p[weight]) for p in all_cells) == 1
    terminal_words = {code: {str(u): packet([i for i in by_terminal.get(code, ()) if trials[i]["paid_value_physically_read_in_P"] == u])
                             for u in (0, 1)}
                      for code in (f"{k:04b}" for k in range(16))}
    return all_cells, terminal_words


def _scalar(trials, readouts, masses, terminal_words, paid_name):
    result = {}
    for name, weights in masses.items():
        ready = sum(w for trial, w in zip(trials, weights, strict=True) if trial["actual_initial_readiness"])
        paid_pool = {u: sum(w for trial, w in zip(trials, weights, strict=True)
                           if trial["paid_value_physically_read_in_P"] == u) for u in (0, 1)}
        choices = {}
        for col, policy in enumerate(VIEWS):
            groups = {port: Q(0) for port in (*KINDS, "refused")}
            by_u = {u: {port: Q(0) for port in groups} for u in (0, 1)}
            ready_by_u = {u: {port: Q(0) for port in groups} for u in (0, 1)}
            accepted = {"right": Q(0), "wrong": Q(0), "idle_answer": Q(0), "false_answer_without_initial_ready": Q(0),
                        "right_and_ready": Q(0), "wrong_and_ready": Q(0), "answer_on_ready": Q(0)}
            for i, (view, w) in enumerate(zip(readouts, weights, strict=True)):
                terminal = view[col]
                groups[terminal] += w
                actual_u = trials[i]["paid_value_physically_read_in_P"]
                by_u[actual_u][terminal] += w
                if trials[i]["actual_initial_readiness"]:
                    ready_by_u[actual_u][terminal] += w
                if terminal in ("zero", "one"):
                    right = (terminal == "one") == bool(actual_u)
                    accepted["right" if right else "wrong"] += w
                    if not trials[i]["physical_keeper_changed"]:
                        accepted["idle_answer"] += w
                    if not trials[i]["actual_initial_readiness"]:
                        accepted["false_answer_without_initial_ready"] += w
                    if trials[i]["actual_initial_readiness"]:
                        accepted["right_and_ready" if right else "wrong_and_ready"] += w
                        accepted["answer_on_ready"] += w
            assert sum(groups.values()) == 1 and accepted["right"] + accepted["wrong"] == groups["zero"] + groups["one"]
            positive = groups["zero"] + groups["one"]
            conditioning = {}
            for u, ports in ready_by_u.items():
                cohort = sum(ports.values())
                conditioning[str(u)] = {
                    "original_launch_probability_of_this_ready_truth": str(cohort),
                    "conditional_on_actual_ready_and_this_u": {p: str(w / cohort) if cohort else None for p, w in ports.items()},
                }
            assert sum(Q(p["original_launch_probability_of_this_ready_truth"]) for p in conditioning.values()) == ready
            choices[policy] = {
                "original_launch_mass_by_port": {p: str(w) for p, w in groups.items()},
                "original_launch_mass_by_actual_u_and_port": {str(u): {p: str(w) for p, w in ports.items()} for u, ports in by_u.items()},
                "prices_conditioned_on_ready_by_actual_u": conditioning,
                "right_wrong_and_false_indication_per_original_launch": {p: str(w) for p, w in accepted.items()},
                "correct_given_an_answer": str(accepted["right"] / positive) if positive else None,
                "answer_given_actual_ready": str(accepted["answer_on_ready"] / ready) if ready else None,
                "correct_given_actual_ready": str(accepted["right_and_ready"] / ready) if ready else None,
            }
        per_word = [(Q(view["0"][name]), Q(view["1"][name])) for view in terminal_words.values()]
        assert sum(sum(values) for values in per_word) == 1
        supported_unambiguous = sum(a + b for a, b in per_word if a + b and not a * b)
        result[name] = {
            "physical_P_reader": {"correct_per_original_launch": "1", "actual_paid_name_read": paid_name,
                                 "u_probability_by_value": {str(k): str(v) for k, v in paid_pool.items()},
                                 "best_constant_guess": str(max(paid_pool.values()))},
            "terminal_K_best_guesser_over_all_lawful_words": str(sum(max(a, b) for a, b in per_word)),
            "terminal_K_best_zero_error_coverage_over_all_lawful_words": str(supported_unambiguous),
            "ready_event_probability_on_original_launches": str(ready),
            "scored_policies": choices,
        }
    return result


def _projectors(gram):
    by_setting = []
    for setting in range(8):
        z_slots = 7 ^ setting
        table = []
        for answer in range(8):
            supports = [i for i in range(8) if i & z_slots == answer & z_slots]
            numerator = sum((-1) ** ((x ^ y) & setting & answer).bit_count() * gram[x][y]
                            for x in supports for y in supports)
            table.append(Q(numerator, 1 << setting.bit_count()))
        assert sum(table) == 1 and min(table) >= 0
        moments = [sum((-1) ** (q & z_slots & x).bit_count() * gram[x][x ^ (q & setting)]
                       for x in range(8)) for q in range(8)]
        assert all(sum((-1) ** (answer & q).bit_count() * m for q, m in enumerate(moments)) == 8 * value
                   for answer, value in enumerate(table))
        by_setting.append(table)
    for read in range(1, 7):
        seen = {}
        for s, row in enumerate(by_setting):
            marginal = tuple(sum(p for a, p in enumerate(row) if a & read == outcome)
                             for outcome in range(8) if outcome & read == outcome)
            assert seen.setdefault(s & read, marginal) == marginal
    return by_setting


def _I(table, u):
    value = sum(table[7][a] for a in (3, 5, 6, 7)) - table[0][7 * u]
    value -= sum(table[s][a] for s in (1, 2, 4) for a in range(8)
                 if s & a and (7 ^ s) & (a ^ (7 * u)))
    return value


class _FocalStates:
    def __init__(self):
        self.keys = {}
        self.data = []

    def matrix(self, gram):
        if gram not in self.keys:
            i = len(self.data)
            self.keys[gram] = i
            assert sum(gram[i][i] for i in range(8)) == 1
            assert all(gram[i][j] == gram[j][i] for i in range(8) for j in range(8))
            theory = _projectors(gram)
            self.data.append({
                "conditional_gram": [[str(value) for value in line] for line in gram],
                "conditional_probabilities": [[str(value) for value in line] for line in theory],
                "I_c": {str(u): str(_I(theory, u)) for u in (0, 1)},
            })
        return self.keys[gram]

    def preparations(self, positive):
        pointer = tuple(_bits(x, 3)[0] for x in range(8))
        # The copied bit stays orthogonal when unobserved. Applying the same XOR to
        # the record while the focal value is still present returns it to zero.
        returned_pointer = tuple(bit ^ _bits(x, 3)[0] for x, bit in enumerate(pointer))
        assert returned_pointer == (0,) * 8
        diagonal = tuple(tuple(p if x == y else Q(0) for y, p in enumerate(row)) for x, row in enumerate(positive))
        tagged = tuple(tuple(p if pointer[x] == pointer[y] else Q(0) for y, p in enumerate(row))
                       for x, row in enumerate(positive))
        restored = tuple(tuple(p if returned_pointer[x] == returned_pointer[y] else Q(0) for y, p in enumerate(row))
                         for x, row in enumerate(positive))
        assert restored == positive
        return {name: self.matrix(g) for name, g in (
            ("positive", positive), ("ordinary_diagonal", diagonal), ("first_focal_name_copied_and_held", tagged),
            ("same_copy_coherently_returned", restored))}

    def packet(self, indices, support, probabilities, factors, focal_idx, ready_mass):
        trace = sum((probabilities[i] for i in indices), Q(0))
        count = sum(factors[i][2] for i in indices)
        states = None
        if trace:
            coefficients = defaultdict(Q)
            for i in indices:
                # Each compatible unchanged exterior produces the same positive dyad.
                # Conditioning on its old word leaves the focal words equiprobable.
                coefficients[support[i]] += probabilities[i] / len(support[i])
                assert len(factors[i][1][focal_idx]) == len(support[i])
            positive = tuple(tuple(sum((amp for words, amp in coefficients.items() if x in words and y in words), Q(0)) / trace
                                   for y in range(8)) for x in range(8))
            states = self.preparations(positive)
        return {"original_launch_probability": str(trace), "complete_word_count": count, "states": states,
                "conditioned_on_supplied_ready_filter": str(trace / ready_mass) if ready_mass else None}


def _focal_branches(library, factors, focal_idx, trials, readouts, masses):
    groups = {}
    ready_groups = {}
    support = tuple(h[focal_idx] for _, h, _ in factors)
    for col, view in enumerate(VIEWS):
        groups[view] = {label: [i for i, r in enumerate(readouts) if r[col] == label] for label in (*KINDS, "refused")}
        ready_groups[view] = {label: [i for i in indices if trials[i]["actual_initial_readiness"]]
                              for label, indices in groups[view].items()}
    modes = {}
    for mode, weights in masses.items():
        ready_mass = sum(w for w, trial in zip(weights, trials, strict=True) if trial["actual_initial_readiness"])
        all_views = {}
        for view, ports in groups.items():
            ledger = {}
            for terminal, indices in ports.items():
                entry = library.packet(indices, support, weights, factors, focal_idx, None)
                ready_only = library.packet(ready_groups[view][terminal], support, weights, factors, focal_idx, ready_mass)
                entry["initially_ready_component"] = ready_only
                if terminal in ("zero", "one"):
                    entry["actual_truth_components"] = {
                        str(u): library.packet([i for i in indices if trials[i]["paid_value_physically_read_in_P"] == u],
                                               support, weights, factors, focal_idx, None) for u in (0, 1)}
                    assert sum(Q(track["original_launch_probability"]) for track in entry["actual_truth_components"].values()) == Q(
                        entry["original_launch_probability"])
                ledger[terminal] = entry
            assert sum(Q(p["original_launch_probability"]) for p in ledger.values()) == 1
            assert sum(Q(p["initially_ready_component"]["conditioned_on_supplied_ready_filter"]) for p in ledger.values()) == 1
            all_views[view] = ledger
        modes[mode] = all_views
    return modes


def _careful_prices(law, masses, scenarios, library):
    active = scenarios["both_guarded_offers"]
    for weighting in WEIGHTS:
        ready = active["readout"][weighting]["ready_event_probability_on_original_launches"]
        rates = active["readout"][weighting]["scored_policies"]
        terminal = rates["terminal_only"]
        actual = rates["supplied_ready_then_terminal"]
        archival = rates["before_after_audit"]
        p = Q(ready)
        assert p and p < 1
        outcomes = active["focal_ports"][weighting]
        for u, side in enumerate(("zero", "one")):
            formed = outcomes["supplied_ready_then_terminal"][side]
            assert 0 < Q(formed["original_launch_probability"]) == p / 2
            good = formed["states"]
            quantum = library.data[good["positive"]]
            assert good["positive"] == good["same_copy_coherently_returned"]
            assert len({good["positive"], good["first_focal_name_copied_and_held"], good["ordinary_diagonal"]}) == 3
            support = _extensions(u, 1, 3, law)
            expect_gram = [[str(Q(int(x in support and y in support), len(support))) for y in range(8)] for x in range(8)]
            assert quantum["conditional_gram"] == expect_gram
            assert outcomes["before_after_audit"][side]["states"] == good
            noisy = outcomes["terminal_only"][side]
            assert Q(noisy["original_launch_probability"]) == p
            assert all(Q(truth["original_launch_probability"]) == p / 2 for truth in noisy["actual_truth_components"].values())
            assert noisy["states"]["positive"] != good["positive"]
        assert terminal["correct_given_an_answer"] == "1/2" and terminal["answer_given_actual_ready"] == "1"
        assert rates["terminal_only"]["right_wrong_and_false_indication_per_original_launch"]["false_answer_without_initial_ready"] == ready
        assert actual["correct_given_actual_ready"] == "1" and archival["correct_given_actual_ready"] == "1"
        assert rates["supplied_ready_then_terminal"]["original_launch_mass_by_port"]["refused"] == str(1 - p)
        for mode in ("no_offers", "disconnected_offers", "split_shared_name", "reversed_scorer_labels"):
            got = scenarios[mode]["readout"][weighting]["scored_policies"]["supplied_ready_then_terminal"]
            assert got["correct_given_actual_ready"] == "0"
        for mode in ("zero_guard_only", "one_guard_only"):
            got = scenarios[mode]["readout"][weighting]["scored_policies"]["supplied_ready_then_terminal"]
            assert got["correct_given_actual_ready"] == "1/2"
        assert scenarios["no_offers"]["readout"][weighting] == scenarios["disconnected_offers"]["readout"][weighting]
        assert scenarios["no_offers"]["readout"][weighting] == scenarios["split_shared_name"]["readout"][weighting]
        assert active["focal_ports"][weighting] == scenarios["transported_names"]["focal_ports"][weighting]
    assert all(q > 0 for probabilities in masses.values() for q in probabilities)


def _case(law, library):
    founding, rejected = _founding(law)
    turn = _turn(law, founding)
    if turn["status"] != "funded":
        return {"status": "refused", "actual_first_turn": turn, "founding_allowed_words": founding,
                "founding_candidates_refused": rejected, "successful_ports": None}
    factors, focal_idx, projections = _funded_words(law, turn, founding)
    N, M, masses = _denominators(factors)
    histories, renewal, apparatus = _histories(law, turn, factors)
    scenarios = {}
    for label, trials in histories.items():
        marks_reversed = label == "reversed_scorer_labels"
        readouts = [_announcements(row, marks_reversed) for row in trials]
        confusion, by_word = _confusion(factors, trials, masses)
        active_name = apparatus["transported_names"]["apparatus"]["paid"] if label == "transported_names" else PAID
        scenarios[label] = {
            "all_terminal_confusion_cells": confusion, "terminal_words_by_truth": by_word,
            "readout": _scalar(trials, readouts, masses, by_word, active_name),
            "focal_ports": _focal_branches(library, factors, focal_idx, trials, readouts, masses),
            "per_founding_word": tuple({
                **row,
                "same_completion_product_index": i,
                "recorded_before_after_audit_answer": grades[2],
                "supplied_readiness_measurement_at_original_K": "ready" if row["actual_initial_readiness"] else "nonready",
                "supplied_ready_then_terminal_port": grades[1],
                "scorer_terminal_read": grades[0],
            } for i, (row, grades) in enumerate(zip(trials, readouts, strict=True))),
        }
    _careful_prices(law, masses, scenarios, library)
    n = Counter(c for _old, _supports, c in factors)
    transport_laws = tuple(projections[h]["names"] == names for h, names in enumerate(turn["reached"]))
    assert all(transport_laws)
    # Ordinary funding does not depend on an old valuation. It can be observed on the
    # same cut for all old words, while the actual K-ready predicate has nontrivial support.
    base = scenarios["both_guarded_offers"]
    physical_ready = {w: base["readout"][w]["ready_event_probability_on_original_launches"] for w in WEIGHTS}
    return {
        "status": "two_separate_outputs_with_supplied_offers_and_ready_read",
        "actual_first_turn": turn, "whole_projections": projections, "devices": apparatus,
        "complete_population": N, "chronological_eligible_founding_population": M,
        "founding_candidate_words_examined": 256, "founding_candidate_words_refused_with_failed_holdings": rejected,
        "lawful_founding_words_without_an_extension": (),
        "ordinary_completion_multiplicity_histogram": dict(sorted(n.items())),
        "completion_factors": tuple({
            "old_word": old, "compatible_fresh_projected_words_each_child_in_birth_order": choices,
            "complete_count": count, "uniform_complete_each_word": str(Q(1, N)),
            "chronological_each_word": str(Q(1, M * count)),
        } for old, choices, count in factors),
        "scenarios": scenarios, "exact_inverse_reset_repeat_and_idle_reread": renewal,
        "prior_to_birth_same_supported_actuator_and_same_old_word_response": True,
        "ready_precedes_birth_and_can_be_measured_by_the_supplied_instrument": {
            "ready_probability": physical_ready, "ordinary_birth_receipt_per_original_launch": "1",
            "ordinary_funding_receipt_alone_reads_the_same_ambiguous_terminal_ports_as_terminal_only": True,
            "native_K_readiness_signal_received": False, "native_K_value_invocation_observed": False,
            "supplier_of_the_offers": "External scheduler",
            "recipient_of_supplied_readiness_record": "The same K reader that receives the full terminal word",
            "supplied_readiness_record_controls_either_P_offer": False,
            "supplied_instrument_scope": "A separate ordinary K measurement resolves the fixed full-word predicate before either offer, then retains its real output until the terminal read.",
        },
    }


def _digests():
    assert sha256(PRE.read_bytes()).hexdigest() == PRE_HASH
    _, _, ancestry = _ancestors()
    paths = (Path(__file__).resolve(), PRE, HERE / "contract.json", ENGINE, END, ROUTES, *ancestry,
             *sorted((ROOT / "tools/knotlab").glob("*.py")))
    canonical, public = {}, {}
    for path in paths:
        key = str(path.relative_to(ROOT))
        data = path.read_bytes()
        if key in ("tools/knotlab/__init__.py", "tools/knotlab/cli.py", "tools/knotlab/competition.py", "tools/knotlab/knots.py"):
            private = data if b"docs/KNOT_INTUITION.md" in data else data.replace(b"INTUITIONS.md", b"docs/KNOT_INTUITION.md")
            mirror = private.replace(b"docs/KNOT_INTUITION.md", b"INTUITIONS.md")
            canonical[key] = sha256(private).hexdigest()
            public[key] = sha256(mirror).hexdigest()
        else:
            canonical[key] = sha256(data).hexdigest()
    return canonical, public


def run():
    """Return the compact, complete, JSON-ready independent control replay."""
    library = _FocalStates()
    laws = {law: _case(law, library) for law in LAWS}
    sources, mirrors = _digests()
    return {
        "control": "D(3,4,1)",
        "recipe_shared_private_P_private_K": RECIPE,
        "source_sha256": sources, "public_source_variants": mirrors,
        "laws": laws, "conditional_focal_state_library": library.data,
        "factorization": "Use the literal old integer and one word from every listed child fresh factor, in its named birth order. The full stage image keeps those fresh values and replaces only the old integer according to the actual history. Initial and transported words use integer bit n for the value of physical name n.",
        "rate_and_table_order": {
            "uniform_complete": "Equal positive amplitudes on the complete lawful words of this first cut.",
            "chronological": "Equal old-word launch probability, then equal squared amplitude on the actual fresh completions of that old word. The external history retains the old word orthogonally.",
            "focal_words_and_outcomes": "Lexicographic in the registered focal names, transported in that order. Plus is 0, ordinary Z is 0 and changed X is 1.",
            "joint_settings_and_answers": "For the original-launch joint probability, multiply the conditional table cell by the branch probability and divide by eight for the independent fair settings.",
            "retained_exterior": "All unfocused physical registers, including the final original word, and every actually recorded outcome are traced. Complete-source transitions are injective old-word permutations. The supplied focal-bit copy has an orthogonal record until physically returned by the same controlled XOR.",
        },
    }


def _archive(data):
    raw = (json.dumps(data, sort_keys=True, separators=(",", ":")) + "\n").encode()
    buf = BytesIO()
    with gzip.GzipFile(filename="", fileobj=buf, mode="wb", compresslevel=9, mtime=0) as stream:
        stream.write(raw)
    return buf.getvalue()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_mutually_exclusive_group(required=True)
    commands.add_argument("--write", action="store_true")
    commands.add_argument("--check", action="store_true")
    args = parser.parse_args()
    data = run()
    new = _archive(data)
    if args.write:
        OUTPUT.parent.mkdir(parents=True, exist_ok=True)
        OUTPUT.write_bytes(new)
    else:
        assert OUTPUT.read_bytes() == new, "writer control archive differs from exact replay"
    print(f"{'wrote' if args.write else 'verified'} {OUTPUT.name} {len(new)} bytes SHA-256 {sha256(new).hexdigest()}")
    for law, case in data["laws"].items():
        if not case.get("scenarios"):
            print(law, case["status"])
            continue
        for weighting in WEIGHTS:
            mode = case["scenarios"]["both_guarded_offers"]["readout"][weighting]
            filtered = mode["scored_policies"]["supplied_ready_then_terminal"]["original_launch_mass_by_port"]
            print(law, weighting, "complete", case["complete_population"], "ready", mode["ready_event_probability_on_original_launches"],
                  "zero", filtered["zero"], "one", filtered["one"])


if __name__ == "__main__":
    main()
