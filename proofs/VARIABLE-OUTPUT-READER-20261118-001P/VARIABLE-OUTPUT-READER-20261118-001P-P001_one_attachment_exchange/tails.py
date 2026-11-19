"""Trace all post-birth histories leading to the two live six-loose records."""

from collections import defaultdict, deque
from hashlib import sha256
import json
from pathlib import Path
import sys

PROOFS = Path(__file__).resolve().parents[2]
ORIGINAL = next((PROOFS / "VARIABLE-OUTPUT-READER-20261118-001O").glob("*/frontier.py"))
assert sha256(ORIGINAL.read_bytes()).hexdigest() == "7fad6370ce65cbd09d457189a9238a69c2e3582e0c41dd024bf344efc2e2e1ed"
sys.path.insert(0, str(ORIGINAL.parent))
import frontier as formation


def trace_targets():
    buckets, _ = formation.all_starts(formation.N.close_prefixes())
    roots = {node for layer in buckets.values() for node in layer if node[0] == 2}
    seen = set(roots)
    queue = deque(roots)
    incoming = defaultdict(set)
    while queue:
        node = queue.popleft()
        third, spending, state = node
        for group in formation.choices(state.frontier)[0]:
            if spending and state.fourth in group:
                continue
            new_spend = spending or (len(group) if state.fourth in group else 0)
            if new_spend == 2:
                continue
            new_state = formation.advance(state, group)
            successor = (third, new_spend, new_state)
            incoming[successor].add((node, group))
            if successor not in seen:
                seen.add(successor)
                queue.append(successor)

    targets = [n for n in seen if n[1] == 3 and sum(n[2].frontier.loose) == 6 and formation.menu_roles(n[2])]
    summaries = []
    for goal in targets:
        source_child = goal[2].child
        remaining = goal[2].frontier.loose[source_child] if source_child != formation.OTHER else 0
        visited = {goal}
        pending = deque([goal])
        events = set()
        while pending:
            here = pending.popleft()
            for parent, group in incoming[here]:
                events.add((parent, here, group))
                if parent not in visited:
                    visited.add(parent)
                    pending.append(parent)

        def suffixes(node, ancestors):
            assert node not in ancestors, "A cycle would allow longer suffixes."
            result = {()} if node in roots else set()
            for previous, marks in incoming[node]:
                for earlier in suffixes(previous, ancestors | {node}):
                    result.add(earlier + ((len(marks), previous[2].fourth in marks,
                                           previous[2].child in marks),))
            return result

        tails = suffixes(goal, frozenset())
        frontier = goal[2].frontier
        summaries.append({"surviving_child_outputs": remaining,
                          "predecessor_states_including_goal": len(visited),
                          "root_records_at_the_fourth_birth": len(roots & visited),
                          "tagged_moves_in_backward_graph": len(events),
                          "all_suffixes_after_fourth_birth": sorted(tails),
                          "fields_per_move": ["parent count", "uses fourth site", "uses spending child"],
                          "active_counts": frontier.loose,
                          "active_neighbor_masks": frontier.adjacent,
                          "retired_neighbor_masks": frontier.retired,
                          "fourth_index": goal[2].fourth, "child_index": source_child})
    summaries.sort(key=lambda item: -item["surviving_child_outputs"])
    assert [s["surviving_child_outputs"] for s in summaries] == [2, 1]
    assert summaries[0]["all_suffixes_after_fourth_birth"] == [((3, True, False),)]
    assert summaries[1]["all_suffixes_after_fourth_birth"] == [((3, True, False), (3, False, True))]
    return {"reachable_states_with_binary_third_and_no_binary_spend": len(seen), "live_six_loose": summaries}


if __name__ == "__main__":
    print(json.dumps(trace_targets(), indent=2))
