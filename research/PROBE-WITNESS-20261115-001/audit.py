"""Independent fixed-probe certificates and physical/cost replay.

The witness checker reconstructs original raw assignments and reads the two
public columns directly.  It does not trust a producer's sampled signatures.
Three different signatures exclude a one-bit summary of THIS triple; they
neither establish a global minimum nor exclude a two-bit summary.
"""

from __future__ import annotations

from copy import deepcopy
from collections import Counter, defaultdict
from datetime import datetime
from functools import lru_cache
import gzip
import hashlib
import importlib.util
import json
from pathlib import Path
from statistics import median


ROOT = Path(__file__).resolve().parents[2]
TICKET = "PROBE-WITNESS-20261115-001"
DEFAULT = ROOT / "artifacts" / TICKET / (TICKET + "-E001_fixed_probes")
ORACLE_PATH = ROOT / "research/FOLD-TWO-OUTPUT-20261115-001/audit.py"
ORACLE_SHA256 = "adbe5f223102b41091ee0a13367288a1e13929fbed6d8a05564bec25c568db1d"
PRIOR_PATH = ROOT / "research/TRIPLE-ORDER-20261115-001/audit.py"
PRIOR_SHA256 = "504a6c0ff92a2a70a37b3691d2425ee3d9fab1c080b0cd8078b3444e1b182b89"


@lru_cache(maxsize=1)
def oracle():
    if hashlib.sha256(ORACLE_PATH.read_bytes()).hexdigest() != ORACLE_SHA256:
        raise ValueError("terminal independent oracle changed")
    spec = importlib.util.spec_from_file_location("probe_witness_terminal_oracle", ORACLE_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@lru_cache(maxsize=1)
def prior():
    if hashlib.sha256(PRIOR_PATH.read_bytes()).hexdigest() != PRIOR_SHA256:
        raise ValueError("terminal independent split/response oracle changed")
    spec = importlib.util.spec_from_file_location("probe_witness_terminal_split_oracle", PRIOR_PATH)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def original_input(n, group, local, outside_value):
    outside = tuple(i for i in range(n) if i not in group)
    return oracle().scatter(local, group) | oracle().scatter(outside_value, outside)


class RawObservations:
    """Audit-only scalar cache; paired rewires cannot reuse changed-port bits."""

    def __init__(self):
        self.bits = {}
        self.requests = self.hits = self.fresh_bits = 0

    def read_pair(self, n, targets, raw):
        values = []
        for truth in targets:
            self.requests += 1
            key = n, truth, raw
            if key in self.bits:
                self.hits += 1
            else:
                self.bits[key] = (truth >> raw) & 1
                self.fresh_bits += 1
            values.append(self.bits[key])
        return tuple(values)


def signatures(n, targets, group, contexts, locals=range(8), observations=None):
    """Contexts are compact outside assignments, shared by EVERY local state."""
    cache = RawObservations() if observations is None else observations
    return tuple(tuple(cache.read_pair(n, targets, original_input(n, group, local, context))
                       for context in contexts) for local in locals)


def make_witness(n, targets, group, contexts, observations=None):
    """First three distinct signatures in canonical local-state order, or None."""
    require = oracle().require
    require(1 <= len(contexts) <= 2, "one or two fixed outside contexts required")
    cache = RawObservations() if observations is None else observations
    states, values, seen = [], [], set()
    for local in range(8):
        signature = signatures(n, targets, group, contexts, (local,), cache)[0]
        if signature not in seen:
            states.append(local)
            values.append(signature)
            seen.add(signature)
            if len(seen) == 3:
                return dict(group=list(group), contexts=list(contexts), local_states=states,
                            values=[[list(pair) for pair in row] for row in values])
    return None


def verify_witness(n, targets, witness):
    require = oracle().require
    group = witness.get("group")
    require(isinstance(group, (list, tuple)) and len(group) == 3 and
            all(type(i) is int for i in group) and list(group) == sorted(set(group)), "malformed witness group")
    group = tuple(group)
    facts = oracle().characterize(n, tuple(targets))
    require(group in dict(facts["ranks"]), "ineligible witness group")
    contexts, states = witness.get("contexts"), witness.get("local_states")
    require(isinstance(contexts, (list, tuple)) and 1 <= len(contexts) <= 2 and
            all(type(v) is int and 0 <= v < 1 << (n - 3) for v in contexts), "fixed outside contexts")
    require(isinstance(states, (list, tuple)) and len(states) >= 3 and len(states) == len(set(states)) and
            all(type(v) is int and 0 <= v < 8 for v in states), "local witness states")
    expected = signatures(n, tuple(targets), group, tuple(contexts), tuple(states))
    require(oracle().canonical(witness.get("values")) == oracle().canonical(expected), "witness disagrees with original raw outputs")
    require(len(set(expected)) >= 3, "witness does not exclude one bit")
    return dict(valid=True, triple=group, sampled_signatures=len(set(expected)),
                local_lower_bound_bits=(len(set(expected)) - 1).bit_length(),
                raw_inputs=[[original_input(n, group, local, c) for c in contexts] for local in states])


def compact_record(n, targets, record):
    """Independent interpreter for [mask,a,b,c,settings_mask,scheme]."""
    require = oracle().require
    require(isinstance(record, (list, tuple)) and len(record) == 6 and all(type(v) is int for v in record),
            "compact witness must contain six integers")
    mask, a, b, c, settings, scheme = record
    require(mask > 0 and mask < 1 << n and mask.bit_count() == 3, "compact group mask")
    require(settings in (1, 2, 3) and 0 <= scheme < 4, "compact probe settings")
    group = tuple(j for j in range(n) if mask & (1 << j))
    outside = tuple(j for j in range(n) if not mask & (1 << j))
    pattern = 0 if scheme == 0 else sum(1 << j for j in range(n) if (j // scheme) % 2 == 0)
    first = pattern & (((1 << n) - 1) ^ mask)
    second = first ^ (((1 << n) - 1) ^ mask)
    raw_contexts = ([first] if settings == 1 else [second] if settings == 2 else [first, second])
    contexts = [sum(((raw >> j) & 1) << k for k, j in enumerate(outside)) for raw in raw_contexts]
    require(len({a, b, c}) == 3 and all(0 <= v < 8 for v in (a, b, c)), "compact local states")
    values = signatures(n, tuple(targets), group, tuple(contexts), (a, b, c))
    receipt = verify_witness(n, targets, dict(group=group, contexts=contexts, local_states=(a, b, c), values=values))
    receipt.update(mask=mask, settings=settings, scheme=scheme)
    return receipt


@lru_cache(maxsize=None)
def validated_record(n, targets, record):
    return compact_record(n, targets, record)


@lru_cache(maxsize=None)
def probe_schedule(n, targets, group, scheme):
    """Literal point-query discovery, independent of packed producer helpers."""
    mask = sum(1 << j for j in group)
    pattern = 0 if scheme == 0 else sum(1 << j for j in range(n) if (j // scheme) % 2 == 0)
    first = pattern & (((1 << n) - 1) ^ mask)
    outside = (first, first ^ (((1 << n) - 1) ^ mask))
    order = tuple((0, j) for j in range(3)) + tuple((1, j) for j in range(3)) + tuple(
        (side, j) for j in range(3, 8) for side in (0, 1))
    left, right, combined = {}, {}, {}
    first_values, reads = {}, []
    for side, local in order:
        raw = outside[side] | oracle().scatter(local, group)
        reads.append(raw)
        value = tuple((truth >> raw) & 1 for truth in targets)
        if side == 0:
            first_values[local] = value
            left.setdefault(value, local)
            if len(left) == 3:
                states, settings = tuple(left.values()), 1
            else:
                continue
        else:
            right.setdefault(value, local)
            if len(right) == 3:
                states, settings = tuple(right.values()), 2
            else:
                combined.setdefault((first_values[local], value), local)
                if len(combined) == 3:
                    states, settings = tuple(combined.values()), 3
                else:
                    continue
        record = (mask, *states, settings, scheme)
        return tuple(reads), record
    return tuple(reads), None


def oracle_choices(n, targets):
    """Reproduce the deliberately nonoptimal, free calibration advice."""
    require = oracle().require
    choices = {"oracle-menu": {}, **{f"skip-{s}": {} for s in range(4)}}
    scores = {}
    for group, _ in oracle().characterize(n, tuple(targets))["ranks"]:
        mask = sum(1 << j for j in group)
        values = []
        for scheme in range(4):
            reads, record = probe_schedule(n, tuple(targets), group, scheme)
            score = None if record is None else (len(reads)+(6 if record[4] == 3 else 3), len(reads), 2 if record[4] == 3 else 1)
            values.append(score)
            choices[f"skip-{scheme}"][mask] = scheme if score is not None else -1
            if record is not None:
                require(oracle().partition(n, tuple(targets), group)[0] > 2, "probe falsely excludes a one-bit cut")
        scores[mask] = tuple(values)
        best = min(((score, scheme) for scheme, score in enumerate(values) if score is not None), default=(None, -1))
        choices["oracle-menu"][mask] = best[1]
    return choices, scores


class VerifierReplay:
    """Reconstruct independent evidence reads, exact fallbacks and warm geometry."""

    def __init__(self, n):
        self.n = n
        self.geometry = set()

    def check(self, targets, result, certificate, base_certificate):
        require = oracle().require
        n, targets = self.n, tuple(targets)
        records = result.get("witnesses", ())
        require(isinstance(records, (list, tuple)), "witness record sequence")
        certified, rows = set(), set()
        requests = single = double = 0
        needed = set()
        for record in records:
            evidence = validated_record(n, targets, tuple(record))
            group = tuple(evidence["triple"])
            require(group not in certified, "duplicate witness cut")
            certified.add(group)
            needed.add(group)
            queried = [r for entry in evidence["raw_inputs"] for r in entry]
            requests += len(queried)
            rows.update(queried)
            single += record[4] != 3
            double += record[4] == 3
        group = tuple(sorted(result["triple"]))
        facts = oracle().characterize(n, targets)
        needed.add(group)
        packed_columns, exact_groups, effective, alternatives = 8, 1, 0, 0
        width = result["width"]
        if width > 1:
            for other, _ in facts["ranks"]:
                if other == group:
                    continue
                needed.add(other)
                if width == 2 and other in certified:
                    effective += 1
                    continue
                alternatives += 1
                exact_groups += 1
                seen = set()
                bound = 1 << (width - 1)
                for response in prior().dense_responses(n, targets, other):
                    packed_columns += 1
                    seen.add(response)
                    if len(seen) > bound:
                        break
        extra = dict(included_witnesses=len(records), accepted_witnesses=len(records), effective_witnesses=effective,
                     exact_alternatives=alternatives, verifier_row_requests=requests, verifier_row_reads=len(rows),
                     verifier_row_cache_hits=requests-len(rows), verifier_output_bits_read=2*len(rows),
                     witnesses_one_setting=single, witnesses_two_settings=double, chosen_exact_classifications=1,
                     packed_residual_columns=packed_columns, packed_residual_shifts=packed_columns-exact_groups,
                     packed_residual_masks=packed_columns, geometry_builds=len(needed-self.geometry),
                     classified_groups=1 if width == 1 else facts["eligible_count"])
        self.geometry.update(needed)
        require(certificate == {**base_certificate, **extra}, "paid evidence/fallback verifier receipt")
        return extra


PROBE_FIELDS = ("probe_candidates", "probe_witness_hits", "probe_unresolved_fallback", "resolved_by_witness",
                "attempted_by_exact", "exact_bound_rejections", "probe_disabled_groups", "probe_skipped_for_wider_bound",
                "probe_skipped_by_advice", "probe_row_requests", "probe_row_unique", "probe_row_reuses",
                "probe_output_bit_reads", "probe_signature_tests", "witness_single_hits", "witness_double_hits",
                "witnesses_discarded_after_width1", "witness_records_returned", "witness_single_returned",
                "witness_double_returned", "witness_row_references", "witness_distinct_rows", "witness_single_distinct_rows",
                "witness_double_distinct_rows", "probe_advice_calls", "probe_interface_cache_hits", "witness_cache_records_reused")


def replay_discovery(n, targets, result, enabled, scheme, advice=None):
    """Replay every proposed triple, sampled row, fallback and bound update."""
    require = oracle().require
    facts = oracle().characterize(n, tuple(targets))
    work = dict.fromkeys(PROBE_FIELDS, 0)
    work["probe_advice_calls"] = int(advice is not None)
    observed, witnesses = set(), []
    bound, best = 8, None
    trials = failures = incumbents = exact_columns = unpacked = 0
    schedule_sides = (0,0,0,1,1,1,0,1,0,1,0,1,0,1,0,1)
    for group, full_count in facts["ranks"]:
        trials += 1
        record = None
        if not enabled:
            work["probe_disabled_groups"] += 1
        elif bound > 2:
            work["probe_skipped_for_wider_bound"] += 1
        else:
            raw_mask = sum(1 << j for j in group)
            selected = scheme if advice is None else advice.get(raw_mask, scheme)
            if selected == -1:
                work["probe_skipped_by_advice"] += 1
            else:
                work["probe_candidates"] += 1
                reads, record = probe_schedule(n, tuple(targets), group, selected)
                work["probe_row_requests"] += len(reads)
                observed.update(reads)
                work["probe_signature_tests"] += len(reads)+sum(schedule_sides[:len(reads)])-int(record is not None and record[4]==2)
                if record is not None:
                    require(full_count > 2, "unsound probe discovery")
                    witnesses.append(record)
                    work["probe_witness_hits"] += 1
                    work["resolved_by_witness"] += 1
                    work["witness_double_hits" if record[4] == 3 else "witness_single_hits"] += 1
                    failures += 1
                    continue
                work["probe_unresolved_fallback"] += 1
        work["attempted_by_exact"] += 1
        seen = set()
        for response in prior().dense_responses(n, tuple(targets), group):
            seen.add(response)
            exact_columns += 1
            if len(seen) > bound:
                break
        if len(seen) > bound:
            work["exact_bound_rejections"] += 1
            failures += 1
            continue
        require(len(seen) == full_count, "truncated accepted exact code")
        unpacked += full_count
        incumbents += 1
        best = group, full_count, (full_count - 1).bit_length()
        if best[2] == 1:
            work["witnesses_discarded_after_width1"] = len(witnesses)
            witnesses.clear()
            break
        bound = 1 << (best[2] - 1)
    require(best is not None and tuple(result["triple"]) == best[0] and result["class_count"] == best[1] and
            result["width"] == best[2], "probe priority or selected exact cut changed")
    require(result["witnesses"] == [list(w) for w in witnesses], "returned/discarded probe certificates")
    work["probe_row_unique"] = len(observed)
    work["probe_row_reuses"] = work["probe_row_requests"] - len(observed)
    work["probe_output_bit_reads"] = 2 * len(observed)
    single, double = set(), set()
    for record in witnesses:
        evidence = validated_record(n, tuple(targets), tuple(record))
        rows = [r for entry in evidence["raw_inputs"] for r in entry]
        work["witness_row_references"] += len(rows)
        if record[4] == 3:
            work["witness_double_returned"] += 1
            double.update(rows)
        else:
            work["witness_single_returned"] += 1
            single.update(rows)
    work["witness_records_returned"] = len(witnesses)
    work["witness_distinct_rows"] = len(single | double)
    work["witness_single_distinct_rows"] = len(single)
    work["witness_double_distinct_rows"] = len(double)
    expected = dict(tasks=1,input_rows_received=2<<n,eligible_group_count=facts["eligible_count"],support_bit_tests=2*n,
                    group_cache_hits=0,group_trials=trials,groups_requested=trials,group_failures=failures,
                    group_incumbents=incumbents,group_bound_rejections=failures,joint_tables_joined=1,
                    residual_joint_rows=exact_columns,residual_packed_shifts=exact_columns-work["attempted_by_exact"],
                    residual_packed_masks=exact_columns,residual_row_equivalents=exact_columns*(1 << (n-2)),
                    joint_class_lookups=exact_columns,residual_pairs_unpacked=unpacked,**work)
    for key,value in expected.items():
        require(result["work"][key] == value, "probe/exact accounting " + key)
    require(result["work"]["group_layout_builds"]+result["work"]["group_layout_hits"] == trials+1, "probe group geometry requests")
    require(result["probe_enabled"] == enabled and result["probe_scheme"] == scheme and
            result["calibration_advice_used"] == (advice is not None), "probe/advice execution mode")
    require(result["work"]["physical_output_comparisons"] == 2 and result["work"]["physical_output_bits_checked"] == 2 << n,
            "both physical outputs checked")
    require(result["work"]["NAND_gates_appended"] == result["work"]["physical_reachable_gates"]+
            result["work"]["physical_pruned_gates"], "probe physical dead-gate accounting")
    return work


HELD = ("zero-one", "primitive", "four-cofactor", "matched-exact", "full-recheck", "reference", "lexical", "primitive-new-check")
CALIBRATION = ("zero-one", "alternating", "blocks-two", "blocks-three", "oracle-menu", "skip-0", "skip-1", "skip-2", "skip-3", "matched-exact", "primitive")
CONSTANT = CALIBRATION[:4]
PRIMITIVES = ("primitive", "four-cofactor", "matched-exact", "reference", "lexical", "primitive-new-check")
OLD_CHECK = ("primitive", "reference", "four-cofactor", "lexical", "full-recheck")
OLD_ENGINE = ("primitive", "primitive-new-check", "reference", "four-cofactor", "lexical")


def read(path):
    return json.loads(Path(path).read_bytes())


def check_bindings(out):
    design, data = read(out/"design.json"), read(out/"data-bound.json")
    for name,value in design["sources"].items():
        oracle().require(oracle().digest(ROOT/name)==value, "changed fixed source " + name)
    for name,value in data.items():
        if name.endswith(".json"):
            oracle().require(oracle().digest(out/name)==value, "changed fixed data " + name)
    oracle().require(datetime.fromisoformat(design["frozen_utc"]) < datetime.fromisoformat(data["opened_utc"]) <=
                     datetime.fromisoformat(data["sealed_utc"]), "source/data freeze chronology")
    return design,data


def check_panels(out):
    panels={p:read(out/(p+".json")) for p in ("calibration","held")}
    grades={p:read(out/(p+"-grades.json")) for p in panels}
    reports={}
    for panel,side,domain in (("calibration","train",0),("held","test",1)):
        reports[panel]=prior().check_panel(side,panels[panel],grades[panel])
        oracle().require(all(int(g[k][:2],16)%4==domain for g in grades[panel].values() for k in ("structure","truth_family")),
                         "four-way structural domain")
    for field in ("raw_families","consumer_families"):
        oracle().require(not set(reports["calibration"][field])&set(reports["held"][field]), "cross-panel domain leakage")
    previous_raw,previous_structures=set(),set()
    order=ROOT/"artifacts/TRIPLE-ORDER-20261115-001/TRIPLE-ORDER-20261115-001-E001_rank_triples"
    fold=ROOT/"artifacts/FOLD-TWO-OUTPUT-20261115-001/FOLD-TWO-OUTPUT-20261115-001-E001_joint_tables"
    old_panels=[(read(order/(p+".json")),read(order/(p+"-grades.json"))) for p in ("train","held")]
    fold_grades=read(fold/"grades.json")
    old_panels += [(read(fold/(p+".json")),fold_grades[p]) for p in ("primary","sensitivity")]
    for tasks,key in old_panels:
        for t in tasks:
            if t["n"] not in (7,8,9):continue
            previous_raw.add(prior().raw_family(t["n"],tuple(t["outputs"])))
            g=key[t["id"]]
            if g["kind"]=="shared":previous_structures.add(prior().consumer_family(t["n"],g["logical_consumers"]))
    for report in reports.values():
        oracle().require(not set(report["raw_families"])&previous_raw and not set(report["consumer_families"])&previous_structures,
                         "predecessor fixture reused")
    return panels,grades,reports


def count_row(task,grade,raw,certificate):
    res=raw["result"] or {};cert=certificate or {};w=res.get("work",{});records=res.get("witnesses",[])
    exact=raw["failure"] is None and cert.get("exact",False)
    c=Counter(tasks=1,exact=int(exact),width1=int(exact and cert["width"]==1),width2=int(exact and cert["width"]==2),
              rows=cert.get("verified_assignments",0),output_bits=cert.get("verified_output_bits",0),gates=cert.get("gates",0),
              eligible=len(oracle().characterize(task["n"],tuple(task["outputs"]))["ranks"]),returned_witnesses=len(records),
              single=sum(r[4]!=3 for r in records),double=sum(r[4]==3 for r in records),
              exact_search=w.get("attempted_by_exact",w.get("group_trials",w.get("triple_trials",0))),
              effective=cert.get("effective_witnesses",0),accepted=cert.get("accepted_witnesses",0),
              exact_alternatives=cert.get("exact_alternatives",cert.get("alternatives_checked",0)),
              verifier_requests=cert.get("verifier_row_requests",0),verifier_reads=cert.get("verifier_row_reads",0),
              verifier_reuse=cert.get("verifier_row_cache_hits",0))
    for record in records:c["scheme_"+str(record[5])]+=1
    for name in ("probe_row_requests","probe_row_unique","probe_row_reuses","probe_output_bit_reads","probe_candidates",
                 "probe_witness_hits","probe_unresolved_fallback","resolved_by_witness","exact_bound_rejections",
                 "witnesses_discarded_after_width1","witness_row_references","witness_distinct_rows"):
        c[name]=w.get(name,0)
    for name in ("cpu_ns","wall_ns","init_cpu_ns","synth_cpu_ns","verify_cpu_ns","verify_wall_ns","serialization_cpu_ns","return_bytes"):
        c[name]=oracle().integer(raw[name],name)
    oracle().require(c["cpu_ns"]>=sum(c[k] for k in ("init_cpu_ns","synth_cpu_ns","verify_cpu_ns","serialization_cpu_ns")),
                     "paid row omits a measured component")
    return c


def compare(x,y):
    return dict(cpu_gap_ns=x["paid_cpu_ns"]-y["paid_cpu_ns"],cpu_ratio=x["paid_cpu_ns"]/y["paid_cpu_ns"],
                wall_gap_ns=x["paid_wall_ns"]-y["paid_wall_ns"],
                paired_cpu_wins=sum(a<b for a,b in zip(x["cpu_repeats_ns"],y["cpu_repeats_ns"],strict=True)))


def wins(x,y):
    c=compare(x,y)
    return c["cpu_gap_ns"]<0 and c["paired_cpu_wins"]>=7


def coverage(tasks,grades):
    result=defaultdict(Counter)
    for task in tasks:
        _,scores=oracle_choices(task["n"],tuple(task["outputs"]))
        for group,count in oracle().characterize(task["n"],tuple(task["outputs"]))["ranks"]:
            available=scores[sum(1<<i for i in group)]
            for tag in ("all",grades[task["id"]]["kind"]):
                row=result[tag];row["groups"]+=1;row["impossible_one"]+=count>2
                row["scheme0"]+=available[0] is not None;row["any_scheme"]+=any(v is not None for v in available)
                for i,v in enumerate(available):row["available_"+str(i)]+=v is not None
    return dict(result)


def audit(out):
    require,digest,canonical=oracle().require,oracle().digest,oracle().canonical
    design,data=check_bindings(out)
    panels,grades,split=check_panels(out)
    advice_files={arm:read(out/(arm+".json")) for arm in ("oracle-menu","skip-0","skip-1","skip-2","skip-3")}
    hints={arm:[] for arm in advice_files}
    for index,task in enumerate(panels["calibration"]):
        expected,_=oracle_choices(task["n"],tuple(task["outputs"]))
        for arm,rows in advice_files.items():
            row={int(k):v for k,v in rows[index].items()}
            require(row==expected[arm], "clairvoyant advice mismatch")
            hints[arm].append(row)
    counts=defaultdict(dict);groups=defaultdict(list);work_runs=defaultdict(list);fingerprints={}
    failures=[];totals=Counter();stream_hashes={};physical_cache={};logical_choices={}
    events=[json.loads(l) for l in (out/"results.jsonl").read_text().splitlines()]
    for event in events:
        require(event["status"]=="ok", "unresolved process failure")
        s=event["result"];panel,arm,rep=s["panel"],s["arm"],s["repeat"];key=panel,arm
        require(panel in panels and arm in (HELD if panel=="held" else CALIBRATION) and 0<=rep<8 and rep not in counts[key], "unexpected/duplicate case")
        require(s["cpu"]==design["cpu"] and digest(out/s["file"])==s["sha256"], "worker CPU or stream hash")
        stream_hashes[s["file"]]=s["sha256"]
        with gzip.open(out/s["file"],"rt") as f:rows=[json.loads(l) for l in f]
        require(len(rows)==len(panels[panel])==s["tasks"], "incomplete deployed stream")
        total,ops=Counter(),Counter();by=defaultdict(Counter);identity=[];choices=[];verifiers={};ordered={}
        for index,(task,raw) in enumerate(zip(panels[panel],rows,strict=True)):
            require(task["id"]==raw["id"], "public task sequence changed")
            n,targets,result=task["n"],tuple(task["outputs"]),raw["result"]
            cert=None
            if raw["failure"] is None:
                pkey=canonical([n,targets,{k:result[k] for k in prior().PHYSICAL_FIELDS if k in result}])
                if pkey not in physical_cache:
                    physical_cache[pkey]=oracle().verify_result(n,targets,result)
                    totals.update(unique_physical_programs=1,executed_scalar_rows=1<<n,executed_scalar_output_bits=2<<n,
                                  executed_scalar_NANDs=physical_cache[pkey][1]["scalar_NAND_evaluations"])
                base,physical=physical_cache[pkey]
                for record in result.get("witnesses",[]):validated_record(n,targets,tuple(record))
                if arm in OLD_CHECK:
                    require(raw["certificate"]==base, "archived physical checker receipt")
                    cert=base
                else:
                    if n not in verifiers:verifiers[n]=VerifierReplay(n)
                    extra=verifiers[n].check(targets,result,raw["certificate"],base)
                    cert={**base,**extra}
                if arm not in OLD_ENGINE:
                    advice=hints[arm][index] if arm in hints else None
                    scheme=CONSTANT.index(arm) if arm in CONSTANT else 0
                    replay_discovery(n,targets,result,arm!="matched-exact",scheme,advice)
                elif arm in ("lexical","four-cofactor"):
                    if n not in ordered:ordered[n]=prior().TraceReplay(n,"lex" if arm=="lexical" else "cofactor",None)
                    ordered[n].check(targets,result)
                else:
                    oracle().verify_work(n,targets,result)
                public_return={**{k:result[k] for k in ("n","triple","class_count","width","summary_wires")},
                               "circuit":{k:result["circuit"][k] for k in ("gates","outputs")},"witnesses":result.get("witnesses",[])}
                require(len(canonical(public_return))==raw["return_bytes"], "physical/evidence serialization bytes")
                totals.update(covered_program_returns=1,covered_return_assignments=1<<n,covered_output_bits=2<<n,
                              covered_returned_witnesses=len(result.get("witnesses",[])))
            else:
                failures.append([event["case"],task["id"],raw["failure"]])
            grade=grades[panel][task["id"]]
            m=count_row(task,grade,raw,cert);total.update(m)
            for tag in (grade["kind"],str(n),grade["operation"]):by[tag].update(m)
            ops.update({k:v for k,v in (result or {}).get("work",{}).items() if type(v)is int})
            identity.append([result.get(k) for k in ("triple","width","summary_wires","circuit","witnesses")])
            choices.append([result.get(k) for k in ("triple","width","summary_wires","circuit")])
        encoded=canonical(identity)
        require(key not in fingerprints or fingerprints[key]==encoded, "deterministic programs/proofs changed between repeats")
        fingerprints[key]=encoded;logical_choices[key]=canonical(choices)
        total.update(startup_cpu_ns=s["startup_cpu_ns"],startup_wall_ns=s["startup_wall_ns"],
                     paid_cpu_ns=s["startup_cpu_ns"]+total["cpu_ns"],paid_wall_ns=s["startup_wall_ns"]+total["wall_ns"])
        counts[key][rep]=total;groups[key].append(by);work_runs[key].append(ops)
    methods={}
    for panel,roster in (("held",HELD),("calibration",CALIBRATION)):
        methods[panel]={}
        for arm in roster:
            key=panel,arm
            require(set(counts[key])==set(range(8)), "missing scheduled deployments "+str(key))
            series=[counts[key][r] for r in range(8)]
            row=methods[panel][arm]=oracle().median_fields(series)
            row["groups"]={tag:oracle().median_fields([r[tag] for r in groups[key]]) for tag in groups[key][0]}
            row["work"]=oracle().median_fields(work_runs[key]);row["cpu_repeats_ns"]=[r["paid_cpu_ns"] for r in series]
            row["wall_repeats_ns"]=[r["paid_wall_ns"] for r in series]
    held,cal=methods["held"],methods["calibration"]
    benchmark=min(PRIMITIVES,key=lambda a:held[a]["paid_cpu_ns"])
    constant=min(CONSTANT,key=lambda a:cal[a]["paid_cpu_ns"])
    skip=min(("skip-0","skip-1","skip-2","skip-3"),key=lambda a:cal[a]["paid_cpu_ns"])
    menu=cal["oracle-menu"];active=sum(menu.get("scheme_"+str(i),0)>0 for i in range(4))
    valid_cal=not any(f[0].startswith("calibration-") for f in failures)
    context=valid_cal and active>1 and wins(menu,cal[constant]) and wins(menu,cal[skip])
    abstain=valid_cal and wins(cal[skip],cal[constant]) and wins(cal[skip],cal["matched-exact"])
    decision=dict(best_constant=constant,best_skip=skip,menu_schemes_used=active,
                  menu_vs_constant=compare(menu,cal[constant]),menu_vs_skip=compare(menu,cal[skip]),
                  skip_vs_constant=compare(cal[skip],cal[constant]),skip_vs_no_probe=compare(cal[skip],cal["matched-exact"]),
                  select_context=bool(context),select_skip=bool(abstain),next="context" if context else "skip" if abstain else "stop")
    comparisons={a:compare(held["zero-one"],v) for a,v in held.items()}
    held_win=not any(f[0].startswith("held-") for f in failures) and wins(held["zero-one"],held[benchmark])
    potential={panel:coverage(panels[panel],grades[panel]) for panel in panels}
    official=read(out/"result.json")
    for name,value in dict(methods=methods,benchmark=benchmark,held_comparisons=comparisons,held_repeatable_win=held_win,
                           coverage=potential,failures=failures).items():
        require(canonical(official[name])==canonical(value), "assessor aggregation "+name)
    for name,value in decision.items():require(canonical(official["headroom"][name])==canonical(value), "headroom decision "+name)
    require(official["replay_totals"]==dict(tasks=totals["covered_program_returns"]+len(failures),
                                          rows=totals["covered_return_assignments"],output_bits=totals["covered_output_bits"]), "replay denominator")
    matched={}
    for panel,roster in (("held",HELD),("calibration",CALIBRATION)):
        baseline=logical_choices[panel,"matched-exact"]
        matched[panel]={arm:logical_choices[panel,arm]==baseline for arm in roster if arm not in ("reference","lexical","four-cofactor")}
    return dict(schema_version=1,ticket=TICKET,verdict="PASS",auditor_sha256=digest(__file__),
                terminal_oracle_sha256=ORACLE_SHA256,terminal_split_oracle_sha256=PRIOR_SHA256,
                source_design_sha256=digest(out/"design.json"),data_sha256=digest(out/"data-bound.json"),result_sha256=digest(out/"result.json"),
                streams=stream_hashes,independence="Original raw-row certificates; literal exact class and scalar NAND replay; complete probe/cache/fallback and CPU aggregation; no producer imports or timed solver reruns.",
                self_test=self_test(),split=split,replay=dict(totals),validated_distinct_witness_bindings=validated_record.cache_info().currsize,
                physical_factoring="Every asserted physical field plus original target tables must match byte-for-byte before reusing a scalar execution; all receipts, evidence and logical work are checked.",
                matched_physical_outputs=matched,benchmark=benchmark,held_repeatable_win=held_win,held_comparisons=comparisons,
                headroom=decision,headroom_vs_calibration_primitive={"menu":compare(menu,cal["primitive"]),"best_skip":compare(cal[skip],cal["primitive"])},
                methods=methods,coverage=potential,failures=failures,
                nonclaims=["Three signatures exclude only one bit at this triple; every other cut and any needed two-bit upper bound remain obligations.",
                           "Two contexts can miss distinguishing outside assignments, so inconclusive screens use exact fallback.",
                           "The free advice is nondeployable and not a proved optimal chooser: cache history and full CPU are not minimized by its witness-length score.",
                           "A within-probe headroom signal is not evidence of paid usefulness against faster primitives.",
                           "Repeated timings are the same96 held and24 calibration matched pairs, not fresh scientific examples."])


def self_test():
    # This cut has four classes, but a DIFFERENT eligible cut needs one bit.
    n = 4
    pair = [0, 0]
    for raw in range(16):
        a, b, c, d = [(raw >> i) & 1 for i in range(4)]
        h = a & b & c
        pair[0] |= (h ^ d) << raw
        pair[1] |= (h & d) << raw
    group = (0, 2, 3)
    positive = make_witness(n, tuple(pair), group, (0, 1))
    verified = verify_witness(n, pair, positive)
    compact = [sum(1 << j for j in group), *positive["local_states"], 3, 0]
    oracle().require(compact_record(n, pair, compact)["raw_inputs"] == verified["raw_inputs"],
                     "compact certificate raw-row reconstruction")
    oracle().require(verified["local_lower_bound_bits"] == 2 and
                     oracle().characterize(n, tuple(pair))["minimum_bits"] == 1,
                     "local lower bound was mistaken for global minimum")
    oracle().require(make_witness(n, tuple(pair), group, (0,)) is None and
                     oracle().partition(n, tuple(pair), group)[0] == 4,
                     "inconclusive sample was treated as a one-bit proof")
    # There is only one eligible triple and it really needs exactly TWO bits.
    pair2 = [0, 0]
    for raw in range(32):
        a, b, c, d, e = [(raw >> i) & 1 for i in range(5)]
        pair2[0] |= ((((a & b) ^ c) & d)) << raw
        pair2[1] |= ((((a & c) ^ b) | e)) << raw
    w2 = make_witness(5, tuple(pair2), (0, 1, 2), (0, 3))
    verify_witness(5, pair2, w2)
    oracle().require(oracle().characterize(5, tuple(pair2))["minimum_bits"] == 2,
                     "three signatures incorrectly exclude a two-bit construction")
    cache = RawObservations()
    cache.read_pair(n, pair, 15)
    before = cache.fresh_bits
    changed = (pair[0], pair[1] ^ (1 << 15))
    observed = cache.read_pair(n, changed, 15)
    oracle().require(cache.fresh_bits == before + 1 and observed == (0, 0), "stale changed-output cache bit")
    mutations = []
    bad = deepcopy(positive)
    bad["values"][0][0][0] ^= 1
    mutations.append(("wrong raw answer", bad))
    bad = deepcopy(positive)
    bad["contexts"][1] = 2
    mutations.append(("invalid outside assignment", bad))
    bad = deepcopy(positive)
    bad["local_states"][1] = bad["local_states"][0]
    mutations.append(("repeated local state", bad))
    for label, bad in mutations:
        try:
            verify_witness(n, pair, bad)
        except ValueError:
            pass
        else:
            raise AssertionError("malformed witness accepted: " + label)
    return dict(local_two_bit_certificate_with_global_one_bit=True,
                low_signature_count_inconclusive=True, three_signatures_do_not_exclude_two_bits=True,
                changed_output_cache_isolated=True, malformed_witnesses_rejected=[x[0] for x in mutations],
                physical_fixtures=oracle().self_test())


if __name__ == "__main__":
    import argparse
    import json
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true")
    parser.add_argument("--artifacts", type=Path, default=DEFAULT)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report=self_test() if args.self_test else audit(args.artifacts.resolve())
    if args.output:
        oracle().require(args.output.resolve()==DEFAULT/"audit.json", "output outside owned receipt")
        args.output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report if args.self_test else {k:report[k] for k in
          ("verdict","replay","benchmark","held_repeatable_win","headroom","headroom_vs_calibration_primitive")},indent=2,sort_keys=True))
