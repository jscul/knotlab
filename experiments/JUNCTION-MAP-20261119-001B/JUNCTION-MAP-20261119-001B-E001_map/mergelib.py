"""The merged reading (JUNCTION-MAP-20261119-001B, pilot): a first-round group of three that shares two knots with another block is
read as an ordinary simplex (its pairs as candidate pairs, merged with the blocks it overlaps) instead of being excluded or kept
as a loop of length two.  Patched from clusters.analyse; everything else is the rule's."""
import inspect
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'experiments/CLUSTER-ALL-20261119-001B/CLUSTER-ALL-20261119-001B-E001_census'))
import clusters as Cl  # noqa: E402


class Overlap(Exception):
    pass


def _build():
    ns = dict(Cl.__dict__)
    ns['Overlap'] = Overlap
    ns['DEMOTE'] = set()
    src = inspect.getsource(Cl.analyse)
    reps = [
        ("    hyper = [tuple(sorted(g)) for g in groups if len(g) > 2]\n",
         "    hyper = [tuple(sorted(g)) for g in groups if len(g) > 2 and tuple(sorted(g)) not in DEMOTE]\n"),
        ("        if len(B) >= 2:\n            simp.append(B)\n",
         "        if len(B) >= 2:\n            simp.append(B)\n    simp += [tuple(sorted(g)) for g in groups if tuple(sorted(g)) in DEMOTE]\n"),
        ("            return {'scope': False, 'why': 'a round-1 group of three sharing two knots with another block'}\n",
         "            raise Overlap(G)\n"),
    ]
    for a, b in reps:
        assert src.count(a) == 1, a
        src = src.replace(a, b)
    exec(compile(src, Cl.__file__, 'exec'), ns)
    for name in ('_series', 'series'):
        exec(compile(inspect.getsource(getattr(Cl, name)), Cl.__file__, 'exec'), ns)
    return ns


_NS = _build()


def series(sizes, edges, N):
    _NS['DEMOTE'] = set()
    for _ in range(64):
        try:
            return _NS['series'](sizes, edges, N)
        except Overlap as ex:
            _NS['DEMOTE'].add(ex.args[0])
    return None
