"""Checks for RING-LAW-20261109-001A: which self-blind contact laws see how rings continue through a contact, and what the affine ones
cost (ring_law_lib.py beside this file).

    python3 -B check.py          verify against result.json
    python3 -B check.py --write  write result.json from a fresh run
"""
import collections
import hashlib
import itertools
import json
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import ring_law_lib as L  # noqa: E402

RR = L.RR
OUT = {}
T0 = time.time()
LAWS = [(u, v) for u in range(16) for v in range(16)]


def check(name, ok, info):
    OUT[name] = {"pass": bool(ok), "info": info}
    print(("PASS " if ok else "FAIL ") + name, "(%.0fs)" % (time.time() - T0), flush=True)
    if not ok:
        print(json.dumps(info, indent=1, default=str)[:3000])


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def table(w, l, r):
    return (w >> ((l << 1) | r)) & 1


def labelled_automaton(sig, g, law):
    """every cell's update as a function of labelled cells: contacts by id, own cells by (dart of their corner, offset)"""
    net = L.Net(sig, g, law)
    cyc = RR.cycles(sig)
    rot = {i: [d >> 1 for d in r] for i, r in enumerate(cyc)}
    label = {c: ("contact", c) for c in range(net.E)}
    for i, v in enumerate(sorted(rot, key=repr)):
        R, ds = net.rings[i], cyc[v]
        cpos = [j for j, b in enumerate(R) if b < net.E]
        assert [R[j] for j in cpos] == [d >> 1 for d in ds]
        for k, j in enumerate(cpos):
            off, jj = 1, (j + 1) % len(R)
            while jj != cpos[(k + 1) % len(cpos)]:
                label[R[jj]] = ("corner", ds[k], off)
                off, jj = off + 1, (jj + 1) % len(R)
    out = {}
    for b, l in net.own:
        out[label[b]] = ("xor", tuple(sorted([label[l], label[b]])))
    for c, sides in net.con:
        # the contact's update as a truth table over its four labelled neighbours in a canonical order
        names = sorted({label[x] for l, r, a in sides for x in (l, r)})
        idx = {n: i for i, n in enumerate(names)}
        tt = []
        for bits in itertools.product((0, 1), repeat=len(names)):
            val = 0
            for l, r, (u0, u1, u2, u3) in sides:
                x, y = bits[idx[label[l]]], bits[idx[label[r]]]
                val ^= u0 ^ (u1 & x) ^ (u2 & y) ^ (u3 & x & y)
            tt.append(val)
        out[label[c]] = (tuple(names), tuple(tt))
    return out, net


def main():
    write = "--write" in sys.argv
    man = json.loads((HERE / "manifest.json").read_text())
    bound = man.get("parent_bindings", {})
    check("0_dependencies_bound", bool(bound) and all(sha(ROOT / p) == h for p, h in bound.items()), bound)

    # 1. Theorem 1 at one contact: exchanging the arriving cells changes the contact's function exactly when the ANF condition says
    agree, blind = 0, 0
    for u, v in LAWS:
        same = all(table(u, la, ra) ^ table(v, lb, rb) == table(u, lb, ra) ^ table(v, la, rb)
                   for la, ra, lb, rb in itertools.product((0, 1), repeat=4))
        agree += same == (not L.classify((u, v))["sees the routing"])
        blind += same
    cls = collections.Counter((k, v) for law in LAWS for k, v in L.classify(law).items())
    check("1_the_laws_that_see_the_routing", agree == 256 and blind == 32,
          {"laws": 256, "condition agrees with the truth tables": agree, "blind laws": blind,
           "classes": {"%s: %s" % k: n for k, n in sorted(cls.items())}})

    # 2. Theorem 1 on a network: the square 4 x 4 torus and its line network are the same automaton exactly for the blind laws
    sig, rot, edges, B = RR.lattice("square", 4)
    lines = RR.reroute(sig, RR.classes("square", rot)[1])
    agree2 = 0
    for law in LAWS:
        a, _ = labelled_automaton(sig, 2, law)
        b, _ = labelled_automaton(lines, 2, law)
        agree2 += (a == b) == (not L.classify(law)["sees the routing"])
    check("2_rerouting_changes_the_automaton_exactly_for_the_laws_that_see", agree2 == 256, {"laws agreeing": agree2})

    # 3. Theorem 2: under an affine law that sees the routing, every contact reads exactly one of its two arriving cells, so the other
    # ring's chain of left-neighbour reads stops at the contact (the cell after the contact reads the contact, not the arriving cell)
    ok3, n3, both = True, 0, 0
    for law in LAWS:
        k = L.classify(law)
        if not k["affine"]:
            continue
        net = L.Net(sig, 2, law)
        for c, sides in net.con:
            read_arrivals = [l in net.reads[c] for l, r, a in sides]
            if k["sees the routing"]:
                ok3 &= sum(read_arrivals) == 1
                n3 += 1
            else:
                both += all(read_arrivals)
    check("3_an_affine_law_that_sees_reads_one_arriving_cell", ok3 and n3 > 0,
          {"contacts read under affine laws that see": n3, "contacts reading both arrivals under blind affine laws": both})

    # 4. Theorem 3: under an affine law binding is needing (contacts 0 and 1 of the 4 x 4 torus, both rings, lags 1 to 4)
    ok4, n4 = True, 0
    for law in LAWS:
        if not L.classify(law)["affine"]:
            continue
        net = L.Net(sig, 2, law)
        for c in (0, 1):
            for X in net.contact_rings(c):
                for T in range(1, 5):
                    ok4 &= L.binds_exactly(net, c, X, T) == L.needs_exactly(net, c, X, T)
                    n4 += 1
    check("4_affine_binding_is_needing", ok4, {"affine laws": 64, "cases": n4})

    allok = all(v["pass"] for v in OUT.values())
    result = {"ticket": "RING-LAW-20261109-001A", "checks": OUT, "status": "passed" if allok else "failed",
              "seconds": round(time.time() - T0, 1)}
    path = HERE / "result.json"
    if write:
        path.write_text(json.dumps(result, indent=1, default=str) + "\n")
        print("wrote", path)
    else:
        old = json.loads(path.read_text())
        same = {k: v["pass"] for k, v in old["checks"].items()} == {k: v["pass"] for k, v in OUT.items()}
        print("matches result.json" if same else "DIFFERS from result.json")
        sys.exit(0 if same and allok else 1)


if __name__ == "__main__":
    main()
