"""Helper for BOND-DEPTH-A1: take the not-yet-read families of the slow workers from the end of their lists, using the frozen
run_family unchanged; writes runs_help_<h>.jsonl. Duplicates (if an original worker reaches the same family) are identical by
construction and are dropped by idx in the summary."""
import importlib.util, json, glob, os, sys, time
D = "experiments/BOND-DEPTH-20261112-001A/BOND-DEPTH-20261112-001A-E001_spine_bonds"
s = importlib.util.spec_from_file_location("bd", os.path.join(D, "census.py"))
B = importlib.util.module_from_spec(s); s.loader.exec_module(B)
h, H = int(sys.argv[1]), int(sys.argv[2])
fams = B.families_one_def()
done = {json.loads(l)["idx"] for f in glob.glob(os.path.join(B.OUT, "runs_*.jsonl")) for l in open(f)}
todo = [(j, idx, d) for j, (idx, d) in enumerate(fams) if idx not in done]
todo = sorted(todo, key=lambda x: -x[0])                     # from the end of each worker's list backwards
mine = [t for k, t in enumerate(todo) if k % H == h]
f = open(os.path.join(B.OUT, f"runs_help_{h}.jsonl"), "w")
for j, idx, d in mine:
    cur = {json.loads(l)["idx"] for g in glob.glob(os.path.join(B.OUT, "runs_[0-9]*.jsonl")) for l in open(g)}
    if idx in cur:
        continue
    t0 = time.time()
    r = B.run_family(d)
    f.write(json.dumps(dict(idx=idx, l=d[0][1], seconds=round(time.time() - t0, 1), helper=h, **r)) + "\n"); f.flush()
f.close()
