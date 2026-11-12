#!/usr/bin/env python3
"""Has the learner ever found a target faster than blind search? (research/SEARCH-AUDIT-20261112-001/preregistration.md)

    .venv/bin/python3 -B audit.py [--write]
PYTHONHASHSEED=0. For every case: the classes (or laws) the learner can rest at, the chance p that one uniform draw among the signings at
rest gives the target (interface flips included), the blind median and mean, and the learner's recorded probes to find. Reads recorded
runs only."""
import glob
import itertools
import json
import math
import os
import statistics
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
T0 = time.time()


def p_path(rel):
    return str(ROOT / rel)


def flips_share(m, target):
    """share of the interface's own flips (each input, and the read distinction) that turn map m into target"""
    k = int(math.log2(len(m)))
    pats = list(itertools.product((0, 1), repeat=k))
    idx = {x: i for i, x in enumerate(pats)}
    sw = {"0": "1", "1": "0", "u": "u", "x": "x"}
    hit = 0
    for f in itertools.product((0, 1), repeat=k):
        for o in (0, 1):
            new = "".join((sw if o else {c: c for c in "01ux"})[m[idx[tuple(a ^ b for a, b in zip(x, f))]]] for x in pats)
            hit += new == target
    return hit / 2 ** (k + 1)


def blind(p):
    if p <= 0:
        return None, None
    if p >= 1:
        return 1, 1.0
    return math.ceil(math.log(0.5) / math.log(1 - p)), 1 / p


def classify(probes_found, n_runs, bmed):
    if bmed is None:
        return "no target at rest"
    found = sorted(probes_found)
    pr = found + [math.inf] * (n_runs - len(found))
    med = statistics.median(pr)
    within = sum(x <= bmed for x in pr)
    if med <= bmed / 2 and within >= 0.75 * n_runs:
        return "learning"
    if med > 2 * bmed:
        return "slower than search"
    return "search"


def case_row(name, p, runs, n_rest, n_target_classes):
    bmed, bmean = blind(p)
    found = [r for r in runs if r[0]]
    probes = [r[1] for r in found]
    med = statistics.median(sorted(probes) + [math.inf] * (len(runs) - len(found))) if runs else None
    return {"case": name, "classes or laws at rest": n_rest, "of them giving the target (up to interface flips)": n_target_classes,
            "p per draw": round(p, 5), "blind median": bmed, "blind mean": None if bmean is None else round(bmean, 1),
            "runs": len(runs), "found": len(found), "learner median probes": med if med != math.inf else "not found in half",
            "learner probes when found": sorted(probes), "reading": classify(probes, len(runs), bmed)}


# ---------------------------------------------------------------- 1. native writing of addresses

def native_write():
    sys.path.insert(0, p_path("proofs/NATIVE-WRITE-20261110-001A/NATIVE-WRITE-20261110-001A-P001_native_writing"))
    import write_lib as W
    d = json.load(open(glob.glob(p_path("proofs/NATIVE-WRITE-20261110-001A/*/result.json"))[0]))["checks"]["rows"]["test"]
    out = []
    for name, rec in d.items():
        sp = W.Space(name)
        rest = [sp.acting(s) for s in sp.O.classes(sp.K) if W.has_floor_state(sp.K, s, sp.floor2 // 2)]
        by = {}
        for r in rec["rows"]:
            by.setdefault(tuple(r["target"]), []).append((str(r["outcome"]).startswith("exact"), r["probes"]))
        for tg, runs in sorted(by.items()):
            c = sum(a == tg for a in rest)
            out.append(case_row("native writing / %s / address %s" % (name, list(tg)), c / len(rest), runs, len(rest), c))
    return out


# ---------------------------------------------------------------- 2. gates with the credit learner, 3. deeper memories

def read_maps(K, s, ports_list):
    """read_map for several interfaces of one class with one solver (the same readings as io_lib.read_map)"""
    from pysat.solvers import Solver
    out = []
    with Solver(name="cadical153", bootstrap_with=list(K.clauses(s))) as so:
        for ports in ports_list:
            ins, o = ports[:2], ports[2]
            m = ""
            for x in itertools.product((0, 1), repeat=2):
                a = [(p + 1) if v else -(p + 1) for p, v in zip(ins, x)]
                v0, v1 = so.solve(assumptions=a + [-(o + 1)]), so.solve(assumptions=a + [o + 1])
                m += "x" if not (v0 or v1) else ("u" if v0 and v1 else ("1" if v1 else "0"))
            out.append(m)
    return out


def gate_space(args):
    """one space of a gate family: every case on it, the class maps read once per class"""
    lib, name, cases = args
    W = _gate_lib(lib)
    sp = W.Space(name)
    rest = [s for s in sp.O.classes(sp.K) if W.has_floor_state(sp.K, s, sp.floor2 // 2)]
    keys = sorted(cases)
    maps = [read_maps(sp.K, s, [cases[k][0] for k in keys]) for s in rest]
    out = []
    for j, iname in enumerate(keys):
        ports, runs = cases[iname]
        tg = runs[0][2]
        shares = [flips_share(m[j], tg) for m in maps]
        out.append(case_row("%s / %s / target %s" % (name, iname, tg), sum(shares) / len(rest), [(a, b) for a, b, _ in runs],
                            len(rest), sum(x > 0 for x in shares)))
    return out


def _gate_lib(lib):
    if lib == "credit":
        sys.path.insert(0, p_path("proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance"))
        import credit_lib as C
        return C.W
    sys.path.insert(0, p_path("proofs/DEEP-MEM-20261111-001A/DEEP-MEM-20261111-001A-P001_deeper_memories_from_examples"))
    import deep_lib as L
    return L.W


def gate_cases(spaces_rows, W, I, read_map, groups_of, lib="credit"):
    by = {}
    for (name, iname), v in spaces_rows.items():
        by.setdefault(name, {})[iname] = v
    with Pool(min(8, len(by))) as pool:
        parts = pool.map(gate_space, [(lib, name, cases) for name, cases in sorted(by.items())])
    return [r for part in parts for r in part]


def sturdy():
    sys.path.insert(0, p_path("proofs/CREDIT-PIN-20261110-001B/CREDIT-PIN-20261110-001B-P001_credit_from_pinned_dissonance"))
    import credit_lib as C
    d = json.load(open(glob.glob(p_path("proofs/STURDY-PROBE-20261110-001A/*/result.json"))[0]))["checks"]["rows"]["sturdier probe, credit learner"]
    rows = {}
    for key, rr in d.items():
        name, iname = key.split(" / ")
        sp = C.W.Space(name)
        ports = dict(C.I.interfaces(sp))[iname]
        r0 = rr[0]
        rows.setdefault((name, iname), (ports, []))[1].append((r0["outcome"] in ("learned, held", "learned, not held"), r0["probes"], r0["target"]))
    return gate_cases(rows, C.W, C.I, C.I.read_map, None)


def deep():
    sys.path.insert(0, p_path("proofs/DEEP-MEM-20261111-001A/DEEP-MEM-20261111-001A-P001_deeper_memories_from_examples"))
    import deep_lib as L
    d = json.load(open(glob.glob(p_path("proofs/DEEP-MEM-20261111-001A/*/result.json"))[0]))["checks"]["rows"]
    rows = {}
    cache = {}
    for key, rec in d.items():
        name, g = key.split(" / ")
        if name not in cache:
            sp = L.W.Space(name)
            cache[name] = {str(gg): ports for gg, ports, kind in L.groups(sp)}
        ports = cache[name][g]
        r0 = rec["rows"][0]
        rows.setdefault((name, g), (ports, []))[1].append((r0["outcome"] in ("learned, held", "learned, not held"), r0["probes"], r0["target"]))
    return gate_cases(rows, L.W, L.I, L.I.read_map, None, lib="deep")


# ---------------------------------------------------------------- 4 to 6. parity and counts

def first_rows(paths):
    runs = []
    for p in paths:
        for l in open(p):
            if l.strip():
                r = json.loads(l)["rows"][0]
                runs.append((r["outcome"] in ("learned, held", "learned, not held"), r.get("probes") or 0))
    return runs


def parity_cases():
    sys.path.insert(0, p_path("proofs/SHARED-COUNT-20261111-001A/SHARED-COUNT-20261111-001A-P001_counting_through_a_shared_distinction"))
    import join_lib as J
    F, U = J.F, J.U
    PL = F._parity_lib()
    out = []
    lp = json.load(open(p_path("proofs/LEARN-PARITY-20261111-001A/LEARN-PARITY-20261111-001A-P001_learning_parity/result.json")))["checks"]["rows"]
    for tname, sp in (("T1", PL.t1()), ("T2", PL.t2())):
        rest = [s for s in U.all_classes(sp.K) if sp.K.sat(s)[0]]
        shares = [flips_share(F.read_map_k(sp.K, s, sp.ports), "01101001") for s in rest]
        runs = [(r[0]["outcome"] in ("learned, held", "learned, not held"), r[0]["probes"]) for k, r in lp.items() if k.startswith(tname + " run")]
        out.append(case_row("parity / %s" % tname, sum(shares) / len(rest), runs, len(rest), sum(x > 0 for x in shares)))
    B = J.Joined(2)
    rest = [c for c in itertools.product(range(4), repeat=2)]
    shares = [flips_share(F.read_map_k(B, B.signing(c), B.ports), F.parity_string(5, 0)) for c in rest]
    runs = first_rows([p_path("proofs/SHARED-COUNT-20261111-001A/SHARED-COUNT-20261111-001A-P001_counting_through_a_shared_distinction/runs_learn2.jsonl")])
    out.append(case_row("count of five / J2", sum(shares) / len(rest), runs, len(rest), sum(x > 0 for x in shares)))
    return out


def law_cases():
    sys.path.insert(0, p_path("proofs/NATIVE-GRADE-20261112-001A/NATIVE-GRADE-20261112-001A-P001_a_graded_native_rule"))
    import grade_lib as G
    N, UL, F = G.N, G.UL, G.F
    out = []
    J1 = G.J.Joined(1)
    K0 = J1.copies[0]
    B, T, _ = UL.chosen_undrawn()

    def rest_laws(base, keep):
        pt = [list(t) for t in base.pt]
        _, seqs = N.shortest_sequences(pt)
        for law in UL.laws(base):
            sums = [sum(law[3 * k + pt[k].index(d)] for (k, d) in seq) % 2 for seq in seqs]
            if keep(law, sums):
                yield law

    def run_case(name, base, ports, keep, files):
        laws = [l for l in rest_laws(base, keep) if _sat(base, l)]
        shares = [flips_share(F.read_map_k(base, l, ports), "01101001") for l in laws]
        out.append(case_row(name, sum(shares) / len(laws), first_rows(files), len(laws), sum(x > 0 for x in shares)))

    LR = "proofs/LAW-RIGIDITY-20261112-001"
    NG = "proofs/NATIVE-GRADE-20261112-001A/NATIVE-GRADE-20261112-001A-P001_a_graded_native_rule"
    kast = lambda law, sums: not K0.even_faces(law)
    run_case("rest set of the faces, no grade (R) / J1", J1, J1.ports, kast, [p_path(LR + "A/LAW-RIGIDITY-20261112-001A-P001_the_two_jobs_apart/runs_learnR.jsonl")])
    run_case("rest set of the faces, rigid repair (RS) / J1", J1, J1.ports, kast, [p_path(LR + "A/LAW-RIGIDITY-20261112-001A-P001_the_two_jobs_apart/runs_learnRS.jsonl")])
    run_case("every shortest sum 1 (N1) / J1", J1, J1.ports, lambda l, s: all(v == 1 for v in s), [p_path(LR + "B/LAW-RIGIDITY-20261112-001B-P001_a_native_rest_set/runs_learnN1J1.jsonl")])
    run_case("every shortest sum 0 (N0) / U", B, T, lambda l, s: all(v == 0 for v in s), [p_path(LR + "B/LAW-RIGIDITY-20261112-001B-P001_a_native_rest_set/runs_learnN0U.jsonl")])
    run_case("all shortest sums equal, graded (GE) / J1", J1, J1.ports, lambda l, s: len(set(s)) == 1, [p_path(NG + "/runs_learnJ1.jsonl")])
    run_case("all shortest sums equal, graded (GE) / U", B, T, lambda l, s: len(set(s)) == 1, [p_path(NG + "/runs_learnU.jsonl")])
    return out


def _sat(base, law):
    from pysat.solvers import Solver
    with Solver(name="cadical153", bootstrap_with=base.clauses(law)) as so:
        return so.solve()


def job(name):
    return name, {"native writing": native_write, "gates (credit learner, sturdier probe)": sturdy, "deeper memories": deep,
                  "parity and the count of five": parity_cases, "rest-set and graded learners": law_cases}[name]()


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    names = ["native writing", "gates (credit learner, sturdier probe)", "deeper memories", "parity and the count of five", "rest-set and graded learners"]
    res = {}
    for n in names:
        res[n] = job(n)[1]
        if "--write" in sys.argv:
            (HERE / ("result_%s.json" % n.split(" ")[0])).write_text(json.dumps(res[n], indent=1, default=str) + "\n")
        print(n, {r["reading"] for r in res[n]}, round(time.time() - T0, 1), "s", flush=True)
    rows = [r for n in names for r in res[n]]
    tally = {}
    for r in rows:
        tally[r["reading"]] = tally.get(r["reading"], 0) + 1
    out = {"by family": {n: {k: sum(r["reading"] == k for r in res[n]) for k in sorted({r["reading"] for r in res[n]})} for n in names},
           "all cases": tally, "any case learning": any(r["reading"] == "learning" for r in rows), "cases": rows,
           "seconds": round(time.time() - T0, 1)}
    if "--write" in sys.argv:
        (HERE / "result.json").write_text(json.dumps(out, indent=1, default=str) + "\n")
    print(json.dumps({k: v for k, v in out.items() if k != "cases"}, indent=1, default=str))


if __name__ == "__main__":
    main()
