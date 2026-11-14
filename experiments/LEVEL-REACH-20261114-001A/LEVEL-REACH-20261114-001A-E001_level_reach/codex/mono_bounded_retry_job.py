"""One fresh retry after the preceding runner has released the same case."""
import json
from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import mono_remaining_retry_job as delegate


def setup(params):
    state = json.loads((HERE / 'mono_remaining_retry' / 'state.json').read_text())
    assert state['final'] and not state['in_flight']
    assert params['ids'] == '0758783d31dde76fe9f2f1e3f17d2f8c077710f5fdd6a8d478363a186001d00b'
    delegate.setup(params)


def cases():
    yield from delegate.cases()


def run(case_id, payload):
    return delegate.run(case_id, payload)
