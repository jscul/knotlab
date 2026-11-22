"""Independently check which earlier words the full direct successor can distinguish."""
from collections import Counter, defaultdict
from fractions import Fraction
from itertools import product
import json

from weigh_successor import BASE, HERE, ROOT, W, Birth, distribution, factor, source_data


def check():
    ledger = source_data()
    old_table = json.loads((ROOT / "research" / BASE / "cross_checks.json").read_text())
    results = {}
    for law in ("parity", "nae"):
        for route in ("intact", "interrupted", "sham"):
            births = [Birth(r["holder"], tuple(r["parents"]), tuple(r["consumed_names"]), tuple(r["fresh_names"]))
                      for cut in ledger["cases"][route][law]["cuts"] for r in cut["births"]]
            for i, wmark in enumerate(W):
                h, = [b for b in births if wmark in b.paid]
                u, = set(h.paid) - {wmark}
                raw = defaultdict(Fraction)
                shapes = {}
                for send in (0, 1):
                    old = dict(zip(ledger["original_name_order"], map(int, ledger["common_original_words"][law]), strict=True))
                    if send:
                        old[510], old[563] = old[563], old[510]
                    part, _ = distribution(law, births, old, (*W, u), {})
                    assert len(part) == 16 and sum(part.values()) == 1
                    check_w = Counter()
                    for values, mass in part.items():
                        bits, other = "".join(map(str, values[:3])), values[3]
                        check_w[bits] += mass
                        # Include the entire fresh word on H. Both chronological samples of it refer to the same word.
                        for young in product((0, 1), repeat=len(h.fresh)):
                            p = factor(law, (values[i], other), len(young), young)
                            if p:
                                raw[bits, other, send, young] += mass * p / 2
                    ref_route = "diverted" if route == "interrupted" else "intact"
                    ref = old_table[law][ref_route]["probability_by_word_keep_then_swap"]
                    assert all(Fraction(ref[key][send]) == v for key, v in check_w.items())
                assert sum(raw.values()) == 1
                for mode in ("anonymous", "addressed"):
                    records = defaultdict(lambda: defaultdict(Counter))
                    for (bits, other, send, young), p in raw.items():
                        x = int(bits[i])
                        incoming = (x + other,) if mode == "anonymous" else (x, other)
                        cell = records[incoming, young]
                        cell["W"][bits] += p
                        cell["Wi"][x] += p
                        cell["first_send"][send] += p
                    classes = Counter()
                    certifies_x = Fraction(0)
                    for (inc, young), cell in records.items():
                        mixed = inc == (1,) if mode == "anonymous" else inc[0] != inc[1]
                        expected = 8 if mode == "anonymous" and mixed else 4
                        assert len(cell["W"]) == expected and len(cell["first_send"]) == 2
                        classes[expected] += 1
                        if len(cell["Wi"]) == 1:
                            certifies_x += sum(cell["Wi"].values())
                    shapes[mode] = {"distinct_complete_readings": len(records), "earlier_words_per_reading": dict(classes),
                                    "mass_where_the_paid_bit_is_certain": str(certifies_x),
                                    "best_word": str(sum(max(t["W"].values()) for t in records.values())),
                                    "best_bit": str(sum(max(t["Wi"].values()) for t in records.values())),
                                    "best_first_send": str(sum(max(t["first_send"].values()) for t in records.values()))}
                results[f"{law}/{route}/H{i}"] = {"holder": h.holder, "old_paid_bit": wmark, "other_input": u,
                                                   "all_joint_W_and_other_input_values_per_first_action": 16,
                                                   "readings": shapes}
    return results


if __name__ == "__main__":
    results = check()
    (HERE / "direct_retention.json").write_text(json.dumps(results, indent=2) + "\n")
    for k, v in results.items():
        if "/intact/" in k:
            print(k, v["readings"]["anonymous"])

