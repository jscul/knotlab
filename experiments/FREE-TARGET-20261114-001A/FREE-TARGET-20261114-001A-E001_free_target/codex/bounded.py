"""Exact fixed-budget, call-labelled saturation with finite witness schemas.

The unrestricted marked tables are a least closure, not a depth scan.  A
table's marks name distinct variables introduced inside that copy; incoming
ports are never marked again.  Mark coordinates are ordered by the copy that
introduces them (local indices first, then calls in source order).  Every
finite support has exactly such an ordering, so label permutations are not
needed.

At a boundary, F contains the possible port masks for full assignments to the
selected members.  D contains the masks for *all* assignments after any one
member is forgotten.  Side tables and local selections induce exact maps on
(F,D).  The selected-member count is retained.  Determinizing the resulting
call-labelled finite graph permits different supports at different target
depths while requiring one eventually periodic descending path.

Only positive accepting cycles certify boundedness.  Every cap is reported;
an interrupted closure or graph search is never a negative result.
"""
from __future__ import annotations

from collections import deque
from itertools import combinations, product
from pathlib import Path
import os
import sys
import time

sys.dont_write_bytecode = True


DEFAULT_LIMITS = {
    "profiles": 20000,
    "compositions": 2000000,
    "operations": 4096,
    "nfa_states": 30000,
    "nfa_edges": 400000,
    "subsets": 5000,
    "subset_edges": 20000,
    "base_assignments": 65536,
    "image_cache": 30000,
    "seconds": 1500.0,
    "memory_bytes": 5800000000,
}


class SearchLimit(RuntimeError):
    def __init__(self, detail, reason="cap"):
        super().__init__(detail)
        self.reason = reason


class _Guard:
    def __init__(self, checkpoint, limits):
        self.config = dict(DEFAULT_LIMITS)
        self.external = None
        if isinstance(limits, dict):
            unknown = set(limits) - set(self.config)
            if unknown:
                raise ValueError("unknown bounded-search limits: " + repr(sorted(unknown)))
            self.config.update(limits)
        elif limits is not None:
            self.external = limits.checkpoint
        self.callback = checkpoint
        self.started = time.monotonic()
        self.ticks = 0
        self.peak = 0

    def check(self, force=False):
        self.callback()
        if self.external is not None:
            self.external()
        self.ticks += 1
        if not force and self.ticks % 128:
            return
        try:
            rss = int(Path("/proc/self/statm").read_text().split()[1]) * os.sysconf("SC_PAGE_SIZE")
        except (FileNotFoundError, IndexError, ValueError):
            rss = 0
        self.peak = max(self.peak, rss)
        if rss >= self.config["memory_bytes"]:
            raise SearchLimit("bounded-search RSS ceiling reached", "memory")
        if time.monotonic() - self.started >= self.config["seconds"]:
            raise SearchLimit("bounded-search internal time ceiling reached")

    def cap(self, name, value):
        self.check()
        if value > self.config[name]:
            raise SearchLimit(f"{name} {value} exceeds explicit cap {self.config[name]}")


def _set_bits(mask):
    while mask:
        low = mask & -mask
        yield low.bit_length() - 1
        mask ^= low


def _parts(total, slots):
    if not slots:
        if total == 0:
            yield ()
        return
    if slots == 1:
        yield (total,)
        return
    for first in range(total + 1):
        for rest in _parts(total - first, slots - 1):
            yield (first,) + rest


def _mask(table):
    return sum(1 << j for j, value in enumerate(table) if bool(value))


class _Profiles:
    def __init__(self, prep, guard):
        self.prep, self.guard = prep, guard
        self.blocks = {}
        pending = [prep.S]
        while pending:
            typ = pending.pop()
            if typ in self.blocks:
                continue
            flat = prep.flat(typ)
            if (1 << flat["V"]) > guard.config["base_assignments"]:
                raise SearchLimit(f"type {typ} has 2**{flat['V']} local assignments, above explicit cap")
            self.blocks[typ] = dict(flat, nonknots=[(j, c, tuple(a)) for j, (c, a)
                                                   in enumerate(flat["calls"]) if c != "K"])
            pending.extend(c for c, _ in flat["calls"] if c != "K")
        self.types = tuple(sorted(self.blocks))
        self.records, self.rows, self.index, self.banks = [], [], {}, {}
        self.zero = {}
        self.bases = {}
        self.completed_marks = 0
        self.compositions = 0
        self.round_counts = []
        for typ in self.types:
            relation = _mask(prep.G[typ])
            self.zero[typ] = self._add(typ, 0, relation, None, None)[0]
        self.parents = {typ: [] for typ in self.types}
        for typ, block in self.blocks.items():
            for slot, (_, callee, _) in enumerate(block["nonknots"]):
                self.parents[callee].append((typ, slot))

    def _add(self, typ, count, relation, owned, children):
        key = (typ, count, relation)
        if key in self.index:
            return self.index[key], False
        self.guard.cap("profiles", len(self.records) + 1)
        number = len(self.records)
        self.index[key] = number
        self.records.append(dict(type=typ, count=count, relation=relation,
                                 own=owned, children=children))
        ports = self.blocks[typ]["k"]
        self.rows.append(tuple(tuple(mark for mark in range(1 << count)
                                     if relation & (1 << (p | (mark << ports))))
                               for p in range(1 << ports)))
        self.banks.setdefault((typ, count), []).append(number)
        return number, True

    def base(self, typ, continued=None):
        """Allowed local words, with the designated continuation left open."""
        key = (typ, continued)
        if key in self.bases:
            return self.bases[key]
        block = self.blocks[typ]
        p_mask = (1 << block["k"]) - 1
        result = []
        for assignment in range(1 << block["V"]):
            if assignment % 256 == 0:
                self.guard.check()
            states, valid, outgoing = [], True, 0
            for j, (callee, args) in enumerate(block["calls"]):
                state = sum(((assignment >> source) & 1) << bit
                            for bit, source in enumerate(args))
                if callee == "K":
                    if state == 0 or state == (1 << len(args)) - 1:
                        valid = False
                        break
                else:
                    states.append(state)
                    if j == continued:
                        outgoing = state
                    elif not self.prep.G[callee][state]:
                        valid = False
                        break
            if valid:
                result.append((assignment, assignment & p_mask, outgoing, tuple(states)))
        self.bases[key] = result
        return result

    def selections(self, typ, total, continued=None, own_min=0, seed=False):
        """All unordered fresh selections, partitioned among the child copies."""
        block = self.blocks[typ]
        eligible = [(slot, callee) for slot, (flat_j, callee, _) in enumerate(block["nonknots"])
                    if flat_j != continued]
        for own_count in range(own_min, min(total, block["V"] - block["k"]) + 1):
            for counts in _parts(total - own_count, len(eligible)):
                if seed and any(n >= total for n in counts):
                    continue
                sources = [self.banks.get((callee, n), ())
                           for (_, callee), n in zip(eligible, counts)]
                if any(not bank for bank in sources):
                    continue
                for owned in combinations(range(block["k"], block["V"]), own_count):
                    for chosen in product(*sources):
                        self.guard.check()
                        children = [-1] * len(block["nonknots"])
                        for (slot, _), child in zip(eligible, chosen):
                            children[slot] = child
                        yield owned, tuple(children)

    def compose_rows(self, typ, owned, children, continued=None):
        """Exact table on (new marks, input ports), with output-port masks."""
        self.compositions += 1
        self.guard.cap("compositions", self.compositions)
        block = self.blocks[typ]
        count = len(owned) + sum(self.records[x]["count"] for x in children if x >= 0)
        rows = [[0] * (1 << block["k"]) for _ in range(1 << count)]
        positive = [(slot, child, self.records[child]["count"])
                    for slot, child in enumerate(children)
                    if child >= 0 and self.records[child]["count"]]
        for serial, (assignment, incoming, outgoing, child_states) in enumerate(self.base(typ, continued)):
            if serial % 256 == 0:
                self.guard.check()
            variants = [sum(((assignment >> source) & 1) << bit
                            for bit, source in enumerate(owned))]
            offset = len(owned)
            for slot, child, marks in positive:
                possible = self.rows[child][child_states[slot]]
                variants = [old | (new << offset) for old in variants for new in possible]
                offset += marks
                if not variants:
                    break
            for marks in variants:
                rows[marks][incoming] |= 1 << outgoing
        return count, tuple(tuple(row) for row in rows)

    def compose_profile(self, typ, owned, children):
        count, rows = self.compose_rows(typ, owned, children)
        p = self.blocks[typ]["k"]
        relation = 0
        for marks, row in enumerate(rows):
            for incoming, allowed in enumerate(row):
                if allowed:
                    relation |= 1 << (incoming | (marks << p))
        return self._add(typ, count, relation, tuple(owned), tuple(children))

    def saturate(self, marks):
        """Least closure by mark count, followed by all zero-mark contexts."""
        while self.completed_marks < marks:
            count = self.completed_marks + 1
            before = len(self.records)
            agenda = deque()
            # Every non-unary introduction splits the marks into smaller
            # child supports, or introduces at least one local variable.
            for typ in self.types:
                for owned, children in self.selections(typ, count, seed=True):
                    number, fresh = self.compose_profile(typ, owned, children)
                    if fresh:
                        agenda.append(number)
            # A support may be arbitrarily far below the current copy.  This
            # closure is what removes any finite observation-depth cutoff.
            while agenda:
                child = agenda.popleft()
                typ = self.records[child]["type"]
                for parent, slot in self.parents[typ]:
                    children = [self.zero[c] for _, c, _ in self.blocks[parent]["nonknots"]]
                    children[slot] = child
                    number, fresh = self.compose_profile(parent, (), tuple(children))
                    if fresh:
                        agenda.append(number)
                self.guard.check()
            self.completed_marks = count
            self.round_counts.append(dict(marks=count, added=len(self.records) - before,
                                          total=len(self.records)))


def _compiled(rows, count, guard):
    """Both full and every one-forgotten map, on all 256 input masks."""
    full, forgotten = [0] * 256, [0] * 256

    def merge(row, target):
        image = [0] * 256
        for p in range(8):
            width = 1 << p
            for lower in range(width):
                image[width + lower] = image[lower] | row[p]
        for source, result in enumerate(image):
            target[source] |= 1 << result

    for row in rows:
        merge(row, full)
        guard.check()
    for erased in range(count):
        bit = 1 << erased
        for marks in range(1 << count):
            if not marks & bit:
                merge(tuple(a | b for a, b in zip(rows[marks], rows[marks | bit])), forgotten)
                guard.check()
    return tuple(full), tuple(forgotten)


class _Graph:
    def __init__(self, profiles, budget, guard, top_choices=None):
        self.profiles, self.k, self.guard = profiles, budget, guard
        self.S = profiles.prep.S
        block = profiles.blocks[self.S]
        if block["k"] != 3:
            raise ValueError("SELF boundary must have three formal ports")
        self.calls = [j for j, (c, _) in enumerate(block["calls"]) if c == self.S]
        self.operations, self.operation_index = [], {}
        self.middle = [[] for _ in self.calls]
        self.closing = []
        self.states, self.state_index, self.starts = [], {}, {}
        self.edges, self.close_cache = {}, {}
        self.edge_count = 0
        self.full_cache, self.forgot_cache = {}, {}
        self.subsets, self.subset_index, self.subset_edges, self.parents = [], {}, {}, {}
        self.accepted = []
        self.expanded = 0
        # Every side support reserves a distinct main port and target-own
        # variable outside that side subtree, hence at most k-2 marks.
        profiles.saturate(budget - 2)
        for label, flat_j in enumerate(self.calls):
            for count in range(budget - 1):
                for owned, children in profiles.selections(self.S, count, continued=flat_j):
                    number = self.add_operation(label, owned, children)
                    if number not in self.middle[label]:
                        self.middle[label].append(number)
        for count in range(1, budget):
            for owned, children in profiles.selections(self.S, count, own_min=1):
                number = self.add_operation(None, owned, children)
                if number not in self.closing:
                    self.closing.append(number)
        choices = top_choices if top_choices is not None else (
            selected for size in range(1, min(3, budget - 1) + 1)
            for selected in combinations(range(3), size))
        for top in choices:
            top = tuple(top)
            if not top or len(set(top)) != len(top) or any(j not in range(3) for j in top):
                raise ValueError("invalid distinct main-port selection")
            if len(top) >= budget:
                continue
            full = self.top_family(top)
            erased = 0
            for j in range(len(top)):
                erased |= self.top_family(top[:j] + top[j + 1:])
            state = self.intern((full, erased, len(top)))
            self.starts.setdefault(state, top)
        self.initial = self.intern_subset(frozenset(self.starts))

    @staticmethod
    def top_family(top):
        masks = []
        for word in range(1 << len(top)):
            masks.append(sum(1 << p for p in range(8)
                             if all(((p >> variable) & 1) == ((word >> bit) & 1)
                                    for bit, variable in enumerate(top))))
        return sum(1 << mask for mask in set(masks))

    def add_operation(self, label, owned, children):
        flat_j = None if label is None else self.calls[label]
        count, rows = self.profiles.compose_rows(self.S, owned, children, flat_j)
        full, forgotten = _compiled(rows, count, self.guard)
        key = (label, count, full, forgotten)
        if key in self.operation_index:
            return self.operation_index[key]
        self.guard.cap("operations", len(self.operations) + 1)
        number = len(self.operations)
        self.operation_index[key] = number
        self.operations.append(dict(continued=label, count=count, own=tuple(owned),
                                    children=tuple(children), full=full, forgotten=forgotten))
        return number

    def intern(self, state):
        if state in self.state_index:
            return self.state_index[state]
        self.guard.cap("nfa_states", len(self.states) + 1)
        number = len(self.states)
        self.state_index[state] = number
        self.states.append(state)
        return number

    def image(self, family, operation, erased=False):
        cache = self.forgot_cache if erased else self.full_cache
        key = (operation, family)
        if key in cache:
            return cache[key]
        table = self.operations[operation]["forgotten" if erased else "full"]
        answer = 0
        for port_mask in _set_bits(family):
            answer |= table[port_mask]
        if len(cache) >= self.guard.config["image_cache"]:
            cache.clear()
        cache[key] = answer
        return answer

    def apply(self, state, operation):
        full, erased, count = state
        return (self.image(full, operation),
                self.image(erased, operation) | self.image(full, operation, erased=True),
                count + self.operations[operation]["count"])

    def close(self, number):
        if number in self.close_cache:
            return self.close_cache[number]
        state = self.states[number]
        answer = None
        if not state[1] & 1:
            for operation in self.closing:
                size = state[2] + self.operations[operation]["count"]
                if not 3 <= size <= self.k:
                    continue
                full, erased, _ = self.apply(state, operation)
                # Output has zero ports: mask 0 means no extension and mask 1
                # means an extension.  K3 is checked separately from K1.
                if full & 1 and full & 2 and not erased & 1:
                    answer = operation
                    break
                self.guard.check()
        self.close_cache[number] = answer
        return answer

    def successors(self, number, label):
        key = (number, label)
        if key in self.edges:
            return self.edges[key]
        state = self.states[number]
        targets = {}
        for operation in self.middle[label]:
            if state[2] + self.operations[operation]["count"] >= self.k:
                continue
            target = self.apply(state, operation)
            # A missing assignment after a deletion can never be repaired by
            # adding constraints below the boundary.  Nor can an empty full
            # relation acquire an allowed state.  These are exact prunings.
            if target[1] & 1 or not target[0] & ~1:
                continue
            index = self.intern(target)
            if index not in targets:
                self.edge_count += 1
                self.guard.cap("nfa_edges", self.edge_count)
                targets[index] = operation
            self.guard.check()
        result = tuple(sorted(targets.items()))
        self.edges[key] = result
        return result

    def intern_subset(self, state, parent=None):
        if state in self.subset_index:
            return self.subset_index[state]
        self.guard.cap("subsets", len(self.subsets) + 1)
        number = len(self.subsets)
        self.subset_index[state] = number
        self.subsets.append(state)
        self.parents[number] = parent
        self.accepted.append(any(self.close(j) is not None for j in sorted(state)))
        return number

    def step(self, number, label):
        key = (number, label)
        if key in self.subset_edges:
            return self.subset_edges[key]
        self.guard.cap("subset_edges", len(self.subset_edges) + 1)
        target = frozenset(v for u in self.subsets[number] for v, _ in self.successors(u, label))
        result = self.intern_subset(target, (number, label))
        self.subset_edges[key] = result
        self.guard.check()
        return result

    def follow_recurring(self, word):
        prefix, cycle = list(word.get("prefix", ())), list(word.get("cycle", ()))
        if not cycle or any(type(j) is not int or not 0 <= j < len(self.calls) for j in prefix + cycle):
            raise ValueError("invalid recurring call word")
        nodes, labels, number = [self.initial], [], self.initial
        for label in prefix:
            number = self.step(number, label)
            labels.append(label)
            nodes.append(number)
        seen, phase = {}, 0
        while (number, phase) not in seen:
            seen[number, phase] = len(labels)
            label = cycle[phase]
            number = self.step(number, label)
            labels.append(label)
            nodes.append(number)
            phase = (phase + 1) % len(cycle)
        start = seen[number, phase]
        result = dict(preperiod=start, period=len(labels) - start,
                      cycle_acceptance=[self.accepted[j] for j in nodes[start:-1]])
        if all(result["cycle_acceptance"]):
            return (labels[:start], labels[start:], nodes), result
        return None, result

    def _accepting_cycle(self):
        """SCCs of the currently known accepting subset edges."""
        retained = {j for j, yes in enumerate(self.accepted) if yes}
        adjacency = {j: [] for j in retained}
        reverse = {j: [] for j in retained}
        for (u, label), v in self.subset_edges.items():
            if u in retained and v in retained:
                adjacency[u].append((v, label))
                reverse[v].append(u)
        seen, order = set(), []
        for root in sorted(retained):
            if root in seen:
                continue
            seen.add(root)
            stack = [(root, 0)]
            while stack:
                u, offset = stack[-1]
                if offset == len(adjacency[u]):
                    order.append(u)
                    stack.pop()
                    continue
                stack[-1] = (u, offset + 1)
                v = adjacency[u][offset][0]
                if v not in seen:
                    seen.add(v)
                    stack.append((v, 0))
                self.guard.check()
        seen.clear()
        for root in reversed(order):
            if root in seen:
                continue
            component, stack = set(), [root]
            seen.add(root)
            while stack:
                u = stack.pop()
                component.add(u)
                for v in reverse[u]:
                    if v not in seen:
                        seen.add(v)
                        stack.append(v)
            for u in sorted(component):
                for v, label in adjacency[u]:
                    if v not in component:
                        continue
                    if u == v:
                        return u, [label]
                    # Any edge inside a nontrivial SCC closes to a concrete
                    # cycle.  All its vertices have passed acceptance.
                    parents, pending = {v: None}, deque([v])
                    while pending and u not in parents:
                        x = pending.popleft()
                        for y, edge_label in adjacency[x]:
                            if y in component and y not in parents:
                                parents[y] = (x, edge_label)
                                pending.append(y)
                    if u in parents:
                        back, x = [], u
                        while x != v:
                            x, edge_label = parents[x]
                            back.append(edge_label)
                        return u, [label] + list(reversed(back))
        return None

    def general(self):
        cursor = 0
        while cursor < len(self.subsets):
            for label in range(len(self.calls)):
                self.step(cursor, label)
            cursor += 1
            self.expanded = cursor
            if cursor % 16 == 0 or cursor == len(self.subsets):
                cycle = self._accepting_cycle()
                if cycle is not None:
                    start, cycle_labels = cycle
                    prefix, u = [], start
                    while self.parents[u] is not None:
                        u, label = self.parents[u]
                        prefix.append(label)
                    prefix.reverse()
                    nodes, u = [self.initial], self.initial
                    for label in prefix + cycle_labels:
                        u = self.step(u, label)
                        nodes.append(u)
                    return prefix, cycle_labels, nodes
            self.guard.check()
        return None

    def metrics(self):
        return dict(profiles=len(self.profiles.records), marked_closure=self.profiles.round_counts,
                    compositions=self.profiles.compositions, operations=len(self.operations),
                    nfa_states=len(self.states), nfa_edges=self.edge_count,
                    subsets=len(self.subsets), subset_edges=len(self.subset_edges),
                    expanded_subsets=self.expanded)

    def certificate(self, lasso):
        prefix, cycle, nodes = lasso
        if not cycle or nodes[-1] != nodes[len(prefix)]:
            raise AssertionError("lasso does not return to its starting subset")
        if not all(self.accepted[j] for j in nodes[len(prefix):-1]):
            raise AssertionError("lasso contains a nonaccepting cycle step")
        bad = [depth for depth, node in enumerate(nodes[:-1]) if not self.accepted[node]]
        onset = max(1, (max(bad) + 1) if bad else 1)
        retained_edges, states, operations, closing = {}, set(), set(), {}
        for phase, (node, label) in enumerate(zip(nodes, prefix + cycle)):
            states.update(self.subsets[node])
            for source in self.subsets[node]:
                arcs = self.successors(source, label)
                retained_edges[source, label] = arcs
                operations.update(operation for _, operation in arcs)
            accepted = next((state for state in sorted(self.subsets[node])
                             if self.close(state) is not None), None)
            if accepted is not None:
                operation = self.close(accepted)
                closing[accepted] = operation
                operations.add(operation)
        states.update(self.subsets[nodes[-1]])
        profiles, pending = set(), [child for op in operations
                                   for child in self.operations[op]["children"] if child >= 0]
        while pending:
            number = pending.pop()
            if number in profiles:
                continue
            profiles.add(number)
            pending.extend(self.profiles.records[number]["children"] or ())
        block = self.profiles.blocks[self.S]
        identity, depth, phase, seen = (0, 1, 2), 0, 0, {}
        for label in prefix:
            args = block["calls"][self.calls[label]][1]
            identity = tuple(identity[a] if a < 3 else None for a in args)
            depth += 1
        while (identity, phase) not in seen:
            seen[identity, phase] = depth
            label = cycle[phase]
            args = block["calls"][self.calls[label]][1]
            identity = tuple(identity[a] if a < 3 else None for a in args)
            phase, depth = (phase + 1) % len(cycle), depth + 1
        carried = sorted({x for x in identity if x is not None})
        return dict(
            schema_version=1, method="exact marked-table saturation and labelled subset graph",
            k=self.k, onset=onset, prefix=list(prefix), cycle=list(cycle),
            path=dict(prefix=list(prefix), cycle=list(cycle)),
            main=self.profiles.prep.main, S=self.S, entry=None,
            depth_convention="root S at depth 0; one SELF call increases depth by one",
            side_profile_marks=self.k - 2,
            carried_top_ports=carried, carried=bool(carried),
            carried_meaning="top identities present in every sufficiently deep target port tuple",
            self_calls=[dict(call_index=i, flat_call_index=j,
                             arguments=list(block["calls"][j][1])) for i, j in enumerate(self.calls)],
            automaton=dict(
                starts=[dict(state=s, top_ports=list(top)) for s, top in sorted(self.starts.items())],
                states={str(s): [hex(self.states[s][0]), hex(self.states[s][1]), self.states[s][2]]
                        for s in sorted(states)},
                edges=[dict(source=s, call=label, target=t, operation=op)
                       for (s, label), arcs in sorted(retained_edges.items()) for t, op in arcs],
                closing={str(s): op for s, op in sorted(closing.items())},
                subsets=[sorted(self.subsets[j]) for j in nodes],
                cycle_start=len(prefix),
                acceptance=[self.accepted[j] for j in nodes],
                operations={str(op): {key: (list(value) if isinstance(value, tuple) else value)
                                     for key, value in self.operations[op].items()
                                     if key not in ("full", "forgotten")}
                            for op in sorted(operations)},
                profiles={str(p): {key: (hex(value) if key == "relation" else
                                        list(value) if isinstance(value, tuple) else value)
                                   for key, value in self.profiles.records[p].items()}
                          for p in sorted(profiles)}),
            witness_schema="choose an accepting NFA run for each path prefix; attach operation/profile own marks at their introduction copies",
            search=self.metrics())


def search(prep, recurring_word=None, checkpoint=lambda: None, limits=None):
    """Return an exact positive certificate, or explicit completed/capped attempts.

    A nonholding main's target-depth convention is ambiguous in the frozen
    specification.  Only that affected part is skipped, as instructed.
    """
    guard = _Guard(checkpoint, limits)
    result = dict(certificate=None, attempts=[], reason=None,
                  metadata=dict(limits=guard.config, exact=True, budgets=[3, 4, 5],
                                incomplete_search_is_not_negative=True))
    if prep.S is None:
        result["reason"] = "no certificate at k <= 5"
        result["metadata"]["detail"] = "no SELF-holding target type"
        return result
    if prep.main != prep.S:
        result["reason"] = "ambiguity"
        result["metadata"]["detail"] = (
            "main != S: depth through flattened entry versus original derivation depth is unspecified; "
            "only bounded certificates are skipped")
        return result
    profiles = None
    try:
        guard.check(force=True)
        profiles = _Profiles(prep, guard)
        for budget in (3, 4, 5):
            attempt = dict(k=budget, status="running")
            result["attempts"].append(attempt)
            graph = None
            try:
                graph = _Graph(profiles, budget, guard)
                lasso = None
                if recurring_word is not None:
                    lasso, attempt["recurring_word_search"] = graph.follow_recurring(recurring_word)
                if lasso is None:
                    lasso = graph.general()
                if lasso is not None:
                    result["certificate"] = graph.certificate(lasso)
                    attempt.update(status="certified", metadata=graph.metrics())
                    result["reason"] = None
                    break
                attempt.update(status="complete_no_certificate", metadata=graph.metrics())
            except Exception as error:
                reason = getattr(error, "reason", None)
                if reason not in ("cap", "memory"):
                    raise
                attempt.update(status=reason, detail=str(error))
                if graph is not None:
                    attempt["metadata"] = graph.metrics()
                else:
                    attempt["metadata"] = dict(profiles=len(profiles.records),
                                               completed_side_marks=profiles.completed_marks,
                                               compositions=profiles.compositions)
                # Larger budgets need this same exact marked-table closure.
                # If it did not close, repeating it cannot make that prerequisite
                # complete.  Preserve the not-attempted budgets explicitly.
                if profiles.completed_marks < budget - 2 or reason == "memory":
                    for later in range(budget + 1, 6):
                        result["attempts"].append(dict(k=later, status=reason,
                            detail="not attempted: the required smaller marked-table closure did not complete"))
                    break
                # A shared time ceiling also prevents useful later attempts.
                guard.check(force=True)
        if result["certificate"] is None:
            reasons = [x["status"] for x in result["attempts"]]
            result["reason"] = "memory" if "memory" in reasons else "cap" if "cap" in reasons else "no certificate at k <= 5"
    except Exception as error:
        reason = getattr(error, "reason", None)
        if reason not in ("cap", "memory"):
            raise
        result["reason"] = reason
        result["metadata"]["detail"] = str(error)
        attempted = {x["k"] for x in result["attempts"]}
        for budget in (3, 4, 5):
            if budget not in attempted:
                result["attempts"].append(dict(k=budget, status=reason, detail="shared resource ceiling"))
    result["metadata"].update(seconds=round(time.monotonic() - guard.started, 6),
                               peak_memory_bytes=guard.peak,
                               profiles=0 if profiles is None else len(profiles.records))
    return result


def control_fixtures():
    """Repository-derived strict-NAE controls; no population inputs are read."""
    class Prep:
        def __init__(self, knots, calls):
            self.S = self.main = 0
            self.holding, self.own, self.k, self.alive = {0}, [1], 3, True
            self.G = {0: [True] * 8}
            self._flat = dict(k=3, V=4, calls=[("K", tuple(k)) for k in knots] + [(0, tuple(a)) for a in calls])

        def flat(self, typ):
            if typ != 0:
                raise ValueError("control has one type")
            return self._flat

        def blocks(self, ray="first"):
            indices = [j for j, (c, _) in enumerate(self._flat["calls"]) if c == 0]
            j = indices[0 if ray == "first" else -1]
            return self._flat, self._flat, j, j

    return {
        "persistent": dict(prep=Prep(((0, 2, 3),), ((0, 1, 3),)), word=dict(prefix=[], cycle=[0])),
        "repeated_port_identity": dict(prep=Prep(((0, 2, 3),), ((0, 0, 3),)), word=dict(prefix=[], cycle=[0])),
        # With top port 0 selected, a bond must inspect the second child's
        # own variable: its local NAE is (top0, target-own, side-own).
        "carried_top_with_side_member": dict(prep=Prep(((1, 2, 3),), ((0, 1, 3), (1, 0, 3))),
                                             word=dict(prefix=[], cycle=[0]), top_choices=((0,),)),
    }


def controls(checkpoint=lambda: None, limits=None):
    """Executable positive controls, including direct independent SAT replay."""
    import witness_check
    results = {}
    for name, fixture in control_fixtures().items():
        guard = _Guard(checkpoint, limits)
        profiles = _Profiles(fixture["prep"], guard)
        graph = _Graph(profiles, 3, guard, top_choices=fixture.get("top_choices"))
        lasso, orbit = graph.follow_recurring(fixture["word"])
        if lasso is None:
            results[name] = dict(passed=False, detail="positive control has no accepting lasso", orbit=orbit)
            continue
        certificate = graph.certificate(lasso)
        replay = witness_check.check(fixture["prep"], certificate, checkpoint=checkpoint, limits=limits)
        passed = replay["passed"]
        if name == "carried_top_with_side_member":
            passed = passed and all(row.get("uses_side_member") and row.get("uses_carried_top")
                                    for row in replay.get("depths", []))
        results[name] = dict(passed=bool(passed), certificate=certificate, replay=replay)
    return dict(passed=all(row["passed"] for row in results.values()), controls=results)
