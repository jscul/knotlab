"""Literal state and support checks for the seven-knot held-out exception."""
import argparse
import itertools
import json
import os
import random
import resource
import subprocess
import sys
import time
from collections import Counter
from pathlib import Path

from frozen_recount_core import grow
from periodic import kernel, mask, pivots

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]


def heldout(index):
    n = 7
    randomizer = random.Random(20261206+n)
    pairs = list(itertools.combinations(range(n), 2))
    accepted = 0
    while True:
        meetings = [pair for pair in pairs if randomizer.random() < 1/3]
        copies = [randomizer.randrange(1, 3) for _ in meetings]
        loose = [randomizer.randrange(3) for _ in range(n)]
        if sum(copies) + sum(loose) > 18:
            continue
        rows = [[] for _ in range(n)]
        next_id = 0
        for (a, b), size in zip(meetings, copies):
            rows[a].extend(range(next_id, next_id+size))
            rows[b].extend(range(next_id, next_id+size))
            next_id += size
        for r, q in zip(rows, loose):
            r.extend(range(next_id, next_id+q))
            next_id += q
        if min(map(len,rows)) < 3:
            continue
        seen = {0}
        for _ in rows:
            for a, b in meetings:
                if a in seen or b in seen:
                    seen.update([a,b])
        if len(seen) == n:
            if accepted == index:
                return rows
            accepted += 1


def all_states(basis):
    states = [0]
    for v in basis:
        states += [s^v for s in states]
    return states


def profile(functional, basis):
    return mask(j for j, v in enumerate(basis) if (functional & v).bit_count() % 2)


def literals(rows):
    n = max(x for r in rows for x in r)+1
    z = kernel(rows, n)
    states = all_states(z)
    moves = set()
    for i in range(n):
        through = [s for s in states if s & (1 << i)]
        if through:
            smallest = min(s.bit_count() for s in through)
            moves.update(s for s in through if s.bit_count() == smallest)
    h = pivots(moves)
    bits = len(z)-len(h)
    labels = {}
    for length in range(1,n+1):
        for names in itertools.combinations(range(n),length):
            f = mask(names)
            value = profile(f,z)
            if value and value not in labels and not profile(f,h):
                labels[value] = names
        if len(labels) == 2**bits-1:
            break
    results = []
    for value, places in labels.items():
        f = mask(places)
        def witness(visible):
            return next((s for s in states if s & visible == 0 and (s & f).bit_count()%2), None)
        separating = [witness(mask(r)) for r in rows]
        first_read = None
        for k in range(1,len(rows)+1):
            for subset in itertools.combinations(range(len(rows)),k):
                seen = {x for i in subset for x in rows[i]}
                if witness(mask(seen)) is None:
                    first_read = subset
                    break
            if first_read is not None:
                break
        results.append({"evaluation_on_allowed_basis":value, "places": places,
                        "zero_view_opposite_state_per_support":separating,
                        "reading_supports":[i for i,s in enumerate(separating) if s is None],
                        "smallest_collection_reading_label":first_read})
    return states, {"supports":rows, "allowed_states":len(states), "move_count":len(moves),
                    "allowed_rank":len(z), "move_rank":len(h),"labels":results}


def check_projection(rows):
    """Send each distinct projected relation to the repository's canonical test."""
    n = max(x for r in rows for x in r)+1
    z = kernel(rows,n)
    checks = {}
    reports = []
    for r in rows:
        allowed = {profile(v, [1 << d for d in r]) for v in all_states(pivots(s & mask(r) for s in z))}
        names = ['x'+str(j) for j in range(len(r))]
        key = (len(r), tuple(sorted(allowed)))
        if key not in checks:
            checks[key] = canonical(allowed, names)
        reports.append(checks[key]["is_knot"])
    return reports


def canonical(allowed, names):
    forbidden = [i for i in range(1<<len(names)) if i not in allowed]
    clauses = [' '.join(('~' if v >> j & 1 else '')+name for j,name in enumerate(names)) for v in forbidden]
    cmd = [sys.executable, '-B','-m','knotlab','check','--cnf','; '.join(clauses),
           '--loops',*names[:-1],'--contact',names[-1],'--json']
    p = subprocess.run(cmd, capture_output=True, check=True, text=True, cwd=ROOT,
                       env={**os.environ,'PYTHONPATH':'tools'})
    obj = json.loads(p.stdout)
    return {key:obj[key] for key in ('is_knot','binding','invisible_in_parts','coexistence')}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    resource.setrlimit(resource.RLIMIT_AS, (1<<30,1<<30))
    t = time.monotonic()
    # First rank-two case is enough to time one exact recount.
    source = heldout(239)
    grown = grow(source)
    assert grown.status == 'funded'
    states, counted = literals(grown.stage)
    unread = [r for r in counted["labels"] if not r["reading_supports"]]
    assert len(unread)==2
    f,g = (mask(r["places"]) for r in unread)
    joint = Counter(str((s&f).bit_count()%2)+str((s&g).bit_count()%2) for s in states)
    assert len(set(joint.values())) == 1 and len(joint) == 4
    output = {"sample":"240th accepted labelled seven-knot start", "source":source,"grown":counted,
              "unread_parities_joint_counts":dict(sorted(joint.items())),
              "grown_projected_knot_test":check_projection(grown.stage),
              "derived_sum_knot_test":canonical({0,3,5,6}, ['a','b','c'])}
    if not args.pilot:
        output["source_counts"] = literals(source)[1]
    output["seconds"] = round(time.monotonic()-t,4)
    (HERE/('witness_pilot.json' if args.pilot else 'witness.json')).write_text(json.dumps(output,indent=2)+'\n')


if __name__ == "__main__":
    main()
