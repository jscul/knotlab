"""Independent integrity checks of the completed required output files."""

from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
INPUT = ROOT / "artifacts/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds/runs_merged.jsonl"
INF = 10**9


def main():
    records = {r["idx"]: r for r in map(json.loads, INPUT.read_text().splitlines())}
    rows = [json.loads(s) for s in (HERE / "rates.jsonl").read_text().splitlines()]
    summary = json.loads((HERE / "summary.json").read_text())
    assert len(rows) == len(records) == 664
    assert len({r["idx"] for r in rows}) == 664
    assert {r["idx"] for r in rows} == set(records)
    assert [r["idx"] for r in rows] == sorted(records)
    checked_depths = 0
    for row in rows:
        assert row["status"] in ("done", "timeout"), (row["idx"], row["status"], row.get("error"))
        assert 0 <= row["nodes"] <= 2_000_000
        if row["complete"]:
            assert row["nodes"] < 2_000_000
        assert isinstance(row["seconds"], (int, float)) and row["seconds"] >= 0
        assert row["seconds"] < 1205, (row["idx"], row["seconds"])
        if row["status"] == "timeout":
            assert row["seconds"] >= 1199
        old = records[row["idx"]].get("L", [])
        if row.get("gate_status", "").startswith("checked"):
            assert len(row["L_recomputed"]) == len(old)
            observed = [(m["s"], m["yours"], m["record"]) for m in row["mismatches"]]
            expected = [(s, a, b) for s, (a, b) in enumerate(zip(row["L_recomputed"], old), 1) if a != b]
            assert observed == expected
            assert row["gate_ok"] is (not expected)
            checked_depths += len(old)
        if row["status"] == "done":
            assert row["complete"] or row["lambda_status"] == "partial"
            if old:
                assert row["gate_ok"] is not None
            else:
                assert row["gate_ok"] is None and row["gate_status"] == "skipped_no_record_L"
            if row["lambda"] is None:
                assert row["lambda_float"] is None
                assert row["cyclic_sccs"] == 0
                assert row["zero_mean"] is False
            else:
                rate = Fraction(row["lambda"])
                assert row["lambda"] == f"{rate.numerator}/{rate.denominator}"
                assert row["lambda_float"] == float(rate)
                assert row["zero_mean"] is (rate == 0)
                assert rate >= 0 and row["cyclic_sccs"] > 0
            if row["bounded_all"] is True:
                assert row["bounded_good_starts"] > 0
                assert row["bounded_good_cycles"] > 0
                assert row["zero_mean"] is True
            elif row["bounded_all"] is False:
                assert row["bounded_good_starts"] == 0
                assert row["bounded_affected_starts"] == 0
            else:
                assert not row["complete"] and row["bounded_affected_starts"] > 0

    def verify_counts(part, subset):
        assert part["families"] == len(subset)
        assert part["complete"] == sum(bool(r["complete"]) for r in subset)
        assert part["gate_mismatches_total"] == sum(len(r["mismatches"]) for r in subset)
        assert part["lambda_distribution"] == dict(Counter(r["lambda"] for r in subset if r["lambda"] is not None))
        assert part["lambda_none"] == sum(r["lambda"] is None for r in subset)
        assert part["bounded_all"] == sum(r["bounded_all"] is True for r in subset)
        assert part["zero_mean_without_bounded_all"] == sum(r["zero_mean"] is True and r["bounded_all"] is False for r in subset)
        assert part["timeout"] == sum(r["status"] == "timeout" for r in subset)
        assert part["errors"] == 0

    verify_counts(summary, rows)
    for name in ("bounded", "rising", "flat", "capped"):
        verify_counts(summary["by_record_class"][name], [r for r in rows if r["record_class"] == name])
    ambiguous = [r for r in rows if r["record_class"] is None]
    verify_counts(summary["ambiguous_record_class"], ambiguous)
    assert summary["ambiguous_record_class_indices"] == [r["idx"] for r in ambiguous]
    assert sum(v["families"] for v in summary["by_record_class"].values()) + len(ambiguous) == 664
    assert summary["mismatches"] == [m for r in rows for m in r["mismatches"]]
    for path, digest in summary["input_sha256"].items():
        assert hashlib.sha256((ROOT / path).read_bytes()).hexdigest() == digest
    result = dict(families=len(rows), checked_depths=checked_depths,
                  mismatches=summary["gate_mismatches_total"], integrity="passed",
                  input_hashes="unchanged", timeouts=summary["timeout"], errors=0)
    (HERE / "validation.json").write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps(result))


if __name__ == "__main__":
    main()
