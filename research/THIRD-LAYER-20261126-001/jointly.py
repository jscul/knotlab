"""jointly.py OUT.jsonl: the stricter test of a fact held by the whole (the advisor's attack, THIRD-LAYER-20261126-001).
A class fact is *read by no single knot* when no one knot's own class functionals give it (the test of the binding
studies); it is *jointly unread* when it is not even a sum of class facts that single knots read (the layers study's
measure): it lies outside the span of the laws and of every knot's own class functionals.  Read, under both readings
of a small change, for the carriers of every binding the record holds: the 32 built ring families (each ring's own
loose distinctions, rounds 1 to 3, and the new carriers, rounds 2 and 3), the advisor's 14-knot start (rounds 0 to 3),
the ten-knot path witness (round 3) and the held-out eight-knot witness (round 2, start and new carriers)."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BUILT-BINDING-20261126-001'))
import repro as RP, built as BU, families as FA
BD = BU.BD; classes, forbid = RP.classes, RP.forbid


def judge(st, carriers):
    names, idx, rows = RP.space(st); n = len(names); Z = classes.nullspace(rows, n)
    out = {}
    for tag, (_, ix, moves) in (('SHORT', RP.MC.moves_of(st)), ('UPTO5', RP.T2.moves_upto(st, 5))):
        assert ix == idx
        local = []
        for r in st:
            ks = [idx[x] for x in r]
            mrows = [sum(((m >> i) & 1) << j for j, i in enumerate(ks)) for m in moves]
            local.append([sum(((v >> j) & 1) << i for j, i in enumerate(ks)) for v in classes.nullspace(mrows, len(ks))])
        allloc = [v for loc in local for v in loc]; rj = classes.rank(rows + allloc)
        res = []
        for c in carriers:
            f = sum(1 << idx[x] for x in c)
            label = all(bin(f & m).count('1') % 2 == 0 for m in moves) and any(bin(f & z).count('1') % 2 for z in Z)
            single = any(classes.rank(rows + loc + [f]) == classes.rank(rows + loc) for loc in local)
            joint = classes.rank(rows + allloc + [f]) == rj
            res.append({'class fact': label, 'read by one knot': single, 'a sum of single-knot facts': joint})
        out[tag] = res
    return out


def stages(S, rounds):
    st = S; yield 0, st, []
    for t in range(1, rounds + 1):
        st2, status, births = forbid.grown(st, 'parity', 'ordinary')
        if status != 'funded': return
        st = st2; yield t, st, births


if __name__ == '__main__':
    with open(sys.argv[1], 'w') as f:
        def put(r): f.write(json.dumps(r) + '\n'); f.flush(); print(json.dumps(r)[:300], flush=True)
        S, _ = BU.build('base'); rings = BU.build('base')[1]
        for t, st, _ in stages(S, 3): put({'start': 'the 14-knot start', 'round': t, 'carriers': 'ring parities', **judge(st, rings)})
        for label, kw in FA.members():
            S, rings, loose = RP.rings_start(**kw)
            lineage = {k: r for r, ring in enumerate(rings) for k in ring}; prev = None
            for t, st, births in stages(S, 3):
                if len({x for r in st for x in r}) > 400: break
                if t: 
                    car, new = RP.ring_carriers(None, births, lineage); lineage.update(new)
                    put({'start': label, 'round': t, 'carriers': 'start groups', **judge(st, loose)})
                    if prev is not None and len(prev) == len(rings): put({'start': label, 'round': t, 'carriers': 'new', **judge(st, [prev[r] for r in range(len(rings))])})
                    prev = car
        cert = json.load(open(ROOT / 'research/BINDING-20261126-001/referee-R1/path_certificate.json'))
        S = [s for name, s in BD.witnesses() if name.startswith('referee sampled')][0]
        for t, st, _ in stages(S, 3):
            if t == 3: put({'start': 'the ten-knot path witness', 'round': 3, 'carriers': 'paths', **judge(st, cert['path_supports'])})
        h = json.load(open(ROOT / 'research/BUILT-BINDING-20261126-001/referee-R1/heldout_certificate.json'))
        S = forbid.supports_of(forbid.sampled(8, 300, 20261206 + 8)[18])
        for t, st, _ in stages(S, 2):
            if t == 2:
                put({'start': 'the held-out eight-knot witness', 'round': 2, 'carriers': 'start readers', **judge(st, h['carriers'])})
                put({'start': 'the held-out eight-knot witness', 'round': 2, 'carriers': 'new readers', **judge(st, h['new_distinction_carriers'])})
