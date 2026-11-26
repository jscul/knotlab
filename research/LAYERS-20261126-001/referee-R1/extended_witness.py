"""Check the sampled witness with literal shortest changes and class observations.

Run with PYTHONPATH=tools for the public knot test on actual projected states.
"""

import argparse
import json
from pathlib import Path
import sys

from extended_rounds import connected
from frozen_recount_core import all_words, grow, mask, motion, names_of, owners_of, projected_equality
from knotlab.knots import check_knot
from knotlab.relations import Relation


HERE = Path(__file__).resolve().parent
CANONICAL_GROWTH = HERE.parents[2] / 'experiments' / (
    'NAE-GROWTH-20261119-001B/NAE-GROWTH-20261119-001B-E001_nae'
)


def parity(word, functional):
    return (word & functional).bit_count() % 2


def projected_knot(row, allowed):
    variables = tuple(f"x{place}" for place in row)
    joint_states = frozenset(tuple(bool(word & (1 << place)) for place in row) for word in allowed)
    relation = Relation(variables, joint_states)
    return check_knot(relation, variables[:-1], variables[-1]).is_knot


def certificate(witness, depth, canonical):
    rows = tuple(tuple(row) for row in witness['start supports'])
    ownership = owners_of(rows)
    meetings = [(*holders, 1) for holders in ownership.values() if len(holders) == 2]
    assert connected(len(rows), meetings)
    parities = witness['stages'][0]['analysis']['parities independent of listed readings']
    first, second = map(mask, parities)

    def label_value(word):
        return parity(word, first) | (parity(word, second) << 1)

    previous = motion(rows)
    assert all(projected_knot(row, all_words(word & mask(row) for word in previous.allowed)) for row in rows)
    canonical_model = canonical.S.from_junctions(rows)
    canonical_rule = canonical.parity_rule(canonical.F.fewest)
    source_labels = [label for label in (first, second, first ^ second) if previous.is_label(label)]
    report = {
        'cohort': witness['cohort'],
        'sample index': witness['sample index'],
        'start supports': rows,
        'start classes': previous.classes,
        'start supports passed K1–K3': len(rows),
        'connected through shared distinctions': True,
        'two parities over start distinctions': parities,
        'parities also labeling a start class': [list(names_of(label)) for label in source_labels],
        'rounds': [],
    }
    for stage in witness['stages'][:depth]:
        growth = grow(rows)
        assert growth.status == 'funded'
        rows = growth.stage
        assert rows == tuple(tuple(row) for row in stage['supports'])
        canonical_record = canonical_model.step(canonical_rule, None)
        assert canonical_record['new'] == len(growth.births)
        assert tuple(tuple(row) for row in canonical_model.bits_of) == rows
        result = motion(rows)
        assert result.classes == (1 << stage['analysis']['label rank']) == 4
        assert projected_equality(previous, result)
        assert all(parity(move, first) == parity(move, second) == 0 for move in result.moves)
        assert all_words(label_value(word) for word in result.allowed) == {0, 1, 2, 3}
        offset = 1 + max(owners_of(rows))
        visible_counts = []
        for row in rows:
            visible = mask(row)
            joint = all_words((word & visible) | (label_value(word) << offset) for word in result.allowed)
            observations = {word & visible for word in joint}
            assert len(joint) == 4 * len(observations)
            assert projected_knot(row, observations)
            visible_counts.append(len(observations))
        report['rounds'].append({
            'round': stage['round'],
            'new supports': rows[len(previous.rows):],
            'allowed rank': len(result.allowed),
            'move rank': len(result.move_basis),
            'shortest changes counting ties per distinction': result.ties,
            'distinct shortest changes': len(result.moves),
            'supports passed K1–K3': len(rows),
            'exact stage matched declared growth engine': True,
            'both parities kept by every shortest change': True,
            'every parity pair occurs at every allowed individual support reading': True,
            'number of allowed readings on each listed support': visible_counts,
        })
        previous = result
    return report


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--pilot', action='store_true')
    args = parser.parse_args()
    original = json.loads((HERE / 'extended_results.json').read_text())
    sys.path.insert(0, str(CANONICAL_GROWTH))
    import naelib

    reports = [certificate(witness, 1 if args.pilot else len(witness['stages']), naelib)
               for witness in original['witnesses']]
    print(json.dumps(reports, indent=2))
