"""Independently read live one-output-spent examples and the two remaining loose bits."""
from collections import Counter
from importlib.util import module_from_spec, spec_from_file_location
from itertools import combinations
from pathlib import Path
from tempfile import TemporaryDirectory
import json
import sys


PREVIOUS = Path(__file__).resolve().parents[2] / "VARIABLE-OUTPUT-READER-20261118-001N"
REFERENCE = PREVIOUS / "VARIABLE-OUTPUT-READER-20261118-001N-P001_fourth_at_the_parents"


def predecessor(name):
    spec = spec_from_file_location("spent_reference_" + name, REFERENCE / (name + ".py"))
    module = module_from_spec(spec)
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


physics = predecessor("table_tools")

BASE = ((0,1,2), (0,3,4,5), (1,6,7,8), (2,9,10,11), (3,6,12,13), (4,9,14,15),
        (12,14,16,17), (7,10,16,18,19,20))
SHRINK = BASE + ((5,8,21,22), (15,21,18,23,24))
DOUBLE_HIGH = ((0,1,2), (0,3,4,5), (1,6,7,8), (3,6,9,10), (4,7,11,12), (9,11,13,14),
               (5,13,15,16), (2,15,17,18), (8,17,19,20), (10,16,19,21,22,23),
               (14,21,24,25), (12,20,24,26,27,28), (18,22,29,30), (25,29,31,32),
               (23,26,33,34), (30,33,35,36))
CASES = {
    "first_live": BASE + ((13,18,21,22),),
    "fourth_holds_surviving_mark": BASE + ((5,8,21,22), (13,18,23,24)),
    "both_child_outputs_used": SHRINK + ((11,23,25,26), (17,24,27,28)),
    "two_six_place_sites_live": DOUBLE_HIGH
}


def at(matrix, a, b):
    return matrix[a][b]


def assess(rows, matrix, recheck_span):
    events = physics.replay(rows)
    high_births = [i for i,event in enumerate(events) if i and len(event["fresh"]) == 3]
    fourth = high_births[-1]
    assert len(high_births) == 4 and len(events[fourth]["parents"]) == 3
    holders, _ = physics.incidence(rows)
    outputs = set(events[fourth]["fresh"])
    both = sorted(b for b in outputs if len(holders[b]) == 1)
    spent, = outputs.difference(both)
    assert len(both) == 2
    child, = set(holders[spent]) - {fourth}
    shrinks = [i for i,event in enumerate(events) if len(event["parents"]) == 3 and len(event["fresh"]) == 2]
    before = physics.allowed(rows[:child])
    immediately = physics.allowed(rows[:child+1])
    menu = physics.allowed(rows)
    assert menu
    width = physics.width(rows)
    pairs = tuple(combinations(range(width), 2))
    raw = {pair: at(matrix,*pair) for pair in pairs}
    if recheck_span:
        assert physics.parity_minima(rows,(2,))[2] == raw
    stars = [set(row) for row in rows]
    witnesses = []
    for star in stars:
        size = len(star)
        def names_close(a):
            return {a} | {b for b in range(width) if b != a and at(matrix,a,b) <= size}

        fitting = [pair for pair in combinations(sorted(star),2)
                   if at(matrix,*pair) == size and names_close(pair[0]) & names_close(pair[1]) == star]
        witnesses.append(fitting[:1])
    assert at(matrix,*both) == 6
    assert all(at(matrix,both[0],j) == at(matrix,both[1],j) for j in range(width) if j not in both)
    assert sorted(i for i in range(width) if i == spent or at(matrix,spent,i) <= len(rows[child])) == sorted(rows[child])
    old_frontier = sorted(bit for bit in holders
                          if sum(bit in star for i,star in enumerate(stars) if i != fourth) == 1)
    old_holder = {b:next(i for i,star in enumerate(stars) if i != fourth and b in star) for b in old_frontier}
    through_six = {bit for bit in old_frontier if at(matrix,both[0],bit) == 6}
    high_sets = []
    for more in combinations(sorted(through_six), 4):
        if len({old_holder[b] for b in more}) < 4:
            continue
        group = tuple(sorted([*both,*more]))
        if all(at(matrix,*pair) <= 6 for pair in combinations(group,2)):
            high_sets.append(group)
    assert tuple(sorted(rows[fourth])) in high_sets
    # Switches that satisfy the pair tests can still fail bipartition, reachability or full remeasurement.
    neighborhood = sorted([both[0], *(x for x in range(width) if x != both[0] and at(matrix,both[0],x) <= 6)])
    return {"history":rows, "width":width, "fourth_site":fourth, "spending_site":child, "spent_bit":spent,
            "remaining_loose_pair":both, "child_support":sorted(rows[child]), "shrinking_sites":shrinks,
            "before_spend":sorted(before), "immediate_menu":sorted(immediately), "present_menu":sorted(menu),
            "fourth_named_roles":physics.roles(rows,fourth,menu).get(next(iter(sorted(menu)))),
            "child_named_roles":physics.roles(rows,child,menu).get(next(iter(sorted(menu)))),
            "D5_closed_row_of_loose_output":neighborhood, "one_forcing_pair_per_star_if_present":witnesses,
            "number_of_individually_forced_stars":sum(map(bool,witnesses)), "site_count":len(rows),
            "old_boundary_after_removing_fourth":old_frontier,
            "possible_fourth_stars_if_other_sites_known_necessary_pair_tests":high_sets,
            "exact_pair_count":len(raw), "exact_D_histogram":dict(sorted(Counter(k-1 for k in raw.values()).items())),
            "direct_parity_minima_checked":recheck_span}


def run():
    with TemporaryDirectory(prefix="one-spent-holders-") as scratch:
        binary = physics.compiler(Path(scratch) / "pair_bonds")
        matrices = physics.all_tables(binary,CASES.values())
    data={name:assess(rows,mat,True) for (name,rows),mat in zip(CASES.items(),matrices,strict=True)}
    assert data["first_live"]["present_menu"] == [(5,11,21),(5,11,22)]
    case=data["fourth_holds_surviving_mark"]
    assert (15,19,21) in set(case["before_spend"]) & set(case["present_menu"])
    case=data["both_child_outputs_used"]
    assert case["shrinking_sites"] == [case["spending_site"]] and case["immediate_menu"] == []
    assert case["present_menu"] == [(13,22,27),(13,22,28)]
    case=data["two_six_place_sites_live"]
    assert len(case["present_menu"]) == 8 and case["shrinking_sites"] == []
    return data


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
