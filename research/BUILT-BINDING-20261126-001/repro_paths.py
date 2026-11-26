"""repro_paths.py OUT.json: the binding referee's ten-knot path witness, reproduced with the canonical engine and the
thread's own readings (repro.analyse).  BUILT-BINDING-20261126-001; README.md.  The three carriers are the referee's
path supports, named as the canonical engine names the grown stage (checked equal to the referee's stage)."""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import repro as RP, binding as BD
ROOT = HERE.parents[1]
cert = json.load(open(ROOT / 'research/BINDING-20261126-001/referee-R1/path_certificate.json'))
S = [s for name, s in BD.witnesses() if name.startswith('referee sampled')][0]
st = S; out = {'start': 'referee sampled 10-34', 'rounds': []}
for t in range(1, 5):
    st, status, births = RP.forbid.grown(st, 'parity', 'ordinary')
    assert status == 'funded'
    if t == 3:
        out['stage equals the referee\'s'] = sorted(map(sorted, st)) == sorted(map(sorted, cert['grown_knots']))
    names = {x for r in st for x in r}
    if all(x in names for c in cert['path_supports'] for x in c):
        r = RP.analyse(S, st, cert['path_supports']); r['round'] = t; out['rounds'].append(r)
json.dump(out, open(sys.argv[1], 'w'), indent=1); print(json.dumps(out)[:3000])
