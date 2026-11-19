"""Part C (P4): clusters by size split by parts, for the three frozen joins.  python3 -B partc.py <out.json>"""
import json
import sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import parts  # noqa: E402
J = parts.M.J
R = J.ring_edges
N = 13


def summary(s):
    rows = {}
    for k in sorted(s):
        tot = sum(s[k].values())
        multi = sum(v for p, v in s[k].items() if len(p) >= 2)
        rows[k] = {'total': tot, 'parts': {'+'.join(p): v for p, v in s[k].items()}, 'share_two_or_more': multi / tot}
    return rows


out = {}
e = R(5) + R(7, 5) + [(0, 5)]
out['5-7 by a distinction'] = summary(parts.shares(12, e, {k: 'ring5' if k < 5 else 'ring7' for k in range(12)}, N))
e = R(5) + R(5, 5) + [(0, 10), (10, 5)]
out['5-5 through a path of one'] = summary(parts.shares(11, e, {k: 'ringA' if k < 5 else ('ringB' if k < 10 else 'path') for k in range(11)}, N))
e = R(5) + [(1, 5), (5, 6)]
sp = {'4': 1, '5': 2, '6': 1}
sz = J.bare_sizes(7, e, sp)
out['ring 4,4,4,4,5 with a hanging pair (2, 1)'] = summary(parts.shares_general(sz, e, {k: 'ring' if k < 5 else 'pair' for k in range(7)}, N))
ok = True
for name, rows in list(out.items()):
    for k, r in rows.items():
        if k >= 10 and r['share_two_or_more'] <= 0.9:
            ok = False
    singles = {}
    for k, r in rows.items():
        for p, v in r['parts'].items():
            if '+' not in p:
                singles.setdefault(p, []).append(v)
    out[name + ' (single-part counts by size)'] = singles
json.dump({'joins': out, 'share_ok': ok}, open(sys.argv[1], 'w'), indent=1)
for name, rows in out.items():
    if isinstance(rows, dict) and 1 in rows:
        print(name, [(k, round(r['share_two_or_more'], 4)) for k, r in rows.items() if k in (5, 10, 13)])
    else:
        print(name, rows)
print('share_ok', ok)
