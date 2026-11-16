"""Ten-case smoke: first nine D cases and first U case, sorted by case id.

This covers constant-2, constant-3, half-rate (k_max=4), and U continuation.
"""
from pathlib import Path
import sys
sys.path.insert(0, str(Path(__file__).resolve().parent))
import job
from population import populations

PANEL = []


def setup(params):
    global PANEL
    # Exercise the actual public setup for each population before fork.
    job.setup({'pop': 'D'})
    job.setup({'pop': 'U'})
    pops = populations()
    PANEL = sorted(pops['D'][:9] + pops['U'][:1], key=lambda row: row['id'])


def cases():
    for row in PANEL:
        yield row['id'], row


run = job.run
