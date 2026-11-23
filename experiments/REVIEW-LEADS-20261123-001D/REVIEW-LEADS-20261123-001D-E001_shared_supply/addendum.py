"""Write the construction addendum before any joint start is grown.

Builds every joint start, checks it lawful under both knot laws, reads the first parent step's proposals (a plan, not a
growth), and writes `construction_addendum.md` and `.json`. Run from the repository root:

    timeout 600 prlimit --as=12884901888 .venv/bin/python -B experiments/REVIEW-LEADS-20261123-001D/\
REVIEW-LEADS-20261123-001D-E001_shared_supply/addendum.py

Nothing here writes a birth: `engine.ordinary_layer` only reads the proposals of the start.
"""
from collections import Counter
from datetime import datetime, timezone
import json

import engine
import lib

OUT_MD = lib.HERE / "construction_addendum.md"
OUT_JSON = lib.HERE / "construction_addendum.json"
SHA_FILE = lib.ARTIFACTS / "construction_addendum.sha256"


def alone_info(src):
    P = engine.Pres.from_stars(src.stars)
    status, parents, fresh, _ = engine.ordinary_layer(P)
    assert status == "extend"
    D = src.donor
    through = [g for g in parents if D in g]
    needed = {a: [r for r in src.needed(a) if r >= len(src.stars)] for a in src.future_ticks()}
    needed_thr = {a: sorted(r for r in rs if D in src.roles[r][0]) for a, rs in needed.items()}
    return {
        "knots": len(src.stars), "recorded_depth": src.depth, "donor": D, "donor_recorded_birth_depth": src.levels.get(D, 0),
        "first_ask_recorded_step": src.levels.get(D, 0) + 1, "donor_loose": P.loose[D], "donor_arity": len(src.stars[D]),
        "plan_births": len(parents), "plan_births_through_donor": [list(g) for g in through],
        "demand_on_donor": len(through), "future_ticks": src.future_ticks(),
        "needed_unrealized_roles": {a: len(v) for a, v in needed.items()},
        "needed_roles_through_donor": {a: v for a, v in needed_thr.items()},
        "needed_role_parent_sets_through_donor": {a: [list(src.roles[r][0]) for r in v] for a, v in needed_thr.items()},
        "plan": [list(g) for g in parents],
    }


def joint_info(j, X, Y, alone):
    P = engine.Pres.from_stars(j.stars)
    status, parents, fresh, shortages = engine.ordinary_layer(P)
    info = {"knots": len(j.stars), "distinctions": len({d for s in j.stars for d in s}), "donor": j.donor,
            "donor_arity": len(j.stars[j.donor]), "donor_loose": P.loose[j.donor],
            "donor_shared_with": sorted(P.nbr[j.donor]), "status_step1": status,
            "shortages": [list(map(int, s)) for s in shortages]}
    owners = Counter(d for s in j.stars for d in s)
    info["donor_shared_distinctions"] = sum(1 for d in j.stars[j.donor] if owners[d] == 2)
    if status == "extend":
        info["plan_births"] = len(parents)
        through = [g for g in parents if j.donor in g]
        cls = Counter()
        for g in through:
            if len(g) == 1:
                cls["unary"] += 1
                continue
            kinds = {j.origin[k] for k in g if k != j.donor}
            cls["X" if kinds <= {"X"} else "Y" if kinds <= {"Y"} else "cross"] += 1
        info["step1_proposals_through_donor"] = {"total": len(through), "x_pure": cls["X"], "y_pure": cls["Y"],
                                                 "cross": cls["cross"], "unary_among_them": cls["unary"]}
        mapped = set()
        for i in (0, 1):
            m = j.maps[i]
            for g in alone[i]["plan"]:
                mapped.add(tuple(sorted(m[k] for k in g)) if len(g) > 1 else (m[g[0]],))
        extra = [list(g) for g in parents if tuple(g) not in mapped]
        info["step1_proposals_not_in_either_alone_plan"] = extra
        info["step1_alone_proposals_missing_in_joint"] = len([g for g in mapped if g not in set(parents)])
    return info


def knot_rows(j):
    P = engine.Pres.from_stars(j.stars)
    inv = [{v: k for k, v in m.items()} for m in j.maps]
    rows = []
    for k, s in enumerate(j.stars):
        origin = j.origin[k]
        role = None
        depth = 0
        if origin in ("X", "D"):
            src, a = j.srcs[0], k
            depth = src.levels.get(a, 0)
        else:
            src, a = j.srcs[1], inv[1][k]
            depth = src.levels.get(a, 0)
        rows.append({"id": k, "origin": origin, "source_id": a, "recorded_depth": depth, "arity": len(s),
                     "loose": P.loose[k], "shared_with": sorted(P.nbr[k])})
    return rows


SPECS = [
    # name, class, X, Y, repair-needed
    ("S1", "same-step (recorded first asks 1 and 1), original donors", "R0", "R0", True),
    ("S2", "same-step (recorded first asks 6 and 6), first parents of tick 6", "R5", "R5", False),
    ("T1", "staggered (recorded first asks 1 and 6)", "R0", "R5", False),
    ("T2", "staggered (recorded first asks 6 and 10)", "R5", "R9", False),
    ("T3", "staggered (recorded first asks 1 and 6), marked original with the spare", "R0m", "R5", False),
]


def main():
    S = lib.ring_sources()
    phys = lib.recorded().physical
    doc = {"written_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "sources": {}, "starts": {}}
    alone = {k: alone_info(v) for k, v in S.items()}
    doc["sources"] = alone
    lines = []
    A = lines.append
    for name, label, xk, yk, needs_repair in SPECS:
        X, Y = S[xk], S[yk]
        entry = {"class": label, "x": xk, "y": yk, "variants": {}}
        repair = {}
        if needs_repair:
            unfunded = lib.merge(name + "-unfunded", X, Y, 0)
            st, _, _, shortages = engine.ordinary_layer(engine.Pres.from_stars(unfunded.stars))
            assert st == "stall"
            entry["unfunded_merge"] = {"step1_status": st, "shortages": [list(map(int, s)) for s in shortages]}
            repair = {int(k): int(n) for k, n in shortages}
        for s in (0, 1):
            j = lib.merge(f"{name}-s{s}", X, Y, s, repair)
            lawful = {}
            for law in lib.LAWS:
                phys.certify_source(j.stars, law)
                lawful[law] = ("every star's projected relation equals its full relation (fixtures.certify_source); "
                               "the knotlab K1-K3 checker is run on the relation of every arity up to 5, larger arities "
                               "use the same expected relation")
            info = joint_info(j, X, Y, [alone[xk], alone[yk]])
            info["lawful"] = lawful
            info["knots_table"] = knot_rows(j)
            entry["variants"][f"s{s}"] = info
        entry["repair_extra_loose_slots"] = repair
        doc["starts"][name] = entry

    # ---------------------------------------------------------------------------------------------------------------
    A("# Construction addendum, written before any joint start is grown")
    A("")
    A("Experiment `REVIEW-LEADS-20261123-001D-E001`. Frozen text of this file is hashed in "
      "`artifacts/REVIEW-LEADS-20261123-001D/REVIEW-LEADS-20261123-001D-E001_shared_supply/construction_addendum.sha256` "
      "before `gate.py` stage 2 or `grow.py` writes a single birth of a joint start. It supplements, and changes no "
      "definition in, `research/REVIEW-LEADS-20261123-001D/preregistration.md`.")
    A("")
    A("**Disclosure.** Before this file was written one ordinary growth of the repaired S1-type merge (both ring "
      "originals, shortage repair) was run in a scratch script outside the experiment folder to size the horizon: births "
      "per parent step 22, 36, 59, 101, 176, 320, 595 through step 7. No other joint start was grown and no outcome of "
      "any serial rule was read before this file was hashed.")
    A("")
    A("## 1. Which sources can be placed in a joint start inside the frozen horizon")
    A("")
    A("The horizon is 400 births or 12 completed parent steps. Gate 1 (`gate.py 1`, `gate1.json`) measures the ordinary "
      "growth of each recorded source alone. Only the clock of the scarcity study, the eight-knot ring with one marked "
      "spare, has a recorded tick inside the horizon (parent steps 6 and 10). The seven-knot source, the nine-knot drawn "
      "source and the two clocks of the 21-knot structure first tick at parent steps 15 to 31, after the cumulative "
      "ordinary births have passed 400 at step 7, 5 and 5 respectively. Those four are left out of the joint starts and "
      "recorded in `deviations.md`. Every joint start below therefore joins two copies of the scarcity clock, each "
      "copy taken at the cut where the donor is a knot of the recorded history.")
    A("")
    g1 = json.loads((lib.ARTIFACTS / "gate1.json").read_text())
    A("Gate 1 as run (`gate1.json`):")
    A("")
    A("| source alone | ordinary growth: tick made at step | guarded rule: tick made at birth number | recompute rule, `unrestricted`: first tick | recompute rule: second tick |")
    A("| --- | --- | --- | --- | --- |")
    for nm, r in g1["clock_alone"].items():
        o = r["ordinary"]["ticks_made_at_step"]
        gd = r["guarded"]["tick_birth_number"]
        rc = r["recompute"]["unrestricted"]
        ages = sorted(map(int, rc))
        first = rc[str(ages[0])]
        second = rc[str(ages[1])] if len(ages) > 1 else None
        A(f"| {nm} | {', '.join(f'tick {a}: {o[a]}' for a in sorted(o, key=int))} | "
          f"{', '.join(f'tick {a}: {gd[a]}' for a in sorted(gd, key=int))} | {first['status']} ({first.get('births', '-')} births, "
          f"{first['states_searched']} states) | {(second['status'] + ' (' + str(second['states_searched']) + ' states)') if second else 'none recorded after the stage'} |")
    A("")
    A("Under the `joins_first` pool the first tick is reproduced alone for " + ", ".join(
        nm for nm, r in g1["clock_alone"].items()
        if r["recompute"]["joins_first"][str(sorted(map(int, r["recompute"]["joins_first"]))[0])]["status"] == "made") +
      " and not for " + ", ".join(
        nm for nm, r in g1["clock_alone"].items()
        if r["recompute"]["joins_first"][str(sorted(map(int, r["recompute"]["joins_first"]))[0])]["status"] != "made") +
      " (exhausted at 745 states).")
    A("")
    A("Births at the recorded cuts (5, 6, 9, 10) agree with the scarcity receipt for the bare ring and both attachments. "
      "Other sources: " + "; ".join(f"{k}: cumulative ordinary births pass 400 at step {v['first_step_where_cumulative_births_pass_400']}, "
      f"first recorded tick at step {', '.join(str(t['first_tick_step']) for t in v['recorded_first_tick'].values())}"
      for k, v in g1["other_sources"].items()) + ".")
    A("")
    A("## 2. The construction")
    A("")
    A("A source is a presentation: the original ring, or the ring after 5 or 9 complete ordinary parent steps (the "
      "warm stages that the scarcity study already uses). Its donor is a knot that pays into its tick: an original "
      "(the ring knot opposite the marked one, or the marked one that holds the spare) or the first parent of a tick "
      "(knot 57 of the 63-knot stage for tick 6, knot 126 of the 135-knot stage for tick 10). The joint start is the "
      "disjoint union of the two presentations with the two donors made one knot. The merged knot holds both supports "
      "(every shared distinction and every loose distinction of both), less the shortfall s: s = 1 removes one loose "
      "distinction of the second source's part. A knot's holdings are never changed afterwards.")
    A("")
    A("Why the stage cuts: under ordinary growth every live knot pays all its loose distinctions in the single parent "
      "step after its birth (each leftover loose distinction pays one unary birth). Two sources that share one knot "
      "therefore always ask it in the same parent step of the joint growth. Two donors can differ only in recorded time: "
      "the step of the source's own recorded history at which its tick first draws on the donor "
      "(donor birth depth + 1). A pair is called **same-step** when these recorded steps are equal and "
      "**staggered** when they differ. A pair that differs in the step of the joint growth does not exist for a shared "
      "knot (stated, not tested).")
    A("")
    A("Merging two live knots that each have live neighbours changes the proposals: the merged knot is a common "
      "witness of its neighbours on both sides, so the four cross pairs between them are new proposals. With both donors "
      "original ring knots this is S1 below: the unfunded merge stalls at step 1 with the shortages listed. S1 is run "
      "with those exact shortages repaired (extra loose slots at the four neighbours, as the scarcity study's "
      "attachment does at a host's neighbours), reported as a second version of the definition. A donor whose "
      "neighbours on one side are all spent (a stage knot) creates no cross pair; S2, T1, T2 and T3 need no repair.")
    A("")
    A("## 3. The sources")
    A("")
    A("| source | stage | donor (id in stage) | recorded first ask | loose at donor | demand on donor (plan births through it) | roles through donor needed for tick 6 / tick 10 |")
    A("| --- | ---: | ---: | ---: | ---: | ---: | --- |")
    for k, v in alone.items():
        thr = v["needed_roles_through_donor"]
        A(f"| {k} | {v['recorded_depth']} | {v['donor']} | step {v['first_ask_recorded_step']} | {v['donor_loose']} | "
          f"{v['demand_on_donor']} | {', '.join(f'tick {a}: {len(r)}' for a, r in thr.items())} |")
    A("")
    A("## 4. The joint starts")
    A("")
    A("| start | class | X + Y | knots | donor | donor loose s=0 / s=1 | demand X + Y | recorded first asks | step-1 plan s=0 | step-1 plan s=1 |")
    A("| --- | --- | --- | ---: | ---: | --- | --- | --- | --- | --- |")
    for name, e in doc["starts"].items():
        v0, v1 = e["variants"]["s0"], e["variants"]["s1"]
        X, Y = S[e["x"]], S[e["y"]]
        dx, dy = alone[e["x"]]["demand_on_donor"], alone[e["y"]]["demand_on_donor"]
        fx, fy = alone[e["x"]]["first_ask_recorded_step"], alone[e["y"]]["first_ask_recorded_step"]
        A(f"| {name} | {e['class'].split(' (')[0]} | {e['x']} + {e['y']} | {v0['knots']} | {v0['donor']} | "
          f"{v0['donor_loose']} / {v1['donor_loose']} | {dx} + {dy} | {fx} / {fy} | "
          f"{v0['status_step1']}, {v0.get('plan_births', '-')} births | "
          f"{v1['status_step1']}, " + (f"{v1['plan_births']} births" if v1['status_step1'] == 'extend' else f"shortages {v1['shortages']}") + " |")
    A("")
    for name, e in doc["starts"].items():
        v0, v1 = e["variants"]["s0"], e["variants"]["s1"]
        A(f"### {name}: {e['class']}")
        A("")
        A(f"X = {e['x']}, Y = {e['y']}. The donor is joint knot {v0['donor']}, arity {v0['donor_arity']}, shared with "
          f"knots {v0['donor_shared_with']} through {v0['donor_shared_distinctions']} distinctions, loose "
          f"{v0['donor_loose']} (s = 0) or {v1['donor_loose']} (s = 1).")
        if "unfunded_merge" in e:
            A(f"Unfunded merge: step-1 status `{e['unfunded_merge']['step1_status']}`, shortages (knot, missing) "
              f"{e['unfunded_merge']['shortages']}. Repair used: extra loose slots {e['repair_extra_loose_slots']}.")
        pr = v0["step1_proposals_through_donor"]
        A(f"At s = 0 the first step is funded with {v0['plan_births']} births; {pr['total']} of them take a loose "
          f"distinction of the donor ({pr['x_pure']} from X's side, {pr['y_pure']} from Y's, {pr['cross']} cross, "
          f"{pr['unary_among_them']} unary). Proposals not in either source's alone plan: "
          f"{v0['step1_proposals_not_in_either_alone_plan']}; alone proposals missing from the joint plan: "
          f"{v0['step1_alone_proposals_missing_in_joint']}.")
        if v1["status_step1"] == "stall":
            A(f"At s = 1 the first step stalls with shortages {v1['shortages']}.")
        else:
            p1 = v1["step1_proposals_through_donor"]
            A(f"At s = 1 the first step is still funded, with {v1['plan_births']} births: {p1['total']} take a loose "
              f"distinction of the donor ({p1['x_pure']} from X's side, {p1['y_pure']} from Y's, {p1['unary_among_them']} "
              f"unary). The one missing distinction removes the unary birth of the donor from the plan.")
        A(f"Lawfulness (`certify_source`, both laws): {v0['lawful']['parity']}; the same for not-all-equal; also at s = 1.")
        A("")
        A("Every knot (id, origin X/Y/D, recorded birth depth, arity, loose, shared with):")
        A("")
        A("```")
        for r in v0["knots_table"]:
            A(f"{r['id']:>3} {r['origin']} d{r['recorded_depth']:<2} arity {r['arity']:<2} loose {r['loose']:<2} "
              f"shared {r['shared_with']}")
        A("```")
        A("")
    A("## 5. Fixed before any growth")
    A("")
    A("**Pairs.** Same-step: S2 (and S1 with its repair). Staggered: T1, T2, T3, in each of which the first member "
      "(X) asks earlier in recorded time. The earlier asker for P2 is X.")
    A("")
    A("**Registered ticks.** The recorded ticks of the scarcity study at tick ages 6 and 10, restricted to ages after "
      "the stage. A tick is made when a physical birth realizes its whole ancestry by parent sets (the role "
      "map of `raw.py`, `ordinary_roles` and `realizations`).")
    A("")
    A("**Ordinary growth** (gate 2): `engine.ordinary_layer`, whole parent steps, through the latest registered tick "
      "age of the start or until 100,000 cumulative births, whichever comes first (a tick age not reached is reported "
      "as not reached by the gate), checked against the archived `literal_turn` on the first three steps of every start.")
    A("")
    A("**Guarded serial rule**: write the ordinary plan of the least unfinished parent step one birth at a time; the "
      "births that are roles of a registered tick go first inside a step; a step whose plan is unfunded stalls as a "
      "whole and nothing after it is written; stop at 400 births or 12 completed parent steps.")
    A("")
    A("**Recompute-after-every-birth rule**: the proposals of `raw.py` (`facts`, `pool`, `apply`) with the child's "
      "fresh count read from the current demand, implemented count-level in `engine.py` and compared with the archived "
      "functions at every state of random walks (gate 1: 360 states per ring and pool policy, plus 60 per policy under "
      "not-all-equal, all equal). Pool policy `unrestricted` is primary; `joins_first` is reported separately and only "
      "for sources whose first tick the alone gate reproduces under it. A birth is **contested** when the shared donor "
      "has more enabled multi-parent proposals than loose distinctions. Every enabled multi-parent proposal through the "
      "donor is a branch at a contested birth; the contested births exist at the start and are resolved before any other "
      "birth, until none is contested. A **leaf** is a state with no contested birth. Branches are enumerated exactly with "
      "equal states merged (the numbers of choice sequences are exact); sampling by seed 2026112304 is used only if more "
      "than 20,000 distinct leaves occur. At each leaf the outcome of every registered tick is (a) `made` if a "
      "depth-first search (20,000 states) over births that are roles of the tick's ancestry finds a firing completion "
      "(run for the first registered tick of each source only, because gate 1 does not reproduce a second tick under "
      "this rule: from the original ring the search is undecided at 20,000 states, from the 63-knot stage it is exhausted "
      "at 193 states with no firing order); otherwise (b) `lost` if, after a fair continuation at the donor (every enabled "
      "multi-parent proposal through it written in ascending order, then offered unary births, until the donor holds no "
      "loose distinction), a parent that the tick requires holds no loose distinction (the certificate names the parent "
      "and the birth that spent its last one) or a larger common child excludes a required pair; otherwise `open`. "
      "For a second tick only (b) is applied.")
    A("")
    A("**Reading of the predictions.** P1: no registered tick of either source has a loss certificate in any branch "
      "at s = 0, under each rule. P2: at s = 1 on T1, T2, T3 the earlier asker X has no lost tick in any branch, under "
      "each rule; the failing clause (a branch in which the later asker keeps ticking and X loses) is reported as well. "
      "P3: at s = 1 on S1 and S2 both a branch in which X loses and Y does not and a branch in which Y loses and X does "
      "not occur. Where a stalled step writes nothing, the outcome is `stalled`, not a loss certificate, and is "
      "reported as such.")
    A("")
    text = "\n".join(lines) + "\n"
    OUT_MD.write_text(text)
    OUT_JSON.write_text(json.dumps(doc, indent=1, sort_keys=True) + "\n")
    lib.ARTIFACTS.mkdir(parents=True, exist_ok=True)
    digest = lib.file_sha256(OUT_MD)
    SHA_FILE.write_text(f"{digest}  construction_addendum.md\nwritten_utc {doc['written_utc']}\n"
                        f"json_sha256 {lib.file_sha256(OUT_JSON)}  construction_addendum.json\n")
    print(digest)


if __name__ == "__main__":
    main()
