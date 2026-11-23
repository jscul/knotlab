"""Enumerate the forward value states separately from the physical receipt replay.

An oriented pair in each of five current knots gives the values it pays to
its two different children. A routing of physically interchangeable loose
names realizes this description. Neither labels nor a global cut number are
inputs to the archived physical return reader.
"""
from collections import Counter, deque
from itertools import product
import json

PHASES = 5
WORDS = tuple(product((0, 1), repeat=2))


def legal(law, row):
    return sum(row) % 2 == 0 if law == "parity" else min(row) != max(row)


def inputs(state, phase):
    return (state[phase][0], state[(phase + 1) % PHASES][1])


def signal(state):
    a, b = inputs(state, 0)
    return int(a != b)


def extensions(law, paid):
    return tuple(w for w in WORDS if legal(law, paid + w))


def allowed_step(law, previous, current):
    return all(legal(law, inputs(previous, i) + bank)
               for i, bank in enumerate(current))


def quiet(t):
    return ((t % 2, t % 2),) * PHASES


def quiet_certificate():
    rows = [[] for _ in range(PHASES)]
    values = []
    for left, right, multiplicity in [(0, 1, 2), (1, 2, 1), (2, 3, 1), (3, 4, 1), (4, 0, 3)]:
        for slot in range(multiplicity):
            name = len(values)
            rows[left].append(name)
            rows[right].append(name)
            values.append(int(slot == 0))
    for holder in rows:
        holder.extend(range(len(values), len(values) + 2))
        values.extend((0, 0))
    for holder in rows:
        for law in ("parity", "nae"):
            assert legal(law, tuple(values[n] for n in holder))
    for t in (0, 1):
        for law in ("parity", "nae"):
            assert allowed_step(law, quiet(t), quiet(t + 1)) and signal(quiet(t)) == 0
        overlap = set(extensions("parity", (t, t))) & set(extensions("nae", (t, t)))
        assert overlap == {(1-t, 1-t)}
    return dict(exact_rows=rows, exact_founder_word=values, live_period=2,
                shared_law_history="unique alternating live values; every recorded pair agrees")


def code(banks):
    return sum((a + 2*b) << (2*i) for i, (a, b) in enumerate(banks))


def banks(state):
    return tuple(((state >> (2*i)) & 1, (state >> (2*i + 1)) & 1)
                 for i in range(PHASES))


def quotient(law):
    # Recover all legal successors without multiplying or weighting histories.
    # A newborn's two physical marks can take any ordered legal pair, including
    # both permutations. No two newborns assign the same fresh name.
    queue = deque([0])
    seen = {0}
    options = Counter()
    target_signals = {i: signal(banks(i)) for i in range(1 << (2*PHASES))}
    while queue:
        previous = banks(queue.popleft())
        choices = [extensions(law, inputs(previous, p)) for p in range(PHASES)]
        successor_count = 0
        readings = set()
        for candidate in product(*choices):
            state = code(candidate)
            successor_count += 1
            readings.add(target_signals[state])
            if state not in seen:
                seen.add(state)
                queue.append(state)
        assert readings == {0, 1}
        options[successor_count] += 1
    return dict(reachable=len(seen), one_step_choices_histogram=dict(sorted(options.items())),
                transitions=sum(n * count for n, count in options.items()),
                states_with_both_readings_available_after_one_bank_write=len(seen),
                terminal_states=0)


def maximum_witness(law, t):
    if t == 0:
        return quiet(0)
    if law == "nae":
        return ((0, 1),) * PHASES
    stationary = (0, 0, 0, 0, 1)
    return tuple((stationary[i], stationary[(i + t - 1) % PHASES])
                 for i in range(PHASES))


def periodic_checks(law):
    # Interval indices here display a proven structural period. The other
    # replay identifies each event from physical holdings independently.
    highest = [maximum_witness(law, t) for t in range(22)]
    assert all(allowed_step(law, a, b) for a, b in zip(highest, highest[1:]))
    # Ten cuts include both the structural period and the reference parity.
    assert highest[1:11] == highest[11:21]
    receipts = []
    for age in (5, 10, 15, 20):
        pair = inputs(highest[age-1], 0)
        assert pair == (0, 1)
        receipts.append(dict(display_cut=age, quiet_paid=inputs(quiet(age-1), 0), high_paid=pair))
    return dict(period_after_first_write=5 if law=="parity" else 1,
                first_ten_positive_live_words=[code(s) for s in highest[1:11]],
                four_distinct_returns=receipts)


def read_prescribed(law, message):
    previous = quiet(0)
    recorded = []
    for age in range(1, PHASES * len(message) + 1):
        if age % PHASES == 0:
            recorded.append(signal(previous))
        next_is_return = (age + 1) % PHASES == 0
        current = []
        for i in range(PHASES):
            choices = extensions(law, inputs(previous, i))
            if next_is_return and i == 0:
                options = [w for w in choices if w[0] == 0]
            elif next_is_return and i == 1:
                target = message[(age + 1) // PHASES - 1]
                options = [w for w in choices if w[1] == target]
            else:
                options = choices
            current.append(min(options))
        previous = tuple(current)
    assert tuple(recorded) == message


def replay():
    start = quiet_certificate()
    by_law = {}
    for law in ("parity", "nae"):
        for msg in product((0, 1), repeat=6):
            read_prescribed(law, msg)
        by_law[law] = dict(quotient=quotient(law), periodic=periodic_checks(law),
                           prescribed_six_return_words=64)
    return dict(quiet_start=start, laws=by_law,
                normalization="one outcome per actual positive phase return, no odds")


if __name__ == "__main__":
    print(json.dumps(replay(), indent=2, sort_keys=True))
