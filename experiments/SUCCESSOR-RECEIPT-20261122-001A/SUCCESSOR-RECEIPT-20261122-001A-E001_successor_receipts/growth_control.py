"""Check the ordinary successors and the separately supplied later source."""

from collections import defaultdict
from contextlib import contextmanager
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys

from pysat.solvers import Minisat22


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "alternate.json.gz"
PRIOR = "HIDDEN-SENDER-MARKS-20261122-001A"
DATA = ROOT / "artifacts" / PRIOR / (PRIOR + "-E001_hidden_sends")
GROWTH = DATA / "growth.json.gz"
WORDS = DATA / "whole_words.json.gz"
REPLAY = ROOT / "research/REPEATED-SENDS-20261122-001/check_fixed_holder.py"
FOURTH = ROOT / "research/REPEATED-SENDS-20261122-001/fixed_holder_replay.json"
SOURCES = {
    GROWTH: "f89de84f884b323e40f81a59dc7afa0e734bf4dc974e26eb5c7be9c5f775ce9a",
    WORDS: "d652b46212ed4fdd3ad344596ce9a6c1b2cc2be3327cb8fbac6a765226c2f290",
    REPLAY: "e1857f93f36276ad6f6484da1ab5feab95a9393bee99cc53f5f7d6e34adc8a00",
    FOURTH: "6ac79b178c1019a6a93b03eae30468483333bdb95ea2896fb7c3a2b5be840eee",
}
LAWS = ("parity", "nae")
ROUTES = ("intact", "interrupted", "sham")
R = 294
W = (1754, 1755, 1756)
H = (631, 633, 634)
U = (1748, 1753, 1764)
OLD_SOURCE = (510, 563)


def read_store(path):
    return json.loads(gzip.decompress(path.read_bytes()))


def load(path=OUTPUT):
    return read_store(path)


def marks(names):
    return sum(1 << n for n in names)


def bits(word, names):
    return "".join(str(word >> n & 1) for n in names)


def owners(stars):
    out = defaultdict(list)
    for holder, row in enumerate(stars):
        assert len(row) == len(set(row)) >= 3
        for name in row:
            out[name].append(holder)
    assert all(len(pair) in (1, 2) for pair in out.values())
    return out


def append_rows(stars, layer):
    return stars + tuple(tuple(row["consumed_names"] + row["fresh_names"]) for row in layer["births"])


def third_stars(growth, law, route):
    stars = tuple(map(tuple, growth["original_stars"]))
    for cut in growth["cases"][route][law]["cuts"]:
        stars = append_rows(stars, cut)
    return stars


def load_grown(law, route, path=OUTPUT):
    """Recover the complete fourth-cut board from the saved exact receipts."""
    saved = load(path)["courses"][law][route]["fourth"]
    if saved["status"] != "extend":
        raise ValueError(f"Fourth cut for {law}/{route} {saved['status']}")
    return append_rows(third_stars(read_store(GROWTH), law, route), saved)


def previous():
    spec = spec_from_file_location("b309_previous_fixed_holder", REPLAY)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def paid_cut(module, original, law, cap):
    """Confront the capped plan and the previous literal allocator with incidence."""
    old = owners(original)
    plan = module.engine.step(module.engine.from_stars(original), law, max_births=cap)
    out = {"status": plan.status, "cap": cap, "births": [], "shortages": plan.shortages,
           "planned_births_lower": plan.planned_births_lower}
    if plan.status != "extend":
        return original, out
    assert not plan.implied
    reached, ledger = module.append_fourth(list(original), law)
    unused = {d for d, pair in old.items() if len(pair) == 1}
    granted = set()
    current = owners(reached)
    for i, ((paid, fresh), parents, count, demand) in enumerate(zip(
            ledger, plan.parents, plan.fresh, plan.demand, strict=True)):
        holder = len(original) + i
        actual_parents = [old[name][0] for name in paid]
        assert actual_parents == list(parents)
        assert count == len(fresh) == max(1, 3 - len(parents), demand)
        for donor, name in zip(actual_parents, paid, strict=True):
            assert old[name] == [donor] and current[name] == [donor, holder]
            unused.remove(name)
        for d in fresh:
            assert d not in old and d not in granted and current[d] == [holder]
            granted.add(d)
        out["births"].append({"holder": holder, "parents": actual_parents, "consumed_names": list(paid),
                              "fresh_names": list(fresh), "demand": demand, "grant": count})
    assert not unused and len(out["births"]) <= cap
    assert tuple(reached) == append_rows(original, out)
    return tuple(reached), out


def receipt(holding, before, after, births):
    """A single anonymous batch from all-private to all-shared on the fresh bank."""
    h, fresh = holding["holder"], holding["fresh_names"]
    assert fresh and all(before[d] == [h] for d in fresh)
    peers = []
    payments = []
    by_id = {row["holder"]: row for row in births}
    for name in fresh:
        assert h in after[name]
        child, = (p for p in after[name] if h != p)
        paid = by_id[child]
        assert paid["consumed_names"][paid["parents"].index(h)] == name
        peers.append(child)
        payments.append({"name": name, **paid})
    clock_ids = {}
    trace = [[None] * len(fresh), [clock_ids.setdefault(peer, len(clock_ids)) for peer in peers]]
    return {"coholder_samples": trace, "physical_payments": payments, "positive_local_finish": True}


def check_fourth(module, growth, past, law, route):
    before = third_stars(growth, law, route)
    reached, cut = paid_cut(module, before, law, 1024)
    if cut["status"] != "extend":
        return {"fourth": cut, "successors": []}, before, reached
    assert len(cut["births"]) == past[law][route]["further_births"] == 964
    third = {row["holder"]: row for row in growth["cases"][route][law]["cuts"][2]["births"]}
    old, new = owners(before), owners(reached)
    assert before[R] == reached[R] == (949, 957, *W)
    assert all(new[n] == old[n] and len(old[n]) == 2 for n in (*before[R], *OLD_SOURCE))
    records = []
    for i, (xi, h, other) in enumerate(zip(W, H, U, strict=True)):
        row = third[h]
        assert old[xi] == [R, h] and new[xi] == [R, h]
        assert R in row["parents"] and row["consumed_names"][row["parents"].index(R)] == xi
        assert set(row["consumed_names"]) == {xi, other}
        assert len(set(row["parents"])) == 2
        assert all(old[d] == [p, h] for p, d in zip(row["parents"], row["consumed_names"], strict=True))
        result = receipt(row, old, new, cut["births"])
        records.append({"position": i, "earlier_R_name": xi, "other_inherited_name": other,
                        "actual_birth": row, **result})
    return {"fourth": cut, "successors": records}, before, reached


def select(fourth, stage_three):
    owner = owners(stage_three)
    eligible, excluded = [], []
    for row in fourth["births"]:
        parents = row["parents"]
        for h in set(parents).intersection(H):
            if len(parents) != 2:
                excluded.append({"receiving_child": row["holder"], "H": h, "reason": "parent count differs from two"})
                continue
            k, = set(parents) - {h}
            private = sorted(n for n in stage_three[k] if owner[n] == [k])
            if len(private) < 2:
                excluded.append({"receiving_child": row["holder"], "H": h, "K": k,
                                 "reason": "fewer than two private marks at K"})
                continue
            p = dict(zip(parents, row["consumed_names"], strict=True))
            hp, q = p[h], p[k]
            assert owner[hp] == [h] and owner[q] == [k]
            spare = next(n for n in private if n != q)
            i = H.index(h)
            assert W[i] not in row["consumed_names"]
            eligible.append({"G": row["holder"], "H": h, "K": k, "position": i, "paid_h": hp,
                             "paid_q": q, "spare_q": spare, "old_R_name": W[i], "other_H_input": U[i]})
    eligible.sort(key=lambda row: (row["K"] in H, row["position"], row["G"], row["K"]))
    return {"eligible": eligible, "excluded": excluded, "selected": eligible[0] if eligible else None}


class WordCheck:
    def __init__(self, law, stars):
        self.law = law
        self.rows = [(marks(row), len(row)) for row in stars]
        self.domain = marks(owners(stars))

    def allowed(self, word):
        assert word >= 0 and word & ~self.domain == 0
        if self.law == "parity":
            return all((word & mask).bit_count() % 2 == 0 for mask, _ in self.rows)
        return all(0 < (word & mask).bit_count() < width for mask, width in self.rows)


def parity_completion(check, fixed, ones):
    pivots = {}
    for row, _ in check.rows:
        rhs = (row & ones).bit_count() & 1
        row &= ~fixed
        while row:
            pivot = row.bit_length() - 1
            if pivot not in pivots:
                pivots[pivot] = row, rhs
                break
            stored, needed = pivots[pivot]
            row ^= stored
            rhs ^= needed
        else:
            if rhs:
                return None
    result = ones
    for pivot, (row, rhs) in sorted(pivots.items()):
        if (row & result).bit_count() % 2 != rhs:
            result |= 1 << pivot
    return result


@contextmanager
def completions(law, stars, old, old_names):
    check = WordCheck(law, stars)
    locked = marks(old_names)
    assert old & ~locked == 0
    with Minisat22() as solver:
        if law == "nae":
            for row in stars:
                solver.add_clause([d + 1 for d in row])
                solver.add_clause([-d - 1 for d in row])
            for d in old_names:
                solver.add_clause([d + 1 if old >> d & 1 else -d - 1])

        def complete(pins):
            assert not set(pins) & set(old_names)
            if law == "parity":
                one = marks(d for d, value in pins.items() if value)
                word = parity_completion(check, locked | marks(pins), old | one)
            else:
                literals = [d + 1 if value else -d - 1 for d, value in sorted(pins.items())]
                word = marks(lit - 1 for lit in solver.get_model() if lit > 0) if solver.solve(assumptions=literals) else None
            if word is not None:
                assert word & locked == old and check.allowed(word)
                assert all(word >> d & 1 == value for d, value in pins.items())
            return word

        yield complete


def extend(word, cut, check):
    original = word
    for row in cut["births"]:
        paid = row["consumed_names"]
        fresh = row["fresh_names"]
        count = bits(word, paid).count("1")
        if (check.law == "parity" and count % 2) or (check.law == "nae" and count == 0):
            word |= 1 << fresh[0]
    assert check.allowed(word)
    new = marks(n for row in cut["births"] for n in row["fresh_names"])
    assert original & new == 0 and word & ~new == original
    return word


def full_paired_witness(pre, g, choice, fourth, finish, checks):
    check_three, check_four, check_final = checks
    q, spare = choice["paid_q"], choice["spare_q"]
    hp = choice["paid_h"]
    assert bits(pre, (q, spare)) == "01" and check_three.allowed(pre)
    changed = pre ^ marks((q, spare))
    assert bits(changed, (q, spare)) == "10" and check_three.allowed(changed)
    arms = {}
    for label, word in (("I", pre), ("T", changed)):
        after = extend(word, fourth, check_four)
        end = extend(after, finish, check_final) if finish["status"] == "extend" else after
        assert bits(after, (hp, q)) == bits(end, (hp, q))
        assert bits(after, g["fresh_names"]) == bits(end, g["fresh_names"])
        arms[label] = {"cut_three_after": hex(word), "cut_four_after": hex(after),
                       "cut_five_after": hex(end) if finish["status"] == "extend" else None}
    return {"common_cut_three_state": hex(pre), "K_transposes": [q, spare], "arms": arms}


def count_fresh(law, incoming, width):
    if law == "parity":
        return 1 << (width - 1)
    return (1 << width) - int(incoming in ("00", "11"))


def readings(relation, law, width=None):
    """A full bank remains in every read, with exact multiplicities for G."""
    targets = ("whole_W", "W_i", "K_action", "whole_W_and_K_action", "W_i_and_K_action")
    response = {}
    for orientation, rows in relation.items():
        total = 0
        unique = dict.fromkeys(targets, 0)
        report = []
        for shown, possibilities in sorted(rows.items()):
            weights = 1 if width is None else count_fresh(law, shown, width)
            total += weights
            memberships = [sorted({entry[i] for entry in possibilities}) for i in range(len(targets))]
            for key, values in zip(targets, memberships, strict=True):
                if len(values) == 1:
                    unique[key] += weights
            report.append({"read": shown, "distinct_fresh_words": weights,
                           "possible_targets": dict(zip(targets, memberships, strict=True))})
        response[orientation] = {
            "complete_local_record_count": total,
            "uniquely_identifying_record_count": unique,
            "zero_error": {key: bool(total) and val == total for key, val in unique.items()},
            "record_support": report,
        }
    return response


def alternate_mode(law, named, mode, births, complete, fourth, fifth, checks):
    h, g = births[named["H"]], births[named["G"]]
    xi, y, hp, q, spare = (named[key] for key in ("old_R_name", "other_H_input", "paid_h", "paid_q", "spare_q"))
    pos = named["position"]
    private = h["fresh_names"]
    assert hp in private
    h_index = private.index(hp)
    possible_h = {}
    examples = []
    full_h = {key: defaultdict(set) for key in ("oriented", "anonymous", "fresh_only")}
    full_g = {key: defaultdict(set) for key in ("oriented", "anonymous")}
    impossibilities = []
    for w in map("".join, product("01", repeat=3)):
        old = dict(zip(W, map(int, w), strict=True))
        locked = {**old, q: 0, spare: 1}
        feasible = {}
        for values in product((0, 1), repeat=1 + len(private)):
            side, *fresh = values
            if mode == "calibrated" and (side or any(val for i, val in enumerate(fresh) if i != h_index)):
                continue
            pin = {**locked, y: side, **dict(zip(private, fresh, strict=True))}
            word = complete(pin)
            if word is None:
                continue
            hp_bit = fresh[h_index]
            if mode == "calibrated":
                assert hp_bit == old[xi] if law == "parity" else hp_bit or old[xi]
            feasible.setdefault(hp_bit, word)
            old_view = f"{old[xi]}{side}"
            fresh_view = "".join(map(str, fresh))
            for k_choice in ("I", "T"):
                feature = w[pos]
                assignment = (w, feature, k_choice, w + "|" + k_choice, feature + "|" + k_choice)
                full_h["oriented"][old_view + "|" + fresh_view].add(assignment)
                full_h["anonymous"]["".join(sorted(old_view)) + "|" + fresh_view].add(assignment)
                full_h["fresh_only"][fresh_view].add(assignment)
        possible_h[w] = sorted(feasible)
        for hp_bit in (0, 1):
            if hp_bit not in feasible:
                impossibilities.append({"W": w, "h": hp_bit})
                continue
            for q_value, k_choice in enumerate(("I", "T")):
                shown = f"{hp_bit}{q_value}"
                feature = w[pos]
                assignment = (w, feature, k_choice, w + "|" + k_choice, feature + "|" + k_choice)
                full_g["oriented"][shown].add(assignment)
                full_g["anonymous"]["".join(sorted(shown))].add(assignment)
            example = full_paired_witness(feasible[hp_bit], g, named, fourth, fifth, checks)
            examples.append({"W": w, "h": hp_bit, **example})
    raw_support = sorted({(int(w[pos]), hp) for w, bank in possible_h.items() for hp in bank})
    if mode == "calibrated":
        expected = {(0, 0), (1, 1)} if law == "parity" else {(0, 1), (1, 0), (1, 1)}
        assert set(raw_support) <= expected
    return {"paid_h_by_full_W": possible_h, "supported_W_i_and_h": raw_support,
            "unavailable_W_h": impossibilities, "whole_paired_examples": examples,
            "H_readings_with_its_finish": readings(full_h, law),
            "G_readings": readings(full_g, law, len(g["fresh_names"]))}


def alternate_law(module, law, selected, course, past, third, fourth, root_word, old_names):
    g = course["fourth"]["births"][selected["G"] - len(third)]
    named = selected
    fifth_board, fifth = paid_cut(module, fourth, law, 4096)
    final = fifth_board if fifth["status"] == "extend" else fourth
    assert g["holder"] == selected["G"]
    fourth_cut = course["fourth"]
    birth = {row["holder"]: row for row in past["cuts"][2]["births"] + fourth_cut["births"]}
    check = WordCheck(law, third), WordCheck(law, fourth), WordCheck(law, final)
    q, spare = named["paid_q"], named["spare_q"]
    k = birth[named["K"]]
    assert q in k["fresh_names"] and spare in k["fresh_names"]
    assert all(owners(third)[mark] == [named["K"]] for mark in (q, spare))
    assert named["paid_h"] in birth[named["H"]]["fresh_names"]
    assert not set(OLD_SOURCE).intersection((q, spare))
    with completions(law, third, root_word, old_names) as complete:
        ready_options = {}
        for w in map("".join, product("01", repeat=3)):
            bind = dict(zip(W, map(int, w), strict=True))
            ready_options[w] = ["".join(map(str, pair)) for pair in product((0, 1), repeat=2)
                                if complete({**bind, q: pair[0], spare: pair[1]}) is not None]
        modes = {mode: alternate_mode(law, named, mode, birth, complete, fourth_cut, fifth, check)
                 for mode in ("natural", "calibrated")}
    completion = receipt(g, owners(fourth), owners(final), fifth["births"]) if fifth["status"] == "extend" else None
    return {"G_actual_birth": g, "K_private_pair": [q, spare], "admissible_K_pairs_at_each_W": ready_options,
            "fifth": fifth, "G_own_finish": completion, "G_observation_end": "finish" if completion else "birth",
            "G_fresh_support_rule": (
                "For the reported inherited bits, the fresh word is any complete bank whose full "
                "birth row satisfies the named law. The entire bank is held and stable. The reported "
                "support count includes each such fresh word once for each disclosed inherited pair."
            ),
            "modes": modes}


def build():
    raw = {path: path.read_bytes() for path in SOURCES}
    assert {path: sha256(text).hexdigest() for path, text in raw.items()} == SOURCES
    growth = json.loads(gzip.decompress(raw[GROWTH]))
    words = json.loads(gzip.decompress(raw[WORDS]))
    prior = json.loads(raw[FOURTH])
    module = previous()
    courses = {}
    positions = {}
    for law in LAWS:
        courses[law] = {}
        for route in ROUTES:
            course, third, fourth = check_fourth(module, growth, prior, law, route)
            courses[law][route] = course
            positions[law, route] = third, fourth
    first = courses["parity"]["intact"]["fourth"]
    candidates = select(first, positions["parity", "intact"][0]) if first["status"] == "extend" else {
        "eligible": [], "excluded": [], "selected": None}
    alternate = {}
    if candidates["selected"] is not None:
        for law in LAWS:
            third, fourth = positions[law, "intact"]
            assert select(courses[law]["intact"]["fourth"], third) == candidates
            old = int(words["old_words"][f"{law}-00"]["common_before"], 16)
            assert bits(old, OLD_SOURCE) == "01"
            issued = [i for i in growth["original_name_order"] if old >> i & 1]
            assert bits(old, growth["original_name_order"]) == growth["common_original_words"][law]
            assert marks(issued) == old
            alternate[law] = alternate_law(module, law, candidates["selected"], courses[law]["intact"],
                                           growth["cases"]["intact"][law], third, fourth, old,
                                           growth["original_name_order"])
    return {"schema": "b309-successor-physical-control-v1",
            "input_sha256": {str(path.relative_to(ROOT)): digest for path, digest in SOURCES.items()},
            "courses": courses, "later_source_enrollment": candidates, "later_source_controls": alternate}


if __name__ == "__main__":
    data = json.dumps(build(), sort_keys=True, separators=(",", ":")).encode()
    OUTPUT.write_bytes(gzip.compress(data, compresslevel=9, mtime=0))
    print(sha256(OUTPUT.read_bytes()).hexdigest(), OUTPUT)
