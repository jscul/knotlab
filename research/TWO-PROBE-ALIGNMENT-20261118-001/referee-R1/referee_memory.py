"""Referee R1 for TWO-PROBE-ALIGNMENT-20261118-001: does memory beat the obstruction?  The study's game (its check_start.py and the
predecessor it loads, imported read only, to build the physical types, observations, action orbits and their outcomes); the referee's
own solver for a rule WITH perfect recall.

  ../../../.venv/bin/python -B referee_memory.py > referee_memory.json      (from this directory)

The study's theorem is over stationary rules: one action orbit per observed table, the same on every visit.  A rule that remembers
its earlier tables and actions (names still change between decisions) knows a belief: the set of physical types consistent with what
it has seen.  The referee builds the belief game from the study's start type, every belief reachable under every action, and solves
it by the least fixed point (a belief wins when some action's every outcome is a safe second junction or a winning belief).  The
study's own outcome sets (`transitions`) give the moves; nothing else of its solver is used.  Also reported: the stationary game by
the referee's own fixed point over uniform policies is NOT recomputed (that is the study's z3 and search); only the memory game.
"""
import importlib.util
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
D = ROOT / "proofs/TWO-PROBE-ALIGNMENT-20261118-001/TWO-PROBE-ALIGNMENT-20261118-001-P001_two_live"
sys.path.insert(0, str(D))
spec = importlib.util.spec_from_file_location("study_start", D / "check_start.py")
S = importlib.util.module_from_spec(spec)
sys.modules["study_start"] = S
spec.loader.exec_module(S)


def build(rules):
    inherited = S.load_predecessor()
    game = S.PhysicalGame(inherited)
    relations = [game.rows(p) for p in game.positions]
    tables = tuple(game.source.bond_table(rows, p.width)[0] for p, rows in zip(game.positions, relations))
    cl = S.classify_observations(game, tables, rules.instrument_groups)
    orbits = S.action_roster(game, cl, rules)
    edges = S.transitions(game, cl, orbits, rules)
    return game, cl[2], orbits, edges


def solve_memory(game, obs, orbits, edges):
    """Least fixed point over beliefs (frozensets of physical types sharing one observation)."""
    start = frozenset([game.start])
    succ = {}                      # belief -> list over actions of (safe?, successor beliefs)
    todo = [start]
    while todo:
        B = todo.pop()
        if B in succ:
            continue
        o = obs[next(iter(B))]
        row = []
        for c in range(len(orbits[o])):
            out = set()
            for t in B:
                out |= edges[t][c]
            safe = not (out & {S.UNAVAILABLE, S.MISALIGNED})
            nxt = defaultdict(set)
            for t in out:
                if t >= 0:
                    nxt[obs[t]].add(t)
            beliefs = [frozenset(v) for v in nxt.values()]
            row.append((safe, beliefs))
            if safe:
                todo.extend(b for b in beliefs if b not in succ)
        succ[B] = row
    win = {}
    changed = True
    rank = 0
    while changed:
        changed = False
        rank += 1
        new = {}
        for B, row in succ.items():
            if B in win:
                continue
            for safe, beliefs in row:
                if safe and all(b in win for b in beliefs):
                    new[B] = rank
                    break
        if new:
            win.update(new)
            changed = True
    sizes = sorted(len(B) for B in succ)
    return {"reachable beliefs (under safe actions)": len(succ), "largest belief": sizes[-1] if sizes else 0,
            "beliefs of more than one type": sum(1 for s in sizes if s > 1),
            "winning beliefs": len(win), "start wins with memory": start in win,
            "worst-case actions through the commitment with memory": win.get(start)}


if __name__ == "__main__":
    controls = {
        "individually addressed (the theorem's game)": S.Rules(),
        "two created together when idle": S.Rules(create_two_from_idle=True),
        "automatic erase of either or all": S.Rules(automatic_erase=True),
        "automatic erase or replace of either or all (a positive control)": S.Rules(automatic_erase=True, automatic_replace=True),
    }
    out = {}
    for name, rules in controls.items():
        game, obs, orbits, edges = build(rules)
        out[name] = solve_memory(game, obs, orbits, edges)
        print(name, out[name], file=sys.stderr, flush=True)
    print(json.dumps(out, indent=1))
