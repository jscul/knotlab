"""Does R3 depend on the names of the distinctions?  (After VARIABLE-OUTPUT-READER-20261118-001J's ring comparison.)
(1) Codex's 27-distinction example: its twelve junctions (frontier.json, closure, two shrinking joins), our own exact table, R3
under the identity, the transposition 0 <-> 24, and 20 random renamings.  (2) The ring at rounds 10, 15, 20 under 10 renamings.
Run: .venv/bin/python -B names.py  -> names.json beside the artifacts."""
import json
import random
import sys
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import exact_table as X  # noqa: E402
R, R3 = job.R, job.R3
FRONTIER = ROOT / 'proofs/VARIABLE-OUTPUT-READER-20261118-001J/VARIABLE-OUTPUT-READER-20261118-001J-P001_seven_to_six/frontier.json'


def renamed_read(reader, table, perm, top):
    t = {tuple(sorted((perm[a], perm[b]))): d for (a, b), d in table.items()}
    inv = {v: k for k, v in perm.items()}
    return {frozenset(inv[x] for x in s) for s in reader(t, top)}


def trial(reader, stars, table, top, perms):
    truth = set(stars)
    own = R.owners(stars)
    loose = frozenset(b for b, js in own.items() if len(js) == 1)
    return [job.verdict(renamed_read(reader, table, p, top), truth, loose) for p in perms]


def perms_for(labels, k, seed):
    rng = random.Random(seed)
    out = [{x: x for x in labels}]
    for _ in range(k):
        img = list(labels)
        rng.shuffle(img)
        out.append(dict(zip(labels, img)))
    return out


def main():
    res = {}
    rows = json.loads(FRONTIER.read_text())['closure']['first_histories_by_shrinking_joins']['2']
    stars = [frozenset(r) for r in rows]
    K = max(map(len, stars))
    H = K + 3
    table = X.exact_table(stars, H)
    labels = sorted(R.owners(stars))
    swap = {x: x for x in labels}
    swap[0], swap[24] = 24, 0
    perms = [{x: x for x in labels}, swap] + perms_for(labels, 20, 7)[1:]
    ex = {'junctions': len(stars), 'distinctions': len(labels), 'largest': K,
          'loose': sorted(b for b, js in R.owners(stars).items() if len(js) == 1)}
    for name, reader in (('r3', R3.r3), ('r3m', job.r3m)):
        for h in (4, K - 1, H):
            v = trial(reader, stars, R.pooled(table, h), h + 1, perms)
            ex[f'{name}_h{h}'] = {'identity': v[0], 'swap_0_24': v[1], 'random_20': dict(__import__('collections').Counter(v[2:]))}
    res['codex_27'] = ex
    ring = {}
    for T in (10, 15, 20):
        P = R.grow(T)
        st = R.stars_of(P)
        K = max(map(len, st))
        tab, _ = R.bond_table(st, 6, K + 2)
        labels = sorted(R.owners(st))
        v = trial(R3.r3, st, tab, K + 3, perms_for(labels, 10, T))
        ring[T] = dict(__import__('collections').Counter(v))
    res['ring_r3_under_renamings'] = ring
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'names.json').write_text(json.dumps(res, indent=1))
    print(json.dumps(res, indent=1))


if __name__ == '__main__':
    main()
