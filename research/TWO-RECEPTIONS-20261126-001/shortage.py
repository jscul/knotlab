"""shortage.py: does any law of the record with no number set by hand make a knot short after the start, and do two
patterns joined under it hear later far changes?  Second study of TWO-RECEPTIONS-20261126-001 (README.md, B).

Laws, a short knot waiting: the ordinary count with no take and with each recorded take (MET with the oldest or the
newest candidate, MET-SOLE, STEPS1-SOLE, STEPS2-SOLE, J-EACH-PART); FLOOR1 ("just enough for three places"); the eight
parent-owing rations of the record (eng.RATIONS_OWING).  Pairs: a sample of 100 of the 646 census receivers drawn
with seed 20261126, each against the five senders of the switch census, joined by a meeting through two link knots;
12 rounds, 1,500 knots or the engine's guard at four times the fold engine's limits (takes can give a distinction
hundreds of holders).  Read per round: members short that were made after the start; whether the two patterns'
own members are linked; and, after round 3, one more loose distinction at up to five far members in a linked part
and two in parts not linked, and whether the receiver's own births then differ.

    shortage.py run I0 I1     sample receivers I0..I1-1, a JSON line per pair and law"""
import sys, os, json, random
HERE = os.path.dirname(os.path.abspath(__file__))
LK = os.path.join(HERE, '..', 'LINKED-UNDER-CAP-20261126-001')
sys.path.insert(0, LK)
import linked
second, receivers, ring_line, jam, bench, eng = linked.second, linked.receivers, linked.ring_line, linked.jam, linked.bench, linked.eng
ROUNDS, BOUND = 12, 1500
second.ROUNDS, second.BOUND = ROUNDS, BOUND
bench.MULT = 4          # the engine's guard at four times the fold engine's limits: a run whose rosters explode stops there
LAWS = [('ORD', None, None), ('ORD', 'MET', 'OLDEST'), ('ORD', 'MET', 'NEWEST'), ('ORD', 'MET-SOLE', None), ('ORD', 'STEPS1-SOLE', None),
        ('ORD', 'STEPS2-SOLE', None), ('ORD', 'J-EACH-PART', None), ('FLOOR1', None, None)] + [(r, None, None) for r in eng.RATIONS_OWING]
SEED = 20261126


def law_of(r, take, choice):
    return eng.Law(r, 'CANCEL-WAIT', take, 'nae', choice)


def made_short(g):
    """per round: members short in that round that were made after the start"""
    out = []
    for c in range(len(g.rows)):
        S = g.snaps[c]; R = eng.build_roster(S, eng.live_members(S), 'p', eng.Guard(1000))
        owe = {}
        for q in R.groups:
            for u in q: owe[u] = owe.get(u, 0) + 1
        out.append(sum(1 for u in R.members if owe.get(u, 0) > R.h[u] and S.made[u] > 0))
    return out


def pair(A, B, lw):
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    W = ring_line.Growth(st, ro, law_of(*lw)); W.run(ROUNDS, BOUND)
    lk = linked.linked_rounds(W)
    out = {'A': A, 'B': B, 'law': list(lw), 'rounds': len(W.rows), 'ended': W.stop or 'rounds', 'made short': made_short(W), 'linked': lk, 'changes': []}
    if len(W.rows) > 3 and lk[2] is not None:
        for want, n in ((True, 5), (False, 2)):
            ms, dist = linked.far_members(W, 3, want)
            for u in ms[:n]:
                H = ring_line.fork_at(W, 3); ring_line.mark(H, u); H.run(ROUNDS, BOUND)
                r, m = ring_line.first_own_diff(W, H, 3)
                out['changes'].append({'linked': want, 'sharings': dist.get(u), 'heard': r, 'rounds': m})
    return out


if __name__ == '__main__':
    R = receivers.register()
    sample = sorted(random.Random(SEED).sample(range(646), 100))
    for i in sample[int(sys.argv[2]):int(sys.argv[3])]:
        for B in receivers.SENDERS:
            for lw in LAWS:
                print(json.dumps(pair(R[i][0], B, lw)), flush=True)
