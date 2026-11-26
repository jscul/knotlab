"""Check the one-meeting ordinary-count hearing directly in the recorded engine."""
from itertools import product
from collections import deque
from pathlib import Path
import json
import resource
import sys
from time import perf_counter

from pysat.solvers import Solver

resource.setrlimit(resource.RLIMIT_AS, (512 * 1024**2,) * 2)
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(next((ROOT / "experiments/WHAT-A-BIRTH-CARRIES-20261125-001B").glob("*/eng.py")).parent))
import eng

START = [[0, 3, 4, 7], [1, 2, 5, 6, 8], [0, 1, 2]]


def clauses(state):
    for row in state.places:
        yield [d+1 for d in row]
        yield [-d-1 for d in row]


def complete_projection(solver, ds, test_own):
    for bits in product((0, 1), repeat=len(ds)):
        signs = [d+1 if bit else -d-1 for d, bit in zip(ds, bits)]
        should_extend = not test_own or len(set(bits)) > 1
        if solver.solve(assumptions=signs) != should_extend:
            return False
    return True


def sharing_steps(state, knot, targets):
    todo = deque([(knot, 0)])
    seen = {knot}
    while todo:
        u, steps = todo.popleft()
        if u in targets:
            return steps
        for v in state.meets(u) - seen:
            seen.add(v)
            todo.append((v, steps+1))


def grow(add, stars, roles, choice, target=None):
    state = eng.from_stars(stars)
    law = eng.Law("ORD", "CANCEL-WAIT", "MET", "nae", choice)
    origins = list(roles)
    with Solver(bootstrap_with=list(clauses(state))) as solver:
        assert all(complete_projection(solver, ds, True) for ds in state.places)
    rounds = []
    for rnd in (1, 2):
        if rnd == 2 and add:
            if target is None:
                target = next(u for u, role in enumerate(origins) if role == 2 and state.made[u] == 1)
            assert origins[target] == 2 and state.usable(target)
            near = {u for u, role in enumerate(origins) if role == 1}
            measured = sharing_steps(state, target, near)
            d = state.n_distinctions
            state.places[target].append(d)
            state.holders.append([target])
            state.maker.append(target)
            state.barred.append(False)
        prior = list(clauses(state))
        rec = eng.play_round(state, law, eng.Guard(4))
        assert not rec["short"]
        own = []
        with Solver(bootstrap_with=prior) as solver:
            for birth in rec["births"]:
                u = birth["id"]
                role = 0
                for parent in birth["parents"]:
                    role |= origins[parent]
                origins.append(role)
                assert birth["f"] > 0
                assert complete_projection(solver, birth["inputs"], False)
                if role == 1:
                    own.append({"parents":birth["parents"],"fresh":birth["f"],
                                "places":len(state.places[u]),"demand":birth["D"]})
        rows = {"births":len(rec["births"]), "short":len(rec["short"]), "receiver":own}
        if rnd == 2 and add:
            rows.update(target=target, sharings_to_any_receiver_owned=measured)
        rounds.append(rows)
    return rounds


if __name__ == "__main__":
    start = perf_counter()
    larger = "--three-meetings" in sys.argv
    if larger:
        fixture = json.loads(Path(__file__).with_name("inference_longer.json").read_text())["witness"][0]
        case = (fixture["places"], [1 << r for r in fixture["owners"]], "NEWEST", fixture["reading"]["marked"])
    else:
        case = (START, [1, 2, 4], "OLDEST", None)
    runs = {str(add):grow(add, *case) for add in ([False] if "--pilot" in sys.argv else [False, True])}
    print(json.dumps({"runs":runs,"seconds":round(perf_counter()-start,6)}, indent=2))
