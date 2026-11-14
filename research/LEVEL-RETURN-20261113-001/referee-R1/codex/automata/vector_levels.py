"""Fresh vectorized address actions and direct state checks at levels 1..22."""
from hashlib import sha256
from pathlib import Path
import argparse
import json
import resource
import time

import numpy as np

ROOT = Path(__file__).resolve().parents[5]
OUT = Path(__file__).resolve().parent
SOURCE = ROOT / "research/ADDR-KNOTS-20261113-001/referee-R1/codex/returns"
KEYS = {
    "two": "91c75673c09d90467aefb05915109cabd5a02fc0103944cb525be8f56ca212c2",
    "three": "f4fd01e9afa5631440f1607276c889547b4767423ee44873e86cf9c85b7d2c4d",
}


def scalar_map(key, q, x, n):
    _, swaps, zero, one, _ = key
    y = 0
    for pos in range(n - 1, -1, -1):
        b = (x >> pos) & 1
        y = 2 * y + (b ^ swaps[q])
        q = (one if b else zero)[q]
    return y


def scalar_word(key, word, x, n):
    for q in reversed(word):
        x = scalar_map(key, q, x, n)
    return x


def scalar_control(key, n, words, actions):
    checked = 0
    for wi, word in enumerate(words):
        expected = np.array([scalar_word(key, word, x, n)
                             for x in range(1 << n)], dtype=np.uint32)
        assert np.array_equal(expected, actions[wi]), (n, wi)
        checked += len(expected)
    return checked


def iterate(key, maximum):
    s, swaps, zero, one, placements = key
    words = [()] + [(q,) for q in range(s)] + [(q, r) for q in range(s) for r in range(s)]
    previous = np.zeros((s, 1), dtype=np.uint32)
    rows = []
    scalar_checked = 0
    for n in range(1, maximum + 1):
        t0 = time.monotonic()
        half = 1 << (n - 1)
        bases = np.empty((s, half * 2), dtype=np.uint32)
        for q in range(s):
            bases[q, :half] = np.uint32(swaps[q] << (n - 1)) | previous[zero[q]]
            bases[q, half:] = np.uint32((1 ^ swaps[q]) << (n - 1)) | previous[one[q]]
        previous = bases
        identity = np.arange(half * 2, dtype=np.uint32)
        actions = [identity] + [bases[q] for q in range(s)] + [
            bases[q, bases[r]] for q in range(s) for r in range(s)
        ]
        assert words[0] == () and np.array_equal(actions[0], identity)
        if n <= 8:
            scalar_checked += scalar_control(key, n, words, actions)
        parity = (np.bitwise_count(identity) & 1).astype(np.uint8)
        first_last = (((identity >> (n - 1)) ^ identity) & 1).astype(np.uint8)
        yield n, actions, parity, first_last, t0, scalar_checked


def family(name, maximum):
    raw = (SOURCE / (KEYS[name] + ".json")).read_bytes()
    key = json.loads(raw)["key"]
    rows = []
    for n, actions, parity, first_last, t0, scalar_checked in iterate(key, maximum):
        state = parity if name == "two" else first_last
        details = []
        distinct_bad = set()
        for placement in key[4]:
            a, b, c = (actions[i] for i in placement)
            retained = (a != b) & (a != c) & (b != c)
            monochromatic = (state[a] == state[b]) & (state[a] == state[c])
            bad = retained & monochromatic
            bad_count = int(np.count_nonzero(bad))
            bad_indices = np.flatnonzero(bad)
            examples = []
            for x in bad_indices[:8]:
                triple = tuple(sorted((int(a[x]), int(b[x]), int(c[x]))))
                examples.append({"input": int(x), "word": format(int(x), f"0{n}b"),
                                 "images": [int(a[x]), int(b[x]), int(c[x])],
                                 "knot": triple, "values": [int(state[a[x]]),
                                                             int(state[b[x]]),
                                                             int(state[c[x]])]})
            if bad_count <= 16:
                for x in bad_indices:
                    distinct_bad.add(tuple(sorted((int(a[x]), int(b[x]), int(c[x])))))
            elif name == "two":
                raise AssertionError(("unexpectedly many #2 bad inputs", n, placement, bad_count))
            details.append({"placement": placement,
                            "retained_inputs": int(np.count_nonzero(retained)),
                            "excluded_inputs": len(a) - int(np.count_nonzero(retained)),
                            "monochromatic_before_exclusion": int(np.count_nonzero(monochromatic)),
                            "bad_inputs": bad_count, "bad_examples": examples})
        bad_total = sum(d["bad_inputs"] for d in details)
        if name == "two" and n >= 3 and n % 2:
            assert bad_total == 0, (name, n, bad_total)
        if name == "three" and n >= 2 and not n % 2:
            assert bad_total == 0, (name, n, bad_total)
        if name == "two" and n >= 4 and not n % 2:
            assert bad_total == 2 and len(distinct_bad) == 2
            assert [d["bad_inputs"] for d in details] == [2, 0, 0]
            assert [e["input"] for e in details[0]["bad_examples"]] == [2, 3]
            # The original identity image is x=2 or 3; these address sets differ.
            assert 2 in next(t for t in distinct_bad if 2 in t)
            assert 3 in next(t for t in distinct_bad if 3 in t)
        row = {"level": n, "addresses": 1 << n, "state": "parity" if name == "two" else "first_last",
               "placements": details, "bad_inputs_total": bad_total,
               "distinct_bad_knots": sorted(distinct_bad) if name == "two" else None,
               "seconds": time.monotonic() - t0}
        rows.append(row)
        print(json.dumps({"key": name, "level": n, "bad_inputs": bad_total,
                          "seconds": row["seconds"]}), flush=True)
    return {"key": key, "source_sha256": sha256(raw).hexdigest(), "levels": rows,
            "scalar_word_values_checked_through_8": scalar_checked}


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--max-level", type=int, default=22)
    args = parser.parse_args()
    t0 = time.monotonic()
    results = {name: family(name, args.max_level) for name in KEYS}
    # Wrong parity and wrong state are independently falsified here too.
    assert results["two"]["levels"][3]["bad_inputs_total"] == 2
    assert results["three"]["levels"][2]["bad_inputs_total"] > 0
    result = {"status": "passed", "maximum_level": args.max_level, "families": results,
              "seconds": time.monotonic() - t0,
              "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
              "source_sha256": sha256(Path(__file__).read_bytes()).hexdigest(),
              "numpy": np.__version__, "imports_producer_code": False,
              "identity_is_explicit_arange_at_index_zero": True}
    target = OUT / f"vector_levels_{args.max_level}.json"
    target.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({"status": "passed", "maximum_level": args.max_level,
                      "seconds": result["seconds"], "max_rss_kib": result["max_rss_kib"]}))


if __name__ == "__main__":
    main()
