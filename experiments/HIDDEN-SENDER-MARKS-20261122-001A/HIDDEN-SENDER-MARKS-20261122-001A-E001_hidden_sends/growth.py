"""Replay the enrolled ordinary payments and read the local finishing incidence."""

from collections import defaultdict
import gzip
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name / "growth.json.gz"
B305 = "TWO-SENDS-AND-GROWN-KEEPERS-20261122-001A"
B283 = "LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001B"
ORDINARY = ROOT / "artifacts" / B305 / (B305 + "-E001_two_sends") / "ordinary.json"
PHYSICAL = ROOT / "artifacts" / B283 / (B283 + "-E001_private_pulses") / "physical.json.gz"
FIXTURES = ROOT / "experiments/GENERATORS-20261120-001A/GENERATORS-20261120-001A-E001_generators/fixtures.py"
OPERATOR = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary/end_operator.py"
SOURCES = {
    ORDINARY: "c58ffc91241edb3bc797dc0a7b63bcaaa7f23d88ec9fd352ac558dabc3678d0e",
    PHYSICAL: "fc16f39c199ebad21c8d7dda47e6f76d1a589365f43c71d51080c525acf421e4",
    FIXTURES: "b4b4fe62f796ec138a48e08e1264e37264b0a964be44c8423c6890d888b50c49",
    OPERATOR: "cffce06049dee59029790d1668e34aa6efef0cd34cb34997379d0b9cbd4c3ece",
}
LAWS = ("parity", "nae")
CONDITIONS = ("intact", "interrupted", "sham")
MARKS = {"a": 510, "b": 563, "r": 677}
HOLDERS = {"S0": 80, "C": 162, "D": 163, "F": 164, "P": 165, "J": 292, "R": 294}


def load(path=OUTPUT):
    """Load the completed ordinary replay without running the allocator."""
    with gzip.open(path, "rt", encoding="utf-8") as stream:
        return json.load(stream)


def original_values(data, law):
    """Return the complete immutable prepared old word in physical coordinates."""
    return dict(zip(data["original_name_order"], map(int, data["common_original_words"][law]), strict=True))


def stars_at(data, condition, law, cut):
    """Recover the physical holdings at any completed cut, including the original."""
    cuts = data["cases"][condition][law]["cuts"]
    if not 0 <= cut <= len(cuts):
        raise ValueError(f"Cut {cut} is outside the saved replay")
    original = tuple(map(tuple, data["original_stars"]))
    return original + tuple(tuple(birth["consumed_names"] + birth["fresh_names"])
                            for layer in cuts[:cut] for birth in layer["births"])


def swap_label(name):
    if name == MARKS["a"]:
        return MARKS["r"]
    if name == MARKS["r"]:
        return MARKS["a"]
    return name


def fixture_module():
    spec = spec_from_file_location("b307_enrolled_legacy_fixture", FIXTURES)
    assert spec is not None and spec.loader is not None
    fixture = module_from_spec(spec)
    sys.modules[spec.name] = fixture
    spec.loader.exec_module(fixture)
    assert Path(fixture.step.__code__.co_filename).resolve() == OPERATOR
    return fixture


def incidence(stars):
    result = defaultdict(list)
    for holder, row in enumerate(stars):
        assert len(row) == len(set(row)) >= 3
        for name in row:
            result[name].append(holder)
    assert all(len(holders) in (1, 2) for holders in result.values())
    return result


def ordinary_plan(fixture, stars, law, age, priority=None):
    """Use the archived complete-cut plan and literal donor allocation."""
    plan = fixture.step(fixture.from_stars(stars), law, max_births=1024)
    assert plan.status == "extend" and not plan.shortages and not plan.implied, (age, law, plan)
    status, literal, _ = fixture.literal_turn(stars, law)
    assert status == plan.status and len(literal) == len(plan.parents)
    assert tuple(row.parents for row in literal) == plan.parents
    assert tuple(len(row.fresh) for row in literal) == plan.fresh
    if priority is not None:
        # A coherent recoding carries the old allocator order along with its coordinates.
        supply = defaultdict(list)
        for name, holders in incidence(stars).items():
            if len(holders) == 1:
                supply[holders[0]].append(name)
        queues = {holder: iter(sorted(names, key=priority)) for holder, names in supply.items()}
    births = []
    for row, demand in zip(literal, plan.demand, strict=True):
        marks = row.inputs if priority is None else tuple(next(queues[payer]) for payer in row.parents)
        births.append({"holder": row.knot, "parents": list(row.parents), "consumed_names": list(marks),
                       "fresh_names": list(row.fresh), "demand": demand, "grant": len(row.fresh)})
    if priority is not None:
        assert all(next(queue, None) is None for queue in queues.values())
    return {"age": age, "status": "extend", "births": births}


def materialize(stars, layer):
    """Independently verify actual unique funding and all-fresh completion."""
    before = incidence(stars)
    available = {name for name, holders in before.items() if len(holders) == 1}
    free_count = len(available)
    fresh_names = set()
    newborns = []
    donor_counts = defaultdict(int)
    for birth in layer["births"]:
        parents, paid, fresh = (birth[key] for key in ("parents", "consumed_names", "fresh_names"))
        assert birth["holder"] == len(stars) + len(newborns)
        assert parents and len(parents) == len(set(parents))
        assert len(fresh) == birth["grant"] == max(1, 3 - len(parents), birth["demand"])
        for donor, name in zip(parents, paid, strict=True):
            assert before[name] == [donor]
            available.remove(name)
            donor_counts[donor] += 1
        for name in fresh:
            assert name not in before and name not in fresh_names
            fresh_names.add(name)
        newborns.append(tuple(paid + fresh))
    assert not available
    grown = stars + tuple(newborns)
    after = incidence(grown)
    assert {name for name, row in after.items() if len(row) == 1} == fresh_names
    for birth in layer["births"]:
        for donor, name in zip(birth["parents"], birth["consumed_names"], strict=True):
            assert after[name] == [donor, birth["holder"]]
    # One separate fresh name per row extends any admitted old word in either law.
    layer.update(old_assignments_extend=True, total_loose_inputs=free_count,
                 paid_count_by_donor={str(holder): count for holder, count in sorted(donor_counts.items())})
    return grown


def first_cut(fixture, original, law, condition):
    if condition == "intact":
        return ordinary_plan(fixture, original, law, 1)
    enrolled = tuple(tuple(map(swap_label, row)) for row in original)
    assert list(map(set, enrolled)) == list(map(set, original))
    ranking = swap_label if condition == "sham" else None
    layer = ordinary_plan(fixture, enrolled, law, 1, priority=ranking)
    # The only temporary names moved are old names. Holder identifiers are physical.
    for birth in layer["births"]:
        for key in ("consumed_names", "fresh_names"):
            birth[key] = list(map(swap_label, birth[key]))
    return layer


def contributor_rows(birth):
    return [{"holder": parent, "distinction": name, "local_position": position}
            for position, (parent, name) in enumerate(zip(
                birth["parents"], birth["consumed_names"], strict=True
            ))]


def receiver_clocks(stages, cuts):
    indexed = {birth["holder"]: (i, birth) for i, cut in enumerate(cuts, 1) for birth in cut["births"]}
    owners = list(map(incidence, stages))
    receivers = {}
    for label in ("C", "D", "F", "P", "J", "R"):
        holder = HOLDERS[label]
        birth_cut, birth = indexed[holder]
        inherited, fresh = birth["consumed_names"], birth["fresh_names"]
        assert fresh and tuple(inherited + fresh) == stages[birth_cut][holder]
        anonymous = {}
        clock = []
        finish = None
        for age in range(birth_cut, len(stages)):
            partners = []
            for name in fresh:
                peers = set(owners[age][name]) - {holder}
                if peers:
                    peer, = peers
                    partners.append(anonymous.setdefault(peer, len(anonymous)))
                else:
                    partners.append(None)
            if not clock or partners != clock[-1]:
                clock.append(partners)
            if all(slot is not None for slot in partners):
                finish = age
                break
        assert finish == birth_cut + 1 and clock[0] == [None] * len(fresh) and len(clock) == 2
        payments = []
        for position, name in enumerate(fresh):
            child, = set(owners[finish][name]) - {holder}
            child_age, paid_birth = indexed[child]
            assert child_age == finish
            assert paid_birth["consumed_names"][paid_birth["parents"].index(holder)] == name
            payments.append({"fresh_position": position, "physical_name": name, "recipient": child,
                             "all_contributors": contributor_rows(paid_birth)})
        receivers[label] = {
            "holder": holder,
            "holding": inherited + fresh,
            "inherited_names": inherited,
            "fresh_names": fresh,
            "contributors": contributor_rows(birth),
            "local_clock": clock,
            "finish_payments": payments,
        }
    return receivers


def replay(fixture, original, law, condition):
    stages = [original]
    cuts = [first_cut(fixture, original, law, condition)]
    stages.append(materialize(original, cuts[0]))
    for age in (2, 3):
        layer = ordinary_plan(fixture, stages[-1], law, age)
        stages.append(materialize(stages[-1], layer))
        cuts.append(layer)
    return {"cuts": cuts, "receivers": receiver_clocks(stages, cuts)}


def archived_words(ordinary, source):
    names = sorted(incidence(source))
    words = {}
    sham = {}
    for law in LAWS:
        old = ordinary["ordinary_preconsumption_private_swap"][law]["original_and_first_cut_witness"]
        assert old["original_name_order"] == names
        word = old["common_initial_word"]
        values = dict(zip(names, map(int, word), strict=True))
        assert (values[MARKS["a"]], values[MARKS["b"]]) == (0, 1)
        assert all((sum(values[d] for d in row) % 2 == 0 if law == "parity"
                    else len({values[d] for d in row}) == 2) for row in source)
        transported = {swap_label(name): value for name, value in values.items()}
        assert {swap_label(name): value for name, value in transported.items()} == values
        words[law] = word
        sham[law] = "".join(str(transported[name]) for name in names)
    return names, words, sham


def verify_comparisons(cases, ordinary):
    for law in LAWS:
        intact, interrupted, sham = (cases[name][law] for name in CONDITIONS)
        assert intact == sham
        assert intact["cuts"][1:] == interrupted["cuts"][1:]
        archive = ordinary["actual_ordinary_cuts"]["intact"][law]
        for current, previous in zip(intact["cuts"][:2], archive, strict=True):
            assert current["births"] == [{k: v for k, v in row.items() if k != "input_projection"}
                                         for row in previous["births"]]
        original, rerouted = intact["cuts"][0], interrupted["cuts"][0]
        assert original.keys() == rerouted.keys()
        assert all(original[k] == rerouted[k] for k in original if k != "births")
        changed = {}
        for before, after in zip(original["births"], rerouted["births"], strict=True):
            assert before.keys() == after.keys()
            assert all(before[key] == after[key] for key in before if key != "consumed_names")
            if before["consumed_names"] != after["consumed_names"]:
                changed[before["holder"]] = before["consumed_names"], after["consumed_names"]
        assert changed == {HOLDERS["C"]: ([510, 515], [677, 515]),
                           HOLDERS["F"]: ([677, 720], [510, 720])}
        for receiver in ("R", "J", "P", "D"):
            assert intact["receivers"][receiver] == interrupted["receivers"][receiver]
        for receiver in ("C", "F"):
            assert intact["receivers"][receiver]["local_clock"] == interrupted["receivers"][receiver]["local_clock"]
        r = intact["receivers"]["R"]
        assert r["holding"] == [949, 957, 1754, 1755, 1756]
        assert [(p["holder"], p["distinction"]) for p in r["contributors"]] == [(162, 949), (165, 957)]
    for case in CONDITIONS:
        assert cases[case]["parity"] == cases[case]["nae"]


def build():
    """Run the frozen three cuts in all physical funding conditions."""
    blobs = {path: path.read_bytes() for path in SOURCES}
    assert {path: sha256(data).hexdigest() for path, data in blobs.items()} == SOURCES
    ordinary = json.loads(blobs[ORDINARY])
    prior = json.loads(gzip.decompress(blobs[PHYSICAL]))
    original = next(row for row in prior["cases"] if row["case"] == "intact")
    stars = tuple(map(tuple, original["original_stars"]))
    assert original["live_roles"]["S0"] == HOLDERS["S0"]
    assert original["loose_names"]["S0"] == list(MARKS.values())
    names, words, sham_words = archived_words(ordinary, stars)
    fixture = fixture_module()
    cases = {condition: {law: replay(fixture, stars, law, condition) for law in LAWS} for condition in CONDITIONS}
    verify_comparisons(cases, ordinary)
    return {
        "schema": "b307-ordinary-growth-v1",
        "source_sha256": {str(path.relative_to(ROOT)): digest for path, digest in SOURCES.items()},
        "original_stars": original["original_stars"],
        "physical_marks": MARKS,
        "physical_holders": HOLDERS,
        "original_name_order": names,
        "common_original_words": words,
        "coherent_sham": {
            "original_name_to_enrollment": {str(MARKS["a"]): MARKS["r"], str(MARKS["r"]): MARKS["a"]},
            "source_action_in_enrollment": [swap_label(MARKS["a"]), MARKS["b"]],
            "sender_payment_order_in_enrollment": list(map(swap_label, MARKS.values())),
            "complete_words_in_enrollment": sham_words,
            "receiver_fresh_instruments_in_enrollment": {
                label: list(map(swap_label, record["fresh_names"]))
                for label, record in cases["sham"]["parity"]["receivers"].items()
            },
        },
        "finish_readout": (
            "The local clock records the initial private bank and the next changed sharing pattern in "
            "order of owned fresh marks. None denotes private. Equal integer slots denote the same "
            "anonymous other holder. FINISH is the first batch in which every initially private mark "
            "is shared. Physical contributor and identity fields are available only to the scorer."
        ),
        "cases": cases,
    }


if __name__ == "__main__":
    encoded = json.dumps(build(), sort_keys=True, separators=(",", ":")).encode("utf-8")
    OUTPUT.write_bytes(gzip.compress(encoded, compresslevel=9, mtime=0))
    print(sha256(OUTPUT.read_bytes()).hexdigest(), OUTPUT)
