"""The registered runs of the pre-registration ("Runs (frozen)", items 2 to 4), as data."""

R3W = ('RATION-3', 'CANCEL-WAIT')
F1R = ('FLOOR1', 'CANCEL-RETIRE')
F1O = ('FLOOR1', 'CANCEL-OFFSHOOT')
ORD = ('ORD', 'STALL')

LAWS6 = ('R0', 'R1', 'R2', 'R3', 'R3L', 'CONTROL')
CAP_TABLE = 10_000_000
CAP_OTHER = 1_000_000

# item 2, first table: (row id, start, family, cutoffs)
TABLE = [
    ('D2(4,3)-R3W', 'D2(4,3)', R3W, (1,)),
    ('D2(5,3)-R3W', 'D2(5,3)', R3W, (1,)),
    ('Ring(5,3)-R3W', 'Ring(5,3)', R3W, (1, 2)),
    ('C8X3-R3W', 'C8X3', R3W, (1,)),
    ('TWO-KNOT-F1R', 'TWO-KNOT', F1R, (2, 3, 4)),
    ('TWO-KNOT-F1O', 'TWO-KNOT', F1O, (2, 3, 4)),
    ('THREE-KNOT-F1R', 'THREE-KNOT', F1R, (2, 3, 4)),
    ('THREE-KNOT-F1O', 'THREE-KNOT', F1O, (2, 3, 4)),
    ('TWO-KNOT-ORD', 'TWO-KNOT', ORD, (3,)),
    ('LONE-FOUR-ORD', 'LONE-FOUR', ORD, (4,)),
    ('D2(4,3)-ORD', 'D2(4,3)', ORD, (2,)),
    ('Ring(5,3)-ORD', 'Ring(5,3)', ORD, (2,)),
    ('SCC-R3W', 'SCC', R3W, (1,)),
]

# item 2, T(d)
TD_STARTS = ('D2(4,3)', 'D2(6,3)', 'D2(8,3)', 'D2(12,3)', 'C8X3')
TD_DS = tuple(range(2, 11))

# item 4
BEYOND = [
    ('D2(4,3)-R3W-r3', 'D2(4,3)', R3W, 3),
    ('Ring(5,3)-F1R-r3', 'Ring(5,3)', F1R, 3),
    ('Ring(5,3)-F1O-r3', 'Ring(5,3)', F1O, 3),
    ('GEN7-F1R-r3', 'GEN7', F1R, 3),
    ('GEN7-F1O-r3', 'GEN7', F1O, 3),
]

# needed for a verdict on P4 at n = 6 (the prediction names n = 6; not a row of the first table)
EXTRA = [('D2(6,3)-R3W-R3L', 'D2(6,3)', R3W, 1, 'R3L')]


def gate_pairs():
    """Every (start, family) of the runs, with the largest last round R any of its cutoffs needs."""
    pairs = {}
    for _, start, fam, cuts in TABLE:
        pairs.setdefault((start, fam), set()).update(cuts)
    for start in TD_STARTS:
        pairs.setdefault((start, R3W), set()).add(1)
    for _, start, fam, r in BEYOND:
        pairs.setdefault((start, fam), set()).add(r)
    for _, start, fam, r, _ in EXTRA:
        pairs.setdefault((start, fam), set()).add(r)
    return pairs
