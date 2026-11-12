import sys, json, math, random
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
import exhpy
from multiprocessing import Pool
def task(arg):
    q, b, items = arg
    k = regen(q, b)
    qs = [(max(0, i - 8), min(799, j + 8), i, j, L, 10**9) for (g, i, j, L) in items]
    res = exhpy.run(800, k, qs)
    return [(q, b, g, i, j, L, r[0], r[1], r[2]) for (g, i, j, L), r in zip(items, res)]
if __name__ == "__main__":
    bases = load_bases(); rng = random.Random(5)
    args = []
    for rec in bases:
        items = []
        for p in rec["pairs"]:
            if p["status"] == "ok" and p["g"] >= 32:
                W = min(799, p["j"] + 8) - max(0, p["i"] - 8) + 1
                if math.comb(W - 2, p["L"] - 2) <= 3 * 10**7:
                    items.append((p["g"], p["i"], p["j"], p["L"]))
        rng.shuffle(items)
        if items: args.append((rec["q"], rec["base"], items[:3]))
    out = []
    with Pool(6) as pool:
        for r in pool.imap_unordered(task, args):
            out += r
            for x in r: print(x, "OK" if x[5] == x[6] else "MISMATCH", flush=True)
    json.dump(out, open("spot.json", "w"))
