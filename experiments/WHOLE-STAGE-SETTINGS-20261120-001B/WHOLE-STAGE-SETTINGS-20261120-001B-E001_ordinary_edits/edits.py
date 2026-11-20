"""Fixed local surplus edits and an ordinary complete-round receipt."""

from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations


def from_meetings(meetings, supply):
    supports = [[] for _ in supply]
    next_bit = 0
    for a, b, multiplicity in meetings:
        shared = list(range(next_bit, next_bit + multiplicity))
        supports[a].extend(shared)
        supports[b].extend(shared)
        next_bit += multiplicity
    for support, amount in zip(supports, supply, strict=True):
        support.extend(range(next_bit, next_bit + amount))
        next_bit += amount
    return tuple(map(tuple, supports))


def holders(supports):
    result = {}
    for index, row in enumerate(supports):
        for d in row:
            result.setdefault(d, []).append(index)
    return result


def private_marks(supports):
    held = holders(supports)
    return {index: tuple(bit for bit in row if len(held[bit]) == 1)
            for index, row in enumerate(supports)}


@dataclass(frozen=True)
class Preparation:
    name: str
    mechanism: str
    base: tuple
    readers: tuple
    marks: tuple
    group: str = "built"

    @property
    def optional(self):
        first = max(holders(self.base)) + 1
        return first, first + 1

    def edited(self, settings, swap_side=None):
        out = list(self.base)
        for side, (setting, holder, mark, optional) in enumerate(zip(settings, self.readers, self.marks, self.optional, strict=True)):
            if setting:
                row = out[holder] + (optional,)
                if side == swap_side and mark in row:
                    row = tuple(optional if d == mark else mark if d == optional else d for d in row)
                out[holder] = row
        return tuple(out)


def make_preparation(name, mechanism, meetings, supply, alice, bob):
    base = from_meetings(meetings, supply)
    marks = private_marks(base)
    return Preparation(name, mechanism, base, (alice, bob), (marks[alice][0], marks[bob][0] if marks[bob] else None))


def cycle(size):
    return [(i, (i + 1) % size, 1) for i in range(size)]


def built_cases():
    yield make_preparation("S_cycle_five", "S", cycle(5), (1, 1, 2, 2, 2), 0, 1)
    yield make_preparation("S_no_written_meeting", "S", [(0, 2, 2), (1, 3, 2), (2, 3, 1), (2, 4, 1), (3, 4, 1)],
                           (1, 1, 2, 2, 3), 0, 1)
    for radius in (2, 4, 8):
        size = 4 * radius + 1
        loose = [2] * size
        loose[0] = loose[2 * radius] = 1
        yield make_preparation(f"S_cycle_{size}", "S", cycle(size), loose, 0, 2 * radius)
    yield make_preparation("C_binary", "C", [(0, 2, 2), (1, 2, 2)], (1, 1, 0), 0, 2)
    yield make_preparation("C_ternary", "C", [(0, 3, 2), (1, 3, 1), (1, 4, 1), (2, 4, 1),
                                              (2, 5, 1), (0, 5, 1), (4, 5, 1)], (1, 1, 1, 0, 0, 0), 0, 3)
    remote_pair = ((0, 1), (0, 4), (1, 4), (1, 6), (2, 3), (2, 5), (3, 4), (5, 6))
    yield make_preparation("C_binary_remote", "C", [(a, b, 2) for a, b in remote_pair], (1, 1, 0, 0, 0, 0, 0), 0, 2)
    remote = ((0, 1), (1, 2), (2, 0), (0, 3), (3, 4), (4, 5), (5, 6), (6, 7), (7, 1))
    yield make_preparation("C_ternary_remote", "C", [(a, b, 2) for a, b in remote], (1, 1, 1, 0, 0, 0, 0, 0), 0, 5)


def connections(supports):
    graph = {index: set() for index in range(len(supports))}
    for owner in holders(supports).values():
        if len(owner) == 2:
            a, b = owner
            graph[a].add(b)
            graph[b].add(a)
        else:
            assert len(owner) == 1
    return graph


def distance(graph, left, right):
    todo = deque([(left, 0)])
    seen = {left}
    while todo:
        point, n = todo.popleft()
        if point == right:
            return n
        for following in graph[point] - seen:
            seen.add(following)
            todo.append((following, n + 1))
    return None


def proposal_receipt(old, law, name_floor, engine, compact):
    plan = engine.J.S.from_junctions(old)
    plan.nbits = max(plan.nbits, name_floor)
    live = [i for i in plan.live if plan.loose(i)]
    groups = [tuple(sorted(group)) for group in plan.groups_among(live)]
    assert groups == [tuple(sorted(group)) for group in engine.J.fastlib._orig(plan, live)]
    use = Counter(parent for group in groups for parent in group)
    shortage = [(i, use[i] - len(plan.loose(i))) for i in live if use[i] > len(plan.loose(i))]
    reference = None
    try:
        reference = compact.step(compact.from_stars(old), law)
    except ValueError as error:
        if "one connected presentation" not in str(error):
            raise
    choose = engine.parity_rule if law == "parity" else engine.nae_rule
    receipt = plan.step(choose(engine.J.F.fewest), None)
    payload = {"groups": groups, "shortages": shortage, "live": live}
    if receipt is None:
        assert shortage and (reference is None or reference.status == "stall")
        return old, {**payload, "status": "stall", "births": [], "closes": False}
    if not receipt["new"]:
        assert not live and (reference is None or reference.status == "closed")
        return old, {**payload, "status": "closed", "births": [], "closes": False}
    written = tuple(map(tuple, plan.bits_of))
    before = holders(old)
    out = []
    for knot in range(len(old), len(written)):
        consumed = [d for d in written[knot] if d in before]
        by_parent = {before[d][0]: d for d in consumed}
        assert all(len(before[d]) == 1 for d in consumed) and len(by_parent) == len(consumed)
        fresh = tuple(sorted(set(written[knot]) - before.keys()))
        assert len(fresh) == plan.fresh[knot]
        out.append({"knot": knot, "parents": tuple(sorted(by_parent)), "old_inputs": tuple(sorted(by_parent.items())),
                    "fresh": fresh, "fresh_count": len(fresh), "demand": plan.demand_at_birth[knot]})
    if reference is not None:
        assert reference.status == "extend"
        assert (reference.parents, reference.fresh, reference.demand) == tuple(
            tuple(row[key] for row in out) for key in ("parents", "fresh_count", "demand"))
    assert Counter(d for row in out for _, d in row["old_inputs"]) == Counter(d for d, people in before.items() if len(people) == 1)
    return written, {**payload, "status": "extend", "births": out, "closes": not plan.live}


def responses(preparation, edited, stage, receipt):
    owners = holders(stage)
    if preparation.mechanism == "S":
        return tuple(int(len(owners[mark]) == 2) for mark in preparation.marks)
    a = preparation.marks[0]
    b = preparation.optional[1]
    alice = any(not row["fresh"] and a in dict(row["old_inputs"]).values() for row in receipt["births"])
    bob = b in holders(edited) and len(owners[b]) == 2
    return int(alice), int(bob)


def separations(preparation, edited, receipt):
    written = connections(edited)
    live = receipt["live"]
    witnesses = {holder: set() for holder in live}
    for a, b in combinations(live, 2):
        if written[a] & written[b]:
            witnesses[a].add(b)
            witnesses[b].add(a)
    alice, bob = preparation.readers
    holding_steps = distance(written, alice, bob)
    marks_both = preparation.marks[1] is not None or preparation.optional[1] in holders(edited)
    return {"written_holder_steps": holding_steps,
            "private_mark_steps": holding_steps + 1 if marks_both and holding_steps is not None else None,
            "witnessed_steps": distance(witnesses, alice, bob) if bob in live else None,
            "meets": bob in written[alice], "common_witnesses": sorted(written[alice] & written[bob]),
            "bob_is_live": bob in live,
            "common_proposed_child": any({alice, bob} <= set(group) for group in receipt["groups"])}
