"""Fresh scalar placement controls and a finite counterexample about tail classes."""
import itertools
import json
import random
from pathlib import Path

from fresh_patterns import direct_state, pattern, words


def scalar_pattern(key, n, reverse=True):
    catalog = words(key[0])
    output = set()
    for x in range(1 << n):
        for placement in key[4]:
            images = []
            for i in placement:
                y = x
                w = catalog[i]
                for q in reversed(w) if reverse else w:
                    y = direct_state(key, q, y, n)
                images.append(y)
            if len(set(images)) == 3:
                output.add(tuple(sorted(images)))
    return sorted(output)


def main():
    rng = random.Random(90261)
    checked = 0
    order_distinguished = 0
    for s in range(1, 6):
        for _ in range(8):
            count = len(words(s))
            placements = list(itertools.combinations(range(count), 3))
            selected = rng.sample(placements, min(len(placements), 5))
            key = [s, [rng.randrange(2) for _ in range(s)], [rng.randrange(s) for _ in range(s)],
                   [rng.randrange(s) for _ in range(s)], selected]
            for n in range(1, 6):
                expected = scalar_pattern(key, n)
                assert expected == pattern(key, n)
                checked += 1
                order_distinguished += expected != scalar_pattern(key, n, reverse=False)
    # This explicit fixture was found independently by the wording reviewer
    # in a permitted raw record. Test it again through this task's fresh builder.
    key = [2, [1, 0], [1, 0], [1, 1], [[0, 1, 6], [2, 3, 5], [3, 4, 6]]]
    knots = pattern(key, 4)
    tail_classes = {}
    for tail in range(4):
        inner = sorted({tuple(x >> 2 for x in triple) for triple in knots
                        if all((x & 3) == tail for x in triple)})
        tail_classes[f'{tail:02b}'] = inner
    assert tail_classes['00'] == [] and tail_classes['01'] == []
    assert tail_classes['10'] == [(0, 1, 2), (0, 1, 3)]
    assert tail_classes['10'] == tail_classes['11']
    result = {'scalar_vs_inductive_pattern_cases': checked,
              'incorrect_word_order_detected_cases': order_distinguished,
              'tail_inner_invariance_counterexample': {'key': key, 'level': 4, 'suffix_length': 2,
                                                      'knots': knots, 'projected_inner_knots': tail_classes}}
    assert order_distinguished > 0
    (Path(__file__).resolve().parent / 'pattern_controls.json').write_text(json.dumps(result, indent=2) + '\n')
    print(json.dumps(result))


if __name__ == '__main__':
    main()
