"""Bounded compact growth and a literal-holdings witness replay."""

from collections import Counter
from contextlib import contextmanager
from pathlib import Path
import sys

from pysat.solvers import Cadical195


ROOT = Path(__file__).resolve().parents[3]
NAE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae"
ORDINARY = ROOT / "experiments/ORDINARY-DYNAMICS-20261120-001A/ORDINARY-DYNAMICS-20261120-001A-E001_ordinary"
sys.path[:0] = [str(NAE), str(ORDINARY)]
import end_operator as ordinary
import naelib as literal

HORIZON = 5
ROUND_BIRTH_LIMIT = 192
LOOKAHEAD_GROUP_LIMIT = 1024
WITNESS_PAIR_LIMIT = 32768
_proposals = ordinary._proposals


class GrowthCapacity(Exception):
    pass


def guard_witness_pairs(blocks):
    pairs = sum(len(row) * (len(row) - 1) // 2 for row in blocks)
    if pairs > WITNESS_PAIR_LIMIT:
        raise GrowthCapacity("witness_pair_cap")


def capped_proposals(end, cap):
    guard_witness_pairs(end.blocks)
    if cap is not None:
        return _proposals(end, cap)
    try:
        return _proposals(end, LOOKAHEAD_GROUP_LIMIT)
    except ordinary._Cap as error:
        raise GrowthCapacity("lookahead_cap") from error


@contextmanager
def bounded_operator():
    # The published step already accepts a birth cap. Its one unbounded internal
    # call is the following round's demand calculation. The wrapper imposes a
    # cap there before adopting any result and keeps exact calculations below it.
    previous = ordinary._proposals
    ordinary._proposals = capped_proposals
    try:
        yield
    finally:
        ordinary._proposals = previous


def observation(parent_counts, fresh):
    shape = Counter(zip(parent_counts, fresh, strict=True))
    return {"births": len(fresh), "loose": sum(fresh), "live": sum(n > 0 for n in fresh),
            "arity_and_fresh": [[p, f, k] for (p, f), k in sorted(shape.items())]}


def compact_growth(stars, law, horizon=HORIZON):
    end = ordinary.from_stars(stars)
    rows = []
    with bounded_operator():
        for _ in range(horizon):
            if not end.opens:
                break
            try:
                turn = ordinary.step(end, law, max_births=ROUND_BIRTH_LIMIT)
            except GrowthCapacity as error:
                return {"rounds": rows, "stop": str(error), "stop_round": len(rows) + 1}
            if turn.status != "extend":
                return {"rounds": rows, "stop": turn.status, "stop_round": len(rows) + 1,
                        "shortages": [list(row) for row in turn.shortages],
                        "planned_births_lower": turn.planned_births_lower}
            rows.append(observation(tuple(map(len, turn.parents)), turn.fresh))
            end = turn.end
    halt = "horizon" if end.opens else "closed"
    return {"rounds": rows, "stop": halt,
            "stop_round": None if halt == "horizon" else len(rows)}


def sign(value):
    return (value > 0) - (value < 0)


def late_signature(growth):
    rounds = growth["rounds"]
    if len(rounds) != HORIZON or growth["stop"] != "horizon":
        return None
    b = [row["births"] for row in rounds]
    parents = {p for row in rounds[2:] for p, _, _ in row["arity_and_fresh"]}
    return (sign(b[2] - b[1]), sign(b[3] - b[2]), sign(b[4] - b[3]),
            1 in parents, any(p >= 3 for p in parents))


def is_whole_closure_relay(growth, law):
    # In one connected presentation the compact parity closing case is a
    # single birth. Until that birth, these two laws have the same holdings.
    return law == "nae" and any(row["births"] == 1 for row in growth["rounds"])


def early_bin(growth):
    """Only the first two rounds are visible to the mutation selector."""
    rounds = growth["rounds"][:2]
    bands = {min(3, p) for row in rounds for p, _, _ in row["arity_and_fresh"]}
    if not rounds or len(rounds) < 2 or not rounds[-1]["live"]:
        state = growth["stop"]
    else:
        state = "live"
    direction = None if len(rounds) < 2 else sign(rounds[1]["births"] - rounds[0]["births"])
    return (direction, len(bands), 3 in bands, state)


def collision_read(growth, n):
    if len(growth["rounds"]) < 3:
        return None
    first, second, third = growth["rounds"][:3]
    return (n, first["births"], second["births"]), second["loose"], third["births"]


def renamed_stars(start):
    """Rebuild the witness independently with reversed founder and distinction names."""
    rows = [[] for _ in start.loose]
    at = 0
    for u, v in reversed(start.meetings):
        rows[u].append(at)
        rows[v].append(at)
        at += 1
    for k, loose in reversed(list(enumerate(start.loose))):
        rows[k].extend(range(at, at + loose))
        at += loose
    return tuple(tuple(sorted(row, reverse=True)) for row in reversed(rows))


def literal_source(stars):
    """Check both founder projections by an independent encoding and solver."""
    verdict = {}
    for law in ("parity", "nae"):
        expected = [tuple(w.bit_count() % 2 == 0 if law == "parity" else w not in (0, (1 << len(row)) - 1)
                          for w in range(1 << len(row))) for row in stars]
        with Cadical195() as solver:
            for row, table in zip(stars, expected, strict=True):
                for word, is_allowed in enumerate(table):
                    if not is_allowed:
                        solver.add_clause([(v + 1) * (-1 if word & (1 << i) else 1) for i, v in enumerate(row)])
            for row, table in zip(stars, expected, strict=True):
                for word, is_allowed in enumerate(table):
                    pins = [(v + 1) * (1 if word & (1 << i) else -1) for i, v in enumerate(row)]
                    if solver.solve(assumptions=pins) != is_allowed:
                        raise ValueError(f"literal {law} founder projection disagrees")
        verdict[law] = {"founder_word_counts": [sum(table) for table in expected],
                        "projection_queries": sum(map(len, expected))}
    return verdict


def replay(start, law, wanted_rounds):
    """Exact literal growth to the requested cut on an independent labeling."""
    stars = renamed_stars(start)
    certificate = literal_source(stars)
    presentation = literal.S.from_junctions(stars)
    base_rule = literal.S.gf2(literal.F.fewest)
    implication_calls = 0
    if law == "nae":
        def rule(presentation, info, rng):
            nonlocal implication_calls
            implication_calls += 2 * len(info)
            return literal_nae_rule(presentation, info, rng)
        literal_nae_rule = literal.nae_rule(literal.F.fewest)
    else:
        rule = base_rule
    rows = []
    for _ in range(wanted_rounds):
        old = len(presentation.bits_of)
        live = [j for j in presentation.live if presentation.loose(j)]
        counts = Counter(parent for child in live for parent in presentation.nbr[child])
        # The checked compact prefix bounds the materialized work; the literal
        # runner also refuses large live inputs rather than silently truncate.
        if len(live) > ROUND_BIRTH_LIMIT:
            raise GrowthCapacity("literal_live_cap")
        if sum(c * (c - 1) // 2 for c in counts.values()) > WITNESS_PAIR_LIMIT:
            raise GrowthCapacity("literal_witness_pair_cap")
        turn = presentation.step(rule, None)
        if turn is None or turn["new"] == 0:
            return {"rounds": rows, "status": "stall" if turn is None else "closed",
                    "founder_certificates": certificate, "nae_implication_queries": implication_calls}
        if turn["new"] > ROUND_BIRTH_LIMIT:
            raise GrowthCapacity("literal_birth_cap")
        rows.append(observation(presentation.parents[old:], presentation.fresh[old:]))
    halt = "live" if presentation.live else "closed"
    return {"rounds": rows, "status": halt, "founder_certificates": certificate,
            "nae_implication_queries": implication_calls}
