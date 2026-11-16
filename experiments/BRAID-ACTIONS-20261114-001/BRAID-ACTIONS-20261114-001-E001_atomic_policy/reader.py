"""Learn two Boolean scan instructions for a public, variable-length packet."""

from functools import lru_cache
from itertools import product

import actions


POINTS = tuple(product(range(3), repeat=2))
ALL = (1 << 512) - 1
TRAIN = sum(1 << world for world in range(512) if world.bit_count() % 2 == 0)
ORIGINAL = tuple(sum(1 << w for w in range(512) if w & (1 << i)) for i in range(9))
PORTS = tuple(product((0, 1), range(3), (-1, 0, 1, 2)))
TRAIN_PORTS = tuple(product((0, 1), (0, 1), (-1, 0, 1)))


def index(pair):
    return 3 * pair[0] + pair[1]


def node_value(expr, bits):
    op = expr[0]
    if op == "input":
        return int(bits[expr[1]])
    if op == "const":
        return expr[1]
    left = node_value(expr[1], bits)
    if op == "NOT":
        return 1 ^ left
    right = node_value(expr[2], bits)
    return {"AND": int.__and__, "OR": int.__or__, "XOR": int.__xor__}[op](left, right)


def catalogue():
    def semantic(expr):
        return sum(node_value(expr, tuple((i >> j) & 1 for j in range(3))) << i for i in range(8))

    initial = [("input", i) for i in range(3)] + [("const", 0), ("const", 1)]
    best = {semantic(expr): (0, expr) for expr in initial}
    levels = [list(best)]
    for cost in range(1, 4):
        fresh = {}

        def offer(mask, expr):
            if mask not in best and (mask not in fresh or expr < fresh[mask]):
                fresh[mask] = expr

        for truth in levels[cost - 1]:
            offer(255 ^ truth, ("NOT", best[truth][1]))
        for left_cost in range(cost):
            for a in levels[left_cost]:
                for b in levels[cost - 1 - left_cost]:
                    left, right = sorted((best[a][1], best[b][1]))
                    for op, truth in (("AND", a & b), ("OR", a | b), ("XOR", a ^ b)):
                        offer(truth, (op, left, right))
        levels.append(list(fresh))
        best.update({truth: (cost, expr) for truth, expr in fresh.items()})
    return [{"truth_mask": truth, "gate_count": cost, "expr": expr, "initial": seed}
            for truth, (cost, expr) in sorted(best.items(), key=lambda item: item[1])
            for seed in (0, 1)]


def cycle(ports):
    return tuple(ports[i % len(ports)] for i in range(9))


def training_menus():
    menus = [cycle([port]) for port in TRAIN_PORTS]
    menus.extend(cycle([a, b]) for a in TRAIN_PORTS for b in TRAIN_PORTS if a != b)
    for i, a in enumerate(TRAIN_PORTS):
        menus.append(cycle((a, TRAIN_PORTS[(i+1) % 12], TRAIN_PORTS[(i+5) % 12])))
    return tuple(menus)


def match(port, pair):
    _, left, right = port
    return pair[0] == left and (right == -1 or pair[1] == right)


def frame_values(moves):
    """Execute the frozen bit programs on each of the nine legal points."""
    forward = tuple(tuple(actions.apply(moves["forward"], p)) for p in POINTS)
    undo = tuple(tuple(actions.apply(moves["inverse"], p)) for p in POINTS)
    return forward, undo


def reach(port, undo):
    return sum(1 << i for i, pair in enumerate(POINTS)
               if match(port, undo[i] if port[0] else pair))


def original_query(port, forward):
    return sum(1 << i for i, pair in enumerate(POINTS)
               if match(port, pair if port[0] else forward[i]))


def truth_column(mask, original_cols=ORIGINAL):
    value = 0
    for i, column in enumerate(original_cols):
        if mask & (1 << i):
            value |= column
    return value


def crossed_columns(forward, original_cols=ORIGINAL):
    cols = [0] * 9
    for i, destination in enumerate(forward):
        cols[index(destination)] |= original_cols[i]
    return cols


def scan(truth, seed, a, b):
    state = seed
    for i in range(9):
        address = state | (((a >> i) & 1) << 1) | (((b >> i) & 1) << 2)
        state = (truth >> address) & 1
    return state


def scan_columns(gate, cols, mask):
    """Same nine logical transitions on every world, bit-sliced for scoring."""
    state = ALL if gate["initial"] else 0
    bits = gate["truth_mask"]
    for i, value in enumerate(cols):
        base = 4 * ((mask >> i) & 1)
        next_state = 0
        for saved in (0, 1):
            side = state if saved else ALL ^ state
            for present in (0, 1):
                if bits & (1 << (base + 2 * present + saved)):
                    next_state |= side & (value if present else ALL ^ value)
        state = next_state
    return state


def allocation(masks, may_share):
    reps = []
    binding = []
    for requested in masks:
        slot = next((i for i, rep in enumerate(reps) if may_share(rep, requested)), None)
        if slot is None:
            slot = len(reps)
            reps.append(requested)
        binding.append(slot)
    return tuple(reps), tuple(binding)


def allocator(gate):
    @lru_cache(maxsize=None)
    def may_share(previous, new):
        return bool(scan(gate["truth_mask"], gate["initial"], previous, new))
    return may_share


def fit(moves):
    forward, undo = frame_values(moves)
    raw_menus = training_menus()
    # Exclude held-out worlds before computing any target or crossed column.
    train_cols = tuple(column & TRAIN for column in ORIGINAL)
    cols = crossed_columns(forward, train_cols)
    gold = {port: truth_column(original_query(port, forward), train_cols) for port in TRAIN_PORTS}
    masks = {port: reach(port, undo) for port in TRAIN_PORTS}
    prepared = [(tuple(masks[p] for p in menu), tuple(gold[p] for p in menu)) for menu in raw_menus]
    counts = {p: sum(menu.count(p) for menu in raw_menus) for p in TRAIN_PORTS}
    gates = catalogue()
    improvements = {"aggregate": [], "reuse": []}
    best = None
    for candidate in gates:
        scored = {mask: scan_columns(candidate, cols, mask) & TRAIN for mask in set(masks.values())}
        errors = sum(counts[p] * (scored[masks[p]] ^ gold[p]).bit_count() for p in TRAIN_PORTS)
        rank = (errors, candidate["gate_count"], candidate["expr"], candidate["initial"])
        if best is None or rank < best:
            best, aggregate, outputs = rank, candidate, scored
            improvements["aggregate"].append([errors, candidate["gate_count"]])

    distances = {(mask, actual): (predicted ^ actual).bit_count()
                 for mask, predicted in outputs.items() for actual in gold.values()}
    best = None
    nworlds = TRAIN.bit_count()
    for candidate in gates:
        allowed = allocator(candidate)
        errors = slots = 0
        for menu_masks, answers in prepared:
            reps, binding = allocation(menu_masks, allowed)
            slots += len(reps)
            errors += sum(distances[reps[i], answer] for i, answer in zip(binding, answers))
        rank = (errors, slots, candidate["gate_count"], candidate["expr"], candidate["initial"])
        if best is None or rank < best:
            best, reuse = rank, candidate
            improvements["reuse"].append([errors, slots * nworlds, candidate["gate_count"]])
    return {"aggregate": aggregate, "reuse": reuse}, {
        "candidate_gate_and_initial_choices_per_stage": len(gates), "worlds": nworlds,
        "menus": len(raw_menus), "queries": nworlds * len(raw_menus) * 9,
        "training_errors": best[0], "training_payload_bits": best[1] * nworlds,
        "score_improvements": improvements}


def public_plan(checkpoint, menu):
    _, undo = frame_values(checkpoint["moves"])
    return allocation(tuple(reach(p, undo) for p in menu), allocator(checkpoint["reader"]["reuse"]))


def cross_relation(moves, original):
    current = 0
    for i, point in enumerate(POINTS):
        if original & (1 << i):
            current |= 1 << index(actions.apply(moves["forward"], point))
    return current


def send(checkpoint, current, plan):
    reps, _ = plan
    gate = checkpoint["reader"]["aggregate"]
    return tuple(scan(gate["truth_mask"], gate["initial"], current, rep) for rep in reps)


def receive(checkpoint, public_wiring, packet, actual_port):
    """A literal receiver can reconstruct its slot using only public fields."""
    reps, binding = public_plan(checkpoint, public_wiring)
    if len(packet) != len(reps) or any(bit not in (0, 1) for bit in packet):
        raise ValueError("invalid packet for public wiring")
    return packet[binding[actual_port]]
