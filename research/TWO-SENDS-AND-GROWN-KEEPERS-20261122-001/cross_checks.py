"""Independent checks of the physical records in the two frozen experiments."""
from collections import Counter
from functools import reduce
from itertools import product
from pathlib import Path
import gzip
import json
import z3

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
EPIC = HERE.name


def read_receipt(leaf, name):
    path, = (ROOT / "artifacts" / (EPIC + leaf)).glob("*/" + name)
    raw = path.read_bytes()
    return json.loads(gzip.decompress(raw) if name.endswith(".gz") else raw)


def legal(bits, law):
    return sum(bits) % 2 == 0 if law == "parity" else len(set(bits)) == 2


def check_keeper_extensions():
    """From the physical supports alone, pin an entire keeper and each paid bit."""
    counts = {law: Counter() for law in ("parity", "nae")}
    for record in read_receipt("B", "census.json.gz")["records"]:
        if record["historical_control"]:
            continue
        law = record["law"]
        count = counts[law]
        count["proposals"] += 1
        stages = record["stages"]
        if not stages[0]["canonical"]:
            continue
        count["lawful_starts"] += 1
        focals = []
        for stage, transition in zip(stages[1:], record["transitions"]):
            assert stage["canonical"]
            holdings = stage["holdings"]
            owners = Counter(d for holder in holdings for d in holder)
            for birth in transition.get("births", []):
                if len(birth["paid"]) == 1 and len(birth["fresh"]) == 3:
                    focals.append((birth["paid"][0], tuple(birth["fresh"])))
                    count["focal_children"] += 1
            applicable = [(u, names) for u, names in focals if all(owners[d] == 1 for d in names)]
            if not applicable:
                continue
            solver = z3.Solver()
            variables = {d: z3.Bool(f"d_{d}") for d in owners}
            for holder in holdings:
                marks = [variables[d] for d in holder]
                if law == "parity":
                    solver.add(z3.Not(reduce(z3.Xor, marks)))
                else:
                    solver.add(z3.Or(marks), z3.Or([z3.Not(m) for m in marks]))
            for u, names in applicable:
                for holder in holdings:
                    if set(holder).intersection((u, *names)):
                        continue
                    count["separate_placements"] += 1
                    for bits in product((False, True), repeat=len(holder)):
                        if not legal(bits, law):
                            continue
                        fixed = [variables[d] if bit else z3.Not(variables[d])
                                 for d, bit in zip(holder, bits, strict=True)]
                        for value in (False, True):
                            assert solver.check(*fixed, variables[u] == value) == z3.sat
                            count["complete_word_extensions"] += 1
    for count in counts.values():
        assert (count["proposals"], count["lawful_starts"], count["focal_children"],
                count["separate_placements"]) == (38, 28, 47, 280)
    return counts


def check_founder_control():
    """Terminal-only and ready-then-terminal reads on the original eight marks."""
    out = {}
    for law in ("parity", "nae"):
        counts = Counter()
        for values in product((0, 1), repeat=8):
            a, b, c, u, v, x, y, s = values
            keeper = (a, b, c, s)
            if not (legal(keeper, law) and legal((a, b, c, u, v, x, y), law)):
                continue
            terminal = (a, c, b, s) if u == 0 else (c, b, a, s)
            answer = {(1, 0, 1, 0): 0, (0, 1, 1, 0): 1}.get(terminal)
            ready = keeper == (1, 1, 0, 0)
            counts["original_words"] += 1
            counts["ready"] += ready
            if answer is not None:
                counts["correct" if answer == u else "wrong"] += 1
                assert (answer == u) == ready
        out[law] = counts
    assert (out["parity"]["ready"], out["parity"]["wrong"], out["parity"]["original_words"]) == (8, 8, 64)
    assert (out["nae"]["ready"], out["nae"]["wrong"], out["nae"]["original_words"]) == (16, 16, 222)
    return out


def check_sends():
    """Read only physical marks along every stored canonical state sequence."""
    data = read_receipt("A", "sends.json.gz")
    short = ["10010", "00110"]
    long = ["10010", "01010", "10001", "00101"]
    counts = {law: Counter() for law in ("parity", "nae")}
    for run in data["all_physical_orders"]:
        interrupted = run["condition"] == "interrupted"
        enabled = run["condition"] != "read_disabled" and run["offer"] == 2
        expected = [long if enabled and not interrupted else short,
                    long if enabled and interrupted else short]
        assert run["receiver_transcripts"] == expected
        expected_orders = 15 if enabled else 6
        assert run["complete_orders"] == expected_orders
        tally = counts[run["law"]]
        tally["launch_conditions"] += 1
        tally["all_schedules"] += expected_orders
        if run["naming"] != "original" or run["reversed_bank"]:
            continue
        board = data["originals"][str(int(interrupted))]
        sockets = [device["receipt"] + device["memory"] for device in board["devices_in_c8_u8_order"]]
        first = int(run["common_initial_before_name_transport"], 16)
        def observe(delta):
            return ["".join(str(((first ^ delta) >> name) & 1) for name in socket)
                    for socket in sockets]
        states = {int(node["delta_from_initial"], 16): node["enabled"]
                  for node in run["all_order_state_graph"]}
        todo = [(0, [[word] for word in observe(0)])]
        terminal = 0
        while todo:
            delta, records = todo.pop()
            if not states[delta]:
                assert records == expected
                terminal += 1
            for move in states[delta]:
                after = int(move["after_delta"], 16)
                word = first ^ delta
                for a, b in move["swaps"]:
                    if ((word >> a) ^ (word >> b)) & 1:
                        word ^= (1 << a) | (1 << b)
                assert word == first ^ after
                local = observe(after)
                extended = [old + ([new] if old[-1] != new else [])
                            for old, new in zip(records, local, strict=True)]
                todo.append((after, extended))
        assert terminal == expected_orders
        tally["physically_redecoded_canonical_orders"] += terminal
    for tally in counts.values():
        assert (tally["launch_conditions"], tally["all_schedules"],
                tally["physically_redecoded_canonical_orders"]) == (36, 324, 54)
    return counts


if __name__ == "__main__":
    print(json.dumps({"two_sends": check_sends(), "separate_keeper": check_keeper_extensions(),
                      "founder_calibration": check_founder_control()}, indent=2))
