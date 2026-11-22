"""Build bounded game worlds from literal ordinary-growth holdings."""

import sys
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from random import Random
from typing import Literal

from networkx import from_prufer_sequence


ROOT = Path(__file__).resolve().parents[2]
ENGINE = ROOT / "experiments/NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae"
sys.path.insert(0, str(ENGINE))
import naelib as growth  # noqa: E402


Law = Literal["parity", "nae"]
MAX_ROUNDS = 3


@dataclass(frozen=True, slots=True)
class Birth:
    """The actual payments as (parent, distinction) pairs and the fresh grants."""

    holder: int
    formation: int
    payments: tuple[tuple[int, int], ...]
    grants: tuple[int, ...]
    demand: int


@dataclass(frozen=True, slots=True)
class Stage:
    """A successful cut, with (shared distinction, other holder) links."""

    formation: int
    holdings: tuple[tuple[int, ...], ...]
    links: tuple[tuple[tuple[int, int], ...], ...]
    loose: tuple[tuple[int, ...], ...]
    born: tuple[int, ...]


@dataclass(frozen=True, slots=True)
class Attempt:
    """One growth attempt with its resulting stage index and any shortages."""

    status: Literal["born", "stall", "closed"]
    stage: int
    births: tuple[Birth, ...] = ()
    shortages: tuple[tuple[int, int], ...] = ()


@dataclass(frozen=True, slots=True)
class World:
    """The source and its replay, with private names for the game runtime."""

    seed: int
    law: Law
    source_key: str
    stages: tuple[Stage, ...]
    attempts: tuple[Attempt, ...]
    births: tuple[Birth, ...]
    stop: Literal["horizon", "stall", "closed"]


def _bill(presentation, live):
    return Counter(holder for group in presentation.groups_among(live) for holder in group)


def _tree_key(tree, loose):
    def rooted(holder, parent):
        children = sorted(rooted(child, holder) for child in tree[holder] if child != parent)
        return f"{loose[holder]}({''.join(children)})"

    return min(rooted(holder, None) for holder in tree)


def _draw_source(seed):
    rng = Random(seed)
    size = rng.randrange(3, 8)
    tree = from_prufer_sequence([rng.randrange(size) for _ in range(size - 2)])
    meetings = tuple(sorted(tuple(sorted(meeting)) for meeting in tree.edges))
    degree = [tree.degree[holder] for holder in range(size)]
    funded = bool(rng.getrandbits(1))
    loose = [max(0, 3 - d) + rng.getrandbits(1) for d in degree]
    if funded:
        # Pay the computed bill for the baseline live roster. A spent holder
        # owes zero, so this adjustment keeps that roster fixed.
        baseline = growth.J.stars_from([d + s for d, s in zip(degree, loose, strict=True)], meetings)
        live = [holder for holder, count in enumerate(loose) if count]
        bills = _bill(growth.S.from_junctions(baseline), live)
        loose = [max(count, bills[holder]) for holder, count in enumerate(loose)]
    return rng, degree, meetings, loose, _tree_key(tree, loose)


def source_key(seed: int) -> str:
    """Classify the starting holdings up to relabeling, without growing them."""
    return _draw_source(seed)[-1]


def _snapshot(presentation, born=()):
    holdings = tuple(tuple(row) for row in presentation.bits_of)
    links = [[] for _ in holdings]
    loose = [[] for _ in holdings]
    for name, owners in sorted(presentation.owner.items()):
        if len(owners) == 1:
            loose[owners[0]].append(name)
        else:
            left, right = owners
            links[left].append((name, right))
            links[right].append((name, left))
    return Stage(
        presentation.rounds, holdings, tuple(map(tuple, links)), tuple(map(tuple, loose)), born,
    )


def _read_birth(presentation, holder):
    support = presentation.bits_of[holder]
    paid = presentation.parents[holder]
    # Growth appends the new holder after each paid name's original holder.
    payments = tuple((presentation.owner[name][0], name) for name in support[:paid])
    return Birth(
        holder, presentation.round_of[holder], payments, tuple(support[paid:]),
        presentation.demand_at_birth[holder],
    )


def sample_world(seed: int, law: Law, *, rounds: int = MAX_ROUNDS) -> World:
    """Draw one source and replay up to three complete attempts of ordinary growth."""
    if law not in ("parity", "nae"):
        raise ValueError(f"unknown knot law {law!r}")
    if not isinstance(rounds, int) or not 0 <= rounds <= MAX_ROUNDS:
        raise ValueError(f"rounds must be an integer from 0 to {MAX_ROUNDS}")

    rng, degree, meetings, loose, key = _draw_source(seed)
    sizes = [d + s for d, s in zip(degree, loose, strict=True)]
    stars = growth.J.stars_from(sizes, meetings)
    names = list(range(sum(sizes) - len(meetings)))
    rng.shuffle(names)
    presentation = growth.S.from_junctions([[names[name] for name in row] for row in stars])
    rule = growth.parity_rule(growth.F.fewest) if law == "parity" else growth.nae_rule(growth.F.fewest)
    stages = [_snapshot(presentation)]
    attempts = []
    births = []
    stop = "horizon"
    for _ in range(rounds):
        before = stages[-1]
        turn = presentation.step(rule, None)
        if turn is None:
            live = [holder for holder, names in enumerate(before.loose) if names]
            bills = _bill(presentation, live)
            shortages = tuple((holder, bills[holder] - len(before.loose[holder]))
                              for holder in live if bills[holder] > len(before.loose[holder]))
            attempts.append(Attempt("stall", before.formation, shortages=shortages))
            stop = "stall"
            break
        if not turn["new"]:
            attempts.append(Attempt("closed", before.formation))
            stop = "closed"
            break

        born = tuple(range(len(before.holdings), len(presentation.bits_of)))
        cohort = tuple(_read_birth(presentation, holder) for holder in born)
        stages.append(_snapshot(presentation, born))
        attempts.append(Attempt("born", stages[-1].formation, cohort))
        births.extend(cohort)
    if stop == "horizon" and not any(stages[-1].loose):
        stop = "closed"
    return World(seed, law, key, tuple(stages), tuple(attempts), tuple(births), stop)
