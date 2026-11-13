"""Core computation for the registered addressed-pattern census.

An automaton is ``(swap, successor0, successor1)``.  A key is
``(s, swap, successor0, successor1, placements)``; placements contain indices
into :func:`words`.  Ordinary words use zero-based state indices, whereas
product words use signed, one-based state indices (negative means inverse).
All word products act right to left.  Addresses are integers with their
first letter in the most significant position.

Importing this module starts no run and writes no files.
"""

from collections import deque
from functools import lru_cache
import hashlib
import itertools
import json
import resource
import struct
import sys
import time

import numpy as np
from pysat.solvers import Solver


LEVELS = 12
CONFLICT_BUDGET = 2_000_000
HASH_SERIALIZATION = (
    "sha1; levels 1..12; each level: little-endian signed int64 level, "
    "little-endian signed int64 row count, then C-order little-endian "
    "signed int64 sorted unique rows; no other bytes"
)
_RANK = {"finitary": 0, "bounded": 1, "polynomial": 2, "exponential": 3}


def words(s):
    """Identity, single states, and lexicographically ordered state pairs."""
    s = int(s)
    if s < 1:
        raise ValueError("an automaton must have at least one state")
    return [()] + [(q,) for q in range(s)] + [
        (q, r) for q in range(s) for r in range(s)
    ]


def gamma(rng):
    """Elias-gamma draw using fair coins; return the value and bit count."""
    z = 0
    while rng.random() < 0.5:
        z += 1
    value = 1
    for _ in range(z):
        value = 2 * value + (rng.random() < 0.5)
    return value, 2 * z + 1


def _automaton(aut):
    if len(aut) != 3:
        raise ValueError("automaton must contain swap, successor0, successor1")
    sw, d0, d1 = (tuple(int(q) for q in row) for row in aut)
    s = len(sw)
    if not s or len(d0) != s or len(d1) != s:
        raise ValueError("automaton arrays must have the same positive length")
    if any(bit not in (0, 1) for bit in sw):
        raise ValueError("root permutations must be bits")
    if any(q < 0 or q >= s for q in d0 + d1):
        raise ValueError("successor state outside the automaton")
    return sw, d0, d1


def normalize_key(key):
    """Return an immutable key with sorted, deduplicated placements."""
    if len(key) != 5:
        raise ValueError("key must contain s, swap, successor0, successor1, placements")
    s = int(key[0])
    aut = _automaton(key[1:4])
    if s != len(aut[0]):
        raise ValueError("key state count disagrees with the automaton")
    word_count = 1 + s + s * s
    placements = set()
    for placement in key[4]:
        triple = tuple(sorted(int(w) for w in placement))
        if len(triple) != 3 or len(set(triple)) != 3:
            raise ValueError("each placement must have three distinct word indices")
        if triple[0] < 0 or triple[-1] >= word_count:
            raise ValueError("placement word index outside words(s)")
        placements.add(triple)
    return (s, *aut, tuple(sorted(placements)))


def key_json(key):
    """JSON-compatible normalized key, with no tuple-specific encoding."""
    s, sw, d0, d1, placements = normalize_key(key)
    return [s, list(sw), list(d0), list(d1), [list(t) for t in placements]]


def key_id(key):
    """SHA-256 of the compact, normalized JSON key."""
    raw = json.dumps(key_json(key), separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(raw.encode("ascii")).hexdigest()


@lru_cache(maxsize=32)
def _state_actions(aut, n):
    """All state actions, sharing the previous-level calculation."""
    sw, d0, d1 = aut
    s = len(sw)
    if n == 0:
        out = np.zeros((s, 1), dtype=np.int64)
    else:
        half = 1 << (n - 1)
        previous = _state_actions(aut, n - 1)
        out = np.empty((s, 2 * half), dtype=np.int64)
        for q in range(s):
            out[q, :half] = previous[d0[q]] + sw[q] * half
            out[q, half:] = previous[d1[q]] + (1 ^ sw[q]) * half
    out.flags.writeable = False
    return out


def action(aut, word, n):
    """Act on all ``2**n`` addresses; return an int64 permutation vector."""
    aut = _automaton(aut)
    n = int(n)
    if n < 0:
        raise ValueError("level must be nonnegative")
    word = tuple(int(q) for q in word)
    if any(q < 0 or q >= len(aut[0]) for q in word):
        raise ValueError("word state outside the automaton")
    out = np.arange(1 << n, dtype=np.int64)
    states = _state_actions(aut, n)
    for q in reversed(word):
        out = states[q, out]
    return np.ascontiguousarray(out, dtype=np.int64)


def level_pattern(key, n):
    """The distinct sorted address triples, in lexicographic row order."""
    s, sw, d0, d1, placements = normalize_key(key)
    n = int(n)
    if n < 0:
        raise ValueError("level must be nonnegative")
    if not placements:
        return np.empty((0, 3), dtype=np.int64)
    aut = (sw, d0, d1)
    states = _state_actions(aut, n)
    W = words(s)
    images = {}
    for w in sorted({w for triple in placements for w in triple}):
        word = W[w]
        if not word:
            images[w] = np.arange(1 << n, dtype=np.int64)
        elif len(word) == 1:
            images[w] = states[word[0]]
        else:
            images[w] = states[word[0], states[word[1]]]
    pieces = []
    for triple in placements:
        rows = np.stack([images[w] for w in triple], axis=1)
        rows.sort(axis=1)
        keep = (rows[:, 0] != rows[:, 1]) & (rows[:, 1] != rows[:, 2])
        rows = rows[keep]
        if rows.size:
            if n <= 21:
                # The packed integer order is precisely lexicographic row order.
                pieces.append((rows[:, 0] << (2 * n)) |
                              (rows[:, 1] << n) | rows[:, 2])
            else:
                pieces.append(rows)
    if not pieces:
        return np.empty((0, 3), dtype=np.int64)
    if n <= 21:
        codes = np.unique(np.concatenate(pieces))
        mask = (1 << n) - 1
        out = np.empty((len(codes), 3), dtype=np.int64)
        out[:, 0] = codes >> (2 * n)
        out[:, 1] = (codes >> n) & mask
        out[:, 2] = codes & mask
        return out
    return np.ascontiguousarray(np.unique(np.concatenate(pieces), axis=0), dtype=np.int64)


def relative_product(wi, wj):
    """Signed one-based product word for ``wj * inverse(wi)``."""
    wi = tuple(int(q) for q in wi)
    wj = tuple(int(q) for q in wj)
    if any(q < 0 for q in wi + wj):
        raise ValueError("relative_product expects ordinary zero-based words")
    return tuple(q + 1 for q in wj) + tuple(-(q + 1) for q in reversed(wi))


def product_automaton(aut, items):
    """Reachable product automaton, with its initial product at state zero.

    A signed product's section has the same number of factors.  No word
    cancellation or group-equality oracle is needed for this finite closure.
    """
    sw, d0, d1 = _automaton(aut)
    items = tuple(int(item) for item in items)
    if any(item == 0 or abs(item) > len(sw) for item in items):
        raise ValueError("product factors must be signed one-based state indices")
    states = [items]
    indices = {items: 0}
    out_sw, out_d0, out_d1 = [], [], []
    cursor = 0
    while cursor < len(states):
        product = states[cursor]
        successors = []
        root_swap = None
        for letter in (0, 1):
            current = letter
            section = [0] * len(product)
            for position in range(len(product) - 1, -1, -1):
                item = product[position]
                q = abs(item) - 1
                if item > 0:
                    successor = d1[q] if current else d0[q]
                    current ^= sw[q]
                    section[position] = successor + 1
                else:
                    current ^= sw[q]
                    successor = d1[q] if current else d0[q]
                    section[position] = -(successor + 1)
            swap = current ^ letter
            if root_swap is None:
                root_swap = swap
            elif root_swap != swap:
                raise AssertionError("a product lost binary invertibility")
            section = tuple(section)
            target = indices.get(section)
            if target is None:
                target = len(states)
                indices[section] = target
                states.append(section)
            successors.append(target)
        out_sw.append(root_swap)
        out_d0.append(successors[0])
        out_d1.append(successors[1])
        cursor += 1
    return tuple(out_sw), tuple(out_d0), tuple(out_d1)


def activity_class(aut, starts):
    """Exact maximal activity class of the given starting states.

    Identity states are those unable to reach a swap.  On the remaining
    reachable states, an SCC with more internal transitions than states
    gives exponential activity.  Otherwise the maximal number of cyclic
    SCCs on a directed path is the polynomial degree plus one.
    """
    sw, d0, d1 = _automaton(aut)
    size = len(sw)
    starts = tuple(sorted(set(int(q) for q in starts)))
    if any(q < 0 or q >= size for q in starts):
        raise ValueError("activity start outside the automaton")
    if not starts:
        return "finitary", None

    predecessors = [[] for _ in range(size)]
    for q in range(size):
        predecessors[d0[q]].append(q)
        predecessors[d1[q]].append(q)
    nontrivial = bytearray(size)
    queue = deque(q for q, bit in enumerate(sw) if bit)
    for q in queue:
        nontrivial[q] = 1
    while queue:
        q = queue.popleft()
        for p in predecessors[q]:
            if not nontrivial[p]:
                nontrivial[p] = 1
                queue.append(p)

    # Restrict to nonidentity sections reachable from the requested starts.
    reachable = bytearray(size)
    stack = [q for q in starts if nontrivial[q]]
    while stack:
        q = stack.pop()
        if reachable[q]:
            continue
        reachable[q] = 1
        if nontrivial[d0[q]] and not reachable[d0[q]]:
            stack.append(d0[q])
        if nontrivial[d1[q]] and not reachable[d1[q]]:
            stack.append(d1[q])
    nodes = [q for q in range(size) if reachable[q]]
    if not nodes:
        return "finitary", None

    # Iterative Kosaraju avoids recursion limits on long product automata.
    seen = bytearray(size)
    order = []
    for root in nodes:
        if seen[root]:
            continue
        seen[root] = 1
        dfs = [(root, 0)]
        while dfs:
            q, index = dfs[-1]
            if index == 2:
                order.append(q)
                dfs.pop()
                continue
            dfs[-1] = (q, index + 1)
            target = d0[q] if index == 0 else d1[q]
            if reachable[target] and not seen[target]:
                seen[target] = 1
                dfs.append((target, 0))

    component = [-1] * size
    component_sizes = []
    for root in reversed(order):
        if component[root] != -1:
            continue
        label = len(component_sizes)
        count = 0
        component[root] = label
        stack = [root]
        while stack:
            q = stack.pop()
            count += 1
            for p in predecessors[q]:
                if reachable[p] and component[p] == -1:
                    component[p] = label
                    stack.append(p)
        component_sizes.append(count)

    count = len(component_sizes)
    internal = [0] * count
    successors = [[] for _ in range(count)]
    indegree = [0] * count
    for q in nodes:
        source = component[q]
        for target in (d0[q], d1[q]):
            if not reachable[target]:
                continue
            destination = component[target]
            if source == destination:
                # Parallel transitions count separately in the cycle criterion.
                internal[source] += 1
            else:
                successors[source].append(destination)
                indegree[destination] += 1
    if any(edges > vertices for edges, vertices in zip(internal, component_sizes)):
        return "exponential", None
    cyclic = [int(edges >= vertices) for edges, vertices in zip(internal, component_sizes)]
    best = list(cyclic)
    queue = deque(q for q in range(count) if not indegree[q])
    while queue:
        source = queue.popleft()
        for destination in successors[source]:
            best[destination] = max(best[destination], best[source] + cyclic[destination])
            indegree[destination] -= 1
            if not indegree[destination]:
                queue.append(destination)
    cycles = max(best, default=0)
    if cycles == 0:
        return "finitary", None
    if cycles == 1:
        return "bounded", 0
    return "polynomial", cycles - 1


@lru_cache(maxsize=16_384)
def _relative_activity(aut, items):
    return activity_class(product_automaton(aut, items), (0,))


@lru_cache(maxsize=8_192)
def _letter_activity(aut, starts):
    return activity_class(aut, starts)


def _class_rank(result):
    label, degree = result
    return _RANK[label], degree if degree is not None else -1


def description_classes(key):
    """Secondary letter class and primary relative class of a description."""
    s, sw, d0, d1, placements = normalize_key(key)
    aut = (sw, d0, d1)
    W = words(s)
    used_words = {w for triple in placements for w in triple}
    starts = tuple(sorted({q for w in used_words for q in W[w]}))
    letter = _letter_activity(aut, starts)
    relative = ("finitary", None)
    products = {
        relative_product(W[wi], W[wj])
        for triple in placements for wi in triple for wj in triple if wi != wj
    }
    for items in sorted(products):
        candidate = _relative_activity(aut, items)
        if _class_rank(candidate) > _class_rank(relative):
            relative = candidate
        if relative[0] == "exponential":
            break
    return letter, relative


@lru_cache(maxsize=8_192)
def _automaton_class(aut):
    sw, d0, d1 = aut
    s = len(sw)
    best = None
    for renaming in itertools.permutations(range(s)):
        new_sw = [0] * s
        new_d0 = [0] * s
        new_d1 = [0] * s
        for old in range(s):
            new = renaming[old]
            new_sw[new] = sw[old]
            new_d0[new] = renaming[d0[old]]
            new_d1[new] = renaming[d1[old]]
        for first, second in ((new_d0, new_d1), (new_d1, new_d0)):
            candidate = (tuple(new_sw), tuple(first), tuple(second))
            if best is None or candidate < best:
                best = candidate
    return json.dumps([s, *[list(row) for row in best]], separators=(",", ":"))


def automaton_class(key_or_aut, s=None):
    """Canonical string under state renaming and exchange of the letters.

    Accept an automaton, a complete key, or ``(s, swap, successor0,
    successor1)``.  The state count is part of the canonical string.
    """
    if len(key_or_aut) == 5:
        declared = int(key_or_aut[0])
        aut = _automaton(key_or_aut[1:4])
    elif len(key_or_aut) == 4:
        declared = int(key_or_aut[0])
        aut = _automaton(key_or_aut[1:4])
    else:
        aut = _automaton(key_or_aut)
        declared = len(aut[0]) if s is None else int(s)
    if declared != len(aut[0]):
        raise ValueError("state count disagrees with the automaton")
    return _automaton_class(aut)


def settled_flags(key):
    s, sw, _d0, _d1, placements = normalize_key(key)
    W = words(s)
    root = [sum(sw[q] for q in word) % 2 for word in W]
    return {
        "s1": s == 1,
        "single_placement": len(placements) == 1,
        "first_letter_settled": all(
            len({root[w] for w in triple}) > 1 for triple in placements
        ),
    }


def solve_pattern(pattern, n, previous_model=None, solver_name="cadical195",
                  budget=CONFLICT_BUDGET):
    """Budgeted NAE solving with a true unit at the smallest used address.

    ``previous_model`` is the immediately preceding level's alive model.
    Its prefix lift is a phase preference, never a constraint.  An alive
    result supplies a Boolean model for every address, including unused ones.
    """
    start = time.perf_counter()
    n = int(n)
    if n < 0:
        raise ValueError("level must be nonnegative")
    count = 1 << n
    rows = np.asarray(pattern, dtype=np.int64)
    if not rows.size:
        rows = rows.reshape((0, 3))
    if rows.ndim != 2 or rows.shape[1] != 3:
        raise ValueError("pattern must have three columns")
    if rows.size and (int(rows.min()) < 0 or int(rows.max()) >= count):
        raise ValueError("pattern address outside the level")
    budget = int(budget)
    if budget < 1:
        raise ValueError("a finite positive conflict budget is required")
    phase_requested = previous_model is not None
    if phase_requested and (n < 1 or len(previous_model) != count // 2):
        raise ValueError("previous model must belong to the immediately preceding level")
    info = {
        "phase_requested": phase_requested,
        "phase_applied": False,
        "phase_supported": None,
        "solver": solver_name,
        "budget": budget,
    }
    if not rows.size:
        model = ([bool(previous_model[x >> 1]) for x in range(count)]
                 if phase_requested else [False] * count)
        return {"verdict": 1, "conflicts": 0,
                "wall_seconds": time.perf_counter() - start,
                "model": model, **info}

    clauses = []
    for a, b, c in rows.tolist():
        positive = [a + 1, b + 1, c + 1]
        clauses.append(positive)
        clauses.append([-positive[0], -positive[1], -positive[2]])
    clauses.append([int(rows.min()) + 1])
    with Solver(name=solver_name, bootstrap_with=clauses) as solver:
        if phase_requested:
            phases = [(x + 1) if previous_model[x >> 1] else -(x + 1)
                      for x in range(count)]
            try:
                solver.set_phases(phases)
                info["phase_supported"] = True
                info["phase_applied"] = True
            except (NotImplementedError, AttributeError):
                info["phase_supported"] = False
        before = int(solver.accum_stats().get("conflicts", 0))
        solver.conf_budget(budget)
        answer = solver.solve_limited()
        conflicts = int(solver.accum_stats().get("conflicts", 0)) - before
        model = None
        if answer is True:
            model = [False] * count
            for literal in solver.get_model() or ():
                address = abs(literal) - 1
                if address < count:
                    model[address] = literal > 0
        verdict = None if answer is None else int(answer)
    return {"verdict": verdict, "conflicts": conflicts,
            "wall_seconds": time.perf_counter() - start,
            "model": model, **info}


def fate_fields(knots_n, verdict_n):
    """Classify only when every completion of null verdicts agrees."""
    if len(knots_n) != len(verdict_n):
        raise ValueError("knot and verdict profiles must have equal length")
    nonempty = [i for i, knots in enumerate(knots_n) if knots]
    dead = [i for i, value in enumerate(verdict_n) if value == 0]
    first_death = dead[0] + 1 if dead else None
    if not nonempty:
        fate = "F0"
    else:
        first = nonempty[0]
        if verdict_n[first] == 0:
            fate = "F1"
        elif verdict_n[first] is None:
            fate = "FU"
        elif any(verdict_n[i] == 0 for i in nonempty if i > first):
            fate = "F2"
        elif any(verdict_n[i] is None for i in nonempty if i > first):
            fate = "FU"
        else:
            fate = "F3"
    returned = any(value == 1 for value in verdict_n[dead[0] + 1:]) if dead else False
    return {
        "fate": fate,
        "first_death": first_death,
        "null_before_death": bool(dead and any(v is None for v in verdict_n[:dead[0]])),
        "undecided_after": bool(
            fate in ("F1", "F2") and dead and
            any(v is None for v in verdict_n[dead[0] + 1:])
        ),
        "return": returned,
    }


def _peak_rss_mb():
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss
    return float(value) / (1024.0 * 1024.0 if sys.platform == "darwin" else 1024.0)


def evaluate_key(key, solver_name="cadical195", budget=CONFLICT_BUDGET):
    """Read every level 1..12, streaming patterns even after a death."""
    start = time.perf_counter()
    key = normalize_key(key)
    knots_n, join_n, verdict_n, conflicts_n, wall_n, phase_n = [], [], [], [], [], []
    level_wall_n = []
    digest = hashlib.sha1()
    previous_model = None
    for n in range(1, LEVELS + 1):
        level_start = time.perf_counter()
        pattern = level_pattern(key, n)
        count = len(pattern)
        knots_n.append(count)
        if count:
            last_bits = pattern & 1
            joins = (last_bits[:, 0] != last_bits[:, 1]) | (last_bits[:, 0] != last_bits[:, 2])
            join_n.append(int(np.count_nonzero(joins)))
        else:
            join_n.append(0)
        digest.update(struct.pack("<qq", n, count))
        digest.update(np.ascontiguousarray(pattern, dtype="<i8").tobytes(order="C"))
        result = solve_pattern(pattern, n, previous_model, solver_name, budget)
        verdict_n.append(result["verdict"])
        conflicts_n.append(result["conflicts"])
        wall_n.append(result["wall_seconds"])
        phase_n.append({name: result[name] for name in
                        ("phase_requested", "phase_applied", "phase_supported")})
        previous_model = result["model"] if result["verdict"] == 1 else None
        level_wall_n.append(time.perf_counter() - level_start)
    letter, relative = description_classes(key)
    j10, j11, j12 = join_n[-3:]
    if j10 == j11 == j12:
        joining_growth = "constant"
    elif j12 > 0 and j12 >= 1.15 * j11 and j11 >= 1.15 * j10:
        joining_growth = "grows"
    else:
        joining_growth = "other"
    return {
        "key": key_json(key),
        "key_id": key_id(key),
        "pattern_hash": digest.hexdigest(),
        "hash_serialization": HASH_SERIALIZATION,
        "knots_n": knots_n,
        "join_n": join_n,
        "verdict_n": verdict_n,
        "conflicts_n": conflicts_n,
        "wall_n": wall_n,
        "level_wall_n": level_wall_n,
        "phase_n": phase_n,
        **fate_fields(knots_n, verdict_n),
        "rho_max": max(knots / (1 << n) for n, knots in enumerate(knots_n, 1)),
        "rho12": knots_n[-1] / (1 << LEVELS),
        "letter_class": letter[0],
        "letter_degree": letter[1],
        "rel_class": relative[0],
        "rel_degree": relative[1],
        "automaton_class": automaton_class(key),
        "flags": settled_flags(key),
        "join_growth": joining_growth,
        "total_wall_seconds": time.perf_counter() - start,
        "peak_rss_mb": _peak_rss_mb(),
    }
