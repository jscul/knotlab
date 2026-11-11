"""Run the six-bit learning experiment. The learner sees only post-move assignments."""

from argparse import ArgumentParser
from dataclasses import dataclass
from hashlib import sha256
from itertools import product
import json
from pathlib import Path
from time import perf_counter

from learner import learn


ID = "SIX-BIT-REUSE-20261111-001-E001"
PORTS = "abcxyz"  # Names are for reporting and constructing the environment.
SIX_BIT_WORDS = tuple(product((0, 1), repeat=6))
FOUR_BIT_WORDS = tuple(product((0, 1), repeat=4))
ALL = 0xff  # All eight entries permitted.


def word(bits):
    return "".join(str(bit) for bit in bits)


def entries(mask, size):
    return "".join("1" if mask & (1 << i) else "0" for i in range(size))


@dataclass(frozen=True)
class LocalRule:
    ports: tuple
    forbidden: tuple

    def permits(self, state):
        return tuple(state[i] for i in self.ports) not in self.forbidden


def not_all_equal(triple):
    indices = tuple(PORTS.index(v) for v in triple)
    return LocalRule(indices, ((0, 0, 0), (1, 1, 1)))


def recode(rules):
    # Physical y[i] = x[order[i]] XOR polarity[i].
    order = (4, 2, 0, 5, 3, 1)
    negated = {1, 4}
    recoded = []
    for rule in rules:
        ports = tuple(order.index(old_port) for old_port in rule.ports)
        forbidden = tuple(tuple(value ^ (i in negated) for value, i in zip(row, ports))
                          for row in rule.forbidden)
        recoded.append(LocalRule(ports, forbidden))
    return tuple(recoded)


def panels():
    triples = ("abc", "ayz", "xbz", "xyc")
    original = tuple(not_all_equal(t) for t in triples)
    equivalent = tuple(not_all_equal(t) for t in ("xyz", "xbc", "ayc", "abz"))
    result = {"original": original, "equivalent": equivalent}
    for omitted in triples:
        result["remove_" + omitted] = tuple(not_all_equal(t) for t in triples if t != omitted)
    result["free"] = ()
    result["disconnected"] = (LocalRule((0, 1), ((0, 1), (1, 0))),)
    result["recoded"] = recode(original)
    return result


def legal_initial_states(rules):
    # Evaluation can enumerate starts. Inside any episode, this list is inaccessible.
    return tuple(state for state in SIX_BIT_WORDS if all(rule.permits(state) for rule in rules))


def attempt(state, port, rules):
    candidate = list(state)
    candidate[port] ^= 1
    candidate = tuple(candidate)
    for rule in rules:
        if port in rule.ports and not rule.permits(candidate):
            return state
    return candidate


def explore(start, rules):
    learner = learn(start)
    trace = bytearray(start)
    state = start
    try:
        port = next(learner)
        while True:
            state = attempt(state, port, rules)
            trace.append(port)
            trace.extend(state)
            port = learner.send(state)
    except StopIteration as completed:
        record = completed.value
    return record, sha256(trace).hexdigest()


# The consumer has no base, walker, labels or task predicate. These two checks
# are ordinary constraints on four fresh external bits and a shared hidden bit.
def table_allows(mask, a, b, c):
    index = 4 * a + 2 * b + c
    return bool(mask & (1 << index))


def upstairs(first_table, second_table, shared=True):
    hidden_pairs = ((0, 0), (1, 1)) if shared else tuple(product((0, 1), repeat=2))
    result = []
    for p, q, r, s in FOUR_BIT_WORDS:
        allowed = any(
            table_allows(first_table, p, q, left) and table_allows(second_table, right, r, s)
            for left, right in hidden_pairs
        )
        result.append(int(allowed))
    return word(result)


def reuse(masks):
    lower, upper = {}, {}
    for triple, mask in masks.items():
        name = "".join(PORTS[i] for i in triple)
        lower[name] = entries(mask, 8)
        upper[name] = upstairs(mask, mask)
    # All twenty transfers above have already run. Only the scorer names xyz.
    selected = masks[(3, 4, 5)]
    interventions = {
        "erased": upstairs(ALL, ALL),
        "split_hidden": upstairs(selected, selected, shared=False),
        "admit_000_in_first": upstairs(selected | 1, selected),
        "admit_111_in_first": upstairs(selected | (1 << 7), selected),
    }
    return {"lower": lower, "upper": upper, "interventions_xyz": interventions}


def trajectory(record):
    return [
        {"state": word(entry["state"]),
         "trial": entry["trial_count"],
         "learned_assignments_per_triple": list(entry["masks"])}
        for entry in record["trajectory"]
    ]


def run(smoke=False):
    started = perf_counter()
    root = Path(__file__).resolve().parent
    result = {
        "experiment_id": ID,
        "evidence_stage": "exploratory",
        "contract_sha256": sha256((root / "contract.json").read_bytes()).hexdigest(),
        "producer_sha256": {name: sha256((root / name).read_bytes()).hexdigest()
                            for name in ("learner.py", "run.py")},
        "entry_order": "Ascending binary words, 1 means allowed. Trajectory masks use bit 4a+2b+c for local word abc, in lexicographic triple order.",
        "panels": {},
    }
    first_signal = None
    for panel_name, rules in panels().items():
        readings, runs, discovered = {}, [], {}
        for start in legal_initial_states(rules):
            record, trace_hash = explore(start, rules)
            key = tuple(record["masks"].items())
            # Deduplicate only the serialized evidence, after every cold learner
            # and its upper consumer have both run independently.
            transfer = reuse(record["masks"])
            if key not in discovered:
                label = "reading_" + str(len(discovered) + 1)
                discovered[key] = label
                readings[label] = transfer
            label = discovered[key]
            if first_signal is None:
                first_signal = perf_counter() - started
                result["first_trajectory"] = trajectory(record)
            runs.append({
                "start": word(start), "readings": label, "reached": record["visited_count"],
                "forward_trials": record["forward_trials"], "backtracks": record["backtracks"],
                "trial_count": record["trial_count"], "max_stack": record["max_stack"],
                "trace_sha256": trace_hash,
            })
            if smoke:
                break
        result["panels"][panel_name] = {"readings": readings, "runs": runs}
        if smoke:
            break
    return result, first_signal, perf_counter() - started


def main():
    parser = ArgumentParser(description=__doc__)
    parser.add_argument("--smoke", action="store_true", help="only the first original start")
    parser.add_argument("--output", type=Path, help="save the full deterministic record")
    args = parser.parse_args()
    result, first_signal, elapsed = run(args.smoke)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    for name, panel in result["panels"].items():
        run_counts = sorted({r["reached"] for r in panel["runs"]})
        first = next(iter(panel["readings"].values()))
        print(f"{name}: {len(panel['runs'])} starts, reached {run_counts}, "
              f"first start xyz={first['lower']['xyz']} upstairs={first['upper']['xyz']}")
    print(f"First transfer {first_signal:.4f}s. Elapsed {elapsed:.3f}s.")


if __name__ == "__main__":
    main()
