"""Blind choices on a fixed candidate bank, then real search-and-check deployments."""
from __future__ import annotations

import argparse
import base64
from collections import Counter
from hashlib import sha256
import heapq
import json
from pathlib import Path
import sys
import time
import zlib

HERE = Path(__file__).resolve().parent
TICKET = 'RENAME-SELECT-20261114-001'
ROOT = HERE.parents[2]
sys.path.insert(0, str(ROOT / 'research' / TICKET))
sys.path.insert(0, str(HERE))

import problems
import selection
import stream

SEEDS = (101, 211, 307)
CHECKPOINTS = (1568, 3104, 6176, 12320, 24608, 49184)
CAP = CHECKPOINTS[-1]
SUBMISSIONS = 4
DEPLOYMENTS = ('shortest', 'fitted', 'direct')


def compact(data):
    return json.dumps(data, sort_keys=True, separators=(',', ':')).encode()


def fingerprint(data):
    return sha256(compact(data)).hexdigest()


def event_record(event):
    if event is None:
        return None
    return {'proposal': event['first_proposal'], 'genome': bytes(event['genome']).hex(),
            'expanded_length': event['expanded_length'], 'macro_calls': event['macro_calls']}


def make_stream(seed, condition, observations, grammar):
    return stream.CandidateStream(seed, condition, tuple(observations), tuple(observations.values()),
                                  grammar=grammar)


def bank_and_choices(seed, condition, observations):
    """No task ID, specification, hidden answers or verifier is provided here."""
    grammar = stream.make_grammar()
    source = make_stream(seed, condition, observations, grammar)
    source.advance_to(CAP)
    snap = source.snapshot()
    events = snap['new_perfect_events']
    choices, rankings, models = {}, {}, {}
    for mode in selection.MODES:
        ranker = selection.Ranker(mode, observations, selection.Predictions(grammar))
        ranking = sorted(range(len(events)), key=lambda i: ranker.key(events[i]))
        rankings[mode] = ranking
        choices[mode] = event_record(events[ranking[0]]) if ranking else None
        models[mode] = ranker.model
    rows = [[e['first_proposal'], bytes(e['genome']).hex()] for e in events]
    blob = compact(rows)
    result = {'training_observations': [[list(p), y] for p, y in observations.items()],
              'bank_count': len(events), 'bank_sha256': sha256(blob).hexdigest(),
              'bank_zlib_base64': base64.b64encode(zlib.compress(blob, 6)).decode(),
              'choices': choices, 'models': models, 'training_best': event_record(snap['best']),
              'initial_population_sha256': snap['initial_population_sha256'],
              'whole_search_cost': snap['prefix_cost']}
    result['blind_commitment'] = fingerprint([result['bank_sha256'], models, choices])
    return grammar, events, rankings, result


def assess_choices(mask, grammar, events, rankings, blind):
    """Offline scientific measurement, with all choices already fixed."""
    if blind['blind_commitment'] != fingerprint([blind['bank_sha256'], blind['models'], blind['choices']]):
        raise ValueError('Blind selection changed')
    held_truth = sum(((mask >> problems.index(p)) & 1) << i for i, p in enumerate(problems.HELD))
    effects = []
    gram_cache = selection.Predictions(grammar)
    for e in events:
        genome = tuple(e['genome'])
        bits = gram_cache.predict(genome, problems.HELD, 'evaluation')
        effects.append(sum(bit << i for i, bit in enumerate(bits)))
    valid = sum(v == held_truth for v in effects)
    scores = {}
    for mode, order in rankings.items():
        worst_left = len(events) - valid
        wins = 0
        for i in order:
            if effects[i] == held_truth:
                wins += worst_left
            else:
                worst_left -= 1
        chosen = effects[order[0]] if order else None
        scores[mode] = {'held_correct': None if chosen is None else 9 - (chosen ^ held_truth).bit_count(),
                        'exact': chosen == held_truth, 'held_prediction_mask': chosen,
                        'correct_pair_choices': wins, 'eligible_pairs': valid * (len(events)-valid)}
    return {'held_truth_mask': held_truth, 'n_exact_in_pool': valid, 'distinct_held_predictions': len(set(effects)),
            'scores': scores, 'offline_evaluation_cost': dict(gram_cache.cost)}


class Certificate:
    """The strategy receives one pass/fail bit and no failing test identity or value."""
    def __init__(self, hidden_cells, hidden_label, prediction_cache):
        self.cells = hidden_cells
        self.hidden_label = hidden_label
        self.known_truth = {}
        self.predictions = prediction_cache
        self.cost = Counter()

    def passes(self, genome):
        for cell in self.cells:
            bit, = self.predictions.predict(genome, (cell,), 'verification')
            if cell not in self.known_truth:
                self.known_truth[cell] = self.hidden_label(cell)
                self.cost['fresh_truth_labels'] += 1
            self.cost['truth_reads'] += 1
            self.cost['answer_comparisons'] += 1
            if bit != self.known_truth[cell]:
                return False
        return True


def account(prefix, n, observations, ranker, predictions, certificate):
    # Fixed per-proposal fitness is two ANDs and one complement across the lanes.
    search = prefix['program_plus_readout_logical_gates']
    fitness = 3 * n * len(observations)
    fit = ranker.cost if ranker else Counter()
    pc, vc = predictions.cost, certificate.cost
    model_fit = fit['fit_label_reads'] + fit['fit_comparisons']
    rank_work = pc['ranking_program_gates'] + pc['ranking_readout_gates'] + fit['candidate_vote_comparisons']
    verification = (pc['verification_program_gates'] + pc['verification_readout_gates'] +
                    vc['truth_reads'] + vc['answer_comparisons'] + vc['fresh_truth_labels'])
    components = {'training_label_reads': len(observations), 'search_program_and_readout': search,
                  'fitness_bit_operations': fitness, 'fit_label_reads_and_comparisons': model_fit,
                  'rank_prediction_and_comparison': rank_work, 'certificate': verification}
    return {'work_units': sum(components.values()), 'components': components,
            'search': prefix, 'fit_and_ranking': dict(fit), 'prediction': dict(pc), 'checking': dict(vc)}


def deploy(seed, condition, observations, mode, hidden_cells, hidden_label):
    """Each call actually runs until certification or the fixed cap, with independent caches."""
    started = time.perf_counter()
    grammar = stream.make_grammar()
    src = make_stream(seed, condition, observations, grammar)
    cache = selection.Predictions(grammar)
    ranker = None if mode == 'direct' else selection.Ranker(mode, observations, cache)
    verifier = Certificate(hidden_cells, hidden_label, cache)
    cursor = 0
    attempted = set()
    requests = []
    bank = []
    returned = None
    n = 0
    if mode == 'direct':
        while n < CAP and returned is None:
            src.advance_to_next_perfect_or(CAP)
            snap = src.snapshot(event_cursor=cursor)
            n, cursor = snap['proposal'], snap['event_cursor']
            for event in snap['new_perfect_events']:
                genome = tuple(event['genome'])
                passed = verifier.passes(genome)
                requests.append([n, event['first_proposal'], passed])
                if passed:
                    returned = event
                    break
    else:
        for checkpoint in CHECKPOINTS:
            src.advance_to(checkpoint)
            snap = src.snapshot(event_cursor=cursor)
            n, cursor = snap['proposal'], snap['event_cursor']
            bank.extend(snap['new_perfect_events'])
            eligible = (e for e in bank if e['first_proposal'] not in attempted)
            offered = heapq.nsmallest(SUBMISSIONS, eligible, key=ranker.key)
            for e in offered:
                attempted.add(e['first_proposal'])
                passed = verifier.passes(tuple(e['genome']))
                requests.append([n, e['first_proposal'], passed])
                if passed:
                    returned = e
                    break
            if returned is not None:
                break
    elapsed = time.perf_counter() - started
    return {'returned': event_record(returned), 'correct_return': returned is not None,
            'cap_exhausted_without_return': returned is None, 'proposals': n,
            'unique_training_perfect_seen': cursor, 'requests': requests, 'wall_seconds': elapsed,
            'cost': account(snap['prefix_cost'], n, observations, ranker, cache, verifier)}


def setup(params):
    if params:
        raise ValueError('Frozen study accepts no parameter overrides')


def cases():
    for p in problems.panel():
        for seed in SEEDS:
            yield f"{p['id']}-{seed}", {'task': p['id'], 'seed': seed}


def run(case_id, payload):
    specs = problems.panel()
    task = payload['task']
    seed = payload['seed']
    position = next(i for i, p in enumerate(specs) if p['id'] == task)
    if seed not in SEEDS or case_id != f'{task}-{seed}':
        raise ValueError('undeclared experiment case')
    mask = specs[position]['mask']
    get_label = lambda cell: (mask >> problems.index(cell)) & 1
    observations = {p: get_label(p) for p in problems.TRAIN}
    index = position * len(SEEDS) + SEEDS.index(seed)
    order = ('raw','reuse') if index % 2 == 0 else ('reuse','raw')
    result = {'task': task, 'seed': seed, 'arms': {}}
    for condition in order:
        grammar, events, rankings, blind = bank_and_choices(seed, condition, observations)
        # The sealed choice and common bank enter the evaluator; the operational
        # deployments below start from scratch with no access to these outputs.
        assessed = assess_choices(mask, grammar, events, rankings, blind)
        start = (index + int(condition == 'reuse')) % len(DEPLOYMENTS)
        modes = DEPLOYMENTS[start:] + DEPLOYMENTS[:start]
        result['arms'][condition] = {'blind': blind, 'assessment': assessed, 'deployed': {
            mode: deploy(seed, condition, observations, mode, problems.HELD, get_label) for mode in modes}}
    return result


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('task')
    parser.add_argument('seed', type=int)
    args = parser.parse_args()
    print(json.dumps(run(f'{args.task}-{args.seed}', vars(args)), sort_keys=True))
