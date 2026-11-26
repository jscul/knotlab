"""Purposeful replay of the peak, a stalled control and starts from both source lists."""
import argparse
import json
from collections import Counter
from archive import records, SETTINGS
from measure import measure
from rings import compare
from starts import census_start, extension_start, grow


CASES = {
    'census': [(424, 'four-knot sample maximum'), (201, 'four-knot one-class control'),
               (98, 'four-knot start whose grown stages have two classes')],
    'extension': [(407, 'six-knot start with two class bits'),
                  (1001, 'seven-knot start attaining the extension maximum'),
                  (2342, 'eight-knot start with two free classes')],
}


def run(pilot):
    results = []
    for kind, chosen in CASES.items():
        archived = {(int(r['structure'].split()[-1]), r['round']): r for r in records(kind)}
        for i, description in chosen:
            knots = (census_start if kind == 'census' else extension_start)(i)
            if (kind, i) == ('census', 424):
                held = Counter(d for row in knots for d in row)
                assert len(knots) == 4 and all(sum(held[d] == 1 for d in row) == 2 for row in knots)
                meetings = [[len(set(a) & set(b)) for b in knots if b != a] for a in knots]
                assert all(sorted(row) == [0, 1, 1] for row in meetings)
            source = knots
            for r in range(5):
                record = archived[i, r]
                for pinned, setting in enumerate(SETTINGS):
                    result = measure(knots, bool(pinned))
                    compare(result, record[setting])
                    results.append(dict(roster=kind, source_id=i, description=description,
                                        source=source if not r and not pinned else None,
                                        round=r, pinned=bool(pinned), **result))
                if pilot:
                    return results
                if r < 4:
                    new = grow(knots)
                    if new == knots:
                        assert (i, r + 1) not in archived
                        break
                    knots = new
    return results


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('--pilot', action='store_true')
    print(json.dumps(run(p.parse_args().pilot), indent=1))
