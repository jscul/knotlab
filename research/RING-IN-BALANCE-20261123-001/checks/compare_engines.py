"""Gate G(a) of ticket C, and a cross-check of ticket A's engine: two engines written independently from the frozen text.
Ticket C's part-round law under ALL-IN-TURN (c0_trace.json) against ticket A's complete rounds (extra_trace.json), rounds 1
to 8, on Ring(5, 3), D2(4, 3) and D2(5, 3) under the two and the three added rules.  Compared per round: members, parts,
sorted usable loose counts, sorted sizes of the inclusion-maximal met sets, births, total fresh distinctions, and the sorted
list of births as (parents, fresh).  Run from the repository root."""
import json, pathlib
root = pathlib.Path(__file__).resolve().parents[3]
a = json.loads((root / "artifacts/RING-IN-BALANCE-20261123-001A/RING-IN-BALANCE-20261123-001A-E001_ring/extra_trace.json").read_text())["runs"]
c = json.loads((root / "artifacts/RING-IN-BALANCE-20261123-001C/RING-IN-BALANCE-20261123-001C-E001_no_round/c0_trace.json").read_text())["runs"]
ok = True
for start_c, start_a in (("Ring(5,3)", "Ring(5, 3)"), ("D2(4,3)", "D2(4, 3)"), ("D2(5,3)", "D2(5, 3)")):
    for law in ("two", "three"):
        ra = {r["round"]: r for r in a[f"{start_a} | {law} added rules"]["rows"]}
        same = True
        for row in c[start_c][law]:
            x = ra[row["sweep"]]
            left = (row["members"], row["parts"], row["h_sorted"], row["maximal_met_set_sizes_sorted"], row["births"], row["fresh_total"], [list(b) for b in row["births_sorted"]])
            right = (x["members"], x["parts"], sorted(x["h"]), sorted(x["metset_sizes"]), x["births"], x["fresh_total"], sorted(list(b) for b in x["birth_list"]))
            if left != right:
                same = ok = False
                print(f"{start_c} {law} round {row['sweep']}: DIFFER\n  C: {left}\n  A: {right}")
                break
        print(f"{start_c:10s} {law:5s} rules: {'equal on rounds 1 to 8' if same else 'differ'}")
print("G(a):", "pass" if ok else "FAIL")
