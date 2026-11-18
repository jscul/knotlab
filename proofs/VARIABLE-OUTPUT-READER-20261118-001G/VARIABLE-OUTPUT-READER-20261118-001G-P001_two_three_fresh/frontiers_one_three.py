"""Check four loose distinctions with exactly one three-fresh addition."""

from __future__ import annotations

import argparse
import json
from collections import Counter, deque
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

import frontiers as base


HERE = Path(__file__).resolve().parent
PREDECESSORS = {
    "frontiers.py": "9680bf28e091af0aab224ed086d00c1fd6c80170e9f318ed8f66e652e9e01081",
    "frontiers.json": "eff3a9d66167b7fed4c6fd4ad628d8ce7442c470d0b5aa6169bb82046111ff39",
}
MAX_UNARY = MAX_TRIPLE = 2
MIN_SITES = 3


@dataclass(frozen=True, order=True)
class State:
    incidence: base.Frontier
    unary: int
    triple: int
    used_three: bool
    sites: int

    def record(self):
        f = self.incidence
        return [self.unary, self.triple, int(self.used_three), self.sites, f.loose, f.adjacent, f.retired]


def successor(state, parents, fresh_count):
    front = state.incidence
    newest = len(front.loose)
    used = base.mask(parents)
    balances = tuple(n - (p in parents) for p, n in enumerate(front.loose))
    rows = tuple(old | ((1 << newest) if (used >> p) & 1 else 0) for p, old in enumerate(front.adjacent))
    retiring = tuple(rows[p] for p, n in enumerate(balances) if n == 0)
    kept = (*tuple(p for p, n in enumerate(balances) if n), newest)
    updated = base.Frontier((*balances, fresh_count), (*rows, used), (*front.retired, *retiring))
    return State(base.canonical(updated.restrict(kept))[0], state.unary + (len(parents) == 1),
                 state.triple + (len(parents) == 3), state.used_three or fresh_count == 3,
                 min(MIN_SITES, state.sites + 1))


def literal_step(scopes, parents, fresh_count):
    checks = dict(enumerate(scopes))
    rule = base.original_rule()
    owners, _ = rule.incidence(checks)
    loose = rule.loose_ports(owners)
    old_bits = tuple(min(loose[p]) for p in parents)
    assert fresh_count in (2, 3)
    assert rule.legal_local_move(checks, old_bits, base.FRESH_FOR_PARENT_TEST)
    fresh = tuple(range(len(owners), len(owners) + fresh_count))
    assert not (set(fresh) & owners.keys())
    return (*scopes, (*old_bits, *fresh)), {"parents": parents, "consumed": old_bits, "fresh": fresh}


def run():
    for name, digest in PREDECESSORS.items():
        assert sha256((HERE / name).read_bytes()).hexdigest() == digest
    assert json.loads((HERE / "frontiers.json").read_text())["shortest_target"] is None
    seed = State(base.snapshot(base.START)[0], 0, 0, False, 1)
    queue = deque([seed])
    representatives = {seed: (base.START, ())}
    successors = {}
    budget_counts = Counter()
    stage_counts = Counter()
    seen_targets = {}
    examined, edges, revisits = 0, 0, 0
    widest = 0
    first_outside_width = None
    while queue:
        state = queue.popleft()
        scopes, path = representatives[state]
        front, names, ports = base.snapshot(scopes)
        assert front == state.incidence and min(len(scopes), MIN_SITES) == state.sites
        width = sum(front.loose)
        assert width == 3 + state.unary - state.triple + state.used_three
        widest = max(widest, width)
        if width > 6 and first_outside_width is None:
            first_outside_width = state
        budget_counts[state.unary, state.triple, state.used_three] += 1
        stage_counts[state.sites, width, state.used_three] += 1
        if width == 4 and state.used_three and state.sites == MIN_SITES:
            seen_targets.setdefault((state.unary, state.triple), state)

        moves = base.verify_literal_moves(scopes, front, names, ports)
        examined += len(moves)
        outgoing = []
        for parents in sorted(moves):
            if len(parents) == 1 and state.unary == MAX_UNARY:
                continue
            if len(parents) == 3 and state.triple == MAX_TRIPLE:
                continue
            for fresh_count in ((2,) if state.used_three else (2, 3)):
                nxt = successor(state, parents, fresh_count)
                physical, action = literal_step(scopes, tuple(names[i] for i in parents), fresh_count)
                assert base.snapshot(physical)[0] == nxt.incidence
                edges += 1
                outgoing.append((parents, fresh_count, nxt))
                if nxt in representatives:
                    revisits += 1
                else:
                    representatives[nxt] = physical, (*path, action)
                    queue.append(nxt)
        successors[state] = tuple(outgoing)

    assert successors.keys() == representatives.keys()
    assert all(nxt in successors for outgoing in successors.values() for _, _, nxt in outgoing)
    assert edges - revisits == len(successors) - 1

    def witness(state):
        scopes, path = representatives[state]
        replay = base.START
        for old in path:
            replay, checked = literal_step(replay, old["parents"], len(old["fresh"]))
            assert old == checked
        assert replay == scopes
        return {"junctions": len(scopes), "loose": sum(state.incidence.loose),
                "unary": state.unary, "three_parent": state.triple, "used_three_fresh": state.used_three,
                "appended_history": path, "scopes": scopes}

    target = min(seen_targets.values(), key=lambda state: len(representatives[state][0]), default=None)
    order = sorted(successors)
    identifiers = {state: i for i, state in enumerate(order)}
    fixed_point = [[state.record(), [(parents, count, identifiers[nxt])
                                    for parents, count, nxt in successors[state]]] for state in order]
    initial_one_three, _ = literal_step(base.START, (0,), 3)
    assert sum(base.snapshot(initial_one_three)[0].loose) == 5
    return {
        "predecessors": PREDECESSORS,
        "caps": {"unary": MAX_UNARY, "three_parent": MAX_TRIPLE, "three_fresh_additions": 1,
                 "sites_saturated_at": MIN_SITES},
        "target": {"loose": 4, "three_fresh_additions": 1, "minimum_junctions": MIN_SITES},
        "possible_target_budgets": [[t, t] for t in range(MAX_TRIPLE + 1)],
        "reachable_states": len(successors),
        "parent_actions_checked_before_caps": examined,
        "verified_transitions": edges,
        "transitions_reaching_previous_state": revisits,
        "maximum_loose_count": widest,
        "first_loose_count_above_six": witness(first_outside_width) if first_outside_width else None,
        "by_budgets_unary_triple_three_fresh": [[u, t, int(s), k] for (u, t, s), k in sorted(budget_counts.items())],
        "by_saturated_site_count_loose_and_three_fresh": [
            [sites, loose, int(s), n] for (sites, loose, s), n in sorted(stage_counts.items())
        ],
        "shortest_target": witness(target) if target else None,
        "target_witness_by_unary_and_triple_budgets": [
            [u, t, witness(state)] for (u, t), state in sorted(seen_targets.items())
        ],
        "positive_three_fresh_control": {"first_unary_produces_five_loose": True},
        "fixed_point_sha256": sha256(json.dumps(fixed_point, separators=(",", ":")).encode()).hexdigest(),
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write", action="store_true", help="Write frontiers_one_three.json")
    args = parser.parse_args()
    content = json.dumps(run(), indent=2, sort_keys=True) + "\n"
    path = HERE / "frontiers_one_three.json"
    if args.write:
        path.write_text(content)
    else:
        assert path.read_text() == content
        print("One-three-fresh frontier closure reproduced.")
