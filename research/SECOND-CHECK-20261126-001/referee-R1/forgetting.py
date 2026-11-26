"""Project all other distinctions away before calling the record's knot test."""
import argparse
import json
import os
import subprocess
import sys
from collections import Counter
from functools import cache
from itertools import product
from pathlib import Path
from rebuild import independent, kernel, loose, mask, places, residual, syndrome, union

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def project(equations, row):
    observed = list(places(row))
    rest = union(equations) & ~row
    columns = independent(syndrome(1 << i, equations) for i in places(rest))
    values = set()
    for bits in product((0, 1), repeat=len(observed)):
        word = mask(i for i, b in zip(observed, bits) if b)
        if not residual(syndrome(word, equations), columns):
            values.add("".join(map(str, bits)))
    # Independent projection by generating the restrictions of all legal basis words.
    generators = kernel(equations, union(equations).bit_length())
    restricted = {0}
    for g in generators:
        restricted.update({x ^ (g & row) for x in restricted})
    assert {"".join(str(x >> i & 1) for i in observed) for x in restricted} == values
    return tuple(sorted(values))


@cache
def knot_test(arity, states):
    names = [f"d{i}" for i in range(arity)]
    excluded = [bits for bits in product("01", repeat=arity) if "".join(bits) not in states]
    clauses = [" ".join(("-" if bit == "1" else "")+name for name, bit in zip(names, bits))
               for bits in excluded]
    command = [sys.executable, "-B", "-m", "knotlab", "check", "--cnf", ";".join(clauses),
               "--loops", *names[:-1], "--contact", names[-1], "--erasure", "forgetting", "--json"]
    run = subprocess.run(command, env={**os.environ, "PYTHONPATH": str(ROOT/"tools")},
                         capture_output=True, text=True)
    if arity < 3:
        assert run.returncode and "at least two loops" in run.stderr
        return "too few places"
    run.check_returncode()
    report = json.loads(run.stdout)
    assert tuple(report["allowed"]) == states
    loss = all(len({s[:i]+s[i+1:] for s in states}) == 2**(arity-1) for i in range(arity))
    expected = bool(excluded), loss, bool(states)
    assert tuple(report[k] for k in ("binding", "loss_on_erasure", "coexistence")) == expected
    assert report["is_knot"] == all(expected)
    return "K1/K2/K3=" + "".join(str(int(v)) for v in expected)


def run(n, case):
    stage = [mask(r) for r in case["free"]["grown_places"]]
    receipts = {}
    for name in ("free", "pinned"):
        moves = [mask(r) for r in case[name]["moves"]]
        pins = [1 << i for i in places(loose(stage))] if name == "pinned" else []
        for label, rows, equations in (("exchange", moves, moves),
                                       ("exchange with original laws", moves, stage+pins+moves),
                                       ("old holders", stage[:n], stage+pins),
                                       ("new holders", stage[n:], stage+pins)):
            title = f"{name} / {label}"
            receipts[title] = []
            for row in rows:
                allowed = project(equations, row)
                verdict = knot_test(row.bit_count(), allowed)
                receipts[title].append(dict(places=list(places(row)), allowed=allowed, verdict=verdict))
            print(n, title, dict(Counter(r["verdict"] for r in receipts[title])))
    return receipts


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("sizes", nargs="+", type=int, choices=range(5, 9))
    p.add_argument("--output", type=Path)
    args = p.parse_args()
    data = json.loads((HERE/"rings.json").read_text())
    result = {n: run(n, data[str(n)]) for n in args.sizes}
    if args.output:
        args.output.write_text(json.dumps(result, separators=(",", ":"))+"\n")


if __name__ == "__main__":
    main()
