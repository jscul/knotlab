"""Rank observed whole and component closures and export fixed named witnesses."""

from panels_sources import COUNTS


PANEL_ORDER = {panel: i for i, panel in enumerate(COUNTS)}


def witness(draw, cut, birth):
    history = draw['laws']['parity']['cuts']
    before = draw['source_rows'] if cut['age'] == 1 else history[cut['age'] - 2]['after_rows']
    inside = next(c for c in cut['components'] if birth['holder'] in c['holders'])
    return {'panel': draw['panel'], 'draw': draw['draw'], 'age': cut['age'], 'source_rows': draw['source_rows'],
            'before_rows': before, 'after_rows': cut['after_rows'], 'holder': birth['holder'], 'parents': birth['parents'],
            'inputs': birth['inputs'], 'fresh': birth['fresh'], 'new_names': birth['new_names'], 'support': birth['support'],
            'component_holders': inside['holders'], 'component_names': inside['names'], 'whole_closed': cut['whole_closed'],
            'births': cut['births'], 'closing_event': birth if 'operator_positive' in birth else None,
            'source_provenance': {k: v for k, v in draw.items() if k not in ('source_rows', 'laws')},
            'parity_history': history[:cut['age']],
            'nae_first_cut': next(iter(draw['laws']['nae']['cuts']), None)}


def rank(draw, cut, birth, full):
    size = (len(cut['after_rows']), sum(len(c['names']) for c in cut['components'])) if full else (
        len(birth['component_holders']), len(birth['component_names']))
    return (*size, birth['closing_arity'], cut['age'], PANEL_ORDER[draw['panel']], draw['draw'], birth['holder'])


def publish_minima(records):
    parity_events = [(draw, cut, event) for draw in records for cut in draw['laws']['parity']['cuts']
                     for event in cut['new_closing_components']]

    def minimum(cases, full):
        if not cases:
            return None
        found = min(cases, key=lambda t: rank(*t, full))
        result = witness(*found)
        return dict(result, ranking_key=rank(*found, full))

    def compare(cases):
        positive = [t for t in cases if t[-1]['operator_positive']]
        whole = [t for t in positive if t[1]['whole_closed']]
        continuing = [t for t in positive if not t[1]['whole_closed']]
        return {'whole': minimum(whole, True), 'component': minimum(positive, False),
                'continuing_component': minimum(continuing, False),
                'whole_arity_at_least_three': minimum([t for t in whole if t[-1]['closing_arity'] >= 3], True),
                'component_arity_at_least_three': minimum([t for t in positive if t[-1]['closing_arity'] >= 3], False),
                'continuing_arity_at_least_three': minimum([t for t in continuing if t[-1]['closing_arity'] >= 3], False)}

    positive_fresh = next((witness(draw, cut, birth) for panel in ('T', 'E') for draw in records if draw['panel'] == panel
                           for cut in draw['laws']['parity']['cuts'] for birth in cut['births'] if birth['fresh'] > 0), None)
    return {**compare(parity_events), 'negative': minimum([x for x in parity_events if not x[-1]['operator_positive']], False),
            'positive_fresh': positive_fresh,
            'panels': {p: compare([t for t in parity_events if t[0]['panel'] == p]) for p in sorted({r['panel'] for r in records})}}
