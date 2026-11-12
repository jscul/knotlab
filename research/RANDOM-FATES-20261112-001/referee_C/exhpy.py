import subprocess, os
HERE = os.path.dirname(os.path.abspath(__file__))
def trans_table(N, knots):
    by = [[] for _ in range(N)]
    for t in knots:
        assert max(t) - min(t) <= 3
        by[max(t)].append(t)
    rows = []
    for m in range(N):
        for s in range(8):
            for x in (0, 1):
                val = {m - 3: (s >> 2) & 1, m - 2: (s >> 1) & 1, m - 1: s & 1, m: x}
                ok = True
                for t in by[m]:
                    a, b, c = (val[v] for v in t)
                    if a == b == c:
                        ok = False
                rows.append(((s << 1) & 7 | x) if ok else -1)
    return rows
def run(N, knots, queries):
    """queries: list of (lo, hi, i, j, K, budget). Returns list of (best or None, nodes, hit, members)."""
    rows = trans_table(N, knots)
    inp = [str(N), " ".join(map(str, rows)), str(len(queries))] + [" ".join(map(str, q)) for q in queries]
    out = subprocess.run([os.path.join(HERE, "exh")], input="\n".join(inp) + "\n", capture_output=True, text=True, check=True).stdout
    res = []
    for line in out.strip().splitlines():
        a = list(map(int, line.split()))
        res.append((a[0] or None, a[1], a[2], a[3:]))
    return res
