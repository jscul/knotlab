"""Writes eng_cap.py in this folder: the shared growth engine (ticket B of WHAT-A-BIRTH-CARRIES-20261125-001,
unchanged in its own folder) with the cap of three made a cap of any size.  Each replacement must match exactly once."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, '..', '..', '..'))
SRC = os.path.join(ROOT, 'experiments', 'WHAT-A-BIRTH-CARRIES-20261125-001B',
                   'WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot', 'eng.py')
t = open(SRC).read()
REPS = [
("RATIONS_RECORDED = ('FLOOR1', 'CAP-3', 'ORD')",
 "RATIONS_RECORDED = ('FLOOR1', 'CAP-3', 'ORD') + tuple('CAP-%d' % c for c in (2, 4, 5, 6, 7, 8, 9, 10, 12))"),
("        if r == 'CAP-3':\n            return min(q, 3)",
 "        if r.startswith('CAP-'):\n            return min(q, int(r[4:]))"),
]
for a, b in REPS:
    assert t.count(a) == 1, a
    t = t.replace(a, b)
open(os.path.join(HERE, 'eng_cap.py'), 'w').write(t)
print('eng_cap.py written,', len(REPS), 'replacements')
