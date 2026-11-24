"""Self-checks of the birth-by-birth engine and determinism checks (called from selfcheck.py)."""

import json
import os

import birth_by_birth as bb
import growth as g


def _state(b):
    parts = sorted(sorted(P.members) for P in b.parts.values())
    shorts = sorted(u for P in b.parts.values() for u in P.short)
    moves = sorted(b.reg_all.items)
    opn = sorted(sorted(G) for P in b.parts.values() for G in P.open)
    return {"metc": sorted((x, sorted(M)) for x, M in b.metc.items()), "parts": parts, "short": shorts,
            "moves": moves, "open": opn, "move_gens": sorted(b.move_gen_count.items()),
            "short_gens": sorted(b.short_gen_count.items())}


def incremental_vs_full(cases=None, seeds=(0, 1, 2), moves=120):
    if cases is None:
        cases = [(st, rule, order) for st in ["D2(4,3)", "D2(5,3)", "DW(5,3)", "Ring(5,3)", "Ring(7,3)"]
                 for rule in ["ANY", "DEAD"] for order in ["BG-UNIFORM", "UNIFORM"]]
    checked = 0
    for st, rule, order in cases:
        for seed in seeds:
            b = bb.BBB(st, rule, "RATION-3", "WAIT", order, seed=seed, run_id="selfcheck")
            for _ in range(moves):
                full = bb.BBB.recomputed(b)
                a, c = _state(b), _state(full)
                assert a == c, (st, rule, order, seed, b.moves_made, {k: (a[k], c[k]) for k in a if a[k] != c[k]})
                b.S.check()
                checked += 1
                gm = b.jam_check()
                if gm == bb.INF or b.S.nknots() > 1500:
                    break
                b.apply(b.choose(gm))
    # the ordinary present-state law (G(b)) as well
    for st in ["TWO-THREE", "LONE-FOUR"]:
        for seed in range(4):
            b = bb.BBB(st, "ANY", "PRESENT-ORD", "FIRST-COME", "UNIFORM", seed=seed, run_id="selfcheck",
                       check_start_copy=False)
            for _ in range(80):
                full = bb.BBB.recomputed(b)
                assert _state(b) == _state(full), (st, seed, b.moves_made)
                b.S.check()
                checked += 1
                gm = b.jam_check()
                if gm == bb.INF:
                    break
                b.apply(b.choose(gm))
    return {"states_compared": checked, "agree": True}


def d2_4_trace(path):
    b = bb.BBB("D2(4,3)", "DEAD", "RATION-3", "WAIT", "BG-OFFSHOOTS", seed=0, run_id="C2")
    lines = ["Birth-by-birth law on D2(4,3): DEAD, RATION-3, waiting, BY-GENERATION with offshoots first, seed 0",
             "(run identity as in C2). Knots 0-3 are the members, 4-7 the dead knots w_0..w_3 (w_i meets members",
             "i and i+1). Before every move: every member with its generation, h, open groups and whether it is",
             "short, and the moves of least generation. Printed through generation 1, that is until no move of",
             "generation 1 or less is left.", ""]
    while True:
        gm = b.jam_check()
        lines.append(f"state after {b.moves_made} moves ({b.S.nknots()} knots):")
        lines.extend(b.describe())
        if gm == bb.INF or gm > 1:
            break
        key = b.choose(gm)
        kind, P = key
        c, f = b.apply(key)
        lines.append(f"  move {b.moves_made}: {'join' if kind == 'J' else 'offshoot'} of {list(P)} "
                     f"(move generation {max(b.S.gen[u] for u in P)}) -> knot {c}, generation {b.S.gen[c]}, "
                     f"{f} fresh")
        lines.append("")
    lines.append("")
    lines.append(f"moves made by move generation: { {k: dict(v) for k, v in sorted(b.made_by_gen.items())} }")
    lines.append(f"jams recorded (generation: first record): {b.jam_first}")
    with open(path, "w") as fh:
        fh.write("\n".join(lines) + "\n")
    return {"path": path, "moves": b.moves_made, "made_by_gen": {k: dict(v) for k, v in b.made_by_gen.items()},
            "jam_first": b.jam_first}


def bbb_checks(art):
    return {"incremental_vs_full": incremental_vs_full(),
            "d2_4_trace": d2_4_trace(os.path.join(art, "d2_4_trace.txt"))}


TIMING = ("wall_s", "time_s", "run_time_s", "maxrss_mb")


def strip_timing(x):
    if isinstance(x, dict):
        return {k: strip_timing(v) for k, v in x.items() if k not in TIMING}
    if isinstance(x, list):
        return [strip_timing(v) for v in x]
    return x


def canon(x):
    return json.dumps(strip_timing(x), sort_keys=True, default=str)


def determinism_checks():
    import run_c1
    import run_c2
    out = {}
    jobs1 = [("D2(5,3)", "two", "UNIFORM", 3), ("Ring(5,3)", "three", "LEAST-TIME", 7), ("D2(4,3)", "two", "ALL-IN-TURN", 0)]
    out["C1"] = all(canon(run_c1.one(j)) == canon(run_c1.one(j)) for j in jobs1)
    # a rerun in a separate process as well (Python's str hashing differs between processes)
    import subprocess
    import sys
    code = ("import json, run_c1, run_c2, selfcheck_bbb as s; print(s.canon([run_c1.one(%r), run_c2.one(%r)]))"
            % (jobs1[0], ("Ring(5,3)", "ANY", "UNIFORM", 5)))
    here = os.path.dirname(os.path.abspath(__file__))
    outs = [subprocess.run([sys.executable, "-B", "-c", code], cwd=here, capture_output=True, text=True,
                           env=dict(os.environ, PYTHONHASHSEED=str(s))).stdout for s in (1, 2)]
    out["separate_processes_different_hash_seeds"] = outs[0] == outs[1] and len(outs[0]) > 10
    jobs2 = [("D2(5,3)", "DEAD", "BG-UNIFORM", 4), ("Ring(7,3)", "ANY", "UNIFORM", 9), ("DW(5,3)", "ANY", "BG-JOINS", 1)]
    out["C2"] = all(canon(run_c2.one(j)) == canon(run_c2.one(j)) for j in jobs2)
    a = bb.every_order()
    b = bb.every_order()
    out["C3"] = json.dumps(a, sort_keys=True) == json.dumps(b, sort_keys=True)
    out["pass"] = all(out.values())
    return out
