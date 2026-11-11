"""Acquire triple supports by a reversible walk, without a model of the rules.

``learn(initial)`` yields one anonymous port index. Send back the complete
assignment after the environment attempts that flip. A rejected attempt must
return the unchanged assignment; an accepted attempt must return exactly the
one-bit change. Accepted changes are assumed reversible.

The learner owns its depth-first traversal, visit memory, and support masks.
It skips a proposal when the changed assignment is already in its visit memory.
Each other proposal is a forward trial, whether accepted or rejected. Each
first-entry move is physically undone once on returning from its descendants.
Thus forward trials are at most the port count times the visited count, and
backtracks equal the visited count minus one on completion. The returned
trial count includes both kinds of attempted flip.

Masks use bit ``4 * first + 2 * second + third`` for a triple's observed word.
Trajectory masks follow ``combinations(range(port_count), 3)`` order. The first
entry records the initial observation at trial zero; each later entry records
one first visit after receiving the environment's resulting assignment.
"""

from collections.abc import Generator
from itertools import combinations


State = tuple[int, ...]
Triple = tuple[int, int, int]


def _assignment(values: State, port_count: int | None = None) -> State:
    """Validate the sensed values without inferring anything about legality."""
    if not isinstance(values, tuple):
        raise ValueError("an observation must be a tuple of bits")
    if port_count is not None and len(values) != port_count:
        raise ValueError("an observation changed the number of ports")
    if any(type(value) is not int or value not in (0, 1) for value in values):
        raise ValueError("an observation must contain only integer bits")
    return values


def learn(initial: State) -> Generator[int, State, dict]:
    """Return acquired supports when all reachable one-bit moves are exhausted.

    The result contains ``masks`` keyed by index triples, ``visited_count``,
    ``forward_trials``, ``backtracks``, ``trial_count``, ``max_stack`` (including
    the root frame), and a list ``trajectory`` of first-observation records.
    Each record has the observed ``state``, the same running count fields,
    and a tuple ``masks`` in the documented triple order. No observation or
    traversal memory is retained between separate calls.
    """
    initial = _assignment(initial)
    port_count = len(initial)
    triples: tuple[Triple, ...] = tuple(combinations(range(port_count), 3))
    masks = dict.fromkeys(triples, 0)
    visited = {initial}
    # Frames contain the current assignment, next port, and first-entry port.
    stack: list[tuple[State, int, int | None]] = [(initial, 0, None)]
    forward_trials = 0
    backtracks = 0
    max_stack = 1
    trajectory: list[dict] = []

    def observe(state: State) -> None:
        for first, second, third in triples:
            word = 4 * state[first] + 2 * state[second] + state[third]
            masks[first, second, third] |= 1 << word
        trajectory.append(
            {
                "state": state,
                "visited_count": len(visited),
                "trial_count": forward_trials + backtracks,
                "forward_trials": forward_trials,
                "backtracks": backtracks,
                "masks": tuple(masks[triple] for triple in triples),
            }
        )

    observe(initial)
    while stack:
        state, next_port, incoming_port = stack[-1]
        if next_port < port_count:
            stack[-1] = (state, next_port + 1, incoming_port)
            candidate = (
                state[:next_port]
                + (1 - state[next_port],)
                + state[next_port + 1 :]
            )
            if candidate in visited:
                continue

            forward_trials += 1
            response = _assignment((yield next_port), port_count)
            if response == state:
                continue
            if response != candidate:
                raise ValueError("a flip changed something other than its port")

            visited.add(response)
            stack.append((response, 0, next_port))
            max_stack = max(max_stack, len(stack))
            observe(response)
            continue

        stack.pop()
        if stack:
            # The caller must execute the inverse first-entry move, too.
            assert incoming_port is not None
            backtracks += 1
            response = _assignment((yield incoming_port), port_count)
            if response != stack[-1][0]:
                raise ValueError("the environment did not reverse an accepted flip")

    return {
        "masks": masks,
        "visited_count": len(visited),
        "forward_trials": forward_trials,
        "backtracks": backtracks,
        "trial_count": forward_trials + backtracks,
        "max_stack": max_stack,
        "trajectory": trajectory,
    }
