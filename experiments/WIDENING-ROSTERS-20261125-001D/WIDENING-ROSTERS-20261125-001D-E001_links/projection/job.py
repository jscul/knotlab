"""Certify every actual first-meeting triple from neutral producer histories."""

from collections import Counter, defaultdict
from dataclasses import dataclass
import gzip
import hashlib
from itertools import product
import json
import os
from pathlib import Path
import sys
import tempfile
from time import monotonic

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[3]
sys.path.insert(0, str(HERE))
sys.path.insert(0, str(ROOT / "scripts"))

from longrun import load_results
from stage import NaeProjection, ParityProjection, ordered_mask
from truth import classify


@dataclass(frozen=True)
class Round:
    holdings: tuple[tuple[int, ...], ...]
    knots: int
    distinctions: int
    holder_counts: tuple[int, ...]
    barred: frozenset[int]
    takes: dict[int, tuple[int, ...]]


def from_jsonl(root, name, expected_digest):
    path = (root / name).resolve(strict=True)
    if not path.is_relative_to(root):
        raise ValueError(f"input path escaped the producer artifact directory: {name}")
    seen = hashlib.sha256()
    rows = []
    with gzip.open(path, "rb") as source:
        for line in source:
            seen.update(line)
            rows.append(json.loads(line))
    if seen.hexdigest() != expected_digest:
        raise ValueError(f"input digest mismatch: {name}")
    return rows


def parse_rounds(rows):
    rounds = []
    supports = []
    distinction_count = 0
    holders = Counter()
    for t, row in enumerate(rows):
        if row["round"] != t:
            raise ValueError(f"out-of-order support round {t}")
        batch = []
        news = set()
        for support in row["supports"]:
            if len(support) < 1 or len(set(support)) != len(support):
                raise ValueError(f"invalid support for knot {len(supports) + len(batch)}")
            for d in support:
                if type(d) is not int or d < 0:
                    raise ValueError(f"invalid distinction at round {t}: {d}")
                holders[d] += 1
                if d >= distinction_count:
                    news.add(d)
            batch.append(tuple(sorted(support)))
        births = row.get("births")
        since = len(supports)
        takes = {}
        if births is not None:
            expected = list(range(since, since + len(batch))) if t else []
            if [birth["id"] for birth in births] != expected:
                raise ValueError(f"birth provenance differs from support order at round {t}")
            for birth in births:
                u = birth["id"]
                taken = tuple(birth["takes"])
                if len(set(taken)) != len(taken) or not set(taken) <= set(batch[u - since]):
                    raise ValueError(f"recorded takes are absent from {u}'s support at round {t}")
                if any(d >= distinction_count for d in taken):
                    raise ValueError(f"recorded take of a fresh distinction by {u} at round {t}")
                takes[u] = taken
        distinction_count += len(news)
        supports.extend(batch)
        if len(supports) != row["knots"] or distinction_count != row["distinctions"]:
            raise ValueError(f"inconsistent counts at round {t}")
        if news and max(news) >= distinction_count:
            raise ValueError(f"nonconsecutive distinction names at round {t}")
        barred = frozenset(row.get("barred", ()))
        if any(d not in range(distinction_count) or holders[d] != 1 for d in barred):
            raise ValueError(f"barred distinction is absent or shared at round {t}")
        rounds.append(Round(
            tuple(batch), len(supports), distinction_count,
            tuple(holders[d] for d in range(distinction_count)), barred, takes,
        ))
    if not rounds:
        raise ValueError("support history is empty")
    return rounds, [frozenset(support) for support in supports]


def event_key(event):
    return (event["s"], event["X"], event["Y"], event["t"])


def route_key(route):
    return (route["route"], route["w"], route["u"], route["v"])


def verify_events(events, rounds, supports, splits):
    seen_events = set()
    for event in events:
        s, x, y, t = event_key(event)
        if s not in splits or not s < t < len(rounds):
            raise ValueError(f"meeting at {t} does not follow its registered split at {s}")
        if not x or not y or x != sorted(set(x)) or y != sorted(set(y)) or x >= y:
            raise ValueError(f"noncanonical source parts at split {s}")
        if set(x) & set(y) or min(x[0], y[0]) < 0 or max(x[-1], y[-1]) >= rounds[s].knots:
            raise ValueError(f"invalid source parts at split {s}")
        key = (s, tuple(x), tuple(y))
        if key in seen_events:
            raise ValueError(f"multiple first meetings of the same source parts at split {s}")
        seen_events.add(key)
        seen_routes = set()
        for route in event["routes"]:
            kind, w, u, v = route_key(route)
            if (kind, w, u, v) in seen_routes:
                raise ValueError(f"duplicate route for first meeting at {s}/{t}")
            seen_routes.add((kind, w, u, v))
            if min(w, u, v) < 0 or max(w, u, v) >= rounds[t].knots or u == v:
                raise ValueError(f"invalid holder roles at first meeting {s}/{t}")
            a, b = supports[u] - supports[v], supports[v] - supports[u]
            if route["a"] != sorted(a) or route["b"] != sorted(b):
                raise ValueError(f"exclusive endpoint places differ from whole-stage supports at {s}/{t}")
            x_arms = route["x_arms"]
            y_arms = route["y_arms"]
            contacts = route["contacts"]
            if any(values != sorted(set(values)) for values in (x_arms, y_arms, contacts)):
                raise ValueError(f"noncanonical route distinctions at {s}/{t}")
            if not set(contacts) <= supports[u] & supports[v]:
                raise ValueError(f"the candidate identity is absent at one endpoint at {s}/{t}")
            if kind == "take":
                actor, holder = route["recipient"], route["pre_holder"]
                if (
                    len(contacts) != 1 or w != holder or {actor, holder} != {u, v}
                    or not holder < rounds[t - 1].knots <= actor
                    or not contacts[0] < rounds[t - 1].distinctions
                    or contacts[0] not in rounds[t].takes.get(actor, ())
                    or x_arms != contacts or y_arms != contacts
                ):
                    raise ValueError(f"cross take lacks a newborn recipient and opposing pre-holder at {s}/{t}")
            elif kind in ("met", "demand"):
                if (
                    w in (u, v) or not x_arms or not y_arms
                    or set(x_arms) != supports[w] & supports[u]
                    or set(y_arms) != supports[w] & supports[v]
                    or set(contacts) != set(x_arms) & set(y_arms)
                ):
                    raise ValueError(f"route arms do not match actual held distinctions at {s}/{t}")
            else:
                raise ValueError(f"unexpected meeting route {kind!r}")
    return sorted(events, key=event_key)


def project_events(rounds, events, law):
    by_round = defaultdict(list)
    for event in events:
        by_round[event["t"]].extend(event["routes"])
    requests = {}
    for t, routes in by_round.items():
        triples = set()
        previous = set()
        old = rounds[t - 1].distinctions
        for route in routes:
            for c, a, b in product(route["contacts"], route["a"], route["b"]):
                triples.add(tuple(sorted((a, b, c))))
                if a < old and b < old:
                    previous.add(tuple(sorted((a, b))))
        if triples:
            requests[t] = (triples, previous)
    if not requests:
        return {}, {}, {"projection_calls": 0, "unique_triples": 0, "unique_prior_pairs": 0}
    if law == "nae":
        backend = NaeProjection
    elif law == "parity":
        backend = ParityProjection
    else:
        raise ValueError(f"unsupported knot law {law}")
    reported = {}
    prior = {}
    with backend() as solver:
        for t, stage in enumerate(rounds[:max(requests) + 1]):
            if t in requests:
                triples, previous = requests[t]
                prior[t] = {pair: solver.project(pair) for pair in sorted(previous)}
            solver.add(stage.holdings)
            if t in requests:
                reported[t] = {triple: solver.project(triple) for triple in sorted(triples)}
        calls = solver.calls
    return reported, prior, {
        "projection_calls": calls,
        "unique_triples": sum(map(len, reported.values())),
        "unique_prior_pairs": sum(map(len, prior.values())),
    }


def rows_with_masks(case, law, rounds, events, reported, prior):
    for event in events:
        s, x, y, t = event_key(event)
        old = rounds[t - 1].distinctions
        for route in sorted(event["routes"], key=route_key):
            key = (case, law, s, x, y, t, *route_key(route))
            for c, a, b in product(route["contacts"], route["a"], route["b"]):
                mask = ordered_mask((a, b, c), reported[t])
                earlier = ordered_mask((a, b), prior[t]) if a < old and b < old else None
                yield (*key, c, a, b, mask, earlier)


def split_arm_rows(case, law, events):
    for event in events:
        s, x, y, t = event_key(event)
        for route in sorted(event["routes"], key=route_key):
            if not route["contacts"]:
                yield (case, law, s, x, y, t, *route_key(route), route["x_arms"], route["y_arms"])


def write_rows(root, folder, rows):
    path = root / folder
    path.mkdir(parents=True, exist_ok=True)
    digest = hashlib.sha256()
    count = 0
    with tempfile.NamedTemporaryFile(dir=path, prefix=".pending-", delete=False) as file:
        pending = Path(file.name)
        try:
            with gzip.GzipFile(filename="", fileobj=file, mode="wb", mtime=0, compresslevel=3) as stream:
                for row in rows:
                    line = json.dumps(row, separators=(",", ":")).encode("ascii") + b"\n"
                    digest.update(line)
                    stream.write(line)
                    count += 1
            file.flush()
            os.fsync(file.fileno())
            sha = digest.hexdigest()
            final = path / f"{sha}.jsonl.gz"
            try:
                os.link(pending, final)
            except FileExistsError:
                pass
        finally:
            pending.unlink(missing_ok=True)
    return {"file": str(final.relative_to(root)), "sha256": sha, "rows": count}


def summarize_masks(source, rounds, counts, by_route, prior_classes, by_prior, constants, annotations, first):
    initial_distinctions = rounds[0].distinctions
    for row in source:
        t, route, c, a, b, mask, earlier = row[5], row[6], row[10], *row[11:]
        category = classify(mask)
        counts[mask] += 1
        origin = "start_held" if c < initial_distinctions else "made"
        by_route[(route, origin)][mask] += 1
        constants.update(category["constant_roles"])
        stage = rounds[t]
        for role, d in zip("abc", (a, b, c), strict=True):
            if stage.holder_counts[d] > 1:
                state = "shared"
            elif d in stage.barred:
                state = "barred_loose"
            else:
                state = "usable_loose"
            annotations[f"{role}_{state}"] += 1
        if earlier == 15:
            state = "both_prior_and_free"
        elif earlier is not None:
            state = "both_prior_but_constrained"
        else:
            old = rounds[t - 1].distinctions
            n_prior = (a < old) + (b < old)
            state = "one_prior" if n_prior else "neither_prior"
        prior_classes[state] += 1
        by_prior[category["category"]][state] += 1
        first.setdefault(category["category"], row)
        yield row


def setup(params):
    global FROZEN, RULES, PRODUCED, SOURCE_ROOT, OUT_ROOT
    for file in ("stage.py", "truth.py"):
        src = hashlib.sha256((HERE / file).read_bytes()).hexdigest()
        if src != params[f"{Path(file).stem}_sha256"]:
            raise ValueError(f"projection source digest mismatch for {file}")
    contract_bytes = (HERE.parent / "contract.json").read_bytes()
    contract_digest = hashlib.sha256(contract_bytes).hexdigest()
    if contract_digest != params["contract_sha256"]:
        raise ValueError("projection contract digest mismatch")
    contract = json.loads(contract_bytes)
    if contract["status"] != "frozen":
        raise ValueError("the projection contract must be frozen")
    path = HERE.parent / contract["cases"]
    data = path.read_bytes()
    case_digest = hashlib.sha256(data).hexdigest()
    if case_digest != contract["inputs"][str(path.relative_to(ROOT))]:
        raise ValueError("projection input does not match the frozen case panel")
    FROZEN = json.loads(data)
    RULES = params.get("rules", "MOST").split(",")
    if len(set(RULES)) != len(RULES) or not set(RULES) <= set(contract["rules"]):
        raise ValueError("requested projection rules are outside the frozen rule panel")
    PRODUCED = {}
    for record in load_results(Path(params["producer"])).values():
        if record["status"] != "ok":
            continue
        result = record["result"]
        if (result["cases_sha256"], result["contract_sha256"]) != (case_digest, contract_digest):
            raise ValueError("producer trajectory belongs to a different frozen experiment")
        key = (result["case"], result["rule"], result["kl"])
        if key in PRODUCED:
            raise ValueError(f"duplicate trajectory result {key}")
        PRODUCED[key] = result
    SOURCE_ROOT = Path(params["producer_artifacts"]).resolve(strict=True)
    OUT_ROOT = Path(params["artifact_dir"]).resolve()


def cases():
    for case in FROZEN:
        for rule in RULES:
            for law in ("nae", "parity"):
                key = (case["id"], rule, law)
                if key in PRODUCED:
                    yield "/".join(key), (case, PRODUCED[key])


def prepare(case, receipt, root):
    if any(case[field] != receipt[field] for field in ("start", "ration", "treatment")):
        raise ValueError(f"growth and frozen case disagree at {case['id']}")
    start = monotonic()
    source = from_jsonl(root, receipt["support_file"], receipt["support_sha256"])
    if any("births" not in row or "barred" not in row for row in source):
        raise ValueError(f"trajectory receipt lacks stage provenance at {case['id']}")
    rounds, supports = parse_rounds(source)
    if receipt["rounds_read"] != len(rounds) - 1:
        raise ValueError(f"trajectory receipt has the wrong terminal round at {case['id']}")
    if receipt["rounds_read"] > case["rounds"] or receipt["knots"] != rounds[-1].knots:
        raise ValueError(f"trajectory terminal disagrees with recorded result or bound at {case['id']}")
    events = verify_events(
        from_jsonl(root, receipt["events_file"], receipt["events_sha256"]),
        rounds, supports, case["splits"],
    )
    if len(events) != receipt["meeting_counts"].get("meetings", 0):
        raise ValueError(f"trajectory receipt has the wrong meeting count at {case['id']}")
    return rounds, events, monotonic() - start


def run(case_id, payload):
    case, receipt = payload
    name, rule, law = receipt["case"], receipt["rule"], receipt["kl"]
    if case_id != f"{name}/{rule}/{law}" or case["id"] != name:
        raise ValueError("trajectory identifiers disagree")
    rounds, events, load_seconds = prepare(case, receipt, SOURCE_ROOT)
    started = monotonic()
    projected, prior, work = project_events(rounds, events, law)
    project_seconds = monotonic() - started
    counts = Counter()
    by_route = defaultdict(Counter)
    prior_classes = Counter()
    by_prior = defaultdict(Counter)
    constants = Counter()
    annotations = Counter()
    first = {}
    triple = write_rows(
        OUT_ROOT, "triples",
        summarize_masks(
            rows_with_masks(name, law, rounds, events, projected, prior), rounds,
            counts, by_route, prior_classes, by_prior, constants, annotations, first,
        ),
    )
    split = write_rows(OUT_ROOT, "split_arms", split_arm_rows(name, law, events))
    categories = Counter()
    for mask, n in counts.items():
        categories[classify(mask)["category"]] += n
    return {
        "case": name, "rule": rule, "kl": law, "rounds_read": len(rounds) - 1,
        "support_sha256": receipt["support_sha256"], "events_sha256": receipt["events_sha256"],
        "events": len(events),
        "events_without_qualified_routes": sum(not event["routes"] for event in events),
        "routes": sum(len(event["routes"]) for event in events),
        "triple": triple,
        "split_arms": split,
        "masks": counts,
        "categories": categories,
        "by_route_and_origin": [
            {"route": kind, "origin": origin, "masks": n}
            for (kind, origin), n in sorted(by_route.items())
        ],
        "constant_roles": constants,
        "literal_annotations": annotations,
        "preexisting_side_cases": prior_classes,
        "category_by_prior_side_case": by_prior,
        "first_by_category": first,
        "load_seconds": load_seconds,
        "project_seconds": project_seconds,
        **work,
    }
