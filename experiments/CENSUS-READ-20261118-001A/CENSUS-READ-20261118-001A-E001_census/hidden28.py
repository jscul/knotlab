"""The coordinator's uniqueness question on Codex's width-28 example (VARIABLE-OUTPUT-READER-20261118-001K high_check.json): two
histories, the cap {12,20,21,25,26,27} or {12,20,22,25,26,27} on the same eleven-junction prefix, with one table; the exchange of 21
and 22 is a table symmetry that moves the cap.  What do R3 and R3n (version 2) return, under the identity and the exchange?
Run: .venv/bin/python -B hidden28.py  -> hidden28.json beside the artifacts."""
import json
import sys
from pathlib import Path

sys.setrecursionlimit(100000)
HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import job  # noqa: E402
import exact_table_v2 as X  # noqa: E402
import reader3n_v2 as N  # noqa: E402
import job_exact3 as J  # noqa: E402
R, R3 = job.R, job.R3
SRC = ROOT / 'proofs/VARIABLE-OUTPUT-READER-20261118-001K/VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh/high_check.json'


def main():
    d = json.loads(SRC.read_text())
    prefix = [frozenset(s) for s in d['prefix_junctions']]
    caps = [frozenset(t['cap_inputs'] + t['cap_outputs']) for t in d['transition']]
    out = {}
    tables = []
    for side, cap in zip('AB', caps):
        stars = prefix + [cap]
        K = max(map(len, stars))
        H = K + 2
        tab = X.exact_table(stars, H)
        tables.append(tab)
        labels = sorted(R.owners(stars))
        swap = {x: x for x in labels}
        swap[21], swap[22] = 22, 21
        truth = set(stars)
        res = {'width': len(labels), 'junctions': len(stars)}
        for name, reader in (('r3', R3.r3), ('r3n', N.r3n)):
            for pname, perm in (('identity', {x: x for x in labels}), ('swap_21_22', swap)):
                got = J.renamed(reader, tab, perm, H + 1)
                res[f'{name}_{pname}'] = {'missed': sorted(map(sorted, truth - got)), 'extra': sorted(map(sorted, got - truth)),
                                          'output_invariant_under_swap': {frozenset(swap[b] for b in s) for s in got} == got,
                                          'output_within_truth': got <= truth}
        res['symmetry'] = J.symmetry(stars, tab)
        out[side] = res
    out['tables_equal'] = tables[0] == tables[1]
    dest = ROOT / 'artifacts/CENSUS-READ-20261118-001A/CENSUS-READ-20261118-001A-E001_census'
    (dest / 'hidden28.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
