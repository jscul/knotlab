"""Replay literal and parity-compensated value preparations on one physical trace."""

from collections import Counter
from dataclasses import replace
from fractions import Fraction
from functools import cache
from gzip import compress, decompress
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
DESIGN = ROOT / "research/STORED-BIT-AND-NEXT-ACTION-20261122-001/design_candidate.md"
DESIGN_HASH = "596dd60e5e8c79254855e7b609eb125f76d71307248963ee747d136430127d95"
PRIOR = ROOT / "research/SPARE-AND-NEXT-PAYMENT-20261122-001/same_prefix.json"
TRACE, = (ROOT / "artifacts/SPARE-AND-NEXT-PAYMENT-20261122-001A").glob("*/physical_trace.json.gz")
LIBRARY, = (ROOT / "experiments/SPARE-AND-NEXT-PAYMENT-20261122-001A").glob("*/check.py")
OLD_CHECK = run_path(str(LIBRARY))
H, R, COLLATERAL = 98, 111, 118
X, COMPENSATOR = 231, 232
COMPANIONS = (214, 217)
LITERAL_BACKGROUND = (183, 189, 232, 233)
COMPENSATED_BACKGROUND = (183, 189, 233)
R_FRESH = (263, 264)
LAWS = ("parity", "nae")


def bits(values):
    return "".join(map(str, values))


def pick(word, slots):
    return tuple(word[i] for i in slots)


def legal(law, word):
    n = sum(word)
    return n % 2 == 0 if law == "parity" else 0 < n < len(word)


@cache
def fresh_words(law, paid, width):
    return tuple(bank for bank in product((0, 1), repeat=width) if legal(law, paid + bank))


def valid(law, word, holdings):
    return all(legal(law, pick(word, holding)) for holding in holdings)


def replay(law, raw):
    frames = {1: tuple(map(tuple, raw["source"]))}
    cohorts = {}
    for size in range(2, 11):
        grown, births, _ = OLD_CHECK["append_cut"](frames[size - 1], law)
        if size <= 9:
            actual = [(b.knot, list(b.parents), list(b.paid), list(b.fresh), b.demand) for b in births]
            expected = [(b["knot"], b["parents"], b["paid"], b["fresh"], b["demand"])
                        for b in raw["cohorts"][str(size)]]
            assert actual == expected
        frames[size], cohorts[size] = grown, births
    return frames, cohorts


def extend(law, prefix, before, births, pins=None):
    """Write each independent fresh bank once, keeping every previous value."""
    pins = {} if pins is None else pins
    word, holdings = list(prefix), list(before)
    assert valid(law, word, holdings)
    for b in births:
        assert b.knot == len(holdings)
        assert b.fresh == tuple(range(len(word), len(word) + len(b.fresh)))
        allowed = fresh_words(law, pick(word, b.paid), len(b.fresh))
        bank = next((w for w in allowed if all(pins.get(i, a) == a for i, a in zip(b.fresh, w, strict=True))), None)
        if bank is None:
            raise ValueError(f"No lawful new word at holder {b.knot} for pins on {b.fresh}")
        holdings.append(b.holding)
        word.extend(bank)
    assert all(word[i] == a for i, a in pins.items())
    assert tuple(word[:len(prefix)]) == prefix and valid(law, word, holdings)
    return tuple(word)


def find_birth(rows, knot):
    return next(b for b in rows if b.knot == knot)


def payment_edges(rows, mark):
    row, = (b for b in rows if mark in b.paid)
    return {"mark": mark, "payer": row.parents[row.paid.index(mark)], "child": row.knot,
            "parents": row.parents, "paid": row.paid, "fresh": row.fresh, "demand": row.demand}


def physical_receipt(frames, cohorts):
    h = find_birth(cohorts[8], H)
    r = find_birth(cohorts[9], R)
    assert h.paid == (183, 189) and h.fresh == (231, 232, 233)
    assert (r.parents, r.paid, r.fresh) == ((90, 92, H), (*COMPANIONS, X), R_FRESH)
    nine = {str(mark): payment_edges(cohorts[9], mark) for mark in (*COMPANIONS, X, COMPENSATOR)}
    assert nine[str(COMPENSATOR)]["child"] == COLLATERAL
    ten = {str(mark): payment_edges(cohorts[10], mark) for mark in R_FRESH}
    assert [ten[str(mark)]["child"] for mark in R_FRESH] == [132, 134]
    owners = OLD_CHECK["owners"]
    assert owners(frames[8])[X] == (H,) and owners(frames[9])[X] == owners(frames[10])[X] == (H, R)
    for mark in R_FRESH:
        assert owners(frames[9])[mark] == (R,) and owners(frames[10])[mark] == (R, ten[str(mark)]["child"])
    stages = {size: {"status": "extend", "births": len(births), "every_birth_has_fresh_distinctions": all(b.fresh for b in births),
                     "new_distinctions": sum(len(b.fresh) for b in births), "refusal": False}
              for size, births in cohorts.items()}
    assert stages[10]["births"] == 24 and stages[10]["new_distinctions"] == 58
    return {"H_holding_at_eight": h.holding, "R_holding_at_nine": r.holding, "payments_into_size_nine": nine,
            "R_payments_into_size_ten": ten, "ordinary_stages": stages,
            "x_remains_held_by_R_after_its_own_payment": True,
            "full_size_ten_roster": [{"knot": b.knot, "parents": b.parents, "paid": b.paid,
                                      "fresh": b.fresh, "demand": b.demand} for b in cohorts[10]]}


def swapped_r_allocations(frames, cohorts):
    rows = cohorts[10]
    original_owner = OLD_CHECK["owners"](frames[10])
    switched = {a: b for a, b in zip(R_FRESH, reversed(R_FRESH), strict=True)}
    changed = tuple(replace(b, paid=tuple(switched.get(i, i) for i in b.paid)) for b in rows)
    swapped_holding = frames[9] + tuple(b.holding for b in changed)
    swapped_owner = OLD_CHECK["owners"](swapped_holding)
    assert {i for i in original_owner if original_owner[i] != swapped_owner[i]} == set(R_FRESH)
    for a, b in zip(rows, changed, strict=True):
        assert (a.knot, a.parents, a.fresh) == (b.knot, b.parents, b.fresh)
        if R in a.parents:
            assert all(x == y for i, (x, y) in enumerate(zip(a.paid, b.paid, strict=True)) if a.parents[i] != R)
        else:
            assert a == b
    return {"archived": rows, "swapped_R_private_marks": changed}


def support_description(support):
    predicates = {"fresh_parity": {a ^ b for a, b in support}, "fresh_equal": {a == b for a, b in support},
                  "at_least_one_fresh_one": {bool(a or b) for a, b in support},
                  "both_fresh_one": {bool(a and b) for a, b in support}}
    return {"full_support": sorted(map(bits, support)), "uniform_probability_per_fresh_word": Fraction(1, len(support)),
            "possible_values_263_and_264": [sorted({w[i] for w in support}) for i in range(2)],
            "probability_of_one_at_263_and_264": [Fraction(sum(w[i] for w in support), len(support)) for i in range(2)],
            "forced_predicates": {name: next(iter(values)) for name, values in predicates.items() if len(values) == 1}}


def available_background(law, frame, cohorts, early, background, companion, mode):
    marks = LITERAL_BACKGROUND if mode == "literal" else COMPENSATED_BACKGROUND
    given = dict(zip(marks, background, strict=True))
    end_seven = extend(law, early, frame[6], cohorts[7], {i: given[i] for i in (183, 189)})
    preps, unavailable = {}, {}
    for x in (0, 1):
        set_bits = {**given, X: x, **dict(zip(COMPANIONS, companion, strict=True))}
        if mode == "compensated_parity":
            # For x=0 this is the unique setting of 232. It reverses at x=1.
            set_bits[COMPENSATOR] = (sum(background) + x) % 2
        h_word = pick(set_bits, frame[8][H])
        if not legal(law, h_word):
            unavailable[str(x)] = {"H_word": bits(h_word), "reason": "old H law forbids this proposed prepayment word"}
            continue
        at_eight = extend(law, end_seven, frame[7], cohorts[8], set_bits)
        assert pick(at_eight, frame[8][H]) == h_word
        preps[x] = at_eight
    assert preps
    if len(preps) == 2:
        first, second = preps[0], preps[1]
        expected = {X} if mode == "literal" else {X, COMPENSATOR}
        changes = {i for i, (a, b) in enumerate(zip(first, second, strict=True)) if a != b}
        assert changes == expected and first[X] == 0 and second[X] == 1
        assert first[:len(end_seven)] == second[:len(end_seven)] == end_seven
    return preps, unavailable, end_seven


def future_witnesses(law, old, frames, cohorts, allocations, collateral_control):
    r = find_birth(cohorts[9], R)
    paid = pick(old, r.paid)
    support = fresh_words(law, paid, len(r.fresh))
    table = support_description(support)
    table["actual_inherited_R_word"] = bits(paid)
    table["retained_value_on_shared_231"] = old[X]
    assert table["possible_values_263_and_264"] == [[0, 1], [0, 1]]
    table["actual_value_paid_on_263_by_R_fresh_word"] = {bits(f): f[0] for f in support}
    archive = {"word_through_size_eight": bits(old), "supported_R_fresh_words": {}, "collateral_fresh_witnesses_if_compensated": {}}
    for f in support:
        at_nine = extend(law, old, frames[8], cohorts[9], dict(zip(R_FRESH, f, strict=True)))
        assert pick(at_nine, r.fresh) == f and at_nine[X] == old[X]
        successors = {}
        for name, births in allocations.items():
            at_ten = extend(law, at_nine, frames[9], births)
            assert pick(at_ten, r.fresh) == f and at_ten[X] == old[X]
            successors[name] = bits(at_ten)
            assert all(at_ten[mark] == value for mark, value in zip(r.fresh, f, strict=True))
        archive["supported_R_fresh_words"][bits(f)] = {"word_through_size_nine": bits(at_nine),
                                                      "words_through_size_ten_by_allocation": successors}
    if collateral_control:
        c = find_birth(cohorts[9], COLLATERAL)
        has = pick(old, c.paid)
        c_words = fresh_words(law, has, len(c.fresh))
        table["compensated_sibling_118"] = {"paid_word": bits(has), "fresh_support": sorted(map(bits, c_words)),
                                           "uniform_probability_per_word": Fraction(1, len(c_words))}
        for bank in c_words:
            at_nine = extend(law, old, frames[8], cohorts[9], dict(zip(c.fresh, bank, strict=True)))
            next_word = extend(law, at_nine, frames[9], allocations["archived"])
            assert pick(next_word, c.fresh) == bank
            archive["collateral_fresh_witnesses_if_compensated"][bits(bank)] = {
                "word_through_size_nine": bits(at_nine), "word_through_size_ten": bits(next_word)}
    return table, archive


def comparison(supports):
    if set(supports) != {"0", "1"}:
        return None
    left, right = (set(supports[str(x)]["full_support"]) for x in (0, 1))
    output = {"common_fresh_words": sorted(left & right), "exclusive_to_x0": sorted(left - right),
              "exclusive_to_x1": sorted(right - left), "individual_fresh_bit_forced": False,
              "any_change_in_R_payments_or_recipients_at_fixed_allocation": False}
    assert all(supports[str(x)]["possible_values_263_and_264"] == [[0, 1], [0, 1]] for x in (0, 1))
    return output


def summarize_settings(cells):
    grouped = {}
    for c, d in product((0, 1), repeat=2):
        pair = bits((c, d))
        rows = [row for row in cells.values() if row["other_R_inputs"] == pair]
        shared = [row["matched_comparison"] for row in rows if row["matched_comparison"]]
        if shared:
            assert all(r == shared[0] for r in shared)
        by_x = {str(x): [row["available_arms"][str(x)] for row in rows if str(x) in row["available_arms"]] for x in (0, 1)}
        assert all(all(s["full_support"] == options[0]["full_support"] for s in options) for options in by_x.values())
        grouped[pair] = {"backgrounds_tested": len(rows), "matched_backgrounds": len(shared),
                         "one_sided_x0": sum(set(row["available_arms"]) == {"0"} for row in rows),
                         "one_sided_x1": sum(set(row["available_arms"]) == {"1"} for row in rows),
                         "support_by_available_x": {x: o[0]["full_support"] if o else [] for x, o in by_x.items()},
                         "R_fresh_comparison_in_matched_backgrounds": shared[0] if shared else None}
    return grouped


def study(law, mode, frame, cohorts, initial, allocations):
    early = initial
    for size in range(2, 7):
        early = extend(law, early, frame[size - 1], cohorts[size])
    length = len(LITERAL_BACKGROUND if mode == "literal" else COMPENSATED_BACKGROUND)
    cells, bundle = {}, {}
    for background in product((0, 1), repeat=length):
        for companions in product((0, 1), repeat=2):
            name = f"{bits(background)}|{bits(companions)}"
            prepared, failed, seven = available_background(law, frame, cohorts, early, background, companions, mode)
            old_words, branches = {}, {}
            for x, old in prepared.items():
                old_words[str(x)], branches[str(x)] = future_witnesses(
                    law, old, frame, cohorts, allocations, collateral_control=mode == "compensated_parity")
            if mode == "compensated_parity":
                assert set(old_words) == {"0", "1"}
                one, two = (old_words[str(x)]["compensated_sibling_118"] for x in (0, 1))
                assert set(one["fresh_support"]).isdisjoint(two["fresh_support"])
                assert len(one["fresh_support"]) == len(two["fresh_support"]) == 4
            changes = [i for i, (a, b) in enumerate(zip(prepared[0], prepared[1], strict=True)) if a != b] if len(prepared) == 2 else []
            cells[name] = {"background_at_H": bits(background), "other_R_inputs": bits(companions),
                           "available_arms": old_words, "unavailable_preparations": failed,
                           "all_changed_mark_names_in_matched_preparation": changes if len(prepared) == 2 else None,
                           "matched_comparison": comparison(old_words), "receiver_physically_pays_263": True}
            bundle[name] = {"common_word_through_size_seven": bits(seven), "arms": branches}
    total = Counter(len(cell["available_arms"]) for cell in cells.values())
    assert total == (Counter({1: 64}) if law == "parity" and mode == "literal" else
                     Counter({2: 32}) if mode == "compensated_parity" else Counter({1: 8, 2: 56}))
    return {"strata_tested": len(cells), "matched_strata": total[2], "one_sided_strata": total[1],
            "unreachable_both_arms": 0, "by_other_R_inputs": summarize_settings(cells), "strata": cells}, bundle


def report_law(law, raw, prior):
    frames, cohorts = replay(law, raw)
    # Start with one archived lawful founding word, then build new matched continuations.
    archived = prior["extra"]["common_prefix_by_H_fresh_word"]
    for word_value in archived.values():
        assert valid(law, tuple(map(int, word_value)), frames[8])
    initial = tuple(map(int, archived["000"][:len(OLD_CHECK["owners"](frames[1]))]))
    assert valid(law, initial, frames[1])
    physical = physical_receipt(frames, cohorts)
    allocations = swapped_r_allocations(frames, cohorts)
    mode_names = ("literal", "compensated_parity") if law == "parity" else ("literal",)
    tests, worlds = {}, {}
    for mode in mode_names:
        tests[mode], worlds[mode] = study(law, mode, frames, cohorts, initial, allocations)
    physical["R_fresh_owner_routes_by_value_independent_allocation"] = {
        name: {str(mark): payment_edges(rows, mark) for mark in R_FRESH} for name, rows in allocations.items()}
    return {"physical": physical, "comparisons": tests}, worlds


def main():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_HASH
    traces = json.loads(decompress(TRACE.read_bytes()))
    prior = json.loads(PRIOR.read_text())
    reports, laws = {}, {}
    for law in LAWS:
        reports[law], laws[law] = report_law(law, traces[law]["loaded"], prior[law])
    assert reports["parity"]["physical"] == reports["nae"]["physical"]
    output = {"schema": "stored-bit-next-payment-v1", "laws": reports, "weighting":
              "For a fixed complete older word, choose each lawful fresh word with equal weight at each birth. No prior on older words.",
              "source_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                for p in (DESIGN, TRACE, PRIOR, LIBRARY, OLD_CHECK["OPERATOR"])}}
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / "results.json").write_text(json.dumps(output, default=str, sort_keys=True, indent=2) + "\n")
    witness_data = {"schema": "stored-bit-complete-words-v1", "bit_order": "ascending physical name starting at zero", "laws": laws}
    (OUTPUT / "worlds.json.gz").write_bytes(compress(json.dumps(witness_data, sort_keys=True, separators=(",", ":")).encode(), mtime=0))
    print(OUTPUT)


if __name__ == "__main__":
    main()
