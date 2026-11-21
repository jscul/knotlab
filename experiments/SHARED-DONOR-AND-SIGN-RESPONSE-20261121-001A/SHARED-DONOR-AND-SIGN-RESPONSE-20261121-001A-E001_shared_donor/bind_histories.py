"""Bind each selected later subinterval to its literal first and second physical cut."""
from hashlib import sha256
from pathlib import Path
import gzip
import json

HERE=Path(__file__).resolve().parent
OUTPUT=HERE.parents[2]/"artifacts"/HERE.parent.name/HERE.name
SITES=(20,21,23,25)
NAME={f"w{i}":f"w{j}" for j,i in enumerate(SITES,1)}


def erased_ends(n,a,b):
    return [[0,n],[a,n],[a,b]]


def main():
    physical_path=OUTPUT/"physical.json.gz"
    clock_path=OUTPUT/"clock.json.gz"
    with gzip.open(physical_path,"rt") as stream: physical=json.load(stream)
    with gzip.open(clock_path,"rt") as stream: clock=json.load(stream)
    original={case["case"]:case for case in physical["cases"]}
    rows=[]
    for arm in clock["cases"]:
        mode=arm["gates"]
        if mode=="archive": continue
        life="active" if arm["lifetime"]=="active" else "rewired"
        case=original[f"{life}_{mode}"]
        for law,ledger in case["laws"].items():
            data=ledger["shared_donor"]
            first=sorted(data["gate_inputs"],key=lambda r:int(r["gate_site"]))
            joint,=data["actual_through_births"]
            first_ids=[t["holder"] for t in first]
            assert len({t["actual_name_from_payer"] for t in first})==2
            assert set(first[0]["parents"])&set(first[1]["parents"])=={data["payer"]}
            assert len(joint["parents"])==2 and set(first_ids)==set(joint["parents"])
            assert joint["grant"]==arm["local_common_child"]["grant"],(case["case"],joint["grant"],arm["local_common_child"])
            assert joint["has_exactly_the_two_crossings"]
            for i,entry in enumerate(first):
                want={NAME.get(role,role) for role in arm["local_common_child"]["first_groups"][i]}
                assert want==set(entry["original_donor_roles"])
                assert entry["grant"]==(4 if mode[i]=="C" else 6)
                assert len(set(entry["fresh_names"])&set(joint["consumed_names"]))==1
            for reader,records in arm["readers"].items():
                for point in records:
                    for witness in point["minimizers"]:
                        intervals=witness["mixed_local_rank_three_ancestor_in_incoming"]
                        if reader=="extended":assert len(intervals)==1
                        for a,b in intervals:
                            inc=witness["incoming_word"]
                            assert inc[a:b]==["c20","c21","c22"]
                            assert [[NAME.get(v,v) for v in inc[a:b-1]],[NAME.get(v,v) for v in inc[a+1:b]]]==[
                                ["c20","c21"],["c21","c22"]]
                            rows.append({"case":case["case"],"law":law,"reader":reader,"m":point["send"],
                                         "send_size":point["send"],"receiving_size":witness["size"],
                                         "first_source_donor":data["payer"],"two_private_names":[p["actual_name_from_payer"] for p in first],
                                         "first_groups":first_ids,"first_group_grants":[p["grant"] for p in first],
                                         "through_child":joint["holder"],"through_child_inputs":joint["consumed_names"],
                                         "through_child_grant":joint["grant"],
                                         "incoming_word_true_deletion_chain_ranges":erased_ends(len(inc),a,b),
                                         "convention":"Delete left endpoints one at a time to the middle pair, then right endpoints one at a time. Each step is a true parent."})
    p=OUTPUT/"bound_histories.json.gz"
    receipts={"physical_sha256":sha256(physical_path.read_bytes()).hexdigest(),
              "clock_sha256":sha256(clock_path.read_bytes()).hexdigest(),"rows":rows}
    serialized=(json.dumps(receipts,sort_keys=True,separators=(",",":"))+"\n").encode()
    p.write_bytes(gzip.compress(serialized,compresslevel=9,mtime=0))
    print(len(rows),"actual physical bindings",sha256(p.read_bytes()).hexdigest())


if __name__=="__main__":main()
