"""Task-local ranking. Task identity, certification answers and target definitions are unavailable."""
from collections import Counter
from itertools import permutations, product

POINTS = tuple(product(range(3), repeat=3))
PERMUTATIONS = tuple(permutations(range(3)))
MODES = ('shortest', 'fitted', 'always')


def transported_votes(mode, observations):
    """Fit a decision for each nonidentity permutation and form votes only outside training."""
    if mode not in MODES:
        raise ValueError(mode)
    costs = Counter()
    model = {'accepted': [], 'evidence': [], 'margins': {}}
    votes = Counter()
    if mode == 'shortest':
        return model, votes, costs
    for perm in PERMUTATIONS[1:]:
        moved = {p: tuple(perm[i] for i in p) for p in observations}
        # A 3-cycle can supply oriented pairs that are genuinely different. A
        # transposition can visit both ends of the same unordered pair.
        pairs = {tuple(sorted((p, q))) for p, q in moved.items() if q != p and q in observations}
        classes = set()
        mismatches = 0
        if mode == 'fitted':
            for p, q in pairs:
                left, right = observations[p], observations[q]
                classes.update((left, right))
                mismatches += left != right
                costs['fit_label_reads'] += 2
                costs['fit_comparisons'] += 1
            model['evidence'].append([list(perm), len(pairs), len(classes), mismatches])
            if len(pairs) < 2 or len(classes) != 2 or mismatches:
                continue
        model['accepted'].append(list(perm))
        for source, dest in moved.items():
            if dest not in observations:
                votes[dest] += 2 * observations[source] - 1
                costs['fit_label_reads'] += 1
                costs['vote_additions'] += 1
    votes = {cell: votes[cell] for cell in sorted(votes) if votes[cell]}
    model['margins'] = {''.join(map(str, p)): w for p, w in votes.items()}
    return model, votes, costs


class Predictions:
    """A fresh per-deployment cache of computed *predictions*. No true labels enter it."""
    def __init__(self, grammar):
        self.grammar = grammar
        self.values = {}
        self.inputs = {}
        self.cost = Counter()

    def predict(self, genome, cells, stage):
        if not cells:
            return ()
        known = self.values.setdefault(genome, {})
        missing = tuple(p for p in cells if p not in known)
        if missing:
            if missing not in self.inputs:
                self.inputs[missing] = tuple(sum(((p[j] >> b) & 1) << lane
                                                 for lane, p in enumerate(missing))
                                             for j in range(3) for b in (1, 0))
            program = self.grammar.expand(genome)
            counts = self.grammar.counts(program)
            mask = (1 << len(missing)) - 1
            out = self.grammar.execute_packed(program, self.inputs[missing], mask)
            predicted = mask ^ (out[4] | out[5])
            for lane, point in enumerate(missing):
                known[point] = (predicted >> lane) & 1
            self.cost[stage + '_input_executions'] += len(missing)
            self.cost[stage + '_program_gates'] += len(missing) * sum(counts[1:])
            self.cost[stage + '_readout_gates'] += 2 * len(missing)
            self.cost[stage + '_packed_program_plus_readout'] += sum(counts[1:]) + 2
        self.cost[stage + '_cached_predictions'] += len(cells) - len(missing)
        return tuple(known[p] for p in cells)


class Ranker:
    def __init__(self, mode, observations, predictions):
        self.mode = mode
        self.model, self.votes, self.cost = transported_votes(mode, observations)
        self.cells = tuple(self.votes)
        self.predictions = predictions
        self.penalties = {}

    def key(self, event):
        genome = tuple(event['genome'])
        if genome not in self.penalties:
            bits = self.predictions.predict(genome, self.cells, 'ranking')
            self.penalties[genome] = sum(abs(self.votes[p]) for p, bit in zip(self.cells, bits)
                                         if bit != (self.votes[p] > 0))
            self.cost['candidate_vote_comparisons'] += len(self.cells)
        self.cost['rank_key_requests'] += 1
        return self.penalties[genome], event['expanded_length'], event['first_proposal']


def first_key(event):
    return event['first_proposal']
