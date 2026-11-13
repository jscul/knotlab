"""The merge used on 2026-11-13 (kept as code after BOND-DEPTH-R1): all raw records (the 8 workers and 12 helpers) in raw/, one record
per family (the first seen; duplicates agree in every scientific field), unfinished families written with an empty L."""
import glob, importlib.util, json, os
HERE = os.path.dirname(os.path.abspath(__file__))
s = importlib.util.spec_from_file_location("bd", os.path.join(HERE, "census.py"))
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
recs = {}
for f in sorted(glob.glob(os.path.join(B.OUT, "raw", "runs_*.jsonl"))):
    for line in open(f):
        r = json.loads(line)
        recs.setdefault(r["idx"], r)
with open(os.path.join(B.OUT, "runs_merged.jsonl"), "w") as out:
    for idx, _ in B.families_one_def():
        out.write(json.dumps(recs.get(idx, dict(idx=idx, L=[], rate=None, states=None, unfinished=True))) + "\n")
