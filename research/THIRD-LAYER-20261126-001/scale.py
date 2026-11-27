"""scale.py: class facts at a scale k (a small change is any allowed change of at most k distinctions), read by least
flipping changes (minflip.least): a parity is a class fact at scale k when no allowed change of at most k flips it and
the laws do not fix it; a knot's own class facts at scale k are the parities of subsets of its distinctions with that
property; a fact is held by no part at scale k when it is not in the span of the laws and of every knot's own class
facts at scale k.  THIRD-LAYER-20261126-001."""
import sys, itertools
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BUILT-BINDING-20261126-001')); sys.path.insert(0, str(HERE))
import repro as RP, minflip as MF
classes = RP.classes


def is_fact(st, support, k):
    w = MF.least(st, support, kmax=k)
    return w is not None and isinstance(w, str)          # 'more than k': no change of at most k flips it


def local_facts(st, k, cache=None):
    out = []
    for r in st:
        facts = []
        for size in range(1, len(r) + 1):
            for sub in itertools.combinations(r, size):
                if is_fact(st, list(sub), k): facts.append(list(sub))
        out.append(facts)
    return out


def held_by_no_part(st, supports, k):
    names, idx, rows = RP.space(st)
    loc = local_facts(st, k)
    vecs = [sum(1 << idx[x] for x in sub) for facts in loc for sub in facts]
    r0 = classes.rank(rows + vecs)
    res = []
    for sup in supports:
        f = sum(1 << idx[x] for x in sup)
        res.append({'class fact at k': is_fact(st, sup, k), 'held by no part at k': classes.rank(rows + vecs + [f]) > r0})
    return res, sum(len(x) for x in loc)
