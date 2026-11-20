"""Recover the oldest unfinished set of parents from the physical supports.

The reference and its names enter only the checker below. Any order of the
remaining births in one recovered set is permitted, up to loose-slot renaming.
"""
from argparse import ArgumentParser
from collections import Counter, defaultdict, deque
from dataclasses import dataclass
from math import factorial
from pathlib import Path
from random import Random
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
ORDINARY = "ORDINARY-DYNAMICS-20261120-001A"
sys.path.insert(0, str(ROOT / "experiments" / ORDINARY / (ORDINARY + "-E001_ordinary")))
from end_operator import End, step

@dataclass
class Decision:
    status: str
    remaining: Counter
    depth: int | None = None


def current_decision(stars, law):
    """Only existing knots and their immutable supports are inputs."""
    holders = defaultdict(list)
    for knot, star in enumerate(stars):
        for distinction in star:
            holders[distinction].append(knot)
    neighbors = [Counter() for _ in stars]
    loose = Counter()
    for owners in holders.values():
        if len(owners) == 1:
            loose[owners[0]] += 1
        else:
            left, right = owners
            neighbors[left][right] += 1
            neighbors[right][left] += 1
    source = {k for k, near in enumerate(neighbors) if any(n >= 2 for n in near.values())}
    if not source:
        return Decision("source unrecognized", Counter())
    if not loose:
        return Decision("closed", Counter())
    depth = dict.fromkeys(source, 0)
    todo = deque(source)
    while todo:
        knot = todo.popleft()
        for other in neighbors[knot]:
            if other not in depth:
                depth[other] = depth[knot] + 1
                todo.append(other)
    level = min(depth[k] for k in loose)
    old = [k for k in depth if depth[k] == level]
    supply = {}
    for k in old:
        # Within-source distinctions were shared before the first birth.
        # All other incoming distinctions came from the preceding level.
        incoming = sum(m for other, m in neighbors[k].items()
                       if depth[other] < level or level == 0 and other in source)
        fresh = len(stars[k]) - incoming
        if fresh:
            supply[k] = fresh
    witnesses = source if level == 0 else [k for k in depth if depth[k] == level - 1]
    blocks = [tuple(k for k in neighbors[w] if k in supply) for w in witnesses]
    plan = step(End(supply, tuple(blocks)), law)
    if plan.status != "extend":
        return Decision(plan.status, Counter(), level)
    remaining = Counter(zip(plan.parents, plan.fresh, strict=True))
    for child in depth:
        if depth[child] != level + 1:
            continue
        parents = tuple(sorted(k for k in neighbors[child] if depth[k] == level))
        entry = (parents, len(stars[child]) - len(parents))
        if remaining[entry] <= 0:
            raise ValueError("written child is inconsistent with the recovered holdings")
        remaining[entry] -= 1
    return Decision("ready", +remaining, level)


def prioritize(remaining, joins_first):
    multiple = Counter({item: n for item, n in remaining.items() if len(item[0]) > 1})
    return multiple if joins_first and multiple else remaining


def check_seven(shifted, depth_bound=4):
    name = "FRESH-DEMAND-20261120-001A"
    sys.path.insert(0, str(ROOT / "experiments" / name / (name + "-E001_orders")))
    import fixed_map as reference
    reference.MAX_SIZE = depth_bound + 1
    stars, parents, outgoing, _ = reference.literal_map(shifted, reference.pieces(shifted))
    labels = sorted(stars, key=reference.order)
    rng = Random(20261120714 + shifted)
    summary = []
    for depth in range(depth_bound):
        old = [k for k in labels if len(k) <= depth + 1]
        layer = [k for k in labels if len(k) == depth + 2]
        total = len(layer)
        scans = Counter()
        serializations = {}
        for policy in (False, True):
            joins = sum(len(parents[child]) > 1 for child in layer)
            serializations["joins first" if policy else "any"] = (factorial(joins) * factorial(total - joins)
                                                                   if policy else factorial(total))
        for mask in range((1 << total) - 1):
            written = [child for i, child in enumerate(layer) if mask >> i & 1]
            todo = [child for i, child in enumerate(layer) if not mask >> i & 1]
            physical = old + written
            rng.shuffle(physical)
            number = {k: i for i, k in enumerate(physical)}
            # One simultaneous renaming of every distinction for each prefix.
            bit_names = sorted(set().union(*(stars[k] for k in physical)))
            shuffled = bit_names.copy()
            rng.shuffle(shuffled)
            rename = dict(zip(bit_names, shuffled, strict=True))
            supports = [tuple(rename[x] for x in stars[k]) for k in physical]
            target = Counter((tuple(sorted(number[p] for p in parents[child])), len(outgoing[child]))
                             for child in todo)
            for law in ("parity", "nae"):
                decision = current_decision(supports, law)
                assert decision.status == "ready" and decision.depth == depth
                assert decision.remaining == target
                for priority in (False, True):
                    already_unary = any(len(parents[c]) == 1 for c in written)
                    pending_multi = any(len(parents[c]) > 1 for c in todo)
                    if priority and already_unary and pending_multi:
                        continue
                    choices = prioritize(decision.remaining, priority)
                    expected = [c for c in todo
                                if not priority or not pending_multi or len(parents[c]) > 1]
                    assert choices == Counter((tuple(sorted(number[p] for p in parents[c])),
                                               len(outgoing[c])) for c in expected)
                    tag = law + (" joins first" if priority else " any")
                    scans[tag + " states"] += 1
                    scans[tag + " eligible incidences"] += len(expected)
        summary.append({"current_depth": depth, "births": total,
                        "checks": dict(scans), "orders_with_fixed_slots": serializations})
    return summary


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "artifacts" / HERE.parent.name / HERE.name / "cohort.json")
    output = parser.parse_args().out
    result = {"checked_operation": "present physical supports, fresh distinctions at birth; no map passed to reader",
              "seed_for_renamings": 20261120714, "depth_bound":4,
              "W spent": check_seven(False), "W live": check_seven(True)}
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2) + "\n")
    for arm in ("W spent", "W live"):
        print(arm, [(row["births"], row["checks"]["parity any states"]) for row in result[arm]])


if __name__ == "__main__":
    main()
