import sys, time, json, random
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
import exhpy
from multiprocessing import Pool
BUD = 3 * 10**7
def task(rec):
    q, b = rec["q"], rec["base"]
    knots = regen(q, b)
    assert len(knots) == rec["knots"]
    pp = regen_pairs(q, b)
    assert all((p["i"], p["j"]) == (a[2], a[3]) for p, a in zip(rec["pairs"], pp))
    step = B.make_step(800, knots)
    items = []
    for p in rec["pairs"]:
        if p["g"] <= 16:
            items.append(("census", p["i"], p["j"], p["L"], p["members"]))
    rng = random.Random(C.seed_of("referee", q, b))
    for _ in range(10):
        i = rng.randrange(40, 700); j = i + rng.randint(1, 20)
        L, S, st = B.least_bond(800, knots, i, j, margin=8, step=step)
        items.append(("extra", i, j, L, S))
    qs = []
    for kind, i, j, L, S in items:
        lo, hi = max(0, i - 8), min(799, j + 8)
        K = L if L else 12
        qs.append((lo, hi, i, j, K, BUD))
    res = exhpy.run(800, knots, qs)
    out = []
    for (kind, i, j, L, S), (bst, nodes, hit, mem) in zip(items, res):
        out.append({"kind": kind, "i": i, "j": j, "L_dp": L, "L_exh": bst, "nodes": nodes, "hit": hit, "dp_members": S, "exh_members": mem})
    # also confirm the frozen L for all census pairs with a fresh run of bonddp (reproducibility), g <= 128 only to save time
    rep = 0; repbad = []
    for p in rec["pairs"]:
        if p["g"] <= 64:
            L, S, st = B.least_bond(800, knots, p["i"], p["j"], margin=8, step=step)
            rep += 1
            if L != p["L"]: repbad.append((p["i"], p["j"], p["L"], L))
    return {"q": q, "base": b, "cmp": out, "reproduced": rep, "repro_bad": repbad}
if __name__ == "__main__":
    bases = load_bases(); done = {(json.loads(l)["q"], json.loads(l)["base"]) for l in open("win_cmp_part1.jsonl")}; bases = [r for r in bases if (r["q"], r["base"]) not in done]
    with Pool(20) as pool, open("win_cmp_part2.jsonl", "w") as f:
        for r in pool.imap_unordered(task, bases):
            f.write(json.dumps(r) + "\n"); f.flush()
            bad = [c for c in r["cmp"] if c["L_dp"] != c["L_exh"] or c["hit"]]
            print(r["q"], r["base"], len(r["cmp"]), "bad", len(bad), "repro_bad", r["repro_bad"], flush=True)
