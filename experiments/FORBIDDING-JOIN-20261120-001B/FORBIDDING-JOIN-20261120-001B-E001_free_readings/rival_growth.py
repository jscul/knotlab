"""Recompute ordinary proposals on the current stage before applying a cutoff."""

from collections import Counter


ARMS = ("ordinary", "one_fewer", "arity_floor")


def live_and_groups(model, engine):
    live = [k for k in model.live if model.loose(k)]
    groups = model.groups_among(live)
    assert groups == engine.J.fastlib._orig(model, live)
    demand = Counter(parent for group in groups for parent in group)
    shortages = {k: demand[k] - len(model.loose(k)) for k in live if demand[k] > len(model.loose(k))}
    return live, groups, shortages


def next_funding(supports, engine):
    model = engine.J.S.from_junctions(supports)
    live, groups, shortages = live_and_groups(model, engine)
    status = "closed" if not live else "stalled" if shortages else "ready"
    return {"status": status, "live": live, "groups": [sorted(group) for group in groups], "shortages": shortages}


def cut(arm, p, q):
    floor = max(0, 3 - p)
    if arm == "ordinary":
        return q
    if arm == "one_fewer":
        return min(q, max(floor, q - 1))
    assert arm == "arity_floor"
    return min(q, floor)


def grow(old, law, arm, engine, allocation="first"):
    """The ordinary engine builds the scratch roster and supplies the actual implication flags."""
    proposal = engine.J.S.from_junctions(old)
    live, groups, shortages = live_and_groups(proposal, engine)
    if not live:
        return None, {"status": "closed"}
    if shortages:
        assert proposal.step(engine.J.F.fewest, None) is None
        return None, {"status": "stalled", "shortages": shortages}

    planned = {}

    def remember(model, info, rng):
        count = engine.J.F.fewest(model, info, rng)
        planned.update((row["j"], (row.copy(), q)) for row, q in zip(info, count, strict=True))
        return count

    rule = engine.parity_rule(remember) if law == "parity" else engine.nae_rule(remember)
    grown = proposal.step(rule, None)
    assert grown["new"] == len(planned) > 0
    old_size = len(old)
    newborn = []
    records = []
    paid = Counter()
    parent_sets = Counter()
    old_names = set(d for support in old for d in support)
    for knot in range(old_size, len(proposal.bits_of)):
        info, q = planned[knot]
        consumed = tuple(sorted(bit for bit in proposal.bits_of[knot] if bit in old_names))
        available = tuple(sorted(bit for bit in proposal.bits_of[knot] if bit not in old_names))
        p = len(consumed)
        demand = info["d"]
        assert p == info["p"] and len(available) == q and demand == proposal.demand_at_birth[knot]
        f = cut(arm, p, q)
        fresh = available[:f] if allocation == "first" else available[q - f:]
        parents = tuple(sorted(next(owner for owner in proposal.owner[bit] if owner < old_size) for bit in consumed))
        assert len(set(parents)) == p and len(fresh) == f
        paid.update(consumed)
        parent_sets[parents] += 1
        newborn.append(consumed + fresh)
        records.append({"knot": knot, "parents": parents, "inputs": consumed, "p": p, "D": demand, "q": q, "f": f,
                        "old_inputs_already_imply_law": info["implied"], "ordinary_fresh": available, "fresh": fresh})

    before = engine.J.S.from_junctions(old)
    loose = {k: before.loose(k) for k in live}
    group_uses = Counter(parent for group in groups for parent in group)
    assert paid == Counter(bit for row in loose.values() for bit in row)
    reference = Counter(tuple(sorted(group)) for group in groups)
    reference.update((k,) for k, row in loose.items() for _ in range(len(row) - group_uses[k]))
    assert parent_sets == reference
    stage = old + tuple(newborn)
    owners = Counter(bit for support in stage for bit in support)
    assert all(amount in (1, 2) for amount in owners.values())
    return stage, {"status": "funded", "births": records, "following_funding": next_funding(stage, engine)}
