"""Paths, content checks, and canonical scientific receipts for the learned-library experiment."""
import hashlib
import json
from pathlib import Path
import sys

HERE=Path(__file__).resolve().parent
ROOT=HERE.parents[2]
TICKET=HERE.parent.name
NOTES=ROOT/'research'/TICKET
DATA=ROOT/'artifacts'/TICKET/HERE.name
FIRST='FOLD-DEPTH-20261115-001'
FIRST_EXP=ROOT/'experiments'/FIRST/(FIRST+'-E001_supplied_fold')
FIRST_OUT=ROOT/'artifacts'/FIRST/FIRST_EXP.name
FIRST_NOTES=ROOT/'research'/FIRST
sys.path.insert(0,str(FIRST_EXP))
sys.path.insert(0,str(HERE))


def encoded(value):
    return json.dumps(value,sort_keys=True,separators=(',',':'),allow_nan=False).encode()


def read(path):
    return json.loads(path.read_bytes())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def save_new(path,value):
    with path.open('xb') as writer:
        writer.write(encoded(value)+b'\n')


def verify_sources(mapping):
    for name, expected in mapping.items():
        if sha(ROOT/name)!=expected:
            raise ValueError(f'frozen source changed at {name}')
