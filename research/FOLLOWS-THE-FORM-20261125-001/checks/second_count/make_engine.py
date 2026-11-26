"""Writes eng.py in this folder: ticket B's engine (WHAT-A-BIRTH-CARRIES-20261125-001B, unchanged in its own folder)
with seven more taking rules, none of which uses a name or looks at parts.  Each replacement must match exactly once.

  reach      MET   : knots the parent meets (share a distinction with it), as in ticket B's take of a sole candidate;
             MET2  : those knots and the knots they meet (two holder steps of knots).
  selection  SOLE  : take the candidate when exactly one is on offer (ticket B's);
             ALL   : take every candidate;
             FEW   : take the candidate with the fewest holders, when exactly one has the fewest;
             MANY  : take the candidate with the most holders, when exactly one has the most.
A join draws from the knots within reach of every one of its parents, as in ticket B."""
import os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = sys.argv[1] if len(sys.argv) > 1 else os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
SRC = os.path.join(ROOT, 'experiments', 'WHAT-A-BIRTH-CARRIES-20261125-001B',
                   'WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot', 'eng.py')
t = open(SRC).read()
REPS = [
("TAKES = (None, 'MET', 'MET-SOLE', 'STEPS1-SOLE', 'STEPS2-SOLE', 'J-EACH-PART')",
 "TAKES = (None, 'MET', 'MET-SOLE', 'STEPS1-SOLE', 'STEPS2-SOLE', 'J-EACH-PART',\n"
 "         'MET-ALL', 'MET-FEW', 'MET-MANY', 'MET2-SOLE', 'MET2-ALL', 'MET2-FEW', 'MET2-MANY')\n"
 "MET_KIND = ('MET', 'MET-SOLE', 'MET-ALL', 'MET-FEW', 'MET-MANY', 'MET2-SOLE', 'MET2-ALL', 'MET2-FEW', 'MET2-MANY')\n\n\n"
 "def reach(S, take, p):\n"
 "    \"\"\"The knots a birth of parent p may draw from: those p meets; under MET2 also those they meet.\"\"\"\n"
 "    m = S.meets(p)\n"
 "    if take.startswith('MET2'):\n"
 "        out = set(m)\n"
 "        for w in m:\n"
 "            out.update(S.meets(w))\n"
 "        out.discard(p)\n"
 "        return out\n"
 "    return m"),
("        if take not in ('MET', 'MET-SOLE'):\n            return []\n        common = None\n        for p in ps:\n            m = S.meets(p)",
 "        if take not in MET_KIND:\n            return []\n        common = None\n        for p in ps:\n            m = reach(S, take, p)"),
("        if take in ('MET', 'MET-SOLE'):\n            src = S.meets(p)",
 "        if take in MET_KIND:\n            src = reach(S, take, p)"),
("        if take is not None and (b['kind'] == 'offshoot' or take in ('MET', 'MET-SOLE')):",
 "        if take is not None and (b['kind'] == 'offshoot' or take in MET_KIND):"),
("                elif take == 'J-EACH-PART':\n                    b['takes'] = [d for d, _ in c]\n",
 "                elif take == 'J-EACH-PART' or take.endswith('-ALL'):\n                    b['takes'] = [d for d, _ in c]\n"
 "                elif take.endswith('-FEW') or take.endswith('-MANY'):\n"
 "                    nh = [len(S.holders[d]) for d, _ in c]\n"
 "                    best = min(nh) if take.endswith('-FEW') else max(nh)\n"
 "                    if nh.count(best) == 1:\n"
 "                        b['takes'] = [c[nh.index(best)][0]]\n"),
]
for a, b in REPS:
    assert t.count(a) == 1, a[:60]
    t = t.replace(a, b)
open(os.path.join(HERE, 'eng.py'), 'w').write(t)
print('eng.py written:', len(REPS), 'replacements')
