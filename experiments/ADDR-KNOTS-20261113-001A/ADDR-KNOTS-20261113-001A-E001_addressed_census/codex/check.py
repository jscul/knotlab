"""Checks for proof.md of ADDR-KNOTS-20261113-001B: B0 (one rule on two letters always lives) and the Fano rule on seven letters.
Run: .venv/bin/python -B check.py   (writes result.json next to this file)."""
import itertools, json, os, random, hashlib
import numpy as np
from pysat.solvers import Cadical153

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = 10


def act(aut, word, n):
    """Apply a word of relabelings (applied right to left, 'q0 q1' = q0 after q1) to every binary address of length n.
    aut = (swap bits, successor after reading 0, successor after reading 1); addresses as integers, first letter most significant."""
    sw, d0, d1 = (np.array(v) for v in aut)
    y = np.arange(1 << n, dtype=np.int64)
    for q in reversed(word):
        st = np.full(y.shape, q); out = np.zeros_like(y)
        for i in range(n - 1, -1, -1):
            b = (y >> i) & 1
            out = (out << 1) | (b ^ sw[st]); st = np.where(b == 0, d0[st], d1[st])
        y = out
    return y


def alive(K):
    if len(K) == 0:
        return True
    S = Cadical153()
    for a, b, c in K.tolist():
        S.add_clause([a + 1, b + 1, c + 1]); S.add_clause([-a - 1, -b - 1, -c - 1])
    r = S.solve(); S.delete(); return r


def knots(images):
    T = np.stack(images, 1)
    ok = (T[:, 0] != T[:, 1]) & (T[:, 1] != T[:, 2]) & (T[:, 0] != T[:, 2])
    return np.unique(np.sort(T[ok], 1), axis=0)


def b0_case(aut, triple):
    for n in range(1, LEVELS + 1):
        if not alive(knots([act(aut, w, n) for w in triple])):
            return n
    return None


def words(s):
    return [()] + [(q,) for q in range(s)] + [(q, r) for q in range(s) for r in range(s)]


def automata(s):
    for sw in itertools.product((0, 1), repeat=s):
        for d0 in itertools.product(range(s), repeat=s):
            for d1 in itertools.product(range(s), repeat=s):
                yield (sw, d0, d1)


def main():
    out = {"B0_small": {"cases": 0, "dead": []}, "B0_random": {"cases": 0, "dead": []}, "fano": {}}
    for s in (1, 2):
        for aut in automata(s):
            for tr in itertools.combinations(words(s), 3):
                out["B0_small"]["cases"] += 1
                d = b0_case(aut, tr)
                if d: out["B0_small"]["dead"].append([aut, tr, d])
    rng = random.Random(20261113)
    W3 = words(3)
    for _ in range(2000):
        aut = (tuple(rng.randrange(2) for _ in range(3)), tuple(rng.randrange(3) for _ in range(3)), tuple(rng.randrange(3) for _ in range(3)))
        tr = tuple(rng.sample(W3, 3))
        out["B0_random"]["cases"] += 1
        d = b0_case(aut, tr)
        if d: out["B0_random"]["dead"].append([aut, tr, d])
    # Fano: seven letters, a adds 1 mod 7 to the first letter; rule (e, a, a^3); addresses x = first letter + 7 * rest
    for n in range(1, 5):
        N = 7 ** n; x = np.arange(N); first, rest = x % 7, x // 7
        img = [x, (first + 1) % 7 + 7 * rest, (first + 3) % 7 + 7 * rest]
        out["fano"][n] = "alive" if alive(knots(img)) else "dead"
    ok = not out["B0_small"]["dead"] and not out["B0_random"]["dead"] and all(v == "dead" for v in out["fano"].values())
    out["status"] = "passed" if ok else "failed"
    out["check_sha256"] = hashlib.sha256(open(__file__, "rb").read()).hexdigest()
    json.dump(out, open(os.path.join(HERE, "result.json"), "w"), indent=1, default=list)
    print(out["status"], out["B0_small"]["cases"], len(out["B0_small"]["dead"]), out["B0_random"]["cases"], len(out["B0_random"]["dead"]), out["fano"])


if __name__ == "__main__":
    main()
