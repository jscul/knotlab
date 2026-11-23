"""R5, order.  One replay of the recorded case in which the order of births under the
recompute-after-every-birth rule decides whether a tick is lost.

Recorded case: artifacts/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A/.../witness.json (eight-knot
clock with an attached original, nine common births, then at birth 10 either the clock's own pair 4,6
(control) or the pair 4 and the attached original (treatment); both take the one remaining loose
distinction of knot 4).

This script rebuilds every birth itself.  The serial rule is recomputed from the holdings after every
birth: the pool is the set of groups of the present holdings that have no older common child, plus a
unary birth for every live knot that holds more loose distinctions than the groups in the pool use.
Reference ancestry of the marked tick and the ancestry-isomorphism test are imported read-only from
research/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001/audit_last_spend.py.

Run (from the repository root):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""

from collections import Counter
import json
import sys

import engine as E

ROOT = E.ROOT
WITNESS = ROOT / ("artifacts/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A/"
                  "LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001A-E001_last_slot/witness.json")
AUDIT = ROOT / "research/LAST-DISTINCTION-AND-PRIVATE-PULSES-20261121-001/audit_last_spend.py"
ARTIFACTS = ROOT / "artifacts/REVIEW-LEADS-20261123-001E/REVIEW-LEADS-20261123-001E-E001_signal_routes"


def serial_pool(holdings, original_count):
    """Eligible births under recompute-after-every-birth with unrestricted priority."""
    owners = E.holders_of(holdings)
    loose = E.loose_of(holdings, owners)
    nbrs = E.neighbours_of(holdings, owners)
    groups = E.proposed_groups(holdings, owners, loose, nbrs)
    children = [{j for j in n if j >= original_count and j > i} for i, n in enumerate(nbrs)]
    groups = [g for g in groups if not set.intersection(*(children[j] for j in g))]
    use = Counter(j for g in groups for j in g)
    unary = [(j,) for j, ds in loose.items() if len(ds) > use[j]]
    return {tuple(g) for g in groups} | set(unary), loose, owners


def write_event(holdings, event, original_count):
    pool, loose, owners = serial_pool(holdings, original_count)
    parents = tuple(sorted(event["parents"]))
    assert parents in pool, ("not eligible after recompute", parents)
    consumed = event["consumed_slots"]
    assert [owners[s] for s in consumed] == [[p] for p in event["parents"]], "slot not held loose by the parent"
    assert event["child"] == len(holdings)
    fresh = event["fresh"]
    assert not set(fresh) & set(owners)
    return holdings + [list(consumed) + list(fresh)], pool


def replay(case, reference, audit, law):
    source = [list(r) for r in case["source"]]
    n0 = len(source)
    attached = n0 - 1
    holdings = [list(r) for r in source]
    writes = {}
    pools = []
    for event in case["common"]:
        holdings, pool = write_event(holdings, event, n0)
        pools.append(len(pool))
        writes[event["child"]] = event["parents"]
    prefix = [list(r) for r in holdings]
    prefix_writes = dict(writes)
    pool, loose, owners = serial_pool(prefix, n0)
    control_group, outside_group = tuple(sorted(case["control"][0]["parents"])), tuple(sorted(case["treatment"][0]["parents"]))
    report = {"law": law, "common_births": len(case["common"]), "pool_sizes_along_common_prefix": pools,
              "pool_at_fork": len(pool),
              "both_choices_eligible_after_recompute": control_group in pool and outside_group in pool,
              "control_group": control_group, "outside_group": outside_group,
              "loose_of_donor_before_fork": loose[4], "same_last_slot_in_both_choices":
              case["control"][0]["consumed_slots"][case["control"][0]["parents"].index(4)]
              == case["treatment"][0]["consumed_slots"][case["treatment"][0]["parents"].index(4)] == loose[4][0]}
    assert report["both_choices_eligible_after_recompute"] and len(loose[4]) == 1

    # ordinary contrast: the complete-round rule on the same prefix has no order to choose
    plan = E.plan_round([tuple(r) for r in prefix], law)
    report["ordinary_round_on_the_same_prefix"] = {
        "status": plan.status, "shortages": plan.shortages,
        "proposes_both_pairs": control_group in plan.groups and outside_group in plan.groups}

    results = {}
    for key, events in (("control", case["control"]), ("treatment", case["treatment"])):
        holdings, writes = [list(r) for r in prefix], dict(prefix_writes)
        for event in events:
            holdings, _ = write_event(holdings, event, n0)
            writes[event["child"]] = event["parents"]
        loose_after = audit.held_loose(holdings)
        old_knots_unchanged = all(list(holdings[k]) == list(source[k]) for k in range(n0))
        possible, later = audit.future_bound(reference["graph"], reference["roles"], writes, loose_after)
        hits = audit.exact_turns(reference["graph"], writes)
        results[key] = {"births_after_prefix": len(events), "total_births": len(writes) - 0,
                        "marked_turn_realized_at": hits, "tick_birth_number": (hits[0] - n0 + 1) if hits else None,
                        "tick_still_possible_by_future_bound": bool(possible[reference["tip"]]) or bool(later[reference["tip"]]),
                        "donor_loose_after": sorted(loose_after[4]), "old_knot_holdings_unchanged": old_knots_unchanged,
                        "pair_4_6_has_common_child": any({4, 6} <= set(ps) for ps in writes.values())}
        if key == "treatment":
            # permanent exhaustion: knot 4 is spent and no later birth can give a spent knot a loose distinction
            pool_after, _, _ = serial_pool(holdings, n0)
            results[key]["pair_4_6_proposable_after"] = control_group in pool_after
            results[key]["knot_4_live_after"] = 4 in {j for j, ds in E.loose_of(holdings).items() if ds}
        else:
            pool_after, _, _ = serial_pool(holdings, n0)
            results[key]["outside_pair_proposable_after_tick"] = outside_group in pool_after
    report.update(results)
    c, t = results["control"], results["treatment"]
    report["order_decides_tick"] = bool(c["old_knot_holdings_unchanged"] and t["old_knot_holdings_unchanged"]
                                        and c["marked_turn_realized_at"] and not t["marked_turn_realized_at"]
                                        and not t["tick_still_possible_by_future_bound"]
                                        and not c.get("outside_pair_proposable_after_tick", True))
    return report


def main():
    audit = E.load_module(AUDIT, "audit_last_spend")
    sys.path.insert(0, str(ROOT / "research/TICK-BIRTHS-AND-SCARCITY-20261121-001"))
    graph, roles, tip = audit.reference_turn()
    reference = {"graph": graph, "roles": roles, "tip": tip}
    data = json.loads(WITNESS.read_bytes())
    rows = []
    for naming in ("witnesses", "reversed_source_names"):
        for law, case in data[naming].items():
            row = replay(case, reference, audit, law)
            row["naming"] = naming
            rows.append(row)
            print(json.dumps(row, sort_keys=True, default=list), flush=True)
    ok = all(r["order_decides_tick"] and r["both_choices_eligible_after_recompute"] for r in rows)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "r5_order.json").write_text(json.dumps(rows, indent=1, sort_keys=True, default=list) + "\n")
    print("R5", "replayed: the order decides the tick in every law and naming" if ok else "NOT REPLAYED")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
