"""JOINT-RECORDS-R1: which complement-closed relations on s seam distinctions occur as projections of not-all-equal patterns
(knots on three distinct distinctions) with up to h hidden distinctions; exhaustive over all knot sets (referee's own code)."""
import itertools, json, sys
def run(s, h):
    n = s + h
    A = list(itertools.product((0, 1), repeat=n))
    knots = list(itertools.combinations(range(n), 3))
    masks = []
    for k in knots:
        m = 0
        for i, a in enumerate(A):
            if not (a[k[0]] == a[k[1]] == a[k[2]]): m |= 1 << i
        masks.append(m)
    proj = {}
    for i, a in enumerate(A):
        proj.setdefault(a[:s], []).append(i)
    seamkeys = list(itertools.product((0, 1), repeat=s))
    found = set()
    full = (1 << len(A)) - 1
    # depth-first over knot subsets with pruning by allowed mask (memo on mask)
    seen = set()
    stack = [(0, full)]
    while stack:
        j, m = stack.pop()
        if (j, m) in seen: continue
        seen.add((j, m))
        rel = frozenset(t for t in seamkeys if any(m >> i & 1 for i in proj[t]))
        found.add(rel)
        if j < len(knots):
            stack.append((j + 1, m)); stack.append((j + 1, m & masks[j]))
    total = 2 ** (2 ** (s - 1))
    return dict(s=s, hidden=h, found=len(found), complement_closed=total)
res = [run(2, 1), run(2, 2), run(2, 3), run(3, 1), run(3, 2), run(3, 3)]
print(json.dumps(res, indent=1))
