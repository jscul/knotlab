"""Independent counting from the five reached holdings and local permutations.

The investigator separately runs the physical schedule and growth engine.
This check reconstructs the information seen on each intact or disconnected
sibling, every source word, the focal measurement, and the cost of readiness.
"""
from collections import Counter, defaultdict
from fractions import Fraction
from functools import cache
from itertools import product


def legal(bits, law):
    return sum(bits) % 2 == 0 if law == "parity" else min(bits) != max(bits)


def triples(paid, law):
    return [v for v in product(range(2), repeat=3) if legal((paid,*v),law)]


def cycle(v, paid):
    current = list(v)
    moves = ((0,1),(1,2)) if paid else ((1,2),(0,1))
    changed = 0
    for i,j in moves:
        changed += current[i] != current[j]
        current[i],current[j] = current[j],current[i]
    return tuple(current), changed


@cache
def decode(row, paid, law, connected):
    after, changes = cycle(row, paid) if connected else (row, 0)
    # The two retained scratch bits and the physically restored exterior word
    # determine the prefix of the moved word even when no offer fired.
    signature = after[:2]
    if len(set(row)) == 1:
        candidates = [p for p in (0,1) if legal((p,*row),law)]
    else:
        candidates = [p for p in (0,1) if cycle(row,p)[0][:2] == signature]
    assert len(candidates) <= 1
    return (candidates[0] if candidates else None), changes


def keeper(decoded, law):
    if None in decoded:
        return None
    if law == "parity":
        return sum(decoded) % 2
    if len(set(decoded)) == 1:
        return 1-decoded[0]
    return None


@cache
def joined_extensions(exterior_status, law):
    """Count all 27 auxiliary bits after fixing a complete old word."""
    total = 0
    for abc in product(range(2), repeat=3):
        if law == "parity":
            choices_h = 2**18   # eighteen scratch names, one forced H slack
        else:
            # With all 12 shared values equal, one private extension is forbidden.
            uniform_shared = all(v == exterior_status for v in abc)
            choices_h = 2**19-int(uniform_shared)
        for de in product(range(2), repeat=3):
            choices_k = sum(legal((*abc,*de,k),law) for k in (0,1))
            choices_l = sum(legal((*de,s),law) for s in (0,1))
            total += choices_h * choices_k * choices_l
    return total


def focal_table(gram):
    tr = sum(gram[i][i] for i in range(8))
    ans = {}
    for x in range(8):
        z = x ^ 7
        for a in range(8):
            row = [(-1)**((u&a&x).bit_count()) if (u^a)&z == 0 else 0
                   for u in range(8)]
            n = sum(row[u]*gram[u][v]*row[v] for u,v in product(range(8),repeat=2))
            ans[x,a] = Fraction(n,(1 << x.bit_count())*tr)
        assert sum(ans[x,a] for a in range(8)) == 1
    return ans


def excess(table, p):
    target = p*7
    total = -table[0,target]+sum(table[7,a] for a in range(8) if a.bit_count()>=2)
    for x in (1,2,4):
        total -= sum(table[x,a] for a in range(8) if x&a and (7^x)&(a^target))
    return total


def run(law):
    gross = joined = 0
    writes, wrong, changed_by_unplug = Counter(), Counter(), Counter()
    focal_counts = Counter()
    ext_support, paid_support = defaultdict(set), defaultdict(set)
    for u in product(range(2),repeat=4):
        if not legal(u,law):
            continue
        focal = triples(u[0],law)
        for ext in product(*(triples(v,law) for v in u[1:])):
            nr = len(focal)
            gross += nr
            exterior = set(sum(ext,()))
            joined += nr * joined_extensions(next(iter(exterior)) if len(exterior)==1 else -1,law)
            ext_support[ext].add(u[0])
            paid_support[(u[1:],ext)].add(u[0])
            on = [decode(r,p,law,True) for r,p in zip(ext,u[1:])]
            off = [decode(r,p,law,False) for r,p in zip(ext,u[1:])]
            ans = keeper([bit for bit,n in on],law)
            if ans is None:
                continue
            off_ans = keeper([bit for bit,n in off],law)
            moves = sum(n>0 for bit,n in on)
            writes[ans,moves] += nr
            wrong[ans] += nr*(ans != u[0])
            changed_by_unplug[ans] += nr*(ans != off_ans)
            for f in focal:
                focal_counts[ans,sum(v<<i for i,v in enumerate(f))] += 1
    assert not any(wrong.values())
    kernel = sum(writes.values())
    # Certify every refused nonfocal view has an opposite initial orientation.
    informative = sum(len(c)==1 for c in paid_support.values())
    assert informative*len(triples(0,law)) == kernel
    print(law,"complete source",gross,"lawful joined",joined,
          "ready fraction among lawful",Fraction(gross,joined))
    print("  correct by orientation and number of moved siblings", sorted(writes.items()))
    print("  write, any move, three moves", Fraction(kernel,gross),
          Fraction(sum(changed_by_unplug.values()),gross),
          Fraction(sum(n for (a,m),n in writes.items() if m==3),gross))
    print("  all raw launches",Fraction(kernel,gross*(1<<27)),"all lawful joined",Fraction(kernel,joined))
    print("  decisive exterior views",sum(len(c)==1 for c in ext_support.values()),"of",len(ext_support))
    for a in (0,1):
        freq = [focal_counts[a,i] for i in range(8)]
        envs, = {n for n in freq if n}
        gram = [[envs if n and m else 0 for n in freq] for m in freq]
        tag = [[v if (i^j)&1 == 0 else 0 for i,v in enumerate(row)] for j,row in enumerate(gram)]
        print("  port",a,"focal counts",freq,"64-cell excess",excess(focal_table(gram),a),
              "copied focal bit",excess(focal_table(tag),a))


if __name__ == "__main__":
    for law in ("nae","parity"):
        run(law)
