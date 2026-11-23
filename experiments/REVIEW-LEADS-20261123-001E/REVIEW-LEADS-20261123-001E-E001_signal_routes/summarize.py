"""Print the tables of the draft note from the stored outputs (no recomputation).

  .venv/bin/python -B <this file>
"""

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
ART = ROOT / "artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes"


def load(name):
    return json.loads((ART / name).read_text())


def gate():
    g = load("gate.json")
    print("## Gate\n")
    print("| history | law | R1 clean violations | R1 fault (after round) flagged | R2 clean differing of 64 | R2 veto differing of 64 |")
    print("|---|---|---:|---|---:|---:|")
    for r1, r2 in zip(g["rows"]["r1"], g["rows"]["r2"], strict=True):
        f = r1["fault"]
        print(f"| {r1['history']} | {r1['law']} | {r1['clean_violations']} | {f.get('flagged')} ({f.get('injected_after_round')}) "
              f"| {r2['clean']['versions_with_different_births']} | {r2['fault']['versions_with_different_births']} |")
    print(f"\nfailures: {g['failures']}\n")


def r1():
    print("## R1\n")
    print("| history | law | rounds | knots | distinctions | clean violations | engine = reference (rounds) | unpaid loose after a funded round | fault flagged |")
    print("|---|---|---:|---:|---:|---:|---:|---:|---|")
    total = flagged = 0
    for name in sorted(ART.glob("r1_*.json")):
        for r in json.loads(name.read_text()):
            f = r["fault"]
            total += f.get("flagged") is not None
            flagged += bool(f.get("flagged"))
            print(f"| {r['history']} | {r['law']} | {r['rounds_grown']} | {r['knots_end']} | {r['distinctions_end']} | {r['clean_violations']} "
                  f"| {r['engine_agrees_with_reference_rounds']}/{r['engine_agrees_with_reference_rounds'] + r['engine_disagrees_with_reference_rounds'] + r['rounds_not_cross_checked_(not_connected_or_over_400_births)']} "
                  f"| {r['extra_audit']['unpaid_loose_after_round']} | {f.get('flagged')} (after round {f.get('injected_after_round')}) |")
    print(f"\nfaults flagged {flagged} of {total} injectable histories\n")


def r2():
    print("## R2\n")
    print("| history | law | rounds | knots | versions | lawful at end | differing | sampling |")
    print("|---|---|---:|---:|---:|---:|---:|---|")
    for name in sorted(ART.glob("r2_*.json")):
        if name.name.endswith("_fault.json"):
            continue
        for r in json.loads(name.read_text()):
            print(f"| {r['history']} | {r['law']} | {r['rounds']} | {r['knots_end']} | {r['versions']} | {r['versions_lawful_at_end']} "
                  f"| {r['versions_with_different_births']} | {r['sampling']} |")
    print()


def r3():
    print("## R3\n")
    print("| structure | law | step | old distinctions | births | raw allocations | classes | changed round births | changed later births | grown-word counts | classes with uniform-present TV > 0 | max TV uniform present | classes with old-word TV > 0 | max TV old-word |")
    print("|---|---|---|---:|---:|---:|---:|---:|---:|---|---:|---|---:|---|")
    for name in sorted(ART.glob("r3_*.json")):
        if name.name == "r3_minimal.json":
            continue
        d = json.loads(name.read_text())
        for s in d["steps"]:
            if "skipped" in s:
                print(f"| {d['structure']} | {d['law']} | {s['label']} | skipped | | | | | | {s['skipped']} | | | | |")
                continue
            if s.get("sampled_not_enumerated"):
                print(f"| {d['structure']} | {d['law']} | {s['label']} | {s['old_distinctions']} | {s['births']} | {s['raw_allocations']} "
                      f"| {s['allocations_sampled']} sampled | {s['classes_with_changed_round_births']} | {s['classes_with_changed_later_births']} "
                      f"| {s['grown_allowed_words_canonical']} (different counts: {s['classes_with_different_grown_word_count']}) | not computed | | not computed | |")
                continue
            print(f"| {d['structure']}{' (beyond cap)' if 'beyond' in name.name else ''} | {d['law']} | {s['label']} | {s['old_distinctions']} | {s['births']} | {s['raw_allocations']} "
                  f"| {s['allocation_classes']} | {s['classes_with_changed_round_births']} | {s['classes_with_changed_later_births']} "
                  f"| {s['distinct_grown_allowed_word_counts']} | {s['classes_with_uniform_present_tv_nonzero']} | {s['max_tv_uniform_present_vs_canonical']} ({s['max_tv_uniform_present_decimal']:.6f}) "
                  f"| {s['classes_with_old_word_tv_nonzero']} | {s['max_tv_old_word_vs_canonical']} |")
    print("\n### per knot (only that knot's allocation varies)\n")
    print("| structure | law | step | knot | loose | group births | unary births | classes | interchangeable (uniform present) | max TV uniform present | interchangeable (old word) |")
    print("|---|---|---|---:|---:|---:|---:|---:|---|---|---|")
    for name in sorted(ART.glob("r3_*.json")):
        if name.name == "r3_minimal.json":
            continue
        d = json.loads(name.read_text())
        for s in d["steps"]:
            for k, info in sorted(s.get("knots", {}).items(), key=lambda kv: int(kv[0])):
                num, den = map(int, info["uniform_max_tv"].split("/"))
                print(f"| {d['structure']}{' (beyond cap)' if 'beyond' in name.name else ''} | {d['law']} | {s['label']} | {k} | {info['loose']} | {info['group_births']} | {info['unary_births']} "
                      f"| {info['classes']} | {info['interchangeable_uniform_present']} | {info['uniform_max_tv']} ({num / den:.6f}) | {info['interchangeable_old_word']} |")
    print()


def r4_r5():
    d = load("r4_groups.json")
    print("## R4\n")
    print(json.dumps(d["summary"], indent=1, sort_keys=True))
    print(json.dumps(d["reference_operator_proposals_equal_on_stages"]), json.dumps(d["parent_rosters_equal_under_both_laws"]))
    print("\n## R5\n")
    for r in load("r5_order.json"):
        c, t = r["control"], r["treatment"]
        print(f"- {r['naming']} / {r['law']}: both choices eligible {r['both_choices_eligible_after_recompute']}; control tick at birth {c['tick_birth_number']}; "
              f"treatment tick {t['marked_turn_realized_at']} (donor loose after {t['donor_loose_after']}); order decides {r['order_decides_tick']}; "
              f"ordinary round on the same prefix: {r['ordinary_round_on_the_same_prefix']['status']}")
    print()


def minimal():
    path = ART / "r3_minimal.json"
    if not path.exists():
        return
    d = load("r3_minimal.json")
    print("## Smallest lawful start with an allocation effect\n")
    print(json.dumps(d["search"], sort_keys=True))
    print(json.dumps(d.get("example_gate", {}), sort_keys=True))
    for law, table in d.get("example", {}).items():
        print(f"\n### {law}\n")
        print("knots", table["knots"], "births", table["births"])
        print("old words (bit i = i-th distinction):", table["old_words"])
        for a in table["allocations"]:
            print(" pays", a["pays"], "children inputs", a["children_inputs"], "uniform-present weights", a["uniform_present_weights_per_word"],
                  "total", a["uniform_present_total"], "TV vs first", a["tv_uniform_present_vs_first"])


if __name__ == "__main__":
    for part in (gate, r1, r2, r3, r4_r5, minimal):
        try:
            part()
        except FileNotFoundError as error:
            print("missing:", error)
