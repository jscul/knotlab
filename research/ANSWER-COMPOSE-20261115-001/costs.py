"""Measure cache setup and one-packet/one-question traffic for exact returns."""

import argparse
import hashlib
import json
import math
import os
import statistics
import subprocess
import sys
import time
from pathlib import Path


STUDY = "ANSWER-COMPOSE-20261115-001"
FAMILY = STUDY+"-E001_packet_nand"
ROOT = Path(__file__).resolve().parents[2]
EXP = ROOT/"experiments"/STUDY/FAMILY
DEFAULT_OUT = ROOT/"artifacts"/STUDY/FAMILY
METHODS = ("certified","lookup","four")
USES = (1,16,256,4096,65536)
LINK_US = (0,1,10,100)
TRAFFIC = 128
REPEATS = 3
sys.path.insert(0,str(EXP))


def read(path):
    return json.loads(path.read_bytes())


def shape(plan):
    return (tuple(plan["ports"]),plan["omitted_port"],plan.get("dag"),plan.get("lookup"))


def endpoint(out,method,side):
    # Generation and auditing of this workload are outside deployed endpoint work.
    import packet_io
    import compiler
    import panels
    schedules=panels.held_panel()
    expected=read(out/"plans.json")["wirings"]
    cpu=time.process_time_ns
    start=cpu()
    if method=="certified":
        import learner
        checkpoint=read(out/"checkpoint.json")
    model_ns=cpu()-start
    planning_ns=checking_ns=preparing_ns=traffic_ns=qa_ns=0
    sum_width=wire_parser_nands=wire_answer_nands=observed=lut_reads=0
    for index,(ident,wiring,_) in enumerate(schedules):
        start=cpu()
        if method=="certified":
            proposal=learner.plan(checkpoint,wiring)
        elif method=="lookup":
            plan,_=compiler.compile_lookup(wiring)
        else:
            plan=compiler.all_four()
        planning_ns+=cpu()-start
        if method=="certified":
            start=cpu()
            plan,_=compiler.certify(wiring,proposal)
            checking_ns+=cpu()-start
        if shape(plan)!=shape(expected[ident][side][method]):
            raise ValueError("Timed endpoint disagrees with the frozen result")
        ports=tuple(plan["ports"])
        sum_width+=len(ports)
        raws=[(149*k+37*index)&511 for k in range(TRAFFIC)]
        queries=[(k+index)%4 for k in range(TRAFFIC)]
        if side=="sender":
            start=cpu()
            packets=[packet_io.query_values(wiring,raw,ports) for raw in raws]
            traffic_ns+=cpu()-start
            observed+=sum(map(len,packets))
            wire_parser_nands+=TRAFFIC*sum(packet_io.parser_gate_cost(wiring[p]) for p in ports)
        else:
            start=cpu()
            reader=compiler.prepare_reader(plan)
            preparing_ns+=cpu()-start
            # Measure decoding without charging a second sender to this endpoint.
            packets=[packet_io.query_values(wiring,raw,ports) for raw in raws]
            start=cpu()
            answers=[reader(packet,q) for packet,q in zip(packets,queries,strict=True)]
            traffic_ns+=cpu()-start
            observed+=sum(answers)
            if "lookup" in plan:
                lut_reads+=queries.count(plan["omitted_port"])
            if plan.get("dag") is not None:
                wire_answer_nands+=len(plan["dag"]["gates"])*queries.count(plan["omitted_port"])
            # Scientific equivalence check of the accelerated measured receiver.
            start=cpu()
            for msg in range(1<<len(ports)):
                bits=tuple((msg>>i)&1 for i in range(len(ports)))
                for q in packet_io.ALL_PORTS:
                    ref=learner.receive_plan(plan,bits,q) if method=="certified" else compiler.lookup_receive(plan,bits,q)
                    if reader(bits,q)!=ref:
                        raise ValueError("Prepared receiver changed the physical program")
            assert all(ans==panels.truth(wiring,r)[q] for ans,r,q in zip(answers,raws,queries,strict=True))
            qa_ns+=cpu()-start
    return {"method":method,"side":side,"wirings":len(schedules),"uses_per_wiring":TRAFFIC,
            "load_ns":model_ns,"plan_ns":planning_ns,"explicit_certificate_ns":checking_ns,
            "prepare_reader_ns":preparing_ns,"traffic_ns":traffic_ns,"scientific_qa_ns":qa_ns,
            "sum_packet_width":sum_width,"physical_parser_nands":wire_parser_nands,
            "physical_decoder_nands":wire_answer_nands,"physical_lut_reads":lut_reads,
            "observed":observed}


def winning_interval(intercept,slope,others):
    low=1
    high=None
    for base,rate in others:
        d0,d1=intercept-base,slope-rate
        if d1==0:
            if d0>=0:
                return None
        elif d1<0:
            low=max(low,math.floor(d0/(-d1))+1)
        else:
            bound=math.ceil(-d0/d1)-1
            high=bound if high is None else min(high,bound)
    return None if high is not None and high<low else [low,high]


def benchmark(out):
    runs=[]
    env=os.environ|{"OPENBLAS_NUM_THREADS":"1","PYTHONHASHSEED":"0"}
    for repeated in range(REPEATS):
        order=METHODS[repeated:]+METHODS[:repeated]
        for method in order:
            for side in ("sender","receiver"):
                run=subprocess.run([sys.executable,"-B",__file__,"endpoint","--out",str(out),
                                    "--method",method,"--side",side],check=True,capture_output=True,text=True,env=env)
                record=json.loads(run.stdout)
                runs.append(record|{"repeat":repeated})
        print(f"Completed timing round {repeated+1}/{REPEATS}",file=sys.stderr,flush=True)
    fitted=json.loads((out/"results.jsonl").read_text().strip())["result"]
    model_bits=(out/"checkpoint.json").stat().st_size*8
    profiles={}
    for method in METHODS:
        subset=[row for row in runs if row["method"]==method]
        assert len({row["sum_packet_width"] for row in subset})==1
        def aggregate(key,divisor=1):
            pairs=[sum(r[key] for r in subset if r["repeat"]==i)/(1e9*divisor) for i in range(REPEATS)]
            return {"median":statistics.median(pairs),"range":[min(pairs),max(pairs)]}
        setup_keys=("load_ns","plan_ns","explicit_certificate_ns","prepare_reader_ns")
        setups=[sum(sum(r[k] for k in setup_keys) for r in subset if r["repeat"]==i)/1e9 for i in range(REPEATS)]
        profiles[method]={"acquisition_s":fitted["fit_cpu_seconds"] if method=="certified" else 0,
                          "setup_s":{"median":statistics.median(setups),"range":[min(setups),max(setups)]},
                          "components_s":{k:aggregate(k) for k in setup_keys},
                          "traffic_s_per_use_of_each_wiring":aggregate("traffic_ns",TRAFFIC),
                          "packet_bits_per_use_of_each_wiring":subset[0]["sum_packet_width"],
                          "checkpoint_bits_distributed_once":model_bits if method=="certified" else 0}
    comparisons={}
    for price in LINK_US:
        coefficients={}
        for method,p in profiles.items():
            link=price*1e-6
            coefficients[method]=[p["acquisition_s"]+p["setup_s"]["median"]+link*p["checkpoint_bits_distributed_once"],
                                  p["traffic_s_per_use_of_each_wiring"]["median"]+link*p["packet_bits_per_use_of_each_wiring"]]
        comparisons[str(price)]={
            "coefficients_seconds":coefficients,
            "projected_seconds":{str(n):{k:a+n*b for k,(a,b) in coefficients.items()} for n in USES},
            "uses_per_wiring_where_certified_beats_both":winning_interval(*coefficients["certified"],
                                                                         [coefficients["lookup"],coefficients["four"]])}
    value={"ticket":STUDY,"methodology":"Process CPU; 3 fresh processes per arm and endpoint; median paired endpoint setup and traffic. Shared parser already installed. One trained checkpoint transfer. No real packet cache.",
           "reference_certificate":"The lookup compiler proves the projection while building the LUT; four copies are correct by construction.",
           "repeats":REPEATS,"packets_per_wiring_timed":TRAFFIC,"runs":runs,"profiles":profiles,"link_us_per_bit":comparisons,
           "plans_sha256":hashlib.sha256((out/"plans.json").read_bytes()).hexdigest()}
    with (out/"costs.json").open("x") as stream:
        json.dump(value,stream,sort_keys=True,separators=(",",":"))
    return profiles


if __name__=="__main__":
    cli=argparse.ArgumentParser(description=__doc__)
    cli.add_argument("action",choices=("endpoint","benchmark"))
    cli.add_argument("--out",type=Path,default=DEFAULT_OUT)
    cli.add_argument("--method",choices=METHODS)
    cli.add_argument("--side",choices=("sender","receiver"))
    args=cli.parse_args()
    v=benchmark(args.out) if args.action=="benchmark" else endpoint(args.out,args.method,args.side)
    print(json.dumps(v,sort_keys=True))
