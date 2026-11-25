"""Run BG (PB16, the controls of the readings) and run B0 (PB17, ticket A's run 2 results re-read).

BG: Y alone of two-22 and of one-2 under COPY-LAW(t), no taking rule, both knot laws: the parts of its form after rounds 1
to 8; version 1's worked case (X one-2, Y two-22, W3, COPY-LAW(CANCEL-RETIRE)): its births and descents, its round-0
roster against three-222 alone's, and under not-all-equal the two-knot parts descended from both at every round against
three-222 alone's parts of that form.
B0: in ticket A's run 2 results file, the parts the same as the run's own Y by descent at every round.

usage: python -B bg.py
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P

PB16 = {('two-22', 'RETIRE'): [0, 2, 0, 4, 0, 8, 0, 16], ('two-22', 'OFFSHOOT'): [0, 2, 1, 4, 4, 9, 12, 22],
        ('two-22', 'WAIT'): [0, 2, 0, 5, 0, 12, 0, 29], ('one-2', 'RETIRE'): [0] * 8,
        ('one-2', 'OFFSHOOT'): [0, 0, 1, 0, 2, 1, 4, 4], ('one-2', 'WAIT'): [0, 0, 0, 1, 0, 2, 0, 5]}


def own_form_counts(S0, mem, law, base, forms):
    R0 = pm.roster_of(S0.copy(), law)
    part = next(p for p in R0.parts if set(mem) <= set(p))
    f = forms.classify(R0, part)
    run = mcb.grow(S0, law, base)
    out = []
    for t in range(1, run.rounds_done + 1):
        R = mcb.roster_or_none(run.snap[t], law)
        out.append(None if R is None else sum(1 for p in R.parts if forms.classify(R, p) == f))
    return f, out, run


def controls():
    res = {}
    ok = True
    for (kind, t), want in PB16.items():
        for kl in ('nae', 'parity'):
            base = 'COPY-LAW(%s)' % t
            law = mcb.law1(base, kl)
            forms = mcb.Forms()
            S0, mem = mcb.alone_b(kind, 'Y alone')
            f, got, run = own_form_counts(S0, mem, law, base, forms)
            eq = got == want
            ok = ok and eq
            res['%s alone | %s | %s' % (kind, mcb.bl(base) if hasattr(mcb, 'bl') else base, kl)] = {
                'counts': got, 'P B16': want, 'equal': eq, 'knot fails': mc.knot_tests_A(run)['n_fails']}
    return ok, res


def worked_case():
    key = 'one-2 + two-22 / W3'
    out = {}
    base = 'COPY-LAW(RETIRE)'
    S0, X, Y = mcb.start_b(key)
    SA, memA = mcb.alone_b('three-222', 'Y alone')
    for kl in ('nae', 'parity'):
        law = mcb.law1(base, kl)
        forms = mcb.Forms()
        mforms = mcb.Forms()
        A = mcb.grow(S0, law, base)
        B = mcb.grow(SA, law, base)
        R0, RA0 = pm.roster_of(S0.copy(), law), pm.roster_of(SA.copy(), law)
        r0 = sorted(Counter(mforms.classify(R0, p) for p in R0.parts).items())
        ra0 = sorted(Counter(mforms.classify(RA0, p) for p in RA0.parts).items())
        # the two-knot part's form: Y alone of two-22 at round 0
        S2, mem2 = mcb.alone_b('two-22', 'Y alone')
        R2 = pm.roster_of(S2.copy(), law)
        f2 = forms.classify(R2, next(p for p in R2.parts if set(mem2) <= set(p)))
        births, rows = [], []
        for t in range(1, max(A.rounds_done, B.rounds_done) + 1):
            row = {'t': t}
            if t <= A.rounds_done:
                S = A.snap[t]
                desc = mc.descent_map(S, X, Y, 0)
                R = mcb.roster_or_none(S, law)
                if R is not None:
                    row['run A: two-knot parts from both'] = sum(
                        1 for p in R.parts if forms.classify(R, p) == f2 and all(desc.get(u) == 'both' for u in p))
                    row['run A: two-knot parts, any descent'] = sum(1 for p in R.parts if forms.classify(R, p) == f2)
                row['run A: members'] = len(mcb.members_now(S))
                for b in A.records[t - 1]['births']:
                    births.append({'round': t, 'knot': b['id'], 'kind': b['kind'], 'parents': b['parents'],
                                   'parents\' descents': [mc.descent_map(A.snap[t - 1], X, Y, 0).get(p)
                                                          for p in b['parents']],
                                   'inputs': b['inputs'], 'fresh': b['fresh'], 'implied': b['implied'],
                                   'descent': desc.get(b['id'])})
                row['run A closes'] = bool(A.records[t - 1]['closing'])
            if t <= B.rounds_done:
                RB = mcb.roster_or_none(B.snap[t], law)
                if RB is not None:
                    row['three-222 alone: two-knot parts'] = sum(1 for p in RB.parts if forms.classify(RB, p) == f2)
            rows.append(row)
        out[kl] = {'round-0 roster the same as three-222 alone\'s': len(r0) == len(ra0) and _same_unmarked(R0, RA0),
                   'rounds (run A, three-222 alone)': [A.rounds_done, B.rounds_done], 'per round': rows,
                   'births of run A (first 40)': births[:40], 'knot fails': mc.knot_tests_A(A)['n_fails']}
    nae = out['nae']['per round']
    out['under not-all-equal, run A from both equals three-222 alone, round by round'] = all(
        r.get('run A: two-knot parts from both') == r.get('three-222 alone: two-knot parts') for r in nae
        if 'three-222 alone: two-knot parts' in r and 'run A: two-knot parts from both' in r)
    out['under not-all-equal, at rounds 4, 6, 8'] = [next((r.get('run A: two-knot parts from both') for r in nae
                                                           if r['t'] == t), None) for t in (4, 6, 8)]
    par = out['parity']
    out['under parity, the round-2 join of three parents closes and leaves nothing'] = any(
        b['round'] == 2 and b['kind'] == 'join' and len(b['parents']) == 3 and b['implied']
        for b in par['births of run A (first 40)']) and par['rounds (run A, three-222 alone)'][0] <= 2 or any(
        r['t'] == 2 and r.get('run A closes') and r.get('run A: members') == 0 for r in par['per round'])
    return out


def _same_unmarked(R1, R2):
    f = mcb.Forms()
    return sorted(Counter(f.classify(R1, p) for p in R1.parts).items()) == \
        sorted(Counter(f.classify(R2, p) for p in R2.parts).items())


def b0():
    """PB17: ticket A's run 2 results, the parts the same as the run's own Y by descent (D 3.1's reading)."""
    sys.path.insert(0, mcb.A_DIR)
    import common as CA
    rows = CA.read_jsonl('run2.jsonl.gz')
    c = Counter()
    c_no_ex = Counter()
    for r in rows:
        for name, d in r['designs'].items():
            for pr in d.get('per_round', []):
                for k, n in pr['form']['by_descent'].items():
                    c[k] += n
                    if name != 'made-2-exchanged':
                        c_no_ex[k] += n
    pairs = Counter()
    pairs_no_ex = Counter()
    for r in rows:
        for name, d in r['designs'].items():
            for pr in d.get('per_round', []):
                for k, n in pr['form']['by_descent'].items():
                    if n:
                        pairs[k] += 1
                        if name != 'made-2-exchanged':
                            pairs_no_ex[k] += 1
    return {'laws': len(rows), 'parts by descent (all designs)': dict(c),
            'pairs of a run and a round, by descent (all designs)': dict(pairs),
            'pairs of a run and a round, by descent (without made-2-exchanged)': dict(pairs_no_ex),
            'parts by descent (without made-2-exchanged)': dict(c_no_ex),
            'PB17': 'holds' if not c.get('both') and not c.get('mixed') else 'fails'}


def main():
    cb.cap_memory(7)
    ok, res = controls()
    wc = worked_case()
    out = {'PB16 controls': {'all equal': ok, 'rows': res}, 'PB16 worked case': wc, 'PB17': b0()}
    cb.write_json('bg.json', out)
    cb.log('PB16 controls equal:', ok, '; worked case:', wc['under not-all-equal, at rounds 4, 6, 8'],
           wc['under not-all-equal, run A from both equals three-222 alone, round by round'],
           wc['under parity, the round-2 join of three parents closes and leaves nothing'], '; PB17:',
           out['PB17']['PB17'])


if __name__ == '__main__':
    main()
