"""Run the registered fit, release blind predictions, then let the scorer join labels."""

import argparse
from collections import Counter, defaultdict
from datetime import datetime, timezone
from hashlib import sha256
from importlib.util import module_from_spec, spec_from_file_location
import json
from pathlib import Path
import resource
import sys
from time import monotonic

from learner import KnotLearner, pattern_counts
from ordinary import NumericGroups
from scoring import summarize

FAMILY = Path(__file__).resolve().parent
TICKET = FAMILY.parent.name
ROOT = FAMILY.parents[2]
RECORD = ROOT / "research" / TICKET
ARCHIVE = ROOT / "artifacts" / TICKET / FAMILY.name
PRIOR = ROOT / "experiments/PIXEL-LETTERS-20261122-001/PIXEL-LETTERS-20261122-001-E001_letters/learner.py"
PANEL = FAMILY / "panel"
LAWS = ("parity","nae")
SCHEDULES = ("ordinary","opposite","shifted")
LIMIT = 64


def load_previous():
    spec = spec_from_file_location("previous_pixel_classifier", PRIOR)
    previous = module_from_spec(spec)
    spec.loader.exec_module(previous)
    return previous.KnotLearner


def packed(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":")).encode("ascii")


def digest(path):
    return sha256(path.read_bytes()).hexdigest()


def load(path):
    return json.loads(path.read_text())


def lines(path):
    return [json.loads(line) for line in path.read_text().splitlines()]


def save(path, obj):
    with path.open("x") as f:
        json.dump(obj, f, sort_keys=True, indent=2)
        f.write("\n")


def save_lines(path, data):
    with path.open("xb") as f:
        for obj in data:
            f.write(packed(obj) + b"\n")


def check(path, expected):
    if digest(path) != expected:
        raise ValueError(f"Content seal mismatch for {path}")


def public_rows(path):
    data = lines(path)
    seen = set()
    for row in data:
        if set(row) != {"id","pixels"}:
            raise ValueError("Public row has undeclared fields")
        raw = row["pixels"]
        if type(raw) is not str or len(raw) != 64 or set(raw) - set("01"):
            raise ValueError("Invalid 64-bit input")
        if sha256(raw.encode()).hexdigest() != row["id"] or row["id"] in seen:
            raise ValueError("Public row identity does not match a distinct bitmap")
        seen.add(row["id"])
    return data


def validate_inputs(*panel_names):
    contract = load(FAMILY / "contract.json")
    if contract["status"] != "Frozen":
        raise ValueError("Fit requires a frozen contract")
    check(FAMILY / "proposed_contract.json", contract["approved_candidate_sha256"])
    check(RECORD / "design_review/red_team_report.json", contract["design_review_sha256"])
    reviewed = load(FAMILY / "proposed_contract.json")
    if reviewed != {**{k:v for k,v in contract.items() if k not in
                   {"approved_candidate_sha256","design_review_sha256","frozen_utc","status"}}, "status":"Proposed"}:
        raise ValueError("Scientific contract differs from the reviewed proposal")
    resources = [PRIOR, *(FAMILY / name for name in ("learner.py","ordinary.py","study.py","scoring.py")),
                 *(PANEL / name for name in panel_names)]
    for p in resources:
        check(p, contract["source_sha256"][str(p.relative_to(ROOT))])


def open_phase(out, name):
    target = out / name
    target.mkdir(exist_ok=False, parents=True)
    return target


def release(target, parents, start, observations):
    obj = {"files": {p.name: digest(p) for p in sorted(target.iterdir())},
           "parents": {k:digest(v) for k,v in parents.items()},
           "contract": digest(FAMILY / "contract.json"),
           "observations": observations, "utc": datetime.now(timezone.utc).isoformat(),
           "seconds": round(monotonic()-start, 6), "max_rss_kib": resource.getrusage(resource.RUSAGE_SELF).ru_maxrss,
           "python": sys.version.split()[0]}
    save(target / "release.json", obj)


def check_release(target):
    obj = load(target / "release.json")
    check(FAMILY / "contract.json", obj["contract"])
    for name, expected in obj["files"].items():
        check(target / name, expected)
    return obj


def train(out):
    start = monotonic()
    validate_inputs("train.jsonl","training_key.jsonl")
    gate = RECORD / "audit/R1/red_team_report.json"
    approval = load(gate)
    bindings = [x for x in approval["input_digests"] if
                (gate.parent / x["path"]).resolve() == FAMILY / "contract.json"]
    if approval["gate"] != "run_authorization" or approval["verdict"] != "PASS" or len(bindings) != 1:
        raise ValueError("Missing run authorization for this contract")
    check(FAMILY / "contract.json", bindings[0]["sha256"])
    views = public_rows(PANEL / "train.jsonl")
    keys = lines(PANEL / "training_key.jsonl")
    teaching = {r["id"]: "LT".index(r["label"]) for r in keys}
    if len(views) != LIMIT or [r["condition"] for r in keys] != ["train"]*LIMIT or set(teaching) != {r["id"] for r in views}:
        raise ValueError("Incomplete or invalid acquisition bank")
    ordinary = [teaching[row["id"]] for row in views]
    if Counter(ordinary) != {0:32,1:32}:
        raise ValueError("Unbalanced acquisition bank")
    schedules = {"ordinary": ordinary, "opposite": [1-x for x in ordinary], "shifted": ordinary[17:]+ordinary[:17]}
    prior = load_previous()
    devices = {f"{law}-{v}":KnotLearner(law,training_limit=LIMIT) for v in SCHEDULES for law in LAWS}
    devices.update({f"integer-{v}":NumericGroups(training_limit=LIMIT) for v in SCHEDULES})
    devices.update({f"previous-{law}":prior(law,training_limit=LIMIT) for law in LAWS})
    target = open_phase(out,"fit")
    receipts = []
    signatures = {v: [Counter(),Counter()] for v in SCHEDULES}
    for i, row in enumerate(views):
        pixels = tuple(map(int,row["pixels"]))
        obs = {}
        for key, device in devices.items():
            v = "ordinary" if key.startswith("previous") else key.split("-")[1]
            guess = device.predict(pixels)
            correct = guess == schedules[v][i]
            device.learn(pixels, guess, correct)
            obs[key] = {"guess": guess, "correct": correct}
            if not key.startswith("integer"):
                obs[key]["after_sha256"] = sha256(packed(device.export_memory())).hexdigest()
        # Observer-only accounting; no path into any device.
        h = tuple(pattern_counts(pixels))
        for v in SCHEDULES:
            signatures[v][schedules[v][i]][h] += 1
        receipts.append({"presentation":i+1,"id":row["id"],"arms":obs})
    save_lines(target / "receipts.jsonl",receipts)
    fits = {}
    for key, device in devices.items():
        if not key.startswith("previous"):
            diagnostics = device.finalize()
            fits[key] = diagnostics if diagnostics is not None else device.selection()
        save(target/(key+".json"), device.export_memory())
    fits["shift_control"] = {"labels_changed":sum(a!=b for a,b in zip(ordinary,schedules["shifted"])),
        "class_histogram_multisets_changed": [signatures["ordinary"][c] != signatures["shifted"][c] for c in (0,1)],
        "distinct_train_histograms":len(set(signatures["ordinary"][0]) | set(signatures["ordinary"][1]))}
    save(target/"diagnostics.json",fits)
    release(target, {"run_authorization":gate,"image_stream":PANEL/"train.jsonl","training_rewards":PANEL/"training_key.jsonl"},
            start, {"presentations":len(views),"arms":len(devices),"epochs":1})


def issue(device, xs):
    return [device.predict(pixels) for pixels in xs]


def predict(out):
    start = monotonic()
    validate_inputs("queries.jsonl")
    fit = out/"fit"
    check_release(fit)
    queries = public_rows(PANEL/"queries.jsonl")
    xs = [tuple(map(int,q["pixels"])) for q in queries]
    histograms = [tuple(pattern_counts(p)) for p in xs]
    # All distinct query signatures get a literal diagnostic read on the first bitmap having it.
    # Every fitted primary reader separately reads every raw bitmap in full.
    witnesses = {}
    for i,h in enumerate(histograms):
        witnesses.setdefault(h,i)
    target = open_phase(out,"blind")
    actions = {}
    prior = load_previous()
    raw_details = []
    for law in LAWS:
        exports = {v: load(fit / f"{law}-{v}.json") for v in SCHEDULES}
        for v, other in (("ordinary","opposite"),("opposite","ordinary")):
            dev = KnotLearner.from_memory(exports[v])
            if law == "parity" and v == "ordinary":
                raw_details = [dev.explain(p) for p in xs]
                actions[f"{law}-{v}"] = [r["guess"] for r in raw_details]
                details = {str(i):dev.explain(xs[i],detail=True) for i in witnesses.values()}
                save(target/"rule_votes.json", {"mask_order":dev.selection()["masks"],
                     "by_first_index":details})
            else:
                actions[f"{law}-{v}"] = issue(dev,xs)
            dev.restore_memory(exports[v])
            actions[f"{law}-sham-{v}"] = issue(dev,xs)
            dev.restore_memory(exports[other])
            actions[f"{law}-swapped-{v}"] = issue(dev,xs)
            dev.clear_memory()
            actions[f"{law}-clear-{v}"] = issue(dev,xs)
            dev.restore_memory(exports[v])
            actions[f"{law}-restored-{v}"] = issue(dev,xs)
            if dev.export_memory() != exports[v]:
                raise ValueError("Learned words were not restored")
            if v == "ordinary":
                previous_selection = dev.selection()
                for intervention in ("erase","allsize"):
                    dev.restore_memory(exports[v])
                    if intervention == "erase":
                        dev.erase_selection()
                    else:
                        dev.use_all_same_size()
                    changed = dev.selection()
                    for name in ("class_counts","class_totals"):
                        if previous_selection[name] != changed[name]:
                            raise ValueError("Membership intervention changed class calibration")
                    choices = {h:dev.predict(xs[i]) for h,i in witnesses.items()}
                    actions[f"{law}-{intervention}-ordinary"] = [choices[h] for h in histograms]
        actions[f"{law}-shifted"] = issue(KnotLearner.from_memory(exports["shifted"]),xs)
        actions[f"previous-{law}"] = issue(prior.from_memory(load(fit/f"previous-{law}.json")),xs)
    for v in SCHEDULES:
        twin = NumericGroups.from_memory(load(fit/f"integer-{v}.json"))
        actions[f"integer-{v}"] = issue(twin,xs)
    log = [{"id":q["id"],"actions":{arm:v[i] for arm,v in actions.items()},
            "counts":raw_details[i]["counts"],"votes":raw_details[i]["votes"],"abstentions":raw_details[i]["abstentions"]}
           for i,q in enumerate(queries)]
    save_lines(target/"predictions.jsonl",log)
    release(target,{"fitted_state_release":fit/"release.json","queries":PANEL/"queries.jsonl"},start,
            {"images":len(xs),"arms":len(actions),"distinct_signatures":len(witnesses),"feedback_events":0})


def score(out):
    start = monotonic()
    fit, blind = out/"fit", out/"blind"
    check_release(fit)
    check(fit/"release.json",check_release(blind)["parents"]["fitted_state_release"])
    validate_inputs("queries.jsonl","scorer_key.jsonl","train.jsonl","training_key.jsonl")
    view = {r["id"]:r["pixels"] for r in public_rows(PANEL/"queries.jsonl")}
    train_labels = {k["id"]:k["label"] for k in lines(PANEL/"training_key.jsonl")}
    known = defaultdict(set)
    for r in public_rows(PANEL/"train.jsonl"):
        known[tuple(pattern_counts(tuple(map(int,r["pixels"]))))].add(train_labels[r["id"]])
    result = summarize(lines(blind/"predictions.jsonl"),lines(PANEL/"scorer_key.jsonl"),view,known)
    target = open_phase(out,"scored")
    save(target/"scores.json",result)
    release(target,{"blind_release":blind/"release.json","scorer_key":PANEL/"scorer_key.jsonl"},
            start,{"images":len(view),"primary_gate":result["primary_gate"]})


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("phase",choices=("train","predict","score"))
    parser.add_argument("--out",type=Path,default=ARCHIVE)
    args = parser.parse_args()
    {"train":train,"predict":predict,"score":score}[args.phase](args.out)

