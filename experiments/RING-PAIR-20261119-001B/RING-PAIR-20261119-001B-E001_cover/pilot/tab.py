import joinlib_path  # noqa
import re, job
from scope import in_scope
cs = dict(job.cases())
res = {}
for line in open('all_blocks.txt'):
    m = re.match(r'(\S+) (match|MISS|not covered)', line)
    if m: res[m.group(1)] = m.group(2)
from collections import Counter
T = Counter()
for cid, r in res.items():
    p = cs[cid]
    ok, why = in_scope(p['n'], [tuple(e) for e in p['edges']], p['surplus'])
    T[(ok, r, why)] += 1
    if ok and r != 'match': print('IN SCOPE BUT', r, cid)
print(T)
