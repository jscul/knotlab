"""Birth-by-birth listings of cases where this engine's result differs from a number under "Known before the runs"
(brief, item 6): every round's groups, owing, short members and births (as gate_listing_b.txt), then, for each s,
the parts after round s, their classes, and every meeting of a pair of them with its round, how it was found and its
linking set.

  python -B replay.py <start> <law id> <knot law> [rounds]
"""
import sys

sys.dont_write_bytecode = True

import common
import eng
import gate
import read


def listing(sname, lid, kl, rounds=7):
    st = common.load('starts.json')
    fam = {L['id']: L for L in common.load('family.json')['search']}
    L = fam[lid]
    law = eng.Law(L['ration'], L['treatment'], L['take'], kl)
    stars = st['stars'][sname] if sname in st['stars'] else st['extra']['stars']
    run = eng.run_stars(stars, law, rounds=rounds)
    lines = ['=== %s, %s (%s), rounds 1..%d; stop %s' % (sname, law.name(), lid, run.rounds_read, run.stop)]
    for rec in run.recs:
        lines += gate.round_lines(rec)
        lines.append('   candidates: %s' % [(b['id'], [c[0] for c in b['cands']]) for b in rec['births'] if b['cands']])
    keys = read.Keys(run)
    for s in (1, 2, 3, 4):
        if run.rounds_read <= s:
            lines.append(' s = %d: not read past round s' % s)
            continue
        R = run.recs[s]['roster']
        parts = eng.roster_parts(R)
        mp = {u: i for i, P in enumerate(parts) for u in P}
        cls = eng.classes_of_parts(run.snaps[s], parts)
        bits = read.desc_bits(run, s, mp)
        meet = read.first_meetings(run, s, bits)
        lines.append(' s = %d: parts %s; classes %s' % (s, [list(P) for P in parts], cls))
        for (a, b), (t, how) in sorted(meet.items()):
            wholly = cls[a] != cls[b]
            v = read.View(run, keys, bits, a, b, s, parts[a], parts[b])
            Lk = read.linking(v, t, read.RoundIndex(run.recs[t - 1], bits), read.ancestor_bits(run.snaps[t]))
            lines.append('   parts %d and %d (wholly apart: %s) meet at round %d by %s; linking %s; %s' % (
                a, b, wholly, t, '/'.join(how), [(x['knot'], x['made'], x['class']) for x in Lk['linking']],
                Lk['link_verdict']))
        if not meet:
            lines.append('   no pair of these parts meets by round %d' % run.rounds_read)
    return lines


if __name__ == '__main__':
    sname, lid, kl = sys.argv[1:4]
    rounds = int(sys.argv[4]) if len(sys.argv) > 4 else 7
    common.check_frozen()
    lines = listing(sname, lid, kl, rounds)
    name = 'listing_%s_%s_%s.txt' % (sname.replace('(', '').replace(')', '').replace(',', '-'), lid, kl)
    with open(common.out_path(name), 'w') as f:
        f.write('\n'.join(lines) + '\n')
    print(name, len(lines))
