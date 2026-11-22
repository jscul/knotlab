"""Count the complete words, trace unread names and certify the two-by-two filter.

Run with the project's Python and SymPy. No study output files are imported.
"""
from itertools import product
from pathlib import Path
from runpy import run_path

import sympy as sp


BITS = tuple(product((0, 1), repeat=3))


def allowed(law, word):
    if law == "parity":
        return sum(word) % 2 == 0
    return len(set(word)) == 2


def environment(law, shared):
    return {e for e in product((0, 1), repeat=2) if allowed(law, (shared, *e))}


def check_source(first, companion, shared_index):
    base = [w for w in BITS if allowed(first, w)]
    env = [environment(companion, value) for value in (0, 1)]
    paths = [(w, e) for w in base for e in sorted(env[w[shared_index]])]
    primary_projection = {w for w, e in paths}
    companion_projection = {(w[shared_index], *e) for w, e in paths}
    assert primary_projection == {w for w in BITS if allowed(first, w)}
    assert companion_projection == {w for w in BITS if allowed(companion, w)}
    size = len(paths)
    expected = {"parity": 2, "nae": 3}[companion]
    assert size == len(base) * expected and len(env[0]) == len(env[1])
    assert env[0] - env[1] and env[1] - env[0]
    # Rows are accessible complete words. The cols are the two unread bits.
    matrix = sp.Matrix([[int((w, e) in paths) for e in product((0, 1), repeat=2)] for w in base])
    reduced = matrix * matrix.T / size
    assert reduced.trace() == 1 and set(reduced.diagonal()) == {sp.Rational(1, len(base))}
    for i, j in product(range(len(base)), repeat=2):
        x, y = base[i][shared_index], base[j][shared_index]
        assert reduced[i, j] == sp.Rational(len(env[x] & env[y]), size)
    # For equal physical evidence in every accessible register, an exclusive
    # unread companion word forbids changing the shared name on that path.
    for w in base:
        s = w[shared_index]
        assert any(not allowed(companion, (1-s, *e)) for e in env[s])
    if first == companion == "nae" and shared_index == 2:
        # The ordinary probabilities of 000 and 111 vanish, yet the coherence
        # between 001 and 110 survives tracing the companion. After partial
        # transpose on b it gives this minor on (000, 111).
        entry = reduced[base.index((0, 0, 1)), base.index((1, 1, 0))]
        minor = sp.Matrix([[0, entry], [entry, 0]])
        assert minor.det() == -sp.Rational(1, 81)
    print(first, companion, ("a" if shared_index == 0 else "b"),
          f"{size}/32 full words; unread overlap {len(env[0] & env[1])}/{expected}")


def check_returns(s):
    # s=a: first retain a as the sole herald value, then transfer c and b
    # to private bits. The physical knot finishes (s,1-s,0) on every path.
    source = sp.Matrix([[int(allowed("nae", (s, c, b))) for b in (0, 1)] for c in (0, 1)])
    for c, b in product((0, 1), repeat=2):
        if source[c, b]:
            stages = [(s, c, b), (s, 1-s, b), (s, 1-s, 0)]
            assert all(allowed("nae", w) for w in stages)
            for law in ("parity", "nae"):
                for e in environment(law, s):
                    assert all(allowed(law, (w[0], *e)) for w in stages)
    # Work after transfer is exactly C/sqrt(3). Force a scalar identity
    # on success by left-multiplication with k C^{-1}.
    gram = source * source.T
    assert gram.trace() == 3 and gram.det() == 1
    small = (3-sp.sqrt(5))/2
    inv = source.inv()
    assert inv * source == sp.eye(2)
    refusal = sp.eye(2) - small * inv.T * inv
    assert sp.simplify(refusal.det()) == 0 and refusal.trace().is_positive
    per_launch = sp.simplify(2 * small / 3)
    assert per_launch == 1-sp.sqrt(5)/3
    return per_launch


def main():
    earlier = Path(__file__).resolve().parents[1] / "ERASURE-AND-CLOSING-SIGNS-20261121-001A"
    canonical = run_path(str(earlier / "ordinary_routes.py"))["_canonical_ternaries"]()
    for name in ("parity", "nae"):
        assert canonical[name]["is_knot"]
    for first, companion, index in product(("parity", "nae"), ("parity", "nae"), (2, 0)):
        check_source(first, companion, index)
    p = check_returns(0)
    assert check_returns(1) == p
    print("Shared a and primary NAE: exact attainable p =", p, "=", p.evalf(8))
    print("Each of the four raw sign records on 00 weighs p/4 before grouping; refusal weighs 1-p.")


if __name__ == "__main__":
    main()
