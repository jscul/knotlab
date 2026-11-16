"""Check finite training examples used in the decision note."""
from functools import cache
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
PREDECESSOR = "FIVE-PRODUCT-TOTAL-WORK-20261115-001"
for letter, slug in (("A", "charged_tree"), ("B", "learned_affine_work")):
    ticket = PREDECESSOR + letter
    sys.path.insert(0, str(ROOT / "proofs" / ticket / f"{ticket}-P001_{slug}"))

from charged import exact_costs
from verifier import equation, sources, span

SIDES = sources(1)
QUESTIONS = tuple(equation(mask, 1) for mask in range(1, 512))


@cache
def closes_within(cell, budget):
    """All affine questions and separately paid checks, used here through cost three."""
    if not cell:
        return True
    if budget == 0:
        return False
    for side in SIDES.values():
        after = span(cell & side)
        if not after or (after != cell and closes_within(after, budget - 1)):
            return True
    if budget >= 3:
        for question in QUESTIONS:
            yes, no = cell & question, cell - question
            if not yes or not no:
                continue
            for left_cost in range(1, budget - 1):
                if closes_within(yes, left_cost) and closes_within(no, budget - 1 - left_cost):
                    return True
    return False


def check_original_training():
    opposite = equation(1, 1)
    sizes = []
    for a in (0, 1):
        broader = opposite & equation(4, a)
        narrower = broader & equation(256, 0)
        for cell in (narrower, broader):
            for c in (0, 1):
                branch = cell & equation(16, c)
                after = span(branch & SIDES["R"])
                assert after and not (after & SIDES["P"])
        sizes.append([len(narrower), len(broader)])
    return sizes


def check_one_size_further():
    # On seven products set x0=1, x2=a, x1=x3=u=v=0. The last
    # four input bits realize two independent products and their displayed total.
    rich = plain = 0
    for point in range(32):
        y, w, t, r, s = ((point >> i) & 1 for i in range(5))
        expected = (y & w) ^ (t & r)
        for a in (0, 1):
            x = (1, 0, a, 0, y, w, t, w ^ r)
            total = sum(b * c for b, c in zip(x, x[1:])) % 2
            assert total == expected
        if s == expected:
            rich |= 1 << point
        else:
            plain |= 1 << point
    cost = exact_costs(5, rich, plain).weighted
    assert cost == 11
    return cost


def check_nearby_guard():
    # Replace x2 by x4, keeping the same two reports and all operations.
    opposite = equation(1, 1)
    first = equation(256, 0)
    results = []
    for a in (0, 1):
        second = equation(16, a)
        both = opposite & first & second
        # These are all three affine hyperplanes containing the conjunction.
        wider = (first, second, equation(272, a))
        assert closes_within(both, 3) and not closes_within(both, 2)
        assert all(not closes_within(opposite & guard, 3) for guard in wider)
        rich_hull = span(both & SIDES["R"])
        plain_hull = span(rich_hull & SIDES["P"])
        assert plain_hull and not (plain_hull & SIDES["R"])
        results.append(3)
    return results


if __name__ == "__main__":
    print(json.dumps({
        "status": "passed",
        "original_narrow_and_wide_training_domain_sizes": check_original_training(),
        "seven_product_training_minimum_on_section": check_one_size_further(),
        "nearby_x4_guard_training_costs": check_nearby_guard(),
    }, indent=2))
