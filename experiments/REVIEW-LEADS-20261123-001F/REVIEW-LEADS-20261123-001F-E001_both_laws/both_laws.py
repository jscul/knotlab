"""Shared engine of REVIEW-LEADS-20261123-001F-E001: the rule (even parity and
not-all-equal) on ordinary growth.

Imported, read-only, from the program's archive (sources noted in SOURCES):
  * GENERATORS-20261120-001A fixtures.py: the ordinary growth engine
    (``trajectory`` / ``literal_turn``: who is born, from which parents, with how
    many fresh distinctions; the structure never depends on values) and
    ``source_from`` for building a source from meetings and loose counts;
  * CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B phase_clocks.py: the
    five-founder clock (``source_cases()['five_odd']``) and its physically
    identified phase order.

A history is, up to renaming, an assignment of one bit to every (child, parent)
edge of the growth graph (the value of the distinction the parent pays to that
child) together with, for each newborn at the horizon, the number of ones among
its still-loose fresh distinctions. A knot's word is the multiset of its
incident edge bits plus its loose ones, so a word is lawful exactly when its
number of ones is. Two continuations that differ by a renaming of fresh
distinctions have the same edge bits, and two with different edge bits cannot
be renamed into each other. That identification is what the counts below use;
``brute_force_classes`` checks it against explicit named distinctions.
"""

from __future__ import annotations

import hashlib
import importlib.util
import itertools
import json
import math
import random
import sys
import time
from collections import Counter, defaultdict
from dataclasses import dataclass
from functools import cache
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
TICKET = "REVIEW-LEADS-20261123-001F"
OUT = ROOT / "artifacts" / TICKET / f"{TICKET}-E001_both_laws"
FIXTURE = ROOT / ("experiments/GENERATORS-20261120-001A/"
                  "GENERATORS-20261120-001A-E001_generators/fixtures.py")
CLOCK = ROOT / ("experiments/CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B/"
                "CALIBRATIONS-CLOCKS-AND-WIDER-KNOTS-20261120-001B-E001_receivers/phase_clocks.py")
SOURCES = {"fixtures": FIXTURE, "phase_clocks": CLOCK,
           "preregistration": ROOT / "research" / TICKET / "preregistration.md"}
SEED = 2026112306
START_CAP = 4096
START_DRAW = 1024
ARMS = ("rule", "parity", "nae")
sys.setrecursionlimit(20000)
sys.path.insert(0, str(ROOT / "tools"))


# --------------------------------------------------------------------------- loading
def _load(name, path):
    if name in sys.modules:
        return sys.modules[name]
    sys.path.insert(0, str(path.parent))
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


@cache
def fixtures():
    return _load("both_laws_fixtures", FIXTURE)


@cache
def phase_clocks():
    return _load("both_laws_phase_clocks", CLOCK)


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_hashes():
    return {k: sha(v) for k, v in SOURCES.items()}


# --------------------------------------------------------------------------- the rule
def lawful(arm, n, k):
    """May a knot of n places hold k ones under the arm's rule?"""
    if arm == "rule":
        return k % 2 == 0 and 0 < k < n
    if arm == "parity":
        return k % 2 == 0
    if arm == "nae":
        return 0 < k < n
    raise ValueError(arm)


def completions(arm, p, fresh, s):
    """Numbers of ones among the fresh distinctions that complete a newborn whose p
    incoming values hold s ones."""
    n = p + fresh
    return tuple(f for f in range(fresh + 1) if lawful(arm, n, s + f))


# --------------------------------------------------------------------------- sources
def seven_source():
    return fixtures().source_from(
        [(0, 1), (0, 1), (0, 4), (1, 4), (2, 4), (2, 6), (3, 4), (3, 5), (5, 6)],
        [3, 0, 3, 3, 3, 2, 2])


def nine_source():
    return fixtures().source_from(
        [(0, 2), (0, 3), (0, 5), (1, 2), (2, 7), (3, 8), (4, 5), (4, 8), (5, 6), (6, 7)],
        [5, 2, 4, 3, 3, 4, 3, 3, 2])


def five_source():
    return phase_clocks().source_cases()["five_odd"]


# --------------------------------------------------------------------------- structure
@dataclass
class Structure:
    name: str
    stars: tuple
    layers: list            # layers[l-1] = list of births of parent step l
    horizon: int
    knots_by_step: list
    max_steps: int
    cap: int
    stalled_at: int | None  # first step whose turn was not an extension, if any
    both_laws_agree: bool

    @property
    def n0(self):
        return len(self.stars)

    def loose(self, u):
        owners = Counter(d for row in self.stars for d in row)
        return sum(1 for d in self.stars[u] if owners[d] == 1)

    def births(self, depth=None):
        depth = self.horizon if depth is None else depth
        return [b for layer in self.layers[:depth] for b in layer]

    def layer_of(self):
        return {b.knot: l for l, layer in enumerate(self.layers, 1) for b in layer}

    def arities(self, depth=None):
        depth = self.horizon if depth is None else depth
        founders = Counter(len(r) for r in self.stars)
        born = Counter(len(b.support) for b in self.births(depth))
        return founders, born


def build_structure(name, stars, max_steps, cap):
    """Ordinary growth to the horizon: the last step with at most ``cap`` knots in
    all and at most ``max_steps`` parent steps."""
    f = fixtures()
    knots = [len(stars)]
    frames, layers = [stars], []
    stalled = None
    agree = True
    other_frames = [stars]
    for step in range(1, max_steps + 1):
        status, births, _ = f.literal_turn(frames[-1], "parity")
        status2, births2, _ = f.literal_turn(other_frames[-1], "nae")
        if status != "extend" or status2 != "extend":
            stalled = step
            break
        agree &= (status == status2 and [(b.parents, b.fresh) for b in births] ==
                  [(b.parents, b.fresh) for b in births2])
        if knots[-1] + len(births) > cap:
            layers.append(births)  # kept only to show the step that crosses the cap
            knots.append(knots[-1] + len(births))
            break
        layers.append(births)
        knots.append(knots[-1] + len(births))
        frames.append(frames[-1] + tuple(b.support for b in births))
        other_frames.append(other_frames[-1] + tuple(b.support for b in births2))
    horizon = max(i for i, k in enumerate(knots) if k <= cap and i <= max_steps)
    return Structure(name, stars, layers[:horizon], horizon, knots, max_steps, cap,
                     stalled, agree)


# --------------------------------------------------------------------------- starts
class Starts:
    """Valued starts of one structure for one arm."""

    def __init__(self, stars):
        self.stars = stars
        owners = defaultdict(list)
        for u, row in enumerate(stars):
            for d in row:
                owners[d].append(u)
        self.D = len({d for r in stars for d in r})
        assert sorted(owners) == list(range(self.D))
        self.shared = sorted(d for d, o in owners.items() if len(o) == 2)
        self.loose_bits = {u: [d for d in row if len(owners[d]) == 1]
                           for u, row in enumerate(stars)}
        self.mask = [sum(1 << d for d in row) for row in stars]
        self.loose_mask = [sum(1 << d for d in self.loose_bits[u]) for u in range(len(stars))]
        self.arity = [len(r) for r in stars]

    def is_lawful(self, arm, value):
        return all(lawful(arm, self.arity[u], (value & self.mask[u]).bit_count())
                   for u in range(len(self.stars)))

    def count_lawful(self, arm):
        total = 0
        for bits in itertools.product((0, 1), repeat=len(self.shared)):
            val = dict(zip(self.shared, bits))
            prod = 1
            for u, row in enumerate(self.stars):
                s = sum(val[d] for d in row if d in val)
                h = len(self.loose_bits[u])
                prod *= sum(math.comb(h, k) for k in range(h + 1)
                            if lawful(arm, self.arity[u], s + k))
                if not prod:
                    break
            total += prod
        return total

    def enumerate_lawful(self, arm):
        out = []
        for bits in itertools.product((0, 1), repeat=len(self.shared)):
            base = sum(b << d for b, d in zip(bits, self.shared))
            per_founder = []
            for u, row in enumerate(self.stars):
                s = (base & self.mask[u]).bit_count()
                options = []
                lb = self.loose_bits[u]
                for pattern in range(1 << len(lb)):
                    if lawful(arm, self.arity[u], s + pattern.bit_count()):
                        options.append(sum(1 << d for i, d in enumerate(lb) if pattern >> i & 1))
                if not options:
                    per_founder = None
                    break
                per_founder.append(options)
            if per_founder is None:
                continue
            for combo in itertools.product(*per_founder):
                out.append(base | sum(combo))
        return sorted(out)

    def draw(self, arm):
        """Every lawful valuation if there are at most START_CAP of them, else
        START_DRAW distinct lawful valuations from random.Random(SEED), by
        rejection from uniform bit strings (each accepted string is uniform over
        the lawful valuations; repeats are skipped)."""
        n = self.count_lawful(arm)
        if n <= START_CAP:
            vals = self.enumerate_lawful(arm)
            assert len(vals) == n
            return n, "all", vals, 0
        rng = random.Random(SEED)
        seen, out, raw = set(), [], 0
        while len(out) < START_DRAW:
            v = rng.getrandbits(self.D)
            raw += 1
            if v in seen or not self.is_lawful(arm, v):
                continue
            seen.add(v)
            out.append(v)
        return n, "drawn", out, raw

    def carried(self, value, live):
        """Ones among the loose distinctions of each live founder."""
        return tuple((value & self.loose_mask[u]).bit_count() for u in live)


def start_digest(vals):
    return hashlib.sha256(",".join(map(str, vals)).encode()).hexdigest()


# --------------------------------------------------------------------------- frontier counting
class Overflow(Exception):
    pass


class HistoryCounter:
    """Exact number of histories to ``depth`` parent steps, from a start's carried
    counts, by elimination of knots in a fixed order (a frontier of open knots,
    each with the number of ones it still has to pay).

    A knot is open while it has unprocessed children. Processing a newborn picks
    one bit from each of its parents (within the parents' remaining budgets, and
    leaving each parent able to pay its remaining children), then a number f of
    ones among its fresh distinctions that the arm allows. f becomes the newborn's
    budget when it has children inside the depth; a newborn at the depth instead
    contributes the number of allowed f (its loose ones are part of the history).
    """

    def __init__(self, struct, arm, depth, cap_states=3_000_000, deadline=None):
        self.struct, self.arm, self.depth, self.cap = struct, arm, depth, cap_states
        self.deadline = deadline
        self.calls = 0
        self.memo = {}
        self._plan()

    def _plan(self):
        st, depth = self.struct, self.depth
        births = st.births(depth)
        layer_of = st.layer_of()
        children = defaultdict(list)
        for b in births:
            for p in b.parents:
                children[p].append(b.knot)
        for b in births:
            if layer_of[b.knot] < depth:
                assert len(children[b.knot]) == len(b.fresh), (b.knot, len(children[b.knot]), len(b.fresh))
            else:
                assert not children[b.knot]
        live = [u for u in range(st.n0) if st.loose(u) > 0]
        for u in live:
            assert len(children[u]) == st.loose(u), u
        self.live = live
        self.children = children
        frontier = list(live)
        remaining = {u: len(children[u]) for u in live}
        done = set(range(st.n0))
        todo = {b.knot: b for b in births}
        steps = []
        self.max_frontier = len(frontier)
        while todo:
            best = None
            for b in todo.values():
                if not all(p in done for p in b.parents):
                    continue
                fr = len(frontier)
                for p in b.parents:
                    if remaining[p] == 1:
                        fr -= 1
                if children[b.knot]:
                    fr += 1
                key = (fr, layer_of[b.knot], b.knot)
                if best is None or key < best[0]:
                    best = (key, b)
            b = best[1]
            positions = [frontier.index(p) for p in b.parents]
            after = [remaining[p] - 1 for p in b.parents]
            closes = [pos for pos, a in zip(positions, after) if a == 0]
            for p in b.parents:
                remaining[p] -= 1
            for pos in sorted(closes, reverse=True):
                del frontier[pos]
            opens = bool(children[b.knot])
            if opens:
                frontier.append(b.knot)
                remaining[b.knot] = len(children[b.knot])
            done.add(b.knot)
            del todo[b.knot]
            p = len(b.parents)
            fresh = len(b.fresh)
            allowed = [completions(self.arm, p, fresh, s) for s in range(p + 1)]
            steps.append((positions, tuple(after), tuple(closes), opens, allowed, b.knot))
            self.max_frontier = max(self.max_frontier, len(frontier))
        self.steps = steps
        self.nsteps = len(steps)

    def count(self, carried):
        return self._solve(0, tuple(carried))

    def count_by_carried(self, carried, layer):
        """Counter: number of ones among the loose distinctions of the knots born at
        parent step ``layer`` (the carried count at that stage) -> number of histories."""
        self._track = layer
        if not hasattr(self, "_layer_of_step"):
            lo = self.struct.layer_of()
            self._layer_of_step = [lo[step[5]] for step in self.steps]
            self._memo_acc = {}
        return self._solve_acc(0, tuple(carried))

    def _solve_acc(self, i, state):
        if i == self.nsteps:
            return {0: 1} if not state else {}
        key = (self._track, i, state)
        hit = self._memo_acc.get(key)
        if hit is not None:
            return hit
        self.calls += 1
        if len(self._memo_acc) > self.cap or (
                self.deadline is not None and self.calls % 2048 == 0 and time.time() > self.deadline):
            raise Overflow
        positions, after, closes, opens, allowed, _ = self.steps[i]
        tracked = self._layer_of_step[i] == self._track
        total = {}
        budget = list(state)
        for bits in itertools.product((0, 1), repeat=len(positions)):
            ok = True
            for pos, bit, a in zip(positions, bits, after):
                left = budget[pos] - bit
                if left < 0 or left > a:
                    ok = False
                    break
            if not ok:
                continue
            fs = allowed[sum(bits)]
            if not fs:
                continue
            new = budget[:]
            for pos, bit in zip(positions, bits):
                new[pos] -= bit
            kept = [v for j, v in enumerate(new) if j not in closes]
            for f in fs:
                sub = self._solve_acc(i + 1, tuple(kept + [f]) if opens else tuple(kept))
                add = f if tracked else 0
                for k, m in sub.items():
                    total[k + add] = total.get(k + add, 0) + m
        self._memo_acc[key] = total
        return total

    def _solve(self, i, state):
        if i == self.nsteps:
            return 1 if not state else 0
        key = (i, state)
        hit = self.memo.get(key)
        if hit is not None:
            return hit
        self.calls += 1
        if len(self.memo) > self.cap or (
                self.deadline is not None and self.calls % 2048 == 0 and time.time() > self.deadline):
            raise Overflow
        positions, after, closes, opens, allowed, _ = self.steps[i]
        total = 0
        budget = list(state)
        p = len(positions)
        for bits in itertools.product((0, 1), repeat=p):
            ok = True
            for pos, bit, a in zip(positions, bits, after):
                left = budget[pos] - bit
                if left < 0 or left > a:
                    ok = False
                    break
            if not ok:
                continue
            fs = allowed[sum(bits)]
            if not fs:
                continue
            new = budget[:]
            for pos, bit in zip(positions, bits):
                new[pos] -= bit
            kept = [v for j, v in enumerate(new) if j not in closes]
            if opens:
                for f in fs:
                    total += self._solve(i + 1, tuple(kept + [f]))
            else:
                total += len(fs) * self._solve(i + 1, tuple(kept))
        self.memo[key] = total
        return total


# --------------------------------------------------------------------------- SAT survival
class Cnf:
    def __init__(self):
        self.clauses = []
        self.n = 0

    def var(self):
        self.n += 1
        return self.n

    def add(self, *lits):
        out = []
        for lit in lits:
            if lit is True:
                return
            if lit is False:
                continue
            out.append(lit)
        self.clauses.append(out)

    def counter(self, lits):
        """g[0..d+1]: g[k] true iff at least k of lits are true (full equivalence);
        g[0] is True and g[d+1] is False."""
        d = len(lits)
        prev = [True] + [False] * (d + 1)
        for i, l in enumerate(lits, 1):
            cur = [True] + [None] * (d + 1)
            for k in range(1, d + 2):
                if k > i:
                    cur[k] = False
                    continue
                s = self.var()
                cur[k] = s
                a, b = prev[k], prev[k - 1]
                # s <-> a or (l and b)
                self.add(-s, a, l)
                self.add(-s, a, b)
                self.add(_neg(a), s)
                self.add(-l, _neg(b), s)
            prev = cur
        return prev

    def allow(self, lits, allowed):
        g = self.counter(lits)
        d = len(lits)
        for k in range(d + 1):
            if k in allowed:
                continue
            # not exactly k ones: not (g[k] and not g[k+1])
            self.add(_neg(g[k]), g[k + 1])
        return g


def _neg(x):
    if x is True:
        return False
    if x is False:
        return True
    return -x


class Survival:
    """Does a start have a whole lawful history through ``depth`` parent steps?
    One SAT instance (edge bits, one counter per knot), the start enters by
    assumptions on the founders' counters."""

    def __init__(self, struct, arm, depth):
        from pysat.solvers import Cadical153
        self.struct, self.arm, self.depth = struct, arm, depth
        cnf = Cnf()
        births = struct.births(depth)
        layer_of = struct.layer_of()
        edge = {}
        children = defaultdict(list)
        for b in births:
            for p in b.parents:
                edge[(b.knot, p)] = cnf.var()
                children[p].append(b.knot)
        self.live = [u for u in range(struct.n0) if struct.loose(u) > 0]
        self.founder_counter = {}
        for u in self.live:
            lits = [edge[(c, u)] for c in children[u]]
            assert len(lits) == struct.loose(u)
            self.founder_counter[u] = cnf.counter(lits)
        for b in births:
            p = len(b.parents)
            fresh = len(b.fresh)
            lits = [edge[(b.knot, q)] for q in b.parents]
            if layer_of[b.knot] < depth:
                lits += [edge[(c, b.knot)] for c in children[b.knot]]
                assert len(lits) == p + fresh
                allowed = {k for k in range(p + fresh + 1) if lawful(arm, p + fresh, k)}
            else:
                allowed = {s for s in range(p + 1) if completions(arm, p, fresh, s)}
            cnf.allow(lits, allowed)
        self.solver = Cadical153(bootstrap_with=cnf.clauses)
        self.nvars, self.nclauses = cnf.n, len(cnf.clauses)
        self.edge_vars = sorted(edge.values())
        self._next_var = cnf.n
        last = [b for b in births if layer_of[b.knot] == depth]
        self._last = [([edge[(b.knot, q)] for q in b.parents], len(b.parents), len(b.fresh)) for b in last]

    def _assumptions(self, carried):
        assume = []
        for u, c in zip(self.live, carried):
            g = self.founder_counter[u]
            if c >= 1:
                assume.append(g[c])
            if c + 1 <= len(g) - 2:
                assume.append(-g[c + 1])
        return assume

    def alive(self, carried):
        return self.solver.solve(assumptions=self._assumptions(carried))

    def unique(self, carried):
        """None if the start has no history to this depth, True if it has exactly one
        whole history (edge bits and the number of ones among the still-loose fresh
        distinctions of the newborns at the depth), False if at least two."""
        assume = self._assumptions(carried)
        if not self.solver.solve(assumptions=assume):
            return None
        model = set(l for l in self.solver.get_model() if l > 0)
        multiplicity = 1
        for lits, p, fresh in self._last:
            sone = sum(1 for l in lits if l in model)
            multiplicity *= len(completions(self.arm, p, fresh, sone))
        if multiplicity > 1:
            return False
        self._next_var += 1
        act = self._next_var
        self.solver.add_clause([-act] + [(-v if v in model else v) for v in self.edge_vars])
        another = self.solver.solve(assumptions=assume + [act])
        self.solver.add_clause([-act])
        return not another

    def close(self):
        self.solver.delete()


class SurvivalFrom:
    """Can the budgets of the knots born at parent step ``base`` (the numbers of ones
    among their loose distinctions) be continued by a whole lawful history through
    ``depth`` parent steps? The same edge-bit instance as Survival, with the knots
    of step ``base`` playing the part of the founders."""

    def __init__(self, struct, arm, depth, base):
        from pysat.solvers import Cadical153
        assert 1 <= base < depth
        self.struct, self.arm, self.depth, self.base = struct, arm, depth, base
        cnf = Cnf()
        births = [b for layer in struct.layers[base:depth] for b in layer]
        layer_of = struct.layer_of()
        edge = {}
        children = defaultdict(list)
        for b in births:
            for p in b.parents:
                edge[(b.knot, p)] = cnf.var()
                children[p].append(b.knot)
        self.live = [b.knot for b in struct.layers[base - 1] if len(b.fresh) > 0]
        self.counter = {}
        for u in self.live:
            lits = [edge[(c, u)] for c in children[u]]
            assert len(lits) == len(next(b for b in struct.layers[base - 1] if b.knot == u).fresh)
            self.counter[u] = cnf.counter(lits)
        for b in births:
            p, fresh = len(b.parents), len(b.fresh)
            lits = [edge[(b.knot, q)] for q in b.parents]
            if layer_of[b.knot] < depth:
                lits += [edge[(c, b.knot)] for c in children[b.knot]]
                allowed = {k for k in range(p + fresh + 1) if lawful(arm, p + fresh, k)}
            else:
                allowed = {s for s in range(p + 1) if completions(arm, p, fresh, s)}
            cnf.allow(lits, allowed)
        self.solver = Cadical153(bootstrap_with=cnf.clauses)

    def alive(self, budgets):
        assume = []
        for u, c in zip(self.live, budgets):
            g = self.counter[u]
            if c >= 1:
                assume.append(g[c])
            if c + 1 <= len(g) - 2:
                assume.append(-g[c + 1])
        return self.solver.solve(assumptions=assume)

    def close(self):
        self.solver.delete()


# --------------------------------------------------------------------------- brute force check
def brute_force_classes(struct, arm, depth, value):
    """Explicit named-distinction enumeration of every lawful completion and every
    allocation of loose distinctions to children, to ``depth`` steps, from the
    valuation ``value``; then the classes of the resulting continuations

      * under renaming of fresh distinctions only (the start's own distinctions,
        loose ones included, keep their names), and
      * under renaming of every distinction (equal-valued loose distinctions of
        a founder interchangeable too): the value-flow classes.

    A continuation is summarised by what each distinction is held by and its
    value; two continuations are related by a renaming exactly when the summaries
    agree up to that renaming."""
    stars = struct.stars
    D = len({d for r in stars for d in r})
    vals = {d: value >> d & 1 for d in range(D)}
    holders = defaultdict(list)
    for u, row in enumerate(stars):
        for d in row:
            holders[d].append(u)
    loose_of = {u: [d for d in stars[u] if len(holders[d]) == 1] for u in range(struct.n0)}
    by_layer = struct.layers[:depth]
    literal, flow = set(), set()

    def recurse(l, vals, loose_of, held):
        if l == depth:
            fixed = tuple(sorted((d, tuple(sorted(held[d])), vals[d]) for d in vals if d < D))
            fresh = tuple(sorted((tuple(sorted(held[d])), vals[d]) for d in vals if d >= D))
            literal.add((fixed, fresh))
            flow.add(tuple(sorted((tuple(sorted(held[d])), vals[d]) for d in vals)))
            return
        layer = by_layer[l]
        parents_here = sorted({p for b in layer for p in b.parents})
        per_parent = []
        for p in parents_here:
            ch = [b.knot for b in layer if p in b.parents]
            assert len(ch) == len(loose_of[p]), (p, ch, loose_of[p])
            per_parent.append([list(zip(ch, perm)) for perm in itertools.permutations(loose_of[p])])
        for combo in itertools.product(*per_parent):
            gave = defaultdict(dict)
            for p, pairs in zip(parents_here, combo):
                for child, d in pairs:
                    gave[child][p] = d
            ranges, opts = [], []
            for b in layer:
                inputs = [gave[b.knot][p] for p in b.parents]
                s = sum(vals[d] for d in inputs)
                n = len(b.parents) + len(b.fresh)
                opts.append((b, inputs))
                ranges.append([bits for bits in itertools.product((0, 1), repeat=len(b.fresh))
                               if lawful(arm, n, s + sum(bits))])
            for pick in itertools.product(*ranges):
                new_vals = dict(vals)
                new_held = {d: list(h) for d, h in held.items()}
                new_loose = dict(loose_of)
                for (b, inputs), bits in zip(opts, pick):
                    for d in inputs:
                        new_held[d].append(b.knot)
                    ids = []
                    for bit in bits:
                        d = len(new_vals)
                        new_vals[d] = bit
                        new_held[d] = [b.knot]
                        ids.append(d)
                    new_loose[b.knot] = ids
                recurse(l + 1, new_vals, new_loose, new_held)

    recurse(0, dict(vals), loose_of, {d: list(h) for d, h in holders.items()})
    return len(literal), len(flow)


# --------------------------------------------------------------------------- the clock
def clock_phases(struct):
    """Phase bookkeeping of the five-founder clock from the engine's own births:
    ring[t][p] is the knot K_t(p); returns the stages at which the enrolled
    receiver K_t(0) is a return (its last original is the marked founder again)."""
    order, marker = phase_clocks().identify_origin(struct.stars)
    prev = list(order)
    ring = [list(order)]
    words = {k: (k,) for k in order}
    returns = []
    for t, layer in enumerate(struct.layers, 1):
        assert len(layer) == 5, (t, len(layer))
        cur = [None] * 5
        for b in layer:
            assert len(b.parents) == 2 and len(b.fresh) == 2
            ps = set(b.parents)
            hits = [p for p in range(5) if ps == {prev[p], prev[(p + 1) % 5]}]
            assert len(hits) == 1, (t, b)
            p = hits[0]
            assert cur[p] is None
            cur[p] = b.knot
            words[b.knot] = words[prev[p]] + (words[prev[(p + 1) % 5]][-1],)
        assert None not in cur
        ring.append(cur)
        prev = cur
        if words[cur[0]][-1] == order[0]:
            returns.append(t)
    return order, marker, ring, words, returns


class Ring:
    """The five-phase clock on carried counts. K_t(p) pays a_p to K_{t+1}(p) and b_p
    to K_{t+1}(p-1) with a_p + b_p = c_p; newborn p receives (a_p, b_{p+1}) and has
    two fresh distinctions, so four places. A return is the birth of K_t(0) at
    t = 5, 10, ...; it signals when its two incoming values differ."""

    P = 5
    RETURN_EVERY = 5

    def __init__(self, arm, T=30):
        self.arm, self.T = arm, T
        self.memo = {}
        self.trans = {c: self._transitions(c) for c in itertools.product((0, 1, 2), repeat=self.P)}

    def _transitions(self, c):
        options = {0: [(0, 0)], 1: [(1, 0), (0, 1)], 2: [(1, 1)]}
        out = Counter()
        for alloc in itertools.product(*(options[x] for x in c)):
            a = [x for x, _ in alloc]
            b = [y for _, y in alloc]
            xs = [a[p] for p in range(self.P)]
            ys = [b[(p + 1) % self.P] for p in range(self.P)]
            fs = [completions(self.arm, 2, 2, xs[p] + ys[p]) for p in range(self.P)]
            sig = int(xs[0] != ys[0])
            for f in itertools.product(*fs):
                out[(f, sig)] += 1
        return out

    def future(self, t, c):
        """Counter: pattern of return signals at stages t+1..T -> number of histories."""
        key = (t, c)
        hit = self.memo.get(key)
        if hit is not None:
            return hit
        if t == self.T:
            res = Counter({(): 1})
        else:
            res = Counter()
            ret = (t + 1) % self.RETURN_EVERY == 0
            for (c2, sig), m in self.trans[c].items():
                for pat, k in self.future(t + 1, c2).items():
                    res[((sig,) + pat) if ret else pat] += m * k
        self.memo[key] = res
        return res

    def future_counts(self, t, c):
        """Counter: number of signalling returns among stages t+1..T -> number of histories."""
        memo = self.__dict__.setdefault("_memo_counts", {})
        key = (t, c)
        hit = memo.get(key)
        if hit is not None:
            return hit
        if t == self.T:
            res = Counter({0: 1})
        else:
            res = Counter()
            ret = (t + 1) % self.RETURN_EVERY == 0
            for (c2, sig), m in self.trans[c].items():
                add = sig if ret else 0
                for k, cnt in self.future_counts(t + 1, c2).items():
                    res[k + add] += m * cnt
        memo[key] = res
        return res

    def reach(self, starts):
        """Per stage 0..T the set of carried-count vectors reachable from any start."""
        layer = set(starts)
        out = [set(layer)]
        for _ in range(self.T):
            layer = {c2 for c in layer for (c2, _) in self.trans[c]}
            out.append(set(layer))
        return out

    def alive_depth(self, c):
        """Largest t <= T such that some history of t parent steps exists."""
        layer = {c}
        for t in range(self.T):
            layer = {c2 for x in layer for (c2, _) in self.trans[x]}
            if not layer:
                return t
        return self.T


def null_single_position(p0, T=30):
    """Hand null (counting_null.md, H7) for carried count 1 or 9 with the single
    at phase p0: histories by number of signals, from the walk x -> x or x-1 mod 5
    with a return signalling when x_{5j} = 0. Independent of Ring."""
    walk = Counter({(p0 % 5, 0): 1})
    for t in range(1, T + 1):
        nxt = Counter()
        for (x, k), m in walk.items():
            for x2 in (x, (x - 1) % 5):
                k2 = k + (1 if (t % 5 == 0 and x2 == 0) else 0)
                nxt[(x2, k2)] += m
        walk = nxt
    out = Counter()
    for (x, k), m in walk.items():
        out[k] += m
    return out
