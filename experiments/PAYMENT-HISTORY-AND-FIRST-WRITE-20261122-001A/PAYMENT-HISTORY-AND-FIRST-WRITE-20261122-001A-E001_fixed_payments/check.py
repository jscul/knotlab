"""Check fresh extensions after fixing every physical payment in a quiet cut."""

from collections import Counter, defaultdict
from hashlib import sha256
from itertools import product
from math import prod
import json
from pathlib import Path
from runpy import run_path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
DESIGN = ROOT / "research/PAYMENT-HISTORY-AND-FIRST-WRITE-20261122-001/design_candidate.md"
DESIGN_HASH = "f5988ad2ab10ba8311b7c546dae745a442a9c7571be961045dbb1dbffa6734c6"
OLD_CHECK, = (ROOT / "experiments/WRITTEN-BIT-AND-JOIN-VETO-20261122-001A").glob("*/check.py")
ARCHIVE, = (ROOT / "artifacts/QUIET-START-AND-FIRST-WRITE-20261122-001A").glob("*/results.json")
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "results.json"
OLD = run_path(str(OLD_CHECK))
State = OLD["State"]
bits = OLD["bits"]
lawful = OLD["lawful"]


def owners(holdings):
    by_mark = defaultdict(list)
    for holder, row in enumerate(holdings):
        for mark in row:
            by_mark[mark].append(holder)
    assert all(len(held) in (1, 2) for held in by_mark.values())
    return by_mark


def fixed_bank(law, transport, before, birth):
    old_word = tuple(before.actual[i] for i in birth.paid)
    assert old_word == tuple(before.reference[i] for i in birth.paid)
    legal = tuple(bank for bank in product((0, 1), repeat=len(birth.fresh)) if lawful(law, old_word + bank))
    assert legal
    reference = legal[0]
    if transport == "opposite" and len(set(old_word)) == 1:
        reference = (1 - old_word[0],) * len(birth.fresh)
    assert reference in legal
    return legal, reference


def closing_receipt(before, births):
    row, = births
    assert not row.fresh
    current = owners(before.holdings)
    spent = {mark for mark, holding in current.items() if len(holding) == 1}
    shared = {mark for mark, holding in current.items() if len(holding) == 2}
    assert set(row.paid) == spent and len(row.paid) >= 3
    for word in (before.actual, before.reference):
        old_total = sum(word[i] for holding in before.holdings for i in holding)
        assert old_total - 2 * sum(word[i] for i in shared) == sum(word[i] for i in row.paid)
        assert sum(word[i] for i in row.paid) % 2 == 0
    return {"all_current_loose_names_consumed": sorted(spent), "already_shared_names_counted_twice": sorted(shared),
            "actual_boundary_word": bits(before.actual[i] for i in row.paid),
            "reference_boundary_word": bits(before.reference[i] for i in row.paid),
            "only_fresh_word": ""}


def examine_bound_cut(law, transport, before, births, planned):
    assert before.actual == before.reference
    current = owners(before.holdings)
    all_paid = [mark for b in births for mark in b.paid]
    all_fresh = [mark for b in births for mark in b.fresh]
    assert len(all_paid) == len(set(all_paid))
    assert set(all_paid) == {mark for mark, hs in current.items() if len(hs) == 1}
    assert len(all_fresh) == len(set(all_fresh)) and not set(current).intersection(all_fresh)
    local = tuple(fixed_bank(law, transport, before, b) for b in births)
    banks = tuple(allowed for allowed, _ in local)
    references = tuple(ref for _, ref in local)
    assert tuple((r, (r,)) for r in references) == OLD["factors"](law, transport, before, births)
    is_closing = planned["implied_parity_closure"]
    quiet = OLD["materialize"](law, before, births, references, references)
    after = owners(quiet.holdings)
    projection_by_other_words = [defaultdict(set) for _ in births]
    actual_count = 0
    # Any whole extension restricts to these bank factors. Verify the full converse.
    for candidate in product(*banks):
        state = OLD["materialize"](law, before, births, references, candidate)
        assert state.holdings == quiet.holdings and state.reference == quiet.reference
        assert state.actual[:len(before.actual)] == before.actual
        for i, record in enumerate(projection_by_other_words):
            record[candidate[:i] + candidate[i + 1:]].add(candidate[i])
        actual_count += 1
    assert actual_count == prod(len(words) for words in banks)
    assert quiet.actual == quiet.reference
    receipt = []
    for b, (allowed, ref), projection in zip(births, local, projection_by_other_words, strict=True):
        assert all(set(allowed) == fiber for fiber in projection.values())
        payments = []
        for parent, mark in zip(b.parents, b.paid, strict=True):
            assert current[mark] == [parent] and after[mark] == [parent, b.holder]
            assert quiet.actual[mark] == before.actual[mark]
            payments.append({"payer": parent, "mark": mark, "value": before.actual[mark],
                             "old_owners": current[mark], "new_owners": after[mark]})
        assert all(after[mark] == [b.holder] for mark in b.fresh)
        forced = {mark: ref[i] for i, mark in enumerate(b.fresh) if len({w[i] for w in allowed}) == 1}
        receipt.append({**OLD["serialize_birth"](b), "paid_physical_assignments": payments, "reference_fresh_word": bits(ref),
                        "lawful_fresh_words_at_all_fixed_sibling_words": list(map(bits, allowed)),
                        "number_of_lawful_fixed_sibling_assignments": len(projection),
                        "absolute_bits_forced_to_reference": forced})
    assert all(after[m] == hs for m, hs in current.items() if len(hs) == 2)
    shared_parent = Counter(parent for b in births for parent in b.parents)
    report = {"fixed_older_holdings": before.holdings, "fixed_older_actual_and_reference": bits(before.actual),
              "all_bound_births": receipt, "joint_fresh_support_count": actual_count,
              "joint_reference_word_available": True, "one_quiet_whole_extension": bits(quiet.actual),
              "actual_payment_obligations_by_old_holder": dict(shared_parent),
              "number_of_loose_distinctions_after": sum(len(v) == 1 for v in after.values()),
              "closing": closing_receipt(before, births) if is_closing else None}
    return quiet, report


def paid_signatures(births):
    return tuple((b.parents, b.paid) for b in births)


def replay_setting(law, reference, transport):
    start = State(OLD["FOUNDER"], reference, reference)
    paths = {(): start}
    report = {}
    for n in (1, 2, 3):
        reached = {}
        records = {}
        for past, before in paths.items():
            planned = OLD["plan"](law, before, True)
            ordinary = OLD["plan"](law, before, False)
            assert planned == ordinary and planned["status"] == "extend"
            choices = OLD["binding_options"](before)
            bound = tuple(OLD["bind"](before, planned, case) for case in choices)
            assert len(set(map(paid_signatures, bound))) == len(choices)
            if n == 1:
                assert len(choices) == 6 and len(set(planned["parent_roster"])) == 1
                # Keeping the founder names, the three unary recipients can be
                # renamed to match exactly by which mark each receives.
                normalized = {tuple(sorted((b.parents, b.paid, len(b.fresh)) for b in roster)) for roster in bound}
                assert len(normalized) == 1
            elif n == 2:
                assert len(choices) == 8 and set(planned["parent_roster"]) == {(1, 2), (1, 3), (2, 3)}
                assert all(Counter(p for b in rows for p in b.parents) == {1: 2, 2: 2, 3: 2} for rows in bound)
            else:
                assert len(choices) == 1 and len(planned["parent_roster"]) == 1
                assert planned["implied_parity_closure"] == (law == "parity")
                assert planned["fresh_grants"] == ((0,) if law == "parity" else (1,))
            for index, roster in enumerate(bound):
                key = (*past, index)
                quiet, receipt = examine_bound_cut(law, transport, before, roster, planned)
                reached[key] = quiet
                records["/".join(map(str, key))] = receipt
        paths = reached
        report[str(n)] = {"admitted_payment_histories": len(records), "per_bound_history": records,
                          "joint_support_size_histogram": Counter(r["joint_fresh_support_count"] for r in records.values())}
    assert [report[str(n)]["admitted_payment_histories"] for n in (1, 2, 3)] == [6, 48, 48]
    assert all(not OLD["loose_names"](s.holdings) for s in paths.values()) == (law == "parity")
    return {"law": law, "fixed_reference_transport": transport, "founding_actual_and_reference": bits(reference),
            "quiet_cut_receipts": report, "first_cut_unary_display_renaming_classes": 1,
            "second_cut_distinct_fixed_old_payment_allocations_per_reached_prefix": 8,
            "same_lawful_quiet_continuation_available_in_every_bound_cut": True,
            "no_loose_distinctions_after_third_cut": law == "parity"}


def verify_archived_extension(law, old_holdings, old_actual, old_reference, cut):
    old_owners = owners(old_holdings)
    assert sorted(i for b in cut["births"] for i in b["paid"]) == sorted(i for i, hs in old_owners.items() if len(hs) == 1)
    assert all(old_owners[i] == [holder] for b in cut["births"]
               for holder, i in zip(b["parents"], b["paid"], strict=True))
    actual, reference = cut["complete_actual"], cut["reference"]
    assert actual.startswith(old_actual) and reference.startswith(old_reference)
    grown = old_holdings + tuple(tuple(b["paid"] + b["fresh"]) for b in cut["births"])
    OLD["check_state"](law, State(grown, tuple(map(int, actual)), tuple(map(int, reference))))
    return grown, actual, reference


def archived_physical_examples(archive):
    entries = {}
    for name, report in archive["replay"].items():
        law = report["law"]
        controls = report["controlled_examples_by_policy"]["F"]
        joined, vetoed, *_ = controls["controlled_traces_varying_all_H_words"]
        missing = controls["H_alone_with_U_J_reference_words"][0]
        assert joined["target_read"]["outcome"] == "join"
        assert vetoed["target_read"]["outcome"] == "veto_with_H_payment_deviation"
        assert missing["target_read"]["outcome"] == "missing"
        assert vetoed["target_read"]["parents"] == joined["target_read"]["parents"]
        assert vetoed["guard_off_at_same_reached_stage"]["actual_target_join"]["parents"] == vetoed["target_read"]["parents"]
        context = {"joined": joined, "vetoed": vetoed, "target_missing": missing}
        for trial in context.values():
            stars = OLD["FOUNDER"]
            actual = reference = report["initial_actual_and_reference"]
            for cut in ("first_cut", "second_cut"):
                stars, actual, reference = verify_archived_extension(law, stars, actual, reference, trial[cut])
            for cut in ("third_cut", "guard_off_at_same_reached_stage"):
                verify_archived_extension(law, stars, actual, reference, trial[cut])
        entries[name] = {"archive_owned_by_prior_study": True, "archive_selector": "representative F controls",
                         "first_H_U_J_bank_words_by_control": {k: t["first_H_U_J_fresh_words"] for k, t in context.items()},
                         "joined": joined["target_read"], "vetoed": vetoed["target_read"],
                         "same_reached_stage_guard_off_restored": vetoed["guard_off_at_same_reached_stage"]["actual_target_join"],
                         "target_missing": missing["target_read"]}
    return entries


def main():
    assert sha256(DESIGN.read_bytes()).hexdigest() == DESIGN_HASH
    memo = {name: replay_setting(*params) for name, params in OLD["SETTINGS"].items()}
    out = {"schema": "fixed-payments-first-write-v1", "settings": memo,
           "archived_causal_control_examples": archived_physical_examples(json.loads(ARCHIVE.read_text())),
           "provenance_sha256": {str(p.relative_to(ROOT)): sha256(p.read_bytes()).hexdigest()
                                 for p in (DESIGN, OLD_CHECK, ARCHIVE, OLD["OPERATOR"], OLD["GUARD"])}}
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(json.dumps(out, sort_keys=True, separators=(",", ":")) + "\n")
    print(OUTPUT)


if __name__ == "__main__":
    main()
