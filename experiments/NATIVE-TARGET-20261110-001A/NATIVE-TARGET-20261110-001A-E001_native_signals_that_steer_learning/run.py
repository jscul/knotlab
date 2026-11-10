"""NATIVE-TARGET-20261110-001A-E001: native signals that steer learning to the over-agreeing face (exploratory; see contract.json).

After the split of a least state's violated line on a class-forced torus (LEARN-HANDLES-20261109-001A), every line agrees at one face f(i),
holes are faces of deg 0, and a hole at h moves along a line i at h to f(i). The native rules see only the law and the fixed state: their
dissonance, the states the law allows (N: states with the same dissonance as x), or their own possible moves (sight). R7 is the reference
rule with the outside distance to w0.
Writes artifacts/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/run/result.json."""
import json
import math
import os
import random
import sys
import time
from collections import Counter, defaultdict
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LIB = ROOT / "proofs/LEARN-HANDLES-20261109-001A/LEARN-HANDLES-20261109-001A-P001_learning_resolves_a_class_forced_pair_only_by_winding"
sys.path.insert(0, str(LIB))
import handles_lib as H  # noqa: E402

OUT = ROOT / "artifacts/NATIVE-TARGET-20261110-001A/NATIVE-TARGET-20261110-001A-E001_native_signals_that_steer_learning/run"
T0 = time.time()


def log(*a):
    print(round(time.time() - T0, 1), *a, flush=True)


# ---------------------------------------------------------------------------------------------------- the starts of check 5
def starts(tori):
    """repeat LEARN-HANDLES-20261109-001A checks 2 and 5 with their seeds: the least states, then the (state, split side) pairs"""
    rng = random.Random(20261109)
    least = {}
    for T in tori:
        s = T.classes[T.forced[0]]
        least[T.name] = T.least_states_brute(s)[1] if T.n <= 20 else T.least_states_sat(s, rng, 200)
    rr, out = random.Random(5), {}
    for T in tori:
        s = T.classes[T.forced[0]]
        xs = least[T.name]
        pick = xs if len(xs) <= 200 else rr.sample(xs, 200)
        row, got = Counter(), []
        for x in pick:
            k = rr.randrange(3)
            got.append((x, k))
            s2, f, deg, l0, w0 = T.split(s, x, k)
            for rule, budget in (("no_reversal", 20 * T.V), ("random", 50 * T.V * T.V)):
                if rule == "random" and row["random runs"] >= 50:
                    continue
                okr, steps, moves = T.run_rule(f, deg, w0, rule, rr, budget)
                row[rule + " runs"] += 1
                if not okr and rule == "no_reversal":
                    T.run_rule(f, deg, w0, rule, rr, 10 * budget)
        out[T.name] = got
    return out


# ---------------------------------------------------------------------------------------------------- configurations and moves
class Conf:
    __slots__ = ("f", "deg", "s", "last")

    def __init__(self, f, deg, s, last=None):
        self.f, self.deg, self.s, self.last = list(f), list(deg), list(s), dict(last or {})

    def copy(self):
        return Conf(self.f, self.deg, self.s, self.last)

    def holes(self):
        return [v for v, d in enumerate(self.deg) if d == 0]

    def resolved(self):
        return all(d == 1 for d in self.deg)


def moves_of(T, c, h):
    return [(h, i, c.f[i]) for i in T.lines_at[h]]


def candidates(T, c):
    out = []
    for h in c.holes():
        ms = moves_of(T, c, h)
        keep = [m for m in ms if m[2] != c.last.get(h)]
        out += keep or ms
    return out


def all_moves(T, c):
    return [m for h in c.holes() for m in moves_of(T, c, h)]


def apply(T, c, m):
    h, i, w = m
    d = c.copy()
    k = T.side(i, h, w)
    d.f[i] = h
    d.deg[h] += 1
    d.deg[w] -= 1
    d.s[3 * i + k] ^= 1
    d.last.pop(h, None)
    if d.deg[w] == 0:
        d.last[w] = h
    return d, (i, k)


def absorbs(c, m):
    return c.deg[m[2]] >= 2


# ---------------------------------------------------------------------------------------------------- N: states with the same dissonance
class Counter_N:
    """N(s, target) = the number of states y with no violated line and floor(deg_y(v) / 2) = target[v] at every face. Moves keep every
    line agreeing at one face, so x's violated set is empty after the split. Enumeration for small n; a transfer matrix on thin tori."""

    def __init__(self, T):
        self.T, K = T, T.K
        self.n = T.n
        self.thin = T.params not in [tuple(t) for t in H.SL.FANO_TORI]
        # each face's corners as (line, corner), with the points of the corner's two sides
        self.face_corners = [list(K.corners_at[v]) for v in range(T.V)]
        if self.thin:
            slice_of, _ = H.SL.chain(K)
            self.pos = slice_of
            n = self.n
            at = {p: q for q, p in enumerate(slice_of)}
            self.at = at

            def anchor(P):
                sl = {slice_of[p] for p in P}
                for a in range(n):
                    if sl == {a % n, (a + 1) % n, (a + 2) % n}:
                        return a
                raise AssertionError("constraint not on three consecutive slices")
            self.line_anchor = defaultdict(list)
            for i in range(n):
                self.line_anchor[anchor(K.pt[i])].append(i)
            self.face_anchor = defaultdict(list)
            for v in range(T.V):
                P = set()
                for (i, c) in self.face_corners[v]:
                    P.update((K.pt[i][(c + 1) % 3], K.pt[i][(c + 2) % 3]))
                self.face_anchor[anchor(P)].append(v)

    def brute(self, s, target):
        T, K, n = self.T, self.T.K, self.n
        X = np.arange(1 << n, dtype=np.int64)
        ok = np.ones(1 << n, dtype=bool)
        lit = {}
        for i in range(n):
            for k in range(3):
                lit[(i, k)] = (((X >> K.pt[i][k]) & 1) ^ s[3 * i + k]).astype(np.int8)
            ok &= ~((lit[(i, 0)] == lit[(i, 1)]) & (lit[(i, 1)] == lit[(i, 2)]))
        for v in range(T.V):
            dv = np.zeros(1 << n, dtype=np.int8)
            for (i, c) in self.face_corners[v]:
                dv += (lit[(i, (c + 1) % 3)] == lit[(i, (c + 2) % 3)]).astype(np.int8)
            ok &= (dv // 2) == target[v]
        return int(ok.sum())

    def tm(self, s, target):
        n = self.n
        if not hasattr(self, "memo"):
            K = self.T.K
            self.memo = [dict() for _ in range(n)]
            self.keys = []
            for a in range(n):
                es = set()
                for i in self.line_anchor[a]:
                    es.update(3 * i + k for k in range(3))
                for v in self.face_anchor[a]:
                    for (i, c) in self.face_corners[v]:
                        es.update((3 * i + (c + 1) % 3, 3 * i + (c + 2) % 3))
                self.keys.append((sorted(es), list(self.face_anchor[a])))
        mat = np.eye(4, dtype=np.int64)
        for a in range(n):
            es, fs = self.keys[a]
            key = (tuple(s[e] for e in es), tuple(target[v] for v in fs))
            M = self.memo[a].get(key)
            if M is None:
                M = self.memo[a][key] = np.array(self._anchor_matrix(a, s, target), dtype=np.int64)
            mat = mat @ M
        return int(np.trace(mat))

    def _anchor_matrix(self, a, s, target):
        T, K, n = self.T, self.T.K, self.n
        if True:
            pts = [self.at[a % n], self.at[(a + 1) % n], self.at[(a + 2) % n]]
            allowed = []
            for b in range(8):
                val = {pts[0]: (b >> 2) & 1, pts[1]: (b >> 1) & 1, pts[2]: b & 1}
                good = True
                for i in self.line_anchor[a]:
                    L = [val[K.pt[i][k]] ^ s[3 * i + k] for k in range(3)]
                    if L[0] == L[1] == L[2]:
                        good = False
                        break
                if good:
                    for v in self.face_anchor[a]:
                        dv = 0
                        for (i, c) in self.face_corners[v]:
                            k1, k2 = (c + 1) % 3, (c + 2) % 3
                            dv += (val[K.pt[i][k1]] ^ s[3 * i + k1]) == (val[K.pt[i][k2]] ^ s[3 * i + k2])
                        if dv // 2 != target[v]:
                            good = False
                            break
                allowed.append(good)
            M = [[0] * 4 for _ in range(4)]
            for b in range(8):
                if allowed[b]:
                    M[b >> 1][b & 3] = 1
            return M

    def count(self, c):
        target = [d // 2 for d in c.deg]
        return self.tm(c.s, target) if self.thin else self.brute(c.s, target)


# ---------------------------------------------------------------------------------------------------- the rules
def sight_first_moves(T, c, r):
    """the first moves of the shortest sequences (at most r moves of one hole) that end by absorbing, or [] if none"""
    best, firsts = None, []

    def rec(cc, h, depth, first):
        nonlocal best, firsts
        for m in moves_of(T, cc, h):
            f0 = first or m
            if absorbs(cc, m):
                if best is None or depth < best:
                    best, firsts = depth, [f0]
                elif depth == best and f0 not in firsts:
                    firsts.append(f0)
                continue
            if depth < r and (best is None or depth < best):
                d, _ = apply(T, cc, m)
                rec(d, m[2], depth + 1, f0)
    for h in c.holes():
        rec(c, h, 1, None)
    return firsts


def run(T, cnt, c0, rule, rng, budget):
    c, moves, steps = c0.copy(), [], 0
    while not c.resolved():
        if steps >= budget:
            return False, steps, moves
        if rule == "R0":
            m = rng.choice(all_moves(T, c))
        elif rule in ("R1", "R2", "R3"):
            fm = sight_first_moves(T, c, int(rule[1]))
            m = rng.choice(fm) if fm else rng.choice(candidates(T, c))
        else:
            cand = candidates(T, c)
            ab = [mv for mv in cand if absorbs(c, mv)] if rule == "R5" else []
            if ab:
                m = rng.choice(ab)
            else:
                scored = [(cnt.count(apply(T, c, mv)[0]), mv) for mv in cand]
                key = min(sc for sc, _ in scored) if rule == "R6" else max(sc for sc, _ in scored)
                m = rng.choice([mv for sc, mv in scored if sc == key])
        c, mk = apply(T, c, m)
        moves.append(mk)
        steps += 1
    return True, steps, moves


def replay_ok(T, s2, x, moves, s0):
    sf, local = T.replay(s2, x, moves)
    viol, dg, D, E = T.tally(sf, x)
    z = [a ^ b for a, b in zip(sf, s0)]
    return bool(local and not viol and E == 0 and not D and T.label(z) != (0, 0))


def main():
    if os.environ.get("PYTHONHASHSEED") != "0":
        os.execve(sys.executable, [sys.executable, "-B"] + sys.argv, {**os.environ, "PYTHONHASHSEED": "0"})
    tori = [H.Torus(*t) for t in H.class_forced_tori(40)]
    st = starts(tori)
    log("starts", sum(len(v) for v in st.values()))
    rng = random.Random(1110)
    RES = {"verification": [], "rules": [], "diagnostic": []}
    entropic = {T.name for T in tori if T.params in [tuple(t) for t in H.SL.FANO_TORI] or (T.params[1:] == (1, 1))}

    # transfer matrix against enumeration
    vr = random.Random(7)
    for T in tori:
        if T.n > 20:
            continue
        cnt = Counter_N(T)
        if not cnt.thin:
            continue
        s0 = T.classes[T.forced[0]]
        agree = 0
        for j in range(20):
            x, k = st[T.name][vr.randrange(len(st[T.name]))]
            s2, f, deg, l0, w0 = T.split(s0, x, k)
            c = Conf(f, deg, s2)
            for _ in range(vr.randrange(11)):
                if c.resolved():
                    break
                c, _ = apply(T, c, vr.choice(all_moves(T, c)))
            target = [d // 2 for d in c.deg]
            agree += cnt.tm(c.s, target) == cnt.brute(c.s, target)
        RES["verification"].append({"torus": T.name, "configurations": 20, "transfer matrix = enumeration": agree})
    log("verified", all(r["transfer matrix = enumeration"] == 20 for r in RES["verification"]))

    for T in tori:
        cnt = Counter_N(T) if T.name in entropic else None
        s0 = T.classes[T.forced[0]]
        row = {"torus": T.name, "points": T.n}
        res = defaultdict(lambda: {"runs": 0, "resolved": 0, "steps": [], "replay failures": 0})
        diag = defaultdict(list)
        for j, (x, k) in enumerate(st[T.name]):
            s2, f, deg, l0, w0 = T.split(s0, x, k)
            c0 = Conf(f, deg, s2)
            rules = [("R0", 50 * T.V * T.V), ("R1", 50 * T.V * T.V), ("R2", 50 * T.V * T.V), ("R3", 50 * T.V * T.V)]
            if cnt is not None and j < 50:
                rules += [("R4", 20 * T.V), ("R5", 20 * T.V), ("R6", 20 * T.V)]
            for rule, budget in rules:
                ok, steps, moves = run(T, cnt, c0, rule, rng, budget)
                r = res[rule]
                r["runs"] += 1
                if ok:
                    r["resolved"] += 1
                    r["steps"].append(steps)
                    r["replay failures"] += not replay_ok(T, s2, x, moves, s0)
            ok, steps, moves = T.run_rule(f, deg, w0, "no_reversal", rng, 50 * T.V * T.V)
            r = res["R7"]
            r["runs"] += 1
            if ok:
                r["resolved"] += 1
                r["steps"].append(steps)
                r["replay failures"] += not replay_ok(T, s2, x, moves, s0)
            # the diagnostic: N along a random walk, before the first absorption
            if cnt is not None and j < 50:
                c, dt = c0.copy(), T.dist(w0)
                for _ in range(200):
                    hs = c.holes()
                    if len(hs) < 2 or c.deg[w0] != 3:
                        break
                    diag[min(dt[h] for h in hs)].append(math.log(cnt.count(c)))
                    c, _ = apply(T, c, rng.choice(all_moves(T, c)))
        for rule in sorted(res):
            r = res[rule]
            row[rule] = {"runs": r["runs"], "resolved": r["resolved"], "replay failures": r["replay failures"],
                         "mean steps": round(float(np.mean(r["steps"])), 2) if r["steps"] else None}
        RES["rules"].append(row)
        if diag:
            RES["diagnostic"].append({"torus": T.name, "mean log N by distance": {d: [round(float(np.mean(v)), 3), len(v)]
                                                                                 for d, v in sorted(diag.items())}})
        log(T.name, {k: (row[k]["resolved"], row[k]["runs"], row[k]["mean steps"]) for k in row if k.startswith("R")})

    # decisions
    rows = RES["rules"]
    big = [r for r in rows if r["points"] >= 10]
    every = lambda rule, rs: all(r[rule]["resolved"] == r[rule]["runs"] for r in rs if rule in r)  # noqa: E731
    beats = lambda rule, rs: all(r[rule]["mean steps"] is not None and r[rule]["mean steps"] < r["R0"]["mean steps"]  # noqa: E731
                                 for r in rs if rule in r)
    falls = all(r["R1"]["mean steps"] >= r["R2"]["mean steps"] >= r["R3"]["mean steps"] for r in big)
    diag_falls = []
    for d in RES["diagnostic"]:
        ds = sorted(d["mean log N by distance"])
        vals = [d["mean log N by distance"][k][0] for k in ds]
        diag_falls.append(all(a >= b for a, b in zip(vals, vals[1:])))
    ebig = [r for r in big if "R4" in r]
    RES["decisions"] = {
        "F1: R1-R3 resolve every run": all(every(x, rows) for x in ("R1", "R2", "R3")),
        "F1: R1-R3 beat R0 on every torus of >= 10 points": all(beats(x, big) for x in ("R1", "R2", "R3")),
        "F1: mean steps fall with r on every torus of >= 10 points": falls,
        "F2: R4 resolves every run": every("R4", rows),
        "F2: R5 resolves every run": every("R5", rows),
        "F2: R4 beats R0 on every R4 torus of >= 10 points": beats("R4", ebig) and every("R4", ebig),
        "F2: R5 beats R0 on every R4 torus of >= 10 points": beats("R5", ebig) and every("R5", ebig),
        "F2 diagnostic: mean log N falls with distance on every R4 torus": all(diag_falls),
        "F3: R6 slower than R0 or fails some run on some torus": not (every("R6", rows) and beats("R6", ebig)),
        "every resolved run replays": all(r[k]["replay failures"] == 0 for r in rows for k in r if k.startswith("R")),
        "R7 resolves every run": every("R7", rows),
    }
    RES["seconds"] = round(time.time() - T0, 1)
    OUT.mkdir(parents=True, exist_ok=True)
    (OUT / "result.json").write_text(json.dumps(RES, indent=1, default=str) + "\n")
    log("wrote", OUT / "result.json", json.dumps(RES["decisions"], indent=1))


if __name__ == "__main__":
    main()
