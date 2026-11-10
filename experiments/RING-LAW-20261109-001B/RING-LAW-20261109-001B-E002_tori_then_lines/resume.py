"""RING-LAW-20261109-001B-E002: finish the census after run.py was killed for memory (see contract.json; run.py is unchanged).

    .venv/bin/python3 -B resume.py    appends to partial.jsonl and progress.txt, then writes result.json

run.py was killed by the out-of-memory killer at its 16 GiB cap after 3,562 of its 4,002 readings, all appended to partial.jsonl:
every R2 and R3 reading and R1 on the nine tori and the line networks of n = 4, with R1 on the line networks of n = 5 unfinished.
This reads the finished readings back, reads the missing R1 readings with run.py's own r1 (the same networks, laws and lags) in
8 worker processes, each replaced after every reading so that no solver's memory is kept, and builds result.json with run.py's
summary, copied unchanged below."""
import collections
import importlib.util
import json
import sys
import time
from multiprocessing import Pool
from pathlib import Path

HERE = Path(__file__).resolve().parent
spec = importlib.util.spec_from_file_location("run_e002", HERE / "run.py")
R = importlib.util.module_from_spec(spec)
sys.modules["run_e002"] = R
spec.loader.exec_module(R)
L, OUT, LAWS, SELECTED, H = R.L, R.OUT, R.LAWS, R.SELECTED, R.H


def main():
    t0 = time.time()
    nets = [(k, n, gr) for k in R.KINDS for n in R.SIZES for gr in R.GROUPINGS]
    nets1 = [net for net in nets if net[2] == "torus" or net[1] in R.LINE_SIZES_R1]
    b1, b23 = {}, {}
    for line in open(OUT / "partial.jsonl"):
        row = json.loads(line)
        key = tuple(row["key"][:3]) + (tuple(row["key"][3]),)
        (b1 if row["reading"] == "R1" else b23)[key] = row["value"]
    missing = [net + (law,) for net in nets1 for law in LAWS if net + (law,) not in b1]
    assert all(net + (law,) in b23 for net in nets for law in SELECTED)
    log = open(OUT / "progress.txt", "a")
    part = open(OUT / "partial.jsonl", "a")
    print("resume", len(b1), "R1 and", len(b23), "R2 R3 readings read back,", len(missing), "R1 readings to read", file=log, flush=True)
    with Pool(8, maxtasksperchild=1) as pool:
        for i, (key, val) in enumerate(pool.imap_unordered(R.timed_r1, missing, chunksize=1)):
            b1[key] = val[0]
            print(json.dumps({"reading": "R1", "key": key, "value": val[0], "seconds": round(val[1], 1)}), file=part, flush=True)
            print("r1 resume", i, key, val, round(time.time() - t0), file=log, flush=True)
    # run.py's summary, unchanged
    table, seeing_binders = {}, []
    for net in nets1:
        cnt = collections.Counter()
        for law in LAWS:
            k = L.classify(law)
            cls = ("affine" if k["affine"] else "nonlinear") + (", sees the routing" if k["sees the routing"] else ", blind") + \
                  (", both rings pass" if k["both rings pass"] else ", a ring cut")
            v = b1[net + (law,)]
            cnt[(cls, v)] += 1
            if k["sees the routing"] and v.startswith("binds"):
                seeing_binders.append([*net, list(law), v])
        table["%s %d %s" % net] = {"%s: %s" % key: m for key, m in sorted(cnt.items())}
    plain = {"%s %d %s %s" % (*net, law): b23[net + (law,)] for net in nets for law in SELECTED}
    sel_nl = [law for law in SELECTED if not L.classify(law)["affine"]]
    passing = lambda law: L.classify(law)["both rings pass"]
    h1 = not [r for r in seeing_binders if r[2] == "torus"]
    h2 = any(r[0] == "square" and r[2] == "lines" and passing(tuple(r[3])) for r in seeing_binders) and \
        not [r for r in seeing_binders if r[0] != "square" and r[2] == "lines" and passing(tuple(r[3]))]
    h3 = all(b23[net + (law,)]["needs both rings at every lag to %d" % H] for net in nets for law in sel_nl)
    h4 = all(b23[net + (law,)]["late"] == 0 for net in nets for law in sel_nl)
    control = {"%s %d %s" % net: b23[net + ((12, 12),)]["late"] for net in nets}
    result = {"experiment": "RING-LAW-20261109-001B-E002",
              "H1 on no torus does a law that sees the routing bind both rings at every lag read": h1,
              "H2 on the square line networks some law that sees the routing with both rings passing binds to lag 6, on the others none": h2,
              "H3 the eight symmetric nonlinear laws need both rings at every lag to 64": h3,
              "H4 under them every torus and line network read is on time": h4,
              "laws that see the routing and bind": seeing_binders, "control (12, 12): late (ring, contact) pairs": control,
              "binding by class of law": table, "needing and the plain reading": plain,
              "seconds": "run.py 4,875 s to its last logged reading, then resume.py %.1f s" % (time.time() - t0),
              "resumed": "run.py was killed for memory after 3,562 of 4,002 readings; resume.py read the other %d" % len(missing)}
    (OUT / "result.json").write_text(json.dumps(result, indent=1) + "\n")
    print(json.dumps({k: v for k, v in result.items() if k not in ("binding by class of law", "needing and the plain reading")}, indent=1))


if __name__ == "__main__":
    main()
