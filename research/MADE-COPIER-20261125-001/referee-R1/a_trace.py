"""Look for a changed full part hidden by the first-pattern trace."""

import argparse
from itertools import product
import json

from a_replay import DESIGNS, Guard, Law, finish, grow, holders, mask_for, prepare, roster, stated_choice


def first_pattern_trace(previous, current, origin):
    holding = holders(previous.knots)
    _, loose, met, _ = roster(current)
    from_x = {u for u, flag in enumerate(current.descent) if flag & 1}
    first_knot = len(origin.knots)
    first_place = origin.distinctions
    x_new_knots = sorted(u for u in from_x if u >= first_knot)
    all_new_places = set().union(*(current.knots[u] for u in x_new_knots))
    x_new_places = sorted(v for v in all_new_places if v >= first_place and min(
        u for u, knots in enumerate(current.knots) if v in knots
    ) in from_x)
    knot_names = {u: u for u in range(first_knot)}
    knot_names.update({u: first_knot + i for i, u in enumerate(x_new_knots)})
    place_names = {v: v for v in range(first_place)}
    place_names.update({v: first_place + i for i, v in enumerate(x_new_places)})
    births = []
    for birth in current.births:
        if any(parent not in from_x for parent in birth.parents):
            continue
        takes = birth.regular + (() if birth.extra is None else (birth.extra,))
        births.append((tuple(knot_names[u] for u in birth.parents),
                       tuple(place_names.get(v, -1) for v in takes),
                       tuple(len(holding[v]) > 1 for v in takes), len(birth.fresh)))
    members = {u for u in loose if u in from_x}
    counts = tuple(sorted((knot_names[u], len(loose[u]), len(current.knots[u] & current.barred)) for u in members))
    restricted = {q & members for q in met if len(q & members) >= 2}
    met_sets = sorted(tuple(sorted(knot_names[u] for u in q)) for q in restricted
                      if not any(q < p for p in restricted))
    return births, counts, met_sets


def parts_with_x(state):
    _, _, _, parts = roster(state)
    return sorted((tuple(sorted(u for u in part if state.descent[u] & 1)), mask_for(state, part) == 3)
                  for part in parts if any(state.descent[u] & 1 for u in part))


def common_knots_holding(current, distinction, present_before):
    holding, loose, _, _ = roster(current)
    all_x_members = {u for u in loose if current.descent[u] == 1}
    return sorted(w for w in holding[distinction]
                  if w < present_before and len(
                      (set().union(*(holding[v] for v in current.knots[w])) - {w}) & all_x_members) >= 2)


def nae_failures(state):
    from pysat.solvers import Solver

    knots = [tuple(sorted(u + 1 for u in knot)) for knot in state.knots]
    clauses = [[sign * u for u in knot] for knot in knots for sign in (-1, 1)]
    with Solver(bootstrap_with=clauses) as solver:
        assert solver.solve()
        return [i for i, knot in enumerate(knots) if len(knot) < 2 or any(
            not solver.solve(assumptions=[-knot[0], *(sign * u for sign, u in zip(signs, knot[1:]))])
            for signs in product((-1, 1), repeat=len(knot) - 1) if 1 in signs
        )]


def probe(limit):
    laws = (Law("FLOOR1", treatment, "MET", choice, knot_law)
            for knot_law, treatment, choice in product(("nae", "parity"), ("OFFSHOOT", "WAIT", "RETIRE"),
                                                       ("OLDEST", "NEWEST", "IN-TURN", "BY-COUNT")))
    tested = 0
    for law, (name, design) in product(laws, DESIGNS.items()):
        if limit is not None and tested >= limit:
            break
        tested += 1
        origin_index = design["s"]
        states, _ = grow(design, law, rounds=5)
        origin = states[origin_index]
        for prior, recorded, following in zip(states[origin_index:], states[origin_index + 1:], states[origin_index + 2:]):
            prepared = prepare(prior, law)
            taking = [birth for birth in prepared[0] if birth.candidates]
            chosen = [stated_choice(birth, prior, law.choice) for birth in taking]
            try:
                observed_part = parts_with_x(recorded)
                observed_trace = first_pattern_trace(prior, recorded, origin)
                following_trace = first_pattern_trace(recorded, following, origin)
            except Guard:
                continue
            for i, birth in enumerate(taking):
                if mask_for(prior, birth.parents) != 2:
                    continue
                for other in set(birth.candidates) - {chosen[i]}:
                    changed = chosen[:]
                    changed[i] = other
                    try:
                        alternate = finish(prior, law, prepared, changed)
                        actual_part = parts_with_x(alternate)
                        if actual_part == observed_part:
                            continue
                        before_common = common_knots_holding(recorded, chosen[i], len(prior.knots))
                        after_common = common_knots_holding(alternate, other, len(prior.knots))
                        if not (before_common or after_common):
                            continue
                        if observed_trace != first_pattern_trace(prior, alternate, origin):
                            continue
                        next_round = prepare(alternate, law)
                        next_choices = [stated_choice(b, alternate, law.choice) for b in next_round[0] if b.candidates]
                        next_state = finish(alternate, law, next_round, next_choices)
                        if following_trace == first_pattern_trace(alternate, next_state, origin):
                            return {
                                "completed configurations": tested, "design": name, "law": law.__dict__,
                                "changed at round": recorded.t, "next round": following.t,
                                "parents that take": birth.parents, "original take": chosen[i], "changed take": other,
                                "original common knots holding the take": before_common,
                                "changed common knots holding the take": after_common,
                                "original X parts": observed_part, "changed X parts": actual_part,
                                "same X traces at both rounds": [observed_trace, following_trace],
                                "not-all-equal failing knots, original": [nae_failures(recorded), nae_failures(following)],
                                "not-all-equal failing knots, one altered take": [nae_failures(alternate), nae_failures(next_state)],
                            }
                    except Guard:
                        continue
    return {"completed configurations": tested, "witness found": False}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int)
    print(json.dumps(probe(parser.parse_args().limit), indent=2, sort_keys=True))
