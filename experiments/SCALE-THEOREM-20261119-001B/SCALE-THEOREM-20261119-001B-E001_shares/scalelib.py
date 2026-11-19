"""SCALE-THEOREM-20261119-001B: SCALE-SHARE's samples read by the proved theorems instead of the cluster rule.

Samples are SCALE-SHARE-20261119-001B's (scale.chain: Metropolis over labelled descriptions of n knots of 3 to 5 places, any
multiplicities, connected; the same seeds give the same samples), weighted to distinct arrangements by |Aut| / n!.  Each is
classified by DOUBLE-IDENT's class (stall; out by (S3) or (S4); one loose; no loose; in), and, in the class, its growth class is
read off the relayed extended complex piece by piece (DOUBLE-IDENT ticket B's rule: a finished piece closes or relays, a tree core
with R rays has dimension R, a bare single cycle dimension 1, any other cycle exponential)."""
import importlib.util
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


SC = _load('ss_scale', 'experiments/SCALE-SHARE-20261119-001B/SCALE-SHARE-20261119-001B-E001_shares/scale.py')
DC = _load('di_check', 'proofs/DOUBLE-IDENT-20261119-001A/DOUBLE-IDENT-20261119-001A-P001_doubles/machine_check.py')
DM = _load('di_dims', 'experiments/DOUBLE-IDENT-20261119-001B/DOUBLE-IDENT-20261119-001B-E001_dims/dims.py')


def theorem_class(sizes, M):
    sz, e = SC.edges_of(sizes, M)
    c = DC.classify(sz, e)
    if c == 'stall':
        return 'stall', None
    if c == 'out':
        return 'out', None
    D, why = DM.predict(sz, e)
    return 'in', D


def label(D):
    return {0: 'closes', 'exp': 'exponential'}.get(D, f'dimension {D}')
