"""P2: a value-keyed setting.  One observer's setting is a function f of its three old values (256 functions); the other's
is fixed.

Pooled reading (pre-registered): every old word together with its lawful fresh completions under the birth its own values
select is one finished word, all of equal weight, pooled with no normalisation per setting.  From the full-enumeration joint
tables J_ab (complete records), the other observer's complete-record weights are  P_f[r] = sum_y sum_w J_{a, f(y)}[r, (y, w)]
(Bob keyed; Alice keyed likewise).
Normalized-per-setting reading (reported beside it): the words of the finished structure at (a, b) are weighted by 1 / Z_ab,
the number of allowed words of that finished structure, before pooling.
The change is the total-variation distance between the other observer's complete-record distributions under two functions,
maximised over all ordered pairs of the 256 functions and over the fixed setting, for each observer keyed.  Exact fractions
for every pair within 1e-12 of the float maximum.  The change relative to a fixed setting (pairs with a constant function)
and the six functions keyed to one old value (the earlier policy test) are reported as well."""
import json, itertools
from fractions import Fraction
import numpy as np
import common as c

J = c.load_joint(f'{c.ART}/joint_k1_full.json')
Z = {ab: int(J[ab].sum()) for ab in J}
FUNCS = np.array([[(F >> v) & 1 for v in range(8)] for F in range(256)])      # FUNCS[F, v] = setting chosen at old value v


def truth(F):
    """truth table of a function of the keyed observer's old values v = v1 v2 v3 (v1 high bit), listed for v = 000..111."""
    return ''.join(str((F >> v) & 1) for v in range(8))


def weights(keyed, fixed, reading):
    """(256, 16) integer weights of the other observer's complete record under each function."""
    out = np.zeros((256, 16), dtype=object)
    R = {}
    for s in (0, 1):
        T = J[fixed, s] if keyed == 'Bob' else J[s, fixed].T          # rows: other's complete record; columns: keyed's record
        R[s] = T.reshape(16, 8, 2).sum(2)                             # sum over the keyed observer's fresh value
    Zs = {s: (Z[fixed, s] if keyed == 'Bob' else Z[s, fixed]) for s in (0, 1)}
    for F in range(256):
        w = np.zeros(16, dtype=object)
        for v in range(8):
            s = FUNCS[F, v]
            col = R[s][:, v].astype(object)
            w = w + (col if reading == 'pooled' else col * Zs[1 - s])  # normalized: col / Z_s, scaled by Z_0 Z_1
        out[F] = w
    return out


def exact_tv(p, q):
    P = sum(p); Q = sum(q)
    return sum(abs(Fraction(int(x), int(P)) - Fraction(int(y), int(Q))) for x, y in zip(p, q)) / 2


res = {}
for reading in ('pooled', 'normalized'):
    for keyed in ('Bob', 'Alice'):
        for fixed in (0, 1):
            Wt = weights(keyed, fixed, reading)
            Pf = np.array(Wt, dtype=np.float64); Pf = Pf / Pf.sum(1, keepdims=True)
            D = 0.5 * np.abs(Pf[:, None, :] - Pf[None, :, :]).sum(-1)
            m = D.max()
            cand = np.argwhere(D >= m - 1e-12)
            best = Fraction(0); pairs = []
            for F, G in cand:
                tv = exact_tv(Wt[F], Wt[G])
                if tv > best: best = tv; pairs = [(int(F), int(G))]
                elif tv == best: pairs.append((int(F), int(G)))
            const = max(exact_tv(Wt[F], Wt[0]) for F in range(256))
            const_args = [F for F in range(256) if exact_tv(Wt[F], Wt[0]) == const]
            hid_const = exact_tv(Wt[0], Wt[255])
            single = {}
            for j in range(3):
                for flip in (0, 1):
                    F = sum((((v >> (2 - j)) & 1) ^ flip) << v for v in range(8))
                    single[f'old value {j + 1}' + (' negated' if flip else '')] = str(max(exact_tv(Wt[F], Wt[0]), exact_tv(Wt[F], Wt[255])))
            key = f'{reading}|{keyed} keyed|other fixed at {fixed}'
            res[key] = dict(max_change=str(best), max_change_float=float(best), attaining_pairs=len(pairs),
                            example_pair=[truth(pairs[0][0]), truth(pairs[0][1])],
                            pairs=[[truth(F), truth(G)] for F, G in pairs[:16]],
                            max_change_vs_fixed_setting=str(const), functions_attaining_vs_fixed=[truth(F) for F in const_args[:16]],
                            n_functions_attaining_vs_fixed=len(const_args),
                            change_between_the_two_fixed_settings=str(hid_const), single_value_keyed_vs_fixed=single)
            print(f'{key}: largest change {best} = {float(best):.6f} over {len(pairs)} ordered pairs, e.g. f = {truth(pairs[0][0])} vs '
                  f'g = {truth(pairs[0][1])}; vs a fixed setting {const} ({len(const_args)} functions, e.g. {truth(const_args[0])}); '
                  f'between the two fixed settings {hid_const}; keyed to one old value {single}', flush=True)

summary = {}
for reading in ('pooled', 'normalized'):
    ks = [k for k in res if k.startswith(reading)]
    mx = max(Fraction(res[k]['max_change']) for k in ks)
    summary[reading] = dict(max_change=str(mx), at=[k for k in ks if Fraction(res[k]['max_change']) == mx])
held = Fraction(summary['pooled']['max_change']) > 0
print('summary:', json.dumps(summary))
print('P2:', 'HELD' if held else 'FAILED', '(some value-keyed setting changes the other observer\'s complete record under the pooled reading)')
json.dump(dict(results=res, summary=summary, P2='held' if held else 'failed',
               note='truth tables list the chosen setting for the keyed observer\'s old values 000,001,...,111 (first value bit high)'),
          open(f'{c.ART}/item_p2.json', 'w'), indent=1)
