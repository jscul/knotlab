"""rations.py: rations made by hand for SHORT-AGAIN-20261126-001, as laws of the shared growth engine.  Each reads
only what the engine's rations read: whether the new knot is a join or an offshoot, the number p of distinctions it
was given, its demand D (the joins it will be owed next round), and for an offshoot its parent's owing o.  None
reads a name, an ancestor or anything of the whole structure.  Every one gives at least enough for three places
and at least one fresh distinction, as the ordinary count does.

    ONE-FEWER     one fewer than the ordinary count (the ring study's ration of that name, with one at least)
    ODD-FEWER     one fewer when the demand is odd, the ordinary count when it is even
    THIRD-FEWER   one fewer when the demand leaves 2 on division by 3
    JOIN-FEWER    a join one fewer, an offshoot the ordinary count
    BUSY-FEWER    a join one fewer when its demand exceeds its number of parents (the advisor's question 2), else
                  the ordinary count; an offshoot the ordinary count

Importing this module registers them with the bench (bench.LAWS)."""
import sys, os
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'TWO-PATTERNS-20261126-001', 'bench'))
import bench
eng = bench.eng

class Made(eng.Law):
    """a law of the engine with the ration replaced; the treatment, the take and the knot law are the engine's"""
    def __init__(self, name, rule, treatment, take=None):
        eng.Law.__init__(self, 'ORD', treatment, take, 'nae')
        self.made, self.rule = name, rule
    def fresh(self, kind, p, D, o):
        floor = max(3 - p, 1); q = max(D, floor)
        return max(self.rule(kind, p, D, o, q), floor)
    def name(self):
        return '%s/%s/RELEASE/%s/nae' % (self.made, self.treatment, 'no-take' if self.take is None else self.take)

RULES = {
    'ONE-FEWER': lambda kind, p, D, o, q: q - 1,
    'ODD-FEWER': lambda kind, p, D, o, q: q - (D % 2),
    'THIRD-FEWER': lambda kind, p, D, o, q: q - (1 if D % 3 == 2 else 0),
    'JOIN-FEWER': lambda kind, p, D, o, q: q - (1 if kind == 'join' else 0),
    'BUSY-FEWER': lambda kind, p, D, o, q: q - (1 if (kind == 'join' and D > p) else 0),
}
for _name, _rule in RULES.items():
    bench.LAWS[_name] = (lambda treatment, take, n=_name, r=_rule: Made(n, r, treatment, take))
