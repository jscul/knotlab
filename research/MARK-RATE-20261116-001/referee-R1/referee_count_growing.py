"""Referee R1 (MARK-RATE-20261116-001), item 4: count the LEVEL-REACH census descriptions whose orbits grow past four addresses,
directly. Two independent criteria, both my own code:
  (i)  my block closure (referee_blocks.Blocks) raises 'orbit larger than 4' (finite and exact: the orbit types close);
  (ii) explicit orbits (union-find on my own action) at levels 0..10 have a member orbit of more than 4 addresses.
Writes referee_count_growing.json."""
import collections
import gzip
import json
import sys
from pathlib import Path

sys.path.insert(0, '/home/jscul/p-vs-np-contact-first/research/DIRECT-REACH-20261115-001/referee-R1')
from referee_pattern import Aut  # noqa: E402
from referee_blocks import Blocks  # noqa: E402

ROOT = Path('/home/jscul/p-vs-np-contact-first')
CENSUS = ROOT / 'artifacts/LEVEL-REACH-20261114-001A/LEVEL-REACH-20261114-001A-E001_level_reach/records_slim.jsonl.gz'
tally = collections.Counter()
disagree = []
first_level = collections.Counter()
for line in gzip.open(CENSUS, 'rt'):
    r = json.loads(line)
    alive = r.get('union') == 'alive'
    try:
        Blocks(r['key'])
        small = True
    except ValueError as e:
        small = False
        assert 'orbit larger' in str(e), e
    A = Aut(r['key'])
    big_at = next((n for n in range(11) if max(len(o) for o in A.orbits(n)) > 4), None)
    if (big_at is None) != small:
        disagree.append(r['case'])
    if big_at is not None:
        first_level[big_at] += 1
    tally[('alive' if alive else str(r.get('union')), 'small' if small else 'growing')] += 1
out = dict(total=sum(tally.values()), tally={'%s, %s' % k: v for k, v in sorted(tally.items())},
           criteria_disagree=disagree, first_level_with_orbit_over_4=dict(sorted(first_level.items())))
json.dump(out, open(ROOT / 'research/MARK-RATE-20261116-001/referee-R1/referee_count_growing.json', 'w'), indent=1)
print(out)
