"""Independent TOP-INFO R1 finite-relation and whole-main-block audit.

Reuses only permitted earlier referee semantics and SAT projection helpers.
No TOP producer Python is opened or imported. The new transfer is derived
from the mathematical cut: retain every main distinction in its row index,
retain occurrence identity in its partition, and eliminate intermediate
blocks. Explicit unfolding below does not use these transfer relations.
"""
from __future__ import annotations

import gzip
import hashlib
import importlib.util
import itertools
import json
import os
from pathlib import Path
import resource
import time

for _v in ("OMP_NUM_THREADS", "OPENBLAS_NUM_THREADS", "MKL_NUM_THREADS"):
    os.environ[_v] = "1"

ROOT = Path('/home/jscul/p-vs-np-contact-first')
HERE = ROOT / 'research/TOP-INFO-20261114-001/referee-R1/codex'
EARLIER = ROOT / 'research/CARRY-BOUND-20261114-001/referee-R1/codex/window_audit.py'
_spec = importlib.util.spec_from_file_location('earlier_carry_referee_window', EARLIER)
old = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(old)
from pysat.solvers import Solver

READS = {str(EARLIER.relative_to(ROOT)): hashlib.sha256(EARLIER.read_bytes()).hexdigest()}


def read_json(path):
    path = ROOT / path
    assert path.suffix != '.py'
    raw = path.read_bytes()
    READS[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return json.loads(raw)


def read_jsonl(path):
    path = ROOT / path
    assert path.suffix != '.py'
    raw = path.read_bytes()
    READS[str(path.relative_to(ROOT))] = hashlib.sha256(raw).hexdigest()
    if path.suffix == '.gz':
        raw = gzip.decompress(raw)
    return [json.loads(line) for line in raw.splitlines() if line.strip()]


def project_mask(allowed, positions):
    result = 0
    while allowed:
        bit = allowed & -allowed
        allowed ^= bit
        state = bit.bit_length() - 1
        result |= 1 << old.project(state, positions)
    return result


class Relation:
    def __init__(self, labels, allowed):
        self.labels = tuple(labels)
        self.allowed = allowed
        self.n = len(labels)
        self.universe = (1 << (1 << self.n)) - 1
        self.positive = []
        # Repeating bit runs avoid enumerating all assignments per literal.
        for j in range(self.n):
            run = 1 << j
            mask = 0
            unit = (1 << run) - 1
            for offset in range(run, 1 << self.n, 2 * run):
                mask |= unit << offset
            self.positive.append(mask)
        self.cache = {}

    def shattered(self, support):
        support = tuple(sorted(support))
        if support in self.cache:
            return self.cache[support]
        portions = [self.allowed]
        for j in support:
            positive = self.positive[j]
            negative = self.universe ^ positive
            split = []
            for rows in portions:
                a, b = rows & positive, rows & negative
                if not a or not b:
                    self.cache[support] = False
                    return False
                split.extend((a, b))
            portions = split
        answer = bool(self.allowed)
        self.cache[support] = answer
        return answer

    def least_bond(self, roots, target, max_size=6):
        roots, target = set(roots), set(target)
        for size in range(2, min(max_size, self.n) + 1):
            for support in itertools.combinations(range(self.n), size):
                if not roots.intersection(support) or not target.intersection(support):
                    continue
                if self.shattered(support):
                    continue
                if all(self.shattered(support[:j] + support[j + 1:]) for j in range(size)):
                    return {'size': size, 'support': [self.labels[j] for j in support]}
        return {'size': None, 'support': []}

    def pinning(self, roots, target):
        roots, target = tuple(sorted(roots)), tuple(sorted(target))
        union = tuple(sorted(set(roots) | set(target)))
        joint = project_mask(self.allowed, union).bit_count()
        left = project_mask(self.allowed, roots).bit_count()
        right = project_mask(self.allowed, target).bit_count()
        assert not set(roots).intersection(target), 'pinning sides must be distinct identities'
        plain = joint != left * right
        # A cross bond is equivalent to the shattered-side predicate: its
        # intersections with each side are proper subsets and hence full.
        witness = None
        if plain:
            for size in range(2, len(union) + 1):
                for support in itertools.combinations(union, size):
                    if not set(support).intersection(roots) or not set(support).intersection(target):
                        continue
                    if self.shattered(support):
                        continue
                    if all(self.shattered(support[:j] + support[j + 1:]) for j in range(size)):
                        witness = {'size': size, 'T': [self.labels[j] for j in support if j in roots],
                                   'D': [self.labels[j] for j in support if j in target]}
                        break
                if witness:
                    break
        return {'plain_pinned': plain, 'bond_pinned': witness is not None,
                'joint_count': joint, 'left_count': left, 'right_count': right,
                'witness': witness}


def orbit(window, max_levels=2000, max_stored=200000):
    current = dict(window.starts)
    seen, levels = {}, []
    stored = 0
    while True:
        frozen = frozenset(current)
        if frozen in seen:
            pre = seen[frozen]
            return {'preperiod': pre, 'period': len(levels) - pre,
                    'repeat_at': len(levels), 'levels': levels, 'stored_states': stored}
        if len(levels) >= max_levels or stored + len(current) > max_stored:
            raise ValueError('referee orbit cap')
        seen[frozen] = len(levels)
        levels.append(dict(current))
        stored += len(current)
        nxt = {}
        for q, (entry, word) in current.items():
            for label in range(len(window.generators)):
                following = window.step(q, label)
                nxt.setdefault(following, (entry, word + (label,)))
        current = nxt


class WholeMain:
    def __init__(self, raw, S):
        self.one = old.Window(raw, S)
        for name in ('defs', 'G', 'types', 'S', 'main', 'km', 'wrapper', 'flat',
                     'size', 'calls', 'own', 'child_indices', 'generators', 'good'):
            setattr(self, name, getattr(self.one, name))
        self.main_size, self.main_calls = self.flat[self.main]
        self.width = self.main_size
        self.starts = {}
        for entry, (callee, arguments) in enumerate(self.main_calls):
            if callee != S:
                continue
            J = 0
            for assignment in old.block_states(self.main_size, self.main_calls, self.G, entry):
                J |= 1 << (8 * assignment + old.project(assignment, arguments))
            partition = old.canonical(tuple(range(self.width)) + arguments)
            # For main=S this starts at word length one, after its first call.
            word = () if self.wrapper else (self.child_indices.index(entry),)
            self.starts[(J, partition)] = (entry if self.wrapper else None, word)
        assert self.starts
        self.start_depth = int(not self.wrapper)
        self.relations, self.bonds = {}, {}

    def step(self, q, label):
        J, partition = q
        args = self.calls[self.child_indices[label]][1]
        previous_roots = [('old', j) for j in range(self.width)]
        child = [('old', partition[self.width + a]) if a < 3 else ('fresh', a)
                 for a in args]
        return (old.compose(J, self.generators[label], 1 << self.width),
                old.canonical(previous_roots + child))

    def relation(self, q):
        if q in self.relations:
            return self.relations[q]
        J, partition = q
        own_labels = tuple(range(self.width + 3, self.width + self.size))
        labels = tuple(sorted(set(partition) | set(own_labels)))
        positions = {label: j for j, label in enumerate(labels)}
        allowed = 0
        for assignment in self.good:
            port = assignment & 7
            for a in range(1 << self.width):
                if not (J >> (8 * a + port)) & 1:
                    continue
                values = {j: (a >> j) & 1 for j in range(self.width)}
                valid = True
                for j in range(3):
                    label, value = partition[self.width + j], (port >> j) & 1
                    if label in values and values[label] != value:
                        valid = False
                        break
                    values[label] = value
                if not valid:
                    continue
                values.update({label: (assignment >> (3 + j)) & 1
                               for j, label in enumerate(own_labels)})
                allowed |= 1 << sum(values[label] << positions[label] for label in labels)
        assert allowed
        self.relations[q] = (labels, allowed)
        return labels, allowed

    def least_bond(self, q):
        if q not in self.bonds:
            labels, allowed = self.relation(q)
            rel = Relation(labels, allowed)
            roots = [j for j, x in enumerate(labels) if x < self.km]
            target = [j for j, x in enumerate(labels) if x >= self.width + 3]
            self.bonds[q] = rel.least_bond(roots, target)
        return self.bonds[q]

    def mapping(self, q, target):
        partition = q[1]
        mapping = {j: j for j in range(self.width)}
        for j in range(3):
            label = partition[self.width + j]
            if label in mapping:
                assert mapping[label] == target[j]
            mapping[label] = target[j]
        mapping.update({self.width + j: target[j] for j in range(3, self.size)})
        assert len(set(mapping.values())) == len(mapping)
        return mapping


class Unfold:
    """Raw-block CNF with all or selected S descendants and exact boundary.

    No port-to-port generator or transfer composition is used in this class.
    IDs refer to unique distinctions, including carried main-own arguments.
    """
    def __init__(self, w, entry, word, explicit=False, max_vars=15000, max_copies=25000):
        self.w, self.n = w, w.km
        self.clauses, self.copies, self.origins = [], [], {}
        self.target = None
        word = tuple(word)
        cutoff = len(word) + 1

        def visit(which, actual, address, direct_entry=None, is_main=False):
            size, calls = w.flat[which]
            arity = w.defs[which][0]
            own = tuple(range(self.n, self.n + size - arity))
            self.n += len(own)
            env = tuple(actual) + own
            if self.n > max_vars or len(self.copies) >= max_copies:
                raise ValueError('explicit unfolding cap')
            copy = {'definition': which, 'word': list(address), 'entry': direct_entry,
                    'absolute_depth': 0 if is_main else len(address) + int(w.wrapper),
                    'ports': list(actual), 'own': list(own)}
            self.copies.append(copy)
            for v in own:
                self.origins[v] = {k: copy[k] for k in ('definition', 'word', 'entry', 'absolute_depth')}
            if is_main:
                self.main_env = env
            if which == w.S and direct_entry == entry and address == word:
                self.target = env
            for j, (c, args) in enumerate(calls):
                a = tuple(env[x] for x in args)
                descend = False
                child_word, child_entry = address, direct_entry
                if c == w.S:
                    if is_main and w.wrapper:
                        child_word, child_entry = (), j
                        descend = explicit or j == entry
                    else:
                        label = w.child_indices.index(j)
                        child_word = address + (label,)
                        descend = len(child_word) <= cutoff if explicit else (
                            direct_entry == entry and word[:len(child_word)] == child_word)
                if descend:
                    visit(c, a, child_word, child_entry)
                else:
                    mask = 0x7e if c == 'K' else w.G[c]
                    self.clauses.extend(old.clauses_for_relation(a, mask))
            return env

        visit(w.main, tuple(range(w.km)), (), None, True)
        assert self.target is not None
        assert self.main_env == tuple(range(w.main_size))


def direct_check(w, q, path, witness=None, explicit=False, compare=True):
    entry, word = path
    direct = Unfold(w, entry, word, explicit=explicit)
    mapping = w.mapping(q, direct.target)
    labels, expected = w.relation(q)
    with Solver(name='cadical195', bootstrap_with=direct.clauses) as solver:
        assert solver.solve()
        if compare:
            projected = old.sat_projection(solver, tuple(mapping[x] for x in labels))
            assert projected == expected, 'whole-main window differs from explicit raw-block CNF'
        bond = old.verify_bond(solver, tuple(mapping[x] for x in witness)) if witness else None
    return {'entry': entry, 'word': list(word), 'word_depth': len(word),
            'absolute_depth': len(word) + int(w.wrapper), 'explicit_all_copies': explicit,
            'variables': direct.n, 'clauses': len(direct.clauses), 'copies': len(direct.copies),
            'window_labels': list(labels), 'window_actual_ids': [mapping[x] for x in labels],
            'window_allowed_count': expected.bit_count(),
            'full_projection_assignments': (1 << len(labels)) if compare else 0,
            'projection_equal': True if compare else None, 'bond': bond,
            'bond_origins': [direct.origins.get(mapping[x], {'main_port': mapping[x]}) for x in witness]
                            if witness else []}
