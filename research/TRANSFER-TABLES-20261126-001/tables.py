"""tables.py: tables under the recorded transfer law (README.md; frozen in preregistration.md). The law is the
ring-to-end study's (RING-TO-END-20261119-001, experiment E001, transfer.py): ordinary parity growth whose newborns
occupy fresh distinctions according to the parent's values (on an odd input one of a fresh pair; on an even input both
if the parent holds another occupied distinction and the lift mode permits a pair, none otherwise). Founder: one
three-place even knot; one round; the three lift modes (minimum, exact_two, any_pair). Two countings of the reached
states: from the start (the four starts equally weighted, each birth's permitted lifts equally weighted) and from the
finish (every reached state once).

Readers: every split of the distinctions into two readers A, B and an unread rest C, with C of one or two distinctions,
such that no listed law meets both A and B. Per split:
    value reads     each reader's setting a parity of a subset of its distinctions, two settings each: the largest CHSH
                    (the literature's sum of four correlations); signalling: does a reader's answer distribution move
                    with the other's setting
    coherent        the reached states related equally in phase (amplitude the square root of the weight): the reduced
                    state of A + B, its negativity under partial transposition (entangled if positive), the largest CHSH
                    with the model's reads (signed Pauli products on each reader's distinctions: values, changes and
                    combined) and with any reads (a seesaw over all two-valued reads, seeded)
A positive control (two distinctions held by one two-place even law, read by two readers whom that law joins), and the
failing control of the factoring study (each start word divided among all its finished completions at once, under
not-all-equal; the first sampled census start it fails on with at most nine distinctions), under the same coherent test.
    tables.py"""
import sys, json, itertools, random
from fractions import Fraction
from pathlib import Path
import numpy as np
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'experiments/RING-TO-END-20261119-001/RING-TO-END-20261119-001-E001_transfer'))
import transfer                       # noqa: E402

FOUNDERS = (frozenset(), frozenset({0, 1}), frozenset({0, 2}), frozenset({1, 2}))


def reached(mode):
    weights = {}; scopes = None
    for old in FOUNDERS:
        plan = transfer.round_plan(((0, 1, 2),), old)
        first = transfer.realize(plan, mode)
        options = [transfer.lift_options(b, old, mode) for b in first['births']]
        choices = list(itertools.product(*options))
        for choice in choices:
            sel = iter(choice)
            step = transfer.realize(plan, mode, pick=lambda birth, opts: next(sel))
            w = frozenset(step['occupied'])
            weights[w] = weights.get(w, 0) + Fraction(1, len(FOUNDERS) * len(choices))
            scopes = step['stars']
    return weights, [tuple(s) for s in scopes]


def splits(n, scopes):
    out = []
    for size in (1, 2):
        for C in itertools.combinations(range(n), size):
            rest = [d for d in range(n) if d not in C]
            # components of the rest under the laws with C removed
            parent = {d: d for d in rest}
            def find(x):
                while parent[x] != x: x = parent[x]
                return x
            for s in scopes:
                ds = [d for d in s if d in parent]
                for a, b in zip(ds, ds[1:]): parent[find(a)] = find(b)
            comps = {}
            for d in rest: comps.setdefault(find(d), []).append(d)
            comps = list(comps.values())
            for k in range(1, len(comps)):
                for left in itertools.combinations(range(len(comps)), k):
                    A = sorted(d for i in left for d in comps[i]); B = sorted(d for i in range(len(comps)) if i not in left for d in comps[i])
                    if A < B: out.append((tuple(A), tuple(B), C))
    return sorted(set(out))


def chsh_values(dist, A, B):
    """dist: {word (frozenset): prob}. Settings: parities of nonempty subsets; largest |CHSH| and a signalling check"""
    subsA = [s for r in range(1, len(A) + 1) for s in itertools.combinations(A, r)]
    subsB = [s for r in range(1, len(B) + 1) for s in itertools.combinations(B, r)]
    par = lambda w, s: (-1) ** sum(1 for d in s if d in w)
    E = {}
    for sa in subsA:
        for sb in subsB:
            E[(sa, sb)] = float(sum(p * par(w, sa) * par(w, sb) for w, p in dist.items()))
    best = 0.0
    for a0, a1 in itertools.combinations(subsA, 2):
        for b0, b1 in itertools.combinations(subsB, 2):
            c = [E[(a0, b0)], E[(a0, b1)], E[(a1, b0)], E[(a1, b1)]]
            for i in range(4): best = max(best, abs(sum(c) - 2 * c[i]))
    return best


# ---------------------------------------------------------------- the coherent version
PAULI = {'I': np.eye(2), 'X': np.array([[0, 1], [1, 0]]), 'Z': np.array([[1, 0], [0, -1]]), 'Y': np.array([[0, -1j], [1j, 0]])}


def state_vector(dist, n):
    psi = np.zeros(2 ** n)
    for w, p in dist.items():
        psi[sum(1 << (n - 1 - d) for d in w)] = float(p) ** 0.5
    return psi


def reduced(psi, n, keep):
    t = psi.reshape([2] * n)
    rest = [d for d in range(n) if d not in keep]
    t = np.transpose(t, list(keep) + rest).reshape(2 ** len(keep), 2 ** len(rest))
    return t @ t.conj().T


def negativity(rho, na, nb):
    r = rho.reshape(2 ** na, 2 ** nb, 2 ** na, 2 ** nb).transpose(0, 3, 2, 1).reshape(2 ** (na + nb), 2 ** (na + nb))
    ev = np.linalg.eigvalsh((r + r.conj().T) / 2)
    return float(-ev[ev < 0].sum())


def paulis(k):
    out = []
    for labels in itertools.product('IXYZ', repeat=k):
        if all(l == 'I' for l in labels): continue
        M = np.array([[1.0]])
        for l in labels: M = np.kron(M, PAULI[l])
        out.append((''.join(labels), M))
    return out


def pauli_expectations(dist, A, B):
    """<psi| P_A P_B |psi> for every pair of signed Pauli strings on A and on B (identity elsewhere), from the sparse
    coherent state; Y = i X Z on a distinction"""
    amp = {w: float(p) ** 0.5 for w, p in dist.items()}
    Z = sum(a * a for a in amp.values()) ** 0.5; amp = {w: a / Z for w, a in amp.items()}
    def strings(S):
        return [lab for lab in itertools.product('IXYZ', repeat=len(S)) if any(l != 'I' for l in lab)]
    def apply(lab, S, w):
        """P|w> = phase |w'>"""
        ph = 1 + 0j; w2 = set(w)
        for l, d in zip(lab, S):
            bit = d in w2
            if l == 'X': w2 ^= {d}
            elif l == 'Z': ph *= -1 if bit else 1
            elif l == 'Y': ph *= (1j if not bit else -1j); w2 ^= {d}
        return ph, frozenset(w2)
    LA, LB = strings(A), strings(B)
    M = np.zeros((len(LA), len(LB)))
    for j, lb in enumerate(LB):
        for i, la in enumerate(LA):
            tot = 0j
            for w, a in amp.items():
                ph1, w1 = apply(lb, B, w); ph2, w2 = apply(la, A, w1)
                tot += a * ph1 * ph2 * amp.get(w2, 0.0)
            M[i, j] = tot.real
    return M, LA, LB


def chsh_pauli(dist, A, B):
    if len(A) < len(B): A, B = B, A
    M, LA, LB = pauli_expectations(dist, A, B)
    best = 0.0
    for j, k in itertools.combinations(range(len(LB)), 2):
        best = max(best, float(np.abs(M[:, j] + M[:, k]).max() + np.abs(M[:, j] - M[:, k]).max()))
    return best


def chsh_any(rho, na, nb, starts=6, seed=20261130):
    rng = np.random.default_rng(seed); da, db = 2 ** na, 2 ** nb
    def herm_sign(M):
        w, V = np.linalg.eigh((M + M.conj().T) / 2)
        return V @ np.diag(np.where(w >= 0, 1.0, -1.0)) @ V.conj().T
    R = rho.reshape(da, db, da, db)
    def partial_A(Bop):          # Tr_B[rho (I x B)]
        return np.einsum('ijkl,lj->ik', R, Bop)
    def partial_B(Aop):
        return np.einsum('ijkl,ki->jl', R, Aop)
    best = 0.0
    for _ in range(starts):
        Bs = [herm_sign(rng.normal(size=(db, db)) + 1j * rng.normal(size=(db, db))) for _ in range(2)]
        for _ in range(40):
            A0 = herm_sign(partial_A(Bs[0] + Bs[1])); A1 = herm_sign(partial_A(Bs[0] - Bs[1]))
            Bs = [herm_sign(partial_B(A0 + A1)), herm_sign(partial_B(A0 - A1))]
        val = float(np.real(np.trace(rho @ (np.kron(A0, Bs[0] + Bs[1]) + np.kron(A1, Bs[0] - Bs[1])))))
        best = max(best, abs(val))
    return best


def coherent(dist, n, A, B):
    psi = state_vector(dist, n); psi /= np.linalg.norm(psi)
    rho = reduced(psi, n, list(A) + list(B)); na, nb = len(A), len(B)
    out = {'negativity': round(negativity(rho, na, nb), 6), 'CHSH, any reads': round(chsh_any(rho, na, nb), 4),
           "CHSH, the model's reads (Pauli products)": round(chsh_pauli(dist, A, B), 4)}
    return out


def run():
    for mode in ('minimum', 'exact_two'):             # any_pair is the same arm here: every child has two fresh
        weights, scopes = reached(mode)
        n = 1 + max(d for s in scopes for d in s)
        once = {w: Fraction(1, len(weights)) for w in weights}
        allw = [frozenset(d for d in range(n) if v >> d & 1) for v in range(1 << n)]
        allw = [w for w in allw if all(len(w & set(s)) % 2 == 0 for s in scopes)]
        finish = {w: Fraction(1, len(allw)) for w in allw}
        for cname, dist in (('from the start (weights declared)', weights), ('every reached state once', once),
                            ('from the finish (every allowed word of the four laws once: the transfer ignored)', finish)):
            if mode == 'minimum' and cname.startswith('from the finish'): continue
            rows = []
            for A, B, C in splits(n, scopes):
                assert all(not (set(s) & set(A) and set(s) & set(B)) for s in scopes)
                rows.append({'A': A, 'B': B, 'unread': C, 'value reads, largest CHSH': round(chsh_values(dist, A, B), 4),
                             'coherent': coherent(dist, n, A, B)})
            print(json.dumps({'mode': mode, 'counting': cname, 'reached states': len(weights), 'listed laws': scopes,
                              'splits': len(rows),
                              'value reads, largest CHSH over splits': max(r['value reads, largest CHSH'] for r in rows),
                              'coherent: entangled splits': sum(r['coherent']['negativity'] > 1e-9 for r in rows),
                              'coherent: largest CHSH, any reads': max(r['coherent']['CHSH, any reads'] for r in rows),
                              'coherent: largest CHSH, the model\'s reads': max(r['coherent'].get("CHSH, the model's reads (Pauli products)", 0) for r in rows),
                              'rows': rows}), flush=True)
    # the failing control: the first sampled not-all-equal growth on which dividing over the whole growth fails to factor
    sys.path.insert(0, str(HERE.parent / 'FACTOR-WEIGHTS-20261126-001')); sys.path.insert(0, str(HERE.parent / 'FORBID-EDITS-20261126-001'))
    import countings as CT, forbid
    S = forbid.census(); picks = random.Random(20261129).sample(range(len(S)), 300)
    for i in picks:
        stages = [tuple(tuple(k) for k in forbid.supports_of(S[i]))]; rounds_ = []
        for r in range(2):
            new, status, births = forbid.grown(stages[-1], 'nae', 'ordinary')
            if status != 'funded': break
            stages.append(tuple(tuple(k) for k in new)); rounds_.append(births)
        D = sorted({d for k in stages[-1] for d in k})
        if not rounds_ or len(D) > 9: continue
        D, Ws = CT.weightings(stages, rounds_, 'nae')
        if CT.factor_test([list(k) for k in stages[-1]], D, Ws['one stage'])[2] == 0: continue
        ren = {d: j for j, d in enumerate(D)}; scopes = [tuple(ren[d] for d in k) for k in stages[-1]]
        for name in ('one stage', 'start'):
            dist = {frozenset(j for j, v in enumerate(w) if v): x for w, x in Ws[name].items()}
            Z = sum(dist.values()); dist = {k: v / Z for k, v in dist.items()}
            rows = [{'A': A, 'B': B, 'unread': C, 'value reads, largest CHSH': round(chsh_values(dist, A, B), 4),
                     'coherent': coherent(dist, len(D), A, B)} for A, B, C in splits(len(D), scopes)]
            print(json.dumps({'failing control': 'census start %d, not-all-equal, two rounds, %d distinctions' % (i, len(D)),
                              'weighting': name, 'splits': len(rows),
                              'value reads, largest CHSH over splits': max((r['value reads, largest CHSH'] for r in rows), default=None),
                              'coherent: entangled splits': sum(r['coherent']['negativity'] > 1e-9 for r in rows),
                              'coherent: largest CHSH, any reads': max((r['coherent']['CHSH, any reads'] for r in rows), default=None)}), flush=True)
        break
    # positive control: one two-place even law on distinctions 0, 1; readers 0 and 1 (joined by that law)
    dist = {frozenset(): Fraction(1, 2), frozenset({0, 1}): Fraction(1, 2)}
    print(json.dumps({'positive control: one two-place even law, readers it joins': {
        'value reads, largest CHSH': chsh_values(dist, (0,), (1,)), 'coherent': coherent(dist, 2, (0,), (1,))}}), flush=True)
    dist = {frozenset(): Fraction(1, 3), frozenset({1}): Fraction(1, 3), frozenset({0}): Fraction(1, 3)}
    print(json.dumps({'positive control for the model\'s reads: three words 00, 01, 10 equally weighted': {
        'coherent': coherent(dist, 2, (0,), (1,))}}), flush=True)


if __name__ == '__main__':
    run()
