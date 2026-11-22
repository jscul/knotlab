"""Paired source weighting, one-token edits and exact founder admission."""

from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from hashlib import sha256
from heapq import heapify, heappop, heappush
from itertools import combinations, permutations, product
import json
from pathlib import Path
import sys

from pysat.solvers import Minisat22


ROOT = Path(__file__).resolve().parents[3]
GENERATORS = (ROOT / "experiments/GENERATORS-20261120-001A/"
              "GENERATORS-20261120-001A-E001_generators")
sys.path.insert(0, str(GENERATORS))
from fixtures import (canonical_relation, expected_words, nae_add, nae_words,
                      parity_words, source_from)
from knotlab.knots import check_knot
from knotlab.relations import Relation


@dataclass(frozen=True)
class Proposal:
    prufer: tuple[int, ...]
    extra: tuple[int, int] | None
    spare: tuple[int, ...]

    def record(self):
        return asdict(self)

    @classmethod
    def from_record(cls, record):
        extra = record["extra"]
        return cls(tuple(record["prufer"]), None if extra is None else tuple(extra), tuple(record["spare"]))


@dataclass(frozen=True)
class Start:
    meetings: tuple[tuple[int, int], ...]
    loose: tuple[int, ...]

    @property
    def stars(self):
        return source_from(self.meetings, self.loose)


def tree_of(prufer):
    n = len(prufer) + 2
    degree = [1] * n
    for knot in prufer:
        degree[knot] += 1
    leaves = [k for k, d in enumerate(degree) if d == 1]
    heapify(leaves)
    meetings = []
    for knot in prufer:
        meetings.append(tuple(sorted((heappop(leaves), knot))))
        degree[knot] -= 1
        if degree[knot] == 1:
            heappush(leaves, knot)
    meetings.append((heappop(leaves), heappop(leaves)))
    return tuple(sorted(meetings))


def missing_pairs(n, tree):
    return tuple(pair for pair in combinations(range(n), 2) if pair not in tree)


def independent_proposal(rng, sizes=(4, 5, 6)):
    n = rng.choice(sizes)
    prufer = tuple(rng.randrange(n) for _ in range(n - 2))
    extra = rng.choice(missing_pairs(n, tree_of(prufer))) if rng.randrange(2) else None
    return Proposal(prufer, extra, tuple(rng.randrange(2) for _ in range(n)))


def change_item(values, where, replacement):
    return values[:where] + (replacement,) + values[where + 1:]


def other_label(rng, old, n):
    index = rng.randrange(n - 1)
    return index + (index >= old)


def mutate(proposal, rng):
    """Choose one of three edit classes uniformly and edit one supplied token."""
    n = len(proposal.spare)
    edit = rng.randrange(3)
    if edit == 0:
        j = rng.randrange(n - 2)
        prufer = change_item(proposal.prufer, j, other_label(rng, proposal.prufer[j], n))
        return Proposal(prufer, proposal.extra, proposal.spare), "prufer"
    if edit == 1:
        alternatives = (None,) + missing_pairs(n, tree_of(proposal.prufer))
        extra = rng.choice(tuple(pair for pair in alternatives if pair != proposal.extra))
        return Proposal(proposal.prufer, extra, proposal.spare), "extra"
    j = rng.randrange(n)
    spare = change_item(proposal.spare, j, 1 - proposal.spare[j])
    return Proposal(proposal.prufer, proposal.extra, spare), "spare"


def decode(proposal):
    tree = tree_of(proposal.prufer)
    if proposal.extra in tree:
        return None
    meetings = tree if proposal.extra is None else tuple(sorted((*tree, proposal.extra)))
    degrees = Counter(knot for pair in meetings for knot in pair)
    loose = tuple(max(0, 3 - degrees[knot]) + spare for knot, spare in enumerate(proposal.spare))
    return Start(meetings, loose)


def founder_code(start):
    """Exact encoding up to founder renaming, with open counts as labels.

    Any isomorphism preserves degree and open count. Place these type classes
    in sorted order, and minimize meeting incidence over orders within each
    type class. Equal encodings give an isomorphism by aligning minimizers.
    One open distinction per place and one shared distinction per listed
    meeting gives a unique presentation up to distinction renaming as well.
    """
    n = len(start.loose)
    meetings = set(start.meetings)
    degrees = Counter(knot for pair in meetings for knot in pair)
    by_type = defaultdict(list)
    for knot, supply in enumerate(start.loose):
        by_type[(degrees[knot], supply)].append(knot)
    types = sorted(by_type)
    loose = tuple(supply for degree, supply in types for _ in by_type[(degree, supply)])
    pairs = tuple(combinations(range(n), 2))
    least = (1 << len(pairs)) - 1
    for blocks in product(*(tuple(permutations(by_type[kind])) for kind in types)):
        order = tuple(knot for block in blocks for knot in block)
        bits = sum(1 << j for j, (a, b) in enumerate(pairs)
                   if (min(order[a], order[b]), max(order[a], order[b])) in meetings)
        least = min(least, bits)
    return json.dumps((n, loose, least), separators=(",", ":"))


def partition(code):
    digest = sha256(("GROWTH-STATISTICS-20261121-001B/founders/v1:" + code).encode()).digest()
    bucket = int.from_bytes(digest, "big") % 5
    return ("development", "search", "search", "search", "validation")[bucket]


def warm_laws():
    """Check immutable truth tables through the same canonical K1–K3 API."""
    summary = {}
    for law in ("parity", "nae"):
        for size in range(3, 7):
            words = expected_words(law, size)
            if size <= 5:
                canonical_relation(law, size)
            else:
                names = tuple(map(str, range(size)))
                rows = frozenset(tuple(bool(w >> j & 1) for j in range(size)) for w in words)
                if not check_knot(Relation(names, rows), names[:-1], names[-1]).is_knot:
                    raise ValueError(f"canonical knot test failed for {law}/{size}")
            summary[f"{law}/{size}"] = len(words)
    return summary


def certify(stars):
    """Check the actual projected words at every founder, even spent ones."""
    if min(map(len, stars)) < 3 or len(set(map(frozenset, stars))) != len(stars):
        raise ValueError("invalid founder shape in source generator")
    projected_sizes = {"parity": [], "nae": []}
    failures = []
    with Minisat22() as solver:
        for row in stars:
            nae_add(solver, row)
        for knot, row in enumerate(stars):
            observed = {"parity": parity_words(stars, row), "nae": nae_words(solver, row)}
            for law, words in observed.items():
                projected_sizes[law].append(len(words))
                if words != expected_words(law, len(row)):
                    failures.append([law, knot])
    return {"projected_sizes": projected_sizes, "failures": failures,
            "nae_projection_queries": sum(1 << len(row) for row in stars)}
