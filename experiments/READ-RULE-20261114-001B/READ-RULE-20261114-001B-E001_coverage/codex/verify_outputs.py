"""Focused READ output reconciliation; no global checks or source mutations."""
from __future__ import annotations

from collections import Counter
import gzip
import hashlib
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]


def digest(path):
    value = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            value.update(block)
    return value.hexdigest()


def main():
    import ast
    parsed = []
    for path in sorted(HERE.glob("*.py")):
        ast.parse(path.read_text(), filename=str(path))
        parsed.append(path.name)
    outputs = {name: json.loads((HERE / name).read_text())
               for name in ("results.json", "counterexample.json", "summary.json")}
    rows = outputs["results.json"]["families"]
    summary = outputs["summary.json"]
    independent = json.loads((HERE / "r1_independent.json").read_text())
    source = json.loads((HERE / "source_index.json").read_text())
    assert len(rows) == len({row["key"] for row in rows}) == 5964
    assert {row["key"] for row in rows} == {row["key"] for row in source["rows"]}
    assert sum(row["in_scope"] for row in rows) == 5789
    assert sum(row["weight"] for row in rows) == 6028
    assert sum(row["weight"] for row in rows if row["in_scope"]) == 5853
    indexed = {row["key"]: row for row in source["rows"]}
    digest_path = ROOT / "artifacts/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/window_digest.jsonl.gz"
    digest_keys = set()
    with gzip.open(digest_path, "rt") as stream:
        for line in stream:
            record = json.loads(line)
            key = record["key"]
            assert key not in digest_keys
            digest_keys.add(key)
            original = indexed[key]
            for field in ("weight", "in_scope", "stratum"):
                assert original[field] == record[field]
            assert original["raw_verdict"] == record["verdict"]
    assert digest_keys == set(indexed)
    r1 = Counter()
    for row in rows:
        other = independent["families"][row["key"]]
        assert row["R1"]["all_residues"] == other["R1_every_residue"]
        assert row["R1"]["some_residues_only"] == other["R1_progressions_only"]
        assert len(row["R1"]["residues"]) == row["carried"]["period"]
        r1[row["in_scope"], row["R1"]["all_residues"], row["R1"]["some_residues_only"]] += 1
        c = row["conditional"]
        if c["complete"]:
            assert len(c["all_conditionally_rectangular_by_length"]) == 8
            lengths = [n for n, good in enumerate(c["all_conditionally_rectangular_by_length"], 1) if good]
            assert c["r"] == (min(lengths) if lengths else None)
            assert c["certified"] == bool(lengths)
        else:
            assert c["r"] is None and not c["certified"]
    assert r1[True, True, False] == summary["in_scope"]["R1_every"]["success"]["count"]
    assert r1[True, False, True] == summary["in_scope"]["R1_progressions_only"]["success"]["count"]
    success = [row for row in rows if row["in_scope"] and row["conditional"]["complete"] and row["conditional"]["certified"]]
    assert len(success) == summary["Q2"]["rate"]["success"]["count"]
    assert sum(row["weight"] for row in success) == summary["Q2"]["rate"]["success"]["draw_weight"]
    counter = outputs["counterexample.json"]
    for variant in counter["variants"].values():
        assert len(variant["L_s_1_to_6"]) == len(variant["U_s_1_to_6"]) == 6
        assert variant["direct_bonds_verified"]
    for entry in counter["records"]:
        result = entry["result"]
        if entry["operation"] == "direct":
            assert result["status"] == "exact_minimum"
            assert result["verification"]["is_bond"]
            assert result["verification"]["every_deletion_full"]
    assert summary["Q3"]["status"] == counter["Q3"]["status"]
    # All original CARRY records stay at their indexed size and modification time.
    stat = (ROOT / source["source"]).stat()
    assert (stat.st_size, stat.st_mtime_ns) == (source["size"], source["mtime_ns"])
    relative_sources = [
        ROOT / "research/READ-RULE-20261114-001/preregistration.md",
        ROOT / "research/READ-RULE-20261114-001/advisor_review_answer.md",
        ROOT / "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex/relations.py",
        ROOT / "experiments/FORGET-RULE-20261114-001A/FORGET-RULE-20261114-001A-E001_rule/gadget_control.py",
    ]
    carry = ROOT / "experiments/CARRY-BOUND-20261114-001A/CARRY-BOUND-20261114-001A-E001_window/codex"
    relative_sources.extend(carry / name for name in ("window.py", "scope.py", "inputs.py", "direct.py", "summarize.py", "REPORT.md"))
    relative_sources.extend(HERE.glob("*.py"))
    relative_sources.append(digest_path)
    manifest = {str(path.relative_to(ROOT)): digest(path) for path in sorted(relative_sources)}
    manifest[source["source"]] = source["sha256"]
    result = dict(passed=True, parsed_python=parsed, families=5964,
                  exact_independent_R1_agreement=True, JSON_outputs_parsed=True,
                  compact_digest_metadata_agreement=True,
                  source_unchanged_by_size_and_mtime=True,
                  sha256=manifest)
    (HERE / "validation.json").write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "sha256"}))


if __name__ == "__main__":
    main()
