import sys, time, json
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from multiprocessing import Pool
def task(arg):
    q, b, pairs = arg
    knots = regen(q, b)
    step = B.make_step(800, knots)
    out = []
    for (i, j, g) in pairs:
        t0 = time.time()
        L, S, stt = B.least_bond(800, knots, i, j, margin=800, step=step, max_states=300000)
        out.append({"q": q, "base": b, "i": i, "j": j, "g": g, "L_full": L, "status": stt, "sec": round(time.time() - t0, 1)})
    return out
if __name__ == "__main__":
    bases = load_bases()
    args = []
    for r in bases:
        und = [(p["i"], p["j"], p["g"]) for p in r["pairs"] if p["status"] == "none" and p["g"] >= 64]
        # one per gap value per base, up to 4
        seen = set(); pick = []
        for x in und:
            if x[2] not in seen:
                seen.add(x[2]); pick.append(x)
        if pick: args.append((r["q"], r["base"], pick[:4]))
    with Pool(20) as pool, open("undef_full.jsonl", "w") as f:
        for res in pool.imap_unordered(task, args):
            for x in res:
                f.write(json.dumps(x) + "\n")
            f.flush()
            print(res, flush=True)
