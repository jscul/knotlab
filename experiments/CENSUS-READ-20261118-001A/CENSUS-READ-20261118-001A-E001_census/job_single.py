"""Shared-runner job for the timed-out census shards of CENSUS-READ-20261118-001A-E001 (Amendment 1): one arrangement per case,
the same functions as job.py.  --param shards=0039,0123 names the shards."""
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import job  # noqa: E402

_SHARDS = []
_ARR = None


def setup(params):
    global _SHARDS, _ARR
    _SHARDS = [int(x) for x in params.get('shards', '').split(',') if x]
    _ARR = job.load()


def cases():
    for s in _SHARDS:
        for i in range(s * job.SHARD, min(len(_ARR), (s + 1) * job.SHARD)):
            yield f'census-{s:04d}-{i:05d}', {'i': i}


def run(case_id, p):
    return {'arrangements': [job.census_stages(_ARR[p['i']])]}
