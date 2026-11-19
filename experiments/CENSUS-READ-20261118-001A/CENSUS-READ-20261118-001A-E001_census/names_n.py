"""Amendment 2, N1 and N2: the name-free reader R3n on Codex's 27-distinction example (identity, the transposition 0 <-> 24, 20
random renamings; horizons 4, largest - 1 and largest + 3) and on the ring at rounds 10, 15, 20 and 25 (11 namings each).
Run: .venv/bin/python -B names_n.py  -> names_n.json beside the artifacts."""
import json
import sys
from collections import Counter
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import names as NM  # noqa: E402
import reader3n as N  # noqa: E402
import exact_table as X  # noqa: E402
R = NM.R


def main():
    res = {}
    rows = json.loads(NM.FRONTIER.read_text())['closure']['first_histories_by_shrinking_joins']['2']
    stars = [frozenset(r) for r in rows]
    K = max(map(len, stars))
    H = K + 3
    table = X.exact_table(stars, H)
    labels = sorted(R.owners(stars))
    swap = {x: x for x in labels}
    swap[0], swap[24] = 24, 0
    perms = [{x: x for x in labels}, swap] + NM.perms_for(labels, 20, 7)[1:]
    ex = {}
    for h in (4, K - 1, H):
        v = NM.trial(N.r3n, stars, R.pooled(table, h), h + 1, perms)
        ex[f'h{h}'] = {'identity': v[0], 'swap_0_24': v[1], 'random_20': dict(Counter(v[2:]))}
    res['codex_27_r3n'] = ex
    ring = {}
    for T in (10, 15, 20, 25):
        P = R.grow(T)
        st = R.stars_of(P)
        K = max(map(len, st))
        tab, _ = R.bond_table(st, 6, K + 2)
        v = NM.trial(N.r3n, st, tab, K + 3, NM.perms_for(sorted(R.owners(st)), 10, T))
        ring[T] = dict(Counter(v))
    res['ring_r3n_under_renamings'] = ring
    dest = NM.ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    (dest / 'names_n.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
