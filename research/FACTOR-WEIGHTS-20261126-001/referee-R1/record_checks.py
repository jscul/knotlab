"""Check the waiting history's accounting hypotheses and the frozen file identities."""

import argparse
import hashlib
from itertools import islice, product
import json
from pathlib import Path
import resource
import sys
from time import perf_counter

FOLDER = Path(__file__).resolve().parent
RESEARCH = FOLDER.parent.parent
sys.path.insert(0, str(RESEARCH / 'SHORT-AGAIN-20261126-001'))
import ring_line  # Executing waiting rules and their recorded start.
from pysat.solvers import Solver


def freeze():
    result = {}
    base = FOLDER.parent
    for line in (base / 'frozen.sha256').read_text().splitlines():
        digest, name = line.split()
        data = (base / name).read_bytes()
        result[name] = hashlib.sha256(data).hexdigest() == digest
        if name == 'preregistration.md':
            before, marker, _ = data.partition(b'\n## Deviation after the run')
            assert marker
            result['registration before appended deviation'] = hashlib.sha256(before).hexdigest() == digest
        if name == 'square_sample.py':
            comment = b'          # a union of two regions lists each distinction once'
            reverted = b''.join(row for row in data.splitlines(keepends=True)
                                if not row.startswith(comment))
            reverted = reverted.replace(b'sorted(set(region[a]) | set(region[c]))',
                                        b'region[a] + region[c]')
            result['reader code with the original list union'] = hashlib.sha256(reverted).hexdigest() == digest
    return result


def check_waiting(ration, rounds):
    bench = ring_line.bench
    eng = ring_line.eng
    stars, _ = bench.build('source', 'ring', 1, None, 'meeting')
    structure = eng.from_stars(stars)
    law = ring_line.law_of(ration)
    guard = eng.Guard(bench.MULT)
    counts = dict(rounds=0, births=0, waits=0, private_fresh_names=0,
                  births_with_no_fresh=0, nonimplied_without_fresh=0)
    # A cut has an old allowed state in which all of that birth's inputs agree.
    with Solver() as allowed:
        def add_knot(places):
            literals = [1 + d for d in places]
            allowed.add_clause(literals)
            allowed.add_clause([-d for d in literals])

        for knot in structure.places:
            add_knot(knot)
        for _ in range(rounds):
            old_count = structure.n_distinctions
            rec = eng.play_round(structure, law, guard)
            fresh = set()
            counts['rounds'] += 1
            counts['waits'] += sum(act == 'wait' for act in rec['act'].values())
            for birth in rec['births']:
                inputs = birth['inputs']
                names = set(birth['fresh'])
                assert all(d < old_count for d in inputs)
                assert len(names) == len(birth['fresh'])
                assert all(d >= old_count for d in names) and names.isdisjoint(fresh)
                assert all(structure.holders[d] == [birth['id']] for d in names)
                fresh.update(names)
                counts['births'] += 1
                if not names:
                    counts['births_with_no_fresh'] += 1
                    # These laws are invariant under complementing every value.
                    cuts = allowed.solve(assumptions=[1 + d for d in inputs])
                    counts['nonimplied_without_fresh'] += cuts
            assert len(fresh) == structure.n_distinctions - old_count
            counts['private_fresh_names'] += len(fresh)
            for birth in rec['births']:
                add_knot(structure.places[birth['id']])
            assert allowed.solve()
    return counts


def cut_witness(limit):
    # Three knots have distinct pairwise shared names and one loose name each.
    stars = [(0, 2, 3), (0, 1, 4), (1, 2, 5)]
    eng = ring_line.eng
    structure = eng.from_stars(stars)
    law = ring_line.law_of('REC-ONE-FEWER')
    rec = eng.play_round(structure, law, eng.Guard())
    (birth,) = rec['births']
    assert birth['f'] == 0 and birth['p'] == 3
    accepted = kept = 0
    for values in islice(product((0, 1), repeat=6), limit):
        if all(len({values[d] for d in knot}) == 2 for knot in stars):
            accepted += 1
            kept += len({values[d] for d in birth['inputs']}) == 2
    return {'start': stars, 'new_knot': birth['inputs'], 'fresh': birth['f'],
            'old_allowed': accepted, 'kept': kept, 'assignments_examined': limit}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--rounds', type=int, choices=range(1, 5), default=4)
    args = parser.parse_args()
    start = perf_counter()
    rows = {name: check_waiting(name, args.rounds) for name in ('CAP-3', 'REC-ONE-FEWER')}
    print(json.dumps({'waiting': rows, 'cut_witness': cut_witness(16 if args.rounds == 1 else 64),
                      'freeze': freeze(),
                      'seconds_after_imports': round(perf_counter() - start, 5),
                      'peak_rss_kib': resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}, indent=2))


if __name__ == '__main__':
    main()
