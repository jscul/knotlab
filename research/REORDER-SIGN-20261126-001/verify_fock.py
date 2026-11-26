"""Independent check of the rule-applied-to-readings result with explicit fermionic operators.

Nine modes (old a, b, c = 0, 1, 2; each child's fresh pair 3-4, 5-6, 7-8) in a Fock space of dimension 512, built with
Jordan-Wigner matrices in index order. Nothing here uses the listing or string code of the main checker. The start is the
positive parity knot created in the order a, b, c. Each birth is the physical operator
    K_j = (1 - n_j) (1 + c+_y c+_z)/sqrt2 + n_j (c+_y + c+_z)/sqrt2
applied in commit order (a later birth acts on the left). Readers hold their old mode and their child's first fresh mode.
The ordinary reading is (-1)^n_x. The flip reading is one of the two real Hermitian pair flips: F1 = -i g'_x g_y or
F2 = i g_x g'_y, with g = c + c+ and g' = i(c+ - c).
"""

import json
from itertools import combinations, permutations, product
from pathlib import Path

import numpy as np


MODES = 9
DIM = 2 ** MODES
I2, Z = np.eye(2), np.diag([1.0, -1.0])
LOWER = np.array([[0.0, 1.0], [0.0, 0.0]])  # |0><1| on the occupation basis (0 = empty, 1 = occupied)


def kron_all(ops):
    out = np.array([[1.0]])
    for op in ops:
        out = np.kron(out, op)
    return out


def annihilator(k):
    return kron_all([Z] * k + [LOWER] + [I2] * (MODES - k - 1))


C = [annihilator(k) for k in range(MODES)]
CD = [c.T.copy() for c in C]
N = [CD[k] @ C[k] for k in range(MODES)]
ONE = np.eye(DIM)
VAC = np.zeros(DIM)
VAC[0] = 1.0


def start_state(first_created=(2, 1, 0)):
    """Positive parity knot whose occupied old modes are created in the given physical order (first acts first)."""
    psi = np.zeros(DIM)
    for x in product((0, 1), repeat=3):
        if sum(x) % 2:
            continue
        v = VAC.copy()
        for k in first_created:
            if x[k]:
                v = CD[k] @ v
        psi += v
    return psi / np.linalg.norm(psi)


def relative_parity(order, parents_first):
    rank = {p: i for i, p in enumerate(parents_first)}
    seq = [rank[j] for j in order]
    return sum(1 for i, j in combinations(range(3), 2) if seq[i] > seq[j]) % 2


def birth(j):
    x, y, z = j, 3 + 2 * j, 4 + 2 * j
    return ((ONE - N[x]) @ (ONE + CD[y] @ CD[z]) + N[x] @ (CD[y] + CD[z])) / np.sqrt(2)


def flips(kind):
    out = []
    for j in range(3):
        x, y = j, 3 + 2 * j
        g = lambda k: C[k] + CD[k]
        gp = lambda k: 1j * (CD[k] - C[k])
        op = -1j * gp(x) @ g(y) if kind == "F1" else 1j * g(x) @ gp(y)
        assert np.allclose(op.imag, 0) and np.allclose(op, op.conj().T) and np.allclose(op @ op, ONE)
        out.append(op.real)
    for a, b in combinations(range(3), 2):
        assert np.allclose(out[a] @ out[b], out[b] @ out[a])
    return out


def ordinary():
    return [ONE - 2 * N[j] for j in range(3)]


def correlations(psi, zs, xs):
    out = {}
    for k in (0, 2):
        for T in combinations(range(3), k):
            op = ONE
            for j in range(3):
                op = op @ (xs[j] if j in T else zs[j])
            out[T] = float(psi @ op @ psi)
    return out


def full_contradiction(c):
    sharp = all(abs(abs(v) - 1) < 1e-12 for v in c.values())
    product_p = c[()] * c[(0, 1)] * c[(0, 2)] * c[(1, 2)]
    return sharp and product_p < 0, product_p


def scored_win(psi, zs, xs):
    """Chance of the required parity on the four scored settings, as in the benchmark."""
    total = 0.0
    for setting in ((0, 0, 0), (0, 1, 1), (1, 0, 1), (1, 1, 0)):
        want = int(any(setting))
        for outcome in product((0, 1), repeat=3):
            if sum(outcome) % 2 != want:
                continue
            proj = ONE
            for j in range(3):
                op = xs[j] if setting[j] else zs[j]
                proj = proj @ (ONE + (-1) ** outcome[j] * op) / 2
            total += float(psi @ proj @ psi)
    return total / 4


def mermin_best(c):
    pairs = ((0, 1), (0, 2), (1, 2))
    best = 0.0
    for u in product((0, 1), repeat=3):
        score = c[()] - sum(c[p] * (-1) ** (u[p[0]] + u[p[1]]) for p in pairs)
        best = max(best, abs(score))
    return best


def main():
    zs = ordinary()
    out = {}
    for start_name, first in (("parents_created_c_b_a", (2, 1, 0)), ("parents_created_a_b_c", (0, 1, 2))):
        base = start_state(first)
        for kind in ("F1", "F2"):
            xs = flips(kind)
            rows, grown = {}, {}
            for order in permutations(range(3)):
                psi = base.copy()
                for j in order:
                    psi = birth(j) @ psi
                assert abs(np.linalg.norm(psi) - 1) < 1e-12
                grown[order] = psi
                c = correlations(psi, zs, xs)
                full, p = full_contradiction(c)
                rows["".join("abc"[i] for i in order)] = {
                    "order_parity_relative_to_parents_creation": relative_parity(order, first),
                    "ZZZ_XXZ_XZX_ZXX": [round(c[t], 12) for t in ((), (0, 1), (0, 2), (1, 2))],
                    "product_P": round(p, 12), "full_contradiction": full,
                    "scored_win_fixed_labels": round(scored_win(psi, zs, xs), 12),
                }
            # Order recorded but unknown to the readers: equal mixture of the six histories.
            avg = {T: np.mean([correlations(grown[o], zs, xs)[T] for o in grown]) for T in correlations(base, zs, xs)}
            # Order not recorded: the equal-weight coherent sum of the six histories.
            coherent = sum(grown.values())
            norm = float(np.linalg.norm(coherent))
            occupied_old = sorted({tuple((i >> (MODES - 1 - k)) & 1 for k in range(3))
                                   for i in np.nonzero(np.abs(coherent) > 1e-12)[0]})
            out[f"{start_name}/{kind}"] = {
                "orders": rows,
                "order_blind_best_mermin_score": round(mermin_best(avg), 12),
                "coherent_sum_norm_squared_over_36": round(norm ** 2 / 36, 12),
                "coherent_sum_old_words_present": ["".join(map(str, w)) for w in occupied_old],
            }
    path = Path(__file__).with_name("verify_fock.json")
    path.write_text(json.dumps(out, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(out, indent=1))


if __name__ == "__main__":
    main()
