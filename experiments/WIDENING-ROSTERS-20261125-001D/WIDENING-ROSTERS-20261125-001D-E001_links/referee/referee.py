"""Regrow the frozen taking rules and reconstruct first meetings from their actual supports."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
from itertools import combinations
import json
from pathlib import Path
from resource import RUSAGE_SELF, getrusage
import sys
from time import perf_counter

from project import NAEProjector, ParityProjector, read_projection


HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
FAMILY = HERE.parent
B_ENGINE = ROOT / ('experiments/WHAT-A-BIRTH-CARRIES-20261125-001B/'
                   'WHAT-A-BIRTH-CARRIES-20261125-001B-E001_link_through_a_made_knot')
LOCAL = ROOT / ('experiments/LOCAL-ROUND-20261123-001A/'
                'LOCAL-ROUND-20261123-001A-E001_local_round')
STARTS = ROOT / 'research/WHAT-A-BIRTH-CARRIES-20261125-001B/starts.json'
CENSUS = ROOT / 'research/KNOTS-WITHIN-REACH-20261125-001A/census_starts.json'
sys.path.insert(0, str(B_ENGINE))
sys.path.insert(0, str(LOCAL))
import eng
from lr_core import components, compute_groups


def read_json(path):
    return json.loads(path.read_bytes())


def ring_stars(counts):
    stars = [[] for _ in counts]
    for i in range(len(counts)):
        stars[i].append(i)
        stars[(i + 1) % len(counts)].append(i)
    distinction = len(counts)
    for star, count in zip(stars, counts, strict=True):
        star.extend(range(distinction, distinction + count))
        distinction += count
    return stars


def raw_start(name, named, census):
    if name.startswith('census:'):
        return census[int(name.split(':')[1])]['stars']
    if name.startswith('ringk:'):
        return ring_stars([int(n) for n in name.split(':')[1].split(',')])
    if name in named['stars']:
        return named['stars'][name]
    if name == named['extra']['name']:
        return named['extra']['stars']
    raise ValueError(f'unknown frozen start: {name}')


class Selector:
    """Offer sets are read once from the same before-round structure for all births."""

    def __init__(self, stage, rule, recent):
        self.places = stage.places
        self.holders = stage.holders
        self.rule = rule
        self.recent = recent
        self.meetings = {}
        self.offers_cache = {}

    def meets(self, knot):
        if knot not in self.meetings:
            self.meetings[knot] = {holder for d in self.places[knot] for holder in self.holders[d]}
            self.meetings[knot].discard(knot)
        return self.meetings[knot]

    def offers(self, parents):
        if parents in self.offers_cache:
            return self.offers_cache[parents]
        near_by_parent = [self.meets(parent) for parent in parents]
        two_by_parent = []
        for parent, near in zip(parents, near_by_parent, strict=True):
            two = near.union(*(self.meets(knot) for knot in near))
            two.discard(parent)
            two_by_parent.append(two)
        near_all = set.intersection(*near_by_parent) - set(parents)
        two_all = set.intersection(*two_by_parent) - set(parents)
        held = {distinction for parent in parents for distinction in self.places[parent]}
        suppliers = defaultdict(set)
        c1 = set()
        for knot in two_all:
            for distinction in self.places[knot]:
                if distinction not in held and len(self.holders[distinction]) >= 2:
                    suppliers[distinction].add(knot)
                    if knot in near_all:
                        c1.add(distinction)
        self.offers_cache[parents] = c1, suppliers
        return c1, suppliers

    def choose(self, stage, law, birth, roster):
        c1, suppliers = self.offers(birth['parents'])
        c2 = suppliers.keys()
        if len(c2) <= 1 or self.rule == 'SOLE':
            selected = c2
        elif self.rule == 'RECENT':
            selected = c2 & self.recent
        elif self.rule == 'OUTER':
            selected = c2 - c1
        elif self.rule == 'MOST':
            greatest = max(len(self.holders[distinction]) for distinction in c2)
            selected = {d for d in c2 if len(self.holders[d]) == greatest}
        else:
            raise ValueError(self.rule)
        if len(selected) != 1:
            return []
        distinction = next(iter(selected))
        return [(distinction, tuple(sorted(suppliers[distinction])))]


def grow(stars, case, rule, knot_law):
    law = eng.Law(case['ration'], case['treatment'], 'MET-SOLE', knot_law)
    guard = eng.Guard()
    stages = [eng.from_stars(stars)]
    rounds = []
    reach = []
    recent = set()
    stop = None
    original = eng.candidates
    try:
        for round_ in range(1, case['rounds'] + 1):
            before = stages[-1]
            after = before.copy()
            selector = Selector(before, rule, recent)
            eng.candidates = selector.choose
            try:
                record = eng.play_round(after, law, guard)
            except eng.GuardStop:
                stop = 'guard'
                break
            stages.append(after)
            rounds.append(record['births'])
            this_round = []
            for birth in record['births']:
                if birth['takes']:
                    c1, suppliers = selector.offers(birth['parents'])
                    for distinction in birth['takes']:
                        if distinction not in suppliers:
                            raise ValueError('birth took an ineligible distinction')
                        this_round.append({
                            'recipient': birth['id'], 'c': distinction,
                            'near_eligible': distinction in c1,
                            'c1': sorted(c1), 'c2': sorted(suppliers),
                        })
            reach.append(this_round)
            recent = {take['c'] for take in this_round}
            if after.n_knots > case['knot_bound']:
                stop = 'knots'
                break
    finally:
        eng.candidates = original
    return stages, rounds, reach, stop


def live_members(stage):
    return {holders[0] for d, holders in enumerate(stage.holders)
            if len(holders) == 1 and not stage.barred[d]}


@dataclass
class Phase:
    met: dict
    groups: list
    parts: list


def read_phase(stage, members):
    by_witness = defaultdict(set)
    for holders in stage.holders:
        roster_holders = [knot for knot in holders if knot in members]
        if not roster_holders:
            continue
        for witness in holders:
            by_witness[witness].update(roster_holders)
    met = {}
    for witness, met_members in by_witness.items():
        met_members.discard(witness)
        if len(met_members) >= 2:
            met[witness] = met_members
    family = {frozenset(value) for value in met.values()}
    return Phase(met, compute_groups(members, family),
                 [tuple(sorted(part)) for part in components(members, family)])


def part_classes(stage, parts):
    parent = list(range(len(parts)))

    def find(i):
        while parent[i] != i:
            parent[i] = parent[parent[i]]
            i = parent[i]
        return i

    part_of = {member: i for i, part in enumerate(parts) for member in part}
    for holders in stage.holders:
        classes = {find(part_of[member]) for member in holders if member in part_of}
        if classes:
            root = min(classes)
            for other in classes:
                parent[other] = root
    return [find(i) for i in range(len(parts))]


def flags(parts, stages, split):
    end = stages[-1]
    lineage = [0] * end.n_knots
    for i, part in enumerate(parts):
        for member in part:
            lineage[member] = 1 << i
    for knot in range(stages[split].n_knots, end.n_knots):
        for parent in end.parents[knot]:
            lineage[knot] |= lineage[parent]
    return lineage


def indices(bits):
    while bits:
        least = bits & -bits
        yield least.bit_length() - 1
        bits ^= least


def true_pairs(bits, classes, pending):
    for pair in combinations(indices(bits), 2):
        i, j = pair
        if pair in pending and classes[i] != classes[j]:
            yield pair


def ancestors(parents, knot):
    seen = set()
    todo = list(parents[knot])
    while todo:
        parent = todo.pop()
        if parent not in seen:
            seen.add(parent)
            todo.extend(parents[parent])
    return seen


def route_record(kind, w, u, v, after, supports, newborn=None, take=None):
    x = supports[u]
    y = supports[v]
    if take is None:
        x_arms = sorted(x & supports[w])
        y_arms = sorted(y & supports[w])
        contacts = sorted(x & y & supports[w])
    else:
        x_arms = y_arms = contacts = [take['c']]
    row = {
        'route': kind, 'w': w, 'u': u, 'v': v,
        'contacts': contacts, 'x_arms': x_arms, 'y_arms': y_arms,
        'a': sorted(x - y), 'b': sorted(y - x),
        'w_is_start': after.made[w] == 0,
        'w_ancestor_u': w in ancestors(after.parents, u),
        'w_ancestor_v': w in ancestors(after.parents, v),
        'start_held_contacts': [d for d in contacts
                                if any(after.made[p] == 0 for p in after.holders[d])],
    }
    if take is not None:
        row.update(newborn=newborn, pre_holder=w, near_eligible=take['near_eligible'])
    return row


def meeting_receipt(s, t, pair, kinds, parts, lineage, before, after, met, demand, takes):
    i, j = pair
    x = 1 << i
    y = 1 << j
    both = x | y
    supports = list(map(set, after.places))
    routes = {}
    witnesses = set()
    mixed = set()
    offers = {}
    linking_distinctions = set()
    for kind, phase in (('met', met), ('demand', demand)):
        for w, met_members in phase.met.items():
            if w >= before.n_knots:
                continue
            descended_x = [u for u in met_members if lineage[u] & x]
            descended_y = [v for v in met_members if lineage[v] & y]
            if not descended_x or not descended_y:
                continue
            witnesses.add(w)
            for knot in set(descended_x + descended_y):
                linking_distinctions.update(supports[w] & supports[knot])
            from_x = [u for u in descended_x if lineage[u] & both == x]
            from_y = [v for v in descended_y if lineage[v] & both == y]
            if not from_x or not from_y:
                mixed.add((kind, w))
            for u in from_x:
                for v in from_y:
                    routes[(kind, w, u, v)] = route_record(kind, w, u, v, after, supports)
    for take in takes:
        newborn = take['recipient']
        taking = lineage[newborn] & both
        for w in before.holders[take['c']]:
            holding = lineage[w] & both
            if not (taking & x and holding & y or taking & y and holding & x):
                continue
            witnesses.add(w)
            offers[newborn] = {key: take[key] for key in ('c', 'c1', 'c2')}
            # The older meeting definition counts every contact of a linking knot
            # with either descent. The actual cross-take identity is kept on its route.
            for knot, support in enumerate(supports):
                if lineage[knot] & both:
                    linking_distinctions.update(supports[w] & support)
            if taking == x and holding == y:
                u, v = newborn, w
            elif taking == y and holding == x:
                u, v = w, newborn
            else:
                mixed.add(('take', w))
                continue
            routes[('take', w, u, v)] = route_record('take', w, u, v, after, supports, newborn, take)
    return {
        's': s, 't': t, 'X': parts[i], 'Y': parts[j],
        'meeting_types': sorted(kinds),
        'routes': [row for _, row in sorted(routes.items())],
        'linking_knots': sorted(witnesses),
        'linking_distinctions': sorted(linking_distinctions),
        'mixed_witnesses': [list(value) for value in sorted(mixed)],
        'take_offers': offers,
        'only_made_knots': bool(witnesses) and all(after.made[w] > 0 for w in witnesses),
        'start_held_linking_distinctions': [
            d for d in sorted(linking_distinctions)
            if any(after.made[h] == 0 for h in after.holders[d])],
    }


def first_meetings(stages, rounds, reach, splits):
    live = [live_members(stage) for stage in stages]
    met_phases = [read_phase(stage, members) for stage, members in zip(stages, live, strict=True)]
    demand_phases = [read_phase(stages[t], live[t] | {b['id'] for b in births})
                     for t, births in enumerate(rounds, 1)]
    events = []
    for s in splits:
        if s >= len(stages) - 1:
            continue
        parts = met_phases[s].parts
        classes = part_classes(stages[s], parts)
        pending = {pair for pair in combinations(range(len(parts)), 2)
                   if classes[pair[0]] != classes[pair[1]]}
        if not pending:
            continue
        lineage = flags(parts, stages, s)
        for t in range(s + 1, len(stages)):
            before, after = stages[t - 1:t + 1]
            met, demand = met_phases[t - 1], demand_phases[t - 1]
            taken = reach[t - 1]
            seen = defaultdict(set)
            for kind, phase in (('met', met), ('demand', demand)):
                for group in phase.groups:
                    descended = 0
                    for knot in group:
                        descended |= lineage[knot]
                    for pair in true_pairs(descended, classes, pending):
                        seen[pair].add(kind)
            for take in taken:
                for i in indices(lineage[take['recipient']]):
                    for holder in before.holders[take['c']]:
                        for j in indices(lineage[holder]):
                            pair = (min(i, j), max(i, j))
                            if pair in pending:
                                seen[pair].add('take')
            for pair, kinds in sorted(seen.items()):
                events.append(meeting_receipt(s, t, pair, kinds, parts, lineage, before,
                                              after, met, demand, taken))
                pending.remove(pair)
            if not pending:
                break
    return sorted(events, key=lambda e: (e['s'], e['X'], e['Y'], e['t']))


def place_kind(stage, distinction):
    if len(stage.holders[distinction]) > 1:
        return 'shared'
    return 'barred_loose' if stage.barred[distinction] else 'usable_loose'


def projected_rows(case_id, knot_law, stages, events, output):
    projectors = {}
    classes = Counter()
    seen_masks = set()
    annotations = Counter()
    digest = hashlib.sha256()
    buffer = bytearray()

    def flush():
        digest.update(buffer)
        output.write(buffer)
        buffer.clear()

    def projector(round_):
        if round_ not in projectors:
            stage = stages[round_]
            if knot_law == 'parity':
                projectors[round_] = ParityProjector(stage.places)
            else:
                projectors[round_] = NAEProjector(stage.places, stage.n_start)
        return projectors[round_]

    try:
        for event in events:
            t = event['t']
            old = stages[t - 1].n_distinctions
            support = stages[t]
            for route in event['routes']:
                fields = [case_id, knot_law, event['s'], event['X'], event['Y'], t,
                          route['route'], route['w'], route['u'], route['v']]
                prefix = (json.dumps(fields, separators=(',', ':'))[:-1] + ',').encode('utf-8')
                a_count, b_count, c_count = map(len, (route['a'], route['b'], route['contacts']))
                for a in route['a']:
                    annotations[f'a_{place_kind(support, a)}'] += b_count * c_count
                for b in route['b']:
                    annotations[f'b_{place_kind(support, b)}'] += a_count * c_count
                for c in route['contacts']:
                    annotations[f'c_{place_kind(support, c)}'] += a_count * b_count
                    for a in route['a']:
                        for b in route['b']:
                            mask = projector(t).project((a, b, c))
                            pre = projector(t - 1).project((a, b)) if a < old and b < old else None
                            _, _, _, _, kind = read_projection(mask)
                            classes[kind] += 1
                            seen_masks.add(mask)
                            suffix = f'{c},{a},{b},{mask},{pre if pre is not None else "null"}]\n'
                            buffer.extend(prefix)
                            buffer.extend(suffix.encode('ascii'))
                            if len(buffer) >= 131072:
                                flush()
        flush()
        counters = {'witness_pairs': 0, 'sat_queries': 0}
        for value in projectors.values():
            if isinstance(value, NAEProjector):
                counters['witness_pairs'] += value.witnessed_pairs
                counters['sat_queries'] += value.sat_queries
    finally:
        for value in projectors.values():
            value.close()
    return digest.hexdigest(), dict(classes), sorted(seen_masks), dict(+annotations), counters


def assay_or_run(case, rule, knot_law, stars, assay, mask_dir):
    start = perf_counter()
    stages, rounds, reach, stop = grow(stars, case, rule, knot_law)
    after_growth = perf_counter()
    events = first_meetings(stages, rounds, reach, case['splits'])
    after_meetings = perf_counter()
    if rule == 'MOST':
        mask_path = mask_dir / f"{case['id']}--{rule}--{knot_law}.jsonl.gz"
        with mask_path.open('xb') as file, gzip.GzipFile(
                filename='', mode='wb', fileobj=file, compresslevel=1, mtime=0) as output:
            mask_digest, classes, masks, annotations, sat_counts = projected_rows(
                case['id'], knot_law, stages, events, output)
        mask_bytes = mask_path.stat().st_size
    after_projection = perf_counter()
    metrics = {'grow_seconds': after_growth - start,
               'meeting_seconds': after_meetings - after_growth,
               'projection_seconds': after_projection - after_meetings,
               'seconds': after_projection - start,
               'peak_self_rss_kib': getrusage(RUSAGE_SELF).ru_maxrss}
    if assay:
        if rule == 'MOST':
            mask_path.unlink()
            metrics['temporary_receipt_bytes'] = mask_bytes
        return metrics
    result = {
        'case': case['id'], 'kl': knot_law, 'rule': rule, 'start': case['start'],
        'stop': stop, 'rounds_read': len(rounds), 'knots': stages[-1].n_knots,
        'reach': reach, 'events': events, 'metrics': metrics,
    }
    if rule == 'MOST':
        result.update(mask_file=mask_path.name, projection_sha256=mask_digest,
                      projection_count=sum(classes.values()), mask_bytes=mask_bytes,
                      classifications=classes, distinct_masks=masks, literal_annotations=annotations,
                      sat_counts=sat_counts)
    return result


def setup(params):
    global settings
    contract = read_json(FAMILY / 'contract.json')
    case_path = FAMILY / contract['cases']
    for path in (case_path, STARTS, CENSUS):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != contract['inputs'][str(path.relative_to(ROOT))]:
            raise ValueError(f'frozen input changed: {path}')
    mask_dir = Path(params['mask_dir']).resolve()
    mask_dir.mkdir(parents=True, exist_ok=True)
    settings = {'cases': read_json(case_path), 'named': read_json(STARTS),
                'census': read_json(CENSUS), 'rules': contract['rules'],
                'knot_laws': contract['knot_laws'], 'params': params, 'mask_dir': mask_dir}


def cases():
    params = settings['params']
    chosen = settings['cases'][:int(params.get('limit', len(settings['cases'])))]
    for case in chosen:
        if params.get('case_id', case['id']) != case['id']:
            continue
        for rule in settings['rules']:
            if params.get('rule', rule) != rule:
                continue
            for knot_law in settings['knot_laws']:
                if params.get('kl', knot_law) == knot_law:
                    yield f"{case['id']}--{rule}--{knot_law}", (case, rule, knot_law)


def run(case_id, payload):
    case, rule, knot_law = payload
    stars = raw_start(case['start'], settings['named'], settings['census'])
    assay = settings['params'].get('assay') == '1'
    return assay_or_run(case, rule, knot_law, stars, assay, settings['mask_dir'])


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--case-id', required=True)
    parser.add_argument('--rule')
    parser.add_argument('--kl')
    parser.add_argument('--assay', action='store_true')
    parser.add_argument('--mask-dir', required=True)
    args = vars(parser.parse_args())
    args['assay'] = str(int(args['assay']))
    setup({key: value for key, value in args.items() if value is not None})
    for case_id, payload in cases():
        print(json.dumps({'case': case_id, 'result': run(case_id, payload)}), flush=True)
