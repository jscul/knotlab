"""The two scope predicates, transcribed from target_inventory's criteria."""
from __future__ import annotations


class SyntaxPreparation:
    """Usual definitions and inlining counts, with no allowed-state computation."""
    def __init__(self, key):
        import json
        import inputs
        paths = inputs.load_paths()
        defs = paths.CENSUS.normalized(json.loads(key))
        self.u, _ = paths.CENSUS.LS.usual(defs)
        self.main = len(self.u) - 1
        self.holding = {i for i, (_, _, calls) in enumerate(self.u)
                        if any(c == "SELF" for c, _ in calls)}
        self.S = self.main if self.main in self.holding else self.first_holding(self.main)
        self.k = self.u[self.main][0]
        self.own = []
        for _, own, calls in self.u:
            self.own.append(own + sum(self.own[c] for c, _ in calls
                                      if c not in ("K", "SELF") and c not in self.holding))

    def flat(self, definition):
        import inputs
        return inputs.load_paths().Preparation.flat(self, definition)

    def first_holding(self, definition):
        import inputs
        return inputs.load_paths().Preparation.first_holding(self, definition)


def scope(prep):
    types = set(prep.holding)
    blocks = {i: prep.flat(i) for i in types | {prep.main}}

    def reach(start):
        pending, visited = [start], set()
        while pending:
            i = pending.pop()
            if i in visited:
                continue
            visited.add(i)
            pending.extend(c for c, _ in blocks[i]["calls"] if c != "K" and c not in visited)
        return visited

    from_S, from_main = reach(prep.S), reach(prep.main)
    others = sorted(((from_S | from_main) & types) - {prep.S})
    own = [i for i in others if blocks[i]["V"] > blocks[i]["k"]]

    def reaches_S(i, seen=None):
        seen = set() if seen is None else seen
        if i in seen:
            return False
        seen.add(i)
        return any(c == prep.S or reaches_S(c, seen)
                   for c, _ in blocks[i]["calls"] if c != "K" and c != i)

    delayed = [i for i in others if reaches_S(i)]
    return dict(in_scope=not own and not delayed, other_own_types=own, delaying_types=delayed,
                other_own_from_S=any(i in from_S for i in own),
                other_own_from_main=any(i in from_main for i in own),
                wrapper=prep.main != prep.S)


def identity_cycle(prep):
    flat = prep.flat(prep.S)
    adjacency = [set() for _ in range(3)]
    for callee, arguments in flat["calls"]:
        if callee == prep.S:
            for k, j in enumerate(arguments):
                if j < 3:
                    adjacency[j].add(k)
    def visit(j, path):
        return any(k in path or visit(k, path | {k}) for k in adjacency[j])
    return any(visit(j, {j}) for j in range(3))


def stratum(prep, R_i):
    import inputs
    if identity_cycle(prep):
        return "I", dict(identity_cycle=True, status="identity_suffices")
    info = inputs.load_ties().classify_full(R_i)
    if info.get("status") == "ok" and info["tie_cycle"]:
        return "T", info
    if info.get("status") == "ok" and not info["tie_cycle"] and info["idempotent_types"] == ["order"]:
        return "O", info
    return "X", info
