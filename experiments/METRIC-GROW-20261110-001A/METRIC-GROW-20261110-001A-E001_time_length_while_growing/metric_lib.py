"""Time lengths of a growing plane (METRIC-GROW-20261110-001A-E001), on CROSS-WHY-20261110-001B's territory_lib (code 1).

For a doubling schedule from the open n x n tube: balance at every doubling (territory_lib's reading), and for every original ring Y
(at displacement v from ring (0, 0) on the original torus):
- the hearing lag L(v): the first lag at which an own cell of Y depends on ring (0, 0)'s first-row cells (plain dependence);
- the time length T(v): the first lag at which a route of the growing network reaches an own cell of Y from one of ring (0, 0)'s
  first-row own cells, a route being a sequence of cells each read by the next one step later, through own cells kept by a doubling
  and never through a cell born at one. T(v) <= L(v).
- the cell time length T1(v): the same from ring (0, 0)'s own cell at position 1 alone to Y's own cell at position 1, a reading
  between two points, one per ring, rather than between two rings of 4g cells;
- the freeze reading: one route reaching Y at T(v) (or T1(v)) is traced back, every contact of every stage not on it is frozen for that whole stage
  (A38: c <- c, so it holds its newborn value, which carries nothing of ring (0, 0)), and the dependence is recomputed. T(v) is read
  through freezes (A41) when Y's own cell then depends on ring (0, 0)'s first row at lag T(v)."""
import sys
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / "proofs/CROSS-WHY-20261110-001B/CROSS-WHY-20261110-001B-P001_balance_is_read_on_one_territory"))
import territory_lib as T  # noqa: E402


def disp(a, b, n):
    f = lambda x: x if x <= n // 2 else x - n   # noqa: E731
    return f(a), f(b)


class Stage:
    def __init__(self, tube, A, B, start):
        self.tube, self.A, self.B, self.start = tube, A, B, start
        self.ncon = len(tube.contacts)
        self.orig_cells, self.orig_cell1 = {}, {}
        for b, k in enumerate(tube.keys):
            if k[0] == 'o' and isinstance(k[1][0], int) and isinstance(k[1][1], int):
                self.orig_cells.setdefault(k[1], []).append(b)
                if k[2] == 1:
                    self.orig_cell1[k[1]] = b
        self.new2old = None


def run_schedule(n, g, runs, read_balance=True, stop_at_failure=True):
    r = T.NRun(g, n)
    r.double(0)
    stages = [Stage(r.tube, r.A, r.B, 0)]
    readings = []
    if read_balance:
        f, per = r.read()
        readings.append({"lag": 0, "side": len(r.tube.cols), "balanced": not f, "period": per})
    reach = np.zeros((len(r.tube.keys), 2), dtype=bool)     # column 0: from ring (0, 0); column 1: from its cell at position 1
    reach[stages[0].orig_cells[(0, 0)], 0] = True
    reach[stages[0].orig_cell1[(0, 0)], 1] = True
    hist = {0: reach.copy()}
    pre = {}
    Tlag, T1lag, Llag, t = {}, {}, {}, 0
    origs = [Y for Y in stages[0].orig_cells if Y != (0, 0)]
    for k, P in enumerate(runs):
        st = stages[-1]
        for _ in range(P):
            r.step()
            reach = reach[st.A] | reach[st.B]
            t += 1
            hist[t] = reach.copy()
            for Y in origs:
                if Y not in Tlag and reach[st.orig_cells[Y], 0].any():
                    Tlag[Y] = t
                if Y not in T1lag and reach[st.orig_cell1[Y], 1]:
                    T1lag[Y] = t
            for Y in r.originals_hearing():
                Llag.setdefault(Y, t)
        old = r.tube
        pre[t] = reach.copy()
        r.double(t)
        ns = Stage(r.tube, r.A, r.B, t)
        ns.new2old = {}
        new_reach = np.zeros((len(r.tube.keys), 2), dtype=bool)
        for b, key in enumerate(r.tube.keys):
            if key[0] == 'o' and key in old.pos:
                ns.new2old[b] = old.pos[key]
                new_reach[b] = reach[old.pos[key]]
        reach = new_reach
        hist[t] = reach.copy()
        stages.append(ns)
        if read_balance:
            f, per = r.read()
            readings.append({"lag": t, "side": len(r.tube.cols), "balanced": not f, "period": per,
                             "first failure": min(f.values()) if f else None})
            if f and stop_at_failure:
                break
    out = {"n": n, "g": g, "runs": list(runs), "stages": readings,
           "every stage balanced": bool(read_balance and all(s["balanced"] for s in readings) and len(readings) == len(runs) + 1),
           "T": dict(Tlag), "T1": dict(T1lag), "L": dict(Llag)}
    out["_ctx"] = (stages, hist, pre)
    return out


def stage_at(stages, t):
    """index of the stage in force for the step from lag t to t + 1 (the stage that started at the latest doubling <= t)"""
    s = 0
    for i, st in enumerate(stages):
        if st.start <= t:
            s = i
    return s


def freeze_check(res, Y, kind="T"):
    """trace one route reaching Y at T(Y) (kind "T": ring to ring; "T1": cell 1 to cell 1), freeze every other contact stage by stage,
    and say whether Y's cell then depends on the source at that lag"""
    stages, hist, pre = res["_ctx"]
    col = 0 if kind == "T" else 1
    t = res[kind][Y]
    s = stage_at(stages, t)
    st = stages[s]
    cells = [b for b in (st.orig_cells[Y] if kind == "T" else [st.orig_cell1[Y]]) if hist[t][b, col]]
    if not cells:
        return False
    y = cells[0]
    route = set()
    while t > 0:
        st = stages[s]
        if st.start == t and s > 0:
            y = st.new2old[y]
            s -= 1
            st = stages[s]
            arr_prev = hist[t - 1]
        else:
            arr_prev = hist[t - 1]
        a, b = int(st.A[y]), int(st.B[y])
        moves = [c for c in (a, b) if c != y] + [c for c in (a, b) if c == y]
        nxt = next((c for c in moves if arr_prev[c, col]), None)
        if nxt is None:
            return False
        y = nxt
        if y < st.ncon:
            route.add((s, y))
        t -= 1
    # the X-only run with freezes
    x = np.zeros(len(stages[0].tube.keys), dtype=np.uint8)
    if kind == "T":
        # one bit per source cell would be exact; a single bit summed over the ring's cells could cancel, so use the route's own source
        x = np.zeros((len(stages[0].tube.keys), len(stages[0].orig_cells[(0, 0)])), dtype=np.uint8)
        for i, b in enumerate(stages[0].orig_cells[(0, 0)]):
            x[b, i] = 1
    else:
        x[stages[0].orig_cell1[(0, 0)]] = 1
    target = res[kind][Y]
    t = 0
    s = 0
    while t < target:
        st = stages[s]
        x = x[st.A] ^ x[st.B]
        frozen = np.ones(st.ncon, dtype=bool)
        for (ss, c) in route:
            if ss == s:
                frozen[c] = False
        x[:st.ncon][frozen] = 0
        t += 1
        if s + 1 < len(stages) and stages[s + 1].start == t and t < target + 1:
            ns = stages[s + 1]
            nx = np.zeros((len(ns.tube.keys),) + x.shape[1:], dtype=np.uint8)
            for b, ob in ns.new2old.items():
                nx[b] = x[ob]
            x = nx
            s += 1
    st = stages[s]
    return bool(x[st.orig_cells[Y] if kind == "T" else [st.orig_cell1[Y]]].any())


def metric_report(lags, n):
    """the frozen metric properties of a lag function on the original rings: {Y: lag}"""
    import itertools
    L = {disp(a, b, n): lag for (a, b), lag in lags.items()}
    allv = [v for v in itertools.product(range(-(n // 2), n // 2 + 1), repeat=2) if v != (0, 0)]
    full = all(v in L for v in allv)
    taxi = lambda v: abs(v[0]) + abs(v[1])   # noqa: E731
    wrap = lambda u: disp(u[0] % n, u[1] % n, n)   # noqa: E731
    sym = full and all(L[v] == L[(-v[0], -v[1])] for v in allv)
    viol = [] if not full else [(u, w) for u in allv for w in allv if wrap((u[0] + w[0], u[1] + w[1])) != (0, 0)
                                and L[wrap((u[0] + w[0], u[1] + w[1]))] > L[u] + L[w]]
    classes = {}
    for v in allv:
        if v in L:
            classes.setdefault(taxi(v), set()).add(L[v])
    by_class = full and all(len(c) == 1 for c in classes.values())
    inc = by_class and all(min(classes[d + 1]) > max(classes[d]) for d in range(1, max(classes)))
    deaf = 0
    for d in range(1, 2 * (n // 2) + 1):
        if all(v in L for v in allv if taxi(v) == d):
            deaf = d
        else:
            break
    return {"every ring": full, "symmetric": bool(sym), "triangle inequality": bool(full and not viol),
            "triangle violations": len(viol), "constant on taxicab classes": bool(by_class),
            "strictly increasing in taxicab distance": bool(inc), "metric": bool(full and sym and not viol),
            "reads the lattice distance": bool(full and sym and not viol and by_class and inc),
            "reached to distance": deaf, "lags by taxicab distance": {str(d): sorted(c) for d, c in sorted(classes.items())}}
