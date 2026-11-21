"""Ordinary transitions for the enrolled complete-word and keeper comparisons."""

from collections import Counter
from fractions import Fraction
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations, product
import json
import os
from pathlib import Path
import subprocess
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
LAW = ("parity", "nae")
DATA_HOLDERS = ((0, 1, 2), (3, 4, 5), (6, 7, 8), (0, 3, 6), (1, 4, 7), (2, 5, 8))
CHANGE = (1, 2, 7, 8)
Q, T, L, S = range(9, 13)
REGISTERS = tuple((3*i, 3*i+1, 3*i+2) for i in range(13))
A, B, C, Z, H_PRIVATE = range(39, 44)
KEEPER = (A, B, C)
HOLDER = tuple(p for row in REGISTERS for p in row[:2]) + (A, C, Z, H_PRIVATE)
SUBSTRATE = {**{f"register_{i}": row for i, row in enumerate(REGISTERS)}, "K": KEEPER, "H": HOLDER}
B250 = "TWO-KNOTS-ONE-DECISION-20261121-001"
B243 = "SIGN-RECORDS-AND-RECEIVER-TICKS-20261120-001A"
MEASUREMENT = ROOT / "research" / B250 / "measurement.py"
ARCHIVE = ROOT / "artifacts" / B243 / f"{B243}-E001_sign_records" / "physical_histories.json.gz"
GROWTH = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae/naelib.py"


def mask(marks):
    return sum(1 << i for i in marks)


def bit(word, mark):
    return word >> mark & 1


def _names(word):
    return tuple(i for i in range(word.bit_length()) if bit(word, i))


F_MASK = mask(CHANGE)
SEED = ((1 << 9)-1) ^ mask((1, 3, 8))
PAIR = (SEED, SEED ^ F_MASK)


def _transport(mark, reverse):
    if reverse:
        if mark < 39 and mark % 3 != 2:
            return mark + (1 if mark % 3 == 0 else -1)
        if mark in (A, B):
            return A+B-mark
    return mark


def _places(marks, reverse):
    return tuple(_transport(m, reverse) for m in marks)


def _holding(name, reverse):
    return _places(SUBSTRATE[name], reverse)


def encode(data, *, q=0, t=0, l=0, s=0, keeper="110", z=1, h=1, reverse=False):
    """Embed register values as named complementary marks in the fixed apparatus."""
    if not 0 <= data < 1 << 9 or any(v not in (0, 1) for v in (q, t, l, s, z, h)):
        raise ValueError("encoded data and register values must be binary")
    if len(keeper) != 3 or any(v not in "01" for v in keeper):
        raise ValueError("keeper code must have three binary entries")
    values = tuple(bit(data, i) for i in range(9)) + (q, t, l, s)
    occupied = [row[2] for row in REGISTERS]
    occupied.extend(row[v] for row, v in zip(REGISTERS, values, strict=True))
    occupied.extend(m for m, v in zip(KEEPER, keeper, strict=True) if v == "1")
    occupied.extend(m for m, v in ((Z, z), (H_PRIVATE, h)) if v)
    return mask(_places(occupied, reverse))


def _register(word, i, reverse):
    return bit(word, _transport(REGISTERS[i][1], reverse))


def decode(word, *, reverse=False):
    values = tuple(_register(word, i, reverse) for i in range(13))
    return {"data": mask(i for i in range(9) if values[i]), "q": values[Q], "t": values[T], "l": values[L],
            "s": values[S], "keeper": "".join(str(bit(word, i)) for i in _holding("K", reverse)),
            "z": bit(word, Z), "h": bit(word, H_PRIVATE)}


def _locally_allowed(word, row, law):
    n = (word & mask(row)).bit_count()
    return n % 2 == 0 if law == "parity" else 0 < n < len(row)


def _failed_data(data, law):
    return [i for i, row in enumerate(DATA_HOLDERS) if not _locally_allowed(data, row, law)]


def _failed_physical(word, law, reverse=False):
    return [name for name in SUBSTRATE if not _locally_allowed(word, _holding(name, reverse), law)]


def _guard(reg, reverse, value=1):
    return (_transport(REGISTERS[reg][1], reverse), value)


def _exchange_supported(pair, guard, holder, reverse):
    if holder not in SUBSTRATE or len(pair) != 2 or pair[0] == pair[1]:
        return False
    holdings = {name: set(_holding(name, reverse)) for name in SUBSTRATE}
    a, b = pair
    return (a in holdings[holder] and b in holdings[holder] and
            all((a in row) == (b in row) for row in holdings.values()) and
            all(m in holdings[holder] and m not in pair and value in (0, 1) for m, value in guard))


def exchange(word, pair, *, guard=(), holder="H", connected=True, reverse=False):
    """Run one supplied sibling exchange and return (after, enabled, changed)."""
    supported = _exchange_supported(pair, guard, holder, reverse)
    enabled = connected and supported and all(bit(word, m) == value for m, value in guard)
    changed = enabled and bit(word, pair[0]) != bit(word, pair[1])
    return (word ^ mask(pair) if changed else word), enabled, changed


def _trace(name, before, after, enabled, *, offered=True, supported=True, reverse=False, **detail):
    changed = before != after
    status = ("disconnected" if not offered else "unsupported" if not supported else "refused_guard" if not enabled
              else "fired" if changed else "enabled_without_change")
    data = decode(after, reverse=reverse)["data"]
    return {"action": name, "offered": offered, "supported": supported, "enabled": enabled, "changed": changed,
            "status": status, "before": before, "after": after, "before_values": decode(before, reverse=reverse),
            "after_values": decode(after, reverse=reverse), "toggled": _names(before ^ after),
            "physical_law_failures": {law: _failed_physical(after, law, reverse) for law in LAW},
            "decoded_law_failures": {law: _failed_data(data, law) for law in LAW}, **detail}


def _exchange_trace(word, pair, name, *, guard=(), holder="H", connected=True, reverse=False):
    after, enabled, _ = exchange(word, pair, guard=guard, holder=holder, connected=connected, reverse=reverse)
    supported = _exchange_supported(pair, guard, holder, reverse)
    return _trace(name, word, after, enabled, offered=connected, supported=supported, reverse=reverse, holder=holder,
                  pair=tuple(pair), guard=[(m, value, bit(word, m)) for m, value in guard],
                  unchanged_guard=all(bit(word, m) == bit(after, m) for m, _ in guard), supplied_offer=True)


def _register_exchange(word, index, name, *, controls=(), reverse=False, connected=True):
    return _exchange_trace(word, _places(REGISTERS[index][:2], reverse), name,
                           guard=tuple(_guard(c, reverse) for c in controls), reverse=reverse, connected=connected)


def _concerted_trace(word, *, connected, reverse):
    b, c, z = _places((B, C, Z), reverse)
    assert b in _holding("K", reverse) and c in _holding("K", reverse)
    assert c in _holding("H", reverse) and z in _holding("H", reverse)
    assert {name for name in SUBSTRATE if b in _holding(name, reverse)} == {"K"}
    assert {name for name in SUBSTRATE if c in _holding(name, reverse)} == {"K", "H"}
    assert {name for name in SUBSTRATE if z in _holding(name, reverse)} == {"H"}
    left, right = bit(word, b) != bit(word, c), bit(word, z) != bit(word, c)
    enabled = connected and left and right
    after = word ^ mask((b, c, z)) if enabled else word
    assert left == (bit(after, b) != bit(after, c)) and right == (bit(after, z) != bit(after, c))
    if enabled:
        assert bit(after, b) == bit(word, c) and bit(after, c) == bit(word, b) == bit(word, z)
        assert bit(after, z) == bit(word, c)
    return _trace("concerted B,C,z", word, after, enabled, offered=connected, reverse=reverse,
                  local_predicates=[{"holder": "K", "compared": (b, c), "different": left},
                                    {"holder": "H", "compared": (z, c), "different": right}],
                  connecting_mark=c, independently_scheduled=False, supplied_offer=True)


def write_keeper(word, *, stages=(True, True), reverse=False):
    """Run the two offered writer stages on any full word, including disconnected arms."""
    first = _exchange_trace(word, _places((A, C), reverse), "write A,C", guard=(_guard(Q, reverse),),
                            connected=stages[0], reverse=reverse)
    second = _concerted_trace(first["after"], connected=stages[1], reverse=reverse)
    return second["after"], (first, second)


def _complete_change(word, reverse, *, guarded=False, simultaneous=False):
    controls = (Q,) if guarded else ()
    if simultaneous:
        exchanges = [_register_exchange(word, i, f"F[{i}] simultaneous component", controls=controls, reverse=reverse)
                     for i in CHANGE]
        after = word ^ mask(m for row in exchanges for m in row["toggled"])
        trace = _trace("F simultaneous", word, after, all(row["enabled"] for row in exchanges), reverse=reverse,
                       simultaneous_components=exchanges, supplied_offer=True)
        return after, [trace]
    steps = []
    for i in CHANGE:
        action = _register_exchange(word, i, f"F[{i}]", controls=controls, reverse=reverse)
        steps.append(action)
        word = action["after"]
    return word, steps


def _prep_status(word, *, reverse, writer_needed=True, present=True):
    if word is None:
        return "missing_launch"
    if not present:
        return "missing_pre_read_permission"
    if writer_needed:
        keeper = decode(word, reverse=reverse)["keeper"]
        if keeper != "110":
            return "nonready_keeper" if keeper in ("101", "011") else "damaged_keeper"
    for first, second, private in (_places(row, reverse) for row in REGISTERS):
        if bit(word, first) == bit(word, second) or not bit(word, private):
            return "damaged_register"
    if any(_failed_physical(word, law, reverse) for law in LAW):
        return "illegal_physical_launch"
    return "admitted"


def _snapshot(word, reverse):
    if word is None:
        return None
    return {"word": word, **decode(word, reverse=reverse)}


def _basis_outcome(word, status, reverse):
    if status != "admitted":
        return status
    val = decode(word, reverse=reverse)["keeper"]
    return {"110": "unchanged_110", "101": "answer_101", "011": "answer_011"}.get(val, "other_"+val)


def _load(name, path):
    spec = spec_from_file_location(name, path)
    loaded = module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


def _words(row, law):
    return [w for w in range(1 << len(row)) if _locally_allowed(w, tuple(range(len(row))), law)]


def _pack(local, row):
    return mask(m for i, m in enumerate(row) if bit(local, i))


def _unpack(word, row):
    return mask(i for i, m in enumerate(row) if bit(word, m))


def _fill_private(word, shared, private, law):
    count = sum(bit(word, m) for m in shared)
    wanted = count % 2 if law == "parity" else int(count == 0)
    return (word & ~(1 << private)) | (wanted << private)


def extend_holding(name, local_word, law, *, reverse=False):
    """Extend any one full allowed holding to a full allowed assembled word."""
    if law not in LAW or name not in SUBSTRATE:
        raise ValueError("unknown law or holding")
    row = _holding(name, reverse)
    if not 0 <= local_word < 1 << len(row):
        raise ValueError("word lies outside the holding")
    word = _pack(local_word, row)
    if not _locally_allowed(word, row, law):
        raise ValueError("requested local word is forbidden")
    if name != "H":
        h = (word & mask(_holding("H", reverse))).bit_count() % 2 if law == "parity" else 1
        word |= h << H_PRIVATE
    for i in range(13):
        if name != f"register_{i}":
            a, b, c = _places(REGISTERS[i], reverse)
            word = _fill_private(word, (a, b), c, law)
    if name != "K":
        a, b, c = _holding("K", reverse)
        word = _fill_private(word, (a, c), b, law)
    assert not _failed_physical(word, law, reverse) and _unpack(word, row) == local_word
    return word


def _complete_forgotten(local, deleted, law):
    n = local.bit_count()
    v = n % 2 if law == "parity" else int(n == 0)
    below = (1 << deleted)-1
    return (local & below) | ((v + 2*(local >> deleted)) << deleted)


def _canonical_ternaries():
    names = ('a', 'b', 'c')
    out = {}
    for law in LAW:
        patterns = _words(names, law)
        clauses = [" ".join(("~" if bit(w, i) else "")+name for i, name in enumerate(names))
                   for w in range(8) if w not in patterns]
        cmd = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", "a", "b", "--contact", "c", "--json"]
        raw = json.loads(subprocess.check_output(cmd, cwd=ROOT, env={**os.environ, "PYTHONPATH": str(ROOT/"tools")}))
        assert raw["binding"] and raw["coexistence"] and raw["is_knot"]
        assert raw.get("invisible_in_parts", raw.get("loss_on_erasure"))
        out[law] = {k: raw[k] for k in ("allowed", "binding", "coexistence", "is_knot")}
        out[law]["every_one_mark_forgotten_projection_full"] = True
    return out


def _assembled_projections():
    projected = {}
    for reverse, law in product((False, True), LAW):
        holder = _holding("H", reverse)
        ownership = {m: [name for name in SUBSTRATE if m in _holding(name, reverse)] for m in range(44)}
        assert all(1 <= len(held) <= 2 for held in ownership.values())
        assert all(held == ["H"] or len(held) == 1 or held[-1] == "H" for held in ownership.values())
        leaves, arbitrary_checks = {}, []
        for name in SUBSTRATE:
            if name == "H":
                continue
            row = _holding(name, reverse)
            shared = [m for m in row if m in holder]
            private, = (m for m in row if m not in holder)
            local_cases = []
            for fixed in range(4):
                fixed_global = _pack(fixed, shared)
                filling = _fill_private(fixed_global, shared, private, law)
                assert _locally_allowed(filling, row, law)
                local_cases.append({"shared_word": fixed, "private_value": bit(filling, private)})
            local = _words(row, law)
            leaves[name] = {"marks": row, "all_local_word_extensions": {w: extend_holding(name, w, law, reverse=reverse) for w in local},
                            "forbidden_local_words": sorted(set(range(8))-set(local)),
                            "independent_shared_pair_completions": local_cases, "private_mark": private}
        assert len(holder) == 30
        # Every deleted position is checked on both constant words and on both ends of the mixed range.
        # The total completion formula applies to every partial assignment, with no iteration over the large set.
        for deleted in range(len(holder)):
            for partial in (0, (1 << 29)-1, 1, (1 << 29)-2):
                completion = _complete_forgotten(partial, deleted, law)
                full = extend_holding("H", completion, law, reverse=reverse)
                almost = tuple(m for i, m in enumerate(holder) if i != deleted)
                assert _unpack(full, almost) == partial
                arbitrary_checks.append({"deleted": holder[deleted], "fixed_partial": partial, "witness": full})
        bad_h = [1] if law == "parity" else [0, (1 << 30)-1]
        for forb in bad_h:
            assert not _locally_allowed(_pack(forb, holder), holder, law)
        projected[f"{law}/{int(reverse)}"] = {
            "holder_incidences": ownership, "full_ternary_projections": leaves, "H_marks": holder,
            "full_H_projection_size": 1 << 29 if law == "parity" else (1 << 30)-2,
            "H_forbidden_word_witnesses": bad_h, "H_one_deleted_projection_size": 1 << 29,
            "one_deleted_word_checks": arbitrary_checks,
        }

    v1_holder = tuple(p for row in REGISTERS for p in row[:2]) + (*KEEPER, H_PRIVATE)
    v1 = {}
    v1_ready = encode(PAIR[0]) & ~(1 << Z)
    for law in LAW:
        h_word = (1 << H_PRIVATE) | ((1 << A) if law == "parity" else 0)
        assert _locally_allowed(h_word, v1_holder, law) and not _locally_allowed(h_word, KEEPER, law)
        bare = []
        for pair in ((B, C), (A, C)):
            after = v1_ready ^ mask(pair)
            assert all(_locally_allowed(w, row, law) for w in (v1_ready, after) for row in (*REGISTERS, KEEPER, v1_holder))
            bare.append({"pair": pair, "physical_before": v1_ready, "physical_after": after,
                         "K": decode(after)["keeper"], "all_conjuncts_preserved_on_this_write": True})
        v1[law] = {"projected_H_words": 1 << 28 if law == "parity" else 6*(1 << 27),
                   "lawful_H_words": 1 << 29 if law == "parity" else (1 << 30)-2,
                   "allowed_H_unextendible_word": h_word, "forbidden_K_restriction": _unpack(h_word, KEEPER),
                   "selected_bare_writes": bare}
    return {"ternary_canonical": _canonical_ternaries(), "corrected_projections": projected, "failed_v1": v1,
            "total_extension_proof": {
                "from_H": "Each leaf has a different private last mark. Complete it by parity of the shared pair, or by one when both are clear and zero otherwise for not-all-equal. The choices are independent.",
                "from_leaf": "Hold the chosen full leaf fixed. Leave the unused H marks clear except h. Set h to the parity of the fixed H members, or set h to one and z to zero for not-all-equal. Complete all other leaves independently.",
                "forget_one": "Set any deleted mark to the parity of the other values, or supply one when their values are all zero and zero otherwise. This completes every partial assignment. Full projections let these completions extend to the assembled system.",
                "scope": "These arguments are total on the local law. The large holding does not require an enumeration of full words.",
                "external_holder_bare_write_restriction": "For 110 to 101, B and C must have equal incidence in any other parity holder. For 110 to 011, A and C must have equal incidence there. Both one-step writes require that holder to include all three keeper marks or none.",
                "v1_projection": "The old H contains all of K, so H additionally has to satisfy K. Every H word satisfying both extends to the other leaves by their private marks.",
            }}


def _raw_admissions():
    prior = _load("b286_prior_measurement", MEASUREMENT)
    charged = prior.law(DATA_HOLDERS, odd=5)
    source = prior.compile_device(DATA_HOLDERS, charged)
    assert source.status == "ready" and source.named_mask(source.flips[3]) == CHANGE
    assert source.signs[3] == 0 and 3 not in CHANGE
    assert all(not all(_unpack(w, h) in r for h, r in zip(DATA_HOLDERS, charged, strict=True)) for w in range(512))
    tables = {}
    for law in LAW:
        admissions, accepted, splits = [], [], []
        legal = {w: _failed_data(w, law) for w in range(512)}
        for w in range(512):
            v = w ^ F_MASK
            one, other = not legal[w], not legal[v]
            status = "admitted" if one and other else "valid_to_invalid" if one else "invalid_to_valid" if other else "both_invalid"
            admissions.append({"input": w, "reversed": v, "status": status, "input_refused_holders": legal[w],
                               "reversed_refused_holders": legal[v]})
            if w < v and one and other:
                accepted.append({"ordered_words": [(w, v), (v, w)], "read_at_mark_3": bit(w, 3),
                                 "mathematical_sign_settings": [1, -1]})
            if w < v and one != other:
                splits.append((w, v))
        subsets = [{"input": w, "toggled": chosen, "next": w ^ mask(chosen),
                    "failed_holders": legal[w ^ mask(chosen)]}
                   for w in PAIR for count in range(1, len(CHANGE)) for chosen in combinations(CHANGE, count)]
        assert all(not legal[w] for w in PAIR)
        shortest = {}
        for w in PAIR:
            candidates = [(w ^ v).bit_count() for v in legal if v != w and not legal[v]]
            minimum = min(candidates)
            shortest[w] = {"least_hamming_weight": minimum, "compiled_change_is_minimal": minimum == len(CHANGE),
                           "all_least_masks": sorted(w ^ v for v in legal if v != w and not legal[v] and (w ^ v).bit_count() == minimum)}
        tables[law] = {"steps": admissions, "counts": dict(Counter(row["status"] for row in admissions)),
                       "allowed_words": sum(not failures for failures in legal.values()), "closed_pairs": accepted,
                       "split_pairs": splits, "uniform_start_joint_admission": str(Fraction(len(accepted)*2, 512)),
                       "uniform_start_refusal": str(1-Fraction(len(accepted)*2, 512)),
                       "chosen_preparation": {"admission": "1", "word_weights": {w: "1/2" for w in PAIR}},
                       "chosen_proper_subset_checks": subsets,
                       "inclusion_minimal_on_chosen_pair": all(row["failed_holders"] for row in subsets),
                       "chosen_global_weight_checks": shortest,
                       "independently_scheduled_by_original_catalogue": False}
    return {"compiled": {"question": 3, "change": CHANGE, "ordinary_sign_mark": 3, "sign_change_bit": 0,
                         "homogeneous_words": source.carrier, "charged_full_ordinary_words": 0},
            "chosen_pair": PAIR, "laws": tables}


ROUTE_MODES = ("clean", "tag_retained", "tag_ignored", "tag_returned", "tag_into_environment", "tag_forgotten",
               "copied_return_t_only", "copied_return_l_then_t", "old_x_retained", "old_x_returned")


def _append_register(moves, word, index, name, reverse, controls=(), connected=True):
    action = _register_exchange(word, index, name, reverse=reverse, controls=controls, connected=connected)
    moves.append(action)
    return action["after"]


def _reset_t(word, reverse):
    return word ^ mask(_places(REGISTERS[T][:2], reverse)) if _register(word, T, reverse) else word


def _run_route(word, mode, stages, reverse, *, present=True):
    status = _prep_status(word, reverse=reverse, present=present)
    stamp = _snapshot(word, reverse)
    if status != "admitted":
        return {"mode": mode, "launch": status, "initial": stamp, "pre_writer": stamp, "terminal": stamp,
                "outcome": status, "steps": [], "stage_connections": stages,
                "physical_law_failures_on_launch": ({law: _failed_physical(word, law, reverse) for law in LAW}
                                                    if word is not None else None)}

    moves, curr = [], word
    if mode.startswith("old_x_"):
        curr = _append_register(moves, curr, L, "copy old x into l", reverse, (1,))
    curr, changed_data = _complete_change(curr, reverse, guarded=True)
    moves.extend(changed_data)

    if mode.startswith(("tag_", "copied_")):
        curr = _append_register(moves, curr, T, "copy q into t", reverse, (Q,))
    if mode.startswith("copied_"):
        curr = _append_register(moves, curr, L, "copy t into l", reverse, (T,))
    if mode == "copied_return_l_then_t":
        curr = _append_register(moves, curr, L, "return l from t", reverse, (T,))
    if mode in ("tag_returned", "copied_return_t_only", "copied_return_l_then_t"):
        curr = _append_register(moves, curr, T, "return t from q", reverse, (Q,))
    if mode == "tag_into_environment":
        curr = _append_register(moves, curr, S, "copy t into physical environment s", reverse, (T,))
        curr = _append_register(moves, curr, T, "return t using retained physical s", reverse, (S,))
    if mode == "tag_forgotten":
        # This deliberately noninjective classical reset exposes no guard bit or physical copy.
        reset = _reset_t(curr, reverse)
        moves.append(_trace("ordinary merge t=0", curr, reset, True, reverse=reverse,
                            supplied_irreversible_update=True, retained_old_t=False))
        curr = reset
    if mode == "old_x_returned":
        curr = _append_register(moves, curr, L, "subtract new x from l", reverse, (1,))
        curr = _append_register(moves, curr, L, "subtract q from l", reverse, (Q,))

    cut = _snapshot(curr, reverse)
    out, writes = write_keeper(curr, stages=stages, reverse=reverse)
    moves.extend(writes)
    assert all(not failed for row in moves for failed in row["physical_law_failures"].values())
    assert decode(out, reverse=reverse)["data"] == stamp["data"] ^ (F_MASK if stamp["q"] else 0)
    return {"mode": mode, "launch": status, "initial": stamp, "pre_writer": cut, "terminal": _snapshot(out, reverse),
            "outcome": _basis_outcome(out, status, reverse), "steps": moves, "stage_connections": stages,
            "physical_record_access": {"t_read_by_observer": mode != "tag_ignored", "s_designated_unread_environment": mode == "tag_into_environment",
                                      "external_trace_coupled": False},
            "route_register_values_match_launch": all(cut[key] == stamp[key] for key in ("t", "l", "s")),
            "irreversible_reset_used": mode == "tag_forgotten"}


def _json_law(sample, value):
    law = Counter()
    for row, p in sample:
        law[value(row)] += p
    assert sum(law.values()) == 1
    return [{"value": item, "mass": str(p)} for item, p in sorted(law.items(), key=lambda entry: repr(entry[0]))]


TERMINAL_FIELDS = ("data", "q", "t", "l", "s", "keeper", "z", "h", "word")
OUTCOMES = ("answer_101", "answer_011", "unchanged_110")


def _ordinary_probabilities(rows):
    sample = [(row, Fraction(1, len(rows))) for row in rows]
    answers = Counter(row["outcome"] for row in rows)
    accept = [row for row in rows if row["launch"] == "admitted"]
    accepted_answers = Counter(row["outcome"] for row in accept)
    return {"launch_mass": "1", "admission_mass": str(sum(p for row, p in sample if row["launch"] == "admitted")),
            "answer_masses": {outcome: str(Fraction(answers[outcome], len(rows))) for outcome in sorted(set(answers) | set(OUTCOMES))},
            "terminal_joint": _json_law(sample, lambda row: (row["outcome"], *(row["terminal"][k] for k in TERMINAL_FIELDS))
                                      if row["terminal"] is not None else (row["outcome"],)),
            "conditional_answers_given_admission": {o: str(Fraction(accepted_answers[o], len(accept)))
                                                      for o in sorted(set(accepted_answers) | set(OUTCOMES))} if accept else None}


def _recoverable(rows, when, fields):
    supports = [Counter(tuple(row[when][v] for v in fields) for row in rows if row["initial"]["q"] == q) for q in (0, 1)]
    p, r = (sum(row.values()) for row in supports)
    assert p and r
    tv = sum((abs(Fraction(supports[0][z], p)-Fraction(supports[1][z], r)) for z in supports[0].keys() | supports[1].keys()), Fraction()) / 2
    return {"route_supports_disjoint": not (supports[0].keys() & supports[1].keys()), "total_variation": str(tv),
            "common_outcome_count": len(supports[0].keys() & supports[1].keys())}


def _routes():
    banks = {}
    stage_schedules = tuple(product((False, True), repeat=2))
    for reverse, mode, stages in product((False, True), ROUTE_MODES, stage_schedules):
        rows = [_run_route(encode(w, q=q, reverse=reverse), mode, stages, reverse) for w, q in product(PAIR, (0, 1))]
        for row in rows:
            expected_return = mode in ("clean", "tag_returned", "tag_forgotten", "copied_return_l_then_t", "old_x_returned") or row["initial"]["q"] == 0
            if mode == "old_x_retained":
                expected_return = not row["initial"]["data"] >> 1 & 1
            assert row["route_register_values_match_launch"] == expected_return
        key = f"{int(reverse)}/{mode}/{int(stages[0])}{int(stages[1])}"
        basis = {str(w): _ordinary_probabilities([row for row in rows if row["initial"]["data"] == w]) for w in PAIR}
        fixed = {f"{row['initial']['data']}/{row['initial']['q']}": _ordinary_probabilities([row]) for row in rows}
        mixture = _ordinary_probabilities(rows)
        accessible = {"complete_word": TERMINAL_FIELDS, "keeper": ("keeper",), "q": ("q",), "data": ("data",),
                      "data_plus_l": ("data", "l"), "t": ("t",), "s": ("s",),
                      "without_q_and_K": ("data", "t", "l", "s", "z", "h")}
        diagnostic = {}
        for label, population in (("fair_hidden_data", rows), *((str(w), [r for r in rows if r["initial"]["data"] == w]) for w in PAIR)):
            diagnostic[label] = {when: {name: _recoverable(population, when, fields) for name, fields in accessible.items()}
                                 for when in ("pre_writer", "terminal")}
        banks[key] = {"both_physical_laws": LAW, "trials": rows, "fixed_complete_input_probabilities": fixed,
                      "fair_selector_by_basis_word": basis, "fair_selector_and_data": mixture,
                      "preparations_with_same_ordinary_packet_as_fair_selector_and_data": ("plus", "minus", "dephased"),
                      "ordinary_crossed_sign_contrast": "0",
                      "retained_record_route_recovery": diagnostic}
    refusals, mergers = {}, []
    for reverse in (False, True):
        valid = encode(PAIR[0], reverse=reverse)
        damaged_pair = valid ^ (1 << _transport(REGISTERS[Q][1], reverse))
        controls = {"missing_launch": (None, True), "missing_pre_read_permission": (valid, False),
                    "damaged_register": (damaged_pair, True),
                    "nonready_keeper": (encode(PAIR[0], keeper="101", z=0, reverse=reverse), True),
                    "damaged_keeper": (encode(PAIR[0], keeper="111", reverse=reverse), True)}
        refusals[str(int(reverse))] = {key: _run_route(w, "clean", (True, True), reverse, present=present)
                                      for key, (w, present) in controls.items()}
        for key, row in refusals[str(int(reverse))].items():
            assert key == row["outcome"] and row["initial"] == row["terminal"]
            row["probabilities"] = _ordinary_probabilities([row])
        t_words = (valid, encode(PAIR[0], t=1, reverse=reverse))
        merged = tuple(_reset_t(w, reverse) for w in t_words)
        assert t_words[0] != t_words[1] and merged[0] == merged[1] == valid
        mergers.append({"reverse": reverse, "two_full_ready_inputs": t_words, "only_retained_output": valid,
                        "retained_old_t": False, "mass_of_common_output_at_each_singleton": "1"})
    return {"terminal_fields": TERMINAL_FIELDS, "banks": banks, "refused_launches": refusals, "standalone_t_merger": mergers,
            "tag_forgotten_interpretation": "The ordinary t map is many-to-one. Its external audit is not a physical record. The other registers may still contain route information.",
            "tag_ignored_interpretation": "The t mark remains in the physical word even if the observer excludes it from the scored outcome."}


def _run_order(code, w, proxy, mode, reverse):
    prior = encode(w, t=proxy, reverse=reverse)
    moves, curr = [], prior

    def apply(offered, state, label):
        if offered == "F":
            new, constituent = _complete_change(state, reverse)
        else:
            gate = _register_exchange(state, T, "C: swap t if x=1", controls=(1,), reverse=reverse)
            constituent, new = [gate], gate["after"]
        moves.append(_trace(f"{label}:{offered}", state, new, any(e["enabled"] for e in constituent),
                            reverse=reverse, actual_microsteps=constituent, supplied_offer=True))
        return new

    for op in code:
        curr = apply(op, curr, "preparation")
    cut = _snapshot(curr, reverse)
    if mode == "inverse_with_copy":
        curr = _append_register(moves, curr, L, "save t in l before reversing", reverse, (T,))
    if mode.startswith("inverse_"):
        for op in reversed(code):
            curr = apply(op, curr, "inverse preparation")
    controls = (L,) if mode == "inverse_with_copy" else (T,)
    curr = _append_register(moves, curr, Q, "deliver ordinary proxy through q", reverse, controls, connected=mode != "hidden_t")
    terminal, writes = write_keeper(curr, reverse=reverse)
    moves.extend(writes)
    assert decode(terminal, reverse=reverse)["data"] == w
    assert all(not failures for row in moves for failures in row["physical_law_failures"].values())
    return {"four_offers": code, "ordinary_proxy": proxy, "mode": mode, "initial": _snapshot(prior, reverse),
            "pre_inverse_cut": cut, "pre_writer": _snapshot(curr, reverse), "terminal": _snapshot(terminal, reverse),
            "launch": "admitted", "outcome": _basis_outcome(terminal, "admitted", reverse), "steps": moves}


def _order_controls():
    rows = {}
    for reverse, code, proxy, mode in product((False, True), ("FFCC", "FCFC"), (0, 1),
                                               ("retained", "hidden_t", "inverse_without_copy", "inverse_with_copy")):
        cases = [_run_order(code, w, proxy, mode, reverse) for w in PAIR]
        rows[f"{int(reverse)}/{code}/{proxy}/{mode}"] = {
            "basis_singletons": [_ordinary_probabilities([case]) for case in cases], "fair_complete_input_pair": _ordinary_probabilities(cases),
            "crossed_signs_and_dephased_identical_at_fixed_ordinary_arm": True, "cases": cases,
        }
    return {"comparisons": rows, "fixed_reader": "copy a designated retained mark through q into the actual two-stage keeper",
            "mode_hidden_t": "The guard carrying t to q is disconnected. Named t remains on the complete physical apparatus.",
            "no_signed_preparation_setting_delivered": True}


def _ordinary_microprogram(word, program, reverse, *, strict_law=None):
    """Propagate the ordinary singleton probabilities of the addressed steps."""
    rows = [(word, Fraction(1), [], None)]
    for index, controls, half in program:
        next_rows = []
        for before, weight, history, stopped in rows:
            if stopped is not None:
                next_rows.append((before, weight, history, stopped))
                continue
            name = f"{'elementary pulse' if half else 'complete exchange'} {index}"
            move = _register_exchange(before, index, name, controls=controls, reverse=reverse)
            split = half and move["changed"]
            possible = [(before, Fraction(1, 2), "stay"), (move["after"], Fraction(1, 2), "exchange")] if split else [
                (move["after"], Fraction(1), "complete" if not half else "idle")]
            for after, p, selected in possible:
                failures = {law: _failed_data(decode(after, reverse=reverse)["data"], law) for law in LAW}
                if strict_law is not None and failures[strict_law]:
                    refusal = {"law": strict_law, "would_fail_holders": failures[strict_law], "proposed_word": after,
                               "committed_word": before, "step_number": len(history)+1}
                    actual = before
                else:
                    refusal, actual = None, after
                row = _trace(name, before, actual, move["enabled"], reverse=reverse,
                             proposal=move["after"], ordinary_branch=selected, conditional_mass=str(p),
                             guard=move["guard"], pair=move["pair"], strict_policy_refusal=refusal,
                             same_single_step_probabilities_under_both_idle_phase_completions=True)
                assert not any(row["physical_law_failures"].values())
                next_rows.append((actual, weight*p, history+[row], refusal))
        rows = next_rows
    assert sum(row[1] for row in rows) == 1
    return [{"terminal": _snapshot(v, reverse), "mass": str(p), "steps": hs, "refusal": refuse} for v, p, hs, refuse in rows]


def _microprogram_checks(raw):
    predecessor_blocks = tuple((i, (1,), False) for i in CHANGE[1:])
    conjugator = (*predecessor_blocks, (1, (), True), *reversed(predecessor_blocks))
    naive = tuple((i, (), True) for i in CHANGE)
    chosen = {}
    for reverse, w in product((False, True), PAIR):
        start = encode(w, reverse=reverse)
        sequential, steps = _complete_change(start, reverse)
        direct, simultaneous = _complete_change(start, reverse, simultaneous=True)
        assert direct == sequential and decode(direct, reverse=reverse)["data"] == w ^ F_MASK
        assert all(not faults for row in steps + simultaneous for faults in row["physical_law_failures"].values())
        failed_sweeps = {law: _ordinary_microprogram(start, conjugator, reverse, strict_law=law) for law in LAW}
        branches = _ordinary_microprogram(start, conjugator, reverse)
        whole = _ordinary_microprogram(start, naive, reverse)
        assert {r["terminal"]["word"] for r in branches} == {start, direct}
        assert len(whole) == 16 and all(r["mass"] == "1/16" for r in whole)
        for row in whole:
            d = row["terminal"]["data"]
            row["off_pair"] = d not in PAIR
            row["terminal_decoded_failures"] = {law: _failed_data(d, law) for law in LAW}
        chosen[f"{int(reverse)}/{w}"] = {"simultaneous": simultaneous, "sequential": steps,
                                          "balanced_conjugated_exchange": branches, "strict_old_holder_policy": failed_sweeps,
                                          "individually_half_pulsed": whole,
                                          "individually_pulsed_off_pair_mass": str(sum(Fraction(r["mass"]) for r in whole if r["off_pair"])),
                                          "individually_pulsed_illegal_mass": {
                                              law: str(sum(Fraction(r["mass"]) for r in whole if r["terminal_decoded_failures"][law])) for law in LAW}}

    allowed = sorted({w for law in LAW for entry in raw["laws"][law]["closed_pairs"] for w in entry["ordered_words"][0]})
    full = {}
    for w in allowed:
        physical = encode(w)
        check = _ordinary_microprogram(physical, conjugator, False)
        assert {r["terminal"]["data"] for r in check} == {w, w ^ F_MASK}
        full[str(w)] = {"conjugated_microsteps": check,
                        "strict_policy_on_lawful_pair": {law: _ordinary_microprogram(physical, conjugator, False, strict_law=law)
                                                         for law in LAW if not _failed_data(w, law) and not _failed_data(w^F_MASK, law)}}

    # An addressed pair can be equal and perfectly legal in the unrestricted law.
    # A pair drawn from two different register holdings is unsupported, even though H sees both.
    cases = {}
    for law in LAW:
        state = extend_holding("H", 0 if law == "parity" else 1 << (len(HOLDER)-1), law)
        equal = _register_exchange(state, Q, "addressed equal pair")
        bad_pair = _exchange_trace(state, (REGISTERS[Q][0], REGISTERS[T][0]), "unsupported target pair")
        assert equal["enabled"] and not equal["changed"] and not bad_pair["enabled"]
        assert not equal["physical_law_failures"][law]
        cases[law] = {"equal_pair": equal, "not_identically_held": bad_pair}
    return {"chosen_inputs": chosen, "every_admissible_closed_pair": full, "unrestricted_proposal_controls": cases,
            "chronological_compound_program": conjugator, "separate_individual_half_pulses": naive,
            "signed_pulse_amplitudes_are_a_separate_comparison": True}


def _unrestricted_writer():
    result = {}
    for reverse in (False, True):
        a, b, c, z = _places((A, B, C, Z), reverse)
        control = _guard(Q, reverse)[0]
        masks = {name: mask(_holding(name, reverse)) for name in SUBSTRATE}
        tested = []
        for bits in product((0, 1), repeat=5):
            w = mask(mark for mark, value in zip((a, b, c, z, control), bits, strict=True) if value)
            for stage in ((True, False), (False, True)):
                out, steps = write_keeper(w, stages=stage, reverse=reverse)
                rr, _ = write_keeper(out, stages=stage, reverse=reverse)
                assert rr == w
                assert all((w & places).bit_count() == (out & places).bit_count() for places in masks.values())
                tested.append({"actual_active_bits": bits, "selected_stage": stage, "ordinary_word": w, "after": out,
                               "changed": any(row["changed"] for row in steps)})
        result[str(int(reverse))] = tested
    return {"exhaustive_touched_mark_controls": result,
            "full_law_proof_first": "A and C have exactly the same two holders. The q guard is unchanged and available in H.",
            "full_law_proof_second": "Each true local inequality implies B=z differs from C. Jointly flipping B,C,z swaps B,C as held by K and swaps C,z as held by H. No other holding changes, and both local inequalities persist.",
            "scope": "Counts in every full holding are preserved for any values at the untouched marks. Each primitive separately is an involution.",
            "authority": "The concerted two-holder timing and all offered exchanges are supplied. The growth law is not a provider of either writer stage."}


def _funding_replay():
    growth = _load("b286_prior_growth", GROWTH)
    proof = ROOT / "proofs" / f"{B250}P" / f"{B250}P-P001_measurement" / "result.json"
    old = json.loads(proof.read_text())["common_checks"]["structural_and_latch_controls"]["funded_births_at_all_values"]
    source = ((0, 2, 3), (0, 1, 4), (1, 5, 6))
    orders = {}
    for law in LAW:
        legal = [w for w in range(128) if all(_locally_allowed(w, row, law) for row in source)]
        result = {}
        rule = (growth.parity_rule if law == "parity" else growth.nae_rule)(growth.F.fewest)
        for word in legal:
            state = growth.J.S.from_junctions(source)
            assert frozenset((0, 2)) in state.groups_among(state.live)
            assert state.step(rule, None) is not None
            details = []
            for i in range(len(source), len(state.bits_of)):
                paid = state.bits_of[i][:state.parents[i]]
                details.append({"child": i, "paying_parents": [next(k for k in state.owner[b] if k < i) for b in paid],
                                "paid_distinctions": paid, "fresh_names": state.bits_of[i][state.parents[i]:],
                                "grant": state.fresh[i]})
            assert details == old[law]["identical_funded_table"]
            result[word] = details
        assert legal == old[law]["ordinary_words"]
        assembled = growth.J.S.from_junctions(tuple(SUBSTRATE.values()))
        groups = assembled.groups_among(assembled.live)
        due = Counter(payer for group in groups for payer in group)
        shortage = [(p, due[p], len(assembled.loose(p))) for p in assembled.live if due[p] > len(assembled.loose(p))]
        actual = assembled.step(rule, None)
        assert bool(shortage) == (actual is None)
        orders[law] = {"predecessor_input_words": legal, "predecessor_funded_outcomes": result,
                       "assembled_funded_status": "stall" if actual is None else "funded", "assembled_payer_shortages": shortage,
                       "assembled_candidate_groups": [sorted(group) for group in groups],
                       "writer_selected_from_actual_native_births": False}
    return {"predecessor_source": source, "laws": orders, "predecessor_reference": str(proof.relative_to(ROOT)),
            "source_digests": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in (GROWTH, proof)}}


def _native_controls():
    old = ROOT / "research/JOINT-PARENTS-AND-ERASURE-20261120-001/merger_audit.json"
    physical = ROOT / "research" / B243 / "physical_records.md"
    controls = json.loads(old.read_text())
    bounds = [row["examples"]["current_word_allows_contrast"] for row in controls]
    for row in bounds:
        row["bounds"] = {kind: str(Fraction(str(value))) for kind, value in row["bounds"].items()}
    return {"archived_loose_swap": str(physical.relative_to(ROOT)),
            "archived_later_switch_word_and_event_bounds": bounds,
            "earlier_restored_terminal_deterministic_singleton_has_zero_affine_contrast": True,
            "archived_later_parity_load_nae_admission": "undefined",
            "source_digests": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest() for path in (old, physical, ARCHIVE)},
            "authority": "Prior native bounds and lawful two-mark replay are cited controls. The named encoded offers in this study are additional."}


def ordinary_checks():
    """Return the complete registered ordinary subrecord in JSONable form."""
    raw = _raw_admissions()
    return {"apparatus": {"holdings": SUBSTRATE, "binary_registers": REGISTERS, "auxiliary_indices": {"q": Q, "t": T, "l": L, "s": S},
                          "keeper_marks": KEEPER, "H_private_marks": (Z, H_PRIVATE), "semantic_codes": {0: "101", 1: "011"},
                          "reverse_is_passive_transport_of_all_pairs_and_keeper_A_B": True},
            "raw_source": raw, "assembled_law": _assembled_projections(), "writer_primitives": _unrestricted_writer(),
            "ordinary_routes": _routes(), "order_and_proxy": _order_controls(), "intermediate_routes": _microprogram_checks(raw),
            "native_funding": _funding_replay(), "archived_controls": _native_controls(),
            "sources": {str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
                        for path in (Path(__file__).resolve(), HERE/"preregistration.md", MEASUREMENT)}}
