"""Ordinary word, offered-history and physical keeper checks for B287."""

from collections import Counter
from functools import lru_cache
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import permutations, product
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ERASURE = ROOT / "research/ERASURE-AND-CLOSING-SIGNS-20261121-001A"
MOTION = ROOT / "experiments/MOTION-LAW-20261119-001/MOTION-LAW-20261119-001-E001_rules"
HISTORIES = ROOT / "experiments/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A/SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A-E001_sign_records/physical_histories.py"
LAWS = ("parity", "nae")
TERNARY_CODE = {"a": "101", "b": "011", "c": "110"}
TERNARY_EXCHANGES = {"P": (0, 1), "Q": (1, 2), "R": (0, 2)}
AUXILIARY_CODE = {"a": (1, 0), "b": (1, 1), "c": (0, 0), "d": (0, 1)}


@lru_cache(maxsize=None)
def _load(name, path):
    spec = spec_from_file_location(name, path)
    module = module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def _routes():
    return _load("b287_prior_ordinary_routes", ERASURE / "ordinary_routes.py")


def _original_permutations():
    if str(MOTION) not in sys.path:
        sys.path.insert(0, str(MOTION))
    return _load("b287_original_permutations", MOTION / "permutation_controls.py")


def _positions(word):
    return tuple(i for i in range(word.bit_length()) if word >> i & 1)


def _mask(marks):
    return sum(1 << m for m in marks)


def _has(value, mark):
    return value >> mark & 1


def _allowed(word, row_masks, law):
    counts = [(word & support).bit_count() for support in row_masks]
    if law == "parity":
        return all(n % 2 == 0 for n in counts)
    return all(0 < n < support.bit_count() for n, support in zip(counts, row_masks, strict=True))


def _written(display):
    return _mask(i for i, value in enumerate(display) if value == "1")


def _letters(word):
    return "".join(str(_has(word, i)) for i in range(3))


def _word_swap(word, pair):
    a, b = pair
    return word ^ _mask(pair) if _has(word, a) != _has(word, b) else word


def _first_difference(first, second, project):
    for i, (left, right) in enumerate(zip(first, second), start=1):
        a, b = project(left), project(right)
        if a != b:
            return {"slot": i, "left": a, "right": b}
    if len(first) != len(second):
        return {"slot": min(len(first), len(second)) + 1,
                "left": project(first[len(second)]) if len(first) > len(second) else None,
                "right": project(second[len(first)]) if len(second) > len(first) else None}
    return None


def _words_history(first, second):
    return {"offered_name": _first_difference(first, second, lambda s: s["offer"]),
            "changed_flag": _first_difference(first, second, lambda s: s["changed"]),
            "actual_changed_names": _first_difference(first, second, lambda s: s["toggled"]),
            "post_word": _first_difference(first, second, lambda s: s["after"])}


def _ternary_history(word, program, permutation=(0, 1, 2)):
    steps = []
    for operation in program:
        pair = tuple(permutation[i] for i in TERNARY_EXCHANGES[operation])
        after = _word_swap(word, pair)
        steps.append({"offer": operation, "pair": pair, "before": word, "after": after,
                      "physical_before": _letters(word), "physical_after": _letters(after),
                      "enabled": True, "changed": word != after, "toggled": _positions(word ^ after)})
        word = after
    return word, steps


def _ternary_controls():
    routes = _routes()
    canonical = routes._canonical_ternaries()
    studies = {}
    programs = ("P", "Q", "R", "PP", "QQ", "RR", "PQP", "QPQ", "RPP")
    for law in LAWS:
        words = [w for w in range(8) if _allowed(w, (7,), law)]
        assert {_letters(w) for w in words} == set(canonical[law]["allowed"])
        rows = []
        for w in words:
            histories = {name: _ternary_history(w, name) for name in programs}
            assert all(new.bit_count() == w.bit_count() and new in words for new, _ in histories.values())
            assert all(histories[op][0] == w for op in ("PP", "QQ", "RR"))
            assert len({histories[op][0] for op in ("R", "PQP", "QPQ", "RPP")}) == 1
            rows.append({"initial": _letters(w), "initial_mask": w, "occupancy": w.bit_count(),
                         "programs": {name: {"last_word": _letters(new), "steps": h} for name, (new,h) in histories.items()},
                         "first_history_disagreement": {
                             name: _words_history(histories["R"][1], histories[name][1]) for name in ("PQP", "QPQ")},
                         "padded_R_vs_PQP": _words_history(histories["RPP"][1], histories["PQP"][1])})
        namings = []
        for rename in permutations(range(3)):
            def moved(word):
                return _mask(rename[i] for i in _positions(word))
            checked = []
            for w, name in product(words, programs):
                new, old_steps = _ternary_history(w, name)
                renamed_new, changed_steps = _ternary_history(moved(w), name, rename)
                assert renamed_new == moved(new)
                assert [(moved(s["before"]), moved(s["after"]), s["enabled"], s["changed"]) for s in old_steps] == [
                    (s["before"], s["after"], s["enabled"], s["changed"]) for s in changed_steps]
                checked.append({"program": name, "original": w, "transported_input": moved(w), "transported_output": renamed_new})
            namings.append({"marks": rename, "checks": checked})
        studies[law] = {"valid_rows": rows, "refused_words": [_letters(w) for w in range(8) if w not in words],
                        "occupancy_classes": {n: [_letters(w) for w in words if w.bit_count() == n]
                                              for n in sorted({w.bit_count() for w in words})},
                        "all_six_namings": namings, "canonical": canonical[law]}
    return {"chosen_codes": TERNARY_CODE, "direct_exchanges": TERNARY_EXCHANGES, "laws": studies,
            "padding": {"short": "R", "padded": "RPP", "match": "PQP", "primitive_type": "complete named exchange",
                        "R_padded_finishes_with_full_P_inverse_pair": True},
            "invariant": "The complete name permutations conserve occupancy. Reading or bridging coherence between classes needs a separate operation."}


def _threshold_fixture(width, offset=0):
    return ((offset, offset+1, offset+2), (offset, *range(offset+3, offset+width+2)))


def _threshold_trace(state, pools, sequence, original):
    steps = []
    for threshold in sequence:
        selected = [pair for arities, pair in pools if arities & threshold]
        fired = [pair for pair in selected if len(state.intersection(pair)) == 1]
        after = original.apply(state, threshold, pools)
        changes = set().union(*(set(pair) for pair in fired))
        assert state ^ after == changes
        steps.append({"offer": sorted(threshold), "eligible_pairs": selected, "fired_pairs": fired,
                      "before": _mask(state), "after": _mask(after), "changed": bool(changes),
                      "toggled": sorted(changes)})
        state = after
    return _mask(state), steps


def _threshold_source(name, holdings, original):
    names = sorted({m for row in holdings for m in row})
    support = tuple(map(_mask, holdings))
    native = original.local_pools(holdings)
    k4, k5, both, inert = {4}, {5}, {4, 5}, {6}
    programs = {"4": (k4,), "5": (k5,), "union": (both,), "4_then_5": (k4, k5), "5_then_4": (k5, k4),
                "4_then_4": (k4, k4), "5_then_5": (k5, k5), "union_twice": (both, both),
                "4_inert_5": (k4, inert, k5), "5_inert_4": (k5, inert, k4), "inert": (inert,)}
    raw = tuple(_mask(m for m, include in zip(names, bits, strict=True) if include)
                for bits in product((0, 1), repeat=len(names)))
    laws = {}
    for law in LAWS:
        rows, refusals, denominator = [], [], 1 << len(names)
        activities = Counter()
        schedule_witnesses = {}
        for w in sorted(raw):
            if not _allowed(w, support, law):
                refusals.append(w)
                continue
            positions = frozenset(_positions(w))
            traces = {key: _threshold_trace(positions, native, seq, original) for key, seq in programs.items()}
            assert all(_allowed(endpoint, support, law) and all(_allowed(step["after"], support, law) for step in moves)
                       for endpoint, moves in traces.values())
            assert set(traces[key][0] for key in ("4_then_4", "5_then_5", "union_twice", "inert")) == {w}
            assert len({traces[key][0] for key in ("union", "4_then_5", "5_then_4", "4_inert_5", "5_inert_4")}) == 1
            count = len(traces["union"][1][0]["fired_pairs"])
            activities[count] += 1
            if count not in schedule_witnesses:
                schedule_witnesses[count] = {"word": w, "one_offer_vs_separate": _words_history(traces["union"][1], traces["4_then_5"][1]),
                                             "separate_orders": _words_history(traces["4_then_5"][1], traces["5_then_4"][1])}
            rows.append({"word": w, "firing_pool_count": count, "programs": {
                key: {"endpoint": endpoint, "steps": moves} for key,(endpoint, moves) in traces.items()}})
        laws[law] = {"all_raw_inputs": denominator, "lawful_inputs": len(rows), "rejected_inputs": refusals,
                     "coexisting_firing_pool_counts": dict(sorted(activities.items())), "records": rows,
                     "history_disagreement_example_by_firing_count": schedule_witnesses,
                     "offers_by_program": {name: len(seq) for name,seq in programs.items()},
                     "all_total_maps_commute_and_union_equals_both_orders": True,
                     "native_complete_involutions_checked": ["4", "5", "union"]}
    return {"scope": name, "holdings": holdings, "pools": [{"arities": sorted(s), "loose_marks": pool} for s,pool in native],
            "laws": laws, "schedules_marked_externally": True, "actual_native_birth_clock_or_payer_in_these_programs": False}


def _threshold_checks():
    original = _original_permutations()
    h4, h5 = _threshold_fixture(4), _threshold_fixture(5)
    tagged = {"4": _threshold_source("only the width-four source is present", h4, original),
              "5": _threshold_source("only the width-five source is present", h5, original)}
    union = _threshold_source("both labelled pools actually coexist", h4+_threshold_fixture(5, 6), original)
    for law, row in union["laws"].items():
        assert row["lawful_inputs"] == tagged["4"]["laws"][law]["lawful_inputs"]*tagged["5"]["laws"][law]["lawful_inputs"]
        assert set(row["coexisting_firing_pool_counts"]) == {0, 1, 2}
    return {"tagged_choice": tagged, "physical_disjoint_union": union,
            "independence": "An input bearing one fixture tag has only one pool. A simultaneous union includes both pools, even when both fire."}


def basis_words(reverse=False, data=245):
    """Full physical words for the four admitted auxiliary preparations."""
    routes = _routes()
    return {name: routes.encode(data, q=q, s=s, reverse=reverse) for name, (q,s) in AUXILIARY_CODE.items()}


def _primitive_spec(name, reverse):
    routes = _routes()
    target, guarded, required = {
        "P": (routes.S, routes.Q, 1), "Q": (routes.Q, routes.S, 0),
        "J": (routes.Q, routes.S, 1), "J_inverse": (routes.Q, routes.S, 1),
        "R_core": (routes.S, routes.Q, 0), "L": (routes.S, routes.Q, 0),
        "transfer_s_to_q": (routes.Q, routes.S, 1),
    }[name]
    return routes._places(routes.REGISTERS[target][:2], reverse), (routes._guard(guarded, reverse, required),)


def _primitive(word, name, reverse):
    routes = _routes()
    pair, guard = _primitive_spec(name, reverse)
    action = routes._exchange_trace(word, pair, name, guard=guard, reverse=reverse)
    assert action["supported"] and action["unchanged_guard"]
    return action["after"], {"offer": name, **action}


def _program(word, operations, reverse):
    steps = []
    for macro in operations:
        pieces = ("J", "R_core", "J_inverse") if macro == "R" else (macro,)
        for name in pieces:
            word, step = _primitive(word, name, reverse)
            steps.append({"complete_offer_name": macro, **step})
    return word, steps


def _invoke_tag(word, program, *, kind, connected, reverse):
    """Address the old tag from the supplied offer or its actual local firing condition."""
    routes = _routes()
    target = routes._places(routes.REGISTERS[routes.T][:2], reverse)
    first = "J" if program[0] == "R" else program[0]
    pair, guard = _primitive_spec(first, reverse)
    if kind == "offer_identity":
        conditions = [()] if first == "J" else []
    else:
        # The two addresses are mutually exclusive and use actual old target values.
        a, b = pair
        conditions = [(*guard, (a,x), (b,1-x)) for x in (0,1)]
    initial = word
    log = []
    for condition in conditions:
        row = routes._exchange_trace(word, target, "copy first supplied offer" if kind == "offer_identity" else "copy actual first firing",
                                     guard=condition, connected=connected, reverse=reverse)
        assert row["supported"] and row["unchanged_guard"]
        word = row["after"]
        log.append(row)
    if kind == "firing" and connected:
        _, first_action = _primitive(initial, first, reverse)
        assert (word != initial) == first_action["changed"]
    return word, log


def _tagged_paths(word, program, reverse):
    routes = _routes()
    previous_t = routes.decode(word, reverse=reverse)["t"]
    assert previous_t == 0
    result = {}
    for mode in ("absent", "kept", "returned", "disconnected", "offer_address_kept"):
        if mode == "absent":
            start, write_tag = word, []
        else:
            start, write_tag = _invoke_tag(word, program, kind="offer_identity" if mode == "offer_address_kept" else "firing",
                                           connected=mode != "disconnected", reverse=reverse)
        out, route = _program(start, program, reverse)
        steps = {"prior_tag_offer": write_tag, "original_program": route}
        after_first_pass = out
        if mode == "returned":
            back, backward = _program(out, reversed(program), reverse)
            assert back == start
            untagged, undo = _invoke_tag(back, program, kind="firing", connected=True, reverse=reverse)
            assert untagged == word
            out, replay = _program(untagged, program, reverse)
            steps.update({"reverse_original_program": backward, "physically_return_tag": undo, "replay_original_program": replay})
        assert all(not failures for layer in steps.values() for row in layer for failures in row["physical_law_failures"].values())
        result[mode] = {"ordinary_end_word": out, "ordinary_end_state": routes.decode(out, reverse=reverse),
                        "after_first_pass": after_first_pass, "steps": steps,
                        "stored_independent_offer_address": mode == "offer_address_kept",
                        "simulator_trace_is_external_and_uncoupled": True}
    assert result["absent"]["ordinary_end_word"] == result["returned"]["ordinary_end_word"] == result["disconnected"]["ordinary_end_word"]
    result["hidden"] = {**result["kept"], "local_read_excludes_t": True, "t_still_held_physically": True}
    return result


def readout_word(word, *, stages=(True, True), scratch_to_q=False, reverse=False, present=True):
    """Map one complete terminal word through the actual B286 keeper writer."""
    routes = _routes()
    status = routes._prep_status(word, reverse=reverse, present=present)
    if status != "admitted":
        return {"status": status, "launch": word, "arrival": word, "terminal": word, "steps": [],
                "readout": routes.decode(word, reverse=reverse) if word is not None else None,
                "law_failures_at_launch": {law: routes._failed_physical(word, law, reverse) for law in LAWS} if word is not None else None}
    steps = []
    incoming = routes.decode(word, reverse=reverse)
    prev = word
    if scratch_to_q:
        prev, transfer = _primitive(word, "transfer_s_to_q", reverse)
        steps.append(transfer)
    out, physical_writes = routes.write_keeper(prev, stages=stages, reverse=reverse)
    steps.extend(physical_writes)
    assert all(not failure for row in steps for failure in row["physical_law_failures"].values())
    return {"status": "admitted", "launch": word, "arrival": prev, "terminal": out, "steps": steps,
            "readout": routes.decode(out, reverse=reverse), "initial_q": incoming["q"], "initial_s": incoming["s"],
            "scratch_to_q": scratch_to_q, "transfer_q_reads_original_s": scratch_to_q and incoming["q"] == 0,
            "stage_connections": stages, "physical_laws": LAWS}


def _encoded_controls():
    routes = _routes()
    implemented = {}
    ready_programs = ("P", "Q", "R", "L", "J", "PQP", "QPQ", "PP", "QQ", "RR", "RPP")
    for reverse in (False, True):
        words = basis_words(reverse)
        label = {w: k for k,w in words.items()}
        by_input = {}
        for start, word in words.items():
            histories = {p: _program(word, p, reverse) for p in ready_programs}
            assert all(not routes._failed_physical(new, law, reverse) for new, _ in histories.values() for law in LAWS)
            assert set(histories[op][0] for op in ("PP", "QQ", "RR")) == {word}
            assert len({histories[op][0] for op in ("R", "PQP", "QPQ", "RPP")}) == 1
            assert label[histories["L"][0]] == {"c": "d", "d": "c"}.get(start, start)
            if start == "d":
                assert all(histories[p][0] == word for p in ("P", "Q", "R"))
            else:
                assert all(label[histories[op][0]] in "abc" for op in ("P", "Q", "R"))
            tagged = {p: _tagged_paths(word, p, reverse) for p in ("R", "PQP", "QPQ")}
            comparison = {p: {mode: tagged["R"][mode]["ordinary_end_word"] == tagged[p][mode]["ordinary_end_word"]
                              for mode in tagged[p]} for p in ("PQP", "QPQ")}
            by_input[start] = {"initial": word, "initial_fields": routes.decode(word, reverse=reverse), "programs": {
                p: {"endpoint": new, "endpoint_name": label[new], "step_count": len(steps), "steps": steps}
                for p,(new,steps) in histories.items()},
                "untagged_first_difference": {p: _words_history(histories["R"][1], histories[p][1]) for p in ("PQP", "QPQ")},
                "tagged_histories": tagged, "equal_full_endpoint_given_tag_mode": comparison}
        keeper_readouts = {}
        for start, word in words.items():
            keeper_readouts[start] = {f"{int(a)}{int(b)}/{int(use_s)}": readout_word(word, stages=(a,b), scratch_to_q=use_s, reverse=reverse)
                                      for a,b,use_s in product((False, True), repeat=3)}
        refused = {"missing_source": readout_word(None, reverse=reverse),
                   "missing_pre_read_permission": readout_word(words["a"], present=False, reverse=reverse),
                   "encoded_nonready": readout_word(routes.encode(245, keeper="101", z=0, reverse=reverse), reverse=reverse),
                   "damaged_binary": readout_word(words["a"] ^ (1 << routes._guard(routes.Q, reverse)[0]), reverse=reverse)}
        assert all(row["status"] != "admitted" and row["launch"] == row["terminal"] for row in refused.values())
        implemented[str(int(reverse))] = {"words": by_input,
                                          "registered_abc_basis": {a: words[a] for a in "abc"},
                                          "registered_abcd_basis": words,
                                          "all_four_writer_connections": keeper_readouts,
                                          "failed_readouts": refused}
    return {"initial_data": 245, "held_auxiliary_code": AUXILIARY_CODE, "orientations": implemented,
            "H_and_ternary_holdings": routes.SUBSTRATE,
            "inherited_assembled_projection": str((ERASURE / "ordinary_routes.py").relative_to(ROOT)),
            "true_R_address": ("J", "R_core", "J_inverse"),
            "full_R_vs_PQP_ruling": "All enrolled words obey the endpoint equality. Ordinary offered histories and marked histories have their own records.",
            "scratch_reference": "L exchanges s at q=0. The last q-controlled writer can receive an actual s read by a separate guarded q swap.",
            "native_clock_or_payer_supplied_to_these_named_exchanges": False}


def _unrestricted_encoded_controls():
    routes = _routes()
    checks = {}
    for reverse, law in product((False, True), LAWS):
        q, s = (routes._places(routes.REGISTERS[index][:2], reverse) for index in (routes.Q, routes.S))
        H = routes._holding("H", reverse)
        rows = []
        for values in product((0, 1), repeat=4):
            named = {m:b for m,b in zip((*q,*s), values, strict=True)}
            # The two H-private marks can be used to extend every local pattern.
            named[routes.H_PRIVATE] = sum(values) % 2 if law == "parity" else 1
            named[routes.Z] = 0
            local = _mask(i for i,m in enumerate(H) if named.get(m,0))
            word = routes.extend_holding("H", local, law, reverse=reverse)
            assert all(_has(word, m) == v for m,v in named.items())
            programs = ("P", "Q", "R", "J", "JJ", "L", "LL", "PQP", "QPQ", "PP", "QQ", "RR")
            traces = {p: _program(word, p, reverse) for p in programs}
            assert all(not routes._failed_physical(new, law, reverse)
                       and all(not row["physical_law_failures"][law] for row in log) for new, log in traces.values())
            assert all(traces[p][0] == word for p in ("JJ", "LL", "PP", "QQ", "RR"))
            equal_p = traces["PQP"][0] == traces["R"][0]
            equal_q = traces["QPQ"][0] == traces["R"][0]
            is_code = values[0] != values[1] and values[2] != values[3]
            assert not is_code or (equal_p and equal_q)
            rows.append({"native_q_members_then_s_members": values, "full_ordinary_extension": word,
                         "complementary_pairs": is_code, "R_equals_PQP": equal_p, "R_equals_QPQ": equal_q,
                         "programs": {p: {"last_full_word": new, "steps": h} for p,(new,h) in traces.items()}})
        checks[f"{law}/{int(reverse)}"] = {"all_guard_bit_patterns": rows,
                                           "counterexamples_R_to_PQP": [r["native_q_members_then_s_members"] for r in rows if not r["R_equals_PQP"]],
                                           "counterexamples_R_to_QPQ": [r["native_q_members_then_s_members"] for r in rows if not r["R_equals_QPQ"]]}
    return {"checked_classes": checks, "coverage": "All operations access or change only these four physical names. Each class extends to a lawful complete word in either law, and the other marks stay unchanged.",
            "preservation": "Each named guarded exchange uses an unchanged held guard and targets identically held marks. This preserves every full holder count, even outside the complementary preparation."}


def physical_checks():
    """Return complete ordinary evidence and the physical basis-to-keeper map."""
    paths = (Path(__file__).resolve(), HERE/"preregistration.md", MOTION/"permutation_controls.py", MOTION/"sources.py",
             HISTORIES, ERASURE/"ordinary_routes.py", ERASURE/"keeper.py")
    return {"coherent_reference_scope": "These are actual ordinary basis and history checks. Coherent phases and reference calibration are compared independently.",
            "ternary": _ternary_controls(), "ordinary_thresholds": _threshold_checks(),
            "encoded": _encoded_controls(), "encoded_unrestricted": _unrestricted_encoded_controls(),
            "source_digests": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest() for p in paths}}
