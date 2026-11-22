"""Validate local projections for the actual ordinary fourth and fifth cuts."""
from collections import Counter
from itertools import product
from math import comb
from pathlib import Path
import gzip
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
OUTPUT = ROOT / "artifacts" / HERE.parent.name / HERE.name
EARLIER = "HIDDEN-SENDER-MARKS-20261122-001A"
PREVIOUS = ROOT / "artifacts" / EARLIER / (EARLIER + "-E001_hidden_sends")
sys.path.append(str(ROOT / "experiments" / EARLIER / (EARLIER + "-E001_hidden_sends")))
from projection import canonical_knot


def lawful(law, width, ones):
    if law == "parity":
        return ones % 2 == 0
    return 0 < ones < width


def erasures(law, n):
    # Both laws are exchangeable in the positions. Count separately at each
    # possible number of ones among the n-1 distinctions retained.
    assert all(any(lawful(law, n, k + bit) for bit in (0, 1)) for k in range(n))
    allowed = sum(comb(n, k) for k in range(n + 1) if lawful(law, n, k))
    assert 0 < allowed < 2 ** n
    return {"arity": n, "allowed": allowed, "after_any_one_forgetting": 2 ** (n - 1)}


def supports_donation(law, previous_inputs, previous_grant):
    # Fix the actual number of old ones, expose one new bit, complete its siblings.
    assert previous_grant >= 2
    n = previous_inputs + previous_grant
    for k, offered in product(range(previous_inputs + 1), (0, 1)):
        assert any(lawful(law, n, k + offered + j) for j in range(previous_grant))


def check_cut(law, parents, children):
    donors = {r["holder"]: r for r in parents}
    names = [d for r in parents for d in r["fresh_names"]]
    assert len(set(names)) == len(names)
    paid = set()
    widths = Counter()
    row_count = 0
    for r in children:
        previous = r["parents"]
        assert len(previous) == len(set(previous)) and r["grant"] >= 1
        for h, d in zip(previous, r["consumed_names"], strict=True):
            giver = donors[h]
            assert d in giver["fresh_names"] and d not in paid
            paid.add(d)
            supports_donation(law, len(giver["parents"]), giver["grant"])
        # Each one of these paid positions belongs to a different donor; the
        # reserve distinctions used to complete donors are private and disjoint.
        widths[len(previous) + r["grant"]] += 1
        row_count += 2 ** len(previous)
    return {"births": len(children), "possible_paid_words_summed_by_child": row_count,
            "full_holder_widths": dict(sorted(widths.items())),
            "single_erasure": [erasures(law, n) for n in sorted(widths)]}


def main():
    with gzip.open(OUTPUT / "alternate.json.gz", "rt") as f:
        new = json.load(f)
    with gzip.open(PREVIOUS / "growth.json.gz", "rt") as f:
        old = json.load(f)
    report = {}
    for law in ("parity", "nae"):
        report[law] = {"canonical": canonical_knot(law), "fourth": {}}
        for route in ("intact", "interrupted", "sham"):
            third = old["cases"][route][law]["cuts"][-1]["births"]
            fourth = new["courses"][law][route]["fourth"]["births"]
            report[law]["fourth"][route] = check_cut(law, third, fourth)
        fourth = new["courses"][law]["intact"]["fourth"]["births"]
        fifth = new["later_source_controls"][law]["fifth"]["births"]
        report[law]["fifth_intact"] = check_cut(law, fourth, fifth)
    result = OUTPUT / "local_laws.json"
    result.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
    for step in (report["nae"]["fourth"]["intact"], report["nae"]["fifth_intact"]):
        print(step["births"], "births;", step["possible_paid_words_summed_by_child"],
              "possible incoming words over their individual projections")


if __name__ == "__main__":
    main()
