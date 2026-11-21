"""Fresh named controls for the frozen B273 source weightings."""

from collections import Counter
from hashlib import sha256
from itertools import combinations
from pathlib import Path
from random import Random
import sys


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
LEAF = HERE.parent.name
OUT = ROOT / 'artifacts' / LEAF / HERE.name
PREVIOUS = 'LOOSE-NAMES-AND-SPENT-JOINS-20261120-001A'
PREVIOUS_FAMILY = PREVIOUS + '-E001_loose_roles'
sys.path.insert(0, str(ROOT / 'experiments' / PREVIOUS / PREVIOUS_FAMILY))
from control_measure import WEIGHTS, read, record, save, stages, width
from control_panels import LAWS, PANELS, numerical, rate_dict, source_choice, summarize, template_observations, verify_marginal
from control_role_rows import signed_table
from explosive_stages import align_replay, indexed_rings
from census_stages import connected_archive


def all_sign_screen(stage, reading):
    screen = reading['screen']
    loose = set(screen['actual_loose'])
    signs = signed_table(stage['width'], reading['total'], reading['disagreement_counts'])
    extra = []
    kept = []
    for p in screen['predictions']:
        if p['rejections']:
            continue
        forbidden = next(((a, b) for a, b in combinations(p['inputs'], 2)
                          if all(signs[a][z] == signs[b][z] for z in range(len(signs)) if z not in (a, b))), None)
        if forbidden is None:
            kept.append(p['name'])
        else:
            assert p['name'] not in loose
            extra.append({'candidate': p['name'], 'input_twins': forbidden})
    return {'candidates': kept, 'removed_spent': extra, 'remaining_spent': sorted(set(kept) - loose)}


def measure_draw(law, named, canonical):
    actual = stages(named, law)
    template, tables = template_observations(canonical, law)
    assert actual['attempts'] == template['attempts']
    preceding = numerical({'rows': named, 'width': width(named), 'limits': (len(named),)}, law, 'uniform')
    old_total, old_counts, _ = preceding
    assert old_total is not None
    for stage, model, numbers in zip(actual['stages'], template['stages'], tables, strict=True):
        transport = align_replay(model, stage)
        weights = {}
        stage['transport_template_to_draw'] = transport
        stage['weights'] = weights
        for w, (total, counts, cost) in numbers.items():
            if total is None:
                weights[w] = cost
                continue
            moved = {tuple(sorted((transport[a], transport[b]))): c for (a, b), c in counts.items()}
            ordered = {pair: moved[pair] for pair in combinations(range(stage['width']), 2)}
            weights[w] = record(stage, law, w, total, ordered, cost)
            if law == 'nae':
                weights[w]['all_sign'] = all_sign_screen(stage, weights[w])
        if 'unread' not in weights['inherited']:
            current = weights['inherited']
            if old_counts is not None:
                stage['inherited_preserved_pair_entries'] = verify_marginal(old_counts, old_total, stage['width'], current)
            old_total, old_counts = current['total'], rate_dict(stage['width'], current)
        else:
            old_counts = None
        if all('unread' not in weights[w] for w in WEIGHTS):
            a, b = (weights[w] for w in WEIGHTS)
            stage['changed_pair_entries'] = sum(x * b['total'] != y * a['total']
                                                for x, y in zip(a['disagreement_counts'], b['disagreement_counts'], strict=True))
    return actual


def draw_panel(law, panel, small, rings):
    digest = sha256(f'{LEAF}|{law}|{panel}|918273'.encode()).hexdigest()
    random = Random(int(digest, 16))
    result = []
    for i in range(1, 33):
        basis, canonical, details = source_choice(random, panel, small, rings)
        movement = list(range(width(basis)))
        random.shuffle(movement)
        named = tuple(tuple(sorted(movement[x] for x in row)) for row in basis)
        result.append(dict(draw=i, source_permutation=movement, **details, **measure_draw(law, named, canonical)))
    return {'seed_sha256': digest, 'draws': result}


def all_sign_totals(population, age, weighting):
    counts = Counter({k: 0 for k in ('read', 'removed_spent', 'remaining_spent', 'draws_with_remaining_spent')})
    for draw in population['draws']:
        if len(draw['stages']) < age:
            continue
        measure = draw['stages'][age - 1]['weights'][weighting]
        if 'unread' in measure:
            continue
        last = measure['all_sign']
        counts['read'] += 1
        counts['removed_spent'] += len(last['removed_spent'])
        counts['remaining_spent'] += len(last['remaining_spent'])
        counts['draws_with_remaining_spent'] += bool(last['remaining_spent'])
    return counts


def main():
    catalogue = connected_archive()
    rings = tuple(indexed_rings())
    assert len(rings) == 40
    OUT.mkdir(parents=True, exist_ok=True)
    raw = {law: {} for law in LAWS}
    counts = {law: {} for law in LAWS}
    for law in LAWS:
        for panel in PANELS:
            data = draw_panel(law, panel, catalogue[law], rings)
            raw[law][panel] = data
            counts[law][panel] = summarize(data)
            for s in counts[law][panel]:
                if law == 'nae':
                    for w in WEIGHTS:
                        s['weights'][w]['all_sign'] = all_sign_totals(data, s['age'], w)
                print(law, panel, s['age'], s['observed'], s['attempts'], flush=True)
    save(OUT / 'control_draws.json.gz', raw)
    save(OUT / 'control_draw_summary.json', counts)


if __name__ == '__main__':
    main()
