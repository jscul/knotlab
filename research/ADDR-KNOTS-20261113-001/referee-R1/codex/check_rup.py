"""Solver-independent DRUP checker using watched-literal unit propagation.

Deletions are ignored deliberately: keeping earlier, already proved clauses is
sound. Only RUP additions are accepted, not the more general RAT rule.
"""
from __future__ import annotations

import gzip
import json
import sys
from collections import defaultdict
from pathlib import Path


class RUPChecker:
    def __init__(self, original, nvars):
        self.clauses = []
        self.watch = defaultdict(list)
        self.units = []
        self.values = [0] * (nvars + 1)
        self.trail = []
        self.initial_empty = False
        for clause in original:
            self.add(clause)

    def add(self, clause):
        clause = list(dict.fromkeys(clause))
        if not clause:
            self.initial_empty = True
        elif len(clause) == 1:
            self.units.append(clause[0])
        else:
            index = len(self.clauses)
            self.clauses.append(clause)
            self.watch[clause[0]].append(index)
            self.watch[clause[1]].append(index)

    def value(self, literal):
        v = self.values[abs(literal)]
        return v if literal > 0 else -v

    def assign(self, literal):
        v = self.value(literal)
        if v:
            return v > 0
        self.values[abs(literal)] = 1 if literal > 0 else -1
        self.trail.append(literal)
        return True

    def contradiction(self, assumptions):
        for v in self.trail:
            self.values[abs(v)] = 0
        self.trail.clear()
        if self.initial_empty:
            return True
        for literal in self.units:
            if not self.assign(literal):
                return True
        for literal in assumptions:
            if not self.assign(literal):
                return True
        cursor = 0
        while cursor < len(self.trail):
            false_lit = -self.trail[cursor]
            cursor += 1
            bucket = self.watch[false_lit]
            position = 0
            while position < len(bucket):
                clause = self.clauses[bucket[position]]
                if clause[0] == false_lit:
                    clause[0], clause[1] = clause[1], clause[0]
                assert clause[1] == false_lit
                other = clause[0]
                if self.value(other) > 0:
                    position += 1
                    continue
                replacement = None
                for k in range(2, len(clause)):
                    if self.value(clause[k]) >= 0:
                        replacement = k
                        break
                if replacement is not None:
                    clause[1], clause[replacement] = clause[replacement], clause[1]
                    self.watch[clause[1]].append(bucket[position])
                    bucket[position] = bucket[-1]
                    bucket.pop()
                else:
                    if not self.assign(other):
                        return True
                    position += 1
        return False

    def check(self, lines):
        additions = deletions = 0
        for line_number, line in enumerate(lines, 1):
            line = line.strip()
            if not line or line.startswith('c'):
                continue
            if line.startswith('d '):
                deletions += 1
                continue
            numbers = list(map(int, line.split()))
            if not numbers or numbers[-1] != 0 or 0 in numbers[:-1]:
                return {'valid': False, 'line': line_number, 'reason': 'malformed clause'}
            clause = numbers[:-1]
            if any(abs(v) >= len(self.values) for v in clause):
                return {'valid': False, 'line': line_number, 'reason': 'new variable'}
            if not self.contradiction([-v for v in clause]):
                return {'valid': False, 'line': line_number, 'reason': 'addition is not RUP'}
            additions += 1
            if not clause:
                return {'valid': True, 'additions': additions, 'ignored_deletions': deletions,
                        'empty_clause_line': line_number}
            self.add(clause)
        return {'valid': False, 'reason': 'no derived empty clause', 'additions': additions}


def read_dimacs(path):
    clauses = []
    pending = []
    nvars = None
    opener = gzip.open if str(path).endswith('.gz') else open
    with opener(path, 'rt') as handle:
        for line in handle:
            if line.startswith('c'):
                continue
            if line.startswith('p'):
                _, _, count, expected = line.split()
                nvars = int(count)
                continue
            for v in map(int, line.split()):
                if v == 0:
                    clauses.append(pending)
                    pending = []
                else:
                    pending.append(v)
    assert not pending and nvars is not None and len(clauses) == int(expected)
    return nvars, clauses


if __name__ == '__main__':
    count, original = read_dimacs(Path(sys.argv[1]))
    proof = Path(sys.argv[2])
    opener = gzip.open if proof.suffix == '.gz' else open
    with opener(proof, 'rt') as stream:
        result = RUPChecker(original, count).check(stream)
    print(json.dumps(result, sort_keys=True))
    raise SystemExit(0 if result['valid'] else 1)
