"""Deeper memories from examples (research/DEEP-MEM-20261111-001/preregistration.md).

Spaces with deeper or wider composites, built with NEST-ATOMS-20261110-001's nest_lib: D2 (a K_2 composite holding a closed composite of
one leaf and one more leaf, so a leaf sits three levels down) and C3 (a K_3 composite of three leaves). The learner is
CREDIT-PIN-20261110-001B's credit learner with STURDY-PROBE-20261110-001A's sturdier probe, both unchanged. Interfaces: every group with
three outer points (leaves, inner composites, top composites). Maps are scored by SAT afterwards."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/STURDY-PROBE-20261110-001A/STURDY-PROBE-20261110-001A-P001_a_sturdier_probe"))
sys.path.insert(0, str(ROOT / "proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance"))
import probe_lib as P  # noqa: E402
import credit_lib as C  # noqa: E402

W, I, F = C.W, C.I, C.F
SP = W.SP


def C3(leaf):
    W.sphere(3)
    return SP.composite(3, SP.ATOMS[leaf], W.lines_at(3, (2, "max")))


W.SPACES.update({
    "dev D2 C2 thin": lambda: SP.outer_with([SP.D2("thin"), SP.C2("thin")]),
    "dev C3 C2 thin": lambda: SP.outer_with([C3("thin"), SP.C2("thin")]),
    "T1 D2 D2 thin": lambda: SP.outer_with([SP.D2("thin"), SP.D2("thin")]),
    "T2 C3 C3 thin": lambda: SP.outer_with([C3("thin"), C3("thin")]),
    "T3 D2 D2 Fano": lambda: SP.outer_with([SP.D2("Fano"), SP.D2("Fano")]),
})


def groups(sp):
    """every group with three outer points, with its kind: a leaf, or a composite and the number of leaves under it"""
    out = []
    for g in sorted(sp.O.groups):
        lines, ports, _ = sp.O.group_parts(sp.K, g)
        if len(ports) != 3:
            continue
        under = [q for q in sp.leaves if q[:len(g)] == g]
        kind = "leaf" if sp.O.groups[g]["kind"] == "leaf" else ("composite of %d atoms, depth %d" % (len(under), max(len(q) for q in under) - len(g) + 1))
        out.append((g, list(ports), kind))
    return out


def run(sp, ports, targets, seed, budget):
    I.probe = P.sturdy_probe
    params = dict(C.PARAMS, budget=budget)
    return F.run_interface(sp, ports, targets, seed, params=params, learner=C.learn)
