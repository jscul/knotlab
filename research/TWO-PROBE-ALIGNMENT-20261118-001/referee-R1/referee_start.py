"""Referee R1 for TWO-PROBE-ALIGNMENT-20261118-001: the joint-reconfiguration start, from scratch (no study code imported).

  ../../../.venv/bin/python -B referee_start.py > referee_start.json      (from this directory)

The proof's first part (its "Changing both tests together" section): root r = 000 with fresh outputs u, v; test an unused original
a with u; test r, a; if a is a neighbour commit (fresh output, a); if a is two steps away commit (fresh output, n) for n in the
interval of r, a other than r, a; if a is the opposite, configure both tests at once to (a, u), (a, v), then configure (b, u), (r, b)
for any of the six others and decide as before.  After the commitment (a four-place even parity on the port, the neighbour and two
fresh outputs) the probes are erased one at a time.

Every action is taken as a whole orbit under the automorphisms of the CURRENT bond-distance table (the referee's own table and
automorphism search, from referee_collision.py), and every member of every orbit is followed: the check fails if any member is
illegal, a wrong commitment, an erasure of anything but one whole probe, or leads to a state the rule does not cover.  It also checks
that the rule is stationary: two reached states with isomorphic tables get corresponding action orbits.
"""
import itertools
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import referee_collision as RC  # noqa: E402

R, U, V = 0, 8, 9
NBR = {1, 2, 4}


def weight(k):
    return bin(k).count("1")


def interval(a, b):
    """Originals agreeing with a and b wherever a and b agree."""
    agree = ~(a ^ b) & 7
    return {k for k in range(8) if (k & agree) == (a & agree)}


def rows_of(tests, committed=None):
    rows = RC.root(RC.originals())
    width = 10
    if committed is not None:
        port, b = committed
        out = set()
        for row in rows:
            for w1 in (0, 1):
                w2 = ((row >> port) ^ (row >> b) ^ w1) & 1
                out.add(row | (w1 << 10) | (w2 << 11))
        rows, width = out, 12
    for a, b in tests:
        rows = RC.test(rows, a, b, width)
        width += 2
    return rows, width


TABLE_CACHE = {}


def table(tests, committed=None):
    key = (tuple(tests), committed)
    if key not in TABLE_CACHE:
        rows, width = rows_of(tests, committed)
        D = RC.bond_table(rows, width)
        TABLE_CACHE[key] = (D, RC.automorphisms(D), width)
    return TABLE_CACHE[key]


def rule(tests, committed):
    """The proof's rule, on physical roles: returns (operation, operands) for a representative."""
    if committed is not None:
        return ("erase", (12, 13)) if tests else ("done", ())
    if not tests:
        return "add", (1, U)
    if len(tests) == 1:
        (a, port), = tests
        return "add", (R, a)
    t1, t2 = tests
    if set(t1) & {U, V} and set(t2) & {U, V}:          # both tests on the opposite with the two fresh outputs
        return "configure", ((1, U), (R, 1))
    (a, port), (r_, a2) = t1, t2
    assert r_ == R and a2 == a and port in (U, V)
    if weight(a) == 1:
        return "commit", (port, a)
    if weight(a) == 2:
        n = min(interval(R, a) - {R, a})
        return "commit", (port, n)
    return "configure", ((a, U), (a, V))


def apply(tests, committed, op, ops):
    if op == "add":
        return tests + (tuple(ops),), committed
    if op == "configure":
        return tuple(tuple(t) for t in ops), committed
    if op == "commit":
        return tests, tuple(ops)
    if op == "erase":
        width = 12
        idx = next(j for j in range(len(tests)) if (width + 2 * j, width + 2 * j + 1) == tuple(sorted(ops)))
        return tests[:idx] + tests[idx + 1:], committed
    raise ValueError(op)


def legal_state(tests, committed):
    """Is this a state the rule covers (tests on the expected roles)?"""
    if committed is not None:
        port, b = committed
        return port in (U, V) and b in NBR
    if len(tests) > 2:
        return False
    for a, b in tests:
        if a == b or max(a, b) >= 10:
            return False
    if len(tests) == 1:
        (a, port), = tests
        return a in range(1, 8) and port in (U, V)
    if len(tests) == 2:
        t1, t2 = tests
        if {t1, t2} in ({(7, U), (7, V)},) or sorted(tests) == sorted([(7, U), (7, V)]):
            return True
        (a, port), (r_, a2) = t1, t2
        return r_ == R and a2 == a and a in range(1, 8) and port in (U, V)
    return True


def norm_test(t):
    a, b = t
    if a in (U, V) and b < 8:
        a, b = b, a
    if b in (U, V) or a == R:
        return (a, b) if a < 8 else (b, a)
    return tuple(sorted(t))


def orbit(op, ops, aut, width):
    out = set()
    for g in aut:
        if op in ("add", "commit", "erase"):
            out.add((op, tuple(g[x] for x in ops)))
        elif op == "configure":
            out.add((op, tuple(tuple(g[x] for x in t) for t in ops)))
        else:
            out.add((op, ()))
    return out


def canonical_test_order(tests):
    """The rule reads physical roles; put a two-test state in the (original, port), (r, original) order when it is one."""
    if len(tests) != 2:
        return tuple(norm_test(t) for t in tests)
    t1, t2 = (norm_test(t) for t in tests)
    for x, y in ((t1, t2), (t2, t1)):
        if x[1] in (U, V) and y[0] == R and y[1] == x[0]:
            return (x, y)
    return tuple(sorted((t1, t2)))


def explore():
    seen = {}
    report = {"states": 0, "orbit members followed": 0, "failures": [], "commitments": [], "stationary conflicts": 0}
    stack = [((), None, 0)]
    by_sig = {}
    while stack:
        tests, committed, depth = stack.pop()
        tests = canonical_test_order(tests) if committed is None else tests
        key = (tests, committed)
        if key in seen:
            continue
        seen[key] = depth
        report["states"] += 1
        if not legal_state(tests, committed):
            report["failures"].append({"state": [tests, committed], "why": "not a state the rule covers"})
            continue
        op, ops = rule(tests, committed)
        if op == "done":
            rows, width = rows_of((), committed)
            report["clean interface"] = {"rows": len(rows), "width": width,
                                         "projection to the eight originals": len({r & 255 for r in rows})}
            continue
        D, aut, width = table(tests, committed)
        sig = (width, tuple(sorted(tuple(sorted(r)) for r in D)))
        by_sig.setdefault(sig, []).append((tests, committed, op))
        for o, ps in sorted(orbit(op, ops, aut, width)):
            report["orbit members followed"] += 1
            if o == "commit":
                port, b = ps
                ok = port in (U, V) and b in NBR
                report["commitments"].append({"from": [tests], "commit": [port, b], "correct": ok})
                if not ok:
                    report["failures"].append({"state": [tests, committed], "action": [o, ps], "why": "wrong commitment"})
                    continue
                stack.append((tests, (port, b), depth + 1))
            elif o == "erase":
                if tuple(sorted(ps)) not in [(12 + 2 * j, 13 + 2 * j) for j in range(len(tests))]:
                    report["failures"].append({"state": [tests, committed], "action": [o, ps], "why": "erases a non-probe"})
                    continue
                stack.append((*apply(tests, committed, o, ps), depth + 1))
            elif o in ("add", "configure"):
                operands = [ps] if o == "add" else list(ps)
                if any(max(t) >= 10 or t[0] == t[1] for t in operands):
                    report["failures"].append({"state": [tests, committed], "action": [o, ps], "why": "test on a non-permanent"})
                    continue
                nt, nc = apply(tests, committed, o, ps)
                stack.append((nt, nc, depth + 1))
    # stationarity: states with equal row-sorted tables must request the same kind of action
    for sig, items in by_sig.items():
        if len({op for _, _, op in items}) > 1:
            report["stationary conflicts"] += 1
    report["deepest state (actions)"] = max(seen.values())
    report["commitments"] = sorted({(tuple(map(tuple, c["from"][0])), tuple(c["commit"]), c["correct"]) for c in report["commitments"]})
    report["commitments"] = [list(c) for c in report["commitments"]]
    return report


if __name__ == "__main__":
    print(json.dumps(explore(), indent=1, default=str))
