"""Price readiness and retained evidence from the original lawful birth process."""
from __future__ import annotations

from collections import Counter, defaultdict
from dataclasses import dataclass
from fractions import Fraction
import gzip
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
BASE = "HIDDEN-SENDER-MARKS-20261122-001"
PREVIOUS = "REPEATED-SENDS-20261122-001"
W = (1754, 1755, 1756)
R = 294
AB = (510, 563)


@dataclass(frozen=True)
class Birth:
    holder: int
    parents: tuple[int, ...]
    paid: tuple[int, ...]
    fresh: tuple[int, ...]


def source_data():
    ledger, = (ROOT / "artifacts" / (BASE + "A")).glob("*/growth.json.gz")
    with gzip.open(ledger, "rt") as f:
        return json.load(f)


def archived_operator():
    spec = spec_from_file_location("earlier_fourth_cut", ROOT / "research" / PREVIOUS / "check_fixed_holder.py")
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def reconstruct(data, law):
    earlier = archived_operator()
    holdings = [tuple(row) for row in data["original_stars"]]
    births = []
    for cut in data["cases"]["intact"][law]["cuts"]:
        for row in cut["births"]:
            b = Birth(row["holder"], tuple(row["parents"]), tuple(row["consumed_names"]), tuple(row["fresh_names"]))
            assert b.holder == len(holdings)
            births.append(b)
            holdings.append(b.paid + b.fresh)
    before = earlier.owners(holdings)
    extended, fourth = earlier.append_fourth(holdings, law)
    later = []
    for j, (paid, fresh) in enumerate(fourth, len(holdings)):
        parents = tuple(before[n][0] for n in paid)
        assert all(len(before[n]) == 1 for n in paid)
        later.append(Birth(j, parents, paid, fresh))
    assert len(later) == 964 and all(b.fresh for b in later)
    by_id = {b.holder: b for b in births}
    successors = [next(b for b in births if mark in b.paid) for mark in W]
    assert [h.holder for h in successors] == [631, 633, 634]
    ids = {h.holder for h in successors}
    candidates = []
    for b in later:
        if len(b.parents) != 2:
            continue
        for i, h in enumerate(successors):
            if h.holder not in b.parents:
                continue
            k = by_id[next(p for p in b.parents if p != h.holder)]
            if len(k.fresh) >= 2:
                candidates.append((k.holder in ids, i, b.holder, k.holder))
    assert candidates
    _, i, receiver, sender = min(candidates)
    h, k, target = successors[i], by_id[sender], next(b for b in later if b.holder == receiver)
    h_mark = target.paid[target.parents.index(h.holder)]
    q = target.paid[target.parents.index(k.holder)]
    spare = min(set(k.fresh) - {q})
    assert h_mark in h.fresh and q in k.fresh and W[i] in h.paid
    u, = set(h.paid) - {W[i]}
    assert not set(AB).intersection(target.paid + target.fresh)
    return (births, holdings, extended, tuple(later), i, h, k, target, h_mark, q, spare, u, len(candidates))


def factor(law, incoming, size, observed):
    """Marginal mass of specified fresh slots, summing every unspecified completion."""
    m = len(observed)
    free = size - m
    if law == "parity":
        if free:
            return Fraction(1, 2**m)
        return Fraction(int((sum(incoming) + sum(observed)) % 2 == 0), 2**(size - 1))
    homogeneous = len(set(incoming)) == 1
    excluded = homogeneous and all(bit == incoming[0] for bit in observed)
    return Fraction(2**free - int(excluded), 2**size - int(homogeneous))


def distribution(law, births, old, targets, fixed):
    """Sum over each distinct ancestor once, forgetting each value after its last use."""
    target_set = set(targets)
    needed = target_set | fixed.keys()
    relevant = []
    for b in reversed(births):
        read = tuple(n for n in b.fresh if n in needed)
        if read:
            relevant.append((b, read))
            needed.update(b.paid)
    relevant.reverse()
    last = {n: len(relevant) for n in targets}
    for stage, (b, _) in enumerate(relevant):
        for n in b.paid:
            last[n] = max(last.get(n, -1), stage)
    assert all(old[n] == v for n, v in fixed.items() if n in old)
    live = ()
    states = {(): Fraction(1)}
    peak = 1
    for stage, (b, read) in enumerate(relevant):
        options = [(fixed[n],) if n in fixed else (0, 1) for n in read]
        after = tuple(n for n in (*live, *read) if last.get(n, -1) > stage)
        next_states = defaultdict(Fraction)
        for current, weight in states.items():
            bits = dict(zip(live, current, strict=True))
            incoming = tuple(old[n] if n in old else bits[n] for n in b.paid)
            for values in product(*options):
                mass = factor(law, incoming, len(b.fresh), values)
                if mass:
                    bits.update(zip(read, values, strict=True))
                    next_states[tuple(bits[n] for n in after)] += weight * mass
        states, live = dict(next_states), after
        peak = max(peak, len(states))
    assert set(live) == target_set
    order = [live.index(n) for n in targets]
    return ({tuple(bits[j] for j in order): v for bits, v in states.items()},
            {"relevant_births": len(relevant), "largest_partial_table": peak})


def best(pool):
    return sum(max(classes.values()) for classes in pool.values())


def score(mass, index, mode):
    """Bayes accuracies and certificates; all inputs are normalized on the named cohort."""
    tables = {name: defaultdict(Counter) for name in ("word", "retained_bit", "second_action", "bit_and_action")}
    for (word, h, action), weight in mass.items():
        if mode == "anonymous":
            obs = str(h + action)
        elif mode == "addressed":
            obs = str(h) + str(action)
        elif mode == "action_only":
            obs = str(action)
        elif mode == "none":
            obs = "*"
        else:
            raise ValueError(mode)
        truths = (word, word[index], str(action), word[index] + str(action))
        for table, truth in zip(tables.values(), truths, strict=True):
            table[obs][truth] += weight
    results = {}
    for name, table in tables.items():
        assert sum(sum(v.values()) for v in table.values()) == 1
        unique = {o: next(iter(d)) for o, d in table.items() if len(d) == 1}
        results[name] = {"accuracy": str(best(table)),
                         "certain_outcomes": unique,
                         "mass_of_certifying_outcomes": str(sum(sum(table[o].values()) for o in unique))}
    return results


def continuation_examples(law, holdings, extended, fourth, g):
    original = json.loads((ROOT / "research" / BASE / "cross_checks.json").read_text())
    witness = original[law]["intact"]["both_full_extensions"][1]
    word = int(witness["complete_words_after_each_cut_hex"][-1], 16)
    change = (1 << AB[0]) | (1 << AB[1])
    assert all(((word >> n) & 1) == v for n, v in zip(AB, (1, 0), strict=True))
    earlier = archived_operator()
    def failures(w):
        return [j for j, row in enumerate(holdings) if not earlier.legal(law, w, row)]
    assert not failures(word)
    illegal_after = failures(word ^ change)
    assert illegal_after == ([162, 163] if law == "parity" else [])
    new = earlier.extend_example(word, [(b.paid, b.fresh) for b in fourth], law)
    assert all(earlier.legal(law, new, row) for row in extended)
    if not illegal_after:
        assert all(earlier.legal(law, new ^ change, row) for row in extended)
    def read(w, names): return "".join(str(w >> n & 1) for n in names)
    return {"same_complete_pre_offer_hex": hex(word), "first_receipt_word": read(word, W),
            "requested_undo_refused_by_these_holders": illegal_after,
            "common_local_G_word": read(new, g.paid + g.fresh),
            "all_new_fourth_cut_coordinates_equal": True,
            "realized_undo": not illegal_after,
            "fourth_cut_keep_complete_word_hex": hex(new),
            "fourth_cut_after_request_complete_word_hex": hex(new if illegal_after else new ^ change)}


def analyse(data, law):
    births, holdings, grown, fourth, i, h, k, g, h_mark, q, spare, u, count = reconstruct(data, law)
    old = dict(zip(data["original_name_order"], map(int, data["common_original_words"][law]), strict=True))
    p_w, _ = distribution(law, births, old, W, {})
    baseline = json.loads((ROOT / "research" / BASE / "cross_checks.json").read_text())
    first = baseline[law]["intact"]["probability_by_word_keep_then_swap"]
    word_text = lambda bits: "".join(map(str, bits))
    assert {word_text(w): p for w, p in p_w.items()} == {w: Fraction(v[0]) for w, v in first.items()}
    out = {"selection": {"number_of_candidates": count, "old_R_bit_position_from_zero": i,
                         "first_successor": h.holder, "live_sender": k.holder, "later_receiver": g.holder,
                         "first_successor_paid_to_G": h_mark, "sender_paid_to_G": q, "sender_spare": spare,
                         "G_fresh_count": len(g.fresh), "H_other_old_input": u},
           "original_source_interventions": continuation_examples(law, holdings, grown, fourth, g)}
    ready = {q: 0, spare: 1}
    calibrated = {**ready, u: 0, **{n: 0 for n in h.fresh if n != h_mark}}
    for name, fixed in (("ready_only", ready), ("ready_and_H_calibration", calibrated)):
        raw, size = distribution(law, births, old, (*W, h_mark), fixed)
        price = sum(raw.values())
        assert 0 < price <= 1
        by_w = Counter()
        for val, weight in raw.items():
            by_w[val[:3]] += weight
        mass = {(word_text(val[:3]), val[3], action): z / (2 * price)
                for val, z in raw.items() for action in (0, 1)}
        assert sum(mass.values()) == 1
        out[name] = {"cohort_probability_per_original_launch": str(price),
                     "cohort_probability_given_W": {word_text(w): str(by_w[w] / p) for w, p in p_w.items()},
                     "joint_given_cohort_W_h_action": {f"{w}|{v}|{a}": str(p) for (w, v, a), p in mass.items()},
                     "scores": {mode: score(mass, i, mode) for mode in ("none", "action_only", "anonymous", "addressed")},
                     "exact_elimination": size}
    # For two paid inputs the new bank's kernel is identical for the two orientations of mixed bits.
    # All other local events are fixed by the holdings. Conditional on the read, no further term is needed.
    for t in product((0, 1), repeat=min(4, len(g.fresh))):
        assert factor(law, (0, 1), len(g.fresh), t) == factor(law, (1, 0), len(g.fresh), t)
    return out


if __name__ == "__main__":
    data = source_data()
    by_law = {law: analyse(data, law) for law in ("parity", "nae")}
    (HERE / "later_source_joint.json").write_text(json.dumps(by_law, indent=2) + "\n")
    for law, result in by_law.items():
        print(law, result["selection"])
        for key in ("ready_only", "ready_and_H_calibration"):
            r = result[key]
            print(key, r["cohort_probability_per_original_launch"], r["exact_elimination"],
                  {m: (s["retained_bit"]["accuracy"], s["second_action"]["accuracy"],
                       s["bit_and_action"]["accuracy"]) for m, s in r["scores"].items()})

