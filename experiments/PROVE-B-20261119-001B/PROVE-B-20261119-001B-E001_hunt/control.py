"""PROVE-B-20261119-001B control: the advisor's 7-junction start (junctions a, b, c, u, v, u', v'; a-b and a-c sharing two each,
b-u, b-v, c-u', c-v' sharing two each, one loose distinction on each of u, v, u', v'), run through reached_job.test_stage as if it
were a stage.  Every reading-keeping, equation-breaking table symmetry found must fail to extend (it is a counterexample to Claim
B for arrangements in general).  Run: .venv/bin/python -B control.py -> control.json beside the artifacts."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import reached_job as J  # noqa: E402

A = [[0, 1, 2, 3], [0, 1, 4, 5, 6, 7], [2, 3, 8, 9, 10, 11], [4, 5, 12], [6, 7, 13], [8, 9, 14], [10, 11, 15]]


def main():
    a = [frozenset(s) for s in A]
    c, ex = Counter(), []
    J.test_stage(a, J.EX.grow1(a), c, ex, 'advisor')
    t1, _ = J.L.table(J.EX.grow1(a))
    out = {'counts': dict(c), 'next_T_p1_p2': t1[(0, 1)], 'next_T_q1_p2': t1[(1, 2)], 'example': ex[:1]}
    dest = ROOT / 'artifacts/PROVE-B-20261119-001B/PROVE-B-20261119-001B-E001_hunt'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'control.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
