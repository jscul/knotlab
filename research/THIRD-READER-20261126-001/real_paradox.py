"""real_paradox.py: does a three-reader game of certainty exist with real reads only? (README.md, part C.) On g shared
triples (the literature's GHZ state, g copies), each reader holding one qubit of each copy: every choice of two
settings per reader among the real non-identity Pauli products on its qubits (products of values and changes with an
even number of quarter-turns), every one of the eight setting triples whose joint product is a certainty, and whether
those certainties admit a list of values (a GF(2) system on the setting values). One and two copies; two settings
per reader, and three on two copies; each certainty's sign checked against the advisor's lemma (the sum over readers
of half the read's quarter-turn count, so a list always exists); a positive control with signed amplitudes."""
import sys, json, itertools
from pathlib import Path
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'experiments/FOUR-READINGS-20261120-001A/FOUR-READINGS-20261120-001A-E001_signed_rules'))
from census import product            # noqa: E402   i^p X^x Z^z on many qubits


def ghz_stabiliser(g):
    """qubits: reader r's copy c is qubit 3c + r; per copy XXX, ZZI, IZZ"""
    gens = []
    for c in range(g):
        q = [3 * c + r for r in range(3)]
        gens.append((0, sum(1 << j for j in q), 0))
        gens.append((0, 0, (1 << q[0]) | (1 << q[1])))
        gens.append((0, 0, (1 << q[1]) | (1 << q[2])))
    group = {}
    for mask in range(1 << len(gens)):
        acc = (0, 0, 0)
        for i, gg in enumerate(gens):
            if mask >> i & 1: acc = product(acc, gg)
        group[(acc[1], acc[2])] = acc[0]
    return group


def local_reals(g, r):
    """the real non-identity Paulis on reader r's qubits, as Hermitian i^p X^x Z^z (p = x.z mod 4 makes them Hermitian;
    real when x.z is even)"""
    qs = [3 * c + r for c in range(g)]
    out = []
    for xs in itertools.product((0, 1), repeat=g):
        for zs in itertools.product((0, 1), repeat=g):
            x = sum(b << q for b, q in zip(xs, qs)); z = sum(b << q for b, q in zip(zs, qs))
            if x == 0 and z == 0: continue
            if (x & z).bit_count() % 2: continue           # an odd number of quarter-turns: not real
            out.append(((x & z).bit_count() % 4, x, z))
    return out


def paradox(g, settings=2, group=None, check_c=True):
    group = ghz_stabiliser(g) if group is None else group; reals = [local_reals(g, r) for r in range(3)]
    found = 0; tried = 0; example = None
    pairs = [list(itertools.combinations(R, settings)) for R in reals]
    for sa in pairs[0]:
        for sb in pairs[1]:
            for sm in pairs[2]:
                tried += 1
                eqs = []
                for i, j, k in itertools.product(range(settings), repeat=3):
                    P = product(product(sa[i], sb[j]), sm[k])
                    key = (P[1], P[2])
                    if key in group:
                        ph = (P[0] - group[key]) % 4               # P = i^ph * (group element), group element reads +1
                        if ph % 2: continue
                        eqs.append(((1 << i) | (1 << (settings + j)) | (1 << (2 * settings + k)), ph // 2))
                        if check_c: assert ph // 2 == sum(((o[1] & o[2]).bit_count() // 2) for o in (sa[i], sb[j], sm[k])) % 2
                piv = {}; bad = False
                for row, b in eqs:
                    while row:
                        h = row.bit_length() - 1
                        if h in piv: row ^= piv[h][0]; b ^= piv[h][1]
                        else: piv[h] = (row, b); break
                    if not row and b: bad = True
                if bad:
                    found += 1
                    if example is None: example = (sa, sb, sm, len(eqs))
    return {'copies': g, 'setting choices tried': tried, 'games of certainty with real reads': found,
            'example': str(example)}


def signed_control():
    """a positive control with real reads: three distinctions whose amplitude sign is the product of the pairwise values
    (the literature's graph state of three; certainties XZZ, ZXZ, ZZX), where XXX reads -1: a game of certainty"""
    gens = [(0, 0b001, 0b110), (0, 0b010, 0b101), (0, 0b100, 0b011)]
    group = {}
    for mask in range(8):
        acc = (0, 0, 0)
        for i, gg in enumerate(gens):
            if mask >> i & 1: acc = product(acc, gg)
        group[(acc[1], acc[2])] = acc[0]
    return paradox(1, 2, group, check_c=False)


if __name__ == '__main__':
    print(json.dumps({'positive control, signed amplitudes': signed_control()}), flush=True)
    for g, s in ((1, 2), (2, 2), (2, 3)):
        print(json.dumps({**paradox(g, s), 'settings per reader': s}), flush=True)
