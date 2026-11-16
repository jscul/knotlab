"""Generate paid proofs for (x2=a and v=0) implies x0=0 on masks (1,6)."""
from pathlib import Path
import sys


PRIOR = 'FIVE-PRODUCT-TOTAL-WORK-20261115-001B'
FAMILY = Path(__file__).resolve().parents[2] / PRIOR / (PRIOR + '-P001_learned_affine_work')
sys.path.insert(0, str(FAMILY))
from solver import ALL, AXES, INF, Search, old
import verifier as original


GROUP_MENU = tuple(sorted(set(AXES) | {4, 10, 14, 256, 260, 266, 270}))


def training():
    return ['Q', 16, ['R', ['P']], ['R', ['P']]]


def program(a, main):
    return {'premise': [[4, a], [256, 0]], 'conclusion': [1, 0], 'body': training(), 'root': main}


class TwoPremises:
    """Price the number of live uses and which premises their common ancestor already entails."""

    def __init__(self, search, a):
        self.search = search
        self.a = a
        x = old.equation_points(4, a)
        v = old.equation_points(256, 0)
        literal = old.equation_points(1, 0)
        guard = x & v
        negative = guard & ~literal
        positive = guard & literal
        self.training_cost = search.states[search.build(negative)].cost
        self.scores, self.moves = [], []
        for state in search.states:
            raw, fixed = state.raw, state.fixed
            scores = [state.cost] + [INF]*5
            moves = [None]*6
            if fixed & positive and fixed & negative:
                if not (raw & ~guard):
                    after = search.ids[raw & literal]
                    if search.states[after].fixed:
                        scores[1], moves[1] = 1 + search.states[after].cost, ('L', after)
                for tag, child in state.checks:
                    for status in range(1, 6):
                        price = 1 + self.scores[child][status]
                        if price < scores[status]:
                            scores[status], moves[status] = price, (tag, child, status)
                known = int(not (raw & ~x)) + 2*int(not (raw & ~v))
                for q, low, high in state.branches:
                    for i, left in enumerate(self.scores[low]):
                        if left >= INF:
                            continue
                        for j, right in enumerate(self.scores[high]):
                            if right >= INF or not (i or j):
                                continue
                            status = 2+known if i and j else i+j
                            price = 1 + left + right
                            if price < scores[status]:
                                scores[status] = price
                                moves[status] = ('Q', search.menu[q], low, i, high, j)
            self.scores.append(scores)
            self.moves.append(moves)

    def prices(self):
        return [min(INF, main + (self.training_cost if index else 0))
                for index, main in enumerate(self.scores[self.search.root])]

    def proof(self, status):
        def extract(state_id, index):
            if index == 0:
                return self.search.ordinary(state_id)
            move = self.moves[state_id][index]
            if move[0] == 'L':
                return ['L', self.search.ordinary(move[1])]
            if move[0] == 'Q':
                return ['Q', move[1], extract(move[2],move[3]), extract(move[4],move[5])]
            return [move[0], extract(move[1],move[2])]
        return program(self.a, extract(self.search.root, status))


def explicit(search, a, mode):
    """Ask both displayed premises, or separately reach each of the maximal number of uses."""
    x = old.equation_points(4, a)
    v = old.equation_points(256, 0)
    literal = old.equation_points(1,0)

    def use_tree(raw, questions):
        if not questions:
            return ['L', search.ordinary_at(raw & literal)]
        q, *rest = questions
        positive = raw & old.equation_points(q,1)
        return ['Q',q,use_tree(raw ^ positive, rest),use_tree(positive, rest)]

    if mode in ('three', 'four'):
        assert a == 0
        active = old.hull(x & search.sides['left'])
        left = active & old.equation_points(2,0)
        right = active & ~left
        tails = ['Q',2,use_tree(left,[8]),use_tree(right,[8] if mode == 'four' else [])]
        inside_x = ['R',tails]
    else:
        inside_x = ['Q',256,use_tree(x & v,[2]),search.ordinary_at(x & ~v)]
    outside_x = search.ordinary_at(ALL ^ x)
    low, high = (inside_x, outside_x) if a == 0 else (outside_x, inside_x)
    return program(a, ['Q',4,low,high])
