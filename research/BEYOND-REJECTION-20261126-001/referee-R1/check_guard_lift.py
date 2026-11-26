"""Construct a local guarded representative of every allowed pair of terminal words."""
import argparse
import json
from functools import lru_cache
from itertools import product
from time import perf_counter

from check_construction import ARCHIVE, BITS, WORDS, allowed


@lru_cache(maxsize=None)
def fill_device(supports, terminals, word, law):
    assigned = dict(zip(terminals, word))
    loose = sorted(set().union(*supports) - assigned.keys())
    for values in product(BITS, repeat=len(loose)):
        assigned.update(zip(loose, values))
        if all(allowed(tuple(assigned[x] for x in s), law) for s in supports):
            return assigned
    raise ValueError("Unsupported terminal word")


def make_state(old, a, b, law):
    state = {}
    for s, word, cut in [("A", a, 0), ("B", b, 8)]:
        device = tuple(tuple(support) for k, support in old.items() if k.startswith(s + "."))
        terminals = tuple(f"terminal{cut}.{i}" for i in range(3))
        state.update(fill_device(device, terminals, word, law))
    for stage in range(8):
        for i in range(3):
            pair = f"column{stage}.{i}"
            left, first, second = old[pair + ".left"]
            right, *middle = old[pair + ".right"]
            assert middle == [first, second]
            if law == "parity":
                if right in state and state[right] != state[left]:
                    return None
                state[right] = state[left]
            elif stage == 6:  # The three outer guard values at B are chosen from B's word alone.
                state[right] = b[int(right.split(".")[-1])]
            elif right not in state:
                state[right] = state[left]
            state[first], state[second] = next(
                mid for mid in product(BITS, repeat=2)
                if all(allowed((state[t], *mid), law) for t in (left, right)))
    assert len(state) == 95 and all(allowed(tuple(state[x] for x in s), law) for s in old.values())
    return state


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--pilot", action="store_true", help="first preparation and law, all terminal pairs")
    pilot = parser.parse_args().pilot
    start = perf_counter()
    archive = json.loads(ARCHIVE.read_text())["modes"]["primary"]
    out = {}
    for law in (("parity",) if pilot else ("parity", "nae")):
        old_by_input, structure_by_input = {}, {}
        count = 0
        for uv in (["00"] if pilot else sorted(archive)):
            entry = archive[uv]
            u, v = map(int, uv)
            for a, b in product(WORDS, repeat=2):
                state = make_state(entry["old_supports"], a, b, law)
                if state is None:
                    continue
                count += 1
                for side, prep, word in [("A", u, a), ("B", v, b)]:
                    visible = entry["pre_accessible"][side]["owned_distinctions"]
                    key = side, prep, word
                    old_record = {name: (holders, state[name]) for name, holders in visible.items()}
                    assert old_by_input.setdefault(key, old_record) == old_record
            for xy, trial in entry["laws"][law]["trials"].items():
                funded = xy == uv
                for side, prep, own in [("A", u, xy[0]), ("B", v, xy[1])]:
                    key = side, prep, own, funded
                    post = trial["post_accessible"][side]
                    assert structure_by_input.setdefault(key, post) == post
        out[law] = {"old_states_constructed": count, "distinct_old_input_keys": len(old_by_input),
                    "distinct_post_structure_keys": len(structure_by_input)}
    out["elapsed_seconds"] = round(perf_counter() - start, 6)
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main()
