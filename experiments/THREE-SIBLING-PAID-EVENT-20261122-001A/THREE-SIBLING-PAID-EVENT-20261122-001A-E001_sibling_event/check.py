"""Exhaust the isolated four-place founder for the frozen B308 comparison."""

from collections import Counter, defaultdict
from fractions import Fraction
from gzip import compress, decompress
from hashlib import sha256
from itertools import product
import json
from pathlib import Path


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
DESIGN = ROOT / "research/THREE-SIBLING-PAID-EVENT-20261122-001/design_candidate.md"
DESIGN_HASH = "e0b646ef6772d11eae82fa98ad9896bf4e4da507d791494b611a015dc0e9409f"
ARCHIVE, = (ROOT / "artifacts/TWO-SENDS-AND-GROWN-KEEPERS-20261122-001B").glob("*/census.json.gz")
PAID = (0, 1, 2, 3)
FRESH = ((4, 5, 6), (7, 8, 9), (10, 11, 12), (13, 14, 15))
U, A, B, C = PAID
INVERTED = {B, C, *FRESH[B], *FRESH[C]}
BIT_WORDS = tuple(product((0, 1), repeat=3))
OUTCOMES = ("correct_bit", "wrong_bit", "silent", "refused", "invalid", "missing_recorder")


def word(bits):
    return "".join(map(str, bits))


def select(bits, marks):
    return tuple(bits[i] for i in marks)


def lawful(law, bits):
    ones = sum(bits)
    return ones % 2 == 0 if law == "parity" else 0 < ones < len(bits)


def word_lawful(law, bits, holdings):
    return all(lawful(law, select(bits, held)) for held in holdings.values())


def options(law, paid):
    return tuple(fresh for fresh in BIT_WORDS if lawful(law, (*paid, *fresh)))


def ownership(holdings):
    owners = defaultdict(list)
    for holder, held in holdings.items():
        for mark in held:
            owners[mark].append(holder)
    assert all(len(held) in (1, 2) for held in owners.values())
    return owners


def can_fund(holdings, births):
    owners = ownership(holdings)
    open_marks = {mark for mark, held in owners.items() if len(held) == 1}
    paid = Counter(mark for row in births for mark in row["paid"])
    if paid != Counter(open_marks):
        return False
    return all(owners[mark] == [payer] for row in births
               for mark, payer in zip(row["paid"], row["parents"], strict=True))


def extend_holdings(holdings, births):
    assert can_fund(holdings, births)
    next_holdings = dict(holdings)
    used = set(ownership(holdings))
    for row in births:
        assert row["holder"] not in next_holdings and not row["implied"]
        assert len(row["fresh"]) == row["demand"] and not used.intersection(row["fresh"])
        used.update(row["fresh"])
        next_holdings[row["holder"]] = (*row["paid"], *row["fresh"])
    return next_holdings


def recorded_stages(control):
    founder = {0: PAID}
    cut_1, cut_2 = control["transitions"][:2]
    assert cut_1["status"] == cut_2["status"] == "funded"
    first, second = cut_1["births"], cut_2["births"]
    assert len(first) == 4 and len(second) == 6
    for child, row in enumerate(first, 1):
        paid_index = child - 1
        assert row["holder"] == child and row["parents"] == [0]
        assert row["paid"] == [paid_index] and tuple(row["fresh"]) == FRESH[paid_index]
    reached = extend_holdings(founder, first)
    next_state = extend_holdings(reached, second)
    pre_owners, owners, next_owners = (ownership(stage) for stage in (founder, reached, next_state))
    assert all(pre_owners[mark] == [0] and owners[mark] == [0, mark + 1] for mark in PAID)
    assert all(owners[mark] == [1] and next_owners[mark][0] == 1 and len(next_owners[mark]) == 2
               for mark in FRESH[U])
    assert [next_owners[mark][1] for mark in FRESH[U]] == [5, 6, 7]
    omissions = {str(mark): {"would_keep_F": True, "would_keep_A": mark != A,
                              "ordinary_complete_funding": can_fund(founder, [r for r in first if r["paid"] != [mark]])}
                 for mark in (A, B, C)}
    assert not any(row["ordinary_complete_funding"] for row in omissions.values())
    report = {"founder_holding": founder, "first_cut_holdings": reached, "next_cut_holdings": next_state,
              "first_cut_births": len(first), "next_cut_births": len(second),
              "first_cut_single_simultaneous_funding": True,
              "payment_owners_at_launch": {mark: pre_owners[mark] for mark in PAID},
              "payment_owners_at_first_cut": {mark: owners[mark] for mark in PAID},
              "recorder_holding_at_birth": reached[2],
              "recorder_anonymous_birth_coholders_paid_then_fresh": [0, None, None, None],
              "F_original_private_marks_at_read_deadline": FRESH[U],
              "F_payments_next_complete_cut_same_funding": {mark: next_owners[mark][1] for mark in FRESH[U]},
              "single_sibling_contact_removal_controls": omissions}
    return report, reached, second, next_state


def event(full):
    return full[A] == full[B] == full[C]


def read(full):
    fresh = select(full, FRESH[A])
    return fresh[0] if fresh[0] == fresh[1] == fresh[2] else None


def interrupt(full):
    return tuple(value ^ (i in INVERTED) for i, value in enumerate(full))


def confirm_kernel(law, group, a):
    actual = Counter(word(select(full, FRESH[A])) for full in group)
    total = actual.total()
    expected = {word(fresh): Fraction(1, len(options(law, (a,)))) for fresh in options(law, (a,))}
    if not total:
        return {"available_words": 0, "bank_counts": {}, "conditional_A_fresh_law": None}
    measured = {fresh: Fraction(count, total) for fresh, count in sorted(actual.items())}
    assert measured == expected
    return {"available_words": total, "bank_counts": actual, "conditional_A_fresh_law": measured}


def tally(group, original_launches):
    event_counts = {name: dict.fromkeys(OUTCOMES, 0) for name in ("E_true", "E_false")}
    report_values = dict.fromkeys(("0", "1", "silent"), 0)
    for full in group:
        signal = read(full)
        truth = "E_true" if event(full) else "E_false"
        outcome = "silent" if signal is None else "correct_bit" if signal == full[U] else "wrong_bit"
        event_counts[truth][outcome] += 1
        report_values["silent" if signal is None else str(signal)] += 1
    counts = {outcome: sum(row[outcome] for row in event_counts.values()) for outcome in OUTCOMES}
    counts.update({"enrolled": len(group), "first_cut_completed": len(group), "recorder_available": len(group),
                   "event_true": sum(event_counts["E_true"].values()), "event_false": sum(event_counts["E_false"].values()),
                   "true_event_indications": event_counts["E_true"]["correct_bit"] + event_counts["E_true"]["wrong_bit"],
                   "false_event_indications": event_counts["E_false"]["correct_bit"] + event_counts["E_false"]["wrong_bit"]})
    assert sum(counts[outcome] for outcome in OUTCOMES) == len(group)
    return {"counts": counts, "event_truth_by_bit_outcome": event_counts, "report_counts": report_values,
            "F_fresh_word_support": sorted({word(select(full, FRESH[U])) for full in group}),
            "mass_per_original_launch": {key: Fraction(count, original_launches) for key, count in counts.items()},
            "probability_given_stratum": {key: Fraction(count, len(group)) for key, count in counts.items()} if group else None}


def stratify(law, cohort, original_launches):
    by_u = defaultdict(list)
    by_u_f = defaultdict(list)
    by_u_a_f = defaultdict(list)
    for full in cohort:
        u, a = full[U], full[A]
        f = select(full, FRESH[U])
        by_u[u].append(full)
        by_u_f[u, f].append(full)
        by_u_a_f[u, a, f].append(full)
    result = {"all": tally(cohort, original_launches), "by_u": {}, "by_u_F": {}, "A_kernel_by_u_a_F": {}}
    for u in (0, 1):
        assert {select(full, FRESH[U]) for full in by_u[u]} == set(options(law, (u,)))
        result["by_u"][str(u)] = tally(by_u[u], original_launches)
        for f in options(law, (u,)):
            f_key = f"{u}|{word(f)}"
            result["by_u_F"][f_key] = tally(by_u_f[u, f], original_launches)
            for a in (0, 1):
                key = f"{u}|{a}|{word(f)}"
                result["A_kernel_by_u_a_F"][key] = confirm_kernel(law, by_u_a_f[u, a, f], a)
    return result


def continuations(law, initial, rows, final_holdings):
    current = list(initial)
    for row in rows:
        paid = select(current, row["paid"])
        fresh = next(bank for bank in product((0, 1), repeat=len(row["fresh"])) if lawful(law, paid + bank))
        assert row["fresh"] == list(range(len(current), len(current) + len(fresh)))
        current.extend(fresh)
    assert tuple(current[:len(initial)]) == initial and word_lawful(law, current, final_holdings)
    return word(current)


def witness(law, initial, reached, next_cut, final_holdings):
    changed = interrupt(initial)
    assert event(initial) and not event(changed)
    assert all(select(initial, reached[i]) == select(changed, reached[i]) for i in (1, 2))
    assert read(initial) == read(changed)
    return {"u": initial[U], "unchanged_F_full": word(select(initial, reached[1])),
            "unchanged_A_full": word(select(initial, reached[2])), "report_under_both": read(initial),
            "intact": {"E_at_funding": True, "P_before": word(initial[:4]), "complete_at_cut_1": word(initial),
                       "complete_at_cut_2_after_answer_deadline": continuations(law, initial, next_cut, final_holdings)},
            "interrupted": {"E_at_funding": False, "P_before": word(changed[:4]), "complete_at_cut_1": word(changed),
                            "complete_at_cut_2_after_answer_deadline": continuations(law, changed, next_cut, final_holdings)}}


def complete_read_support(law, population, reached):
    support = defaultdict(Counter)
    for full in population:
        record = word(select(full, reached[2]))
        support[record][f"u={full[U]},E={int(event(full))}"] += 1
    for record, counts in support.items():
        a = int(record[0])
        target_keys = {"u=0,E=0", "u=1,E=0"}
        target_keys.update(f"u={u},E=1" for u in (0, 1) if lawful(law, (u, a, a, a)))
        assert set(counts) == target_keys
    return {"common_history": "one inherited shared distinction, three simultaneously fresh private distinctions",
            "A_full_word_to_true_bit_and_event_counts": dict(sorted(support.items())),
            "bit_certifying_A_full_words": [], "event_certifying_A_full_words": []}


def full_conditioning_check(law, population):
    """Vary A's fresh bank freely with every other physical distinction fixed."""
    other_names = sorted(set(range(16)) - set(FRESH[A]))
    by_rest = defaultdict(set)
    for full in population:
        by_rest[select(full, other_names)].add(select(full, FRESH[A]))
    a_index = other_names.index(A)
    assert all(words == set(options(law, (rest[a_index],))) for rest, words in by_rest.items())
    return {"fixed_physical_names": other_names, "number_of_distinct_lawful_fixed_words": len(by_rest),
            "conditional_A_fresh_law_given_every_other_bit": {
                str(a): {word(fresh): Fraction(1, len(options(law, (a,)))) for fresh in options(law, (a,))}
                for a in (0, 1)}}


def run_law(control):
    law = control["law"]
    physical, reached, cut_2, final = recorded_stages(control)
    population = tuple(full for full in product((0, 1), repeat=16) if word_lawful(law, full, reached))
    n_launch = len(population)
    old_words = Counter(full[:4] for full in population)
    local_counts = {u: len(options(law, (u,))) for u in (0, 1)}
    assert local_counts[0] == local_counts[1]
    assert [len(old_words), n_launch] == control["independent_source_and_first_cut_word_counts"]
    assert set(old_words.values()) == {local_counts[0] ** 4}
    assert Fraction(1, len(old_words) * local_counts[0] ** 4) == Fraction(1, n_launch)
    complete = set(population)
    intact = tuple(full for full in population if event(full))
    image = tuple(interrupt(full) for full in intact)
    image_set = set(image)
    assert len(image_set) == len(intact) and image_set.issubset(complete)
    assert all(interrupt(new) == full and not event(new) for full, new in zip(intact, image, strict=True))
    assert all(all(select(old, reached[i]) == select(new, reached[i]) for i in (1, 2))
               for old, new in zip(intact, image, strict=True))
    assert all(all(select(new, reached[i]) == tuple(1 - b for b in select(old, reached[i])) for i in (3, 4))
               for old, new in zip(intact, image, strict=True))
    assert all(read(old) == read(new) for old, new in zip(intact, image, strict=True))
    outside_image = tuple(full for full in population if not event(full) and full not in image_set)
    assert len(population) == len(intact) + len(image) + len(outside_image)
    unavailable_unanimous_preimages = sum(event(interrupt(full)) and interrupt(full) not in complete for full in outside_image)
    cohorts = {name: stratify(law, c, n_launch) for name, c in
               (("all_original_launches", population), ("paired_intact", intact),
                ("paired_interrupted_image", image), ("mixed_outside_image", outside_image))}
    assert cohorts["paired_intact"]["A_kernel_by_u_a_F"] == cohorts["paired_interrupted_image"]["A_kernel_by_u_a_F"]
    witnesses = {}
    for u in (0, 1):
        for label, answer in (("correct", u), ("silent", None)):
            initial = next(full for full in intact if full[U] == u and read(full) == answer)
            witnesses[f"u={u},{label}"] = witness(law, initial, reached, cut_2, final)
    result = {"scope": {"all_original_founders": len(old_words), "full_binary_candidates_checked": 1 << 16,
                        "lawful_complete_launches": n_launch, "per_founder_launch_counts": {word(k): v for k, v in old_words.items()},
                        "conditional_fresh_completion_count_for_every_unary_child": local_counts,
                        "equiprobable_complete_launch_mass": Fraction(1, n_launch)},
              "physical": physical, "cohorts": cohorts, "unselected_local_support": complete_read_support(law, population, reached),
              "full_conditioning_check": full_conditioning_check(law, population),
              "paired_local_histories_identical": len(intact), "paired_interrupted_changed_names": sorted(INVERTED),
              "mixed_words_with_unlawful_unanimous_inverse": unavailable_unanimous_preimages,
              "representative_pairs_with_complete_trajectories": witnesses}
    return result, [[word(old), word(new)] for old, new in zip(intact, image, strict=True)]


def main():
    design_bytes = DESIGN.read_bytes()
    archive_bytes = ARCHIVE.read_bytes()
    assert sha256(design_bytes).hexdigest() == DESIGN_HASH
    metadata = {str(DESIGN.relative_to(ROOT)): DESIGN_HASH, str(ARCHIVE.relative_to(ROOT)): sha256(archive_bytes).hexdigest()}
    archive = json.loads(decompress(archive_bytes))
    controls = [r for r in archive["records"] if r["source"] == "control-isolated-four"]
    assert {r["law"] for r in controls} == {"parity", "nae"} and len(controls) == 2
    results, paired = {}, {}
    for control in controls:
        law = control["law"]
        results[law], paired[law] = run_law(control)
    assert results["parity"]["physical"] == results["nae"]["physical"]
    OUTPUT.mkdir(parents=True, exist_ok=True)
    report = {"schema": "b308-three-sibling-paid-event-v1", "source_sha256": metadata, "laws": results}
    (OUTPUT / "results.json").write_text(json.dumps(report, default=str, sort_keys=True, indent=2) + "\n")
    rows = {"bit_order": list(range(16)), "pair_order": ["intact", "interrupted"], "laws": paired}
    packed = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()
    (OUTPUT / "paired_words.json.gz").write_bytes(compress(packed, mtime=0))
    print(OUTPUT)


if __name__ == "__main__":
    main()
