"""Shared-runner shards for the complete bounded census."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parent))
from census import count_case
from observables import freeze

def cases():
    freeze()
    for n in range(3,11):
        for k in range(1,2*n//3+1):
            yield f"{n:02d}-{k}", [n,k]

def run(case_id,payload):
    return count_case(*payload)
