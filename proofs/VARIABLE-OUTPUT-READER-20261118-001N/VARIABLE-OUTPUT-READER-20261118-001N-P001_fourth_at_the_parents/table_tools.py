"""Literal parent tests and exact bond measurements for the frontier controls."""

from collections import defaultdict, deque
from functools import cache
from hashlib import sha256
from importlib import util
from itertools import combinations
from pathlib import Path
import subprocess
import sys


PROOFS = Path(__file__).resolve().parents[2]
CLASS_FILE = next((PROOFS / "VARIABLE-OUTPUT-READER-20261118-001A").glob("*/check_classes.py"))
CUT_FILE = next((PROOFS / "VARIABLE-OUTPUT-READER-20261118-001H").glob("*/cross_search.cpp"))
CLASS_DIGEST = "8dd0ddaa58aa6e6f8ba1ec20fbe87b0b1c31cb090e93849fb271c8243dcb2472"
CUT_DIGEST = "8c2dbe3fe0f28ddf0987b054f4e5cf68b5b41aaebed3042fc652cba702e2e064"
INFINITY = 255


def module(path, expected, name):
    assert sha256(path.read_bytes()).hexdigest() == expected
    spec = util.spec_from_file_location(name, path)
    loaded = util.module_from_spec(spec)
    sys.modules[name] = loaded
    spec.loader.exec_module(loaded)
    return loaded


TABLES = module(CLASS_FILE, CLASS_DIGEST, "fourth_three_output_table_classes")


def compiler(output):
    assert sha256(CUT_FILE.read_bytes()).hexdigest() == CUT_DIGEST
    subprocess.run(("c++", "-std=c++20", "-O3", str(CUT_FILE), "-o", str(output)), check=True)
    return str(output)


def incidence(rows):
    users = defaultdict(list)
    neighbors = [set() for _ in rows]
    for j, scope in enumerate(rows):
        assert len(set(scope)) == len(scope)
        for bit in scope:
            users[bit].append(j)
    for holders in users.values():
        assert 1 <= len(holders) <= 2
        if len(holders) == 2:
            a, b = holders
            assert b not in neighbors[a]
            neighbors[a].add(b)
            neighbors[b].add(a)
    return users, neighbors


def tests(users, neighbors, bits):
    if not 1 <= len(bits) <= 3 or any(len(users.get(b, ())) != 1 for b in bits):
        return None
    parents = tuple(users[bit][0] for bit in bits)
    if len(set(parents)) != len(parents):
        return None
    pair_witnesses = tuple(tuple(sorted(neighbors[a] & neighbors[b])) for a, b in combinations(parents, 2))
    if not all(pair_witnesses) or len(parents) == 3 and set.intersection(*(neighbors[i] for i in parents)):
        return None
    return parents, pair_witnesses


def replay(rows):
    assert len(rows[0]) == 3
    seen = set(rows[0])
    events = [{"site": 0, "parents": (), "consumes": (), "fresh": rows[0]}]
    for i, row in enumerate(rows[1:], 1):
        consumes = tuple(b for b in row if b in seen)
        fresh = tuple(b for b in row if b not in seen)
        reviewed = tests(*incidence(rows[:i]), consumes)
        assert reviewed is not None and len(fresh) in (2, 3)
        assert len(fresh) == 3 if len(consumes) == 1 else True
        events.append({"site": i, "parents": reviewed[0], "consumes": consumes, "fresh": fresh})
        seen.update(fresh)
    assert seen == set(range(len(seen)))
    return events


def allowed(rows, arities=(3,)):
    users, neighbors = incidence(rows)
    loose = tuple(sorted(bit for bit, holders in users.items() if len(holders) == 1))
    return {p: found for size in arities for p in combinations(loose, size)
            if (found := tests(users, neighbors, p)) is not None}


def roles(rows, site, menu):
    _, neighbors = incidence(rows)
    all_roles = {}
    for marked, (holders, witnesses) in sorted(menu.items()):
        flags = []
        if site in holders:
            flags.append("holder")
        if any(site in pair for pair in witnesses):
            flags.append("pair_witness")
        if not flags and any(site in neighbors[holder] for holder in holders):
            flags.append("adjacent_only")
        if flags:
            all_roles[marked] = {"roles": tuple(flags), "holders": holders, "pair_witnesses": witnesses}
    return all_roles


def two_connected(rows):
    _, graph = incidence(rows)
    for removed in range(len(graph)):
        universe = set(range(len(graph))) - {removed}
        reached = {min(universe)}
        pending = list(reached)
        for i in pending:
            for j in graph[i] & (universe - reached):
                reached.add(j)
                pending.append(j)
        if reached != universe:
            return False
    return True


def masks(rows):
    return tuple(sum(1 << bit for bit in row) for row in rows)


def width(rows):
    return 1 + max(bit for row in rows for bit in row)


def all_tables(binary, fixtures):
    data = "".join(" ".join(map(str, (width(rows), len(rows), *masks(rows)))) + "\n" for rows in fixtures)
    process = subprocess.run([binary], input=data, text=True, capture_output=True, check=True)
    records = []
    for rows, encoded in zip(fixtures, process.stdout.splitlines(), strict=True):
        n = width(rows)
        dense = [bytearray(n) for _ in range(n)]
        for (i, j), value in zip(combinations(range(n), 2), bytes.fromhex(encoded), strict=True):
            dense[i][j] = dense[j][i] = value
        records.append(tuple(map(bytes, dense)))
    return records


def parity_minima(rows, arities=(2, 3)):
    space = {0}
    for row in masks(rows):
        space |= {word ^ row for word in space}
    assert len(space) == 1 << len(rows)
    minimal = []
    minima = {size: {} for size in arities}
    for word in sorted(space - {0}, key=lambda value: (value.bit_count(), value)):
        if any(old & word == old for old in minimal):
            continue
        minimal.append(word)
        bits = tuple(i for i in range(word.bit_length()) if word >> i & 1)
        for size, table in minima.items():
            for query in combinations(bits, size):
                table.setdefault(query, len(bits))
    return minima


def table_upper(table):
    return bytes(table[a][b] for a, b in combinations(range(len(table)), 2))


@cache
def quotient(rows):
    return TABLES.Quotient.make(rows)


def isometry(left, right):
    lq, rq = quotient(left), quotient(right)
    block = next(TABLES.isometries(lq.colored, rq.colored), None)
    if block is None:
        return None
    result = lq.lift(rq, block)
    assert TABLES.disagreement(left, right, result) is None
    return result


def inverse(mapping):
    return tuple(mapping.index(i) for i in range(len(mapping)))


@cache
def generators(table):
    _, _, group = quotient(table).automorphisms()
    assert all(TABLES.disagreement(table, table, g) is None for g in group)
    return group


def compose(left, right):
    return tuple(left[right[i]] for i in range(len(right)))


def transported(items, mapping):
    return {tuple(sorted(mapping[i] for i in group)) for group in items}


def menu_disagreement(left, menu_left, menu_right, mapping):
    if transported(menu_left, mapping) != set(menu_right):
        return mapping
    for g in generators(left):
        if transported(menu_left, g) != set(menu_left):
            return compose(mapping, g)
    return None


def missing_support(left, support, target, mapping):
    identity = tuple(range(len(left)))
    start = tuple(sorted(support))
    orbit = {start: identity}
    queue = deque([start])
    known = set(map(tuple, map(sorted, target)))
    group = generators(left)
    while queue:
        member = queue.popleft()
        current = orbit[member]
        moved = tuple(sorted(mapping[i] for i in member))
        if moved not in known:
            return compose(mapping, current)
        for g in group:
            image = tuple(sorted(g[i] for i in member))
            if image not in orbit:
                orbit[image] = compose(g, current)
                queue.append(image)
    return None


@cache
def physical(rows):
    users, adjacent = incidence(rows)
    counts = [0] * len(rows)
    for holders in users.values():
        if len(holders) == 1:
            counts[holders[0]] += 1
    graph = tuple(tuple(int(j in adjacent[i]) for j in range(len(rows))) for i in range(len(rows)))
    return TABLES.ColoredMatrix.make(graph, tuple(counts))


def ordinary_isomorphic(left, right):
    return len(left) == len(right) and next(TABLES.isometries(physical(left), physical(right)), None) is not None
