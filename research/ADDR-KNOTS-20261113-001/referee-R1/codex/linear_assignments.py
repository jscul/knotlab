"""Seek directly checkable linear colourings on the initially undecided levels.

Failure of this restricted search says nothing about satisfiability.
"""
import json
import time
from pathlib import Path

from fresh_patterns import pattern, verify_assignment


def main():
    home = Path(__file__).resolve().parent
    targets = json.loads((home / 'refinement_selection.json').read_text())
    results = []
    for target in targets:
        start = time.monotonic()
        rec = json.loads((home / target['file']).read_text())
        n = target['level']
        triples = pattern(rec['key'], n)
        candidates = list(range(1, 1 << n))
        for a, b, c in triples:
            d, e = a ^ b, a ^ c
            candidates = [w for w in candidates if ((w & d).bit_count() & 1) or ((w & e).bit_count() & 1)]
            if not candidates:
                break
        outcome = {**target, 'linear_masks_found': candidates, 'seconds': time.monotonic() - start}
        if candidates:
            w = candidates[0]
            values = [bool((w & x).bit_count() & 1) for x in range(1 << n)]
            assert verify_assignment(triples, values)
            outcome['assignment'] = ''.join('1' if v else '0' for v in values)
            outcome['checked_knots'] = len(triples)
        results.append(outcome)
        print(json.dumps({k: v for k, v in outcome.items() if k != 'assignment'}), flush=True)
    (home / 'linear_assignments.json').write_text(json.dumps(results, indent=2) + '\n')


if __name__ == '__main__':
    main()
