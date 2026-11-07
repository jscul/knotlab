import json, time
import pycryptosat
data = json.load(open("spheres.json"))
for k in sorted(data, key=int):
    d = data[k]; n = d["n"]
    S = pycryptosat.Solver(threads=1, time_limit=600)
    pair = {}
    nxt = [n]
    def pv(a, b):
        key = (min(a, b), max(a, b))
        if key not in pair:
            nxt[0] += 1
            pair[key] = nxt[0]
            S.add_xor_clause([a + 1, b + 1, pair[key]], False)   # x_a xor x_b xor e = 0
        return pair[key]
    for L, sg in zip(d["lines"], d["signs"]):
        a, b, c = L
        s = dict(zip(L, sg))
        e1, e2 = pv(a, b), pv(b, c)
        l1 = e1 if (s[a] ^ s[b]) == 0 else -e1
        l2 = e2 if (s[b] ^ s[c]) == 0 else -e2
        S.add_clause([l1, l2])                                   # the pair (a,b) or the pair (b,c) disagrees
    t0 = time.time()
    sat, _ = S.solve()
    dt = time.time() - t0
    print("k", k, "n", n, "satisfiable" if sat else ("unsatisfiable" if sat is False else "unknown"), "time %.2f s" % dt, flush=True)
    if sat is None or dt > 300:
        break
