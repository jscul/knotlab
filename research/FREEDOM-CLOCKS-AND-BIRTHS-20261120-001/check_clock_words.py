"""Check the distinct meanings of clock reception on the recorded return words.

The identified parent map in the 21-knot construction turns each straight
word into a physical knot and each deletion of an end into a true parent.
This independent finite replay uses that theorem, not a new growth rule.
"""
from itertools import product
import json

NEUTRAL = ("v", "r1", "r2", "r3")
MARKERS = {"b0", "b1"}


def one_return(n, marker):
    return NEUTRAL * n + ("v", "s", marker, "t")


def window(period, start, length):
    return tuple(period[(start + i) % len(period)] for i in range(length))


def longest_match(first, second):
    """Allow phases and both orientations; unequal gaps give a finite cutoff."""
    best, example = 0, None
    for rev in (False, True):
        other = second[::-1] if rev else second
        for i, j in product(range(len(first)), range(len(other))):
            count = 0
            while first[(i+count) % len(first)] == other[(j+count) % len(other)]:
                count += 1
                assert count <= len(first) + len(other)
            if count > best:
                best, example = count, (i, j, other)
    return best, example


def compare(n, r, ell):
    slow = one_return(r, "b0")
    period = one_return(n, "b0")*ell + one_return(n, "b1")
    m = 2*len(period)
    source_age = m-1
    shared, (i, j, other) = longest_match(period, slow)
    sent = window(period, i-(m-shared), m)
    receiving = window(other, j, m)
    assert sent[-shared:] == receiving[:shared]
    child = sent + receiving[shared:]
    assert len(child) == 2*m-shared
    assert all(child[k]!=child[k+2] for k in range(len(child)-2))
    assert child[:-1][:m] == sent and child[1:][-m:] == receiving
    assert child[1:][:m] != sent and child[:-1][-m:] != receiving
    marked = [k for k, token in enumerate(sent) if token in MARKERS]
    assert len(marked)>=2 and marked[1]-marked[0] != len(slow)
    return {"send_age": source_age, "maximum_common_length": shared,
            "separation_at_send": m-shared, "first_shared_age": len(child)-1}


def main():
    rows = {}
    for n, r in ((1, 2), (2, 1), (2, 3), (3, 2)):
        trials = [compare(n, r, ell) for ell in range(1,9)]
        assert {item["maximum_common_length"] for item in trials} == {8*min(n,r)+5}
        rows[f"{4*(n+1)} to {4*(r+1)}"] = trials
    return rows


if __name__ == "__main__":
    print(json.dumps(main(), indent=2))
