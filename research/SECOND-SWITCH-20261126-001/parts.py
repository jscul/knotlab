"""parts.py: are the far end's members linked to the switch receiver's own members?  A part is a class of the roster's
joinable relation (members linked through groups), and two parts are linked when a member of each holds one
distinction (the fold study's classes, FD 1.6); that study found that parts sharing nothing never become one part
again under the recorded laws (PARTS-MEET-AGAIN-20261124-001).  Read here with the classes.  For the runs of second.py (the far end's
five nearest members), of waiting_far.py (its nearest waiting member) and of the horizon: the round from which the
receiver's own members and the changed knot are in different parts."""
import sys, os, json, gzip
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import second
receivers, ring_line, again, jam, bench, eng = second.receivers, second.ring_line, second.again, second.jam, second.bench, second.eng
receivers.register()
A = 'tri:122@0'; bench.STARS[A], bench.SITE[A] = second.tri(1), 0

def first_apart(A, B, ration, rounds=16):
    """per round: is some member of B's own in a part holding a member of A's own?"""
    st, ro, _ = jam.changed(A, B, 3, None, 'meeting')
    g = ring_line.Growth(st, ro, jam.law_of(ration, 'CANCEL-WAIT')); g.run(rounds, 3000)
    out = []
    for c in range(1, len(g.rows) + 1):
        S = g.snaps[c]; R = eng.build_roster(S, eng.live_members(S), 'parts', eng.Guard(1000), parts=True)
        cl = eng.classes_of_parts(S, R.parts)                   # parts linked when members of each hold one distinction
        pa = {cl[R.part_of[u]] for u in R.members if ring_line.cls(g.anc[u]) == 'A'}
        pb = {cl[R.part_of[u]] for u in R.members if ring_line.cls(g.anc[u]) == 'B'}
        out.append(None if not pa or not pb else bool(pa & pb))
    return out

if __name__ == '__main__':
    res = {}
    for a, B, law in [(1, 'g3:22@0', 'CAP-3'), (1, 'g1:3@0', 'CAP-3')]:
        res['%s %s' % (B, law)] = first_apart(A, B, law)
    rows = [json.loads(l) for l in open(os.path.join(HERE, 'waiting_far_runs.jsonl'))]
    for B in sorted({r['B'] for r in rows}):
        res[B + ' CAP-3'] = first_apart(A, B, 'CAP-3')
    json.dump(res, open(os.path.join(HERE, 'parts.json'), 'w'), indent=0)
    import collections
    first_false = collections.Counter(next((i + 1 for i, x in enumerate(v) if x is False), None) for v in res.values())
    ever_true_after = sum(1 for v in res.values() if any(x for x in v[3:]))
    print('far ends read', len(res), 'first round apart', dict(first_false), 'in a shared part after round 3:', ever_true_after)
    for k, v in list(res.items())[:4]: print(k, v)
