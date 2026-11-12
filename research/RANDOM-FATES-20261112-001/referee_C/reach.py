"""Referee's reach DP: r(u) = the largest member of any bond containing u (members anywhere). Same (F, G) state as the frozen
programme, but the value kept per state is the largest last member (adding members only raises it), so no j is fixed."""
import sys, json, time
sys.path.insert(0, "/tmp/claude-1000/-home-jscul-p-vs-np-contact-first/f0f2b323-7667-54e0-bff8-c1ab470fc84d/scratchpad/referee_C")
from regen import *
from multiprocessing import Pool
minimal = B.minimal
def reach(N, step, u, max_states=200000):
    layer = {(frozenset([255]), frozenset()): -1}
    for m in range(N):
        nxt = {}
        def put(Fm, Gm, last):
            if 0 in Gm: return
            k = (Fm, Gm); o = nxt.get(k)
            if o is None or o < last: nxt[k] = last
        for (Fm, Gm), last in layer.items():
            if m != u:
                put(minimal(step(R, m, (0, 1)) for R in Fm), minimal(step(R, m, (0, 1)) for R in Gm), last)
            if 0 not in Fm:
                if not Gm:
                    F2 = minimal([step(R, m, (0,)) for R in Fm]); G2 = minimal([step(R, m, (0, 1)) for R in Fm])
                else:
                    F2 = minimal([step(R, m, (x,)) for R in Fm for x in (0, 1)])
                    G2 = minimal([step(R, m, (x,)) for R in Gm for x in (0, 1)] + [step(R, m, (0, 1)) for R in Fm])
                put(F2, G2, m)
        # states that have not yet taken u must not die: they are those whose last < u ... handled by must at m == u
        layer = nxt
        if len(layer) > max_states: return None
    best = [last for (Fm, Gm), last in layer.items() if 0 in Fm]
    return max(best) if best else None
def mirror(N, knots):
    return sorted(tuple(sorted(N - 1 - v for v in t)) for t in knots)
def task(arg):
    q, b, us = arg
    k = regen(q, b); N = 800
    st = B.make_step(N, k); km = mirror(N, k); stm = B.make_step(N, km)
    out = []
    for u in us:
        r = reach(N, st, u)
        bm = reach(N, stm, N - 1 - u)
        out.append((u, r, None if bm is None else N - 1 - bm))
    return (q, b, out)
if __name__ == "__main__":
    args = []
    for q, b in [(0.0, 3), (0.1, 3), (0.3, 1), (0.5, 2), (0.7, 0), (0.9, 6)]:
        for s in range(40, 400, 30):
            args.append((q, b, list(range(s, s + 30))))
    res = {}
    with Pool(int(sys.argv[1])) as pool, open("reach.jsonl", "w") as f:
        for q, b, out in pool.imap_unordered(task, args):
            f.write(json.dumps({"q": q, "base": b, "rows": out}) + "\n"); f.flush()
            print(q, b, out[0], flush=True)
