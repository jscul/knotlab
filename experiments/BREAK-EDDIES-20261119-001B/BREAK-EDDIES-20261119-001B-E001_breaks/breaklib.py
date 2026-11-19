"""The extended cluster rule (BREAK-EDDIES-20261119-001B): CLUSTER-ALL's rule with one change.

Two simplices sharing two or more knots merge into one block only when the merged block is complete (every pair of its knots a
candidate pair).  Otherwise they stay two blocks, and the two knots they share make a loop of length two in the block graph,
which the unrolled map opens out like any other loop.  Everything else (scope, stall, pendants, relay, hyperedges, the count) is
clusters.py's, run unchanged on these blocks; the change is made by patching clusters.analyse's merge test and re-binding
clusters._series to the patched analyse."""
import inspect
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census'))
import clusters as Cl  # noqa: E402

OLD = "                if len(groups_[i] & groups_[j]) >= 2:\n"
NEW = ("                if len(groups_[i] & groups_[j]) >= 2 and _complete(groups_[i] | groups_[j],\n"
       "                                                                    edges_of[i] | edges_of[j]):\n")


def _complete(pts, edges):
    return len(edges) == len(pts) * (len(pts) - 1) // 2


def _build():
    ns = dict(Cl.__dict__)
    ns['_complete'] = _complete
    src = inspect.getsource(Cl.analyse)
    assert src.count(OLD) == 1
    exec(compile(src.replace(OLD, NEW), Cl.__file__, 'exec'), ns)
    for name in ('_series', 'series'):
        exec(compile(inspect.getsource(getattr(Cl, name)), Cl.__file__, 'exec'), ns)
    return ns


_NS = _build()
analyse = _NS['analyse']
series = _NS['series']
