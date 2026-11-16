"""Single learned affine implication, with explicit costs for each search operation."""
from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


PROOFS = Path(__file__).resolve().parents[2]
PREDECESSOR = 'FIVE-PRODUCT-GUARDED-REUSE-20261115-001B'
old_path = PROOFS / PREDECESSOR / (PREDECESSOR + '-P001_guarded_deductions') / 'solver.py'
spec = spec_from_file_location('previous_five_product_evaluators', old_path)
old = module_from_spec(spec)
spec.loader.exec_module(old)
ALL = old.ALL
AXES = tuple(1 << i for i in range(9))
INF = 100_000


@dataclass(slots=True)
class State:
    raw: int
    fixed: int
    checks: tuple
    branches: tuple
    cost: int
    choice: tuple


class Search:
    """Geometry is indexed in increasing dependency order; a query has two proper children."""

    def __init__(self, menu=AXES, sides=None):
        self.menu = tuple(menu)
        self.ones = [old.equation_points(mask, 1) for mask in self.menu]
        self.sides = old.evaluator_sets((1, 6), 1) if sides is None else sides
        self.states = []
        self.ids = {}
        self.root = self.build(ALL)

    def fixed(self, raw):
        while raw:
            after = old.hull(raw & self.sides['left']) & old.hull(raw & self.sides['right'])
            if after == raw:
                return raw
            raw = after
        return 0

    def build(self, raw):
        if raw in self.ids:
            return self.ids[raw]
        checks = []
        branches = []
        cost = INF
        choice = None
        sides = (('R', self.sides['left']), ('P', self.sides['right']))
        empty = next((side for side, rows in sides if not (raw & rows)), None)
        if empty:
            cost, choice = 1, (empty,)
        else:
            for side, rows in sides:
                after = old.hull(raw & rows)
                if after != raw:
                    child = self.build(after)
                    checks.append((side, child))
                    trial = 1 + self.states[child].cost
                    if trial < cost:
                        cost, choice = trial, (side, child)
            for query_index, ones in enumerate(self.ones):
                pos = raw & ones
                neg = raw ^ pos
                if not (pos and neg):
                    continue
                left, right = self.build(neg), self.build(pos)
                branches.append((query_index, left, right))
                trial = 1 + self.states[left].cost + self.states[right].cost
                if trial < cost:
                    cost, choice = trial, ('Q', self.menu[query_index], left, right)
        assert choice is not None
        state = State(raw, self.fixed(raw), tuple(checks), tuple(branches), cost, choice)
        number = len(self.states)
        self.ids[raw] = number
        self.states.append(state)
        return number

    def ordinary(self, state_id):
        choice = self.states[state_id].choice
        if choice[0] == 'Q':
            _, mask, left, right = choice
            return ['Q', mask, self.ordinary(left), self.ordinary(right)]
        if len(choice) == 1:
            return list(choice)
        return [choice[0], self.ordinary(choice[1])]

    def ordinary_at(self, raw):
        return self.ordinary(self.build(raw))

    def single(self, premise, conclusion):
        """Minimum with zero uses, one use, or repeated uses with a common or outside guard."""
        guard = old.equation_points(*premise)
        literal = old.equation_points(*conclusion)
        positive, negative = guard & literal, guard & ~literal
        body = self.build(negative)
        scores = []
        choices = []
        for state in self.states:
            raw, fixed = state.raw, state.fixed
            row = [state.cost, INF, INF, INF]
            moves = [None] * 4
            if fixed & positive and fixed & negative:
                if not (raw & ~guard):
                    after = self.ids[raw & literal]
                    if self.states[after].fixed:
                        row[1], moves[1] = 1 + self.states[after].cost, ('L', after)
                for side, child in state.checks:
                    for index in (1, 2, 3):
                        trial = 1 + scores[child][index]
                        if trial < row[index]:
                            row[index], moves[index] = trial, (side, child, index)
                outside = bool(raw & ~guard)
                for q, left, right in state.branches:
                    for i, a in enumerate(scores[left]):
                        if a >= INF:
                            continue
                        for j, b in enumerate(scores[right]):
                            if not (i or j) or b >= INF:
                                continue
                            if i == 3 or j == 3 or (i and j and outside):
                                index = 3
                            else:
                                index = min(2, i + j)
                            trial = 1 + a + b
                            if trial < row[index]:
                                row[index] = trial
                                moves[index] = ('Q', self.menu[q], left, i, right, j)
            scores.append(row)
            choices.append(moves)

        def extract(state_id, category):
            if category == 0:
                return self.ordinary(state_id)
            move = choices[state_id][category]
            if move[0] == 'Q':
                _, query, left, i, right, j = move
                return ['Q', query, extract(left, i), extract(right, j)]
            if move[0] == 'L':
                return ['L', self.ordinary(move[1])]
            return [move[0], extract(move[1], move[2])]

        best = [min(INF, score + (self.states[body].cost if i else 0))
                for i, score in enumerate(scores[self.root])]
        certs = {i: {'premise': list(premise), 'conclusion': list(conclusion),
                     'body': self.ordinary(body), 'root': extract(self.root, i)}
                 for i in (1, 2, 3) if best[i] < INF}
        return best, certs

    def census_input(self):
        """Plain integer interchange for the separate array-based dynamic program."""
        assert self.menu == AXES
        lines = [str(len(self.states))]
        for state in self.states:
            whole = 0
            for q, ones in enumerate(self.ones):
                if not (state.raw & ones):
                    whole |= 1 << (2*q)
                elif not (state.raw & ~ones):
                    whole |= 1 << (2*q+1)
            words = [(state.fixed >> (64*w)) & ((1 << 64)-1) for w in range(8)]
            shrinks = [child for _, child in state.checks]
            shrink_columns = shrinks + [-1] * (2-len(shrinks))
            branches = [-1] * 18
            for q, no, yes in state.branches:
                branches[2*q:2*q+2] = (no, yes)
            fields = [state.cost, whole, *words, *shrink_columns, *branches]
            lines.append(' '.join(map(str, fields)))
        return '\n'.join(lines) + '\n'


def chosen_proofs(search):
    old_guard = ((256, 0), (1, 0))
    same_guard = ((1, 0), (4, 0))
    cross_guard = ((2, 0), (4, 0))
    best, fixed = search.single(*old_guard)
    same, same_proofs = search.single(*same_guard)
    cross, cross_proofs = search.single(*cross_guard)
    assert best == [23, 26, 32, 33] and same[1:3] == [23, 30] and cross[3] == 30
    proofs = {'ordinary': {'root': search.ordinary(search.root)},
              'old_single': fixed[1], 'old_repeated': fixed[2], 'old_crossing': fixed[3],
              'single_at_tree_optimum': same_proofs[1], 'best_repeated': same_proofs[2],
              'best_crossing': cross_proofs[3]}
    guard = old.equation_points(256, 0)
    literal = old.equation_points(1, 0)
    first = old.equation_points(4, 0)
    ordinary = search.ordinary_at
    tail = lambda g: ['L', ordinary(g & literal)]
    pair = ['Q', 4, tail(guard & first), tail(guard & ~first)]
    definition = {'premise': [256, 0], 'conclusion': [1, 0], 'body': ordinary(guard & ~literal)}
    proofs['old_delay_x2'] = dict(definition, root=['Q', 256, pair, ordinary(ALL ^ guard)])
    proofs['old_hoisted'] = dict(definition, root=['Q', 256, ['L', ordinary(guard & literal)], ordinary(ALL ^ guard)])
    proofs['old_split_once'] = {'root': ['Q', 256, ['Q', 1, ordinary(guard & literal),
                                                    ordinary(guard & ~literal)], ordinary(ALL ^ guard)]}
    crossed_guard, crossed_literal = old.equation_points(2, 0), old.equation_points(4, 0)
    proofs['crossed_reordered'] = {'root': ['Q', 2, ['Q', 4, ordinary(crossed_guard & crossed_literal),
                                                     ordinary(crossed_guard & ~crossed_literal)],
                                           ordinary(ALL ^ crossed_guard)]}
    return proofs
