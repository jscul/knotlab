"""Small one-sided sketch controls, quadratic polar changes of basis, and symbolic path restrictions."""

from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path


ROOT = Path(__file__).resolve().parents[3]
PRIOR = ROOT / "proofs" / "TWO-PRODUCT-SKETCHES-20261115-001A" / "TWO-PRODUCT-SKETCHES-20261115-001A-P001_small_minimax"
spec = spec_from_file_location("predecessor_sketch_points", PRIOR / "solver.py")
points = module_from_spec(spec)
spec.loader.exec_module(points)
affine_hull = points.affine_hull


def require(ok, message):
    if not ok:
        raise ValueError(message)


def parity(v):
    return v.bit_count() & 1


def checksum(x):
    return parity(x & (x >> 1))


def matrix(code, r):
    return tuple((code >> (i * r)) & ((1 << r) - 1) for i in range(r))


def apply(cols, x):
    y = 0
    for i, v in enumerate(cols):
        if x >> i & 1:
            y ^= v
    return y


def bilinear_table(r, code):
    cols = matrix(code, r)
    truth = 0
    for x in range(1 << (2 * r)):
        even = sum(((x >> (2 * j)) & 1) << j for j in range(r))
        odd = sum(((x >> (2 * j + 1)) & 1) << j for j in range(r))
        u = even ^ (even >> 1)
        truth |= parity(u & apply(cols, odd)) << x
    return truth


def anf_truth(n, coefficients):
    truth = 0
    for x in range(1 << n):
        val, monomial = 0, x
        while True:
            val ^= (coefficients >> monomial) & 1
            if not monomial:
                break
            monomial = (monomial - 1) & x
        truth |= val << x
    return truth


def arbitrary_four_tables():
    n = 4
    fixed = sum(1 << i for i in (0, 1, 2, 4, 8, 12))
    canonical = [anf_truth(n, a) for a in range(1 << 16) if not (a & fixed)]
    q = sum(checksum(x) << x for x in range(16))
    changes = {sum((parity(mask & x) ^ constant) << x for x in range(16)) ^ (q if use_q else 0)
               for mask in range(16) for constant in (0, 1) for use_q in (0, 1)}
    require(len(canonical) == 1024 and len(changes) == 64 and
            len({t ^ delta for t in canonical for delta in changes}) == 65536, "four-bit table coverage")
    return canonical


def polar_key(n, truth):
    def at(x): return (truth >> x) & 1
    return sum((at(0) ^ at(1 << i) ^ at(1 << j) ^ at((1 << i) | (1 << j))) << k
               for k, (i, j) in enumerate(combinations(range(n), 2)))


def quadratic_six_classes():
    n, size = 6, 64
    pairs = list(combinations(range(n), 2))
    q = sum(1 << k for k, (i, j) in enumerate(pairs) if j == i + 1)
    qv = [((x << 1) ^ (x >> 1)) & (size - 1) for x in range(size)]
    # Pulling an alternating form A through x -> x + <v,x>_Q v adds
    # (Qv)(Av)^T + (Av)(Qv)^T, encoded above the diagonal.
    shifts = [[sum(((((h >> i) & (g >> j)) ^ ((h >> j) & (g >> i))) & 1) << k
                   for k, (i, j) in enumerate(pairs)) for g in range(size)] for h in qv]
    tables = [bilinear_table(3, code) for code in (0, 1, 2, 10, 11, 12, 94)]
    seen = {}
    for truth in tables:
        seed = polar_key(n, truth)
        seed = min(seed, seed ^ q)
        require(seed not in seen, "two listed quadratic representatives are equivalent")
        seen[seed] = truth
        pending = [seed]
        while pending:
            current = pending.pop()
            cols = [0] * n
            for k, (i, j) in enumerate(pairs):
                if current >> k & 1:
                    cols[i] |= 1 << j
                    cols[j] |= 1 << i
            g = [0] * size
            for v in range(1, size):
                low = v & -v
                g[v] = g[v ^ low] ^ cols[low.bit_length() - 1]
                other = current ^ shifts[v][g[v]]
                other = min(other, other ^ q)
                if other not in seen:
                    seen[other] = truth
                    pending.append(other)
    counts = Counter(seen.values())
    require(len(seen) == 1 << 14 and len(counts) == 7, "quadratic representatives missed a polar form")
    # Direct congruence check on the original Boolean functions, independent of the update formula.
    for truth in tables:
        original = polar_key(n, truth)
        for v in range(size):
            trans = lambda x: x ^ (v if parity(qv[v] & x) else 0)
            recoded = sum(((truth >> trans(x)) & 1) << x for x in range(size))
            av = sum(parity(sum(((original >> k) & 1) << (i if j == t else j)
                                for k, (i, j) in enumerate(pairs) if t in (i, j)) & v) << t
                     for t in range(n))
            require(polar_key(n, recoded) == original ^ shifts[v][av], "transvection did not pull back the form")
            require(all(trans(trans(x)) == x for x in range(size)), "input transvection is not invertible")
    return tables, [counts[t] for t in tables]


def audit_tree(n, truth, tree, fixed_b=None):
    width = n + (1 if fixed_b is not None else 2)
    visible = frozenset(range(1 << width))
    left, right = set(), set()
    for p in visible:
        x = p & ((1 << n) - 1)
        s = (p >> n) & 1
        b = fixed_b if fixed_b is not None else p >> (n + 1)
        if s == checksum(x):
            left.add(p)
        if s != checksum(x) and b == (truth >> x & 1):
            right.add(p)

    def walk(cell, node):
        while cell:
            out = affine_hull(cell & left) & affine_hull(cell & right)
            if out == cell:
                break
            cell = out
        if node is None:
            require(not cell, "a displayed leaf survived repeated whole-relation hulls")
            return 1, 0
        q, lo, hi = node
        require(0 < q < 1 << width, "query coefficient outside the visible roster")
        low = frozenset(p for p in cell if not parity(p & q))
        high = cell - low
        require(low and high, "witness tree includes a constant question")
        nl, dl = walk(low, lo)
        nr, dr = walk(high, hi)
        return nl + nr, 1 + max(dl, dr)
    return walk(visible, tree)


def xor(*polys):
    result = set()
    for p in polys:
        result.symmetric_difference_update(p)
    return result


def mult(p, q):
    # Bit masks denote squarefree monomials of Boolean functions, including the constant 0 mask.
    return xor(*({a | b} for a in p for b in q))


def var(i):
    return {1 << i}


def path_polynomial(images, edge_mask):
    return xor(*(mult(a, b) for i, (a, b) in enumerate(zip(images, images[1:])) if edge_mask >> i & 1))


def half_rank(poly, n):
    cols = [0] * n
    for term in poly:
        require(term.bit_count() <= 2, "rank requires a quadratic")
        if term.bit_count() == 2:
            low = term & -term
            i, j = low.bit_length() - 1, (term ^ low).bit_length() - 1
            cols[i] |= 1 << j
            cols[j] |= 1 << i
    basis = {}
    for v in cols:
        while v:
            j = v.bit_length() - 1
            if j not in basis:
                basis[j] = v
                break
            v ^= basis[j]
    require(len(basis) % 2 == 0, "polar rank must be even")
    return len(basis) // 2


def transfer_checks():
    images = [var(i) for i in range(32)]
    all_edges, a_mask = (1 << 31) - 1, (1 << 14) - 1
    b_mask = sum(1 << i for i in range(15, 30, 2))
    q, a, b = (path_polynomial(images, mask) for mask in (all_edges, a_mask, b_mask))
    pair_ranks = [half_rank(p, 32) for p in (q, a, xor(q, a), b, xor(q, b))]
    require(pair_ranks == [16, 7, 9, 8, 16], "wrong original 31-edge example")
    restricted = [set() for _ in range(14)] + [var(i) for i in range(18)]
    small_q = path_polynomial(restricted[14:], (1 << 17) - 1)
    small_b = path_polynomial(restricted[14:], sum(1 << i for i in range(1, 17, 2)))
    require(path_polynomial(restricted, all_edges) == small_q and not path_polynomial(restricted, a_mask)
            and path_polynomial(restricted, b_mask) == small_b and half_rank(small_q, 18) == 9,
            "restriction did not preserve the concrete one-sided relation")
    # Use independent U_i = even input and V_i = odd_i + odd_{i-1}. Recover odd_i by prefix XOR.
    u = [var(i) for i in range(9)]
    v = [var(i + 9) for i in range(9)]
    original = [x for i in range(9) for x in (u[i], xor(*v[:i + 1]))]
    require(path_polynomial(original, (1 << 17) - 1) == xor(*(mult(ui, vi) for ui, vi in zip(u, v))) and
            path_polynomial(original, sum(1 << i for i in range(1, 17, 2))) ==
            xor(*(mult(u[i], v[j]) for i in range(9) for j in range(i))), "triangular EVEN pencil")
    for setting in range(32):
        z = [({0} if setting >> j & 1 else set()) if j < 5 else v[j] for j in range(9)]
        full_q = xor(*(mult(t, w) for t, w in zip(u, z)))
        full_b = xor(*(mult(u[i], z[j]) for i in range(9) for j in range(i)))
        small_q = xor(*(mult(u[i], z[i]) for i in range(5, 9)))
        small_b = xor(*(mult(u[i], z[j]) for i in range(5, 9) for j in range(5, i)))
        require(all(term.bit_count() <= 1 for term in xor(full_q, small_q) | xor(full_b, small_b)),
                "prefix clearing left a nonlinear correction")
    # A restriction may leave affine radical terms in both reports. Pinning the radical removes
    # them, and an affine checksum correction leaves the exact eighteen-variable matching.
    radial_total = xor(*(mult(var(i), var(9 + i)) for i in range(9)), var(18), var(0), {0})
    radial_sketch = xor(mult(var(1), var(2)), mult(var(3), var(10)), var(18), {0})
    drop_radical = lambda f: {mon for mon in f if not (mon >> 18)}
    require(half_rank(radial_total, 19) == 9 and
            xor(drop_radical(radial_total), var(0), {0}) ==
            xor(*(mult(var(i), var(9 + i)) for i in range(9))) and
            drop_radical(radial_sketch) == xor(mult(var(1), var(2)), mult(var(3), var(10)), {0}),
            "radical pin and affine correction")
    return pair_ranks


def embedding_audit():
    """Check every seven-edge root form's reduction, including all points in both absorption maps."""
    counts = Counter()
    for q in range(1, 1 << 10):
        ell, alpha, beta = q & 255, (q >> 8) & 1, (q >> 9) & 1
        if not (alpha or beta):
            pivot = (ell & -ell).bit_length() - 1
            dirs = [(1 << i) | ((1 << pivot) if ell >> i & 1 else 0) for i in range(8) if i != pivot]
            for answer in (0, 1):
                images = [{1 << j for j, v in enumerate(dirs) if v >> i & 1} |
                          ({0} if i == pivot and answer else set()) for i in range(8)]
                require(half_rank(path_polynomial(images, 127), 7) == 3, "rank on an input hyperplane")
                require(all(t.bit_count() <= 2 for t in path_polynomial(images, 42)), "restricted sketch degree")
            counts["input_rank_three"] += 1
            continue
        if alpha or ell & 129:
            reflected = not alpha and not (ell & 1)
            end_coefficient = (ell >> (7 if reflected else 0)) & 1
            fixed_neighbour = (1 ^ end_coefficient) if alpha else 0
            for answer in (0, 1):
                def embed(p):
                    y, s, b = p & 63, (p >> 6) & 1, (p >> 7) & 1
                    head = (y & 1) | (fixed_neighbour << 1) | (y << 2)
                    if reflected:
                        head = int(f"{head:08b}"[::-1], 2)
                    out_b = b ^ (fixed_neighbour & (y & 1))
                    z = answer ^ parity(ell & head) ^ (alpha & s) ^ (beta & out_b)
                    out_x = head ^ (z << (7 if reflected else 0))
                    return out_x | ((s ^ (z & fixed_neighbour)) << 8) | (out_b << 9)
                origin = embed(0)
                cols = [origin ^ embed(1 << j) for j in range(8)]
                for p in range(256):
                    out = embed(p)
                    y, s, b = p & 63, (p >> 6) & 1, (p >> 7) & 1
                    x, old_s, old_b = out & 255, (out >> 8) & 1, out >> 9
                    require(out == origin ^ apply(cols, p) and parity(q & out) == answer,
                            "absorption map is not affine or chose the wrong child")
                    require((s != checksum(y) or old_s == checksum(x)) and
                            (s == checksum(y) or b != parity(y & (y >> 1) & 10) or
                             (old_s != checksum(x) and old_b == parity(x & (x >> 1) & 42))),
                            "a smaller honest point was lost")
            counts["two_rank_three_absorption_maps"] += 1
        else:
            shift = sum(((ell >> j) & 1) << i for k in (1, 3, 5) for i, j in ((k, k + 1), (k + 1, k)))
            change = lambda x: parity(x & (x >> 1) & 42)
            require(all(change(x ^ shift) ^ change(x) == parity(ell & x) ^ change(shift) for x in range(256)),
                    "root query is not equivalent to the pure sketch bit")
            counts["translated_pure_sketch"] += 1
    require(counts == {"input_rank_three": 255, "two_rank_three_absorption_maps": 704,
                       "translated_pure_sketch": 64}, "root forms were missed")
    return dict(counts)


def rank_nine_maps():
    """Build original-coordinate embeddings, including reduction of a residual rank above nine."""
    def symplectic(poly, directions):
        terms = [tuple(i for i in range(max(directions).bit_length()) if mon >> i & 1)
                 for mon in poly if mon.bit_count() == 2]

        def polar(u, v):
            return sum((((u >> i) & (v >> j)) ^ ((u >> j) & (v >> i))) & 1 for i, j in terms) & 1

        pairs, pending, radical = [], list(directions), []
        while pending:
            u = pending.pop(0)
            partner = next((j for j, v in enumerate(pending) if polar(u, v)), None)
            if partner is None:
                radical.append(u)
                continue
            v = pending.pop(partner)
            pending = [w ^ (u if polar(w, v) else 0) ^ (v if polar(w, u) else 0) for w in pending]
            pairs.append((u, v))
        return pairs, radical

    def substitute(poly, dirs, n):
        images = [{1 << j for j, v in enumerate(dirs) if v >> i & 1} for i in range(n)]
        terms = []
        for mon in poly:
            term = {0}
            while mon:
                low = mon & -mon
                term = mult(term, images[low.bit_length() - 1])
                mon ^= low
            terms.append(term)
        return xor(*terms)

    n = 32
    original = [var(i) for i in range(n)]
    total = path_polynomial(original, (1 << 31) - 1)
    extra = xor(path_polynomial(original, 0x324789AB), mult(var(1), var(3)),
                mult(var(2), var(4)), var(9), {0})
    q_target = xor(*(mult(var(2 * j), var(2 * j + 1)) for j in range(9)))
    examples = []
    for mask in ((1 << 14) - 1, 0b11111, 0b100001101, 0, 0x54015):
        low = path_polynomial(original, mask)
        groups, radical = symplectic(low, [1 << i for i in range(n)])
        require(len(groups) <= 7 and len(radical) + 2 * len(groups) == n, "bad low-rank decomposition")
        isotropic = [u for u, v in groups] + radical
        require(all(t.bit_count() <= 1 for t in substitute(low, isotropic, n)), "small sketch failed to linearize")
        sub_q = substitute(total, isotropic, n)
        more, free = symplectic(sub_q, [1 << i for i in range(len(isotropic))])
        require(len(more) >= 16 - len(groups) and len(free) + 2 * len(more) == len(isotropic),
                "restriction destroyed too much total rank")
        exact = [apply(isotropic, t) for p in more[:9] for t in p]
        residual_q = substitute(total, exact, n)
        residual_low = substitute(low, exact, n)
        residual_extra = substitute(extra, exact, n)
        correction = xor(residual_q, q_target)
        require(all(t.bit_count() <= 1 for t in correction | residual_low)
                and all(t.bit_count() <= 2 for t in residual_extra), "wrong canonical rank-nine reports")

        def evaluate(poly, point):
            return sum((point & mon) == mon for mon in poly) & 1

        for j in range(257):
            y = (j * 8221) & ((1 << 18) - 1)
            x = apply(exact, y)
            require(evaluate(total, x) == (evaluate(q_target, y) ^ evaluate(correction, y)) and
                    evaluate(low, x) == evaluate(residual_low, y) and
                    evaluate(extra, x) == evaluate(residual_extra, y), "raw image failed the visible correction")
        examples.append({"low_half_rank": len(groups), "residual_half_rank_before_trim": len(more),
                         "residual_radical_dimension": len(free), "retained_pairs": 9})
    return examples
