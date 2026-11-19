"""CENSUS-READ-20261118-001A gate C0(b), C0(b'), C0(c).  Run: .venv/bin/python -B gate.py  -> gate.json beside the artifacts."""
import importlib.util
import json
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402
R, R3, S, F, A = job.R, job.R3, job.S, job.F, job.A
ROOT = HERE.parents[2]
spec = importlib.util.spec_from_file_location(
    'ring_read_a_check', ROOT / 'experiments/RING-READ-20261118-001A/RING-READ-20261118-001A-E001_tables/check.py')
CA = importlib.util.module_from_spec(spec)
sys.modules[spec.name] = CA
spec.loader.exec_module(CA)


def stages_in_order(data):
    for key in data:
        P = S.from_junctions(A.stars_of(key))
        for r in range(job.RMAX + 1):
            if len(P.bits_of) > job.JCAP:
                break
            yield key, r, [frozenset(b) for b in P.bits_of]
            if r == job.RMAX:
                break
            res = P.step(S.gf2(F.fewest), None)
            if res is None or res['new'] == 0:
                break


def main():
    data = job.load()
    small, big = [], []
    seen_small = seen_big = 0
    for key, r, st in stages_in_order(data):
        n = len(st)
        if 6 <= n <= 16:
            if seen_small % 7 == 0 and len(small) < 300:
                small.append((key, r, st))
            seen_small += 1
        elif 30 <= n <= 120:
            if seen_big % 25 == 0 and len(big) < 200:
                big.append((key, r, st))
            seen_big += 1
        if len(small) >= 300 and len(big) >= 200:
            break
    out = {'small_stages': len(small), 'big_stages': len(big)}
    bad = 0
    for key, r, st in small:
        K = max(map(len, st))
        a, _ = R.bond_table(st, len(st), K + 2)
        b = CA.brute_table(st, K + 2)
        bad += a != b
    out['small_tables_differing_from_brute_force'] = bad
    bad = 0
    for key, r, st in big:
        K = max(map(len, st))
        a, _ = R.bond_table(st, 6, K + 2)
        b, _ = R.bond_table(st, 8, K + 2)
        bad += a != b
    out['big_tables_differing_6_vs_8'] = bad
    ring = {}
    for T in (10, 15):
        P = R.grow(T)
        st = R.stars_of(P)
        K = max(map(len, st))
        tab, _ = R.bond_table(st, 6, K + 2)
        ring[T] = R3.r3(tab, K + 3) == set(st)
    out['ring_rounds_10_15_exact'] = ring
    out['gate_passes'] = (out['small_tables_differing_from_brute_force'] == 0 and out['big_tables_differing_6_vs_8'] == 0
                          and all(ring.values()) and len(small) == 300 and len(big) == 200)
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'gate.json').write_text(json.dumps(out, indent=1, default=str))
    print(json.dumps(out, indent=1, default=str))


if __name__ == '__main__':
    main()
