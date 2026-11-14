"""FORGET-RULE-20261114-001A, the advisor's counterexample to the downward rule D, as a regression control: x != y realised by
NAE(x,y,u), NAE(x,y,v), NAE(x,y,w), NAE(u,v,w). Block: p0 != a1, p1 != p2, a0 != a2, SELF(a0, a1, a2). Expected: D acyclic, no
port passed by identity, rule A not certified, and the exact semigroup test non-forgetting."""
import json, sys
from pathlib import Path
HERE = Path(__file__).resolve().parent
R = HERE.parents[2]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(R / "experiments/FREE-TARGET-20261114-001A/FREE-TARGET-20261114-001A-E001_free_target/codex"))
import rule_A as A
import inputs, relations
def gadget(x, y, u, v, w):
    return [["K", [x, y, u]], ["K", [x, y, v]], ["K", [x, y, w]], ["K", [u, v, w]]]
calls = gadget(0, 4, 6, 7, 8) + gadget(1, 2, 9, 10, 11) + gadget(3, 5, 12, 13, 14) + [["SELF", [3, 4, 5]]]
defs = [[3, 12, calls]]
paths = inputs.load_paths()
prep = paths.Preparation(defs)
calls_R = relations.per_call(prep)
sg = relations.semigroup([c["relation"] for c in calls_R])
a = A.decide(defs)
out = dict(defs=defs, limit_alive=bool(prep.alive), R=[c["hex"] for c in calls_R], semigroup_r=sg.get("r"),
           recurring_word=sg.get("recurring_word"), rule_A=a)
print(json.dumps(out))
json.dump(out, open(HERE / "gadget_control.json", "w"), indent=1)
