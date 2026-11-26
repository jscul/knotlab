"""Count eligible additions beyond the two placement limits after round three."""
import argparse
from collections import Counter
import json

from mark_check import core, eng, read_rows, STUDY


def check(row):
    recorded = Counter(c['linked'] for c in row['changes'])
    if recorded[True] < 5 and recorded[False] < 2:
        return [0, 0]
    places, roles, _ = core.jam.changed(row['A'], row['B'], 3, None, 'meeting')
    g = core.ring_line.Growth(places, roles, core.law_of(*row['law']))
    g.run(3, 1500)
    s = g.S
    roster = eng.build_roster(s, eng.live_members(s), 'parts', eng.Guard(1000), parts=True)
    classes = eng.classes_of_parts(s, roster.parts)
    receiver = {classes[roster.part_of[u]] for u in roster.members if g.anc[u] == {'A'}}
    counts = Counter(classes[roster.part_of[u]] in receiver for u in roster.members if g.anc[u] == {'B'})
    assert receiver and [min(counts[True], 5),min(counts[False], 2)] == [recorded[True],recorded[False]]
    return [counts[value] - recorded[value] for value in (True, False)]


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--limit', type=int)
    args = parser.parse_args()
    core.receivers.register()
    rows = [r for r in read_rows(STUDY / 'parity_runs.jsonl.gz', None) if 'law' in r]
    selected = [r for r in rows if sum(c['linked'] for c in r['changes']) == 5 or
                sum(not c['linked'] for c in r['changes']) == 2]
    counts = Counter()
    examples = {}
    for r in selected[:args.limit]:
        linked, unlinked = check(r)
        counts.update({'records checked at a limit': 1, 'linked places omitted': linked,
                       'unlinked places omitted': unlinked, 'records with omissions': int(bool(linked + unlinked))})
        if linked or unlinked:
            examples.setdefault(str(r['law']), [r['A'],r['B'],linked,unlinked])
    print(json.dumps({'all at either limit': len(selected), 'counts': counts, 'first example per law': examples},indent=2))
