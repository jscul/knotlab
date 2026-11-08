"""Where the pinwheel's dead ends come from, and what growth needs (GROWTH-LAW-20261107-001C-E001).

Uses ticket B's engine and legality tests unchanged (growth_engine.py, legality.py in GROWTH-LAW-20261107-001B-E001, bound by hash).
`grow_hooked` repeats growth_engine.grow move for move, with the same random draws, and calls a hook after each move, so that
ticket B's runs are reproduced exactly (a control) while legality is traced."""
from __future__ import annotations

import math
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
B = ROOT / "experiments/GROWTH-LAW-20261107-001B/GROWTH-LAW-20261107-001B-E001_pinwheel_grown_outward"
sys.path.insert(0, str(B))
import growth_engine as E  # noqa: E402
import legality as L  # noqa: E402


def seed_key(P):
    return (P.handed(0), P.collar(0)) if P.is_complete(0) else None


def legal_patch(P, climber):
    k = seed_key(P)
    if k is None:
        return None
    return climber.embed(list(P.tiles), k)[0]


class AtlasPatch(E.Patch):
    """the stronger law: a move must also leave every dart farther than 3 from the patch's boundary with its radius-2 code in the
    atlas (the pinwheel's radius-2 law of PINWHEEL-ATLAS-20261107-001A), besides the collar law"""

    def try_move(self, i, key, keep=False):
        added = E.Patch.try_move(self, i, key, keep=True)
        if added == 0:
            return 0
        bad = L.atlas_check(self.tiles)[1]
        if bad or not keep:
            for _ in range(added):
                self.pop()
        return 0 if bad else added


def grow_hooked(by_h, order, rng, max_tiles, choose=None, hook=None, patch_cls=None):
    """growth_engine.grow, move for move. choose(P, i, lm, rng) picks a move among the legal ones (default: the engine's coin);
    hook(P, rec, i, lm, k) runs after each move; patch_cls replaces the collar law's Patch (AtlasPatch: the stronger law)."""
    P = (patch_cls or E.Patch)(by_h)
    C = E.MoveCache(P)
    rec = {"order": order, "moves": 0, "forced": 0, "choices": 0, "options": [], "outcome": None}
    while len(P.tiles) < max_tiles:
        inc = P.incomplete()
        if not inc:
            rec["outcome"] = "closed"
            break
        if order == "forced":
            pick = None
            for i in inc:
                lm = C.get(i)
                if len(lm) <= 1:
                    pick = (i, lm)
                    break
            if pick is None:
                pick = (inc[0], C.get(inc[0]))
            i, lm = pick
        else:
            if order == "bfs":
                i = inc[0]
            elif order == "finger":
                i = inc[-1]
            elif order == "random":
                i = rng.choice(inc)
            else:
                raise ValueError(order)
            lm = C.get(i)
        if not lm:
            rec["outcome"] = "dead end"
            rec["dead_tile"] = i
            break
        rec["moves"] += 1
        if len(lm) == 1:
            rec["forced"] += 1
        else:
            rec["choices"] += 1
            rec["options"].append(len(lm))
        if choose is None:
            k = lm[0] if len(lm) == 1 else rng.choice(lm)
        else:
            k = choose(P, i, lm, rng)
        first = len(P.tiles)
        P.try_move(i, k, keep=True)
        C.moved(first)
        if hook is not None:
            hook(P, rec, i, lm, k)
    if rec["outcome"] is None:
        rec["outcome"] = "size reached"
    rec["tiles"] = len(P.tiles)
    return P, rec


def options_legal(P, i, lm, climber):
    """for each legal move of tile i, is the patch after it still a pinwheel patch?"""
    out = []
    for k in lm:
        added = P.try_move(i, k, keep=True)
        assert added > 0
        out.append(bool(legal_patch(P, climber)))
        for _ in range(added):
            P.pop()
    return out


class _Stop(Exception):
    pass


def trace_run(by_h, order, seed, max_tiles, climber):
    """replay a coin run of ticket B, testing legality after every move. At the first move that leaves the pinwheel's patches,
    replay again with the same coins and, just before that move, test every option it had."""
    first_bad = {}

    def hook(P, rec, i, lm, k):
        if "move" not in first_bad and legal_patch(P, climber) is False:
            first_bad.update(move=rec["moves"], tile=i, tiles=len(P.tiles), options=len(lm), forced=len(lm) == 1)
    P, rec = grow_hooked(by_h, order, random.Random(seed), max_tiles, hook=hook)
    out = {"order": order, "seed": seed, "outcome": rec["outcome"], "tiles": rec["tiles"], "moves": rec["moves"],
           "forced": rec["forced"], "choices": rec["choices"]}
    if "move" not in first_bad:
        return out
    m = first_bad["move"]
    out.update({f"first_illegal_{k}": v for k, v in first_bad.items()})
    out["moves_from_first_illegal_to_end"] = rec["moves"] - m
    if "dead_tile" in rec:
        out["distance_to_dead_tile"] = E.tile_distance(P, first_bad["tile"]).get(rec["dead_tile"])
    seen = {"moves": 0}

    def choose(P2, i2, lm2, rng2):
        seen["moves"] += 1
        if seen["moves"] == m:
            out["first_illegal_option_legality"] = options_legal(P2, i2, lm2, climber)
            raise _Stop
        return lm2[0] if len(lm2) == 1 else rng2.choice(lm2)
    try:
        grow_hooked(by_h, order, random.Random(seed), max_tiles, choose=choose)
    except _Stop:
        pass
    return out


def oracle_run(by_h, order, seed, max_tiles, climber):
    """grow choosing, at each choice, a uniformly random option that keeps the patch a pinwheel patch"""
    log = []

    def choose(P, i, lm, rng):
        if len(lm) == 1:              # a forced move keeps a pinwheel patch one (the genuine continuation is legal)
            return lm[0]
        legal = options_legal(P, i, lm, climber)
        good = [k for k, ok in zip(lm, legal) if ok]
        log.append((len(P.tiles), len(lm), len(good)))
        assert good, "a legal patch with no legal continuation"
        return rng.choice(good)

    P, rec = grow_hooked(by_h, order, random.Random(seed), max_tiles, choose=choose)
    bits_all = sum(math.log2(a) for _, a, _ in log)
    bits_legal = sum(math.log2(g) for _, _, g in log)
    final_legal = legal_patch(P, climber)
    return {"order": order, "seed": seed, "outcome": rec["outcome"], "tiles": rec["tiles"], "moves": rec["moves"],
            "forced": rec["forced"], "choices": rec["choices"], "final_legal": final_legal,
            "choices_log": log, "bits_all_options": round(bits_all, 3), "bits_legal_options": round(bits_legal, 3)}


def strong_run(by_h, order, seed, max_tiles, climber):
    """coin growth under the stronger law (collar law plus the radius-2 atlas)"""
    P, rec = grow_hooked(by_h, order, random.Random(seed), max_tiles, patch_cls=AtlasPatch)
    final_legal = legal_patch(P, climber)
    return {"order": order, "seed": seed, "outcome": rec["outcome"], "tiles": rec["tiles"], "moves": rec["moves"],
            "forced": rec["forced"], "choices": rec["choices"], "final_legal": final_legal,
            "atlas_bad": L.atlas_check(list(P.tiles))[1]}


def strong_replay(by_h, max_tiles):
    """the control: under the stronger law, growth that follows a genuine pinwheel patch (T_6) is never rejected"""
    G = E.Genuine(6)
    rejected = []

    def follow(P, i, lm, rng):
        k = G.replay(P, i)
        if k not in lm:
            rejected.append(len(P.tiles))
            raise _Stop
        return k
    try:
        P, rec = grow_hooked(by_h, "bfs", random.Random(0), max_tiles, choose=follow, patch_cls=AtlasPatch)
        return {"order": "bfs", "seed": 0, "outcome": rec["outcome"], "tiles": rec["tiles"], "moves": rec["moves"],
                "forced": rec["forced"], "choices": rec["choices"], "rejected": False}
    except _Stop:
        return {"order": "bfs", "seed": 0, "outcome": "replay rejected", "tiles": rejected[0], "rejected": True}
