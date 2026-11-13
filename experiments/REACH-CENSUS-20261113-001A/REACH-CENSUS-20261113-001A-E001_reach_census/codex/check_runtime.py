"""Focused runtime/resource/resume checks; no full-census execution."""
import ast
import hashlib
import json
from pathlib import Path
import tempfile
import time

import reach_dp as D
import run_census as R


def main():
    checks = {}
    for path in D.HERE.glob("*.py"):
        ast.parse(path.read_text(), filename=str(path))
    checks["python_syntax"] = True
    bd = D.load_module("runtime_check_bd", D.BD_PATH)
    idx, defs = bd.families_one_def()[0]
    key = D.canonical(defs)
    ordinary = D.compute_family(key, force_dp=True)
    assert ordinary["status"] == "done" and ordinary["nodes"] == 66
    checks["small_graph_unchanged"] = dict(idx=idx, nodes=ordinary["nodes"],
                                           **{"lambda":ordinary["lambda"]})
    original_rss, original_exact = D.rss_bytes, D.REF.exact_eventual_bound
    injected = [False]

    def fake_rss(*args):
        return D.MEMORY_BYTES+1 if injected[0] else original_rss(*args)

    def post_exact(*args):
        value = original_exact(*args)
        injected[0] = True
        return value

    D.rss_bytes, D.REF.exact_eventual_bound = fake_rss, post_exact
    try:
        row = D.compute_family(key, force_dp=True)
        assert row["status"] == "memory_limit" and row["class"] == "unresolved"
        checks["post_exact_memory_stop"] = dict(status=row["status"], actual_allocation=False)
        injected[0] = False
        returned = [False]

        def during_exact(*args):
            injected[0] = True
            time.sleep(.3)
            returned[0] = True
            return original_exact(*args)

        D.REF.exact_eventual_bound = during_exact
        row = D.compute_family(key, force_dp=True)
        assert row["status"] == "memory_limit" and not returned[0]
        checks["during_exact_memory_stop"] = dict(status=row["status"], actual_allocation=False)
    finally:
        D.rss_bytes, D.REF.exact_eventual_bound = original_rss, original_exact
    row = D.compute_family(key, force_dp=True, seconds=.001)
    assert row["status"] == "timeout" and row["class"] == "unresolved"
    checks["family_alarm"] = row["status"]
    row = D.compute_family(key, force_dp=True, node_cap=30)
    assert row["nodes"] == 30 and row["complete"] is False
    checks["node_cap"] = {k:row[k] for k in ("nodes", "complete", "bounded_all", "class")}
    oversized = [(3,6,[("K",(0,3,4))]),
                 (3,6,[(0,(3,4,5)),("SELF",(3,4,6))])]
    row = D.compute_family(D.canonical(oversized))
    assert row["status"] == "block_size" and row["nodes"] == 0
    checks["block_cap"] = {k:row[k] for k in ("main_block_size", "s_block_size", "nodes", "status")}
    exact = original_exact([[(0,0)]], [1], {0:1}, range(4_000_001), [[0]])
    assert exact["eventually_bounded"] is None and exact["reason"] == "product size resource gate"
    checks["product_size_gate"] = exact
    with tempfile.TemporaryDirectory(dir=D.HERE, prefix="runtime_check_") as tmp:
        p = Path(tmp)/"rows.jsonl"
        settled_key = D.canonical([(3,0,[("SELF",(0,1,2))])])
        p.write_text(json.dumps(dict(key=settled_key)))
        recovered = R.read_rows(p, recover=True)
        assert len(recovered) == 1 and p.read_bytes().endswith(b"\n")
        p.write_bytes(p.read_bytes()+b'{"key":')
        recovered = R.read_rows(p, recover=True)
        assert len(recovered) == 1
        tails = list(p.parent.glob("rows.jsonl.interrupted_tail.*.bin"))
        assert len(tails) == 1 and tails[0].read_bytes() == b'{"key":'
        info = R.run_tasks([settled_key], p, workers=1, progress=False)
        assert info["resumed"] == 1 and info["written"] == 0
        checks["resume"] = dict(valid_no_newline_repaired=True, invalid_tail_preserved=True,
                                 existing_key_skipped=True)
    try:
        R.permitted("/tmp/reach_disallowed_output")
    except ValueError:
        checks["output_boundary"] = True
    else:
        raise AssertionError("output boundary not enforced")
    R.dump(D.HERE/"runtime_checks.json", dict(passed=True, checks=checks,
           prior_reach_dp_sha256="9fff2b1cdc77ea85cb286cc1b82e71e5921f3561e7d2fa93ec796287da268a19",
           resource_guard_change="RSS watchdog thread and forced post-referee checkpoint; block maps unchanged",
           code_sha256={name:hashlib.sha256((D.HERE/name).read_bytes()).hexdigest()
                        for name in ("reach_dp.py", "run_census.py", "check_runtime.py")}))
    print(json.dumps(dict(passed=True, checks=list(checks))))


if __name__ == "__main__":
    main()
