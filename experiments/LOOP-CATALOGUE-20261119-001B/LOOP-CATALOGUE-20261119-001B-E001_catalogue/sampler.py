"""Random connected arrangements of n knots (the referee's sampler for CLUSTER-ALL): sizes 3 to 5 uniform; touches drawn one at
a time between random pairs while both have places left, until a drawn count in [n - 1, 2n + 2]; kept when connected."""
import random


def sample(n, seed):
    rng = random.Random(seed)
    while True:
        sizes = [rng.randint(3, 5) for _ in range(n)]
        deg = [0] * n
        edges = []
        want = rng.randint(n - 1, 2 * n + 2)
        tries = 0
        while len(edges) < want and tries < 50 * want:
            tries += 1
            i, j = rng.sample(range(n), 2)
            if deg[i] < sizes[i] and deg[j] < sizes[j]:
                edges.append((min(i, j), max(i, j)))
                deg[i] += 1
                deg[j] += 1
        adj = {k: set() for k in range(n)}
        for a, b in edges:
            adj[a].add(b)
            adj[b].add(a)
        seen, st = {0}, [0]
        while st:
            x = st.pop()
            for z in adj[x] - seen:
                seen.add(z)
                st.append(z)
        if len(seen) == n:
            return sizes, sorted(edges)


def knot_cycle_rank(n, edges):
    return len(edges) - n + 1
