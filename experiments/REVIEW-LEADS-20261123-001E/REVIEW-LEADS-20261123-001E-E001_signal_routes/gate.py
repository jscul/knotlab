"""The gate (row G): both injected faults must be flagged and the unfaulted histories must pass.

  R1 fault: one loose distinction added to an existing knot at the third round (the history's last round
            when it has fewer than three).
  R2 fault: the join veto of the written-bit study on valued versions of the start.

Run first, from the repository root:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
Exit status 0 when the gate holds.
"""

import json
import sys
import time

import engine as E
import r1_holdings as R1
import r2_values as R2

PANEL = ["seven_knot_source", "five_founder_clock", "stall_11", "closing_11", "closing_00",
         "explosive_00", "explosive_04", "explosive_13", "concealed_type_00_funded", "concealed_type_11_funded"]
GATE_R1 = dict(rounds=6, knot_cap=400)
GATE_R2 = (6, 300)          # rounds, knot cap for the valued versions in the gate


def main():
    t0 = time.time()
    rows = {"r1": [], "r2": []}
    failures = []
    for name in PANEL:
        for law in E.LAWS:
            r1 = R1.run_history(name, law, rounds=GATE_R1["rounds"], knot_cap=GATE_R1["knot_cap"])
            rows["r1"].append(r1)
            if r1["clean_violations"] != 0:
                failures.append(("R1 clean history flagged", name, law))
            if r1["fault"].get("flagged") is not True:
                failures.append(("R1 fault missed", name, law))
            clean = R2.check_births(name, law, with_fault=False, horizon=GATE_R2)
            fault = R2.check_births(name, law, with_fault=True, horizon=GATE_R2)
            rows["r2"].append({"clean": clean, "fault": fault})
            if clean["versions_with_different_births"] != 0 or clean["versions_lawful_at_end"] != clean["versions"]:
                failures.append(("R2 clean history flagged", name, law))
            if fault["versions_with_different_births"] == 0:
                failures.append(("R2 fault missed", name, law))
            print(json.dumps({"history": name, "law": law,
                              "R1_clean_violations": r1["clean_violations"],
                              "R1_fault_flagged": r1["fault"].get("flagged"),
                              "R1_fault_injected_after_round": r1["fault"].get("injected_after_round"),
                              "R2_clean_differing": clean["versions_with_different_births"],
                              "R2_veto_differing": fault["versions_with_different_births"],
                              "versions": fault["versions"]}, sort_keys=True), flush=True)
    R1.ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (R1.ARTIFACTS / "gate.json").write_text(json.dumps({"rows": rows, "failures": failures,
                                                        "seconds": round(time.time() - t0, 1)}, indent=1, sort_keys=True) + "\n")
    print("GATE", "PASS" if not failures else "FAIL", failures)
    sys.exit(0 if not failures else 1)


if __name__ == "__main__":
    main()
