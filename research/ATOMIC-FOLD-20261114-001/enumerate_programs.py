"""Find a smallest encoder in the supplied grammar from labeled training examples."""

import argparse
import itertools
import json
import operator


OPS = {"AND": operator.and_, "OR": operator.or_, "XOR": operator.xor,
       "NAND": lambda left, right: ~(left & right)}
CONSUMERS = {
    "c0": ("BC", (1, 2, 3)), "c1": ("AB", (3,)),
    "c2": ("AC", (1, 2, 3)), "c3": ("BC", (3,)),
    "c4": ("AB", (1, 2, 3)), "c5": ("AC", (3,)),
}


def examples(worlds):
    labels = {}
    for name, (pair, queries) in CONSUMERS.items():
        rows = []
        for world in worlds:
            allowed = [set(h for h in (0, 1) if world >> (2 * "ABC".index(rule) + h) & 1)
                       for rule in pair]
            joint = allowed[0] & allowed[1]
            rows.append(tuple(int(any(query >> h & 1 for h in joint)) for query in queries))
        labels[name] = rows
    return labels


def exact_codes(worlds, labels):
    """Search receives input words and answers. It never receives the consumer definitions."""
    all_rows = (1 << len(worlds)) - 1
    inputs = [sum(((world >> i) & 1) << r for r, world in enumerate(worlds))
              for i in range(6)]
    partitions, valid_bits, interested = {}, {}, {}
    for name, signatures in labels.items():
        groups = {}
        for i, signature in enumerate(signatures):
            groups[signature] = groups.get(signature, 0) | 1 << i
        partitions[name] = groups
        n = len(groups)
        if n not in (2, 4):
            raise ValueError("This minimal-width check assumes two or four answer classes")
        # At full capacity each class has exactly one code. Each individual
        # emitted bit must therefore be constant on that entire class.
        valid_bits[name] = {}
        for bits in itertools.product((0, 1), repeat=n):
            mask = sum(group for bit, group in zip(bits, groups.values()) if bit)
            valid_bits[name][mask] = bits
            if len(set(bits)) == 2:
                interested.setdefault(mask, []).append(name)
    winners, count = {}, 0

    def consider(regs, newest, gates):
        for name in interested.get(regs[newest], ()):
            if name in winners:
                continue
            groups, good = partitions[name], valid_bits[name]
            if len(groups) == 2:
                taps = [newest]
            else:
                for earlier in range(newest):
                    other = good.get(regs[earlier])
                    if other and len(set(zip(other, good[regs[newest]]))) == len(groups):
                        taps = [earlier, newest]
                        break
                else:
                    continue
            decoder = {}
            for idx, signature in enumerate(groups):
                code = sum(good[regs[tap]][idx] << bit for bit, tap in enumerate(taps))
                decoder[code] = list(signature)
            winners[name] = {"gates": list(gates), "taps": taps, "decoder": decoder,
                             "candidate_gates_so_far": count}

    def walk(regs, gates, left):
        nonlocal count
        for a, b in itertools.combinations_with_replacement(range(len(regs)), 2):
            for op, function in OPS.items():
                value = function(regs[a], regs[b]) & all_rows
                count += 1
                if value in regs:
                    continue
                grown, trace = regs + [value], gates + [(op, a, b)]
                if left == 1:
                    consider(grown, len(regs), trace)
                else:
                    walk(grown, trace, left - 1)
                if len(winners) == len(labels):
                    return

    for i in range(len(inputs)):
        consider(inputs, i, [])
    gate_counts = [count]
    for depth in (1, 2, 3):
        if len(winners) < len(labels):
            walk(inputs, [], depth)
        gate_counts.append(count)
    if set(winners) != set(labels):
        raise ValueError(f"Missing encoders for {set(labels) - set(winners)}")
    return winners, gate_counts


def decode(world, record):
    regs = [world >> i & 1 for i in range(6)]
    for op, a, b in record["gates"]:
        regs.append(OPS[op](regs[a], regs[b]) & 1)
    code = sum(regs[tap] << i for i, tap in enumerate(record["taps"]))
    return tuple(record["decoder"][code])


def run():
    train = [w for w in range(64) if w.bit_count() % 2 == 0]
    test = sorted(set(range(64)) - set(train))
    winners, counts = exact_codes(train, examples(train))
    for name, labels in examples(test).items():
        predictions = [decode(w, winners[name]) for w in test]
        winners[name]["held_out_all_queries_correct"] = sum(a == b for a, b in zip(predictions, labels))
    return {"worlds_train": len(train), "worlds_held_out": len(test),
            "candidate_gate_evaluations_cumulative_by_depth": counts, "winners": winners}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = run()
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        for name, prog in sorted(result["winners"].items()):
            print(name, "width", len(prog["taps"]), "gates", prog["gates"],
                  "held-out worlds correct", prog["held_out_all_queries_correct"], "/ 32")
