"""Fit the physical payoff, encounter-count and re-paired learners on matched real bites."""

import argparse
from collections import Counter, defaultdict
import csv
from functools import lru_cache
from hashlib import sha256
import json
from pathlib import Path

from exposure import departure_clue, enroll, local
from paired_game import ReversalGame
from reader import PayoffReader
from source_bank import BANK_PATH, LAWS, load_bank, sample_pair


HERE = Path(__file__).resolve().parent
ARMS = ("outcome", "count", "shuffled")
ORDERS = ("primary", "reversed")
FIELDS = (
    "law", "version", "arm", "order", "episode_index", "block_index", "pair_index", "position",
    "seed", "source_key", "replicate", "tape", "turn", "target_holder", "formation", "clue",
    "exception", "even_first", "query_energy_before", "query_energy_after", "actual_paid", "credit_paid",
    "donor_clue", "donor_energy_before", "donor_energy_after", "bite_cost", "turn_costs", "death",
    "eligible_observations", "score_before", "score_after", "actual_route", "public_trace",
)
INPUTS = ("source_bank.py", "paired_game.py", "reader.py", "exposure.py", "training.py",
          "exposure_design.md", "preregistration.md")


def compact(obj):
    return json.dumps(obj, ensure_ascii=True, separators=(",", ":"), sort_keys=True)


def digest(obj):
    return sha256(compact(obj).encode("ascii")).hexdigest()


def write_json(path, obj, *, pretty=False):
    path.write_text(json.dumps(obj, ensure_ascii=True, sort_keys=True,
                               **({"indent": 2} if pretty else {"separators": (",", ":")})) + "\n")


def load_words(path, expected_sha256):
    path = Path(path)
    raw = path.read_bytes()
    key = sha256(raw).hexdigest()
    if key != expected_sha256:
        raise ValueError("Fitted words differ from the released policy hash.")
    record = json.loads(raw)
    if record["schema"] != "feeder-payoff-trained-words-v1":
        raise ValueError("Unknown physical-memory export format.")
    for filename, expected in record["input_sha256"].items():
        candidate = HERE / filename
        if sha256(candidate.read_bytes()).hexdigest() != expected:
            raise ValueError(f"The original training input {filename} differs.")
    return record, key


def run_probe(world, version, pair, cue, *, reader=None, override=None):
    chosen = pair[cue]
    game = ReversalGame(world, tape=chosen["tape"], version=version,
                        training_exception=(pair["holder"], pair["exception"]))
    if reader is not None:
        reader.begin_episode(training=True)
    full_trace, actual_route = [], []
    prior_clue = None
    observed = []
    for turn in range(1, pair["turn"] + 1):
        obs = game.observe()
        actual_route.append(game.snapshot()["holder"])
        foreground = obs.feeder and len(obs.slots) == 3 and obs.previous == "move" and prior_clue is not None
        if foreground:
            observed.append(prior_clue)
        requested = int(turn == pair["turn"])
        issued = reader.decide(obs, probe_bit=requested) if reader is not None else requested
        if requested:
            snap = game.snapshot()
            assert actual_route == chosen["route"] and chosen["current"] == local(obs)
            assert snap["holder"] == pair["holder"] and snap["formation"] == pair["formation"]
            assert pair["holder"] in snap["available"] and snap["meals"] == 0 and observed == [cue]
        assert issued == requested
        tr = game.step(issued)
        slot, after = tr.outgoing_slot, tr.energy_after
        actual = bool(issued and after >= obs.energy)
        credit = actual if override is None else bool(override)
        if reader is not None:
            old = reader.score
            info = reader.after_turn(obs, issued, slot, after, credit_override=override if requested else None)
            if requested:
                assert info["eligible"] and info["route_cue"] == cue
                assert bool(info["actual_paid"]) == actual and bool(info["credit_paid"]) == credit
                assert old == info["score_before"] and reader.score == info["score_after"]
                delta = (1 if cue == "A" else -1) * int(credit)
                assert reader.score == old + delta
            else:
                assert reader.score == old
        step = [*local(obs), int(issued), slot, after]
        full_trace.append(step)
        if requested:
            event = game.last_event
            assert event["consumed"] == actual and event["eligible"] and event["food_before"]
            assert event["denied"] == (not actual)
            assert event["approach"] == (0 if cue == "A" else 1)
            assert after == min(10, obs.energy - 1 + 4 * actual)
            return {"paid": int(actual), "before": obs.energy, "after": after, "death": int(game.done),
                    "public": full_trace, "route": actual_route, "observed": observed}
        assert step == chosen["prefix"][turn - 1]
        assert not game.done and slot is not None
        prior_clue = departure_clue(obs, slot)
    raise AssertionError("A probe must reach its scheduled bite.")


def chronological(selected, order):
    for p in selected:
        a_first = p["A_first"] if order == "primary" else not p["A_first"]
        for cue in (("A", "B") if a_first else ("B", "A")):
            yield p, cue, a_first


def reference_receipts(law, selected, worlds):
    paid = {}
    for ver in (0, 1):
        for p in selected:
            for cue in ("A", "B"):
                r = run_probe(worlds(p["seed"])[law], ver, p, cue)
                paid[ver, p["pair_index"], cue] = r
            assert sum(paid[ver, p["pair_index"], c]["paid"] for c in ("A","B")) == 1
    for p in selected:
        for cue in ("A","B"):
            r0, r1 = (paid[v,p["pair_index"],cue] for v in (0,1))
            assert r0["paid"] != r1["paid"] and r0["public"][-1][:-1] == r1["public"][-1][:-1]
            assert r0["public"][:-1] == r1["public"][:-1]
    return paid


def fit(law, ver, arm, order, selected, worlds, real, csv_writer):
    reader = PayoffReader(law)
    rows = []
    for idx, (p, cue, a_first) in enumerate(chronological(selected, order)):
        j = p["pair_index"]
        donor_cue = None
        override = None
        if arm == "count":
            override = 1
        elif arm == "shuffled":
            desired = int(cue == p["shuffled_payer"])
            donor_cue = next(c for c in ("A","B") if real[ver,j,c]["paid"] == desired)
            override = real[ver,j,donor_cue]["paid"]
        source = worlds(p["seed"])[law]
        before_score = reader.score
        trial = run_probe(source, ver, p, cue, reader=reader, override=override)
        assert real[ver,j,cue] == trial
        donor = None if donor_cue is None else real[ver,j,donor_cue]
        if donor is not None:
            assert donor["before"] == trial["before"] and donor["paid"] == override
        credited = trial["paid"] if override is None else override
        rows.append({"clue": cue, "credit": credited, "actual": trial["paid"],
                     "public": trial["public"], "route": trial["route"], "donor": donor_cue,
                     "block": p["block"], "before": trial["before"], "after": trial["after"]})
        csv_writer.writerow({
            "law": law, "version": ver, "arm": arm, "order": order, "episode_index": idx,
            "block_index": p["block"], "position": p["position"], "pair_index": j, "seed": p["seed"],
            "source_key": p["source_key"], "replicate": p[cue]["replicate"], "tape": p[cue]["tape"],
            "turn": p["turn"], "formation": p["formation"], "target_holder": p["holder"], "clue": cue,
            "exception": int(p["exception"]), "even_first": int(a_first), "query_energy_before": trial["before"],
            "query_energy_after": trial["after"], "actual_paid": trial["paid"], "credit_paid": credited,
            "donor_clue": donor_cue, "donor_energy_before": None if donor is None else donor["before"],
            "donor_energy_after": None if donor is None else donor["after"], "turn_costs": p["turn"],
            "bite_cost": 1, "death": trial["death"], "eligible_observations": len(trial["observed"]),
            "score_before": before_score, "score_after": reader.score,
            "actual_route": compact(trial["route"]), "public_trace": compact(trial["public"]),
        })
    return rows, reader.export_memory()


def audit_series(rows, word, arm, ver):
    margin = {cue: Counter() for cue in ("A","B")}
    for r in rows:
        m = margin[r["clue"]]
        m["attempts"] += 1
        m["paid"] += r["actual"]
        m["denied"] += 1-r["actual"]
        m["credited"] += r["credit"]
        m["death_at_query"] += r["after"] == 0
        m["total_query_energy_before"] += r["before"]
        m["total_query_energy_after"] += r["after"]
    for k in range(0, len(rows), 8):
        block = rows[k:k+8]
        assert len(block) == 8 and len({r["block"] for r in block}) == 1
        assert Counter(r["clue"] for r in block) == {"A":4,"B":4}
        assert sum(r["actual"] for r in block) == 4
        expected_a = 3 if ver == 0 else 1
        assert sum(r["actual"] for r in block if r["clue"] == "A") == expected_a
        credited = [sum(r["credit"] for r in block if r["clue"] == cue) for cue in ("A","B")]
        assert credited == ([4,4] if arm == "count" else [2,2] if arm == "shuffled" else [expected_a,4-expected_a])
        if arm == "shuffled":
            assert all({r["donor"] for r in block[i:i+2]} == {"A","B"} for i in range(0,8,2))
    assert word["score"] == margin["A"]["credited"] - margin["B"]["credited"]
    return {
        "episodes": len(rows), "complete_blocks": len(rows)//8, "margins": {c:dict(x) for c,x in margin.items()},
        "clue_sha256": digest([r["clue"] for r in rows]),
        "paid_sha256": digest([r["actual"] for r in rows]),
        "all_turn_energy_sha256": digest([[[v[1],v[-1]] for v in r["public"]] for r in rows]),
        "query_pre_post_sha256": digest([[r["before"],r["after"]] for r in rows]),
        "prebite_public_sha256": digest([[step[:-1] for step in r["public"]] for r in rows]),
        "actual_physical_routes_sha256": digest([r["route"] for r in rows]),
        "ordered_clue_credit_sha256": digest([[r["clue"],r["credit"]] for r in rows]),
        "physical_score": word["score"], "first_paid": rows[0]["actual"] if rows else None,
        "last_paid": rows[-1]["actual"] if rows else None,
    }


def train(out_dir, *, bank_path=BANK_PATH):
    folds, bank_hash = load_bank(bank_path)
    starts = folds["train"]
    by_seed = {s.seed:s for s in starts}
    @lru_cache(maxsize=96)
    def worlds(seed):
        return sample_pair(by_seed[seed],"train")

    path = out_dir / "training_receipts.csv"
    out_dir.mkdir(parents=True, exist_ok=True)
    opportunity = enroll(starts)
    write_json(out_dir / "exposure_results.json", {
        "schema":"feeder-exposures-v1", "source_bank_sha256":bank_hash,
        "mask_convention":"Integer masks use bit zero for turn 2 and bit four for turn 6; array index is movement replicate.",
        "per_law":opportunity})
    primary, alternative, audit = {}, {}, {}
    with path.open("w", newline="") as f:
        cw = csv.DictWriter(f, fieldnames=FIELDS)
        cw.writeheader()
        for law in LAWS:
            primary[law], alternative[law], audit[law] = {}, {}, {}
            selected = opportunity[law]["selected"]
            actual = reference_receipts(law, selected, worlds)
            for order in ORDERS:
                audit[law][order] = {}
                target = primary[law] if order == "primary" else alternative[law]
                for ver in (0,1):
                    v = str(ver)
                    target[v], audit[law][order][v] = {}, {}
                    for arm in ARMS:
                        rows, word = fit(law,ver,arm,order,selected,worlds,actual,cw)
                        target[v][arm] = word
                        audit[law][order][v][arm] = audit_series(rows,word,arm,ver)
            for order, other in (("primary","reversed"),("reversed","primary")):
                for ver in ("0","1"):
                    opposite = str(1-int(ver))
                    for arm in ARMS:
                        same = audit[law][order][ver][arm]
                        changed = audit[law][order][opposite][arm]
                        crossed = audit[law][other][opposite][arm]
                        assert all(same[k] == changed[k] for k in ("clue_sha256","prebite_public_sha256","actual_physical_routes_sha256"))
                        assert all(same[k] == crossed[k] for k in ("paid_sha256","all_turn_energy_sha256","query_pre_post_sha256"))
                        assert primary[law][ver][arm] == alternative[law][ver][arm]
                        if arm != "outcome":
                            assert same["ordered_clue_credit_sha256"] == changed["ordered_clue_credit_sha256"]
    files = {n:sha256((HERE/n).read_bytes()).hexdigest() for n in INPUTS}
    files["source_bank.json"] = bank_hash
    registry = {"schema":"feeder-payoff-trained-words-v1","policies":primary,"alternate_order":alternative,
                "input_sha256":files, "scope":"FEEDER-PAYOFF-REVERSAL-20261121-001"}
    write_json(out_dir / "learned_words.json", registry, pretty=True)
    sealed = sha256((out_dir/"learned_words.json").read_bytes()).hexdigest()
    write_json(out_dir / "training_replay_metrics.json", {"schema":"feeder-experienced-receipts-v1",
               "learned_words_sha256":sealed, "source_bank_sha256":bank_hash,"per_law":audit,
               "receipt_csv_sha256":sha256(path.read_bytes()).hexdigest(),
               "training_order_checks":["identical full pre-bite observations and actual routes at fixed order across versions",
                                         "identical entire energy and paid chronology across reversal of order and version",
                                         "identical primary and reversed-order fitted physical words"]},pretty=True)
    print(compact({"registry_sha256":sealed,"per_law":{l:{v:{arm:word["score"] for arm,word in arms.items()}
                     for v,arms in policies.items()} for l,policies in primary.items()},
                   "selected_pairs":{l:opportunity[l]["counts"]["selected_pairs"] for l in LAWS}}))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output",default=HERE,type=Path)
    parser.add_argument("--bank",default=BANK_PATH,type=Path)
    opts = parser.parse_args()
    train(opts.output, bank_path=opts.bank)
