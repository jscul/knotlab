"""Rebuild each ordinary cut and exhibit a completed 000 record under both sends."""
from collections import Counter, defaultdict
from fractions import Fraction
from importlib.util import module_from_spec, spec_from_file_location
from itertools import product
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EARLIER = "TWO-SENDS-AND-GROWN-KEEPERS-20261122-001A"
DATA, = (ROOT / "artifacts" / EARLIER).glob("*_two_sends")
ENGINE, = (ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A").glob("*/end_operator.py")
spec = spec_from_file_location("physical_payments", ENGINE)
payments = module_from_spec(spec)
sys.modules[spec.name] = payments
spec.loader.exec_module(payments)
FRESH = (1754, 1755, 1756)


def legal(values, law):
    if law == "parity":
        return sum(values) % 2 == 0
    return len(set(values)) == 2


def value(word, name):
    return (word >> name) & 1


def read(word, names):
    return "".join(str(value(word, n)) for n in names)


def reconstruct(original, law, diverted, archived):
    """The holdings implementation and the ordinary parent-group implementation agree."""
    stages = [original]
    cuts = []
    for number in range(3):
        stars = stages[-1]
        step = payments.step(payments.from_stars(stars), law)
        assert step.status == "extend" and min(step.fresh) >= 1
        owners = Counter(n for holder in stars for n in holder)
        loose = {h: sorted(n for n in row if owners[n] == 1) for h, row in enumerate(stars)}
        if number == 0 and diverted:
            # Conjugating the canonical name ordering at the same sender
            # diverts its first enrolled payment to the former spare's child.
            assert loose[80].count(510) == loose[80].count(677) == 1
            order = {510: 677, 677: 510}
            loose[80].sort(key=lambda n: order.get(n, n))
        next_name = max(owners) + 1
        current = []
        for i, (parents, grant) in enumerate(zip(step.parents, step.fresh, strict=True)):
            paid = tuple(loose[p].pop(0) for p in parents)
            fresh = tuple(range(next_name, next_name + grant))
            next_name += grant
            h = len(stars) + i
            if number < 2:
                reference = archived[number]["births"][i]
                assert h == reference["holder"] and list(parents) == reference["parents"]
                expected = reference["consumed_names"]
                if diverted and number == 0 and h in (162, 164):
                    expected = [{510: 677, 677: 510}.get(x, x) for x in expected]
                assert list(paid) == expected and list(fresh) == reference["fresh_names"]
            current.append((h, paid, fresh))
        assert not any(loose.values())
        cuts.append(current)
        stages.append(stars + [paid + fresh for _, paid, fresh in current])
    return cuts, stages


def finish_record(stages, word):
    """Only the local new values and anonymous identities of their coholders are returned."""
    result = []
    for stars in stages[-2:]:
        partners = []
        for n in FRESH:
            partners.append(tuple(h for h, row in enumerate(stars) if h != 294 and n in row))
        assert all(len(row) <= 1 for row in partners)
        seen = {}
        anonymous = [seen.setdefault(row[0], len(seen)) if row else None for row in partners]
        result.append({"values": read(word, FRESH), "other_holders": anonymous})
    assert result[0]["other_holders"] == [None] * 3
    assert result[1]["other_holders"] == [0, 1, 2]
    return result


def make_witness(initial, cuts, stages, law, swap):
    word = initial ^ ((1 << 510) | (1 << 563)) if swap else initial
    states = []
    assert read(word, (510, 563)) == ("10" if swap else "01")
    # Mixed fresh words at each initially affected NAE child are legal for
    # either old input. Where chosen, the completion is identical in both runs.
    mixed = {162: "101", 163: "101", 164: "1010", 165: "01"}
    for i, current in enumerate(cuts):
        for h, paid, fresh in current:
            incoming = [value(word, n) for n in paid]
            bits = [0] * len(fresh)
            if i == 0 and law == "nae" and h in mixed:
                bits = list(map(int, mixed[h]))
            elif not legal(incoming + bits, law):
                bits[0] = 1
            assert len(bits) == len(fresh) and legal(incoming + bits, law)
            word |= sum(bit << name for bit, name in zip(bits, fresh, strict=True))
        assert all(legal([value(word, n) for n in row], law) for row in stages[i + 1])
        states.append(hex(word))
    record = finish_record(stages, word)
    assert [r["values"] for r in record] == ["000", "000"]
    return {"sender_marks": read(word, (510, 563)), "intermediate_paid_at_R": read(word, (949, 957)),
            "fresh_at_C": read(word, (947, 948, 949)), "fresh_at_P": read(word, (957, 958)),
            "complete_words_after_each_cut_hex": states, "local_record": record}


def probabilities(source, divided, swap, law):
    """Sum over the random one-mark contributions of the two real parents."""
    def marginal(paid, grant, slot):
        words = [w for w in product((0, 1), repeat=grant) if legal(tuple(paid) + w, law)]
        return [Fraction(sum(w[slot] == x for w in words), len(words)) for x in (0, 1)]
    x = value(source, 677) if divided else int(swap)
    c = marginal((x, value(source, 515)), 3, 2)
    p = marginal((value(source, 518), value(source, 523)), 2, 0)
    result = defaultdict(Fraction)
    for a, b in product((0, 1), repeat=2):
        rows = [r for r in product((0, 1), repeat=3) if legal((a, b) + r, law)]
        for r in rows:
            result["".join(map(str, r))] += c[a] * p[b] / len(rows)
    assert sum(result.values()) == 1
    return dict(sorted(result.items()))


def run():
    previous = json.loads((DATA / "ordinary.json").read_text())
    originals = json.loads(gzip.decompress((DATA / "sends.json.gz").read_bytes()))["originals"]["0"]["stars"]
    original = [tuple(row) for row in originals]
    out = {}
    for law in ("parity", "nae"):
        old = previous["ordinary_preconsumption_private_swap"][law]["original_and_first_cut_witness"]
        initial = sum(int(v) << n for n, v in zip(old["original_name_order"], old["common_initial_word"], strict=True))
        assert all(legal([value(initial, n) for n in row], law) for row in original)
        out[law] = {"common_word_before_the_sender_acts_hex": hex(initial)}
        for divided in (False, True):
            cuts, stages = reconstruct(original, law, divided, previous["actual_ordinary_cuts"]["intact"][law])
            assert stages[-1][294] == (949, 957, *FRESH)
            assert {294} == {h for h, row in enumerate(stages[-2]) if set(row).issuperset(FRESH)}
            pair = [make_witness(initial, cuts, stages, law, swap) for swap in (False, True)]
            assert pair[0]["local_record"] == pair[1]["local_record"]
            assert pair[0]["intermediate_paid_at_R"] == pair[1]["intermediate_paid_at_R"]
            assert pair[0]["sender_marks"] != pair[1]["sender_marks"]
            differing_names = []
            for left, right in zip(pair[0]["complete_words_after_each_cut_hex"], pair[1]["complete_words_after_each_cut_hex"], strict=True):
                delta = int(left, 16) ^ int(right, 16)
                differing_names.append([i for i in range(delta.bit_length()) if value(delta, i)])
            if law == "nae":
                assert all(row == [510, 563] for row in differing_names)
            d0, d1 = [probabilities(initial, divided, swap, law) for swap in (False, True)]
            assert len(d0.keys() & d1.keys()) == len(d0 | d1) == 8
            tv = sum(abs(d0[k] - d1[k]) for k in d0) / 2
            out[law]["diverted" if divided else "intact"] = {
                "funded_births": [len(c) for c in cuts], "local_record": pair[0]["local_record"],
                "both_full_extensions": pair, "physically_different_names_per_cut": differing_names,
                "probability_by_word_keep_then_swap": {k: [str(d0[k]), str(d1[k])] for k in d0},
                "total_variation": str(tv), "best_accuracy_if_sends_are_equiprobable": str((1 + tv) / 2),
            }
    # Compare with the sealed producer only after reconstructing the states and weights.
    receipt, = (ROOT / "artifacts" / (HERE.name + "A")).glob("*/supports.json.gz")
    projections = json.loads(gzip.decompress(receipt.read_bytes()))["projections"]
    compared = 0
    for row in projections:
        if row["target"] != "R" or row["side"] != "00":
            continue
        condition = "diverted" if row["route"] == "interrupted" else "intact"
        expected = out[row["law"]][condition]
        weighted = row["weighted"]
        assert row["support"]["common"] == list(expected["probability_by_word_keep_then_swap"])
        for raw, expected_pair in expected["probability_by_word_keep_then_swap"].items():
            assert [weighted["idle"][raw], weighted["swap"][raw]] == expected_pair
            compared += 2
        assert weighted["total_variation"] == expected["total_variation"]
        assert weighted["equal_prior_optimal_accuracy"] == expected["best_accuracy_if_sends_are_equiprobable"]
    assert compared == 96
    return out


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
