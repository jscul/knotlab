"""Replays for ticket B's differences from the disclosed numbers and for PB13's failure: replays_b.json.

1. PB11's parts of Y's form of mixed descent under CAP-3(t) within 6 rounds (seen 44: waiting 36, retiring 4,
   offshoots 4): every run and round, with the part's members, their h and k, parents and descents.
2. PB13's R2 under COPY-LAW(t): the first case, round by round, the forms descended from both for each of the eight Y,
   and for the one Y that has them, the births of the parts' members (parents, inputs with their holders, fresh count,
   descents).
3. PB3's step count (seen 55,244): the rounds every run of B5 reached.

usage: python -B replays_b.py
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import cb  # noqa: E402
import mcb  # noqa: E402
import b1  # noqa: E402

mc, pm, K, P = mcb.mc, mcb.pm, mcb.K, mcb.P


def births_of(run, knots_, X, Y):
    out = []
    for t in range(1, run.rounds_done + 1):
        Sb = run.snap[t - 1]
        db = mc.descent_map(Sb, X, Y, 0)
        da = mc.descent_map(run.snap[t], X, Y, 0)
        for b in run.records[t - 1]['births']:
            if b['id'] in knots_:
                out.append({'round': t, 'knot': b['id'], 'kind': b['kind'], 'parents': b['parents'],
                            'parents\' descents': [db.get(p) for p in b['parents']], 'inputs': b['inputs'],
                            'holders of each input at the start of the round': {str(d): list(Sb.holders[d])
                                                                                for d in b['inputs']},
                            'fresh count': b['f'], 'descent': da.get(b['id'])})
    return out


def ancestors(S, u):
    seen, st = set(), [u]
    while st:
        x = st.pop()
        for p in S.parents[x]:
            if p not in seen:
                seen.add(p)
                st.append(p)
    return seen


def mixed():
    rows = []
    for t_ in ('RETIRE', 'OFFSHOOT', 'WAIT'):
        base = 'CAP-3(%s)' % t_
        for kl in ('nae', 'parity'):
            law = mcb.law1(base, kl)
            forms = mcb.Forms()
            yf = {}
            for kind in mcb.KINDS8:
                SA, mem = mcb.alone_b(kind, 'Y alone')
                R0 = pm.roster_of(SA.copy(), law)
                yf[kind] = forms.classify(R0, next(p for p in R0.parts if set(mem) <= set(p)))
            for key in b1.starts_of('main'):
                S0, X, Y = mcb.start_b(key)
                kx, rest = key.split(' + ')
                ky, way = rest.split(' / ')
                A = mcb.grow(S0, law, base, rounds=6)
                for t in range(1, A.rounds_done + 1):
                    S = A.snap[t]
                    R = mcb.roster_or_none(S, law)
                    if R is None:
                        continue
                    desc = mc.descent_map(S, X, Y, 0)
                    for p in R.parts:
                        ds = Counter(desc.get(u) for u in p)
                        if len(ds) > 1 and forms.classify(R, p) == yf[ky]:
                            rows.append({'law': base + ' ' + kl, 'start': key, 'control': kx == ky, 'round': t,
                                         'members (knot, h, k, parents, descent)': [
                                             (u, R.h[u], R.k[u], list(S.parents[u]), desc.get(u)) for u in sorted(p)]})
    pairs = Counter()
    for r in rows:
        pairs[(r['law'].split(' ')[0], r['control'], r['start'], r['law'], r['round'])] += 1
    c = Counter()
    for (b, ctrl, s, l, t) in pairs:
        c['%s | %s' % (b, 'control' if ctrl else 'X other than Y')] += 1
    return {'pairs of a run and a round, by treatment': dict(c), 'rows': rows}


def r2_case():
    base, kl = 'COPY-LAW(RETIRE)', 'parity'
    law = mcb.law1(base, kl)
    forms = mcb.Forms()
    out = {'law': law.name(), 'X': 'one-2', 'way': 'W3', 'per Y': {}}
    for ky in mcb.KINDS8:
        key = 'one-2 + %s / W3' % ky
        S0, X, Y = mcb.start_b(key)
        A = mcb.grow(S0, law, base)
        lists = []
        both_knots = set()
        for t in range(1, A.rounds_done + 1):
            S = A.snap[t]
            R = mcb.roster_or_none(S, law)
            desc = mc.descent_map(S, X, Y, 0)
            lst = Counter()
            for p in R.parts:
                if all(desc.get(u) == 'both' for u in p):
                    lst[mcb.form_text(forms.desc[forms.classify(R, p)])] += 1
                    both_knots |= set(p)
            lists.append({'round': t, 'forms from both': dict(lst)})
        out['per Y'][ky] = {'rounds': A.rounds_done, 'lists': lists}
        if any(x['forms from both'] for x in lists):
            S = A.snap[A.rounds_done]
            anc = set()
            for u in both_knots:
                anc |= ancestors(S, u) | {u}
            out['per Y'][ky]['births of those parts\' members and their ancestors'] = births_of(
                A, {u for u in anc if S.made[u] > 0}, X, Y)
    return out


def steps():
    rows = cb.read_jsonl('b5.jsonl.gz')
    return {r['law']: {kl: v['steps'] for kl, v in r['PB3'].items()} for r in rows}


def main():
    cb.cap_memory(6)
    out = {'PB11 mixed': mixed(), 'PB13 R2, first case': r2_case(), 'PB3 steps per job and knot law': steps()}
    cb.write_json('replays_b.json', out)
    cb.log('mixed:', out['PB11 mixed']['pairs of a run and a round, by treatment'])


if __name__ == '__main__':
    main()
