"""Reading a growth from a later stage (BREAK-EDDIES-20261119-001B).

The cheapest growth continued from its stage after s rounds is the growth of that stage taken as a start: its junctions as knots
(places = their distinctions), two junctions sharing a distinction as a touch, the live ones exactly those holding a loose
distinction (the last round's).  So the cluster rule can be applied at any stage.  `stage_rule` grows s rounds, takes the stage,
and asks the rule (and the eddy rule) about the rest."""
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/LOOP-CATALOGUE-20261119-001B/LOOP-CATALOGUE-20261119-001B-E001_catalogue'))
import eddy as E  # noqa: E402
J = E.J


def stage(sizes, edges, s):
    """The presentation after s rounds as a start: (sizes, edges), and the counts of rounds 0..s."""
    P = J.S.from_junctions(J.stars_from(sizes, edges))
    P.linalg = False
    for _ in range(s):
        r = P.step(J.F.fewest, None)
        if r is None or r['new'] == 0:
            return None, P.counts_by_round()
    owners = defaultdict(list)
    for j, bits in enumerate(P.bits_of):
        for b in bits:
            owners[b].append(j)
    e = [tuple(sorted(o)) for o in owners.values() if len(o) == 2]
    return ([len(b) for b in P.bits_of], sorted(e)), P.counts_by_round()


def stage_rule(sizes, edges, s, N):
    """The rule's verdict and series from stage s: (status, predicted counts of rounds s + 1 .. s + N)."""
    st, _ = stage(sizes, edges, s)
    if st is None:
        return 'ended', None
    sz, e = st
    v = E.eddy(sz, e)
    A = E.Cl.analyse(sz, e)
    if not A['scope']:
        return 'out of scope', None
    if A['stall']:
        return 'stall', None
    if not E.exact(A):
        return 'break', None
    ser = E.Cl.series(sz, e, N + 1)
    return ('eddy' if v is True else 'no eddy'), ser[1:]
