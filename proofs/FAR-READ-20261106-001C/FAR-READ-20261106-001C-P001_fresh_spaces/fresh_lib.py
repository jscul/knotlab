"""Fresh spaces for FAR-READ-20261106-001C, fixed before any of their creation maps was computed.

- 60 candidates: two to five Fano atoms hung on a random plane space of 6 to 12 points (seeds 7000 to 7059), mostly on the plane;
- 40 candidates: one to three Fano atoms hung on a census space with plane glue (seeds 8000 to 8039).
Every splice is the creation map's own, with a random element, lost element and port permutation. Ticket B's rule is frozen
(`rule_lib.py`, bound by hash).

A cost cap, fixed after a first run with all 100 candidates was stopped for cost before any map was stored or any verdict seen: a
candidate is kept when the space minus its first line has at most CAP solutions (86 of the 100).
"""
import importlib.util
import random
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


FRB = ROOT / "proofs/FAR-READ-20261106-001B/FAR-READ-20261106-001B-P001_a_rule_that_reads_every_saved_space"
RL = load("fr_rule_lib", FRB / "rule_lib.py")
AT, G, FL = RL.AT, RL.G, RL.FL
GL, TR, RD = G.GL, G.TR, G.RD


def plane_space(seed):
    r = random.Random(seed)
    m = r.choice([6, 8, 10, 12])
    k = r.choice([2, 3, 4, 5])
    S = GL.plane(GL.PL.grow(m, r.randrange(10 ** 6)))
    return "plane of %d points + %d atoms (seed %d)" % (m, k, seed), G.hang(S, r, k, ["g"], host_bias="g")


def census_plus(seed, census):
    r = random.Random(seed)
    glued = [(nm, S) for nm, S in census if nm.startswith(("twisted", "untwisted"))]
    nm, S = glued[r.randrange(len(glued))]
    k = r.choice([1, 2, 3])
    return "%s + %d atoms (seed %d)" % (nm, k, seed), G.hang(GL.base(S.H, S.s, S.n), r, k, ["g"])


CAP = 60000


def candidates():
    census = RD.census_spaces()
    return [("fresh plane", nm, S) for nm, S in (plane_space(7000 + s) for s in range(60))] + \
        [("fresh census", nm, S) for nm, S in (census_plus(8000 + s, census) for s in range(40))]


def cost(S):
    """the number of solutions of the space minus its first line"""
    return len(G.TL.solutions(S.H, S.s, S.n, skip=0))


def fresh_spaces(mapper=map):
    """the candidates within the cost cap with their costs, and the names of those beyond it"""
    cands = candidates()
    keep, costs, dropped = [], [], []
    for (src, nm, S), k in zip(cands, mapper(cost, [S for src, nm, S in cands])):
        if k <= CAP:
            keep.append((src, nm, S))
            costs.append(k)
        else:
            dropped.append(nm)
    return keep, costs, dropped


def judge(S, ex):
    """the frozen rule, GLUE-READ C's two-stage rule and the source rule on one space; the yes/no obstruction and far-side separation"""
    import collections
    parts, types, lown, xs, atoms = AT.atoms_of(S)
    n = len(S.H)
    c = collections.Counter()
    c["spaces"] += 1
    c["Fano atoms"] += len(atoms)
    cls = RL.read_atoms(n, ex)
    ok, big = AT.reads_atoms(cls, atoms, lown, types)
    c["the frozen rule reads the atoms"] += ok
    c["the frozen rule counts them"] += len(big) == len(atoms)
    c["GLUE-READ C's two-stage rule reads the atoms"] += AT.reads_atoms(AT.two_stage(n, G.creates(ex))[1], atoms, lown, types)[0]
    kept, total = AT.DL.source_blocks(S, {a: {b: (v is not None and any(v),) for b, v in row.items()} for a, row in ex.items()})
    c["source rule counts the atoms"] += len(kept) == len(atoms)
    out = G.creates(ex)
    inn = {b: {a for a in range(n) if b in out[a]} for b in range(n)}
    c["lines of two atoms indistinguishable by whether creation occurs"] += AT.twins_across_atoms(
        n, lambda a, b: b in out[a] and a in out[b] and out[a] - {b} == out[b] - {a} and inn[a] - {b} == inn[b] - {a}, lown, types)
    val = lambda a, b: ex[a].get(b)  # noqa: E731
    c["lines of two atoms indistinguishable far side by far side"] += AT.twins_across_atoms(
        n, lambda a, b: val(a, b) == val(b, a) and all(val(a, x) == val(b, x) and val(x, a) == val(x, b)
                                                      for x in range(n) if x not in (a, b)), lown, types)
    allatom = set().union(*atoms.values())
    c["atoms acting as one from outside"] += sum(all(len({ex[a].get(x) for a in L}) == 1 for x in allatom - L) for L in atoms.values())
    if not ok:
        c["failures: %s" % ("merged atoms" if any(len({lown[k] for k in cl if k in allatom}) > 1 for cl in big)
                            else "split or dropped")] += 1
    return G.kind_of_space(types), c
