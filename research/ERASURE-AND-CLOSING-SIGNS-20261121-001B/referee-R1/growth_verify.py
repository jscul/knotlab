"""Check the saved physical receipts and the named minimum's projected relations."""

from collections import Counter
from contextlib import redirect_stdout
from hashlib import sha256
import io
from itertools import combinations, product
import json
from pathlib import Path
import runpy
import sys

from growth_replay import ARCHIVE, proposal_groups


HERE = Path(__file__).resolve().parent


def verify_groups():
    candidates = [g for k in (2, 3, 4) for g in combinations(range(4), k)]
    cases = 0
    for included in product((False, True), repeat=len(candidates)):
        witnessed = [set(g) for g, retain in zip(candidates, included) if retain]
        pairs = [g for g in candidates if len(g) == 2 and any(set(g) <= w for w in witnessed)]
        unheld = [
            g for g in candidates if len(g) >= 3
            and all(pair in pairs for pair in combinations(g, 2))
            and not any(set(g) <= w for w in witnessed)
        ]
        maximal = [g for g in unheld if not any(set(g) < set(other) for other in unheld)]
        residual = [pair for pair in pairs if not any(set(pair) <= set(g) for g in maximal)]
        assert proposal_groups(witnessed) == sorted(maximal) + sorted(residual)
        cases += 1
    return cases


def verify_receipts(sample, population):
    digest = sha256(ARCHIVE.read_bytes()).hexdigest()
    for data in (sample, population):
        assert data["archive_sha256"] == digest
        assert not data["mismatches"]
        assert data["address_space_limit_bytes"] == 2684354560
    assert population["founder_pairs_rebuilt"] == 544
    assert population["mismatch_count"] == 0
    assert Counter(h["stratum"] for h in sample["histories"]) == {
        "seeded": 72, "named_positive": 2, "named_control": 2,
    }
    checked = Counter()
    for item in sample["histories"]:
        for law, history in item["laws"].items():
            previous = item["source_rows"]
            for cut in history["cuts"]:
                checked["funded_cuts"] += 1
                for birth in cut["births"]:
                    h = birth["holder"]
                    assert cut["after_rows"][h] == birth["support"]
                    if law == "nae":
                        ones = set(birth["older_word_one_names"])
                        assert not ones.intersection(birth["inputs"])
                        assert all(0 < len(ones.intersection(row)) < len(row) for row in previous)
                        checked["unsigned_nonimplication_words"] += 1
                    if birth["old_span_rows"] is not None:
                        terms = Counter(x for h in birth["old_span_rows"] for x in previous[h])
                        assert [x for x, n in sorted(terms.items()) if n % 2] == birth["inputs"]
                        checked["old_parity_certificates"] += 1
                previous = cut["after_rows"]
    return checked


def canonical_projection(rows, support, law, odd_at=None):
    names = {name for row in rows for name in row}
    formula = []
    for h, row in enumerate(rows):
        for word in product((0, 1), repeat=len(row)):
            if law == "parity":
                admitted = sum(word) % 2 == int(h == odd_at)
            else:
                admitted = 0 < sum(word) < len(word)
            if not admitted:
                formula.append(" ".join(
                    ("-" if bit else "") + f"x{name}" for name, bit in zip(row, word)
                ))
    requested = [f"x{name}" for name in support]
    forgotten = [f"x{name}" for name in sorted(names.difference(support))]
    sys.argv = [
        "knotlab", "check", "--json", "--cnf", ";".join(formula),
        "--loops", *requested[:-1], "--contact", requested[-1], "--witnesses", *forgotten,
    ]
    output = io.StringIO()
    try:
        with redirect_stdout(output):
            runpy.run_module("knotlab", run_name="__main__")
    except SystemExit as code:
        assert code.code == 0
    return json.loads(output.getvalue())


def verify_minimum(sample):
    case = next(h for h in sample["histories"] if (h["panel"], h["draw"]) == ("S", 2))
    even = case["laws"]["parity"]["cuts"][0]["after_rows"]
    unsigned = case["laws"]["nae"]["cuts"][0]["after_rows"]
    checks = {
        "before_closing": canonical_projection(case["source_rows"], even[-1], "parity"),
        "after_even": canonical_projection(even, even[-1], "parity"),
        "after_odd": canonical_projection(even, even[-1], "parity", 4),
        "after_actual_unsigned_birth": canonical_projection(unsigned, unsigned[-1], "nae"),
    }
    even_words = {"".join(map(str, w)) for w in product((0, 1), repeat=4) if sum(w) % 2 == 0}
    assert set(checks["before_closing"]["allowed"]) == set(checks["after_even"]["allowed"]) == even_words
    assert checks["before_closing"]["is_knot"] and checks["after_even"]["is_knot"]
    assert checks["after_odd"]["allowed"] == []
    assert not checks["after_odd"]["coexistence"] and not checks["after_odd"]["invisible_in_parts"]
    assert len(checks["after_actual_unsigned_birth"]["allowed"]) == 30
    assert checks["after_actual_unsigned_birth"]["is_knot"]
    return checks


if __name__ == "__main__":
    sample = json.loads((HERE / "growth_replay.json").read_text())
    population = json.loads((HERE / "growth_all_summary.json").read_text())
    checks = {
        "direct_proposal_group_comparisons": verify_groups(),
        "literal_receipt_comparisons": verify_receipts(sample, population),
        "minimum_projections": verify_minimum(sample),
    }
    (HERE / "growth_verification.json").write_text(json.dumps(checks, indent=2) + "\n")
    print("Verified direct proposal choices, saved physical receipts, and the minimum's projections.")
