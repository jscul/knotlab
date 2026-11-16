"""Freeze the learned policies, then evaluate physical messages and delayed queries."""
import argparse
from collections import Counter
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import sys
import time

TICKET = "BIT-DECODER-20261114-001"
FAMILY = TICKET + "-E001_atomic_codec"
ROOT = Path(__file__).resolve().parents[2]
EXPERIMENT = ROOT / "experiments" / TICKET / FAMILY
DEFAULT_OUT = ROOT / "artifacts" / TICKET / FAMILY
sys.path.insert(0, str(EXPERIMENT))
import codec
import wirings

CONDITIONS = ("any_only", "varied")


def canonical(v):
    return json.dumps(v, sort_keys=True, separators=(",", ":")).encode()


def file_hash(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_bound(path, value):
    b = canonical(value)
    if path.exists():
        if path.read_bytes() != b:
            raise ValueError(f"Frozen content differs at {path}")
    else:
        with path.open("xb") as writer:
            writer.write(b)


def freeze_checkpoints(out):
    raw = [json.loads(line) for line in (out / "results.jsonl").read_text().splitlines()]
    if len(raw) != 2 or {r["case"] for r in raw} != set(CONDITIONS) or any(r["status"] != "ok" for r in raw):
        raise ValueError("Both completed training-only fits are required before evaluation")
    binding = {}
    for row in raw:
        condition = row["case"]
        result = row["result"]
        if result["condition"] != condition:
            raise ValueError("Training case identity mismatch")
        path = out / (condition + "_checkpoint.json")
        write_bound(path, result["checkpoint"])
        digest = file_hash(path)
        if digest != result["checkpoint_sha256"]:
            raise ValueError("Serialized checkpoint differs from fitted parameters")
        binding[condition] = digest
    receipt = {"sources_frozen": file_hash(out / "freeze.json"), "training_output": file_hash(out / "results.jsonl"),
               "checkpoints": binding, "assessment_requires_both": True}
    write_bound(out / "checkpoint_bindings.json", receipt)
    return receipt


def read_policy(out, name, binding):
    path = out / (name + "_checkpoint.json")
    if file_hash(path) != binding["checkpoints"][name]:
        raise ValueError("One of the frozen policies has changed")
    return json.loads(path.read_bytes())


def evaluate_menu(checkpoint, item):
    identity, wiring, meta = item
    sender, receiver = codec.Codec(checkpoint), codec.Codec(checkpoint)
    @lru_cache(None)
    def decode(packet):
        return tuple(receiver.receive(wiring, packet, port) for port in range(4))

    by_packet = {}
    by_answer = {}
    by_prefix = {}
    width_hist = Counter()
    correct_by_port, odd_correct = [0]*4, [0]*4
    all_answers, first_error, truncated_collision = 0, None, None
    packet_bytes = bytearray()
    for raw in range(512):
        packet = tuple(sender.send(wiring, raw))
        if any(type(x) not in (int,bool) or x not in (0,1) for x in packet):
            raise ValueError("The sender emitted a nonbit")
        truth = tuple(wirings.truth(wiring, raw))
        answers = decode(packet)
        if any(type(x) not in (int,bool) or x not in (0,1) for x in answers):
            raise ValueError("The receiver emitted a nonbit")
        width_hist[len(packet)] += 1
        packet_bytes.extend([len(packet),*packet])
        by_packet.setdefault(packet, set()).add(truth)
        by_answer.setdefault(truth, set()).add(packet)
        prefix = packet[:3]
        if prefix in by_prefix:
            old_raw, old_truth = by_prefix[prefix]
            if old_truth != truth and truncated_collision is None:
                truncated_collision = {"raw_masks": [old_raw,raw], "prefix": prefix, "answers": [old_truth,truth]}
        else:
            by_prefix[prefix] = (raw,truth)
        for i in range(4):
            hit = int(truth[i] == answers[i])
            correct_by_port[i] += hit
            if raw.bit_count() % 2:
                odd_correct[i] += hit
        all_answers += answers == truth
        if answers != truth and first_error is None:
            first_error = {"raw_mask":raw, "packet":packet, "target":truth, "decoded":answers}
    if len(width_hist) != 1:
        raise ValueError(f"Input-dependent width on {identity}: {dict(width_hist)}")
    width = next(iter(width_hist))
    floor = (len(by_answer)-1).bit_length()
    # Give a fixed omitted-position baseline the best conceivable decoder of
    # the three other answer bits. An answer-vector collision defeats it.
    recoverable_omissions = [j for j in range(4)
                             if len({v[:j]+v[j+1:] for v in by_answer}) == len(by_answer)]
    return {"id": identity, "family":meta["family"],"padding":meta.get("padding"),"layout":meta["layout"],
            "source_cells":meta.get("source_cells"), "varied_port":meta["varied_port"],"ports":meta.get("port_order"),
            "minimum":floor, "width":width,"answer_patterns":len(by_answer), "distinct_packets":len(by_packet),
            "correct_by_port":correct_by_port, "correct_bits":sum(correct_by_port), "correct_vectors":all_answers,
            "correct_odd_bits":sum(odd_correct), "packet_collisions":sum(len(s)>1 for s in by_packet.values()),
            "answer_groups_with_multiple_packets":sum(len(s)>1 for s in by_answer.values()),
            "physical_messages_sha256":hashlib.sha256(packet_bytes).hexdigest(),
            "optimal_and_exact":width==floor and all_answers==512,"first_error":first_error,
            "recoverable_answer_port_omissions":recoverable_omissions,
            "first_collision_after_three_bits":truncated_collision, "public_plan":codec.packet_plan(checkpoint,wiring)}


def summarize(rows):
    groups={}
    for family in sorted({r["family"] for r in rows} | {"all"}):
        cells = [r for r in rows if family=="all" or r["family"]==family]
        def hist(name):
            return dict(sorted(Counter(r[name] for r in cells).items()))
        groups[family]={
            "wirings":len(cells),"raw_inputs":512*len(cells),"queries":2048*len(cells),
            "correct_bits":sum(r["correct_bits"] for r in cells),
            "correct_vectors":sum(r["correct_vectors"] for r in cells),
            "odd_correct_bits":sum(r["correct_odd_bits"] for r in cells),"odd_queries":1024*len(cells),
            "exact_wirings":sum(r["correct_vectors"]==512 for r in cells),
            "exact_minimum_wirings":sum(r["optimal_and_exact"] for r in cells),
            "widths":hist("width"),"lower_bounds":hist("minimum")}
    return groups


def matched(checkpoint, items):
    index={item[0]:item for item in items}
    sender, receiver = codec.Codec(checkpoint), codec.Codec(checkpoint)
    output={}
    for old,new in (("any","exactly_one"),("matched_negative","exactly_one"),("alias","independent"),
                    ("xor_known","xor_new"),("stress_repeat_exactly_one","stress_cross_exactly_one")):
        totals=Counter()
        example=None
        for _,w,meta in items:
            if meta["family"]!=old or new not in meta["partners"]:
                continue
            other= index[meta["partners"][new]][1]
            port=meta["varied_port"]
            totals["paired_wirings"]+=1
            @lru_cache(None)
            def decoded_old(msg):
                return receiver.receive(w,msg,port)
            @lru_cache(None)
            def decoded_new(msg):
                return receiver.receive(other,msg,port)
            for raw in range(512):
                y,z=wirings.truth(w,raw)[port],wirings.truth(other,raw)[port]
                if y==z:
                    continue
                totals["changed_true_answers"]+=1
                a,b=tuple(sender.send(w,raw)),tuple(sender.send(other,raw))
                ended=decoded_new(b)
                totals["new_answer_correct"]+=ended==z
                if a==b:
                    totals["same_physical_packet"]+=1
                    started=decoded_old(a)
                    totals["same_packet_both_answers_correct"]+=started==y and ended==z
                    totals["stale_receiver_correct_on_same_packet"]+=started==z
                    if example is None and started==y and ended==z:
                        example={"raw":raw,"source_cells":meta["source_cells"],"port":port,"packet":a,
                                 "old":started,"new":ended}
        output[f"{old}__{new}"]={"counts":dict(totals),"first_same_packet_change":example}
    return output


def strict_identifiability_control():
    def positive_triple_only(question, n):
        row=next(v for v in question if len(v)==3)
        return int(any((n>>(abs(x)-1))&1 for x in row))
    counts=Counter()
    for _,w,meta in wirings.training_panel():
        if meta["family"]=="any":
            for n in range(512):
                ref=wirings.truth(w,n)
                counts['training_bits']+=4
                counts['training_correct']+=sum(positive_triple_only(q,n)==truth for q,truth in zip(w,ref))
    for _,w,meta in wirings.held_panel():
        if meta['family']=='exactly_one':
            j=meta['varied_port']
            for n in range(512):
                counts['unseen_fourth_bits']+=1
                counts['unseen_fourth_correct']+=positive_triple_only(w[j],n)==wirings.truth(w,n)[j]
    return dict(counts)


def assess(out):
    binding=json.loads((out/'checkpoint_bindings.json').read_bytes())
    if binding['training_output']!=file_hash(out/'results.jsonl'):
        raise ValueError('Training record changed after freezing')
    rosters={'train':wirings.training_panel(), 'held':wirings.held_panel(), 'stress':wirings.stress_panel()}
    outcome={'ticket':TICKET,'artifact_id':TICKET+'-E001','schema_version':1,'kind':'experiment',
             'evidence_stage':'exploratory','checkpoint_bindings':binding,'panel_audit':wirings.audit(),
             'strict_identifiability':strict_identifiability_control(),'conditions':{}}
    for name in CONDITIONS:
        start=time.perf_counter()
        checkpoint=read_policy(out,name,binding)
        part={}
        for label,items in rosters.items():
            rows=[evaluate_menu(checkpoint,item) for item in items]
            part[label]={'families':summarize(rows),'menus':rows}
        part['matched']=matched(checkpoint,rosters['held']+rosters['stress'])
        part['seconds']=time.perf_counter()-start
        outcome['conditions'][name]=part
        if file_hash(out/(name+'_checkpoint.json'))!=binding['checkpoints'][name]:
            raise ValueError('Evaluation altered checkpoint')
    return outcome


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('action',choices=('freeze','assess'))
    parser.add_argument('--out',type=Path,default=DEFAULT_OUT)
    a=parser.parse_args()
    if a.action=='freeze':
        print(json.dumps(freeze_checkpoints(a.out),indent=2))
    else:
        result=assess(a.out)
        path=a.out/'result.json'
        path.write_text(json.dumps(result,separators=(',',':'))+'\n')
        print(json.dumps({k:row['held']['families']['all'] for k,row in result['conditions'].items()},indent=2))
