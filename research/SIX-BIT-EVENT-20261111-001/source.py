"""Run a six-bit source, six-bit witness and two-bit reader with no supplied input schedule."""

import argparse
import json
from collections import defaultdict, deque
from itertools import product
from pathlib import Path

from polarity import MIXED, PORTS, REST, STATES, TRIPLES, WORDS, steps


def flip(word, index):
    return word[:index] + ("1" if word[index] == "0" else "0") + word[index + 1:]


def source_states(rules):
    return {"".join(bits) for bits in product("01", repeat=6)
            if all(len({bits[PORTS.index(p)] for p in rule}) == 2 for rule in rules)}


def whole_system(rules):
    source = source_states(rules)
    memory_moves = {(s, w): steps(s, w, "one") for s in STATES for w in WORDS}
    graph = {}
    for world, core, pair in product(sorted(source), STATES, ("00", "01", "10", "11")):
        if len(set(core[4] + pair)) == 1:
            continue
        current = (world, core, pair)
        moves = []
        for i in range(6):
            new = flip(world, i)
            moves.append((new, core, pair) if new in source else current)
        for new in memory_moves[core, world[3:]]:
            moves.append((world, new, pair) if len(set(new[4] + pair)) == 2 else current)
        for i in range(2):
            new = flip(pair, i)
            moves.append((world, core, new) if len(set(core[4] + new)) == 2 else current)
        graph[current] = tuple(moves)
    starts = {node for node in graph if node[1] in REST and node[1][4] == "0"}
    return graph, starts


def reachable(starts, graph):
    seen = set(starts)
    pending = list(starts)
    while pending:
        for nxt in graph.get(pending.pop(), ()):
            if nxt not in seen:
                seen.add(nxt)
                pending.append(nxt)
    return seen


def matched_trace(graph, event):
    start = ("001001", "001101", "01")
    other = ("111" if event == "000" else "000")
    initial = (start, False)
    previous = {initial: None}
    pending = deque([initial])
    while pending:
        here = pending.popleft()
        (world, core, pair), seen = here
        if seen and world == start[0] and core[4] == "1" and pair == start[2]:
            path = []
            cursor = here
            while previous[cursor] is not None:
                before, port = previous[cursor]
                path.append({"proposal_index": port, "after": cursor[0]})
                cursor = before
            path.reverse()
            return {"start": start, "moves": path, "common_probe_from": here[0],
                    "probe_after_proposing_q": graph[here[0]][13],
                    "same_probe_from_clear_start": graph[start][13]}
        for port, node in enumerate(graph[here[0]]):
            raw = node[0][3:]
            candidate = (node, seen or raw == event)
            if raw != other and candidate not in previous:
                previous[candidate] = (here, port)
                pending.append(candidate)
    return None


def analyze(rules, include_traces):
    graph, starts = whole_system(rules)
    seen = reachable(starts, graph)
    backward = defaultdict(set)
    for current in seen:
        for nxt in graph[current]:
            backward[nxt].add(current)
    events = {s[0][3:] for s in seen} - set(MIXED)
    targets = {
        "stored_bit_is_one": {s for s in seen if s[1][4] == "1"},
        "upper_pair_is_00": {s for s in seen if s[2] == "00"},
    }
    hitting = {}
    for name, target in targets.items():
        can_reach = reachable(target, backward)
        hitting[name] = {
            "reachable_target_states": len(target),
            "reachable_states_without_a_path_to_target": len(seen - can_reach),
            "hit_with_probability_one_from_all_starts": bool(target) and can_reach == seen,
        }
    return {
        "source_states": len(source_states(rules)), "initial_states": len(starts),
        "reachable_joint_states": len(seen), "equal_words_reachable": sorted(events),
        "upper_pairs_reachable": sorted({s[2] for s in seen}), "hitting": hitting,
        "written_can_fall_back_to_zero": any(
            s[1][4] == "1" and t[1][4] == "0" for s in seen for t in graph[s]
        ),
        "matched_source_traces": {w: matched_trace(graph, w) for w in sorted(events)} if include_traces else {},
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    result = {
        "proposal_order": [*(f"source.{c}" for c in PORTS), *(f"memory.{c}" for c in PORTS),
                           "reader.p", "reader.q"],
        "source_and_witness_coupling": "The source evolves freely. Its xyz drive the three witness couplings. The reader NAE(y,p,q) stays attached and can veto a change. All 14 proposals are equiprobable.",
        "original_source": analyze(TRIPLES, False),
        "source_without_abc": analyze(TRIPLES[1:], True),
    }
    encoded = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        with args.output.open("x", encoding="utf-8") as handle:
            handle.write(encoded)
    else:
        print(encoded, end="")
