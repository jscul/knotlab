"""R4, groups.  Whether the proposed parent groups are a function of the holdings alone, by reading the
engine and by two replays.

Reading.  The functions that form the groups are listed with their parameters and with every name they
read (abstract syntax tree).  The compact reference operator is read the same way.  A reading cannot show
that a function ignores a quantity it is handed, so the replays below do the work.

Replay 1 (renaming).  At every stage of every history, rename all distinctions and renumber all knots by
random permutations and recompute the groups; the groups must be the images of the original groups.
Replay 2 (allocations, values, laws).  Grow each history with a random allocation of loose distinctions
at every round (eight allocations per history), and with valued versions under the clean engine; the
groups at every stage must equal those of the canonical-allocation history (knot numbers are fixed by
the births, so the comparison is direct).  The same stage frames under the two laws must give the same
groups.
Control.  The join-veto engine hands the same holdings different groups under different values; the
replay must catch it.

Run (from the repository root):
  timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file>
"""

import ast
import inspect
import json
import random
import time

import engine as E
import r1_holdings as R1
import r2_values as R2

ARTIFACTS = R1.ARTIFACTS
SEED = 2026112305
PANEL = ["seven_knot_source", "five_founder_clock", "explosive_00", "explosive_04", "explosive_13", "stall_00", "stall_01",
         "stall_11", "closing_11", "closing_01", "concealed_type_00_funded", "concealed_type_11_funded"]
HORIZON = dict(rounds=8, knot_cap=400)
ALLOCATIONS = 8
FORBIDDEN = {"values", "vals", "value", "word", "ref", "reference", "veto", "law", "rng", "random"}


# ----------------------------------------------------------------------------------------------
# Reading
# ----------------------------------------------------------------------------------------------

def names_read(function):
    tree = ast.parse(inspect.getsource(function).lstrip())
    loads = sorted({n.id for n in ast.walk(tree) if isinstance(n, ast.Name) and isinstance(n.ctx, ast.Load)})
    attrs = sorted({n.attr for n in ast.walk(tree) if isinstance(n, ast.Attribute)})
    params = [a.arg for a in tree.body[0].args.args]
    return {"parameters": params, "names_read": loads, "attributes_read": attrs}


def reading():
    out = {}
    for f in (E.holders_of, E.loose_of, E.neighbours_of, E.groups_from_adjacency, E.proposed_groups,
              E.lookahead_demand):
        info = names_read(f)
        info["reads_forbidden_names"] = sorted(set(info["parameters"]) & FORBIDDEN | set(info["names_read"]) & FORBIDDEN)
        out[f.__name__] = info
    ref = E.reference_operator()
    for f in (ref.neighbors, ref.from_stars, ref._maximal_groups, ref._proposals, ref.proposals):
        info = names_read(f)
        info["reads_forbidden_names"] = sorted(set(info["parameters"]) & FORBIDDEN | set(info["names_read"]) & FORBIDDEN)
        out["reference." + f.__name__] = info
    plan_src = inspect.getsource(E.plan_round)
    tree = ast.parse(plan_src)
    # where plan_round reads `law` and `veto`: after the groups are formed
    lines = plan_src.splitlines()
    first_group = next(i for i, l in enumerate(lines) if "proposed_groups(" in l)
    law_lines = [i for i, l in enumerate(lines) if "law" in l and i > first_group and "assert" not in l]
    out["plan_round"] = {"group_call_line": first_group, "lines_using_law_after_groups": law_lines,
                         "lines_using_veto": [i for i, l in enumerate(lines) if "veto" in l]}
    return out


# ----------------------------------------------------------------------------------------------
# Replays
# ----------------------------------------------------------------------------------------------

def stage_frames(name, law):
    stars = R1.start_for(name)
    h = E.grow_history(stars, law, HORIZON["rounds"], knot_cap=HORIZON["knot_cap"], cross_check=False)
    return h.frames


def groups_of(frame):
    return E.proposed_groups(frame)


def rename(frame, rng):
    names = sorted({d for r in frame for d in r})
    new = rng.sample(range(10 * len(names) + 10), len(names))
    dmap = dict(zip(names, new, strict=True))
    order = list(range(len(frame)))
    rng.shuffle(order)                # order[i] = old index placed at new index i
    where = {old: i for i, old in enumerate(order)}
    renamed = tuple(tuple(rng.sample([dmap[d] for d in frame[old]], len(frame[old]))) for old in order)
    return renamed, where


def replay_renaming(frames, rng):
    stages = checked = bad = 0
    for frame in frames:
        base = groups_of(frame)
        renamed, where = rename(frame, rng)
        image = {tuple(sorted(where[k] for k in g)) for g in base}
        stages += 1
        checked += len(base)
        bad += set(groups_of(renamed)) != image
    return {"stages": stages, "groups": checked, "stages_not_covariant": bad}


def random_allocation(plan, rng):
    allocation = E.canonical_allocation(plan)
    for k in allocation:
        rng.shuffle(allocation[k])
    return allocation


def replay_allocations(stars, law, canonical_groups, rounds, cap, rng):
    frame, mismatches, stages = tuple(tuple(r) for r in stars), 0, 0
    for t in range(rounds):
        room = None if cap is None else cap - len(frame)
        plan = E.plan_round(frame, law, max_births=room)
        if plan.status != "extend":
            break
        frame, _ = E.apply_plan(frame, plan, random_allocation(plan, rng))
        stages += 1
        mismatches += groups_of(frame) != canonical_groups[t + 1]
    return stages, mismatches


def replay_values(stars, law, canonical_groups, rounds, cap, rng):
    word = R2.valued_versions(stars, law, rng, 1)[0]
    frames, _, _ = R2.grow_valued(stars, word, law, rounds, cap, rng)
    return sum(groups_of(f) != canonical_groups[i] for i, f in enumerate(frames) if i < len(canonical_groups)), len(frames)


def replay_spare_edit(frames, rng, per_stage=4):
    """Supplementary: an extra loose distinction at a knot that is already live (an edit of the holdings)
    leaves the proposed groups unchanged; it changes funding only."""
    tested = unchanged = funding_changed = 0
    for frame in frames:
        loose = E.loose_of(frame)
        live = [k for k, ds in loose.items() if ds]
        base = groups_of(frame)
        base_status = E.plan_round(frame, "nae", max_births=0).status
        for k in rng.sample(live, min(per_stage, len(live))):
            top = max(d for r in frame for d in r) + 1
            edited = frame[:k] + (frame[k] + (top,),) + frame[k + 1:]
            tested += 1
            unchanged += groups_of(edited) == base
            funding_changed += E.plan_round(edited, "nae", max_births=0).status != base_status
    return {"edits": tested, "edits_leaving_groups_unchanged": unchanged, "edits_changing_status": funding_changed}


def control_veto(stars, law, rng, versions=64):
    """Same holdings, different values: the join veto changes the proposed groups, a replay must see it."""
    words = R2.valued_versions(stars, law, rng, versions)
    ref = R2.reference_word(stars, law)
    plain = E.plan_round(stars, law)
    differing = 0
    for word in words:
        veto = lambda g: any(word[d] != ref[d] for p in g for d in stars[p])
        faulted = E.plan_round(stars, law, veto)
        differing += set(faulted.groups) != set(plain.groups)
    return differing


def main():
    t0 = time.time()
    result = {"reading": reading(), "rows": []}
    forbidden_hits = {k: v["reads_forbidden_names"] for k, v in result["reading"].items() if "reads_forbidden_names" in v}
    for name in PANEL:
        for law in E.LAWS:
            rng = random.Random(f"{SEED}:r4:{name}:{law}")
            frames = stage_frames(name, law)
            canonical_groups = [groups_of(f) for f in frames]
            row = {"history": name, "law": law, "stages": len(frames), "knots_end": len(frames[-1]),
                   "renaming": replay_renaming(frames, rng)}
            alloc_stages = alloc_bad = 0
            for _ in range(ALLOCATIONS):
                s, b = replay_allocations(R1.start_for(name), law, canonical_groups, HORIZON["rounds"], HORIZON["knot_cap"], rng)
                alloc_stages += s
                alloc_bad += b
            row["allocations"] = {"allocation_histories": ALLOCATIONS, "stages": alloc_stages, "stages_with_other_groups": alloc_bad}
            bad_v, n_v = replay_values(R1.start_for(name), law, canonical_groups, HORIZON["rounds"], HORIZON["knot_cap"], rng)
            row["valued_version"] = {"stages": n_v, "stages_with_other_groups": bad_v}
            row["spare_edit_at_a_live_knot"] = replay_spare_edit(frames, rng)
            row["veto_control_versions_with_other_groups_of_64"] = control_veto(R1.start_for(name), law, rng)
            result["rows"].append(row)
            print(json.dumps(row, sort_keys=True), flush=True)
    # the two laws on identical frames: the reference operator's birth roster (its groups plus unary births)
    # under parity and under not-all-equal, and its proposals, against ours on every connected stage
    ref = E.reference_operator()
    law_equal = law_total = agree = total = 0
    for name in PANEL:
        for frame in stage_frames(name, "nae")[:6]:
            try:
                end = ref.from_stars(frame)
            except ValueError:
                continue
            total += 1
            agree += tuple(sorted(ref.proposals(end))) == tuple(sorted(E.proposed_groups(frame)))
            tp, tn = ref.step(end, "parity", max_births=4000), ref.step(end, "nae", max_births=4000)
            law_total += 1
            law_equal += (tp.status == tn.status) and (tp.parents == tn.parents) and (tp.demand == tn.demand)
    result["reference_operator_proposals_equal_on_stages"] = {"agree": agree, "total": total}
    result["parent_rosters_equal_under_both_laws"] = {"equal": law_equal, "total": law_total}
    result["forbidden_names_read_by_group_functions"] = forbidden_hits
    rows = result["rows"]
    result["summary"] = {
        "reading_flags": {k: v for k, v in forbidden_hits.items() if v},
        "renaming_stages_not_covariant": sum(r["renaming"]["stages_not_covariant"] for r in rows),
        "allocation_stages_with_other_groups": sum(r["allocations"]["stages_with_other_groups"] for r in rows),
        "valued_stages_with_other_groups": sum(r["valued_version"]["stages_with_other_groups"] for r in rows),
        "stages_replayed": sum(r["renaming"]["stages"] for r in rows),
        "spare_edits_tested": sum(r["spare_edit_at_a_live_knot"]["edits"] for r in rows),
        "spare_edits_leaving_groups_unchanged": sum(r["spare_edit_at_a_live_knot"]["edits_leaving_groups_unchanged"] for r in rows),
        "spare_edits_changing_status": sum(r["spare_edit_at_a_live_knot"]["edits_changing_status"] for r in rows),
        "allocation_stages_replayed": sum(r["allocations"]["stages"] for r in rows),
        "veto_control_caught": sum(r["veto_control_versions_with_other_groups_of_64"] > 0 for r in rows), "veto_control_rows": len(rows),
        "seconds": round(time.time() - t0, 1)}
    ARTIFACTS.mkdir(parents=True, exist_ok=True)
    (ARTIFACTS / "r4_groups.json").write_text(json.dumps(result, indent=1, sort_keys=True) + "\n")
    print(json.dumps(result["summary"], sort_keys=True))
    print(json.dumps(result["reference_operator_proposals_equal_on_stages"]))
    print(json.dumps(result["parent_rosters_equal_under_both_laws"]))
    print(json.dumps(forbidden_hits, sort_keys=True))


if __name__ == "__main__":
    main()
