"""Output, memory cap and logging for the run scripts of MADE-COPIER-20261125-001A-E001."""
import gzip
import json
import os
import resource
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import mc  # noqa: E402

OUT = mc.OUT
T0 = time.time()


def cap_memory(gb=6):
    lim = int(gb * 1024 ** 3)
    resource.setrlimit(resource.RLIMIT_AS, (lim, lim))


def peak_mb():
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0, 1)


def log(*a):
    print('[%8.1fs %6.0fMB]' % (time.time() - T0, peak_mb()), *a, flush=True)


def out_path(name):
    os.makedirs(OUT, exist_ok=True)
    return os.path.join(OUT, name)


def _default(o):
    if isinstance(o, (set, frozenset)):
        return sorted(o)
    if isinstance(o, tuple):
        return list(o)
    raise TypeError(type(o))


def write_json(name, obj):
    p = out_path(name)
    op = gzip.open if name.endswith('.gz') else open
    with op(p, 'wt') as f:
        json.dump(obj, f, sort_keys=True, default=_default)
    log('wrote', p, os.path.getsize(p), 'bytes')
    return p


class JsonLines:
    def __init__(self, name, mode='w'):
        self.path = out_path(name)
        self.f = (gzip.open if name.endswith('.gz') else open)(self.path, mode + 't')

    def write(self, row):
        self.f.write(json.dumps(row, sort_keys=True, default=_default) + '\n')
        self.f.flush()

    def close(self):
        self.f.close()
        log('wrote', self.path, os.path.getsize(self.path), 'bytes')


def read_jsonl(name):
    """Every complete line (a gzip file still being written, or cut off, is read up to its last complete line)."""
    p = out_path(name)
    if not os.path.exists(p):
        return []
    if p.endswith('.gz'):
        import zlib
        raw = open(p, 'rb').read()
        txt, pos = [], 0
        while pos < len(raw):
            d = zlib.decompressobj(16 + zlib.MAX_WBITS)
            txt.append(d.decompress(raw[pos:]))
            if not d.eof:
                break
            pos = len(raw) - len(d.unused_data)
        lines = b''.join(txt).decode().split('\n')
    else:
        lines = open(p).read().split('\n')
    out = []
    for x in lines:
        if x.strip():
            try:
                out.append(json.loads(x))
            except ValueError:
                pass
    return out
