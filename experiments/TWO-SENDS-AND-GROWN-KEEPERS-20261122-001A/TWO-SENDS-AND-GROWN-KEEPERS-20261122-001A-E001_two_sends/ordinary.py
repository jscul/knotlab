"""Ordinary payments, earlier private receipts and an original-holder control."""

from collections import defaultdict
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
PRIOR_SCOPE = "LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001B"
PRIOR_FAMILY = PRIOR_SCOPE + "-E001_private_pulses"
PRIOR_CODE = ROOT / "experiments" / PRIOR_SCOPE / PRIOR_FAMILY
PRIOR_DATA = ROOT / "artifacts" / PRIOR_SCOPE / PRIOR_FAMILY
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "ordinary.json"
LAWS = ("parity", "nae")


def load_module(name):
    path = PRIOR_CODE / (name + ".py")
    spec = spec_from_file_location("two_sends_prior_" + name, path)
    assert spec is not None and spec.loader is not None
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


def read_archive(name):
    with gzip.open(PRIOR_DATA / name, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def normalized(value):
    """Use the persisted JSON representation for archive comparisons."""
    return json.loads(json.dumps(value))


def owners(stars):
    incidence = defaultdict(list)
    for holder, support in enumerate(stars):
        assert len(support) == len(set(support))
        for name in support:
            incidence[name].append(holder)
    assert all(len(holders) in (1, 2) for holders in incidence.values())
    return dict(incidence)


def check_cut(stars, cut):
    """Independently audit every actual payment and reconstruct the reached holdings."""
    assert cut["status"] == "extend" and not cut["shortages"] and cut["old_assignments_extend"]
    before = owners(stars)
    unused = {name for name, holders in before.items() if len(holders) == 1}
    newborns = []
    fresh_names = set()
    payments = defaultdict(list)
    for child in cut["births"]:
        holder = child["holder"]
        paid = tuple(child["consumed_names"])
        fresh = tuple(child["fresh_names"])
        parents = child["parents"]
        assert holder == len(stars) + len(newborns)
        assert len(parents) == 2 and len(set(parents)) == len(parents)
        assert len(fresh) == child["grant"] == max(1, 3 - len(parents), child["demand"])
        assert len(set(fresh)) == len(fresh) and not fresh_names.intersection(fresh)
        assert not before.keys() & set(fresh)
        assert list(child["input_projection"]) == list(range(1 << len(paid)))
        for payer, name in zip(parents, paid, strict=True):
            assert before[name] == [payer]
            unused.remove(name)
            payments[payer].append(name)
        fresh_names.update(fresh)
        newborns.append(paid + fresh)
    assert not unused
    recorded = {int(holder): sorted(names) for holder, names in cut["paid_names_by_donor"].items()}
    assert {holder: sorted(names) for holder, names in payments.items()} == recorded
    grown = stars + tuple(newborns)
    after = owners(grown)
    assert {name for name, holders in after.items() if len(holders) == 1} == fresh_names
    for child in cut["births"]:
        for payer, name in zip(child["parents"], child["consumed_names"], strict=True):
            assert after[name] == [payer, child["holder"]]
    return grown


def two_cuts(physical, case, archived=None):
    prepared, edits = physical.prepare(case)
    stars = prepared.immutable()
    by_law = {}
    if archived is not None:
        assert normalized(stars) == archived["original_stars"]
        assert normalized(edits) == archived["edits"]
    for law in LAWS:
        reached = stars
        ledger = []
        for cut_number in (1, 2):
            next_stars, cut = physical.literal_cut(reached, law, cut_number)
            assert next_stars == check_cut(reached, cut)
            if archived is not None:
                assert normalized(cut) == archived["laws"][law]["cuts"][cut_number - 1]
            ledger.append(cut)
            reached = next_stars
        by_law[law] = ledger
    assert [cut["births"] for cut in by_law["parity"]] == [cut["births"] for cut in by_law["nae"]]
    return stars, edits, by_law


def prior_receipts(native, earlier, receiver):
    """Replay the two enrolled private arrivals from their physical supports."""
    stars = tuple(map(tuple, native["original_stars"]))
    for law in LAWS:
        cuts = native["laws"][law]["cuts"]
        assert len(cuts) == 2
        first = check_cut(stars, cuts[0])
        check_cut(first, cuts[1])
    world = receiver.World(native)
    assert world.funded and earlier["funded"]
    result = []
    for number in (1, 2):
        word = world.pulse(number)
        sent = world.span_path(word)
        emission = earlier["sender"][f"U{number}"]
        private_roles = {world.role[f"S{i}"] for i in range(7)}
        assert set(word) == private_roles and world.labels(word) == emission["originals"]
        assert len(sent) == emission["rank"] == len(word)
        assert world.price(sent) == emission["grant"]
        assert normalized(world.slot_bind(sent)) == emission["native_parts"]
        assert normalized([row for _, row in world.discharge(sent, full=True)]) == emission["parents"]

        s = len(word)
        reception, _, receiving_arm = world.branched(s - 1, s)
        previous, _, _ = world.branched(s - 1, s - 1)
        assert reception - previous == {receiving_arm[-1]}
        assert world.labels(receiving_arm[-1][-2:]) == ["S6", "S0"]
        assert world.labels(word[-2:]) == ["S6", "S0"]
        width = world.count(word[-1], word[-2])
        actual = world.charge_record(reception, previous, word)
        saved = earlier["S"]["pulses"][str(number)]
        assert {
            key: normalized(value) for key, value in actual.items() if key != "parents"
        } == {key: saved[key] for key in actual if key != "parents"}
        for parent, archived_parent in zip(actual["parents"], saved["parents"], strict=True):
            assert normalized(parent) == {key: archived_parent[key] for key in parent}
        assert normalized(world.slot_bind(reception)) == saved["cross_ancestor_bindings"]
        assert actual["packet_occurrences"] == 1 and actual["selected_first"]
        assert actual["O_free_paying_incoming"] and not actual["all_O_parents_first"]
        assert width == saved["incoming_port"] == 4
        assert s == saved["send_size"] and actual["rank"] - s == saved["delay"]
        result.append({
            "audit_name": f"U{number}",
            "sender_occurrence_word": world.labels(word),
            "emission_size": s,
            "reception_size": actual["rank"],
            "parent_steps_to_reception": saved["delay"],
            "incoming_actual_owners": ["S6", "S0"],
            "arrival_shared_names_on_s0": sorted(world.port[word[-1], word[-2]]),
            "receiving_true_parents": actual["parents"],
            "paid_ancestors_through_two_literal_cuts": saved["cross_ancestor_bindings"],
        })
    lo, hi = (row["reception_size"] for row in result)
    ticks = [2 + 2 * i for i in range(1, len(world.r(result[-1]["emission_size"])) + 1)
             if lo < 2 + 2 * i <= hi and world.r(i)[-1] == world.p]
    assert ticks == earlier["S"]["interval"]["turns"]
    return {"literal_birth_counts": [len(c["births"]) for c in native["laws"]["parity"]["cuts"]],
            "private_receipts": result, "clock_returns_between_receipts": ticks}


def allowed(bits, law):
    if law == "parity":
        return sum(bits) % 2 == 0
    assert law == "nae"
    return len(set(bits)) == 2


def complete(values, support, law):
    free = [name for name in support if name not in values]
    values.update(dict.fromkeys(free, 0))
    bits = tuple(values[name] for name in support)
    if not allowed(bits, law):
        assert free
        values[free[0]] = 1 if law == "parity" else 1 - bits[0]
    assert allowed(tuple(values[name] for name in support), law)


def local_record(values, incidence, support):
    return [[name, values[name], incidence[name]] for name in support]


def word(values, names):
    return "".join(str(values[name]) for name in names)


def first_paid_swap(stars, roles, cut, law):
    """Compare a protected private exchange and idle on the same allowed word."""
    before = owners(stars)
    grown = check_cut(stars, cut)
    after = owners(grown)
    origin = roles["O"]
    sender = roles["S0"]
    support = stars[origin]
    sender_peers = roles["S1"], roles["S6"]
    by_parents = {frozenset(birth["parents"]): birth for birth in cut["births"]}
    children = [by_parents[frozenset((sender, peer))] for peer in sender_peers]
    paid_names = [birth["consumed_names"][birth["parents"].index(sender)] for birth in children]
    assert len(set(paid_names)) == 2 and all(before[name] == [sender] for name in paid_names)
    origin_birth = next(birth for birth in cut["births"] if origin in birth["parents"])
    origin_paid = origin_birth["consumed_names"][origin_birth["parents"].index(origin)]
    assert before[origin_paid] == [origin] and after[origin_paid] == [origin, origin_birth["holder"]]

    # Every earlier shared name joins a live original and a spent witness.
    # Thus spent supports are disjoint and later live rows can use private marks.
    live = {holders[0] for holders in before.values() if len(holders) == 1}
    spent = set(range(len(stars))) - live
    assert all(len(holders) == 1 or len(set(holders) & live) == 1 for holders in before.values())
    assert all(set(stars[holder]).difference(support) for holder in spent)
    assert {origin, sender} <= live and origin != sender
    assert not set(paid_names).intersection(support)
    assert any(before[name] == [sender] and name not in paid_names for name in stars[sender])

    lawful_origin_words = []
    old_names = tuple(sorted(before))
    fresh_names = tuple(sorted(after.keys() - before.keys()))
    a, b = paid_names
    example = None
    for bits in product((0, 1), repeat=len(support)):
        if not allowed(bits, law):
            continue
        initial = dict(zip(support, bits, strict=True))
        initial.update({a: 0, b: 1})
        for holder in sorted(spent) + sorted(live):
            complete(initial, stars[holder], law)
        assert initial.keys() == before.keys()
        swapped = {**initial, a: initial[b], b: initial[a]}
        assert all(allowed(tuple(swapped[name] for name in row), law) for row in stars)
        assert local_record(initial, before, support) == local_record(swapped, before, support)
        idle_after, swap_after = initial.copy(), swapped.copy()
        for row in grown[len(stars):]:
            complete(idle_after, row, law)
            complete(swap_after, row, law)
        assert idle_after.keys() == swap_after.keys() == after.keys()
        idle_record = local_record(idle_after, after, support)
        assert idle_record == local_record(swap_after, after, support)
        assert tuple(idle_after[name] for name in support) == bits
        assert tuple(idle_after[name] for name in paid_names) == (0, 1)
        assert tuple(swap_after[name] for name in paid_names) == (1, 0)
        lawful_origin_words.append(word(initial, support))

        if example is None and initial[origin_paid] == 1:
            example = {
                "original_name_order": old_names,
                "common_initial_word": word(initial, old_names),
                "fresh_name_order": fresh_names,
                "idle_first_cut_fresh_word": word(idle_after, fresh_names),
                "swap_first_cut_fresh_word": word(swap_after, fresh_names),
                "origin_local_before_both": local_record(initial, before, support),
                "origin_local_after_both": idle_record,
                "first_origin_payment": {
                    "name": origin_paid,
                    "value_before_and_after": initial[origin_paid],
                    "child": origin_birth["holder"],
                    "owners_before": before[origin_paid],
                    "owners_after": after[origin_paid],
                },
                "child_local_reads": [{
                    "holder": birth["holder"],
                    "parents": birth["parents"],
                    "sender_paid_name": name,
                    "owners_before": before[name],
                    "owners_after": after[name],
                    "idle": local_record(idle_after, after, grown[birth["holder"]]),
                    "swap": local_record(swap_after, after, grown[birth["holder"]]),
                } for birth, name in zip(children, paid_names, strict=True)],
            }
    assert example is not None
    return {"fixed_origin_holder": origin, "sender_holder": sender, "transposed_names": paid_names,
            "origin_name_order": support, "exact_origin_words_both_arms": lawful_origin_words,
            "original_and_first_cut_witness": example}


def audit():
    physical = load_module("physical")
    receiver = load_module("receiver")
    physical_archive = read_archive("physical.json.gz")
    receipt_archive = read_archive("receipts.json.gz")
    archive_sha = sha256((PRIOR_DATA / "physical.json.gz").read_bytes()).hexdigest()
    assert receipt_archive["physical_sha256"] == archive_sha
    archive = {row["case"]: row for row in physical_archive["cases"]}
    assert physical_archive["bound_source_hashes"][str((PRIOR_CODE / "physical.py").relative_to(ROOT))] == (
        sha256((PRIOR_CODE / "physical.py").read_bytes()).hexdigest()
    )
    previous = {case: prior_receipts(archive[case], receipt_archive["cases"][case], receiver)
                for case in ("intact", "near")}
    stars, _, intact = two_cuts(physical, physical.Case("intact"), archive["intact"])
    crossed, edits, interrupted = two_cuts(physical, physical.Case("position_eight", (8,)))
    assert len(edits) == 1 and edits[0]["site"] == 8
    assert len(crossed) == len(stars)
    roles = archive["intact"]["live_roles"]
    return {
        "schema": "b305-ordinary-two-sends-v1",
        "prior_inputs_sha256": {
            str(path.relative_to(ROOT)): sha256(path.read_bytes()).hexdigest()
            for path in (PRIOR_CODE / "physical.py", PRIOR_CODE / "receiver.py",
                         PRIOR_DATA / "physical.json.gz", PRIOR_DATA / "receipts.json.gz")
        },
        "earlier_native_receipts": previous,
        "earlier_receipt_boundary": (
            "U1 and U2 name supports in the audit. No packet label is an input to the receiving holder. "
            "The literal cuts bind the early paid incidences. Higher receipt ranks use the archived support "
            "and true-parent reconstruction."
        ),
        "actual_ordinary_cuts": {
            case: {law: [{"cut": step["age"], "births": step["births"],
                         "all_old_states_extend_via_independent_fresh_names": True}
                        for step in ledger] for law, ledger in data.items()}
            for case, data in (("intact", intact), ("interrupted_at_position_eight_only", interrupted))
        },
        "interrupted_actual_edits": edits,
        "ordinary_preconsumption_private_swap": {
            law: first_paid_swap(stars, roles, intact[law][0], law) for law in LAWS
        },
        "origin_support_scope": (
            "The exact claim uses only the original O and its own held names and incidences through "
            "the first complete cut. The sender swap fixes its entire original value word. Each live "
            "original other than O has a free private completion name even after the sender marks "
            "are fixed. Each new row has an independent fresh completion name. The two indicated "
            "children can read the change by their inherited mark identities."
        ),
    }


if __name__ == "__main__":
    out = audit()
    OUTPUT.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(sha256(OUTPUT.read_bytes()).hexdigest(), OUTPUT)
