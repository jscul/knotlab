"""explore_reads.py: the advisor's attack on the built bindings: are the ring facts in the span of class facts that
single knots read?  For each stage: k (class facts), 'jointly unread' (k less the dimension that single knots' reads
span: binding.read_stage), and for each connecting knot of the ring starts the parity of its two attachment
distinctions: a class fact? (exploration, before any freeze)"""
import sys, json
from pathlib import Path
HERE = Path(__file__).resolve().parent; ROOT = HERE.parents[1]
sys.path.insert(0, str(ROOT / 'research' / 'BUILT-BINDING-20261126-001'))
import repro as RP, built as BU
BD = BU.BD
def run(label, S, rounds=3):
    st = S
    for t in range(0, rounds + 1):
        if t:
            st, status, births = RP.forbid.grown(st, 'parity', 'ordinary')
            if status != 'funded': print(label, t, status); break
        names, idx, short = RP.MC.moves_of(st); _, idx2, up = RP.T2.moves_upto(st, 5)
        a = BD.read_stage(st, short, idx); b = BD.read_stage(st, up, idx2)
        print(label, 'round', t, 'SHORT k', a['k'], 'jointly unread', a['jointly unread'], '| UPTO5 k', b['k'], 'jointly unread', b['jointly unread'], flush=True)
S, rings, loose = RP.rings_start(); run('30-knot', S)
S, rings, loose = RP.rings_start(link='double'); run('21-knot', S)
S, _ = BU.build('base'); run('14-knot', S)
