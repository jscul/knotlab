"""Fresh finite-state proof of the two state families and exact bad inputs.

No imports from the scientific producer or earlier referee implementations.
"""
from collections import deque
from hashlib import sha256
from pathlib import Path
import json
import resource
import time

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "research/ADDR-KNOTS-20261113-001/referee-R1/codex/returns"
KEYS = {
    "two": "91c75673c09d90467aefb05915109cabd5a02fc0103944cb525be8f56ca212c2",
    "three": "f4fd01e9afa5631440f1607276c889547b4767423ee44873e86cf9c85b7d2c4d",
}


def load(name):
    path = SOURCE / (KEYS[name] + ".json")
    raw = path.read_bytes()
    key = json.loads(raw)["key"]
    return key, {"path": str(path.relative_to(ROOT)), "sha256": sha256(raw).hexdigest()}


def roster(s):
    return [()] + [(q,) for q in range(s)] + [
        (q, r) for q in range(s) for r in range(s)
    ]


def emit(key, residual, letter):
    """Composition acts right to left; sections use each item's INPUT."""
    _, sw, d0, d1, _ = key
    next_residual = [None] * len(residual)
    for j in range(len(residual) - 1, -1, -1):
        q = residual[j]
        old = letter
        letter ^= sw[q]
        next_residual[j] = (d1 if old else d0)[q]
    return tuple(next_residual), letter


def color_start(kind):
    return 0 if kind in ("parity", "constant") else (-1, -1)


def color_step(kind, state, letter):
    if kind == "parity":
        return state ^ letter
    if kind == "constant":
        return 0
    first, _ = state
    return (letter if first == -1 else first, letter)


def color_value(kind, state):
    if kind in ("parity", "constant"):
        return state
    first, last = state
    return 0 if first == -1 else first ^ last


PAIRS = ((0, 1), (0, 2), (1, 2))


def initial(words, kind):
    return (tuple(words), tuple(color_start(kind) for _ in range(3)), 0, 0, 0)


def advance(key, config, letter, kind, minimum):
    residuals, memories, differences, parity, length = config
    steps = [emit(key, r, letter) for r in residuals]
    outputs = [v for _, v in steps]
    for bit, (i, j) in enumerate(PAIRS):
        if outputs[i] != outputs[j]:
            differences |= 1 << bit
    return (
        tuple(r for r, _ in steps),
        tuple(color_step(kind, m, b) for m, b in zip(memories, outputs)),
        differences,
        parity ^ 1,
        min(minimum, length + 1),
    )


def bad(config, kind, minimum, parity, exclude_equal=True):
    _, memories, differences, length_parity, length = config
    c = [color_value(kind, m) for m in memories]
    return (length == minimum and length_parity == parity
            and (differences == 7 or not exclude_equal)
            and c[0] == c[1] == c[2])


def build(key, placement, kind, minimum, parity, exclude_equal=True,
          replace_identity=False):
    words = roster(key[0])
    starts = [words[i] for i in placement]
    if replace_identity:
        starts = [(0,) if not w else w for w in starts]
    start = initial(starts, kind)
    states, indices, transitions, inputs = [start], {start: 0}, [], [""]
    for config in states:
        row = []
        for letter in (0, 1):
            nxt = advance(key, config, letter, kind, minimum)
            if nxt not in indices:
                indices[nxt] = len(states)
                states.append(nxt)
                inputs.append(inputs[indices[config]] + str(letter))
            row.append(indices[nxt])
        transitions.append(row)
    accepts = [bad(c, kind, minimum, parity, exclude_equal) for c in states]
    witnesses = [inputs[i] for i, a in enumerate(accepts) if a]
    return {"placement": placement, "state_kind": kind, "minimum": minimum,
            "length_parity": parity, "exclude_equal": exclude_equal,
            "replace_identity": replace_identity, "states": states,
            "transitions": transitions, "accepting": accepts,
            "shortest_bad_input": min(witnesses, key=lambda s: (len(s), s))
            if witnesses else None}


def expected_step(state, letter):
    # 0: no zeros; 1: one zero; 2: positive even >=2 zeros;
    # 3: odd >=3 zeros; 4: those zeros followed by 1;
    # 5: accepting, one further arbitrary letter; 6: permanently dead.
    return ((1, 6), (2, 6), (3, 4), (2, 6), (5, 5), (6, 6), (6, 6))[state][letter]


def compare_language(automaton, want_special):
    queue = [(0, 0)]
    seen = {(0, 0): ""}
    mismatches = []
    for product_state in queue:
        i, e = product_state
        expected = e == 5 if want_special else False
        if automaton["accepting"][i] != expected:
            mismatches.append(seen[product_state])
        for b in (0, 1):
            nxt = (automaton["transitions"][i][b], expected_step(e, b))
            if nxt not in seen:
                seen[nxt] = seen[product_state] + str(b)
                queue.append(nxt)
    return {"target": "(00)+1(0|1)" if want_special else "empty language",
            "reachable_comparison_states": len(queue),
            "symmetric_difference_accepting_states": len(mismatches),
            "shortest_mismatch": min(mismatches, key=lambda x: (len(x), x))
            if mismatches else None,
            "comparison_states": [[i, e] for i, e in queue]}


def summary(a):
    return {k: v for k, v in a.items() if k not in ("states", "transitions", "accepting")} | {
        "reachable_states": len(a["states"]),
        "accepting_states": sum(a["accepting"]),
    }


def main():
    t0 = time.monotonic()
    families = {}
    full = {}
    sources = {}
    for name, kind, minimum, parity in (("two", "parity", 3, 1),
                                         ("three", "first_last", 2, 0)):
        key, sources[name] = load(name)
        checks = [build(key, p, kind, minimum, parity) for p in key[4]]
        assert all(not any(a["accepting"]) for a in checks)
        families[name] = {"key": key, "all_level_claim": True,
                          "placements": [summary(a) for a in checks]}
        full[name + "_positive"] = checks
    key, _ = load("two")
    exact = [build(key, p, "parity", 4, 0) for p in key[4]]
    comparisons = []
    for a in exact:
        comparison = compare_language(a, a["placement"] == [0, 8, 10])
        assert comparison["symmetric_difference_accepting_states"] == 0
        comparisons.append({"automaton": summary(a), "comparison": comparison})
    full["two_even_exact"] = exact
    controls = []
    for name, kind, minimum, parity, flags, description in (
        ("two", "parity", 4, 0, {}, "wrong length parity for #2"),
        ("three", "first_last", 3, 1, {}, "wrong length parity for #3"),
        ("two", "first_last", 3, 1, {}, "wrong state for #2"),
        ("three", "parity", 2, 0, {}, "wrong state for #3"),
        ("two", "parity", 3, 1, {"exclude_equal": False}, "equal images not excluded"),
        ("two", "parity", 3, 1, {"replace_identity": True}, "identity replaced by map 0"),
    ):
        key, _ = load(name)
        checks = [build(key, p, kind, minimum, parity, **flags) for p in key[4]]
        witnesses = [a for a in checks if a["shortest_bad_input"] is not None]
        assert witnesses, description
        first = min(witnesses, key=lambda a: (len(a["shortest_bad_input"]), a["shortest_bad_input"]))
        controls.append({"description": description, "rejected": True,
                         "witness": summary(first)})
    identity = {"word_index": 0, "word": [], "letter_steps": []}
    for name in KEYS:
        key, _ = load(name)
        for b in (0, 1):
            residual, output = emit(key, (), b)
            assert residual == () and output == b
            identity["letter_steps"].append({"key": name, "input": b,
                                             "output": output, "residual": residual})
    result = {"status": "passed", "sources": sources, "families": families,
              "two_even_exact_language": comparisons, "controls": controls,
              "identity": identity, "seconds": time.monotonic() - t0,
              "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "independence": "Fresh implementation, no producer source read or imported"}
    (OUT / "product_results.json").write_text(json.dumps(result, indent=2) + "\n")
    (OUT / "product_automata.json").write_text(json.dumps(full, indent=2) + "\n")
    print(json.dumps({"status": result["status"],
                      "positive_states": {k: [p["reachable_states"] for p in v["placements"]]
                                          for k, v in families.items()},
                      "comparison_states": [c["comparison"]["reachable_comparison_states"]
                                            for c in comparisons],
                      "controls": len(controls), "seconds": result["seconds"]}))


if __name__ == "__main__":
    main()
