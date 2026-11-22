"""Replay the original payments and one further ordinary cut at the fixed receiver."""
from __future__ import annotations

from collections import Counter, defaultdict
from fractions import Fraction
import gzip
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
OLD = "HIDDEN-SENDER-MARKS-20261122-001"
ENGINE, = (ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A").glob("*/end_operator.py")
spec = spec_from_file_location("recorded_ordinary_operator", ENGINE)
engine = module_from_spec(spec)
sys.modules[spec.name] = engine
spec.loader.exec_module(engine)
RECEIVER = 294
SOURCE = (510, 563)
ISSUED = (1754, 1755, 1756)


def owners(holdings):
    by_name = defaultdict(list)
    for holder, row in enumerate(holdings):
        for name in row:
            by_name[name].append(holder)
    return by_name


def append_fourth(holdings, law):
    """Use the independent complete parent-group operator and allocate actual loose names."""
    before = owners(holdings)
    plan = engine.step(engine.from_stars(holdings), law, max_births=4096)
    assert plan.status == "extend", (law, plan.status, plan.planned_births_lower)
    loose = defaultdict(list)
    for name, shared in sorted(before.items()):
        if len(shared) == 1:
            loose[shared[0]].append(name)
    paid_count = Counter(p for row in plan.parents for p in row)
    assert paid_count == {p: len(names) for p, names in loose.items()}
    assert RECEIVER not in paid_count
    next_name = max(before) + 1
    pools = {p: iter(row) for p, row in loose.items()}
    new_rows = []
    for parents, count in zip(plan.parents, plan.fresh, strict=True):
        paid = tuple(next(pools[p]) for p in parents)
        fresh = tuple(range(next_name, next_name + count))
        assert fresh
        next_name += count
        new_rows.append((paid, fresh))
    grown = holdings + [paid + fresh for paid, fresh in new_rows]
    return grown, new_rows


def legal(law, word, holding):
    total = sum(word >> n & 1 for n in holding)
    return total % 2 == 0 if law == "parity" else 0 < total < len(holding)


def extend_example(word, new_rows, law):
    """Set new bits only. Every fourth-cut newborn has an independent fresh slot."""
    for paid, fresh in new_rows:
        if not legal(law, word, paid + fresh):
            word |= 1 << fresh[0]
    return word


def check():
    source, = (ROOT / "artifacts" / (OLD + "A")).glob("*/growth.json.gz")
    with gzip.open(source, "rt") as fp:
        data = json.load(fp)
    old_examples = json.loads((ROOT / "research" / OLD / "cross_checks.json").read_text())
    result = {}
    for law in ("parity", "nae"):
        result[law] = {}
        for route in ("intact", "interrupted", "sham"):
            old = old_examples[law]["diverted" if route == "interrupted" else "intact"]
            holdings = list(map(tuple, data["original_stars"]))
            trace = []
            source_owners = []
            current = data["cases"][route][law]
            for i, layer in enumerate(current["cuts"]):
                source_owners.append([owners(holdings)[n] for n in SOURCE])
                for birth in layer["births"]:
                    assert len(holdings) == birth["holder"]
                    holdings.append(tuple(birth["consumed_names"] + birth["fresh_names"]))
                if i >= 1:
                    obs = owners(holdings)
                    trace.append([[h for h in obs[n] if h != RECEIVER] for n in ISSUED])
            original_roster = holdings[RECEIVER]
            assert original_roster == (949, 957, *ISSUED)
            frozen = owners(holdings)
            grown, new = append_fourth(holdings, law)
            after = owners(grown)
            assert original_roster == grown[RECEIVER] and len(set(original_roster) & set(SOURCE)) == 0
            assert all(frozen[n] == after[n] and len(after[n]) == 2 for n in original_roster)
            assert all(frozen[n] == after[n] and len(after[n]) == 2 for n in SOURCE)
            trace.append([[h for h in after[n] if h != RECEIVER] for n in ISSUED])
            assert trace[0] == [[], [], []] and trace[1] == trace[2]
            assert len({h for row in trace[1] for h in row}) == 3
            # B307's full 000 witnesses give a direct check on both actions in this further cut.
            examples = []
            for run in old["both_full_extensions"]:
                word = int(run["complete_words_after_each_cut_hex"][-1], 16)
                new_word = extend_example(word, new, law)
                assert all(legal(law, new_word, row) for row in grown)
                assert (word ^ new_word) & ((1 << (max(frozen) + 1)) - 1) == 0
                bits = "".join(str((new_word >> n) & 1) for n in ISSUED)
                assert bits == "000"
                examples.append(dict(sender=run["sender_marks"], visible_word_after_further_births=bits))
            pairs = old["probability_by_word_keep_then_swap"]
            assert len(pairs) == 8
            joint = {word: [Fraction(x) for x in row] for word, row in pairs.items()}
            assert all(x > 0 for row in joint.values() for x in row)
            assert [sum(row[i] for row in joint.values()) for i in range(2)] == [1, 1]
            accuracy = sum(max(row) for row in joint.values()) / 2
            assert accuracy == Fraction(old["best_accuracy_if_sends_are_equiprobable"])
            result[law][route] = {
                "births_through_first_receipt": [len(cut["births"]) for cut in current["cuts"]],
                "further_births": len(new),
                "total_holders_after_further_cut": len(grown),
                "receiver_roster": original_roster,
                "source_holders_initial_and_after_first_payment": source_owners[:2],
                "receiver_issued_other_holders_birth_finish_and_next_cut_spectator_only": trace,
                "permitted_local_events_after_birth": [["shared_with_three_distinct_partners"]],
                "further_local_changes": 0,
                "same_preparation_both_actions_verified_through_next_cut": examples,
                "one_record_and_any_later_reread_accuracy": str(accuracy),
                "diagonal_joint_first_word_and_reread_keep_then_swap": pairs,
                "joint_mass_of_two_distinct_local_finishes": "0",
            }
    return result


if __name__ == "__main__":
    report = check()
    (HERE / "fixed_holder_replay.json").write_text(json.dumps(report, indent=2) + "\n")
    for law, routes in report.items():
        for route, row in routes.items():
            print(law, route, row["further_births"], row["further_local_changes"],
                  row["one_record_and_any_later_reread_accuracy"])
