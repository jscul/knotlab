"""Independently enumerate the middle passages and count the receiver's turns.

The receiver's intake starts with Rb1, Rt, Rb2, a. After a it cannot reenter R.
The only access to S from the middle goes through b, then Sb2. We exhaust the
simple passages between those portals and both orientations of the sent word.
Removing a loop only shortens such a passage. On the S side we retain the
nonretracing condition at the first letter of the sent word. The full parent
and launch-separation checks are in the study's separate scientific replay.
"""
import gzip
import json
from pathlib import Path
import sys
from collections import defaultdict
from itertools import pairwise


def meet(holdings, first, second):
    holdings[first].add(second)
    holdings[second].add(first)


def add_path(holdings, names):
    for first, second in pairwise(names):
        meet(holdings, first, second)


def middle(arm, arc_length):
    holdings = defaultdict(set)
    add_path(holdings, ["a", *(f"u{i}" for i in range(1, 46)), "b"])
    if arm == "absent":
        return holdings
    last = arc_length if arm == "finite" else 2*arc_length
    names = [f"c{i}" for i in range(last+1)]
    add_path(holdings, names)
    if arm != "finite":
        meet(holdings, names[0], names[-1])
    meet(holdings, "a", names[0])
    if arm != "one-port":
        meet(holdings, "b", names[arc_length])
    if arm == "matched":
        for first, second in [("c48", "c49"), ("u23", "u24")]:
            holdings[first].remove(second)
            holdings[second].remove(first)
        meet(holdings, "c48", "u24")
        meet(holdings, "u23", "c49")
    return holdings


def simple_paths(holdings, start, end):
    pending = [(start,)]
    while pending:
        path = pending.pop()
        if path[-1] == end:
            yield path
        else:
            pending.extend(path+(name,) for name in holdings[path[-1]] if name not in path)


def sent_word(size):
    neutral = ["v", "r1", "r2", "r3"]
    ordinary = neutral+["v", "s", "b0", "t"]
    marked = neutral+["v", "s", "b1", "t"]
    period = ordinary*(size//16-1) + marked
    start = period.index("b1")-1
    phase = (period+period)[start:start+len(period)]
    return tuple(phase*2)


def sender_endings(word):
    holdings = defaultdict(set)
    add_path(holdings, ("v", "r1", "r2", "r3", "v"))
    for mark in ("b0", "b1", "b2"):
        add_path(holdings, ("v", "s", mark, "t", "v"))
    for orientation in (word, word[::-1]):
        for approach in simple_paths(holdings, "b2", orientation[0]):
            if len(approach)>1 and approach[-2] == orientation[1]:
                continue
            yield approach + orientation[1:]


def receiver_ticks(size):
    # The exceptional b1 stands at the central occurrence. All other copies on
    # the return side have the ordinary b0 at the corresponding position.
    calendar = ("b0", "t", "v", "r1", "r2", "r3", "v", "r1", "r2", "r3", "v", "s")
    return [2*length for length in range(1, size//2+1) if calendar[-length % len(calendar)] == "b0"]


def longest_marked_run(passage):
    current = longest = 0
    for name in passage:
        current = current+1 if name.startswith("c") else 0
        longest = max(current, longest)
    return longest


def check_arm(arm, arc_length, launch_size):
    passages = list(simple_paths(middle(arm, arc_length), "a", "b"))
    endings = list(sender_endings(sent_word(launch_size)))
    # Three steps from the center to a, the passage to b, then its S ending.
    # The first occurrence of that ending is one step from b.
    choices = [(3 + len(passage)-1 + len(ending), passage)
               for passage in passages for ending in endings]
    fewest = min(length for length, passage in choices)
    earliest = sorted({passage for length, passage in choices if length == fewest})
    size = 2*fewest+1  # only an intake-side addition can give first receipt
    ticks = receiver_ticks(size)
    return {
        "port_lengths": sorted({len(passage)-1 for passage in passages}),
        "first_size": size,
        "past_origin": len(ticks),
        "past_send": sum(tick>launch_size for tick in ticks),
        "tied_middle_paths": len(earliest),
        "consecutive_c_on_minima": sorted(longest_marked_run(passage) for passage in earliest),
    }


def calculate():
    results = {}
    for arc_length in (8, 20, 32, 44):
        arms = ("active", "finite")
        sizes = (32, 48, 64)
        if arc_length == 32:
            arms = ("absent", "active", "finite", "one-port", "matched")
            sizes += (80,)
        for arm in arms:
            results[f"{arm}/{arc_length}"] = {str(m): check_arm(arm, arc_length, m) for m in sizes}
    active = middle("active", 32)
    matched = middle("matched", 32)
    assert {x: len(y) for x, y in active.items()} == {x: len(y) for x, y in matched.items()}
    return results



def check_deletions(intervals):
    for (start, end), (next_start, next_end) in pairwise(intervals):
        assert (next_start-start, end-next_end) in ((1, 0), (0, 1))
    return len(intervals)-1


def check_certificates(independent):
    """Compare the independent counts with every minimal registered word and its two parents."""
    study = Path(__file__).resolve().parent
    evidence = study.parents[1]/"artifacts"/(study.name+"B")
    receipt, = evidence.glob("*/registered.json.gz")
    preparations = json.loads(gzip.decompress(receipt.read_bytes()))["preparations"]
    arm_names = {"short": "finite", "one_port": "one-port", "rewired": "matched"}
    cases = certificates = deletions = 0
    for preparation in preparations:
        variant = preparation["variant"]
        label = arm_names.get(variant, variant)
        for send in preparation["sends"]:
            cases += 1
            launch = send["send_size"]
            ours = independent[f"{label}/{preparation['d']}"][str(launch)]
            assert ours["first_size"] == send["strict_registration_size"]
            assert ours["tied_middle_paths"] == len(send["all_minimizing_port_routes"])
            phase = send["true_phase"]["originals"]
            assert len(phase) == launch
            for certificate in send["certificates"]:
                certificates += 1
                assert ours["past_origin"] == certificate["ticks_since_origin"]
                assert ours["past_send"] == certificate["ticks_since_receiver_launch_anchor"]
                member = certificate["member"]["originals"]
                outside = certificate["incoming_input"]["originals"]
                assert member[1:] == outside
                assert member[:-1] == certificate["continuing_input"]["originals"]
                assert certificate["member"]["actual_parent_windows"] == [[0, len(member)-1], [1, len(member)]]
                intervals = certificate["incoming_to_send"]
                deletions += check_deletions(intervals)
                start, end = intervals[-1]
                assert outside[start:end] in (phase, phase[::-1])
                history = certificate["actual_receiver_chain_intervals_and_ticks"]
                deletions += check_deletions([row[:2] for row in history])
                assert sorted(b-a for a,b,tick in history if tick) == certificate["tick_sizes"]
                start, end = next((a,b) for a,b,tick in history if b-a == launch)
                assert member[start:end] == certificate["launch_anchor"]
                assert certificate["intrinsic_decoded_emissions"]
                neutral = certificate["physical_sham"]
                assert neutral["decoded"] == [] and neutral["member"]["fresh"] == certificate["member"]["fresh"]
    print(f"{cases} arm/send pairs, {certificates} registering members and matched neutral controls, {deletions} endpoint deletions verified.")


if __name__ == "__main__":
    results = calculate()
    if sys.argv[1:] == ["--verify-certificates"]:
        check_certificates(results)
    elif not sys.argv[1:]:
        print(json.dumps(results, sort_keys=True, indent=2))
    else:
        raise SystemExit("Usage: check_receiver_turns.py [--verify-certificates]")
