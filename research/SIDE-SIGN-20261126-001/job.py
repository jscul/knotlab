"""job.py: the census of SIDE-SIGN-20261126-001 through scripts/longrun.py, 25 census starts a case."""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))
import sides

CHUNK = 25


def cases():
    n = len(sides.census_starts())
    for i0 in range(0, n, CHUNK):
        yield f'{i0:05d}', {'i0': i0, 'i1': min(n, i0 + CHUNK)}


def run(case_id, payload):
    rows = []
    for i in range(payload['i0'], payload['i1']): rows += sides.stage_rows(i)
    return {'rows': rows}
