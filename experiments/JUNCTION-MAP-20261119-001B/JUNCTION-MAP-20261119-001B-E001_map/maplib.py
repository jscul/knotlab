"""The junction map (JUNCTION-MAP-20261119-001B).

The growth continued from its stage after s rounds is the growth of that stage taken as a start (BREAK-EDDIES' stagelib): its
junctions are the points, two junctions sharing a distinction touch, and the live ones are the last round's.  The map at stage s
is the cluster rule's candidate map of that start, with the rule's one scope cut lifted: a group of three sharing two knots with
another block is kept, so that the two make a loop of length two in the block graph.  `lifted_series(sizes, edges, s, N)`
predicts rounds s + 1 .. s + N from it."""
import inspect
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/BREAK-EDDIES-20261119-001B/BREAK-EDDIES-20261119-001B-E001_breaks'))
import stagelib as SL  # noqa: E402
Cl = SL.E.Cl

CUT = "            return {'scope': False, 'why': 'a round-1 group of three sharing two knots with another block'}\n"


def _build():
    ns = dict(Cl.__dict__)
    src = inspect.getsource(Cl.analyse)
    assert src.count(CUT) == 1
    exec(compile(src.replace(CUT, "            pass\n"), Cl.__file__, 'exec'), ns)
    for name in ('_series', 'series'):
        exec(compile(inspect.getsource(getattr(Cl, name)), Cl.__file__, 'exec'), ns)
    return ns


_NS = _build()
lifted_analyse = _NS['analyse']
lifted = _NS['series']


def lifted_series(sizes, edges, s, N):
    st, _ = SL.stage(sizes, edges, s)
    if st is None:
        return None
    out = lifted(st[0], st[1], N + 1)
    return out[1:] if isinstance(out, list) else out
