import json, sys, time
import exact
data = json.load(open("spheres.json"))
for k in sorted(data, key=int):
    d = data[k]; n = d["n"]
    S = exact.Exact()
    for p in range(n): S.addVariable("x%d" % p, 0, 1)
    for L, sg in zip(d["lines"], d["signs"]):
        # sum of literals y = x or 1 - x : 1 <= sum <= 2
        coefs, names, const = [], [], 0
        for p, s in zip(L, sg):
            if s: coefs.append(-1); const += 1
            else: coefs.append(1)
            names.append("x%d" % p)
        S.addConstraint(list(zip(coefs, names)), True, 1 - const, True, 2 - const)
    t0 = time.time()
    res = S.runFull(False, 600)
    stats = S.getStats()
    st = dict(stats)
    print("k", k, "n", n, "result", res, "time %.2f s" % (time.time() - t0), {key: v for key, v in st.items() if key.lower() in ("conflicts", "decisions", "propagations") or "cut" in key.lower()}, flush=True)
    if time.time() - t0 > 300: break
