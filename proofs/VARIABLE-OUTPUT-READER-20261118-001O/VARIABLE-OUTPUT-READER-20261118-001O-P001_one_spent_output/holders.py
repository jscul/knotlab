"""Query the frozen K closure for the six-loose prefix needed by a spent twin."""

from hashlib import sha256
from importlib import util
import json
from pathlib import Path
import sys


PROOFS = Path(__file__).resolve().parents[2]
FAMILY = PROOFS / "VARIABLE-OUTPUT-READER-20261118-001K" / "VARIABLE-OUTPUT-READER-20261118-001K-P001_third_three_fresh"


def run():
    script = FAMILY / "closure.py"
    assert sha256(script.read_bytes()).hexdigest() == "79a9d330438f988f094ad364642db6d42a5020f9e5bbab0199d231f357e68240"
    spec = util.spec_from_file_location("third_three_output_closure", script)
    closure = util.module_from_spec(spec)
    sys.modules[spec.name] = closure
    spec.loader.exec_module(closure)

    _, _, transitions, _, _ = closure.explore()
    record = json.loads((FAMILY / "closure.json").read_text())
    state_count = len(transitions)
    transition_count = sum(map(len, transitions.values()))
    digest = closure.fixed_point_digest(transitions)
    assert state_count == record["all_states_with_high_holder_tracking"]
    assert transition_count == record["all_edges_with_high_holder_tracking"]
    assert digest == record["fixed_point_sha256"]

    result = []
    for prior_shrinks in (0, 1):
        states = [s for s in transitions if s.prior_shrinks == prior_shrinks and s.loose == 6]
        has_triple_through_high = 0
        two_loose_at_high = 0
        two_loose_and_any_triple = 0
        for state in states:
            triples = [parents for parents, _, _ in transitions[state] if len(parents) == 3]
            high = state.high_holder
            has_triple_through_high += any(high in group for group in triples)
            if high >= 0 and state.frontier.loose[high] >= 2:
                two_loose_at_high += 1
                two_loose_and_any_triple += bool(triples)
        result.append({
            "shrinks_before_high_birth": prior_shrinks,
            "six_loose_records": len(states),
            "with_triple_through_high": has_triple_through_high,
            "with_at_least_two_loose_at_high": two_loose_at_high,
            "with_two_loose_at_high_and_any_legal_triple": two_loose_and_any_triple,
        })
    return {"tagged_fixed_point_states": state_count, "transitions": transition_count,
            "fixed_point_sha256": digest, "six_loose_after_high_birth": result}


if __name__ == "__main__":
    print(json.dumps(run(), indent=2))
