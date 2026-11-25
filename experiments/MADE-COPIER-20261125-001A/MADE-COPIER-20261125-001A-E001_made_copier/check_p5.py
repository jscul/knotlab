"""P5's first clause, on run 2's runs under COPY-LAW(t) with MET or STEPS-1 (both knot laws; run A of the 12 designs):
every part the same as a member of the design's class (𝒴_made or 𝒴_start, each member's reference from its own run A
under the same law, deviations 4) that contains a member made after round s has as its made members offshoots of start
knots.  Its second clause (no renaming of Y's knots among the made knots) is read from run 2's built-structure reading.

usage: python -B check_p5.py
"""
import os
import sys
from collections import Counter

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import common as C  # noqa: E402
import mc  # noqa: E402
import run2  # noqa: E402

pm, K, P = mc.pm, mc.K, mc.P


def main():
    C.cap_memory(6)
    rows, bad, seen = [], [], Counter()
    for base in mc.BASES_COPY:
        for take in ('MET', 'STEPS-1'):
            for ch in mc.RULES:
                for kl in ('nae', 'parity'):
                    law = mc.make_law(base, take, ch, kl)
                    runs = {}
                    for name in mc.RUN2_DESIGNS:
                        d = mc.design(name)
                        runs[name] = (d,) + run2.run_design(d, law, kl)
                    refs = {'made': {n: runs[n][3] for n in mc.CLASS_MADE if runs[n][3] is not None},
                            'ystart': {n: runs[n][3] for n in mc.CLASS_START if runs[n][3] is not None}}
                    for name, (d, A, view, ref) in runs.items():
                        if ref is None:
                            continue
                        fam = 'made' if name.startswith('made') else 'ystart'
                        for yn, yref in refs[fam].items():
                            for t in range(d.s + 1, A.rounds_done + 1):
                                S = A.snap[t]
                                desc = mc.descent_map(S, d.X, d.Y, d.s)
                                for p_ in mc.form_reading(yref, S, view.roster(t), desc):
                                    made = [u for u in p_['part'] if S.made[u] > d.s]
                                    ok = all(S.kind[u] == 'offshoot' and S.made[S.parents[u][0]] == 0 and
                                             S.kind[S.parents[u][0]] == 'start' for u in made)
                                    seen[(name, yn, take)] += 1
                                    r = {'law': law.name(), 'design': name, 'member': yn, 't': t,
                                         'part': p_['part'], 'made members': made,
                                         'kinds': [S.kind[u] for u in made],
                                         'parents': [list(S.parents[u]) for u in made], 'ok': ok}
                                    rows.append(r)
                                    if not ok:
                                        bad.append(r)
    out = {'P5 first clause': 'holds' if not bad else 'fails', 'parts read': len(rows), 'parts failing': len(bad),
           'failing (first 20)': bad[:20], 'parts by design, member and taking rule':
           {'|'.join(k): v for k, v in sorted(seen.items())}, 'parts (first 40)': rows[:40]}
    C.write_json('check_p5.json', out)
    C.log('P5 first clause:', out['P5 first clause'], len(rows), 'parts,', len(bad), 'failing')


if __name__ == '__main__':
    main()
