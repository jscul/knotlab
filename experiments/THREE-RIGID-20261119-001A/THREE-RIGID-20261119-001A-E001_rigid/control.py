"""THREE-RIGID-20261119-001A control: Proposition X and Codex's two reached counterexamples through rigid_job.check_stage.  Each
must show symmetries that break three-way readings and no three-way rigidity counterexample.
Run: .venv/bin/python -B control.py -> control.json beside the artifacts."""
import json
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
sys.path.insert(0, str(HERE))
import rigid_job as J  # noqa: E402


def main():
    d = json.loads((ROOT / 'artifacts/GROWN-END-SWAP-20261119-001/GROWN-END-SWAP-20261119-001-E001_reached/construct_6.json').read_text())
    once_start = [frozenset(s) for s in [[0, 2, 5, 6, 7], [1, 3, 8, 9], [0, 1, 4], [2, 3, 4], [5, 10, 11], [6, 12, 13], [7, 14, 15]]]
    stages = {'propX': [frozenset(s) for s in [[0, 1, 2, 3], [0, 1, 4, 5, 6, 7], [2, 3, 8, 9, 10, 11], [4, 5, 12], [6, 7, 13], [8, 9, 14], [10, 11, 15]]],
              'codex_twice': [frozenset(s) for s in d['a']['current']],
              'codex_once': J.EX.grow1(once_start)}
    out = {}
    for name, a in stages.items():
        c, ex = Counter(), []
        J.check_stage(a, c, ex, name, J.EX.grow1(a))
        out[name] = dict(c)
    dest = ROOT / 'artifacts/THREE-RIGID-20261119-001A/THREE-RIGID-20261119-001A-E001_rigid'
    dest.mkdir(parents=True, exist_ok=True)
    (dest / 'control.json').write_text(json.dumps(out, indent=1))
    print(json.dumps(out, indent=1))


if __name__ == '__main__':
    main()
