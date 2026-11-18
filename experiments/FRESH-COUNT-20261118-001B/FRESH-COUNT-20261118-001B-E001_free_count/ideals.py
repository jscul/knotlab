"""Check T1 of FRESH-COUNT-20261118-001A on a grown presentation: the junctions are the ideals of size at most t of the descent
order on the offshoots (the one-parent junctions), parents are lower covers, rank is round, no ideal is built twice and none of
size below the last round is missing (Birkhoff's representation, the literature's distributive lattice of order ideals)."""


def check(P):
    n = len(P.bits_of)
    par = [set() for _ in range(n)]
    for b, js in P.owner.items():
        if len(js) == 2:
            u, v = sorted(js)          # junction ids grow with time: the older one is the parent
            par[v].add(u)
    offs = [v for v in range(n) if len(par[v]) == 1]
    idx = {q: i for i, q in enumerate(offs)}
    ideal = [0] * n
    for v in range(n):
        m = 0
        for u in par[v]:
            m |= ideal[u]
        if v in idx:
            m |= 1 << idx[v]
        ideal[v] = m
    errors = []
    seen = {}
    for v in range(n):
        if bin(ideal[v]).count('1') != P.round_of[v]:
            errors.append(f'rank {v}')
        if ideal[v] in seen:
            errors.append(f'built twice {v} {seen[ideal[v]]}')
        seen[ideal[v]] = v
        for u in par[v]:
            diff = ideal[v] & ~ideal[u]
            if bin(diff).count('1') != 1 or (ideal[u] & ~ideal[v]):
                errors.append(f'not a cover {u} {v}')
        if len(errors) > 5:
            break
    # every ideal of size < last round must be a junction (the last round may be cut short by a junction cap)
    below = [ideal[q] & ~(1 << idx[q]) for q in offs]
    T = P.rounds
    missing, frontier, total = 0, {0}, 1
    for size in range(1, T):
        nxt = set()
        for I in frontier:
            for i in range(len(offs)):
                if not (I >> i) & 1 and (below[i] & ~I) == 0:
                    nxt.add(I | (1 << i))
        total += len(nxt)
        missing += sum(1 for I in nxt if I not in seen)
        frontier = nxt
        if total > 200000:
            break
    return {'errors': errors, 'missing': missing, 'offshoots': len(offs), 'ideals_checked': total}
