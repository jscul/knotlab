"""grow_list.py LAW IN.jsonl OUT.jsonl [ROUNDS]: grow each start listed in IN (one JSON object with 'stars' per line) to
ROUNDS (default 24) under LAW with the look-alike study's growth, unchanged; the 30,000-knot cap stays."""
import sys, os, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, '..', 'LOOK-ALIKE-20261126-001'))
import alike

if __name__ == '__main__':
    law, src, out = sys.argv[1], sys.argv[2], sys.argv[3]
    rounds = int(sys.argv[4]) if len(sys.argv) > 4 else 24
    with open(out, 'w') as f:
        for l in open(src):
            x = json.loads(l)
            g = alike.grow(x['stars'], rounds=rounds, knot_law=law)
            x.update(g); x.update({'knot law': law, 'kind': alike.kind([r['n'] for r in g['rows']], g['end'])})
            f.write(json.dumps(x) + '\n'); f.flush()
