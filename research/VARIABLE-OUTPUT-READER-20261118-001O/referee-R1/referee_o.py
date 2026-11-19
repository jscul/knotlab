"""Referee R1 for VARIABLE-OUTPUT-READER-20261118-001O (own code, on the referee's 001F/001G/001L-R1 machinery; histories read from
the study's notes and JSON files as data; no Codex code imported or run).

  ../../../.venv/bin/python -B referee_o.py <part> > referee_o_<part>.json      (from this directory)

The one-spent family: the four-addition family (001N) whose fourth three-output junction takes three parents, with exactly one of
its three outputs used later by a two- or three-parent two-fresh join (the spending child), the other two still loose.

Parts:
  w23   frontier.md's width-23 source (menus just before and after the spend) and census.json's width-23 swap (10 16).
  w25   frontier.md's width-25 example: the first eight sites of the width-23 source with (5, 8, 21, 22), then the spending child
        (13, 18, 23, 24): menus before and after, which survive, and the table's symmetries through D = 4, D = 5 and in full.
  w31   residual.json's width-31 fixture: membership (the fourth junction's spent output, the child's two spent outputs), the menu,
        the roles, and the table's symmetries through D = 4, D = 5 and in full.
"""
import json
import sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001L/referee-R1"))
sys.path.insert(0, str(ROOT / "research/VARIABLE-OUTPUT-READER-20261118-001N/referee-R1"))
import referee_l as L  # noqa: E402
import referee_n as N  # noqa: E402

F, RG = L.F, L.RG
STUDY = ROOT / "proofs/VARIABLE-OUTPUT-READER-20261118-001O/VARIABLE-OUTPUT-READER-20261118-001O-P001_one_spent_output"
W23 = [[0, 1, 2], [0, 3, 4, 5], [1, 6, 7, 8], [2, 9, 10, 11], [3, 6, 12, 13], [4, 9, 14, 15], [12, 14, 16, 17],
       [7, 10, 16, 18, 19, 20], [13, 18, 21, 22]]


def one_spent(J):
    """In the four-addition family, the fourth three-output junction three-parent, exactly one of its outputs used."""
    if not N.in_four(J):
        return False
    fresh, parents = L.profile(J)
    four = [k for k in range(3, len(J)) if fresh[k] == 3][-1]
    if parents[four] != 3:
        return False
    outs = [x for x in J[four] if all(x not in Q for Q in J[:four])]
    used = sum(1 for x in outs if any(x in Q for Q in J[four + 1:]))
    return used == 1


def symmetry_rows(J, m):
    K, n, _ = L.table(J)
    S = {frozenset(s) for s in J}
    out = {}
    for name, C in (("D4", F.clip(K, 5)), ("D5", F.clip(K, 6)), ("full", K)):
        g = F.generators(C)[0]
        out[f"through {name}: every symmetry keeps the menu, the supports"] = [F.keeps(g, m) if m else True, F.keeps(g, S)]
    return out


def part_w23():
    J, ok, _, _ = RG.replay(W23)
    before = L.menu(J[:-1])
    after = L.menu(J)
    out = {"frontier.md source": {"width": 1 + max(max(s) for s in J), "legal": ok, "one-spent": one_spent(J),
                                  "menu just before the spend": sorted(sorted(t) for t in before),
                                  "menu just after": sorted(sorted(t) for t in after), **symmetry_rows(J, after)}}
    w = json.load(open(STUDY / "census.json"))["comparison_examples"]["D4"]
    J2, ok2, _, _ = RG.replay(w["left"]["chronological_supports"])
    K, n, _ = L.table(J2)
    p = w["permutation"]
    m = L.menu(J2)
    mk = w["marked_example"]
    out["census.json swap"] = {"width": n, "legal": ok2, "one-spent": one_spent(J2), "swap": [x for x in range(n) if p[x] != x],
                               "pairs equal through D = 4, D = 5 and in full": [L.pairs_equal(K, K, p, 5), L.pairs_equal(K, K, p, 6), L.pairs_equal(K, K, p)],
                               "mark legal, image legal": [frozenset(mk["left"]) in m, frozenset(mk["right"]) in m],
                               "least bond through mark, image": [L.least_bond_through(J2, mk["left"]), L.least_bond_through(J2, mk["right"])]}
    return out


def part_w25():
    pre = W23[:8] + [[5, 8, 21, 22]]
    full = pre + [[13, 18, 23, 24]]
    J0, ok0, _, _ = RG.replay(pre)
    J, ok, _, _ = RG.replay(full)
    before, after = L.menu(J0), L.menu(J)
    return {"width": 1 + max(max(s) for s in J), "legal": [ok0, ok], "one-spent": one_spent(J),
            "the fourth junction": sorted(J[7]), "spent output": 18,
            "menu before the spend": sorted(sorted(t) for t in before), "menu after": sorted(sorted(t) for t in after),
            "after = the triples of before that avoid 18": after == {t for t in before if 18 not in t},
            **symmetry_rows(J, after)}


def part_w31():
    d = json.load(open(STUDY / "residual.json"))
    c = d["shortest_named_cases_with_a_spent_child_output"][d["selected_fixture_index"]]
    J, ok, _, _ = RG.replay(c["junction_supports"])
    m = L.menu(J)
    own = defaultdict(list)
    for k, S in enumerate(J):
        for x in S:
            own[x].append(k)
    child = c["spending_child"]
    child_out = [x for x in J[child] if len(own[x]) >= 1 and own[x][0] == child]
    return {"width": 1 + max(max(s) for s in J), "legal": ok, "one-spent": one_spent(J), "in the four-addition family": N.in_four(J),
            "fourth site": sorted(J[c["fourth_site"]]), "spending child": sorted(J[child]),
            "the child's outputs, and how many are used": [child_out, sum(len(own[x]) == 2 for x in child_out)],
            "menu": sorted(sorted(t) for t in m), "menu equals the study's current menu": m == {frozenset(t) for t in c["current"]},
            "legal triples": len(m), **symmetry_rows(J, m)}


if __name__ == "__main__":
    print(json.dumps({"w23": part_w23, "w25": part_w25, "w31": part_w31}[sys.argv[1]](), indent=1, default=str))
