"""PC-COUNT-20261110-001B-E001: the exact F2 degrees of the sphere's count on K_2, K_3 and K_4 (exploratory; see contract.json).

    .venv/bin/python3 -B run.py    writes artifacts/PC-COUNT-20261110-001B/PC-COUNT-20261110-001B-E001_small_sphere_degrees/run/result.json

pcdeg.c (compiled here into the artifact folder) decides at one degree D whether 1 lies in the F2 Nullstellensatz span (ns) or the
standard polynomial-calculus closure (pc) of a formula's clause falsifiers. For each sphere and formula the degrees D = 3, 4, ... are read
in order until 1 is derived, or a run passes the memory cap (that degree and all above it undecided). Formulas: NAE(K_k), the count,
with the falsifiers of its own clauses (COUNT-NOTE-20261107-001B's sa_lib.falsifiers); and the control NAE(K_k) and FACE(K_k), the
count's clauses with the conjunctions of its three-point faces (sa_lib.certificate's terms with coefficient -1), whose sum with the
line conjunctions is 1."""
import json
import subprocess
import sys
import time
import importlib.util
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SA = next((ROOT / "proofs/COUNT-NOTE-20261107-001B").iterdir())
sys.path.insert(0, str(SA))
spec = importlib.util.spec_from_file_location("sa_lib", SA / "sa_lib.py")
S = importlib.util.module_from_spec(spec)
spec.loader.exec_module(S)
OUT = ROOT / "artifacts" / "PC-COUNT-20261110-001B" / "PC-COUNT-20261110-001B-E001_small_sphere_degrees" / "run"
SPHERES = (2, 3, 4)
MEM_MIB = 15000


def falsifier(assign):
    """the multilinear F2 polynomial of a conjunction {variable: value}: x for value 1, 1 + x for value 0"""
    poly = {0}
    for v, val in assign.items():
        if val == 1:
            poly = {m | (1 << v) for m in poly}
        else:
            new = set()
            for m in poly:
                new ^= {m}
                new ^= {m | (1 << v)}
            poly = new
    return poly


def formulas(k):
    lines, signs, n = S.sphere(k)
    count = [falsifier(dict(c)) for c in sorted(S.falsifiers(k), key=sorted)]
    terms, info = S.certificate(k)
    faces = [falsifier(J) for c, J in terms if c == -1]
    assert info["sum of the terms is the constant 1"]
    return n, {"count": count, "control": count + faces}


def run(binary, mode, D, n, axioms):
    inp = "%d %d\n" % (n, len(axioms)) + "".join("%d %s\n" % (len(a), " ".join(map(str, sorted(a)))) for a in axioms)
    out = subprocess.run([str(binary), mode, str(D), str(MEM_MIB)], input=inp, capture_output=True, text=True, check=True).stdout
    return json.loads(out)


def main():
    t0 = time.time()
    OUT.mkdir(parents=True, exist_ok=True)
    binary = OUT / "pcdeg"
    subprocess.run(["gcc", "-O3", "-march=native", "-o", str(binary), str(HERE / "pcdeg.c")], check=True)
    log = open(OUT / "progress.txt", "w")
    result = {"experiment": "PC-COUNT-20261110-001B-E001", "readings": {}}
    for k in SPHERES:
        n, fs = formulas(k)
        for name in ("control", "count"):
            for mode in ("pc", "ns"):
                key = "K_%d %s %s" % (k, name, mode)
                reading = {"points": n, "clauses": len(fs[name]), "runs": []}
                for D in range(3, n + 1):
                    r = run(binary, mode, D, n, fs[name])
                    reading["runs"].append(r)
                    print(key, json.dumps(r), round(time.time() - t0), file=log, flush=True)
                    if "skipped" in r:
                        reading["degree"] = "undecided: more than %d (degree %d passes the memory cap)" % (D - 1, D)
                        reading["lower bound"] = D
                        break
                    if r["refuted"]:
                        reading["degree"] = D
                        reading["lower bound"] = D
                        break
                result["readings"][key] = reading
    deg = lambda k, name, mode: result["readings"]["K_%d %s %s" % (k, name, mode)]["degree"]
    lo = lambda k, name, mode: result["readings"]["K_%d %s %s" % (k, name, mode)]["lower bound"]
    exact = lambda k, name, mode: isinstance(deg(k, name, mode), int)
    result["H1 the count's polynomial-calculus degree on K_3 is above K_2's"] = (
        lo(3, "count", "pc") > deg(2, "count", "pc") if exact(2, "count", "pc") else None)
    result["H2 on K_2 and K_3 the count's polynomial-calculus degree is below its Nullstellensatz degree"] = {
        "K_%d" % k: (deg(k, "count", "pc") < lo(k, "count", "ns")) if exact(k, "count", "pc") else None for k in (2, 3)}
    result["H3 the control has degree 3 in both systems on every sphere read"] = all(
        deg(k, "control", m) == 3 for k in SPHERES for m in ("pc", "ns") if exact(k, "control", m)) and all(
        exact(k, "control", m) for k in SPHERES for m in ("pc", "ns"))
    result["H4 the count's polynomial-calculus degree on K_4 is above K_3's, when both are decided"] = (
        lo(4, "count", "pc") > deg(3, "count", "pc") if exact(3, "count", "pc") else None)
    result["seconds"] = round(time.time() - t0, 1)
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k != "readings"}, indent=1))
    print(json.dumps({k: v["degree"] for k, v in result["readings"].items()}, indent=1))


if __name__ == "__main__":
    main()
