"""laws.py ARM OUT.jsonl [--chunk I/C]: chains of eight and the carried step one layer up on every census start under a
growth law.  CHAIN-LAWS-20261127-001; README.md.

ARM is 'ordinary', 'one_fewer' (A129) or 'arity_floor' (A130).  For every census start, rounds 0 to 6 as far as growth
is funded: the number of chains of eight (CHAIN-STEP's chains.py, capped at 1,000) and, for at most three chains, the
carried bare-chain pattern checked on the whole stage (CHAIN-STEP's check_mapped: lower triples, no lower reading read
at a knot, seven upper words with free pairs, every chain law needed)."""
import sys, json, time
from pathlib import Path
HERE = Path(__file__).resolve().parent
CS = HERE.parent / 'CHAIN-STEP-20261127-001'
sys.path.insert(0, str(CS)); sys.path.insert(0, str(HERE.parent / 'FOUR-CLAUSE-20261127-001')); sys.path.insert(0, str(HERE.parent / 'UPPER-GROWN-20261127-001'))
import chains as CH, chain_step as CST
F = CST.RB.forbid

if __name__ == '__main__':
    arm, out = sys.argv[1], sys.argv[2]; args = sys.argv[3:]
    starts = F.census(); order = list(range(len(starts)))
    if '--chunk' in args:
        ci, cn = map(int, args[args.index('--chunk') + 1].split('/')); order = order[ci::cn]
    with open(out, 'w') as f:
        for i in order:
            t0 = time.time(); st = F.supports_of(starts[i]); rows = []
            for t in range(7):
                ch = list(CH.chains(st, 8, 1000)); row = {'round': t, 'knots': len(st), 'chains': len(ch)}
                if ch:
                    m = [CST.check_mapped(st, c) for c in ch[:3]]
                    row['carried steps'] = sum(1 for x in m if x['a step']); row['every law needed'] = sum(1 for x in m if x['a step'] and x['every chain law needed'])
                rows.append(row)
                if t == 6: break
                nxt, status, births = F.grown(st, 'nae', arm)
                if status != 'funded': rows.append({'stopped': status, 'after round': t}); break
                st = nxt
            f.write(json.dumps({'start': i, 'rows': rows, 'seconds': round(time.time() - t0, 1)}) + '\n'); f.flush()
