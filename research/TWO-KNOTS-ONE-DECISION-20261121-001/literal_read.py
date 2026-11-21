"""Exact centralized resolve-on-read comparison and private transcript laws.

A holder index is its position in the supplied catalogue. Bits in each
answer mask follow that holder's supplied mark order. The two readers share
one eligible union draw and retain only their own last successful answers.
"""

from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from fractions import Fraction
from itertools import product
from typing import NamedTuple


Request = int | None
Memory = tuple[int, int] | None
State = tuple[Memory, Memory]
Transition = tuple[int | None, int | None, Fraction, State]


class Readout(NamedTuple):
    """One reader's addressed request, receipt status and recorded answer."""

    request: Request
    status: str
    answer: int | None


Transcript = tuple[Readout, ...]
Policy = Sequence[Request] | Callable[[Transcript], Request]
Candidate = tuple[int | None, int | None, int]


class LiteralReader:
    def __init__(self, holdings: Sequence[Sequence[int]], allowed: Sequence[Iterable[int]], bias=False):
        self.holdings = tuple(tuple(holder) for holder in holdings)
        allowed_words = tuple(tuple(words) for words in allowed)
        if len(self.holdings) != len(allowed_words):
            raise ValueError("each holder must have one relation")
        for marks, words in zip(self.holdings, allowed_words, strict=True):
            if any(type(mark) is not int for mark in marks) or len(set(marks)) != len(marks):
                raise ValueError("a holder must contain distinct integer mark names")
            if any(type(word) is not int or word < 0 or word >= 1 << len(marks) for word in words):
                raise ValueError("an allowed answer must be an integer mask in its holder's listed order")
        self.allowed = tuple(tuple(sorted(set(words))) for words in allowed_words)
        self.bias = bool(bias)

        roster = sorted({mark for marks in self.holdings for mark in marks})
        bits = {mark: 1 << i for i, mark in enumerate(roster)}
        assignments = [tuple(bits[mark] for mark in marks) for marks in self.holdings]
        self._supports = tuple(sum(row) for row in assignments)
        self._embeddings = tuple(
            {word: sum(bit for j, bit in enumerate(row) if word >> j & 1) for word in words}
            for row, words in zip(assignments, self.allowed, strict=True)
        )
        self._pool_cache = {}
        self._transition_cache = {}

    @staticmethod
    def start() -> State:
        """Both readers are ready and neither has a previous answer."""
        return None, None

    def _address(self, request: Request) -> Request:
        if type(request) is int and 0 <= request < len(self.holdings):
            return request
        return None

    def readout(self, request: Request, answer: int | None) -> Readout:
        if request is None:
            status = "idle"
        elif self._address(request) is None:
            status = "invalid_address"
        elif answer is None:
            status = "no_eligible_union"
        else:
            status = "success"
        return Readout(request, status, answer)

    def _pool(self, holder: Request, prior: Memory):
        if holder is None:
            return ((None, 0),)
        key = holder, prior
        if key not in self._pool_cache:
            if prior is None:
                shared, known = 0, 0
            else:
                old_holder, old_answer = prior
                shared = self._supports[holder] & self._supports[old_holder]
                known = self._embeddings[old_holder][old_answer]
            self._pool_cache[key] = tuple((word, named) for word, named in self._embeddings[holder].items()
                                          if (named ^ known) & shared == 0)
        return self._pool_cache[key]

    def _candidates(self, state: State, left: Request, right: Request) -> tuple[Candidate, ...]:
        shared = (self._supports[left] & self._supports[right]) if left is not None and right is not None else 0
        first_shared = shared & -shared
        return tuple(
            (left_word, right_word, 2 if self.bias and left_named & first_shared else 1)
            for (left_word, left_named), (right_word, right_named) in product(
                self._pool(left, state[0]), self._pool(right, state[1])
            )
            if (left_named ^ right_named) & shared == 0
        )

    def candidates(self, state: State, left: Request, right: Request) -> tuple[Candidate, ...]:
        """Evaluator metadata: each union assignment as two restrictions and its integer weight.

        The two agreeing restrictions specify one complete union assignment.
        A refused address is screened before the draw and supplies no relation.
        An empty tuple means the valid requesting relations have no joint answer.
        """
        return self._candidates(state, self._address(left), self._address(right))

    def step(self, state: State, left: Request, right: Request) -> tuple[Transition, ...]:
        """Enumerate local answers, exact weights and the ensuing literal states."""
        left, right = self._address(left), self._address(right)
        key = state, left, right
        if key not in self._transition_cache:
            eligible = self._candidates(state, left, right)
            if not eligible:
                result = ((None, None, Fraction(1), state),)
            else:
                total = sum(weight for _, _, weight in eligible)
                exact = {weight: Fraction(weight, total) for weight in {row[2] for row in eligible}}
                result = tuple(
                    (lword, rword, exact[weight],
                     ((left, lword) if lword is not None else state[0],
                      (right, rword) if rword is not None else state[1]))
                    for lword, rword, weight in eligible
                )
            self._transition_cache[key] = result
        return self._transition_cache[key]

    def _transcript_law(self, slots, left, right, observe, initial):
        if type(slots) is not int or slots < 0:
            raise ValueError("the number of slots must be a nonnegative integer")
        policies = tuple(p if callable(p) else tuple(p) for p in (left, right))
        adaptive = tuple(callable(p) for p in policies)
        if any(len(p) != slots for p, dynamic in zip(policies, adaptive, strict=True) if not dynamic):
            raise ValueError("a fixed policy must supply one request per slot")
        keep = tuple(i in observe or adaptive[i] for i in (0, 1))
        paths = {(self.start() if initial is None else initial, ((), ())): Fraction(1)}
        for slot in range(slots):
            next_paths = Counter()
            for (state, records), mass in paths.items():
                lreq, rreq = (p(records[i]) if adaptive[i] else p[slot] for i, p in enumerate(policies))
                for lans, rans, weight, new_state in self.step(state, lreq, rreq):
                    visible = tuple(records[i] + (self.readout(req, ans),) if keep[i] else ()
                                    for i, (req, ans) in enumerate(((lreq, lans), (rreq, rans))))
                    next_paths[new_state, visible] += mass * weight
            paths = next_paths
        laws = Counter()
        for (_, records), mass in paths.items():
            laws[tuple(records[i] for i in observe)] += mass
        return dict(laws)

    def joint_transcripts(self, slots: int, left: Policy, right: Policy, *, initial: State | None = None
                          ) -> dict[tuple[Transcript, Transcript], Fraction]:
        """Evaluator's joint law. A callable policy sees only its own private prefix."""
        return self._transcript_law(slots, left, right, (0, 1), initial)

    def private_transcripts(self, slots: int, left: Policy, right: Policy, observer=0, *, initial: State | None = None
                           ) -> dict[Transcript, Fraction]:
        """Exact one-reader law, summing every other-reader outcome without postselection."""
        if observer not in (0, 1):
            raise ValueError("observer must be reader 0 or 1")
        return {history: weight for (history,), weight in
                self._transcript_law(slots, left, right, (observer,), initial).items()}


def prefix_law(law: dict[Transcript, Fraction], length: int) -> dict[Transcript, Fraction]:
    prefix = Counter()
    for history, weight in law.items():
        prefix[history[:length]] += weight
    return dict(prefix)


def total_variation(first, second) -> Fraction:
    return sum((abs(first.get(key, 0) - second.get(key, 0)) for key in first.keys() | second.keys()), Fraction()) / 2


def first_difference(first: dict[Transcript, Fraction], second: dict[Transcript, Fraction]):
    """Give the earliest differing private slot and an exact witness, or None."""
    slots = max((len(history) for history in first.keys() | second.keys()), default=0)
    for length in range(1, slots + 1):
        a, b = prefix_law(first, length), prefix_law(second, length)
        witnesses = [prefix for prefix in a.keys() | b.keys() if a.get(prefix, 0) != b.get(prefix, 0)]
        if witnesses:
            witness = min(witnesses, key=repr)
            return dict(slot=length, prefix=witness, first_mass=a.get(witness, Fraction()),
                        second_mass=b.get(witness, Fraction()), total_variation=total_variation(a, b))
    return None
