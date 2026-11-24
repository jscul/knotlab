"""A side check made while surveying the record for this study: the canonical K1-K3 test on one parity knot and one
not-all-equal knot alone, for 3 to 8 places. An earlier record states this was checked for every arity 3 through 8, while the
code it used calls the canonical checker only up to 5 places.  Run from the repository root:
PYTHONPATH=tools python3 -B research/RING-IN-BALANCE-20261123-001/checks/arity_check.py"""
from itertools import product
from knotlab.relations import Relation
from knotlab.knots import check_knot

for law in ("parity", "not-all-equal"):
    for size in range(3, 9):
        names = tuple(map(str, range(size)))
        rows = frozenset(w for w in product((False, True), repeat=size)
                         if (sum(w) % 2 == 0 if law == "parity" else 0 < sum(w) < size))
        verdict = check_knot(Relation(names, rows), names[:-1], names[-1])
        print(f"{law:14s} {size} places: {len(rows):3d} allowed states, knot: {verdict.is_knot}")
        assert verdict.is_knot
