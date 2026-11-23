"""Gates of REVIEW-LEADS-20261123-001D-E001.

    stage 1: each source alone (ordinary growth, guarded rule, recompute-after-every-birth rule), the engine against the
             archived implementation, and the sources whose recorded tick lies outside the horizon;
    stage 2: with shortfall 0 each source inside each joint start ticks as it does alone (run only after the construction
             addendum has been hashed).

Run from the repository root:
    timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> 1
    timeout 600 prlimit --as=12884901888 .venv/bin/python -B <this file> 2
"""
from collections import Counter
import json
import sys
import time

import engine
import lib

ART = lib.ARTIFACTS
RECEIPT = (lib.ROOT / "artifacts/TICK-BIRTHS-AND-SCARCITY-20261121-001B/"
           "TICK-BIRTHS-AND-SCARCITY-20261121-001B-E001_serial/receipt.json")
# Recorded first tick of each other source (parent step) and where it is recorded.
OTHER_TICKS = {
    "seven_knot": {"first_tick_step": 15, "record": "research/GENERATORS-20261120-001/source.md (k=1 release at size 16)"},
    "nine_knot": {"first_tick_step": 17, "record": "research/READS-HOLDERS-SOURCES-20261120-001C/results.md (launches at ages 17 and 25)"},
    "clock_21_knot_16": {"first_tick_step": 31, "record": "research/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001/decision.md (sends at 31, 47, 63; periods 16 and 24)"},
    "clock_21_knot_24": {"first_tick_step": 47, "record": "same record"},
}


def ordinary_counts(stars, steps, cap):
    P = engine.Pres.from_stars(stars)
    total, rows = 0, []
    for step in range(1, steps + 1):
        status, parents, fresh, sc = engine.ordinary_layer(P)
        if status != "extend":
            rows.append({"step": step, "status": status, "shortages": [list(map(int, x)) for x in sc]})
            break
        total += len(parents)
        rows.append({"step": step, "births": len(parents), "cumulative": total})
        if total > cap:
            break
        engine.apply_layer(P, parents, fresh)
    return rows


def other_sources():
    phys = lib.recorded().physical
    clocks = lib.load("fc_clocks", "experiments/FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B/"
                      "FREEDOM-CLOCKS-AND-BIRTHS-20261120-001B-E001_clocks/clocks.py")
    meetings = [(0, 1), (0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6)]
    seven = phys.source_from(meetings, [3, 0, 3, 3, 3, 2, 2])
    _, twentyone, _ = clocks.physical_frame(4)
    cert = json.load(open(lib.ROOT / "artifacts/READS-HOLDERS-SOURCES-20261120-001C/READS-HOLDERS-SOURCES-20261120-001C-E001_repeated_release/certificates.json"))
    nine = tuple(tuple(h) for h in cert["proved_draws"][0]["holders"])
    out = {}
    for name, stars, recorded_keys in (("seven_knot", seven, ["seven_knot"]), ("nine_knot", nine, ["nine_knot"]),
                                      ("clock_21_knot", twentyone, ["clock_21_knot_16", "clock_21_knot_24"])):
        for law in lib.LAWS:
            phys.certify_source(stars, law)
        rows = ordinary_counts(stars, lib.CAP_STEPS, 3000)
        over = next((r["step"] for r in rows if r.get("cumulative", 0) > lib.CAP_BIRTHS), None)
        out[name] = {"knots": len(stars), "distinctions": len({d for s in stars for d in s}),
                     "lawful_under_both_laws": True, "ordinary_growth": rows,
                     "first_step_where_cumulative_births_pass_400": over,
                     "recorded_first_tick": {k: OTHER_TICKS[k] for k in recorded_keys},
                     "first_recorded_tick_inside_horizon": all(OTHER_TICKS[k]["first_tick_step"] <= lib.CAP_STEPS
                                                              for k in recorded_keys)}
    return out


def replay_recorded(stars, path, law, policy, nsource):
    """Write a found completion through the archived `facts`/`pool`/`apply`, both laws' input tests included."""
    raw = lib.recorded()
    cur = tuple(stars)
    for role, parents, fresh in path:
        _, loose, children, anc, byp, multi, unary = raw.facts(cur, nsource)
        assert tuple(parents) in raw.pool(multi, unary, policy), (role, parents)
        cur, row = raw.apply(cur, nsource, tuple(parents), law)
        assert len(row["fresh"]) == fresh
    return cur


def stage1():
    S = lib.ring_sources()
    raw = lib.recorded()
    out = {"stage": 1}
    t0 = time.time()
    # ---- the engine against the archived implementation -------------------------------------------------------------
    compared = Counter()
    for host in (None, 3, 2):
        source = raw.ordinary_roles(host, "parity")[0]
        for policy in lib.POLICIES:
            for seed in range(3):
                compared[(str(host), policy)] += lib.crosscheck(source, "parity", policy, seed, 120, nsource=8)
    for policy in lib.POLICIES:
        source = raw.ordinary_roles(None, "nae")[0]
        compared[("None", policy, "nae")] += lib.crosscheck(source, "nae", policy, 7, 60, nsource=8)
    out["engine_vs_archived"] = {" ".join(k): v for k, v in compared.items()}

    # ---- the clock alone under ordinary growth: births at the recorded cuts --------------------------------------
    receipt = json.load(open(RECEIPT))
    recorded_births = {}
    for host, key in ((None, "bare"), (3, "attachment_3"), (2, "attachment_2")):
        cuts = receipt["laws"]["parity"][key]["complete_cuts"]
        source = raw.ordinary_roles(host, "parity")[0]
        rows = ordinary_counts(source, 12, 10 ** 6)
        mine = {r["step"]: r["cumulative"] for r in rows}
        recorded_births[key] = {str(a): {"recorded": cuts[str(a)]["births"], "engine": mine[a]} for a in (5, 6, 9, 10)}
        assert all(v["recorded"] == v["engine"] for v in recorded_births[key].values()), key
    out["births_at_recorded_cuts"] = recorded_births

    # ---- ticks of the clock alone under the three rules ------------------------------------------------------------
    alone = {}
    for name in ("R0", "R5", "R9"):
        src = S[name]
        j = lib.alone_joint(src)
        row = {"future_ticks": src.future_ticks()}
        st, rec, ticks = lib.run_ordinary(j, 12, 10 ** 6, check_steps=12)
        row["ordinary"] = {"ticks_made_at_step": {str(a): ticks[(0, a)] for (i, a) in ticks},
                           "expected_step": {str(a): a - src.depth for a in src.future_ticks()},
                           "births_per_step": [r["births"] for r in rec], "archived_turn_agrees_all_steps": True}
        assert {a: ticks[(0, a)] for (i, a) in ticks} == {a: a - src.depth for a in src.future_ticks()}
        gst, grec = lib.run_guarded(j)
        row["guarded"] = {"tick_birth_number": {str(a): v["birth"] for (i, a), v in grec["ticks"].items()},
                          "cap": grec["cap"], "stall": grec["stall"]}
        row["recompute"] = {}
        for policy in lib.POLICIES:
            cell = {}
            for n, age in enumerate(src.future_ticks()):
                status, path, states = lib.find_completion(lib.State(j), 0, age, policy, 20000)
                cell[str(age)] = {"status": status, "states_searched": states}
                if status == "made":
                    cell[str(age)]["births"] = len(path)
                    for law in lib.LAWS:
                        cur = replay_recorded(src.stars, path, law, policy, 8 if name == "R0" else 8)
                        target_ok = raw.realizations(cur, 8, src.ticks[age], src.roles, src.needed(age)) != []
                        assert target_ok
                    cell[str(age)]["replayed_through_archived_apply_both_laws"] = True
                    cell[str(age)]["path"] = [(int(r), list(map(int, k)), int(f)) for r, k, f in path]
            row["recompute"][policy] = cell
        alone[name] = row
    out["clock_alone"] = alone
    out["other_sources"] = other_sources()
    out["seconds"] = round(time.time() - t0, 1)
    ART.mkdir(parents=True, exist_ok=True)
    (ART / "gate1.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out


def stage2():
    sha_line = (ART / "construction_addendum.sha256").read_text().splitlines()[0].split()[0]
    assert sha_line == lib.file_sha256(lib.HERE / "construction_addendum.md"), "addendum changed after hashing"
    S = lib.ring_sources()
    from addendum import SPECS
    out = {"stage": 2, "addendum_sha256": sha_line, "starts": {}}
    for name, label, xk, yk, needs_repair in SPECS:
        X, Y = S[xk], S[yk]
        repair = {}
        if needs_repair:
            unfunded = lib.merge(name, X, Y, 0)
            _, _, _, sc = engine.ordinary_layer(engine.Pres.from_stars(unfunded.stars))
            repair = {int(k): int(n) for k, n in sc}
        j = lib.merge(name, X, Y, 0, repair)
        row = {"class": label}
        last = max(a - s.depth for s in j.srcs for a in s.future_ticks())
        t0 = time.time()
        st, rec, ticks = lib.run_ordinary(j, last, 100000)
        row["ordinary"] = {"steps_run": [r for r in rec], "ticks_made_at_joint_step":
                           {f"{('X', 'Y')[i]} tick {a}": v for (i, a), v in ticks.items()},
                           "expected_joint_step": {f"{('X', 'Y')[i]} tick {a}": a - j.srcs[i].depth
                                                   for i, s in enumerate(j.srcs) for a in s.future_ticks()},
                           "seconds": round(time.time() - t0, 1)}
        reached = set(ticks)
        expected = {(i, a): a - j.srcs[i].depth for i, s in enumerate(j.srcs) for a in s.future_ticks()}
        row["ordinary"]["every_recorded_role_realized_at_its_step"] = {}
        steps_done = len([r for r in rec if r.get("births")])
        for i, s in enumerate(j.srcs):
            maps = j.maps[i]
            by_par = {}
            for k in range(len(st.P)):
                if k >= len(j.stars):
                    by_par.setdefault(st.P.par[k], []).append(k)
            used = set()
            realized = dict(maps)
            checked = realized_n = 0
            fresh_cmp = Counter()
            for r in sorted(s.roles):
                if r < len(s.stars) or s.levels[r] - s.depth > steps_done:
                    continue
                checked += 1
                ps = s.roles[r][0]
                key = tuple(sorted(realized[p] for p in ps)) if all(p in realized for p in ps) else None
                cand = [k for k in by_par.get(key, []) if k not in used] if key is not None else []
                if cand:
                    realized[r] = cand[0]
                    used.add(cand[0])
                    realized_n += 1
                    jf, af = st.P.fresh[cand[0]], s.roles[r][1]
                    fresh_cmp["equal" if jf == af else "joint_more" if jf > af else "joint_fewer"] += 1
            row["ordinary"]["every_recorded_role_realized_at_its_step"][("X", "Y")[i]] = {
                "roles_checked": checked, "roles_realized": realized_n, "all_realized": checked == realized_n,
                "fresh_count_joint_vs_alone": dict(fresh_cmp)}
        row["ordinary"]["gate_ok"] = all(ticks.get(k) == v for k, v in expected.items() if v <= len(rec)) and all(
            v["all_realized"] for v in row["ordinary"]["every_recorded_role_realized_at_its_step"].values())
        row["ordinary"]["ticks_not_reached_by_the_gate"] = [f"{('X', 'Y')[i]} tick {a}" for (i, a), v in expected.items()
                                                            if v > len(rec)]
        # guarded rule
        gst, grec = lib.run_guarded(j)
        row["guarded"] = {"ticks": {f"{('X', 'Y')[i]} tick {a}": v for (i, a), v in grec["ticks"].items()},
                          "births": grec["births"], "cap": grec["cap"], "stall": grec["stall"],
                          "steps_completed": len(grec["steps"])}
        # recompute rule at shortfall 0: no contested birth, then the classification of every tick
        for policy in lib.POLICIES:
            leaves, nodes = lib.contest_leaves(j, policy)
            assert len(leaves) == 1 and next(iter(leaves.values()))[1] == 1
            leaf = next(iter(leaves.values()))[0]
            cls, written = lib.classify_leaf(leaf, policy)
            row.setdefault("recompute", {})[policy] = {"contested_births": len(leaf.P.log), "classification": [
                {str(a): {k: v for k, v in e.items() if k in ("status", "how", "search", "search_states", "tick_age")}
                 for a, e in c.items()} for c in cls]}
        # engine against the archived implementation on this start
        row["engine_vs_archived_states"] = {policy: lib.crosscheck(j.stars, "parity", policy, 11, 80)
                                            for policy in lib.POLICIES}
        out["starts"][name] = row
    ok = all(r["ordinary"]["gate_ok"] for r in out["starts"].values())
    out["gate2_ok_for_every_start"] = ok
    (ART / "gate2.json").write_text(json.dumps(out, indent=1, sort_keys=True) + "\n")
    return out


if __name__ == "__main__":
    which = sys.argv[1]
    result = stage1() if which == "1" else stage2()
    print(json.dumps(result, sort_keys=True)[:6000])
