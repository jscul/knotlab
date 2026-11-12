import sys, json
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from multiprocessing import Pool
def task(arg):
    q, b, pairs = arg
    k = regen(q, b, 1200); st = B.make_step(1200, k)
    return [(q, b, i, j, g, B.least_bond(1200, k, i, j, margin=1200, step=st, max_states=300000)[2]) for i, j, g in pairs]
if __name__ == "__main__":
    args = []
    for r in load_bases():
        if r["base"] in (0, 4) and r["q"] in (0.0, 0.3, 0.5, 0.7):
            pp = [(p["i"], p["j"], p["g"]) for p in r["pairs"] if p["status"] == "none" and p["g"] >= 256][:2]
            if pp: args.append((r["q"], r["base"], pp))
    with Pool(8) as pool:
        for res in pool.imap_unordered(task, args): print(res, flush=True)
