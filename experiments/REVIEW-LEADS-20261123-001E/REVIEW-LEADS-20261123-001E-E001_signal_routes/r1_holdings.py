"""R1, holdings.  In each history every knot's set of distinctions is the same at every later stage as at
its birth.  Injected fault: one loose distinction added to an existing knot at the third step; the check
must flag it.

The recorder reads only the recorded frames (tuples of supports).  Extra audits, reported separately and
not part of the frozen definition: that every funded round pays every loose distinction (nothing is
withheld), that a stall repeats, and that the engine agrees with the compact reference operator.

Run (from the repository root), one group at a time:
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> --group source
Groups: source clock explosive stall closing concealed
"""

import argparse
from collections import defaultdict
import json
import time

import engine as E
import starts as S

ARTIFACTS = E.ROOT / "artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes"

# horizons (rounds) and knot caps; rounds are atomic, so a cap stops before a round that would exceed it
HORIZON = {
    "seven_knot_source": dict(rounds=12, knot_cap=None),          # 12 parent steps
    "five_founder_clock": dict(rounds=31, knot_cap=None),         # six returns: returns at ages 6, 11, ..., 31
    "explosive_00": dict(rounds=400, knot_cap=2000),
    "explosive_04": dict(rounds=400, knot_cap=2000),
    "explosive_13": dict(rounds=400, knot_cap=2000),
}
DEFAULT_HORIZON = dict(rounds=12, knot_cap=2000)

GROUPS = {
    "source": ["seven_knot_source"],
    "clock": ["five_founder_clock"],
    "explosive": ["explosive_00", "explosive_04", "explosive_13"],
    "stall": ["stall_00", "stall_01", "stall_10", "stall_11"],
    "closing": ["closing_00", "closing_01", "closing_10", "closing_11"],
    "concealed": ["concealed_type_00_funded", "concealed_type_01_funded", "concealed_type_10_funded",
                  "concealed_type_11_funded", "concealed_type_00_unedited", "concealed_type_01_unedited",
                  "concealed_type_10_unedited", "concealed_type_11_unedited"],
}


def start_for(name):
    import re
    if name == "seven_knot_source":
        return S.seven_knot_source()
    if name == "five_founder_clock":
        return S.five_founder_clock()
    m = re.fullmatch(r"explosive_(\d\d)", name)
    if m:
        return S.archived_explosive("start-" + m.group(1))
    m = re.fullmatch(r"(stall|closing)_(\d)(\d)", name)
    if m:
        make = S.stall_start if m.group(1) == "stall" else S.closing_start
        return make((int(m.group(2)), int(m.group(3))))
    m = re.fullmatch(r"concealed_type_(\d)(\d)_(funded|unedited)", name)
    if m:
        u, v = int(m.group(1)), int(m.group(2))
        return S.concealed_start(u, v, *((u, v) if m.group(3) == "funded" else (None, None)))
    raise KeyError(name)


# ----------------------------------------------------------------------------------------------
# The check (recorder side only)
# ----------------------------------------------------------------------------------------------

def check_holdings(frames):
    """Return the list of (knot, birth stage, later stage) at which a knot's set of distinctions differs
    from its set at birth."""
    born = {k: 0 for k in range(len(frames[0]))}
    for t in range(1, len(frames)):
        for k in range(len(frames[t - 1]), len(frames[t])):
            born[k] = t
    violations = []
    for t, frame in enumerate(frames):
        for k, row in enumerate(frame):
            if set(frames[born[k]][k]) != set(row) or len(frames[born[k]][k]) != len(row):
                violations.append((k, born[k], t))
    return violations


def extra_audit(frames):
    """Diagnostics beyond the frozen definition: holder counts and payment of every loose distinction."""
    report = {"rounds": len(frames) - 1, "holder_count_violations": 0, "unpaid_loose_after_round": 0,
              "old_distinction_second_holder_only_from_new_knots": True}
    for before, after in zip(frames, frames[1:]):
        holds_before = defaultdict(list)
        for k, row in enumerate(before):
            for d in row:
                holds_before[d].append(k)
        holds_after = defaultdict(list)
        for k, row in enumerate(after):
            for d in row:
                holds_after[d].append(k)
        for d, hs in holds_after.items():
            if len(hs) not in (1, 2) or len(set(hs)) != len(hs):
                report["holder_count_violations"] += 1
        for d, hs in holds_before.items():
            gained = [h for h in holds_after[d] if h not in hs]
            if any(h < len(before) for h in gained):
                report["old_distinction_second_holder_only_from_new_knots"] = False
            if len(hs) == 1 and len(holds_after[d]) != 2:
                report["unpaid_loose_after_round"] += 1
    return report


def fault_at(round_number):
    def edit(t, frame):
        if t != round_number:
            return frame
        top = max(d for row in frame for d in row) + 1
        return (frame[0] + (top,),) + tuple(frame[1:])
    return edit


def run_history(name, law, rounds=None, knot_cap="default", cross_check=True):
    hz = dict(HORIZON.get(name, DEFAULT_HORIZON))
    if rounds is not None:
        hz["rounds"] = rounds
    if knot_cap != "default":
        hz["knot_cap"] = knot_cap
    stars = start_for(name)
    t0 = time.time()
    clean = E.grow_history(stars, law, hz["rounds"], knot_cap=hz["knot_cap"], cross_check=cross_check, name=name)
    clean_violations = check_holdings(clean.frames)
    entry = {"history": name, "law": law, "rounds_grown": len(clean.frames) - 1, "statuses_tail": clean.statuses[-1:],
             "knots_end": len(clean.frames[-1]),
             "distinctions_end": len({d for r in clean.frames[-1] for d in r}),
             "births_per_round_head": [len(b) for b in clean.births][:14],
             "clean_violations": len(clean_violations),
             "engine_agrees_with_reference_rounds": sum(c is True for c in clean.cross_checks),
             "engine_disagrees_with_reference_rounds": sum(c is False for c in clean.cross_checks),
             "rounds_not_cross_checked_(not_connected_or_over_400_births)": sum(c is None for c in clean.cross_checks),
             "extra_audit": extra_audit(clean.frames)}
    # injected fault: third step if the history has one, otherwise its last round (recorded)
    rounds_available = len(clean.frames) - 1
    if rounds_available >= 1:
        at = 3 if rounds_available >= 3 else rounds_available
        faulted = E.grow_history(stars, law, min(hz["rounds"], max(at + 3, 6)), knot_cap=hz["knot_cap"], cross_check=False,
                                 edit=fault_at(at), name=name + "+fault")
        flagged = check_holdings(faulted.frames)
        entry["fault"] = {"injected_after_round": at, "is_third_step": at == 3,
                          "violations": len(flagged), "flagged": bool(flagged),
                          "first_violation": flagged[0] if flagged else None}
    else:
        entry["fault"] = {"injected_after_round": None, "note": "history has no funded round", "flagged": None}
    entry["seconds"] = round(time.time() - t0, 1)
    return entry


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--group", choices=sorted(GROUPS))
    parser.add_argument("--history", help="a single history of the group (own output file)")
    parser.add_argument("--law", choices=E.LAWS)
    args = parser.parse_args()
    assert args.group or args.history
    laws = [args.law] if args.law else list(E.LAWS)
    rows = []
    names = [args.history] if args.history else GROUPS[args.group]
    label = args.history or args.group
    for name in names:
        for law in laws:
            row = run_history(name, law)
            rows.append(row)
            print(json.dumps({k: v for k, v in row.items() if k != "extra_audit"}, sort_keys=True), flush=True)
            print("   extra", json.dumps(row["extra_audit"], sort_keys=True), flush=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    suffix = f"_{args.law}" if args.law else ""
    (ARTIFACTS / f"r1_{label}{suffix}.json").write_text(json.dumps(rows, indent=1, sort_keys=True) + "\n")
    print("clean violations:", sum(r["clean_violations"] for r in rows),
          "| faults flagged:", sum(bool(r["fault"].get("flagged")) for r in rows), "of",
          sum(r["fault"].get("flagged") is not None for r in rows))


if __name__ == "__main__":
    main()
