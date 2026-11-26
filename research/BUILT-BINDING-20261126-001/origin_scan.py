"""origin_scan.py SET OUT.jsonl [ARM]: is every class fact of a grown stage a function of the start's values?
BUILT-BINDING-20261126-001; README.md.

A class label f (even on every small change) is a function of the start's values on the allowed states exactly when it
is even on every allowed change that leaves every start distinction as it was (Z_new); every label is, exactly when
Z_new lies in the span H of the small changes.  If so on a stage, every relation among its class facts is a relation
among functions of the start's values, and by the projection lemma (ordinary growth keeps the start's allowed states on
its own distinctions; refereed in LAYERS-20261126-001 and BINDING-20261126-001) it already held at the start.  Read on
every census start of three to five knots and the 900 fresh starts of six to eight (closing.items), rounds 1 to 3 of
growth under parity with ARM (ordinary by default), under both readings of a small change."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import closing as CL, repro as RP
classes, forbid, MC, T2 = RP.classes, RP.forbid, RP.MC, RP.T2


def stage_check(S, st):
    names, idx, rows = RP.space(st); n = len(names)
    old = {x for r in S for x in r}
    Znew = classes.nullspace(rows + [1 << idx[x] for x in old if x in idx], n)
    out = {'dim Z_new': len(Znew)}
    for tag, moves in (('SHORT', MC.moves_of(st)[2]), ('UPTO5', T2.moves_upto(st, 5)[2])):
        rH = classes.rank(moves)
        out[tag] = classes.rank(moves + Znew) == rH
    return out


if __name__ == '__main__':
    which, out = sys.argv[1], sys.argv[2]; arm = sys.argv[3] if len(sys.argv) > 3 else 'ordinary'
    fails = {'SHORT': 0, 'UPTO5': 0}; read = 0
    with open(out, 'w') as f:
        for name, S in CL.items(which):
            st = S; rows = []
            for t in range(1, 4):
                nxt, status, births = forbid.grown(st, 'parity', arm)
                if status != 'funded': rows.append({'round': t, 'end': status}); break
                st = nxt
                if len({x for r in st for x in r}) > 400: rows.append({'round': t, 'end': 'not read'}); break
                r = stage_check(S, st); r['round'] = t; rows.append(r); read += 1
                for k in fails: fails[k] += not r[k]
            f.write(json.dumps({'start': name, 'rounds': rows}) + '\n'); f.flush()
        f.write(json.dumps({'stages read': read, 'stages where some class fact depends on values the start does not fix': fails}) + '\n')
    print(read, fails)
