"""Independent transfer counts for the matched newborn readers in B252.

The trace counts the old assignments of the shared pairs. Only the two distant
end offers change between the two built arms. The scientific leaf separately
checks the actual grants through the ordinary engine.
"""
from fractions import Fraction
from itertools import product

import numpy as np


BIT = (0, 1)
PAIRS = tuple(product(BIT, repeat=2))
PACKETS = tuple(product(PAIRS, repeat=2))


def permits(law, marks):
    return sum(marks) % 2 == 0 if law == "parity" else min(marks) != max(marks)


def holder(law, extra):
    return np.array([[int(permits(law, x + y + extra)) for y in PAIRS] for x in PAIRS], dtype=object)


def old_counts(law, m):
    center = m // 2
    normal = holder(law, ())
    left = np.linalg.matrix_power(normal, center-1)
    right = np.linalg.matrix_power(normal, m-center)
    ends = {b: holder(law, (b,)) for b in BIT}
    counts = {}
    for u, v in PAIRS:
        mid = left @ holder(law, (u,v)) @ right
        for p,q in PAIRS:
            counts[(u,v,p,q)] = int(np.trace(ends[p] @ mid @ ends[q] @ normal))
    return counts


def multiply_sums(counts, transmissions, local):
    # rows of transmissions are the two local parent inputs, indexed by (u,v).
    return {fresh:sum(n*transmissions[(old[:2],local)]*remotes[fresh]
                      for old, (n,remotes) in counts.items()) for fresh in next(iter(counts.values()))[1]}


def weighting_check(law, m):
    originals = old_counts(law,m)
    # A has a distant joint birth on p,q. In B p now also belongs to a
    # cap holding d,f. Each of q,d,f pays its own unary birth.
    sources = {
        "joint":originals,
        "capped":{(u,v,q,d,f):sum(originals[u,v,p,q] for p in BIT if permits(law,(p,d,f)))
                  for (u,v),(q,d,f) in product(PAIRS,product(BIT,repeat=3))}
    }
    local_map = {(old, packet): int(all(permits(law,(b,)+y) for b,y in zip(old,packet)))
                 for old in PAIRS for packet in PACKETS}
    remote = {}
    for arm, source in sources.items():
        if arm=="joint":
            remote[arm] = {old:{t:int(permits(law,old[2:]+(t,))) for t in BIT} for old in source}
        else:
            remote[arm] = {old:{out:int(all(permits(law,(b,)+z) for b,z in zip(old[2:],out)))
                                 for out in product(PAIRS,repeat=3)} for old in source}

    def normalize(hist):
        total = sum(hist.values())
        return {k:Fraction(v,total) for k,v in hist.items()}

    result = {}
    for arm,source in sources.items():
        rows = {old:(n,remote[arm][old]) for old,n in source.items()}
        reached = {packet:multiply_sums(rows,local_map,packet) for packet in PACKETS}
        for exponent in (1,2):
            before = {uv:sum(n**exponent for old,n in source.items() if old[:2]==uv) for uv in PAIRS}
            after = {packet:sum(n**exponent for n in ways.values()) for packet,ways in reached.items()}
            pre,post = normalize(before),normalize(after)
            event = sum(v for (r,s),v in post.items() if r[0]==s[0])
            result[arm,exponent] = (pre,post,event)
    print(law,m,"meetings parameter, local first fresh values equal")
    for exp in (1,2):
        x,y = result["joint",exp], result["capped",exp]
        print("   power",exp, "old local words match:",x[0]==y[0],
              "new joint / capped:",x[2],y[2], "full packets match:",x[1]==y[1])
    assert result["joint",1][0] == result["capped",1][0]
    if law=="parity":
        assert all(result["joint",p]==result["capped",p] for p in (1,2))
    else:
        assert all(result["joint",p][2]!=result["capped",p][2] for p in (1,2))
    return result


if __name__ == "__main__":
    for law,m in product(("parity","nae"),(6,8,10)):
        weighting_check(law,m)
