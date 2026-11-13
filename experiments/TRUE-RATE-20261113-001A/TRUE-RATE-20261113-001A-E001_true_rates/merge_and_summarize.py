"""Thread-written: merge the two run journals by idx and summarize TRUE-RATE (with the post-hoc carried-port certificate)."""
import collections
import json
import os
import sys
from fractions import Fraction

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
CODEX = os.path.join(os.path.dirname(os.path.abspath(__file__)), "codex")
OUT = os.path.join(ROOT, "artifacts/TRUE-RATE-20261113-001A/TRUE-RATE-20261113-001A-E001_true_rates")
PR = os.path.join(ROOT, "artifacts/PROVED-RATE-20261113-001A")
TB = os.path.join(ROOT, "artifacts/TRUE-BOND-20261113-001A/TRUE-BOND-20261113-001A-E001_side_branches/true_rates_all.jsonl")


def jsonl(path):
    with open(path) as fh:
        return [json.loads(line) for line in fh if line.strip()]


def main():
    rows = {}
    for name in ("true_rate_flat4.jsonl", "true_rate_rest.jsonl"):
        for r in jsonl(os.path.join(CODEX, name)):
            assert r["idx"] not in rows, r["idx"]
            rows[r["idx"]] = r
    assert len(rows) == 226, len(rows)
    pr_file = next(os.path.join(d, "rates_all.jsonl") for d in
                   (os.path.join(PR, x) for x in os.listdir(PR)) if os.path.isfile(os.path.join(d, "rates_all.jsonl")))
    ray = {r["idx"]: r for r in jsonl(pr_file)}
    tb = {r["idx"]: r for r in jsonl(TB)}
    cert = {int(k): v for k, v in json.load(open(os.path.join(CODEX, "thread_carried_certificate.json"))).items()}
    complete = {i: r for i, r in rows.items() if r.get("closed") and r.get("complete")}
    lam = {i: Fraction(r["lambda_true"]) for i, r in complete.items() if r.get("lambda_true") is not None}
    lam_ray = {i: Fraction(ray[i]["lambda"]) for i in rows}
    shortened = {i for i, r in tb.items()
                 if any(a is not None and b is not None and a > b for a, b in zip(r["L_ray"], r["L"]))}
    others = [i for i in lam if i not in cert or not cert[i]["bounded_by_3_all_s"]]
    summary = {
        "families": len(rows),
        "status": dict(collections.Counter(r["status"] for r in rows.values())),
        "closed_and_complete": len(complete),
        "zero_cycle_in_complete": sorted(i for i, r in complete.items() if r.get("zero_cycle")),
        "zero_cycle_anywhere": sorted(i for i, r in rows.items() if r.get("zero_cycle")),
        "gate_ok_in_complete": sum(1 for r in complete.values() if r.get("gate_ok")),
        "gate_mismatch_kinds": dict(collections.Counter(m["kind"] for r in rows.values() for m in (r.get("mismatches") or []))),
        "lambda_true_complete": {str(k): v for k, v in sorted(collections.Counter(lam.values()).items())},
        "lambda_true_equals_ray_in_complete": sum(1 for i in others if lam[i] == lam_ray[i]),
        "lambda_true_below_ray_in_complete": sorted(i for i in others if lam[i] < lam_ray[i]),
        "complete_among_shortened": sorted(i for i in complete if i in shortened),
        "upper_bounds_not_complete": {str(k): v for k, v in sorted(collections.Counter(
            Fraction(r["lambda_true"]) for i, r in rows.items() if i not in complete and r.get("lambda_true")).items())},
        "errors": {i: r.get("error") for i, r in rows.items() if r["status"] in ("error", "memory_limit", "timeout")},
        "carried_port_families": sorted(cert),
        "certified_bounded_by_3_all_s": sorted(i for i, v in cert.items() if v["bounded_by_3_all_s"]),
        "certified_lambda_ray": {i: str(lam_ray[i]) for i, v in sorted(cert.items()) if v["bounded_by_3_all_s"]},
        "carried_and_shortened": sorted(i for i in cert if i in shortened),
        "shortened_without_carried_port": len(shortened - set(cert)),
        "seconds_total": round(sum(r["seconds"] for r in rows.values()), 1),
    }
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "true_rates_all.jsonl"), "w") as fh:
        for i in sorted(rows):
            fh.write(json.dumps(rows[i], sort_keys=True) + "\n")
    with open(os.path.join(OUT, "summary.json"), "w") as fh:
        json.dump(summary, fh, indent=1, sort_keys=True)
    print(json.dumps({k: v for k, v in summary.items() if k != "errors"}, indent=1))
    print("errors:", json.dumps(summary["errors"])[:800])


if __name__ == "__main__":
    sys.exit(main())
