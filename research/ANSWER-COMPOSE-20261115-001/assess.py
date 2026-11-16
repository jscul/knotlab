"""Freeze sources and the fitted checkpoint, record raw plans, then grade."""

import argparse
import hashlib
import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

STUDY = "ANSWER-COMPOSE-20261115-001"
FAMILY = STUDY + "-E001_packet_nand"
ROOT = Path(__file__).resolve().parents[2]
RESEARCH = ROOT / "research" / STUDY
EXP = ROOT / "experiments" / STUDY / FAMILY
DEFAULT_OUT = ROOT / "artifacts" / STUDY / FAMILY
sys.path.insert(0, str(EXP))
import compiler
import learner
import packet_io
import panels

ARMS = ("raw", "certified", "lookup", "four", "one_call")


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":")).encode()


def hash_file(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def digest(value):
    return hashlib.sha256(canonical(value)).hexdigest()


def load(path):
    return json.loads(path.read_bytes())


def bind(path, value):
    data = canonical(value)
    if path.exists():
        if path.read_bytes() != data:
            raise ValueError(f"Bound record changed at {path}")
        return
    with path.open("xb") as stream:
        stream.write(data)


def sources(out):
    path = out / "freeze.json"
    stamp = load(path)["utc"] if path.exists() else datetime.now(timezone.utc).isoformat()
    files = [EXP / name for name in ("contract.json", "job.py", "packet_io.py", "learner.py", "compiler.py")]
    files += [RESEARCH / n for n in ("panels.py","preregistration.md","assess.py","costs.py")]
    files += [packet_io.PARSER_PATH]
    old = "BIT-DECODER-20261114-001"
    files += [ROOT/"experiments"/old/(old+"-E001_atomic_codec")/"codec.py"]
    files += [ROOT/"research"/"GROUP-SENDER-20261115-001"/"panels.py"]
    train, held = panels.training_panel(), panels.held_panel()
    if len({canonical(w) for _,w,_ in (*train,*held)}) != len(train)+len(held):
        raise ValueError("A public wiring occurs in more than one row")
    record = {"utc":stamp, "before_fit":True, "files":{str(f.relative_to(ROOT)):hash_file(f) for f in files},
              "training_panel_sha256":digest(train), "held_panel_sha256":digest(held),
              "train_count":len(train), "held_count":len(held)}
    bind(path,record)
    return record


def freeze(out):
    if not (out/"freeze.json").exists():
        raise ValueError("Missing training-source freeze")
    manifest = sources(out)
    records = [json.loads(l) for l in (out/"results.jsonl").read_text().splitlines()]
    if len(records) != 1 or records[0]["case"]!="packet_nand" or records[0]["status"]!="ok":
        raise ValueError("Expected exactly one successful fit")
    row = records[0]
    assert row["job_sha"] == hash_file(EXP/"job.py")
    assert datetime.fromisoformat(row["finished_at"]) >= datetime.fromisoformat(manifest["utc"])
    checkpoint = row["result"]["checkpoint"]
    bind(out/"checkpoint.json",checkpoint)
    assert hash_file(out/"checkpoint.json")==row["result"]["checkpoint_sha256"]
    receipt = {"checkpoint_sha256":hash_file(out/"checkpoint.json"),"sources_sha256":hash_file(out/"freeze.json"),
               "training_output_sha256":hash_file(out/"results.jsonl")}
    bind(out/"checkpoint_binding.json",receipt)
    return receipt


def checked_checkpoint(out):
    binding = load(out/"checkpoint_binding.json")
    for name,key in (("checkpoint.json","checkpoint_sha256"),("freeze.json","sources_sha256"),("results.jsonl","training_output_sha256")):
        if hash_file(out/name)!=binding[key]:
            raise ValueError(f"Broken training binding for {name}")
    return load(out/"checkpoint.json")


def propose(out):
    checkpoint = checked_checkpoint(out)
    sources(out)
    rows = {}
    for ident,w,_ in panels.held_panel():
        rows[ident] = {"raw":learner.plan(checkpoint,w), "one_call":learner.plan(checkpoint,w,max_calls=1)}
    record = {"checkpoint_sha256":hash_file(out/"checkpoint.json"), "plans":rows}
    bind(out/"raw_proposals.json",record)
    return {"wirings":len(rows),"raw_proposals_sha256":hash_file(out/"raw_proposals.json")}


def compile_plans(out):
    cp = checked_checkpoint(out)
    proposed = load(out/"raw_proposals.json")
    assert proposed["checkpoint_sha256"] == hash_file(out/"checkpoint.json")
    rows = {}
    for ident,w,_ in panels.held_panel():
        stored = proposed["plans"][ident]
        # Each endpoint has only the public wiring and the frozen policy.
        receiver_raw = learner.plan(cp,w)
        receiver_one = learner.plan(cp,w,max_calls=1)
        assert digest(receiver_raw)==digest(stored["raw"]) and digest(receiver_one)==digest(stored["one_call"])
        send_cert, cert_work = compiler.certify(w,stored["raw"])
        recv_cert, _ = compiler.certify(w,receiver_raw)
        send_lookup,lookup_work = compiler.compile_lookup(w)
        recv_lookup,_ = compiler.compile_lookup(w)
        assert send_cert==recv_cert and send_lookup==recv_lookup
        rows[ident] = {
            "sender":{**stored,"certified":send_cert,"lookup":send_lookup,"four":compiler.all_four()},
            "receiver":{"raw":receiver_raw,"one_call":receiver_one,"certified":recv_cert,"lookup":recv_lookup,"four":compiler.all_four()},
            "certificate":cert_work,"lookup_work":lookup_work,
        }
    bind(out/"plans.json",{"proposal_sha256":hash_file(out/"raw_proposals.json"),"wirings":rows})
    return {"wirings":len(rows),"plans_sha256":hash_file(out/"plans.json")}


def receive(arm,plan,packet,port):
    if arm in ("lookup","four"):
        return compiler.lookup_receive(plan,packet,port)
    return learner.receive_plan(plan,packet,port)


def information(answers):
    signatures = set(answers)
    possible = []
    for omitted in range(4):
        keys = {tuple(v[p] for p in range(4) if p!=omitted) for v in signatures}
        if len(keys)==len(signatures):
            possible.append(omitted)
    return {"distinct_answers":len(signatures),"minimum_bits":(len(signatures)-1).bit_length(),
            "possible_omissions":possible,"projection_bits":3 if possible else 4}


def evaluate_row(w,answers,arm,outbound,inbound):
    ports=compiler.checked_ports(outbound)
    total=correct_odd=full=0
    per_port=[0]*4
    first=None
    digestor=hashlib.sha256()
    for raw,wanted in enumerate(answers):
        packet=(learner.send_plan(w,raw,outbound) if arm in ("raw","certified","one_call")
                else packet_io.query_values(w,raw,ports))
        assert len(packet)==len(ports) and all(type(x) is int and x in (0,1) for x in packet)
        digestor.update(bytes((len(packet),))+bytes(packet))
        returned=tuple(receive(arm,inbound,packet,p) for p in range(4))
        assert all(type(x) in (int,bool) and x in (0,1) for x in returned)
        matches=tuple(x==y for x,y in zip(wanted,returned,strict=True))
        total+=sum(matches)
        full+=all(matches)
        if raw.bit_count()%2:
            correct_odd+=sum(matches)
        for p,ok in enumerate(matches):
            per_port[p]+=ok
        if not all(matches) and first is None:
            first={"raw":raw,"packet":packet,"wanted":wanted,"returned":returned}
    return {"width":len(ports),"ports":ports,"omitted_port":outbound["omitted_port"],
            "correct_questions":total,"correct_vectors":full,"correct_odd":correct_odd,
            "correct_by_port":per_port,"first_error":first,"physical_sha256":digestor.hexdigest(),
            "decoder_nands":len((outbound.get("dag") or {}).get("gates",[]))}


def summarize(rows):
    out={}
    for arm in ARMS:
        rec=[(r,r["arms"][arm]) for r in rows]
        out[arm]={"correct_questions":sum(v["correct_questions"] for _,v in rec),"total_questions":2048*len(rec),
                  "correct_odd":sum(v["correct_odd"] for _,v in rec),
                  "all_exact_wirings":sum(v["correct_vectors"]==512 for _,v in rec),
                  "exact_minimum_wirings":sum(v["correct_vectors"]==512 and v["width"]==r["minimum_bits"] for r,v in rec),
                  "exact_projection_wirings":sum(v["correct_vectors"]==512 and v["width"]==r["projection_bits"] for r,v in rec),
                  "widths":dict(Counter(v["width"] for _,v in rec)),"sum_width":sum(v["width"] for _,v in rec)}
    return out


def grade(out):
    checked_checkpoint(out)
    data=load(out/"plans.json")
    assert data["proposal_sha256"]==hash_file(out/"raw_proposals.json")
    result=[]
    for ident,w,meta in panels.held_panel():
        plans=data["wirings"][ident]
        answers=[tuple(panels.truth(w,raw)) for raw in range(512)]
        rows={k:evaluate_row(w,answers,k,plans["sender"][k],plans["receiver"][k]) for k in ARMS}
        result.append({"id":ident,"metadata":meta,**information(answers),"arms":rows,
                       "even_answer_parity_rows":sum(sum(v)%2==0 for v in answers),
                       "certificate_status":plans["certificate"]["status"],
                       "certificate_wrong_rows":plans["certificate"]["wrong_rows"]})
    groups=sorted({r["metadata"]["family"] for r in result})
    record={"ticket":STUDY,"artifact_id":STUDY+"-E001","kind":"experiment","evidence_stage":"exploratory",
            "schema_version":1,"rows":result,"summary":summarize(result),
            "families":{k:summarize([r for r in result if r["metadata"]["family"]==k]) for k in groups},
            "plans_sha256":hash_file(out/"plans.json")}
    bind(out/"result.json",record)
    return record["summary"]


if __name__=="__main__":
    parser=argparse.ArgumentParser(description=__doc__)
    actions={"sources":sources,"freeze":freeze,"propose":propose,"compile":compile_plans,"grade":grade}
    parser.add_argument("action",choices=actions)
    parser.add_argument("--out",type=Path,default=DEFAULT_OUT)
    args=parser.parse_args()
    print(json.dumps(actions[args.action](args.out),indent=2))
