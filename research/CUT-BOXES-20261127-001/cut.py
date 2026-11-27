"""cut.py OUT.jsonl [--chunk I/C]: cut one link of each twelve-knot closed system that carries a box.  CUT-BOXES-20261127-001.

For each of UPPER-GROWN's twelve-point graphs with a box (out/cubic_12_*.jsonl there, the same seeded generation), one
link chosen by a seeded draw (seed 20261129 plus the graph's position) is cut: its distinction stays with one end knot
and the other end gets a new distinction of its own.  The open system (twelve knots, nineteen distinctions, two loose) is
searched in full for bonds and boxes; each box is read for its upper image and the laws it needs."""
import sys, json, glob, random
from pathlib import Path
HERE = Path(__file__).resolve().parent
UG = HERE.parent / 'UPPER-GROWN-20261127-001'
sys.path.insert(0, str(UG))
import cubic as CU, boxes as BX
RB = BX.RB

if __name__ == '__main__':
    out = sys.argv[1]
    G = {tuple(map(tuple, sorted(map(list, g.edges())))): g for g in CU.graphs(12, 3000, 1012)}
    rows = [json.loads(l) for f in sorted(glob.glob(str(UG / 'out' / 'cubic_12_*.jsonl'))) for l in open(f)]
    rows = sorted([r for r in rows if r['boxes'] > 0], key=lambda r: r['links'])
    if '--chunk' in sys.argv:
        ci, cn = map(int, sys.argv[sys.argv.index('--chunk') + 1].split('/')); pick = list(enumerate(rows))[ci::cn]
    else: pick = list(enumerate(rows))
    with open(out, 'w') as f:
        for pos, r in pick:
            S = [list(k) for k in CU.system(G[tuple(map(tuple, r['links']))])]
            links = sorted({x for k in S for x in k}); cut = random.Random(20261129 + pos).choice(links)
            ends = [i for i, k in enumerate(S) if cut in k]; new = max(links) + 1
            S[ends[1]] = [new if x == cut else x for x in S[ends[1]]]; S = tuple(tuple(k) for k in S)
            b = RB.bonds(RB.Stage(S, 'nae'), 'agree')['bonds']; bx = BX.find_boxes(b)
            recs = [BX.read_box(S, x, len(S)) for x in bx[:50]]
            f.write(json.dumps({'graph': pos, 'boxes before': r['boxes'], 'cut distinction': cut, 'knots at its ends': ends,
                                'bonds': len(b), 'boxes': len(bx),
                                'upper missing exactly one': sum(1 for x in recs if len(x['upper missing']) == 1),
                                'laws needed (sizes)': sorted({len(x.get('laws needed', [])) for x in recs}),
                                'example': recs[:1]}) + '\n'); f.flush()
