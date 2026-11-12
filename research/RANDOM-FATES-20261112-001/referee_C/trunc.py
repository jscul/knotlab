import sys, time, json, random
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from multiprocessing import Pool
def task(rec):
    q, b = rec["q"], rec["base"]
    k800 = regen(q, b, 800); k1200 = regen(q, b, 1200)
    assert k1200[:len(k800)] == k800
    extra_old = [t for t in k1200[len(k800):] if max(t) < 800]
    step = B.make_step(1200, k1200)
    out = []
    for p in rec["pairs"]:
        if p["g"] >= 128:
            L, S, st = B.least_bond(1200, k1200, p["i"], p["j"], margin=8, step=step)
            out.append((p["g"], p["i"], p["j"], p["L"], L))
    return {"q": q, "base": b, "extra_knots_within_800": extra_old, "pairs": out}
if __name__ == "__main__":
    bases = load_bases()
    sel = [r for r in bases if r["base"] in (0, 1, 2)]
    with Pool(18) as pool, open("trunc.jsonl", "w") as f:
        for r in pool.imap_unordered(task, sel):
            f.write(json.dumps(r) + "\n"); f.flush()
            diff = [x for x in r["pairs"] if x[3] != x[4]]
            print(r["q"], r["base"], "extra knots on <800:", r["extra_knots_within_800"], "pairs", len(r["pairs"]), "changed", diff, flush=True)
